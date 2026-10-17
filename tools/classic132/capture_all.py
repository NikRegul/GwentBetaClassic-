"""One user-started Classic session: attach after world load, trace and dump.

Software debugger breakpoints are temporary changes to our own child's memory.
Original instructions are restored before detach; executable/save files are
never written. Full dumps stay locally in this workspace for offline analysis.
"""
import argparse
import ctypes as C
from datetime import datetime
import json
import msvcrt
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import threading
import time
import traceback

from capture_scaleform import Trace, DBG_CONTINUE, DBG_NOT_HANDLED
from capture_menu_log import GAME, digest, snapshot

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'BetaGwent/build/classic132-full-feedback'
MANIFEST = ROOT / 'BetaGwent/build/classic081-complete-audit/all-trace-points.json'
REGISTERS = dict(rax=120, rcx=128, rdx=136, rbx=144, rsp=152, rbp=160, rsi=168,
                 rdi=176, r8=184, r9=192, r10=200, r11=208, r12=216, r13=224,
                 r14=232, r15=240, rip=248)


class FullTrace(Trace):
    def __init__(self, process, out, manifest, self_test=False):
        super().__init__(process, out, [], self_test)
        self.manifest = manifest
        self.code_points, self.steps, self.dumped = {}, {}, set()
        self.armed = self_test
        self.target_files = set()
        self.target_objects = {}
        self.render_due = {}
        self.render_break_pending = False
        self.image_names = {}
        self.exe_data = b'' if self_test else (GAME / 'bin/x64/witcher3.exe').read_bytes()
        self.restore_verified = False
        self.event_exception = None
        self.fail_self_test = False
        self.cancel_requested = False
        self.cleanup_done = threading.Event()
        self.console_handler = None
        for name, arguments, result in [
            ('WriteProcessMemory', [C.c_void_p, C.c_void_p, C.c_void_p, C.c_size_t, C.POINTER(C.c_size_t)], C.c_int),
            ('VirtualProtectEx', [C.c_void_p, C.c_void_p, C.c_size_t, C.c_uint32, C.POINTER(C.c_uint32)], C.c_int),
            ('FlushInstructionCache', [C.c_void_p, C.c_void_p, C.c_size_t], C.c_int),
            ('DebugActiveProcess', [C.c_uint32], C.c_int),
            ('DebugBreakProcess', [C.c_void_p], C.c_int),
        ]:
            fn = getattr(self.k, name)
            fn.argtypes, fn.restype = arguments, result

    def write_code(self, address, data):
        protection = C.c_uint32()
        handle = int(self.process._handle)
        if not self.k.VirtualProtectEx(handle, address, len(data), 0x40, C.byref(protection)):
            raise C.WinError(C.get_last_error())
        try:
            buffer, written = C.create_string_buffer(data), C.c_size_t()
            if not self.k.WriteProcessMemory(handle, address, buffer, len(data), C.byref(written)) or written.value != len(data):
                raise C.WinError(C.get_last_error())
            if not self.k.FlushInstructionCache(handle, address, len(data)):
                raise C.WinError(C.get_last_error())
        finally:
            unused = C.c_uint32()
            if not self.k.VirtualProtectEx(handle, address, len(data), protection.value, C.byref(unused)):
                raise C.WinError(C.get_last_error())

    def expected_bytes(self, address):
        rva = address - self.base
        for section in self.manifest['sections']:
            if section['rva'] <= rva < section['rva'] + section['rawSize']:
                offset = section['rawOffset'] + rva - section['rva']
                return self.exe_data[offset:offset + 8]
        raise RuntimeError('Dynamic breakpoint is outside the audited executable')

    def add_point(self, name, address, signature=None):
        if address in self.code_points:
            return
        expected = bytes.fromhex(signature) if signature else self.expected_bytes(address)
        actual = self.memory(address, len(expected))
        if actual != expected or not actual or actual[0] == 0xCC:
            raise RuntimeError('Loader instruction signature differs: ' + name)
        self.code_points[address] = dict(name=name, original=actual[:1], enabled=True)
        self.write_code(address, b'\xcc')
        self.record('CODE_POINT_ADDED', 0, name=name, address=hex(address),
                    rva=hex(address - self.base), original=actual.hex())

    def install_points(self, deep=False):
        for point in self.manifest['points']:
            if deep or point['name'] in ('RESOURCE_GATE', 'GFX_MESSAGE'):
                self.add_point(point['name'], self.base + point['rva'], point['signature'])

    def restore_code(self):
        for address, point in self.code_points.items():
            if point['enabled']:
                self.write_code(address, point['original'])
                point['enabled'] = False
        self.restore_verified = all(self.memory(a, 1) == p['original'] for a, p in self.code_points.items())

    def registers(self, context):
        return {name: C.c_uint64.from_address(context + offset).value for name, offset in REGISTERS.items()}

    def detailed(self, name, tid, regs, **extra):
        stack = self.memory(regs['rsp'], 2048)
        callers = []
        if self.base:
            for i in range(0, len(stack) - 7, 8):
                value = struct.unpack_from('<Q', stack, i)[0]
                if self.base <= value < self.base + self.manifest.get('imageSize', 0):
                    callers.append(dict(stackOffset=i, rva=hex(value - self.base)))
        memory = {r: dict(address=hex(regs[r]), bytes=self.memory(regs[r], 512).hex())
                  for r in ('rcx', 'rdx', 'r8', 'r9', 'rbx', 'rsi', 'rdi') if regs[r]}
        self.record(name, tid, registers={k: hex(v) for k, v in regs.items()},
                    stack=stack.hex(), executablePointers=callers, referencedMemory=memory, **extra)

    def failure_dump(self, key, tid, reason):
        if key in self.dumped or len(self.dumped) >= 4:
            return
        self.dumped.add(key)
        name = ('state-' if str(key).startswith(('loaded-', 'rendered-')) else 'failure-') + str(key) + '.dmp'
        path = self.out / name
        (self.out / 'breakpoints.json').write_text(json.dumps([
            dict(address=hex(a), rva=hex(a - self.base), name=p['name'],
                 original=p['original'].hex(), enabled=p['enabled'])
            for a, p in self.code_points.items()], indent=2), 'utf8')
        # A console-close event has a short Windows deadline. Leave no INT3/TF
        # in the game during a potentially long native dump call, so even a
        # forced collector exit here cannot strand our instrumentation.
        enabled = [address for address, point in self.code_points.items() if point['enabled']]
        self.restore_code()
        for step_tid in self.steps:
            storage, context = self.context(self.threads[step_tid])
            C.c_uint32.from_address(context + 68).value &= ~0x100
            if not self.k.SetThreadContext(self.threads[step_tid], context):
                raise C.WinError(C.get_last_error())
        print('Сохраняю локальный снимок памяти:', path, flush=True)
        dbg = C.WinDLL('C:/Windows/System32/dbghelp.dll', use_last_error=True)
        dbg.MiniDumpWriteDump.argtypes = [C.c_void_p, C.c_uint32, C.c_void_p, C.c_uint32,
                                        C.c_void_p, C.c_void_p, C.c_void_p]
        dbg.MiniDumpWriteDump.restype = C.c_int
        # Full memory + handles + unloaded modules + process/thread data +
        # full memory map + thread info + ignore inaccessible regions.
        flags = 0x21926
        with path.open('wb') as stream:
            success = dbg.MiniDumpWriteDump(int(self.process._handle), self.process.pid,
                                            msvcrt.get_osfhandle(stream.fileno()), flags, None, None, None)
            error = C.get_last_error() if not success else 0
        self.record('MEMORY_DUMP', tid, reason=reason, path=str(path), success=bool(success),
                    error=hex(error), bytes=path.stat().st_size, flags=hex(flags),
                    originalCodeRestoredDuringDump=self.restore_verified)
        if not self.cancel_requested:
            stepping = {step['address'] for step in self.steps.values()}
            if self.event_exception:
                stepping.add(self.event_exception[1])
            for address in enabled:
                self.code_points[address]['enabled'] = True
                if address not in stepping:
                    self.write_code(address, b'\xcc')
            for step_tid in self.steps:
                storage, context = self.context(self.threads[step_tid])
                C.c_uint32.from_address(context + 68).value |= 0x100
                if not self.k.SetThreadContext(self.threads[step_tid], context):
                    raise C.WinError(C.get_last_error())
        if success:
            print('Снимок памяти сохранён:', path.name, flush=True)
        else:
            print('Снимок памяти не сохранён; код ошибки записан в лог:', hex(error), flush=True)
        if self.self_test:
            assert success and path.read_bytes()[:4] == b'MDMP'

    def target(self, address):
        detail = self.file_details(address)
        name = detail['name'].lower()
        relevant = detail['fileId'] in self.target_files or name in ('deck_builder.redswf', 'gwint_game.redswf') or ('betagwent' in name and name.endswith('.redswf'))
        if relevant:
            self.target_files.add(detail['fileId'])
            self.target_objects[address] = detail
        return relevant, detail

    def point_hit(self, name, tid, regs):
        if self.self_test:
            self.record(name, tid, text=self.ascii(regs['rcx']))
            if name == 'POINT_0':
                address = min(self.code_points) + 64
                if address not in self.code_points:
                    self.add_point('POINT_4', address, self.memory(address, 8).hex())
                self.failure_dump('self-test', tid, 'self-test only')
                if getattr(self, 'test_late_snapshot', False):
                    self.render_due['self-test'] = (time.monotonic() + 0.05, 0)
                if self.fail_self_test:
                    raise RuntimeError('Expected self-test interruption')
            return
        if name == 'GFX_MESSAGE':
            message = self.ascii(regs['rsp'] + 0x50)
            self.record(name, tid, message=message)
            if not self.dumped and 'Loader failed to open' in message and ('gwint' in message.lower() or 'betagwent' in message.lower()):
                self.failure_dump('menu-open', tid, message)
            return
        if name == 'RESOURCE_GATE':
            relevant, detail = self.target(regs['rcx'])
            if not relevant:
                return
            if not self.armed:
                self.armed = True
                self.install_points(deep=True)
                self.record('DEEP_TRACE_ARMED', tid, file=detail, points=len(self.code_points))
            self.detailed(name, tid, regs, file=detail)
            return
        if not self.armed:
            return
        extra = {}
        if name in ('GFX_IMAGE_FILE', 'GFX_IMAGE_BINDING'):
            string = self.pointer(regs['r8']) & ~3
            filename = self.ascii(string + 12) if string else ''
            self.image_names[tid] = filename
            extra.update(image=filename, createInfo=self.memory(regs['rdx'], 112).hex())
        if name == 'GFX_IMAGE_TEXTURE':
            texture = regs['rdi']
            extra.update(image=self.image_names.get(tid, ''), texture=hex(texture),
                         textureType=self.native_type(texture),
                         linkage=self.native_string(texture + 0xe8),
                         renderProxy=hex(self.pointer(texture + 0xd0)))
        if name == 'GFX_IMAGE_CREATED':
            extra.update(image=self.image_names.get(tid, ''), imageObject=hex(regs['rdi']),
                         imageType=self.native_type(regs['rdi']))
        if name == 'GFX_TEXTURE_LOOKUP_RESULT':
            control = regs['rax']
            texture = self.pointer(control)
            texture = self.pointer(texture + 0x10) if texture else 0
            extra.update(image=self.native_string(regs['rsi']), control=hex(control),
                         texture=hex(texture), textureType=self.native_type(texture))
        if name == 'GFX_IMAGE_FILE_CREATED':
            extra.update(image=self.image_names.get(tid, ''), imageObject=hex(regs['rax']),
                         imageType=self.native_type(regs['rax']))
        if name in ('RESOURCE_CLASS', 'RESOURCE_FAILED', 'RESOURCE_LOAD_START'):
            relevant, detail = self.target(regs['rdx'] if name == 'RESOURCE_CLASS' else regs['rcx'])
            extra['file'] = detail
            if name == 'RESOURCE_FAILED' and relevant:
                self.failure_dump(detail['fileId'], tid, 'Resource marked failed before destruction')
        if name == 'RESOURCE_CLASS_RETURN':
            class_object = regs['rdi']
            state = self.memory(class_object, 112)
            extra.update(classObject=hex(class_object), expectedSwfClass=hex(self.pointer(self.base + 0x2c4bbe0)),
                         classState=state.hex(), abstractFlag=bool(state[0x68] & 1) if len(state) > 0x68 else None)
        if name == 'RESOURCE_LOAD_RESULT':
            relevant, detail = self.target(regs['rdi'])
            resource = self.pointer(regs['rdi'] + 0x10)
            extra.update(file=detail, resource=hex(resource), resourceType=self.native_type(resource))
            if relevant and not resource:
                self.failure_dump(detail['fileId'], tid, 'GetOrLoad returned no resource')
            elif relevant and resource:
                self.failure_dump('loaded-' + str(detail['fileId']), tid,
                                  'Target menu resource loaded: preserve texture handles and native state for offline rendering diagnosis')
                if detail['name'].lower().rsplit('\\', 1)[-1] in (
                        'deck_builder.redswf', 'gwint_game.redswf', 'betagwent_board.redswf', 'betagwent_kegop.redswf'):
                    self.render_due.setdefault(detail['fileId'], (time.monotonic() + 5, resource))
        if name in ('ASYNC_BUNDLE_GATE', 'SYNC_BUNDLE_GATE'):
            fid = regs['rdx'] & 0xFFFFFFFF
            extra.update(fileId=fid, chain=self.selected_chain(regs['rcx'], fid))
        if name == 'ASYNC_SELECTED':
            extra.update(selected=bool(regs['rax'] & 255),
                         entry=self.bundle_entry(regs['rsp'] + 0x40),
                         chain=self.selected_chain(regs['rbx'], regs['rsi'] & 0xFFFFFFFF))
        if name == 'ASYNC_IMPLEMENTATION_CALL':
            method = self.pointer(self.pointer(regs['rcx']) + 8)
            extra.update(method=hex(method), entry=self.bundle_entry(regs['rsp'] + 0x40),
                         bundleType=self.native_type(regs['rcx']),
                         bundleMemory=self.memory(regs['rcx'], 2048).hex())
            if self.base <= method < self.base + self.manifest['imageSize']:
                self.add_point('DYNAMIC_ASYNC_IMPLEMENTATION', method)
                self.record('DYNAMIC_METHOD_CODE', tid, address=hex(method), rva=hex(method - self.base),
                            bytes=self.expected_bytes(method).hex())
        if name == 'DYNAMIC_ASYNC_IMPLEMENTATION':
            extra.update(entry=self.bundle_entry(regs['rdx']),
                         bundleMemory=self.memory(regs['rcx'], 4096).hex(),
                         taskOutPointer=hex(regs['r9']))
        if name == 'ASYNC_IMPLEMENTATION_RESULT':
            extra.update(status=regs['rax'] & 0xFFFFFFFF,
                         entry=self.bundle_entry(regs['rsp'] + 0x40), task=hex(self.pointer(regs['rdi'])))
        if name == 'ASYNC_REQUEST_RESULT':
            relevant, detail = self.target(regs['rbx'])
            task = self.pointer(regs['rbp'] - 0x51)
            extra.update(status=regs['rax'] & 0xFFFFFFFF, file=detail, task=hex(task),
                         taskType=self.native_type(task), taskMemory=self.memory(task, 2048).hex())
            if relevant and (regs['rax'] & 0xFFFFFFFF) == 2:
                self.failure_dump(detail['fileId'], tid, 'Async reader request returned failure status 2')
        if name == 'ASYNC_TASK_RESULT':
            extra.update(status=regs['rax'] & 0xFFFFFFFF,
                         task=hex(regs['r12']), taskType=self.native_type(regs['r12']),
                         taskMemory=self.memory(regs['r12'], 2048).hex(),
                         reader=hex(self.pointer(regs['rbp'] - 0x61)))
        if name == 'BUNDLE_READER':
            extra.update(path=self.native_string(regs['rcx'] + 0x30), entry=self.bundle_entry(regs['r9']))
        if name == 'PHYSICAL_OPEN_RESULT':
            extra.update(path=self.native_string(regs['rsi']), opened=bool(regs['rax'] & 255))
        if name == 'CR2W_HEADER':
            extra.update(success=bool(regs['rax'] & 255),
                         header=self.memory(regs['rsp'] + 0x20, 160).hex(),
                         tables=self.memory(regs['rdi'], 84).hex())
        self.detailed(name, tid, regs, **extra)

    def on_breakpoint(self, tid, address):
        point = self.code_points.get(address)
        if not point or not point['enabled']:
            return False
        handle = self.threads[tid]
        storage, context = self.context(handle)
        # Restore the displaced instruction before executing it exactly once.
        self.write_code(address, point['original'])
        C.c_uint64.from_address(context + 248).value = address
        if not self.k.SetThreadContext(handle, context):
            raise C.WinError(C.get_last_error())
        self.point_hit(point['name'], tid, self.registers(context))
        if self.cancel_requested:
            return True
        # Do not suspend other threads across ContinueDebugEvent. Two queued
        # breakpoint events can otherwise suspend each other's stepping thread
        # and deadlock the resource workers. During this small unpatched window
        # another thread may pass without a trace event; execution stays intact.
        self.steps[tid] = dict(address=address)
        C.c_uint32.from_address(context + 68).value |= 0x100
        if not self.k.SetThreadContext(handle, context):
            raise C.WinError(C.get_last_error())
        return True

    def on_step(self, tid):
        step = self.steps.pop(tid, None)
        if not step:
            return False
        storage, context = self.context(self.threads[tid])
        C.c_uint32.from_address(context + 68).value &= ~0x100
        point = self.code_points.get(step['address'])
        if point and point['enabled'] and not any(
                pending['address'] == step['address'] for pending in self.steps.values()):
            self.write_code(step['address'], b'\xcc')
        if not self.k.SetThreadContext(self.threads[tid], context):
            raise C.WinError(C.get_last_error())
        return True

    def cleanup(self):
        suspended = []
        if not self.exited:
            for tid, handle in self.threads.items():
                if self.k.SuspendThread(handle) != 0xFFFFFFFF:
                    suspended.append(handle)
            self.restore_code()
            for tid, handle in self.threads.items():
                try:
                    storage, context = self.context(handle)
                    C.c_uint32.from_address(context + 68).value &= ~0x100
                    if self.event_exception and self.event_exception[0] == tid:
                        address = self.event_exception[1]
                        if address in self.code_points and C.c_uint64.from_address(context + 248).value == address + 1:
                            C.c_uint64.from_address(context + 248).value = address
                    self.k.SetThreadContext(handle, context)
                except OSError:
                    pass
            if self.active_event:
                self.k.ContinueDebugEvent(*self.active_event, DBG_CONTINUE)
                self.active_event = None
            for handle in suspended:
                self.k.ResumeThread(handle)
            if not self.k.DebugActiveProcessStop(self.process.pid):
                self.record('CLEANUP_ERROR', 0, error=str(C.get_last_error()))
        else:
            # The address space no longer exists after EXIT_PROCESS.
            self.restore_verified = True
        for handle in self.threads.values():
            self.k.CloseHandle(handle)
        self.log.close()

    def protect_console_close(self):
        # Windows gives a console-close handler only a short grace period.
        # Request detach in the debugger thread, where its debug events belong.
        prototype = C.WINFUNCTYPE(C.c_int, C.c_uint32)
        @prototype
        def handler(event):
            if event not in (0, 1, 2, 5, 6):
                return False
            self.cancel_requested = True
            self.cleanup_done.wait(4)
            return True
        self.k.SetConsoleCtrlHandler.argtypes = [prototype, C.c_int]
        self.k.SetConsoleCtrlHandler.restype = C.c_int
        if not self.k.SetConsoleCtrlHandler(handler, True):
            raise C.WinError(C.get_last_error())
        self.console_handler = handler

    def run(self, timeout=1800):
        self.k.DebugSetProcessKillOnExit(False)
        try:
            if not self.self_test:
                self.protect_console_close()
            while not self.exited:
                if self.cancel_requested:
                    self.record('DETACH_REQUESTED', 0)
                    break
                if time.monotonic() - self.started > timeout:
                    self.timed_out = True
                    break
                if not self.self_test and msvcrt.kbhit() and msvcrt.getwch().lower() == 'q':
                    self.cancel_requested = True
                    continue
                if len(self.dumped) < 4 and not self.render_break_pending and any(
                        due <= time.monotonic() for key, (due, resource) in self.render_due.items()
                        if 'rendered-' + str(key) not in self.dumped):
                    if not self.k.DebugBreakProcess(int(self.process._handle)):
                        raise C.WinError(C.get_last_error())
                    self.render_break_pending = True
                event = C.create_string_buffer(176)
                if not self.k.WaitForDebugEvent(event, 200):
                    if time.monotonic() - self.started > timeout:
                        self.timed_out = True
                        break
                    continue
                data = event.raw
                kind, pid, tid = struct.unpack_from('<3I', data)
                self.active_event, self.event_exception = (pid, tid), None
                status = DBG_CONTINUE
                if kind == 3:
                    hfile, hprocess, hthread, self.base = struct.unpack_from('<4Q', data, 16)
                    self.threads[tid] = hthread
                    if hfile:
                        self.k.CloseHandle(hfile)
                    if not self.self_test:
                        self.install_points()
                elif kind == 2:
                    self.threads[tid] = struct.unpack_from('<Q', data, 16)[0]
                elif kind == 4:
                    step = self.steps.pop(tid, None)
                    if step and not any(p['address'] == step['address'] for p in self.steps.values()):
                        point = self.code_points[step['address']]
                        if point['enabled']:
                            self.write_code(step['address'], b'\xcc')
                    handle = self.threads.pop(tid, None)
                    if handle:
                        self.k.CloseHandle(handle)
                elif kind == 5:
                    self.exited = True
                    self.record('PROCESS_EXIT', tid, code=struct.unpack_from('<I', data, 16)[0])
                elif kind == 6:
                    hfile = struct.unpack_from('<Q', data, 16)[0]
                    if hfile:
                        self.k.CloseHandle(hfile)
                elif kind == 8:
                    address, wide, length = struct.unpack_from('<QHH', data, 16)
                    text = self.memory(address, min(length * (2 if wide else 1), 65536)).decode(
                        'utf-16le' if wide else 'utf8', errors='replace').rstrip('\0')
                    if self.self_test and text.startswith('FULLTRACE_POINTS='):
                        for point in json.loads(text.split('=', 1)[1]):
                            self.add_point(point['name'], point['address'], point['signature'])
                    elif self.self_test and text == 'FULLTRACE_RESTORE':
                        self.restore_code()
                        assert self.restore_verified
                    else:
                        self.record('OUTPUT_DEBUG_STRING', tid, message=text)
                elif kind == 1:
                    code = struct.unpack_from('<I', data, 16)[0]
                    address = struct.unpack_from('<Q', data, 32)[0]
                    self.event_exception = (tid, address)
                    if code == 0x80000003 and self.on_breakpoint(tid, address):
                        pass
                    elif code == 0x80000004 and self.on_step(tid):
                        pass
                    elif code == 0x80000003 and self.render_break_pending:
                        self.render_break_pending = False
                        for key, (due, resource) in list(self.render_due.items()):
                            if due > time.monotonic() or 'rendered-' + str(key) in self.dumped:
                                continue
                            self.record('RENDER_SNAPSHOT', tid, menuFileId=key, resource=hex(resource),
                                        resourceType=self.native_type(resource),
                                        resourceBytes=self.memory(resource, 512).hex())
                            self.failure_dump('rendered-' + str(key), tid,
                                              'Five seconds after menu load: capture actual GFx images and GPU texture state')
                    elif code != 0x80000003:
                        status = DBG_NOT_HANDLED
                        if not struct.unpack_from('<I', data, 168)[0]:
                            self.record('UNHANDLED_EXCEPTION', tid, code=hex(code), address=hex(address))
                            self.failure_dump('exception', tid, 'Unhandled exception')
                if not self.k.ContinueDebugEvent(pid, tid, status):
                    raise C.WinError(C.get_last_error())
                self.active_event = self.event_exception = None
        finally:
            try:
                self.cleanup()
            finally:
                self.cleanup_done.set()
                if self.console_handler:
                    self.k.SetConsoleCtrlHandler(self.console_handler, False)
        return dict(exited=self.exited, timedOut=self.timed_out, events=len(self.hits),
                    counts={k: self.hits.count(k) for k in sorted(set(self.hits))},
                    softwareBreakpoints=len(self.code_points), dumps=len(self.dumped),
                    cancelled=self.cancel_requested, otherThreadsSuspendedForStep=False,
                    originalInstructionsRestored=self.restore_verified)


def self_test():
    out = OUTPUT / ('self-test-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    out.mkdir(parents=True)
    child = r'''
import ctypes as C,json,sys,threading,time
ATTACH_WAIT
k=C.WinDLL('kernel32');k.VirtualAlloc.restype=C.c_void_p
k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,C.c_uint32,C.c_uint32]
address=k.VirtualAlloc(None,4096,0x3000,0x40);assert address
code=b'\xb8\x2a\0\0\0\xc3'+b'\x90'*10
C.memmove(address,code*5,80)
points=[dict(name='POINT_'+str(i),address=address+i*16,signature=code[:8].hex()) for i in range(5)]
k.OutputDebugStringA(('FULLTRACE_POINTS='+json.dumps(points[:4])).encode())
text=C.create_string_buffer(b'FULL_TRACE_SELF_TEST')
def call():
 for point in points:assert C.CFUNCTYPE(C.c_int,C.c_void_p)(point['address'])(C.addressof(text))==42
call();t=threading.Thread(target=call);t.start();t.join()
STRESS
RESTORE
time.sleep(SLEEP)
assert C.string_at(address,80)==code*5
call()
'''
    stress = '''
barrier=threading.Barrier(12)
def concurrent():
 barrier.wait()
 for i in range(20):call()
threads=[threading.Thread(target=concurrent) for _ in range(12)]
for t in threads:t.start()
for t in threads:t.join(20)
assert not any(t.is_alive() for t in threads), 'Concurrent resource callers deadlocked'
'''
    for label, restore, delay, timeout in [('normal', 'k.OutputDebugStringA(b"FULLTRACE_RESTORE")', 0, 30),
                                           ('detach', 'pass', 2, 0.5),
                                           ('concurrent-attach', 'k.OutputDebugStringA(b"FULLTRACE_RESTORE")', 0, 60),
                                           ('late-snapshot', 'pass', 1, 0.5)]:
        destination = out / label
        destination.mkdir()
        attached = label == 'concurrent-attach'
        code = child.replace('RESTORE', restore).replace('SLEEP', str(delay)).replace(
            'STRESS', stress if attached else 'pass').replace('ATTACH_WAIT', 'sys.stdin.readline()' if attached else 'pass')
        process = subprocess.Popen([sys.executable, '-c', code], stdin=subprocess.PIPE,
                                   creationflags=subprocess.CREATE_NO_WINDOW | (0 if attached else 2))
        trace = FullTrace(process, destination, {}, self_test=True)
        trace.test_late_snapshot = label == 'late-snapshot'
        if attached:
            assert trace.k.DebugActiveProcess(process.pid), C.get_last_error()
            process.stdin.write(b'go\n')
            process.stdin.flush()
        result = trace.run(timeout)
        process.wait(timeout=8)
        assert process.returncode == 0 and result['originalInstructionsRestored'], result
        assert result['timedOut'] == (label in ('detach', 'late-snapshot'))
        assert all(result['counts'].get('POINT_' + str(i), 0) >= 2 for i in range(5)), result
        assert not result['otherThreadsSuspendedForStep']
        if label == 'late-snapshot':
            assert result['counts'].get('RENDER_SNAPSHOT') == 1, result
            assert (destination / 'state-rendered-self-test.dmp').exists()
        (destination / 'result.json').write_text(json.dumps(result, indent=2), 'utf8')
    destination = out / 'interruption'
    destination.mkdir()
    code = child.replace('RESTORE', 'pass').replace('SLEEP', '0').replace('STRESS', 'pass').replace('ATTACH_WAIT', 'pass')
    process = subprocess.Popen([sys.executable, '-c', code],
                               creationflags=2 | subprocess.CREATE_NO_WINDOW)
    trace = FullTrace(process, destination, {}, self_test=True)
    trace.fail_self_test = True
    try:
        trace.run(20)
        raise AssertionError('Expected interruption did not occur')
    except RuntimeError as error:
        assert str(error) == 'Expected self-test interruption', error
    process.wait(timeout=8)
    assert process.returncode == 0 and trace.restore_verified
    destination = out / 'console-cancel'
    destination.mkdir()
    code = child.replace('RESTORE', 'pass').replace('SLEEP', '2').replace(
        'STRESS', stress).replace('ATTACH_WAIT', 'pass')
    process = subprocess.Popen([sys.executable, '-c', code], creationflags=2 | subprocess.CREATE_NO_WINDOW)
    trace = FullTrace(process, destination, {}, self_test=True)
    trace.protect_console_close()
    timer = threading.Timer(0.1, lambda: trace.console_handler(0))
    timer.start()
    result = trace.run(20)
    timer.join(5)
    process.wait(timeout=8)
    assert process.returncode == 0 and result['cancelled'] and trace.restore_verified, result
    (destination / 'result.json').write_text(json.dumps(result, indent=2), 'utf8')
    print('Full trace self-test passed: late attach, 12 concurrent callers / 1,200 calls, software/dynamic points, minidump, original bytes, exit, detach, console cancellation and interrupted callback. Game not launched.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    check = subprocess.run(['powershell', '-NoProfile', '-Command',
                            '@(Get-Process witcher3 -ErrorAction SilentlyContinue).Count'],
                           capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if int(check.stdout.strip() or '0'):
        raise RuntimeError('Сначала закройте игру, затем запустите сборщик.')
    manifest = json.loads(MANIFEST.read_text('utf8'))
    exe = GAME / 'bin/x64/witcher3.exe'
    if digest(exe) != manifest['executableSha256']:
        raise RuntimeError('Exe отличается от проверенной 1.32.')
    out = OUTPUT / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    out.mkdir(parents=True)
    if shutil.disk_usage(out).free < 16 * 1024**3:
        raise RuntimeError('Для полного локального снимка нужно 16 ГиБ свободного места.')
    before = snapshot()
    (out / 'installed-before.json').write_text(json.dumps(before, ensure_ascii=False, indent=2), 'utf8')
    (out / 'trace-manifest.json').write_bytes(MANIFEST.read_bytes())
    source_inventory = []
    for mod in (GAME / 'Mods').iterdir():
        if not mod.is_dir():
            continue
        for path in sorted(mod.rglob('*')):
            if path.is_file():
                source_inventory.append(dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path)))
    caches = [dict(path=str(p), bytes=p.stat().st_size, sha256=digest(p))
              for p in (GAME / 'content/content0').glob('*.redscripts')]
    (out / 'all-installed-files.json').write_text(json.dumps(dict(modFiles=source_inventory, scriptCaches=caches), indent=2), 'utf8')
    (out / 'installed-gui-dlc.json').write_text(json.dumps(before.get('classicGuiDLC', []), indent=2), 'utf8')
    for name in ('resources.ini', 'rendering.ini', 'debug.ini'):
        shutil.copy2(GAME / 'bin/config/base' / name, out / name)
    print('Папка логов:', out, flush=True)
    started = time.time()
    # Load the world with no debugger and no breakpoints whatsoever. The user
    # explicitly arms diagnostics only after their save has finished loading.
    process = subprocess.Popen([str(exe), '-debugscripts'], cwd=exe.parent)
    print('Игра запущена обычным способом, сборщик пока НЕ подключён.', flush=True)
    input('Загрузите сохранение до управления Геральтом. Затем вернитесь сюда и нажмите Enter: ')
    if process.poll() is not None:
        raise RuntimeError('Игра уже закрыта; диагностика не подключалась.')
    trace = FullTrace(process, out, manifest)
    trace.record('USER_ARMED_AFTER_WORLD_LOAD', 0, process=process.pid)
    print('Подключаю диагностику. Теперь можно вернуться в игру и открыть колоды.', flush=True)
    print('Если можно вернуться в мир, попробуйте NPC-гвинт в этом же запуске.', flush=True)
    print('Снимок памяти сохранится автоматически; во время записи игра будет на паузе.', flush=True)
    print('Не закрывайте после первого снимка: оставьте колоды на экране до второго снимка rendered.', flush=True)
    print('Затем проверьте редактор и NPC-партию; в бою тоже подождите снимка rendered.', flush=True)
    print('После этого закройте игру. Q в этом окне отключает сбор без закрытия игры.', flush=True)
    if not trace.k.DebugActiveProcess(process.pid):
        trace.log.close()
        raise C.WinError(C.get_last_error())
    error = None
    try:
        result = trace.run()
    except BaseException:
        error = traceback.format_exc()
        (out / 'collector-error.txt').write_text(error, 'utf8')
        result = dict(error=error, originalInstructionsRestored=trace.restore_verified)
    log = Path.home() / 'Documents/The Witcher 3/scriptslog.txt'
    if log.exists() and log.stat().st_mtime >= started - 2:
        shutil.copy2(log, out / 'scriptslog.txt')
    result.update(executableFileUnchanged=digest(exe) == manifest['executableSha256'],
                  installedFilesUnchanged=before == snapshot(), gameFilesWritten=False,
                  processMemoryTemporarilyInstrumented=True, localMemoryDumps=True,
                  attachedOnlyAfterUserConfirmedWorldLoad=True)
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
    print('Готово. Логи и снимки памяти сохранены:', out, flush=True)
    if error:
        print('Сбор прерван ошибкой; подробности сохранены в collector-error.txt.', flush=True)


if __name__ == '__main__':
    main()

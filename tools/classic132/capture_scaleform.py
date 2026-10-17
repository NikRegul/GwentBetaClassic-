"""User-started diagnostic of suppressed Classic GFx errors and file opens.

Observes only its own child. Four hardware execute breakpoints read state;
no WriteProcessMemory, code patch, game-file or save-file writes are used.
Never import this module to start a game: entry is explicitly under main().
"""
import argparse
import ctypes as C
from datetime import datetime
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time

from capture_menu_log import GAME, snapshot, digest

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'BetaGwent/build/classic132-scaleform-feedback'
MANIFEST = ROOT / 'BetaGwent/build/classic081-complete-audit/trace-points.json'
DBG_CONTINUE = 0x10002
DBG_NOT_HANDLED = 0x80010001


class Trace:
    def __init__(self, process, out, points, self_test=False):
        self.process, self.out, self.points = process, out, points
        self.self_test = self_test
        self.k = C.WinDLL('kernel32', use_last_error=True)
        for name, arguments, result in [
            ('WaitForDebugEvent', [C.c_void_p, C.c_uint32], C.c_int),
            ('ContinueDebugEvent', [C.c_uint32, C.c_uint32, C.c_uint32], C.c_int),
            ('ReadProcessMemory', [C.c_void_p, C.c_void_p, C.c_void_p, C.c_size_t, C.POINTER(C.c_size_t)], C.c_int),
            ('GetThreadContext', [C.c_void_p, C.c_void_p], C.c_int),
            ('SetThreadContext', [C.c_void_p, C.c_void_p], C.c_int),
            ('CloseHandle', [C.c_void_p], C.c_int),
            ('SuspendThread', [C.c_void_p], C.c_uint32),
            ('ResumeThread', [C.c_void_p], C.c_uint32),
            ('DebugSetProcessKillOnExit', [C.c_int], C.c_int),
            ('DebugActiveProcessStop', [C.c_uint32], C.c_int),
        ]:
            fn = getattr(self.k, name)
            fn.argtypes, fn.restype = arguments, result
        self.threads, self.original, self.pending, self.hits = {}, {}, {}, []
        self.resource_files = {}
        self.thread_teb, self.large_reads = {}, {}
        self.point_overrides, self.return_values = {}, {}
        self.base = 0
        self.active_event = None
        self.exited = False
        self.timed_out = False
        self.started = time.monotonic()
        self.log = (out / 'scaleform.jsonl').open('w', encoding='utf8')

    def memory(self, address, size):
        if not address or not 0 < size <= 65536:
            return b''
        buf, read = C.create_string_buffer(size), C.c_size_t()
        self.k.ReadProcessMemory(int(self.process._handle), address, buf, size, C.byref(read))
        return buf.raw[:read.value]

    def ascii(self, address, limit=2048):
        return self.memory(address, limit).split(b'\0')[0].decode('utf8', errors='replace')

    def pointer(self, address):
        raw = self.memory(address, 8)
        return struct.unpack('<Q', raw)[0] if len(raw) == 8 else 0

    def native_string(self, address):
        raw = self.memory(address, 12)
        if len(raw) != 12:
            return ''
        pointer, length = struct.unpack('<QI', raw)
        if not 0 < length <= 4096:
            return ''
        return self.memory(pointer, length * 2).decode('utf-16le', errors='replace').rstrip('\0')

    def native_type(self, address):
        vtable = self.pointer(address)
        locator = self.pointer(vtable - 8) if vtable >= 8 else 0
        raw = self.memory(locator, 24)
        if len(raw) != 24:
            return None
        signature, offset, ctor_offset, descriptor, hierarchy, self_rva = struct.unpack('<6I', raw)
        if signature != 1:
            return None
        return self.ascii(locator - self_rva + descriptor + 16, 256)

    def bundle_entry(self, address):
        raw = self.memory(address, 24)
        if len(raw) != 24:
            return None
        fid, bid, offset, packed, memory, compression = struct.unpack('<IH2x4I', raw)
        return dict(fileId=fid, bundleId=bid, offset=offset, packedBytes=packed,
                    memoryBytes=memory, compression=compression)

    def effective_point(self, tid, slot):
        return self.point_overrides.get(tid, {}).get(slot, self.points[slot])

    def observe_return(self, tid, slot, context, name, values):
        rsp = C.c_uint64.from_address(context + 152).value
        address = self.pointer(rsp)
        if not address:
            return
        self.point_overrides.setdefault(tid, {})[slot] = dict(name=name, address=address)
        self.return_values[(tid, slot)] = values

    def finish_return(self, tid, slot):
        self.point_overrides.get(tid, {}).pop(slot, None)
        return self.return_values.pop((tid, slot), {})

    def file_details(self, address):
        raw = self.memory(address, 72)
        return dict(fileObject=hex(address), name=self.native_string(address + 0x18),
                    flags=raw[0x28] if len(raw) > 0x28 else None,
                    fileId=struct.unpack_from('<I', raw, 0x40)[0] if len(raw) >= 0x44 else None)

    def selected_chain(self, manager, fid):
        # Layout verified from CMetadataStore::SelectEntry (0xc18b0).
        metadata = self.pointer(manager + 0x10)
        prefix = self.memory(metadata + 0x30, 24)
        result = dict(metadata=hex(metadata), entries=[])
        if len(prefix) != 24:
            return result
        files, file_count, entries, entry_count = struct.unpack('<QIQI', prefix)
        result.update(fileCount=file_count, entryCount=entry_count)
        if not 0 < fid < file_count:
            return result
        raw = self.memory(files + fid * 32, 32)
        if len(raw) != 32:
            return result
        info = struct.unpack('<8I', raw)
        result['fileInfo'] = dict(nameOffset=info[0], packedBytes=info[2], memoryBytes=info[3],
                                  firstEntry=info[4], compression=info[5], bufferId=info[6], hasBuffer=info[7])
        eid, visited = info[4], set()
        active = self.pointer(manager + 0x18)
        while 0 < eid < entry_count and eid not in visited and len(visited) < 12:
            visited.add(eid)
            raw = self.memory(entries + eid * 20, 20)
            if len(raw) != 20:
                break
            file_id, bid, offset, size, nxt = struct.unpack('<5I', raw)
            bitmap = self.memory(active + (bid // 32) * 4, 4) if bid < 65536 else b''
            loaded = bool(struct.unpack('<I', bitmap)[0] & (1 << (bid % 32))) if len(bitmap) == 4 else None
            result['entries'].append(dict(entry=eid, fileId=file_id, bundleId=bid,
                                           offset=offset, packedBytes=size, nextEntry=nxt, bundleActive=loaded))
            eid = nxt
        return result

    def context(self, handle):
        storage = C.create_string_buffer(1248)
        address = (C.addressof(storage) + 15) & ~15
        C.c_uint32.from_address(address + 48).value = 0x100013
        if not self.k.GetThreadContext(handle, address):
            raise C.WinError(C.get_last_error())
        return storage, address

    def arm(self, tid):
        if not self.points:
            return
        handle = self.threads[tid]
        storage, context = self.context(handle)
        if tid not in self.original:
            self.original[tid] = C.string_at(context + 72, 48)
        for i in range(len(self.points)):
            point = self.effective_point(tid, i)
            address = point['address'] if 'address' in point else self.base + point['rva']
            C.c_uint64.from_address(context + 72 + i * 8).value = address
        C.c_uint64.from_address(context + 104).value = 0
        C.c_uint64.from_address(context + 112).value = 0x55
        if not self.k.SetThreadContext(handle, context):
            raise C.WinError(C.get_last_error())

    def record(self, kind, tid, **values):
        event = dict(seconds=round(time.monotonic() - self.started, 3), kind=kind, thread=tid, **values)
        self.log.write(json.dumps(event, ensure_ascii=False) + '\n')
        self.log.flush()
        self.hits.append(kind)

    def breakpoint(self, tid):
        handle = self.threads[tid]
        storage, context = self.context(handle)
        dr6 = C.c_uint64.from_address(context + 104).value
        hit = dr6 & 15
        if not hit:
            return False
        def reg(offset):
            return C.c_uint64.from_address(context + offset).value
        for i in range(len(self.points)):
            if not hit & (1 << i):
                continue
            point = self.effective_point(tid, i)
            name = point['name']
            if self.self_test:
                if name == 'SELF_RETURN':
                    self.record(name, tid, **self.finish_return(tid, i))
                else:
                    self.record(name, tid, text=self.ascii(reg(128)))
                    if name == 'POINT_0':
                        self.observe_return(tid, i, context, 'SELF_RETURN', dict(returnObserved=True))
            elif name == 'FILE_OPEN':
                path = self.ascii(reg(136))
                self.pending.setdefault(tid, []).append(path)
                caller = self.memory(reg(152), 8)
                self.record(name, tid, path=path, caller=hex(struct.unpack('<Q', caller)[0]) if len(caller) == 8 else None)
            elif name == 'RESOURCE_RESOLVED':
                self.record(name, tid, path=(self.pending.get(tid) or [None])[-1],
                            resourceFound=bool(reg(168)))
            elif name == 'FILE_RESULT':
                stack = self.pending.get(tid, [])
                self.record(name, tid, path=stack.pop() if stack else None, opened=bool(reg(176)))
            elif name == 'GFX_MESSAGE':
                # Audited point after vsnprintf and newline stripping. The
                # retail function otherwise destroys this message silently.
                self.record(name, tid, message=self.ascii(reg(152) + 0x50))
            elif name == 'DEPOT_LOOKUP':
                # After CResourceDepot::FindFile; RBP still owns the input
                # String, RAX is the resulting file object before loading.
                path = self.native_string(reg(160))
                if 'betagwent' in path.lower() or '\\gwint\\' in path.lower():
                    file_object = reg(120)
                    if file_object:
                        self.resource_files[file_object] = path
                    self.record(name, tid, path=path, fileFound=bool(file_object),
                                fileObject=hex(file_object), fileType=self.native_type(file_object))
            elif name == 'RESOURCE_LOAD_RESULT':
                # After the synchronous GetOrLoad, before its handle is read.
                file_object = reg(176)
                if file_object in self.resource_files:
                    resource_object = self.pointer(file_object + 0x10)
                    self.record(name, tid, path=self.resource_files[file_object],
                                resourceObject=hex(resource_object), loaded=bool(resource_object),
                                resourceType=self.native_type(resource_object),
                                fileState=self.memory(file_object, 96).hex())
            elif name == 'CR2W_HEADER':
                # At ReadHeader's common return: AL is success, the original
                # 160-byte header is still at RSP+0x20. RDI owns read tables.
                header = self.memory(reg(152) + 0x20, 160)
                table_object = reg(176)
                tables = self.memory(table_object, 84)
                root_class = None
                if len(tables) >= 48:
                    strings_pointer, strings_size = struct.unpack_from('<QI', tables, 0)
                    names_pointer, names_count = struct.unpack_from('<QI', tables, 12)
                    exports_pointer, exports_count = struct.unpack_from('<QI', tables, 36)
                    first_export = self.memory(exports_pointer, 24) if exports_count else b''
                    if len(first_export) == 24:
                        name_id = struct.unpack_from('<H', first_export)[0]
                        if name_id < names_count:
                            row = self.memory(names_pointer + name_id * 8, 8)
                            if len(row) == 8:
                                string_offset = struct.unpack_from('<I', row)[0]
                                if string_offset < strings_size:
                                    root_class = self.ascii(strings_pointer + string_offset, 256)
                success = bool(reg(120) & 255)
                if root_class in ('CSwfResource', 'CMenuResource') or not success:
                    self.record(name, tid, success=success, rootClass=root_class,
                                header=header.hex(), readerType=self.native_type(reg(144)),
                                tables=tables.hex())
            elif name == 'BUNDLE_READER':
                entry = self.bundle_entry(reg(192))  # R9: selected runtime entry.
                path = self.native_string(reg(128) + 0x30)
                if entry and (entry['packedBytes'] > 4 * 1024 * 1024 or
                              entry['fileId'] == 26654 or 'modbetagwent' in path.lower()):
                    self.large_reads[tid] = dict(path=path, entry=entry)
                    self.record(name, tid, path=path, entry=entry)
            elif name == 'LARGE_RAW_RESULT':
                entry = self.bundle_entry(reg(168))  # RSI remains the entry.
                if entry and entry['packedBytes'] > 4 * 1024 * 1024:
                    prior = self.large_reads.get(tid, {})
                    self.record(name, tid, path=prior.get('path'), entry=entry,
                                readerOpened=bool(reg(120)))
            elif name == 'PHYSICAL_OPEN_RESULT':
                path = self.native_string(reg(168))
                if 'mods' in path.lower() or tid in self.large_reads:
                    teb = self.thread_teb.get(tid, 0)
                    error = self.memory(teb + 0x68, 4) if teb else b''
                    self.record(name, tid, path=path, opened=bool(reg(120) & 255),
                                lastError=struct.unpack('<I', error)[0] if len(error) == 4 else None)
            elif name in ('RESOURCE_GATE', 'RESOURCE_CLASS'):
                file_object = reg(128) if name == 'RESOURCE_GATE' else reg(136)
                detail = self.file_details(file_object)
                if detail['fileId'] == 26654 or 'betagwent' in detail['name'].lower():
                    self.record(name, tid, **detail)
                    self.observe_return(tid, i, context, name + '_RETURN',
                                        dict(fileObjectAddress=file_object, **detail))
            elif name in ('RESOURCE_GATE_RETURN', 'RESOURCE_CLASS_RETURN'):
                detail = self.finish_return(tid, i)
                file_object = detail.pop('fileObjectAddress', 0)
                after = self.file_details(file_object)
                if name == 'RESOURCE_CLASS_RETURN':
                    class_object = reg(120)
                    expected_class = self.pointer(self.base + 0x2c4bbe0)
                    class_state = self.memory(class_object, 112)
                    self.record(name, tid, classFound=bool(class_object),
                                classObject=hex(class_object), classState=class_state.hex(),
                                expectedSwfClass=hex(expected_class),
                                classMatchesExpectedSwf=bool(class_object and class_object == expected_class),
                                abstractFlag=bool(class_state[0x68] & 1) if len(class_state) > 0x68 else None,
                                before=detail, after=after)
                else:
                    self.record(name, tid, startLoading=bool(reg(120) & 255), before=detail, after=after)
            elif name == 'BUNDLE_GATE':
                fid = reg(136) & 0xFFFFFFFF
                if fid == 26654:
                    chain = self.selected_chain(reg(128), fid)
                    self.record(name, tid, fileId=fid, **chain)
                    self.observe_return(tid, i, context, 'BUNDLE_GATE_RETURN', dict(fileId=fid))
            elif name == 'BUNDLE_GATE_RETURN':
                self.record(name, tid, readerFound=bool(reg(120)), readerType=self.native_type(reg(120)),
                            **self.finish_return(tid, i))
        for slot in range(len(self.points)):
            point = self.effective_point(tid, slot)
            address = point['address'] if 'address' in point else self.base + point['rva']
            C.c_uint64.from_address(context + 72 + slot * 8).value = address
        C.c_uint64.from_address(context + 104).value = 0
        C.c_uint32.from_address(context + 68).value |= 1 << 16  # RF: execute the observed instruction once.
        if not self.k.SetThreadContext(handle, context):
            raise C.WinError(C.get_last_error())
        return True

    def cleanup(self):
        # On an interrupted collector, restore original hardware debug state
        # before detaching. Never terminate the user's game on a timeout.
        suspended = []
        if not self.exited:
            for tid, handle in self.threads.items():
                if self.k.SuspendThread(handle) != 0xFFFFFFFF:
                    suspended.append(handle)
                    if tid in self.original:
                        try:
                            storage, context = self.context(handle)
                            C.memmove(context + 72, self.original[tid], 48)
                            if not self.k.SetThreadContext(handle, context):
                                raise C.WinError(C.get_last_error())
                        except OSError as error:
                            self.record('CLEANUP_ERROR', tid, error=str(error))
            if self.active_event:
                self.k.ContinueDebugEvent(*self.active_event, DBG_CONTINUE)
                self.active_event = None
            # DebugActiveProcessStop closes the debug-event thread handles.
            # Resume after restoring every thread, while these handles are
            # still valid, then detach immediately.
            for handle in suspended:
                self.k.ResumeThread(handle)
            detached = self.k.DebugActiveProcessStop(self.process.pid)
            if not detached:
                self.record('CLEANUP_ERROR', 0, error='DebugActiveProcessStop failed: ' + str(C.get_last_error()))
        for handle in self.threads.values():
            self.k.CloseHandle(handle)
        self.log.close()

    def run(self, timeout=1800):
        self.k.DebugSetProcessKillOnExit(False)
        try:
            while not self.exited:
                event = C.create_string_buffer(176)
                if not self.k.WaitForDebugEvent(event, 200):
                    if time.monotonic() - self.started >= timeout:
                        self.timed_out = True
                        break
                    continue
                data = event.raw
                kind, pid, tid = struct.unpack_from('<3I', data)
                self.active_event = (pid, tid)
                status = DBG_CONTINUE
                if kind == 3:
                    hfile, hprocess, hthread, self.base = struct.unpack_from('<4Q', data, 16)
                    self.threads[tid] = hthread
                    self.thread_teb[tid] = struct.unpack_from('<Q', data, 64)[0]
                    if hfile:
                        self.k.CloseHandle(hfile)
                    if not self.self_test:
                        for point in self.points:
                            signature = bytes.fromhex(point['signature'])
                            if self.memory(self.base + point['rva'], len(signature)) != signature:
                                raise RuntimeError('Native loader signature differs: ' + point['name'])
                    self.arm(tid)
                elif kind == 2:
                    self.threads[tid] = struct.unpack_from('<Q', data, 16)[0]
                    self.thread_teb[tid] = struct.unpack_from('<Q', data, 24)[0]
                    self.arm(tid)
                elif kind == 4:
                    handle = self.threads.pop(tid, None)
                    self.original.pop(tid, None)
                    self.pending.pop(tid, None)
                    self.thread_teb.pop(tid, None)
                    self.large_reads.pop(tid, None)
                    self.point_overrides.pop(tid, None)
                    for key in [key for key in self.return_values if key[0] == tid]:
                        self.return_values.pop(key)
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
                    if self.self_test and text.startswith('TRACE_SELFTEST_POINTS='):
                        self.points = json.loads(text.split('=', 1)[1])
                        for thread in self.threads:
                            self.arm(thread)
                    else:
                        self.record('OUTPUT_DEBUG_STRING', tid, message=text)
                elif kind == 1:
                    code = struct.unpack_from('<I', data, 16)[0]
                    if code == 0x80000004 and self.breakpoint(tid):
                        pass
                    elif code != 0x80000003:
                        status = DBG_NOT_HANDLED
                        if not struct.unpack_from('<I', data, 168)[0]:
                            self.record('UNHANDLED_EXCEPTION', tid, code=hex(code),
                                        address=hex(struct.unpack_from('<Q', data, 32)[0]))
                if not self.k.ContinueDebugEvent(pid, tid, status):
                    raise C.WinError(C.get_last_error())
                self.active_event = None
        finally:
            self.cleanup()
        return dict(timedOut=self.timed_out, exited=self.exited,
                    events=len(self.hits), counts={name: self.hits.count(name) for name in sorted(set(self.hits))})


def self_test():
    out = OUTPUT / ('self-test-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    out.mkdir(parents=True)
    child = r'''
import ctypes as C,json,threading
k=C.WinDLL('kernel32');k.VirtualAlloc.restype=C.c_void_p
k.VirtualAlloc.argtypes=[C.c_void_p,C.c_size_t,C.c_uint32,C.c_uint32]
address=k.VirtualAlloc(None,4096,0x3000,0x40)
assert address
C.memmove(address,b'\xc3'+b'\x90'*15+b'\xc3'+b'\x90'*15+b'\xc3'+b'\x90'*15+b'\xc3',49)
points=[dict(name='POINT_'+str(i),address=address+i*16) for i in range(4)]
k.OutputDebugStringA(('TRACE_SELFTEST_POINTS='+json.dumps(points)).encode())
text=C.create_string_buffer(b'HARDWARE_TRACE_SELF_TEST')
def call():
 for point in points:C.CFUNCTYPE(None,C.c_void_p)(point['address'])(C.addressof(text))
call()
t=threading.Thread(target=call);t.start();t.join()
'''
    process = subprocess.Popen([sys.executable, '-c', child], creationflags=2 | subprocess.CREATE_NO_WINDOW)
    trace = Trace(process, out, [], self_test=True)
    result = trace.run(20)
    process.wait(timeout=5)
    records = [json.loads(line) for line in (out / 'scaleform.jsonl').read_text('utf8').splitlines()]
    assert process.returncode == 0 and not result['timedOut']
    for i in range(4):
        hits = [r for r in records if r['kind'] == 'POINT_' + str(i)]
        assert len(hits) == 2 and all(r['text'] == 'HARDWARE_TRACE_SELF_TEST' for r in hits), hits
        assert len({r['thread'] for r in hits}) == 2
    returns = [r for r in records if r['kind'] == 'SELF_RETURN']
    assert len(returns) == 2 and all(r['returnObserved'] for r in returns)
    # Exercise interrupted collection too: the child must survive detachment
    # with its original debug registers and finish normally on its own.
    detach_out = out / 'detach'
    detach_out.mkdir()
    detach_child = child + '\nimport time;time.sleep(2);call()\n'
    process = subprocess.Popen([sys.executable, '-c', detach_child], creationflags=2 | subprocess.CREATE_NO_WINDOW)
    result = Trace(process, detach_out, [], self_test=True).run(0.5)
    process.wait(timeout=6)
    assert result['timedOut'] and not result['exited'] and process.returncode == 0
    assert 'CLEANUP_ERROR' not in (detach_out / 'scaleform.jsonl').read_text('utf8')
    print('Hardware trace self-test passed: four points, dynamic returns, two threads, normal exit and safe detach. Game not launched.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--profile', choices=('scaleform', 'resource', 'bundle', 'gate'), default='scaleform')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    running = subprocess.run(['powershell', '-NoProfile', '-Command',
                              '@(Get-Process witcher3 -ErrorAction SilentlyContinue).Count'],
                             capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if int(running.stdout.strip() or '0'):
        raise RuntimeError('Сначала закройте Witcher 3, затем запустите сборщик.')
    exe = GAME / 'bin/x64/witcher3.exe'
    manifest_path = MANIFEST if args.profile == 'scaleform' else MANIFEST.with_name(args.profile + '-trace-points.json')
    manifest = json.loads(manifest_path.read_text('utf8'))
    if digest(exe) != manifest['executableSha256']:
        raise RuntimeError('Exe отличается от проверенной версии 1.32; сбор остановлен.')
    output = OUTPUT if args.profile == 'scaleform' else OUTPUT.with_name('classic132-' + args.profile + '-feedback')
    out = output / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    out.mkdir(parents=True)
    before = snapshot()
    (out / 'installed-before.json').write_text(json.dumps(before, ensure_ascii=False, indent=2), 'utf8')
    print('Загрузите сохранение и один раз откройте колоды до зависания.', flush=True)
    if args.profile == 'scaleform':
        print('Если колоды открылись, проверьте редактор, выход и запуск партии.', flush=True)
    else:
        print('Для этого сбора достаточно один раз открыть колоды; партию проверять не нужно.', flush=True)
    print('После проверки закройте игру. При зависании — через Диспетчер задач.', flush=True)
    print('Окно сборщика оставьте открытым. Логи:', out, flush=True)
    started = time.time()
    process = subprocess.Popen([str(exe), '-debugscripts'], cwd=exe.parent, creationflags=2)
    result = Trace(process, out, manifest['points']).run()
    log = Path.home() / 'Documents/The Witcher 3/scriptslog.txt'
    if log.exists() and log.stat().st_mtime >= started - 2:
        shutil.copy2(log, out / 'scriptslog.txt')
    result.update(executablePatched=False, gameFilesWritten=False, savesWritten=False,
                  hardwareExecutePoints=4, profile=args.profile, installedFilesUnchanged=before == snapshot())
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf8')
    print('Готово. Логи сохранены:', out, flush=True)


if __name__ == '__main__':
    main()

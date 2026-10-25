"""Run the original 1.32 executable in its script verification/exit mode.

Requires an isolated runtime tree: its bin and content0/scripts are real copies,
and content0 script caches must not be links to the installed game's caches.
"""
import argparse
from contextlib import contextmanager
import ctypes
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import struct
import time
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from build_inputs import CLASSIC_RUNTIME


@contextmanager
def without_store_provider(probe, logs, enabled):
    """Temporarily omit the optional GOG service from the private compile probe."""
    source = probe / 'bin/ddi/GOG.dll'
    backup = logs / 'GOG.dll.disabled'
    if not enabled or not source.exists():
        yield
        return
    if source.is_symlink() or source.stat().st_nlink != 1 or not source.resolve().is_relative_to(probe):
        raise ValueError('Store provider must be a private probe copy')
    source.rename(backup)
    try:
        yield
    finally:
        backup.rename(source)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def wait_with_debug_output(process, timeout, destination, compiler_feedback=False):
    """Read OutputDebugString from our child; never attach to other processes."""
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.WaitForDebugEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
    kernel.ContinueDebugEvent.argtypes = [ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32]
    kernel.ReadProcessMemory.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
                                       ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
    kernel.CloseHandle.argtypes = [ctypes.c_void_p]
    kernel.OpenThread.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
    kernel.OpenThread.restype = ctypes.c_void_p
    kernel.GetThreadContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel.SetThreadContext.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    kernel.WriteProcessMemory.argtypes = kernel.ReadProcessMemory.argtypes
    kernel.FlushInstructionCache.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
    def read_memory(address, size):
        buffer = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t()
        if not kernel.ReadProcessMemory(int(process._handle), address, buffer, size, ctypes.byref(read)) or read.value != size:
            raise RuntimeError('Cannot read own compiler feedback memory')
        return buffer.raw
    def write_memory(address, value):
        buffer = ctypes.create_string_buffer(value)
        written = ctypes.c_size_t()
        if not kernel.WriteProcessMemory(int(process._handle), address, buffer, len(value), ctypes.byref(written)):
            raise RuntimeError('Cannot instrument own compiler return point')
        kernel.FlushInstructionCache(int(process._handle), address, len(value))
    def strings_array(address, count):
        if not 0 <= count <= 10000:
            raise RuntimeError('Unexpected compiler feedback array size')
        result = []
        for i in range(count):
            record = read_memory(address + i * 28, 28)
            line = struct.unpack_from('<I', record)[0]
            values = []
            for offset in (4, 16):
                pointer, length = struct.unpack_from('<QI', record, offset)
                if not 0 <= length <= 65536:
                    raise RuntimeError('Unexpected compiler feedback string length')
                values.append(read_memory(pointer, length * 2).decode('utf-16le', errors='replace').rstrip('\x00') if length else '')
            result.append(f'{values[0]}({line}): {values[1]}')
        return result
    started = time.monotonic()
    timed_out = False
    exit_code = None
    breakpoint = None
    feedback = None
    with destination.open('w', encoding='utf8') as log:
        while exit_code is None:
            event = ctypes.create_string_buffer(176)
            if not kernel.WaitForDebugEvent(event, 200):
                if time.monotonic() - started > timeout and not timed_out:
                    timed_out = True
                    process.kill()
                if time.monotonic() - started > timeout + 10:
                    raise RuntimeError('Native debugger did not receive child exit')
                continue
            data = event.raw
            kind, pid, tid = struct.unpack_from('<III', data)
            status = 0x00010002
            if kind == 8:
                address, unicode, length = struct.unpack_from('<QHH', data, 16)
                size = min(length * (2 if unicode else 1), 1048576)
                buffer = ctypes.create_string_buffer(size)
                read = ctypes.c_size_t()
                if size and kernel.ReadProcessMemory(int(process._handle), address, buffer, size, ctypes.byref(read)):
                    value = buffer.raw[:read.value].decode('utf-16le' if unicode else 'utf8', errors='replace').rstrip('\x00')
                    log.write(value + ('\n' if not value.endswith('\n') else ''))
                    log.flush()
            elif kind == 1:
                exception = struct.unpack_from('<I', data, 16)[0]
                exception_address = struct.unpack_from('<Q', data, 32)[0]
                first_chance = struct.unpack_from('<I', data, 168)[0]
                log.write(f'Exception code=0x{exception:08x} address=0x{exception_address:x} firstChance={first_chance}\n');log.flush()
                if exception == 0x80000003 and breakpoint and exception_address == breakpoint:
                    thread = kernel.OpenThread(0x1F03FF, False, tid)
                    context_storage = ctypes.create_string_buffer(1248)
                    context_address = (ctypes.addressof(context_storage) + 15) & ~15
                    ctypes.c_uint32.from_address(context_address + 48).value = 0x00100003
                    if not thread or not kernel.GetThreadContext(thread, context_address):
                        raise RuntimeError('Cannot inspect own compiler return context')
                    rbp = ctypes.c_uint64.from_address(context_address + 160).value
                    rax = ctypes.c_uint64.from_address(context_address + 120).value
                    collector = read_memory(rbp - 128, 32)
                    errors_pointer, errors_count = struct.unpack_from('<QI', collector, 8)
                    warnings_pointer, warnings_count = struct.unpack_from('<QI', collector, 20)
                    feedback = dict(compilerReturnedSuccess=bool(rax & 255),
                                    errors=strings_array(errors_pointer, errors_count),
                                    warnings=strings_array(warnings_pointer, warnings_count),
                                    returnPointRva='0x1254ef', collectorLayout='CScriptCompilationMessages: two arrays of 28-byte line/file/message records')
                    destination.with_name('compiler-feedback.json').write_text(json.dumps(feedback, ensure_ascii=False, indent=2) + '\n', 'utf8')
                    write_memory(breakpoint, b'\x84')
                    ctypes.c_uint64.from_address(context_address + 248).value = breakpoint
                    kernel.SetThreadContext(thread, context_address)
                    kernel.CloseHandle(thread)
                    breakpoint = None
                if exception != 0x80000003:
                    status = 0x80010001
            elif kind == 5:
                exit_code = struct.unpack_from('<I', data, 16)[0]
            elif kind in (3, 6):
                if kind == 3 and compiler_feedback:
                    image_base = struct.unpack_from('<Q', data, 40)[0]
                    breakpoint = image_base + 0x1254ef
                    if read_memory(breakpoint, 2) != b'\x84\xc0':
                        raise RuntimeError('Compiler return-point signature differs from audited 1.32')
                    write_memory(breakpoint, b'\xcc')
                file_handle = struct.unpack_from('<Q', data, 16)[0]
                if file_handle not in (0, 0xFFFFFFFFFFFFFFFF):
                    module_path = ctypes.create_unicode_buffer(32768)
                    kernel.GetFinalPathNameByHandleW.argtypes = [ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_uint32,ctypes.c_uint32]
                    if kernel.GetFinalPathNameByHandleW(file_handle,module_path,len(module_path),0):
                        module_base=struct.unpack_from('<Q',data,40 if kind==3 else 24)[0]
                        log.write(f'Module base=0x{module_base:x} path={module_path.value}\n');log.flush()
                    kernel.CloseHandle(file_handle)
            kernel.ContinueDebugEvent(pid, tid, status)
    # EXIT_PROCESS_DEBUG_EVENT already supplies the authoritative exit code.
    # Waiting again on the handle can deadlock with injected exit handlers
    # while this thread still owns the native debug object. Compilation still
    # requires explicit successful compiler feedback AND a fresh script cache.
    process.returncode = exit_code
    return timed_out, feedback


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe-root', type=Path, required=True)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--baseline-only', action='store_true')
    parser.add_argument('--label', required=True)
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--show-errors', action='store_true')
    parser.add_argument('--interactive-errors', action='store_true', help='Allow the native compiler error dialog for diagnosis')
    parser.add_argument('--debug-output', action='store_true', help='Capture native diagnostic output from our own child process')
    parser.add_argument('--compiler-feedback', action='store_true', help='Capture the audited 1.32 compiler return value and diagnostic collector')
    parser.add_argument('--without-store-provider', action='store_true', help='Temporarily omit the private probe GOG service DLL; restore after compilation')
    args = parser.parse_args()
    if not 1 <= args.timeout <= 300:
        parser.error('Timeout must be 1..300 seconds')
    probe = args.probe_root.resolve()
    if probe != CLASSIC_RUNTIME.resolve() and not probe.is_relative_to((ROOT / 'BetaGwent/build').resolve()):
        parser.error('Probe runtime must be the permanent Classic toolchain or inside BetaGwent/build')
    if not re.fullmatch(r'[A-Za-z0-9-]+', args.label):
        parser.error('Invalid run label')
    prepared = args.prepared.resolve()
    prep = json.loads((prepared / 'preparation.json').read_text('utf8'))
    audit = json.loads(Path(prep['audit']).read_text('utf-8-sig'))
    if sha(Path(prep['audit'])) != prep['auditSha256']:
        parser.error('Audit manifest changed')
    game = Path(audit['game'])
    exe = probe / 'bin/x64/witcher3.exe'
    if sha(exe) != audit['executableSha256']:
        parser.error('Probe executable differs from audited 1.32')
    content0 = probe / 'content/content0'
    for p in [probe / 'bin', content0, content0 / 'scripts']:
        if p.is_junction() or p.is_symlink():
            parser.error('Writable runtime paths must be real copies')
    for p in content0.glob('*.redscripts'):
        if p.is_symlink() or p.stat().st_nlink != 1:
            parser.error('Compiler cache must be owned by probe: ' + str(p))
    logs = probe / 'runs' / args.label
    if logs.exists():
        parser.error('Run output exists; select a new label')
    logs.mkdir(parents=True)
    # Keep just compiler inputs/resources here, without touching the installed mod.
    if not args.baseline_only:
        patch = prepared / 'Mods/modBetaGwentClassic132/content/scripts'
        if {p.relative_to(patch).as_posix(): sha(p) for p in patch.rglob('*.ws')} != prep['outputScripts']:
            parser.error('Prepared script sources differ from the manifest')
        old_mods=probe/'Mods'
        if old_mods.exists():
            if old_mods.is_junction() or old_mods.is_symlink() or old_mods.resolve().parent != probe:
                parser.error('Probe Mods must be owned by this workspace')
            shutil.move(str(old_mods),str(logs/'before-Mods'))
        shutil.copytree(prepared / 'Mods', probe / 'Mods', dirs_exist_ok=True)
    elif (probe / 'Mods').exists():
        parser.error('Baseline runtime must have no Mods folder')
    (probe / 'bin/config/base/debug.ini').write_text('[Debug]\nDebugScripts=true\nLogDebugScripts=true\n'
                                                  'DebugScriptsForceFlush=true\nDebugScriptsLogDir=' + str(logs) + '\\\n', 'utf8')
    before_artifacts = {str(p): dict(sha256=sha(p), modifiedNs=p.stat().st_mtime_ns)
                        for p in content0.rglob('*.redscripts') if p.is_file()}
    for p in content0.glob('x64*.redscripts'):
        shutil.move(str(p), str(logs / ('before-' + p.name)))
    # Removing only our own generated cache forces recompilation. The retail
    # -forcescriptcompilation switch bypasses the compiler feedback dialog.
    command = [str(exe), '-debugscripts']
    if args.baseline_only:
        command.append('-forcescriptcompilation')
    if not args.interactive_errors:
        command.append('-verifyscriptsandexit')
    if not args.show_errors:
        command.append('-silentscripts')
    # The retail compiler can truncate the user log even with a redirected
    # debug directory. Preserve it before creating the compiler process.
    user_log = Path.home() / 'Documents/The Witcher 3/scriptslog.txt'
    if user_log.exists():
        shutil.copy2(user_log, logs / 'before-user-scriptslog.txt')
    started = time.monotonic()
    with without_store_provider(probe, logs, args.without_store_provider), (logs / 'stdout.txt').open('wb') as stdout, (logs / 'stderr.txt').open('wb') as stderr:
        debug = args.debug_output or args.compiler_feedback
        feedback = None
        process = subprocess.Popen(command, cwd=exe.parent, stdin=subprocess.DEVNULL,
                                   stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW | (2 if debug else 0))
        print(json.dumps(dict(pid=process.pid, command=command, log=str(logs))), flush=True)
        timed_out = False
        if debug:
            timed_out, feedback = wait_with_debug_output(process, args.timeout, logs / 'native-debug.txt', args.compiler_feedback)
        else:
            try:
                process.wait(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                process.kill()
                process.wait(timeout=10)
    artifacts = [dict(path=str(p), bytes=p.stat().st_size, sha256=sha(p), modifiedNs=p.stat().st_mtime_ns)
                 for p in content0.rglob('*.redscripts') if p.is_file()]
    fresh_artifacts = [p for p in artifacts if p['path'] not in before_artifacts or
                       p['modifiedNs'] != before_artifacts[p['path']]['modifiedNs'] or
                       p['sha256'] != before_artifacts[p['path']]['sha256']]
    user_log = Path.home() / 'Documents/The Witcher 3/scriptslog.txt'
    if user_log.exists() and user_log.stat().st_mtime >= time.time() - (time.monotonic() - started) - 2:
        shutil.copy2(user_log, logs / 'scriptslog.txt')
    log_files = [p for p in logs.rglob('*.txt') if p.is_file()]
    log_files += [p for p in probe.glob('scriptslog*') if p.is_file()]
    transcripts = '\n'.join(p.read_text('utf8', errors='replace') for p in log_files)
    errors = sorted(set(line for line in transcripts.splitlines() if re.search(r'\bError\b|\bFatal\b', line)))
    if feedback:
        errors = feedback['errors']
    result = dict(command=command, executableSha256=sha(exe), baselineOnly=args.baseline_only, storeProviderDisabled=args.without_store_provider,
                  preparationManifestSha256=sha(prepared / 'preparation.json'),
                  preparedDirectory=str(prepared),
                  exitCode=process.returncode, timedOut=timed_out, elapsedSeconds=round(time.monotonic()-started, 2),
                  artifacts=artifacts, freshArtifacts=fresh_artifacts, errors=errors, logFiles=[str(p) for p in log_files],
                  compilerFeedback=feedback,
                  compilePassed=bool(feedback and feedback['compilerReturnedSuccess'] and not errors and not timed_out and fresh_artifacts),
                  installedGameModified=False, gameplayVerified=False)
    (logs / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', 'utf8')
    print(json.dumps({k: result[k] for k in ('exitCode','timedOut','elapsedSeconds','compilePassed','freshArtifacts','errors')}, ensure_ascii=False, indent=2), flush=True)
    raise SystemExit(0 if result['compilePassed'] else 1)


if __name__ == '__main__':
    main()

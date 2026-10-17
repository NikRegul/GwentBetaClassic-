"""User-started Classic menu diagnostics; does not install or patch anything."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from native_compile import wait_with_debug_output

ROOT = Path(__file__).resolve().parents[2]
GAME = Path('D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt')
OUTPUT = ROOT / 'BetaGwent/build/classic132-native-feedback'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def snapshot():
    mods = []
    for folder in sorted((GAME / 'Mods').glob('*')):
        if not folder.is_dir():
            continue
        files = []
        for name in ('info.json', 'content/blob0.bundle', 'content/metadata.store', 'content/dep.cache'):
            path = folder / name
            if path.is_file():
                files.append(dict(path=str(path), bytes=path.stat().st_size,
                                  sha256=digest(path)))
        mods.append(dict(folder=folder.name, files=files))
    settings = Path.home() / 'Documents/The Witcher 3/mods.settings'
    addon = GAME / 'DLC/dlcBetaGwentClassic132Assets'
    addon_files = [dict(path=str(path), bytes=path.stat().st_size, sha256=digest(path))
                   for path in sorted(addon.rglob('*')) if path.is_file()] if addon.exists() else []
    return dict(game=str(GAME), mods=mods,
                classicGuiDLC=addon_files,
                modsSettings=settings.read_text('utf-8-sig', errors='replace')
                if settings.exists() else None)


def self_test():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    path = OUTPUT / 'collector-self-test.txt'
    code = ('import ctypes; k=ctypes.WinDLL("kernel32");'
            'k.OutputDebugStringA(b"CLASSIC_COLLECTOR_ANSI");'
            'k.OutputDebugStringW("CLASSIC_COLLECTOR_WIDE")')
    process = subprocess.Popen([sys.executable, '-c', code], creationflags=2)
    timed_out, _ = wait_with_debug_output(process, 15, path, compiler_feedback=False)
    text = path.read_text('utf8')
    assert not timed_out and process.returncode == 0
    assert 'CLASSIC_COLLECTOR_ANSI' in text and 'CLASSIC_COLLECTOR_WIDE' in text
    print('Collector self-test passed. The game was not launched.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    check = subprocess.run(
        ['powershell', '-NoProfile', '-Command',
         '@(Get-Process witcher3 -ErrorAction SilentlyContinue).Count'],
        capture_output=True, text=True, check=True,
        creationflags=subprocess.CREATE_NO_WINDOW)
    if int(check.stdout.strip() or '0'):
        raise RuntimeError('Сначала закройте Witcher 3, затем запустите сборщик ещё раз.')
    exe = GAME / 'bin/x64/witcher3.exe'
    if not exe.is_file():
        raise FileNotFoundError(exe)
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    out = OUTPUT / stamp
    out.mkdir(parents=True, exist_ok=False)
    before = snapshot()
    (out / 'installed-before.json').write_text(
        json.dumps(before, ensure_ascii=False, indent=2), 'utf8')
    print('Загрузите сохранение и откройте колоды, чтобы повторить зависание.', flush=True)
    print('Затем закройте игру. При необходимости — через Диспетчер задач.', flush=True)
    print('Оставьте это окно открытым до завершения сбора.', flush=True)
    print('Папка логов:', out, flush=True)
    started = time.time()
    command = [str(exe), '-debugscripts']
    process = subprocess.Popen(command, cwd=exe.parent, creationflags=2)
    # Only the process launched by this collector is observed. No breakpoints,
    # executable changes, mod installation or changes to save files are made.
    # The existing debugger's watchdog is a last resort after 30 minutes.
    timed_out, _ = wait_with_debug_output(
        process, 1800, out / 'native-engine.txt', compiler_feedback=False)
    log = Path.home() / 'Documents/The Witcher 3/scriptslog.txt'
    fresh = log.exists() and log.stat().st_mtime >= started - 2
    if fresh:
        shutil.copy2(log, out / 'scriptslog.txt')
    after = snapshot()
    (out / 'result.json').write_text(json.dumps(dict(
        command=command, exitCode=process.returncode, timedOut=timed_out,
        freshScriptsLog=fresh, installedFilesUnchanged=before == after,
        compilerInstrumentation=False, executablePatched=False,
        elapsedSeconds=round(time.time() - started, 2)), indent=2), 'utf8')
    print('Готово. Логи сохранены:', out, flush=True)


if __name__ == '__main__':
    main()

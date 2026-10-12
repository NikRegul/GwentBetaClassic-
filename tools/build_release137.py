"""Build five voice packages with thirteen independently selectable text languages."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'BetaGwent/build/stage137'
VOICES = ('en', 'ru', 'de', 'it', 'pt-br')
SHA = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
RUN = datetime.now().strftime('%Y%m%d-%H%M%S-%f')


@contextmanager
def presentation_lock():
    """Share the PowerShell entry point's Windows FileShare.None lock."""
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.CreateFileW(str(ROOT/'BetaGwent/build/presentation-build.lock'),
                                0xC0000000, 0, None, 4, 0x80, None)
    if handle == ctypes.c_void_p(-1).value:
        raise RuntimeError('Another project build holds presentation-build.lock')
    try: yield
    finally: kernel.CloseHandle(handle)


def step(name, command):
    log = BASE/'logs137'/f'{RUN}-{name}.log'
    log.parent.mkdir(parents=True, exist_ok=True)
    print(name, flush=True)
    with log.open('wb') as output:
        result = subprocess.run(command, cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        print(log.read_text('utf8', errors='replace')[-14000:], flush=True)
        raise RuntimeError(name+' failed; '+str(log))
    return log


def python(name, *arguments): return step(name, [sys.executable, '-X', 'utf8', *map(str, arguments)])


def compile_scripts(languages=VOICES):
    report_path=BASE/'compilations137.json'
    report=json.loads(report_path.read_text('utf8')) if report_path.exists() else {}
    for language in languages:
        patch = BASE/language/'sources/scripts'
        assert len(list(patch.rglob('*.ws'))) == 70
        for attempt in range(3):
            output = ROOT/f'BetaGwent/build/board-compile137{language}-{RUN}-attempt{attempt}'
            try:
                python('scripts-'+language+f'-{attempt}', 'tools/recon/run_redkit_compile.py',
                       '--out', output, '--patch', patch, '--timeout', '300', '--terms-already-accepted')
                break
            except RuntimeError:
                result_file = output/'result.json'
                if not result_file.exists() or attempt == 2: raise
                result = json.loads(result_file.read_text('utf8'))
                log = (output/'stdout.txt').read_text('utf8', errors='replace')
                if '[Script]: Error [' in log: raise
                if result.get('processExitCode') != 0xC0000008 and not (result.get('timedOut') and "Starting commandlet 'compilescripts'" not in log): raise
        result = json.loads((output/'result.json').read_text('utf8'))
        assert result['exitCode'] == 0 and not result['timedOut']
        report[language] = dict(run=RUN, compiled=str(output), blobSha256=SHA(output/'compiled/blob.rsblob'),
                                sources=result['patchSourcesBefore'])
    (BASE/'compilations137.json').write_text(json.dumps(report, indent=2)+'\n', 'utf8')


def retire_packages(languages,staging=True):
    """Preserve prior unpublished outputs; never silently reuse a frozen project."""
    moved=[]
    for language in languages:
        candidates=[(ROOT/f'BetaGwent/release/GwentBetaClassic-0.6.1-{language.upper()}.zip',
                     ROOT/f'BetaGwent/release/quarantine/0.6.1-{RUN}'),
                    (ROOT/f'BetaGwent/release/GwentBetaClassic-0.6.1-{language.upper()}.zip.sha256',
                     ROOT/f'BetaGwent/release/quarantine/0.6.1-{RUN}')]
        if staging:candidates.append((ROOT/f'BetaGwent/build/release137/{language}',ROOT/f'BetaGwent/build/history137/{RUN}'))
        for source,folder in candidates:
            if not source.exists():continue
            target=folder/source.name
            assert source.resolve().is_relative_to(ROOT.resolve()) and target.resolve().is_relative_to(ROOT.resolve())
            assert not target.exists()
            folder.mkdir(parents=True,exist_ok=True)
            source.rename(target)
            moved.append({'from':str(source),'to':str(target)})
    if moved:
        record=BASE/'logs137'/f'{RUN}-preserved-previous-outputs.json'
        record.parent.mkdir(parents=True,exist_ok=True)
        record.write_text(json.dumps(moved,indent=2)+'\n','utf8')
    return moved

def package(languages=VOICES,rebuild=False):
    # Never freeze a user's edited dictionary behind stale font/text resources.
    python('current-assets137','tools/ui/check_assets137.py')
    if rebuild:retire_packages(languages)
    compiled = json.loads((BASE/'compilations137.json').read_text('utf8'))
    for language in languages:
        assert language in compiled
        for phase in ('prepare', 'cook', 'strings', 'audio', 'dependencies', 'pack', 'metadata', 'archive'):
            if phase == 'prepare' and (ROOT/f'BetaGwent/build/release137/{language}/frozen.json').exists(): continue
            python('package-'+language+'-'+phase, 'tools/build_language_release.py', phase,
                   '--stage', '137', '--version', '0.6.1', '--language', language,
                   '--compiled', compiled[language]['compiled'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--step', choices=('full', 'prepare', 'scripts', 'menus', 'package', 'verify'), default='full')
    parser.add_argument('--language', choices=('all','both',*VOICES), default='all', help='all builds all five voice packages')
    parser.add_argument('--rebuild-existing',action='store_true',help='Preserve old selected outputs and create a fresh staging project (implied by --step full)')
    arguments = parser.parse_args()
    languages=VOICES if arguments.language in ('all','both') else (arguments.language,)
    # A full build always produces fresh packages from current sources: earlier archives
    # and frozen staging are preserved (quarantine/history), never silently reused.
    rebuild=arguments.rebuild_existing or arguments.step=='full'
    BASE.mkdir(parents=True, exist_ok=True)
    lock_path = ROOT/'BetaGwent/build/.build.lock'
    # Serialize this entry point, including the nested legacy preparation.
    import msvcrt
    with lock_path.open('a+b') as lock:
        lock.seek(0); lock.write(b'1'); lock.flush(); lock.seek(0)
        try: msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError: raise RuntimeError('Another project build is running')
        try:
            if arguments.step=='package' and not rebuild:
                existing=[language for language in languages if (ROOT/f'BetaGwent/release/GwentBetaClassic-0.6.1-{language.upper()}.zip').exists()]
                if existing:raise RuntimeError('Existing archives: '+','.join(existing)+'. Use -RebuildExisting to preserve them and rebuild.')
            if arguments.step in ('full', 'prepare'):
                step('baseline-and-regressions', ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                     '-File', str(ROOT/'tools/Build-GwentBeta.ps1'), '-Stage', '135', '-Version', '0.6.1',
                     '-Step', 'prepare', '-CheckAI'])
            with presentation_lock():
                if arguments.step in ('full', 'prepare'):
                    python('leader-pages', 'tools/ui/build_leaders137.py')
                    python('languages', 'tools/ui/build_languages137.py')
                    python('voices', 'tools/ui/build_voice137.py')
                    snapshot=BASE/'regressions'/RUN/'snapshot'
                    python('snapshot137','tools/ai/snapshot.py',snapshot)
                    python('regressions137','tools/check_release137.py','--snapshot',snapshot)
                if arguments.step in ('full', 'scripts'): compile_scripts(languages)
                if arguments.step in ('full', 'menus'):
                    python('menus', 'tools/build_presentation94.py', '--stage', '137', '--language', 'ru')
                if arguments.step in ('full', 'package'): package(languages,rebuild)
                if arguments.step in ('full', 'verify'):
                    python('release-verification', 'tools/verify_release137.py','--language',arguments.language)
            print('Finished requested 0.6.1 phase:', arguments.step, flush=True)
        finally:
            lock.seek(0); msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)


if __name__ == '__main__': main()

"""Isolated UI development; never invokes the release build or touches AI scripts."""
import argparse
import ctypes
import hashlib
import json
import shutil
import subprocess
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / 'BetaGwent/drafts/ui-polish138'
LIVE = ROOT / 'BetaGwent/ui/src'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

@contextmanager
def build_locks():
    # Same two locks as build_release137.py; acquire BOTH before changing live inputs.
    import msvcrt
    from ctypes import wintypes
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                  wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    with (ROOT / 'BetaGwent/build/.build.lock').open('r+b') as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        handle = None
        try:
            handle = kernel.CreateFileW(str(ROOT/'BetaGwent/build/presentation-build.lock'),
                                       0xC0000000, 0, None, 4, 0x80, None)
            if handle == ctypes.c_void_p(-1).value:
                raise RuntimeError('Presentation build is active; live sources were not changed')
            yield
        finally:
            if handle is not None and handle != ctypes.c_void_p(-1).value:
                kernel.CloseHandle(handle)
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)

def init():
    if (DRAFT/'baseline.json').exists():
        raise RuntimeError('Draft already exists; preserve ongoing work')
    DRAFT.mkdir(parents=True, exist_ok=True)
    shutil.copytree(LIVE, DRAFT/'src')
    baseline = {str(p.relative_to(LIVE)).replace('\\','/'): sha(p) for p in LIVE.rglob('*.as')}
    # Detect a concurrent source edit even during the initial copy.
    for name, value in baseline.items():
        if sha(DRAFT/'src'/name) != value:
            raise RuntimeError('Source changed during snapshot: '+name)
    (DRAFT/'baseline.json').write_text(json.dumps(baseline, indent=2)+'\n', 'utf8')
    print('Isolated UI snapshot created:', DRAFT)

def changed():
    baseline = json.loads((DRAFT/'baseline.json').read_text('utf8'))
    return baseline, [p for p in (DRAFT/'src').rglob('*.as')
                      if baseline.get(p.relative_to(DRAFT/'src').as_posix()) != sha(p)]

def check():
    baseline, paths = changed()
    conflicts = [p.relative_to(DRAFT/'src').as_posix() for p in paths
                 if (LIVE/p.relative_to(DRAFT/'src')).exists()
                 and sha(LIVE/p.relative_to(DRAFT/'src')) != baseline.get(p.relative_to(DRAFT/'src').as_posix())]
    print(json.dumps({'changed':[p.relative_to(DRAFT/'src').as_posix() for p in paths],
                      'conflicts':conflicts, 'liveSourcesModified':False}, indent=2))
    if conflicts:
        raise RuntimeError('Concurrent edits need merging; nothing was applied')

def apply():
    with build_locks():
        check()
        baseline, paths = changed()
        verified=json.loads((DRAFT/'evidence/checks.json').read_text('utf8'))
        regressions=json.loads((DRAFT/'evidence/regressions.json').read_text('utf8'))
        if not regressions or any(r['exitCode']!=0 for r in regressions):
            raise RuntimeError('UI regressions are not passing')
        for p in paths:
            name=p.relative_to(DRAFT/'src').as_posix()
            if verified['sources'].get(name)!=sha(p):
                raise RuntimeError('Changed source was not tested: '+name)
            # The compile copy only rewrites Embed paths. The three changed files have no Embeds.
            if (DRAFT/'compile/src'/name).read_text('utf-8-sig')!=p.read_text('utf-8-sig'):
                raise RuntimeError('Changed source was not compiled: '+name)
        movies=json.loads((DRAFT/'compile/result.json').read_text('utf8'))['movies']
        for movie in movies:
            if sha(DRAFT/'compile'/(movie['entry']+'.swf'))!=movie['sha256']:
                raise RuntimeError('Compiled menu changed after validation')
        backup = DRAFT/'before-apply'
        if backup.exists():
            raise RuntimeError('Already applied or backup exists; review before reapplying')
        backup.mkdir()
        for p in paths:
            relative = p.relative_to(DRAFT/'src')
            if (LIVE/relative).exists():
                target=backup/relative; target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(LIVE/relative, target)
        applied=[]
        try:
            for p in paths:
                relative=p.relative_to(DRAFT/'src');target=LIVE/relative
                target.parent.mkdir(parents=True, exist_ok=True);applied.append(relative)
                shutil.copy2(p, target)
        except Exception:
            for relative in reversed(applied):
                if (backup/relative).exists():shutil.copy2(backup/relative,LIVE/relative)
                else:(LIVE/relative).unlink(missing_ok=True)
            raise
        record={'version':'0.6.2','stage':138,'sources':{p.relative_to(DRAFT/'src').as_posix():sha(p) for p in paths},
                'sourceChecks':verified['checks'],'regressionSuites':len(regressions),'compiledMenus':len(movies),
                'nativeGameTested':False,'releaseArchivesModified':False,'aiScriptsModified':False}
        (ROOT/'docs/evidence/ui138.json').write_text(json.dumps(record,indent=2)+'\n','utf8')
        print('Applied UI sources only. Release archives, generated menus and native scripts were not changed.')

def compile_menus():
    build = DRAFT/'compile'; build.mkdir(exist_ok=True)
    compiled = build/'src'
    shutil.copytree(DRAFT/'src', compiled, dirs_exist_ok=True)
    # Embeds resolve relative to the .as file; point ONLY the throwaway compiler copy at live read-only assets.
    for p in compiled.rglob('*.as'):
        text = p.read_text('utf-8-sig').replace('../assets/', (ROOT/'BetaGwent/ui/assets').as_posix()+'/')
        p.write_text(text, 'utf8')
    java = Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    config = build/'config.xml'
    config.write_text('''<flex-config xmlns="http://www.adobe.com/2006/flex-config">
<target-player>11.1</target-player><swf-version>14</swf-version><compiler>
<debug>false</debug><compress>false</compress><optimize>true</optimize><strict>true</strict>
<external-library-path><path-element>'''+(ROOT/'tools/vendor/royale-player-api-0.9.12/royale-typedefs-playerglobal-0.9.12-swf.swc').as_posix()+'''</path-element></external-library-path>
<source-path><path-element>'''+compiled.as_posix()+'''</path-element></source-path><theme/>
</compiler></flex-config>''', 'utf8')
    reports=[]
    for entry in ('BetaGwentNpcMenu','BetaGwentDeckMenu','BetaGwentKegMenu'):
        log=build/(entry+'.log'); movie=build/(entry+'.swf')
        command=[str(java) if java.exists() else 'java','-Xmx1536m','-Duser.language=en','-Duser.country=US','-jar',
                 str(ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib/mxmlc.jar'),
                 '-load-config='+str(config), '-output='+str(movie),
                 '-source-path+='+r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\gameplay\gui_new\actionscript',
                 '-includes+=scaleform.gfx.KeyboardEventEx',str(compiled/(entry+'.as'))]
        print('Compile isolated '+entry, flush=True)
        with log.open('wb') as out:
            result=subprocess.run(command,cwd=build,stdout=out,stderr=subprocess.STDOUT,
                                  creationflags=subprocess.CREATE_NO_WINDOW,timeout=300)
        output=log.read_text('utf8',errors='replace')
        if result.returncode or 'Error:' in output:
            print(output[-12000:]); raise RuntimeError(entry+' failed')
        reports.append({'entry':entry,'bytes':movie.stat().st_size,'sha256':sha(movie)})
    (build/'result.json').write_text(json.dumps({'movies':reports,'nativeGameTested':False},indent=2)+'\n','utf8')
    print('Three isolated menus compiled. No shared SWF/GFx, atlases or release outputs changed.')

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('init','check','apply','compile'))
    args=parser.parse_args()
    {'init':init,'check':check,'apply':apply,'compile':compile_menus}[args.action]()

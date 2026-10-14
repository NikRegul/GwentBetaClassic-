"""Build 0.6.3 using audited AI/motion and the unchanged 0.6.2 languages/assets."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/stage139'
VOICES=('ru','en','de','it','pt-br')
RUN=datetime.now().strftime('%Y%m%d-%H%M%S')

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(path):return json.loads(path.read_text('utf-8-sig'))
def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n','utf8')
def step(name,*args):
    log=BASE/'logs'/f'{RUN}-{name}.log';log.parent.mkdir(parents=True,exist_ok=True)
    print(name,flush=True)
    with log.open('wb') as f:r=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode:
        print(log.read_text('utf8',errors='replace')[-6500:],flush=True)
        raise RuntimeError(f'{name} failed: {log}')
    return log
def inputs():
    sys.path.insert(0,str(ROOT/'tools/ai'))
    from snapshot import verify
    snapshot=ROOT/'BetaGwent/build/audit139/candidate'
    manifest=verify(snapshot)
    regressions=read(ROOT/'docs/evidence/regressions139.json')
    assert regressions['passed'] and regressions['fingerprint']==manifest['fingerprint']
    for c in regressions['checks']:assert c['exitCode']==0 and sha(ROOT/c['script'])==c['sha256']
    sources={p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'BetaGwent/ui/src').glob('*.as')}
    sources.update(manifest['files'])
    old=read(ROOT/'BetaGwent/build/audit139/baseline/manifest.json')
    changed=[name for name,digest in old['files'].items() if manifest['files'][name]!=digest]
    assert changed==['BetaGwent/development/scripts/game/betagwent/duelSession.ws'],changed
    record=dict(stage=139,version='0.6.3',fingerprint=manifest['fingerprint'],sources=sources,
        previousArchives={p.name:sha(p) for p in (ROOT/'BetaGwent/release').glob('GwentBetaClassic-0.6.2-*.zip')},
        reusedAssets={name:sha(ROOT/'docs/evidence'/name) for name in ('languages138.json','voice138.json','leaders137.json')},
        changedScripts=changed,nativeGameTested=False)
    target=ROOT/'docs/evidence/inputs139.json'
    if target.exists():assert read(target)==record,'Inputs changed during staged build'
    else:save(target,record)
    return record
def scripts(languages):
    report_path=BASE/'compilations139.json';report=read(report_path) if report_path.exists() else {}
    for language in languages:
        patch=BASE/language/'sources/scripts'
        if not patch.exists():shutil.copytree(ROOT/f'BetaGwent/build/stage138/{language}/sources/scripts',patch)
        shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent/duelSession.ws',patch/'game/betagwent/duelSession.ws')
        assert len(list(patch.rglob('*.ws')))==70
        if language in report:
            assert all(sha(patch/f['path'])==f['sha256'] for f in report[language]['sources'])
            continue
        for attempt in range(3):
            output=BASE/f'compile-{language}-{RUN}-{attempt}'
            try:
                step('scripts-'+language+f'-{attempt}','tools/recon/run_redkit_compile.py','--out',output,'--patch',patch,'--timeout','300','--terms-already-accepted')
                break
            except RuntimeError:
                transcript=(output/'stdout.txt').read_text('utf8',errors='replace')
                result=read(output/'result.json')
                if '[Script]: Error [' in transcript or attempt==2:raise
                if result.get('processExitCode')!=0xC0000008 and not result.get('timedOut'):raise
        r=read(output/'result.json');assert r['exitCode']==0 and not r['timedOut'] and r['patchSourcesUnchangedDuringCompile']
        report[language]=dict(compiled=str(output),sources=r['patchSourcesBefore'],blobSha256=sha(output/'compiled/blob.rsblob'))
        save(report_path,report)
def package(languages):
    compiled=read(BASE/'compilations139.json')
    for language in languages:
        seed_audio_cache(language)
        for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive'):
            step('package-'+language+'-'+phase,'tools/build_language_release.py',phase,'--stage','139','--version','0.6.3','--language',language,'--compiled',compiled[language]['compiled'])
def seed_audio_cache(language):
    # Voices are unchanged. The normal audio step verifies the embedded bank
    # again; avoid rebuilding a cache whose complete bank bytes already match.
    previous=ROOT/f'BetaGwent/build/release138/{language}/audio-cooked/CookedPC/soundspc.cache'
    target=ROOT/f'BetaGwent/build/release139/{language}/audio-cooked/CookedPC/soundspc.cache'
    if target.exists() or not previous.exists():return
    bank=Path(read(ROOT/'docs/evidence/voice138.json')[language]['bank']).read_bytes()
    data=previous.read_bytes()
    assert data[:4]==b'CS3W' and len(data)==len(bank)+104 and data[64:64+len(bank)]==bank
    target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(previous,target)
def verify(languages):
    sys.path.insert(0,str(ROOT/'tools/ui'))
    from verify_bundle96 import verify as verify_bundle
    from verify_cooked_menu95 import verify as verify_cooked
    record=read(ROOT/'docs/evidence/inputs139.json')
    regressions=read(ROOT/'docs/evidence/regressions139.json')
    motion=read(ROOT/'docs/evidence/motion139.json')
    assert regressions['passed'] and regressions['fingerprint']==record['fingerprint']
    assert motion['actualActionScript'] and motion['checks']>=1070
    assert motion['sourceSha256']==sha(ROOT/'BetaGwent/ui/src/BetaGwentBoard.as')
    for name,digest in record['sources'].items():assert sha(ROOT/name)==digest,name
    for name,digest in record['previousArchives'].items():assert sha(ROOT/'BetaGwent/release'/name)==digest,name
    for name,digest in record['reusedAssets'].items():assert sha(ROOT/'docs/evidence'/name)==digest,name
    menus=read(ROOT/'docs/evidence/stage139-completion.json')
    for name,digest in menus['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,name
    assert len(menus['menus'])==4
    compiled=read(BASE/'compilations139.json');packages=[]
    for language in languages:
        base=ROOT/f'BetaGwent/build/release139/{language}';work=base/'project/BetaGwent0924/workspace'
        compilation=compiled[language];r=read(Path(compilation['compiled'])/'result.json')
        assert r['exitCode']==0 and not r['timedOut'] and r['patchSourcesUnchangedDuringCompile']
        for f in compilation['sources']:assert sha(work/'scripts'/f['path'])==f['sha256']
        assert sha(work/'scripts/game/betagwent/duelSession.ws')==sha(ROOT/'BetaGwent/development/scripts/game/betagwent/duelSession.ws')
        for menu in menus['menus']:
            source=Path(menu['resource']);assert sha(source)==menu['sha256']
            suffix='' if menu['entry']=='BetaGwentBoard' else '-'+menu['entry']
            bridge=read(ROOT/f'docs/evidence/stage139-ru-board-bridge-bytecode{suffix}.json')
            native=read(ROOT/f'docs/evidence/stage139-ru-board-resource-update{suffix}.json')
            build=read(ROOT/f'docs/evidence/stage139-ru-board-build{suffix}.json')
            assert build['sources']==menus['sources'],'Menus were built from different sources'
            assert bridge['passed'] and native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
            verify_cooked(work/'betagwent'/source.name,base/'cooked/betagwent'/source.name)
        content=base/'package/Mods/modBetaGwent0924/content'
        voice_bank=Path(read(ROOT/'docs/evidence/voice138.json')[language]['bank']).read_bytes()
        audio=(content/'soundspc.cache').read_bytes()
        assert audio[:4]==b'CS3W' and len(audio)==len(voice_bank)+104 and audio[64:64+len(voice_bank)]==voice_bank
        bundle=verify_bundle(content/'blob0.bundle',base/'bundle-input',require_uncompressed_gui=True,gui_limit_mib=56)
        assert not any('betagwentpremium' in f['path'].lower() or 'redux' in f['path'].lower() for f in bundle['entries'])
        assert sha(content/'precompiled.rsblob')==compilation['blobSha256']
        release=read(ROOT/f'docs/evidence/stage139-release-{language}.json');archive=Path(release['archive'])
        assert release['version']=='0.6.3' and release['archiveVerified'] and sha(archive)==release['archiveSha256']
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
            manifest=json.loads(z.read('manifest.json'))
            assert set(z.namelist())=={'manifest.json',*(f['path'] for f in manifest['files'])}
            for f in manifest['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
            assert set(manifest['textLanguages'])==set(read(ROOT/'docs/evidence/languages138.json')['languages'])
        packages.append(dict(language=language,archive=str(archive),sha256=release['archiveSha256'],bytes=archive.stat().st_size))
    save(ROOT/'docs/evidence/validation139.json',dict(stage=139,version='0.6.3',passed=True,packages=packages,previous062ArchivesUnmodified=True,nativeGameTested=False))
    print('Verified 0.6.3: '+','.join(languages),flush=True)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--step',choices=('full','scripts','menus','package','verify'),default='full')
    p.add_argument('--language',choices=('all',*VOICES),default='ru')
    a=p.parse_args();languages=VOICES if a.language=='all' else (a.language,)
    BASE.mkdir(parents=True,exist_ok=True)
    if a.step in ('full','package'):
        existing=[language for language in languages if (ROOT/f'BetaGwent/release/GwentBetaClassic-0.6.3-{language.upper()}.zip').exists()]
        if existing:raise RuntimeError('0.6.3 archives already exist: '+','.join(existing)+'. Verify them or use a new version.')
    from build_release138 import presentation_lock
    with presentation_lock():
        inputs()
        if a.step in ('full','scripts'):scripts(languages)
        if a.step in ('full','menus'):step('menus','tools/build_presentation94.py','--stage','139','--language','ru')
        if a.step in ('full','package'):package(languages)
        if a.step in ('full','verify'):verify(languages)
if __name__=='__main__':main()

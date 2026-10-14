"""Package and verify the combined 0.6.6 RU test build from frozen Stage 142 inputs."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/stage142'
SNAPSHOT=ROOT/'BetaGwent/build/audit142/final'
COMPILED=BASE/'compile-final-ru'
RUN=datetime.now().strftime('%Y%m%d-%H%M%S')
VERSION='0.6.6'

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')
def step(name,*args):
    log=BASE/'logs'/f'{RUN}-{name}.log';log.parent.mkdir(parents=True,exist_ok=True)
    print(name,flush=True)
    with log.open('wb') as f:r=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode:
        print(log.read_text('utf8',errors='replace')[-6000:],flush=True);raise RuntimeError(str(log))

def inputs():
    sys.path.insert(0,str(ROOT/'tools/ai'))
    from snapshot import verify
    snapshot=verify(SNAPSHOT)
    checks=read(ROOT/'docs/evidence/regressions142.json')
    assert checks['passed'] and checks['fingerprint']==snapshot['fingerprint'] and len(checks['checks'])==50
    for c in checks['checks']:assert c['exitCode']==0 and sha(ROOT/c['script'])==c['sha256'],c['script']
    compilation=read(COMPILED/'result.json')
    assert compilation['exitCode']==0 and not compilation['timedOut'] and compilation['patchSourcesUnchangedDuringCompile']
    scripts=BASE/'ru/sources/scripts'
    assert len(compilation['patchSourcesBefore'])==70
    for item in compilation['patchSourcesBefore']:assert sha(scripts/item['path'])==item['sha256']
    for name in ('duelSession.ws','duelNilfDependencies.ws','shopRuntime.ws','duelAudio.ws'):
        assert sha(scripts/'game/betagwent'/name)==sha(ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
    menus=read(ROOT/'docs/evidence/stage142-completion.json')
    assert len(menus['menus'])==4
    current={p.name:sha(p) for p in (ROOT/'BetaGwent/ui/src').glob('*.as')}
    assert menus['sources']==current
    for m in menus['menus']:
        suffix='' if m['entry']=='BetaGwentBoard' else '-'+m['entry']
        build=read(ROOT/f'docs/evidence/stage142-ru-board-build{suffix}.json')
        bridge=read(ROOT/f'docs/evidence/stage142-ru-board-bridge-bytecode{suffix}.json')
        native=read(ROOT/f'docs/evidence/stage142-ru-board-resource-update{suffix}.json')
        assert build['sources']==current and bridge['passed'] and native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
        assert sha(Path(m['resource']))==m['sha256']
    previous={p.name:sha(p) for p in (ROOT/'BetaGwent/release').glob('GwentBetaClassic-0.6.[345]-*.zip')}
    record=dict(stage=142,version=VERSION,fingerprint=snapshot['fingerprint'],scripts=compilation['patchSourcesBefore'],uiSources=current,
        previousArchives=previous,voiceBankSha256=read(ROOT/'docs/evidence/voice141.json')['ru']['sha256'],nativeGameTested=False)
    path=ROOT/'docs/evidence/inputs142.json'
    if path.exists():assert read(path)==record,'Frozen 0.6.6 inputs changed'
    else:save(path,record)
    return record

def verify_package():
    sys.path.insert(0,str(ROOT/'tools/ui'))
    from verify_bundle96 import verify as verify_bundle
    from verify_cooked_menu95 import verify as verify_cooked
    record=inputs();base=ROOT/'BetaGwent/build/release142/ru'
    work=base/'project/BetaGwent0924/workspace';content=base/'package/Mods/modBetaGwent0924/content'
    for item in record['scripts']:assert sha(work/'scripts'/item['path'])==item['sha256']
    assert sha(content/'precompiled.rsblob')==sha(COMPILED/'compiled/blob.rsblob')
    for item in read(ROOT/'docs/evidence/stage142-completion.json')['menus']:
        verify_cooked(Path(item['resource']),base/'cooked/betagwent'/Path(item['resource']).name)
    bundle=verify_bundle(content/'blob0.bundle',base/'bundle-input',require_uncompressed_gui=True,gui_limit_mib=56)
    for item in read(ROOT/'docs/evidence/leader-intros142.json')['resources'].values():
        assert sha(work/item['path'])==item['sha256'];verify_cooked(work/item['path'],base/'cooked'/item['path'])
    # Each named base-game and expansion inn stock is present in the frozen package.
    innkeepers=read(ROOT/'docs/evidence/innkeeper-kegs142.json')
    for item in innkeepers['overlays']:assert sha(work/item['path'])==item['overlaySha256']
    bank=Path(read(ROOT/'docs/evidence/voice141.json')['ru']['bank']).read_bytes();audio=(content/'soundspc.cache').read_bytes()
    assert audio[:4]==b'CS3W' and len(audio)==len(bank)+104 and audio[64:64+len(bank)]==bank
    release=read(ROOT/'docs/evidence/stage142-release-ru.json');archive=Path(release['archive'])
    assert release['version']==VERSION and release['archiveVerified'] and sha(archive)==release['archiveSha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        manifest=json.loads(z.read('manifest.json'));assert set(z.namelist())=={'manifest.json',*(f['path'] for f in manifest['files'])}
        for f in manifest['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
    assert len(manifest['textLanguages'])==13
    for name,digest in record['previousArchives'].items():assert sha(ROOT/'BetaGwent/release'/name)==digest
    report=dict(stage=142,version=VERSION,language='ru',passed=True,regressionSuites=50,nativeScripts=70,nativeMenus=4,
        sourceFingerprint=record['fingerprint'],archive=str(archive),archiveSha256=release['archiveSha256'],bytes=archive.stat().st_size,
        bundleEntries=len(bundle['entries']),oneShotLeaders=12,loopFallbackLeaders=9,previousArchivesUnmodified=True,nativeGameTested=False)
    save(ROOT/'docs/evidence/validation142.json',report);print(json.dumps(report),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--step',choices=('package','verify'),default='package');a=p.parse_args()
    from build_release138 import presentation_lock
    with presentation_lock():
        if a.step=='package':
            assert not (ROOT/f'BetaGwent/release/GwentBetaClassic-{VERSION}-RU.zip').exists(),'Existing releases are immutable'
            inputs()
            for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive'):
                step('package-ru-'+phase,'tools/build_language_release.py',phase,'--stage','142','--version',VERSION,'--language','ru','--compiled',COMPILED)
        verify_package()

if __name__=='__main__':main()

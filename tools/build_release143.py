"""Package and verify the combined 0.6.7 RU test build from frozen Stage 143 inputs."""
import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'BetaGwent/build/stage143'
SNAPSHOT=ROOT/'BetaGwent/build/audit143/final-v2'
COMPILED=BASE/'compile-final-ru-v2'
RUN=datetime.now().strftime('%Y%m%d-%H%M%S')
VERSION='0.6.7'

def gui_budget():
    path=BASE/'gui-budget.json'
    value=read(path)['guiLimitMiB'] if path.exists() else 56
    assert isinstance(value,int) and 1<=value<100,'Invalid GUI loading target'
    return value

def ui_source_directory():
    path=BASE/'ui-profile.json'
    if not path.exists():return ROOT/'BetaGwent/ui/src'
    profile=read(path);directory=Path(profile['sourceDir']).resolve()
    assert directory.is_relative_to(BASE.resolve()),'UI profile must stay inside its build stage'
    for item in profile['assets']:assert sha(Path(item['path']))==item['sha256'],'UI profile asset changed'
    for name,digest in profile['baseSources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,'Canonical UI changed during variant build'
    return directory

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2)+'\n','utf8')
def step(name,*args):
    if args and str(args[0]).endswith('build_language_release.py') and '--gui-limit-mib' not in args:
        args=(*args,'--gui-limit-mib',str(gui_budget()))
    log=BASE/'logs'/f'{RUN}-{name}.log';log.parent.mkdir(parents=True,exist_ok=True)
    print(name,flush=True)
    with log.open('wb') as f:r=subprocess.run([sys.executable,'-X','utf8',*map(str,args)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if r.returncode:
        print(log.read_text('utf8',errors='replace')[-6000:],flush=True);raise RuntimeError(str(log))

def inputs():
    sys.path.insert(0,str(ROOT/'tools/ai'))
    from snapshot import verify
    snapshot=verify(SNAPSHOT)
    checks=read(ROOT/'docs/evidence/regressions143.json')
    assert checks['passed'] and checks['fingerprint']==snapshot['fingerprint'] and len(checks['checks'])==51
    for c in checks['checks']:assert c['exitCode']==0 and sha(ROOT/c['script'])==c['sha256'],c['script']
    compilation=read(COMPILED/'result.json')
    assert compilation['exitCode']==0 and not compilation['timedOut'] and compilation['patchSourcesUnchangedDuringCompile']
    scripts=BASE/'ru/sources/scripts'
    assert len(compilation['patchSourcesBefore'])==70
    for item in compilation['patchSourcesBefore']:assert sha(scripts/item['path'])==item['sha256']
    for name in ('duelSession.ws','duelNilfDependencies.ws','shopRuntime.ws','duelAudio.ws'):
        assert sha(scripts/'game/betagwent'/name)==sha(ROOT/'BetaGwent/development/scripts/game/betagwent'/name)
    menus=read(ROOT/'docs/evidence/stage143-completion.json')
    assert len(menus['menus'])==4
    current={p.name:sha(p) for p in ui_source_directory().glob('*.as')}
    assert menus['sources']==current
    for m in menus['menus']:
        suffix='' if m['entry']=='BetaGwentBoard' else '-'+m['entry']
        build=read(ROOT/f'docs/evidence/stage143-ru-board-build{suffix}.json')
        bridge=read(ROOT/f'docs/evidence/stage143-ru-board-bridge-bytecode{suffix}.json')
        native=read(ROOT/f'docs/evidence/stage143-ru-board-resource-update{suffix}.json')
        assert build['sources']==current and bridge['passed'] and native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
        assert sha(Path(m['resource']))==m['sha256']
    previous={p.name:sha(p) for p in (ROOT/'BetaGwent/release').glob('GwentBetaClassic-0.6.[3456]-*.zip')}
    record=dict(stage=143,version=VERSION,fingerprint=snapshot['fingerprint'],scripts=compilation['patchSourcesBefore'],uiSources=current,
        previousArchives=previous,voiceBankSha256=read(ROOT/'docs/evidence/voice141.json')['ru']['sha256'],nativeGameTested=False)
    spell_art=read(ROOT/'docs/evidence/spell-art143.json')
    for item in spell_art['textures']:
        assert sha(ROOT/item['output'])==item['sha256']
        assert sha(ROOT/item['source'])==item['sourceSha256']
    record['spellArt']=spell_art['textures']
    if int(BASE.name.removeprefix('stage'))>=161:
        from shop_keg_icon161 import validate as validate_shop_icon, ASSET, MANIFEST
        record['shopKegIcon']=validate_shop_icon()
        record['shopKegIcon'].update(manifestSha256=sha(MANIFEST),assetSha256=sha(ASSET),
                                   scriptSha256=sha(ROOT/'tools/shop_keg_icon161.py'))
    path=ROOT/'docs/evidence/inputs143.json'
    if path.exists():assert read(path)==record,'Frozen 0.6.7 inputs changed'
    else:save(path,record)
    return record

def verify_package():
    sys.path.insert(0,str(ROOT/'tools/ui'))
    from verify_bundle96 import verify as verify_bundle
    from verify_cooked_menu95 import verify as verify_cooked
    record=inputs();base=ROOT/'BetaGwent/build/release143/ru'
    work=base/'project/BetaGwent0924/workspace';content=base/'package/Mods/modBetaGwent0924/content'
    for item in record['scripts']:assert sha(work/'scripts'/item['path'])==item['sha256']
    assert sha(content/'precompiled.rsblob')==sha(COMPILED/'compiled/blob.rsblob')
    for item in read(ROOT/'docs/evidence/stage143-completion.json')['menus']:
        verify_cooked(Path(item['resource']),base/'cooked/betagwent'/Path(item['resource']).name)
    bundle=verify_bundle(content/'blob0.bundle',base/'bundle-input',require_uncompressed_gui=True,gui_limit_mib=gui_budget())
    if 'shopKegIcon' in record:
        from shop_keg_icon161 import validate as validate_shop_icon
        validate_shop_icon(work)
        icon=read(base/'project/BetaGwent0924/betagwent-assets/shop-icon.json')
        assert icon['iconSha256']==record['shopKegIcon']['sha256']
        assert sha(content/'texture.cache')==icon['cacheSha256']
    for item in read(ROOT/'docs/evidence/leader-intros142.json')['resources'].values():
        assert sha(work/item['path'])==item['sha256'];verify_cooked(work/item['path'],base/'cooked'/item['path'])
    # Each named base-game and expansion inn stock is present in the frozen package.
    innkeepers=read(ROOT/'docs/evidence/innkeeper-kegs142.json')
    for item in innkeepers['overlays']:assert sha(work/item['path'])==item['overlaySha256']
    bank=Path(read(ROOT/'docs/evidence/voice141.json')['ru']['bank']).read_bytes();audio=(content/'soundspc.cache').read_bytes()
    assert audio[:4]==b'CS3W' and len(audio)==len(bank)+104 and audio[64:64+len(bank)]==bank
    release=read(ROOT/'docs/evidence/stage143-release-ru.json');archive=Path(release['archive'])
    assert release['version']==VERSION and release['archiveVerified'] and sha(archive)==release['archiveSha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        manifest=json.loads(z.read('manifest.json'));assert set(z.namelist())=={'manifest.json',*(f['path'] for f in manifest['files'])}
        for f in manifest['files']:assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
    assert len(manifest['textLanguages'])==13
    for name,digest in record['previousArchives'].items():assert sha(ROOT/'BetaGwent/release'/name)==digest
    report=dict(stage=143,version=VERSION,language='ru',passed=True,regressionSuites=len(read(ROOT/'docs/evidence/regressions143.json')['checks']),nativeScripts=70,nativeMenus=4,
        sourceFingerprint=record['fingerprint'],archive=str(archive),archiveSha256=release['archiveSha256'],bytes=archive.stat().st_size,
        bundleEntries=len(bundle['entries']),guiLimitMiB=gui_budget(),
        guiMenus={Path(m['resource']).name:dict(bytes=(base/'cooked/betagwent'/Path(m['resource']).name).stat().st_size,MiB=(base/'cooked/betagwent'/Path(m['resource']).name).stat().st_size/1048576) for m in read(ROOT/'docs/evidence/stage143-completion.json')['menus']},
        oneShotLeaders=12,loopFallbackLeaders=9,previousArchivesUnmodified=True,nativeGameTested=False)
    if 'shopKegIcon' in record:report['shopKegIcon']=record['shopKegIcon']
    save(ROOT/'docs/evidence/validation143.json',report);print(json.dumps(report),flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--step',choices=('package','verify'),default='package');a=p.parse_args()
    from build_release138 import presentation_lock
    with presentation_lock():
        if a.step=='package':
            assert not (ROOT/f'BetaGwent/release/GwentBetaClassic-{VERSION}-RU.zip').exists(),'Existing releases are immutable'
            inputs()
            for phase in ('prepare','cook','strings','audio','dependencies','pack','metadata','archive'):
                step('package-ru-'+phase,'tools/build_language_release.py',phase,'--stage','143','--version',VERSION,'--language','ru','--compiled',COMPILED)
        verify_package()

if __name__=='__main__':main()

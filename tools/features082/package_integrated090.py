"""Stage 0.9.0 candidates from the exact compiled inputs; never publish them.

Archives stay under the build directory until the Classic gameplay check passes.
Accepted audio, art, native texture bindings and DLC are checked by build_release.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys, zipfile

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/'BetaGwent/build/release090-integrated'
BUILD=ROOT/'BetaGwent/build/release090-package-candidate'
sys.path.insert(0,str(Path(__file__).parent))
import build_release as pack


def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def hashes(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*.ws')}


def prepare(platform):
    part=BUILD/platform
    assert not part.exists(),'Keep a completed or interrupted candidate immutable'
    classic=json.loads((INPUT/'classic-prepared-final/preparation.json').read_text('utf8'))
    assert hashes(INPUT/'scripts')==classic['sourceScripts']
    result=json.loads(pack.CLASSIC_COMPILE.read_text('utf8'))
    assert result['compilePassed'] and not result['errors']
    assert result['preparationManifestSha256']==sha(INPUT/'classic-prepared-final/preparation.json')
    ng=json.loads((INPUT/'compile-nextgen-final/result.json').read_text('utf8'))
    assert ng['exitCode']==0 and ng['patchSourcesUnchangedDuringCompile']
    assert {p['path']:p['sha256'] for p in ng['patchSourcesBefore']}==classic['sourceScripts']
    assert sha(INPUT/'compile-nextgen-final/compiled/blob.rsblob')==ng['artifacts'][0]['sha256'].lower()
    BUILD.mkdir(exist_ok=True)
    if not (BUILD/'redux').exists():
        shutil.copytree(ROOT/'BetaGwent/build/release082-polish2/redux',BUILD/'redux')
    part.mkdir()
    (part/'menus').mkdir()
    shutil.copy2(INPUT/platform/'menus-final/menus.json',part/'menus/menus.json')
    if (INPUT/platform/'extra-resources').exists():
        shutil.copytree(INPUT/platform/'extra-resources',part/'extra-resources')
    if platform=='classic':
        shutil.copy2(INPUT/'classic/subimages.json',part/'subimages.json')
        (part/'ui/src').mkdir(parents=True)
        shutil.copy2(INPUT/'classic/ui/src/BetaGwentHDArt.as',part/'ui/src/BetaGwentHDArt.as')
        if not (BUILD/'classic-prepared').exists():
            shutil.copytree(INPUT/'classic-prepared-final',BUILD/'classic-prepared')
    else:
        if not (BUILD/'compile-nextgen').exists():
            (BUILD/'compile-nextgen/compiled').mkdir(parents=True)
            shutil.copy2(INPUT/'compile-nextgen-final/result.json',BUILD/'compile-nextgen/result.json')
            shutil.copy2(INPUT/'compile-nextgen-final/compiled/blob.rsblob',BUILD/'compile-nextgen/compiled/blob.rsblob')


def finish(part,mod,report):
    package=part/'package'
    path=package/'Mods'/mod/'info.json'
    info=json.loads(path.read_text('utf8'))
    info.update(version='0.9.0',nativeGameplayVerified=False,deckExchange=True,
                consoleCommands=True,reduxInventoryCompatibility=True,embeddedCleaner=True)
    path.write_text(json.dumps(info,ensure_ascii=False,indent=2),'utf8')
    docs=package/'BetaGwentDocs';docs.mkdir(exist_ok=True)
    for name in ['README_PREVIEW_RU.md','README_0.8.2_RC_RU.txt','UPDATE.md']:
        stale=docs/name
        if stale.exists():stale.unlink()  # Only copied docs in this owned candidate.
    for lang in ['EN','RU']:
        public=ROOT/'docs/releases/0.9.0/nexus'/lang.lower()
        shutil.copy2(public/'description.md',docs/f'README_{lang}.md')
        shutil.copy2(public/'changelog.md',docs/f'CHANGELOG_{lang}.md')
        shutil.copy2(ROOT/f'docs/releases/0.9.0_CLEANUP_{lang}.md',docs/f'CLEANUP_{lang}.md')
    shutil.copy2(ROOT/'tools/features082/Copy-Deck-Code.cmd',package/'Copy-Deck-Code.cmd')
    shutil.copy2(ROOT/'tools/features082/Copy-Deck-Code.ps1',docs/'Copy-Deck-Code.ps1')
    shutil.copy2(ROOT/'tools/features082/save_fact_index.py',docs/'save_fact_index.py')
    report.update(version='0.9.0',candidate=True,gameplayVerified=False,saveFilesModified=False,
                  embeddedCleaner=True,osClipboardInGameVerified=False,nativeSaveRoundTripVerified=False,
                  classicLocaleLoadingFixVerifiedInGame=False,
                  isengrimRegressionChecks=150,tacticalScenarios=1426)
    if part.name=='classic':
        locale=json.loads((INPUT/'classic-languages-fixed/verification.json').read_text('utf8'))
        assert len(locale['locales'])==13
        for row in locale['locales']:
            resource=part/'resources/gameplay/gui_new/swf/betagwenttext'/(row['locale']+'.redswf')
            assert sha(resource)==row['sha256'],row['locale']
        report['localeResourcesReexported']=13
    (part/'release-verification.json').write_text(json.dumps(report,indent=2),'utf8')
    (docs/'BuildInfo.json').write_text(json.dumps(report,indent=2),'utf8')
    for stale in package.glob('manifest-*.json'):stale.unlink()
    files=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p))
           for p in sorted(package.rglob('*')) if p.is_file()]
    manifest=dict(version='0.9.0',platform=report['platform'],files=files,nativeGameplayVerified=False)
    (package/'manifest-0.9.0.json').write_text(json.dumps(manifest,indent=2),'utf8')
    destination=BUILD/'archives';destination.mkdir(exist_ok=True)
    name='GwentBetaClassic-0.9.0-'+report['platform']+'-AllLanguages.zip'
    archive=destination/name
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(package.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(package).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    digest=sha(archive)
    archive.with_suffix('.zip.sha256').write_text(digest+'  '+name+'\n','ascii')
    (part/'archive.json').write_text(json.dumps(dict(path=str(archive),bytes=archive.stat().st_size,sha256=digest),indent=2),'utf8')
    print(json.dumps(dict(platform=report['platform'],candidate=str(archive),bytes=archive.stat().st_size)),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('platform',choices=['classic','nextgen'])
    args=parser.parse_args()
    pack.BUILD=BUILD;pack.VERSION='0.9.0'
    pack.CLASSIC_COMPILE=ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release090-final-fixed-unrestricted/result.json'
    pack.finish=finish
    prepare(args.platform)
    getattr(pack,args.platform)()


if __name__=='__main__':main()

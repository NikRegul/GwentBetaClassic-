"""Verify final 0.4.0 artifacts, fresh native sources and comparison evidence."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text('utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    evidence=ROOT/'docs/evidence'
    menus=read(evidence/'stage119-completion.json')
    assert len(menus['menus'])==8
    assert all(m['bindings']==46 and sha(Path(m['resource']))==m['sha256'] for m in menus['menus'])
    for name,digest in menus['sources'].items():
        assert sha(ROOT/'BetaGwent/ui/src'/name)==digest, name
    checks=read(evidence/'stage119-final-archetypes.json')
    assert checks['profiles']==46 and checks['checks']>=534
    comparison=read(ROOT/'BetaGwent/training/comparison119-release/report.json')
    assert comparison['completedGames']==comparison['plannedGames']==184 and comparison['errors']==0
    assert len(comparison['perDeck'])==46
    result={'stage':119,'version':'0.4.0','nativeMenus':8,'bindingsPerMenu':46,'archetypeChecks':checks['checks'],
        'archetypes':46,'comparisonGames':184,'candidateWins':comparison['wins'],'baselineWins':comparison['losses'],
        'draws':comparison['draws'],'errors':0,'confirmedBetter':comparison['confirmedBetter'],
        'gameRuntimeVerified':False,'retailInstallationModified':False,'packages':[]}
    for language in ('ru','en'):
        build=ROOT/f'BetaGwent/build/board-compile119{language}-release'
        compile=read(build/'result.json')
        assert compile['exitCode']==0 and not compile['timedOut'] and compile['patchSourcesUnchangedDuringCompile']
        assert 'Success! Patch scripts blob saved' in (build/'stdout.txt').read_text('utf8',errors='replace')
        for artifact in compile['artifacts']:assert sha(Path(artifact['path'])).upper()==artifact['sha256']
        project=ROOT/f'BetaGwent/build/release119/{language}/project/BetaGwent0924/workspace/scripts'
        for source in compile['patchSourcesBefore']:assert sha(project/source['path'])==source['sha256'], source['path']
        assert len(compile['patchSourcesBefore'])==67
        release=read(evidence/f'stage119-release-{language}.json');archive=Path(release['archive'])
        assert release['version']=='0.4.0' and release['archiveVerified'] and sha(archive)==release['archiveSha256']
        with zipfile.ZipFile(archive) as zipped:
            assert zipped.testzip() is None
            for item in release['files']:assert hashlib.sha256(zipped.read(item['path'])).hexdigest()==item['sha256'],item['path']
            assert all(name in zipped.namelist() for name in ('UPDATE.md','LICENSE','SOURCE.txt'))
        result['packages'].append({'language':language,'archive':str(archive),'bytes':archive.stat().st_size,
            'sha256':release['archiveSha256'],'freshCompiledSources':67,'crcAndManifestVerified':True})
    previous=ROOT/'BetaGwent/release/GwentBetaClassic-0.3.5-preview.5-RU.zip'
    assert sha(previous)=='b26a68e39d18de9285908cbb5c427d6534b9f3861b311ecd4d6afe973fadba9d'
    result['previousPreviewUnmodified']=True
    (evidence/'stage119-final-release.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

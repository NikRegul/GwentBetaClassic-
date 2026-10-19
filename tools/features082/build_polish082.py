from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).parent))
import build_release as build
revision=sys.argv[2] if len(sys.argv)>2 else 'polish1'
assert revision in ['polish1','polish2']
build.BUILD=build.ROOT/('BetaGwent/build/release082-'+revision);build.VERSION='0.8.2-'+revision
build.CLASSIC_COMPILE=build.ROOT/('BetaGwent/build/universal081/classic-runtime/runs/release082-polish2-phase-native/result.json' if revision=='polish2' else 'BetaGwent/build/universal081/classic-runtime/runs/release082-polish1-native/result.json')
original=build.finish
def finish(part,mod,report):
    # Ship current publication/install notes and generate a fresh hash manifest.
    docs=part/'package/BetaGwentDocs';docs.mkdir(exist_ok=True)
    for lang in ['ru','en']:
        source=build.ROOT/'docs/releases/0.8.2-polish1/nexus'/lang
        for name,target in [('description.md','README_'+lang.upper()+'.md'),('changelog.md','CHANGELOG_'+lang.upper()+'.md')]:shutil.copy2(source/name,docs/target)
    for p in (part/'package').glob('manifest-*.json'):p.unlink()
    original(part,mod,report)
build.finish=finish
if __name__=='__main__':{'classic':build.classic,'nextgen':build.nextgen}[sys.argv[1]]()

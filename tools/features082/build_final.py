"""Freeze and rebuild 0.8.2 from the final RC3 source revision."""
from pathlib import Path
import hashlib,json,shutil,sys
import build_release as build

ROOT=build.ROOT
BUILD=ROOT/'BetaGwent/build/release082-final'
SOURCE=ROOT/'BetaGwent/build/release082-rc3-ready'
build.BUILD=BUILD
build.VERSION='0.8.2'
build.CLASSIC_COMPILE=ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release082-final-native/result.json'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def prepare():
    assert not BUILD.exists(),'Use a fresh directory; completed sources are immutable'
    BUILD.mkdir()
    for name in ['scripts','redux','classic-prepared','classic-audit']:
        shutil.copytree(SOURCE/name,BUILD/name)
    for platform in ['classic','nextgen']:
        part=BUILD/platform;part.mkdir()
        for name in ['ui','extra-resources']:shutil.copytree(SOURCE/platform/name,part/name)
        shutil.copy2(SOURCE/platform/'ui-inputs.json',part/'ui-inputs.json')
    shutil.copy2(SOURCE/'classic/subimages.json',BUILD/'classic/subimages.json')
    for name in ['exchange-languages.json','exchange-fonts.json','font-code-tables.json']:
        p=SOURCE/name
        if p.exists():shutil.copy2(p,BUILD/name)
    records={}
    for part in ['scripts','classic-prepared','classic/ui','nextgen/ui','redux','classic/extra-resources','nextgen/extra-resources']:
        for p in (BUILD/part).rglob('*'):
            if p.is_file():
                rel=p.relative_to(BUILD)
                assert sha(p)==sha(SOURCE/rel)
                records[rel.as_posix()]=sha(p)
    (BUILD/'source-freeze.json').write_text(json.dumps(dict(version='0.8.2',source=str(SOURCE),files=records,sourceCodeChanges=False),indent=2),'utf8')
    print('Frozen',len(records),'files; UI and scripts exactly match final RC3 sources.')

if __name__=='__main__':
    {'prepare':prepare,'nextgen':build.nextgen,'classic':build.classic}[sys.argv[1]]()

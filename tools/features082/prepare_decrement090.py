"""Avoid the Number declocal opcode implicated by the Classic failure dump."""
from pathlib import Path
import shutil,json,hashlib

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release090-integrated'
OUT=ROOT/'BetaGwent/build/release090-decrement-fix'
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']


def main():
    assert not OUT.exists()
    reports=[]
    for platform in ['classic','nextgen']:
        target=OUT/platform;target.mkdir(parents=True)
        shutil.copytree(SOURCE/platform/'ui',target/'ui')
        for folder in COPIES:
            path=target/'ui'/folder/'BetaGwentTextLanguage.as'
            raw=path.read_bytes();text=raw.decode('utf-8-sig')
            assert text.count('size--;')==3,path
            text=text.replace('size--;','size=Math.max(Number(spec.minimum),size-1);')
            path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
        manifest=json.loads((SOURCE/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(SOURCE/'classic/subimages.json',target/'subimages.json')
        reports.append(dict(platform=platform,replacements=15,sourceUnchanged=True))
    # Keep the maintained UI mirrors aligned; frozen integrated inputs stay intact.
    for folder in COPIES:
        shutil.copy2(OUT/'nextgen/ui'/folder/'BetaGwentTextLanguage.as',ROOT/'BetaGwent/ui'/folder/'BetaGwentTextLanguage.as')
    (OUT/'preparation.json').write_text(json.dumps(dict(candidate=True,nativeGameplayVerified=False,reason='Classic crash stack enters numeric local decrement conversion; only layoutButton emits Number declocal',platforms=reports),indent=2),'utf8')
    print('Prepared both platform sources, 5 mirrors each; gameplay unverified.')


if __name__=='__main__':main()

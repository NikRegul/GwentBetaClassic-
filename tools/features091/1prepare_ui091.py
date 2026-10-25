"""Apply reviewed UI and glossary changes to the accepted platform-specific UI."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import UI_BASELINE
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
NAMES=['BetaGwentBoard.as','BetaGwentController.as','BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentBanners090.as']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert not out.exists()
    before=UI_BASELINE/'nextgen/ui/src'
    current=ROOT/'BetaGwent/ui/src'
    changes={}
    for name in NAMES:
        if not (before/name).exists():
            changes[name]=None
            continue
        old=(before/name).read_text('utf-8-sig');new=(current/name).read_text('utf-8-sig')
        aa=old.splitlines(True);bb=new.splitlines(True)
        changes[name]=[(''.join(aa[g[0][1]:g[-1][2]]),''.join(bb[g[0][3]:g[-1][4]])) for g in difflib.SequenceMatcher(None,aa,bb,autojunk=False).get_grouped_opcodes(3)]
        assert changes[name]
    for platform in ['classic','nextgen']:
        source=UI_BASELINE/platform;target=out/platform
        shutil.copytree(source/'ui',target/'ui')
        for name in NAMES:
            if changes[name] is None:
                raw=(current/name).read_bytes().decode('utf-8-sig').replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
                for folder in COPIES:(target/'ui'/folder/name).write_bytes(b'\xef\xbb\xbf'+raw)
                continue
            text=(target/'ui/src'/name).read_text('utf-8-sig')
            for old,new in changes[name]:
                assert text.count(old)==1,(platform,name,old[:100])
                text=text.replace(old,new,1)
            raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
            for folder in COPIES:(target/'ui'/folder/name).write_bytes(raw)
            assert len({sha(target/'ui'/c/name) for c in COPIES})==1
            assert b'\n' not in raw.replace(b'\r\n',b'')
        manifest=json.loads((source/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={f.name:sha(f) for f in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(source/'subimages.json',target/'subimages.json')
    (out/'gamepad-source.json').write_text(json.dumps({n:sha(current/n) for n in NAMES},indent=2),'utf8')
    print('Prepared gamepad fixes for both platforms, five BOM/CRLF copies each.')

if __name__=='__main__':main()

"""Apply reviewed UI and glossary changes to the accepted platform-specific UI."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import UI_BASELINE
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
NAMES=['BetaGwentBoard.as','BetaGwentController.as','BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentBanners090.as','BetaGwentReleaseText093.as']

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
            if platform=='classic' and name=='BetaGwentBoard.as':
                # Reviewed three-way merge of Classic baseline, NextGen baseline,
                # and current UI; preserve Classic languageButton implementation.
                assert sha(source/'ui/src'/name)=='635f40a29b99122eec42226dc660b408ace05e42a7ffadb12bdbe8df7f0d94c2', 'Classic UI baseline changed'
                assert sha(before/name)=='55d098620f500e3a61f229fc04b76d13ddd1fd9a601a7efea6c9b51a007d70d3', 'NextGen UI baseline changed'
                assert sha(current/name)=='f2e2f454ae4c66c0ac7cc1698cbddd2e90bc52c3c1fcfeed97c143a9fbc4c01c', 'Updated UI source changed'
                overlay=Path(__file__).with_name('BetaGwentBoard_classic093.as')
                assert overlay.is_file(), 'Missing reviewed Classic board UI overlay'
                assert sha(overlay)=='2988a25c8e7ba5e407b58c565eae0a159bba02b45c2a4c5b232adcfe274f0097', 'Classic UI overlay changed'
                text=overlay.read_text('utf-8-sig')
            else:
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

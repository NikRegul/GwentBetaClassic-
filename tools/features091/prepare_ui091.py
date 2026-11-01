"""Apply reviewed UI and glossary changes to the accepted platform-specific UI."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import UI_BASELINE
sys.path.insert(0,str(Path(__file__).resolve().parent))
import editor_vfx094
sys.path.insert(0,str(ROOT/'tools/ui'))
import window_art098
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
NAMES=['BetaGwentBoard.as','BetaGwentController.as','BetaGwentCardText.as','BetaGwentRelated091.as','BetaGwentBanners090.as','BetaGwentReleaseText093.as',
       'BetaGwentElementArt164.as','BetaGwentEditorFx094.as','BetaGwentEditorFxData094.as','BetaGwentEditorValid095.as','BetaGwentEditorValidData095.as','BetaGwentEditorChrome096.as','BetaGwentEditorSlot096.as','BetaGwentEditorSlotData096.as','BetaGwentPassCoin096.as','BetaGwentUiText096.as','BetaGwentTextLanguage.as','BetaGwentWindowArt098.as']

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
                assert sha(current/name)=='96c78c18779f2446402f0ccebd1179072c246923659e8a68b197d0e5a344b253', 'Updated UI source changed'
                overlay=Path(__file__).with_name('BetaGwentBoard_classic093.as')
                assert overlay.is_file(), 'Missing reviewed Classic board UI overlay'
                assert sha(overlay)=='00cd653fc2f691990c4b8677361798c6fd9fe9c44dcd2a784c4079f27fa9ae5b', 'Classic UI overlay changed'
                text=overlay.read_text('utf-8-sig')
            else:
                for old,new in changes[name]:
                    assert text.count(old)==1,(platform,name,old[:100])
                    text=text.replace(old,new,1)
            raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
            for folder in COPIES:(target/'ui'/folder/name).write_bytes(raw)
            assert len({sha(target/'ui'/c/name) for c in COPIES})==1
            assert b'\n' not in raw.replace(b'\r\n',b'')
        # 0.9.4a: Beta deck-editor add/remove frames (extended Elements atlas;
        # Classic also gets native DefineSubImage cell classes).
        vfx=editor_vfx094.prepare(target/'ui',platform,source)
        assert vfx,'Missing reviewed editor effect atlas (data/beta924/design/editor_vfx094.json)'
        window_art098.prepare(target/'ui',platform,source)
        manifest=json.loads((source/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={f.name:sha(f) for f in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(source/'subimages.json',target/'subimages.json')
    (out/'gamepad-source.json').write_text(json.dumps({n:sha(current/n) for n in NAMES},indent=2),'utf8')
    print('Prepared gamepad fixes for both platforms, five BOM/CRLF copies each.')

if __name__=='__main__':main()

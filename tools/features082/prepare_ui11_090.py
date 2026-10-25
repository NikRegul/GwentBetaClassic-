"""0.9.0 release UI fix for Classic 1.32 (release090-ui10 -> release090-ui11).

1.32 opens only menu names from the stock guiconfig, so the Classic keg menu is the
stock TestMenu (r4test.menu / panel_test.redswf, package_classic132keg090.py). Its
movie must register under that name: the engine calls OnConfigUI only for
registerMenu(<the requested name>). Build 15 showed it: panel_test and all nine keg
texture pages loaded, the movie registered as "BetaGwentKeg" and the menu was closed
without OnConfigUI.

Classic only: BetaGwentKegMenu registers as "TestMenu"; the three keg checks in
BetaGwentBoard use isKegMenu() instead of comparing the name. Next-Gen is copied
unchanged (menus included). All five Classic copies stay identical, UTF-8 BOM + CRLF.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from prepare_ui7_090 import ROOT, COPIES, replace, write

SOURCE = ROOT / 'BetaGwent/build/release090-ui10'
OUT = ROOT / 'BetaGwent/build/release090-ui11'
NL = '\n'


def board(s):
    s = replace(s, 'if(registrationName()=="DeckBuilder"||registrationName()=="BetaGwentKeg")entryMode=1;',
                'if(registrationName()=="DeckBuilder"||isKegMenu())entryMode=1;')
    s = replace(s, 'if(registrationName()=="BetaGwentKeg")send("OnBetaGwentBoardClose",[]);else render();',
                'if(isKegMenu())send("OnBetaGwentBoardClose",[]);else render();')
    s = replace(s, 'BetaGwentHDArt.has(BetaGwentKeg109.FRAME0)&&registrationName()=="BetaGwentKeg"?0:1;',
                'BetaGwentHDArt.has(BetaGwentKeg109.FRAME0)&&isKegMenu()?0:1;')
    s = replace(s, '        protected function registrationName():String { return "BetaGwentBoard"; }' + NL,
                '        protected function registrationName():String { return "BetaGwentBoard"; }' + NL +
                '        // Keg reward movie. Classic 1.32 registers it as the stock TestMenu.' + NL +
                '        protected function isKegMenu():Boolean { return false; }' + NL)
    assert 'registrationName()=="BetaGwentKeg"' not in s
    return s


def keg(s):
    s = replace(s, '    // Stage 109: keg-opening menu (guiconfig BetaGwentKeg -> betagwent\\betagwent_kegop.menu).',
                '    // Stage 109: keg-opening menu. Classic 1.32: stock TestMenu -> gameplay\\gui_new\\guirsrc\\r4test.menu' + NL +
                '    // (1.32 opens only names from the stock guiconfig; registerMenu must use the requested name).')
    s = replace(s, 'override protected function registrationName():String { return "BetaGwentKeg"; }',
                'override protected function registrationName():String { return "TestMenu"; }' + NL +
                '        override protected function isKegMenu():Boolean { return true; }')
    return s


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args(); out = args.out.resolve(); assert not out.exists()
    out.mkdir(parents=True)
    shutil.copytree(args.source / 'nextgen', out / 'nextgen')
    target = out / 'classic'; target.mkdir()
    shutil.copytree(args.source / 'classic/ui', target / 'ui')
    src = target / 'ui/src'
    for name, fix in [('BetaGwentBoard.as', board), ('BetaGwentKegMenu.as', keg)]:
        p = src / name; write(p, fix(p.read_text('utf-8-sig')))
        for folder in COPIES:
            if folder != 'src' and (target / 'ui' / folder).is_dir(): shutil.copy2(p, target / 'ui' / folder / name)
    for name in ['BetaGwentBoard.as', 'BetaGwentKegMenu.as']:
        digests = {hashlib.sha256((target / 'ui' / f / name).read_bytes()).hexdigest() for f in COPIES if (target / 'ui' / f).is_dir()}
        raw = (src / name).read_bytes()
        assert len(digests) == 1 and raw.startswith(b'\xef\xbb\xbf') and b'\r\n' in raw and b'\n' not in raw.replace(b'\r\n', b''), name
    manifest = json.loads((args.source / 'classic/ui-inputs.json').read_text('utf8'))
    manifest['sources'] = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in src.glob('*.as')}
    (target / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    shutil.copy2(args.source / 'classic/subimages.json', target / 'subimages.json')
    print('Prepared release UI 11: Classic keg movie registers as TestMenu; Next-Gen unchanged.')


if __name__ == '__main__':
    main()

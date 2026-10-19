"""0.9.0 release UI (release090-ui8 -> release090-ui9).

* Removes the visible "banner: ..." test text (build 6 diagnostic): a failed
  banner page keeps the normal small flag and only writes a trace line.
* Import/Export buttons are shown only when the Optional-CopyButton bridge
  answers its side-effect-free probe (betagwent:windows-clipboard-v1); the
  result is cached per board. Without bin both buttons are hidden.
Deck list alignment and IMPORT_TRACE log lines from build 8 are kept.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from prepare_ui7_090 import ROOT, COPIES, replace, write

SOURCE = ROOT / 'BetaGwent/build/release090-ui8'
OUT = ROOT / 'BetaGwent/build/release090-ui9'
NL = '\n'


def board(s):
    a = s.index('            var diagnose:Function=function():void{')
    b = s.index('            };', a) + len('            };')
    s = s[:a] + ('            var diagnose:Function=function():void{' + NL +
                 '                // Log only: the complete small face stays as the fallback.' + NL +
                 '                trace("UI_ERROR banner_fallback="+BetaGwentBanners090.lastError);' + NL +
                 '            };') + s[b:]
    assert '"banner: "' not in s
    return bridge_gate(s)


def bridge_gate(s):
    s = replace(s, '        private function copyExchange():Boolean' + NL,
                '        private var nativeClipboard090:int=-1;' + NL +
                '        // Import/Export need the Optional-CopyButton bridge; without it both are hidden.' + NL +
                '        private function hasNativeClipboard090():Boolean' + NL +
                '        {' + NL +
                '            if(nativeClipboard090<0){' + NL +
                '                nativeClipboard090=0;' + NL +
                '                try{var probeClass:Object=getDefinitionByName("flash.desktop.Clipboard");if(probeClass.generalClipboard.setData("betagwent:windows-clipboard-v1",""))nativeClipboard090=1;}catch(probeError:Error){}' + NL +
                '            }' + NL +
                '            return nativeClipboard090==1;' + NL +
                '        }' + NL +
                '        private function copyExchange():Boolean' + NL)
    s = replace(s, '        private function drawDeckExchangeButtons():void' + NL + '        {' + NL,
                '        private function drawDeckExchangeButtons():void' + NL + '        {' + NL +
                '            if(!hasNativeClipboard090())return;' + NL)
    s = replace(s, '            if(!ready||nameOpen||!(selectingDecks||editingDeck)||(!importing&&!editingDeck))return;' + NL,
                '            if(!ready||nameOpen||!(selectingDecks||editingDeck)||(!importing&&!editingDeck))return;' + NL +
                '            if(!hasNativeClipboard090())return;' + NL)
    assert s.count('hasNativeClipboard090()') == 3
    return s


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args(); out = args.out.resolve(); assert not out.exists()
    for platform in ['classic', 'nextgen']:
        target = out / platform; target.mkdir(parents=True)
        shutil.copytree(args.source / platform / 'ui', target / 'ui')
        p = target / 'ui/src/BetaGwentBoard.as'; write(p, board(p.read_text('utf-8-sig')))
        for folder in COPIES:
            if folder != 'src' and (target / 'ui' / folder).is_dir(): shutil.copy2(p, target / 'ui' / folder / p.name)
            if platform == 'nextgen' and (ROOT / 'BetaGwent/ui' / folder).is_dir(): shutil.copy2(p, ROOT / 'BetaGwent/ui' / folder / p.name)
        manifest = json.loads((args.source / platform / 'ui-inputs.json').read_text('utf8'))
        manifest['sources'] = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in (target / 'ui/src').glob('*.as')}
        (target / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
        if platform == 'classic': shutil.copy2(args.source / 'classic/subimages.json', target / 'subimages.json')
    print('Prepared release UI: no visible banner diagnostics, Import/Export only with bin.')


if __name__ == '__main__':
    main()

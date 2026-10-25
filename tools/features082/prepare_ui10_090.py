"""0.9.0 release UI fix (release090-ui9 -> release090-ui10).

Deck screens (deck choice, editor, catalog) show the large Beta card in the
right panel. Build 7 placed it at x=1580 with w=260 and moved the title and
ability block with it, so the card left its slot and the text drifted right.
Now the title/ability block keeps the battle-preview position (centred in the
panel) and the large card (w=240) is centred in the same slot; its faction
banner overhangs to the left/top inside the panel.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from prepare_ui7_090 import ROOT, COPIES, replace, write

SOURCE = ROOT / 'BetaGwent/build/release090-ui9'
OUT = ROOT / 'BetaGwent/build/release090-ui10'
NL = '\n'


def board(s):
    a = s.index('        private function drawBetaSidePreview(')
    b = s.index('        private function ', a + 10)
    body = s[a:b]
    body = replace(body, 'var w:Number=big?260:312,h:Number=Math.round(big?260/BETA_LARGE_CARD_ASPECT:312/BETA_CARD_ASPECT);',
                   'var w:Number=big?240:312,h:Number=Math.round(big?240/BETA_LARGE_CARD_ASPECT:312/BETA_CARD_ASPECT);')
    body = replace(body, 'var previewX:Number=big?1580:1477+(405-w)/2;',
                   '// Title/ability block keeps the panel position; the large card is centred in the same slot.' + NL +
                   '            var previewX:Number=1477+(405-312)/2,cardX:Number=1477+(405-w)/2;')
    body = replace(body, 'var card:Sprite=new Sprite();card.x=previewX;', 'var card:Sprite=new Sprite();card.x=cardX;')
    body = replace(body, 'animations.push({sprite:card,fromX:previewX+24,fromY:card.y,toX:previewX,',
                   'animations.push({sprite:card,fromX:cardX+24,fromY:card.y,toX:cardX,')
    body = replace(body, 'card.x=previewX+24;card.alpha=0;', 'card.x=cardX+24;card.alpha=0;')
    assert 'card.x=previewX' not in body and '1580' not in body
    return s[:a] + body + s[b:]


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
    print('Prepared release UI 10: deck-screen card centred in its slot, text block back in place.')


if __name__ == '__main__':
    main()

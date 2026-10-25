"""Align large-card strength with the original Beta faction ornaments.

The user's screenshots are visual references only. All bitmap pages and glyphs
remain original Beta assets. In particular, keep the restored Nilfgaard Gold
sun rays: DATA's pixel dimensions describe a transform, never a crop rectangle.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
COPIES = ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']
NAMES = ['BetaGwentBoard.as', 'BetaGwentBanners090.as']
# Centres of the empty number areas in the original rasterized banner pages.
# Bronze and Silver share mesh geometry. Gold has a separate ornament.
ANCHORS = {
    'Neutral': [(135, 120), (195, 182)],
    'Monsters': [(145, 130), (173, 175)],
    'Nilfgaard': [(140, 140), (181, 184)],
    'Northern': [(100, 110), (158, 194)],
    'Scoiatael': [(165, 130), (189, 179)],
    'Skellige': [(150, 140), (233, 190)],
}
# Visible ink centres in card fractions; the Gwent Numbers font has substantial
# bearings, so layoutBigPower090 still centres the glyph ink, not the text box.
CENTRES = {'Neutral': (.030, .092), 'Monsters': (.045, .092),
           'Nilfgaard': (.025, .088), 'Northern': (.030, .090),
           'Scoiatael': (.032, .085), 'Skellige': (.025, .085)}
SCALE = .92
# The smaller em and ink centres belong to the Bronze/Silver artwork, not to
# Gold's larger ornament. These are source-page pixels, so the banner itself
# does not need to move when the strength is corrected.
NON_GOLD_ANCHORS = {'Neutral': (135, 120), 'Monsters': (165, 130),
                    'Nilfgaard': (138, 140), 'Northern': (94, 110),
                    'Scoiatael': (190, 130), 'Skellige': (150, 140)}
NON_GOLD_EM = .115


def non_gold_numbers(banner, board):
    data = json.loads(re.search(r'DATA:Object=(.*);', banner)[1])
    slots = json.loads(re.search(r'SLOTS:Object=(.*);', banner)[1])
    gold = {k: list(v) for k, v in slots.items() if k.endswith('_Gold')}
    for key, row in data.items():
        faction, tier = key.split('_')
        if tier == 'Gold':
            continue
        x, y = NON_GOLD_ANCHORS[faction]
        slots[key] = [round(row[0] + x * row[2] / row[4], 9),
                      round(row[1] + y * row[3] / row[5], 9), NON_GOLD_EM]
    assert gold == {k: v for k, v in slots.items() if k.endswith('_Gold')}
    banner = re.sub(r'SLOTS:Object=.*;', 'SLOTS:Object=' + json.dumps(slots, separators=(',', ':')) + ';', banner)
    old = 'Math.round(h*.16)'
    new = 'Math.round(h*(slot.length>2?Number(slot[2]):.16))'
    if new not in board:
        assert board.count(old) == 1
        board = board.replace(old, new)
    return banner, board


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, s):
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


def patch(banner, board):
    if 'Reference-aligned strength slots' in banner or 'Strength ink centre X/Y' in banner:
        return non_gold_numbers(banner, board)
    match = re.search(r'DATA:Object=(.*);', banner)
    data = json.loads(match[1])
    slots = {}
    for key, row in data.items():
        faction, tier = key.split('_')
        anchor = ANCHORS[faction][tier == 'Gold']
        centre = CENTRES[faction]
        if key == 'Neutral_Bronze' or key == 'Neutral_Silver':
            centre = (.030, .095)
        sx, sy = row[2] * SCALE / row[4], row[3] * SCALE / row[5]
        # Preserve the native page's full extent, including rays outside the
        # historical nominal px width of Nilfgaard_Gold.
        row[:4] = [round(centre[0] - anchor[0] * sx, 9),
                   round(centre[1] - anchor[1] * sy, 9),
                   round(row[2] * SCALE, 9), round(row[3] * SCALE, 9)]
        slots[key] = list(centre)
    banner = banner[:match.start(1)] + json.dumps(data, separators=(',', ':')) + banner[match.end(1):]
    banner = re.sub(r'SLOTS:Object=.*;', 'SLOTS:Object=' + json.dumps(slots, separators=(',', ':')) + ';', banner)
    banner = banner.replace('// Centre of the power number on each banner (card fractions).',
                            '// Reference-aligned strength slots: all six factions and three tiers.')
    assert banner.count('return s?s:[-0.035, 0.06]') == 1
    banner = banner.replace('return s?s:[-0.035, 0.06]', 'return s?s:SLOTS["Neutral_Bronze"]')
    assert board.count('Math.round(h*.115)') == 1
    # Gwent Numbers ink is about 0.52 of the em square: .16 em/card-height
    # produces the ~.084 ink/card-height seen in Beta's detailed card view.
    board = board.replace('Math.round(h*.115)', 'Math.round(h*.16)')
    return non_gold_numbers(banner, board)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    out = args.out.resolve()
    assert out.is_relative_to(ROOT / 'BetaGwent/build') and not out.exists()
    out.mkdir(parents=True)
    canonical = ROOT / 'BetaGwent/ui'
    before = out / 'before'
    for folder in COPIES:
        (before / folder).mkdir(parents=True)
        for name in NAMES:
            shutil.copy2(canonical / folder / name, before / folder / name)
    banner, board = patch((canonical / 'src' / NAMES[1]).read_text('utf-8-sig'),
                          (canonical / 'src' / NAMES[0]).read_text('utf-8-sig'))
    for folder in COPIES:
        write(canonical / folder / NAMES[0], board)
        write(canonical / folder / NAMES[1], banner)
    # Apply the current canonical UI changes to the platform-specific baseline.
    # Copying build-inputs/ui alone would omit current related-card/controller
    # changes. The established release preparer preserves Classic-only code.
    subprocess.run([sys.executable, str(ROOT / 'tools/features091/prepare_ui091.py'),
                    '--out', str(out / 'sources')], cwd=ROOT, check=True)
    report = dict(scale=SCALE, anchors=ANCHORS, centres=CENTRES, nonGoldNumberAnchors=NON_GOLD_ANCHORS,
                  nonGoldEm=NON_GOLD_EM, screenshotsUsedAsAssets=False,
                  originalBannerPagesModified=False, sources={n: sha(canonical / 'src' / n) for n in NAMES})
    (out / 'source-change.json').write_text(json.dumps(report, indent=2), 'utf8')
    print('Prepared strength placement for both platforms and five canonical source copies:', out)


if __name__ == '__main__':
    main()

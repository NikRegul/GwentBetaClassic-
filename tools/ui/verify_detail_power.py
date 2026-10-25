"""Check final menu budgets and the untouched original native banner pixels."""
from pathlib import Path
import argparse
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/classic132'))
from formats import Resource


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, default=ROOT / 'BetaGwent/build/detail-power-tierfix-20261023')
    a = p.parse_args()
    report = json.loads((a.build / 'ui-patch/manifest.json').read_text('utf8'))
    results = {}
    for version, key in [('1.32', 'classic'), ('5.0+', 'nextgen')]:
        rows = report['platforms'][version]['menus']
        assert len(rows) == 4
        for row in rows:
            assert row['nativeTextureChunksPreserved'] and row['imageDefinitionsPreserved']
            assert row['bytes'] < (32 if key == 'classic' else 65) * 1024**2
        folder = a.build / 'ui-patch' / key / 'resources/gameplay/gui_new/swf/betagwentbanners'
        assert len(list(folder.glob('*.redswf'))) == 18
        for path in folder.glob('*.redswf'):
            faction, tier = path.stem.split('_')
            faction = next(n for n in ['Neutral', 'Monsters', 'Nilfgaard', 'Northern', 'Scoiatael', 'Skellige'] if n.lower() == faction)
            dds = ROOT / 'BetaGwent/build/banners090-rays-input' / (faction + '_' + tier.title() + '.dds')
            resource = Resource(path.read_bytes())
            _, pos = resource.properties(resource.chunks[1])
            tail = resource.chunks[1][pos:]
            pixels = tail[28:] if key == 'classic' else tail[24:-4]
            assert pixels == dds.read_bytes()[128:], 'Original banner pixels changed: ' + str(path)
        results[key] = dict(menus=4, largestMenuBytes=max(m['bytes'] for m in rows),
                            all18OriginalBannerPagesIdentical=True, goldNilfgaardRaysPreserved=True)
    # Only the requested two canonical files changed during this task.
    original = a.build / 'before/src'
    before = (original / 'BetaGwentBoard.as').read_bytes()
    after = (ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as').read_bytes()
    new = b'Math.round(h*(slot.length>2?Number(slot[2]):.16))'
    expected = before.replace(b'Math.round(h*.115)', new).replace(b'Math.round(h*.16)', new)
    assert expected == after
    old_banner = (original / 'BetaGwentBanners090.as').read_text('utf-8-sig')
    new_banner = (ROOT / 'BetaGwent/ui/src/BetaGwentBanners090.as').read_text('utf-8-sig')
    tables = lambda s, name: json.loads(re.search(name + r':Object=(.*);', s)[1])
    assert tables(old_banner, 'DATA') == tables(new_banner, 'DATA'), 'Banner placement changed'
    old_slots, new_slots = tables(old_banner, 'SLOTS'), tables(new_banner, 'SLOTS')
    for key in old_slots:
        if key.endswith('_Gold'):
            assert old_slots[key] == new_slots[key], 'Accepted Gold strength changed'
    for name in ['BetaGwentBoard.as', 'BetaGwentBanners090.as']:
        expected = (ROOT / 'BetaGwent/ui/src' / name).read_bytes()
        for copy in ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']:
            raw = (ROOT / 'BetaGwent/ui' / copy / name).read_bytes()
            assert raw == expected and raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n', b'')
    output = dict(platforms=results, canonicalBoardChangeLimitedToStrengthEmSelection=True,
                  allBannerTransformsPreserved=True, acceptedGoldPreserved=True,
                  sourceAndNativePixelChecksPassed=True, screenshotsUsedAsAssets=False, inGameVerified=False)
    (a.build / 'verification.json').write_text(json.dumps(output, indent=2), 'utf8')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()

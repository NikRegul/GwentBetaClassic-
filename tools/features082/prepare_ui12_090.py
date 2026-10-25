"""0.9.0 Classic keg menu art (release090-ui11 -> release090-ui12).

On 1.32 the keg menu opened (build 16) with a black screen: cards were visible, but the
keg scene, background, troll flipbook and keg backs (HDArt pages 21-31) were not. The
log shows those pages on route=atlas-fill (a scrollRect view of the whole inline page),
the same route that left the Classic deck editor without its decoration in 0.8.1 until
fix12 drew it from native DefineSubImage fragments (docs/reviews/2026-10-16-classic081-
native-subimages.md). Pages 21-31 were never given fragments.

This adds one full-slot fragment per keg slot (56): BitmapAsset classes, registry entries
in BetaGwentClassicSubImages and rows in subimages.json. package_final090 binds them to
the existing atlas images (build_classic_subimages.add_fragments); no pixels change.
Classic only; Next-Gen copied unchanged. All five Classic copies stay identical.
"""
from pathlib import Path
import argparse, hashlib, json, re, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from prepare_ui7_090 import ROOT, COPIES, write

SOURCE = ROOT / 'BetaGwent/build/release090-ui11'
OUT = ROOT / 'BetaGwent/build/release090-ui12'
KEG_PAGES = set(range(21, 32))
CLASS = '''package {
 import mx.core.BitmapAsset;
 public class %s extends BitmapAsset {
  public function %s(){super();}
 }
}
'''


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=OUT)
    parser.add_argument('--source', type=Path, default=SOURCE)
    args = parser.parse_args(); out = args.out.resolve(); assert not out.exists()
    out.mkdir(parents=True)
    shutil.copytree(args.source / 'nextgen', out / 'nextgen')
    target = out / 'classic'; target.mkdir()
    shutil.copytree(args.source / 'classic/ui', target / 'ui')
    src = target / 'ui/src'
    art = (src / 'BetaGwentHDArt.as').read_text('utf-8-sig')
    slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', art).group(1))
    embedded = {int(p) for p in re.findall(r'\] private static var Page(\d+):Class;', art)}
    assert KEG_PAGES <= embedded, sorted(KEG_PAGES - embedded)
    manifest = json.loads((args.source / 'classic/subimages.json').read_text('utf8'))
    entries = manifest['entries']; known = {r['className'] for r in entries}
    assert not any(r['page'] in KEG_PAGES for r in entries), 'keg fragments already present'
    added = []
    for key, slot in sorted(slots.items(), key=lambda kv: int(kv[0])):
        if slot[0] not in KEG_PAGES: continue
        assert all(int(v) == v for v in slot), key
        page, x, y, width, height = map(int, slot)
        name = 'BetaGwentClassicAtlas' + ('N' if int(key) < 0 else 'P') + str(abs(int(key))) + '_0'
        assert name not in known and not (src / (name + '.as')).exists(), name
        added.append(dict(id=int(key), page=page, x=x, y=y, width=width, height=height,
                          clip=[0, 0, width, height], className=name))
    assert len(added) == 56, len(added)
    registry = src / 'BetaGwentClassicSubImages.as'; text = registry.read_text('utf-8-sig')
    end = text.index('};', text.index('private static var classes:Object={'))
    lines = ''.join(',\n"%d:0:0:%d:%d":%s' % (r['id'], r['width'], r['height'], r['className']) for r in added)
    text = text[:end] + lines + text[end:]
    for folder in COPIES:
        base = target / 'ui' / folder
        if not base.is_dir(): continue
        for r in added: write(base / (r['className'] + '.as'), CLASS % (r['className'], r['className']))
        write(base / registry.name, text)
    digests = {hashlib.sha256((target / 'ui' / f / registry.name).read_bytes()).hexdigest() for f in COPIES if (target / 'ui' / f).is_dir()}
    assert len(digests) == 1
    manifest['entries'] = entries + added
    (target / 'subimages.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    inputs = json.loads((args.source / 'classic/ui-inputs.json').read_text('utf8'))
    inputs['sources'] = {q.name: hashlib.sha256(q.read_bytes()).hexdigest() for q in src.glob('*.as')}
    (target / 'ui-inputs.json').write_text(json.dumps(inputs, indent=2), 'utf8')
    print('Prepared release UI 12: %d Classic keg fragments (pages 21-31); Next-Gen unchanged.' % len(added))


if __name__ == '__main__':
    main()

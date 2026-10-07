"""Pack the original Beta ribbon crown halves (crown-{blue,red}-{1,2}) into page 13.

Read-only source: Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber/panels
(sprites used by level8 PlayerRibbon/CrownsView/CrownHalf1..2). Writes
BetaGwent/ui/assets/battle103/crowns103.png and registers ids -1540..-1543 on
page 13 in BetaGwentHDArt.as (pixel scale 1, like page 12).
"""
from pathlib import Path
import argparse, hashlib, json, os, re, sys
ROOT = Path(__file__).resolve().parents[2]
NAMES = {-1540: 'crown-blue-1', -1541: 'crown-blue-2', -1542: 'crown-red-1', -1543: 'crown-red-2'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--panels', type=Path, default=ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber/panels')
    ap.add_argument('--root', type=Path, default=ROOT)
    a = ap.parse_args()
    if os.name == 'nt':
        sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
    import UnityPy
    from PIL import Image
    env = UnityPy.load(str(a.panels))
    sprites = {o.read().m_Name: o for o in env.objects if o.type.name == 'Sprite'}
    atlas = Image.new('RGBA', (512, 256)); slots = {}; x = 0; records = []
    for ident, name in NAMES.items():
        image = sprites[name].read().image.convert('RGBA')
        atlas.paste(image, (x, 0)); slots[str(ident)] = [13, x, 0, image.width, image.height]
        records.append(dict(id=ident, name=name, pathId=sprites[name].path_id, size=list(image.size)))
        x += image.width + 2
    out = a.root / 'BetaGwent/ui/assets/battle103/crowns103.png'; out.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(out)
    source = a.root / 'BetaGwent/ui/src/BetaGwentHDArt.as'; raw = source.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw; text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text)
    bindings = json.loads(m[1]); bindings.update(slots)
    text = text[:m.start(1)] + json.dumps(bindings, separators=(',', ':')) + text[m.end(1):]
    if 'private static var Page13:Class' not in text:
        text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle103/crowns103.png",compression="true",quality="100")] private static var Page13:Class;\n private static var types:Array=')
        text = text.replace('Page11,Page12];', 'Page11,Page12,Page13];')
    text = text.replace('var pixelScale:Number=page==12?1:0.75;', 'var pixelScale:Number=page>=12?1:0.75;')
    if 'Page11,Page12,Page13];' not in text or 'page>=12?1:0.75' not in text:
        raise SystemExit('BetaGwentHDArt.as layout changed; refusing partial edit')
    out_text = text.replace('\n', '\r\n') if crlf else text
    source.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out_text.encode('utf8'))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    (a.root / 'docs/evidence/beta-crowns103.json').write_text(json.dumps(dict(stage=103, sprites=records, slots=slots,
        atlas=str(out), size=list(atlas.size), sha256=digest, source=str(a.panels)), indent=2) + '\n', 'utf8')
    print('Packed', len(records), 'crown halves into page 13')


if __name__ == '__main__':
    main()

"""Pack original Gwent Beta 0.9.24 row-weather textures into art page 19.

Sources: sharedassets8.assets (FrostTokenEffect, FogTokenEffect, RainTokenEffect,
DroughtTokenEffect, RaghNarRoogTokenEffect, SkelligeStormTokenEffect,
GoldenFrothTokenEffect, Moonlight/BloodMoon, PitfallTrap, RowEffect_DragonsDreamSmoke).
Unity shader composites are baked to straight-alpha layers; GFx animates them.
Writes BetaGwent/ui/assets/battle107/weather107.png, registers ids -1950.. on page 19,
and generates BetaGwent/ui/src/BetaGwentWeather107.as.
Run:  python tools/ui/build_weather107.py   (needs UnityPy; original bundle is read only)
"""
from pathlib import Path
import hashlib, json, re, sys
from PIL import Image, ImageChops, ImageFilter, ImageEnhance
import UnityPy

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
OUT = ROOT / 'BetaGwent/ui/assets/battle107/weather107.png'
PAGE = 19

def light_alpha(image):
    image = image.convert('RGBA')
    if image.getchannel('A').getextrema() != (255, 255):
        return image
    r, g, b, _ = image.split()
    a = ImageChops.lighter(ImageChops.lighter(r, g), b)
    out = Image.new('RGBA', image.size)
    px = []
    for (rr, gg, bb), aa in zip(zip(r.getdata(), g.getdata(), b.getdata()), a.getdata()):
        px.append((rr * 255 // aa, gg * 255 // aa, bb * 255 // aa, aa) if aa else (0, 0, 0, 0))
    out.putdata(px)
    return out

def tint(image, rgb, alpha=1.0):
    a = image.getchannel('A').point(lambda v: int(v * alpha))
    out = Image.new('RGBA', image.size, rgb + (0,)); out.putalpha(a)
    lum = image.convert('L')
    base = Image.merge('RGB', [lum.point(lambda v, c=c: min(255, c * (60 + v) // 255 + v // 3)) for c in rgb])
    out = Image.merge('RGBA', base.split() + (a,))
    return out

def mask_alpha(image, mask, floor=0.0):
    a = image.getchannel('A'); m = mask.convert('L').resize(image.size, Image.Resampling.LANCZOS)
    m = m.point(lambda v: int(255 * (floor + (1 - floor) * v / 255)))
    image = image.copy(); image.putalpha(ImageChops.multiply(a, m)); return image

def main():
    env = UnityPy.load(str(SOURCE)); tex = {}
    for o in env.objects:
        if o.type.name == 'Texture2D':
            d = o.read(); tex.setdefault(d.m_Name, o.path_id); tex[(d.m_Name, o.path_id)] = d
    objs = {o.path_id: o for o in env.objects}
    def T(name, pid=None):
        pid = pid or tex[name]; return objs[pid].read().image.convert('RGBA')
    layers = []
    def add(ident, label, image, size):
        layers.append((ident, label, image.resize(size, Image.Resampling.LANCZOS)))
    # Frost: snow clumps at the row ends, icy edge spikes, frosted rim overlay.
    add(-1950, 'frost-cover', light_alpha(T('Frost_Cover')), (1024, 96))
    add(-1951, 'frost-spikes', light_alpha(T('Frost_Spikes')), (1024, 96))
    body = light_alpha(T('Frost_MainTex_Overlay1'))
    add(-1952, 'frost-rim', mask_alpha(tint(body, (170, 220, 255), 0.95), T('Frost_SoftCardRowEdgeMask1').convert('L'), 0.25), (512, 64))
    # Fog: soft cloud body, stronger at the row edges.
    cloud = T('NoiseCloud1_Alpha')
    fog = Image.new('RGBA', cloud.size, (225, 228, 222, 0)); fog.putalpha(cloud.getchannel('A'))
    add(-1953, 'fog-body', mask_alpha(fog, T('Fog_SoftEdgeMask').convert('L'), 0.45), (512, 64))
    # Rain: wet blue sheet, drops.
    add(-1954, 'rain-wet', T('Rain_WetCardRowBase'), (512, 64))
    add(-1955, 'rain-drops', light_alpha(T('WaterDrops1_Alpha')), (32, 96))
    # Korath heat / drought: cracked earth and sand dust.
    add(-1956, 'drought-cracks', T('DroughtBoard_1024x128'), (1024, 96))
    add(-1957, 'drought-sand', T('SandDustTiling'), (512, 64))
    # Ragh Nar Roog: burning rocks and glowing veins.
    add(-1958, 'ragh-rocks', T('raghnaroog_background_png'), (1024, 96))
    add(-1959, 'ragh-veins', tint(light_alpha(T('Mask_raghnarroog_emision')), (255, 120, 40)), (1024, 96))
    # Skellige storm: sea surface and lightning.
    sea = T('SkelligeStormSeaTilingSmall'); sea = mask_alpha(sea, T('RainMask').convert('L'), 0.0)
    add(-1960, 'storm-sea', sea, (512, 96))
    # Moon (Moonlight boon / Blood Moon contact) and Golden Froth foam.
    add(-1962, 'moon', T('Moon'), (96, 96))
    foam = T('GoldenFrothFoamTex'); cell = foam.width // 5
    add(-1963, 'froth-foam', foam.crop((cell * 2, cell * 2, cell * 3, cell * 3)), (48, 48))
    # Pitfall trap: splintered planks; Dragon's Dream: smoke dragon head.
    add(-1964, 'pitfall-wood', T('PitfallTrap_WoodCracks'), (1024, 96))
    add(-1965, 'dream-head', light_alpha(T('RowDragonsDreamSmoke_Head')), (48, 96))
    add(-1966, 'sparkle', light_alpha(T('Frost_SmallSparcles', None)), (32, 32))
    add(-1967, 'nova', light_alpha(T('LightNova1')), (32, 32))
    # Stage 108: card tokens. Spying = TokenSpyingEye with the red TokenSpyingIris; revealed = TokenVisibility.
    eye = T('TokenSpyingEye'); iris = T('TokenSpyingIris'); eye.alpha_composite(iris, ((eye.width - iris.width) // 2, (eye.height - iris.height) // 2 - 2))
    add(-1968, 'token-spying', eye, (128, 64))
    add(-1969, 'token-visibility', T('TokenVisibility'), (64, 64))
    # Pack: full-width strips first, then half strips, then small sprites.
    page = Image.new('RGBA', (1024, 1024)); slots = {}; x = y = row = 0
    for ident, label, im in sorted(layers, key=lambda l: (-l[2].width, -l[2].height)):
        if x + im.width > 1024: x = 0; y += row; row = 0
        page.alpha_composite(im, (x, y)); slots[str(ident)] = [PAGE, x, y, im.width, im.height]
        x += im.width; row = max(row, im.height)
    used = (y + row + 3) // 4 * 4
    OUT.parent.mkdir(parents=True, exist_ok=True); page.crop((0, 0, 1024, used)).save(OUT)
    src = ROOT / 'BetaGwent/ui/src/BetaGwentHDArt.as'; raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw; text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text)
    binding = {k: v for k, v in json.loads(m[1]).items() if v[0] != PAGE}
    clash = set(binding) & set(slots)
    if clash: raise SystemExit('atlas id clash: ' + ','.join(sorted(clash)))
    binding.update(slots)
    text = text[:m.start(1)] + json.dumps(binding, separators=(',', ':')) + text[m.end(1):]
    if 'private static var Page19:Class' not in text:
        text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle107/weather107.png",compression="true",quality="100")] private static var Page19:Class;\n private static var types:Array=')
        text = text.replace('Page17,Page18];', 'Page17,Page18,Page19];')
    if 'Page18,Page19' not in text: raise SystemExit('BetaGwentHDArt.as layout changed')
    src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + (text.replace('\n', '\r\n') if crlf else text).encode('utf8'))
    names = {label: ident for ident, label, _ in layers}
    consts = ',\n            '.join('%s:int=%d' % (re.sub(r'[^A-Z0-9]', '_', label.upper()), ident) for label, ident in names.items())
    (ROOT / 'BetaGwent/ui/src/BetaGwentWeather107.as').write_text('''package {
    // GENERATED by tools/ui/build_weather107.py: original Beta row-weather layers (art page 19).
    public class BetaGwentWeather107 {
        public static const %s;
    }
}
''' % consts, 'utf8')
    (ROOT / 'docs/evidence/beta-weather107.json').write_text(json.dumps(dict(stage=107, page=PAGE, atlas=str(OUT), size=[1024, used],
        sha256=hashlib.sha256(OUT.read_bytes()).hexdigest(), sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        layers={label: slots[str(ident)] for ident, label, _ in layers}), indent=1) + '\n', 'utf8')
    print('page 19:', len(layers), 'layers, used height', used)

if __name__ == '__main__':
    main()

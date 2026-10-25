"""Render source-derived card QA; no screenshot pixels are used."""
from pathlib import Path
import argparse
import json
import math
import re
import sys
from PIL import Image, ImageChops, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/classic132'))
from formats import Resource


def number(canvas, value, cx, cy, size, font):
    glyphs = [font['glyphs'][str(ord(c))] for c in value]
    scale = size / 64
    x0 = min(g['bounds'][0] + sum(h['advance'] for h in glyphs[:i]) for i, g in enumerate(glyphs))
    x1 = max(g['bounds'][2] + sum(h['advance'] for h in glyphs[:i]) for i, g in enumerate(glyphs))
    y0 = min(g['bounds'][1] for g in glyphs)
    y1 = max(g['bounds'][3] for g in glyphs)
    pen = cx - (x0 + x1) * scale / 2
    baseline = cy + (y0 + y1) * scale / 2
    for g in glyphs:
        mask = Image.new('1', canvas.size)
        for loop in g['loops']:
            part = Image.new('1', canvas.size)
            ImageDraw.Draw(part).polygon([(pen + x * scale, baseline - y * scale) for x, y in loop], fill=1)
            mask = ImageChops.logical_xor(mask, part)
        canvas.paste((255, 255, 255), (0, 0), mask.convert('L'))
        pen += g['advance'] * scale


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, default=ROOT / 'BetaGwent/build/detail-power-20261023')
    a = p.parse_args()
    src = ROOT / 'BetaGwent/ui/src'
    text = (src / 'BetaGwentBanners090.as').read_text('utf-8-sig')
    data = json.loads(re.search(r'DATA:Object=(.*);', text)[1])
    slots = json.loads(re.search(r'SLOTS:Object=(.*);', text)[1])
    art = (src / 'BetaGwentHDArt.as').read_text('utf-8-sig')
    art_slots = json.loads(re.search(r'private static var slots:Object=(.*);', art)[1])
    pages = {int(i): (src / f).resolve() for f, i in re.findall(r'Embed\(source="([^"]+)"[^\n]+Page(\d+):Class', art)}
    fonts = json.loads((ROOT / 'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
    cards = json.loads((ROOT / 'data/beta924/planning/full_catalog.json').read_text('utf8'))['cards']
    factions = {'Neutral': 1, 'Monsters': 2, 'Nilfgaard': 4, 'Northern': 8, 'Scoiatael': 16, 'Skellige': 32}
    proofs = []
    canvas = Image.new('RGB', (2160, 1410), '#111517')
    for col, (faction, bit) in enumerate(factions.items()):
        for row, tier in enumerate(['Bronze', 'Silver', 'Gold']):
            key = faction + '_' + tier
            d = data[key]
            # Render a complete native page. In particular, do NOT crop to d[4]
            # (292 px for Nilfgaard Gold); its restored rays extend to x=366.
            banner = Image.open(ROOT / 'BetaGwent/build/banners090-rays-input' / (key + '.dds')).convert('RGBA')
            factor = 3
            cw, ch = 259 * factor, 364 * factor
            im = Image.new('RGB', (360 * factor, 450 * factor), '#111517')
            x, y = 78 * factor, 60 * factor
            code = 8 if tier == 'Gold' else 4 if tier == 'Silver' else 2
            candidates = [c for c in cards if c['faction'] == bit and c['tier'] == code and c['power'] > 0 and not c['leader']]
            card = (candidates or [c for c in cards if c['faction'] == bit and c['power'] > 0 and not c['leader']])[0]
            if faction == 'Northern' and tier == 'Silver':
                card = next(c for c in cards if c['templateId'] == 122207)
            if faction == 'Northern' and tier == 'Gold':
                card = next(c for c in cards if c['templateId'] == 122103)
            pic = Image.open(ROOT / 'BetaGwent/ui/assets/cards' / (str(card['templateId']) + '.png')).convert('RGB')
            im.paste(ImageOps.fit(pic, (cw, ch), method=Image.Resampling.LANCZOS, centering=(.5, .25)), (x, y))
            page, ax, ay, aw, ah = art_slots[str(-1602 if tier == 'Gold' else -1601 if tier == 'Silver' else -1600)]
            frame = Image.open(pages[page]).convert('RGBA').crop((ax, ay, ax + aw, ay + ah)).resize((cw, ch), Image.Resampling.LANCZOS)
            im.paste(frame, (x, y), frame)
            sx, sy = d[2] * cw / d[4], d[3] * ch / d[5]
            banner = banner.resize((round(banner.width * sx), round(banner.height * sy)), Image.Resampling.LANCZOS)
            im.paste(banner, (round(x + d[0] * cw), round(y + d[1] * ch)), banner)
            value = '10' if faction == 'Monsters' else str(card['power'])
            # AS rounds the em size before glyph layout at the real card size.
            em = math.floor(364 * (slots[key][2] if len(slots[key]) > 2 else .16) + .5)
            number(im, value, x + slots[key][0] * cw, y + slots[key][1] * ch, em * factor, fonts['GwentNumbers'])
            im = im.resize((360, 450), Image.Resampling.LANCZOS)
            ImageDraw.Draw(im).text((12, 432), key, fill='#ddd3b4')
            canvas.paste(im, (col * 360, row * 470))
            proofs.append(dict(key=key, strength=value, centre=slots[key], em=em, fullPageUsed=True))
    a.build.mkdir(parents=True, exist_ok=True)
    canvas.save(a.build / 'all-factions.png')
    canvas.crop((0, 940, 2160, 1390)).save(a.build / 'gold-factions.png')
    canvas.crop((0, 0, 2160, 920)).save(a.build / 'bronze-silver.png')
    canvas.crop((1080, 470, 1440, 920)).save(a.build / 'northern-silver.png')
    # Check the actual native pixels, independently of the preview PNGs.
    dds = (ROOT / 'BetaGwent/build/banners090-rays-input/Nilfgaard_Gold.dds').read_bytes()
    native_checks = {}
    for platform in ['classic', 'nextgen']:
        path = ROOT / 'BetaGwent/build/banners090-sdk-fix5' / platform / 'resources/gameplay/gui_new/swf/betagwentbanners/nilfgaard_gold.redswf'
        resource = Resource(path.read_bytes())
        _, pos = resource.properties(resource.chunks[1])
        tail = resource.chunks[1][pos:]
        pixels = tail[28:] if platform == 'classic' else tail[24:-4]
        assert pixels == dds[128:], 'Restored sun ray pixels differ: ' + platform
        native_checks[platform] = dict(restoredRayPixelsIdentical=True, nativeResource=str(path))
    native = Image.open(ROOT / 'BetaGwent/build/banners090-rays-input/Nilfgaard_Gold.dds').convert('RGBA')
    assert native.getchannel('A').crop((292, 56, 367, 320)).getextrema()[1] > 0
    (a.build / 'preview-proof.json').write_text(json.dumps(dict(cards=proofs, nativeSunRays=native_checks,
        screenshotsUsedAsAssets=False, inGameVerified=False), indent=2), 'utf8')
    print('Rendered 18 source-derived cards; restored native sun ray pixels verified on both platforms.')


if __name__ == '__main__':
    main()

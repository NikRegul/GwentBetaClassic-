"""Static composition of source assets in the stage-103 layout (BetaGwentBoardLayout).
Not a game screenshot: GFx text, filters and animations are not reproduced."""
from pathlib import Path
import json, re, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT = Path(__file__).resolve().parents[2]; UI = ROOT / 'BetaGwent/ui'
s = (UI / 'src/BetaGwentHDArt.as').read_text('utf-8-sig')
slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', s)[1])
L = json.loads((ROOT / 'docs/evidence/beta-layout103.json').read_text('utf8'))['layout']
pages = ['cards-' + str(i) for i in range(9)] + ['boards', 'interface-10', 'interface-11']
canvas = Image.new('RGBA', (1920, 1080), '#29261f')
def font(size, bold=False):
    for f in (['C:/Windows/Fonts/arialbd.ttf'] if bold else ['C:/Windows/Fonts/arial.ttf']) + glob.glob('/usr/share/fonts/truetype/dejavu/DejaVuSans' + ('-Bold' if bold else '') + '.ttf'):
        try: return ImageFont.truetype(f, size)
        except OSError: pass
    return ImageFont.load_default()
def art(ident, w, h):
    page, x, y, sw, sh = slots[str(ident)]; scale = 1 if page >= 12 else .75
    source = {12: UI / 'assets/battle101/battle_widgets101.png', 13: UI / 'assets/battle103/crowns103.png'}.get(page) or UI / ('assets/compact98/' + pages[page] + '.png')
    im = Image.open(source).convert('RGBA').crop((round(x * scale), round(y * scale), round((x + sw) * scale), round((y + sh) * scale)))
    return im.resize((max(1, round(w)), max(1, round(h))), Image.Resampling.LANCZOS)
def paint(ident, w, h, x, y, tint=None, mirror=False, alpha=1.0):
    im = art(ident, w, h)
    if mirror: im = ImageOps.mirror(im)
    if tint:
        r, g, b, a = im.split(); r = r.point(lambda v: round(v * tint[0])); g = g.point(lambda v: round(v * tint[1])); b = b.point(lambda v: round(v * tint[2])); im = Image.merge('RGBA', (r, g, b, a))
    if alpha < 1: im.putalpha(im.split()[3].point(lambda v: round(v * alpha)))
    canvas.alpha_composite(im, (round(x), round(y)))
def main():
    draw = ImageDraw.Draw(canvas); f22 = font(22); big = font(58, True); f30 = font(30, True)
    paint(-1311, 2160, 1080, -120, 0)
    crowns = {1: 1, 2: 0}
    for side, faction in ((1, 2), (2, 1)):
        x, y, w, h = L['boardHalf'][str(side)]; paint(-1300 - faction * 2 - (side - 1), w, h, x, y, mirror=True)
    for side, faction in ((1, 2), (2, 1)):
        x, y, w, h = L['ribbon'][f'{faction}:{side}']; paint(-1530 - faction * 2 - (side - 1), w, h, x, y, (.25, .68, 1) if side == 1 else (1, .22, .16))
        for half in (1, 2):
            cx, cy, cw, ch = L['crownHalf'][f'{side}:{half}']; won = crowns[side] >= half
            paint((-1540 if side == 1 else -1542) + half - 1, cw, ch, cx, cy, None if won else (.42, .42, .42), alpha=1 if won else .32)
        sx, sy, sw, sh = L['score'][str(side)]; draw.text((sx + sw / 2, sy + sh / 2), '72' if side == 1 else '156', font=big, fill='white', anchor='mm')
        lx, ly, lw, lh = L['leader'][str(side)]; w, h = 104, 146
        px = lx + (lw - w) / 2; py = min(ly + (lh - h) / 2, 1080 - h - 8) if side == 1 else max(ly + (lh - h) / 2, 8)
        paint(200158 if side == 1 else 200164, w, h, px, py)
        for key in ('grave', 'deck'):
            gx, gy, gw, gh = L[key][str(side)]; cw = min(gw - 8, (gh - 8) * 256 / 360); ch = cw * 360 / 256
            paint(-1510, cw, ch, gx + (gw - cw) / 2, gy + (gh - ch) / 2)
            draw.text((gx + gw / 2, gy + gh / 2), '8' if key == 'grave' else '6', font=f30, fill='white', anchor='mm')
        ix, iy, iw, ih = L['handCounter'][str(side)]; paint(-1522, iw * .7, ih * .7, ix + iw * .15, iy + ih * .15)
        draw.text((ix + iw / 2, iy + ih + 12 if side == 1 else iy - 12), '10', font=f22, fill='white', anchor='mm')
        for zone in (1, 2, 4):
            rx, ry, rw, rh = L['rows'][f'{side}:{zone}']
            draw.rectangle((rx, ry, rx + rw, ry + rh), outline=(111, 184, 217, 90))
            qx, qy, qw, qh = L['rowScore'][f'{side}:{zone}']; draw.text((qx + qw / 2, qy + qh / 2), str({1: 16, 2: 24, 4: 32}[zone]), font=f30, fill='white', anchor='mm')
            cards = (112103, 113308, 113316, 112102); step = (rh - 8) * 256 / 360 + 8; cwid = step - 8; left = rx + (rw - len(cards) * step + 8) / 2
            for j, ident in enumerate(cards): paint(ident, cwid, rh - 8, left + j * step, ry + 4)
        draw.text((40, y + h + 4 if side == 1 else L['ribbon'][f'{faction}:{side}'][1] - 30), 'Геральт' if side == 1 else 'Соперник', font=f22, fill='#7acae4' if side == 1 else '#eaa18b')
    paint(-1500, 135.8, 131.3, 138.8, 474.8, (.2, .68, 1)); paint(-1503, 135.8 * .55, 131.3 * .55, 138.8 + 135.8 * .225, 474.8 + 131.3 * .225)
    hx, hy, hw, hh = L['hand']['1']; hand = (112103, 113308, 112102, 113316, 112103, 112101, 112104, 113308, 112102); n = len(hand)
    step = min(108, (hw - 100) / (n - 1)); left = hx + (hw - (100 + step * (n - 1))) / 2
    for i, ident in enumerate(hand): paint(ident, 100, 140, left + i * step, 920)
    for i in range(8): paint(-1510, 46, 68, 1039.4 - (54 * 7 + 46) / 2 + i * 54, 24)
    draw.text((40, 14), 'Раунд 2 · Ваш ход', font=f22, fill='#f1e8d3')
    draw.text((40, 868), 'P · пас   L · лидер\nD · колода   G / H · сброс', font=f22, fill='#beb7a4')
    for y in (754, 810, 868): draw.rectangle((1532, y, 1844, y + 48), outline='#977c52', width=2)
    draw.rectangle((1504, 162, 1872, 668), outline='#977c52', width=3)
    draw.text((1518, 180), 'STATIC ASSET LAYOUT\nNot a native game render', font=f22, fill='#d8d0bb')
    target = ROOT / 'BetaGwent/build/layout103-preview.png'; canvas.convert('RGB').save(target); print(target)
if __name__ == '__main__': main()

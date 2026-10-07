"""Stage 108 GUI budget: repack art page 11 (compact98/interface-11.png) without the
sprites the Beta skin no longer draws, so every cooked menu stays under 55 MiB.

Removed: the 30-frame fog intro flipbook -210..-239 (row fog now uses the scrolling
Beta layers of page 19), freeing room for the HD leader covers of page 20.
Page 11 keeps its 0.75 pixel scale; logical slot sizes are unchanged.
"""
from pathlib import Path
import json, re
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'BetaGwent/ui/src/BetaGwentHDArt.as'
OLD = ROOT / 'BetaGwent/ui/assets/compact98/interface-11.png'
NEW = ROOT / 'BetaGwent/ui/assets/battle107/interface11-108.png'
DROP = set(range(-239, -209))
S = 0.75


def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text)
    slots = json.loads(m[1])
    if 'compact98/interface-11.png' not in text: raise SystemExit('page 11 already repacked')
    page = Image.open(OLD).convert('RGBA')
    keep = sorted((int(k) for k, v in slots.items() if v[0] == 11 and int(k) not in DROP),
                  key=lambda k: -slots[str(k)][4])
    crops = {}
    for k in keep:
        _, x, y, w, h = slots[str(k)]
        crops[k] = page.crop((round(x * S), round(y * S), round((x + w) * S), round((y + h) * S)))
    # MaxRects packing (rectpack); positions on multiples of 3 so x/0.75 stays integral.
    from rectpack import newPacker, MaxRectsBssf
    best = None
    for width in range(1536, 2817, 48):
        packer = newPacker(rotation=False, pack_algo=MaxRectsBssf)
        for k in keep:
            im = crops[k]; packer.add_rect(im.width + 6 + (-im.width) % 3, im.height + 6 + (-im.height) % 3, k)
        packer.add_bin(width, 8192); packer.pack()
        rects = packer.rect_list()
        if len(rects) != len(keep): continue
        height = max(y + h for _, x, y, w, h, _k in rects)
        if best is None or width * height < best[0]: best = (width * height, width, height, rects)
    _, width, height, rects = best
    out = Image.new('RGBA', (width, height))
    for _, x, y, w, h, k in rects:
        cx, cy = x + (-x) % 3, y + (-y) % 3
        out.paste(crops[k], (cx, cy))
        _, ox, oy, lw, lh = slots[str(k)]
        slots[str(k)] = [11, round(cx / S, 4), round(cy / S, 4), lw, lh]
    used = (height + 4 + 3) // 4 * 4
    width = (width + 3) // 4 * 4; full = Image.new('RGBA', (width, used)); full.paste(out, (0, 0)); out = full
    out = out.crop((0, 0, width, used)); out.save(NEW)
    for k in DROP: slots.pop(str(k), None)
    text = text[:m.start(1)] + json.dumps(slots, separators=(',', ':')) + text[m.end(1):]
    text = text.replace('../assets/compact98/interface-11.png', '../assets/battle107/interface11-108.png')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + (text.replace('\n', '\r\n') if crlf else text).encode('utf8'))
    print('page 11:', page.size, '->', out.size, 'kept', len(keep), 'dropped', len(DROP))


if __name__ == '__main__':
    main()

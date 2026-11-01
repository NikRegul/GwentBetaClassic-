"""Place the Beta deck-builder chrome (stage 096) into unused editor-atlas space.

Same contract as prepare_valid_texture094a.py: the extended Elements atlas
keeps its size, every assigned cell and every BC3 block outside the new cells
is unchanged, so the native menus grow by 0 bytes. Each new cell is appended
to data/beta924/design/editor_vfx094.json (Classic gets a native frame class
per rect from editor_vfx094.prepare) and listed in BetaGwentEditorChrome096.as.
Run once: python tools/ui/add_editor_chrome096.py
"""
from pathlib import Path
import hashlib, io, json
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sha = lambda b: hashlib.sha256(b).hexdigest()
ICONS = ['db_filter_reset', 'db_filter_new_all', 'db_filter_new_new', 'db_filter_sort_asc', 'db_filter_sort_desc',
         'db_filter_owned_all_icon', 'db_filter_owned_owned', 'db_filter_owned_unowned', 'db_filter_faction_all_icon', 'textsearch_icon']
LARGE = ['btn_square_idle', 'btn_square_toggle_frame', 'btn_square_hovered', 'symbol_scraps', 'symbol_barrels']
CONST = {'db_filter_reset': 'RESET', 'db_filter_new_all': 'NEW_ALL', 'db_filter_new_new': 'NEW_NEW', 'db_filter_sort_asc': 'SORT_ASC',
         'db_filter_sort_desc': 'SORT_DESC', 'db_filter_owned_all_icon': 'OWNED_ALL', 'db_filter_owned_owned': 'OWNED_OWNED',
         'db_filter_owned_unowned': 'OWNED_UNOWNED', 'db_filter_faction_all_icon': 'FACTION_ALL', 'textsearch_icon': 'SEARCH_ICON',
         'btn_square_idle': 'SQUARE', 'btn_square_toggle_frame': 'SQUARE_ON', 'btn_square_hovered': 'SQUARE_HOVER',
         'symbol_scraps': 'SCRAPS', 'symbol_barrels': 'KEGS'}


def bleed(im):
    """Copy edge colour into fully transparent texels (bilinear sampling)."""
    a = np.array(im, np.float32); alpha = a[:, :, 3] > 0
    if alpha.all() or not alpha.any(): return im
    rgb = a[:, :, :3].copy(); known = alpha.copy()
    for _ in range(8):
        acc = np.zeros_like(rgb); cnt = np.zeros(known.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            k = np.roll(known, (dy, dx), (0, 1)); c = np.roll(rgb, (dy, dx), (0, 1))
            acc += c * k[:, :, None]; cnt += k
        grow = (~known) & (cnt > 0)
        rgb[grow] = acc[grow] / cnt[grow][:, None]; known |= grow
    a[:, :, :3] = rgb
    return Image.fromarray(np.rint(a).astype(np.uint8), 'RGBA')


def fitted(src, cell, inner):
    im = Image.open(src).convert('RGBA'); s = inner / max(im.size)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.Resampling.LANCZOS)
    out = Image.new('RGBA', (cell, cell), (0, 0, 0, 0)); out.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
    return bleed(out)


def main():
    spec = ROOT / 'data/beta924/design/editor_vfx094.json'; data = json.loads(spec.read_text('utf8'))
    assert 'chrome096' not in data, 'already applied'
    atlas_file = ROOT / 'BetaGwent/ui/assets/elements164/Elements.png'; blocks_file = ROOT / 'BetaGwent/ui/assets/editor094/append-bc3.bin'
    atlas_raw = atlas_file.read_bytes(); old_blocks = blocks_file.read_bytes()
    assert sha(atlas_raw) == data['extendedAtlasSha256'] and sha(old_blocks) == data['appendedBlocksSha256']
    before = Image.open(io.BytesIO(atlas_raw)).convert('RGBA'); w, h = before.size; base_h = data['baseSize'][1]
    assert [w, h] == data['size']
    sprites = ROOT / 'BetaGwent/ui/assets/editor096'; sources = json.loads((sprites / 'sources.json').read_text('utf8'))
    cells = []
    for i, name in enumerate(ICONS): cells.append((name, [1436 + 44 * (i % 8), 3312 + 44 * (i // 8), 40, 40], fitted(sprites / (name + '.png'), 40, 36)))
    for i, name in enumerate(LARGE):
        inner = 48 if name.startswith('btn_') else 44
        cells.append((name, [1940 + 52 * (i % 2), 3140 + 52 * (i // 2), 48, 48], fitted(sprites / (name + '.png'), 48, inner)))
    occupied = np.zeros((h - base_h, w), bool)
    for x, y, rw, rh in data['rects']: occupied[y - base_h:y - base_h + rh, x:x + rw] = True
    after = before.copy(); new_blocks = bytearray(old_blocks); touched = set()
    for name, (x, y, cw, ch), im in cells:
        assert x % 4 == y % 4 == cw % 4 == ch % 4 == 0 and y >= base_h and x + cw <= w and y + ch <= h
        # 4 px of untouched transparent texels around every cell (bilinear).
        assert not occupied[max(0, y - base_h - 4):y - base_h + ch + 4, max(0, x - 4):x + cw + 4].any(), name
        assert not np.array(before.crop((x, y, x + cw, y + ch)))[:, :, 3].any(), name
        occupied[y - base_h:y - base_h + ch, x:x + cw] = True
        after.paste(im, (x, y))
        enc = io.BytesIO(); im.save(enc, format='DDS', pixel_format='DXT5'); dds = enc.getvalue()
        assert dds[84:88] == b'DXT5' and len(dds) == 128 + cw * ch
        patch = dds[128:]
        for row in range(ch // 4):
            dest = (((y - base_h) // 4 + row) * (w // 4) + x // 4) * 16; src = row * (cw // 4) * 16; length = (cw // 4) * 16
            new_blocks[dest:dest + length] = patch[src:src + length]; touched.update(range(dest // 16, (dest + length) // 16))
    assert len(new_blocks) == len(old_blocks)
    for index in range(len(old_blocks) // 16):
        if index not in touched: assert old_blocks[index * 16:(index + 1) * 16] == new_blocks[index * 16:(index + 1) * 16]
    for x, y, rw, rh in data['rects']: assert before.crop((x, y, x + rw, y + rh)).tobytes() == after.crop((x, y, x + rw, y + rh)).tobytes()
    assert before.crop((0, 0, w, base_h)).tobytes() == after.crop((0, 0, w, base_h)).tobytes()
    first = len(data['rects'])
    for name, rect, im in cells: data['rects'].append(rect)
    enc = io.BytesIO(); after.save(enc, format='PNG', optimize=True); atlas_new = enc.getvalue()
    data['extendedAtlasSha256'] = sha(atlas_new); data['appendedBlocksSha256'] = sha(bytes(new_blocks))
    data['chrome096'] = dict(first=first, names=[c[0] for c in cells], sources={c[0]: sources[c[0]] for c in cells},
                             addedTextureBytes=0, patchedUnusedBc3Bytes=sum(c[1][2] * c[1][3] for c in cells), nativeGameTested=False)
    atlas_file.write_bytes(atlas_new); blocks_file.write_bytes(bytes(new_blocks))
    spec.write_text(json.dumps(data, indent=2) + '\n', 'utf8')
    consts = ','.join('%s:int=%d' % (CONST[c[0]], i) for i, c in enumerate(cells))
    rects = json.dumps([c[1] for c in cells], separators=(',', ':'))
    text = '''package {
    import flash.display.Sprite;
    // GENERATED by tools/ui/add_editor_chrome096.py: Beta deck-builder chrome
    // (filter squares, scraps/kegs symbols) in unused extended-atlas cells.
    public class BetaGwentEditorChrome096 {
        public static const FIRST:int=%d;
        public static const %s;
        private static const RECTS:Array=%s;
        // Top-left anchored w x h cell, or null when this menu's atlas lacks it.
        public static function cell(id:int,w:Number,h:Number):Sprite {
            var rect:Array=RECTS[id];if(!rect)return null;
            var art:Sprite=BetaGwentElementArt164.region(FIRST+id,rect,w,h);if(!art)return null;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;
            art.x=w/2;art.y=h/2;holder.addChild(art);return holder;
        }
    }
}
''' % (first, consts, rects)
    raw = b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode('utf8')
    for folder in ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']:
        (ROOT / 'BetaGwent/ui' / folder / 'BetaGwentEditorChrome096.as').write_bytes(raw)
    preview = Image.new('RGBA', (512, 160), (52, 40, 28, 255))
    for i, (name, rect, im) in enumerate(cells): preview.alpha_composite(im.resize((48, 48)), ((i % 10) * 51, (i // 10) * 54 + 4))
    preview.save(ROOT / 'BetaGwent/ui/assets/editor096/contact-sheet.png')
    print(json.dumps(dict(first=first, cells=len(cells), touchedBlocks=len(touched), addedTextureBytes=0,
                          extendedAtlasSha256=data['extendedAtlasSha256'], appendedBlocksSha256=data['appendedBlocksSha256'])))


if __name__ == '__main__': main()

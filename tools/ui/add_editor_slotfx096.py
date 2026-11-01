"""Deck-row Beta effects UIDBSlotAdd / UIDBSlotRemove / UIDBCounter (0.9.6).

Input: BetaGwent/build/deck-slot096-recipes-20261027-02 (preview_editor_vfx094.py
--roots UIDBSlotAdd UIDBSlotRemove UIDBCounter --no-render --include-circle
--axis-sizes). Textures follow the ValidVFX convention of the shared
VFX/Common/AdditiveAlpha shader: stored as textureRGB*textureAlpha^2 with alpha 1;
GFx multiplies RGB by vertexRGB*Brightness*vertexAlpha in an additive layer.
Cells go into unused extended-atlas space (+0 bytes), like add_editor_chrome096.
Flare00 is shared with ValidVFX (cell 28). Run once.
"""
from pathlib import Path
import hashlib, io, json
import numpy as np
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
RECIPES = ROOT / 'BetaGwent/build/deck-slot096-recipes-20261027-02'
AUDIT = ROOT / 'BetaGwent/build/deck-slot094a-vfx-audit-20261027-01/audit.json'
sha = lambda b: hashlib.sha256(b).hexdigest()
LARGE = ['1966174394013479457', '5381511042347067181', '529148685541844436', '8291112154811470388', '1310364071583600757']
LARGE_AT = [(1992, 3244), (1940, 3296), (1992, 3296), (1940, 3348), (1992, 3348)]
SMALL = ['-6902289644465539758']
SPARKS = '-3492548496821012592'
SMALL_AT = [(1524 + 44 * i, 3356) for i in range(5)]
FLARE00 = '4999763527807536617'
PRESETS = ['UIDBSlotAdd', 'UIDBSlotRemove', 'UIDBCounter']


def prepared(img, size):
    a = np.array(img.convert('RGBA'), np.float32) / 255
    rgb = a[:, :, :3] * a[:, :, 3:4] ** 2
    im = Image.fromarray(np.rint(np.concatenate([rgb, np.ones(rgb.shape[:2] + (1,), np.float32)], 2) * 255).astype(np.uint8), 'RGBA')
    return im.resize((size, size), Image.Resampling.LANCZOS)


def main():
    spec = ROOT / 'data/beta924/design/editor_vfx094.json'; data = json.loads(spec.read_text('utf8'))
    assert 'slotFx096' not in data and 'chrome096' in data and data['validVfx094a']['index'] == 28
    audit = json.loads(AUDIT.read_text('utf8'))
    brightness = {}
    for mid, m in audit['materials'].items():
        brightness[m['textures'][0]['texture']] = m['floats']['_Brightness']
        assert m['floats']['_AlphaPower'] == 1.0 and m['colors']['_TintColor'] == dict(r=1.0, g=1.0, b=1.0, a=1.0)
    atlas_file = ROOT / 'BetaGwent/ui/assets/elements164/Elements.png'; blocks_file = ROOT / 'BetaGwent/ui/assets/editor094/append-bc3.bin'
    atlas_raw = atlas_file.read_bytes(); old_blocks = blocks_file.read_bytes()
    assert sha(atlas_raw) == data['extendedAtlasSha256'] and sha(old_blocks) == data['appendedBlocksSha256']
    before = Image.open(io.BytesIO(atlas_raw)).convert('RGBA'); w, h = before.size; base_h = data['baseSize'][1]
    tex = lambda t: Image.open(RECIPES / 'textures' / (t + '.png'))
    cells = []  # (key, rect, image)
    for t, (x, y) in zip(LARGE, LARGE_AT): cells.append((t, [x, y, 48, 48], prepared(tex(t), 48)))
    for t, (x, y) in zip(SMALL, SMALL_AT): cells.append((t, [x, y, 40, 40], prepared(tex(t), 40)))
    sheet = tex(SPARKS); assert sheet.size == (128, 512)
    for k in range(4):
        x, y = SMALL_AT[1 + k]; cells.append((SPARKS + ':' + str(k), [x, y, 40, 40], prepared(sheet.crop((0, 128 * k, 128, 128 * (k + 1))), 40)))
    occupied = np.zeros((h - base_h, w), bool)
    for x, y, rw, rh in data['rects']: occupied[y - base_h:y - base_h + rh, x:x + rw] = True
    after = before.copy(); blocks = bytearray(old_blocks); touched = set()
    for key, (x, y, cw, ch), im in cells:
        assert x % 4 == y % 4 == 0 and x + cw <= w and y + ch <= h
        assert not occupied[max(0, y - base_h - 4):y - base_h + ch + 4, max(0, x - 4):x + cw + 4].any(), key
        occupied[y - base_h:y - base_h + ch, x:x + cw] = True; after.paste(im, (x, y))
        enc = io.BytesIO(); im.save(enc, format='DDS', pixel_format='DXT5'); patch = enc.getvalue()[128:]
        assert len(patch) == cw * ch
        for row in range(ch // 4):
            dest = (((y - base_h) // 4 + row) * (w // 4) + x // 4) * 16; src = row * (cw // 4) * 16; n = (cw // 4) * 16
            blocks[dest:dest + n] = patch[src:src + n]; touched.update(range(dest // 16, (dest + n) // 16))
    for i in range(len(old_blocks) // 16):
        if i not in touched: assert old_blocks[i * 16:(i + 1) * 16] == blocks[i * 16:(i + 1) * 16]
    for x, y, rw, rh in data['rects']: assert before.crop((x, y, x + rw, y + rh)).tobytes() == after.crop((x, y, x + rw, y + rh)).tobytes()
    first = len(data['rects'])
    index = {FLARE00: 28}
    for i, (key, rect, im) in enumerate(cells): data['rects'].append(rect); index[key] = first + i
    packets = json.loads((RECIPES / 'packets.json').read_text('utf8'))
    out = {}
    for preset in PRESETS:
        frames = packets[preset]; assert len(frames) == 48
        rows = []
        for f in frames:
            row = []
            for p in f['particles']:
                q = p['pose']; t = Path(p['texture']).stem
                if not q.get('visible', True): continue
                assert p['blend'] == 'add'
                key = t + ':' + str(int(q.get('frame', 0))) if t == SPARKS else t
                gain = 2.0 * brightness[t] / 2.0  # vertex RGB * Brightness * vertex alpha
                a = float(q['a']) * brightness[t]
                row.append([index[key]] + [round(float(q[k]), 3) for k in ('x', 'y', 'w', 'h', 'angle')] +
                           [round(float(q[k]), 4) for k in ('r', 'g', 'b')] + [round(a, 4)])
            rows.append(row)
        out[preset] = dict(ms=round(frames[-1]['seconds'] * 1000, 3), frames=rows)
    rects = {str(i): data['rects'][i] for i in sorted(set(index.values()))}
    enc = io.BytesIO(); after.save(enc, format='PNG', optimize=True); atlas_new = enc.getvalue()
    data['extendedAtlasSha256'] = sha(atlas_new); data['appendedBlocksSha256'] = sha(bytes(blocks))
    data['slotFx096'] = dict(first=first, cells=[c[0] for c in cells], sharedFlare00=28, source=str(RECIPES.relative_to(ROOT)),
                             packetsSha256=sha((RECIPES / 'packets.json').read_bytes()), auditSha256=sha(AUDIT.read_bytes()),
                             textureRgb='sourceRGB*sourceAlpha^2', outputAlpha=1, vertexRgbMultiplier='vertexRGB*Brightness*vertexAlpha',
                             downscaled={c[0]: c[1][2] for c in cells}, addedTextureBytes=0, nativeAppearanceVerified=False)
    atlas_file.write_bytes(atlas_new); blocks_file.write_bytes(bytes(blocks)); spec.write_text(json.dumps(data, indent=2) + '\n', 'utf8')
    text = '''package {
    // GENERATED by tools/ui/add_editor_slotfx096.py: Beta UIDBSlotAdd,
    // UIDBSlotRemove and UIDBCounter, 48 source samples each. Particle:
    // [cell, x, y, w, h, angle, r, g, b, gain]; units are the 292 x 37 source slot,
    // origin at its top centre. Colour = textureRGB*a^2 x rgb x gain (additive).
    public class BetaGwentEditorSlotData096 {
        public static const RECTS:Object=%s;
        public static const ADD_MS:Number=%s;public static const REMOVE_MS:Number=%s;public static const COUNTER_MS:Number=%s;
        public static const ADD:Array=%s;
        public static const REMOVE:Array=%s;
        public static const COUNTER:Array=%s;
    }
}
''' % (json.dumps(rects, separators=(',', ':')), out['UIDBSlotAdd']['ms'], out['UIDBSlotRemove']['ms'], out['UIDBCounter']['ms'],
       json.dumps(out['UIDBSlotAdd']['frames'], separators=(',', ':')), json.dumps(out['UIDBSlotRemove']['frames'], separators=(',', ':')),
       json.dumps(out['UIDBCounter']['frames'], separators=(',', ':')))
    raw = b'\xef\xbb\xbf' + text.replace('\n', '\r\n').encode('utf8')
    for folder in ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']:
        (ROOT / 'BetaGwent/ui' / folder / 'BetaGwentEditorSlotData096.as').write_bytes(raw)
    print(json.dumps(dict(first=first, cells=len(cells), particles={k: sum(map(len, v['frames'])) for k, v in out.items()},
                          ms={k: v['ms'] for k, v in out.items()}, dataBytes=len(raw))))


if __name__ == '__main__': main()

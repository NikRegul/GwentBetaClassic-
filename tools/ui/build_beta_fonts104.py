"""Embed the original Gwent Beta 0.9.24 fonts into a compiled board SWF.

Apache Royale cannot embed fonts (FontEmbeddingNotSupported), so after mxmlc this tool
inserts DefineFont3 tags (vector outlines traced from the Beta TMP SDF atlases, see
beta_fonts_vector104.py) and a SymbolClass binding them to the AS3 classes
BetaFontHalisMedium / BetaFontHalisBold / BetaFontDin / BetaFontNumbers (BetaGwentFonts.as
registers them). Glyphs the Beta atlases lack (space, arrows, ·, ×, −, |, *, ^, △, ○) are
added from DejaVu Sans Condensed scaled to the Beta cap height.

Usage: build_beta_fonts104.py prepare   -> BetaGwent/ui/build/beta-fonts104.json (vector cache)
       build_beta_fonts104.py inject SWF -> rewrites SWF in place (uncompressed FWS only)
"""
from pathlib import Path
import argparse, hashlib, json, os, struct, sys
ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/fonts'
CACHE = ROOT / 'BetaGwent/ui/build/beta-fonts104.json'
EM = 1024 * 20          # DefineFont3 EM square (20x resolution)
SAMPLE = 64.0           # TMP sampling point size (pixels per em)
SCALE = EM / SAMPLE
FACES = [  # (asset, swf name, bold, AS3 class)
    ('HalisGRMedium', 'Halis GR', False, 'BetaFontHalisMedium'),
    ('HalisGRBold', 'Halis GR', True, 'BetaFontHalisBold'),
    ('PFDinTextCondPro', 'PF Din Text Cond Pro', False, 'BetaFontDin'),
    ('GwentNumbers', 'Gwent Numbers', False, 'BetaFontNumbers'),
]
FALLBACK = ' *^|·×←↑→↓−△○□'
FALLBACK_FONTS = ['/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf', 'C:/Windows/Fonts/arial.ttf']


def fallback_glyphs(chars, cap_height):
    from fontTools.ttLib import TTFont
    from fontTools.pens.recordingPen import RecordingPen
    path = next((p for p in FALLBACK_FONTS if os.path.exists(p)), None)
    if not path: raise SystemExit('No fallback font for ' + chars)
    font = TTFont(path); cmap = font.getBestCmap(); gs = font.getGlyphSet()
    upm = font['head'].unitsPerEm; cap = getattr(font['OS/2'], 'sCapHeight', 0) or upm * 0.73
    k = cap_height / cap; out = {}
    for ch in chars:
        name = cmap.get(ord(ch))
        if not name: continue
        pen = RecordingPen(); gs[name].draw(pen)
        loops, cur, last = [], [], None
        def q(p0, p1, p2, n=6):
            return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(1, n + 1)]]
        for op, args in pen.value:
            if op == 'moveTo': cur = [args[0]]; last = args[0]
            elif op == 'lineTo': cur.append(args[0]); last = args[0]
            elif op == 'qCurveTo':
                pts = list(args); start = last
                for i in range(len(pts) - 1):
                    ctrl = pts[i]; end = pts[i + 1] if i == len(pts) - 2 else ((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
                    cur += q(start, ctrl, end); start = end
                last = pts[-1]
            elif op == 'curveTo':
                p0 = last; p1, p2, p3 = args
                for t in [i / 8 for i in range(1, 9)]:
                    cur.append(((1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0],
                                (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]))
                last = p3
            elif op in ('closePath', 'endPath'):
                if len(cur) > 2:
                    # TrueType outer contours are clockwise with y up; after the SWF y flip the body
                    # would be on the left, so reverse to keep it on the right (fillStyle1).
                    loops.append([[x * k, y * k] for x, y in reversed(cur)])
                cur = []
        adv = font['hmtx'][name][0] * k
        xs = [p[0] for l in loops for p in l] or [0]; ys = [p[1] for l in loops for p in l] or [0]
        out[ord(ch)] = dict(advance=adv, loops=loops, bounds=[min(xs), min(ys), max(xs), max(ys)])
    return out


def prepare(bundle):
    sys.path.insert(0, str(Path(__file__).parent))
    from beta_fonts_vector104 import build
    fonts = build(bundle)
    out = {}
    for asset, *_ in FACES:
        f = fonts[asset]; glyphs = {int(c): dict(advance=g['advance'], bounds=[float(v) for v in g['bounds']],
                                                 loops=[[[round(float(x), 3), round(float(y), 3)] for x, y in l] for l in g['loops']])
                                    for c, g in f['glyphs'].items()}
        if asset != 'GwentNumbers':
            cap = float(f['info'].get('CapHeight') or 45)
            for code, g in fallback_glyphs(''.join(ch for ch in FALLBACK if ord(ch) not in glyphs), cap).items():
                glyphs[code] = g
            glyphs[32] = dict(advance=SAMPLE * (0.26 if 'Halis' in asset else 0.21), bounds=[0, 0, 0, 0], loops=[])
        out[asset] = dict(info={k: f['info'][k] for k in ('Ascender', 'Descender', 'LineHeight', 'CapHeight')},
                          glyphs={str(k): v for k, v in sorted(glyphs.items())},
                          kerning=[[int(p['AscII_Left']), int(p['AscII_Right']), float(p['XadvanceOffset'])] for p in f['kerning']])
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(out, ensure_ascii=False, separators=(',', ':')), 'utf8')
    return out


class Bits:
    def __init__(self): self.out = bytearray(); self.acc = 0; self.n = 0
    def ub(self, v, n):
        for i in range(n - 1, -1, -1):
            self.acc = (self.acc << 1) | ((v >> i) & 1); self.n += 1
            if self.n == 8: self.out.append(self.acc); self.acc = 0; self.n = 0
    def sb(self, v, n): self.ub(v & ((1 << n) - 1), n)
    def align(self):
        if self.n: self.out.append(self.acc << (8 - self.n)); self.acc = 0; self.n = 0
        return bytes(self.out)


def sbits(*values):
    need = 1
    for v in values:
        b = (v if v >= 0 else ~v).bit_length() + 1; need = max(need, b)
    return need


def rect(xmin, xmax, ymin, ymax):
    b = Bits(); n = sbits(xmin, xmax, ymin, ymax); b.ub(n, 5)
    for v in (xmin, xmax, ymin, ymax): b.sb(v, n)
    return b.align()


def shape(loops):
    b = Bits(); b.ub(1, 4); b.ub(0, 4)
    first = True; px = py = 0
    for loop in loops:
        pts = [(int(round(x * SCALE)), int(round(-y * SCALE))) for x, y in loop]
        if len(pts) < 3: continue
        x0, y0 = pts[0]
        b.ub(0, 1); b.ub(0, 1); b.ub(0, 1); b.ub(1 if first else 0, 1); b.ub(0, 1); b.ub(1, 1)  # moveTo (+fillStyle1)
        n = sbits(x0, y0); b.ub(n, 5); b.sb(x0, n); b.sb(y0, n)
        if first: b.ub(1, 1); first = False
        px, py = x0, y0
        for x, y in pts[1:] + [pts[0]]:
            dx, dy = x - px, y - py
            if dx == 0 and dy == 0: continue
            n = max(2, sbits(dx, dy)); b.ub(1, 1); b.ub(1, 1); b.ub(n - 2, 4); b.ub(1, 1); b.sb(dx, n); b.sb(dy, n)
            px, py = x, y
    b.ub(0, 6)
    return b.align()


def define_font3(font_id, name, bold, face):
    codes = sorted(int(c) for c in face['glyphs'])
    glyphs = [face['glyphs'][str(c)] for c in codes]
    shapes = [shape(g['loops']) for g in glyphs]
    offsets, pos = [], 4 * (len(codes) + 1)
    for s in shapes: offsets.append(pos); pos += len(s)
    body = bytearray(struct.pack('<H', font_id))
    body.append(0x80 | 0x08 | 0x04 | (0x01 if bold else 0))  # HasLayout, WideOffsets, WideCodes, Bold
    body.append(1)                                           # language: Latin (Cyrillic shares rendering)
    nm = name.encode('utf8') + b'\0'; body.append(len(nm)); body += nm  # Flash writes the NUL into FontNameLen
    body += struct.pack('<H', len(codes))
    for o in offsets: body += struct.pack('<I', o)
    body += struct.pack('<I', pos)
    for s in shapes: body += s
    for c in codes: body += struct.pack('<H', c)
    info = face['info']
    body += struct.pack('<HHh', int(round(info['Ascender'] * SCALE)), int(round(-info['Descender'] * SCALE)),
                        int(round((info['LineHeight'] - info['Ascender'] + info['Descender']) * SCALE)))
    for g in glyphs: body += struct.pack('<h', max(-32768, min(32767, int(round(g['advance'] * SCALE)))))
    for g in glyphs:
        x0, y0, x1, y1 = g['bounds']; body += rect(int(x0 * SCALE), int(x1 * SCALE), int(-y1 * SCALE), int(-y0 * SCALE))
    pairs = [(l, r, a) for l, r, a in face['kerning'] if str(l) in face['glyphs'] and str(r) in face['glyphs']]
    body += struct.pack('<H', len(pairs))
    for l, r, a in pairs: body += struct.pack('<HHh', l, r, int(round(a * SCALE)))
    return tag(75, bytes(body))


def tag(code, body):
    return struct.pack('<HI', (code << 6) | 0x3F, len(body)) + body


DEFINE_TAGS = {2, 6, 10, 11, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 75, 83, 84, 87, 90, 91}


def inject(swf_path, faces):
    data = bytearray(Path(swf_path).read_bytes())
    if data[:3] != b'FWS': raise SystemExit('Expected uncompressed FWS SWF')
    nbits = data[8] >> 3; pos = 8 + (5 + 4 * nbits + 7) // 8 + 4
    tags, max_id, abc_index = [], 0, None
    while pos < len(data):
        h, = struct.unpack_from('<H', data, pos); code, ln = h >> 6, h & 0x3F; hl = 2
        if ln == 0x3F: ln, = struct.unpack_from('<I', data, pos + 2); hl = 6
        if code in DEFINE_TAGS and ln >= 2: max_id = max(max_id, struct.unpack_from('<H', data, pos + hl)[0])
        if code == 75 and b'Halis GR' in data[pos:pos + hl + 64]: raise SystemExit('Fonts already injected')
        if code in (82, 72) and abc_index is None: abc_index = len(tags)
        tags.append((pos, hl + ln)); pos += hl + ln
        if code == 0: break
    if abc_index is None: raise SystemExit('No DoABC tag')
    fonts, symbols = b'', []
    for i, (asset, name, bold, cls) in enumerate(FACES):
        fid = max_id + 1 + i; fonts += define_font3(fid, name, bold, faces[asset]); symbols.append((fid, cls))
    sym = struct.pack('<H', len(symbols)) + b''.join(struct.pack('<H', i) + c.encode() + b'\0' for i, c in symbols)
    abc_start, abc_len = tags[abc_index]
    out = data[:abc_start] + fonts + data[abc_start:abc_start + abc_len] + tag(76, sym) + data[abc_start + abc_len:]
    struct.pack_into('<I', out, 4, len(out))
    Path(swf_path).write_bytes(bytes(out))
    return dict(fonts=[dict(id=i, cls=c) for i, c in symbols], bytesAdded=len(out) - len(data), sha256=hashlib.sha256(out).hexdigest())


def write_as(faces):
    """BetaGwentFonts.as + one Font subclass per face (SymbolClass targets)."""
    src = ROOT / 'BetaGwent/ui/src'
    for _, _, _, cls in FACES:
        (src / (cls + '.as')).write_text('package {\n    import flash.text.Font;\n    // DefineFont3 bound by tools/ui/build_beta_fonts104.py inject.\n'
                                         '    public class ' + cls + ' extends Font {}\n}\n', 'utf8')
    def charset(asset):
        # Codepoint ranges as integers: keeps Cyrillic out of string literals (localization89 scans them).
        cps = sorted(int(c) for c in faces[asset]['glyphs'] if int(c) >= 32); out = []
        for c in cps:
            if out and out[-1][1] == c - 1: out[-1][1] = c
            else: out.append([c, c])
        return ','.join('%d,%d' % (a, b) for a, b in out)
    esc = lambda s: s
    body = '''package {
    import flash.text.Font;
    import flash.text.TextField;
    import flash.text.TextFormat;
    // GENERATED by tools/ui/build_beta_fonts104.py: original Gwent Beta 0.9.24 fonts.
    public class BetaGwentFonts {
        public static const BODY:String="PF Din Text Cond Pro";
        public static const TITLE:String="Halis GR";
        public static const NUMBERS:String="Gwent Numbers";
        private static const BODY_CHARS:Array=[%s];
        private static const TITLE_CHARS:Array=[%s];
        private static const NUMBER_CHARS:Array=[%s];
        private static var checked:Boolean=false;
        public static var available:Boolean=false;
        public static function init():Boolean
        {
            if(checked)return available;checked=true;
            try{
                Font.registerFont(BetaFontHalisMedium);Font.registerFont(BetaFontHalisBold);
                Font.registerFont(BetaFontDin);Font.registerFont(BetaFontNumbers);
                for each(var f:Font in Font.enumerateFonts(false))if(f.fontName==BODY)available=true;
            }catch(e:Error){available=false;}
            return available;
        }
        public static function supports(face:String,value:String):Boolean
        {
            if(!init()||value==null)return false;
            var set:Array=face==NUMBERS?NUMBER_CHARS:face==TITLE?TITLE_CHARS:BODY_CHARS;
            for(var i:int=0;i<value.length;i++){
                var c:int=value.charCodeAt(i);if(c==10||c==13)continue;
                var found:Boolean=false;for(var r:int=0;r<set.length;r+=2)if(c>=set[r]&&c<=set[r+1]){found=true;break;}
                if(!found)return false;
            }
            return true;
        }
        // Apply a Beta face when every character exists in it; otherwise keep the game font.
        public static function apply(field:TextField,face:String,size:Number,color:uint,bold:Boolean=false,align:String=null,spacing:Number=0):Boolean
        {
            var beta:Boolean=supports(face,field.text);
            var format:TextFormat=new TextFormat(beta?face:"$NormalFont",size,color,bold&&(!beta||face==TITLE),null,null,null,null,align);
            if(beta&&spacing!=0)format.letterSpacing=spacing;
            field.embedFonts=beta;field.defaultTextFormat=format;field.setTextFormat(format);
            return beta;
        }
    }
}
''' % (esc(charset('PFDinTextCondPro')), esc(charset('HalisGRBold')), esc(charset('GwentNumbers')))
    (src / 'BetaGwentFonts.as').write_text(body, 'utf8')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('step', choices=['prepare', 'inject', 'as'])
    ap.add_argument('swf', nargs='?')
    ap.add_argument('--bundle', type=Path, default=BUNDLE)
    a = ap.parse_args()
    if a.step == 'prepare':
        if os.name == 'nt': sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
        r = prepare(a.bundle); print('prepared', {k: len(v['glyphs']) for k, v in r.items()})
    elif a.step == 'as':
        write_as(json.loads(CACHE.read_text('utf8'))); print('wrote BetaGwentFonts.as')
    else:
        faces = json.loads(CACHE.read_text('utf8'))
        print(json.dumps(inject(a.swf, faces)))

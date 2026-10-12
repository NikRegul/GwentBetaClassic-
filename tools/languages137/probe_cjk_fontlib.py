"""Probe: CJK font library SWFs (DefineFont3 from the prepared Noto subsets) for jp/kr/zh_cn/zh_tw.

Uses the mod's own DefineFont3 writer (tools/ui/build_beta_fonts104.py). Curves are flattened
to line segments exactly as the writer expects. Produces one standalone SWF per locale
(FWS + CWS) under languages137/fonts/fontlib-probe and a size report. Not used by any build.
"""
from pathlib import Path
import json, struct, sys, zlib
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/ui'))
import build_beta_fonts104 as W
L = ROOT / 'BetaGwent/build/languages137/fonts'
OUT = L / 'fontlib-probe'; OUT.mkdir(parents=True, exist_ok=True)
SAMPLE = W.SAMPLE  # glyph units: TMP pixels at 64 pt, like the existing Beta faces

def face_from(path, steps_q=3, steps_c=4):
    font = TTFont(path); cmap = font.getBestCmap(); gs = font.getGlyphSet(); upm = font['head'].unitsPerEm
    k = SAMPLE / upm; hhea = font['hhea']; glyphs = {}
    def q(p0, p1, p2, n): return [((1-t)**2*p0[0]+2*(1-t)*t*p1[0]+t*t*p2[0], (1-t)**2*p0[1]+2*(1-t)*t*p1[1]+t*t*p2[1]) for t in [i/n for i in range(1, n+1)]]
    for code, name in cmap.items():
        pen = RecordingPen(); gs[name].draw(pen); loops, cur, last = [], [], None
        for op, args in pen.value:
            if op == 'moveTo': cur = [args[0]]; last = args[0]
            elif op == 'lineTo': cur.append(args[0]); last = args[0]
            elif op == 'qCurveTo':
                pts = list(args); start = last
                for i in range(len(pts) - 1):
                    end = pts[i+1] if i == len(pts) - 2 else ((pts[i][0]+pts[i+1][0])/2, (pts[i][1]+pts[i+1][1])/2)
                    cur += q(start, pts[i], end, steps_q); start = end
                last = pts[-1]
            elif op == 'curveTo':
                p0 = last; p1, p2, p3 = args
                for t in [i/steps_c for i in range(1, steps_c+1)]:
                    cur.append(((1-t)**3*p0[0]+3*(1-t)**2*t*p1[0]+3*(1-t)*t*t*p2[0]+t**3*p3[0], (1-t)**3*p0[1]+3*(1-t)**2*t*p1[1]+3*(1-t)*t*t*p2[1]+t**3*p3[1]))
                last = p3
            elif op in ('closePath', 'endPath'):
                if len(cur) > 2: loops.append([[x*k, y*k] for x, y in reversed(cur)])
                cur = []
        xs = [p[0] for l in loops for p in l] or [0]; ys = [p[1] for l in loops for p in l] or [0]
        glyphs[str(code)] = dict(advance=font['hmtx'][name][0]*k, loops=loops, bounds=[min(xs), min(ys), max(xs), max(ys)])
    info = dict(Ascender=hhea.ascent*k, Descender=hhea.descent*k, LineHeight=(hhea.ascent-hhea.descent+hhea.lineGap)*k, CapHeight=hhea.ascent*k*0.7)
    return dict(info=info, glyphs=glyphs, kerning=[])

def swf(tags):
    body = W.rect(0, 20, 0, 20) + struct.pack('<HH', 0x1800, 1) + W.tag(69, struct.pack('<I', 0x08)) + b''.join(tags) + W.tag(0, b'')
    fws = b'FWS' + bytes([10]) + struct.pack('<I', 8 + len(body)) + body
    cws = b'CWS' + bytes([10]) + struct.pack('<I', len(fws)) + zlib.compress(fws[8:], 9)
    return fws, cws

report = {}
for locale in ('jp_jp', 'kr_kr', 'zh_cn', 'zh_tw'):
    plan = json.loads((L / 'prepared' / locale / 'plan.json').read_text('utf8'))
    tags = []; faces = {}
    for i, role in enumerate(('body', 'title')):
        path = L / 'prepared' / locale / plan['faces'][role]['file']
        face = face_from(path)
        t = W.define_font3(100 + i, 'BetaCJK ' + locale + (' Bold' if role == 'title' else ''), role == 'title', face)
        tags.append(t); faces[role] = dict(glyphs=len(face['glyphs']), tagBytes=len(t))
    fws, cws = swf(tags)
    (OUT / f'fonts_{locale}.swf').write_bytes(cws)
    body_only = swf(tags[:1])
    report[locale] = dict(faces=faces, uncompressedBoth=len(fws), compressedBoth=len(cws), uncompressedBodyOnly=len(body_only[0]), compressedBodyOnly=len(body_only[1]))
    print(locale, {k: (v['glyphs'], round(v['tagBytes']/2**20, 2)) for k, v in faces.items()}, 'MiB uncompressed', round(len(fws)/2**20, 2), 'cws', round(len(cws)/2**20, 2))
(OUT / 'report.json').write_text(json.dumps(report, indent=1) + '\n', 'utf8')

"""Vector outlines of the Gwent Beta TMP SDF fonts (HalisGR Medium/Bold, PF Din Text
Cond Pro, GwentNumbers). Iso-line 0.5 of the signed distance field (contourpy, linear
interpolation), Douglas-Peucker simplification, orientation fixed so the glyph body is on
the right of every edge (SWF fillStyle1). Units: TMP pixels at the 64pt sampling size,
y up from the baseline."""
import numpy as np
import contourpy

FONTS = ['HalisGRMedium', 'HalisGRBold', 'PFDinTextCondPro', 'GwentNumbers']


def load(fonts_bundle):
    import UnityPy
    env = UnityPy.load(str(fonts_bundle))
    tex, data = {}, {}
    for o in env.objects:
        if o.type.name == 'Texture2D':
            t = o.read()
            if t.m_Name in FONTS: tex[t.m_Name] = np.array(t.image.convert('RGBA'))[..., 3].astype(float) / 255.0
        elif o.type.name == 'MonoBehaviour':
            try: d = o.read_typetree()
            except Exception: continue
            if d.get('m_Name') in FONTS and 'm_glyphInfoList' in d:
                data[d['m_Name']] = dict(info=d['m_fontInfo'], glyphs=d['m_glyphInfoList'],
                                         kerning=(d.get('m_kerningInfo') or {}).get('kerningPairs', []))
    missing = [f for f in FONTS if f not in tex or f not in data]
    if missing: raise SystemExit('Missing font assets: ' + ', '.join(missing))
    return tex, data


def rdp(points, eps):
    if len(points) < 3: return points
    a, b = points[0], points[-1]; ab = b - a; n = np.hypot(*ab)
    rel = points - a
    d = np.abs(ab[0] * rel[:, 1] - ab[1] * rel[:, 0]) / n if n > 1e-9 else np.hypot(*rel.T)
    i = int(np.argmax(d))
    if d[i] > eps:
        return np.vstack([rdp(points[:i + 1], eps)[:-1], rdp(points[i:], eps)])
    return np.vstack([a, b])


def simplify_closed(loop, eps):
    loop = loop[:-1] if np.allclose(loop[0], loop[-1]) else loop
    if len(loop) < 4: return loop
    far = int(np.argmax(np.hypot(*(loop - loop[0]).T)))
    first = rdp(loop[:far + 1], eps); second = rdp(np.vstack([loop[far:], loop[:1]]), eps)
    return np.vstack([first[:-1], second[:-1]])


def glyph_outline(sdf, g, padding, eps=0.12):
    x0 = int(np.floor(g['x'])) - padding; y0 = int(np.floor(g['y'])) - padding
    x1 = int(np.ceil(g['x'] + g['width'])) + padding; y1 = int(np.ceil(g['y'] + g['height'])) + padding
    H, W = sdf.shape
    crop = np.zeros((y1 - y0 + 2, x1 - x0 + 2))
    sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
    crop[1 + sy0 - y0:1 + sy1 - y0, 1 + sx0 - x0:1 + sx1 - x0] = sdf[sy0:sy1, sx0:sx1]
    gen = contourpy.contour_generator(z=crop, name='serial')
    loops = []
    for line in gen.lines(0.5):
        if len(line) < 4: continue
        pts = simplify_closed(np.asarray(line, float), eps)
        if len(pts) < 3: continue
        # Orientation: sample just to the right (y down raster) of the longest edge.
        seg = np.roll(pts, -1, axis=0) - pts; k = int(np.argmax(np.hypot(*seg.T)))
        mid = pts[k] + seg[k] / 2; nrm = np.array([-seg[k][1], seg[k][0]]) / max(1e-9, np.hypot(*seg[k]))
        probe = mid + nrm * 0.6
        px, py = int(round(probe[0])), int(round(probe[1]))
        inside = 0 <= py < crop.shape[0] and 0 <= px < crop.shape[1] and crop[py, px] > 0.5
        if not inside: pts = pts[::-1]
        # raster (col,row) -> font units: x right, y up from the baseline.
        fx = g['xOffset'] + (pts[:, 0] - 1 + x0 + 0.5 - g['x'])
        fy = g['yOffset'] - (pts[:, 1] - 1 + y0 + 0.5 - g['y'])
        loops.append(np.stack([fx, fy], 1))
    return loops


def build(fonts_bundle):
    tex, data = load(fonts_bundle)
    out = {}
    for name in FONTS:
        info = data[name]['info']; pad = int(info.get('Padding', 5))
        glyphs = {}
        for g in data[name]['glyphs']:
            loops = [] if g['width'] <= 0 or g['height'] <= 0 else glyph_outline(tex[name], g, pad)
            glyphs[int(g['id'])] = dict(advance=float(g['xAdvance']), loops=loops,
                                        bounds=[g['xOffset'], g['yOffset'] - g['height'], g['xOffset'] + g['width'], g['yOffset']])
        out[name] = dict(info=info, glyphs=glyphs, kerning=data[name]['kerning'])
    return out

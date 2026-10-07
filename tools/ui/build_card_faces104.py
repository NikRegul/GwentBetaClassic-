"""Bake Gwent Beta 0.9.24 small-card faces (board/hand) into atlas page 14.

Source (read-only): cardassets/fronts/meshdata (SmallCardFull mesh, shader
CardShaders/Combined) and cardassets/fronts/uber (<Faction>_SmallCardMesh_Banner).
Shader reading: layer by sign(u) and v>1; Lbot = _EdgeTex (the faction Banner
texture), tier column frac(u + 1 + tier/3): 0 bronze (wood), 1 silver, 2 gold.
Frame strips are identical for all factions; the faction banner is short on small
cards (reference: original client screenshots) - top + 3-tooth tail.
Ids: -1600..-1602 frames (bronze, silver, gold), -1610..-1615 banners
(Monsters, Nilfgaard, Northern, Scoiatael, Skellige, Neutral).
Card plane 17.6 x 21.4 units; frame/banner placement constants are emitted to JSON.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, sys
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
CARD = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/cardassets/fronts'
FACTIONS = ['Monsters', 'Nilfgaard', 'Northern', 'Scoiatael', 'Skellige', 'Neutral']
PX = 15.0  # pixels per mesh unit (row cards are ~5 px/unit on screen: 3x supersampling)


def raster(can, pts, uvs, sampler):
    H, W = can.shape[:2]
    (ax, ay), (bx, by), (cx, cy) = pts
    d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(d) < 1e-9: return
    x0, y0 = np.floor(pts.min(0)).astype(int); x1, y1 = np.ceil(pts.max(0)).astype(int)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W - 1, x1), min(H - 1, y1)
    if x1 < x0 or y1 < y0: return
    yy, xx = np.mgrid[y0:y1 + 1, x0:x1 + 1] + 0.5
    wa = ((by - cy) * (xx - cx) + (cx - bx) * (yy - cy)) / d; wb = ((cy - ay) * (xx - cx) + (ax - cx) * (yy - cy)) / d; wc = 1 - wa - wb
    m = (wa >= -1e-4) & (wb >= -1e-4) & (wc >= -1e-4)
    u = wa * uvs[0, 0] + wb * uvs[1, 0] + wc * uvs[2, 0]; v = wa * uvs[0, 1] + wb * uvs[1, 1] + wc * uvs[2, 1]
    col = sampler(u, v)
    mm = m & (col[..., 3] > 8)
    sub = can[y0:y1 + 1, x0:x1 + 1]; sub[mm] = col[mm]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fronts', type=Path, default=CARD)
    ap.add_argument('--root', type=Path, default=ROOT)
    a = ap.parse_args()
    if os.name == 'nt': sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
    import UnityPy
    from UnityPy.helpers.MeshHelper import MeshHandler
    from PIL import Image
    env = UnityPy.load(str(a.fronts / 'meshdata'))
    meshes = []
    for o in env.objects:
        if o.type.name == 'Mesh' and o.read().m_Name == 'SmallCardFull':
            h = MeshHandler(o.read()); h.process()
            meshes.append((np.array(h.m_Vertices), np.array(h.m_UV0), np.array(h.get_triangles()[0]).reshape(-1, 3)))
    tex = {}
    env2 = UnityPy.load(str(a.fronts / 'uber'))
    for o in env2.objects:
        if o.type.name == 'Texture2D':
            t = o.read()
            for f in FACTIONS:
                if t.m_Name == f + '_SmallCardMesh_Banner': tex[f] = np.array(t.image.convert('RGBA')).astype(np.uint8)
    assert len(tex) == 6, 'missing faction banner textures'
    left, right, bottom, top = -8.82, 8.82, -10.73, 10.73
    W, H = int(round((right - left) * PX)), int(round((top - bottom) * PX))
    tris = []
    for v, uv, T in meshes:
        for t in T:
            q = uv[t]; p = v[t]
            if q[:, 0].mean() >= 0 or q[:, 1].mean() > 1: continue       # art / masks
            if q[:, 0].min() < -0.83 and p[:, 0].max() < -4.0: continue  # long banner quads
            tris.append((p, q))
    tris.sort(key=lambda pq: -pq[0][:, 2].mean())  # far -> near
    ref = tex['Northern']; th, tw = ref.shape[:2]
    images = {}
    for tier in range(3):
        can = np.zeros((H, W, 4), np.uint8)
        def sampler(u, v, tier=tier):
            fu = (u + 1 + tier / 3.0) % 1.0; fv = np.clip(v, 0, 1)
            return ref[((1 - fv) * (th - 1)).astype(int), (fu * (tw - 1)).astype(int)]
        for p, q in tris:
            pts = np.array([((x - left) * PX, (top - y) * PX) for x, y, z in p])  # camera view, X right
            raster(can, pts, q, sampler)
        images[-1600 - tier] = Image.fromarray(can)
    # Short banner: columns u 0.005..0.166 of group 0; top 0.961.., body, 3-tooth tail.
    bw, blen = 4.4, 8.2
    for i, f in enumerate(FACTIONS):
        t = tex[f]; th, tw = t.shape[:2]
        col = Image.fromarray(t[:, int(0.005 * tw):int(0.166 * tw)])
        cw, ch = col.size
        alpha = np.array(col)[..., 3] > 40
        rows = np.where(alpha.any(1))[0]; first, last = int(rows[0]), int(rows[-1])
        width = alpha.sum(1) / float(cw)
        body = [r for r in range(first, last + 1) if width[r] > 0.9]
        tail_start = body[-1] if body else last - cw  # last full-width row: the tail begins after it
        tail_rows = (max(first, tail_start - int(0.35 * cw)), last + 1)
        top_rows = (first, tail_rows[0])
        upper = col.crop((0, top_rows[0], cw, top_rows[1])); tail = col.crop((0, tail_rows[0], cw, tail_rows[1]))
        out_w = int(round(bw * PX)); out_h = int(round(blen * PX))
        scale = out_w / cw
        tail_h = int(round(tail.size[1] * scale)); upper_h = out_h - tail_h
        banner = Image.new('RGBA', (out_w, out_h))
        up = np.array(upper.resize((out_w, max(1, int(round(upper.size[1] * scale)))), Image.LANCZOS)).astype(float)
        tl = np.array(tail.resize((out_w, tail_h), Image.LANCZOS)).astype(float)
        k = min(10, upper_h, up.shape[0] - upper_h if up.shape[0] > upper_h else 0)
        canvas = np.zeros((out_h, out_w, 4)); canvas[:upper_h] = up[:upper_h]; canvas[upper_h:] = tl
        # Cross-fade the seam: the cut is inside the plain cloth of both pieces.
        for r in range(k):
            w = (r + 1) / (k + 1.0)
            canvas[upper_h - k + r] = up[upper_h - k + r] * (1 - w) + tl[0] * w if False else up[upper_h - k + r] * (1 - w) + tl[min(r, tl.shape[0] - 1)] * w
        banner = Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))
        images[-1610 - i] = banner
    page = Image.new('RGBA', (1024, 512)); slots = {}; x = 0
    for ident in (-1600, -1601, -1602):
        page.paste(images[ident], (x, 0)); slots[str(ident)] = [14, x, 0, W, H]; x += W + 2
    x = 0
    for i in range(6):
        ident = -1610 - i; im = images[ident]
        page.paste(im, (x, H + 4)); slots[str(ident)] = [14, x, H + 4, im.size[0], im.size[1]]; x += im.size[0] + 2
    out = a.root / 'BetaGwent/ui/assets/battle104/cardfaces104.png'; out.parent.mkdir(parents=True, exist_ok=True); page.save(out)
    layout = dict(cardUnits=[right - left, top - bottom], bannerUnits=dict(x=0.12, y=0.33, w=bw, h=blen),
                  artAspect=round((right - left) / (top - bottom), 4), pxPerUnit=PX)
    src = a.root / 'BetaGwent/ui/src/BetaGwentHDArt.as'; raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text); bindings = json.loads(m[1]); bindings.update(slots)
    text = text[:m.start(1)] + json.dumps(bindings, separators=(',', ':')) + text[m.end(1):]
    if 'private static var Page14:Class' not in text:
        text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle104/cardfaces104.png",compression="true",quality="100")] private static var Page14:Class;\n private static var types:Array=')
        text = text.replace('Page12,Page13];', 'Page12,Page13,Page14];')
    if 'Page13,Page14];' not in text: raise SystemExit('HDArt layout changed')
    out_text = text.replace('\n', '\r\n') if crlf else text
    src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out_text.encode('utf8'))
    (a.root / 'docs/evidence/beta-cardfaces104.json').write_text(json.dumps(dict(stage=104, slots=slots, layout=layout,
        atlas=str(out), sha256=hashlib.sha256(out.read_bytes()).hexdigest()), indent=2) + '\n', 'utf8')
    print('card faces: 3 frames, 6 banners ->', out)


if __name__ == '__main__':
    main()

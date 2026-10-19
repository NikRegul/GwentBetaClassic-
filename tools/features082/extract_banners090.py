"""Rasterize the banner UV partition of Beta's large-card meshes.

The flatten blend shape preserves UVs. Sorting whole triangles by average Z
produces seams where cloth and ornaments intersect. Positive-U illustration
tiles must never sample the banner atlas. Keep only the EdgeTex banner UVs
and select the nearest surface per pixel.
"""
from pathlib import Path
import argparse, hashlib, json, sys
import numpy as np
from PIL import Image, ImageFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
import UnityPy
from UnityPy.helpers.MeshHelper import MeshHandler

FRONTS = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/cardassets/fronts'
FACTIONS = ['Neutral', 'Monsters', 'Nilfgaard', 'Northern', 'Scoiatael', 'Skellige']
ImageFile.MAXBLOCK = 16 * 1024 * 1024


def raster(mesh, texture, density=40):
    helper = MeshHandler(mesh); helper.process()
    v = np.array(helper.m_Vertices, dtype=float)
    for b in mesh.m_Shapes.vertices:
        v[b.index] += [b.vertex.x, b.vertex.y, b.vertex.z]
    uv = np.array(helper.m_UV0)
    triangles = np.concatenate([np.array(group) for group in helper.get_triangles()])
    areas = np.abs(np.cross(v[triangles[:, 1]] - v[triangles[:, 0]], v[triangles[:, 2]] - v[triangles[:, 0]])[:, 2])
    art_ids = np.argsort(areas)[-2:]
    # Nilfgaard Gold's sun crosses the atlas midpoint. In this exact mesh the
    # 689 negative-U ornament triangles precede the two illustration triangles;
    # its 28 frame triangles follow them. A generic half-atlas cut loses rays.
    nilf_gold = mesh.m_Name == 'Nilfgaard_LargeCardMesh_Gold'
    ornament_end = int(min(art_ids))
    if nilf_gold:
        assert sorted(art_ids.tolist()) == [697, 698] and len(triangles) == 729
    art = v[np.unique(triangles[art_ids])]
    left, bottom = art[:, :2].min(0); right, top = art[:, :2].max(0)
    lo = v[:, :2].min(0); hi = v[:, :2].max(0)
    width, height = np.ceil((hi - lo) * density).astype(int)
    rgba = np.zeros((height, width, 4), np.uint8)
    depth = np.full((height, width), np.inf)
    tex = np.array(texture.convert('RGBA'))
    th, tw = tex.shape[:2]
    for number, ids in enumerate(triangles):
        # CardFront: _EdgeTex is addressed by negative U (+1 offset).
        # Its left half holds cloth/ornaments; the right half holds frames.
        # Positive-U quads sample _MainTex (card illustration), NOT the banner
        # atlas. Treating those four art tiles as cloth caused the square seams.
        # Keep the existing card frame/illustration; export only the banner.
        if nilf_gold:
            if number >= ornament_end or uv[ids, 0].mean() >= 0:continue
        elif uv[ids, 0].mean() >= -.5:continue
        points = v[ids]
        xy = np.c_[(points[:, 0] - lo[0]) * density, (hi[1] - points[:, 1]) * density]
        a, b, c = xy
        den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(den) < 1e-8: continue
        x0, y0 = np.maximum(0, np.floor(xy.min(0))).astype(int)
        x1, y1 = np.minimum([width - 1, height - 1], np.ceil(xy.max(0))).astype(int)
        yy, xx = np.mgrid[y0:y1+1, x0:x1+1] + .5
        wa = ((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        wb = ((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
        weights = np.stack([wa, wb, 1-wa-wb], -1)
        inside = weights.min(-1) >= -1e-7
        z = weights @ points[:, 2]
        coords = weights @ uv[ids]
        # Combined shader uses frac(u) for the banner/frame atlas, while the
        # final two large triangles are the separate card illustration plane.
        coords[:, :, 0] %= 1
        tx = np.clip(coords[:, :, 0] * tw - .5, 0, tw-1)
        ty = np.clip((1-coords[:, :, 1]) * th - .5, 0, th-1)
        ix, iy = tx.astype(int), ty.astype(int)
        fx, fy = (tx-ix)[..., None], (ty-iy)[..., None]
        jx, jy = np.minimum(ix+1, tw-1), np.minimum(iy+1, th-1)
        sample = ((tex[iy, ix]*(1-fx)+tex[iy, jx]*fx)*(1-fy) + (tex[jy, ix]*(1-fx)+tex[jy, jx]*fx)*fy).astype(np.uint8)
        opaque = sample[:, :, 3] >= 26
        patch = depth[y0:y1+1, x0:x1+1]
        mask = inside & opaque & (z <= patch + 1e-6)
        patch[mask] = z[mask]
        rgba[y0:y1+1, x0:x1+1][mask] = sample[mask]
    im = Image.fromarray(rgba)
    box = im.getbbox(); assert box
    im = im.crop(box)
    x = lo[0] + box[0]/density; y = hi[1] - box[1]/density
    return im, dict(x=(x-left)/(right-left), y=(top-y)/(top-bottom),
                   w=im.width/density/(right-left), h=im.height/density/(top-bottom),
                   px=list(im.size), cardUnits=[right-left, top-bottom], artDepth=float(art[:,2].mean()))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=ROOT/'BetaGwent/build/banners090-seamfix-input')
    args = ap.parse_args(); args.out.mkdir(parents=True, exist_ok=False)
    env = UnityPy.load(str(FRONTS/'meshdata'))
    meshes = {o.read().m_Name:o.read() for o in env.objects if o.type.name=='Mesh'}
    env = UnityPy.load(str(FRONTS/'uber'))
    textures = {o.read().m_Name:o.read().image for o in env.objects if o.type.name=='Texture2D' and o.read().m_Name.endswith('_LargeCardMesh_Banner')}
    rows = {}; images = {}
    for faction in FACTIONS:
        for tier in ['Bronze', 'Silver', 'Gold']:
            key = faction+'_'+tier
            im, row = raster(meshes[faction+'_LargeCardMesh_'+tier], textures[faction+'_LargeCardMesh_Banner'])
            images[key] = im; rows[key] = row
            print(key, im.size, flush=True)
    size = tuple(1 << (max(im.size[i] for im in images.values())-1).bit_length() for i in [0,1])
    for key, im in images.items():
        page = Image.new('RGBA', size); page.paste(im,(0,0))
        png = args.out/(key+'.png'); page.save(png)
        page.save(args.out/(key+'.dds'), pixel_format='DXT5')
        rows[key]['sha256'] = hashlib.sha256(png.read_bytes()).hexdigest()
    report = dict(canvas=size, source='Beta 0.9.24.3.432 LargeCardMesh + flatten; EdgeTex banner UV partition, per-pixel min-Z, bilinear UV',
                  sourceHashes={n:hashlib.sha256((FRONTS/n).read_bytes()).hexdigest() for n in ['meshdata','uber']}, banners=rows)
    (args.out/'banners.json').write_text(json.dumps(report, indent=2),'utf8')


if __name__ == '__main__': main()

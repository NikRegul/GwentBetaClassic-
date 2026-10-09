"""Bake the original faction meshes and UVs into ten 2D board halves.

Orthographic adaptation for the native GFx atlas; source meshes/textures remain
unchanged. This is not a recreation of Unity lighting or perspective shaders.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'BetaGwent/build/beta-presentation91/boards/halfs/factions'
OUTPUT = ROOT/'BetaGwent/ui/assets/beta-boards'
FACTIONS = {1:2,2:4,3:8,4:16,5:32}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def mesh_data(path):
    vertices, uvs, faces = [], [], []
    for line in path.read_text('utf8').splitlines():
        fields=line.split()
        if not fields:continue
        if fields[0]=='v':vertices.append(list(map(float,fields[1:4])))
        elif fields[0]=='vt':uvs.append(list(map(float,fields[1:3])))
        elif fields[0]=='f':
            polygon=[tuple(int(v)-1 for v in field.split('/')[:2]) for field in fields[1:]]
            for i in range(1,len(polygon)-1):faces.append([polygon[0],polygon[i],polygon[i+1]])
    return np.array(vertices),np.array(uvs),faces

def bake(mesh,texture,scale,offset,size=None,world_bounds=None,frontmost=False):
    vertices,uvs,faces=mesh_data(mesh)
    width,height=size or (1536,540)
    lower,upper=vertices.min(axis=0),vertices.max(axis=0)
    if world_bounds:
        lower=np.array(world_bounds[0]);upper=np.array(world_bounds[1])
    screen=np.array(vertices,copy=True)
    screen[:,0]=(vertices[:,0]-lower[0])/(upper[0]-lower[0])*(width-1)
    screen[:,1]=(upper[1]-vertices[:,1])/(upper[1]-lower[1])*(height-1)
    pixels=np.array(Image.open(texture).convert('RGBA'))
    canvas=np.zeros((height,width,4),dtype=np.uint8)
    # Unity's battle camera is at Z=-185 looking towards +Z. The near surface
    # therefore has the smallest Z. Keep the legacy order opt-in for other bakes.
    depth=np.full((height,width),np.inf if frontmost else -np.inf)
    for face in faces:
        p=screen[[f[0] for f in face]]
        tex=uvs[[f[1] for f in face]]*scale+offset
        x0,y0=np.maximum(0,np.floor(p[:,:2].min(axis=0)).astype(int))
        x1,y1=np.minimum([width-1,height-1],np.ceil(p[:,:2].max(axis=0)).astype(int))
        if x1<x0 or y1<y0:continue
        a,b,c=p
        denominator=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(denominator)<1e-8:continue
        yy,xx=np.mgrid[y0:y1+1,x0:x1+1]
        wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/denominator
        wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/denominator
        wc=1-wa-wb
        z=wa*a[2]+wb*b[2]+wc*c[2]
        visible=(z<=depth[y0:y1+1,x0:x1+1]) if frontmost else (z>=depth[y0:y1+1,x0:x1+1])
        mask=(wa>=-1e-5)&(wb>=-1e-5)&(wc>=-1e-5)&visible
        uv=wa[:,:,None]*tex[0]+wb[:,:,None]*tex[1]+wc[:,:,None]*tex[2]
        tx=np.clip(uv[:,:,0]*(pixels.shape[1]-1),0,pixels.shape[1]-1)
        ty=np.clip((1-uv[:,:,1])*(pixels.shape[0]-1),0,pixels.shape[0]-1)
        ix,iy=np.floor(tx).astype(int),np.floor(ty).astype(int)
        fx,fy=(tx-ix)[:,:,None],(ty-iy)[:,:,None]
        sample=np.rint(pixels[iy,ix]*(1-fx)*(1-fy)
            +pixels[iy,np.minimum(ix+1,pixels.shape[1]-1)]*fx*(1-fy)
            +pixels[np.minimum(iy+1,pixels.shape[0]-1),ix]*(1-fx)*fy
            +pixels[np.minimum(iy+1,pixels.shape[0]-1),np.minimum(ix+1,pixels.shape[1]-1)]*fx*fy).astype(np.uint8)
        mask &= sample[:,:,3]>0
        canvas[y0:y1+1,x0:x1+1][mask]=sample[mask]
        depth[y0:y1+1,x0:x1+1][mask]=z[mask]
    image=Image.fromarray(canvas)
    return image if size else image.resize((512,180),Image.Resampling.LANCZOS)

def extract():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    entries,halves,hashes=[],[],{}
    sheet=Image.new('RGB',(1024,5*210),'#243340');draw=ImageDraw.Draw(sheet)
    for folder,faction in FACTIONS.items():
        directory=SOURCE/str(folder)
        metadata={int(p.name.split('-',1)[0]) if not p.name.startswith('-') else -int(p.name.split('-')[1]):(p,json.loads(p.read_text('utf8'))) for p in directory.glob('*.json')}
        files={int(p.name.split('-',1)[0]) if not p.name.startswith('-') else -int(p.name.split('-')[1]):p for p in directory.glob('*') if p.suffix in ('.obj','.png')}
        for side,name in [(1,'board_bottom'),(2,'board_top')]:
            go=next(ident for ident,(p,d) in metadata.items() if p.name.endswith('-GameObject.json') and d['m_Name']==name)
            filt=next(d for p,d in metadata.values() if p.name.endswith('-MeshFilter.json') and d['m_GameObject']['m_PathID']==go)
            renderer=next(d for p,d in metadata.values() if p.name.endswith('-MeshRenderer.json') and d['m_GameObject']['m_PathID']==go)
            material_path,mat=metadata[renderer['m_Materials'][0]['m_PathID']]
            binding=next(v for k,v in mat['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
            mesh,texture=files[filt['m_Mesh']['m_PathID']],files[binding['m_Texture']['m_PathID']]
            for p in [mesh,texture,material_path]:hashes[str(p)]=sha(p)
            image=bake(mesh,texture,[binding['m_Scale'][k] for k in ('x','y')],[binding['m_Offset'][k] for k in ('x','y')])
            whole=OUTPUT/f'faction-{faction}-side-{side}.png';image.save(whole)
            first=-1000-(folder-1)*8-(side-1)*4
            tiles=[]
            for col in range(4):
                tile=OUTPUT/f'{first-col}.png';image.crop((col*128,0,(col+1)*128,180)).save(tile)
                tiles.append(first-col)
                entries.append(dict(atlasId=first-col,name=f'{name}-faction-{faction}-tile-{col}',thumbnail=str(tile),thumbnailSha256=sha(tile),
                                    source=str(texture),sourceSha256=sha(texture),mesh=str(mesh),meshSha256=sha(mesh),faction=faction,side=side))
            halves.append(dict(faction=faction,side=side,image=str(whole),atlasIds=tiles))
            sheet.paste(image,((side-1)*512,(folder-1)*210),image)
            draw.text(((side-1)*512+8,(folder-1)*210+184),f'Faction {faction}, side {side}',fill='white')
    assert all(sha(Path(path))==digest for path,digest in hashes.items())
    background_dir=SOURCE.parents[1]/'backgrounds/multiplayer/0'
    original=next(background_dir.glob('*-BasicBackground.png'))
    hashes[str(original)]=sha(original)
    background=Image.open(original).convert('RGBA').resize((512,360),Image.Resampling.LANCZOS)
    for row in range(2):
        for col in range(4):
            ident=-1100-row*4-col;tile=OUTPUT/f'{ident}.png'
            background.crop((col*128,row*180,(col+1)*128,(row+1)*180)).save(tile)
            entries.append(dict(atlasId=ident,name=f'Beta-background-{row}-{col}',thumbnail=str(tile),thumbnailSha256=sha(tile),
                                source=str(original),sourceSha256=sha(original)))
    sheet.save(ROOT/'BetaGwent/ui/build/beta-boards91.png')
    (ROOT/'docs/evidence/beta-boards91.json').write_text(json.dumps(dict(halves=halves,sourceHashes=hashes,sourceUnchanged=True,tiles=entries,
        adaptation='Original meshes/UVs, orthographic unlit 2D projection, 512x180 per half',nativeRuntimeVerified=False),indent=2)+'\n','utf8')
    return entries

if __name__=='__main__':print('Baked',len(extract()),'atlas tiles for ten faction halves and background.')

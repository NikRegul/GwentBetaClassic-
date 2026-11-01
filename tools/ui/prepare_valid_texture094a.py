"""Stage ValidVFX's shared flare inside unused editor-atlas space.

Preserve every assigned cell and all BC3 blocks outside the unused slot. The
source shader's textureRGB*textureAlpha^2 is preprocessed; its vertex tint,
brightness and vertex alpha must later multiply RGB in GFx, with output alpha1.
No canonical asset, prepared menu or release is modified.
"""
from pathlib import Path
import argparse,copy,hashlib,io,json
import numpy as np
from PIL import Image
from editor_shader094 import sample
ROOT=Path(__file__).resolve().parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audit',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
 metadata=ROOT/'data/beta924/design/editor_vfx094.json';original=json.loads(metadata.read_text('utf8'))
 atlas_file=ROOT/'BetaGwent/ui/assets/elements164/Elements.png';blocks_file=ROOT/'BetaGwent/ui/assets/editor094/append-bc3.bin'
 atlas_raw=atlas_file.read_bytes();old_blocks=blocks_file.read_bytes()
 assert sha(atlas_raw)==original['extendedAtlasSha256'] and sha(old_blocks)==original['appendedBlocksSha256']
 audit=json.loads((a.audit/'audit.json').read_text('utf8'));assert sha((ROOT/audit['source']).read_bytes())==audit['sourceSha256']
 material=audit['materials']['3040660544023381124'];assert material['floats']==dict(_AlphaPower=1.0,_Brightness=2.0)
 assert material['colors']['_TintColor']==dict(r=1.0,g=1.0,b=1.0,a=1.0)
 assert audit['shaders'][material['shader']]['blend']==dict(srcBlend=1.0,destBlend=1.0,blendOp=0.0)
 texture=material['textures'][0];assert texture['property']=='_MainTex' and texture['scale']==dict(x=1.0,y=1.0) and texture['offset']==dict(x=0.0,y=0.0)
 source_file=a.audit/'textures'/(texture['texture']+'.png');assert sha(source_file.read_bytes())==audit['textures'][texture['texture']]['pngSha256']
 source=np.array(Image.open(source_file).convert('RGBA'),np.float32)/255
 th,tw=source.shape[:2];assert tw==th==128
 rgb=source[:,:,:3]*source[:,:,3:4]**2
 flare=Image.fromarray(np.rint(np.concatenate([rgb,np.ones((th,tw,1),np.float32)],axis=2)*255).astype(np.uint8))
 before=Image.open(io.BytesIO(atlas_raw)).convert('RGBA');w,h=before.size;base_h=original['baseSize'][1]
 assert [w,h]==original['size'] and w%4==h%4==base_h%4==0
 occupied=np.zeros((h-base_h,w),bool)
 for x,y,rw,rh in original['rects']:occupied[y-base_h:y-base_h+rh,x:x+rw]=True
 # The first 4-aligned empty slot is deterministic, no existing cell is moved.
 slot=next(([x,y,tw,th] for y in range(base_h,h-th+1,4) for x in range(0,w-tw+1,4)
            if not occupied[y-base_h:y-base_h+th,x:x+tw].any()),None)
 assert slot is not None,'No free source-sized flare slot; do not shrink the source texture to fit'
 x,y,_,_=slot;after=before.copy();after.paste(flare,(x,y))
 for rx,ry,rw,rh in original['rects']:
  assert before.crop((rx,ry,rx+rw,ry+rh)).tobytes()==after.crop((rx,ry,rx+rw,ry+rh)).tobytes()
 assert before.crop((0,0,w,base_h)).tobytes()==after.crop((0,0,w,base_h)).tobytes()
 encoded=io.BytesIO();flare.save(encoded,format='DDS',pixel_format='DXT5');dds=encoded.getvalue()
 assert dds[84:88]==b'DXT5' and len(dds)==128+tw*th
 new_blocks=bytearray(old_blocks);patch=dds[128:];touched=set()
 for row in range(th//4):
  dest=(((y-base_h)//4+row)*(w//4)+x//4)*16;src=row*(tw//4)*16;length=(tw//4)*16
  new_blocks[dest:dest+length]=patch[src:src+length];touched.update(range(dest//16,(dest+length)//16))
 assert len(new_blocks)==len(old_blocks)
 for index in range(len(old_blocks)//16):
  if index not in touched:assert old_blocks[index*16:(index+1)*16]==new_blocks[index*16:(index+1)*16]
 decoded=np.array(Image.open(io.BytesIO(dds)).convert('RGBA'),np.float32)/255
 # Quantify preprocessing-before-bilinear and BC3 error separately. This is
 # an approximation report, not native colour-space/render acceptance.
 uv=np.random.default_rng(940025).random((16384,2),dtype=np.float32)
 exact=sample(source,uv,0);expected=exact[:,:3]*exact[:,3:4]**2
 preprocessed=sample(np.array(flare,np.float32)/255,uv,0)[:,:3]
 compressed=sample(decoded,uv,0)[:,:3]
 def error(v):
  delta=(v-expected)*2 # source maximum brightness before vertex attenuation
  return dict(maxAbsolute=float(abs(delta).max()),rms=float(np.sqrt(np.mean(delta**2))))
 out.mkdir();after.save(out/'Elements.png');flare.save(out/'ValidFlare.png');(out/'append-bc3.bin').write_bytes(new_blocks)
 data=copy.deepcopy(original);data['rects'].append(slot);data['extendedAtlasSha256']=sha((out/'Elements.png').read_bytes());data['appendedBlocksSha256']=sha(new_blocks)
 data['validVfx094a']=dict(index=len(data['rects'])-1,sourceTexture=texture['texture'],sourceShader=material['shader'],
  textureRgb='sourceRGB*sourceAlpha^2',outputAlpha=1,vertexRgbMultiplier='sourceVertexRGB*2*sourceVertexAlpha',
  continuousLifetimeBoundsVerified=False,nativeAppearanceVerified=False)
 (out/'editor_vfx094.json').write_text(json.dumps(data,indent=2)+'\n','utf8')
 report=dict(complete=True,sourceSha256=audit['sourceSha256'],sourceTextureSha256=sha(source_file.read_bytes()),
  previousMetadataSha256=sha(metadata.read_bytes()),previousAtlasSha256=sha(atlas_raw),previousBlocksSha256=sha(old_blocks),
  slot=slot,cellIndex=data['validVfx094a']['index'],atlasSizeUnchanged=True,assignedPixelsUnchanged=True,
  allBlocksOutsideUnusedSlotUnchanged=True,addedTextureBytes=0,patchedUnusedBc3Bytes=tw*th,
  preprocessingError=error(preprocessed),bc3AndPreprocessingError=error(compressed),samples=len(uv),
  canonicalUiChanged=False,nativeMenuSizeVerified=False,nativeGameplayVerified=False,
  nextStep='Compile isolated GFx implementation with RGB vertex-alpha multiplication and test the real menu budget and lifecycle before adoption')
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))

if __name__=='__main__':main()

"""Isolated ValidVFX preview using the extracted pixel shader and axis recipes.

No canonical atlas, menu, accepted battle effect or ready release is changed.
The coordinate box encloses every sampled rotated quad; no card-sized crop.
"""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np
from PIL import Image,ImageDraw
from editor_shader094 import MaterialProgram
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--audit',type=Path,required=True);p.add_argument('--shaders',type=Path,required=True)
 p.add_argument('--recipes',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
 audit=json.loads((a.audit/'audit.json').read_text('utf8'));recipe=json.loads((a.recipes/'recipes.json').read_text('utf8'))
 proof=json.loads((a.recipes/'report.json').read_text('utf8'));shaders=json.loads((a.shaders/'report.json').read_text('utf8'))
 assert proof['complete'] and proof['sourceUnchanged'] and not proof['canonicalUiChanged']
 assert audit['sourceSha256']==proof['sourceSha256']==shaders['sourceSha256']==sha(ROOT/audit['source'])
 preset=recipe['presets']['ValidVFX'];timeline=json.loads((a.recipes/'packets.json').read_text('utf8'))['ValidVFX']
 assert len(preset['emitters'])==2 and len(timeline)==48 and not proof['omitted']
 assert all(e.get('sizeOverY') for e in preset['emitters'])
 materials={}
 for node in audit['presets']['ValidVFX']['nodes']:
  assert node['scale']==dict(x=1.0,y=1.0,z=1.0) and node['rotation']==dict(x=0.0,y=0.0,z=0.0,w=1.0)
  particle=next((c for c in node['components'] if c['type']=='ParticleSystem'),None)
  renderer=next((c for c in node['components'] if c['type']=='ParticleSystemRenderer'),None)
  if not particle:continue
  config=renderer['configuration'];assert config['m_RenderMode']==0 and config['m_RenderAlignment']==2
  assert config['m_Pivot']==dict(x=0.0,y=0.0,z=0.0) and len(renderer['materials'])==1
  mid=renderer['materials'][0];materials[mid]=MaterialProgram(a.audit,a.shaders,audit,mid)
  assert materials[mid].shader['blend']==dict(srcBlend=1.0,destBlend=1.0,blendOp=0.0)
 assert len(materials)==1
 # Source root translation is retained relative to the stat-widget origin.
 root=preset['sourceRootPose']['position'];boxes=[]
 for frame in timeline:
  for part in frame['particles']:
   pose=part['pose'];angle=math.radians(pose['angle']);co,si=abs(math.cos(angle)),abs(math.sin(angle))
   ex,ey=(co*pose['w']+si*pose['h'])/2,(si*pose['w']+co*pose['h'])/2
   cx,cy=pose['x']+root[0],pose['y']-root[1];boxes.append([cx-ex,cy-ey,cx+ex,cy+ey])
 x0,y0=math.floor(min(b[0] for b in boxes))-4,math.floor(min(b[1] for b in boxes))-4
 x1,y1=math.ceil(max(b[2] for b in boxes))+4,math.ceil(max(b[3] for b in boxes))+4
 w,h=x1-x0,y1-y0;assert 0<w<1024 and 0<h<1024
 xx,yy=np.meshgrid(x0+np.arange(w)+.5,y0+np.arange(h)+.5)
 out.mkdir();(out/'frames').mkdir();selected=[0,5,10,20,32,47];sheet=Image.new('RGB',(w*3,(h+24)*2));frames=[]
 emitters={e['texture']:e for e in preset['emitters']};assert len(emitters)==1
 # Both source emitters share the same material and texture.
 count=0
 for index,frame in enumerate(timeline):
  light=np.zeros((h,w,3),np.float32)
  for part in frame['particles']:
   pose=part['pose'];angle=math.radians(pose['angle']);dx=xx-(pose['x']+root[0]);dy=yy-(pose['y']-root[1])
   u=(math.cos(angle)*dx+math.sin(angle)*dy)/pose['w']+.5
   v=.5-(-math.sin(angle)*dx+math.cos(angle)*dy)/pose['h']
   inside=(u>=0)&(u<1)&(v>=0)&(v<1);iy,ix=np.where(inside)
   if not len(ix):continue
   assert part['columns']==1 and part['rows']==1 and part['blend']=='add'
   uv=np.c_[u[inside],v[inside],np.zeros(len(ix)),np.ones(len(ix))]
   color=np.tile([pose[k] for k in ['r','g','b','a']],(len(ix),1))
   program=next(iter(materials.values()));pixels=program.shade({'v1':uv,'v2':color},frame['seconds'])
   assert np.isfinite(pixels).all() and np.all(pixels[:,3]==1)
   light[iy,ix]+=np.maximum(0,pixels[:,:3]);count+=1
  image=Image.fromarray(np.round(np.clip(light,0,1)*255).astype(np.uint8));image.save(out/'frames'/('add-%02d.png'%index))
  # A labelled neutral stat panel is only context, not a recreation of the UI.
  bg=np.zeros_like(light);bg[:]=[.10,.14,.15]
  image=Image.fromarray(np.round(np.clip(bg+light,0,1)*255).astype(np.uint8))
  if index in selected:
   tile=Image.new('RGB',(w,h+24));tile.paste(image,(0,24));ImageDraw.Draw(tile).text((8,6),'ValidVFX %.3f s'%frame['seconds'],fill='white')
   i=selected.index(index);sheet.paste(tile,((i%3)*w,(i//3)*(h+24)))
  frames.append(dict(seconds=frame['seconds'],sha256=sha(out/'frames'/('add-%02d.png'%index))))
 sheet.save(out/'contact-sheet.png')
 report=dict(complete=True,sourceSha256=audit['sourceSha256'],auditSha256=sha(a.audit/'audit.json'),
  recipesSha256=sha(a.recipes/'recipes.json'),packetsSha256=sha(a.recipes/'packets.json'),shaderReportSha256=sha(a.shaders/'report.json'),
  evaluatedAssemblySha256=hashlib.sha256(next(iter(materials.values())).assembly.encode()).hexdigest(),
  extent=[x0,y0,x1,y1],pixels=[w,h],rootPose=preset['sourceRootPose'],frames=frames,shadedParticlePackets=count,
  sourceShaderInstructionsEvaluated=True,blend='One/One Add',canonicalUiChanged=False,nativeGameplayVerified=False,
  limitations=['Offline XY projection at one texel per source unit; sampled axis curves and deterministic source-particle model',
   'Source pixel instructions with bilinear mip0; GPU colour-space/derivatives and native Scaleform appearance remain unverified',
   'Sampled enclosing bounds are not continuous-lifetime bounds or proof of a native resource budget; no effect is shipped'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps({k:report[k] for k in ['complete','pixels','extent','shadedParticlePackets']}))

if __name__=='__main__':main()

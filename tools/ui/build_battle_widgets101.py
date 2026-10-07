"""Compact original Beta battle widgets; never rewrites original client assets."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from beta_board_sources import bake
OUT=ROOT/'BetaGwent/ui/assets/battle101';OUT.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(items):
 free=[(0,0,512,512)];result={}
 for ident,im in sorted(items.items(),key=lambda v:(-max(v[1].size),-v[1].width*v[1].height)):
  w,h=im.size;options=[(min(fw-w,fh-h),fw*fh-w*h,x,y) for x,y,fw,fh in free if fw>=w and fh>=h]
  if not options:raise ValueError('Widgets exceed the 1 MiB atlas budget: '+str(ident))
  _,_,x,y=min(options);result[ident]=(x,y,w,h);next_free=[]
  for fx,fy,fw,fh in free:
   if x+w<=fx or x>=fx+fw or y+h<=fy or y>=fy+fh:next_free.append((fx,fy,fw,fh));continue
   if x>fx:next_free.append((fx,fy,x-fx,fh))
   if x+w<fx+fw:next_free.append((x+w,fy,fx+fw-x-w,fh))
   if y>fy:next_free.append((fx,fy,fw,y-fy))
   if y+h<fy+fh:next_free.append((fx,y+h,fw,fy+fh-y-h))
  free=[r for i,r in enumerate(next_free) if not any(i!=j and q[0]<=r[0] and q[1]<=r[1] and q[0]+q[2]>=r[0]+r[2] and q[1]+q[3]>=r[1]+r[3] and (q!=r or j<i) for j,q in enumerate(next_free))]
 return result
def main():
 sources={};items={};records=[]
 def remember(p):sources[str(p)]=sha(p)
 def add(ident,im,name,source,pid,resize=None):
  im=im.convert('RGBA')
  if resize:im=im.resize(resize,Image.Resampling.LANCZOS)
  items[ident]=im;records.append(dict(id=ident,name=name,source=str(source),pathId=pid,size=list(im.size)))
 p=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets';remember(p)
 env=UnityPy.load(str(p));objects={o.path_id:o for o in env.objects}
 mask=np.asarray(objects[655].read().image.convert('RGB').resize((256,256),Image.Resampling.LANCZOS))
 base=np.asarray(objects[725].read().image.convert('RGBA')).copy()
 base[:,:,3]=np.maximum(mask[:,:,1],mask[:,:,2])
 add(-1500,Image.fromarray(base),'CoinNeutralBase + original RGB mask',p,725,(128,128))
 for i,pid in enumerate((533,546,512,758,592)):add(-1501-i,objects[pid].read().image,objects[pid].read().m_Name,p,pid,(64,64))
 back=objects[650].read().image.convert('RGBA').crop((0,0,384,512))
 add(-1510,back,'Neutral card back face; excludes mesh side UV',p,650,(128,180))
 p=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber/panels';remember(p)
 env=UnityPy.load(str(p));sprites={o.read().m_Name:o for o in env.objects if o.type.name=='Sprite'}
 names=['board-icon-graveyard','board-icon-deck','board-icon-hand','big_crown_empty','big_crown_half_blue','big_crown_full_blue','big_crown_half_red','big_crown_full_red']
 for i,name in enumerate(names):
  o=sprites[name];add(-1520-i,o.read().image,name,p,o.path_id,(48,48) if i<3 else (84,74))
 for faction in range(1,6):
  directory=ROOT/f'BetaGwent/build/beta-presentation91/boards/halfs/factions/{faction}'
  for side,suffix in ((1,'Bottom'),(2,'Top')):
   mesh=next(directory.glob('*BoardRibbon_'+suffix+'*.obj'))
   material=next(q for q in directory.glob('*Material.json') if 'Ribbon'+suffix in json.loads(q.read_text('utf8'))['m_Name'])
   data=json.loads(material.read_text('utf8'));binding=next(v for k,v in data['m_SavedProperties']['m_TexEnvs'] if k=='_MainTex')
   texture=next(directory.glob(str(binding['m_Texture']['m_PathID'])+'-*.png'))
   for q in (mesh,material,texture):remember(q)
   art=bake(mesh,texture,[binding['m_Scale'][k] for k in ('x','y')],[binding['m_Offset'][k] for k in ('x','y')],size=(180,64))
   # Unity mesh export reverses the screen X convention. Keep the pointed
   # ribbon tail on the left, as in the original match HUD reference.
   add(-1530-(faction-1)*2-(side-1),ImageOps.mirror(art),data['m_Name'],texture,binding['m_Texture']['m_PathID'])
 slots=pack(items);atlas=Image.new('RGBA',(512,512))
 for ident,im in items.items():
  x,y,w,h=slots[ident];atlas.paste(im,(x,y));im.save(OUT/(str(-ident)+'.png'))
 path=OUT/'battle_widgets101.png';atlas.save(path)
 source=ROOT/'BetaGwent/ui/src/BetaGwentHDArt.as';text=source.read_text('utf-8-sig')
 import re
 match=re.search(r'private static var slots:Object=(\{.*?\});',text)
 bindings=json.loads(match[1]);bindings.update({str(k):[12,*v] for k,v in slots.items()})
 text=text[:match.start(1)]+json.dumps(bindings,separators=(',',':'))+text[match.end(1):]
 if 'private static var Page12:Class' not in text:
  text=text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle101/battle_widgets101.png",compression="true",quality="100")] private static var Page12:Class;\n private static var types:Array=')
  text=text.replace('Page10,Page11];','Page10,Page11,Page12];')
 text=text.replace('var s:Array=slots[id];var page:int=s[0];var bitmap:Bitmap;','var s:Array=slots[id];var page:int=s[0];var pixelScale:Number=page==12?1:0.75;var bitmap:Bitmap;')
 text=text.replace('(s[1]+s[3])*0.75','(s[1]+s[3])*pixelScale').replace('(s[2]+s[4])*0.75','(s[2]+s[4])*pixelScale')
 text=text.replace('(s[1]+x)*0.75','(s[1]+x)*pixelScale').replace('(s[2]+y)*0.75','(s[2]+y)*pixelScale').replace('cw*0.75','cw*pixelScale').replace('ch*0.75','ch*pixelScale')
 source.write_text(text,'utf8')
 report=dict(stage=101,widgets=records,slots=slots,atlas=str(path),size=[512,512],rawBytes=512*512*4,sha256=sha(path),sources=sources,originalsUnchanged=all(sha(Path(q))==h for q,h in sources.items()),unityShaderParity=False)
 (ROOT/'docs/evidence/beta-battle-widgets101.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print(str(len(items))+' original widgets packed into one 512x512 page')
if __name__=='__main__':main()

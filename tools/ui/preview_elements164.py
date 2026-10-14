"""Offline contact sheet from packets exported by the actual ActionScript model."""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/elements164'
data=json.loads((BASE/'preview-packets.json').read_text())
names=['LightMagic','DarkMagic','Physical','Fire','Ice','Earth','Air']
atlases=[Image.open(ROOT/'BetaGwent/ui/assets/elements164/Elements.png').convert('RGBA')]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
W,H=260,175
sheet=Image.new('RGBA',(W*4,H*len(data['previews'])),(24,22,20,255))
def cell(tile,pose):
 r=data['rects'][tile];im=atlases[r[0]].crop((r[1],r[2],r[1]+r[3],r[2]+r[4]))
 channels=list(im.split())
 for k in range(4):channels[k]=channels[k].point(lambda v:v*pose[['r','g','b','a'][k]])
 im=Image.merge('RGBA',channels)
 w,h=max(1,min(1400,round(pose['w']))),max(1,min(1400,round(pose['h'])))
 return im.resize((w,h),Image.Resampling.BILINEAR).rotate(-pose['angle'],Image.Resampling.BICUBIC,expand=True)
for row,preview in enumerate(data['previews']):
 for col,frame in enumerate(preview['frames']):
  panel=Image.new('RGBA',(W,H),(49,45,38,255));draw=ImageDraw.Draw(panel)
  draw.rectangle((0,90,W,94),fill=(96,83,63));draw.rectangle((104,44,156,122),fill=(66,79,71),outline=(178,160,110),width=2)
  method=preview['preset']['method'];ext=preview['preset']['extent'];ux=220/ext[0] if method>=2 else 52/22;uy=110/ext[1] if method>=2 else ux
  for s in frame['static']:
   pose=s.get('layout') or dict(w=s['size'][0]*ux,h=s['size'][1]*uy,r=s['rgb'][0],g=s['rgb'][1],b=s['rgb'][2],a=s['alpha']*.7,angle=0)
   im=cell(s['tile'][1],pose);panel.alpha_composite(im,(round(W/2+pose.get('x',0)-im.width/2),round(83+pose.get('y',0)-im.height/2)))
  for particle in frame['particles']:
   p=particle['pose']
   if not p['visible']:continue
   pose=dict(p,w=p['w']*ux,h=p['h']*uy)
   im=cell(particle['tile'][1]+p['frame'],pose)
   panel.alpha_composite(im,(round(W/2+p['x']*ux-im.width/2),round(83+p['y']*uy-im.height/2)))
  draw=ImageDraw.Draw(panel);draw.rectangle((0,0,W,34),fill=(24,22,20,255));draw.text((5,2),preview['name'],font=font,fill='white');draw.text((5,18),f"{frame['seconds']:.2f}s",font=font,fill=(188,182,166))
  sheet.alpha_composite(panel,(col*W,row*H))
output=BASE/'elements-contact.png';sheet.convert('RGB').save(output)
print(output)

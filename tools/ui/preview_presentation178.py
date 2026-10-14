"""Presentation preview from actual AS particle packets, source blend per emitter.

This is a 2D projection preview; the retail Scaleform renderer still needs a
game check. No ordinary smoke/leaf particle is silently turned into light.
"""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont,ImageChops
root=Path(__file__).resolve().parents[2];base=root/'tmp/presentation178';base.mkdir(exist_ok=True)
data=json.loads((base/'packets.json').read_text())
proof=json.loads((root/'docs/evidence/elements164.json').read_text())
additive={e['particle'] for e in proof['sourceParticles'] if 'Additive' in e['shader']}
atlas=Image.open(root/'BetaGwent/ui/assets/elements164/Elements.png').convert('RGBA')
card=Image.open(root/'BetaGwent/ui/assets/cards/112101.png').convert('RGBA').resize((84,118))
names=['CardLandingEffect','GoldLanding','CardFrostLandingEffect','CardMistLandingEffect','CardRainLandingEffect','SpawnBlink','AmbushEffect','NatureTransform','PromoteSimpleVFX','DemoteParticleSimpleVFX']
W,H=300,214;ux=84/22;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
sheet=Image.new('RGB',(W*4,H*len(names)),(35,32,27))
for row,name in enumerate(names):
 preview=next(p for p in data['previews'] if p['name']==name)
 for col,frame in enumerate(preview['frames']):
  panel=Image.new('RGBA',(W,H),(49,45,38,255));panel.alpha_composite(card,(W//2-42,60))
  for particle in frame['particles']:
   p=particle['pose']
   if not p['visible']:continue
   rect=data['rects'][particle['tile'][1]+p['frame']]
   im=atlas.crop((rect[1],rect[2],rect[1]+rect[3],rect[2]+rect[4]))
   channels=list(im.split())
   for k,key in enumerate(['r','g','b','a']):channels[k]=channels[k].point(lambda v:v*p[key])
   im=Image.merge('RGBA',channels)
   w,h=p['w']*ux,p['h']*ux;scale=min(1,55*ux/max(w,h));w=max(1,round(w*scale));h=max(1,round(h*scale))
   im=im.resize((w,h),Image.Resampling.BILINEAR).rotate(-p['angle'],Image.Resampling.BICUBIC,expand=True)
   x=round(W/2+p['x']*ux-im.width/2);y=round(119+p['y']*ux-im.height/2)
   if particle['particleId'] in additive:
    light=Image.new('RGBA',(W,H));light.alpha_composite(im,(x,y))
    rgb=light.convert('RGB');alpha=light.getchannel('A');rgb=Image.merge('RGB',[ImageChops.multiply(ch,alpha) for ch in rgb.split()])
    panel=ImageChops.add(panel.convert('RGB'),rgb).convert('RGBA')
   else:panel.alpha_composite(im,(x,y))
  draw=ImageDraw.Draw(panel);draw.rectangle((0,0,W,36),fill=(24,22,20));draw.text((5,3),name,font=font,fill='white');draw.text((5,19),f"{frame['seconds']:.2f}s / source materials",font=font,fill=(186,180,164))
  sheet.paste(panel.convert('RGB'),(col*W,row*H))
output=base/'presentation-contact.png';sheet.save(output);print(output)

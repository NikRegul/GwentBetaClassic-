"""Presentation preview from actual AS particle packets, source blend per emitter.

This is a 2D projection preview; the retail Scaleform renderer still needs a
game check. No ordinary smoke/leaf particle is silently turned into light.
"""
from pathlib import Path
import json,math
from PIL import Image,ImageDraw,ImageFont,ImageChops
root=Path(__file__).resolve().parents[2];base=root/'tmp/status191';base.mkdir(exist_ok=True)
data=json.loads((root/'tmp/status-packets191.json').read_text())
proof=json.loads((root/'docs/evidence/elements164.json').read_text())
additive={e['particle'] for e in proof['sourceParticles'] if 'Additive' in e['shader']}
atlas=Image.open(root/'BetaGwent/ui/assets/elements164/Elements.png').convert('RGBA')
card=Image.open(root/'BetaGwent/ui/assets/cards/112101.png').convert('RGBA').resize((84,118))
names=['ResilienceTokenShow','ResilienceTokenHide','SpyingTokenShow','RevealTokenShow','CardTimerVFX','ArmorIncrease','ArmorDecrease']
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
output=base/'status-particles-contact.png';sheet.save(output);print(output)

# Separate badge preview, using the same normalized tables/positions as the
# AS renderer. Source meshes supply the artwork; 3D rotation is not emulated.
manifest=json.loads((root/'BetaGwent/build/element-vfx163/manifest.json').read_text())
textures={t['pathId']:t for t in manifest['textures'] if t['asset']=='sharedassets8.assets'}
def texture(ident):return Image.open(root/textures[ident]['image']).convert('RGBA')
tables=json.loads((root/'docs/evidence/status-source191.json').read_text())['tables']
eye=texture(793);iris=texture(504);eye.alpha_composite(iris,((eye.width-iris.width)//2,(eye.height-iris.height)//2-2))
parts={'ResilienceToken':[(754,'bar',.5,.9475,.86,.095),(530,'left',.075,.945,.09,.17),(786,'right',.925,.945,.09,.17),(548,'shield',.5,.905,.26,.27)],
 'SpyingToken':[(793,'eye',.58,(3+21)/118,.5,21/118)],'RevealToken':[(573,'icon',69/84,103/118,34/84,34/118)]}
bw,bh=240,190;badges=Image.new('RGB',(bw*5,bh*len(tables)),(35,32,27))
def sample(v,p):
 at=p*(len(v)-1);a=int(at);b=min(len(v)-1,a+1);return v[a]+(v[b]-v[a])*(at-a)
for row,(key,clip) in enumerate(tables.items()):
 name=key.rsplit('_',1)[0]
 for col,progress in enumerate([0,.25,.5,.75,1]):
  panel=Image.new('RGBA',(bw,bh),(49,45,38,255));panel.alpha_composite(card,(bw//2-42,48))
  for ident,part,x,y,w,h in parts[name]:
   d=clip['parts'][part];sx=sample(d['sx'],progress);sy=sample(d['sy'],progress);alpha=sample(d['alpha'],progress)
   if sx<=.0001 or sy<=.0001 or alpha<=.0001 or key.endswith('_hide') and progress==1:continue
   im=(eye if ident==793 else texture(ident)).resize((max(1,round(w*84*sx)),max(1,round(h*118*sy))),Image.Resampling.LANCZOS)
   im.putalpha(im.getchannel('A').point(lambda v:v*max(0,min(1,alpha))))
   cx=bw/2-42+x*84+sample(d['dx'],progress)*84/22;cy=48+y*118-sample(d['dy'],progress)*84/22
   panel.alpha_composite(im,(round(cx-im.width/2),round(cy-im.height/2)))
  draw=ImageDraw.Draw(panel);draw.text((5,4),key,font=font,fill='white');draw.text((5,21),f'{progress*clip["ms"]:.0f} ms / original curves',font=font,fill=(186,180,164));badges.paste(panel.convert('RGB'),(col*bw,row*bh))
output=base/'status-badges-contact.png';badges.save(output);print(output)

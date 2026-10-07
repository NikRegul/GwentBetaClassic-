"""Static composition of source assets for layout review, not a game screenshot."""
from pathlib import Path
import json,re
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];UI=ROOT/'BetaGwent/ui'
s=(UI/'src/BetaGwentHDArt.as').read_text('utf8')
slots=json.loads(re.search(r'private static var slots:Object=(\{.*?\});',s)[1])
pages=['cards-'+str(i) for i in range(9)]+['boards','interface-10','interface-11']
canvas=Image.new('RGBA',(1920,1080),'#29261f')
def art(ident,w,h):
 page,x,y,sw,sh=slots[str(ident)];scale=1 if page==12 else .75
 source=UI/'assets/battle101/battle_widgets101.png' if page==12 else UI/('assets/compact98/'+pages[page]+'.png')
 im=Image.open(source).convert('RGBA').crop((round(x*scale),round(y*scale),round((x+sw)*scale),round((y+sh)*scale)))
 return im.resize((w,h),Image.Resampling.LANCZOS)
def paint(ident,w,h,x,y,tint=None):
 im=art(ident,w,h)
 if tint:
  r,g,b,a=im.split();r=r.point(lambda v:round(v*tint[0]));g=g.point(lambda v:round(v*tint[1]));b=b.point(lambda v:round(v*tint[2]));im=Image.merge('RGBA',(r,g,b,a))
 canvas.alpha_composite(im,(x,y))
def main():
 paint(-1311,2160,1080,-120,0)
 for side,faction in ((1,2),(2,1)):
  paint(-1300-faction*2-(side-1),1160,400,312,554 if side==1 else 154)
  y=706 if side==1 else 338
  paint(-1530-faction*2-(side-1),324,114,72,y,(.25,.68,1) if side==1 else (1,.22,.16))
  paint(-1524 if side==1 else -1523,84,74,95,y+23)
  paint(200158 if side==1 else 200164,72,101,270 if side==1 else 90,946 if side==1 else 184)
  for zone,x in ((32,1560),(16,1716)):
   py=946 if side==1 else 12;paint(-1510,72,101,x,py);paint(-1501-faction,30,30,x+21,py+36);paint(-1520 if zone==32 else -1521,32,32,x+81,py+66)
  paint(-1522,27,27,76 if side==1 else 96,1018 if side==1 else 302)
 paint(-1500,124,124,214,488,(.2,.68,1));paint(-1503,68,68,242,516)
 draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22);big=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',58)
 for side,y,score in ((1,706,'72'),(2,338,'156')):draw.text((238,y+28),score,font=big,fill='white')
 for side,y in ((1,584),(2,218)):
  for i in range(3):
   draw.text((363,y+i*104+25),str([16,24,32][i]),font=font,fill='white')
   for j,ident in enumerate((112103,113308,113316,112102)):
    paint(ident,63,88,665+j*72,y+i*104+4)
 for i,ident in enumerate((112103,113308,112102,113316,112103,112101,112104)):paint(ident,94,132,484+i*112,924)
 draw.text((76,947),'Геральт',font=font,fill='#7acae4');draw.text((90,151),'Соперник',font=font,fill='#eaa18b')
 draw.text((76,867),'P · пас   L · лидер\nD · колода   G / H · сброс',font=font,fill='#beb7a4')
 for y in (12,946):
  draw.text((1640,y+25),'8',font=font,fill='white');draw.text((1796,y+25),'6',font=font,fill='white')
 for y in (754,810,868):draw.rectangle((1532,y,1844,y+48),outline='#977c52',width=2)
 draw.rectangle((1504,130,1872,668),outline='#977c52',width=3)
 draw.text((1518,148),'STATIC ASSET LAYOUT\nNot a native game render',font=font,fill='#d8d0bb')
 target=ROOT/'BetaGwent/build/layout101-preview.png';canvas.convert('RGB').save(target);print(target)
if __name__=='__main__':main()

"""Render source-driven layout proofs, not native game screenshots."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];BUILD=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BetaGwent/build/release082-polish1'
data=json.loads((BUILD/'ui-polish-tests.json').read_text('utf8'));proofs=data['previews'][:3]
sheet=Image.new('RGB',(1440,1040),'#111715');draw=ImageDraw.Draw(sheet)
fontpath='C:/Windows/Fonts/arial.ttf'
for index,p in enumerate(proofs):
    if p['screen']=='confirm':p['width']=700;p['height']=260
    scale=min(640/p['width'],720/p['height']);w,h=round(p['width']*scale),round(p['height']*scale)
    canvas=Image.new('RGB',(w,h),'#141c1c');d=ImageDraw.Draw(canvas)
    d.rounded_rectangle((6,6,w-7,h-7),radius=12,outline='#a28b5d',width=2)
    for n in p['nodes']:
        x,y,width,height=[round(n[k]*scale) for k in ['x','y','w','h']]
        if p['screen']=='confirm':x-=round(610*scale);y-=round(410*scale)
        value=n.get('value','')
        if n.get('background'):d.rectangle((x,y,x+width,y+height),fill='#233b45')
        if n['kind']=='button':d.rounded_rectangle((x,y,x+width,y+height),radius=3,fill='#293631',outline='#947e55')
        if value:
            size=max(8,round(n.get('size',18)*scale));font=ImageFont.truetype(fontpath,size)
            while font.getlength(value)>width-8 and size>7:size-=1;font=ImageFont.truetype(fontpath,size)
            lines=value.split('\n');offset=0
            for line in lines:
                dx=x+(width-font.getlength(line))/2 if n['kind']=='button' else x+4
                dy=y+(height-size)/2 if n['kind']=='button' else y+3+offset
                d.text((dx,dy),line,font=font,fill='#e2d6bb');offset+=size+3
    ox=30 if index<2 else 760;oy=60 if index!=1 else 565
    sheet.paste(canvas,(ox,oy));draw.text((ox,oy-28),p['screen']+' / source layout proof',font=ImageFont.truetype(fontpath,18),fill='white')
draw.text((760,820),'Layout proofs from executed ActionScript methods.\nNative game rendering and final fonts need in-game acceptance.',font=ImageFont.truetype(fontpath,18),fill='#c5c3af')
sheet.save(BUILD/'ui-layout-proof.png');print(BUILD/'ui-layout-proof.png')
if __name__=='__main__':pass

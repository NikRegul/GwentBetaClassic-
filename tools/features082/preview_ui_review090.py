"""Offline layout proof from executed AS methods and original Beta glyphs."""
from pathlib import Path
import json,math,re
from PIL import Image,ImageDraw,ImageChops,ImageFont,ImageOps
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/release090-ui-review2'
proofs=json.loads((BUILD/'ui-review-tests.json').read_text('utf8'))['proofs']
fonts=json.loads((ROOT/'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
faces={'Halis GR':'HalisGRMedium','PF Din Text Cond Pro':'PFDinTextCondPro','Gwent Numbers':'GwentNumbers'}
cache={}


def face_for(n):return fonts[faces.get(n.get('face'),'PFDinTextCondPro')]
def width(text,font,size):return sum(font['glyphs'].get(str(ord(c)),{'advance':30})['advance']*size/64 for c in text)


def draw_text(im,n):
    font=face_for(n);size=n.get('size') or 20;color=n.get('color') or 0xEEE8DA
    rgb=((color>>16)&255,(color>>8)&255,color&255)
    lines=[];line=''
    for paragraph in str(n.get('value') or '').split('\n'):
        line=''
        for word in paragraph.split(' '):
            candidate=(line+' '+word).strip()
            if line and width(candidate,font,size)>n['w']-4:lines.append(line);line=word
            else:line=candidate
        lines.append(line)
    y=n['y']+2;advance=font['info']['LineHeight']*size/64
    for line in lines:
        if y>n['y']+n.get('h',1000):break
        x=n['x']+2
        if n.get('align')=='center':x+=(n['w']-4-width(line,font,size))/2
        baseline=y+font['info']['Ascender']*size/64
        for c in line:
            g=font['glyphs'].get(str(ord(c)))
            if not g:x+=size*.5;continue
            key=(faces.get(n.get('face'),'PFDinTextCondPro'),size,c)
            if key not in cache:
                x0,y0,x1,y1=g['bounds'];scale=size/64
                ox=math.floor(x0*scale)-1;oy=math.floor(-y1*scale)-1
                w=max(1,math.ceil(x1*scale)-ox+2);h=max(1,math.ceil(-y0*scale)-oy+2)
                mask=Image.new('1',(w*2,h*2))
                for loop in g['loops']:
                    if len(loop)<3:continue
                    part=Image.new('1',mask.size);ImageDraw.Draw(part).polygon([((a*scale-ox)*2,(-b*scale-oy)*2) for a,b in loop],fill=1)
                    mask=ImageChops.logical_xor(mask,part)
                cache[key]=(mask.convert('L').resize((w,h),Image.Resampling.LANCZOS),ox,oy)
            mask,ox,oy=cache[key];im.paste(rgb,(round(x+ox),round(baseline+oy)),mask);x+=g['advance']*size/64
        y+=advance


for proof in proofs:
    im=Image.new('RGB',(1920,1080),'#0d1418');d=ImageDraw.Draw(im)
    if proof['screen'].startswith('round-'):
        d.rectangle((499,440,1428,576),fill='black',outline='#8c8c8c',width=2)
        d.rectangle((500,441,1427,510),fill='#204367')
        d.line((963,526,963,558),fill='#8c8c8c',width=2)
    for n in proof['nodes']:
        x,y=n['x'],n['y'];w,h=n.get('w',0),n.get('h',0)
        if n['kind'] in ['panel','button']:
            color=n.get('color',0x29342d);d.rectangle((x,y,x+w,y+h),fill=((color>>16)&255,(color>>8)&255,color&255),outline='#837254',width=1)
            if n['kind']=='button':draw_text(im,dict(n,kind='text',value=n['value'],size=20,y=y+(h-26)/2,h=32,face='PF Din Text Cond Pro',align='center',color=0xE8DBBD))
        elif n['kind']=='text':draw_text(im,n)
        elif n['kind']=='card':
            p=ROOT/f'BetaGwent/ui/assets/cards/{n["id"]}.png'
            if p.exists():
                card=ImageOps.fit(Image.open(p).convert('RGB'),(round(w),round(h)),method=Image.Resampling.LANCZOS);im.paste(card,(round(x),round(y)));d.rectangle((x,y,x+w,y+h),outline='#b99a62',width=2)
        elif n['kind']=='art' and n['id'] in [-1523,-1524,-1525,-1526,-1527]:
            data=json.loads((ROOT/'docs/evidence/beta-battle-widgets101.json').read_text('utf8'));sx,sy,sw,sh=data['slots'][str(n['id'])]
            icon=Image.open(data['atlas']).convert('RGBA').crop((sx,sy,sx+sw,sy+sh)).resize((round(w),round(h)),Image.Resampling.LANCZOS)
            im.paste(icon,(round(x),round(y)),icon)
    if proof['screen'].startswith('round-'):im=im.crop((480,420,1448,596))
    else:im=im.resize((1280,720),Image.Resampling.LANCZOS)
    im.save(BUILD/(proof['screen']+'-layout.png'))
print('Rendered 7 tutorials and 3 round layouts with source Beta glyphs (not game screenshots).')

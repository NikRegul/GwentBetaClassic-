"""Source-asset composition for the retail layout fix, not a game screenshot."""
from pathlib import Path
import argparse, json, re, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ui'))
from preview_detail_power import number


def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args()
    src=ROOT/'BetaGwent/ui/src'
    report=json.loads((a.out/('editor-layout-source-v2.json' if (a.out/'editor-layout-source-v2.json').exists() else 'editor-layout-source.json')).read_text('utf8'))
    text=(src/'BetaGwentHDArt.as').read_text('utf-8-sig')
    rects=json.loads(re.search(r'private static var slots:Object=(.*);',text)[1])
    pages={int(n):(src/f).resolve() for f,n in re.findall(r'Embed\(source="([^"]+)"[^\n]+Page(\d+):Class',text)}
    cache={}
    def art(canvas,ident,x,y,w,h):
        page,ax,ay,aw,ah=rects[str(ident)]
        if page not in cache:cache[page]=Image.open(pages[page]).convert('RGBA')
        im=cache[page].crop((ax,ay,ax+aw,ay+ah)).resize((round(w),round(h)),Image.Resampling.LANCZOS)
        canvas.alpha_composite(im,(round(x),round(y)))
    def label(canvas,value,x,y,w,size=18):
        draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',size)
        draw.text((x+(w-draw.textlength(value,font=font))/2,y),value,font=font,fill='#eee8da')
    canvas=Image.new('RGBA',(1920,1080),'#111517')
    art(canvas,-1851,21,129,426,858)
    for i,item in enumerate(report['statsArt']):
        art(canvas,[-3749,-3719,-3720,-3721][i],item['x'],item['y'],item['w'],item['h'])
    for i,item in enumerate(report['statsLabels']):label(canvas,item['text'],item['x'],item['y']+(16 if i<3 else 0),item['w'])
    board=(src/'BetaGwentBoard.as').read_text('utf-8-sig')
    editor=board.split('private function drawBetaDeckEditor():void',1)[1].split('private function betaFilterButton',1)[0]
    name_y=int(re.search(r'nameRow.y=(\d+)',editor)[1])
    leader_y=int(re.search(r'leaderCard,46,(\d+),372,60,true',editor)[1])
    list_y=int(re.search(r'deckListTop178=(\d+)',editor)[1])
    art(canvas,-3718,46,name_y,372,44);label(canvas,'МОЯ КОЛОДА 1',54,name_y+11,280)
    strips=(src/'BetaGwentDeckArt104.as').read_text('utf8')
    slots=dict((int(k),int(v)) for k,v in re.findall(r'(\d+):(-\d+)',strips))
    rows=[(200160,'КРАХ АН КРАЙТ',5,True),(152109,'МОРСКОЙ ВЕПРЬ',8,False),(200212,'СКЬЯЛЛЬ',5,False),(152214,'УДАЛЬРИК',13,False),(152209,'МОРКВАРГ',9,False)]
    for i,(ident,name,power,leader) in enumerate(rows):
        x,y,w,h=46,leader_y if leader else list_y+(i-1)*40,372,60 if leader else 38
        ImageDraw.Draw(canvas).rectangle((x+2,y+2,x+w-2,y+h-2),fill='#0c0c0c')
        aw=w*(.72 if leader else .62);art(canvas,slots[ident],x+w-aw-3,y+3,aw,h-6)
        art(canvas,-3709 if leader or ident==152109 else -3710,x,y,w,h)
        label(canvas,str(power),x+2,y+(h-20)/2,38,16);label(canvas,name,x+52,y+(h-20)/2,260,16)
    art(canvas,-1851,1477,138,405,822);art(canvas,-1852,1545,177,285,398)
    banners=json.loads(re.search(r'DATA:Object=(.*);',(src/'BetaGwentBanners090.as').read_text('utf8'))[1])
    x,y,w,h=report['largePreview'];pic=Image.open(ROOT/'BetaGwent/ui/assets/cards/152214.png').convert('RGBA')
    canvas.alpha_composite(ImageOps.fit(pic,(round(w),round(h)),Image.Resampling.LANCZOS,centering=(.5,.25)),(round(x),round(y)))
    art(canvas,-1601,x,y,w,h)
    d=banners['Skellige_Silver'];banner=Image.open(ROOT/'BetaGwent/build/banners090-rays-input/Skellige_Silver.dds').convert('RGBA')
    banner=banner.resize((round(banner.width*d[2]*w/d[4]),round(banner.height*d[3]*h/d[5])),Image.Resampling.LANCZOS)
    canvas.alpha_composite(banner,(round(x+d[0]*w),round(y+d[1]*h)))
    fonts=json.loads((ROOT/'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
    number(canvas,'13',x+w*.025,y+h*.085,round(h*.115),fonts['GwentNumbers'])
    art(canvas,-1744,1523.5,586,312,76)
    art(canvas,-1764,1523.5,584,312,4)
    label(canvas,'УДАЛЬРИК',1523.5,596,312,20)
    panels=Image.new('RGBA',(871,900),'#111517')
    panels.alpha_composite(canvas.crop((21,129,447,987)),(10,32));panels.alpha_composite(canvas.crop((1477,138,1882,960)),(456,32))
    label(panels,'Проверка компоновки по исходным ресурсам',0,6,871,18)
    panels.convert('RGB').save(a.out/'editor-layout-preview.png')
    print(a.out/'editor-layout-preview.png')


if __name__=='__main__':main()

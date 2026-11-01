import json,re,sys,os
from PIL import Image,ImageDraw,ImageFont
ROOT=os.environ['ROOT'];UI=ROOT+'/BetaGwent/ui/src/'
hd=open(UI+'BetaGwentHDArt.as',encoding='utf-8-sig').read()
SL=json.loads(re.search(r'private static var slots:Object=(.*);',hd)[1])
PAGES={int(n):os.path.normpath(UI+f) for f,n in re.findall(r'Embed\(source="([^"]+)"[^\n]*?Page(\d+):Class',hd)}
cache={}
def page(n):
    if n not in cache:cache[n]=Image.open(PAGES[n]).convert('RGBA')
    return cache[n]
EL=Image.open(ROOT+'/BetaGwent/ui/assets/elements164/Elements.png').convert('RGBA')
FD=ROOT+'/BetaGwent/build-inputs/authoring/languages137/fonts/prepared/ru_ru/'
fonts={}
def font(face,size,bold):
    key=(face,int(size),bold)
    if key not in fonts:
        name='PFDinTextCondPro-Bold' if face in('title','numbers') or bold else 'PFDinTextCondPro-Medium'
        try:fonts[key]=ImageFont.truetype(FD+name+'.subset.ttf',max(6,int(round(size))))
        except Exception:fonts[key]=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',max(6,int(size)))
    return fonts[key]
def rgb(c,a):return ((c>>16)&255,(c>>8)&255,c&255,int(max(0,min(1,a))*255))
def paste(canvas,img,x,y,a,clip):
    if a<1:
        al=img.getchannel('A').point(lambda v:int(v*a));img.putalpha(al)
    x,y=int(round(x)),int(round(y))
    if clip:
        cx,cy,cw,ch=[int(round(v)) for v in clip]
        l,t=max(x,cx),max(y,cy);r,b=min(x+img.width,cx+cw),min(y+img.height,cy+ch)
        if r<=l or b<=t:return
        img=img.crop((l-x,t-y,r-x,b-y));x,y=l,t
    canvas.alpha_composite(img,(max(0,x),max(0,y)),(max(0,-x),max(0,-y)))
def draw(ops,out):
    canvas=Image.new('RGBA',(1920,1080),(8,10,12,255))
    fill=None;line=None
    for o in ops:
        try:
            if 'g' in o:
                g=o['g'];k=g[0]
                if k=='reset':fill=None;line=None
                elif k=='fill':fill=(g[1],g[2])
                elif k=='gradient':fill={'colors':g[1],'alpha':g[2]}
                elif k=='line':line=(g[1],g[2],g[3]) if g[1] else None
                elif k=='end':fill=None
                elif k in('rect','circle','ellipse'):
                    if k=='rect':x,y,w,h=g[1:5]
                    elif k=='circle':x,y,w,h=g[1]-g[3],g[2]-g[3],2*g[3],2*g[3]
                    else:x,y,w,h=g[1:5]
                    W,H=int(abs(w*o['sx']))+2,int(abs(h*o['sy']))+2
                    if W<=0 or H<=0 or W>4000 or H>4000:continue
                    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
                    shape=d.rectangle if k=='rect' else d.ellipse
                    if isinstance(fill,dict):
                        for yy in range(H):
                            t=yy/max(1,H-1);c0,c1=fill['colors'][0],fill['colors'][-1]
                            color=tuple(round(((c0>>shift)&255)*(1-t)+((c1>>shift)&255)*t) for shift in (16,8,0))
                            alpha=round(255*(fill['alpha'][0]*(1-t)+fill['alpha'][-1]*t))
                            d.line((0,yy,W,yy),fill=(*color,alpha))
                    elif fill and fill[1]>0:shape((0,0,W-2,H-2),fill=rgb(fill[0],fill[1]))
                    if line:shape((0,0,W-2,H-2),outline=rgb(line[1],line[2]),width=max(1,int(line[0])))
                    paste(canvas,im,o['x']+x*o['sx'],o['y']+y*o['sy'],o['a'],o['clip'])
                continue
            if 'art' in o:
                a=o['art'];s=SL.get(str(a['id']))
                if not s:continue
                pg,ax,ay,aw,ah=s;src=page(pg);pixel_scale=.75 if pg<12 else 1
                if 'sub' in a and a['sub']:
                    sx,sy,sw,sh=a['sub'];im=src.crop(tuple(round(v*pixel_scale) for v in (ax+sx,ay+sy,ax+sx+sw,ay+sy+sh)))
                else:im=src.crop(tuple(round(v*pixel_scale) for v in (ax,ay,ax+aw,ay+ah)))
                # Rasterize shared boundaries consistently; independently rounding each
                # strip's height invents a one-pixel gap absent from the AS geometry.
                W=int(round(o['x']+abs(a['w']*o['sx'])))-int(round(o['x']))
                H=int(round(o['y']+abs(a['h']*o['sy'])))-int(round(o['y']))
                if W<1 or H<1:continue
                im=im.resize((W,H),Image.Resampling.LANCZOS)
                x=o['x'];
                if o['sx']<0:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT);x-=W
                paste(canvas,im,x,o['y'],o['a'],o['clip']);continue
            if 'chrome' in o:
                x0,y0,w0,h0=o['chrome'];im=EL.crop((x0,y0,x0+w0,y0+h0)).resize((max(1,int(o['w'])),max(1,int(o['h']))),Image.Resampling.LANCZOS)
                paste(canvas,im,o['x'],o['y'],o['a'],o['clip']);continue
            if 'text' in o:
                f=font(o.get('face'),o['size'],o.get('bold'));lines=str(o['text']).replace('\r','\n').split('\n')
                if o.get('wrap'):
                    wrapped=[]
                    probe=ImageDraw.Draw(canvas)
                    for line in lines:
                        current=''
                        for word in re.findall(r'\S+\s*',line):
                            if current and probe.textlength(current+word,font=f)>o['w']:
                                wrapped.append(current.rstrip());current=''
                            current+=word
                        wrapped.append(current.rstrip())
                    lines=wrapped
                lh=int(o['size']*1.2);W=int(max(10,o['w']));H=lh*len(lines)+6
                im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
                for i,l in enumerate(lines):
                    tw=d.textlength(l,font=f);x=0 if o.get('align') in(None,'left') else (W-tw)/2 if o['align']=='center' else W-tw
                    d.text((x+1,i*lh+3),l,font=f,fill=(0,0,0,160));d.text((x,i*lh+2),l,font=f,fill=rgb(o['color'],1))
                paste(canvas,im,o['x'],o['y'],o['a'],o['clip'])
        except Exception as e:
            print('op fail',e,str(o)[:120])
    canvas.convert('RGB').save(out,quality=88)
scenes=json.load(open(sys.argv[1]))
for k,v in scenes.items():
    draw(v,sys.argv[2]+'/'+k+'.jpg');print(k)

"""Fix asynchronous large-banner/power layout and restore the battle side face."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release090-windows-paste'
OUT=ROOT/'BetaGwent/build/release090-banner-runtime'
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']

def replace(s,a,b):
    assert s.count(a)==1,a[:100]
    return s.replace(a,b)
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))

def board(s):
    s=replace(s,'motion:Boolean=true,big:Boolean=false):void','motion:Boolean=true,big:Boolean=false):Object')
    a=s.index('            var b:Array=betaBannerRect(w,h);',s.index('private function paintBetaFace('))
    b=s.index('        private function statusVisible191',a)
    s=s[:a]+'''            var b:Array=betaBannerRect(w,h);
            var icon:int=-1610-(faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:5);
            if(!big){paintArt(p,icon,b[2],b[3],b[0],b[1]);return null;}
            // Keep a complete small face until the native banner is ready.
            // This layer stays below power/status even when loading fails later.
            var flag:Sprite=new Sprite();p.addChild(flag);
            paintArt(flag,icon,b[2],b[3],b[0],b[1]);
            var face:Object={large:false,power:null,color:0xFFFFFF};
            var loaded:Function=function():void{
                face.large=true;flag.visible=false;
                if(face.power)layoutBigPower090(face.power,w,h,uint(face.color));
            };
            BetaGwentBanners090.paint(p,entry?int(entry.faction):1,tier,w,h,null,loaded);
            return face;
        }
        // Switch the power and banner together, only after successful loading.
        private function layoutBigPower090(field:TextField,w:Number,h:Number,color:uint):void
        {
            var size:int=Math.max(16,Math.round(h*.115));
            field.x=w*.015-size;field.y=h*.004;field.width=size*2;field.height=size*1.7;
            if(!BetaGwentFonts.apply(field,BetaGwentFonts.NUMBERS,size,color,true,"center")){field.defaultTextFormat=new TextFormat("$NormalFont",size,color,true,null,null,null,null,"center");field.setTextFormat(field.defaultTextFormat);}
            centerBetaNumber(field,w*.015,h*.075,size);
        }
        private function betaBigPowerField(p:Sprite,value:String,w:Number,h:Number,color:uint,face:Object=null):TextField
        {
            var field:TextField=betaPowerField(p,value,w,h,color);
            if(face){face.power=field;face.color=color;if(face.large)layoutBigPower090(field,w,h,color);}
            return field;
        }
''' +s[b:]
    s=replace(s,'paintBetaFace(picture,c.templateId,cw,ch,side,false,true,true);','var face:Object=paintBetaFace(picture,c.templateId,cw,ch,side,false,true,true);')
    s=replace(s,'cw,ch,c.power!=null?powerColor(c):0xFFFFFF);','cw,ch,c.power!=null?powerColor(c):0xFFFFFF,face);')
    # Combat uses its accepted small-card presentation, including power and armour.
    s=replace(s,'312/BETA_LARGE_CARD_ASPECT','312/BETA_CARD_ASPECT')
    s=replace(s,'paintBetaFace(card,c.templateId,w,h,side,animatePortrait,true,true);','paintBetaFace(card,c.templateId,w,h,side,animatePortrait);')
    s=replace(s,'betaBigPowerField(card,String(c.power),w,h,powerColor(c));','betaPowerField(card,String(c.power),w,h,powerColor(c));')
    return s

def loader(s):
    s=replace(s,'+name+".swf"','+name.toLowerCase()+".swf"')
    s=replace(s,'h:Number,fallback:Function):Boolean','h:Number,fallback:Function,ready:Function=null):Boolean')
    s=replace(s,'var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;',
        'var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;holder.visible=false;')
    s=replace(s,'var complete:Function=function(e:Event):void{state.done=true;};','''var complete:Function=function(e:Event):void{
                state.done=true;if(state.retired)return;
                if(!loader.content||loader.content.width<=0||loader.content.height<=0){failed(e);return;}
                if(ready!=null)ready();holder.visible=true;
            };''')
    return s

def main():
    global OUT
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=OUT)
    OUT=parser.parse_args().out.resolve()
    assert OUT.is_relative_to(ROOT/'BetaGwent/build')
    assert not OUT.exists()
    for platform in ['classic','nextgen']:
        target=OUT/platform;target.mkdir(parents=True)
        shutil.copytree(SOURCE/platform/'ui',target/'ui')
        for name,patch in [('BetaGwentBoard.as',board),('BetaGwentBanners090.as',loader)]:
            p=target/'ui/src'/name;write(p,patch(p.read_text('utf-8-sig')))
            for folder in COPIES:
                if folder!='src':shutil.copy2(p,target/'ui'/folder/name)
                if platform=='nextgen':shutil.copy2(p,ROOT/'BetaGwent/ui'/folder/name)
        manifest=json.loads((SOURCE/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (target/'ui/src').glob('*.as')}
        (target/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
        if platform=='classic':shutil.copy2(SOURCE/'classic/subimages.json',target/'subimages.json')
    shutil.copytree(SOURCE/'scripts',OUT/'scripts')
    print('Prepared synchronized banner/power loading, safe fallback and original battle preview.')

if __name__=='__main__':main()

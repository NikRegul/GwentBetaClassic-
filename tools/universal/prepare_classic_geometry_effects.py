"""Follow the native fix13 trace: bounded hand geometry and linked effect cells."""
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/classic081-hand-fix13'
OUT=ROOT/'BetaGwent/build/classic081-geometry-effects-fix14'


def change(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new)


def write(path,text):
    path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))


def main():
    assert not (OUT/'menus').exists() and not (OUT/'package').exists(),'Keep compiled candidates immutable'
    shutil.copytree(SOURCE/'ui',OUT/'ui',dirs_exist_ok=True)
    board=(SOURCE/'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    start=board.index('            var handArea:Array=skin==3?BetaGwentBoardLayout.hand["1"]:null;')
    end=board.index('            for each(var c:Object in cards)',start)
    board=board[:start]+'''            var handGeometry:Object=classicHandLayout(handSlots.length);
            classicHandLayoutState="count="+handSlots.length+" left="+handGeometry.left+" step="+handGeometry.step+" width="+handGeometry.width;
            var handWidth:Number=handGeometry.width;
'''+board[end:]
    board=change(board,'x:handLeft+slot*step,','x:classicHandX(slot,handGeometry),')
    board=change(board,'        private function drawCards():void', '''        private var classicHandLayoutState:String="";
        private function classicHandLayout(count:int):Object
        {
            // Keep numeric layout outside drawCards' large replay method. Trace
            // fix13 showed every hand X clamped to INT_MIN/20 by native GFx.
            if(count<1)count=1;
            var left:Number=484,span:Number=970,width:Number,spacing:Number;
            if(skin==3){
                var area:Array=BetaGwentBoardLayout.hand["1"] as Array;
                left=area?Number(area[0]):645.5;span=area?Number(area[2]):787.7;
                if(!isFinite(left)||left<0||left>1920)left=645.5;
                if(!isFinite(span)||span<104||span>1920)span=787.7;
                width=104;spacing=0;
                if(count>1){spacing=(span-width)/(count-1);if(spacing>108)spacing=108;}
                left=left+(span-width-spacing*(count-1))/2;
            }else{
                width=span/count;if(width>112)width=112;width-=8;spacing=width+8;
            }
            return {left:left,step:spacing,width:width};
        }
        private function classicHandX(rank:int,layout:Object):Number
        {
            var x:Number=Number(layout.left)+rank*Number(layout.step);
            // Never assign a NaN/Infinity or stale off-screen replay coordinate
            // to the native display list. Preserve distinct ordered slots.
            if(!isFinite(x)||x<0||x>1816)x=645.5+rank*32;
            return x;
        }
        private function drawCards():void''')
    board=board.replace('classic_hand_fix13','classic_geometry_fix14')
    board=change(board,'        private var classicHandReportAt:int=0;', '''        private var classicHandReportAt:int=0;
        private var classicHandReportKeys:Object={};''')
    board=change(board,'            var received:int=0,created:int=0,visibleCount:int=0;var states:Array=[];', '''            var reportKey:String=revision+":"+phase+":"+requestId+":"+playing;
            if(classicHandReportKeys[reportKey])return;classicHandReportKeys[reportKey]=true;
            var received:int=0,created:int=0,visibleCount:int=0,inBounds:int=0;var states:Array=[];''')
    board=change(board,'                created++;if(sprite.visible&&sprite.alpha>0&&sprite.parent==content)visibleCount++;', '''                created++;if(sprite.visible&&sprite.alpha>0&&sprite.parent==content)visibleCount++;
                if(isFinite(sprite.x)&&sprite.x>=0&&sprite.x+sprite.width<=1920&&sprite.y>=0&&sprite.y<1080)inBounds++;''')
    board=change(board,'" playing="+playing+" request="+requestId', '" inBounds="+inBounds+" layout="+classicHandLayoutState+" playing="+playing+" request="+requestId')

    entries=json.loads((SOURCE/'subimages.json').read_text('utf8'))['entries']
    art=(SOURCE/'ui/src/BetaGwentHDArt.as').read_text('utf-8-sig')
    slots=json.loads(re.search(r'private static var slots:Object=(\{.*?\});',art).group(1))
    for key,slot in slots.items():
        if slot[0]!=19:continue
        page,x,y,w,h=slot
        parts=[(0,0,w,h)]
        if int(key)==-1963:parts += [(i%6*64,i//6*64,64,64) for i in range(36)]
        for index,(cx,cy,cw,ch) in enumerate(parts):
            name='BetaGwentClassicWeatherN'+str(abs(int(key)))+'_'+str(index)
            entries.append(dict(id=int(key),page=page,x=x+cx,y=y+cy,width=cw,height=ch,clip=[cx,cy,cw,ch],className=name))
    hdentries=list(entries)
    rects=json.loads(re.search(r'RECTS:Array=(\[.*?\]);',(SOURCE/'ui/src/BetaGwentElementData164.as').read_text('utf-8-sig')).group(1))
    effectKeys={}
    def effect(family,index,page,atlas,x,y,w,h):
        name='BetaGwentClassicEffect'+family.title()+str(index)
        entries.append(dict(id=0,page=page,atlas=atlas,x=x,y=y,width=w,height=h,clip=[0,0,w,h],className=name))
        effectKeys[family+':'+str(index)]=name
    for i,r in enumerate(rects):
        assert r[0]==0
        effect('element',i,100,'Elements_png',*r[1:])
    for i in range(48):effect('kill',i,101 if i<32 else 102,'kill_beta_png' if i<32 else 'kill2_beta_png',(i%32)%8*128,(i%32)//8*128,128,128)
    for i in range(4):effect('banishhit',i,103,'banish_beta_png',i%2*128,i//2*128,128,128)
    for i in range(9):effect('banishshard',i,103,'banish_beta_png',i%3*64,256+i//3*64,64,64)
    mapping=',\n'.join('"'+':'.join(map(str,[r['id'],*r['clip']]))+'":'+r['className'] for r in hdentries)
    registry='''package {
 public class BetaGwentClassicSubImages {
  private static var classes:Object={'''+mapping+'''};
  public static function find(id:int,x:Number,y:Number,w:Number,h:Number):Class {
   return classes[id+":"+x+":"+y+":"+w+":"+h] as Class;
  }
 }
}
'''
    effectMap=',\n'.join('"'+k+'":'+v for k,v in effectKeys.items())
    effects='''package {
 import flash.display.Bitmap;
 import flash.display.Sprite;
 public class BetaGwentClassicEffects {
  private static var classes:Object={'''+effectMap+'''};
  public static function view(key:String,w:Number,h:Number):Sprite {
   var type:Class=classes[key] as Class;if(!type)return null;
   var bitmap:Bitmap=new type() as Bitmap;
   if(!bitmap||bitmap.width<=0||bitmap.height<=0)return null;
   bitmap.smoothing=true;bitmap.pixelSnapping="never";
   var result:Sprite=new Sprite();result.mouseEnabled=false;result.mouseChildren=false;
   result.addChild(bitmap);result.scaleX=w/bitmap.width;result.scaleY=h/bitmap.height;return result;
  }
 }
}
'''
    element=(SOURCE/'ui/src/BetaGwentElementArt164.as').read_text('utf-8-sig')
    element=change(element,'            var family:int=int(rect[0]);', '''            var nativeCell:Sprite=BetaGwentClassicEffects.view("element:"+index,w,h);
            if(nativeCell){
                sprite.graphics.clear();while(sprite.numChildren)sprite.removeChildAt(0);
                nativeCell.x=-w/2;nativeCell.y=-h/2;sprite.addChild(nativeCell);return;
            }
            var family:int=int(rect[0]);''')
    kill=(SOURCE/'ui/src/BetaGwentKillArt144.as').read_text('utf-8-sig')
    kill=change(kill,'            var bitmap:Bitmap;', '''            var nativeCell:Sprite=BetaGwentClassicEffects.view("kill:"+index,w,h);
            if(nativeCell){
                nativeCell.x=-w/2;nativeCell.y=-h/2;
                var nativeHolder:Sprite=new Sprite();nativeHolder.mouseEnabled=false;nativeHolder.mouseChildren=false;nativeHolder.addChild(nativeCell);
                if(tint>=0)nativeHolder.transform.colorTransform=new ColorTransform(((tint>>16)&255)/255,((tint>>8)&255)/255,(tint&255)/255,alpha);
                else if(alpha<1)nativeHolder.alpha=alpha;
                if(add)nativeHolder.blendMode="add";return nativeHolder;
            }
            var bitmap:Bitmap;''')
    banish=(SOURCE/'ui/src/BetaGwentBanish160.as').read_text('utf-8-sig')
    banish=change(banish,'            if(!shared){', '''            var nativeIndex:int=Math.max(0,index)%(kind==HIT?4:9);
            var nativeCell:Sprite=BetaGwentClassicEffects.view((kind==HIT?"banishhit:":"banishshard:")+nativeIndex,w,h);
            if(nativeCell){
                nativeCell.x=-w*pivotX;nativeCell.y=-h/2;
                var nativeHolder:Sprite=new Sprite();nativeHolder.mouseEnabled=false;nativeHolder.mouseChildren=false;nativeHolder.addChild(nativeCell);
                nativeHolder.transform.colorTransform=new ColorTransform(r,g,b,1);return nativeHolder;
            }
            if(!shared){''')
    texts={'BetaGwentBoard.as':board,'BetaGwentClassicSubImages.as':registry,'BetaGwentClassicEffects.as':effects,
           'BetaGwentElementArt164.as':element,'BetaGwentKillArt144.as':kill,'BetaGwentBanish160.as':banish}
    oldNames={r['className'] for r in entries[:703]}
    for r in entries:
        if r['className'] in oldNames:continue
        name=r['className'];texts[name+'.as']='package {\n import mx.core.BitmapAsset;\n public class '+name+' extends BitmapAsset {\n  public function '+name+'(){super();}\n }\n}\n'
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name,text in texts.items():write(OUT/'ui'/folder/name,text)
    manifest=json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'ui/src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    (OUT/'subimages.json').write_text(json.dumps(dict(entries=entries),indent=2),'utf8')
    (OUT/'preparation.json').write_text(json.dumps(dict(weatherFragments=len(hdentries)-703,effectFragments=len(effectKeys),
        existingUIFragmentsPreserved=703,existingTexturePixelsPreserved=True),indent=2),'utf8')
    print('Prepared fix14:',len(entries),'native fragments; five pinned source copies.')


if __name__=='__main__':main()

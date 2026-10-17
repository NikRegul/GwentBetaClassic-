"""Normalize the native image contract and retain the accepted Classic battle."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/classic081-geometry-effects-fix14'
OUT=ROOT/'BetaGwent/build/classic081-visual-fix15'


def change(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new)


def write(path,text):
    path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))


def main():
    assert not OUT.exists(),'Keep earlier builds immutable'
    shutil.copytree(SOURCE/'ui',OUT/'ui')
    hd=(SOURCE/'ui/src/BetaGwentHDArt.as').read_text('utf-8-sig')
    hd=change(hd,'fragmentView.addChild(bitmap);fragmentView.scaleX=w/bitmap.width;fragmentView.scaleY=h/bitmap.height;',
        'bitmap.scaleX=w/bitmap.width;bitmap.scaleY=h/bitmap.height;fragmentView.addChild(bitmap);')
    hd=change(hd,'    return nativeView;','    return unitView(nativeView);')
    hd=change(hd,'result.addChild(bitmap);result.scaleX=w/pw;result.scaleY=h/ph;return result;',
        'result.addChild(bitmap);result.scaleX=w/pw;result.scaleY=h/ph;return unitView(result);')
    hd=change(hd,' public static function release():void', ''' // Public art views have unit scale, like the graphics-fill path. Size is
 // internal, so flips, pulses and animation scale never erase atlas fitting.
 private static function unitView(image:Sprite):Sprite {
  var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;
  holder.addChild(image);return holder;
 }
 public static function release():void''')
    effects=(SOURCE/'ui/src/BetaGwentClassicEffects.as').read_text('utf-8-sig')
    effects=change(effects,'result.addChild(bitmap);result.scaleX=w/bitmap.width;result.scaleY=h/bitmap.height;return result;',
        'bitmap.scaleX=w/bitmap.width;bitmap.scaleY=h/bitmap.height;result.addChild(bitmap);return result;')
    board=(SOURCE/'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    board=change(board,'half.scaleX=-1;half.x=area[0]+area[2];',
        'half.scaleX=-half.scaleX;half.x=area[0]+area[2];')
    board=change(board,'                    particles.scrollRect=new Rectangle(0,0,geometry.w,geometry.h);', '''                    // Classic scrollRect can suppress an entire weather subtree.
                    // A vector mask keeps the same row boundary and moving layers.
                    var weatherMask:Sprite=new Sprite();weatherMask.mouseEnabled=false;weatherMask.mouseChildren=false;
                    weatherMask.graphics.beginFill(0xFFFFFF);weatherMask.graphics.drawRect(0,0,geometry.w,geometry.h);weatherMask.graphics.endFill();
                    particles.addChild(weatherMask);particles.mask=weatherMask;''')
    board=change(board,'            finishLeaderRender();\n            if(restoreHand&&controller.active)',
        '            finishLeaderRender();finishClassicVisualRender();\n            if(restoreHand&&controller.active)')
    board=change(board,'drawGalleryControls();finishLeaderRender();return;',
        'drawGalleryControls();finishLeaderRender();finishClassicVisualRender();return;')
    board=change(board,'        private var boardFocusKey:String="";', '''        private var classicVisualRenderMs:int=0;
        private var classicVisualSampled:Boolean=false;
        private function finishClassicVisualRender():void
        {
            var builtAt:int=getTimer(),oldStart:int=animationStarted;
            classicVisualRenderMs=Math.max(0,builtAt-oldStart);classicVisualSampled=false;
            // Class construction/atlas setup are not part of the displayed clip.
            // Otherwise a slow render can consume a short impact before frame 1.
            animationStarted=builtAt;
            if(playing&&frameDeadline>0)frameDeadline=builtAt+frameDuration;
            for each(var fx:Object in weatherEffects)if(fx.start>=oldStart){
                fx.start+=classicVisualRenderMs;
                if(weatherBirths[fx.key])weatherBirths[fx.key].start=fx.start;
            }
            reportClassicVisualState("built");
        }
        private function reportClassicVisualState(phase:String):void
        {
            if(!connected||selectingDecks||editingDeck||browsingCatalog||kegOpen||entryMode==1)return;
            var weather:Array=[],elements:Array=[];
            for each(var fx:Object in weatherEffects){
                var partStates:Array=[];
                for each(var part:Object in fx.nativeParts){var view:Sprite=part.sprite;
                    partStates.push(part.kind+":"+view.x+","+view.y+","+view.width+","+view.height+",a="+view.alpha+",v="+view.visible);}
                weather.push(fx.key+":token="+fx.token+",age="+(getTimer()-fx.start)+",a="+fx.sprite.alpha+
                    ",v="+fx.sprite.visible+",children="+fx.sprite.numChildren+",attached="+(fx.sprite.parent==content)+",parts="+partStates.join(";"));
            }
            for each(var motion:Object in animations)if(motion.element164){
                var effect:BetaGwentElement164=motion.element164 as BetaGwentElement164;
                elements.push("duration="+effect.durationMs+",particles="+effect.particleCount+",x="+effect.x+",y="+effect.y+
                    ",a="+effect.alpha+",children="+effect.numChildren+",delay="+motion.delay+",finished="+motion.finished);
            }
            send("OnBetaGwentControllerTrace",[0,"VISUAL_STATE","classic_visual_fix15",
                "phase="+phase+" revision="+revision+" cue="+(activeCue?activeCue.kind:0)+" renderMs="+classicVisualRenderMs+
                " elapsed="+(getTimer()-animationStarted)+" frameMs="+frameDuration+" weather="+weather.join("|")+" elements="+elements.join("|")]);
        }
        private var boardFocusKey:String="";''')
    board=change(board,'            if(complete)animations=[];', '''            if(!classicVisualSampled){classicVisualSampled=true;reportClassicVisualState("frame");}
            if(complete)animations=[];''')
    texts={'BetaGwentBoard.as':board,'BetaGwentHDArt.as':hd,'BetaGwentClassicEffects.as':effects}
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name,text in texts.items():write(OUT/'ui'/folder/name,text)
    manifest=json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'ui/src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    shutil.copy2(SOURCE/'subimages.json',OUT/'subimages.json')
    saved=OUT/'previous-feedback';saved.mkdir()
    shutil.copy2(Path.home()/'Documents/The Witcher 3/scriptslog.txt',saved/'scriptslog.txt')
    (saved/'capture.json').write_text(json.dumps(dict(path=str(ROOT/'BetaGwent/build/classic132-full-feedback/20261016-225031-687212'),
        texturesLoaded=30,userConfirmed='Battle completed, hand and voices and consume work; row scores displaced; frost and impacts missing'),indent=2),'utf8')
    print('Prepared fix15: unit-scale art views, preserved mirror scale, weather mask, post-render clock.')


if __name__=='__main__':main()

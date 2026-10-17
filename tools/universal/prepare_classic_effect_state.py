"""Explicit presentation defaults and native leader-frame rendering for Classic."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/classic081-visual-fix15'
OUT=ROOT/'BetaGwent/build/classic081-effect-state-fix16'


def change(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new)


def write(path,text):
    path.write_bytes(b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))


def main():
    assert not OUT.exists(),'Keep prior builds immutable'
    shutil.copytree(SOURCE/'ui',OUT/'ui')
    ui=(SOURCE/'ui/src/BetaGwentUi138.as').read_text('utf-8-sig')
    ui=change(ui,'        public static var filters:Object={};', '''        public static var filters:Object={};
        private static var classicInitialized:Boolean=false;
        public static function initializeClassic():String {
            var before:String="intensity="+intensity+",scenes="+scenes+",flashes="+flashes+",dynamic="+dynamicLeaders;
            if(!classicInitialized){
                // Execute assignments instead of relying on native trait defaults.
                // The Classic trace showed intensity=0 despite the declared 1.
                flashes=true;shake=true;scenes=1;chains=true;helpLabels=true;intensity=1;dynamicLeaders=true;
                classicInitialized=true;
            }
            return before+" -> intensity="+intensity+",scenes="+scenes+",flashes="+flashes+",dynamic="+dynamicLeaders;
        }''')
    element=(SOURCE/'ui/src/BetaGwentElement164.as').read_text('utf-8-sig')
    element=change(element,'        public static const MAX_UNITS:Number=55;', '''        public static const MAX_UNITS:Number=classicMaxUnits();
        private static function classicMaxUnits():Number { return 55; }''')
    element=change(element,'            mouseEnabled=false;mouseChildren=false;reduced=small;intensity=strength;maxUnits=sizeLimit;travelPx=travel;', '''            if(!isFinite(strength)||strength<=0)strength=1;
            if(!isFinite(sizeLimit)||sizeLimit<=0)sizeLimit=55;
            mouseEnabled=false;mouseChildren=false;reduced=small;intensity=strength;maxUnits=sizeLimit;travelPx=travel;''')
    element=change(element,'        public function render(progress:Number):void {', '''        public function classicState():String {
            var visibleCount:int=0;var width:Number=0,alpha:Number=0;
            for each(var item:Object in cells){var sprite:Sprite=item.sprite;
                if(sprite.visible){visibleCount++;width=Math.max(width,Math.abs(sprite.scaleX));alpha=Math.max(alpha,sprite.transform.colorTransform.alphaMultiplier);}}
            return "intensity="+intensity+",limit="+maxUnits+",units="+ux+","+uy+",visibleCells="+visibleCount+",maxScaleX="+width+",maxAlpha="+alpha;
        }
        public function render(progress:Number):void {''')
    board=(SOURCE/'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    board=change(board,'        public function BetaGwentBoard()\n        {', '''        private var classicPresentationInit:String="";
        public function BetaGwentBoard()
        {
            classicPresentationInit=BetaGwentUi138.initializeClassic();''')
    board=change(board,'        private var classicVisualRenderMs:int=0;', '''        private var classicVisualProbeAt:int=0;
        private var classicVisualRenderMs:int=0;''')
    board=change(board,'            reportClassicVisualState("built");', '''            classicVisualProbeAt=builtAt+Math.max(40,Math.min(frameDuration-60,cueImpactDelay()+100));
            reportClassicVisualState("built");''')
    board=change(board,'            updateReplayMouse(now);', '''            updateReplayMouse(now);
            if(classicVisualProbeAt>0&&now>=classicVisualProbeAt){classicVisualProbeAt=0;reportClassicVisualState("peak");}''')
    board=change(board,'",a="+effect.alpha+",children="+effect.numChildren+",delay="+motion.delay+",finished="+motion.finished);',
        '",a="+effect.alpha+",children="+effect.numChildren+",delay="+motion.delay+",finished="+motion.finished+","+effect.classicState());')
    board=change(board,'" elapsed="+(getTimer()-animationStarted)+" frameMs="+frameDuration+" weather="+weather.join("|")+" elements="+elements.join("|")]);', '''" elapsed="+(getTimer()-animationStarted)+" frameMs="+frameDuration+
                " intensity="+BetaGwentUi138.intensity+" maxUnits="+BetaGwentElement164.MAX_UNITS+" scenes="+BetaGwentUi138.scenes+
                " flashes="+BetaGwentUi138.flashes+" dynamic="+BetaGwentUi138.dynamicLeaders+" init="+classicPresentationInit+
                " weather="+weather.join("|")+" elements="+elements.join("|")]);''')
    board=board.replace('classic_visual_fix15','classic_effect_state_fix16')
    texts={'BetaGwentBoard.as':board,'BetaGwentUi138.as':ui,'BetaGwentElement164.as':element}
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name,text in texts.items():write(OUT/'ui'/folder/name,text)
    manifest=json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'ui/src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8');shutil.copy2(SOURCE/'subimages.json',OUT/'subimages.json')
    saved=OUT/'previous-feedback';saved.mkdir();shutil.copy2(Path.home()/'Documents/The Witcher 3/scriptslog.txt',saved/'scriptslog.txt')
    (saved/'capture.json').write_text(json.dumps(dict(path=str(ROOT/'BetaGwent/build/classic132-full-feedback/20261016-231718-476173'),
        observed='weather subtree alpha=0 with nonzero visible child layers; leader pages loaded but BitmapData-only renderAt'),indent=2),'utf8')
    print('Prepared explicit Classic presentation defaults, particle size guard and peak diagnostics.')


if __name__=='__main__':main()

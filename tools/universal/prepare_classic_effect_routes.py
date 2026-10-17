"""Keep accepted visuals while completing Classic effect opacity and native UV routes."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/classic081-opacity-fix17'
OUT = ROOT / 'BetaGwent/build/classic081-effect-routes-fix18'


def change(s, old, new):
    assert s.count(old) == 1, old[:120]
    return s.replace(old, new)


def write(p, s):
    p.write_bytes(b'\xef\xbb\xbf' + s.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


def explicit_colors(s):
    """Supply AS3's documented defaults instead of native optional arguments."""
    marker = 'new ColorTransform('
    at = 0
    changes = []
    defaults = ['1', '1', '1', '1', '0', '0', '0', '0']
    while (a := s.find(marker, at)) >= 0:
        start = a + len(marker)
        depth, i, split = 1, start, []
        for i in range(start, len(s)):
            c = s[i]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
            elif c == ',' and depth == 1:
                split.append(i)
        assert depth == 0
        count = len(split) + 1 if s[start:i].strip() else 0
        assert count <= 8
        if count < 8:
            suffix = (',' if count else '') + ','.join(defaults[count:])
            s = s[:i] + suffix + s[i:]
            changes.append(dict(argumentsBefore=count, argumentsAfter=8))
            i += len(suffix)
        at = i + 1
    return s, changes


def main():
    assert not OUT.exists(), 'Keep previous candidates immutable'
    shutil.copytree(SOURCE / 'ui', OUT / 'ui')
    board = (SOURCE / 'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    board = change(board, '        private var classicVisualProbeAt:int=0;', '''        private var classicVisualFlightAt:int=0;
        private var classicCueRoot:Sprite;
        private var classicVisualProbeAt:int=0;''')
    board = change(board,
        '            if(classicVisualProbeAt>0&&now>=classicVisualProbeAt){classicVisualProbeAt=0;reportClassicVisualState("peak");}',
        '''            if(classicVisualFlightAt>0&&now>=classicVisualFlightAt){classicVisualFlightAt=0;reportClassicVisualState("flight");}
            if(classicVisualProbeAt>0&&now>=classicVisualProbeAt){classicVisualProbeAt=0;reportClassicVisualState("peak");}''')
    board = change(board, '            classicVisualProbeAt=builtAt+',
        '            classicVisualFlightAt=0;if(activeCue&&activeCue.kind==2)classicVisualFlightAt=builtAt+80;\n            classicVisualProbeAt=builtAt+')
    board = change(board, '                " intensity="+BetaGwentUi138.intensity+',
        '                " cueAlpha="+(classicCueRoot?classicCueRoot.alpha:1)+" intensity="+BetaGwentUi138.intensity+')
    assert board.count('fx.alpha=BetaGwentUi138.intensity;') == 2
    board = board.replace('fx.alpha=BetaGwentUi138.intensity;', 'classicCueOpacity(fx);')
    board = change(board, '        private function drawVisualCue():void', '''        private function classicCueOpacity(sprite:Sprite):void
        {
            var value:Number=Number(BetaGwentUi138.intensity);sprite.alpha=value;classicCueRoot=sprite;
        }
        private function classicMotionAlpha(sprite:Object,motion:Object,elapsed:Number,delay:Number,progress:Number):void
        {
            var value:Number=0;var apply:Boolean=false;
            if(motion.status191||motion.element164){if(elapsed>=delay)value=1;apply=true;}
            if(motion.fade){
                value=1;if(motion.fromAlpha!=null)value=Number(motion.fromAlpha);
                value=value*(1-progress);apply=true;
            }else if(motion.appear){value=Math.min(1,progress*3);apply=true;}
            if(motion.scene){value=Math.max(0,Math.min(1,progress/.18,(1-progress)/.18));apply=true;}
            if(motion.hideBeforeDelay&&elapsed<delay){value=0;apply=true;}
            if(apply)sprite.alpha=value;
        }
        private function drawVisualCue():void''')
    board = change(board,
        '                if(motion.status191){BetaGwentStatus191(motion.status191).render(progress);sprite.alpha=elapsed<delay?0:1;}',
        '                if(motion.status191)BetaGwentStatus191(motion.status191).render(progress);')
    board = change(board, '                    sprite.alpha=elapsed<delay?0:1;\n                }\n                if(motion.coinFaces)',
        '                }\n                if(motion.coinFaces)')
    board = change(board, '''                if(motion.fade)sprite.alpha=(motion.fromAlpha!=null?motion.fromAlpha:1)*(1-progress);
                else if(motion.appear)sprite.alpha=Math.min(1,progress*3);
                if(motion.scene)sprite.alpha=Math.max(0,Math.min(1,progress/.18,(1-progress)/.18));
                if(motion.hideBeforeDelay&&elapsed<delay)sprite.alpha=0;''',
        '                classicMotionAlpha(sprite,motion,elapsed,delay,progress);')
    board = board.replace('classic_opacity_fix17', 'classic_effect_routes_fix18')

    element = (SOURCE / 'ui/src/BetaGwentElement164.as').read_text('utf-8-sig')
    element = change(element, '        public var particleCount:int;', '        public var particleCount:int;\n        public var presetName:String;')
    element = change(element, '            mouseEnabled=false;mouseChildren=false;reduced=small;',
        '            presetName=name;mouseEnabled=false;mouseChildren=false;reduced=small;')
    start = element.index('                    sprite.alpha=Math.min(1,progress*12,')
    end = element.index('                    continue;', start)
    element = element[:start] + '                    classicStaticTick(item,progress);\n' + element[end:]
    element = change(element, '        public static function classicParticleColor(', '''        private function classicStaticTick(item:Object,progress:Number):void {
            var value:Number=1;var rising:Number=progress*12,falling:Number=(1-progress)*8;
            if(rising<value)value=rising;if(falling<value)value=falling;
            value=value*Number(item.static.alpha);
            if(item.trail&&!item.physical)value=value*0.35;
            value=value*intensity;
            var sprite:Sprite=item.sprite as Sprite;sprite.alpha=value;item.expectedAlpha=value;
            if(item.trail&&item.physical&&travelPx>0){
                var full:Number=Number(item.layout.w),grown:Number=progress*travelPx/full;
                if(grown>1)grown=1;if(grown<.02)grown=.02;
                sprite.scaleX=grown;sprite.x=full*.05-full*grown/2;
            }
        }
        public static function classicParticleColor(''')
    element = change(element, '            return "intensity="+intensity+',
        '            return "preset="+presetName+",parentAlpha="+(parent?parent.alpha:1)+",intensity="+intensity+')
    element = change(element, '            var visibleCount:int=0;var width:Number=0,alpha:Number=0,packetAlpha:Number=0;',
        '            var staticStates:Array=[];var visibleCount:int=0;var width:Number=0,alpha:Number=0,packetAlpha:Number=0;')
    element = change(element, '            for each(var item:Object in cells){var sprite:Sprite=item.sprite;',
        '            for each(var item:Object in cells){var sprite:Sprite=item.sprite;\n                if(item.static)staticStates.push(item.static.name+":actual="+sprite.alpha+",expected="+item.expectedAlpha);')
    element = change(element, '",packetAlpha="+packetAlpha;', '",packetAlpha="+packetAlpha+",static="+staticStates.join(";");')

    entries = json.loads((SOURCE / 'subimages.json').read_text('utf8'))['entries']
    previous_count = len(entries)
    registry = (SOURCE / 'ui/src/BetaGwentClassicEffects.as').read_text('utf-8-sig')
    mappings = []
    def fragment(key, page, atlas, x, y, w, h):
        name = 'BetaGwentClassicRoute' + re.sub('[^a-zA-Z0-9]', '_', key)
        entries.append(dict(id=0,page=page,atlas=atlas,x=x,y=y,width=w,height=h,clip=[0,0,w,h],className=name))
        mappings.append('"'+key+'":'+name)
        write(OUT / 'ui/src' / (name+'.as'), 'package { import mx.core.BitmapAsset; public class '+name+' extends BitmapAsset { public function '+name+'(){super();} } }\n')
    for kind in range(7):
        for frame in range(4):
            x,y,w,h = 0,0,128,128
            if kind == 0:x=frame*128;h=256
            elif kind == 1:x=frame*128;y=256;h=64
            elif kind == 2:x=frame*64;y=320;w=h=64
            elif kind == 3:x=256;y=320
            elif kind == 4:x=384;y=320
            elif kind == 5:y=384
            else:x=128;y=384
            fragment('lightning:'+str(kind)+':'+str(frame),104,'lightning_beta_png',x,y,w,h)
    for name,page in [('fire',105),('frame',106),('lightning',107),('sparks',108)]:
        png = SOURCE/'ui/assets/special143'/(name+'.png')
        width,height=struct.unpack('>II',png.read_bytes()[16:24])
        for frame in range(25 if name=='fire' else 4 if name=='sparks' else 1):
            x,y,w,h=0,0,width,height
            if name=='fire':x=frame%5*100+2;y=frame//5*132+2;w=96;h=128
            elif name=='sparks':x=frame%2*128;y=frame//2*128;w=h=128
            fragment('spell:'+name+':'+str(frame),page,name+'_png',x,y,w,h)
    registry = change(registry, '"banishshard:8":BetaGwentClassicEffectBanishshard8};',
        '"banishshard:8":BetaGwentClassicEffectBanishshard8,\n'+',\n'.join(mappings)+'};')
    lightning = (SOURCE/'ui/src/BetaGwentLightning144.as').read_text('utf-8-sig')
    lightning = change(lightning, '            var bitmap:Bitmap=shared?', '''            var nativeFrame:int=Math.max(0,index)%4;
            var nativeView:Sprite=BetaGwentClassicEffects.view("lightning:"+kind+":"+nativeFrame,w,h);
            if(nativeView){
                nativeView.x=-w/2;nativeView.y=-h/2;
                var nativeHolder:Sprite=new Sprite();nativeHolder.mouseEnabled=false;nativeHolder.mouseChildren=false;
                nativeHolder.addChild(nativeView);return nativeHolder;
            }
            var bitmap:Bitmap=shared?''')
    spell=(SOURCE/'ui/src/BetaGwentSpellArt143.as').read_text('utf-8-sig')
    spell=change(spell, '            var type:Class=name=="fire"?', '''            var nativeFrame:int=0;
            if(name=="fire")nativeFrame=Math.max(0,Math.min(24,frame));
            else if(name=="sparks")nativeFrame=frame%4;
            var nativeView:Sprite=BetaGwentClassicEffects.view("spell:"+name+":"+nativeFrame,w,h);
            if(nativeView)return nativeView;
            var type:Class=name=="fire"?''')
    texts={'BetaGwentBoard.as':board,'BetaGwentElement164.as':element,'BetaGwentClassicEffects.as':registry,
           'BetaGwentLightning144.as':lightning,'BetaGwentSpellArt143.as':spell}
    colors={}
    for path in (OUT/'ui/src').glob('*.as'):
        text=texts.get(path.name,path.read_text('utf-8-sig'))
        text,changes=explicit_colors(text)
        if changes:colors[path.name]=changes
        if path.name in texts or changes:texts[path.name]=text
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        for name,text in texts.items():write(OUT/'ui'/folder/name,text)
        for path in (OUT/'ui/src').glob('BetaGwentClassicRoute*.as'):
            if folder!='src':shutil.copy2(path,OUT/'ui'/folder/path.name)
    (OUT/'subimages.json').write_text(json.dumps(dict(entries=entries),indent=2),'utf8')
    manifest=json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'ui/src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    (OUT/'route-source-audit.json').write_text(json.dumps(dict(changedExistingSources=sorted(texts),
        explicitColorConstructors=colors,addedNativeFragments=len(entries)-previous_count,
        originalFragmentsRetained=previous_count,weatherOpacityMethodPreserved=True,lightningFramesAndMotionPreserved=True,
        dissolveSourceUnchanged=True,nativeGameTested=False),indent=2),'utf8')
    saved=OUT/'previous-feedback';saved.mkdir()
    shutil.copy2(Path.home()/'Documents/The Witcher 3/scriptslog.txt',saved/'scriptslog.txt')
    print('Prepared Classic effect routes: static opacity, replay opacity, explicit colour defaults and native lightning/fire cells.')


if __name__=='__main__':main()

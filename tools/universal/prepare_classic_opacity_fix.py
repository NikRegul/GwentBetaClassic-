"""Isolate the Classic opacity calculations observed failing in fix16."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/classic081-effect-state-fix16'
OUT = ROOT / 'BetaGwent/build/classic081-opacity-fix17'


def change(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def write(path, text):
    path.write_bytes(b'\xef\xbb\xbf' + text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf8'))


def main():
    assert not OUT.exists(), 'Keep existing candidates immutable'
    shutil.copytree(SOURCE / 'ui', OUT / 'ui')
    board = (SOURCE / 'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    board = change(board,
        '                p.alpha=BetaGwentUi138.intensity*(fx.token==1?1:BetaGwentBetaMotion.sample("PREVIEW",Math.min(1,t/intro)));if(redraw)p.graphics.clear();',
        '''                if(redraw)p.graphics.clear();
                classicWeatherOpacity(fx,t,intro);''')
    board = change(board, '        private function animateWeather(e:Event):void', '''        // Keep the opacity assignment out of the large multi-branch weather tick.
        // fix16 reports intensity=1, visible layers, but parent alpha=0.
        private function classicWeatherOpacity(fx:Object,t:Number,intro:Number):void
        {
            var value:Number=Number(BetaGwentUi138.intensity);
            if(int(fx.token)!=1){
                var progress:Number=t/intro;if(progress>1)progress=1;
                var entrance:Number=BetaGwentBetaMotion.sample("PREVIEW",progress);
                value=value*entrance;
            }
            fx.expectedAlpha=value;
            var sprite:Sprite=fx.sprite as Sprite;
            sprite.alpha=value;
        }
        private function animateWeather(e:Event):void''')
    board = change(board,
        '",v="+fx.sprite.visible+",children="+fx.sprite.numChildren+",attached="+(fx.sprite.parent==content)+",parts="+partStates.join(";"));',
        '",expected="+fx.expectedAlpha+",v="+fx.sprite.visible+",children="+fx.sprite.numChildren+",attached="+(fx.sprite.parent==content)+",parts="+partStates.join(";"));')
    board = board.replace('classic_effect_state_fix16', 'classic_opacity_fix17')
    element = (SOURCE / 'ui/src/BetaGwentElement164.as').read_text('utf-8-sig')
    element = change(element,
        '                var color:ColorTransform=item.color;color.redMultiplier=out.r;color.greenMultiplier=out.g;color.blueMultiplier=out.b;\n                color.alphaMultiplier=out.a*intensity*(reduced ? 0.45*(1-progress) : 1);sprite.transform.colorTransform=color;',
        '''                var color:ColorTransform=classicParticleColor(out,intensity,reduced,progress);
                item.color=color;sprite.transform.colorTransform=color;''')
    element = change(element, '        public static function random(state:Object):Number {', '''        // Explicit constructor arguments avoid mutating the native transform's
        // default-valued multiplier slots. No material or source alpha is changed.
        public static function classicParticleColor(out:Object,strength:Number,small:Boolean,progress:Number):ColorTransform {
            var alpha:Number=Number(out.a)*strength;
            if(small)alpha=alpha*0.45*(1-progress);
            return new ColorTransform(Number(out.r),Number(out.g),Number(out.b),alpha,0,0,0,0);
        }
        public static function classicChannel(e:Object,time:Number,colorTime:Number,colorRandom:Number,overRandom:Number,channel:int):Number {
            var value:Number;
            if(channel==3)value=Number(e.alpha);else value=Number(e.rgb[channel]);
            value=value*gradientValue(e.color,colorTime,colorRandom,channel);
            if(e.over)value=value*gradientValue(e.over,time,overRandom,channel);
            if(channel==3&&value>1)value=1;
            return value;
        }
        public static function random(state:Object):Number {''')
    old = '''            out.r=e.rgb[0]*gradientValue(e.color,r[5],r[6],0)*(e.over?gradientValue(e.over,t,r[7],0):1);
            out.g=e.rgb[1]*gradientValue(e.color,r[5],r[6],1)*(e.over?gradientValue(e.over,t,r[7],1):1);
            out.b=e.rgb[2]*gradientValue(e.color,r[5],r[6],2)*(e.over?gradientValue(e.over,t,r[7],2):1);
            out.a=Math.min(1,e.alpha*gradientValue(e.color,r[5],r[6],3)*(e.over?gradientValue(e.over,t,r[7],3):1));'''
    new = '\n'.join('            out.%s=classicChannel(e,t,r[5],r[6],r[7],%d);' % (channel, i)
                    for i, channel in enumerate('rgba'))
    element = change(element, old, new)
    element = change(element, '            var visibleCount:int=0;var width:Number=0,alpha:Number=0;',
        '            var visibleCount:int=0;var width:Number=0,alpha:Number=0,packetAlpha:Number=0;')
    element = change(element,
        'if(sprite.visible){visibleCount++;width=Math.max(width,Math.abs(sprite.scaleX));alpha=Math.max(alpha,sprite.transform.colorTransform.alphaMultiplier);}',
        'if(sprite.visible){visibleCount++;width=Math.max(width,Math.abs(sprite.scaleX));alpha=Math.max(alpha,sprite.transform.colorTransform.alphaMultiplier);if(item.packet)packetAlpha=Math.max(packetAlpha,Number(item.packet.a));}')
    element = change(element, '",maxAlpha="+alpha;', '",maxAlpha="+alpha+",packetAlpha="+packetAlpha;')
    texts = {'BetaGwentBoard.as': board, 'BetaGwentElement164.as': element}
    for folder in ['src', 'src-BetaGwentBoard', 'src-GwintGame', 'src-DeckBuilder', 'src-BetaGwentKeg']:
        for name, text in texts.items():
            write(OUT / 'ui' / folder / name, text)
    manifest = json.loads((SOURCE / 'ui-inputs.json').read_text('utf8'))
    manifest['sources'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT / 'ui/src').glob('*.as')}
    (OUT / 'ui-inputs.json').write_text(json.dumps(manifest, indent=2), 'utf8')
    shutil.copy2(SOURCE / 'subimages.json', OUT / 'subimages.json')
    shutil.copytree(SOURCE / 'feedback-20261018', OUT / 'previous-feedback')
    print('Prepared isolated Classic opacity candidate; original weather, particles, materials and leader frames retained.')


if __name__ == '__main__':
    main()

"""Stage113: fixed pulse pivots, synchronized row counts and weather exit motion."""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'
DRAFT=ROOT/'BetaGwent/build/stage113/draft/BetaGwentBoard.as'

def one(src,old,new):
    if src.count(old)!=1:raise ValueError('Expected one animation integration point: '+old[:90])
    return src.replace(old,new,1)

def main():
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
    s=SOURCE.read_text('utf-8-sig')
    s=one(s,'weatherFades.push({sprite:oldWeather.sprite,start:getTimer(),alpha:oldWeather.sprite.alpha});',
        'weatherFades.push({sprite:oldWeather.sprite,effect:oldWeather,start:getTimer(),alpha:oldWeather.sprite.alpha});')
    s=one(s,'fading.sprite.alpha=fading.alpha*(1-fadeProgress);',
        '''advanceWeatherTextures(fading.effect,now);
                fading.sprite.alpha=fading.alpha*(1-BetaGwentBetaMotion.sample("PREVIEW",fadeProgress));''')
    start=s.index('                    for each(var part:Object in fx.nativeParts){',s.index('private function animateWeatherBody'))
    end=s.index('                    if(fx.beta&&redraw)',start)
    block=s[start:end]
    block=block.replace('                            continue;','                            updateFogIntro(part,t);continue;',1)
    helper='''        // Continue original texture motion during clearing; no frozen weather frame.
        private function advanceWeatherTextures(fx:Object,now:int):void
        {
            if(!fx||!fx.nativeParts)return;
            var t:Number=(now-fx.start)/1000;
'''+block+'''        }
'''
    s=s[:start]+'                    advanceWeatherTextures(fx,now);\n'+s[end:]
    s=one(s,'        private function animateWeather(e:Event):void',helper+'        private function animateWeather(e:Event):void')
    # Recenter changing digits from original ink metrics, then pulse around their
    # fixed visible center. Scale never walks a score outside its diamond/ribbon.
    s=one(s,'toValue:scores[side-1],duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:',
        'toValue:scores[side-1],numberX:scoreBox[0]+scoreBox[2]/2,numberY:scoreBox[1]+scoreBox[3]/2,numberSize:60,duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:')
    s=one(s,'field.x=cx-field.width/2-offset[0];field.y=cy-offset[1];',
        'field.x=cx-field.width/(2*field.scaleX)-offset[0];field.y=cy-offset[1];')
    old='''                if(skin==3)centerBetaNumber(rowTotal,rowScore[0]+rowScore[2]/2,rowScore[1]+rowScore[3]/2,32);'''
    new=old+'''
                if(skin==3 && playing && activeCue && activeCue.kind==2 && !reducedMotion){
                    var oldTotal:int=0;
                    for each(var previousUnit:Object in displayedCards)
                        if(previousUnit.side==side && previousUnit.zone==zone && (int(previousUnit.tokens)&8)==0)oldTotal+=previousUnit.power;
                    if(oldTotal!=total){
                        rowTotal.text=String(oldTotal);
                        animations.push({sprite:rowTotal,fromX:rowTotal.x,fromY:rowTotal.y,toX:rowTotal.x,toY:rowTotal.y,counter:rowTotal,
                            fromValue:oldTotal,toValue:total,numberX:rowScore[0]+rowScore[2]/2,numberY:rowScore[1]+rowScore[3]/2,numberSize:32,
                            duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:total>oldTotal?"POWER_UP":"POWER_DOWN",delay:cueImpactDelay()*animationTempo});
                    }
                }'''
    s=one(s,old,new)
    old='''                sprite.scaleX=scaleX;sprite.scaleY=scaleY;sprite.rotation=angle;'''
    new='''                // A numeric pulse uses the glyph center as its pivot. Ordinary
                // card movement still uses the card's layout/flight coordinates.
                if(motion.numberSize && sprite is TextField){
                    centerBetaNumber(sprite as TextField,motion.numberX,motion.numberY,motion.numberSize);
                    sprite.x=motion.numberX-(motion.numberX-sprite.x)*scaleX;
                    sprite.y=motion.numberY-(motion.numberY-sprite.y)*scaleY;
                }else if(motion.scaleCurve && sprite is TextField){
                    sprite.x+=(sprite.width/sprite.scaleX)*(motion.baseScaleX-scaleX)/2;
                    sprite.y+=(sprite.height/sprite.scaleY)*(motion.baseScaleY-scaleY)/2;
                }
                sprite.scaleX=scaleX;sprite.scaleY=scaleY;sprite.rotation=angle;'''
    s=one(s,old,new)
    DRAFT.parent.mkdir(parents=True,exist_ok=True);DRAFT.write_text(s,'utf8')
    if a.apply:SOURCE.write_text(s,'utf8')
    print('Stage113 animation changes', 'applied' if a.apply else 'prepared')

if __name__=='__main__':main()

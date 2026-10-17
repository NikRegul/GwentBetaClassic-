"""Prepare a pinned Classic follow-up; retain the accepted native subimages."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/classic081-subimages-fix12'
OUT = ROOT / 'BetaGwent/build/classic081-hand-fix13'


def replace(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new)


def main():
    assert not OUT.exists(), 'Keep previous candidates immutable'
    shutil.copytree(SOURCE / 'ui', OUT / 'ui')
    text = (SOURCE / 'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    text = replace(text,
        'for each(var motion:Object in animations)if(motion.sprite==sprite){motion.finished=true;sprite.x=motion.toX;sprite.y=motion.toY;}',
        'for each(var motion:Object in animations)if(motion.sprite==sprite)finishHandLayoutMotion(motion,sprite);')
    text = replace(text, '        private function safeHistoryCard(', '''        private function finishHandLayoutMotion(motion:Object,sprite:Sprite):void
        {
            // A hover takes over the hand layout, including the final appearance
            // state. Merely marking an appear motion finished leaves alpha at 0.
            motion.finished=true;sprite.x=motion.toX;sprite.y=motion.toY;
            if(motion.appear)sprite.alpha=1;
            if(motion.toScaleX!=null)sprite.scaleX=motion.toScaleX;
            if(motion.toScaleY!=null)sprite.scaleY=motion.toScaleY;
            if(motion.toRotation!=null)sprite.rotation=motion.toRotation;
        }
        private function safeHistoryCard(''')
    text = replace(text,
        'var ribbon:Array=BetaGwentBoardLayout.ribbon[faction+":"+side]||BetaGwentBoardLayout.ribbon["2:"+side];',
        'var ribbon:Array=classicBattleRibbon(faction,side);')
    text = replace(text, '        private function drawBetaBattleHud():void', '''        private function classicBattleRibbon(faction:int,side:int):Array
        {
            var source:Array=BetaGwentBoardLayout.ribbon[faction+":"+side]||BetaGwentBoardLayout.ribbon["2:"+side];
            var result:Array=source.concat();
            var scoreBox:Array=BetaGwentBoardLayout.score[String(side)];
            // Keep the pointed edge inside the total-score column, leaving a
            // visible gap before the middle row's rail and separate row score.
            result[2]=Math.min(result[2],scoreBox[0]+scoreBox[2]-result[0]);
            return result;
        }
        private function drawBetaBattleHud():void''')
    old = '''                    animations.push({sprite:p,fromX:originX,fromY:originY,toX:p.x,toY:p.y,fade:false,remove:false,appear:true,
                        duration:isHand?260:activeCue&&activeCue.kind==1?600:420,arc:isHand?0:36,betaFlight:true,settle:!isHand,tilt:originX<p.x?5:-5,fromRotation:0,toRotation:handAngle,fromScaleX:.8,fromScaleY:.8,toScaleX:1,toScaleY:1});
                    p.x=originX;p.y=originY;p.alpha=0;'''
    new = '''                    // The initial post-mulligan hand is a complete snapshot,
                    // not a draw cue. Show it immediately; only actual draws
                    // animate from the deck. Board arrivals retain their flight.
                    if(!isHand||activeCue&&activeCue.kind==14){
                        animations.push({sprite:p,fromX:originX,fromY:originY,toX:p.x,toY:p.y,fade:false,remove:false,appear:true,
                            duration:isHand?260:activeCue&&activeCue.kind==1?600:420,arc:isHand?0:36,betaFlight:true,settle:!isHand,tilt:originX<p.x?5:-5,fromRotation:0,toRotation:handAngle,fromScaleX:.8,fromScaleY:.8,toScaleX:1,toScaleY:1});
                        p.x=originX;p.y=originY;p.alpha=0;
                    }'''
    text = replace(text, old, new)
    text = replace(text, '            displayedCards=nextCards;', '''            displayedCards=nextCards;
            reportClassicHandState("built");classicHandReportAt=getTimer()+1200;''')
    text = replace(text, '        private var artworkReportPending:Boolean=false;', '''        private var classicHandReportAt:int=0;
        private function reportClassicHandState(phase:String):void
        {
            if(!connected||selectingDecks||editingDeck||browsingCatalog||kegOpen||entryMode==1)return;
            var received:int=0,created:int=0,visibleCount:int=0;var states:Array=[];
            for each(var c:Object in cards)if(c.side==1&&c.zone==8){
                received++;var sprite:Sprite=cardSprites[c.id] as Sprite;
                if(!sprite){states.push(c.id+":missing");continue;}
                created++;if(sprite.visible&&sprite.alpha>0&&sprite.parent==content)visibleCount++;
                states.push(c.id+":"+sprite.x+","+sprite.y+","+sprite.width+","+sprite.height+
                    ",a="+sprite.alpha+",s="+sprite.scaleX+","+sprite.scaleY+",v="+sprite.visible+
                    ",children="+sprite.numChildren+",attached="+(sprite.parent==content));
            }
            send("OnBetaGwentControllerTrace",[0,"HAND_STATE","classic_hand_fix13",
                "phase="+phase+" revision="+revision+" received="+received+" created="+created+" visible="+visibleCount+
                " playing="+playing+" request="+requestId+":"+requestKind+" pending="+canPlacePending()+
                " content="+content.x+","+content.y+","+content.scaleX+","+content.scaleY+","+content.alpha+","+content.visible+
                " clip="+content.scrollRect+" cards="+states.join(";")]);
        }
        private var artworkReportPending:Boolean=false;''')
    text = replace(text, '            updateReplayMouse(now);', '''            updateReplayMouse(now);
            if(classicHandReportAt>0&&now>=classicHandReportAt){classicHandReportAt=0;reportClassicHandState("settled");}''')
    raw = b'\xef\xbb\xbf' + text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        (OUT / 'ui' / folder / 'BetaGwentBoard.as').write_bytes(raw)
    manifest = json.loads((SOURCE/'ui-inputs.json').read_text('utf8'))
    manifest['sources'] = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (OUT/'ui/src').glob('*.as')}
    (OUT/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    shutil.copy2(SOURCE/'subimages.json',OUT/'subimages.json')
    # Preserve the current live script log before another launch can replace it.
    saved = OUT/'previous-feedback';saved.mkdir()
    live = Path.home()/'Documents/The Witcher 3/scriptslog.txt'
    if live.exists():shutil.copy2(live,saved/'scriptslog.txt')
    capture = ROOT/'BetaGwent/build/classic132-full-feedback/20261016-212559-523754'
    (saved/'capture.json').write_text(json.dumps(dict(path=str(capture),
        files=[dict(name=p.name,bytes=p.stat().st_size) for p in capture.iterdir() if p.is_file()],
        userConfirmed='Editor and all tabs work; own hand absent after mulligan; score ribbon overlaps row'),indent=2),'utf8')
    print('Prepared fix13 in five isolated BOM/CRLF source copies; prior logs retained.')


if __name__=='__main__':main()

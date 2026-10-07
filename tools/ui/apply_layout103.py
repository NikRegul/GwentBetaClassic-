"""Switch the Beta battle skin (skin==3) to BetaGwentBoardLayout (original level8 projection).
Fail-closed: every anchor must match exactly once. Preserves BOM/CRLF."""
from pathlib import Path
import sys
ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
src = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
t = raw.decode('utf-8-sig').replace('\r\n', '\n')
if 'BetaGwentBoardLayout.' in t: raise SystemExit('Already applied')
R = []
def rep(old, new):
    global t
    n = t.count(old)
    if n != 1: raise SystemExit(f'Anchor matched {n} times: {old[:90]!r}')
    t = t.replace(old, new); R.append(old[:60])

# 1. Board halves: HD bake world bounds projected on the original row plane.
rep("""                var half:Sprite=BetaGwentCardArt.view(-1300-number*2-(side-1),1160,400);
                if(half){
                    // Match the camera's screen X convention: original Unity
                    // mesh export puts the score rail on the opposite edge.
                    half.scaleX=-1;half.x=1472;half.y=side==1?554:154;content.addChild(half);
                }""",
"""                var area:Array=BetaGwentBoardLayout.boardHalf[String(side)];
                var half:Sprite=BetaGwentCardArt.view(-1300-number*2-(side-1),area[2],area[3]);
                if(half){
                    // Match the camera's screen X convention: original Unity
                    // mesh export puts the score rail on the opposite edge.
                    half.scaleX=-1;half.x=area[0]+area[2];half.y=area[1];content.addChild(half);
                }""")
# 2. Rows: original row colliders (180 x 23.5 world units).
rep("if(skin==3)return {x:604,y:(side==1?584:218)+ordinal*104,w:742,h:96};",
    "if(skin==3){var row:Array=BetaGwentBoardLayout.rows[side+\":\"+zone];return {x:row[0],y:row[1],w:row[2],h:row[3]};}")
# 3. Row totals: LocationScores/*Score centres.
rep("""var rowTotal:TextField=text(content,String(total),geometry.x-(skin==3?104:88),geometry.y+24,75,skin==3?32:26,0xFFFFFF);rowTotal.height=49;""",
"""var rowScore:Array=skin==3?BetaGwentBoardLayout.rowScore[side+":"+zone]:null;
                var rowTotal:TextField=text(content,String(total),skin==3?rowScore[0]+rowScore[2]/2-40:geometry.x-88,skin==3?rowScore[1]+rowScore[3]/2-24:geometry.y+24,skin==3?80:75,skin==3?32:26,0xFFFFFF);rowTotal.height=49;""")
# 4. Round header out of the opponent hand strip.
rep("""current==2?"Ход соперника":"Ожидание"),skin==3?1140:1320,26,skin==3?350:560,24);""",
    """current==2?"Ход соперника":"Ожидание"),skin==3?40:1320,skin==3?14:26,skin==3?360:560,24);""")
# 5. Side panel starts below the opponent deck/graveyard (original y 5..154).
rep("""            betaFrame(content,1504,130,368,538);
            panel(content,1512,138,352,522,0x070908,.55);
            battlePreview=new Sprite();battlePreview.x=1516;battlePreview.y=140;content.addChild(battlePreview);
            inspection=text(content,"Наведите на карту.\\nI или Shift + клик — полное описание.",1532,520,312,19,0xD8D0BB);inspection.height=134;""",
"""            var panelTop:Number=skin==3?162:130;
            betaFrame(content,1504,panelTop,368,668-panelTop);
            panel(content,1512,panelTop+8,352,660-panelTop-8,0x070908,.55);
            battlePreview=new Sprite();battlePreview.x=1516;battlePreview.y=panelTop+10;content.addChild(battlePreview);
            inspection=text(content,"Наведите на карту.\\nI или Shift + клик — полное описание.",1532,skin==3?556:520,312,19,0xD8D0BB);inspection.height=skin==3?104:134;""")
# 6. HUD: ribbon, crown halves, score, leader, names, pass, hand counter, piles, coin.
start = t.index('        private function drawBetaBattleHud():void')
end = t.index('        private function drawBetaPile(side:int,zone:int,x:Number,y:Number,count:int):void')
old_hud = t[start:end]
for must in ('paintArt(banner,-1530-faction*2-(side-1),324,114,0,0);', 'coin.x=214;coin.y=488;', 'leader.x=side==1?270:90;'):
    if must not in old_hud: raise SystemExit('HUD body changed: ' + must)
new_hud = '''        private function drawBetaBattleHud():void
        {
            // Positions: BetaGwentBoardLayout (original level8 PlayerRibbon,
            // CrownsView/CrownHalf1..2, PlayerScore, Leader, Counters, CoinRoot).
            for(var side:int=1;side<=2;side++){
                var faction:int=editorFactionIndex(cardFaction(int(leaderIds[side-1])));
                var key:String=String(side);
                var ribbon:Array=BetaGwentBoardLayout.ribbon[faction+":"+side]||BetaGwentBoardLayout.ribbon["2:"+side];
                var banner:Sprite=new Sprite();banner.x=ribbon[0];banner.y=ribbon[1];banner.mouseEnabled=false;banner.mouseChildren=false;content.addChild(banner);
                paintArt(banner,-1530-faction*2-(side-1),ribbon[2],ribbon[3],0,0);
                banner.transform.colorTransform=new ColorTransform(side==1 ? 0.25 : 1,side==1 ? 0.68 : 0.22,side==1 ? 1 : 0.16);
                for(var halfIndex:int=1;halfIndex<=2;halfIndex++){
                    var slot:Array=BetaGwentBoardLayout.crownHalf[side+":"+halfIndex];
                    var won:Boolean=crowns[side-1]>=halfIndex;
                    var crown:Sprite=new Sprite();crown.x=slot[0];crown.y=slot[1];crown.mouseEnabled=false;crown.mouseChildren=false;content.addChild(crown);
                    paintArt(crown,(side==1?-1540:-1542)+(halfIndex-1),slot[2],slot[3],0,0);
                    // Not yet won: the same half, dimmed and desaturated.
                    if(!won){crown.alpha=.32;crown.transform.colorTransform=new ColorTransform(.42,.42,.42);}
                    if(won&&activeCue&&activeCue.kind==6&&halfIndex>previousCrowns[side-1]&&!reducedMotion){
                        animations.push({sprite:crown,fromX:slot[0],fromY:slot[1],toX:slot[0],toY:slot[1],appear:true,duration:480,delay:260,fromScaleX:1.7,fromScaleY:1.7,toScaleX:1,toScaleY:1});
                        crown.alpha=0;crown.scaleX=crown.scaleY=1.7;
                    }
                }
                var scoreBox:Array=BetaGwentBoardLayout.score[key];
                var scoreX:Number=scoreBox[0]-18,scoreY:Number=scoreBox[1]+scoreBox[3]/2-42;
                var value:TextField=text(content,String(scores[side-1]),scoreX,scoreY,scoreBox[2]+36,60,0xFFFFFF);value.height=84;
                value.defaultTextFormat=new TextFormat("$NormalFont",60,0xFFFFFF,true,null,null,null,null,"center");value.setTextFormat(value.defaultTextFormat);
                if(playing&&activeCue&&activeCue.kind==2&&previousScores[side-1]!=scores[side-1]&&!reducedMotion){
                    value.text=String(previousScores[side-1]);
                    animations.push({sprite:value,fromX:scoreX,fromY:scoreY,toX:scoreX,toY:scoreY,counter:value,fromValue:previousScores[side-1],toValue:scores[side-1],duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:scores[side-1]>previousScores[side-1]?"POWER_UP":"POWER_DOWN",delay:cueImpactDelay()*animationTempo});
                }
                var seat:Array=betaLeaderRect(side);
                var leader:Sprite=new Sprite();leader.x=seat[0];leader.y=seat[1];content.addChild(leader);
                paintChoiceArt(leader,int(leaderIds[side-1]),seat[2],seat[3]);
                var available:Boolean=side==1?leaderOne:leaderTwo;if(!available)leader.alpha=.45;
                var leaderText:Object=BetaGwentCardText.find(int(leaderIds[side-1]));
                var leaderView:Object={id:0,templateId:int(leaderIds[side-1]),title:leaderNames[side-1],side:side,zone:64,power:leaderText?leaderText.power:0,tokens:0};
                attachInspect(leader,leaderView,templateDetails[leaderIds[side-1]],seat[2],seat[3]);
                if(side==1&&available&&canAct()){
                    var playLeader:Function=function():void{submitBoard("OnBetaGwentBoardLeader",[revision]);};
                    controller.registerControl(leader,"Лидер · "+leaderTitle,playLeader,leaderView,templateDetails[leaderIds[side-1]],"control",null,new Rectangle(0,0,seat[2],seat[3]));
                    leader.buttonMode=true;leader.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{if(!isInspectMouse(e))submitBoard("OnBetaGwentBoardLeader",[revision]);});
                }
                text(content,side==1?"Геральт":"Соперник",40,side==1?ribbon[1]+ribbon[3]+4:ribbon[1]-30,210,24,side==1?0x7ACAE4:0xEAA18B).height=40;
                if((flags&(side==1?1:2))!=0)text(content,"ПАС",262,side==1?ribbon[1]+ribbon[3]+4:ribbon[1]-30,150,24,0xEBD797).height=34;
                var count:int=side==2?enemyHand:0;
                if(side==1)for each(var c:Object in cards)if(c.side==1&&c.zone==8)count++;
                var icon:Array=BetaGwentBoardLayout.handCounter[key];
                paintArt(content,-1522,icon[2]*.7,icon[3]*.7,icon[0]+icon[2]*.15,icon[1]+icon[3]*.15);
                var handText:TextField=text(content,String(count),icon[0]-10,side==1?icon[1]+icon[3]-6:icon[1]-30,icon[2]+20,24);handText.height=38;
                handText.defaultTextFormat=new TextFormat("$NormalFont",24,0xF1E8D3,true,null,null,null,null,"center");handText.setTextFormat(handText.defaultTextFormat);
                var grave:Array=BetaGwentBoardLayout.grave[key],deck:Array=BetaGwentBoardLayout.deck[key];
                drawBetaPile(side,32,grave[0],grave[1],graves[side-1],grave[2],grave[3]);
                drawBetaPile(side,16,deck[0],deck[1],deckCounts[side-1],deck[2],deck[3]);
            }
            var shown:int=current==1||current==2?current:coinSide;if(shown==0)shown=1;
            // CoinBase mesh (r=12.21) projected: centre (206.7,540.4), 135.8 x 131.3.
            var coinBox:Array=[138.8,474.8,135.8,131.3];
            var coin:Sprite=new Sprite();coin.x=coinBox[0];coin.y=coinBox[1];coin.mouseEnabled=false;coin.mouseChildren=false;content.addChild(coin);
            paintArt(coin,-1500,coinBox[2],coinBox[3],0,0);
            coin.transform.colorTransform=new ColorTransform(shown==1 ? 0.2 : 1,shown==1 ? 0.68 : 0.2,shown==1 ? 1 : 0.15);
            var coinIcon:Sprite=new Sprite();coinIcon.mouseEnabled=false;coinIcon.mouseChildren=false;content.addChild(coinIcon);
            var iconW:Number=coinBox[2]*.55,iconH:Number=coinBox[3]*.55;
            paintArt(coinIcon,-1501-editorFactionIndex(cardFaction(int(leaderIds[shown-1]))),iconW,iconH,coinBox[0]+(coinBox[2]-iconW)/2,coinBox[1]+(coinBox[3]-iconH)/2);
            if(shown!=coinSide&&!reducedMotion){
                animations.push({sprite:coin,fromX:coinBox[0],fromY:coinBox[1],toX:coinBox[0],toY:coinBox[1],appear:true,curve:"PREVIEW",duration:300,fromScaleX:.3,fromScaleY:1,toScaleX:1,toScaleY:1});coin.scaleX=.3;coin.alpha=0;
            }
            coinSide=shown;
            text(content,"P · пас   L · лидер\\nD · колода   G / H · сброс",40,868,330,16,0xBEB7A4).height=56;
        }
        private function betaLeaderRect(side:int):Array
        {
            // Original Leader collider is 146 x 200 at hand depth and is cut by
            // the screen edge; keep the visible card fully on screen.
            var r:Array=BetaGwentBoardLayout.leader[String(side)];
            var w:Number=104,h:Number=146;
            return [r[0]+(r[2]-w)/2,side==1?Math.min(r[1]+(r[3]-h)/2,1080-h-8):Math.max(r[1]+(r[3]-h)/2,8),w,h];
        }
        private function betaDeckPoint(side:int):Array
        {
            var r:Array=BetaGwentBoardLayout.deck[String(side)];return [r[0]+(r[2]-80)/2,r[1]+(r[3]-110)/2];
        }
'''
t = t[:start] + new_hud + t[end:]
# 7. Piles take their original size.
rep("""        private function drawBetaPile(side:int,zone:int,x:Number,y:Number,count:int):void
        {
            var pile:Sprite=new Sprite();pile.x=x;pile.y=y;content.addChild(pile);
            paintCardBack(pile,72,101,side);
            var top:Object=null;
            if(zone==32)for each(var c:Object in cards)if(c.side==side&&c.zone==32&&(top==null||c.index>top.index))top=c;
            if(top)paintChoiceArt(pile,top.templateId,66,95);
            paintArt(pile,zone==32?-1520:-1521,32,32,81,66);
            text(pile,String(count),80,25,64,28).height=40;""",
"""        private function drawBetaPile(side:int,zone:int,x:Number,y:Number,count:int,w:Number=72,h:Number=101):void
        {
            // Card stack inside the original 25.2 x 30 collider (card aspect kept).
            var cw:Number=Math.min(w-8,(h-8)*256/360),ch:Number=cw*360/256;
            var pile:Sprite=new Sprite();pile.x=x+(w-cw)/2;pile.y=y+(h-ch)/2;content.addChild(pile);
            paintCardBack(pile,cw,ch,side);
            var top:Object=null;
            if(zone==32)for each(var c:Object in cards)if(c.side==side&&c.zone==32&&(top==null||c.index>top.index))top=c;
            if(top)paintChoiceArt(pile,top.templateId,cw-6,ch-6);
            paintArt(pile,zone==32?-1520:-1521,32,32,cw-34,ch-36);
            var pileCount:TextField=text(pile,String(count),0,ch/2-20,cw,28);pileCount.height=40;
            pileCount.defaultTextFormat=new TextFormat("$NormalFont",28,0xFFFFFF,true,null,null,null,null,"center");pileCount.setTextFormat(pileCount.defaultTextFormat);""")
rep("""controller.registerControl(pile,(zone==32?"Сброс":"Колода")+" · "+(side==1?"Геральт":"Соперник"),action,null,null,"control",null,new Rectangle(0,0,144,106));""",
    """controller.registerControl(pile,(zone==32?"Сброс":"Колода")+" · "+(side==1?"Геральт":"Соперник"),action,null,null,"control",null,new Rectangle(0,0,cw,ch));""")
# 8. Own hand inside the original Hand collider (cards overlap like the original fan).
rep("""            var step:Number=Math.min(112,970/Math.max(1,handCount));
            var handWidth:Number=step-8;""",
"""            var handArea:Array=skin==3?BetaGwentBoardLayout.hand["1"]:null;
            var handLeft:Number=skin==3?handArea[0]:484;
            var handWidth:Number=skin==3?100:Math.min(112,970/Math.max(1,handCount))-8;
            var step:Number=skin==3?(handCount>1?Math.min(108,(handArea[2]-handWidth)/(handCount-1)):0):handWidth+8;
            if(skin==3)handLeft+=(handArea[2]-(handWidth+step*Math.max(0,handCount-1)))/2;""")
rep("var g:Object=isHand?{x:484+c.index*step,", "var g:Object=isHand?{x:handLeft+c.index*step,")
# 9. Played-card staging: original PresentationView per side.
rep("betaFlight:flight,staged:flight,stageX:860,stageY:380,stageScaleX:160/cardWidth,stageScaleY:225/cardHeight,",
    "betaFlight:flight,staged:flight,stageX:skin==3?BetaGwentBoardLayout.presentation[String(c.side)][0]:860,stageY:skin==3?BetaGwentBoardLayout.presentation[String(c.side)][1]:380,stageScaleX:(skin==3?BetaGwentBoardLayout.presentation[String(c.side)][2]:160)/cardWidth,stageScaleY:(skin==3?BetaGwentBoardLayout.presentation[String(c.side)][3]:225)/cardHeight,")
# 10. Draw/summon origins from the original deck positions.
rep("if(isHand&&activeCue&&activeCue.kind==14){originX=skin==3?1716:310;originY=skin==3?946:776;}",
    "if(isHand&&activeCue&&activeCue.kind==14){originX=skin==3?betaDeckPoint(1)[0]:310;originY=skin==3?betaDeckPoint(1)[1]:776;}")
rep("{originX=skin==3?1716:310;originY=skin==3?(c.side==1?946:12):(c.side==1?776:426);}",
    "{originX=skin==3?betaDeckPoint(c.side)[0]:310;originY=skin==3?betaDeckPoint(c.side)[1]:(c.side==1?776:426);}")
rep("else if(c.side==2){originX=630+Math.min(9,enemyHand)*54;originY=96;}",
    "else if(c.side==2){originX=skin==3?1039-23:630+Math.min(9,enemyHand)*54;originY=skin==3?24:96;}")
# 11. Pending placement card beside the leader.
rep("var p:Sprite=panel(content,484,926,80,140,0x173340,.96);", "var p:Sprite=panel(content,skin==3?660:484,926,80,140,0x173340,.96);")
rep("text(content,c.title+\" · сила \"+c.power,586,932,670,25,powerColor(c));", "text(content,c.title+\" · сила \"+c.power,skin==3?752:586,932,skin==3?660:670,25,powerColor(c));")
# 12. Leader cue highlight follows the leader seat.
rep("""                var y:Number=skin==3?(activeCue.side==1?946:184):(activeCue.side==1?575:225);
                fx.graphics.lineStyle(4,0xCFB176,.95);fx.graphics.drawRoundRect(skin==3?(activeCue.side==1?268:88):98,y-2,skin==3?76:284,skin==3?105:229,8,8);""",
"""                var seat:Array=skin==3?betaLeaderRect(activeCue.side):null;
                var y:Number=skin==3?seat[1]:(activeCue.side==1?575:225);
                fx.graphics.lineStyle(4,0xCFB176,.95);fx.graphics.drawRoundRect(skin==3?seat[0]-2:98,y-2,skin==3?seat[2]+4:284,skin==3?seat[3]+4:229,8,8);""")
# 13. Opponent hand backs: centred on the original top Hand collider.
rep("""            var spacing:Number=Math.min(54,750/Math.max(1,count));
            var backWidth:Number=Math.min(46,Math.max(8,spacing-4));""",
"""            var spacing:Number=Math.min(54,(skin==3?740:750)/Math.max(1,count));
            var backWidth:Number=Math.min(46,Math.max(8,spacing-4));
            var backsLeft:Number=skin==3?1039.4-(spacing*Math.max(0,count-1)+backWidth)/2:630,backsTop:Number=skin==3?24:96;""")
rep("back.x=630+i*spacing;back.y=96;", "back.x=backsLeft+i*spacing;back.y=backsTop;")
rep("var drawX:Number=skin==3?1716:310;var drawY:Number=skin==3?12:426;", "var drawX:Number=skin==3?betaDeckPoint(2)[0]:310;var drawY:Number=skin==3?betaDeckPoint(2)[1]:426;")
rep("animations.push({sprite:back,fromX:drawX,fromY:drawY,toX:finalX,toY:96,", "animations.push({sprite:back,fromX:drawX,fromY:drawY,toX:finalX,toY:backsTop,")

out = t.replace('\n', '\r\n') if crlf else t
src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + out.encode('utf8'))
print('applied', len(R), 'edits')

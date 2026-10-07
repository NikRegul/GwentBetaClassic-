"""Stage 104: Gwent Beta match intro (UIGameIntroRootPrefab) for skin 3.

Shown once per match when the first mulligan request arrives: red opponent half,
blue player half, leader cards fly in, name/title, leader plate, VS. The leader
lines play through OnBetaGwentAudioIntro (duelAudio.Intro). Click/Esc skips.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
MARK = '// stage104-intro'
METHODS = r'''
        // stage104-intro: UIGameIntroRootPrefab (handshake) presentation.
        private var introLayer:Sprite=new Sprite();
        private var introArmed:Boolean=true;
        private var introStart:int=0;
        private var introParts:Array=[];
        private static const INTRO_MS:int=4600;
        private function maybeStartIntro():void
        {
            var onBoard:int=0;for each(var placed:Object in cards)if((int(placed.zone)&7)!=0)onBoard++;
            var mulliganStart:Boolean=round==1&&requestKind==1&&rowMode==0&&requestCount==0&&(flags>>4)==0&&onBoard==0&&scores[0]==0&&scores[1]==0;
            if(!mulliganStart){introArmed=true;return;}
            if(!introArmed||skin!=3||entryMode==1)return;
            introArmed=false;startIntro();
        }
        private function introPart(s:Sprite,t0:int,t1:int,dx:Number=0,dy:Number=0,scale:Number=1):Sprite
        { introParts.push({sprite:s,t0:t0,t1:t1,dx:dx,dy:dy,scale:scale,x:s.x,y:s.y});s.alpha=0;return s; }
        private function introSide(side:int):void
        {
            var top:Boolean=side==2;var leader:int=int(leaderIds[side-1]);var fi:int=sideFaction(side);
            var half:Sprite=new Sprite();half.mouseEnabled=false;introLayer.addChild(half);half.y=top?0:540;
            half.graphics.beginFill(top?0x1C0606:0x04121E,1);half.graphics.drawRect(0,0,1920,540);half.graphics.endFill();
            var tint:ColorTransform=top?new ColorTransform(0,0,0,.55,150,22,18,0):new ColorTransform(0,0,0,.55,24,92,150,0);
            var left:Sprite=new Sprite();half.addChild(left);paintArt(left,BetaGwentHud104.introLeft(Math.min(4,fi)),316,540,0,0);left.transform.colorTransform=tint;
            var right:Sprite=new Sprite();half.addChild(right);paintArt(right,BetaGwentHud104.introRight(Math.min(4,fi)),282,540,1638,0);right.transform.colorTransform=tint;
            introPart(half,0,350);
            var cardX:Number=top?1147:547,cardY:Number=top?92:618;
            var w:Number=271,h:Number=Math.round(271/BETA_CARD_ASPECT);
            var deck:Sprite=new Sprite();deck.x=cardX+(top?18:-18);deck.y=cardY+8;deck.rotation=top?7:-7;introLayer.addChild(deck);
            paintCardBack(deck,w,h,side);introPart(deck,top?250:1050,top?650:1450,top?320:-320,0);
            var card:Sprite=new Sprite();card.x=cardX;card.y=cardY;introLayer.addChild(card);
            paintBetaFace(card,leader,w,h,side);
            var text0:Object=BetaGwentCardText.find(leader);
            if(text0&&text0.power>0)betaPowerField(card,String(text0.power),w,h,0xFFFFFF);
            card.filters=[new GlowFilter(0x000000,.8,24,24,2,2)];
            introPart(card,top?300:1100,top?760:1560,top?360:-360,0);
            var info:Sprite=new Sprite();info.x=top?540:967;info.y=top?160:705;introLayer.addChild(info);
            paintArt(info,side==1?BetaGwentHud104.PLAYER_AVATAR:BetaGwentHud104.avatar(leader,fi),47,47,153,12);
            var name:String=side==1?"Геральт":(npcDeckLabel&&npcDeckLabel.length?npcDeckLabel:"Соперник");
            betaLabel(info,name,212,6,300,21,side==1?0x3EA9E0:0xD0383A,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(info,side==1?"Ведьмак":"Мастер гвинта",212,34,300,18,side==1?0xB9D84A:0xEDE7DA,BetaGwentFonts.BODY);
            info.graphics.lineStyle(2,0x6E6E6E,.9);info.graphics.moveTo(0,95);info.graphics.lineTo(458,95);
            info.graphics.beginFill(0x9A9A9A);info.graphics.moveTo(229,89);info.graphics.lineTo(235,95);info.graphics.lineTo(229,101);info.graphics.lineTo(223,95);info.graphics.endFill();
            introPart(info,top?500:1300,top?900:1700,0,top?-16:16);
            var plate:Sprite=new Sprite();plate.x=top?592:1020;plate.y=top?280:822;introLayer.addChild(plate);
            paintArt(plate,BetaGwentHud104.titleBg(fi),356,80,0,0);
            betaLabel(plate,String(leaderNames[side-1]||"").toUpperCase(),0,10,356,21,0xFFFFFF,BetaGwentFonts.TITLE,true,"center",3);
            betaLabel(plate,BetaGwentCardTags.text(leader)||"",0,44,356,17,0xE4E0D6,BetaGwentFonts.BODY,false,"center");
            introPart(plate,top?650:1450,top?1050:1850,0,top?-12:12);
        }
        private function startIntro():void
        {
            finishIntro();
            setChildIndex(introLayer,numChildren-1);
            introLayer.mouseEnabled=true;introLayer.mouseChildren=false;introLayer.alpha=1;
            introLayer.graphics.beginFill(0,1);introLayer.graphics.drawRect(0,0,1920,1080);introLayer.graphics.endFill();
            introSide(2);introSide(1);
            var line:Sprite=new Sprite();introLayer.addChild(line);
            line.graphics.lineStyle(2,0x8A8A8A,.8);line.graphics.moveTo(0,540);line.graphics.lineTo(1920,540);introPart(line,0,350);
            var vs:Sprite=new Sprite();vs.x=960;vs.y=545;introLayer.addChild(vs);
            paintArt(vs,BetaGwentHud104.VS,196,127,-98,-63);introPart(vs,700,1000,0,0,2.2);
            introLayer.addEventListener(MouseEvent.CLICK,skipIntro);
            introStart=getTimer();
            send("OnBetaGwentAudioIntro",[int(leaderIds[1]),int(leaderIds[0])]);
        }
        private function skipIntro(e:MouseEvent=null):void
        { if(e)e.stopImmediatePropagation();if(introStart>0)introStart=Math.min(introStart,getTimer()-INTRO_MS+380); }
        private function finishIntro():void
        {
            introStart=0;introParts=[];introLayer.removeEventListener(MouseEvent.CLICK,skipIntro);
            introLayer.graphics.clear();while(introLayer.numChildren)introLayer.removeChildAt(0);introLayer.mouseEnabled=false;
        }
        private function animateIntro(e:Event):void
        {
            if(introStart<=0)return;
            var t:int=getTimer()-introStart;
            if(t>=INTRO_MS){finishIntro();return;}
            introLayer.alpha=t>INTRO_MS-380?(INTRO_MS-t)/380:1;
            for each(var part:Object in introParts){
                var k:Number=Math.max(0,Math.min(1,(t-part.t0)/Math.max(1,part.t1-part.t0)));
                var ease:Number=1-Math.pow(1-k,3);
                part.sprite.alpha=k;
                part.sprite.x=part.x+part.dx*(1-ease);part.sprite.y=part.y+part.dy*(1-ease);
                if(part.scale!=1){var s:Number=part.scale+(1-part.scale)*ease;part.sprite.scaleX=part.sprite.scaleY=s;}
            }
        }
'''

def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
    if MARK in t: raise SystemExit('already applied')
    def rep(a, b):
        nonlocal t
        if t.count(a) != 1: raise SystemExit('anchor %d: %r' % (t.count(a), a[:90]))
        t = t.replace(a, b)
    rep('        private function betaLeaderRect(side:int):Array', METHODS.lstrip('\n').replace('        // stage104-intro: UI', '        ' + MARK + '\n        // UI') + '        private function betaLeaderRect(side:int):Array')
    rep('            addChild(nameLayer);\n', '            addChild(nameLayer);\n            addChild(introLayer);introLayer.mouseEnabled=false;\n')
    rep('            addEventListener(Event.ENTER_FRAME,animateBetaOverlay);\n', '            addEventListener(Event.ENTER_FRAME,animateBetaOverlay);\n            addEventListener(Event.ENTER_FRAME,animateIntro);\n')
    rep('            previousTurn=current;\n', '            previousTurn=current;\n            maybeStartIntro();\n')
    # The YOUR TURN banner must not fire underneath the intro.
    rep('            if(skin==3&&current==1&&previousTurn!=1&&requestKind!=1', '            if(skin==3&&introStart==0&&current==1&&previousTurn!=1&&requestKind!=1')
    if crlf: t = t.replace('\n', '\r\n')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))
    print('intro applied')

if __name__ == '__main__':
    main()

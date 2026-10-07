"""Stage 104: Gwent Beta battle HUD for skin 3 (BetaGwentBoard.as).

Avatar/name/title, Beta counters, opponent hand as full card backs, side preview
(large card + faction name plate + description), action hints, menu button,
hold-to-pass coin, turn glow, PASS strips, YOUR TURN banner, round result window.
Idempotent: refuses when the marker is already present.
"""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
MARK = '// stage104-hud'

METHODS = r'''
        // stage104-hud: original Beta battle HUD (UIBattlePrefab, UIBoardPlayerControl,
        // UISidePreview, UIBoardMessagesPrefab/YourTurnBanner, UIPlayerPassPrefab).
        private var betaOverlay:Sprite=new Sprite();
        private var turnBannerAt:int=0;
        private var previousTurn:int=0;
        private var passHoldStart:int=0;
        private var passRing:Sprite;
        private static const PASS_HOLD_MS:int=650;
        private function betaFace(face:String,field:TextField,size:Number,color:uint,bold:Boolean=false,align:String=null,spacing:Number=0):TextField
        {
            if(!BetaGwentFonts.apply(field,face,size,color,bold,align,spacing)){
                var f:TextFormat=new TextFormat("$NormalFont",size,color,bold,null,null,null,null,align);field.defaultTextFormat=f;field.setTextFormat(f);
            }
            return field;
        }
        private function betaLabel(parent:Sprite,value:String,x:Number,y:Number,w:Number,size:Number,color:uint,face:String,bold:Boolean=false,align:String=null,spacing:Number=0):TextField
        {
            var field:TextField=text(parent,value,x,y,w,int(size),color);field.multiline=false;field.wordWrap=false;field.height=size*1.6;
            return betaFace(face,field,size,color,bold,align,spacing);
        }
        private function sideFaction(side:int):int
        { return editorFactionIndex(cardFaction(int(leaderIds[Math.max(0,side-1)]))); }
        private function drawBetaTurnGlow():void
        {
            if(current!=1&&current!=2)return;
            var g:Sprite=new Sprite();g.mouseEnabled=false;g.mouseChildren=false;content.addChild(g);
            var m:Matrix=new Matrix();var top:Boolean=current==2;
            m.createGradientBox(1920,150,top?Math.PI/2:-Math.PI/2,0,top?0:930);
            g.graphics.beginGradientFill(GradientType.LINEAR,top?[0xD0261B,0xD0261B]:[0x2C9BE6,0x2C9BE6],[.55,0],[0,255],m);
            g.graphics.drawRect(0,top?0:930,1920,150);g.graphics.endFill();
            g.graphics.beginFill(top?0xFF5A3C:0x6FD2FF,.55);g.graphics.drawRect(0,top?0:1076,1920,4);g.graphics.endFill();
            if(!reducedMotion)animations.push({sprite:g,fromX:0,fromY:0,toX:0,toY:0,appear:true,remove:false,duration:420});
        }
        private function drawBetaProfile(side:int):void
        {
            var top:Number=side==2?38:985;
            var frame:Sprite=new Sprite();frame.x=75;frame.y=top;frame.mouseEnabled=false;frame.mouseChildren=false;content.addChild(frame);
            frame.graphics.beginFill(0x000000,.85);frame.graphics.drawRect(-2,-2,61,61);frame.graphics.endFill();
            paintArt(frame,side==1?BetaGwentHud104.PLAYER_AVATAR:BetaGwentHud104.avatar(int(leaderIds[1]),sideFaction(2)),57,57,0,0);
            var name:String=side==1?"Геральт":(npcDeckLabel&&npcDeckLabel.length?npcDeckLabel:"Соперник");
            betaLabel(content,name,192,top-3,320,21,side==1?0x3EA9E0:0xD0383A,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(content,String(leaderNames[side-1]||""),192,top+26,330,17,0xEDE7DA,BetaGwentFonts.BODY);
        }
        private function drawBetaCounter(icon:int,value:int,cx:Number,side:int):void
        {
            var iconY:Number=side==2?66:974,numberY:Number=side==2?22:1010;
            paintArt(content,icon,32,32,cx-16,iconY);
            var n:TextField=betaLabel(content,String(value),cx-40,numberY,80,30,0xCFC8BA,BetaGwentFonts.NUMBERS,false,"center");n.height=44;
        }
        private function drawBetaCoinControls(coin:Sprite,coinBox:Array):void
        {
            if(!canAct())return;
            coin.mouseEnabled=true;coin.buttonMode=true;
            passRing=new Sprite();passRing.mouseEnabled=false;passRing.x=coinBox[0]+coinBox[2]/2;passRing.y=coinBox[1]+coinBox[3]/2;content.addChild(passRing);
            coin.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{if(isInspectMouse(e))return;e.stopImmediatePropagation();passHoldStart=getTimer();
                if(stage)stage.addEventListener(MouseEvent.MOUSE_UP,cancelPassHold);});
            var hint:Sprite=new Sprite();hint.mouseEnabled=false;hint.mouseChildren=false;content.addChild(hint);
            paintArt(hint,BetaGwentHud104.KEY_LC,36,36,20,414);
            betaLabel(hint,"ЗАЖМИТЕ, ЧТОБЫ СПАСОВАТЬ",60,416,330,22,0xF2EEE4,BetaGwentFonts.BODY);
        }
        private function cancelPassHold(e:MouseEvent=null):void
        {
            passHoldStart=0;if(stage)stage.removeEventListener(MouseEvent.MOUSE_UP,cancelPassHold);
            if(passRing)passRing.graphics.clear();
        }
        private function drawBetaMenuButton():void
        {
            var b:Sprite=new Sprite();b.x=165;b.y=854;content.addChild(b);
            paintArt(b,BetaGwentHud104.MENU_IDLE,78,54,0,0);
            var hover:Sprite=new Sprite();hover.mouseEnabled=false;paintArt(hover,BetaGwentHud104.MENU_HOVER,78,54,0,0);hover.alpha=0;b.addChild(hover);
            b.buttonMode=true;
            b.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{hover.alpha=1;});
            b.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{hover.alpha=0;});
            b.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();openControllerMenu();});
            controller.registerControl(b,"Меню",openControllerMenu,null,null,"control",null,new Rectangle(0,0,78,54));
        }
        private var hintRight:Number=1880;
        private function drawBetaHint(label:String,icon:int,callback:Function,enabled:Boolean=true):void
        {
            var h:Sprite=new Sprite();h.y=866;content.addChild(h);
            var field:TextField=betaLabel(h,label.toUpperCase(),0,6,600,22,enabled?0xF2EEE4:0x8E8A82,BetaGwentFonts.BODY,false,null,.5);
            var w:Number=Math.ceil(field.textWidth)+8;field.width=w;
            var iconW:Number=icon!=0?40:0;field.x=iconW;
            if(icon!=0)paintArt(h,icon,36,36,0,1);
            h.x=hintRight-(iconW+w);hintRight=h.x-28;
            if(callback!=null&&enabled){
                h.buttonMode=true;h.mouseChildren=false;
                h.graphics.beginFill(0,0);h.graphics.drawRect(0,0,iconW+w,38);h.graphics.endFill();
                h.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                controller.registerControl(h,label,callback,null,null,"control",null,new Rectangle(0,0,iconW+w,38));
            }else{h.mouseEnabled=false;h.mouseChildren=false;}
        }
        private function drawBetaActions():void
        {
            hintRight=1880;
            if(playing){drawBetaHint("Пропустить",BetaGwentHud104.KEY_LC,skipReplay);return;}
            if(requestId>0&&requestFinish){
                drawBetaHint(isCaranthirChoice()?"Мороз без перемещения":templateChoice?"Выберите вариант":pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):handPowerChoice?"Выберите отряд":graveyardChoice?"Без поглощения":requestKind==1?"Закончить обмен":leaderRow?"Отмена":"Без цели",
                    BetaGwentHud104.KEY_LC,requestAction("OnBetaGwentRequestFinish"),ready&&requestFinish&&(!rowRequest||leaderRow||rowMode==3||rowMode==1||rowMode>=8));
            }else if(requestId>0)drawBetaHint("Выбор обязателен",0,null,false);
            drawBetaHint("Осмотреть",BetaGwentHud104.KEY_RC,null,true);
            if((flags>>4)>0&&ready){
                betaWideButton("Повторить",700,640,240,entryMode!=2,function():void{submitBoard("OnBetaGwentBoardRematch",[serverRevision]);});
                betaWideButton("Закрыть",980,640,240,connected,requestBoardClose);
            }
        }
        private function betaWideButton(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function):void
        {
            var b:Sprite=new Sprite();b.x=x;b.y=y;content.addChild(b);b.alpha=enabled?1:.5;
            paintArt(b,BetaGwentHud104.WIDE_IDLE,w,48,0,0);
            var hover:Sprite=new Sprite();hover.mouseEnabled=false;paintArt(hover,BetaGwentHud104.WIDE_HOVER,w,48,0,0);hover.alpha=0;b.addChild(hover);
            betaLabel(b,title.toUpperCase(),0,10,w,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2).mouseEnabled=false;
            if(enabled){
                b.buttonMode=true;b.mouseChildren=false;
                b.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{hover.alpha=1;});
                b.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{hover.alpha=0;});
                b.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                controller.registerControl(b,title,callback,null,null,"control",null,new Rectangle(0,0,w,48));
            }
        }
        private function drawBetaPassStrips():void
        {
            for(var side:int=1;side<=2;side++){
                if((flags&(side==1?1:2))==0)continue;
                var s:Sprite=new Sprite();s.mouseEnabled=false;s.mouseChildren=false;content.addChild(s);
                var shade:Sprite=new Sprite();s.addChild(shade);paintArt(shade,BetaGwentHud104.STATUS_SHADOW,1920,130,0,0);
                if(side==1){shade.scaleY=-1;shade.y=1080;}
                shade.alpha=.9;
                betaLabel(s,"ПАС",560,side==2?44:976,800,46,0xEFE9DC,BetaGwentFonts.TITLE,true,"center",10);
            }
        }
        private function clearBattlePreview():void
        { if(battlePreview)while(battlePreview.numChildren)battlePreview.removeChildAt(0);battlePreviewKey=""; }
        private function drawBetaSidePreview(c:Object,detail:Object):void
        {
            var side:int=int(c.side)||1;
            var w:Number=312,h:Number=Math.round(312/BETA_CARD_ASPECT);
            var card:Sprite=new Sprite();card.x=1550;card.y=572-h;battlePreview.addChild(card);
            if(c.templateId>0){
                paintBetaFace(card,c.templateId,w,h,side);
                var original:Object=BetaGwentCardText.find(c.templateId);
                if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0))betaPowerField(card,String(c.power),w,h,powerColor(c));
            }else paintCardBack(card,w,h,2);
            card.filters=[new GlowFilter(side==2?0xE0402A:0x3AA8F0,.85,16,16,2,2)];
            if(!reducedMotion){
                animations.push({sprite:card,fromX:1574,fromY:card.y,toX:1550,toY:card.y,curve:"PREVIEW",duration:BetaGwentBetaMotion.duration("PREVIEW"),appear:true});
                card.x=1574;card.alpha=0;
            }
            var entry:Object=BetaGwentFullCatalog.find(c.templateId);
            var faction:int=entry?int(entry.faction):1;
            var fi:int=(faction&62)==0?sideFaction(side):editorFactionIndex(faction);
            if(c.templateId<=0)fi=sideFaction(2);
            paintArt(battlePreview,BetaGwentHud104.titleBg(fi),283,76,1579,586);
            paintArt(battlePreview,BetaGwentHud104.titleLine(fi),283,4,1579,584);
            var title:String=String(c.title||"").toUpperCase();
            var name:TextField=betaLabel(battlePreview,title,1593,592,262,20,0xFFFFFF,BetaGwentFonts.TITLE,true,null,3);
            if(name.textWidth>256)betaFace(BetaGwentFonts.TITLE,name,Math.max(13,Math.floor(20*252/name.textWidth)),0xFFFFFF,true,null,2);
            betaLabel(battlePreview,c.templateId>0?(BetaGwentCardTags.text(c.templateId)||""):"",1593,626,262,16,0xE4E0D6,BetaGwentFonts.BODY);
            var hidden:Boolean=(c.zone&7)!=0&&(int(c.tokens)&8)!=0;
            var reading:String=hidden?ambushReading(c):readableText(detail?detail.description:c.description);
            if(c.timer!=null&&int(c.timer)>=0)reading+=(reading.length?"\n":"")+"Счётчик: "+int(c.timer);
            var info:Sprite=new Sprite();info.x=1579;info.y=662;battlePreview.addChild(info);
            var body:TextField=text(info,reading,14,10,255,18,0xEDEAE2);body.wordWrap=true;body.multiline=true;
            body.height=Math.min(330,body.textHeight+10);
            var bh:Number=Math.max(56,body.height+20);
            var bg:Sprite=new Sprite();info.addChildAt(bg,0);paintArt(bg,BetaGwentHud104.infoBg(fi),283,bh,0,0);
            paintArt(info,BetaGwentHud104.titleLine(fi),283,4,0,bh-2);
        }
        private function drawBetaRoundBanner(parent:Sprite,animate:Boolean):void
        {
            var result:Object=lastRoundResult;if(!result)return;
            var matchWinner:int=int(result.flags)>>4;
            var winner:int=matchWinner>0?matchWinner:result.scores[0]>result.scores[1]?1:result.scores[0]<result.scores[1]?2:3;
            var title:String=matchWinner>0?(winner==1?"ПОБЕДА!":winner==2?"ПОРАЖЕНИЕ!":"НИЧЬЯ!"):(winner==1?"ВЫ ВЫИГРАЛИ РАУНД!":winner==2?"ПРОТИВНИК ВЫИГРАЛ РАУНД!":"НИЧЬЯ!");
            var next:int=int(result.round)+1;
            var line:String=matchWinner>0?"Партия завершена":next>=3?"Начало финального раунда!":"Начало второго раунда!";
            var root:Sprite=new Sprite();root.mouseEnabled=false;root.mouseChildren=false;parent.addChild(root);
            root.graphics.beginFill(winner==1?0x02121E:winner==2?0x1E0303:0x0E0E0E,.78);root.graphics.drawRect(0,0,1920,1080);root.graphics.endFill();
            var box:Sprite=new Sprite();box.x=499;box.y=440;root.addChild(box);
            box.graphics.beginFill(0x000000,.94);box.graphics.drawRect(0,0,929,136);box.graphics.endFill();
            var bar:Sprite=new Sprite();box.addChild(bar);paintArt(bar,BetaGwentHud104.POPUP_TITLE,929,70,0,0);
            bar.transform.colorTransform=winner==1?new ColorTransform(.35,.9,1.6):winner==2?new ColorTransform(1.9,.45,.35):new ColorTransform(1,1,1);
            box.graphics.lineStyle(2,0x8C8C8C,.9);box.graphics.drawRect(0,0,929,136);
            box.graphics.lineStyle(1,0x5A5A5A,.9);box.graphics.moveTo(0,70);box.graphics.lineTo(929,70);
            for each(var corner:Array in [[0,0,1,1],[929,0,-1,1],[0,136,1,-1],[929,136,-1,-1]]){
                box.graphics.lineStyle(2,0xBDBDBD,1);box.graphics.moveTo(corner[0],corner[1]+corner[3]*9);box.graphics.lineTo(corner[0],corner[1]);box.graphics.lineTo(corner[0]+corner[2]*9,corner[1]);
            }
            betaLabel(box,title,0,12,929,36,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",7);
            betaLabel(box,line,0,88,929,20,0xF2F0EA,BetaGwentFonts.BODY,false,"center");
            if(animate&&!reducedMotion){
                animations.push({sprite:root,fromX:0,fromY:0,toX:0,toY:0,appear:true,remove:false,duration:380});root.alpha=0;
            }
        }
        private function drawYourTurnBanner():void
        {
            var b:Sprite=new Sprite();b.x=960;b.y=520;b.mouseEnabled=false;b.mouseChildren=false;betaOverlay.addChild(b);
            paintArt(b,BetaGwentHud104.TURN_LEFT,145,75,-371,-46);
            paintArt(b,BetaGwentHud104.TURN_RIGHT,145,75,226,-46);
            paintArt(b,BetaGwentHud104.TURN_BG,522,128,-261,-64);
            betaLabel(b,"ВАШ ХОД!",-261,-26,522,38,0xFFFFFF,BetaGwentFonts.TITLE,true,"center",5);
        }
        private function animateBetaOverlay(e:Event):void
        {
            var now:int=getTimer();
            if(turnBannerAt>0){
                var t:int=now-turnBannerAt;
                if(t>1800||skin!=3){turnBannerAt=0;while(betaOverlay.numChildren)betaOverlay.removeChildAt(0);}
                else{
                    if(!betaOverlay.numChildren)drawYourTurnBanner();
                    betaOverlay.alpha=t<220?t/220:t>1450?Math.max(0,(1800-t)/350):1;
                    var b:Sprite=betaOverlay.getChildAt(0) as Sprite;var s:Number=t<220?(0.8+0.2*t/220):1;b.scaleX=b.scaleY=s;
                }
            }
            if(passHoldStart>0&&passRing){
                var p:Number=Math.min(1,(now-passHoldStart)/PASS_HOLD_MS);var r:Number=72;
                passRing.graphics.clear();passRing.graphics.lineStyle(6,0xEAD7A0,.95);
                var steps:int=Math.max(2,Math.round(48*p));
                passRing.graphics.moveTo(0,-r);
                for(var i:int=1;i<=steps;i++){var a:Number=-Math.PI/2+Math.PI*2*p*i/steps;passRing.graphics.lineTo(Math.cos(a)*r,Math.sin(a)*r);}
                if(p>=1){cancelPassHold();if(canAct())submitBoard("OnBetaGwentBoardPass",[revision]);}
            }
        }
'''

def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
    if MARK in t: raise SystemExit('stage104 HUD already applied')
    def rep(a, b, n=1):
        nonlocal t
        if t.count(a) != n: raise SystemExit('anchor %d != %d: %r' % (t.count(a), n, a[:90]))
        t = t.replace(a, b)
    rep('    import flash.geom.Rectangle;\n', '    import flash.geom.Rectangle;\n    import flash.geom.Matrix;\n    import flash.display.GradientType;\n')
    rep('        private function betaLeaderRect(side:int):Array', METHODS.lstrip('\n') + '        private function betaLeaderRect(side:int):Array')
    # layers / frame hooks
    rep('addChild(background); addChild(content);addChild(aimLayer);', 'addChild(background); addChild(content);addChild(aimLayer);addChild(betaOverlay);betaOverlay.mouseEnabled=false;betaOverlay.mouseChildren=false;')
    rep('            addEventListener(Event.ENTER_FRAME,animateReplay);\n', '            addEventListener(Event.ENTER_FRAME,animateReplay);\n            addEventListener(Event.ENTER_FRAME,animateBetaOverlay);\n')
    rep('            activeCue=frame.cue;playing=replayFrames.length>0;ready=true;\n',
        '            activeCue=frame.cue;playing=replayFrames.length>0;ready=true;\n'
        '            if(skin==3&&current==1&&previousTurn!=1&&requestKind!=1&&(flags>>4)==0&&activeCue.kind!=6)turnBannerAt=getTimer();\n'
        '            previousTurn=current;\n')
    # render(): status line, side panel, actions
    rep('            text(content,"Раунд "+round+"  ·  "+', '            if(skin!=3)text(content,"Раунд "+round+"  ·  "+')
    rep('            animateWeather(null);drawBacks();drawVisualCue();\n', '            animateWeather(null);drawBacks();if(skin==3)drawBetaPassStrips();drawVisualCue();\n')
    a = '            var panelTop:Number=skin==3?162:130;\n'
    b = '            if(skin!=3)text(content,"P — пас · L — лидер · D — колода\\nG / H — сброс · ПКМ / X — карта",1532,978,312,17,0xB9B4A9).height=54;\n'
    i, j = t.index(a), t.index(b) + len(b)
    block = t[i:j]
    t = t[:i] + ('            if(skin==3){\n'
                 '                battlePreview=new Sprite();battlePreview.mouseEnabled=false;battlePreview.mouseChildren=false;content.addChild(battlePreview);\n'
                 '                inspection=new TextField();drawBetaActions();\n'
                 '            }else{\n' + block + '            }\n') + t[j:]
    # side preview
    rep('            while(battlePreview.numChildren)battlePreview.removeChildAt(0);\n            paintArt(battlePreview,-1250-',
        '            while(battlePreview.numChildren)battlePreview.removeChildAt(0);\n            if(skin==3){drawBetaSidePreview(c,detail);return;}\n            paintArt(battlePreview,-1250-')
    rep('glow.alpha=0;hoverCardId=0;hoveredCard=null;hoveredDetail=null;hoverPreviewAt=0;updateFocusedInspection();',
        'glow.alpha=0;hoverCardId=0;hoveredCard=null;hoveredDetail=null;hoverPreviewAt=0;if(skin==3&&keyboardFocusId==0&&selected==0)clearBattlePreview();updateFocusedInspection();')
    # HUD: glow first, profile, counters, menu, coin
    rep('            // Positions: BetaGwentBoardLayout (original level8 PlayerRibbon,\n',
        '            drawBetaTurnGlow();\n            // Positions: BetaGwentBoardLayout (original level8 PlayerRibbon,\n')
    rep('''                text(content,side==1?"Геральт":"Соперник",40,side==1?ribbon[1]+ribbon[3]+4:ribbon[1]-30,210,24,side==1?0x7ACAE4:0xEAA18B).height=40;
                if((flags&(side==1?1:2))!=0)text(content,"ПАС",262,side==1?ribbon[1]+ribbon[3]+4:ribbon[1]-30,150,24,0xEBD797).height=34;
''', '                drawBetaProfile(side);\n')
    a = '                var icon:Array=BetaGwentBoardLayout.handCounter[key];\n'
    b = 'handText.setTextFormat(handText.defaultTextFormat);}\n'
    i, j = t.index(a), t.index(b, t.index(a)) + len(b)
    t = t[:i] + ('                drawBetaCounter(-1522,count,456,side);\n'
                 '                drawBetaCounter(-1520,graves[side-1],1533,side);\n'
                 '                drawBetaCounter(-1521,deckCounts[side-1],1877,side);\n') + t[j:]
    rep('            text(content,"P · пас   L · лидер\\nD · колода   G / H · сброс",40,868,330,16,0xBEB7A4).height=56;\n',
        '            drawBetaCoinControls(coin,coinBox);drawBetaMenuButton();\n')
    # piles: counters moved to the HUD; empty graveyard shows the neutral back
    rep('            paintCardBack(pile,cw,ch,side);\n            var top:Object=null;',
        '            if(zone==32&&skin==3){paintArt(pile,BetaGwentHud104.cardBack(5),cw,ch,0,0);pile.alpha=.85;}else paintCardBack(pile,cw,ch,side);\n            var top:Object=null;')
    rep('            paintArt(pile,zone==32?-1520:-1521,32,32,cw-34,ch-36);\n            var pileCount:TextField',
        '            if(skin!=3)paintArt(pile,zone==32?-1520:-1521,32,32,cw-34,ch-36);\n            var pileCount:TextField')
    rep('if(skin!=3||!BetaGwentFonts.apply(pileCount,BetaGwentFonts.NUMBERS,28,0xFFFFFF,true,"center"))',
        'if(skin==3)pileCount.visible=false;else if(!BetaGwentFonts.apply(pileCount,BetaGwentFonts.NUMBERS,28,0xFFFFFF,true,"center"))')
    rep('            if(count==0)pile.alpha=.45;\n', '            if(count==0&&!(skin==3&&zone==32))pile.alpha=.45;\n')
    # card backs
    rep('            if(skin==3&&paintArt(parent,-1510,w,h,0,0)){\n                paintArt(parent,-1501-editorFactionIndex(cardFaction(int(leaderIds[side-1]))),w*.42,w*.42,w*.29,h*.36);\n                return;\n            }\n',
        '            if(skin==3&&paintArt(parent,BetaGwentHud104.cardBack(sideFaction(side)),w,h,0,0))return;\n')
    # opponent hand: full-size backs in the original strip (648..1430, y 8..124)
    rep('''            var spacing:Number=Math.min(54,(skin==3?740:750)/Math.max(1,count));
            var backWidth:Number=Math.min(46,Math.max(8,spacing-4));
            var backsLeft:Number=skin==3?1039.4-(spacing*Math.max(0,count-1)+backWidth)/2:630,backsTop:Number=skin==3?24:96;''',
        '''            var backHeight:Number=skin==3?116:68;
            var backWidth:Number=skin==3?Math.round(116*BETA_CARD_ASPECT):46;
            var spacing:Number=skin==3?Math.min(backWidth+2,(782-backWidth)/Math.max(1,count-1)):Math.min(54,750/Math.max(1,count));
            if(skin!=3)backWidth=Math.min(46,Math.max(8,spacing-4));
            var backsLeft:Number=skin==3?1039-(spacing*Math.max(0,count-1)+backWidth)/2:630,backsTop:Number=skin==3?8:96;''')
    rep('                if(exposed){paintChoiceArt(back,exposed.templateId,backWidth,68);if(backWidth>=24)text(back,String(exposed.power),2,2,backWidth-4,14,powerColor(exposed));back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,68);}\n                else paintCardBack(back,backWidth,68,2);',
        '                if(exposed&&skin==3){paintBetaFace(back,exposed.templateId,backWidth,backHeight,2);betaPowerField(back,String(exposed.power),backWidth,backHeight,powerColor(exposed));back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,backHeight);}\n'
        '                else if(exposed){paintChoiceArt(back,exposed.templateId,backWidth,68);if(backWidth>=24)text(back,String(exposed.power),2,2,backWidth-4,14,powerColor(exposed));back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,68);}\n'
        '                else paintCardBack(back,backWidth,backHeight,2);')
    # cues: no caption strip / round-start plate on the Beta board; Beta round window
    rep('            else if(activeCue.kind==7){\n                var startBanner', '            else if(activeCue.kind==7&&skin!=3){\n                var startBanner')
    rep('''            }else{
                var strip:Sprite=panel(fx,610,160,820,46,0x101619,.94);''', '''            }else if(skin!=3){
                var strip:Sprite=panel(fx,610,160,820,46,0x101619,.94);''')
    rep('            var result:Object=lastRoundResult;if(!result)return;\n            var matchWinner:int=int(result.flags)>>4;\n            var winner:int=matchWinner>0?matchWinner:result.scores[0]>result.scores[1]?1:result.scores[0]<result.scores[1]?2:3;\n            var title:String=winner==3?"НИЧЬЯ"',
        '            if(skin==3){drawBetaRoundBanner(parent,animate);return;}\n            var result:Object=lastRoundResult;if(!result)return;\n            var matchWinner:int=int(result.flags)>>4;\n            var winner:int=matchWinner>0?matchWinner:result.scores[0]>result.scores[1]?1:result.scores[0]<result.scores[1]?2:3;\n            var title:String=winner==3?"НИЧЬЯ"')
    # controller menu: rematch is no longer on the board
    rep('            editorSmallButton(box,"Завершить партию…",28,486,584,58,true,requestBoardClose);\n',
        '            editorSmallButton(box,"Завершить партию…",28,486,584,58,true,requestBoardClose);\n'
        '            if(skin==3)editorSmallButton(box,"Пропустить анимацию",28,554,584,58,playing,function():void{closeControllerMenu();skipReplay();});\n')
    t = t.replace('        private var betaOverlay:Sprite', '        ' + MARK + '\n        private var betaOverlay:Sprite', 1)
    if crlf: t = t.replace('\n', '\r\n')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))
    print('stage104 HUD applied')


if __name__ == '__main__':
    main()

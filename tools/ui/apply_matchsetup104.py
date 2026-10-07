"""Stage 104: Gwent Beta match setup (UIMatchSetupPrefab) + deck picker (DeckPickerPrefab) for skin 3.

Usage: apply_matchsetup104.py [BetaGwentBoard.as]
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
MARK = '// stage104-matchsetup'
METHODS = r'''
        // stage104-matchsetup: UIMatchSetupPrefab (title plaque, deck list, leader frame,
        // НАЧАТЬ БОЙ, side preview) and DeckPickerPrefab/DeckList (ЗАМЕНИТЬ КОЛОДУ).
        private var pickerSide:int=0;
        private var deckListScroll:int=0;
        private function tierFrame(tier:int):int
        { return tier==8||tier==1?BetaGwentDeckArt104.DP_GOLD:tier==4?BetaGwentDeckArt104.DP_SILVER:BetaGwentDeckArt104.DP_BRONZE; }
        private function betaPlaque(title:String):void
        {
            paintArt(content,BetaGwentHud104.CHAIN,14,60,650,-6);paintArt(content,BetaGwentHud104.CHAIN,14,60,1256,-6);
            betaNine(content,-1400,690,74,615,30);
            betaLabel(content,title.toUpperCase(),615,46,690,30,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",6).mouseEnabled=false;
        }
        private function deckSlotRow(parent:Sprite,c:Object,x:Number,y:Number,w:Number,h:Number,leader:Boolean=false):Sprite
        {
            var row:Sprite=new Sprite();row.x=x;row.y=y;parent.addChild(row);
            row.graphics.beginFill(0x0C0C0C,1);row.graphics.drawRect(2,2,w-4,h-4);row.graphics.endFill();
            var art:int=BetaGwentDeckArt104.slot(c.templateId);
            var artW:Number=leader?w*.72:w*.62;
            if(art!=0)paintArt(row,art,artW,h-6,w-artW-3,3);
            var shade:Sprite=new Sprite();row.addChild(shade);var m:Matrix=new Matrix();m.createGradientBox(artW,h,0,w-artW-3,0);
            shade.graphics.beginGradientFill(GradientType.LINEAR,[0x0C0C0C,0x0C0C0C],[1,0],[0,200],m);shade.graphics.drawRect(w-artW-3,3,artW,h-6);shade.graphics.endFill();
            paintArt(row,tierFrame(int(c.tier)),w,h,0,0);
            var unit:Boolean=int(c.typeMask)==4||leader;
            if(leader){
                paintArt(row,BetaGwentDeckArt104.DP_DIAMOND,h*.92,h*.92,4,h*.04);
                paintArt(row,BetaGwentDeckArt104.DP_CROWN,h*.34,h*.34,4+h*.29,h*.06);
                betaLabel(row,String(c.power),4,h*.36,h*.92,h*.36,0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");
            }else if(unit)betaLabel(row,String(c.power),6,(h-h*.62*1.5)/2+2,32,h*.62,0xF2EEE4,BetaGwentFonts.NUMBERS,false,"center");
            else paintArt(row,int(c.tier)==8?BetaGwentDeckArt104.DP_SPECIAL_GOLD:int(c.tier)==4?BetaGwentDeckArt104.DP_SPECIAL_SILVER:BetaGwentDeckArt104.DP_SPECIAL_BRONZE,h*.55,h*.55,10,h*.22);
            var nameX:Number=leader?h+8:42;
            var name:TextField=betaLabel(row,String(c.title).toUpperCase(),nameX,(h-27)/2,w-nameX-46,leader?19:16,0xF2EEE4,leader?BetaGwentFonts.TITLE:BetaGwentFonts.BODY,leader,null,1.5);
            name.filters=[new GlowFilter(0,1,4,4,4,1)];
            if(int(c.copies)>1){
                paintArt(row,BetaGwentDeckArt104.DP_COPIES,h-12,h-12,w-h+6,6);
                betaLabel(row,"x"+int(c.copies),w-h+6,(h-26)/2,h-12,16,0xF2EEE4,BetaGwentFonts.BODY,false,"center");
            }
            return row;
        }
        private function drawBetaDeckList(viewed:Object,side:int):void
        {
            var fi:int=editorFactionIndex(cardFaction(viewed.leaderId));
            paintArt(content,BetaGwentHud104.WOOD_PANEL,415,840,30,135);
            paintArt(content,BetaGwentDeckArt104.stats(Math.min(4,fi)),371,108,52,150);
            var golds:int=0,silvers:int=0,bronzes:int=0,total:int=0;
            for each(var c:Object in viewed.cards){var n:int=int(c.copies);total+=n;if(c.tier==8)golds+=n;else if(c.tier==4)silvers+=n;else if(c.tier==2)bronzes+=n;}
            var counters:Array=[[BetaGwentDeckArt104.DP_STAT_GOLD,golds+"/4",0xF6D36B],[BetaGwentDeckArt104.DP_STAT_SILVER,silvers+"/6",0xE6E6E6],[BetaGwentDeckArt104.DP_STAT_BRONZE,String(bronzes),0xE0B07A]];
            for(var k:int=0;k<3;k++){
                paintArt(content,counters[k][0],46,54,152+k*62,158);
                betaLabel(content,counters[k][1],148+k*62,170,54,18,counters[k][2],BetaGwentFonts.BODY,false,"center");
            }
            betaLabel(content,"КАРТЫ: "+total,52,222,371,18,0xF2EEE4,BetaGwentFonts.BODY,false,"center",1);
            var leader:Object=leaderOption(chosenLeaders[side-1]);
            var leaderCard:Object={templateId:chosenLeaders[side-1],title:leader?leader.title:viewed.leader,power:leader?leader.power:0,tier:1,typeMask:4,copies:1,side:side,description:leader?leader.description:""};
            var lrow:Sprite=deckSlotRow(content,leaderCard,46,262,372,60,true);
            attachInspect(lrow,leaderCard,{description:leaderCard.description},372,60);
            var sorted:Array=viewed.cards.concat();
            sorted.sort(function(a:Object,b:Object):Number{return b.tier!=a.tier?b.tier-a.tier:(int(b.typeMask==4)*b.power)-(int(a.typeMask==4)*a.power);});
            var visible:int=15;deckListScroll=Math.max(0,Math.min(deckListScroll,sorted.length-visible));
            var list:Sprite=new Sprite();content.addChild(list);
            list.graphics.beginFill(0,0);list.graphics.drawRect(46,328,372,visible*40);list.graphics.endFill();
            for(var i:int=deckListScroll;i<Math.min(sorted.length,deckListScroll+visible);i++){
                var card:Object=sorted[i];card.side=side;
                var r:Sprite=deckSlotRow(list,card,46,328+(i-deckListScroll)*40,372,38);
                attachInspect(r,card,{description:card.description},372,38);
            }
            list.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();deckListScroll=Math.max(0,deckListScroll+(e.delta<0?2:-2));render();});
            if(deckListScroll>0)betaLabel(content,"▲",410,316,20,14,0xCFC8BA,BetaGwentFonts.BODY);
            if(deckListScroll+visible<sorted.length)betaLabel(content,"▼",410,928,20,14,0xCFC8BA,BetaGwentFonts.BODY);
        }
        private function drawBetaDeckPicker():void
        {
            paintArt(content,BetaGwentHud104.WOOD_PANEL,415,840,30,135);
            betaLabel(content,pickerSide==1?"ВАША КОЛОДА":"КОЛОДА СОПЕРНИКА",52,150,371,20,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",3);
            var savedCount:int=0;for each(var saved:Object in deckOptions)if(saved.id>=1001)savedCount++;
            var y:Number=190;
            if(pickerSide==1&&savedCount<8){
                var nd:Sprite=new Sprite();nd.x=46;nd.y=y;content.addChild(nd);
                paintArt(nd,BetaGwentDeckArt104.DP_NEWDECK,372,62,0,0);paintArt(nd,BetaGwentDeckArt104.DP_NEWDECK_ICON,34,34,18,14);
                betaLabel(nd,"НОВАЯ КОЛОДА",62,18,290,18,0xF2EEE4,BetaGwentFonts.TITLE,true,null,2);
                attachEditorClick(nd,openEditorAction(0));controller.registerControl(nd,"Новая колода",openEditorAction(0),null,null,"control",null,new Rectangle(0,0,372,62));
                y+=70;
            }
            var perPage:int=Math.floor((960-y)/78);var pages:int=Math.max(1,Math.ceil(deckOptions.length/perPage));presetPage=Math.min(presetPage,pages-1);
            for(var i:int=presetPage*perPage;i<Math.min(deckOptions.length,(presetPage+1)*perPage);i++){
                var option:Object=deckOptions[i];
                var allowed:Boolean=pickerSide==2||entryMode!=2||forcedFaction==0||cardFaction(option.leaderId)==forcedFaction;
                var b:Sprite=new Sprite();b.x=46;b.y=y+(i-presetPage*perPage)*78;content.addChild(b);b.alpha=allowed?1:.45;
                b.graphics.beginFill(0x0C0C0C,1);b.graphics.drawRect(2,2,368,68);b.graphics.endFill();
                var art:int=BetaGwentDeckArt104.slot(option.leaderId);if(art!=0)paintArt(b,art,240,64,128,4);
                var sm:Matrix=new Matrix();sm.createGradientBox(240,72,0,128,0);
                b.graphics.beginGradientFill(GradientType.LINEAR,[0x0C0C0C,0x0C0C0C],[1,0],[0,200],sm);b.graphics.drawRect(128,4,240,64);b.graphics.endFill();
                paintArt(b,BetaGwentDeckArt104.DP_GOLD,372,72,0,0);
                paintArt(b,BetaGwentDeckArt104.ornament(Math.min(4,editorFactionIndex(cardFaction(option.leaderId)))),62,62,-12,5);
                betaLabel(b,String(option.title).toUpperCase(),70,12,290,18,0xF2EEE4,BetaGwentFonts.TITLE,true,null,1.5).filters=[new GlowFilter(0,1,4,4,4,1)];
                betaLabel(b,String(option.leader),70,40,290,16,0xD8D2C4,BetaGwentFonts.BODY).filters=[new GlowFilter(0,1,4,4,4,1)];
                var current:Boolean=option.id==(pickerSide==1?ownPreset:enemyPreset);
                if(current)b.filters=[new GlowFilter(0x34C6FF,1,14,14,3,2)];
                if(allowed){
                    var pick:Function=pickDeck(option.id);
                    attachEditorClick(b,pick);controller.registerControl(b,option.title,pick,null,null,"control",null,new Rectangle(0,0,372,72));
                }
            }
            if(pages>1){
                betaWideButton("‹",52,914,70,ready&&presetPage>0,function():void{presetPage--;render();});
                betaWideButton("›",340,914,70,ready&&presetPage+1<pages,function():void{presetPage++;render();});
            }
        }
        private function pickDeck(id:int):Function
        {
            var side:int=pickerSide;var select:Function=selectDeckAction(side,id);
            return function():void{pickerSide=0;deckListScroll=0;select();};
        }
        private function drawBetaMatchSetup():void
        {
            paintArt(content,BetaGwentDeckArt104.BG_SETUP,1920,1080,0,0);
            betaPlaque(entryMode==2?(npcDeckLabel&&npcDeckLabel.length?npcDeckLabel:"Бой"):entryMode==1?"Колоды":"Тренировка");
            var viewed:Object=deckOption(ownPreset);
            if(pickerSide>0)drawBetaDeckPicker();
            else if(viewed)drawBetaDeckList(viewed,1);
            else betaLabel(content,"Получаю составы колод…",52,180,371,18,0xF2EEE4,BetaGwentFonts.BODY,false,"center");
            // centre: parchment, status ribbon, leader frame, НАЧАТЬ БОЙ
            content.graphics.beginFill(0x0D0F10,.97);content.graphics.drawRect(455,135,1007,840);content.graphics.endFill();
            content.graphics.lineStyle(3,0x4A4D4F,1);content.graphics.drawRect(455,135,1007,840);content.graphics.lineStyle();
            paintArt(content,BetaGwentHud104.PARCHMENT,967,800,475,155);
            var fi:int=editorFactionIndex(cardFaction(chosenLeaders[0]));
            var first:Object=deckOption(ownPreset);var second:Object=deckOption(enemyPreset);
            var canStart:Boolean=ready&&first!=null&&(entryMode==2||second!=null);
            paintArt(content,BetaGwentHud104.titleBg(fi),640,72,639,222);
            content.graphics.lineStyle(3,0x2A2A2A,1);content.graphics.drawRect(639,222,640,72);content.graphics.lineStyle();
            betaLabel(content,entryMode==1?"ВАШИ КОЛОДЫ":canStart?"МОЖНО НАЧИНАТЬ!":"ВЫБЕРИТЕ КОЛОДУ",639,244,640,22,0xF2EEE4,BetaGwentFonts.BODY,false,"center",1);
            var frame:Sprite=new Sprite();frame.x=629;frame.y=350;content.addChild(frame);
            var size:Array=BetaGwentHDArt.size(chosenLeaders[0]);
            if(size){
                var sw:Number=size[0],sh:Number=size[1];var cw:Number=sw,ch:Number=Math.min(sh,sw*440/625);
                var leaderArt:Sprite=BetaGwentHDArt.clip(chosenLeaders[0],625,440,0,(sh-ch)*.2,cw,ch);
                if(leaderArt){leaderArt.x=18;leaderArt.y=18;frame.addChild(leaderArt);}
            }
            betaNine(frame,BetaGwentDeckArt104.MS_FRAME,661,475);
            var leader:Object=leaderOption(chosenLeaders[0]);
            var tag:Sprite=new Sprite();tag.x=780;tag.y=322;content.addChild(tag);
            paintArt(tag,BetaGwentDeckArt104.MS_NAME_BG,358,61,0,0);paintArt(tag,-1501-Math.min(4,fi),34,34,24,13);
            betaLabel(tag,leader?leader.title:(first?first.leader:""),62,16,268,18,0xF2EEE4,BetaGwentFonts.BODY);
            var sideLeaders:Array=leadersForFaction(cardFaction(chosenLeaders[0]));
            if(sideLeaders.length>1&&pickerSide==0){
                var at:int=0;for(var li:int=0;li<sideLeaders.length;li++)if(sideLeaders[li].id==chosenLeaders[0])at=li;
                betaWideButton("‹",700,326,56,ready,selectLeaderAction(1,sideLeaders[(at+sideLeaders.length-1)%sideLeaders.length].id));
                betaWideButton("›",1162,326,56,ready,selectLeaderAction(1,sideLeaders[(at+1)%sideLeaders.length].id));
            }
            var corner:Sprite=new Sprite();corner.x=594;corner.y=650;content.addChild(corner);paintArt(corner,BetaGwentDeckArt104.MS_CORNERS,144,176,0,0);
            var corner2:Sprite=new Sprite();corner2.x=1324;corner2.y=650;corner2.scaleX=-1;content.addChild(corner2);paintArt(corner2,BetaGwentDeckArt104.MS_CORNERS,144,176,0,0);
            if(entryMode!=1){
                paintArt(content,BetaGwentDeckArt104.MS_BUTTON_BG,415,151,752,734);
                var start:Sprite=new Sprite();start.x=831;start.y=780;content.addChild(start);start.alpha=canStart?1:.55;
                paintArt(start,BetaGwentDeckArt104.MS_BUTTON,256,60,0,0);
                var hover:Sprite=new Sprite();hover.mouseEnabled=false;paintArt(hover,BetaGwentDeckArt104.MS_BUTTON_HOVER,256,60,0,0);hover.alpha=0;start.addChild(hover);
                betaLabel(start,"НАЧАТЬ БОЙ",0,15,256,22,0x2A1A06,BetaGwentFonts.TITLE,true,"center",2).mouseEnabled=false;
                if(canStart){
                    var go:Function=function():void{if(!ready||!selectingDecks)return;var expected:int=revision;ready=false;send("OnBetaGwentDeckStart",[expected]);};
                    start.buttonMode=true;start.mouseChildren=false;
                    start.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{hover.alpha=1;});
                    start.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{hover.alpha=0;});
                    start.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();go();});
                    controller.registerControl(start,"Начать бой",go,null,null,"control",null,new Rectangle(0,0,256,60));
                }
            }
            if(entryMode==0){
                betaLabel(content,"Соперник: "+(second?second.title+" · "+second.leader:"—"),500,912,620,18,0x3A2A16,BetaGwentFonts.BODY);
                betaWideButton("Сменить",1150,904,200,ready,function():void{pickerSide=pickerSide==2?0:2;presetPage=0;render();});
            }else if(entryMode==2)betaLabel(content,"Соперник: "+npcDeckLabel+" · выход из боя считается поражением",500,912,900,18,0x3A2A16,BetaGwentFonts.BODY);
            // right: wooden preview panel
            paintArt(content,BetaGwentHud104.WOOD_PANEL,405,822,1477,138);
            paintArt(content,BetaGwentHud104.PREVIEW_SLOT,285,398,1545,177);
            battlePreview=new Sprite();battlePreview.mouseEnabled=false;battlePreview.mouseChildren=false;content.addChild(battlePreview);
            inspection=new TextField();
            if(leader)showBattleCard({templateId:chosenLeaders[0],title:leader.title,power:leader.power,side:1,zone:64,tokens:0,description:leader.description},{description:leader.description});
            // bottom buttons
            var savedCount:int=0;for each(var saved:Object in deckOptions)if(saved.id>=1001)savedCount++;
            betaWideButton(pickerSide==1?"Назад":"Заменить колоду",560,1002,300,ready,function():void{pickerSide=pickerSide==1?0:1;presetPage=0;render();});
            betaWideButton(ownPreset>=1001?"Редактировать":"Копировать",880,1002,260,ready&&(ownPreset>=1001||savedCount<8),openEditorAction(ownPreset));
            betaWideButton("Все карты",1160,1002,200,ready,function():void{browsingCatalog=true;catalogPage=0;render();});
            betaWideButton(entryMode==2?"Отказаться":"Выход",1380,1002,200,connected,requestBoardClose);
            if(entryMode==1&&(pendingKeg||unopenedKegs>0))betaWideButton(pendingKeg?"Бочка: выбор":"Бочки · "+unopenedKegs,1600,1002,260,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});
        }
'''

def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
    if MARK in t: raise SystemExit('already applied')
    def rep(a, b):
        nonlocal t
        if t.count(a) != 1: raise SystemExit('anchor %d: %r' % (t.count(a), a[:90]))
        t = t.replace(a, b)
    rep('        private function drawDeckSelection():void\n        {\n',
        METHODS.lstrip('\n').replace('        // stage104-matchsetup: UI', '        ' + MARK + '\n        // UI') +
        '        private function drawDeckSelection():void\n        {\n            if(skin==3){drawBetaMatchSetup();return;}\n')
    if crlf: t = t.replace('\n', '\r\n')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))
    print('match setup applied to', SRC)

if __name__ == '__main__':
    main()

"""One-time stage93 layout migration from the preserved stage92 AS source."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
path=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'
s=(ROOT/'tmp/presentation93/BetaGwentBoard.before.as').read_text('utf8')
def block(start,end,new):
 global s
 a=s.index(start);b=s.index(end,a);s=s[:a]+new+'\n'+s[b:]
def change(old,new):
 global s
 assert old in s,old[:120];s=s.replace(old,new)

change('private var skin:int=2;','private var skin:int=3;\n        private var battlePreview:Sprite;\n        private var battlePreviewKey:String="";')
block('        private function editorSmallButton(', '        private function attachEditorClick(', '''        private function editorSmallButton(parent:Sprite,title:String,x:Number,y:Number,w:Number,h:Number,enabled:Boolean,callback:Function):void
        {editorBetaButton(parent,title,x,y,w,h,enabled,callback);}
''')
block('        private function editorBetaButton(', '        private function showEditorCard(', '''        private function betaNine(parent:Sprite,id:int,w:Number,h:Number,x:Number=0,y:Number=0):Sprite
        {
            var result:Sprite=new Sprite();result.x=x;result.y=y;parent.addChild(result);
            var size:Array=BetaGwentHDArt.size(id);if(!size)return result;
            var sx:Number=Math.min(24,size[0]/3),sy:Number=Math.min(24,size[1]/3);
            var dx:Number=Math.min(12,w/3),dy:Number=Math.min(12,h/3);
            var sourceX:Array=[0,sx,size[0]-sx],sourceY:Array=[0,sy,size[1]-sy];
            var sourceW:Array=[sx,size[0]-sx*2,sx],sourceH:Array=[sy,size[1]-sy*2,sy];
            var targetX:Array=[0,dx,w-dx],targetY:Array=[0,dy,h-dy];
            var targetW:Array=[dx,w-dx*2,dx],targetH:Array=[dy,h-dy*2,dy];
            for(var row:int=0;row<3;row++)for(var col:int=0;col<3;col++){
                var piece:Sprite=BetaGwentHDArt.clip(id,targetW[col],targetH[row],sourceX[col],sourceY[row],sourceW[col],sourceH[row]);
                if(piece){piece.x=targetX[col];piece.y=targetY[row];result.addChild(piece);}
            }return result;
        }
        private function betaFrame(parent:Sprite,x:Number,y:Number,w:Number,h:Number,id:int=-1414):Sprite
        {
            var p:Sprite=new Sprite();p.x=x;p.y=y;parent.addChild(p);
            p.graphics.beginFill(0,0);p.graphics.drawRect(0,0,w,h);p.graphics.endFill();
            betaNine(p,id,w,h);return p;
        }
        private function editorBetaButton(parent:Sprite,title:String,x:Number,y:Number,w:Number,h:Number,enabled:Boolean,callback:Function,chosen:Boolean=false):Sprite
        {
            var p:Sprite=new Sprite();p.x=x;p.y=y;parent.addChild(p);
            p.graphics.beginFill(0,0);p.graphics.drawRect(0,0,w,h);p.graphics.endFill();
            betaNine(p,enabled?(chosen?-1402:-1400):-1403,w,h);
            var hover:Sprite=betaNine(p,-1401,w,h);hover.alpha=0;
            p.alpha=enabled?1:.5;p.buttonMode=enabled;
            var label:TextField=text(p,title,12,Math.max(3,(h-26)/2),w-24,18,chosen?0xFFE6A0:0xE3D6BE);
            label.multiline=false;label.wordWrap=false;label.height=h-label.y-3;
            if(label.textWidth>w-24)label.setTextFormat(new TextFormat("$NormalFont",Math.max(12,Math.floor(18*(w-24)/label.textWidth)),chosen?0xFFE6A0:0xE3D6BE));
            if(enabled){
                controller.registerControl(p,title,callback);
                p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{hover.alpha=1;});
                p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{hover.alpha=0;});
            }return p;
        }
''')
change('paintArt(editorPreview,c.templateId,216,304,102,80);','paintArt(editorPreview,c.templateId,256,360,82,80);\n            betaNine(editorPreview,-1412,260,364,80,78);')
change('editorPreview.graphics.drawRect(102,80,216,304);','editorPreview.graphics.drawRect(82,80,256,360);')
change('panel(editorPreview,106,84,52,40','panel(editorPreview,86,84,52,40')
change('113,87,44,28','93,87,44,28')
change('16,406,388,20','16,454,388,20')
change('16,442,388,18','16,490,388,18')
change('paintArt(editorPreview,-1270,388,7,16,501);','paintArt(editorPreview,-1270,388,7,16,548);')
change('420,304,0,512);info.alpha=.3','420,260,0,560);info.alpha=.65')
change('description,16,524,388,22','description,16,574,388,22')
change('inspection.height=282;','inspection.height=232;')
change('var tile:Sprite=panel(editorCollection,(n%6)*154,int(n/6)*300,142,239,0x142027,.9);','var tile:Sprite=betaFrame(editorCollection,(n%6)*154,int(n/6)*300,142,239,-1414);')
change('paintArt(tile,c.templateId,134,188,4,4);','paintArt(tile,c.templateId,134,188,4,4);betaNine(tile,-1412,138,192,2,2);')
change('for(var shelf:int=0;shelf<2;shelf++)paintArt(editorCollection,-1210,924,32,0,244+shelf*300);','for(var shelf:int=0;shelf<2;shelf++)for(var beam:int=0;beam<3;beam++)paintArt(editorCollection,-1210,308,48,beam*308,244+shelf*300);')
change('for(var bg:int=0;bg<8;bg++)paintArt(content,-1200-bg,480,540,(bg%4)*480,int(bg/4)*540);','paintArt(content,-1310,1920,1080,0,0);')
change('panel(content,0,0,1920,1080,0x050909,.25);','panel(content,0,0,1920,1080,0x050909,.15);')
change('panel(content,44,88,388,884,0x090E10,.9);','betaFrame(content,44,88,388,884);\n            panel(content,52,96,372,868,0x090A0A,.45);')
change('panel(content,1440,88,436,930,0x090E10,.9);','betaFrame(content,1440,88,436,930);\n            panel(content,1448,96,420,914,0x090A0A,.5);')
change('paintArt(content,-1211,20,880,436,88);paintArt(content,-1211,20,930,1412,88);','for(var post:int=0;post<3;post++){paintArt(content,-1211,38,294,426,88+post*294);paintArt(content,-1211,38,294,1398,88+post*294);}\n            paintArt(content,-1420-editorFactionIndex(editorState.faction),388,122,44,210);')
change('var field:TextField=text(content,value,x,y,w,24);','betaNine(content,-1410,w,40,x,y);\n            var field:TextField=text(content,value,x+12,y+3,w-24,24);')
change('field.background=true;field.backgroundColor=0x192A31;field.border=true;field.borderColor=0xA48A60;','field.background=false;field.border=false;')
block('        private function changeSkin(', '        private function text(', '''        private function changeSkin(value:int):void
        {
            skin=value;
            while(background.numChildren)background.removeChildAt(0);
            if(skin==3){paintArt(background,-1311,2160,1080,-120,0);return;}
            var bitmap:Bitmap=(skin==1?new ClassicBoard():new WideBoard()) as Bitmap;
            bitmap.smoothing=true;bitmap.width=1920;bitmap.height=1920*bitmap.bitmapData.height/bitmap.bitmapData.width;
            bitmap.y=(1080-bitmap.height)/2;background.addChild(bitmap);
        }
''')
block('        private function button(', '        private function rowGeometry(', '''        private function button(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function,parent:Sprite=null):TextField
        {
            var p:Sprite=editorBetaButton(parent||content,title,x,y,w,48,enabled,callback);
            return p.getChildAt(p.numChildren-1) as TextField;
        }
''')
change('var top:Number=skin==1?', 'if(skin==3)return {x:437,y:(side==1?584:218)+ordinal*104,w:754,h:96};\n            var top:Number=skin==1?')
marker='        private function canAct():Boolean'
change(marker,'''        private function rowLayout(side:int,zone:int,extra:int=0):Object
        {
            var g:Object=rowGeometry(side,zone);var count:int=extra;
            for each(var unit:Object in cards)if(unit.side==side&&unit.zone==zone)count++;
            var step:Number=Math.min((g.h-8)*256/360+8,(g.w-24)/Math.max(1,count));
            return {x:g.x+(g.w-Math.max(1,count)*step+8)/2,step:step,w:step-8};
        }
'''+marker)
change('var g:Object=rowGeometry(c.side,c.zone);\n                return {anchor:id,index:c.index,target:0,side:c.side,zone:c.zone,x:g.x+12+c.index*88,y:g.y,w:80,h:g.h};','var g:Object=rowGeometry(c.side,c.zone);var layout:Object=rowLayout(c.side,c.zone,1);\n                return {anchor:id,index:c.index,target:0,side:c.side,zone:c.zone,x:layout.x+c.index*layout.step,y:g.y,w:layout.w,h:g.h};')
change('units.sortOn("index",Array.NUMERIC);\n            for(var i:int=0;i<=units.length;i++){','units.sortOn("index",Array.NUMERIC);var layout:Object=rowLayout(side,zone,1);\n            for(var i:int=0;i<=units.length;i++){')
change('x:g.x+12+i*88,y:g.y,w:80,h:g.h','x:layout.x+i*layout.step,y:g.y,w:layout.w,h:g.h')
change('units.sortOn("index",Array.NUMERIC);\n            for each(c in units)if(mouseX<g.x+12+c.index*88+40)return {anchor:c.id,index:c.index,target:0,side:side,zone:zone,x:g.x+12+c.index*88,y:g.y,w:80,h:g.h};\n            return {anchor:0,index:units.length,target:0,side:side,zone:zone,x:g.x+12+units.length*88,y:g.y,w:80,h:g.h};','units.sortOn("index",Array.NUMERIC);var layout:Object=rowLayout(side,zone);var pending:Object=rowLayout(side,zone,1);\n            for each(c in units)if(mouseX<layout.x+c.index*layout.step+layout.w/2)return {anchor:c.id,index:c.index,target:0,side:side,zone:zone,x:pending.x+c.index*pending.step,y:g.y,w:pending.w,h:g.h};\n            return {anchor:0,index:units.length,target:0,side:side,zone:zone,x:pending.x+units.length*pending.step,y:g.y,w:pending.w,h:g.h};')
change('var step:Number=Math.min(88,(g.w-24)/(units.length+1));var width:Number=step-8;','var layout:Object=rowLayout(target.side,target.zone,1);var step:Number=layout.step;var width:Number=layout.w;')
change('g.x+12+(unit.index>=index?unit.index+1:unit.index)*step','layout.x+(unit.index>=index?unit.index+1:unit.index)*step')
change('var x:Number=g.x+12+index*step;','var x:Number=layout.x+index*step;')
change('var x:Number=isHand?g.x:g.x+12+c.index*88;\n                var p:Sprite=panel(content,x,g.y+4,isHand?handWidth:80,isHand?140:g.h-8,c.side==1?0x173340:0x4B2925,.96);','var layout:Object=isHand?null:rowLayout(c.side,c.zone);\n                var x:Number=isHand?g.x:layout.x+c.index*layout.step;\n                var cardWidth:Number=isHand?handWidth:layout.w;var cardHeight:Number=isHand?140:g.h-8;\n                var p:Sprite=panel(content,x,g.y+4,cardWidth,cardHeight,0x171714,.96);')
change('var cardWidth:Number=isHand?handWidth:80;\n                var cardHeight:Number=isHand?140:g.h-8;','')
change('flash.graphics.drawRect(0,0,isHand?handWidth:80,isHand?140:g.h-8);','flash.graphics.drawRect(0,0,cardWidth,cardHeight);')
change('clearPlacementGhost();previousPoses=displayedCards;','clearPlacementGhost();previousPoses=displayedCards;\n            battlePreview=null;battlePreviewKey="";tempoLabel=null;motionLabel=null;')
change('panel(content,16,12,1888,64,0x111315,.92);','betaNine(content,-1400,1888,54,16,12);')
change('"Дуэль · карты Beta 0.9.24 · поле DIY"','skin==3?"Дуэль · карты Beta 0.9.24 · поле Beta":"Дуэль · карты Beta 0.9.24 · поле DIY"')
change('profile(2,100,225,0x532723); profile(1,100,575,0x193E53);','profile(2,96,226,0x532723);profile(1,96,588,0x193E53);')
a=s.index('            panel(content,1510,190,360,720');b=s.index('            if(!playing&&requestId>0 && requestKind==1)',a)
old=s[a:b]
# Preserve all authoritative primary-action guards and callbacks.
primary=old[old.index('            if(playing)'):old.index('            button((flags&4)')]
primary=primary.replace('1532,450','1532,790').replace('1532,460','1532,802')
new='''            betaFrame(content,1504,130,368,538);
            panel(content,1512,138,352,522,0x070908,.55);
            battlePreview=new Sprite();battlePreview.x=1516;battlePreview.y=140;content.addChild(battlePreview);
            inspection=text(content,"Наведите на карту.\\nI или Shift + клик — полное описание.",1532,520,312,19,0xD8D0BB);inspection.height=134;
            inspection.mouseEnabled=true;
            inspection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();inspection.scrollV=Math.max(1,Math.min(inspection.maxScrollV,inspection.scrollV-e.delta*3));});
            var statusText:TextField=text(content,isCaranthirChoice()?"Мороз попадёт в ряд напротив Карантира. Можно переместить подсвеченный отряд или подтвердить этот ряд без перемещения. LB / RB — выбрать ряд.":requestId>0?requestMessage:message,1532,684,312,20);
            statusText.height=96;
'''+primary+'''            button("Меню партии",1532,850,312,true,openControllerMenu);
            button("Повторить",1532,912,150,ready&&entryMode!=2,function():void{submitBoard("OnBetaGwentBoardRematch",[serverRevision]);});
            button(entryMode==2&&(flags>>4)==0?"Сдаться":"Закрыть",1694,912,150,connected,function():void{send("OnBetaGwentBoardClose",[]);});
            text(content,"P — пас · L — лидер · D — колода\\nG / H — сброс · ПКМ / X — карта",1532,978,312,17,0xB9B4A9).height=54;
'''
s=s[:a]+new+s[b:]
change('panel(content,484,176,976,43,0x10191F,.97);\n                text(content,requestInstruction(),498,180,946,22,0xF5D77F).height=36;','betaNine(content,-1400,976,43,430,158);\n                text(content,requestInstruction(),446,164,944,22,0xF5D77F).height=34;')
block('        private function drawFactionBoards():void','        private function betaVisual(','''        private function drawFactionBoards():void
        {
            for(var side:int=1;side<=2;side++){
                var faction:int=cardFaction(int(leaderIds[side-1]));
                var number:int=faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:-1;
                if(number<0){var option:Object=deckOption(side==1?ownPreset:enemyPreset);if(option)faction=cardFaction(option.leaderId);number=editorFactionIndex(faction);}
                paintArt(content,-1300-number*2-(side-1),1160,400,312,side==1?554:154);
            }
        }
        private function showBattleCard(c:Object,detail:Object):void
        {
            if(!battlePreview||!c)return;
            var key:String=c.templateId+":"+c.power+":"+c.tokens;
            if(key==battlePreviewKey&&battlePreview.numChildren)return;battlePreviewKey=key;
            while(battlePreview.numChildren)battlePreview.removeChildAt(0);
            paintArt(battlePreview,-1250-editorFactionIndex(cardFaction(c.templateId)),336,50,0,0);
            text(battlePreview,c.title,12,10,312,22,0xF4E1B1).height=40;
            if(c.templateId>0)paintChoiceArt(battlePreview,c.templateId,200,282);else paintCardBack(battlePreview,200,282,2);
            // Isolate the portrait from its faction heading and description.
            var portrait:Sprite=battlePreview.getChildAt(battlePreview.numChildren-1) as Sprite;
            if(portrait){portrait.x=68;portrait.y=62;}
            betaNine(battlePreview,-1412,204,286,66,60);
            text(battlePreview,BetaGwentCardTags.text(c.templateId)||"—",12,352,312,17,0xC9C3A9).height=32;
            if(inspection)inspection.text=cardReading(c,detail);
        }
''')
# portraits use one dedicated holder; paintChoiceArt's source-specific shapes
# must all move together (including the hidden random-unit placeholder).
change('if(c.templateId>0)paintChoiceArt(battlePreview,c.templateId,200,282);else paintCardBack(battlePreview,200,282,2);\n            // Isolate the portrait from its faction heading and description.\n            var portrait:Sprite=battlePreview.getChildAt(battlePreview.numChildren-1) as Sprite;\n            if(portrait){portrait.x=68;portrait.y=62;}','var portrait:Sprite=new Sprite();portrait.x=68;portrait.y=62;battlePreview.addChild(portrait);\n            if(c.templateId>0)paintChoiceArt(portrait,c.templateId,200,282);else paintCardBack(portrait,200,282,2);')
change('var p:Sprite=panel(content,x,y,280,225,color,.88);','var p:Sprite=betaFrame(content,x,y,280,280);\n            panel(p,8,8,264,264,0x070909,.5);\n            paintArt(p,-1420-editorFactionIndex(cardFaction(int(leaderIds[side-1]))),280,66,0,0);')
change('text(p,"Счёт:",18,58,100,34);','text(p,"Счёт:",18,66,140,18);')
change('text(p,String(scores[side-1]),116,58,100,34);','text(p,String(scores[side-1]),18,90,150,52);')
change('fromX:116,fromY:58,toX:116,toY:58','fromX:18,fromY:90,toX:18,toY:90')
change('18,116,172,24','18,156,172,18')
change('seal.y=151','seal.y=190')
change('fromY:151,toX:34+sealIndex*29,toY:151','fromY:190,toX:34+sealIndex*29,toY:190')
change('pile.x=210;pile.y=196','pile.x=223;pile.y=244')
change('paintArt(p,leaderIds[side-1],64,90,198,59);','paintArt(p,leaderIds[side-1],90,126,180,70);betaNine(p,-1412,94,130,178,68);')
change('12,163,180,28','12,207,194,28')
change('12,194,180,27','12,242,194,27')
change('18,194,178,17','18,242,188,17')
change('x,y+245,280','x,y+294,280')
change('geometry.x-150,geometry.y+2,146,13','geometry.x+8,geometry.y+2,geometry.w-16,13')
change('var rowTarget:Sprite=panel(content,hit.x-145,hit.y+hit.height-33,140,30,0x133E50,.96);','var rowTarget:Sprite=betaFrame(content,hit.x+hit.width-184,hit.y+hit.height-31,176,28,-1401);')
change('5,4,130,12','8,3,160,12')
change('var box:Sprite=panel(detailLayer,376,170,1168,740,0x10191F,.99);','var box:Sprite=betaFrame(detailLayer,376,170,1168,740,-1413);\n            panel(box,366,70,774,560,0x080B0C,.8);')
change('if(inspection&&!editingDeck)inspection.text=cardReading(node.card,node.detail);','if(inspection&&!editingDeck)inspection.text=cardReading(node.card,node.detail);showBattleCard(node.card,node.detail);')
change('if(inspection)inspection.text=cardReading(c,detail);\n                while(previewLayer','if(inspection)inspection.text=cardReading(c,detail);showBattleCard(c,detail);\n                while(previewLayer')
change('inspection.text=cardReading(c,detail);\n        }','inspection.text=cardReading(c,detail);showBattleCard(c,detail);\n        }')
change('if(!hoveredCard||editingDeck||detailOpen||dragging||playing||controller.active||canPlaceSelected()||canPlacePending())return;','if(battlePreview||!hoveredCard||editingDeck||detailOpen||dragging||playing||controller.active||canPlaceSelected()||canPlacePending())return;')
block('        private function openControllerMenu():void','        private function controllerPage(','''        private function openControllerMenu():void
        {
            if(detailOpen||pileOpen||kegOpen||browsingCatalog||editingDeck||selectingDecks){controller.focusTag("control");return;}
            if(controllerMenuOpen){closeControllerMenu();return;}
            clearPlacementGhost();controllerMenuOpen=true;
            panel(controllerMenuLayer,0,0,1920,1080,0x080C10,.78);
            var box:Sprite=betaFrame(controllerMenuLayer,330,92,1260,880,-1413);
            text(box,"ДЕЙСТВИЯ",28,18,584,30,0xF5D77F);
            editorSmallButton(box,"Продолжить",28,78,584,58,true,closeControllerMenu);
            editorSmallButton(box,"Пас",28,146,584,58,canAct(),controllerMenuAction("pass"));
            editorSmallButton(box,"Способность лидера",28,214,584,58,canAct()&&leaderOne,controllerMenuAction("leader"));
            editorSmallButton(box,"Посмотреть свою колоду",28,282,584,58,canInspectPile(),controllerMenuAction("deck"));
            editorSmallButton(box,"Ваш сброс",28,350,584,58,canInspectPile(),controllerMenuAction("ownGrave"));
            editorSmallButton(box,"Сброс соперника",28,418,584,58,canInspectPile(),controllerMenuAction("enemyGrave"));
            editorSmallButton(box,"Вернуться в игру / завершить гвинт",28,486,584,58,true,function():void{closeControllerMenu();send("OnBetaGwentBoardClose",[]);});
            text(box,"View — колода · LT / RT — сбросы\\nR3 — лидер · X — подробности карты\\nДля быстрого паса удерживайте Y / △.",28,572,584,22,0xB9B4A9).height=104;
            text(box,"НАСТРОЙКИ",660,18,560,30,0xF5D77F);
            tempoLabel=button("Темп: "+animationTempo+"×",660,78,268,true,cycleTempo,box);
            motionLabel=button(reducedMotion?"Эффекты: кратко":"Эффекты: полно",942,78,278,true,toggleMotion,box);
            button(soundEnabled?"Звук: вкл":"Звук: выкл",660,146,268,true,toggleSound,box);
            button(!betaAudioAvailable?(betaAudioInstalled?"Фразы: банк не загружен":"Фразы: ждут банк"):voiceEnabled?"Фразы: вкл":"Фразы: выкл",942,146,278,betaAudioAvailable,toggleVoice,box);
            button("Поле Beta",660,214,268,true,function():void{closeControllerMenu();changeSkin(3);render();},box);
            button("Поле DIY",942,214,278,true,function():void{closeControllerMenu();changeSkin(skin==1?2:1);render();},box);
            button("Выбор колод",660,282,560,ready&&entryMode!=2,function():void{closeControllerMenu();submitBoard("OnBetaGwentBoardRestart",[serverRevision]);},box);
            text(box,"ПОСЛЕДНИЕ ДЕЙСТВИЯ",660,368,560,20,0xCFB176);
            text(box,actionHistory.slice(0,8).join("\\n"),660,408,560,20,0xD9D6CB).height=320;
        }
''')
a=s.index('        private function showBattleCard(');b=s.index('        private function betaVisual(',a)
s=s[:a]+s[a:b].replace('inspection.text=cardReading(c,detail);showBattleCard(c,detail);','inspection.text=cardReading(c,detail);')+s[b:]
change('        private function editorBetaButton(','''        private function betaWindow(parent:Sprite,x:Number,y:Number,w:Number,h:Number):Sprite
        {
            var p:Sprite=betaFrame(parent,x,y,w,h,-1413);
            panel(p,12,12,w-24,h-24,0x080A09,.5);return p;
        }
        private function editorBetaButton(''')
change('panel(content,64,24,1792,1032,0x101619,.98);','paintArt(content,-1310,1920,1080,0,0);betaWindow(content,64,24,1792,1032);')
change('panel(content,64,24,1792,1032,0x101619,.95);','paintArt(content,-1310,1920,1080,0,0);betaWindow(content,64,24,1792,1032);')
change('tile=panel(content,x,y,258,288,0x1A2D35,.98);','tile=betaFrame(content,x,y,258,288);')
change('paintArt(tile,c.templateId,250,235,4,4);','paintArt(tile,c.templateId,180,253,39,4);betaNine(tile,-1412,184,257,37,2);')
change('var tile:Sprite=panel(content,x,148,tileWidth,236,0x1E2E35,.95);','var tile:Sprite=betaWindow(content,x,148,tileWidth,236);\n                paintArt(tile,-1420-editorFactionIndex(cardFaction(option.leaderId)),tileWidth,72,0,0);')
change('panel(content,96,562,1728,320,0x16232B,.94);','betaWindow(content,96,562,1728,320);')
change('var card:Sprite=panel(content,108+(n%7)*244,574+int(n/7)*154,230,150,0x223943,.97);','var card:Sprite=betaWindow(content,108+(n%7)*244,574+int(n/7)*154,230,150);')
change('var tile:Sprite=panel(catalogGrid,(n%6)*188,int(n/6)*310,176,298,0x1A2D35,.96);','var tile:Sprite=betaFrame(catalogGrid,(n%6)*188,int(n/6)*310,176,298);')
change('catalogDetail=panel(content,1268,143,556,878,0x1B282E,.95);','catalogDetail=betaWindow(content,1268,143,556,878);')
change('var window:Sprite=panel(pileLayer,130,80,1660,920,0x101A20,.99);','var window:Sprite=betaWindow(pileLayer,130,80,1660,920);')
change('var tile:Sprite=panel(window,32+(ordinal%6)*177,204+int(ordinal/6)*270,158,248,0x193442,.98);','var tile:Sprite=betaFrame(window,32+(ordinal%6)*177,204+int(ordinal/6)*270,158,248);')
change('var modal:Sprite=panel(choiceLayer,450,215,1000,600,0x10191F,.98);','var modal:Sprite=betaWindow(choiceLayer,450,185,1000,660);')
change('var slot:int=i-choicePage*12;\n                var p:Sprite=panel(modal,24+(slot%6)*158,108+int(slot/6)*185,140,160,c.revealed?0x193E53:0x532D25,.98);\n                if(c.revealed)paintChoiceArt(p,c.templateId,134,154);','var slot:int=i-choicePage*12;var visibleColumns:int=Math.min(6,requestCards.length-choicePage*12);\n                var p:Sprite=betaFrame(modal,(1000-(visibleColumns*158-18))/2+(slot%6)*158,108+int(slot/6)*210,140,198);\n                if(c.revealed)paintChoiceArt(p,c.templateId,134,188);betaNine(p,-1412,138,192,1,1);')
change('panel(p,3,105,134,52','panel(p,3,143,134,52')
change('c.title,8,108,124,15','c.title,8,146,124,15')
change('p.graphics.drawRect(0,0,140,160);','p.graphics.drawRect(0,0,140,198);')
change('24,490,900,18','24,548,900,18')
change('474,745,180','474,775,180')
change('670,745,180','670,775,180')
change('1124,745,290','1124,775,290')
change('p.graphics.drawRect(0,0,isHand?handWidth:80,isHand?140:g.h-8);','p.graphics.drawRect(0,0,cardWidth,cardHeight);')
change('var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;',
       'if(isHand){var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;}')
change('var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,isHand?13:11);caption.height=32;',
       'if(isHand){var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,13);caption.height=32;}')
change('var fading:Sprite=panel(content,previous.x,previous.y,80,84,previous.side==1?0x173340:0x4B2925,.9);',
       'var fading:Sprite=panel(content,previous.x,previous.y,previous.width,previous.height,0x171714,.9);')
change('paintArt(fading,previous.templateId,74,78);','paintArt(fading,previous.templateId,previous.width-6,previous.height-6);')
change('var deathBand:Sprite=panel(fading,3,52,74,29,0x101315,.85);deathBand.mouseEnabled=false;',
       '// Preserve the actual portrait size during removal as during placement.')
change('var deathTitle:TextField=text(fading,previous.title,8,53,65,11);deathTitle.height=28;','')
change('send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);render();',
       'send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);if(controllerMenuOpen){closeControllerMenu();render();openControllerMenu();}else render();')
path.write_text(s,'utf8')
print('Battle and deckbuilder layout updated; native build pending.')

"""Apply the reviewable 0.7.1 editor/keg patch once; keep AS BOM and CRLF."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'
s=p.read_text('utf-8-sig')
def replace(old,new,count=1):
    global s
    assert s.count(old)==count,(old[:90],s.count(old),count)
    s=s.replace(old,new)

replace('private var editorFlight:Object;', '''private var editorFlight:Object;
        private var editorPosition:int=0;
        private var editorStrength:int=0;
        private var editorBaseline:String=null;
        private var editorExitPrompt:Boolean=false;''')
replace('factionOnly:editorFactionOnly,ownedOnly:editorOwnedOnly};','factionOnly:editorFactionOnly,ownedOnly:editorOwnedOnly,position:editorPosition,strength:editorStrength};')
replace('editorOwnedOnly=f.ownedOnly;','editorOwnedOnly=f.ownedOnly;editorPosition=int(f.position);editorStrength=int(f.strength);')
replace('if(matched){\n                if(editorUndoPending)', '''if(pending.bulk){
                matched=true;
                for(key in now)if(int(now[key])!=int(pending.restore?pending.restore[key]:0))matched=false;
                for(key in pending.restore)if(int(pending.restore[key])>0&&!now.hasOwnProperty(key))matched=false;
            }
            if(matched){
                if(editorUndoPending)''')
replace('else {editorUndo.push({id:pending.id,amount:pending.amount,after:now});', 'else {editorUndo.push({id:pending.id,amount:pending.amount,bulk:pending.bulk,before:pending.before,after:now});')
replace('editorFlight={id:pending.id,amount:pending.amount};','if(!pending.bulk)editorFlight={id:pending.id,amount:pending.amount};')
replace('var c:Object=editorById[last.id];\n            if(!c', '''if(last.bulk){editorUndoPending=true;editorAction("OnBetaGwentDeckEditorRestore")();return;}
            var c:Object=editorById[last.id];
            if(!c''')
replace('private function closeControllerMenu():void\n        {controllerMenuOpen=false;', 'private function closeControllerMenu():void\n        {controllerMenuOpen=false;editorExitPrompt=false;')
replace('if(entryMode==1||(selectingDecks', 'if(editingDeck){requestEditorExit();return;}\n            if(entryMode==1||(selectingDecks')
replace('if(editingDeck&&!detailOpen){','if(editingDeck&&!detailOpen&&!controllerMenuOpen){')
replace('editorAction("OnBetaGwentDeckEditorCancel")();','requestEditorExit();',2)
replace('if(controllerMenuOpen){if(key==27)closeControllerMenu();return;}', '''if(controllerMenuOpen){
                if(key==27)closeControllerMenu();
                else if(editorExitPrompt&&key==13)leaveEditor(true,false);
                return;
            }''')
replace('rememberEditorFilters();editorUndo=[];editorPending=null;editorUndoPending=false;','rememberEditorFilters();editorUndo=[];editorPending=null;editorUndoPending=false;editorBaseline=null;',1)
replace('editorName=title;editorSearch="";editorTier=0;editorType=0;','editorName=title;editorSearch="";editorTier=0;editorType=0;editorPosition=0;editorStrength=0;')
replace('editorCards.sort(sortEditorCards);','editorCards.sort(sortEditorCards);\n            if(editorBaseline==null)editorBaseline=editorSignature();')
replace('else if(eventName=="OnBetaGwentDeckEditorLeader")args.push(id);', '''else if(eventName=="OnBetaGwentDeckEditorClear"||eventName=="OnBetaGwentDeckEditorRestore"){
                    editorPending={bulk:true,before:editorCounts(),slot:editorState.slot,faction:editorState.faction,
                        restore:eventName=="OnBetaGwentDeckEditorRestore"?editorUndo[editorUndo.length-1].before:null};
                }
                else if(eventName=="OnBetaGwentDeckEditorLeader")args.push(id);''')
replace('if(eventName!="OnBetaGwentDeckEditorChange"){editorUndo=[];', 'if(eventName!="OnBetaGwentDeckEditorChange"&&eventName!="OnBetaGwentDeckEditorClear"&&eventName!="OnBetaGwentDeckEditorRestore"){editorUndo=[];')
replace('private function sortEditorCards(a:Object,b:Object):Number', '''private function editorSignature():String
        {
            var parts:Array=[editorName,editorState.faction,editorState.leader],counts:Array=[];
            for each(var c:Object in editorCards)if(c.copies>0)counts.push(c.templateId+":"+c.copies);
            counts.sort();return parts.join("|")+"|"+counts.join(",");
        }
        private function leaveEditor(save:Boolean,nextKeg:Boolean):void
        {
            if(!ready||!editingDeck)return;
            closeControllerMenu();rememberEditorFilters();ready=false;
            send("OnBetaGwentDeckEditorLeave",[revision,save,editorName,nextKeg]);
        }
        private function requestEditorExit(nextKeg:Boolean=false):void
        {
            if(!ready||!editingDeck)return;
            if(editorSignature()==editorBaseline){leaveEditor(false,nextKeg);return;}
            closeControllerMenu();controllerMenuOpen=true;editorExitPrompt=true;
            panel(controllerMenuLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.8);
            var box:Sprite=betaFrame(controllerMenuLayer,420,330,1080,390,-1414);
            text(box,"Сохранить изменения колоды?",34,30,1012,30,0xF5D77F);
            text(box,"Состав, лидер или название изменены. Выберите, что сделать перед выходом.",34,104,1012,23).height=110;
            editorSmallButton(box,"Сохранить",34,270,318,58,true,function():void{leaveEditor(true,nextKeg);});
            editorSmallButton(box,"Не сохранять",380,270,318,58,true,function():void{leaveEditor(false,nextKeg);});
            editorSmallButton(box,"Отмена",726,270,318,58,true,closeControllerMenu);
            controller.focusTag("control");
        }
        private function editorExtraFilter(kind:int):Function
        {
            return function():void{
                if(!ready)return;
                if(kind==1)editorPosition=(editorPosition+1)%6;
                else if(kind==2)editorStrength=(editorStrength+1)%3;
                else {editorSearch="";editorTier=0;editorType=0;editorFactionOnly=false;editorOwnedOnly=false;editorPosition=0;editorStrength=0;}
                editorPage=0;render();
            };
        }
        private function editorPositionMatches(c:Object):Boolean
        {
            if(editorPosition==0)return true;
            if(editorPosition==5)return c.typeMask==2;
            if(c.typeMask!=4)return false;
            var definition:Object=BetaGwentFullCatalog.find(c.templateId);
            var mask:int=definition?int(definition.placementMask):0;
            if(editorPosition==4)return mask!=0&&(mask&(mask-1))!=0;
            return mask==[0,1,2,4][editorPosition];
        }
        private function sortEditorCollection(a:Object,b:Object):Number
        {
            if(editorStrength!=0&&a.power!=b.power)return editorStrength==1?a.power-b.power:b.power-a.power;
            var order:Number=sortEditorCards(a,b);return order!=0?order:a.templateId-b.templateId;
        }
        private function drawEditorExtraFilters(beta:Boolean):void
        {
            var positions:Array=["Позиция: все","Рукопашный","Дальнобойный","Осадный","Подвижные","Событие"];
            var strengths:Array=["По редкости","Слабые сначала","Сильные сначала"];
            var x:Number=beta?482:464,y:Number=beta?272:268;
            editorBetaButton(content,positions[editorPosition],x,y,410,30,ready,editorExtraFilter(1),editorPosition!=0);
            editorBetaButton(content,strengths[editorStrength],x+420,y,254,30,ready,editorExtraFilter(2),editorStrength!=0);
            editorBetaButton(content,"Сбросить фильтры",x+684,y,280,30,ready,editorExtraFilter(0));
        }
        private function sortEditorCards(a:Object,b:Object):Number''')
replace('if(editorTier!=0&&editorTier!=c.tier)continue;','if(!editorPositionMatches(c))continue;\n                if(editorTier!=0&&editorTier!=c.tier)continue;',2)
# Collection order changes without changing deck-list order.
replace('var perPage:int=10;', 'filtered.sort(sortEditorCollection);\n            var perPage:int=10;')
replace('var perPage:int=12;', 'filtered.sort(sortEditorCollection);\n            var perPage:int=12;')
replace('content.graphics.lineStyle(2,0x6A5A44,.8);content.graphics.moveTo(474,286);content.graphics.lineTo(1446,286);content.graphics.lineStyle();','drawEditorExtraFilters(true);')
replace('text(content,"Поиск по названию, способности и тегам",464,268,924,17,0xC5C0AC).height=26;','drawEditorExtraFilters(false);')
replace('ready,editorAction("OnBetaGwentDeckEditorCancel"));','ready,function():void{requestEditorExit();});',2)
replace('editorBetaButton(content,"Отменить",1448,990,420,42,ready,function():void{requestEditorExit();});','''editorBetaButton(content,"Очистить",1448,934,420,42,ready&&editorState.total>0,editorAction("OnBetaGwentDeckEditorClear"));
            editorBetaButton(content,"Отменить карту",1448,878,420,42,ready&&editorUndo.length>0,undoEditorChange);
            editorBetaButton(content,"Отменить",1448,990,420,42,ready,function():void{requestEditorExit();});''')
replace('ready,function():void{send("OnBetaGwentKegOpen",[revision]);});return;}','ready,function():void{requestEditorExit(true);});return;}')
# Keg receipt is acknowledged after the native grant; next opening stays in the same root menu.
replace('kegNewIds={};revision=rev;kegOpen=true;', 'kegNewIds={};revision=rev;serverRevision=rev;kegOpen=true;')
replace('kegPicked=-1;kegFinalVoiced=false; }','kegPicked=-1;kegFinalVoiced=false;kegCommitted=false; }')
replace('private function chooseKeg(id:int):Function\n        { return function():void{if(!ready)return;kegOpen=false;pendingKeg=false;ready=false;send("OnBetaGwentKegChoose",[revision,id]);}; }', '''public function finishKegChoice(rev:int,success:Boolean):void
        {
            if(rev<serverRevision||!kegOpen)return;
            revision=rev;serverRevision=rev;ready=true;kegCommitted=success;
            kegPhase=success?3:2;pendingKeg=!success;render();
        }
        private function chooseKeg(id:int):Function
        {return function():void{if(!ready)return;for(var i:int=0;i<kegOffers.length;i++)if(kegOffers[i].templateId==id){kegPicked=i;commitKegChoice();return;}};}
        private var kegCommitted:Boolean=false;
        private function commitKegChoice():void
        {
            if(!ready||kegCommitted||kegPicked<0||kegPicked>=kegOffers.length)return;
            ready=false;send("OnBetaGwentKegChoose",[revision,int(kegOffers[kegPicked].templateId)]);
        }
        private function nextKeg():void
        {
            if(!ready||!kegCommitted||unopenedKegs<1)return;
            ready=false;send("OnBetaGwentKegOpen",[revision]);
        }''')
replace('{kegPhase=3;kegVoice(6);render();}', '{kegVoice(6);commitKegChoice();}',2)
start=s.index('        private function kegFinish():void')
end=s.index('        private static const KEG_W',start)
s=s[:start]+'''        private function kegFinish():void
        {if(ready&&kegCommitted)kegClose();}
'''+s[end:]
replace('betaWideButton("Готово",820,1002,280,ready,kegFinish);','''if(unopenedKegs>0)betaWideButton("Открыть ещё одну бочку",620,1002,400,ready&&kegCommitted,nextKeg);
                betaWideButton("Готово",unopenedKegs>0?1050:820,1002,280,ready&&kegCommitted,kegFinish);''')
replace('if(skin==3){drawKegBeta();return;}','if(skin==3||kegPhase==3){drawKegBeta();return;}')
p.write_bytes(b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8'))
for folder in ('src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'):
    (ROOT/'BetaGwent/ui'/folder/p.name).write_bytes(p.read_bytes())
print('Patched five AS copies')

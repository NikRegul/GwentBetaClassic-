package
{
    import flash.display.Bitmap;
    import flash.display.Sprite;
    import flash.display.Stage;
    import flash.events.Event;
    import flash.events.MouseEvent;
    import flash.events.KeyboardEvent;
    import flash.events.TextEvent;
    import flash.external.ExternalInterface;
    import flash.geom.Rectangle;
    import flash.utils.getTimer;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import flash.text.TextFieldType;

    [SWF(width="1920", height="1080", frameRate="30", backgroundColor="#101113")]
    public class BetaGwentBoard extends Sprite
    {
        [Embed(source="../assets/board_classic.png", compression="true", quality="100")] private static var ClassicBoard:Class;
        [Embed(source="../assets/board_wide.png", compression="true", quality="100")] private static var WideBoard:Class;
        public var _NATIVE_callGameEvent:Function;
        public var _NATIVE_registerDataBinding:Function;
        public var _NATIVE_unregisterDataBinding:Function;
        public var _NATIVE_registerChild:Function;
        public var _NATIVE_unregisterChild:Function;
        public var _NATIVE_registerRenderTarget:Function;
        public var _NATIVE_unregisterRenderTarget:Function;

        private var background:Sprite=new Sprite();
        private var content:Sprite=new Sprite();
        private var previewLayer:Sprite=new Sprite();
        private var dragLayer:Sprite=new Sprite();
        private var pileLayer:Sprite=new Sprite();
        private var detailLayer:Sprite=new Sprite();
        private var controller:BetaGwentController;
        private var controllerTyping:Boolean=false;
        private var controllerInspectBoard:Boolean=false;
        private var controllerMenuOpen:Boolean=false;
        private var controllerMenuLayer:Sprite=new Sprite();
        private var nameLayer:Sprite=new Sprite();
        private var nameOpen:Boolean=false;
        private var nameField:TextField;
        private var nameCounter:TextField;
        private var nameRevision:int;
        private var nameRussian:Boolean=true;
        private var nameUpper:Boolean=false;
        private var nameKeyAt:int=-1000;
        private var detailBody:TextField;
        private var catalogAbility:TextField;
        private var detailOpen:Boolean=false;
        private var hoveredCard:Object;
        private var hoveredDetail:Object;
        private var pileOpen:Boolean=false;
        private var pileView:Object;
        private var pilePage:int=0;
        private var pileTier:int=0;
        private var pilePicked:Object;
        private var pileDetail:TextField;
        private var pilePicture:Sprite;
        private var cards:Array=[];
        private var revision:int=-1;
        private var round:int=0;
        private var current:int=0;
        private var scores:Array=[0,0];
        private var crowns:Array=[0,0];
        private var flags:int=0;
        private var message:String="Ожидаю связь с WitcherScript...";
        private var selected:int=0;
        private var skin:int=2;
        private var ready:Boolean=false;
        private var connected:Boolean=false;
        private var selectingDecks:Boolean=false;
        private var editingDeck:Boolean=false;
        private var browsingCatalog:Boolean=false;
        private var catalogPage:int=0;
        private var catalogTier:int=0;
        private var catalogFaction:int=0;
        private var catalogType:int=0;
        private var catalogStatus:int=0;
        private var catalogSearch:String="";
        private var catalogPicked:Object;
        private var catalogGrid:Sprite;
        private var catalogDetail:Sprite;
        private var pileChoice:Boolean=false;
        private var editorState:Object;
        private var editorCards:Array=[];
        private var editorById:Object={};
        private var templateDetails:Object={};
        private var templateRules:Object={};
        private var hoverCardId:int=0;
        private var searchDeadline:int=0;
        private var editorPage:int=0;
        private var editorListPage:int=0;
        private var editorTier:int=0;
        private var editorType:int=0;
        private var editorFactionOnly:Boolean=false;
        private var editorSearch:String="";
        private var editorName:String="";
        private var editorCollection:Sprite;
        private var deckOptions:Array=[];
        private var leaderOptions:Array=[];
        private var chosenLeaders:Array=[200055,200158];
        private var leaderIds:Array=[200055,200055];
        private var leaderNames:Array=["Скрытый","Скрытый"];
        private var ownPreset:int=3;
        private var enemyPreset:int=2;
        private var deckViewSide:int=1;
        private var deckPage:int=0;
        private var presetPage:int=0;
        private var revealOwnDeck:Boolean=false;
        private var keyboardStage:Stage;
        private var enemyHand:int=0;
        private var leaderOne:Boolean=false;
        private var leaderTwo:Boolean=false;
        private var graves:Array=[0,0];
        private var requestId:int=0;
        private var requestPlayer:int=0;
        private var requestKind:int=0;
        private var requestMin:int=0;
        private var requestMax:int=0;
        private var requestCount:int=0;
        private var requestFinish:Boolean=false;
        private var requestMessage:String="";
        private var requestCards:Array=[];
        private var choicePage:int=0;
        private var choiceLayer:Sprite=new Sprite();
        private var deckCounts:Array=[0,0];
        private var leaderTitle:String="Скрытый";
        private var rowRequest:Boolean=false;
        private var leaderRow:Boolean=false;
        private var rowMode:int=0;
        private var templateChoice:Boolean=false;
        private var graveyardChoice:Boolean=false;
        private var handPowerChoice:Boolean=false;
        private var weatherRows:Array=[];
        private var weatherEffects:Array=[];
        private var weatherBirths:Object={};
        private var weatherFrame:int=0;
        private var artworkReport:int=-1;
        private var cardDetails:Object={};
        private var playRules:Object={};
        private var placementGhost:Sprite;
        private var placementPreview:Object;
        private var previousPoses:Object={};
        private var departedPoses:Object={};
        private var departedOrder:Array=[];
        private var consumedVisualIds:Object={};
        private var actionHistory:Array=[];
        private var previousCrowns:Array=[0,0];
        private var previousEnemyHand:int=0;
        private var lastRoundResult:Object;
        private var placementCard:Object;
        private var inspection:TextField;
        private var displayedCards:Object={};
        private var animations:Array=[];
        private var animationFrame:int=0;
        private var incoming:Object;
        private var receivingFrames:Array=[];
        private var replayFrames:Array=[];
        private var expectedFrames:int=1;
        private var serverRevision:int=-1;
        private var playing:Boolean=false;
        private var activeCue:Object;
        private var visualTimeScale:Number=1;
        private var frameDuration:Number=230;
        private var audioCueAt:Number=0;
        private var audioCueRevision:int=0;
        private var pendingImpacts:Array=[];
        private var autoRoundAt:int=0;
        private var autoRoundRevision:int=-1;
        private var ownedCopies:Object={};
        private var rewardMessage:String="";
        private var kegOpen:Boolean=false;
        private var pendingKeg:Boolean=false;
        private var unopenedKegs:int=0;
        private var kegAutomatic:Array=[];
        private var kegOffers:Array=[];
        private var frameDeadline:Number=0;
        private var animationStarted:int=0;
        private var keyboardFocusId:int=0;
        private var focusedRow:int=0;
        private var focusedSide:int=1;
        private var heldKey:int=0;
        private var lastKeyTime:int=0;
        private var animationTempo:Number=1;
        private var reducedMotion:Boolean=false;
        private var dragId:int=0;
        private var dragRevision:int=-1;
        private var dragStartX:Number=0;
        private var dragStartY:Number=0;
        private var dragging:Boolean=false;
        private var dragGhost:Sprite;
        private var cardSprites:Object={};
        private var suppressClickUntil:int=0;
        private var tempoLabel:TextField;
        private var motionLabel:TextField;
        private var soundEnabled:Boolean=true;
        private var voiceEnabled:Boolean=true;
        private var audioTickAt:int=0;
        private var skipAudio:Boolean=false;
        private var betaAudioAvailable:Boolean=false;
        private var betaAudioInstalled:Boolean=false;
        private var entryMode:int=0;
        private var npcDeckLabel:String="";
        private var forcedFaction:int=0;
        public function setEntryContext(mode:int,opponent:String,forced:int):void
        { entryMode=mode;npcDeckLabel=opponent;forcedFaction=forced;deckViewSide=1;background.visible=mode!=1; }

        public function BetaGwentBoard()
        {
            graphics.beginFill(0x101113); graphics.drawRect(0,0,1920,1080); graphics.endFill();
            addChild(background); addChild(content);addChild(previewLayer);addChild(dragLayer);addChild(pileLayer);addChild(detailLayer);
            addChild(controllerMenuLayer);
            addChild(nameLayer);
            controller=new BetaGwentController(this,controllerContext,controllerCommand);addChild(controller);
            dragLayer.mouseEnabled=false;dragLayer.mouseChildren=false;
            previewLayer.mouseEnabled=false;previewLayer.mouseChildren=false;
            if(registrationName()=="DeckBuilder")entryMode=1;
            background.visible=entryMode!=1;changeSkin(2); render();
            addEventListener(Event.ENTER_FRAME,animateCards);
            addEventListener(Event.ENTER_FRAME,animateWeather);
            addEventListener(Event.ENTER_FRAME,animateReplay);
            addEventListener(Event.ENTER_FRAME,flushSearch);
            addEventListener(Event.ADDED_TO_STAGE,onAdded);
            addEventListener(Event.REMOVED_FROM_STAGE,onRemoved);
        }
        protected function registrationName():String { return "BetaGwentBoard"; }
        public function setControllerDevice(kind:int,enabled:Boolean,swapped:Boolean):void
        {controller.configure(kind,enabled,swapped);}
        public function setControllerType(value:Boolean):void
        {controller.configure(controller.device,value,controller.swap);}
        public function setGamepadType(value:uint):void
        {controller.configure(int(value),controller.active,controller.swap);}
        public function swapAcceptCancel(value:Boolean):void
        {controller.configure(controller.device,controller.active,value);}
        public function handleForeignInputEvent(type:String,key:int,value:String,navigation:String):void
        {controller.foreignInput(key,value);}
        public function setControllerInput(value:int,purpose:int,title:String,active:Boolean):void
        {
            controllerTyping=active;
            if(active||value!=revision)return;
            if(purpose==1&&editingDeck){editorSearch=title.substr(0,64);editorPage=0;render();}
            else if(purpose==2&&browsingCatalog){catalogSearch=title.substr(0,80);catalogPage=0;render();}
        }
        private function controllerContext():Object
        {
            var base:String=kegOpen?"keg":browsingCatalog?"catalog":editingDeck?"editor":selectingDecks?"selection":requestId>0&&requestKind==1?"choice":canPlaceSelected()||canPlacePending()?"placement":rowRequest?"rows":requestId>0||selected>0?"target":controllerInspectBoard?"inspect":"battle";
            var mode:String=nameOpen?"name":detailOpen?"detail":controllerMenuOpen?"actions":pileOpen?"pile":base;
            var ps:Boolean=controller&&(controller.device==1||controller.device==6);
            var accept:String=ps?"×":"A",back:String=ps?"○":"B";
            if(controller&&controller.swap){var temp:String=accept;accept=back;back=temp;}
            var inspect:String=ps?"□":"X",alt:String=ps?"△":"Y",view:String=ps?"Touchpad":"View";
            var hint:String="↑↓←→ выбор · "+accept+" подтвердить · "+back+" назад · "+inspect+" карта";
            if(mode=="battle")hint="↑↓←→ карта · "+accept+" выбрать · "+inspect+" описание · L3 поле · "+alt+" удержать: пас · Start действия";
            else if(mode=="inspect")hint="↑↓←→ карта на поле · "+inspect+" / "+accept+" описание · L3 / "+back+" вернуться к руке";
            else if(mode=="placement")hint="←→ место вставки · LB/RB ряд · "+accept+" поставить · "+back+" отменить · "+inspect+" описание";
            else if(mode=="target")hint="↑↓←→ подсвеченная цель · "+accept+" применить · "+inspect+" описание · "+(isCaranthirChoice()?"LB/RB Мороз без перемещения":"Start кнопки выбора");
            else if(mode=="rows")hint="↑↓ ряд, включая пустой · "+accept+" применить · "+back+" назад";
            else if(mode=="editor")hint=accept+" добавить/убрать · LT − RT + · "+inspect+" карта · "+view+" список · LB/RB страницы · "+alt+" поиск · Start сохранить";
            else if(mode=="name")hint=accept+" буква · "+inspect+" стереть · "+alt+" пробел · LB/RB RU/EN · Start принять · "+back+" отменить";
            else if(mode=="detail")hint="Правый стик / LB/RB: описание · "+back+" / "+inspect+" закрыть";
            else hint+=" · LB/RB страницы";
            if(playing)hint=accept+" / "+back+": пропустить показ действий";
            var pref:String=mode=="rows"?"row":mode=="placement"?"position":mode=="target"||mode=="choice"||mode=="keg"?"target":mode=="battle"?"hand":mode=="inspect"||mode=="editor"||mode=="catalog"||mode=="pile"?"card":"control";
            return {mode:mode,baseMode:base,typing:controllerTyping,preferred:pref,
                accept:!controllerTyping&&(ready||playing||nameOpen||detailOpen||pileOpen||controllerMenuOpen),replay:playing&&!detailOpen&&!pileOpen,pass:canAct()&&!nameOpen&&!controllerMenuOpen&&!controllerTyping,
                root:nameOpen?nameLayer:detailOpen?detailLayer:controllerMenuOpen?controllerMenuLayer:pileOpen?pileLayer:base=="choice"?choiceLayer:content,
                layers:[{root:choiceLayer,mode:"choice"},{root:nameLayer,mode:"name"},{root:detailLayer,mode:"detail"},{root:controllerMenuLayer,mode:"actions"},{root:pileLayer,mode:"pile"}],
                hint:hint,hintY:mode=="battle"||mode=="inspect"||mode=="placement"||mode=="target"||mode=="rows"?80:mode=="detail"?940:mode=="pile"?1012:1040};
        }
        private function controllerPlacement(id:int):Object
        {
            for each(var c:Object in cards)if(c.id==id){var g:Object=rowGeometry(c.side,c.zone);
                return {anchor:id,index:c.index,target:0,side:c.side,zone:c.zone,x:g.x+12+c.index*88,y:g.y,w:80,h:g.h};}
            return null;
        }
        private function registerControllerPositions(side:int,zone:int):void
        {
            var g:Object=rowGeometry(side,zone),units:Array=[];
            for each(var c:Object in cards)if(c.side==side&&c.zone==zone)units.push(c);
            units.sortOn("index",Array.NUMERIC);
            for(var i:int=0;i<=units.length;i++){
                var target:Object={anchor:i<units.length?units[i].id:0,index:i,target:0,side:side,zone:zone,x:g.x+12+i*88,y:g.y,w:80,h:g.h};
                var slot:Sprite=new Sprite();slot.x=target.x-10;slot.y=g.y;
                slot.graphics.beginFill(0xFFFFFF,0);slot.graphics.drawRect(0,0,20,g.h);slot.graphics.endFill();
                slot.mouseEnabled=false;slot.mouseChildren=false;content.addChild(slot);
                controller.registerControl(slot,(side==1?"Ваш ":"Вражеский ")+(zone==1?"ближний":zone==2?"дальний":"осадный")+" ряд · место "+(i+1),controllerPlaceAction(target),null,null,"position",target);
            }
        }
        private function controllerPlaceAction(target:Object):Function
        {var expected:int=revision;return function():void{if(expected==revision&&rowEnabled(target.side,target.zone))submitPlacement(target);};}
        private function controllerRowAction(side:int,zone:int):Function
        {var expected:int=revision;return function():void{if(expected==revision)chooseRow(side,zone);};}
        private function isCaranthirChoice():Boolean
        {return requestId>0&&(rowMode==16||rowMode==17||rowMode==19);}
        private function controllerCardAction(id:int):void
        {
            if(!ready||playing||detailOpen||pileOpen)return;
            for each(var c:Object in cards)if(c.id==id){
                if(canPlaceBefore(c)){submitPlacement(controllerPlacement(id));return;}
                if(canDirectTarget(c)){submitBoard("OnBetaGwentBoardPlayTarget",[revision,selected,id]);return;}
                if(canAct()&&c.side==1&&c.zone==8&&c.canPlay){
                    controllerInspectBoard=false;
                    selected=selected==id?0:id;keyboardFocusId=selected;focusedRow=0;render();
                    if(selected>0)controller.focusTag(canPlaceSelected()?"position":"target");
                    return;
                }
                openCardDetail(c,cardDetails[id]);return;
            }
        }
        private function closeControllerMenu():void
        {controllerMenuOpen=false;while(controllerMenuLayer.numChildren)controllerMenuLayer.removeChildAt(0);}
        private function controllerMenuAction(name:String):Function
        {return function():void{closeControllerMenu();controllerCommand(name);};}
        private function openControllerMenu():void
        {
            if(detailOpen||pileOpen||kegOpen||browsingCatalog||editingDeck||selectingDecks){controller.focusTag("control");return;}
            if(controllerMenuOpen){closeControllerMenu();return;}
            clearPlacementGhost();controllerMenuOpen=true;
            panel(controllerMenuLayer,0,0,1920,1080,0x080C10,.78);
            var box:Sprite=panel(controllerMenuLayer,640,188,640,710,0x10191F,.99);
            text(box,"ДЕЙСТВИЯ",28,18,584,30,0xF5D77F);
            editorSmallButton(box,"Продолжить",28,78,584,58,true,closeControllerMenu);
            editorSmallButton(box,"Пас",28,146,584,58,canAct(),controllerMenuAction("pass"));
            editorSmallButton(box,"Способность лидера",28,214,584,58,canAct()&&leaderOne,controllerMenuAction("leader"));
            editorSmallButton(box,"Посмотреть свою колоду",28,282,584,58,canInspectPile(),controllerMenuAction("deck"));
            editorSmallButton(box,"Ваш сброс",28,350,584,58,canInspectPile(),controllerMenuAction("ownGrave"));
            editorSmallButton(box,"Сброс соперника",28,418,584,58,canInspectPile(),controllerMenuAction("enemyGrave"));
            editorSmallButton(box,"Вернуться в игру / завершить гвинт",28,486,584,58,true,function():void{closeControllerMenu();send("OnBetaGwentBoardClose",[]);});
            text(box,"View — колода · LT / RT — сбросы\nR3 — лидер · X — подробности карты\nДля быстрого паса удерживайте Y / △.",28,572,584,22,0xB9B4A9).height=104;
        }
        private function controllerPage(direction:int,node:Object):void
        {
            if(detailOpen){controllerScroll(direction*3);return;}
            if(pileOpen){pilePage=Math.max(0,pilePage+direction);pilePicked=null;drawPileView();return;}
            if(browsingCatalog){catalogPage=Math.max(0,catalogPage+direction);redrawCatalogGrid();return;}
            if(editingDeck){if(node&&node.rect.x>=1254)editorListPage=Math.max(0,editorListPage+direction);else editorPage=Math.max(0,editorPage+direction);render();return;}
            if(selectingDecks){
                var viewed:Object=deckOption(deckViewSide==1?ownPreset:enemyPreset);
                if(node&&node.rect.y>=562&&node.rect.y<984&&viewed)deckPage=Math.max(0,Math.min(Math.ceil(viewed.cards.length/14)-1,deckPage+direction));
                else presetPage=Math.max(0,Math.min(Math.ceil(deckOptions.length/4)-1,presetPage+direction));
                render();return;
            }
            if(requestId>0&&requestKind==1){choicePage=Math.max(0,Math.min(Math.ceil(requestCards.length/12)-1,choicePage+direction));render();return;}
            if(canPlaceSelected()||canPlacePending()){controller.focusPlacementRow(direction);return;}
            if(rowRequest||isCaranthirChoice()){controller.focusTag("row",direction);return;}
            controller.focusTag(canPlaceSelected()||canPlacePending()?"position":requestId>0||selected>0?"target":"hand",direction);
        }
        private function controllerScroll(amount:int):void
        {var body:TextField=detailOpen?detailBody:pileOpen?pileDetail:browsingCatalog?catalogAbility:inspection;if(body)body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV+amount));}
        private function controllerCommand(name:String,node:Object=null):void
        {
            if(name=="trace"){send("OnBetaGwentControllerTrace",[node.code,node.action,node.mode,node.focus]);return;}
            if(name=="device"||name=="mouse"){send("OnBetaGwentControllerDevice",[name=="device"]);return;}
            if(name=="clickSound"||name=="tickSound"){uiSound(name=="tickSound"?3:1);return;}
            if(nameOpen&&name!="focus"){
                if(name=="back")closeNameInput();
                else if(name=="inspect")editName("",true);
                else if(name=="alternate")editName(" ");
                else if(name=="menu")submitNameInput();
                else if(name=="previous"||name=="next"){nameRussian=!nameRussian;drawNameKeyboard();}
                return;
            }
            if(name=="skip"||playing&&name=="back"){skipReplay();return;}
            if(name=="board"&&!detailOpen&&!pileOpen&&!editingDeck&&!browsingCatalog&&!selectingDecks&&requestId==0&&selected==0&&!playing){
                controllerInspectBoard=!controllerInspectBoard;render();controller.focusTag(controllerInspectBoard?"card":"hand");return;
            }
            if(editingDeck&&!detailOpen){
                if(name=="ownGrave"||name=="enemyGrave"){
                    var editorNode:Object=controller.getFocus();
                    if(editorNode&&editorNode.card){var currentCard:Object=editorNode.card;
                        if(name=="ownGrave"&&currentCard.copies>0)editorAction("OnBetaGwentDeckEditorChange",currentCard.templateId,-1)();
                        else if(name=="enemyGrave"&&currentCard.canAdd)editorAction("OnBetaGwentDeckEditorChange",currentCard.templateId,1)();}
                    return;
                }
                if(name=="deck"){var pane:Object=controller.getFocus();controller.focusPane(!(pane&&pane.rect.x>=1254));return;}
                if(name=="menu"){if(ready&&editorState.valid)editorAction("OnBetaGwentDeckEditorSave")();return;}
                if(name=="alternate"){if(ready)send("OnBetaGwentControllerSearch",[revision,1,editorSearch]);return;}
            }
            if(name=="alternate"){openControllerMenu();return;}
            if(name=="focus"){
                if(node.row){focusedSide=node.row.side;focusedRow=node.row.zone;keyboardFocusId=0;}
                if(node.placement)showPlacementGhost(node.placement);else clearPlacementGhost();
                if(node.card){hoveredCard=node.card;hoveredDetail=node.detail;if(inspection)inspection.text=cardReading(node.card,node.detail);if(pileOpen)showPileCard(node.card);if(browsingCatalog){catalogPicked=node.card;redrawCatalogDetail();}}
                if(editingDeck&&node.card&&inspection)inspection.text=(node.rect.x>=1254?"Подтвердить — убрать копию. ":"Подтвердить — добавить копию. ")+"Левый триггер − · правый триггер + · просмотр карты.\n"+cardReading(node.card,node.detail);
                return;
            }
            if(name=="back"){
                if(detailOpen){closeCardDetail();return;}if(controllerMenuOpen){closeControllerMenu();return;}if(pileOpen){closePileView();return;}
                if(browsingCatalog){closeCatalog();return;}if(kegOpen){send("OnBetaGwentBoardClose",[]);return;}
                if(editingDeck){editorAction("OnBetaGwentDeckEditorCancel")();return;}if(selectingDecks){send("OnBetaGwentBoardClose",[]);return;}
                if(requestId>0){if(canFinishRequest())sendRequest("OnBetaGwentRequestFinish");return;}
                if(controllerInspectBoard){controllerInspectBoard=false;render();controller.focusTag("hand");return;}
                if(selected>0){selected=0;render();controller.focusTag("hand");return;}openControllerMenu();return;
            }
            if(name=="inspect"){
                if(detailOpen){closeCardDetail();return;}
                if(node&&node.card)openCardDetail(node.card,node.detail);return;
            }
            if(name=="menu"){if(requestId>0){controller.focusTag("control");return;}openControllerMenu();return;}
            if(name=="previous"||name=="next"){controllerPage(name=="previous"?-1:1,node);return;}
            if(name=="scrollUp"||name=="scrollDown"){controllerScroll(name=="scrollUp"?-3:3);return;}
            if(detailOpen||pileOpen||controllerMenuOpen)return;
            if(name=="deck"){inspectPile(1,16);return;}
            if(name=="ownGrave"||name=="enemyGrave"){inspectPile(name=="ownGrave"?1:2,32);return;}
            if(name=="leader"&&canAct()&&leaderOne){submitBoard("OnBetaGwentBoardLeader",[revision]);return;}
            if(name=="pass"&&canAct()){submitBoard("OnBetaGwentBoardPass",[revision]);return;}
        }
        private function onAdded(e:Event):void
        {
            removeEventListener(Event.ADDED_TO_STAGE,onAdded);
            keyboardStage=stage;
            controller.bind(keyboardStage);
            keyboardStage.addEventListener(KeyboardEvent.KEY_DOWN,onKey);
            keyboardStage.addEventListener(KeyboardEvent.KEY_UP,onKeyUp);
            keyboardStage.addEventListener(MouseEvent.MOUSE_MOVE,onDragMove);
            keyboardStage.addEventListener(MouseEvent.MOUSE_UP,onDragEnd);
            keyboardStage.addEventListener(MouseEvent.CLICK,onStageClick,true);
            if(ExternalInterface.available) ExternalInterface.call("registerMenu",registrationName(),this);
            addEventListener(Event.ENTER_FRAME,waitForBridge);
        }
        private function onRemoved(e:Event):void
        {
            controller.dispose();
            removeEventListener(Event.ENTER_FRAME,waitForBridge);
            removeEventListener(Event.ENTER_FRAME,animateCards);
            removeEventListener(Event.ENTER_FRAME,animateWeather);
            removeEventListener(Event.ENTER_FRAME,animateReplay);
            removeEventListener(Event.ENTER_FRAME,flushSearch);
            replayFrames=[];receivingFrames=[];incoming=null;playing=false;
            animations=[]; displayedCards={};
            weatherEffects=[];weatherBirths={};
            BetaGwentCardArt.release();
            if(keyboardStage) {
                keyboardStage.removeEventListener(KeyboardEvent.KEY_DOWN,onKey);
                keyboardStage.removeEventListener(KeyboardEvent.KEY_UP,onKeyUp);
                keyboardStage.removeEventListener(MouseEvent.MOUSE_MOVE,onDragMove);
                keyboardStage.removeEventListener(MouseEvent.MOUSE_UP,onDragEnd);
                keyboardStage.removeEventListener(MouseEvent.CLICK,onStageClick,true);
            }
            clearDrag();keyboardStage=null;
        }
        private function waitForBridge(e:Event):void
        {
            if(connected || _NATIVE_callGameEvent==null) return;
            connected=true; removeEventListener(Event.ENTER_FRAME,waitForBridge);
            send("OnConfigUI",[]);
            send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);
        }
        private function onKeyUp(e:KeyboardEvent):void
        { if(heldKey==e.keyCode)heldKey=0; }
        private function onKey(e:KeyboardEvent):void
        {
            var key:int=e.keyCode;
            if(nameOpen){
                if(key>=136)return;
                if(key==37||key==39||key==36||key==35)return;
                e.preventDefault();e.stopImmediatePropagation();
                if(key==27)closeNameInput();else if(key==13)submitNameInput();
                else if(key==8)editName("",true);else if(key==46)editName("",false,true);
                else if(e.ctrlKey&&key==65)nameField.setSelection(0,nameField.text.length);
                else if(!e.ctrlKey&&!e.altKey){
                    var typed:String="";
                    if(e.charCode>=32)typed=String.fromCharCode(e.charCode);
                    else if(key==32)typed=" ";
                    else if(key>=65&&key<=90)typed=String.fromCharCode(e.shiftKey?key:key+32);
                    else if(key>=48&&key<=57)typed=String.fromCharCode(key);
                    if(typed.length){nameKeyAt=getTimer();editName(typed);}
                }
                return;
            }
            if(detailOpen){e.preventDefault();if(key==27||key==73)closeCardDetail();return;}
            if(kegOpen){e.preventDefault();if(key==27){kegOpen=false;render();}else if(key>=49&&key<=51&&key-49<kegOffers.length)chooseKeg(kegOffers[key-49].templateId)();return;}
            if(key==73&&!(keyboardStage.focus is TextField&&TextField(keyboardStage.focus).type==TextFieldType.INPUT)){
                e.preventDefault();
                if(hoveredCard)openCardDetail(hoveredCard,hoveredDetail);
                else {var focusCard:Object=null;for each(var known:Object in cards)if(known.id==(keyboardFocusId!=0?keyboardFocusId:selected))focusCard=known;
                    if(focusCard)openCardDetail(focusCard,cardDetails[focusCard.id]);}
                return;
            }
            if(pileOpen){
                e.preventDefault();
                if(key==27)closePileView();
                else if(key==37||key==39){pilePage+=key==37?-1:1;pilePicked=null;drawPileView();}
                return;
            }
            if((key==68||key==71||key==72)&&canInspectPile()){
                e.preventDefault();inspectPile(key==72?2:1,key==68?16:32);return;
            }
            if(browsingCatalog){
                if(keyboardStage.focus is TextField&&TextField(keyboardStage.focus).type==TextFieldType.INPUT){
                    if(key==27){keyboardStage.focus=null;e.preventDefault();}return;
                }
                if(key==27){e.preventDefault();closeCatalog();}
                else if(key==37||key==39){e.preventDefault();catalogPage+=key==37?-1:1;redrawCatalogGrid();}
                return;
            }
            if(editingDeck){
                if(keyboardStage.focus is TextField&&TextField(keyboardStage.focus).type==TextFieldType.INPUT){
                    if(key==27){keyboardStage.focus=null;e.preventDefault();}return;
                }
                if(key==27&&ready){e.preventDefault();editorAction("OnBetaGwentDeckEditorCancel")();}return;
            }
            if([27,13,32,37,38,39,40,49,50,51,80,76,78,70].indexOf(key)<0)return;
            e.preventDefault();
            var now:int=getTimer();var arrow:Boolean=key>=37&&key<=40;
            if(heldKey==key&&(!arrow||now-lastKeyTime<110))return;
            heldKey=key;lastKeyTime=now;
            if(dragId!=0){if(key==27){clearDrag();render();}return;}
            if(key==27) {
                if(playing){skipReplay();return;}
                if(selected!=0){selected=0;keyboardFocusId=0;focusedRow=0;render();return;}
                if(requestId>0){
                    if(leaderRow&&canFinishRequest())sendRequest("OnBetaGwentRequestFinish");
                    else if(inspection)inspection.text="Способность уже разыграна. Выберите цель или используйте кнопку завершения выбора.";
                    return;
                }
                if(connected)send("OnBetaGwentBoardClose",[]);return;
            }
            if(playing){if(key==32||key==13)skipReplay();return;}
            if(!ready)return;
            if(selectingDecks){
                if(key==13&&entryMode!=1){ready=false;send("OnBetaGwentDeckStart",[revision]);}
                return;
            }
            if(key==37||key==39){cycleCardFocus(key==37?-1:1);return;}
            if(key==38||key==40){cycleRowFocus(key==38?-1:1);return;}
            if(key>=49&&key<=51){chooseRow(requestId>0&&(rowMode==3||rowMode==9||rowMode==10)?2:1,1<<(key-49));return;}
            if(key==13){activateFocus();return;}
            if(key==70&&canFinishRequest()){sendRequest("OnBetaGwentRequestFinish");return;}
            if(key==80&&canAct())submitBoard("OnBetaGwentBoardPass",[revision]);
            if(key==76&&canAct()&&leaderOne)submitBoard("OnBetaGwentBoardLeader",[revision]);
            if(key==78&&canNextRound())submitBoard("OnBetaGwentBoardNextRound",[revision]);
        }
        private function beginHandDrag(id:int):void
        {
            if(detailOpen||!canAct())return;
            dragId=id;dragRevision=revision;dragStartX=mouseX;dragStartY=mouseY;
        }
        private function clearDrag():void
        {
            clearPlacementGhost();dragId=0;dragging=false;dragGhost=null;dragLayer.graphics.clear();
            while(dragLayer.numChildren)dragLayer.removeChildAt(0);
        }
        private function onStageClick(e:MouseEvent):void
        {
            if(getTimer()<suppressClickUntil){e.preventDefault();e.stopImmediatePropagation();}
        }
        private function dragTarget():Object
        {
            if(canPlaceSelected()||canPlacePending()){
                var placeSide:int=placementSide();
                for(var placeZone:int=1;placeZone<=4;placeZone*=2)if(rowEnabled(placeSide,placeZone)){
                    var row:Object=rowGeometry(placeSide,placeZone);
                    if(mouseX>=row.x&&mouseX<=row.x+row.w&&mouseY>=row.y&&mouseY<=row.y+row.h)return insertionTarget(placeSide,placeZone);
                }
                return null;
            }
            for each(var c:Object in cards)if(canPlaceBefore(c)||canDirectTarget(c)){
                var sprite:Sprite=cardSprites[c.id];
                if(!sprite)continue;
                var body:Object=displayedCards[c.id];
                var bodyWidth:Number=body?body.width*sprite.scaleX:80;
                var bodyHeight:Number=body?body.height*sprite.scaleY:84;
                if(sprite&&mouseX>=sprite.x&&mouseX<=sprite.x+bodyWidth&&mouseY>=sprite.y&&mouseY<=sprite.y+bodyHeight)
                    return {anchor:canPlaceBefore(c)?c.id:0,target:canDirectTarget(c)?c.id:0,side:c.side,zone:c.zone,x:sprite.x,y:sprite.y,w:bodyWidth,h:bodyHeight};
            }
            for(var side:int=1;side<=2;side++)for(var zone:int=1;zone<=4;zone*=2)if(rowEnabled(side,zone)){
                var g:Object=rowGeometry(side,zone);
                if(mouseX>=g.x&&mouseX<=g.x+g.w&&mouseY>=g.y&&mouseY<=g.y+g.h)return {anchor:0,target:0,side:side,zone:zone,x:g.x,y:g.y,w:g.w,h:g.h};
            }
            return null;
        }
        private function onDragMove(e:MouseEvent):void
        {
            if(pileOpen||detailOpen){clearPlacementGhost();return;}
            if(dragId==0){updatePlacementHover();return;}
            if(revision!=dragRevision||!canAct()){clearDrag();return;}
            if(!dragging){
                if(Math.abs(mouseX-dragStartX)+Math.abs(mouseY-dragStartY)<9)return;
                var c:Object;for each(var candidate:Object in cards)if(candidate.id==dragId)c=candidate;
                if(!c||c.side!=1||c.zone!=8||!c.canPlay){clearDrag();return;}
                dragging=true;selected=dragId;keyboardFocusId=0;focusedRow=0;render();
                dragGhost=panel(dragLayer,mouseX+12,mouseY-70,94,140,0x173340,.97);
                paintArt(dragGhost,c.templateId,88,134);
                panel(dragGhost,3,3,34,30,0x101315,.9);text(dragGhost,c.power>0?String(c.power):"★",7,2,40,26,powerColor(c));
                panel(dragGhost,3,104,88,33,0x101315,.9);var caption:TextField=text(dragGhost,c.title,7,106,80,12);caption.height=32;
            }
            dragGhost.x=mouseX+12;dragGhost.y=mouseY-70;
            dragLayer.graphics.clear();var target:Object=dragTarget();
            dragGhost.alpha=target?1:.72;
            if(target){
                dragLayer.graphics.lineStyle(4,0xB0F2E6,.95);
                if(target.target>0)dragLayer.graphics.drawRoundRect(target.x-3,target.y-3,target.w+6,target.h+6,8,8);
                else if(target.anchor>0){dragLayer.graphics.moveTo(target.x-4,target.y);dragLayer.graphics.lineTo(target.x-4,target.y+target.h);}
                else dragLayer.graphics.drawRect(target.x+2,target.y+2,target.w-4,target.h-4);
                showPlacementGhost(target);
            }else{
                clearPlacementGhost();
            }
        }
        private function onDragEnd(e:MouseEvent):void
        {
            if(dragId==0)return;
            var id:int=dragId;var wasDragging:Boolean=dragging;
            var target:Object=wasDragging&&revision==dragRevision&&canAct()?dragTarget():null;
            if(target&&dragGhost&&displayedCards[id]){
                displayedCards[id].x=dragGhost.x;displayedCards[id].y=dragGhost.y;
                displayedCards[id].width=94;displayedCards[id].height=140;
            }
            clearDrag();
            if(!wasDragging)return;
            suppressClickUntil=getTimer()+250;
            if(target){
                if(target.target>0)submitBoard("OnBetaGwentBoardPlayTarget",[revision,id,target.target]);
                else if(target.anchor>0)submitBoard("OnBetaGwentBoardPlayBefore",[revision,id,target.anchor]);
                else chooseRow(target.side,target.zone);
            }else render();
        }
        private function canFinishRequest():Boolean
        { return !pileOpen&&ready&&!playing&&requestId>0&&requestFinish&&(!rowRequest||leaderRow||rowMode==3||rowMode==1||rowMode>=8); }
        private function canNextRound():Boolean
        { return !controllerMenuOpen&&!controllerTyping&&!detailOpen&&!pileOpen&&ready&&!playing&&!selectingDecks&&requestId==0&&(flags&4)!=0&&(flags>>4)==0; }
        private function submitBoard(eventName:String,args:Array):void
        {
            if(detailOpen||pileOpen||!ready||selectingDecks||(playing&&eventName!="OnBetaGwentBoardRestart"&&eventName!="OnBetaGwentBoardRematch"))return;
            // Block repeat clicks until the authoritative reply. Keep the visual origin intact.
            ready=false;
            if(eventName=="OnBetaGwentBoardRematch"||eventName=="OnBetaGwentBoardRestart"){
                displayedCards={};previousPoses={};departedPoses={};departedOrder=[];consumedVisualIds={};actionHistory=[];lastRoundResult=null;previousCrowns=[0,0];previousEnemyHand=0;
            }
            send(eventName,args);
        }
        private function keyboardCandidates():Array
        {
            if(requestId>0&&!rowRequest)return requestCards.concat();
            var result:Array=[];
            for each(var c:Object in cards) {
                if(canPlacePending()?canPlaceBefore(c):canAct()&&c.side==1&&c.zone==8&&c.canPlay)result.push(c);
            }
            result.sortOn(["zone","index"],Array.NUMERIC);return result;
        }
        private function cycleCardFocus(direction:int):void
        {
            var options:Array=keyboardCandidates();if(options.length==0)return;
            var index:int=-1;
            for(var i:int=0;i<options.length;i++)if(options[i].id==keyboardFocusId)index=i;
            index=index<0?(direction>0?0:options.length-1):(index+direction+options.length)%options.length;
            keyboardFocusId=options[index].id;focusedRow=0;
            uiSound(3);
            if(requestId==0)selected=keyboardFocusId;
            if(requestKind==1)choicePage=int(index/12);
            render();
        }
        private function rowEnabled(side:int,zone:int):Boolean
        { return requestId>0&&requestKind==1?false:requestId>0?canSelectRow(side,zone):canPlayRow(side,zone); }
        private function cycleRowFocus(direction:int):void
        {
            var options:Array=[];
            var rows:Array=[{side:2,zone:4},{side:2,zone:2},{side:2,zone:1},{side:1,zone:1},{side:1,zone:2},{side:1,zone:4}];
            var index:int=-1;
            for each(var row:Object in rows)if(rowEnabled(row.side,row.zone))options.push(row);
            if(options.length==0)return;
            for(var i:int=0;i<options.length;i++)if(options[i].side==focusedSide&&options[i].zone==focusedRow)index=i;
            index=index<0?(direction>0?0:options.length-1):(index+direction+options.length)%options.length;
            focusedSide=options[index].side;focusedRow=options[index].zone;keyboardFocusId=0;render();
        }
        private function chooseRow(side:int,zone:int):void
        {
            if(!rowEnabled(side,zone))return;
            if(requestId>0)submitBoard("OnBetaGwentDuelRowTarget",[revision,requestId,side,zone]);
            else if(playRules[selected]&&playRules[selected].kind==2)submitBoard("OnBetaGwentBoardPlayRowTarget",[revision,selected,side,zone]);
            else submitBoard("OnBetaGwentBoardPlay",[revision,selected,zone]);
        }
        private function activateFocus():void
        {
            if(focusedRow>0){chooseRow(focusedSide,focusedRow);return;}
            if(requestId>0&&keyboardFocusId>0) {
                if(canPlacePending())submitBoard("OnBetaGwentDuelPlaceBefore",[revision,requestId,keyboardFocusId]);
                else if(findRequestCard(keyboardFocusId)!=null)sendRequest("OnBetaGwentRequestSelect",keyboardFocusId);
                return;
            }
            if(canFinishRequest()){sendRequest("OnBetaGwentRequestFinish");return;}
            if(canNextRound()){submitBoard("OnBetaGwentBoardNextRound",[revision]);return;}
            if(selected!=0&&inspection)inspection.text="Выберите ряд клавишами ↑ ↓ и Enter, либо нажмите1 /2 /3 для своего ряда.";
        }
        private function send(eventName:String,args:Array):void
        {
            // Royale emits a global receiver for an unqualified Function-slot call.
            // The native adapter requires this registered DisplayObject as receiver.
            if(_NATIVE_callGameEvent!=null) _NATIVE_callGameEvent.call(this,eventName,args);
        }
        public function beginDeckSelection(rev:int,firstPreset:int,secondPreset:int,firstLeader:int,secondLeader:int):void
        {
            if(rev<serverRevision)return;
            clearDrag();browsingCatalog=false;editingDeck=false;editorCollection=null;selectingDecks=true;ready=false;playing=false;revision=rev;serverRevision=rev;
            revealOwnDeck=ownPreset!=firstPreset;ownPreset=firstPreset;enemyPreset=secondPreset;deckPage=0;
            chosenLeaders=[firstLeader,secondLeader];leaderOptions=[];
            receivingFrames=[];replayFrames=[];incoming=null;frameDeadline=0;activeCue=null;
            cards=[];cardDetails={};playRules={};placementCard=null;requestCards=[];requestId=0;selected=0;
            keyboardFocusId=0;focusedRow=0;selected=0;
            rowRequest=false;weatherRows=[];weatherBirths={};displayedCards={};departedPoses={};departedOrder=[];consumedVisualIds={};actionHistory=[];lastRoundResult=null;previousCrowns=[0,0];previousEnemyHand=0;
        }
        public function beginKegOpening(rev:int):void
        { revision=rev;kegOpen=true;pendingKeg=true;kegAutomatic=[];kegOffers=[]; }
        public function setUnopenedKegs(count:int,pending:Boolean):void
        {unopenedKegs=Math.max(0,count);pendingKeg=pending;}
        public function pushKegCard(id:int,ordinary:Boolean):void
        { var card:Object=BetaGwentFullCatalog.find(id);if(card)(ordinary?kegAutomatic:kegOffers).push(card); }
        public function finishKegOpening(rev:int):void
        { if(rev==revision){ready=true;render();} }
        private function chooseKeg(id:int):Function
        { return function():void{if(!ready)return;kegOpen=false;pendingKeg=false;ready=false;send("OnBetaGwentKegChoose",[revision,id]);}; }
        private function drawKeg():void
        {
            panel(content,64,24,1792,1032,0x101619,.98);
            text(content,"BETA GWENT · ОПЛАЧЕННАЯ БОЧКА",96,49,1390,32,0xE8D3A6);
            editorSmallButton(content,"Продолжить позже",1510,48,310,42,true,function():void{kegOpen=false;render();});
            text(content,"Добавлено бронзовых карт: "+kegAutomatic.length+" / 4. Выберите одну редкую карту; варианты сохраняются вместе с игрой.",96,111,1728,24).height=70;
            if(kegAutomatic.length<4)text(content,"Бронза исчерпана: лишние копии не выдаются. Стоимость бочки — 150 крон.",96,167,1728,20,0xE8D3A6);
            var n:int;var c:Object;var tile:Sprite;var x:Number;var y:Number;
            for(n=0;n<kegAutomatic.length+kegOffers.length;n++){
                var ordinary:Boolean=n<kegAutomatic.length;var index:int=ordinary?n:n-kegAutomatic.length;
                c=ordinary?kegAutomatic[index]:kegOffers[index];
                x=ordinary?(1920-(kegAutomatic.length*280-22))/2+index*280:530+index*300;y=ordinary?203:568;
                tile=panel(content,x,y,258,288,0x1A2D35,.98);
                paintArt(tile,c.templateId,250,235,4,4);
                tile.graphics.lineStyle(3,editorTierColor(c.tier));tile.graphics.drawRoundRect(0,0,258,288,8,8);
                panel(tile,4,225,250,58,0x11191C,.95);text(tile,c.title,12,229,232,21).height=54;
                panel(tile,4,4,250,28,0x11191C,.9);
                text(tile,c.tier==1?"Лидер":c.tier==8?"Золото":c.tier==4?"Серебро":"Бронза · получена",10,5,235,19,editorTierColor(c.tier));
                attachInspect(tile,c,{description:c.description},258,288);
                if(!ordinary)controller.registerControl(tile,c.title,chooseKeg(c.templateId),c,{description:c.description},"target");
                if(!ordinary)editorSmallButton(content,"Выбрать · "+(index+1),x,y+305,258,47,ready,chooseKeg(c.templateId));
                animations.push({sprite:tile,fromX:x+129,fromY:y+18,toX:x,toY:y,
                    duration:390,delay:index*110+(ordinary?0:400),hideBeforeDelay:true,appear:true,
                    fromScaleX:.08,fromScaleY:.94,toScaleX:1,toScaleY:1});
            }
            text(content,"Выбор:50% серебро /50% золото или лидер. Лишние копии исключены. Закрытие окна не меняет содержимое.",96,1004,1728,20,0xE8D3A6);
        }
        public function setOwnedCopies(id:int,copies:int):void
        { ownedCopies[id]=copies; }
        public function setRewardMessage(value:String):void
        { rewardMessage=value;if(!playing)render(); }
        public function pushDeckOption(id:int,title:String,description:String,leaderId:int,leader:String,
            units:int,specials:int,golds:int,silvers:int):void
        {
            if(!selectingDecks)return;
            if(entryMode!=0 && id<1001 && (id<16 || id>20))return;
            var option:Object={id:id,title:title,description:description,leaderId:leaderId,
                leader:leader,units:units,specials:specials,golds:golds,silvers:silvers,cards:[]};
            for(var i:int=0;i<deckOptions.length;i++)if(deckOptions[i].id==id){deckOptions[i]=option;return;}
            deckOptions.push(option);
        }
        public function pushLeaderOption(id:int,title:String,description:String,power:int):void
        { if(selectingDecks||editingDeck)leaderOptions.push({id:id,title:title,description:description,power:power}); }
        private function leadersForFaction(faction:int):Array
        { var result:Array=[];for each(var leader:Object in leaderOptions){var c:Object=BetaGwentFullCatalog.find(leader.id);if(c&&c.faction==faction&&(entryMode==0||int(ownedCopies[leader.id])>0))result.push(leader);}return result; }
        private function editorFactionLeader(faction:int):int
        {
            for each(var option:Object in deckOptions)
                if(option.id>=16&&option.id<=20&&cardFaction(option.leaderId)==faction
                    &&(entryMode==0||int(ownedCopies[option.leaderId])>0))return option.leaderId;
            var available:Array=leadersForFaction(faction);
            return available.length>0?available[0].id:0;
        }
        private function editorFactionAvailable(faction:int):Boolean
        { return ready&&editorFactionLeader(faction)>0&&(entryMode!=2||forcedFaction==0||forcedFaction==faction); }
        private function cardFaction(id:int):int
        { var c:Object=BetaGwentFullCatalog.find(id);return c?c.faction:0; }
        private function leaderOption(id:int):Object
        { for each(var option:Object in leaderOptions)if(option.id==id)return option;return null; }
        private function selectLeaderAction(side:int,id:int):Function
        {
            var expected:int=revision;
            return function():void{
                if(!ready||!selectingDecks||revision!=expected)return;
                ready=false;send("OnBetaGwentLeaderSelect",[expected,side,id]);
            };
        }
        public function pushDeckCard(preset:int,templateId:int,title:String,description:String,power:int,
            armor:int,tier:int,typeMask:int,copies:int):void
        {
            var option:Object=deckOption(preset);
            if(selectingDecks&&option)option.cards.push({templateId:templateId,title:title,description:description,
                power:power,armor:armor,tier:tier,typeMask:typeMask,copies:copies,timer:-1,tokens:0});
        }
        public function finishDeckSelection(rev:int):void
        {
            if(!selectingDecks||rev!=revision)return;
            if(revealOwnDeck){
                for(var i:int=0;i<deckOptions.length;i++)if(deckOptions[i].id==ownPreset){presetPage=int(i/4);break;}
                revealOwnDeck=false;deckViewSide=1;
            }
            ready=true;render();reportArtwork();
        }
        private function deckOption(id:int):Object
        { for each(var option:Object in deckOptions)if(option.id==id)return option;return null; }
        private function selectDeckAction(side:int,id:int):Function
        {
            var expected:int=revision;
            return function():void{
                if(!ready||!selectingDecks||revision!=expected)return;
                ready=false;send("OnBetaGwentDeckSelect",[expected,side,id]);
            };
        }
        private function drawDeckSelection():void
        {
            panel(content,64,24,1792,1032,0x101619,.95);
            text(content,entryMode==1?"BETA GWENT 0.9.24 · ВАШИ КОЛОДЫ":"BETA GWENT 0.9.24 · КОЛОДА ПЕРЕД БОЕМ",96,44,1400,32,0xE8D3A6);
            var savedCount:int=0;for each(var saved:Object in deckOptions)if(saved.id>=1001)savedCount++;
            var viewId:int=deckViewSide==1?ownPreset:enemyPreset;
            button("Создать колоду",1200,44,270,ready&&savedCount<8,openEditorAction(0));
            button(viewId>=1001?"Редактировать":"Скопировать состав",1486,44,338,ready&&(viewId>=1001||savedCount<8),openEditorAction(viewId));
            editorSmallButton(content,"Все карты",96,94,226,38,ready,function():void{browsingCatalog=true;catalogPage=0;render();});
            if(pendingKeg||entryMode==1&&unopenedKegs>0)editorSmallButton(content,pendingKeg?"Продолжить выбор бочки":"Открыть бочку · "+unopenedKegs,1420,94,404,38,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});
            text(content,entryMode==2?"Выберите свою колоду. Состав соперника скрыт: "+npcDeckLabel:entryMode==1?"Создайте или отредактируйте колоду. Изменения сохранятся с игровым сейвом.":"Выберите свою колоду и колоду соперника. Состав — ниже.",340,99,1030,22);
            var presetPages:int=Math.max(1,Math.ceil(deckOptions.length/4));presetPage=Math.min(presetPage,presetPages-1);
            if(presetPages>1){
                text(content,"Колоды "+(presetPage+1)+" / "+presetPages,1390,103,164,18,0xE8D3A6);
                button("←",1568,94,80,ready&&presetPage>0,function():void{presetPage--;render();});
                button("→",1660,94,80,ready&&presetPage+1<presetPages,function():void{presetPage++;render();});
            }
            var columns:int=Math.min(4,deckOptions.length);var tileWidth:Number=(1728-(columns-1)*24)/Math.max(1,columns);
            for(var i:int=presetPage*4;i<Math.min(deckOptions.length,(presetPage+1)*4);i++){
                var option:Object=deckOptions[i];var x:Number=96+(i-presetPage*4)*(tileWidth+24);
                var tile:Sprite=panel(content,x,148,tileWidth,236,0x1E2E35,.95);
                if(option.id==ownPreset){tile.graphics.lineStyle(3,0x8ED9F3);tile.graphics.drawRoundRect(0,0,tileWidth,236,8,8);}
                if(entryMode==0&&option.id==enemyPreset){tile.graphics.lineStyle(2,0xE4A488);tile.graphics.drawRoundRect(3,3,tileWidth-6,230,8,8);}
                paintArt(tile,option.leaderId,60,86,12,15);
                text(tile,option.title,86,14,tileWidth-102,columns==4?21:25,0xE8D3A6);
                var desc:TextField=text(tile,option.description,86,50,tileWidth-100,columns==4?16:18);desc.height=72;
                var composition:TextField=text(tile,(option.units+option.specials)+" карт · лидер: "+option.leader+"\n"+option.units+" отрядов · "+option.specials+" особых\n"+option.golds+" золотых · "+option.silvers+" серебряных",12,126,tileWidth-24,16,0xB9B4A9);composition.height=55;
                var buttonWidth:Number=(tileWidth-36)/2;
                button(option.id==ownPreset?"Ваша колода":"Выбрать себе",x+12,332,buttonWidth,ready&&(entryMode!=2||forcedFaction==0||cardFaction(option.leaderId)==forcedFaction),selectDeckAction(1,option.id));
                if(entryMode==0)button(option.id==enemyPreset?"Колода соперника":"Сопернику",x+24+buttonWidth,332,buttonWidth,ready,selectDeckAction(2,option.id));
            }
            for(var side:int=1;side<=2;side++){
                if(side==2&&entryMode!=0)continue;
                var leaderX:Number=side==1?96:990;var picked:Object=leaderOption(chosenLeaders[side-1]);
                var leaderText:TextField=text(content,(side==1?"Ваш лидер: ":"Лидер соперника: ")+(picked?picked.title:"")+(picked?" · сила "+picked.power+"\n"+picked.description:""),leaderX,398,820,18,0xE8D3A6);leaderText.height=44;
                var sideLeaders:Array=leadersForFaction(cardFaction(chosenLeaders[side-1]));
                for(var li:int=0;li<sideLeaders.length;li++){
                    var leader:Object=sideLeaders[li];
                    var leaderStep:Number=820/Math.max(1,sideLeaders.length);
                    editorSmallButton(content,(chosenLeaders[side-1]==leader.id?"● ":"")+leader.title,leaderX+li*leaderStep,444,leaderStep-8,48,ready,selectLeaderAction(side,leader.id));
                }
            }
            button("Смотреть свою",96,504,260,ready,function():void{deckViewSide=1;deckPage=0;render();});
            if(entryMode==0)button("Смотреть соперника",370,504,290,ready,function():void{deckViewSide=2;deckPage=0;render();});
            var viewed:Object=deckOption(deckViewSide==1?ownPreset:enemyPreset);
            if(!viewed){text(content,"Получаю составы колод...",96,470,1500,24);return;}
            var pages:int=Math.max(1,Math.ceil(viewed.cards.length/14));deckPage=Math.min(deckPage,pages-1);
            text(content,(deckViewSide==1?"Ваша колода: ":"Соперник: ")+viewed.title+" · состав · "+(deckPage+1)+" / "+pages,690,514,1120,23,0xE8D3A6);
            panel(content,96,562,1728,320,0x16232B,.94);
            for(var ordinal:int=deckPage*14;ordinal<Math.min(viewed.cards.length,(deckPage+1)*14);ordinal++){
                var c:Object=viewed.cards[ordinal];var n:int=ordinal-deckPage*14;
                var card:Sprite=panel(content,108+(n%7)*244,574+int(n/7)*154,230,150,0x223943,.97);
                paintArt(card,c.templateId,64,86,5,5);
                var label:TextField=text(card,c.title,82,6,144,18,0xF1E8D3);label.height=52;
                text(card,"×"+c.copies+(c.typeMask==4?" · сила "+c.power:" · особая"),82,58,144,17,0xE8D3A6);
                text(card,c.tier==8?"Золото":c.tier==4?"Серебро":"Бронза",82,84,144,16,0xB9B4A9);
                var ability:TextField=text(card,c.description,8,106,214,14,0xD8D0BB);ability.height=38;
                attachInspect(card,c,{description:c.description});
            }
            button("Назад",96,900,164,ready&&deckPage>0,function():void{deckPage--;render();});
            button("Вперёд",274,900,164,ready&&deckPage+1<pages,function():void{deckPage++;render();});
            inspection=text(content,"Наведите на карту: иллюстрация крупнее, теги и полное описание способности.",468,900,1356,18,0xD8D0BB);inspection.height=84;
            var first:Object=deckOption(ownPreset);var second:Object=deckOption(enemyPreset);
            button("Начать партию",96,990,420,entryMode!=1&&ready&&first!=null&&(entryMode==2||second!=null),function():void{
                if(!ready||!selectingDecks)return;var expected:int=revision;ready=false;send("OnBetaGwentDeckStart",[expected]);
            });
            text(content,"Сохранено "+savedCount+" / 8 · "+(entryMode==2?"Выход из боя считается поражением.":(first?first.title:"")+(entryMode==0&&second?" против "+second.title:"")),546,1002,960,19,0xE8D3A6);
            button(entryMode==2?"Отказаться от боя":"Закрыть",1574,990,250,connected,function():void{send("OnBetaGwentBoardClose",[]);});
        }
        // Collection snapshots are authoritative; inputs and filters stay local to this editor.
        public function beginDeckEditor(rev:int,slot:int,faction:int,leader:int,title:String,total:int,golds:int,silvers:int,valid:Boolean):void
        {
            if(rev<serverRevision)return;
            if(!editingDeck||!editorState||editorState.slot!=slot){
                editorName=title;editorSearch="";editorTier=0;editorType=0;editorFactionOnly=false;editorPage=0;editorListPage=0;
            }
            clearDrag();editingDeck=true;selectingDecks=false;ready=false;playing=false;
            var sameCollection:Boolean=editorState&&editorState.faction==faction&&editorCards.length>0;
            revision=rev;serverRevision=rev;leaderOptions=[];
            if(!sameCollection){editorCards=[];editorById={};}
            else for each(var cached:Object in editorCards)cached.copies=0;
            editorState={slot:slot,faction:faction,leader:leader,total:total,golds:golds,silvers:silvers,valid:valid,status:""};
            receivingFrames=[];replayFrames=[];incoming=null;frameDeadline=0;activeCue=null;
            cards=[];requestCards=[];requestId=0;selected=0;keyboardFocusId=0;focusedRow=0;
        }
        public function pushEditorCard(id:int,title:String,description:String,power:int,tier:int,typeMask:int,faction:int,copies:int,canAdd:Boolean):void
        {
            if(!editingDeck)return;
            var entry:Object=editorById[id];
            if(!entry){entry={templateId:id};editorCards.push(entry);editorById[id]=entry;}
            entry.title=title;entry.description=description;entry.power=power;entry.tier=tier;
            entry.typeMask=typeMask;entry.faction=faction;entry.copies=copies;entry.canAdd=canAdd;entry.timer=-1;entry.tokens=0;
        }
        public function pushEditorCopies(id:int,copies:int):void
        { if(editingDeck&&editorById[id])editorById[id].copies=copies; }
        private function flushSearch(e:Event):void
        {
            if(searchDeadline==0||getTimer()<searchDeadline)return;
            searchDeadline=0;
            if(editingDeck)redrawEditorCollection();else if(browsingCatalog)redrawCatalogGrid();
        }
        public function finishDeckEditor(rev:int,status:String):void
        {
            if(!editingDeck||rev!=revision)return;
            editorCards.sort(sortEditorCards);
            for each(var entry:Object in editorCards)entry.canAdd=editorState.total<40&&entry.copies<(entryMode==0?(entry.tier==2?3:1):int(ownedCopies[entry.templateId]))
                &&(entry.tier!=8||editorState.golds<4)&&(entry.tier!=4||editorState.silvers<6);
            editorState.status=status;ready=true;render();reportArtwork();
        }
        private function openEditorAction(id:int):Function
        {
            var expected:int=revision;
            return function():void{
                if(!ready||!selectingDecks||revision!=expected)return;
                ready=false;send("OnBetaGwentDeckEditorOpen",[expected,id]);
            };
        }
        private function editorAction(eventName:String,id:int=0,amount:int=0):Function
        {
            var expected:int=revision;
            return function():void{
                if(!ready||!editingDeck||revision!=expected)return;
                var args:Array=[expected];
                if(eventName=="OnBetaGwentDeckEditorChange")args.push(id,amount);
                else if(eventName=="OnBetaGwentDeckEditorLeader")args.push(id);
                else if(eventName=="OnBetaGwentDeckEditorSave")args.push(editorName);
                ready=false;send(eventName,args);
            };
        }
        private function closeCatalog():void
        { browsingCatalog=false;catalogGrid=null;catalogDetail=null;if(keyboardStage)keyboardStage.focus=null;render(); }
        private function catalogFilter(kind:int,value:int):Function
        { return function():void {
            if(kind==1)catalogFaction=value;else if(kind==2)catalogTier=value;
            else if(kind==3)catalogType=value;else catalogStatus=value;
            catalogPage=0;render();
        }; }
        private function catalogCards():Array
        {
            var found:Array=[];var query:String=catalogSearch.toLowerCase();
            for each(var c:Object in BetaGwentFullCatalog.all()){
                if(catalogFaction&&c.faction!=catalogFaction)continue;
                if(catalogTier&&c.tier!=catalogTier)continue;
                if(catalogType==1&&!c.leader)continue;
                if(catalogType>1&&(c.leader||c.typeMask!=catalogType))continue;
                if(catalogStatus==1&&!c.implemented||catalogStatus==2&&c.implemented)continue;
                if(query&&(c.title+" "+c.description+" "+c.tags+" "+c.templateId).toLowerCase().indexOf(query)<0)continue;
                found.push(c);
            }return found;
        }
        private function catalogPick(c:Object):Function
        { return function():void{catalogPicked=c;redrawCatalogDetail();}; }
        private function redrawCatalogGrid():void
        {
            if(!catalogGrid)return;while(catalogGrid.numChildren)catalogGrid.removeChildAt(0);
            var list:Array=catalogCards();var pages:int=Math.max(1,Math.ceil(list.length/12));
            catalogPage=Math.max(0,Math.min(catalogPage,pages-1));
            for(var i:int=catalogPage*12;i<Math.min(list.length,(catalogPage+1)*12);i++){
                var c:Object=list[i];var n:int=i-catalogPage*12;
                var tile:Sprite=panel(catalogGrid,(n%6)*188,int(n/6)*310,176,298,0x1A2D35,.96);
                tile.graphics.lineStyle(2,editorTierColor(c.tier));tile.graphics.drawRoundRect(0,0,176,298,6,6);
                if(c.hasArt)paintArt(tile,c.templateId,164,230,6,6);
                else text(tile,"Иллюстрация ещё не найдена",12,70,152,20,0xA9B5BA).height=90;
                panel(tile,5,5,166,31,0x11191C,.92);
                text(tile,c.leader?"Лидер":c.typeMask==2?"Особая карта":"Сила: "+c.power,10,7,157,18,powerColor(c));
                panel(tile,5,179,166,57,0x11191C,.9);
                text(tile,c.title,10,182,155,18).height=53;
                text(tile,c.implemented?"Реализована":"Ожидает реализации",8,242,162,16,c.implemented?0x8FD2B0:0xC5A97B).height=23;
                text(tile,c.acquisitionShort||"Получение: не назначен",8,269,162,14,0xB4B5AE);
                attachEditorClick(tile,catalogPick(c));
                controller.registerControl(tile,c.title,catalogPick(c),c,{description:c.description},"card");
            }
            text(catalogGrid,"Найдено: "+list.length+" / "+BetaGwentFullCatalog.all().length+" · страница "+(catalogPage+1)+" / "+pages,180,632,930,20,0xD6C6A8);
            editorSmallButton(catalogGrid,"←",0,628,72,36,catalogPage>0,function():void{catalogPage--;redrawCatalogGrid();});
            editorSmallButton(catalogGrid,"→",84,628,72,36,catalogPage+1<pages,function():void{catalogPage++;redrawCatalogGrid();});
        }
        private function redrawCatalogDetail():void
        {
            if(!catalogDetail)return;while(catalogDetail.numChildren)catalogDetail.removeChildAt(0);
            var c:Object=catalogPicked;if(!c){text(catalogDetail,"Нажмите карту слева, чтобы прочитать описание и способ получения.",22,24,504,24).height=150;return;}
            if(c.hasArt)paintArt(catalogDetail,c.templateId,140,197,22,22);
            text(catalogDetail,c.title,178,22,350,28,0xE8D3A6).height=85;
            var tier:String=c.tier==1?"Лидер":c.tier==8?"Золотая":c.tier==4?"Серебряная":"Бронзовая";
            var factionNames:Object={1:"Нейтральная",2:"Чудовища",4:"Нильфгаард",8:"Северные королевства",16:"Скоя'таэли",32:"Скеллиге"};
            text(catalogDetail,tier+" · "+(c.typeMask==2?"Особая":"Отряд")+"\n"+(c.typeMask==4?"Сила: "+c.power+"\n":"")+factionNames[c.faction],178,122,350,20).height=95;
            text(catalogDetail,c.implemented?"Реализована в текущей версии":"Ещё не реализована для игры",22,237,504,22,c.implemented?0x8FD2B0:0xC5A97B);
            text(catalogDetail,"Теги: "+(c.tags||"—"),22,268,504,18,0xA7DCEE).height=55;
            var ability:TextField=text(catalogDetail,c.description||"Описание в исходной локализации отсутствует.",22,333,504,23);ability.height=200;
            catalogAbility=ability;
            ability.mouseEnabled=true;ability.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{ability.scrollV-=e.delta;e.stopPropagation();});
            editorSmallButton(catalogDetail,"↑",456,540,32,30,true,function():void{ability.scrollV--;});
            editorSmallButton(catalogDetail,"↓",496,540,32,30,true,function():void{ability.scrollV++;});
            text(catalogDetail,c.acquisition,22,587,504,23,0xE8D3A6).height=56;
            text(catalogDetail,"В коллекции: "+int(ownedCopies[c.templateId])+" / "+(c.tier==2?3:1)+". "+(entryMode==0?"Практика позволяет использовать все карты.":"В редакторе доступны только полученные копии."),22,667,504,19,0xB4B5AE).height=85;
        }
        private function drawCatalog():void
        {
            panel(content,64,24,1792,1032,0x101619,.98);
            text(content,"BETA GWENT 0.9.24 · ВСЕ КАРТЫ",96,44,1400,32,0xE8D3A6);
            editorSmallButton(content,"Назад к колодам",1520,44,304,42,true,closeCatalog);
            var fullList:Array=BetaGwentFullCatalog.all();var collected:int=0;
            for each(var template:Object in fullList)if(int(ownedCopies[template.templateId])>0)collected++;
            text(content,"Коллекция: "+collected+" / "+fullList.length+" · осталось "+(fullList.length-collected)+" · нужна одна копия каждой карты и лидера",96,99,1650,22);
            var input:TextField=editorInput(catalogSearch,96,143,1116,80);
            input.addEventListener(Event.CHANGE,function(e:Event):void{catalogSearch=input.text;catalogPage=0;searchDeadline=getTimer()+160;});
            var factions:Array=[0,1,2,8,16,32,4];var titles:Array=["Все","Нейтральные","Чудовища","Север","Скоя'таэли","Скеллиге","Нильфгаард"];
            for(var f:int=0;f<factions.length;f++)editorSmallButton(content,(catalogFaction==factions[f]?"● ":"")+titles[f],96+f*159,199,149,34,true,catalogFilter(1,factions[f]));
            var tiers:Array=[0,8,4,2,1];var tierNames:Array=["Все","Золото","Серебро","Бронза","Лидеры"];
            for(var t:int=0;t<tiers.length;t++)editorSmallButton(content,(catalogTier==tiers[t]?"● ":"")+tierNames[t],96+t*137,243,127,34,true,catalogFilter(2,tiers[t]));
            var types:Array=[0,4,2];var typeNames:Array=["Все","Отряды","Особые"];
            for(var k:int=0;k<types.length;k++)editorSmallButton(content,(catalogType==types[k]?"● ":"")+typeNames[k],797+k*138,243,128,34,true,catalogFilter(3,types[k]));
            var states:Array=["Все","Реализованы","В очереди"];
            for(var st:int=0;st<3;st++)editorSmallButton(content,(catalogStatus==st?"● ":"")+states[st],96+st*230,287,220,34,true,catalogFilter(4,st));
            catalogGrid=new Sprite();catalogGrid.x=96;catalogGrid.y=340;content.addChild(catalogGrid);
            catalogDetail=panel(content,1268,143,556,878,0x1B282E,.95);
            redrawCatalogGrid();redrawCatalogDetail();
        }
        private function editorSmallButton(parent:Sprite,title:String,x:Number,y:Number,w:Number,h:Number,enabled:Boolean,callback:Function):void
        {
            var p:Sprite=panel(parent,x,y,w,h,enabled?0x273B43:0x222426,.96);
            p.alpha=enabled?1:0.45;p.buttonMode=enabled;
            var label:TextField=text(p,title,8,3,w-14,18);label.height=h-4;
            if(enabled){
                controller.registerControl(p,title,callback);
                p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{p.alpha=0.8;});
                p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{p.alpha=1;});
                p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
            }
        }
        private function attachEditorClick(p:Sprite,callback:Function):void
        {
            controller.registerControl(p,"",callback,null,null,"");
            p.buttonMode=true;
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{uiSound(3);callback();});
        }
        private function editorInput(value:String,x:Number,y:Number,w:Number,maxChars:int):TextField
        {
            var field:TextField=text(content,value,x,y,w,24);
            field.height=40;field.type=TextFieldType.INPUT;field.multiline=false;field.wordWrap=false;
            field.selectable=true;field.mouseEnabled=true;field.maxChars=maxChars;
            field.background=true;field.backgroundColor=0x192A31;field.border=true;field.borderColor=0xA48A60;
            var purpose:int=y==112?0:browsingCatalog?2:1;
            controller.registerControl(field,purpose==0?"Название колоды":"Поиск карт",function():void{
                if(!ready)return;
                if(purpose==0)openNameInput();
                else send("OnBetaGwentControllerSearch",[revision,purpose,field.text]);
            });
            field.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{if(purpose==0){openNameInput();e.preventDefault();}else if(keyboardStage)keyboardStage.focus=field;e.stopPropagation();});
            field.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            return field;
        }
        public function setEditorName(value:int,title:String):void
        {
            if(!editingDeck || value!=revision || title.length==0)return;
            editorName=title.substr(0,48);editorState.title=editorName;render();
        }
        private function closeNameInput():void
        {nameOpen=false;nameField=null;nameCounter=null;if(keyboardStage)keyboardStage.focus=null;while(nameLayer.numChildren)nameLayer.removeChildAt(0);}
        private function openNameInput():void
        {
            if(!ready||!editingDeck||nameOpen)return;
            nameOpen=true;nameRevision=revision;
            panel(nameLayer,0,0,1920,1080,0x080C10,.85);
            var box:Sprite=panel(nameLayer,460,220,1000,650,0x10191F,.99);
            text(box,"НАЗВАНИЕ КОЛОДЫ",30,20,920,30,0xF5D77F);
            nameField=text(box,editorName,30,82,940,28);nameField.height=48;
            nameField.type=TextFieldType.INPUT;nameField.multiline=false;nameField.wordWrap=false;nameField.selectable=true;nameField.mouseEnabled=true;nameField.maxChars=48;
            nameField.background=true;nameField.backgroundColor=0x233B45;
            nameField.addEventListener(TextEvent.TEXT_INPUT,function(e:TextEvent):void{
                e.preventDefault();e.stopImmediatePropagation();
                if(getTimer()-nameKeyAt>70)editName(e.text);
            });
            nameCounter=text(box,"",30,140,940,20,0xB9B4A9);nameCounter.height=35;
            if(keyboardStage)keyboardStage.focus=nameField;
            nameField.setSelection(0,nameField.text.length);
            drawNameKeyboard();
        }
        private function editName(value:String,backspace:Boolean=false,forward:Boolean=false):void
        {
            if(!nameField)return;
            var start:int=nameField.selectionBeginIndex,end:int=nameField.selectionEndIndex;
            if(start==end){if(backspace&&start>0)start--;if(forward&&end<nameField.text.length)end++;}
            var next:String=nameField.text.substr(0,start)+value+nameField.text.substr(end);
            if(next.length>48)return;
            nameField.text=next;nameField.setSelection(start+value.length,start+value.length);
            nameCounter.text=next.length+" / 48 · Enter — принять · Esc — отменить";
        }
        private function nameLetter(letter:String):Function
        {return function():void{editName(letter);};}
        private function submitNameInput():void
        {
            if(!nameField)return;
            var title:String=nameField.text.replace(/^\s+|\s+$/g,"");
            if(!title.length){nameCounter.text="Введите название колоды.";return;}
            var value:int=nameRevision;closeNameInput();send("OnBetaGwentDeckNameSubmit",[value,title]);
        }
        private function drawNameKeyboard():void
        {
            var box:Sprite=Sprite(nameLayer.getChildAt(1));
            while(box.numChildren>3)box.removeChildAt(box.numChildren-1);
            var letters:String="1234567890"+(nameRussian?"йцукенгшщзхъфывапролджэячсмитьбюё":"qwertyuiopasdfghjklzxcvbnm")+"-_.";
            if(nameUpper)letters=letters.toUpperCase();
            for(var i:int=0;i<letters.length;i++)editorSmallButton(box,letters.charAt(i),30+(i%11)*85,192+int(i/11)*64,76,54,true,nameLetter(letters.charAt(i)));
            editorSmallButton(box,nameRussian?"RU → EN":"EN → RU",30,520,158,50,true,function():void{nameRussian=!nameRussian;drawNameKeyboard();});
            editorSmallButton(box,nameUpper?"А → а":"а → А",200,520,116,50,true,function():void{nameUpper=!nameUpper;drawNameKeyboard();});
            editorSmallButton(box,"Пробел",328,520,180,50,true,nameLetter(" "));
            editorSmallButton(box,"← Стереть",520,520,180,50,true,function():void{editName("",true);});
            editorSmallButton(box,"Принять",712,520,120,50,true,submitNameInput);
            editorSmallButton(box,"Отмена",844,520,126,50,true,closeNameInput);
            text(box,"Можно печатать с клавиатуры или выбирать буквы мышью / контроллером.\nПринять меняет черновик; затем нажмите «Сохранить колоду».",30,580,940,20,0xB9B4A9).height=58;
            nameCounter.text=nameField.text.length+" / 48 · Enter — принять · Esc — отменить";
        }
        private function editorTierColor(tier:int):uint
        { return tier==8?0xDCC078:tier==4?0xC5D4DC:0xAE8061; }
        private function editorFilterAction(tier:int,typeMask:int,factionOnly:Boolean):Function
        {
            return function():void{
                editorTier=tier;editorType=typeMask;editorFactionOnly=factionOnly;editorPage=0;render();
            };
        }
        private function sortEditorCards(a:Object,b:Object):Number
        {
            if(a.tier!=b.tier)return b.tier-a.tier;
            if(a.typeMask!=b.typeMask)return a.typeMask==4?-1:1;
            if(a.power!=b.power)return b.power-a.power;
            var first:String=a.title.toLowerCase();var second:String=b.title.toLowerCase();
            return first<second?-1:first>second?1:0;
        }
        private function redrawEditorCollection():void
        {
            if(!editorCollection)return;
            while(editorCollection.numChildren)editorCollection.removeChildAt(0);
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            var filtered:Array=[];var query:String=editorSearch.toLowerCase();
            for each(var c:Object in editorCards){
                if(editorTier!=0&&editorTier!=c.tier)continue;
                if(editorType!=0&&editorType!=c.typeMask)continue;
                if(editorFactionOnly&&c.faction==1)continue;
                if(query.length>0&&(c.title+" "+c.description+" "+BetaGwentCardTags.text(c.templateId)).toLowerCase().indexOf(query)<0)continue;
                filtered.push(c);
            }
            // Collection order is cached at the end of the authoritative batch.
            var pages:int=Math.max(1,Math.ceil(filtered.length/12));editorPage=Math.max(0,Math.min(editorPage,pages-1));
            for(var i:int=editorPage*12;i<Math.min(filtered.length,(editorPage+1)*12);i++){
                c=filtered[i];var n:int=i-editorPage*12;
                var tile:Sprite=panel(editorCollection,(n%6)*188,int(n/6)*272,174,256,0x142A34,.97);
                paintArt(tile,c.templateId,166,216,4,4);
                tile.graphics.lineStyle(2,editorTierColor(c.tier),0.95);tile.graphics.drawRoundRect(1,1,172,254,6,6);
                panel(tile,4,4,48,30,0x0B1217,.92);
                text(tile,c.typeMask==4?String(c.power):"★",9,4,42,22,powerColor(c));
                panel(tile,4,158,166,62,0x091319,.9);
                var title:TextField=text(tile,c.title,10,161,156,18);title.height=38;
                text(tile,BetaGwentCardTags.text(c.templateId),7,201,160,12,0xA7DCEE).height=23;
                text(tile,"× "+c.copies+" / "+(entryMode==0?(c.tier==2?3:1):int(ownedCopies[c.templateId])),7,225,70,17,0xE8D3A6).height=26;
                attachInspect(tile,c,{description:c.description},174,256);
                if(c.canAdd&&ready)attachEditorClick(tile,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
                editorSmallButton(tile,"−",83,224,38,27,ready&&c.copies>0,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorSmallButton(tile,"+",127,224,38,27,ready&&c.canAdd,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
            }
            if(filtered.length==0)text(editorCollection,"Карты по этим условиям не найдены.",16,50,1060,26,0xD8D0BB);
            editorSmallButton(editorCollection,"←",0,550,72,34,ready&&editorPage>0,function():void{editorPage--;redrawEditorCollection();});
            editorSmallButton(editorCollection,"→",84,550,72,34,ready&&editorPage+1<pages,function():void{editorPage++;redrawEditorCollection();});
            text(editorCollection,"Коллекция: "+filtered.length+" карт · страница "+(editorPage+1)+" / "+pages,184,554,922,18,0xE8D3A6).height=32;
        }
        private function drawDeckEditor():void
        {
            panel(content,64,24,1792,1032,0x101619,.98);
            text(content,"BETA GWENT 0.9.24 · СОЗДАНИЕ КОЛОДЫ",96,44,1120,32,0xE8D3A6);
            text(content,(editorState.faction==32?"Скеллиге":editorState.faction==16?"Скоя’таэли":editorState.faction==4?"Нильфгаард":editorState.faction==8?"Север":"Чудовища")+" · слот "+editorState.slot+" / 8",1270,48,540,26,0xE8D3A6);
            text(content,"Название колоды",96,88,650,18,0xB9B4A9);
            var nameInput:TextField=editorInput(editorName,96,112,396,48);
            nameInput.addEventListener(Event.CHANGE,function(e:Event):void{editorName=nameInput.text;});
            editorSmallButton(content,"Изменить имя",504,112,152,40,ready,openNameInput);
            editorSmallButton(content,(editorState.faction==2?"● ":"")+"Чудовища",668,94,172,32,editorFactionAvailable(2),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(2)));
            editorSmallButton(content,(editorState.faction==8?"● ":"")+"Север",850,94,172,32,editorFactionAvailable(8),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(8)));
            editorSmallButton(content,(editorState.faction==4?"● ":"")+"Нильфгаард",1032,94,172,32,editorFactionAvailable(4),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(4)));
            editorSmallButton(content,(editorState.faction==16?"● ":"")+"Скоя’таэли",668,134,172,32,editorFactionAvailable(16),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(16)));
            editorSmallButton(content,(editorState.faction==32?"● ":"")+"Скеллиге",850,134,172,32,editorFactionAvailable(32),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(32)));
            var factionLeaders:Array=leadersForFaction(editorState.faction);
            for(var li:int=0;li<factionLeaders.length;li++){
                var leader:Object=factionLeaders[li];
                var leaderStep:Number=1116/Math.max(1,factionLeaders.length);
                editorSmallButton(content,(editorState.leader==leader.id?"● ":"")+leader.title+" · "+leader.power,96+li*leaderStep,174,leaderStep-8,48,ready,editorAction("OnBetaGwentDeckEditorLeader",leader.id));
            }
            var picked:Object=leaderOption(editorState.leader);
            if(picked){
                paintArt(content,picked.id,76,108,1270,102);
                text(content,picked.title+" · сила "+picked.power,1364,104,444,24,0xE8D3A6).height=38;
                text(content,picked.description,1364,146,444,18).height=85;
            }
            var tiers:Array=[0,2,4,8];var tierTitles:Array=["Все редкости","Бронза","Серебро","Золото"];
            for(var ti:int=0;ti<tiers.length;ti++)
                editorSmallButton(content,(editorTier==tiers[ti]?"● ":"")+tierTitles[ti],96+ti*150,244,140,34,ready,editorFilterAction(tiers[ti],editorType,editorFactionOnly));
            editorSmallButton(content,(editorType==0?"● ":"")+"Все",710,244,104,34,ready,editorFilterAction(editorTier,0,editorFactionOnly));
            editorSmallButton(content,(editorType==4?"● ":"")+"Отряды",824,244,152,34,ready,editorFilterAction(editorTier,4,editorFactionOnly));
            editorSmallButton(content,(editorType==2?"● ":"")+"Особые",986,244,150,34,ready,editorFilterAction(editorTier,2,editorFactionOnly));
            editorSmallButton(content,editorFactionOnly?"Ф":"Ф+Н",1146,244,66,34,ready,editorFilterAction(editorTier,editorType,!editorFactionOnly));
            var searchInput:TextField=editorInput(editorSearch,96,300,1116,64);
            searchInput.addEventListener(Event.CHANGE,function(e:Event):void{
                editorSearch=searchInput.text;editorPage=0;searchDeadline=getTimer()+160;
            });
            text(content,"Поиск: название, способность или тег (например, алхимия) · Ф+Н: фракция и нейтральные",96,280,1116,14,0xB9B4A9).height=20;
            panel(content,84,348,1140,594,0x16232B,.92);
            editorCollection=new Sprite();editorCollection.x=96;editorCollection.y=358;content.addChild(editorCollection);
            redrawEditorCollection();
            panel(content,1254,244,570,698,0x16232B,.94);
            text(content,editorState.total+" / 25–40 карт",1270,257,350,29,editorState.valid?0xA6D6AF:0xE8D3A6).height=44;
            editorSmallButton(content,"Очистить",1640,256,168,34,ready&&editorState.total>0,editorAction("OnBetaGwentDeckEditorClear"));
            var units:int=0;var specials:int=0;var selectedCards:Array=[];
            for each(var c:Object in editorCards)if(c.copies>0){
                selectedCards.push(c);if(c.typeMask==4)units+=c.copies;else specials+=c.copies;
            }
            selectedCards.sort(sortEditorCards);
            text(content,"Золото "+editorState.golds+" / 4 · серебро "+editorState.silvers+" / 6\n"+units+" отрядов · "+specials+" особых",1270,306,538,20,0xD8D0BB).height=52;
            var pages:int=Math.max(1,Math.ceil(selectedCards.length/16));editorListPage=Math.max(0,Math.min(editorListPage,pages-1));
            for(var i:int=editorListPage*16;i<Math.min(selectedCards.length,(editorListPage+1)*16);i++){
                c=selectedCards[i];var y:Number=366+(i-editorListPage*16)*33;
                var row:Sprite=panel(content,1270,y,538,30,0x1D3039,.94);
                paintArt(row,c.templateId,20,27,3,1);
                text(row,"×"+c.copies+"  "+c.title,30,2,414,17,editorTierColor(c.tier)).height=28;
                attachInspect(row,c,{description:c.description},538,30);
                if(ready)attachEditorClick(row,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorSmallButton(row,"−",450,1,38,28,ready,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorSmallButton(row,"+",494,1,38,28,ready&&c.canAdd,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
            }
            if(selectedCards.length==0)text(content,"Добавляйте карты из коллекции кнопкой +.\nБронза: до3 копий, серебро и золото: по1.",1270,386,522,22,0xB9B4A9).height=140;
            editorSmallButton(content,"←",1270,902,72,30,ready&&editorListPage>0,function():void{editorListPage--;render();});
            editorSmallButton(content,"→",1352,902,72,30,ready&&editorListPage+1<pages,function():void{editorListPage++;render();});
            text(content,"Состав: "+(editorListPage+1)+" / "+pages,1450,904,350,18,0xB9B4A9).height=30;
            text(content,editorState.status,1270,948,538,18,editorState.valid?0xA6D6AF:0xE8D3A6).height=36;
            button("Сохранить колоду",1270,990,262,ready&&editorState.valid,editorAction("OnBetaGwentDeckEditorSave"));
            button("Отменить",1548,990,276,ready,editorAction("OnBetaGwentDeckEditorCancel"));
            inspection=text(content,"Клик по карте коллекции добавляет копию, по составу — убирает. Наведите, чтобы прочитать способность.",96,956,1116,20,0xD8D0BB);inspection.height=82;
        }

        public function beginVisualBatch(count:int):void
        {
            closeControllerMenu();
            closePileView();
            selectingDecks=false;editingDeck=false;editorCollection=null;
            // A new batch replaces presentation only (e.g. Restart), never game state.
            if(playing){displayedCards={};weatherBirths={};}
            receivingFrames=[];replayFrames=[];incoming=null;expectedFrames=Math.max(1,Math.min(129,count));
            playing=true;ready=false;frameDeadline=0;activeCue=null;
        }
        public function setBoardHeader(rev:int,roundNumber:int,currentPlayer:int,scoreOne:int,scoreTwo:int,
            crownsOne:int,crownsTwo:int,stateFlags:int,status:String):void
        {
            if(rev<serverRevision)return;
            incoming={revision:rev,round:roundNumber,current:currentPlayer,scores:[scoreOne,scoreTwo],
                crowns:[crownsOne,crownsTwo],flags:stateFlags,message:status,cards:[],requestCards:[],
                cardDetails:{},playRules:{},byId:{},weatherRows:[],requestId:0,requestKind:0,rowMode:0,cue:{kind:0,duration:0}};
        }
        public function setBoardCounts(count:int,firstLeader:Boolean,secondLeader:Boolean,graveOne:int,graveTwo:int):void
        {
            if(!incoming)return;incoming.enemyHand=count;incoming.leaderOne=firstLeader;
            incoming.leaderTwo=secondLeader;incoming.graves=[graveOne,graveTwo];
        }
        public function pushBoardCard(id:int,title:String,power:int,armor:int,side:int,zone:int,index:int,canPlay:Boolean,templateId:int):void
        {
            if(!incoming)return;
            var entry:Object={id:id,title:title,power:power,armor:armor,side:side,zone:zone,index:index,canPlay:canPlay,templateId:templateId,timer:-1};
            incoming.cards.push(entry);incoming.byId[id]=entry;
            if(templateDetails[templateId])incoming.cardDetails[id]=templateDetails[templateId];
            if(templateRules[templateId])incoming.playRules[id]=templateRules[templateId];
        }
        public function pushTemplateDetails(id:int,description:String,tier:int,typeMask:int):void
        { templateDetails[id]={description:description,tier:tier,typeMask:typeMask}; }
        public function pushTemplateRules(id:int,kind:int,side:int,types:int,tiers:int,ignore:int,maximum:int,rowMask:int):void
        { templateRules[id]={kind:kind,side:side,types:types,tiers:tiers,ignore:ignore,maximum:maximum,rowMask:rowMask}; }
        public function pushLiveStats(id:int,tokens:int,timer:int,normalPower:int,created:Boolean):void
        { if(incoming&&incoming.byId[id]){incoming.byId[id].tokens=tokens;incoming.byId[id].timer=timer;incoming.byId[id].normalPower=normalPower;incoming.byId[id].created=created;} }
        private function powerColor(c:Object):uint
        {
            if(c&&c.hasOwnProperty("normalPower")){
                if(int(c.power)<int(c.normalPower))return 0xEF665A;
                if(int(c.power)>int(c.normalPower))return 0x79D596;
            }
            return 0xFFFFFF;
        }
        public function pushCardStatus(id:int,tokens:int):void
        {
            if(!incoming)return;
            for each(var card:Object in incoming.cards)if(card.id==id){card.tokens=tokens;return;}
        }
        public function pushCardTimer(id:int,value:int):void
        {
            if(!incoming)return;
            for each(var card:Object in incoming.cards)if(card.id==id){card.timer=value;return;}
        }
        public function setBoardDetails(rev:int,deckOne:int,deckTwo:int,leader:String,selectRow:int):void
        {
            if(!incoming||rev!=incoming.revision)return;
            incoming.deckCounts=[deckOne,deckTwo];incoming.leaderTitle=leader;incoming.rowMode=selectRow;
        }
        public function setPlacementCard(rev:int,templateId:int,title:String,power:int,tier:int):void
        {
            if(incoming&&rev==incoming.revision)incoming.placementCard=templateId>0?
                {templateId:templateId,title:title,power:power,tier:tier}:null;
        }
        public function setBoardLeaders(rev:int,first:int,second:int,firstTitle:String,secondTitle:String):void
        { if(incoming&&rev==incoming.revision){incoming.leaderIds=[first,second];incoming.leaderNames=[firstTitle,secondTitle];} }
        public function setWeatherRow(rev:int,side:int,zone:int,token:int,damage:int):void
        { if(incoming&&rev==incoming.revision)incoming.weatherRows.push({side:side,zone:zone,token:token,damage:damage}); }
        public function pushCardPlayRules(id:int,kind:int,side:int,types:int,tiers:int,ignore:int,maximum:int,rowMask:int):void
        { if(incoming)incoming.playRules[id]={kind:kind,side:side,types:types,tiers:tiers,ignore:ignore,maximum:maximum,rowMask:rowMask}; }
        public function pushCardDetails(id:int,description:String,tier:int,typeMask:int):void
        { if(incoming)incoming.cardDetails[id]={description:description,tier:tier,typeMask:typeMask}; }
        public function setRequestHeader(rev:int,id:int,player:int,kind:int,minimum:int,maximum:int,
            count:int,canFinish:Boolean,status:String):void
        {
            if(!incoming||rev!=incoming.revision)return;
            incoming.requestId=id;incoming.requestPlayer=player;incoming.requestKind=kind;
            incoming.requestMin=minimum;incoming.requestMax=maximum;incoming.requestCount=count;
            incoming.requestFinish=canFinish;incoming.requestMessage=status;
        }
        public function pushRequestCard(id:int,title:String,templateId:int,factionId:int,revealed:Boolean,isSelected:Boolean):void
        {
            if(incoming&&incoming.requestId>0)incoming.requestCards.push({id:id,title:title,templateId:templateId,
                factionId:factionId,revealed:revealed,selected:isSelected,timer:-1});
        }
        public function setVisualCue(rev:int,kind:int,source:int,target:int,side:int,row:int,templateId:int,duration:int,title:String):void
        {
            if(!incoming||rev!=incoming.revision)return;
            incoming.cue={kind:kind,source:source,target:target,side:side,row:row,
                templateId:templateId,duration:duration,title:title};
        }
        public function finishBoardState(rev:int):void
        {
            if(!incoming||rev!=incoming.revision)return;
            serverRevision=rev;receivingFrames.push(incoming);incoming=null;
            if(receivingFrames.length<expectedFrames)return;
            replayFrames=receivingFrames;receivingFrames=[];
            // Only contiguous changes of the same source/row form a visual multi-target action.
            // Rule order and all intermediate snapshots stay intact.
            for(var groupStart:int=0;groupStart<replayFrames.length;groupStart++){
                var groupCue:Object=replayFrames[groupStart].cue;
                if(groupCue.kind!=2)continue;
                var groupEnd:int=groupStart+1;
                while(groupEnd<replayFrames.length){
                    var nextCue:Object=replayFrames[groupEnd].cue;
                    if(nextCue.kind!=2||nextCue.source!=groupCue.source||nextCue.side!=groupCue.side||nextCue.row!=groupCue.row)break;
                    groupEnd++;
                }
                for(var groupIndex:int=groupStart;groupIndex<groupEnd;groupIndex++){
                    replayFrames[groupIndex].cue.sequence=groupIndex-groupStart+1;
                    replayFrames[groupIndex].cue.sequenceSize=groupEnd-groupStart;
                }
                groupStart=groupEnd-1;
            }
            var total:Number=0;
            for each(var frame:Object in replayFrames)total+=Math.max(0,reducedMotion?80:frame.cue.duration);
            visualTimeScale=Math.min(1,8000/Math.max(1,total))/animationTempo;
            showNextFrame();
        }
        public function setVisualTarget(rev:int,templateId:int,power:int,side:int,zone:int):void
        {
            if(incoming&&incoming.revision==rev)incoming.cue.targetView={templateId:templateId,power:power,side:side,zone:zone};
        }
        private function showNextFrame():void
        {
            if(replayFrames.length==0)return;
            clearDrag();var frame:Object=replayFrames.shift();
            if(frame.requestId!=requestId)choicePage=0;
            previousCrowns=crowns.concat();previousEnemyHand=enemyHand;
            revision=frame.revision;round=frame.round;current=frame.current;scores=frame.scores;
            crowns=frame.crowns;flags=frame.flags;message=frame.message;cards=frame.cards;
            cardDetails=frame.cardDetails;playRules=frame.playRules;weatherRows=frame.weatherRows;selected=0;keyboardFocusId=0;focusedRow=0;
            enemyHand=frame.enemyHand;leaderOne=frame.leaderOne;leaderTwo=frame.leaderTwo;
            graves=frame.graves;deckCounts=frame.deckCounts;leaderTitle=frame.leaderTitle;
            leaderIds=frame.leaderIds;leaderNames=frame.leaderNames;placementCard=frame.placementCard;
            rowMode=frame.rowMode;rowRequest=(rowMode>0&&rowMode<5)||(rowMode>=8&&rowMode<=10);leaderRow=rowMode==2;templateChoice=rowMode==5||rowMode==7||rowMode==13;graveyardChoice=rowMode==6;handPowerChoice=rowMode==11;pileChoice=rowMode==12||rowMode==14;
            requestId=frame.requestId;requestPlayer=frame.requestPlayer;requestKind=frame.requestKind;
            requestMin=frame.requestMin;requestMax=frame.requestMax;requestCount=frame.requestCount;
            requestFinish=frame.requestFinish;requestMessage=frame.requestMessage;requestCards=frame.requestCards;
            activeCue=frame.cue;playing=replayFrames.length>0;ready=true;
            if(activeCue.kind==6)lastRoundResult={round:round,scores:scores.concat(),crowns:crowns.concat(),flags:flags,title:activeCue.title};
            if(activeCue.kind==7||activeCue.kind==17)lastRoundResult=null;
            if(activeCue.kind>0&&activeCue.title){
                if(actionHistory.length==0||actionHistory[0]!=activeCue.title)actionHistory.unshift(activeCue.title);
                if(actionHistory.length>6)actionHistory.pop();
            }
            // Readability floors may exceed the8s target on unusually long chains.
            var minimum:Number=reducedMotion?60:activeCue.kind==6?1050:activeCue.kind==7?650:
                activeCue.kind==17?650:activeCue.kind==1?620:activeCue.kind==15||activeCue.kind==16?520:activeCue.kind==2?420:activeCue.kind==10?560:120;
            frameDuration=playing?Math.max(reducedMotion?60:minimum/animationTempo,(reducedMotion?80:frame.cue.duration)*visualTimeScale):360;
            frameDeadline=playing?getTimer()+frameDuration:0;
            render();reportArtwork();
            audioCueAt=0;
            if(!skipAudio&&activeCue.kind>0){audioCueRevision=revision;audioCueAt=getTimer()+cueImpactDelay();}
            if(!playing){
                send("OnBetaGwentVisualDone",[serverRevision]);
                autoRoundAt=canNextRound()?getTimer()+1400:0;autoRoundRevision=revision;
            }else autoRoundAt=0;
        }
        private var artworkReportPending:Boolean=false;
        private function reportArtwork():void { artworkReportPending=true; }
        private function flushArtworkReport():void
        {
            artworkReportPending=false;
            var report:int=BetaGwentCardArt.successes*100+BetaGwentCardArt.failures;
            if(report!=artworkReport){
                artworkReport=report;send("OnBetaGwentArtworkStatus",[BetaGwentCardArt.successes,BetaGwentCardArt.failures]);
                if(BetaGwentCardArt.failures>0)send("OnBetaGwentArtworkFailure",[BetaGwentCardArt.lastError]);
            }
        }
        private function animateReplay(e:Event):void
        {
            var now:int=getTimer();
            if(audioCueAt>0&&now>=audioCueAt){audioCueAt=0;if(audioCueRevision==revision)send("OnBetaGwentAudioCue",[audioCueRevision]);}
            if(connected&&(artworkReportPending||artworkReport!=BetaGwentCardArt.successes*100+BetaGwentCardArt.failures))flushArtworkReport();
            if(connected&&betaAudioInstalled&&now>=audioTickAt){audioTickAt=now+250;send("OnBetaGwentAudioTick",[]);}
            if(playing&&frameDeadline>0&&now>=frameDeadline)showNextFrame();
            if(autoRoundAt>0&&now>=autoRoundAt&&revision==autoRoundRevision&&!detailOpen&&canNextRound()){
                autoRoundAt=0;submitBoard("OnBetaGwentBoardNextRound",[revision]);
            }
        }
        private function skipReplay():void
        {
            if(!playing||replayFrames.length==0)return;
            audioCueAt=0;send("OnBetaGwentAudioCancel",[]);
            // Skipping presentation must not erase the committed action history.
            for each(var skipped:Object in replayFrames)if(skipped.cue.kind>0&&skipped.cue.title){
                if(skipped.cue.kind==6)lastRoundResult={round:skipped.round,scores:skipped.scores.concat(),crowns:skipped.crowns.concat(),flags:skipped.flags,title:skipped.cue.title};
                if(skipped.cue.kind==7||skipped.cue.kind==17)lastRoundResult=null;
                if(actionHistory.length==0||actionHistory[0]!=skipped.cue.title)actionHistory.unshift(skipped.cue.title);
                if(actionHistory.length>6)actionHistory.pop();
            }
            replayFrames=[replayFrames[replayFrames.length-1]];skipAudio=true;showNextFrame();skipAudio=false;
        }

        private function uiSound(kind:int=1):void
        { if(connected&&soundEnabled)send("OnBetaGwentAudioUi",[kind]); }
        public function setAudioStatus(installed:Boolean,available:Boolean):void
        { betaAudioInstalled=installed;betaAudioAvailable=available; }
        private function toggleSound():void
        { soundEnabled=!soundEnabled;send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);render(); }
        private function toggleVoice():void
        { voiceEnabled=!voiceEnabled;send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);render(); }

        private function cycleTempo():void
        {
            var old:Number=animationTempo;animationTempo=old==1?1.5:old==1.5?2:1;
            if(playing){
                var now:int=getTimer();frameDeadline=now+Math.max(0,frameDeadline-now)*old/animationTempo;
                frameDuration*=old/animationTempo;visualTimeScale*=old/animationTempo;
                if(audioCueAt>0)audioCueAt=now+Math.max(0,audioCueAt-now)*old/animationTempo;
            }
            if(tempoLabel)tempoLabel.text="Темп: "+animationTempo+"×";
        }
        private function toggleMotion():void
        {
            reducedMotion=!reducedMotion;
            if(motionLabel)motionLabel.text=reducedMotion?"Эффекты: кратко":"Эффекты: полно";
            if(reducedMotion&&playing)frameDeadline=Math.min(frameDeadline,getTimer()+80);
        }
        private function changeSkin(value:int):void
        {
            skin=value;
            while(background.numChildren) background.removeChildAt(0);
            var bitmap:Bitmap=(skin==1 ? new ClassicBoard() : new WideBoard()) as Bitmap;
            bitmap.smoothing=true;
            bitmap.width=1920; bitmap.height=1920*bitmap.bitmapData.height/bitmap.bitmapData.width;
            bitmap.y=(1080-bitmap.height)/2; background.addChild(bitmap);
        }
        private function text(parent:Sprite,value:String,x:Number,y:Number,w:Number,size:int=22,color:uint=0xF1E8D3):TextField
        {
            var field:TextField=new TextField();
            field.defaultTextFormat=new TextFormat("$NormalFont",size,color);
            field.text=readableText(value); field.x=x; field.y=y; field.width=w; field.height=80;
            field.multiline=true; field.wordWrap=true; field.selectable=false; field.mouseEnabled=false;
            parent.addChild(field); return field;
        }
        private function panel(parent:Sprite,x:Number,y:Number,w:Number,h:Number,color:uint,alpha:Number=.82):Sprite
        {
            var p:Sprite=new Sprite(); p.x=x; p.y=y;
            p.graphics.lineStyle(1,0x8F7959,.65); p.graphics.beginFill(color,alpha);
            p.graphics.drawRoundRect(0,0,w,h,8,8); p.graphics.endFill(); parent.addChild(p); return p;
        }
        private function button(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function,parent:Sprite=null):TextField
        {
            var p:Sprite=panel(parent||content,x,y,w,48,enabled?0x273B43:0x222426);
            p.alpha=enabled?1:.5; p.buttonMode=enabled;
            var label:TextField=text(p,title,12,8,w-20,20);
            if(enabled) {
                controller.registerControl(p,title,callback);
                p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{p.alpha=.82;});
                p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{p.alpha=1;});
                p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{ uiSound();callback(); });
            }
            return label;
        }
        private function rowGeometry(side:int,zone:int):Object
        {
            var ordinal:int=side==1?(zone==1?0:zone==2?1:2):(zone==4?0:zone==2?1:2);
            var top:Number=skin==1?(side==1?557:262):(side==1?552:224);
            var spacing:Number=skin==1?93:103;
            return {x:skin==1?565:548,y:top+ordinal*spacing,w:skin==1?793:846,h:skin==1?82:92};
        }
        private function canAct():Boolean
        { return !detailOpen && !pileOpen && ready && !editingDeck && !selectingDecks && !playing && requestId==0 && current==1 && (flags&1)==0 && (flags&12)==0 && (flags>>4)==0; }
        private function canPlayRow(side:int,zone:int):Boolean
        {
            if(!canAct()||selected==0)return false;
            var rule:Object=playRules[selected];
            if(rule&&rule.kind==2)return (rule.side==0||rule.side==side)&&((int(rule.rowMask)&zone)!=0);
            if(side!=placementSide())return false;
            var detail:Object=cardDetails[selected];
            if(!detail||detail.typeMask!=4)return true;
            var count:int=0;for each(var c:Object in cards)if(c.side==side&&c.zone==zone)count++;
            return count<9;
        }
        private function canDirectTarget(c:Object):Boolean
        {
            var rule:Object=playRules[selected];var detail:Object=cardDetails[c.id];
            return canAct()&&selected!=0&&rule&&rule.kind==1&&detail&&(c.zone&7)!=0
                &&(rule.side==0||rule.side==c.side)&&(detail.typeMask&rule.types)!=0
                &&(detail.tier&rule.tiers)!=0&&(int(c.tokens)&rule.ignore)==0
                &&(rule.maximum==0||c.power<=rule.maximum);
        }
        private function attachDirectTarget(p:Sprite,id:int):void
        {
            controller.registerControl(p,"",function():void{controllerCardAction(id);},null,null,"target");
            p.buttonMode=true;var expectedRevision:int=revision;
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{
                e.stopPropagation();if(revision!=expectedRevision)return;
                for each(var c:Object in cards)if(c.id==id&&canDirectTarget(c)){
                    submitBoard("OnBetaGwentBoardPlayTarget",[revision,selected,id]);return;
                }
            });
        }
        private function clearPlacementGhost():void
        {
            if(placementPreview)for each(var c:Object in cards)if(c.side==placementPreview.side&&c.zone==placementPreview.zone&&cardSprites[c.id])cardSprites[c.id].alpha=1;
            if(placementGhost&&placementGhost.parent)placementGhost.parent.removeChild(placementGhost);
            placementGhost=null;placementPreview=null;
        }
        private function insertionTarget(side:int,zone:int):Object
        {
            var g:Object=rowGeometry(side,zone);var units:Array=[];
            for each(var c:Object in cards)if(c.side==side&&c.zone==zone)units.push(c);
            units.sortOn("index",Array.NUMERIC);
            for each(c in units)if(mouseX<g.x+12+c.index*88+40)return {anchor:c.id,index:c.index,target:0,side:side,zone:zone,x:g.x+12+c.index*88,y:g.y,w:80,h:g.h};
            return {anchor:0,index:units.length,target:0,side:side,zone:zone,x:g.x+12+units.length*88,y:g.y,w:80,h:g.h};
        }
        private function submitPlacement(target:Object):void
        {
            if(!target)return;
            if(target.anchor>0){
                if(canPlacePending())submitBoard("OnBetaGwentDuelPlaceBefore",[revision,requestId,target.anchor]);
                else if(canPlaceSelected())submitBoard("OnBetaGwentBoardPlayBefore",[revision,selected,target.anchor]);
            }else chooseRow(target.side,target.zone);
        }
        private function placementSide():int
        {
            var id:int=placementCard&&canPlacePending()?placementCard.templateId:0;
            if(!canPlacePending())for each(var c:Object in cards)if(c.id==selected)id=c.templateId;
            var definition:Object=BetaGwentFullCatalog.find(id);if(definition)return definition.spy?2:1;
            return 1;
        }
        private function showPlacementGhost(target:Object):void
        {
            if(!target||target.target>0||(!canPlaceSelected()&&!canPlacePending())){clearPlacementGhost();return;}
            if(placementPreview&&placementPreview.side==target.side&&placementPreview.zone==target.zone&&placementPreview.anchor==target.anchor)return;
            clearPlacementGhost();
            var c:Object=placementCard;
            if(!canPlacePending()){c=null;for each(var hand:Object in cards)if(hand.id==selected)c=hand;}
            if(!c)return;var g:Object=rowGeometry(target.side,target.zone);var units:Array=[];var index:int=target.index;
            for each(var unit:Object in cards)if(unit.side==target.side&&unit.zone==target.zone){units.push(unit);if(unit.id==target.anchor)index=unit.index;}
            if(target.anchor==0)index=units.length;
            var step:Number=Math.min(88,(g.w-24)/(units.length+1));var width:Number=step-8;
            placementPreview=target;placementGhost=new Sprite();dragLayer.addChild(placementGhost);
            placementGhost.mouseEnabled=false;placementGhost.mouseChildren=false;
            for each(unit in units){
                if(cardSprites[unit.id])cardSprites[unit.id].alpha=0;
                var u:Sprite=panel(placementGhost,g.x+12+(unit.index>=index?unit.index+1:unit.index)*step,g.y+4,width,g.h-8,0x15343E,.95);
                if((int(unit.tokens)&8)!=0)paintCardBack(u,width,g.h-8,unit.side);else paintArt(u,unit.templateId,width-6,g.h-14);
                text(u,(int(unit.tokens)&8)!=0?"?":String(unit.power),5,1,width-8,21,powerColor(unit));
            }
            var x:Number=g.x+12+index*step;
            var ghost:Sprite=panel(placementGhost,x,g.y+4,width,g.h-8,0x214C59,.95);
            paintArt(ghost,c.templateId,width-6,g.h-14);ghost.alpha=.52;
            placementGhost.graphics.lineStyle(3,0xD9FFF5,1);placementGhost.graphics.drawRect(x,g.y+4,width,g.h-8);
            placementGhost.graphics.moveTo(x+width/2,g.y-3);placementGhost.graphics.lineTo(x+width/2,g.y-15);
            var rowName:String=target.zone==1?"Ближний ряд":target.zone==2?"Дальний ряд":"Осадный ряд";
            var label:Sprite=panel(placementGhost,g.x,g.y-36,g.w,30,0x10191F,.98);
            text(label,rowName+" · позиция "+(index+1)+" / "+(units.length+1)+" · "+c.title+" · нажмите, чтобы разместить",10,3,g.w-20,17,0xD9FFF5).height=27;
            if(c.templateId==132104){
                var frostRow:Object=rowGeometry(2,target.zone);
                placementGhost.graphics.lineStyle(3,0xA3E9FF,.95);placementGhost.graphics.beginFill(0x8ED7FF,.18);
                placementGhost.graphics.drawRect(frostRow.x,frostRow.y,frostRow.w,frostRow.h);placementGhost.graphics.endFill();
                text(placementGhost,"МОРОЗ КАРАНТИРА · ряд напротив",frostRow.x+8,frostRow.y+3,frostRow.w-16,17,0xD5F6FF);
            }
        }
        private function updatePlacementHover():void
        {
            if(!canPlaceSelected()&&!canPlacePending()){clearPlacementGhost();return;}
            var side:int=placementSide();
            for(var zone:int=1;zone<=4;zone*=2)if(rowEnabled(side,zone)){
                var g:Object=rowGeometry(side,zone);
                if(mouseX>=g.x&&mouseX<=g.x+g.w&&mouseY>=g.y&&mouseY<=g.y+g.h){showPlacementGhost(insertionTarget(side,zone));return;}
            }
            clearPlacementGhost();
        }
        private function canSelectRow(side:int,zone:int):Boolean
        {
            if(isCaranthirChoice())return ready&&!playing&&!detailOpen&&side==2&&zone==rowMode-15;
            if(detailOpen||!ready || playing || !rowRequest || requestId==0)return false;
            if(rowMode==3||rowMode==9)return side==2;
            if(rowMode==10)return side==2&&(zone==1||zone==2);
            if(rowMode==8)return side==1;
            if(!leaderRow&&rowMode!=4)return true;
            if(side!=placementSide())return false;
            var count:int=0;
            for each(var c:Object in cards)if(c.side==side&&c.zone==zone)count++;
            return count<9;
        }
        private function paintArt(parent:Sprite,id:int,w:Number,h:Number,x:Number=3,y:Number=3):Boolean
        {
            var view:Sprite=BetaGwentCardArt.view(id,w,h);
            if(!view)return false;
            view.x=x;view.y=y;parent.addChild(view);return true;
        }
        private function render():void
        {
            clearPlacementGhost();previousPoses=displayedCards;
            animations=[];pendingImpacts=[];cardSprites={}; animationFrame=0;animationStarted=getTimer();
            weatherEffects=[];
            hoverCardId=0;hoveredCard=null;hoveredDetail=null;
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(choiceLayer.numChildren)choiceLayer.removeChildAt(0);
            while(content.numChildren) content.removeChildAt(0);
            if(kegOpen){drawKeg();return;}
            if(browsingCatalog){drawCatalog();return;}
            if(editingDeck){drawDeckEditor();if(pendingKeg||entryMode==1&&unopenedKegs>0)editorSmallButton(content,pendingKeg?"Продолжить выбор":"Бочки · "+unopenedKegs,960,44,276,42,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});return;}
            if(selectingDecks){drawDeckSelection();return;}
            if(entryMode==1){text(content,"Открытие редактора колод…",96,88,1720,30,0xE8D3A6);return;}
            panel(content,16,12,1888,64,0x111315,.92);
            text(content,"BETA GWENT 0.9.24",36,24,440,28);
            var ownDeck:Object=deckOption(ownPreset);var enemyDeck:Object=deckOption(enemyPreset);
            text(content,ownDeck&&enemyDeck?ownDeck.title+"  /  "+enemyDeck.title:"Дуэль · карты Beta 0.9.24 · поле DIY",460,28,820,22,0xCFB176);
            text(content,"Раунд "+round+"  ·  "+(templateChoice?(rowMode==13?"Выбор режима":rowMode==7?"Дагон":"Рассвет"):pileChoice?(rowMode==14?"Выбор карты для способности":"Выбор карты для розыгрыша"):handPowerChoice?"Выбор силы из руки":graveyardChoice?"Поглощение из сброса":requestKind==1?"Замена карт":current==1?"Ваш ход":current==2?"Ход соперника":"Ожидание"),1320,26,560,24);
            profile(2,100,225,0x532723); profile(1,100,575,0x193E53);
            drawRows(); drawCards(); drawPendingPlacement();
            for each(var effect:Object in weatherEffects)content.addChild(effect.sprite);
            animateWeather(null);drawBacks();drawVisualCue();
            if(rewardMessage&&(flags>>4)>0)text(content,rewardMessage,510,820,970,25,0xE8D3A6).height=90;
            panel(content,1510,190,360,720,0x111619,.9);
            text(content,"ПАРТИЯ",1532,210,320,20,0xCFB176);
            var statusText:TextField=text(content,isCaranthirChoice()?"Мороз попадёт в ряд напротив Карантира. Можно переместить подсвеченный отряд или подтвердить этот ряд без перемещения. LB / RB — выбрать ряд.":requestId>0?requestMessage:message,1532,254,312,20);
            statusText.height=108;
            text(content,"ПОСЛЕДНИЕ ДЕЙСТВИЯ",1532,366,312,13,0xCFB176);
            var recent:Array=[];
            for(var historyIndex:int=0;historyIndex<Math.min(3,actionHistory.length);historyIndex++){
                var entry:String=actionHistory[historyIndex];recent.push(entry.length>45?entry.substr(0,42)+"…":entry);
            }
            var history:TextField=text(content,recent.join("\n"),1532,388,312,14,0xD9D6CB);history.height=55;
            if(playing)button("Пропустить анимацию",1532,450,312,true,skipReplay);
            else if(requestId>0&&requestFinish) button(isCaranthirChoice()?"Мороз без перемещения":templateChoice?"Выберите вариант":pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):handPowerChoice?"Выберите отряд":graveyardChoice?"Без поглощения":requestKind==1?"Начать раунд":leaderRow?"Отмена":"Без цели",1532,450,312,ready&&requestFinish&&(!rowRequest||leaderRow||rowMode==3||rowMode==1||rowMode>=8),requestAction("OnBetaGwentRequestFinish"));
            else if(requestId>0)text(content,"Выбор обязателен",1532,460,312,22,0xF5D77F).height=45;
            else button("Пас",1532,450,312,canAct(),function():void{submitBoard("OnBetaGwentBoardPass",[revision]);});
            button((flags&4)!=0&&(flags>>4)==0?"Следующий раунд автоматически":"Следующий раунд",1532,510,312,false,function():void{});
            inspection=text(content,"Наведите на карту.\nI или Shift + клик — полное описание.",1532,570,312,19,0xD8D0BB);
            inspection.height=116;
            button("Повторить",1532,690,150,ready&&entryMode!=2,function():void{submitBoard("OnBetaGwentBoardRematch",[serverRevision]);});
            button(entryMode==2&&(flags>>4)==0?"Сдаться":"Закрыть",1694,690,150,connected,function():void{send("OnBetaGwentBoardClose",[]);});
            button("Выбор колод",1532,748,312,ready&&entryMode!=2,function():void{submitBoard("OnBetaGwentBoardRestart",[serverRevision]);});
            button("Доска 1",1532,806,150,true,function():void{changeSkin(1);render();});
            button("Доска 2",1694,806,150,true,function():void{changeSkin(2);render();});
            text(content,"Соперник ходит автоматически.\nПобеда — два выигранных раунда.",1532,862,312,16,0xB9B4A9);
            panel(content,1510,918,360,150,0x111619,.9);
            tempoLabel=button("Темп: "+animationTempo+"×",1532,930,150,true,cycleTempo);
            motionLabel=button(reducedMotion?"Эффекты: кратко":"Эффекты: полно",1694,930,150,true,toggleMotion);
            tempoLabel.defaultTextFormat=new TextFormat("$NormalFont",17,0xF1E8D3);tempoLabel.text=tempoLabel.text;
            motionLabel.defaultTextFormat=new TextFormat("$NormalFont",15,0xF1E8D3);motionLabel.text=motionLabel.text;
            button(soundEnabled?"Звук: вкл":"Звук: выкл",1532,990,150,true,toggleSound);
            button(!betaAudioAvailable?(betaAudioInstalled?"Фразы: банк не загружен":"Фразы: ждут банк"):voiceEnabled?"Фразы: вкл":"Фразы: выкл",1694,990,150,betaAudioAvailable,toggleVoice);
            var controls:TextField=text(content,"← → цель · ↑ ↓ ряд · Enter — выбор\nF — завершить · Esc — отмена\nP — пас · L — лидер · Space — пропуск",1532,1042,312,12,0xB9B4A9);controls.height=38;
            if(!playing&&requestId>0 && requestKind==1) drawChoices();
            updateFocusedInspection();
            if(!playing&&requestId>0){
                panel(content,484,176,976,43,0x10191F,.97);
                text(content,requestInstruction(),498,180,946,22,0xF5D77F).height=36;
            }
            if(focusedRow>0&&(canPlaceSelected()||canPlacePending())&&rowEnabled(focusedSide,focusedRow)){
                showPlacementGhost({anchor:0,index:0,target:0,side:focusedSide,zone:focusedRow});
            }
        }
        private function requestInstruction():String
        {
            if(requestKind==1){
                if(pileChoice)return (rowMode==14?"Выберите карту для способности":"Выберите карту для розыгрыша")+(requestFinish?"":" — пропуск недоступен");
                if(templateChoice)return "Выберите один вариант способности";
                if(handPowerChoice)return "Выберите подсвеченную карту в руке";
                if(graveyardChoice)return "Выберите карту в сбросе";
                return "Замените карты или нажмите «Начать раунд»";
            }
            if(canPlacePending())return "Разместите отряд: свой ряд или союзник для вставки перед ним";
            if(rowRequest)return "Выберите подсвеченный ряд для способности";
            var friendly:Boolean=false;var enemy:Boolean=false;
            for each(var option:Object in requestCards)for each(var live:Object in cards)if(live.id==option.id){
                if(live.side==1)friendly=true;else enemy=true;break;
            }
            return "Укажите "+(enemy&&!friendly?"отряд противника":friendly&&!enemy?"союзный отряд":"подходящий отряд")+
                " — яркая рамка показывает допустимые цели";
        }
        private function markTarget(parent:Sprite,w:Number,h:Number,tint:uint,focused:Boolean):void
        {
            var mark:Sprite=new Sprite();mark.mouseEnabled=false;mark.mouseChildren=false;
            mark.graphics.lineStyle(focused?6:4,tint,1);mark.graphics.drawRect(-2,-2,w+4,h+4);
            mark.graphics.lineStyle(2,0x101315,1);mark.graphics.drawRect(3,3,w-6,h-6);
            mark.graphics.beginFill(tint,1);mark.graphics.moveTo(w/2-9,-12);
            mark.graphics.lineTo(w/2+9,-12);mark.graphics.lineTo(w/2,-3);mark.graphics.endFill();
            parent.addChild(mark);
        }
        private function canInspectPile():Boolean
        { return ready&&!playing&&!selectingDecks&&!editingDeck&&!browsingCatalog&&dragId==0; }
        private function inspectPile(side:int,zone:int):void
        {
            if(!canInspectPile()||!((zone==32&&(side==1||side==2))||(zone==16&&side==1)))return;
            send("OnBetaGwentInspectPile",[revision,side,zone]);
        }
        public function beginPileView(rev:int,side:int,zone:int,count:int):void
        {
            if(rev!=revision||!canInspectPile()||!((zone==32&&(side==1||side==2))||(zone==16&&side==1)))return;
            closePileView();pileView={revision:rev,side:side,zone:zone,count:count,cards:[]};
            pilePage=0;pileTier=0;pilePicked=null;
        }
        public function pushPileCard(templateId:int,title:String,description:String,power:int,armor:int,tier:int,tokens:int,timer:int,typeMask:int):void
        {
            if(!pileView)return;
            pileView.cards.push({templateId:templateId,title:title,description:description,power:power,armor:armor,
                tier:tier,tokens:tokens,timer:timer,typeMask:typeMask});
        }
        public function finishPileView(rev:int):void
        {
            if(!pileView||rev!=revision||rev!=pileView.revision||pileView.cards.length!=pileView.count){closePileView();return;}
            // Stable within an opening; the server already shuffled a copy independently of gameplay.
            for each(var tier:int in [8,4,2])for each(var c:Object in pileView.cards)if((c.tier&tier)!=0&&pileTier==0)pileTier=tier;
            if(pileTier==0)pileTier=2;
            pileOpen=true;hoverCardId=0;
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            drawPileView();
        }
        public function pushPilePowerBase(normalPower:int):void
        { if(pileView&&pileView.cards.length>0)pileView.cards[pileView.cards.length-1].normalPower=normalPower; }
        private function closePileView():void
        {
            pileOpen=false;pileView=null;pilePicked=null;pileDetail=null;pilePicture=null;
            while(pileLayer.numChildren)pileLayer.removeChildAt(0);
        }
        private function pileGroupAction(tier:int):Function
        { return function():void{pileTier=tier;pilePage=0;pilePicked=null;drawPileView();}; }
        private function pileCardInspect(tile:Sprite,c:Object):void
        {
            controller.registerControl(tile,c.title,function():void{showPileCard(c);},c,{description:c.description},"card");
            tile.buttonMode=true;
            tile.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{showPileCard(c);});
            tile.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();showPileCard(c);});
        }
        private function showPileCard(c:Object):void
        {
            if(!pileOpen||!pileDetail||!pilePicture)return;pilePicked=c;
            while(pilePicture.numChildren)pilePicture.removeChildAt(0);
            paintArt(pilePicture,c.templateId,188,262,0,0);
            pileDetail.text=c.title+"\nТеги: "+(BetaGwentCardTags.text(c.templateId)||"—")+
                (c.typeMask==4?"\nСила: "+c.power+(c.armor>0?" · броня: "+c.armor:""):"\nОсобая карта")+
                ((int(c.tokens)&4)!=0?"\nБлокировка":"")+(int(c.timer)>=0?"\nСчётчик: "+c.timer:"")+"\n\n"+c.description;
            pileDetail.scrollV=1;
        }
        private function drawPileView():void
        {
            if(!pileOpen||!pileView)return;
            while(pileLayer.numChildren)pileLayer.removeChildAt(0);
            panel(pileLayer,0,0,1920,1080,0x000000,.76);
            var window:Sprite=panel(pileLayer,130,80,1660,920,0x101A20,.99);
            var name:String=pileView.zone==16?"Ваша колода":pileView.side==1?"Ваш сброс":"Сброс соперника";
            text(window,name+" · "+pileView.count+" карт",32,22,1200,32,0xE8D3A6).height=48;
            text(window,pileView.zone==16?"Карты сгруппированы по цвету. Порядок случайный и не показывает порядок добора.":
                "Просмотр карт в сбросе. Наведите на карту, чтобы прочитать её способность.",32,78,1450,20).height=52;
            editorSmallButton(window,"Закрыть · Esc",1392,24,232,42,true,closePileView);
            var group:Array=[];var tiers:Array=[8,4,2];var names:Array=["Золото","Серебро","Бронза"];
            for(var t:int=0;t<tiers.length;t++){
                var count:int=0;for each(var card:Object in pileView.cards)if((card.tier&tiers[t])!=0)count++;
                editorSmallButton(window,(pileTier==tiers[t]?"● ":"")+names[t]+" · "+count,32+t*230,140,216,40,true,pileGroupAction(tiers[t]));
            }
            for each(var c:Object in pileView.cards)if((c.tier&pileTier)!=0)group.push(c);
            var pages:int=Math.max(1,Math.ceil(group.length/12));pilePage=Math.max(0,Math.min(pilePage,pages-1));
            for(var i:int=pilePage*12;i<Math.min(group.length,pilePage*12+12);i++){
                c=group[i];var ordinal:int=i-pilePage*12;
                var tile:Sprite=panel(window,32+(ordinal%6)*177,204+int(ordinal/6)*270,158,248,0x193442,.98);
                tile.graphics.lineStyle(2,editorTierColor(c.tier));tile.graphics.drawRect(1,1,156,246);
                paintArt(tile,c.templateId,152,212,3,3);
                var strength:Sprite=panel(tile,5,5,146,29,0x0C171D,.84);
                text(strength,c.typeMask==4?"Сила: "+c.power+(c.armor>0?" · "+c.armor:""):"Особая карта",5,2,136,18,powerColor(c)).height=26;
                var caption:Sprite=panel(tile,5,197,148,46,0x0C171D,.9);
                text(caption,c.title,5,2,138,17).height=42;pileCardInspect(tile,c);
            }
            if(group.length==0)text(window,pileView.count==0?(pileView.zone==16?"Колода пуста.":"Сброс пуст."):"В этой группе карт нет.",40,260,1000,28).height=65;
            var detail:Sprite=panel(window,1120,204,504,608,0x18282F,.98);
            pilePicture=new Sprite();pilePicture.x=158;pilePicture.y=16;detail.addChild(pilePicture);
            pileDetail=text(detail,"Выберите карту для просмотра.",22,298,460,21);pileDetail.height=258;
            editorSmallButton(detail,"↑",414,565,30,30,true,function():void{pileDetail.scrollV--;});
            editorSmallButton(detail,"↓",454,565,30,30,true,function():void{pileDetail.scrollV++;});
            if(!pilePicked&&group.length>0)pilePicked=group[pilePage*12];if(pilePicked)showPileCard(pilePicked);
            text(window,"Страница "+(pilePage+1)+" / "+pages+" · ← →",300,847,620,22).height=34;
            editorSmallButton(window,"←",32,840,110,44,pilePage>0,function():void{pilePage--;pilePicked=null;drawPileView();});
            editorSmallButton(window,"→",158,840,110,44,pilePage+1<pages,function():void{pilePage++;pilePicked=null;drawPileView();});
            text(window,"Просмотр не расходует ход. Колода соперника скрыта.",850,848,760,19,0xA7BDCA).height=32;
        }

        private function profile(side:int,x:Number,y:Number,color:uint):void
        {
            var p:Sprite=panel(content,x,y,280,225,color,.88);
            text(p,side==1?"Геральт":"Соперник",18,14,250,25);
            text(p,"Счёт: "+scores[side-1],18,58,172,34);
            text(p,"Раунды: "+crowns[side-1]+" / 2",18,116,172,24);
            for(var sealIndex:int=0;sealIndex<2;sealIndex++){
                var seal:Sprite=new Sprite();seal.mouseEnabled=false;seal.mouseChildren=false;p.addChild(seal);
                seal.x=34+sealIndex*29;seal.y=151;paintRoundSeal(seal,sealIndex<crowns[side-1],side==1?0x8BCFE6:0xE6AD86,10);
                if(activeCue&&activeCue.kind==6&&sealIndex>=previousCrowns[side-1]&&sealIndex<crowns[side-1]){
                    animations.push({sprite:seal,fromX:34+sealIndex*29,fromY:151,toX:34+sealIndex*29,toY:151,
                        fade:false,appear:true,remove:false,duration:480,delay:260,fromScaleX:2,fromScaleY:2,toScaleX:1,toScaleY:1});
                    seal.scaleX=seal.scaleY=2;seal.alpha=0;
                }
            }
            var pile:Sprite=new Sprite();pile.mouseEnabled=false;pile.mouseChildren=false;p.addChild(pile);
            pile.x=210;pile.y=196;paintCardBack(pile,25,23,side);
            paintArt(p,leaderIds[side-1],64,90,198,59);
            editorSmallButton(p,"Сброс: "+graves[side-1]+((flags&(side==1?1:2))!=0?" · ПАС":"")+" · "+(side==1?"G":"H"),12,163,180,28,canInspectPile(),function():void{inspectPile(side,32);});
            if(side==1)editorSmallButton(p,"Колода: "+deckCounts[0]+" · D",12,194,180,27,canInspectPile(),function():void{inspectPile(1,16);});
            else text(p,"Колода: "+deckCounts[1]+" · скрыта",18,194,178,17).height=27;
            var available:Boolean=side==1?leaderOne:leaderTwo;
            if(side==1) button(available?leaderTitle:"Лидер использован",x,y+245,280,canAct()&&available,function():void{submitBoard("OnBetaGwentBoardLeader",[revision]);});
        }
        private function drawRows():void
        {
            for(var side:int=1;side<=2;side++) for(var zone:int=1;zone<=4;zone*=2)
            {
                var geometry:Object=rowGeometry(side,zone);
                var hit:Sprite=new Sprite();hit.x=geometry.x;hit.y=geometry.y;
                var enabled:Boolean=rowEnabled(side,zone);
                hit.buttonMode=enabled;
                hit.graphics.beginFill(0x6FB8D9,enabled?0.2:0.01);
                hit.graphics.drawRect(0,0,geometry.w,geometry.h);hit.graphics.endFill();content.addChild(hit);
                for each(var hazard:Object in weatherRows) if(hazard.side==side&&hazard.zone==zone){
                    var key:String=side+":"+zone;
                    if(hazard.token==0){delete weatherBirths[key];continue;}
                    var tint:uint=hazard.token==1?0x99DCFF:hazard.token==2?0xE2DED1:hazard.token==16||hazard.token==32?0xE98145:hazard.token==128?0xDFC267:hazard.token==256?0xCBC3FF:hazard.token==2048?0xDB6477:hazard.token==512?0xBAA388:hazard.token==1024?0xE5AA54:0x86BFC8;
                    var weather:Sprite=new Sprite();weather.x=geometry.x;weather.y=geometry.y;
                    weather.mouseEnabled=false;weather.mouseChildren=false;
                    weather.graphics.lineStyle(2,tint,.85);weather.graphics.beginFill(tint,.14);
                    weather.graphics.drawRect(0,0,geometry.w,geometry.h);weather.graphics.endFill();content.addChild(weather);
                    var title:String=hazard.token==1?"МОРОЗ":hazard.token==2?"ТУМАН":hazard.token==16?"ЖАРА":hazard.token==32?"РАГНАРЕК":hazard.token==64?"ШТОРМ":hazard.token==128?"ЗОЛОТАЯ ПЕНА":hazard.token==256?"ПОЛНАЯ ЛУНА":hazard.token==2048?"КРОВАВАЯ ЛУНА":hazard.token==512?"ВОЛЧЬЯ ЯМА":hazard.token==1024?"МЕЧТА ДРАКОНА":"ДОЖДЬ";
                    var suffix:String=hazard.token==256?" · +"+hazard.damage:hazard.token==512||hazard.token==2048?" · контакт −"+hazard.damage:hazard.token==1024?" · взрыв −"+hazard.damage:" · "+hazard.damage+(hazard.token==4?" × 2":"");
                    text(content,title+suffix,geometry.x-150,geometry.y+2,146,13,tint);
                    if(!weatherBirths[key]||weatherBirths[key].token!=hazard.token)
                        weatherBirths[key]={token:hazard.token,start:getTimer()};
                    var particles:Sprite=new Sprite();particles.x=geometry.x;particles.y=geometry.y;
                    particles.mouseEnabled=false;particles.mouseChildren=false;
                    particles.scrollRect=new Rectangle(0,0,geometry.w,geometry.h);
                    weatherEffects.push({sprite:particles,w:geometry.w,h:geometry.h,token:hazard.token,
                        start:weatherBirths[key].start,phase:side*31+zone*19});
                    if(hazard.token==1||hazard.token==2||hazard.token==4||hazard.token==64)prepareNativeWeather(weatherEffects[weatherEffects.length-1]);
                }
                if(focusedRow==zone&&focusedSide==side&&enabled){
                    hit.graphics.lineStyle(3,0xF5E6A7,.9);hit.graphics.drawRect(2,2,geometry.w-4,geometry.h-4);
                }
                attachRow(hit,side,zone,true);
                var total:int=0;
                for each(var c:Object in cards) if(c.side==side&&c.zone==zone&&(int(c.tokens)&8)==0) total+=c.power;
                text(content,String(total),geometry.x-88,geometry.y+24,75,26);
            }
        }
        private function attachRow(hit:Sprite,side:int,zone:int,registerRow:Boolean=false):void
        {
            if(registerRow&&rowEnabled(side,zone)){
                if(canPlaceSelected()||canPlacePending())registerControllerPositions(side,zone);
                else {
                    var action:Function=controllerRowAction(side,zone);
                    // A separate target remains visible/focusable even with no
                    // units. Unit inspection must not replace this row action.
                    var rowTarget:Sprite=panel(content,hit.x-145,hit.y+hit.height-33,140,30,0x133E50,.96);
                    rowTarget.mouseEnabled=false;rowTarget.mouseChildren=false;
                    text(rowTarget,isCaranthirChoice()?"МОРОЗ · без движения":"ВЫБРАТЬ РЯД",5,4,130,12,0xD5F6FF).height=25;
                    controller.registerControl(rowTarget,(side==1?"Ваш ":"Вражеский ")+(zone==1?"ближний ряд":zone==2?"дальний ряд":"осадный ряд"),action,null,null,"row",{rowOnly:true,side:side,zone:zone});
                }
            }
            hit.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{
                if((canPlaceSelected()||canPlacePending())&&rowEnabled(side,zone))submitPlacement(insertionTarget(side,zone));else chooseRow(side,zone);
            });
        }
        private function canPlaceSelected():Boolean
        {
            var detail:Object=cardDetails[selected];
            if(!canAct()||requestId!=0||selected==0||!detail||detail.typeMask!=4)return false;
            for each(var c:Object in cards)if(c.id==selected)return c.side==1&&c.zone==8&&c.canPlay;
            return false;
        }
        private function canPlacePending():Boolean
        {
            return !detailOpen&&!pileOpen&&ready&&!selectingDecks&&!playing&&requestId>0&&requestPlayer==1&&requestKind==2&&(rowMode==2||rowMode==4);
        }
        private function drawPendingPlacement():void
        {
            if(!canPlacePending()||placementCard==null)return;
            var c:Object=placementCard;
            var p:Sprite=panel(content,484,926,80,140,0x173340,.96);
            paintArt(p,c.templateId,74,134);
            p.graphics.lineStyle(2,c.tier==8?0xD9B557:c.tier==4?0xCBD1D8:0x99735D);p.graphics.drawRect(0,0,80,140);
            panel(p,3,3,34,34,0x101315,.85);text(p,String(c.power),7,2,40,28,powerColor(c));
            panel(p,3,104,74,33,0x101315,.84);
            var caption:TextField=text(p,c.title,7,106,68,12);caption.height=32;
            text(content,c.title+" · сила "+c.power,586,932,670,25,powerColor(c));
            var hint:TextField=text(content,placementSide()==2?"Разместите шпиона в ряду соперника.\nНажмите отряд: вставить перед ним; пустое место: поставить в конец.":"Нажмите союзника: карта встанет перед ним.\nНажмите пустое место своего ряда: карта встанет в конец.",586,974,670,19);
            hint.text="Наведите на ряд: полупрозрачная карта показывает место вставки.\nКлик подтверждает эту позицию. Шпион размещается у соперника.";hint.height=78;
        }
        private function canPlaceBefore(c:Object):Boolean
        {
            if((!canPlaceSelected()&&!canPlacePending())||c.power<=0||c.side!=placementSide()||(c.zone!=1&&c.zone!=2&&c.zone!=4)||!rowEnabled(c.side,c.zone))return false;
            var detail:Object=cardDetails[c.id];if(!detail||detail.typeMask!=4)return false;
            var count:int=0;
            for each(var other:Object in cards)if(other.side==c.side&&other.zone==c.zone)count++;
            return count<9;
        }
        private function attachPlacement(p:Sprite,anchor:int):void
        {
            controller.registerControl(p,"",function():void{controllerCardAction(anchor);},null,null,"position",controllerPlacement(anchor));
            p.buttonMode=true;
            var expectedRevision:int=revision;
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{
                e.stopPropagation();
                if(revision!=expectedRevision)return;
                for each(var c:Object in cards)if(c.id==anchor){submitPlacement(insertionTarget(c.side,c.zone));return;}
            });
        }
        private function drawCards():void
        {
            var nextCards:Object={};
            var handCount:int=0;
            for each(var hand:Object in cards) if(hand.side==1&&hand.zone==8)handCount++;
            var step:Number=Math.min(112,970/Math.max(1,handCount));
            var handWidth:Number=step-8;
            for each(var c:Object in cards)
            {
                if(c.zone==8&&(c.side!=1||canPlacePending())) continue;
                if(c.zone!=8&&c.zone!=1&&c.zone!=2&&c.zone!=4) continue;
                var isHand:Boolean=c.zone==8;
                if(consumedVisualIds[c.id]&&!(activeCue&&activeCue.kind==11&&activeCue.target==c.id))continue;
                var g:Object=isHand?{x:484+c.index*step,y:selected==c.id?906:926,h:140}:rowGeometry(c.side,c.zone);
                var x:Number=isHand?g.x:g.x+12+c.index*88;
                var p:Sprite=panel(content,x,g.y+4,isHand?handWidth:80,isHand?140:g.h-8,c.side==1?0x173340:0x4B2925,.96);
                cardSprites[c.id]=p;
                if(isHand&&dragging&&c.id==dragId)p.alpha=.3;
                var cardWidth:Number=isHand?handWidth:80;
                var cardHeight:Number=isHand?140:g.h-8;
                var concealed:Boolean=!isHand&&(int(c.tokens)&8)!=0;
                if(concealed)paintCardBack(p,cardWidth,cardHeight,c.side);else paintArt(p,c.templateId,cardWidth-6,cardHeight-6);
                var before:Object=displayedCards[c.id];
                nextCards[c.id]={x:p.x,y:p.y,power:c.power,normalPower:c.normalPower,zone:c.zone,side:c.side,title:c.title,armor:c.armor,templateId:c.templateId,timer:c.timer,tokens:c.tokens,width:cardWidth,height:cardHeight,delta:before?c.power-before.power:0,armorDelta:before?c.armor-before.armor:0};
                var revealed:Boolean=before&&(int(before.tokens)&8)!=0&&!concealed&&!isHand;
                if(before && before.templateId==c.templateId&&!revealed) {
                    if(before.x!=p.x || before.y!=p.y) {
                        var flight:Boolean=before.zone==8&&!isHand;
                        animations.push({sprite:p,fromX:before.x,fromY:before.y,toX:p.x,toY:p.y,fade:false,remove:false,
                            duration:flight?480:isHand?160:280,arc:flight?36:0,betaFlight:flight,tilt:flight?(p.x>before.x?5:-5):0,
                            fromScaleX:flight?before.width/cardWidth:1,fromScaleY:flight?before.height/cardHeight:1,toScaleX:1,toScaleY:1});
                        p.x=before.x;p.y=before.y;
                        if(flight){p.scaleX=before.width/cardWidth;p.scaleY=before.height/cardHeight;}
                    }
                    if(before.power!=c.power || before.armor!=c.armor) {
                        var hitDelay:Number=activeCue&&activeCue.kind==2?cueImpactDelay()*animationTempo:0;
                        var flash:Sprite=new Sprite();flash.mouseEnabled=false;
                        flash.graphics.beginFill(c.power>before.power?0x71C496:c.power<before.power?0xDF705E:0x83C5E5,.5);
                        flash.graphics.drawRect(0,0,isHand?handWidth:80,isHand?140:g.h-8);flash.graphics.endFill();
                        p.addChild(flash);
                        animations.push({sprite:flash,fromX:0,fromY:0,toX:0,toY:0,fade:true,remove:true,duration:220,delay:hitDelay,hideBeforeDelay:true});
                        var delta:int=c.power-before.power;var armorDelta:int=c.armor-before.armor;
                        var label:String=delta!=0?(delta>0?"+":"")+delta:"";
                        if(armorDelta!=0)label+=(label?" · ":"")+"Б "+(armorDelta>0?"+":"")+armorDelta;
                        var number:Sprite=new Sprite();number.mouseEnabled=false;number.mouseChildren=false;
                        text(number,label,0,0,100,30,delta>0?0xA5F5B8:delta<0?0xFFB09B:0xBCEAFF);
                        p.addChild(number);number.x=12;number.y=-8;
                        animations.push({sprite:number,fromX:12,fromY:-8,toX:12,toY:-48,fade:true,remove:true,duration:260,delay:hitDelay,hideBeforeDelay:true});
                        if(delta<0&&!isHand&&!reducedMotion&&before.x==x&&before.y==g.y+4)
                            animations.push({sprite:p,fromX:x,fromY:g.y+4,toX:x,toY:g.y+4,shake:5,remove:false,duration:180,delay:hitDelay});
                        if(armorDelta<0&&!reducedMotion)drawArmorHit(p,cardWidth,armorDelta);
                    }
                } else if(before && (before.templateId!=c.templateId||revealed)) {
                    // Same registry card transforms in its row; cross-fade the art locally.
                    var oldArt:Sprite=panel(content,p.x,p.y,cardWidth,cardHeight,0x18343D,.92);
                    oldArt.mouseEnabled=false;oldArt.mouseChildren=false;
                    if((int(before.tokens)&8)!=0&&(before.zone&7)!=0)paintCardBack(oldArt,cardWidth,cardHeight,before.side);
                    else paintArt(oldArt,before.templateId,cardWidth-6,cardHeight-6);
                    animations.push({sprite:oldArt,fromX:p.x,fromY:p.y,toX:p.x+cardWidth/2,toY:p.y,fade:true,remove:true,
                        duration:250,fromScaleX:1,fromScaleY:1,toScaleX:.04,toScaleY:1});
                    animations.push({sprite:p,fromX:p.x+cardWidth/2,fromY:p.y,toX:p.x,toY:p.y,fade:false,remove:false,appear:true,
                        duration:250,delay:170,fromScaleX:.04,fromScaleY:1,toScaleX:1,toScaleY:1});
                    p.x+=cardWidth/2;p.scaleX=.04;p.alpha=0;
                } else {
                    var originX:Number=p.x;
                    var originY:Number=p.y;
                    if(isHand&&activeCue&&activeCue.kind==14){originX=310;originY=776;}
                    if(!isHand){
                        var summoner:Object=activeCue?(displayedCards[activeCue.source]?displayedCards[activeCue.source]:previousPoses[activeCue.source]?previousPoses[activeCue.source]:departedPoses[activeCue.source]):null;
                        if(activeCue&&(activeCue.kind==15||activeCue.title.indexOf("Из колоды")>=0)){originX=310;originY=c.side==1?776:426;}
                        else if(summoner&&activeCue.source!=c.id){originX=summoner.x;originY=summoner.y;}
                        else if(c.side==2){originX=630+Math.min(9,enemyHand)*54;originY=96;}
                        else{originX=330;originY=730;}
                    }
                    animations.push({sprite:p,fromX:originX,fromY:originY,toX:p.x,toY:p.y,fade:false,remove:false,appear:true,
                        duration:isHand?260:480,arc:isHand?0:36,betaFlight:true,tilt:originX<p.x?5:-5,fromScaleX:.8,fromScaleY:.8,toScaleX:1,toScaleY:1});
                    p.x=originX;p.y=originY;p.alpha=0;
                }
                var detail:Object=cardDetails[c.id];
                if(detail){p.graphics.lineStyle(2,detail.tier==8?0xD9B557:detail.tier==4?0xCBD1D8:0x99735D);p.graphics.drawRect(0,0,isHand?handWidth:80,isHand?140:g.h-8);}
                if(selected==c.id){p.graphics.lineStyle(4,0x80CBD5);p.graphics.drawRect(0,0,handWidth,140);}
                else if(keyboardFocusId==c.id){p.graphics.lineStyle(4,0xF5E6A7);p.graphics.drawRect(-2,-2,cardWidth+4,cardHeight+4);}
                var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;
                var badge:Sprite=panel(p,3,3,34,34,0x101315,.85);badge.mouseEnabled=false;
                var powerValue:String=concealed?"?":c.power>0||!isHand?String(c.power):"★";
                var powerBadge:TextField=text(p,powerValue,7,2,40,isHand?28:25,concealed?0xE9C46A:powerColor(c));
                if(before&&!concealed&&before.power!=c.power&&activeCue&&activeCue.kind==2&&!reducedMotion){
                    powerBadge.text=String(before.power);powerBadge.textColor=powerColor(before);
                    pendingImpacts.push({field:powerBadge,value:powerValue,tint:powerColor(c)});
                }
                var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,isHand?13:11);caption.height=32;
                if(concealed){
                    var ambushBadge:Sprite=panel(p,2,cardHeight*.42,cardWidth-4,19,0x101315,.97);ambushBadge.mouseEnabled=false;ambushBadge.mouseChildren=false;
                    text(ambushBadge,"ЗАСАДА",3,1,cardWidth-8,12,0xF5D77F).height=17;
                }else if(!isHand&&isAmbush(c.templateId))text(p,"РАСКРЫТА",3,cardHeight*.42,cardWidth-6,11,0xA5F5B8).height=18;
                if(c.armor>0||before&&before.armor>0&&activeCue&&activeCue.kind==2&&!reducedMotion) {
                    var armorBadge:Sprite=panel(p,cardWidth-34,3,30,24,0x173B50,.9);armorBadge.mouseEnabled=false;
                    var armorValue:TextField=text(p,c.armor>0?"Б"+c.armor:"",cardWidth-32,4,30,14,0x9CE3EF);
                    if(before&&before.armor!=c.armor&&activeCue&&activeCue.kind==2&&!reducedMotion){
                        armorValue.text=before.armor>0?"Б"+before.armor:"";
                        pendingImpacts.push({field:armorValue,value:c.armor>0?"Б"+c.armor:"",tint:0x9CE3EF});
                    }
                }
                if((int(c.tokens)&4)!=0)paintLock(p,cardWidth-25,31);
                if((int(c.tokens)&1)!=0)text(p,"∞",cardWidth-24,52,22,20,0xC8ED96);
                if((int(c.tokens)&512)!=0){
                    var doomedBadge:Sprite=panel(p,3,39,20,19,0x271715,.9);doomedBadge.mouseEnabled=false;
                    text(p,"×",6,38,18,18,0xF2AC86);
                }
                if(int(c.timer)>=0)paintTimer(p,3,40,int(c.timer),(int(c.tokens)&4)!=0);
                attachInspect(p,c,detail,cardWidth,cardHeight);
                if(!isHand&&!canPlaceBefore(c)&&!canDirectTarget(c)&&((rowRequest&&requestId>0)||(canAct()&&playRules[selected]&&playRules[selected].kind==2)))attachRow(p,c.side,c.zone);
                var target:Object=requestKind==2?findRequestCard(c.id):null;
                if(requestId>0 && target!=null)
                {
                    markTarget(p,cardWidth,cardHeight,c.side==2?0xFFAA75:0x87F5DB,keyboardFocusId==c.id);
                    attachRequestCard(p,c.id);
                }
                else if(!playing&&requestId>0&&requestKind==2&&!rowRequest&&!canPlacePending())p.alpha=.38;
                else if(isHand && requestId==0) attachCard(p,c.id,c.canPlay);
                else if(!isHand&&canDirectTarget(c)) {
                    markTarget(p,cardWidth,cardHeight,0x87F5DB,keyboardFocusId==c.id);
                    attachDirectTarget(p,c.id);
                }
                else if(!isHand&&canPlaceBefore(c)) {
                    p.graphics.lineStyle(3,0x9CF0F5);
                    p.graphics.moveTo(-4,4);p.graphics.lineTo(-4,cardHeight-4);
                    p.graphics.moveTo(-7,10);p.graphics.lineTo(-4,5);p.graphics.lineTo(-1,10);
                    attachPlacement(p,c.id);
                }
            }
            for(var oldId:String in displayedCards) {
                var previous:Object=displayedCards[oldId];
                if(!nextCards[oldId]&&previous.zone!=8){
                    // A deathwish may arrive several frames after the death/move itself.
                    if(!departedPoses.hasOwnProperty(oldId))departedOrder.push(oldId);
                    departedPoses[oldId]=previous;
                    while(departedOrder.length>96)delete departedPoses[departedOrder.shift()];
                }
                if(nextCards[oldId] || previous.zone==8 || consumedVisualIds[oldId])continue;
                var fading:Sprite=panel(content,previous.x,previous.y,80,84,previous.side==1?0x173340:0x4B2925,.9);
                fading.mouseEnabled=false;fading.mouseChildren=false;
                paintArt(fading,previous.templateId,74,78);
                var deathBand:Sprite=panel(fading,3,52,74,29,0x101315,.85);deathBand.mouseEnabled=false;
                text(fading,String(previous.power),8,4,68,26,powerColor(previous));
                var deathTitle:TextField=text(fading,previous.title,8,53,65,11);deathTitle.height=28;
                var vanishes:Boolean=(int(previous.tokens)&512)!=0;
                animations.push({sprite:fading,fromX:previous.x,fromY:previous.y,
                    toX:vanishes?previous.x:260,toY:vanishes?previous.y-32:previous.side==1?748:398,
                    fade:true,remove:true,duration:vanishes?300:400,arc:vanishes?0:28,
                    delay:activeCue&&activeCue.kind==17?Math.min(320,previous.x%400)*.65:0,
                    fromScaleX:1,fromScaleY:1,toScaleX:vanishes?0.5:0.25,toScaleY:vanishes?0.5:0.25});
            }
            // Once the card actually leaves the active rows, release its visual tombstone.
            for(var consumedId:String in consumedVisualIds){
                var stillOnField:Boolean=false;
                for each(var liveCard:Object in cards)if(String(liveCard.id)==consumedId&&(liveCard.zone&7)!=0){stillOnField=true;break;}
                if(!stillOnField)delete consumedVisualIds[consumedId];
            }
            displayedCards=nextCards;
            text(content,canPlacePending()?"Нажмите союзника: поставить перед ним. Пустое место своего ряда: поставить в конец.":rowRequest&&requestId>0?(leaderRow?"Выберите свой подсвеченный ряд для лидера.":"Выберите любой подсвеченный ряд."):requestId>0 && requestKind==2?"Нажмите подсвеченную карту, чтобы применить способность.":
                selected==0?"Выберите или перетащите карту из руки. Перед союзником — вставка слева.":canPlaceSelected()?"Нажмите свой отряд: поставить перед ним. Пустое место ряда: поставить в конец.":playRules[selected]&&playRules[selected].kind==1?"Нажмите подходящий отряд или перетащите особую карту прямо на него.":playRules[selected]&&playRules[selected].kind==2?"Нажмите подходящий ряд или перетащите особую карту прямо в ряд.":"Выберите свой ряд для выбранной карты",485,878,970,18);
        }
        private function animateCards(e:Event):void
        {
            var complete:Boolean=true;var elapsed:Number=getTimer()-animationStarted;
            for(var impactIndex:int=pendingImpacts.length-1;impactIndex>=0;impactIndex--){
                var pending:Object=pendingImpacts[impactIndex];
                if(elapsed<cueImpactDelay())continue;
                pending.field.text=pending.value;pending.field.textColor=pending.tint;
                pendingImpacts.splice(impactIndex,1);
            }
            if(animations.length==0)return;
            for each(var motion:Object in animations) {
                if(motion.finished)continue;
                var duration:Number=reducedMotion?60:(motion.duration?motion.duration:280)/animationTempo;
                var delay:Number=reducedMotion?0:(motion.delay?motion.delay:0)/animationTempo;
                if(playing){delay=Math.min(delay,Math.max(0,frameDuration-70/animationTempo));duration=Math.min(duration,Math.max(40,frameDuration-delay-10));}
                var progress:Number=Math.max(0,Math.min(1,(elapsed-delay)/Math.max(40,duration)));
                var eased:Number=1-Math.pow(1-progress,3);
                // Beta movement has acceleration, deceleration and angular return.
                // GFx uses a 2D approximation; Unity serialized curves are separate.
                if(motion.betaFlight)eased=progress*progress*progress*(progress*(progress*6-15)+10);
                var sprite:Sprite=motion.sprite;
                sprite.x=motion.fromX+(motion.toX-motion.fromX)*eased;
                sprite.y=motion.fromY+(motion.toY-motion.fromY)*eased;
                if(motion.shake&&!reducedMotion)sprite.x+=Math.sin(progress*Math.PI*6)*motion.shake*(1-progress);
                if(motion.arc&&!reducedMotion)sprite.y-=Math.sin(Math.PI*progress)*motion.arc;
                if(motion.fromScaleX!=null){
                    sprite.scaleX=motion.fromScaleX+(motion.toScaleX-motion.fromScaleX)*eased;
                    sprite.scaleY=motion.fromScaleY+(motion.toScaleY-motion.fromScaleY)*eased;
                }
                if(motion.counter){
                    var counter:TextField=motion.counter;
                    counter.text=String(Math.round(motion.fromValue+(motion.toValue-motion.fromValue)*eased));
                }
                if(motion.fromRotation!=null)sprite.rotation=motion.fromRotation+(motion.toRotation-motion.fromRotation)*eased;
                if(motion.betaFlight&&!reducedMotion){
                    sprite.rotation=Math.sin(Math.PI*progress)*(motion.tilt?motion.tilt:4);
                    var lift:Number=1+.055*Math.sin(Math.PI*progress);
                    sprite.scaleX*=lift;sprite.scaleY*=lift;
                }
                if(motion.fade)sprite.alpha=1-progress;
                else if(motion.appear)sprite.alpha=Math.min(1,progress*3);
                if(motion.hideBeforeDelay&&elapsed<delay)sprite.alpha=0;
                if(progress==1){
                    motion.finished=true;
                    if(motion.remove&&sprite.parent)sprite.parent.removeChild(sprite);
                }else complete=false;
            }
            if(complete)animations=[];
        }
        // One timing source keeps the projectile, number and audio in step at
        // every presentation speed. It never delays or reruns game rules.
        private function cueImpactDelay():Number
        {
            if(reducedMotion||!activeCue)return 0;
            var delay:Number=activeCue.kind==1?400:activeCue.kind==2?180:activeCue.kind==10?200:activeCue.kind==15||activeCue.kind==16?160:0;
            return Math.min(delay/animationTempo,Math.max(0,frameDuration-90/animationTempo));
        }
        private function drawVisualCue():void
        {
            if(!activeCue||activeCue.kind==0){
                if(lastRoundResult&&((flags&4)!=0||(flags>>4)>0))drawRoundBanner(content,false);
                return;
            }
            var fx:Sprite=new Sprite();fx.mouseEnabled=false;fx.mouseChildren=false;content.addChild(fx);
            var origin:Object=displayedCards[activeCue.source];
            if(!origin&&(activeCue.kind==13||activeCue.kind==16))origin=departedPoses[activeCue.source];
            var target:Object=displayedCards[activeCue.target];
            var sx:Number=origin?origin.x+40:960;var sy:Number=origin?origin.y+40:430;
            var tint:uint=target&&target.delta>0?0x8FE0AE:target&&target.delta<0?0xEE8B70:0xA7DCEE;
            if(activeCue.kind==1||activeCue.kind==2||activeCue.kind==4||activeCue.kind==8||activeCue.kind==9||activeCue.kind==10){
                if(!origin&&activeCue.source>0&&activeCue.templateId>0){
                    var spell:Sprite=panel(fx,892,312,136,204,0x101315,.97);
                    paintArt(spell,activeCue.templateId,130,198);
                    var prior:Object=previousPoses[activeCue.source];
                    var fromHand:Boolean=activeCue.kind==1&&prior&&prior.zone==8;
                    var fromX:Number=fromHand?prior.x:892;var fromY:Number=fromHand?prior.y:322;
                    animations.push({sprite:spell,fromX:fromX,fromY:fromY,toX:892,toY:312,fade:false,appear:true,remove:false,duration:fromHand?400:140,arc:fromHand?32:0,betaFlight:fromHand,tilt:fromX<892?5:-5,fromScaleX:fromHand?0.59:1,fromScaleY:fromHand?0.68:1,toScaleX:1,toScaleY:1});
                    spell.x=fromX;spell.y=fromY;spell.alpha=0;sx=960;sy=414;
                }
                if(origin){
                    fx.graphics.lineStyle(3,0xF1D075,.95);fx.graphics.drawRect(origin.x-2,origin.y-2,84,88);
                }
                if(activeCue.source==0&&activeCue.row>0){
                    var weather:Object=rowGeometry(activeCue.side,activeCue.row);
                    sx=weather.x+weather.w/2;sy=weather.y+weather.h/2;
                }
                if(target&&activeCue.kind==2){
                    var tx:Number=target.x+40;var ty:Number=target.y+40;
                    fx.graphics.lineStyle(2,tint,.16);fx.graphics.moveTo(sx,sy);fx.graphics.lineTo(tx,ty);
                    fx.graphics.lineStyle(3,tint,.95);fx.graphics.drawRect(target.x-3,target.y-3,86,90);
                    fx.graphics.drawCircle(tx,ty,25);
                    if(!reducedMotion){
                        var impact:Sprite=new Sprite();impact.mouseEnabled=false;impact.mouseChildren=false;
                        impact.graphics.lineStyle(3,tint,.9);impact.graphics.drawCircle(0,0,22);fx.addChild(impact);
                        impact.x=tx;impact.y=ty;
                        animations.push({sprite:impact,fromX:tx,fromY:ty,toX:tx,toY:ty,fade:true,remove:true,duration:220,delay:cueImpactDelay()*animationTempo,hideBeforeDelay:true,fromScaleX:.4,fromScaleY:.4,toScaleX:1.6,toScaleY:1.6});
                        var bolt:Sprite=new Sprite();bolt.mouseEnabled=false;
                        bolt.graphics.beginFill(tint,.2);bolt.graphics.drawCircle(0,0,12);bolt.graphics.endFill();
                        bolt.graphics.beginFill(tint,.95);bolt.graphics.drawCircle(0,0,4);bolt.graphics.endFill();fx.addChild(bolt);
                        bolt.x=sx;bolt.y=sy;
                        animations.push({sprite:bolt,fromX:sx,fromY:sy,toX:tx,toY:ty,fade:false,remove:true,duration:cueImpactDelay()*animationTempo,arc:12,betaFlight:true,tilt:0});
                    }
                }
            }
            if(activeCue.kind==1&&origin&&!reducedMotion){
                var definition:Object=cardDetails[activeCue.source];
                var landingTint:uint=definition&&definition.tier==8?0xE9C46A:definition&&definition.tier==4?0xDDE8F1:0xACD9E2;
                var landing:Sprite=new Sprite();landing.mouseEnabled=false;landing.mouseChildren=false;fx.addChild(landing);
                landing.x=origin.x+40;landing.y=origin.y+40;
                landing.graphics.lineStyle(3,landingTint,.85);landing.graphics.drawEllipse(-40,-28,80,56);
                for(var landingRay:int=0;landingRay<8;landingRay++){
                    var theta:Number=landingRay*Math.PI/4;
                    landing.graphics.moveTo(Math.cos(theta)*35,Math.sin(theta)*24);
                    landing.graphics.lineTo(Math.cos(theta)*48,Math.sin(theta)*35);
                }
                animations.push({sprite:landing,fromX:landing.x,fromY:landing.y,toX:landing.x,toY:landing.y,fade:true,remove:true,duration:200,
                    delay:cueImpactDelay()*animationTempo,hideBeforeDelay:true,fromScaleX:.7,fromScaleY:.7,toScaleX:1.25,toScaleY:1.25});
            }
            if(activeCue.kind==11||activeCue.kind==12)drawConsumeCue(fx,origin);
            if(activeCue.kind==8&&target&&(activeCue.row==0)&&!reducedMotion){
                var resilient:Sprite=new Sprite();resilient.mouseEnabled=false;resilient.mouseChildren=false;fx.addChild(resilient);
                resilient.x=target.x+6;resilient.y=target.y+12;
                text(resilient,"∞",0,0,72,54,0x93E1B5).height=76;
                animations.push({sprite:resilient,fromX:resilient.x,fromY:resilient.y,toX:resilient.x,toY:resilient.y-18,fade:true,remove:true,duration:420});
            }
            if(activeCue.kind==15||activeCue.kind==16)drawSummonCue(fx,origin,target);
            if(activeCue.kind==9&&target){
                var locked:Boolean=false;
                for each(var affected:Object in cards)if(affected.id==activeCue.target)locked=(int(affected.tokens)&4)!=0;
                var seal:Sprite=new Sprite();seal.mouseEnabled=false;seal.mouseChildren=false;fx.addChild(seal);
                seal.x=target.x+28;seal.y=target.y+18;paintLock(seal,0,0);
                var color:uint=locked?0xE9C46A:0x8FE0AE;
                seal.graphics.lineStyle(3,color,.85);seal.graphics.drawCircle(11,12,23);
                animations.push({sprite:seal,fromX:seal.x,fromY:seal.y,toX:seal.x,toY:seal.y,fade:true,remove:true,
                    duration:390,fromScaleX:locked?1.7:1,fromScaleY:locked?1.7:1,toScaleX:locked?1:2,toScaleY:locked?1:2});
            }
            if(activeCue.kind==10&&target){
                var shimmer:Sprite=new Sprite();shimmer.mouseEnabled=false;shimmer.mouseChildren=false;fx.addChild(shimmer);
                shimmer.x=target.x;shimmer.y=target.y;
                shimmer.graphics.beginFill(0x7BD6C4,.6);shimmer.graphics.drawRect(0,0,target.width,target.height);shimmer.graphics.endFill();
                animations.push({sprite:shimmer,fromX:target.x,fromY:target.y,toX:target.x,toY:target.y,fade:true,remove:true,duration:440});
            }
            if(activeCue.kind==13){
                var departed:Object=previousPoses[activeCue.source]?previousPoses[activeCue.source]:departedPoses[activeCue.source];
                if(departed){
                    var omen:Sprite=new Sprite();omen.mouseEnabled=false;omen.mouseChildren=false;fx.addChild(omen);
                    omen.x=departed.x+40;omen.y=departed.y+35;
                    omen.graphics.lineStyle(3,0xDDB89C,.85);omen.graphics.drawCircle(0,0,28);
                    for(var ray:int=0;ray<8;ray++){
                        var angle:Number=ray*Math.PI/4;omen.graphics.moveTo(Math.cos(angle)*33,Math.sin(angle)*33);
                        omen.graphics.lineTo(Math.cos(angle)*44,Math.sin(angle)*44);
                    }
                    animations.push({sprite:omen,fromX:omen.x,fromY:omen.y,toX:omen.x,toY:omen.y,fade:true,remove:true,
                        duration:400,fromScaleX:.7,fromScaleY:.7,toScaleX:1.4,toScaleY:1.4});
                }
            }
            if(activeCue.kind==8&&(activeCue.row==1||activeCue.row==2||activeCue.row==4)){
                var abilityRow:Object=rowGeometry(activeCue.side,activeCue.row);
                fx.graphics.lineStyle(3,0xE7AD68,.85);
                fx.graphics.drawRect(abilityRow.x,abilityRow.y,abilityRow.w,abilityRow.h);
            }
            if(activeCue.kind==4&&activeCue.row>0){
                var row:Object=rowGeometry(activeCue.side,activeCue.row);
                fx.graphics.lineStyle(4,0xCAEAF5,.9);fx.graphics.drawRect(row.x,row.y,row.w,row.h);
                var wave:Sprite=new Sprite();wave.mouseEnabled=false;wave.mouseChildren=false;
                wave.graphics.beginFill(0xCAEAF5,.35);wave.graphics.drawRect(0,0,row.w,row.h);wave.graphics.endFill();
                fx.addChild(wave);wave.x=row.x;wave.y=row.y;
                animations.push({sprite:wave,fromX:row.x,fromY:row.y,toX:row.x,toY:row.y,fade:true,remove:true,duration:330});
                if(!reducedMotion){
                    var sweepLayer:Sprite=new Sprite();sweepLayer.mouseEnabled=false;sweepLayer.mouseChildren=false;fx.addChild(sweepLayer);
                    sweepLayer.x=row.x;sweepLayer.y=row.y;sweepLayer.scrollRect=new Rectangle(0,0,row.w,row.h);
                    var sweep:Sprite=new Sprite();sweep.mouseEnabled=false;sweepLayer.addChild(sweep);
                    sweep.graphics.beginFill(0xD7EFF5,.5);sweep.graphics.drawRect(0,0,40,row.h);sweep.graphics.endFill();
                    animations.push({sprite:sweep,fromX:-40,fromY:0,toX:row.w,toY:0,fade:false,remove:true,duration:330});
                }
            }
            if(activeCue.kind==5){
                var y:Number=activeCue.side==1?575:225;
                fx.graphics.lineStyle(4,0xCFB176,.95);fx.graphics.drawRoundRect(98,y-2,284,229,8,8);
            }
            if(activeCue.kind==6)drawRoundBanner(fx,true);
            else if(activeCue.kind==7){
                var startBanner:Sprite=panel(fx,650,396,650,148,0x101619,.97);
                text(startBanner,"РАУНД "+round,24,16,600,32,0xE9C46A);
                text(startBanner,current==1?"Ваш ход":"Ход соперника",24,66,600,26);
                text(startBanner,"Победы: "+crowns[0]+" : "+crowns[1],24,108,600,18,0xC8C7BB);
                animations.push({sprite:startBanner,fromX:650,fromY:420,toX:650,toY:396,appear:true,remove:false,duration:400});
                startBanner.y=420;startBanner.alpha=0;
            }else{
                var strip:Sprite=panel(fx,610,160,820,46,0x101619,.94);
                var caption:String=activeCue.title;
                if(activeCue.sequenceSize>1)caption+="  ·  изменение "+activeCue.sequence+" / "+activeCue.sequenceSize;
                text(strip,caption,14,5,790,20,0xE9DBBE);
            }
        }
        private function paintRoundSeal(parent:Sprite,filled:Boolean,color:uint,r:Number):void
        {
            parent.graphics.lineStyle(2,filled?color:0x7A766C,.95);
            parent.graphics.beginFill(filled?color:0x20282D,filled?0.85:0.9);
            parent.graphics.moveTo(0,-r);parent.graphics.lineTo(r,0);parent.graphics.lineTo(0,r);parent.graphics.lineTo(-r,0);parent.graphics.lineTo(0,-r);parent.graphics.endFill();
            if(filled){parent.graphics.lineStyle(2,0xFFF0BA,.9);parent.graphics.moveTo(-r*.35,0);parent.graphics.lineTo(-r*.05,r*.3);parent.graphics.lineTo(r*.45,-r*.3);}
        }
        private function drawRoundBanner(parent:Sprite,animate:Boolean):void
        {
            var result:Object=lastRoundResult;if(!result)return;
            var matchWinner:int=int(result.flags)>>4;
            var winner:int=matchWinner>0?matchWinner:result.scores[0]>result.scores[1]?1:result.scores[0]<result.scores[1]?2:3;
            var title:String=winner==3?"НИЧЬЯ":winner==1?"ВЫ ПОБЕДИЛИ":"ПОБЕДИЛ СОПЕРНИК";
            if(matchWinner==0)title=winner==3?"НИЧЬЯ В РАУНДЕ":winner==1?"РАУНД ЗА ВАМИ":"РАУНД ЗА СОПЕРНИКОМ";
            var color:uint=winner==1?0x8ED8EA:winner==2?0xE9AB85:0xE4CE8F;
            var banner:Sprite=panel(parent,638,366,780,216,0x101619,.98);
            banner.mouseEnabled=false;banner.mouseChildren=false;
            banner.graphics.lineStyle(2,color,.9);banner.graphics.drawRoundRect(0,0,780,216,8,8);
            text(banner,title,24,14,735,29,color);
            text(banner,"Геральт",80,60,235,17,0x8ED8EA);text(banner,"Соперник",452,60,235,17,0xE9AB85);
            for(var side:int=1;side<=2;side++){
                var tally:Sprite=new Sprite();tally.mouseEnabled=false;tally.mouseChildren=false;banner.addChild(tally);
                tally.x=side==1?80:452;tally.y=86;
                var value:TextField=text(tally,String(result.scores[side-1]),0,0,240,42,side==winner||winner==3?color:0xB1ACA1);
                if(animate&&!reducedMotion){
                    value.text="0";
                    animations.push({sprite:tally,fromX:tally.x,fromY:86,toX:tally.x,toY:86,fade:false,remove:false,
                        duration:520,delay:100,counter:value,fromValue:0,toValue:result.scores[side-1]});
                }
                for(var sealIndex:int=0;sealIndex<2;sealIndex++){
                    var seal:Sprite=new Sprite();seal.mouseEnabled=false;seal.mouseChildren=false;banner.addChild(seal);
                    seal.x=(side==1?100:472)+sealIndex*40;seal.y=163;
                    paintRoundSeal(seal,sealIndex<result.crowns[side-1],side==1?0x8ED8EA:0xE9AB85,14);
                }
            }
            text(banner,matchWinner>0?"Партия завершена":"Раунд "+result.round+" завершён · следующий начнётся автоматически",24,189,735,16,0xD7D1C3);
            if(animate){
                animations.push({sprite:banner,fromX:638,fromY:394,toX:638,toY:366,appear:true,remove:false,duration:400});
                banner.y=394;banner.alpha=0;
            }
        }
        private function drawSummonCue(fx:Sprite,source:Object,target:Object):void
        {
            if(!target)return;
            var fromDeck:Boolean=activeCue.kind==15;
            var tint:uint=fromDeck?0xA6DCEB:0xDDB382;
            var x:Number=target.x+target.width/2;var y:Number=target.y+target.height/2;
            var gate:Sprite=new Sprite();gate.mouseEnabled=false;gate.mouseChildren=false;fx.addChild(gate);
            gate.x=x;gate.y=y;
            gate.graphics.lineStyle(3,tint,.9);gate.graphics.drawEllipse(-46,-20,92,40);
            gate.graphics.lineStyle(1,tint,.6);gate.graphics.drawEllipse(-35,-14,70,28);
            for(var spoke:int=0;spoke<6;spoke++){
                var a:Number=spoke*Math.PI/3;
                gate.graphics.moveTo(Math.cos(a)*38,Math.sin(a)*17);gate.graphics.lineTo(Math.cos(a)*51,Math.sin(a)*24);
            }
            gate.scaleX=gate.scaleY=.3;gate.alpha=0;
            animations.push({sprite:gate,fromX:x,fromY:y,toX:x,toY:y,fade:true,remove:true,duration:400,delay:100,hideBeforeDelay:true,
                fromScaleX:.3,fromScaleY:.3,toScaleX:1.35,toScaleY:1.35});
            if(source&&activeCue.source!=activeCue.target){
                fx.graphics.lineStyle(2,tint,.55);fx.graphics.moveTo(source.x+40,source.y+35);fx.graphics.lineTo(x,y);
                fx.graphics.lineStyle(3,tint,.9);fx.graphics.drawRect(source.x-2,source.y-2,84,88);
            }
            if(!reducedMotion){
                for(var sparkIndex:int=0;sparkIndex<6;sparkIndex++){
                    var spark:Sprite=new Sprite();spark.mouseEnabled=false;fx.addChild(spark);
                    spark.graphics.beginFill(tint,.95);spark.graphics.drawCircle(0,0,2);spark.graphics.endFill();
                    var angle:Number=sparkIndex*Math.PI/3;
                    animations.push({sprite:spark,fromX:x,fromY:y,toX:x+Math.cos(angle)*56,toY:y+Math.sin(angle)*35,
                        fade:true,remove:true,duration:300,delay:150,hideBeforeDelay:true});spark.x=x;spark.y=y;
                }
            }
        }
        private function drawArmorHit(parent:Sprite,width:Number,delta:int):void
        {
            var shield:Sprite=new Sprite();shield.mouseEnabled=false;shield.mouseChildren=false;parent.addChild(shield);
            shield.x=width-22;shield.y=15;shield.graphics.lineStyle(3,0x9CE3EF,.9);shield.graphics.drawCircle(0,0,16);
            animations.push({sprite:shield,fromX:shield.x,fromY:15,toX:shield.x,toY:15,fade:true,remove:true,
                duration:300,delay:120,hideBeforeDelay:true,fromScaleX:.6,fromScaleY:.6,toScaleX:1.8,toScaleY:1.8});
            for(var piece:int=0;piece<3;piece++){
                var shard:Sprite=new Sprite();shard.mouseEnabled=false;parent.addChild(shard);
                shard.graphics.beginFill(0xA7DCEA,.9);shard.graphics.drawRect(-2,-5,4,10);shard.graphics.endFill();
                shard.x=width-22;shard.y=15;
                animations.push({sprite:shard,fromX:width-22,fromY:15,toX:width-22+(piece-1)*24,toY:48+piece*5,
                    fade:true,remove:true,duration:320,delay:130,hideBeforeDelay:true,fromRotation:0,toRotation:(piece-1)*90});
            }
        }
        private function paintCardBack(parent:Sprite,w:Number,h:Number,side:int):void
        {
            parent.graphics.lineStyle(1,0xA98A61,.9);parent.graphics.beginFill(side==1?0x244A59:0x583126,.98);
            parent.graphics.drawRoundRect(0,0,w,h,5,5);parent.graphics.endFill();
            parent.graphics.lineStyle(1,0xC2A67C,.8);parent.graphics.drawRoundRect(4,4,Math.max(1,w-8),Math.max(1,h-8),3,3);
            parent.graphics.moveTo(w/2,h*.3);parent.graphics.lineTo(w*.7,h/2);parent.graphics.lineTo(w/2,h*.7);parent.graphics.lineTo(w*.3,h/2);parent.graphics.lineTo(w/2,h*.3);
        }
        private function drawConsumeCue(fx:Sprite,source:Object):void
        {
            var view:Object=activeCue.targetView;
            var target:Object=displayedCards[activeCue.target];
            var pose:Object=target?target:previousPoses[activeCue.target];
            var sx:Number=source?source.x+source.width/2:960;
            var sy:Number=source?source.y+source.height/2:430;
            var morsel:Sprite=activeCue.kind==11?cardSprites[activeCue.target]:null;
            var x:Number=pose?pose.x:260;var y:Number=pose?pose.y:view&&view.side==2?398:748;
            if(!morsel&&view&&view.templateId>0){
                morsel=panel(fx,x,y,80,110,0x1C3540,.96);paintArt(morsel,view.templateId,74,104);
            }
            if(morsel){
                morsel.mouseEnabled=false;morsel.mouseChildren=false;
                animations.push({sprite:morsel,fromX:x,fromY:y,toX:sx-6,toY:sy-6,fade:true,remove:true,
                    duration:390,arc:20,fromScaleX:1,fromScaleY:1,toScaleX:.12,toScaleY:.12});
                if(activeCue.kind==11)consumedVisualIds[activeCue.target]=true;
            }
            var pulse:Sprite=new Sprite();pulse.mouseEnabled=false;pulse.mouseChildren=false;fx.addChild(pulse);
            pulse.graphics.lineStyle(3,0xBCA2DF,.95);pulse.graphics.drawCircle(0,0,26);pulse.x=sx;pulse.y=sy;
            animations.push({sprite:pulse,fromX:sx,fromY:sy,toX:sx,toY:sy,fade:true,remove:true,duration:390,
                fromScaleX:.6,fromScaleY:.6,toScaleX:1.8,toScaleY:1.8});
            if(!reducedMotion){
                fx.graphics.lineStyle(4,0xBCA2DF,.4);fx.graphics.moveTo(x+40,y+35);fx.graphics.lineTo(sx,sy);
            }
        }
        private function animateWeather(e:Event):void
        {
            if(weatherEffects.length==0)return;
            if(reducedMotion){for each(var quiet:Object in weatherEffects){quiet.sprite.visible=false;quiet.sprite.graphics.clear();}return;}
            // Ten redraws/second; elapsed time keeps speed independent of frame rate.
            weatherFrame++;if(e&&weatherFrame%3!=0)return;
            var now:int=getTimer();
            for each(var fx:Object in weatherEffects){
                var p:Sprite=fx.sprite;var t:Number=(now-fx.start)/1000;p.visible=true;
                p.alpha=Math.min(1,t/.45);p.graphics.clear();
                if(fx.nativeParts){
                    for each(var part:Object in fx.nativeParts){
                        var view:Sprite=part.sprite;
                        if(part.kind=="fog"){
                            view.x=(t*part.speed+part.phase)%(fx.w+part.width)-part.width;
                            view.y=part.y+Math.sin(t*.6+part.phase)*5;
                            view.alpha=part.alpha*(.8+.2*Math.sin(t*.7+part.phase));
                        }else if(part.kind=="rain"||part.kind=="rain-lower"){
                            view.x=part.x;view.y=(t*150+part.phase)%180-180+(part.kind=="rain-lower"?180:0);view.alpha=part.alpha;
                        }else if(part.kind=="snow"){
                            view.x=(part.phase+t*14)%fx.w;view.y=(part.phase*.37+t*18)%(fx.h+24)-24;
                            view.rotation=Math.sin(t*.4+part.phase)*20;view.alpha=part.alpha;
                        }
                    }
                    continue;
                }
                if(fx.token==2){
                    for(var band:int=0;band<4;band++){
                        var drift:Number=(t*24+band*239+fx.phase)%(fx.w+280)-280;
                        p.graphics.beginFill(0xE0E2DE,.075);
                        p.graphics.drawRoundRect(drift,8+band*13,280,32,32,32);p.graphics.endFill();
                    }
                }else if(fx.token==256||fx.token==2048){
                    var moonTint:uint=fx.token==256?0xCEC4FF:0xDE5871;
                    for(var moonBand:int=0;moonBand<3;moonBand++){
                        p.graphics.lineStyle(2,moonTint,.09+.04*Math.sin(t*1.8+moonBand));
                        p.graphics.drawEllipse(fx.w*.22+moonBand*15,fx.h*.5-10-moonBand*4,fx.w*.42-moonBand*30,20+moonBand*8);
                    }
                }else if(fx.token==512){
                    for(var spike:int=0;spike<12;spike++){
                        var sx:Number=spike*fx.w/12+16;
                        p.graphics.lineStyle(1.5,0xCDB69A,.25);p.graphics.moveTo(sx,fx.h-2);p.graphics.lineTo(sx+5,fx.h-15);p.graphics.lineTo(sx+10,fx.h-2);
                    }
                }else if(fx.token==1024){
                    for(var ember:int=0;ember<16;ember++){
                        var ex:Number=(ember*113+fx.phase+t*9)%fx.w;
                        var ey:Number=fx.h*.6+Math.sin(t*.8+ember)*fx.h*.2;
                        p.graphics.beginFill(0xEBA04D,.2+.1*Math.sin(t*2+ember));p.graphics.drawCircle(ex,ey,2+ember%2);p.graphics.endFill();
                    }
                }else{
                    for(var i:int=0;i<24;i++){
                        var x:Number=(i*97+fx.phase+t*(fx.token==1?10:-35)+fx.w*1000)%fx.w;
                        var y:Number=(i*43+fx.phase+t*(fx.token==1?18:125))%fx.h;
                        if(fx.token==16||fx.token==32||fx.token==128){
                            p.graphics.beginFill(fx.token==128?0xF3D66B:0xF38A49,.28);p.graphics.drawCircle(x,fx.h-y,1+i%3);p.graphics.endFill();
                        }else if(fx.token==1){
                            p.graphics.beginFill(0xE3F6FF,.3);p.graphics.drawCircle(x,y,1+i%2);p.graphics.endFill();
                        }else{
                            p.graphics.lineStyle(1,0xB6E5F0,.28);p.graphics.moveTo(x,y);p.graphics.lineTo(x-4,y+12);
                        }
                    }
                }
            }
        }
        private function paintTimer(parent:Sprite,x:Number,y:Number,value:int,paused:Boolean):void
        {
            var clock:Sprite=new Sprite();clock.mouseEnabled=false;clock.mouseChildren=false;
            clock.graphics.lineStyle(1.5,paused?0x999999:0xE9C46A);
            clock.graphics.beginFill(0x101315,.93);clock.graphics.drawCircle(11,11,11);clock.graphics.endFill();
            text(clock,String(value),3,0,20,16,paused?0xBBBBBB:0xF4D889);
            parent.addChild(clock);clock.x=x;clock.y=y;
        }
        private function paintLock(parent:Sprite,x:Number,y:Number):void
        {
            var icon:Sprite=panel(parent,x,y,22,24,0x111A21,.93);
            icon.mouseEnabled=false;icon.mouseChildren=false;
            icon.graphics.lineStyle(2,0xE9C46A);
            icon.graphics.drawRoundRect(6,3,10,12,7,7);
            icon.graphics.beginFill(0xE9C46A);icon.graphics.drawRoundRect(4,10,14,11,3,3);icon.graphics.endFill();
            icon.graphics.lineStyle(2,0x293946);icon.graphics.moveTo(11,13);icon.graphics.lineTo(11,18);
        }
        private function updateFocusedInspection():void
        {
            if(!inspection)return;var id:int=keyboardFocusId!=0?keyboardFocusId:selected;
            if(id==0)return;
            var c:Object=findRequestCard(id);
            for each(var visible:Object in cards)if(visible.id==id){c=visible;break;}
            if(!c)return;var detail:Object=cardDetails[id];
            inspection.text=cardReading(c,detail);
        }
        private function prepareNativeWeather(fx:Object):void
        {
            fx.nativeParts=[];
            var holder:Sprite=fx.sprite;var i:int;var art:Sprite;var width:Number;
            if(fx.token==1){
                for(i=0;i<3;i++){
                    art=BetaGwentCardArt.view(-3-i,fx.w/3+2,fx.h);if(!art)continue;
                    art.x=i*fx.w/3;art.alpha=.23;holder.addChild(art);
                }
                for(i=0;i<10;i++){
                    art=BetaGwentCardArt.view(-8,14+i%3*6,14+i%3*6);if(!art)continue;holder.addChild(art);
                    fx.nativeParts.push({sprite:art,kind:"snow",phase:i*83+fx.phase,alpha:.26});
                }
            }else if(fx.token==2){
                for(i=0;i<7;i++){
                    width=210+i%3*75;art=BetaGwentCardArt.view(i%2==0?-1:-2,width,fx.h*.8);if(!art)continue;holder.addChild(art);
                    fx.nativeParts.push({sprite:art,kind:"fog",width:width,y:i%3*fx.h*.12,speed:12+i%3*5,phase:i*149+fx.phase,alpha:.14});
                }
            }else {
                for(i=0;i<8;i++){
                    width=fx.w/8+1;
                    for(var layer:int=0;layer<2;layer++){
                        art=BetaGwentCardArt.view(i%2==0?-6:-7,width,180);if(!art)continue;holder.addChild(art);
                        fx.nativeParts.push({sprite:art,kind:"rain",x:i*fx.w/8,phase:layer*180+fx.phase,width:width,alpha:fx.token==64 ? 0.42 : 0.28});
                        // Two neighbouring vertical copies keep the entire row covered.
                        if(layer==1)fx.nativeParts[fx.nativeParts.length-1].kind="rain-lower";
                    }
                }
            }
            holder.mouseEnabled=false;holder.mouseChildren=false;
        }
        private function readableText(value:String):String
        {
            if(value==null)return "";
            return value.split("\\r\\n").join("\n").split("\\n").join("\n").split("/n").join("\n").split("\r\n").join("\n").replace(/<br\s*\/?\s*>/gi,"\n").replace(/<[^>]+>/g,"");
        }
        private function isAmbush(id:int):Boolean
        { return [142204,142208,142210,142307,201779].indexOf(id)>=0; }
        private function ambushReading(c:Object):String
        {
            if(!c||(c.zone&7)==0||(int(c.tokens)&8)==0)return "";
            if(c.templateId==0)return "Засада соперника: карта и условие скрыты до раскрытия.";
            var hint:String=c.templateId==142204?"Ждёт паса соперника. Затем усилит до двух соседей с каждой стороны на 2.":
                c.templateId==142208?"Ждёт розыгрыша вражеского отряда. Затем нанесёт ему 7 урона.":
                c.templateId==201779?"Ждёт бронзовой или серебряной особой карты соперника. Отменит её способность.":
                "Раскроется в начале вашего хода после окончания счётчика.";
            return "ЗАСАДА УСТАНОВЛЕНА\n"+hint+"\nПока закрыта, её сила не входит в счёт ряда.";
        }
        private function cardReading(c:Object,detail:Object,complete:Boolean=false):String
        {
            var hidden:Boolean=(c.zone&7)!=0&&(int(c.tokens)&8)!=0;
            var value:String=c.title+(c.created?" · сотворённая копия":"")+"\n";
            if(c.templateId>0){
                var original:Object=BetaGwentCardText.find(c.templateId);
                if(original&&original.typeMask==4)value+="Исходная сила: "+original.power+(c.power!=null?" · текущая: "+c.power:"")+"\n";
            }
            if(hidden)value+=ambushReading(c)+"\n\n";
            else if((c.zone&7)!=0&&isAmbush(c.templateId))value+="Засада уже раскрыта; её сила учитывается в счёте.\n\n";
            if(c.templateId>0)value+="Теги: "+(BetaGwentCardTags.text(c.templateId)||"—")+"\n\n";
            value+=readableText(complete&&original?original.description:detail?detail.description:c.description);
            if(complete&&original&&original.glossary.length)value+="\n\n"+original.glossary;
            if(complete&&original&&original.flavor.length)value+="\n\n«"+original.flavor+"»";
            if((int(c.tokens)&1)!=0)value+="\n\nСтойкость: останется на поле в следующем раунде.";
            if(c.timer!=null&&int(c.timer)>=0)value+="\nСчётчик: "+int(c.timer)+((int(c.tokens)&4)!=0?" · остановлен блокировкой":" · уменьшается перед своим ходом");
            if((int(c.tokens)&4)!=0)value+="\nБлокировка: пассивные способности и Завещание отключены.";
            return value;
        }
        private function closeCardDetail():void
        {detailOpen=false;detailBody=null;while(detailLayer.numChildren)detailLayer.removeChildAt(0);}
        private function openCardDetail(c:Object,detail:Object):void
        {
            if(!c)return;clearDrag();clearPlacementGhost();detailOpen=true;
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(detailLayer.numChildren)detailLayer.removeChildAt(0);
            var shade:Sprite=panel(detailLayer,0,0,1920,1080,0x080C10,.82);
            shade.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();closeCardDetail();});
            var box:Sprite=panel(detailLayer,376,170,1168,740,0x10191F,.99);
            box.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();});
            var picture:Sprite=panel(box,28,76,320,450,0x173340,.96);
            if(c.templateId>0)paintChoiceArt(picture,c.templateId,314,444);else paintCardBack(picture,320,450,2);
            text(box,c.title,28,18,1100,32,0xF5D77F).height=50;
            var body:TextField=text(box,cardReading(c,detail,true),378,80,752,25);body.height=548;
            detailBody=body;
            body.mouseEnabled=true;body.selectable=true;
            body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopImmediatePropagation();e.preventDefault();body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV-e.delta*3));});
            text(box,"Колесо — прокрутить описание · Esc или I — закрыть",378,642,752,19,0xB9B4A9).height=40;
            var close:Sprite=panel(box,28,642,320,52,0x273B43,.98);close.buttonMode=true;text(close,"Вернуться к игре",16,10,288,23).height=40;
            close.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();closeCardDetail();});
            controller.registerControl(close,"Вернуться",closeCardDetail);
        }
        private function attachInspect(p:Sprite,c:Object,detail:Object,bodyWidth:Number=0,bodyHeight:Number=0):void
        {
            controller.registerControl(p,c.title,null,c,detail,c.zone==8&&c.side==1?"hand":"card");
            var glow:Sprite=new Sprite();glow.mouseEnabled=false;glow.mouseChildren=false;
            glow.graphics.lineStyle(2,0xD6E8E6,.8);
            glow.graphics.drawRect(1,1,(bodyWidth>0?bodyWidth:p.width/p.scaleX)-2,(bodyHeight>0?bodyHeight:p.height/p.scaleY)-2);
            glow.alpha=0;p.addChild(glow);
            p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{
                if(dragging||detailOpen)return;
                hoveredCard=c;hoveredDetail=detail;
                glow.alpha=1;if(hoverCardId==(c.id!=null?c.id:c.templateId))return;hoverCardId=c.id!=null?c.id:c.templateId;
                if(inspection)inspection.text=cardReading(c,detail);
                while(previewLayer.numChildren)previewLayer.removeChildAt(0);
                if(canPlaceSelected()||canPlacePending())return;
                var x:Number=Math.min(1304,Math.max(16,mouseX+20));
                var y:Number=Math.min(628,Math.max(90,mouseY-190));
                var large:Sprite=panel(previewLayer,x,y,600,416,0x101315,.98);
                if(c.templateId>0)paintChoiceArt(large,c.templateId,184,256);else paintCardBack(large,184,256,2);
                text(large,c.title,8,264,184,21,0xF5D77F).height=72;
                text(large,cardReading(c,detail),204,12,382,21).height=354;
                text(large,"I / Shift + клик — открыть и прокрутить",14,378,570,19,0xA7DCEE).height=30;
            });
            p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{
                glow.alpha=0;hoverCardId=0;hoveredCard=null;hoveredDetail=null;updateFocusedInspection();
                while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            });
            p.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{if(e.shiftKey){e.stopImmediatePropagation();e.preventDefault();}});
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{if(e.shiftKey){e.stopImmediatePropagation();e.preventDefault();openCardDetail(c,detail);}});
            p.addEventListener(MouseEvent.RIGHT_CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();e.preventDefault();openCardDetail(c,detail);});
        }
        private function attachCard(p:Sprite,id:int,playable:Boolean):void
        {
            controller.registerControl(p,"",function():void{controllerCardAction(id);},null,null,"hand");
            p.buttonMode=playable;
            if(playable)p.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{beginHandDrag(id);});
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{
                if(canAct()&&playable){uiSound(3);selected=selected==id?0:id;keyboardFocusId=selected;focusedRow=0;render();}
            });
        }
        private function findRequestCard(id:int):Object
        {
            for each(var c:Object in requestCards) if(c.id==id) return c;
            return null;
        }
        private function sendRequest(eventName:String,itemId:int=0):void
        {
            if(pileOpen||detailOpen)return;
            if(!ready || playing || requestId==0) return;
            var args:Array=[revision,requestId,requestPlayer,requestKind];
            if(eventName=="OnBetaGwentRequestSelect") args.push(itemId);
            // Selection is authoritative in WS. Wait for a new full snapshot.
            ready=false;
            // Native may deliver the next snapshot synchronously. Keep its
            // transitions instead of repainting them after the callback returns.
            send(eventName,args);
        }
        private function requestAction(eventName:String,itemId:int=0):Function
        {
            var expectedRevision:int=revision;
            var expectedRequest:int=requestId;
            var expectedPlayer:int=requestPlayer;
            var expectedKind:int=requestKind;
            return function():void
            {
                if(expectedRevision!=revision || expectedRequest!=requestId || expectedPlayer!=requestPlayer || expectedKind!=requestKind) return;
                sendRequest(eventName,itemId);
            };
        }
        private function attachRequestCard(p:Sprite,id:int):void
        {
            p.buttonMode=ready;
            var action:Function=requestAction("OnBetaGwentRequestSelect",id);
            controller.registerControl(p,"",action,null,null,"target");
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{action();});
        }
        private function paintChoiceArt(parent:Sprite,id:int,w:Number,h:Number):void
        {
            if(id!=113402){paintArt(parent,id,w,h);return;}
            var back:Sprite=panel(parent,3,3,w,h,0x24404A,.96);
            back.graphics.lineStyle(2,0xBA9472,.9);back.graphics.drawRoundRect(9,9,w-18,h-18,8,8);
            text(back,"?",w/2-25,24,70,58,0xE4CA92);
            var hint:TextField=text(back,"Случайный\nбронзовый отряд",10,90,w-20,14,0xE7D9C0);hint.height=55;
        }
        private function drawChoices():void
        {
            content.addChild(choiceLayer);
            // Opaque hit surface stops clicks reaching the board behind choices.
            choiceLayer.graphics.clear();choiceLayer.graphics.beginFill(0,0.30);choiceLayer.graphics.drawRect(0,0,1920,1080);choiceLayer.graphics.endFill();
            var modal:Sprite=panel(choiceLayer,450,215,1000,600,0x10191F,.98);
            if(pileChoice&&requestCards.length==0){
                text(modal,"Способность · подходящих карт нет",24,20,950,28,0xE9C46A).height=65;
                text(modal,requestMessage,36,150,920,26).height=200;
                button("Продолжить",1124,745,290,ready&&requestFinish,requestAction("OnBetaGwentRequestFinish"),choiceLayer);
                return;
            }
            text(modal,templateChoice?(rowMode==13?"Выберите вариант способности":rowMode==7?"Дагон · выберите погоду":"Рассвет · выберите вариант"):pileChoice?(rowMode==14?"Выберите карту для способности":"Выберите карту для розыгрыша"):handPowerChoice?"Выберите отряд в руке":graveyardChoice?"Поглощение · выберите отряд из сброса":"Замена карт · осталось "+(requestMax-requestCount),24,16,950,26,0xE9C46A);
            text(modal,templateChoice?(rowMode==13?"Наведите на вариант, чтобы прочитать действие. После выбора появятся допустимые цели.":rowMode==7?"Создайте Густой туман или Проливной дождь. Затем выберите ряд соперника.":"Чистое небо: очистить погоду. Сбор: разыграть случайный бронзовый отряд из колоды."):pileChoice?(rowMode==14?requestMessage:"Выбранная карта будет разыграна из колоды или сброса. Для отряда затем выберите место в ряду."):handPowerChoice?"Изначальная сила выбранного отряда определит эффект. Отряд останется в руке.":graveyardChoice?"Выберите один бронзовый или серебряный отряд. Его сила усилит Гуля; карта исчезнет из сброса.":"Нажмите карту, чтобы сразу заменить её. Можно сохранить руку и начать раунд раньше.",24,57,950,19);
            var pages:int=Math.max(1,Math.ceil(requestCards.length/12));
            choicePage=Math.min(choicePage,pages-1);
            for(var i:int=choicePage*12;i<Math.min(requestCards.length,(choicePage+1)*12);i++)
            {
                var c:Object=requestCards[i];
                var slot:int=i-choicePage*12;
                var p:Sprite=panel(modal,24+(slot%6)*158,108+int(slot/6)*185,140,160,c.revealed?0x193E53:0x532D25,.98);
                if(c.revealed)paintChoiceArt(p,c.templateId,134,154);
                var band:Sprite=panel(p,3,105,134,52,0x101315,.87);band.mouseEnabled=false;
                var name:TextField=text(p,c.templateId==113402?"Сбор · случайный отряд":c.title,8,108,124,15);name.height=46;
                var powerLabel:String="";var choicePowerColor:uint=0xFFFFFF;
                for each(var handCard:Object in cards) if(handCard.id==c.id) {
                    powerLabel=handCard.power>0?"Сила: "+handCard.power:"Особая карта";choicePowerColor=powerColor(handCard);
                    break;
                }
                var powerBand:Sprite=panel(p,3,3,134,25,0x101315,.82);powerBand.mouseEnabled=false;
                text(p,c.revealed?powerLabel:"Рубашка",8,4,124,16,choicePowerColor);
                if(c.revealed){
                    for each(var visibleCard:Object in cards)if(visibleCard.id==c.id){c.tokens=visibleCard.tokens;c.timer=visibleCard.timer;break;}
                    if(int(c.timer)>=0)paintTimer(p,4,30,int(c.timer),(int(c.tokens)&4)!=0);
                    if((int(c.tokens)&4)!=0)paintLock(p,113,30);
                    if((int(c.tokens)&1)!=0)text(p,"∞",112,52,22,20,0xC8ED96);
                    attachInspect(p,c,cardDetails[c.id]);
                }
                if(c.selected||keyboardFocusId==c.id){p.graphics.lineStyle(4,keyboardFocusId==c.id?0xF5E6A7:0xE9C46A);p.graphics.drawRect(0,0,140,160);}
                attachRequestCard(p,c.id);
            }
            text(modal,templateChoice?(rowMode==13?"Вариант выбирается для этого розыгрыша.":rowMode==7?"Выберите одну карту погоды, затем ряд противника.":"Нажмите вариант; затем выберите свой ряд, если разыгрывается отряд."):pileChoice?(rowMode==14?(requestFinish?"Выберите карту для способности.   ·   Страница ":"Выбор обязателен — укажите карту.   ·   Страница "):(requestFinish?"Выберите карту для розыгрыша.   ·   Страница ":"Розыгрыш обязателен — выберите карту.   ·   Страница "))+(choicePage+1)+" / "+pages:handPowerChoice?"Выберите одну карту.   ·   Страница "+(choicePage+1)+" / "+pages:graveyardChoice?"Можно завершить без поглощения.   ·   Страница "+(choicePage+1)+" / "+pages:"Заменено: "+requestCount+" / "+requestMax+"   ·   Страница "+(choicePage+1)+" / "+pages,24,490,900,18);
            button("Назад",474,745,180,ready&&choicePage>0,function():void{choicePage--;render();},choiceLayer);
            button("Вперёд",670,745,180,ready&&choicePage+1<pages,function():void{choicePage++;render();},choiceLayer);
            if(requestFinish&&!templateChoice&&!handPowerChoice)button(pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):graveyardChoice?"Не поглощать":"Начать раунд",1124,745,290,ready&&requestFinish,requestAction("OnBetaGwentRequestFinish"),choiceLayer);
        }
        private function drawBacks():void
        {
            var count:int=Math.max(0,enemyHand);
            var spacing:Number=Math.min(54,750/Math.max(1,count));
            var backWidth:Number=Math.min(46,Math.max(8,spacing-4));
            for(var i:int=0;i<count;i++){
                var back:Sprite=new Sprite();back.mouseEnabled=false;back.mouseChildren=false;content.addChild(back);
                back.x=630+i*spacing;back.y=96;
                var exposed:Object=null;for each(var hc:Object in cards)if(hc.side==2&&hc.zone==8&&hc.index==i&&(hc.tokens&64)!=0)exposed=hc;
                if(exposed){paintChoiceArt(back,exposed.templateId,backWidth,68);if(backWidth>=24)text(back,String(exposed.power),2,2,backWidth-4,14,powerColor(exposed));back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,68);}
                else paintCardBack(back,backWidth,68,2);
                if(activeCue&&activeCue.kind==14&&i>=previousEnemyHand&&enemyHand>previousEnemyHand){
                    var finalX:Number=back.x;
                    animations.push({sprite:back,fromX:310,fromY:426,toX:finalX,toY:96,appear:true,remove:false,
                        duration:380,arc:36,fromScaleX:.6,fromScaleY:.6,toScaleX:1,toScaleY:1});
                    back.x=310;back.y=426;back.scaleX=back.scaleY=.6;back.alpha=0;
                }
            }
        }
    }
}

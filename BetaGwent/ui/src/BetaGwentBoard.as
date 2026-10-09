package
{
    import flash.display.Bitmap;
    import flash.display.Sprite;
    import flash.display.Graphics;
    import flash.display.Stage;
    import flash.events.Event;
    import flash.events.MouseEvent;
    import flash.events.KeyboardEvent;
    import flash.events.TextEvent;
    import flash.external.ExternalInterface;
    import flash.geom.Rectangle;
    import flash.geom.Matrix;
    import flash.display.GradientType;
    import flash.filters.GlowFilter;
    import flash.geom.ColorTransform;
    import flash.utils.getTimer;
    import flash.text.TextField;
    import flash.text.TextFormat;
    import flash.text.TextFieldType;

    [SWF(width="1920", height="1080", frameRate="60", backgroundColor="#101113")]
    public class BetaGwentBoard extends Sprite
    {
        // Some shipping GFx builds omit MouseEvent.RIGHT_CLICK. Resolving
        // that static property before registerMenu aborts the entire menu.
        private static const RIGHT_CLICK_EVENT:String="rightClick";
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
        private var aimLayer:Sprite=new Sprite();
        private var actionPreviewLayer:Sprite=new Sprite();
        private var actionPreviewKey:String="";
        private var requestSourceTemplate:int=0;
        private var aimKey:String="";
        private var targetPulses:Array=[];
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
        private var textPurpose:int=0;
        private var textLimit:int=48;
        private var pendingText:String="";
        private var pendingTextAt:int=0;
        private var detailBody:TextField;
        private var catalogAbility:TextField;
        private var detailOpen:Boolean=false;
        private var rightMouseAt:int=-1000;
        private var hoveredCard:Object;
        private var hoveredDetail:Object;
        private var hoverPreviewAt:int=0;
        private var hoverPreviewX:Number=0;
        private var hoverPreviewY:Number=0;
        private var pileOpen:Boolean=false;
        private var pileView:Object;
        private var pilePage:int=0;
        private var pilePicked:Object;
        private var pileDetail:TextField;
        private var pilePicture:Sprite;
        private static const STRIP_PAGE_SIZE:int=5;
        private static const STRIP_CARD_W:Number=280;
        private static const STRIP_CARD_H:Number=340;
        private var cards:Array=[];
        private var revision:int=-1;
        private var round:int=0;
        private var current:int=0;
        private var scores:Array=[0,0];
        private var crowns:Array=[0,0];
        private var coinSide:int=0;
        private var flags:int=0;
        private var message:String="Ожидаю связь с WitcherScript...";
        private var selected:int=0;
        private var skin:int=3;
        private var battlePreview:Sprite;
        private var battlePreviewKey:String="";
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
        private var editorOwnedOnly:Boolean=false;
        private var editorSearch:String="";
        private var editorName:String="";
        private var editorCollection:Sprite;
        private var editorPreview:Sprite;
        private var editorPreviewId:int=0;
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
        private var requestSourceId:int=0;
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
        private var weatherRedrawAt:int=0;
        private var weatherFades:Array=[];
        private var artworkReport:int=-1;
        private var cardDetails:Object={};
        private var playRules:Object={};
        private var placementGhost:Sprite;
        private var placementPreview:Object;
        private var placementMotions:Array=[];
        private var placementGhostAt:int=0;
        private var previousPoses:Object={};
        private var departedPoses:Object={};
        private var departedOrder:Array=[];
        private var consumedVisualIds:Object={};
        private var actionHistory:Array=[];
        private var previousCrowns:Array=[0,0];
        private var previousScores:Array=[0,0];
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
        private var handSortMode:int=0; // Beta grouping, current power, name, draw order.
        private var handSortReverse:Boolean=true;
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
        private var npcDisplayName:String="";
        private var lastInspectedCard:Object;
        private var forcedFaction:int=0;
        public function setEntryContext(mode:int,opponent:String,forced:int):void
        { entryMode=mode;var lines:Array=readableText(opponent).split("|BG_DECK|").join("\n").split("\n");npcDisplayName=String(lines[0]||"Соперник");npcDeckLabel=String(lines.length>1?lines[1]:lines[0]);forcedFaction=forced;deckViewSide=1;background.visible=mode!=1; }

        public function BetaGwentBoard()
        {
            graphics.beginFill(0x101113); graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080); graphics.endFill();
            addChild(background); addChild(content);addChild(aimLayer);addChild(actionPreviewLayer);actionPreviewLayer.mouseEnabled=false;actionPreviewLayer.mouseChildren=false;addChild(betaOverlay);betaOverlay.mouseEnabled=false;betaOverlay.mouseChildren=false;addChild(previewLayer);addChild(dragLayer);addChild(pileLayer);addChild(detailLayer);
            addChild(controllerMenuLayer);
            addChild(nameLayer);
            addChild(introLayer);introLayer.mouseEnabled=false;
            controller=new BetaGwentController(this,controllerContext,controllerCommand);addChild(controller);
            dragLayer.mouseEnabled=false;dragLayer.mouseChildren=false;
            aimLayer.mouseEnabled=false;aimLayer.mouseChildren=false;
            previewLayer.mouseEnabled=false;previewLayer.mouseChildren=false;
            if(registrationName()=="DeckBuilder"||registrationName()=="BetaGwentKeg")entryMode=1;
            background.visible=entryMode!=1;changeSkin(3); render();
            addEventListener(Event.ENTER_FRAME,animateCards);
            addEventListener(Event.ENTER_FRAME,animateWeather);
            addEventListener(Event.ENTER_FRAME,animateReplay);
            addEventListener(Event.ENTER_FRAME,animateBetaOverlay);
            addEventListener(Event.ENTER_FRAME,animateIntro);
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
            var mode:String=nameOpen?"name":detailOpen?"detail":controllerMenuOpen?"actions":pileOpen?"pile":mulliganConfirm?"confirm":base;
            var ps:Boolean=controller&&(controller.device==1||controller.device==6);
            var accept:String=ps?"×":"A",back:String=ps?"○":"B";
            if(controller&&controller.swap){var temp:String=accept;accept=back;back=temp;}
            var inspect:String=ps?"□":"X",alt:String=ps?"△":"Y",view:String=ps?"Touchpad":"View";
            var hint:String="↑↓←→ выбор · "+accept+" подтвердить · "+back+" назад · "+inspect+" карта";
            if(mode=="battle")hint="←→ рука · ↑ поле · "+accept+" выбрать · "+inspect+" описание · "+alt+" удержать: пас · Start действия";
            else if(mode=="inspect")hint="↑↓←→ карта на поле · "+inspect+" / "+accept+" описание · L3 / "+back+" вернуться к руке";
            else if(mode=="placement")hint="←→ место вставки · ↑↓ / LB/RB ряд · "+accept+" поставить · "+back+" отменить · "+inspect+" описание";
            else if(mode=="target")hint="↑↓←→ подсвеченная цель · "+accept+" применить · "+inspect+" описание · "+(isCaranthirChoice()?"LB/RB Мороз без перемещения":"Start кнопки выбора");
            else if(mode=="rows")hint="↑↓ ряд, включая пустой · "+accept+" применить · "+back+" назад";
            else if(mode=="editor")hint=accept+" добавить/убрать · LT − RT + · "+inspect+" карта · "+view+" список · LB/RB страницы · "+alt+" поиск · Start сохранить";
            else if(mode=="name")hint=accept+" буква · "+inspect+" стереть · "+alt+" пробел · LB/RB RU/EN · Start принять · "+back+" отменить";
            else if(mode=="detail")hint="Правый стик / LB/RB: описание · "+back+" / "+inspect+" закрыть";
            else if(mode=="choice"&&skin==3)hint="←→ карта · "+accept+(isMulliganHand()?" заменить · ":" выбрать · ")+inspect+" описание · Правый стик: текст · Start кнопки";
            else if(mode=="pile"&&pileView&&pileView.zone==16)hint="↑↓←→ карта · "+accept+" / "+inspect+" описание · Правый стик: текст · "+back+" вернуться";
            else hint+=" · LB/RB страницы";
            if(playing)hint=accept+" / "+back+": пропустить показ действий";
            var pref:String=mode=="rows"?"row":mode=="placement"?"position":mode=="target"||mode=="choice"||mode=="keg"?"target":mode=="battle"?"hand":mode=="inspect"||mode=="editor"||mode=="catalog"||mode=="pile"?"card":"control";
            return {mode:mode,baseMode:base,typing:controllerTyping,preferred:pref,
                accept:!controllerTyping&&(ready||playing||nameOpen||detailOpen||pileOpen||controllerMenuOpen),replay:playing&&!detailOpen&&!pileOpen,pass:canAct()&&!nameOpen&&!controllerMenuOpen&&!controllerTyping,
                root:nameOpen?nameLayer:detailOpen?detailLayer:controllerMenuOpen?controllerMenuLayer:pileOpen?pileLayer:mulliganConfirm?mulliganDialog:base=="choice"?choiceLayer:content,
                layers:[{root:choiceLayer,mode:"choice"},{root:mulliganDialog,mode:"confirm"},{root:nameLayer,mode:"name"},{root:detailLayer,mode:"detail"},{root:controllerMenuLayer,mode:"actions"},{root:pileLayer,mode:"pile"}],
                hint:hint,hintY:mode=="battle"||mode=="inspect"||mode=="placement"||mode=="target"||mode=="rows"?80:mode=="detail"?940:1040};
        }
        private function controllerPlacement(id:int):Object
        {
            for each(var c:Object in cards)if(c.id==id){var g:Object=rowGeometry(c.side,c.zone);var layout:Object=rowLayout(c.side,c.zone,1);
                return {anchor:id,index:c.index,target:0,side:c.side,zone:c.zone,x:layout.x+c.index*layout.step,y:g.y,w:layout.w,h:g.h};}
            return null;
        }
        private function registerControllerPositions(side:int,zone:int):void
        {
            var g:Object=rowGeometry(side,zone),units:Array=[];
            for each(var c:Object in cards)if(c.side==side&&c.zone==zone)units.push(c);
            units.sortOn("index",Array.NUMERIC);var layout:Object=rowLayout(side,zone,1);
            for(var i:int=0;i<=units.length;i++){
                var target:Object={anchor:i<units.length?units[i].id:0,index:i,target:0,side:side,zone:zone,x:layout.x+i*layout.step,y:g.y,w:layout.w,h:g.h};
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
        private function requestBoardClose():void
        {
            if(entryMode==1||(selectingDecks&&entryMode!=2)||(flags>>4)!=0){send("OnBetaGwentBoardClose",[]);return;}
            closeControllerMenu();clearPlacementGhost();controllerMenuOpen=true;
            panel(controllerMenuLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.8);
            var box:Sprite=betaFrame(controllerMenuLayer,500,330,920,390,-1414);
            text(box,"Завершить партию?",34,30,850,32,0xF5D77F);
            text(box,"Текущая партия будет завершена. Выход из боя с NPC считается поражением.",34,100,850,24).height=110;
            editorSmallButton(box,"Продолжить партию",34,270,410,58,true,closeControllerMenu);
            editorSmallButton(box,"Сдаться и выйти",476,270,410,58,true,function():void{send("OnBetaGwentBoardClose",[]);});
            controller.focusTag("control");
        }
        public function requestCloseFromGame(ignored:int):void
        {
            // Native CloseMenu input must follow the same safe back navigation.
            if(nameOpen){closeNameInput();return;}
            if(detailOpen||controllerMenuOpen||pileOpen||browsingCatalog||kegOpen||editingDeck||selectingDecks||selected>0){controllerCommand("back");return;}
            openControllerMenu();
        }
        private function controllerMenuAction(name:String):Function
        {return function():void{closeControllerMenu();controllerCommand(name);};}
        private function openControllerMenu():void
        {
            if(detailOpen||pileOpen||kegOpen||browsingCatalog||editingDeck||selectingDecks){controller.focusTag("control");return;}
            if(controllerMenuOpen){closeControllerMenu();return;}
            clearPlacementGhost();controllerMenuOpen=true;
            panel(controllerMenuLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.78);
            var box:Sprite=betaFrame(controllerMenuLayer,330,92,1260,880,-1414);
            text(box,"ДЕЙСТВИЯ",28,18,584,30,0xF5D77F);
            editorSmallButton(box,"Продолжить",28,78,584,58,true,closeControllerMenu);
            text(box,"Удерживайте P / Y / △ или монету для паса.",28,158,584,22).height=40;
            editorSmallButton(box,"Способность лидера",28,214,584,58,canAct()&&leaderOne,controllerMenuAction("leader"));
            editorSmallButton(box,"Посмотреть свою колоду",28,282,584,58,canInspectPile(),controllerMenuAction("deck"));
            editorSmallButton(box,"Ваш сброс",28,350,584,58,canInspectPile(),controllerMenuAction("ownGrave"));
            editorSmallButton(box,"Сброс соперника",28,418,584,58,canInspectPile(),controllerMenuAction("enemyGrave"));
            editorSmallButton(box,"Завершить партию…",28,486,584,58,true,requestBoardClose);
            if(skin==3)editorSmallButton(box,"Пропустить анимацию",28,554,584,58,playing,function():void{closeControllerMenu();skipReplay();});
            text(box,"View — колода · LT / RT — сбросы\nR3 — лидер · X — подробности карты\nO — сортировка руки\nДля быстрого паса удерживайте Y / △.",28,640,584,22,0xB9B4A9).height=130;
            text(box,"НАСТРОЙКИ",660,18,560,30,0xF5D77F);
            tempoLabel=button("Темп: "+animationTempo+"×",660,78,268,true,cycleTempo,box);
            motionLabel=button(reducedMotion?"Эффекты: кратко":"Эффекты: полно",942,78,278,true,toggleMotion,box);
            button(soundEnabled?"Звук: вкл":"Звук: выкл",660,146,268,true,toggleSound,box);
            button(!betaAudioAvailable?(betaAudioInstalled?"Фразы: банк не загружен":"Фразы: ждут банк"):voiceEnabled?"Фразы: вкл":"Фразы: выкл",942,146,278,betaAudioAvailable,toggleVoice,box);
            button("Поле Beta",660,214,268,true,function():void{closeControllerMenu();changeSkin(3);render();},box);
            button("Выбор колод",660,282,560,ready&&entryMode!=2,function():void{closeControllerMenu();submitBoard("OnBetaGwentBoardRestart",[serverRevision]);},box);
            button("Рука: "+handSortName(),660,350,268,!playing&&dragId==0,cycleHandSort,box);
            button(handSortReverse?"По убыванию":"По возрастанию",942,350,278,!playing&&dragId==0&&handSortMode!=3,reverseHandSort,box);
            text(box,"ПОСЛЕДНИЕ ДЕЙСТВИЯ",660,438,560,20,0xCFB176);
            text(box,actionHistory.slice(0,8).join("\n"),660,478,560,20,0xD9D6CB).height=260;
        }

        private function controllerPage(direction:int,node:Object):void
        {
            if(detailOpen){controllerScroll(direction*3);return;}
            if(pileOpen){if(pileView&&pileView.zone==16){controller.focusTag("card",direction);return;}pilePage=Math.max(0,pilePage+direction);pilePicked=null;drawPileView();return;}
            if(browsingCatalog){catalogPage=Math.max(0,catalogPage+direction);redrawCatalogGrid();return;}
            if(editingDeck){if(editorDeckPane(node))editorListPage=Math.max(0,editorListPage+direction);else editorPage=Math.max(0,editorPage+direction);render();return;}
            if(selectingDecks){
                var viewed:Object=deckOption(deckViewSide==1?ownPreset:enemyPreset);
                if(node&&node.rect.y>=562&&node.rect.y<984&&viewed)deckPage=Math.max(0,Math.min(Math.ceil(viewed.cards.length/14)-1,deckPage+direction));
                else presetPage=Math.max(0,Math.min(Math.ceil(deckOptions.length/4)-1,presetPage+direction));
                render();return;
            }
            if(requestId>0&&requestKind==1){if(skin==3){controller.focusTag("target",direction);return;}choicePage=Math.max(0,Math.min(Math.ceil(requestCards.length/12)-1,choicePage+direction));render();return;}
            if(canPlaceSelected()||canPlacePending()){controller.focusPlacementRow(direction);return;}
            if(rowRequest||isCaranthirChoice()){controller.focusTag("row",direction);return;}
            controller.focusTag(canPlaceSelected()||canPlacePending()?"position":requestId>0||selected>0?"target":"hand",direction);
        }
        private function controllerScroll(amount:int):void
        {var node:Object=controller.getFocus();var body:TextField=detailOpen?detailBody:pileOpen?pileDetail:requestKind==1&&skin==3&&node&&node.card&&node.card.stripBody?node.card.stripBody as TextField:browsingCatalog?catalogAbility:inspection;if(body)body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV+amount));}
        private function controllerCommand(name:String,node:Object=null):void
        {
            if(name=="trace"){send("OnBetaGwentControllerTrace",[node.code,node.action,node.mode,node.focus]);return;}
            if(introStart>0&&name!="trace"){skipIntro();return;}
            if(name=="device"||name=="mouse"){send("OnBetaGwentControllerDevice",[name=="device"]);return;}
            if(name=="clickSound"||name=="tickSound"){uiSound(name=="tickSound"?3:1);return;}
            if(mulliganConfirm&&["menu","alternate","previous","next","deck","leader","pass","board","ownGrave","enemyGrave"].indexOf(name)>=0)return;
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
                var handFocus:Object=controller.getFocus();
                var handX:Number=handFocus?handFocus.rect.x+handFocus.rect.width/2:960;
                controllerInspectBoard=!controllerInspectBoard;render();
                if(controllerInspectBoard)controller.focusNearestCard("card",handX,900);else controller.getFocus();return;
            }
            if(editingDeck&&!detailOpen){
                if(name=="ownGrave"||name=="enemyGrave"){
                    var editorNode:Object=controller.getFocus();
                    if(editorNode&&editorNode.card&&editorNode.card.tier!=1){var currentCard:Object=editorNode.card;
                        if(name=="ownGrave"&&currentCard.copies>0)editorAction("OnBetaGwentDeckEditorChange",currentCard.templateId,-1)();
                        else if(name=="enemyGrave"&&currentCard.canAdd)editorAction("OnBetaGwentDeckEditorChange",currentCard.templateId,1)();}
                    return;
                }
                if(name=="deck"){var pane:Object=controller.getFocus();controller.focusPane(editorDeckPane(pane),440,true);return;}
                if(name=="menu"){if(ready)editorAction("OnBetaGwentDeckEditorSave")();return;}
                if(name=="alternate"){if(ready)openTextInput(1,editorSearch);return;}
            }
            if(name=="alternate"){openControllerMenu();return;}
            if(name=="focus"){
                if(node.row){focusedSide=node.row.side;focusedRow=node.row.zone;keyboardFocusId=0;}
                if(node.placement)showPlacementGhost(node.placement);else clearPlacementGhost();
                if(node.card){hoveredCard=node.card;hoveredDetail=node.detail;if(inspection&&!editingDeck)inspection.text=cardReading(node.card,node.detail);showBattleCard(node.card,node.detail);if(pileOpen)showPileCard(node.card);if(browsingCatalog){catalogPicked=node.card;redrawCatalogDetail();}}
                if(requestKind==1&&skin==3&&node.card)showMulliganCard(node.card,node.detail);
                if(editingDeck&&node.card)showEditorCard(node.card);
                return;
            }
            if(name=="back"){
                if(detailOpen){closeCardDetail();return;}if(controllerMenuOpen){closeControllerMenu();return;}if(pileOpen){closePileView();return;}
                if(mulliganConfirm){mulliganConfirm=false;render();return;}
                if(browsingCatalog){closeCatalog();return;}if(kegOpen){send("OnBetaGwentBoardClose",[]);return;}
                if(editingDeck){editorAction("OnBetaGwentDeckEditorCancel")();return;}if(selectingDecks){requestBoardClose();return;}
                if(requestId>0){if(isMulliganHand()&&skin==3)requestMulliganFinish();else if(canFinishRequest())sendRequest("OnBetaGwentRequestFinish");return;}
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
            keyboardStage.addEventListener(RIGHT_CLICK_EVENT,onStageClick,true);
            keyboardStage.addEventListener(MouseEvent.MOUSE_DOWN,onStageMouseDown,true,200);
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
                keyboardStage.removeEventListener(RIGHT_CLICK_EVENT,onStageClick,true);
                keyboardStage.removeEventListener(MouseEvent.MOUSE_DOWN,onStageMouseDown,true);
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
        { if(heldKey==e.keyCode)heldKey=0;if(e.keyCode==80)cancelPassHold(); }
        private function onKey(e:KeyboardEvent):void
        {
            var key:int=e.keyCode;
            if(key==27){e.preventDefault();e.stopImmediatePropagation();}
            if(introStart>0){skipIntro();return;}
            if(controllerMenuOpen){if(key==27)closeControllerMenu();return;}
            if(nameOpen){
                if(key>=136&&key<256)return;
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
                    if(typed.length){
                        // Prefer a real Unicode TEXT_INPUT. Some retail GFx builds only send key codes.
                        if(nameRussian&&typed.length==1&&typed.charCodeAt(0)<128){
                            var latin:String="qwertyuiop[]asdfghjkl;'zxcvbnm,.`";
                            var russian:String="йцукенгшщзхъфывапролджэячсмитьбюё";
                            var at:int=latin.indexOf(typed.toLowerCase());
                            if(at>=0)typed=e.shiftKey?russian.charAt(at).toUpperCase():russian.charAt(at);
                        }
                        pendingText=typed;pendingTextAt=getTimer()+35;
                    }
                }
                return;
            }
            if(detailOpen){e.preventDefault();if(key==27||key==73)closeCardDetail();return;}
            if(mulliganConfirm){
                e.preventDefault();
                if(heldKey==key)return;heldKey=key;
                if(key==27){mulliganConfirm=false;render();}
                else if(key==37||key==39){mulliganAnswer=key==37;render();}
                else if(key==13){if(mulliganAnswer)finishMulligan();else{mulliganConfirm=false;render();}}
                return;
            }
            if(kegOpen&&skin==3){e.preventDefault();kegKey(key);return;}
            if(kegOpen){e.preventDefault();if(key==27){kegOpen=false;render();}else if(key>=49&&key<=51&&key-49<kegOffers.length)chooseKeg(kegOffers[key-49].templateId)();return;}
            if(key==73&&!(keyboardStage.focus is TextField&&TextField(keyboardStage.focus).type==TextFieldType.INPUT)){
                e.preventDefault();
                if(pileOpen&&pilePicked)openCardDetail(pilePicked,{description:pilePicked.description});
                else if(hoveredCard)openCardDetail(hoveredCard,hoveredDetail);
                else if(requestKind==1&&skin==3){var choiceFocus:Object=findRequestCard(keyboardFocusId);if(choiceFocus)openCardDetail(choiceFocus.displayCard||choiceFocus,choiceFocus.displayDetail||cardDetails[choiceFocus.id]);}
                else {var focusCard:Object=null;for each(var known:Object in cards)if(known.id==(keyboardFocusId!=0?keyboardFocusId:selected))focusCard=known;
                    if(focusCard)openCardDetail(focusCard,cardDetails[focusCard.id]);}
                return;
            }
            if(pileOpen){
                e.preventDefault();
                if(key==27)closePileView();
                else if(key==37||key==39)stepPileCard(key==37?-1:1);
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
            if([27,13,32,37,38,39,40,49,50,51,79,80,76,78,70].indexOf(key)<0)return;
            e.preventDefault();
            var now:int=getTimer();var arrow:Boolean=key>=37&&key<=40;
            if(heldKey==key&&(!arrow||now-lastKeyTime<110))return;
            heldKey=key;lastKeyTime=now;
            if(dragId!=0){if(key==27){clearDrag();render();}return;}
            if(key==27) {
                if(mulliganConfirm){mulliganConfirm=false;render();return;}
                if(playing){skipReplay();return;}
                if(selected!=0){selected=0;keyboardFocusId=0;focusedRow=0;render();return;}
                if(requestId>0){
                    if(leaderRow&&canFinishRequest())sendRequest("OnBetaGwentRequestFinish");
                    else if(inspection)inspection.text="Способность уже разыграна. Выберите цель или используйте кнопку завершения выбора.";
                    return;
                }
                if(selectingDecks){requestBoardClose();return;}
                openControllerMenu();return;
            }
            if(playing){if(key==32||key==13)skipReplay();return;}
            if(key==79&&!selectingDecks){e.preventDefault();cycleHandSort();return;}
            if(!ready)return;
            if(selectingDecks){
                if(key==13&&entryMode!=1){ready=false;send("OnBetaGwentDeckStart",[revision]);}
                return;
            }
            if(key==37||key==39){cycleCardFocus(key==37?-1:1);return;}
            if(key==38||key==40){cycleRowFocus(key==38?-1:1);return;}
            if(key>=49&&key<=51){chooseRow(requestId>0&&(rowMode==3||rowMode==9||rowMode==10)?2:1,1<<(key-49));return;}
            if(key==13){activateFocus();return;}
            if(key==70&&canFinishRequest()){if(isMulliganHand()&&skin==3)requestMulliganFinish();else sendRequest("OnBetaGwentRequestFinish");return;}
            if(key==80&&canAct()&&passHoldStart==0)passHoldStart=getTimer();
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
        private function onStageMouseDown(e:MouseEvent):void
        {
            if(isInspectMouse(e)){clearDrag();e.preventDefault();e.stopImmediatePropagation();}
        }
        private function onStageClick(e:MouseEvent):void
        {
            if(isInspectMouse(e)){
                e.preventDefault();e.stopImmediatePropagation();
                var now:int=getTimer();if(now-rightMouseAt<120)return;rightMouseAt=now;
                if(detailOpen){closeCardDetail();return;}
                // Only the uncommitted leader placement may be cancelled.
                // RMB can never confirm a row, card or ability request.
                if(leaderRow&&requestId>0&&canFinishRequest()){
                    sendRequest("OnBetaGwentRequestFinish");return;
                }
                if(selected!=0&&requestId==0){
                    selected=0;keyboardFocusId=0;focusedRow=0;clearPlacementGhost();render();return;
                }
                if(hoveredCard)openCardDetail(hoveredCard,hoveredDetail);
                return;
            }
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
        private var aimSourceId:int=0;
        private function submitBoard(eventName:String,args:Array):void
        {
            if(detailOpen||pileOpen||!ready||selectingDecks||(playing&&eventName!="OnBetaGwentBoardRestart"&&eventName!="OnBetaGwentBoardRematch"))return;
            // Remember what the player just played: its follow-up target request aims from that card.
            if(eventName=="OnBetaGwentBoardLeader")aimSourceId=-1;else if(eventName.indexOf("OnBetaGwentBoardPlay")==0&&args.length>1&&int(args[1])>0)aimSourceId=int(args[1]);
            // Block repeat clicks until the authoritative reply. Keep the visual origin intact.
            ready=false;
            if(eventName=="OnBetaGwentBoardRematch"||eventName=="OnBetaGwentBoardRestart"){
                displayedCards={};previousPoses={};departedPoses={};departedOrder=[];consumedVisualIds={};actionHistory=[];lastRoundResult=null;previousCrowns=[0,0];previousEnemyHand=0;
            }
            send(eventName,args);
        }
        private function keyboardCandidates():Array
        {
            if(requestId>0&&!rowRequest)return isMulliganHand()?sortedHand(requestCards):requestCards.concat();
            var result:Array=[];
            for each(var c:Object in cards) {
                if(canPlacePending()?canPlaceBefore(c):canAct()&&c.side==1&&c.zone==8&&c.canPlay)result.push(c);
            }
            if(!canPlacePending())return sortedHand(result);
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
            if(requestKind==1)choicePage=skin==3?0:int(index/12);
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
        // getTimer stays outside send(): the bridge check forbids global-scope calls there.
        private function bridgeClock():int{return getTimer();}
        private function send(eventName:String,args:Array):void
        {
            // Royale emits a global receiver for an unqualified Function-slot call.
            // The native adapter requires this registered DisplayObject as receiver.
            if(_NATIVE_callGameEvent==null)return;
            var started:int=this.bridgeClock();
            _NATIVE_callGameEvent.call(this,eventName,args);
            // The native call is synchronous: report slow AI turns so WS can lower its lookahead.
            var spent:int=this.bridgeClock()-started;
            if(spent>=300&&eventName.indexOf("OnBetaGwentAudio")<0&&eventName!="OnBetaGwentPerf")_NATIVE_callGameEvent.call(this,"OnBetaGwentPerf",[eventName,spent]);
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
        { revision=rev;kegOpen=true;pendingKeg=true;kegAutomatic=[];kegOffers=[];kegPhase=-1;kegRevealed=[false,false,false,false];kegPicked=-1;kegFinalVoiced=false; }
        public function setUnopenedKegs(count:int,pending:Boolean):void
        {unopenedKegs=Math.max(0,count);pendingKeg=pending;}
        public function pushKegCard(id:int,ordinary:Boolean,scraps:int):void
        { var original:Object=BetaGwentFullCatalog.find(id);if(!original)return;var card:Object={};for(var key:String in original)card[key]=original[key];card.duplicateScraps=scraps;card.ordinary=ordinary;(ordinary?kegAutomatic:kegOffers).push(card); }
        public function finishKegOpening(rev:int):void
        { if(rev==revision){ready=true;render();} }
        private function chooseKeg(id:int):Function
        { return function():void{if(!ready)return;kegOpen=false;pendingKeg=false;ready=false;send("OnBetaGwentKegChoose",[revision,id]);}; }
        // ---------------------------------------------------------------------------------
        // Stage 109: Beta 0.9.24 keg opening. Troll flipbook (keg menu only, pages 21+), flash,
        // four faction backs to reveal, choice of the fifth card, "your new cards".
        private var kegPhase:int=-1;private var kegRevealed:Array=[false,false,false,false];private var kegPicked:int=-1;
        private var kegTroll:Sprite;private var kegT0:int=0;private var kegFlown:Boolean=false;private var kegFinalVoiced:Boolean=false;
        private static const KEG_RARITY_COLOR:Object={1:0xD9D4C7,2:0x3FA9F5,4:0xB35CFF,8:0xF0C24A};
        private function kegCardRarity(c:Object):int{return cardRarity(c);}
        private function kegFactionIndex(faction:int):int{return faction==1?5:editorFactionIndex(faction);}
        private function kegBack(faction:int):int{return BetaGwentKeg109.BACK0-kegFactionIndex(faction);}
        private function kegKey(key:int):void
        {
            if(key==27){kegClose();return;}
            if(kegPhase==0){kegSkipTroll();return;}
            if(kegPhase==1&&(key==32||key==13)){kegRevealNext();return;}
            if(kegPhase==2){if(key>=49&&key<=51&&key-49<kegOffers.length){kegPicked=key-49;render();}else if((key==32||key==13)&&kegPicked>=0){kegPhase=3;kegVoice(6);render();}return;}
            if(kegPhase==3&&(key==32||key==13))kegFinish();
        }
        // Shop troll lines (duelAudio.Keg): 1 smash, 2-5 reveal by rarity, 6 choice, 7 final, 8 before smash.
        private function kegVoice(kind:int):void{ if(connected&&soundEnabled)send("OnBetaGwentAudioKeg",[kind]); }
        private function kegClose():void
        {
            kegStopTroll();kegOpen=false;
            if(registrationName()=="BetaGwentKeg")send("OnBetaGwentBoardClose",[]);else render();
        }
        private function kegStopTroll():void
        { if(kegTroll){kegTroll.removeEventListener(Event.ENTER_FRAME,kegTrollFrame);if(kegTroll.parent)kegTroll.parent.removeChild(kegTroll);kegTroll=null;} }
        private function kegSkipTroll():void{kegStopTroll();kegPhase=1;kegFlown=false;render();}
        private var kegTrollVoices:int=0;
        private function kegTrollFrame(e:Event):void
        {
            if(!kegTroll)return;
            var frame:int=int((getTimer()-kegT0)*BetaGwentKeg109.FPS/1000);
            if(frame>=BetaGwentKeg109.FRAMES){kegSkipTroll();return;}
            if(int(kegTroll.name)==frame)return;kegTroll.name=String(frame);
            while(kegTroll.numChildren)kegTroll.removeChildAt(0);
            var view:Sprite=BetaGwentHDArt.view(BetaGwentKeg109.FRAME0-frame,BetaGwentKeg109.PATCH_W,BetaGwentKeg109.PATCH_H);
            if(view){view.x=BetaGwentKeg109.PATCH_X;view.y=BetaGwentKeg109.PATCH_Y;kegTroll.addChild(view);}
            if(kegTrollVoices==0){kegVoice(8);kegTrollVoices=1;}if(frame>=BetaGwentKeg109.SMASH_FRAME&&kegTrollVoices==1){kegVoice(1);kegTrollVoices=2;}
        }
        private function kegRevealNext():void
        {
            for(var i:int=0;i<kegAutomatic.length;i++)if(!kegRevealed[i]){kegReveal(i);return;}
            kegPhase=2;render();
        }
        private function kegReveal(i:int):void
        {
            if(kegPhase!=1||i<0||i>=kegAutomatic.length||kegRevealed[i])return;
            kegRevealed[i]=true;uiSound(3);var rarity:int=kegCardRarity(kegAutomatic[i]);kegVoice(rarity==8?5:rarity==4?4:rarity==2?3:2);render();
            var card:Sprite=kegSlots[i] as Sprite;
            if(card&&!reducedMotion){
                var w:Number=card.width;card.scaleX=0;
                animations.push({sprite:card,fromX:card.x+w/2,fromY:card.y,toX:card.x,toY:card.y,duration:260,fromScaleX:0,fromScaleY:1,toScaleX:1,toScaleY:1,appear:true});
                betaBurst(content,-103,card.x+KEG_W/2,card.y+KEG_H/2,KEG_W*1.6,KEG_RARITY_COLOR[kegCardRarity(kegAutomatic[i])],0,360);
            }
        }
        private function kegFinish():void
        {
            if(kegPicked<0||kegPicked>=kegOffers.length||!ready)return;
            var id:int=int(kegOffers[kegPicked].templateId);kegStopTroll();
            kegOpen=false;pendingKeg=false;ready=false;send("OnBetaGwentKegChoose",[revision,id]);
        }
        private static const KEG_W:Number=300,KEG_H:Number=365;
        private var kegSlots:Array=[];
        private function kegTitle(title:String,sub:String):void
        {
            betaLabel(content,title,0,34,1920,30,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",6);
            content.graphics.lineStyle(1,0x8C7A5C,.7);content.graphics.moveTo(460,82);content.graphics.lineTo(1460,82);content.graphics.lineStyle();
            betaLabel(content,sub,0,96,1920,19,0xE8E4DA,BetaGwentFonts.BODY,false,"center");
        }
        private function kegCardFace(parent:Sprite,c:Object,x:Number,y:Number,glow:Boolean):Sprite
        {
            var p:Sprite=new Sprite();p.x=x;p.y=y;parent.addChild(p);
            paintBetaFace(p,int(c.templateId),KEG_W,KEG_H,1);
            if(c.typeMask==4||c.power>0)betaPowerField(p,String(c.power),KEG_W,KEG_H,0xFFFFFF);
            var color:uint=KEG_RARITY_COLOR[kegCardRarity(c)];
            if(glow)p.filters=[new GlowFilter(color,1,26,26,2.4,2)];
            var name:TextField=betaLabel(parent,String(c.title).toUpperCase(),x-10,y+KEG_H+14,KEG_W+20,17,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2);
            var stripe:Sprite=new Sprite();stripe.graphics.beginFill(color,1);stripe.graphics.drawRect(0,0,3,46);stripe.graphics.endFill();
            stripe.x=x;stripe.y=y+KEG_H+8;parent.addChild(stripe);
            var outcome:String=c.duplicateScraps<0?"Получена ранее":c.duplicateScraps>0?"Лишняя копия → осколки: +"+c.duplicateScraps:c.ordinary?"Добавлена в коллекцию":"Будет добавлена в коллекцию";
            betaLabel(parent,outcome,x,y+KEG_H+44,KEG_W,17,c.duplicateScraps>0?0xF0CE79:0xA3D8B5,BetaGwentFonts.BODY,false,"center");
            var desc:TextField=text(parent,c.description||"",x+10,y+KEG_H+78,KEG_W-10,15,0xC9C2B4);desc.height=100;
            attachInspect(p,c,{description:c.description},KEG_W,KEG_H);
            return p;
        }
        private function drawKegBeta():void
        {
            kegSlots=[];
            if(kegPhase<0){kegPhase=BetaGwentHDArt.has(BetaGwentKeg109.FRAME0)&&registrationName()=="BetaGwentKeg"?0:1;kegT0=getTimer();kegTrollVoices=0;kegFlown=false;}
            content.graphics.beginFill(0x080909,1);content.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);content.graphics.endFill();
            if(kegPhase==0){
                var scene:Sprite=BetaGwentHDArt.view(BetaGwentKeg109.SCENE,1920,1080);if(scene)content.addChild(scene);
                kegStopTroll();kegTroll=new Sprite();kegTroll.name="-1";content.addChild(kegTroll);
                kegTroll.addEventListener(Event.ENTER_FRAME,kegTrollFrame);kegTrollFrame(null);
                var skip:Sprite=new Sprite();skip.graphics.beginFill(0,0);skip.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);skip.graphics.endFill();
                skip.buttonMode=true;skip.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{kegSkipTroll();});content.addChild(skip);
                controller.registerControl(skip,"Пропустить",kegSkipTroll,null,null,"target");
                return;
            }
            var bg:Sprite=BetaGwentHDArt.view(BetaGwentKeg109.BACKGROUND,1920+2*WIDE_PAD,1080);
            if(bg){bg.x=-WIDE_PAD;content.addChild(bg);}else wideArt(content,BetaGwentDeckArt104.BG_SETUP);
            var shade:Sprite=new Sprite();shade.mouseEnabled=false;shade.graphics.beginFill(0,.35);shade.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);shade.graphics.endFill();content.addChild(shade);
            var i:int;var x:Number;var c:Object;var p:Sprite;
            if(kegPhase==1){
                kegTitle("ВСКРОЙТЕ ПЕРВЫЕ ЧЕТЫРЕ КАРТЫ","Вскройте каждую карту. Вскрыв все четыре, вы сможете выбрать свою пятую карту.");
                var all:Boolean=true;
                for(i=0;i<kegAutomatic.length;i++){
                    c=kegAutomatic[i];x=(1920-(kegAutomatic.length*KEG_W+(kegAutomatic.length-1)*150))/2+i*(KEG_W+150);
                    if(kegRevealed[i]){p=kegCardFace(content,c,x,232,kegCardRarity(c)>=2);kegSlots[i]=p;continue;}
                    all=false;p=new Sprite();p.x=x;p.y=232;content.addChild(p);kegSlots[i]=p;
                    if(!paintArt(p,kegBack(int(c.faction)),KEG_W,KEG_H,0,0)&&!paintArt(p,BetaGwentHud104.cardBack(kegFactionIndex(int(c.faction))),KEG_W,KEG_H,0,0))paintCardBack(p,KEG_W,KEG_H,1);
                    p.buttonMode=true;
                    // Beta: hovering a closed card shows its rarity glow.
                    (function(card:Sprite,index:int,color:uint):void{
                        card.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{card.filters=[new GlowFilter(color,1,30,30,2.6,2)];});
                        card.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{card.filters=[];});
                        card.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{kegReveal(index);});
                        controller.registerControl(card,"Вскрыть карту",function():void{kegReveal(index);},null,null,"target");
                    })(p,i,KEG_RARITY_COLOR[kegCardRarity(c)]);
                    if(!kegFlown&&!reducedMotion){
                        var angle:Number=(i%2==0?-1:1)*(140+i*35);
                        animations.push({sprite:p,fromX:960-KEG_W/2,fromY:420,toX:x,toY:232,duration:520,delay:i*70,hideBeforeDelay:true,appear:true,
                            fromScaleX:.25,fromScaleY:.25,toScaleX:1,toScaleY:1,fromRotation:angle,toRotation:0});
                    }
                }
                if(!kegFlown&&!reducedMotion)betaBurst(content,-103,960,500,900,0x9FD7FF,0,420);
                kegFlown=true;
                betaWideButton(all?"Продолжить":"Открыть следующую",820,1002,280,ready,function():void{if(all){kegPhase=2;render();}else kegRevealNext();});
            }else if(kegPhase==2){
                kegTitle("ВЫБЕРИТЕ ВАШУ ПЯТУЮ КАРТУ","Выберите одну из карт внизу.");
                for(i=0;i<kegOffers.length;i++){
                    c=kegOffers[i];x=(1920-(kegOffers.length*KEG_W+(kegOffers.length-1)*200))/2+i*(KEG_W+200);
                    p=kegCardFace(content,c,x,232,kegPicked==i);if(kegPicked>=0&&kegPicked!=i)p.alpha=.7;
                    p.buttonMode=true;
                    (function(index:int):void{
                        p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{kegPicked=index;uiSound(3);render();});
                        controller.registerControl(p,"Выбрать карту",function():void{kegPicked=index;render();},null,null,"target");
                    })(i);
                }
                betaWideButton("Выбрать",820,1002,280,ready&&kegPicked>=0,function():void{kegPhase=3;kegVoice(6);render();});
            }else{
                kegTitle("ВАШИ НОВЫЕ КАРТЫ!","Лишние копии превращаются в осколки.");
                var got:Array=kegAutomatic.concat(kegPicked>=0?[kegOffers[kegPicked]]:[]);
                var received:int=0,duplicateCount:int=0,totalScraps:int=0,unknown:Boolean=false;
                for each(var result:Object in got){if(result.duplicateScraps<0)unknown=true;else if(result.duplicateScraps>0){duplicateCount++;totalScraps+=result.duplicateScraps;}else received++;}
                if(!unknown)betaLabel(content,"В коллекцию: "+received+" · Лишних копий: "+duplicateCount+" · Осколки: +"+totalScraps,0,150,1920,22,0xF0CE79,BetaGwentFonts.BODY,false,"center");
                var step:Number=Math.min(KEG_W+60,(1820-KEG_W)/Math.max(1,got.length-1));
                for(i=0;i<got.length;i++){
                    x=(1920-(KEG_W+step*(got.length-1)))/2+i*step;p=kegCardFace(content,got[i],x,232,kegCardRarity(got[i])>=2);
                    var firstShow:Boolean=i==got.length-1&&!kegFinalVoiced;
                    if(firstShow){kegFinalVoiced=true;kegVoice(7);}
                    if(firstShow&&!reducedMotion){betaBurst(content,-103,x+KEG_W/2,232+KEG_H/2,820,0x8FD0FF,0,460);
                        animations.push({sprite:p,fromX:x,fromY:232,toX:x,toY:232,duration:420,appear:true,fromScaleX:1.25,fromScaleY:1.25,toScaleX:1,toScaleY:1});}
                }
                betaWideButton("Готово",820,1002,280,ready,kegFinish);
            }
        }
        private function drawKeg():void
        {
            if(skin==3){drawKegBeta();return;}
            wideArt(content,BetaGwentDeckArt104.BG_SETUP);betaWindow(content,64,24,1792,1032);
            text(content,"BETA GWENT · ОПЛАЧЕННАЯ БОЧКА",96,49,1390,32,0xE8D3A6);
            editorSmallButton(content,"Продолжить позже",1510,48,310,42,true,function():void{kegOpen=false;render();});
            text(content,"Добавлено бронзовых карт: "+kegAutomatic.length+" / 4. Выберите одну редкую карту; варианты сохраняются вместе с игрой.",96,111,1728,24).height=70;
            var n:int;var c:Object;var tile:Sprite;var x:Number;var y:Number;
            for(n=0;n<kegAutomatic.length+kegOffers.length;n++){
                var ordinary:Boolean=n<kegAutomatic.length;var index:int=ordinary?n:n-kegAutomatic.length;
                c=ordinary?kegAutomatic[index]:kegOffers[index];
                x=ordinary?(1920-(kegAutomatic.length*280-22))/2+index*280:530+index*300;y=ordinary?203:568;
                tile=betaFrame(content,x,y,258,288);
                paintArt(tile,c.templateId,180,253,39,4);betaNine(tile,-1412,184,257,37,2);
                tile.graphics.lineStyle(3,editorTierColor(c.tier));tile.graphics.drawRoundRect(0,0,258,288,8,8);
                panel(tile,4,225,250,58,0x11191C,.95);text(tile,c.title,12,229,232,21).height=54;
                panel(tile,4,4,250,28,0x11191C,.9);
                text(tile,c.tier==1?"Лидер":c.tier==8?"Золото":c.tier==4?"Серебро":"Бронза",10,5,235,19,editorTierColor(c.tier));
                attachInspect(tile,c,{description:c.description},258,288);
                if(!ordinary)controller.registerControl(tile,c.title,chooseKeg(c.templateId),c,{description:c.description},"target");
                if(!ordinary)editorSmallButton(content,"Выбрать · "+(index+1),x,y+305,258,47,ready,chooseKeg(c.templateId));
                animations.push({sprite:tile,fromX:x+129,fromY:y+18,toX:x,toY:y,
                    duration:390,delay:index*110+(ordinary?0:400),hideBeforeDelay:true,appear:true,
                    fromScaleX:.08,fromScaleY:.94,toScaleX:1,toScaleY:1});
            }
            text(content,"Выбор из трёх карт одной редкости: редкая 60%, эпическая 30%, легендарная 10%. Лишние копии превращаются в осколки. Закрытие окна не меняет содержимое.",96,1004,1728,20,0xE8D3A6);
        }
        public function setOwnedCopies(id:int,copies:int):void
        {
            // Id -1 is the scraps balance, sent after the whole collection: refresh the open catalog once.
            if(id==-1){scraps=copies;if(browsingCatalog){if(catalogGrid)redrawCatalogGrid();redrawCatalogDetail();if(catalogScrapsLabel)catalogScrapsLabel.text="Осколки: "+scraps;}else if(editingDeck&&editorCollection&&skin==3)redrawEditorCollection();return;}
            ownedCopies[id]=copies;
        }
        private var scraps:int=0;private var catalogScrapsLabel:TextField;
        // Beta 0.9.24 rarity and price list: craft 30/80/200/800, mill 10/20/50/200.
        private static const RARE_BRONZE:Array=[113204,113307,113308,113319,113320,122302,122304,122307,122309,122311,122313,122314,122316,122317,122403,132201,132211,132212,132302,132305,132308,132313,132315,132402,132407,132409,133301,142302,142304,142306,142307,142308,142309,142312,142315,142317,152210,152301,152304,152306,152307,152310,152312,152314,152316,152318,153301,162301,162303,162304,162307,162309,162311,162313,162314,200008,200009,200021,200026,200033,200036,200037,200038,200039,200040,200042,200044,200046,200048,200049,200067,200081,200105,200112,200114,200115,200118,200124,200132,200135,200136,200138,200139,200144,200145,200146,200149,200224,200233,200293,200294,200295,200296,200299,200300,200301,200518,200519,200528,200535,200539,200540,201559,201578,201598,201599,201600,201606,201609,201610,201612,201616,201617,201619,201622,201624,201625,201628,201630,201631,201633,201636,201638,201643,201645,201647,201656,201659,201661,201700,201701,201744,201749,201753];
        private function cardRarity(c:Object):int{ if(c.tier==1||c.tier==8)return 8; if(c.tier==4)return 4; return RARE_BRONZE.indexOf(int(c.templateId))>=0?2:1; }
        private function craftCost(c:Object):int{ var r:int=cardRarity(c); return r==8?800:r==4?200:r==2?80:30; }
        private function millValue(c:Object):int{ var r:int=cardRarity(c); return r==8?200:r==4?50:r==2?20:10; }
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
        // stage104-matchsetup
        // UIMatchSetupPrefab (title plaque, deck list, leader frame,
        // НАЧАТЬ БОЙ, side preview) and DeckPickerPrefab/DeckList (ЗАМЕНИТЬ КОЛОДУ).
        private var pickerSide:int=0;
        private var deckListScroll:int=0;
        private function tierFrame(tier:int):int
        { return tier==8||tier==1?BetaGwentDeckArt104.DP_GOLD:tier==4?BetaGwentDeckArt104.DP_SILVER:BetaGwentDeckArt104.DP_BRONZE; }
        private function betaPlaque(title:String):void
        {
            paintArt(content,BetaGwentHud104.CHAIN,14,60,650,-6);paintArt(content,BetaGwentHud104.CHAIN,14,60,1256,-6);
            betaNine(content,-1400,690,74,615,30);
            betaLabel(content,title.toUpperCase(),635,46,650,30,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",6).mouseEnabled=false;
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
                betaSlotLabel(row,"x"+int(c.copies),w-h+6,6,h-12,h-12,16,0xF2EEE4,BetaGwentFonts.BODY);
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
            wideArt(content,BetaGwentDeckArt104.BG_SETUP);
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
            var hdCover:int=BetaGwentCovers107.cover(chosenLeaders[0]);
            if(hdCover!=0&&BetaGwentHDArt.has(hdCover)){
                var coverArt:Sprite=BetaGwentHDArt.view(hdCover,625,440);
                if(coverArt){coverArt.x=18;coverArt.y=18;frame.addChild(coverArt);}
            }else if(size){
                var sw:Number=size[0],sh:Number=size[1];var cw:Number=sw,ch:Number=Math.min(sh,sw*440/625);
                var leaderArt:Sprite=BetaGwentHDArt.clip(chosenLeaders[0],625,440,0,(sh-ch)*.2,cw,ch);
                if(leaderArt){leaderArt.x=18;leaderArt.y=18;frame.addChild(leaderArt);}
            }
            betaNine(frame,BetaGwentDeckArt104.MS_FRAME,661,475);
            var leader:Object=leaderOption(chosenLeaders[0]);
            var tag:Sprite=new Sprite();tag.x=780;tag.y=322;content.addChild(tag);
            paintArt(tag,BetaGwentDeckArt104.MS_NAME_BG,358,61,0,0);paintArt(tag,-1501-Math.min(4,fi),34,34,24,13);
            betaSlotLabel(tag,leader?leader.title:(first?first.leader:""),62,0,234,61,18,0xF2EEE4,BetaGwentFonts.BODY);
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
            }else if(entryMode==2)betaLabel(content,"Соперник: "+npcDisplayName+" · выход из боя считается поражением",500,912,900,18,0x3A2A16,BetaGwentFonts.BODY);
            // right: wooden preview panel
            paintArt(content,BetaGwentHud104.WOOD_PANEL,405,822,1477,138);
            paintArt(content,BetaGwentHud104.PREVIEW_SLOT,285,398,1545,177);
            battlePreview=new Sprite();battlePreview.mouseEnabled=false;battlePreview.mouseChildren=false;content.addChild(battlePreview);
            inspection=new TextField();
            if(leader)showBattleCard({templateId:chosenLeaders[0],title:leader.title,power:leader.power,side:1,zone:64,tokens:0,description:leader.description},{description:leader.description});
            // bottom buttons
            var savedCount:int=0;for each(var saved:Object in deckOptions)if(saved.id>=1001)savedCount++;
            betaWideButton(pickerSide==1?"Назад":"Заменить колоду",560,1002,300,ready,function():void{pickerSide=pickerSide==1?0:1;presetPage=0;render();});
            betaWideButton("Редактировать",880,1002,260,ready&&(ownPreset>=1001||ownPreset>=16&&ownPreset<=20||savedCount<8),openEditorAction(ownPreset));
            betaWideButton("Все карты",1160,1002,200,ready,function():void{browsingCatalog=true;catalogPage=0;render();});
            betaWideButton(entryMode==2?"Отказаться":"Выход",1380,1002,200,connected,requestBoardClose);
            if(entryMode==1&&(pendingKeg||unopenedKegs>0))betaWideButton(pendingKeg?"Бочка: выбор":"Бочки · "+unopenedKegs,1600,1002,260,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});
        }
        private function drawDeckSelection():void
        {
            if(skin==3){drawBetaMatchSetup();return;}
            wideArt(content,BetaGwentDeckArt104.BG_SETUP);betaWindow(content,64,24,1792,1032);
            text(content,entryMode==1?"BETA GWENT 0.9.24 · ВАШИ КОЛОДЫ":"BETA GWENT 0.9.24 · КОЛОДА ПЕРЕД БОЕМ",96,44,1080,28,0xE8D3A6);
            var savedCount:int=0;for each(var saved:Object in deckOptions)if(saved.id>=1001)savedCount++;
            var viewId:int=deckViewSide==1?ownPreset:enemyPreset;
            button("Создать колоду",1200,44,270,ready&&savedCount<8,openEditorAction(0));
            button("Редактировать",1486,44,338,ready&&(viewId>=1001||viewId>=16&&viewId<=20||savedCount<8),openEditorAction(viewId));
            editorSmallButton(content,"Все карты",96,94,226,38,ready,function():void{browsingCatalog=true;catalogPage=0;render();});
            if(entryMode==1&&(pendingKeg||unopenedKegs>0))editorSmallButton(content,pendingKeg?"Продолжить выбор бочки":"Открыть бочку · "+unopenedKegs,96,990,420,48,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});
            text(content,entryMode==2?"Выберите свою колоду. Состав соперника скрыт: "+npcDeckLabel:entryMode==1?"Выберите сохранённую колоду для просмотра или редактирования.":"Выберите свою колоду и колоду соперника. Состав — ниже.",340,99,1000,20);
            var presetPages:int=Math.max(1,Math.ceil(deckOptions.length/4));presetPage=Math.min(presetPage,presetPages-1);
            if(presetPages>1){
                text(content,"Колоды "+(presetPage+1)+" / "+presetPages,1390,103,164,18,0xE8D3A6);
                button("←",1568,94,80,ready&&presetPage>0,function():void{presetPage--;render();});
                button("→",1660,94,80,ready&&presetPage+1<presetPages,function():void{presetPage++;render();});
            }
            var columns:int=Math.min(4,deckOptions.length);var tileWidth:Number=(1728-(columns-1)*24)/Math.max(1,columns);
            for(var i:int=presetPage*4;i<Math.min(deckOptions.length,(presetPage+1)*4);i++){
                var option:Object=deckOptions[i];var x:Number=96+(i-presetPage*4)*(tileWidth+24);
                var tile:Sprite=betaWindow(content,x,148,tileWidth,236);
                paintArt(tile,-1420-editorFactionIndex(cardFaction(option.leaderId)),tileWidth,72,0,0);
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
            betaWindow(content,96,562,1728,320);
            for(var ordinal:int=deckPage*14;ordinal<Math.min(viewed.cards.length,(deckPage+1)*14);ordinal++){
                var c:Object=viewed.cards[ordinal];var n:int=ordinal-deckPage*14;
                var card:Sprite=betaWindow(content,108+(n%7)*244,574+int(n/7)*154,230,150);
                paintArt(card,c.templateId,64,86,5,5);
                var label:TextField=text(card,c.title,82,6,144,18,0xF1E8D3);label.height=52;
                text(card,"×"+c.copies+(c.typeMask==4?" · сила "+c.power:" · особая"),82,58,144,17,0xE8D3A6);
                text(card,c.tier==8?"Золото":c.tier==4?"Серебро":"Бронза",82,84,144,16,0xB9B4A9);
                var ability:TextField=text(card,c.description,8,106,214,14,0xD8D0BB);ability.height=38;
                attachInspect(card,c,{description:c.description},230,150);
            }
            button("Назад",96,900,164,ready&&deckPage>0,function():void{deckPage--;render();});
            button("Вперёд",274,900,164,ready&&deckPage+1<pages,function():void{deckPage++;render();});
            inspection=text(content,"Наведите на карту: иллюстрация крупнее, теги и полное описание способности.",468,900,1356,18,0xD8D0BB);inspection.height=84;
            var first:Object=deckOption(ownPreset);var second:Object=deckOption(enemyPreset);
            if(entryMode!=1)button("Начать партию",96,990,420,ready&&first!=null&&(entryMode==2||second!=null),function():void{
                if(!ready||!selectingDecks)return;var expected:int=revision;ready=false;send("OnBetaGwentDeckStart",[expected]);
            });
            text(content,"Сохранено "+savedCount+" / 8 · "+(entryMode==2?"Выход из боя считается поражением.":(first?first.title:"")+(entryMode==0&&second?" против "+second.title:"")),546,1002,960,19,0xE8D3A6);
            button(entryMode==2?"Отказаться от боя":"Закрыть",1574,990,250,connected,requestBoardClose);
        }
        // Collection snapshots are authoritative; inputs and filters stay local to this editor.
        public function beginDeckEditor(rev:int,slot:int,faction:int,leader:int,title:String,total:int,golds:int,silvers:int,valid:Boolean):void
        {
            if(rev<serverRevision)return;
            if(!editingDeck||!editorState||editorState.slot!=slot){
                editorName=title;editorSearch="";editorTier=0;editorType=0;editorFactionOnly=false;editorOwnedOnly=false;editorCraft=null;editorPage=0;editorListPage=0;
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
            if(nameOpen&&pendingTextAt>0&&getTimer()>=pendingTextAt){var value:String=pendingText;pendingText="";pendingTextAt=0;editName(value);}
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
                if(query&&(c.title+" "+c.description+" "+c.tags+" "+c.templateId).toLowerCase().indexOf(query)<0)continue;
                found.push(c);
            }return found;
        }
        private function catalogPick(c:Object):Function
        { return function():void{catalogPicked=c;redrawCatalogDetail();}; }
        private function redrawCatalogGrid():void
        {
            if(skin==3){redrawBetaCatalogGrid();return;}
            if(!catalogGrid)return;while(catalogGrid.numChildren)catalogGrid.removeChildAt(0);
            var list:Array=catalogCards();var pages:int=Math.max(1,Math.ceil(list.length/12));
            catalogPage=Math.max(0,Math.min(catalogPage,pages-1));
            for(var i:int=catalogPage*12;i<Math.min(list.length,(catalogPage+1)*12);i++){
                var c:Object=list[i];var n:int=i-catalogPage*12;
                var tile:Sprite=betaFrame(catalogGrid,(n%6)*188,int(n/6)*310,176,298);
                tile.graphics.lineStyle(2,editorTierColor(c.tier));tile.graphics.drawRoundRect(0,0,176,298,6,6);
                if(c.hasArt)paintArt(tile,c.templateId,164,230,6,6);
                else text(tile,"Иллюстрация ещё не найдена",12,70,152,20,0xA9B5BA).height=90;
                panel(tile,5,5,166,31,0x11191C,.92);
                text(tile,c.leader?"Лидер":c.typeMask==2?"Особая карта":"Сила: "+c.power,10,7,157,18,powerColor(c));
                panel(tile,5,179,166,57,0x11191C,.9);
                text(tile,c.title,10,182,155,18).height=53;
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
            if(skin==3){redrawBetaCatalogDetail();return;}
            if(!catalogDetail)return;while(catalogDetail.numChildren)catalogDetail.removeChildAt(0);
            var c:Object=catalogPicked;if(!c){text(catalogDetail,"Нажмите карту слева, чтобы прочитать описание и способ получения.",22,24,504,24).height=150;return;}
            if(c.hasArt)paintArt(catalogDetail,c.templateId,140,197,22,22);
            text(catalogDetail,c.title,178,22,350,28,0xE8D3A6).height=85;
            var tier:String=c.tier==1?"Лидер":c.tier==8?"Золотая":c.tier==4?"Серебряная":"Бронзовая";
            var factionNames:Object={1:"Нейтральная",2:"Чудовища",4:"Нильфгаард",8:"Северные королевства",16:"Скоя'таэли",32:"Скеллиге"};
            text(catalogDetail,tier+" · "+(c.typeMask==2?"Особая":"Отряд")+"\n"+(c.typeMask==4?"Сила: "+c.power+"\n":"")+factionNames[c.faction],178,122,350,20).height=95;
            text(catalogDetail,"Теги: "+(c.tags||"—"),22,268,504,18,0xA7DCEE).height=55;
            var ability:TextField=text(catalogDetail,c.description||"Описание в исходной локализации отсутствует.",22,333,504,23);ability.height=200;
            catalogAbility=ability;
            ability.mouseEnabled=true;ability.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{ability.scrollV-=e.delta;e.stopPropagation();});
            editorSmallButton(catalogDetail,"↑",456,540,32,30,true,function():void{ability.scrollV--;});
            editorSmallButton(catalogDetail,"↓",496,540,32,30,true,function():void{ability.scrollV++;});
            text(catalogDetail,c.acquisition,22,587,504,23,0xE8D3A6).height=56;
            text(catalogDetail,"В коллекции: "+int(ownedCopies[c.templateId])+" / "+(c.tier==2?3:1)+". "+(entryMode==0?"Практика позволяет использовать все карты.":"В редакторе доступны только полученные копии."),22,667,504,19,0xB4B5AE).height=85;
            var owned:int=int(ownedCopies[c.templateId]),cap:int=c.tier==2?3:1;
            var rarityNames:Object={1:"Обычная",2:"Редкая",4:"Эпическая",8:"Легендарная"};
            text(catalogDetail,rarityNames[cardRarity(c)]+" · создать "+craftCost(c)+" · осколков: "+scraps,22,758,504,18,0xE8D3A6).height=30;
            var id:int=int(c.templateId);
            editorSmallButton(catalogDetail,"Создать ("+craftCost(c)+")",22,796,246,44,owned<cap&&scraps>=craftCost(c),function():void{send("OnBetaGwentCollectionCraft",[id]);});

        }
        private function drawBetaCatalog():void
        {
            wideArt(content,BetaGwentDeckArt104.BG_BUILDER);
            betaPlaque("КОЛЛЕКЦИЯ");
            paintArt(content,BetaGwentHud104.WOOD_PANEL,405,822,30,135);
            paintArt(content,BetaGwentHud104.WOOD_PANEL,405,822,1477,135);
            betaLabel(content,"Все карты",56,160,354,28,0xEEE7D5,BetaGwentFonts.TITLE,true,"center",2);
            var all:Array=BetaGwentFullCatalog.all(),collected:int=0;
            for each(var c:Object in all)if(int(ownedCopies[c.templateId])>0)collected++;
            text(content,"Коллекция: "+collected+" / "+all.length,56,211,354,22,0xE8D3A6);
            catalogScrapsLabel=text(content,"Осколки: "+scraps,56,253,354,22,0xE8D3A6);
            text(content,"Карты можно получить из бочек или создать за осколки.",56,312,354,21,0xD9D2C3).height=100;
            var input:TextField=editorInput(catalogSearch,474,138,953,46);
            input.addEventListener(Event.CHANGE,function(e:Event):void{catalogSearch=input.text;catalogPage=0;searchDeadline=getTimer()+160;});
            var factions:Array=[0,1,2,8,16,32,4],names:Array=["Все","Нейтральные","Чудовища","Север","Скоя'таэли","Скеллиге","Нильфгаард"];
            for(var i:int=0;i<factions.length;i++)editorBetaButton(content,names[i],474+i*137,202,129,40,true,catalogFilter(1,factions[i]),catalogFaction==factions[i]);
            var tiers:Array=[0,8,4,2,1],tn:Array=["Все","Золото","Серебро","Бронза","Лидеры"];
            for(i=0;i<tiers.length;i++)editorBetaButton(content,tn[i],474+i*115,252,107,40,true,catalogFilter(2,tiers[i]),catalogTier==tiers[i]);
            var types:Array=[0,4,2],typesNames:Array=["Все","Отряды","Особые"];
            for(i=0;i<types.length;i++)editorBetaButton(content,typesNames[i],1065+i*123,252,115,40,true,catalogFilter(3,types[i]),catalogType==types[i]);
            catalogGrid=new Sprite();catalogGrid.x=474;catalogGrid.y=319;content.addChild(catalogGrid);
            catalogDetail=new Sprite();content.addChild(catalogDetail);
            editorBetaButton(content,"Назад к колодам",1515,1002,330,48,true,closeCatalog);
            redrawBetaCatalogGrid();redrawBetaCatalogDetail();
        }
        private function redrawBetaCatalogGrid():void
        {
            if(!catalogGrid)return;while(catalogGrid.numChildren)catalogGrid.removeChildAt(0);
            var list:Array=catalogCards(),pages:int=Math.max(1,Math.ceil(list.length/10));catalogPage=Math.max(0,Math.min(catalogPage,pages-1));
            for(var i:int=catalogPage*10;i<Math.min(list.length,(catalogPage+1)*10);i++){
                var c:Object=list[i],n:int=i-catalogPage*10;var tile:Sprite=new Sprite();tile.x=n%5*192;tile.y=int(n/5)*326;catalogGrid.addChild(tile);
                paintBetaFace(tile,int(c.templateId),173,231,0);
                if(c.typeMask==4||c.leader)betaPowerField(tile,String(c.power),173,231,0xFFFFFF);
                var title:TextField=betaLabel(tile,c.title,0,240,173,18,0xEDE7D8,BetaGwentFonts.TITLE,false,"center");title.height=48;
                if(int(ownedCopies[c.templateId])==0)tile.alpha=.68;
                if(c.acquisitionShort)text(tile,c.acquisitionShort,0,279,173,12,0xCBBE99).height=44;
                attachEditorClick(tile,catalogPick(c));attachInspect(tile,c,{description:c.description},173,231);
                controller.registerControl(tile,c.title,catalogPick(c),c,{description:c.description},"card");
            }
            text(catalogGrid,"Найдено: "+list.length+" · "+(catalogPage+1)+" / "+pages,160,682,630,20,0xD6C6A8);
            editorBetaButton(catalogGrid,"Назад",0,678,140,44,catalogPage>0,function():void{catalogPage--;redrawBetaCatalogGrid();});
            editorBetaButton(catalogGrid,"Вперёд",810,678,140,44,catalogPage+1<pages,function():void{catalogPage++;redrawBetaCatalogGrid();});
        }
        private function redrawBetaCatalogDetail():void
        {
            if(!catalogDetail)return;while(catalogDetail.numChildren)catalogDetail.removeChildAt(0);
            var c:Object=catalogPicked;if(!c)return;
            battlePreview=catalogDetail;drawBetaSidePreview(c,{description:c.description});
            var owned:int=int(ownedCopies[c.templateId]),cap:int=c.tier==2?3:1;
            text(catalogDetail,"В коллекции: "+owned+" / "+cap,56,448,354,23,0xE8D3A6).height=38;
            if(c.acquisitionShort)text(catalogDetail,c.acquisition,56,507,354,21,0xE4DFD0).height=190;
            var rarityNames:Object={1:"Обычная",2:"Редкая",4:"Эпическая",8:"Легендарная"};
            text(catalogDetail,rarityNames[cardRarity(c)]+" · создать "+craftCost(c),56,730,354,22,0xE8D3A6).height=65;
            var id:int=int(c.templateId);
            editorBetaButton(catalogDetail,"Создать ("+craftCost(c)+")",56,823,354,52,owned<cap&&scraps>=craftCost(c),function():void{send("OnBetaGwentCollectionCraft",[id]);});
        }
        private function drawCatalog():void
        {
            if(skin==3){drawBetaCatalog();return;}
            wideArt(content,BetaGwentDeckArt104.BG_SETUP);betaWindow(content,64,24,1792,1032);
            text(content,"BETA GWENT 0.9.24 · ВСЕ КАРТЫ",96,44,1400,32,0xE8D3A6);
            editorSmallButton(content,"Назад к колодам",1520,44,304,42,true,closeCatalog);
            var fullList:Array=BetaGwentFullCatalog.all();var collected:int=0;
            for each(var template:Object in fullList)if(int(ownedCopies[template.templateId])>0)collected++;
            text(content,"Коллекция: "+collected+" / "+fullList.length+" · осталось "+(fullList.length-collected)+" · нужна одна копия каждой карты и лидера",96,99,1150,22);
            catalogScrapsLabel=text(content,"Осколки: "+scraps,1268,99,556,22,0xE8D3A6);
            var input:TextField=editorInput(catalogSearch,96,143,1116,80);
            input.addEventListener(Event.CHANGE,function(e:Event):void{catalogSearch=input.text;catalogPage=0;searchDeadline=getTimer()+160;});
            var factions:Array=[0,1,2,8,16,32,4];var titles:Array=["Все","Нейтральные","Чудовища","Север","Скоя'таэли","Скеллиге","Нильфгаард"];
            for(var f:int=0;f<factions.length;f++)editorSmallButton(content,(catalogFaction==factions[f]?"● ":"")+titles[f],96+f*159,199,149,34,true,catalogFilter(1,factions[f]));
            var tiers:Array=[0,8,4,2,1];var tierNames:Array=["Все","Золото","Серебро","Бронза","Лидеры"];
            for(var t:int=0;t<tiers.length;t++)editorSmallButton(content,(catalogTier==tiers[t]?"● ":"")+tierNames[t],96+t*137,243,127,34,true,catalogFilter(2,tiers[t]));
            var types:Array=[0,4,2];var typeNames:Array=["Все","Отряды","Особые"];
            for(var k:int=0;k<types.length;k++)editorSmallButton(content,(catalogType==types[k]?"● ":"")+typeNames[k],797+k*138,243,128,34,true,catalogFilter(3,types[k]));
            catalogGrid=new Sprite();catalogGrid.x=96;catalogGrid.y=340;content.addChild(catalogGrid);
            catalogDetail=betaWindow(content,1268,143,556,878);
            redrawCatalogGrid();redrawCatalogDetail();
        }
        private function editorSmallButton(parent:Sprite,title:String,x:Number,y:Number,w:Number,h:Number,enabled:Boolean,callback:Function):void
        {editorBetaButton(parent,title,x,y,w,h,enabled,callback);}

        private function attachEditorClick(p:Sprite,callback:Function):void
        {
            controller.registerControl(p,"",callback,null,null,"");
            p.buttonMode=true;
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{uiSound(3);callback();});
        }
        private function editorInput(value:String,x:Number,y:Number,w:Number,maxChars:int):TextField
        {
            betaNine(content,-1410,w,40,x,y);
            var field:TextField=text(content,value,x+12,y+3,w-24,24);
            field.height=40;field.type=TextFieldType.INPUT;field.multiline=false;field.wordWrap=false;
            field.selectable=true;field.mouseEnabled=true;field.maxChars=maxChars;
            field.background=false;field.border=false;
            var purpose:int=y==112?0:browsingCatalog?2:1;
            controller.registerControl(field,purpose==0?"Название колоды":"Поиск карт",function():void{
                if(!ready)return;
                openTextInput(purpose,field.text);
            });
            field.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{openTextInput(purpose,field.text);e.preventDefault();e.stopPropagation();});
            field.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            return field;
        }
        public function setEditorName(value:int,title:String):void
        {
            if(!editingDeck || value!=revision || title.length==0)return;
            editorName=title.substr(0,48);editorState.title=editorName;render();
        }
        private function closeNameInput():void
        {nameOpen=false;nameField=null;nameCounter=null;pendingText="";pendingTextAt=0;if(keyboardStage)keyboardStage.focus=null;while(nameLayer.numChildren)nameLayer.removeChildAt(0);}
        private function openNameInput():void {openTextInput(0,editorName);}
        private function openTextInput(purpose:int,value:String):void
        {
            if(!ready||nameOpen||purpose==0&&!editingDeck)return;
            textPurpose=purpose;textLimit=purpose==0?48:purpose==1?64:80;
            nameOpen=true;nameRevision=revision;
            panel(nameLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.85);
            var box:Sprite=panel(nameLayer,460,220,1000,650,0x10191F,.99);
            text(box,purpose==0?"НАЗВАНИЕ КОЛОДЫ":"ПОИСК КАРТ",30,20,920,30,0xF5D77F);
            nameField=text(box,value,30,82,940,28);nameField.height=48;
            nameField.type=TextFieldType.INPUT;nameField.multiline=false;nameField.wordWrap=false;nameField.selectable=true;nameField.mouseEnabled=true;nameField.maxChars=textLimit;
            nameField.background=true;nameField.backgroundColor=0x233B45;
            nameField.addEventListener(TextEvent.TEXT_INPUT,function(e:TextEvent):void{
                e.preventDefault();e.stopImmediatePropagation();
                pendingText="";pendingTextAt=0;editName(e.text);
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
            if(next.length>textLimit)return;
            nameField.text=next;nameField.setSelection(start+value.length,start+value.length);
            nameCounter.text=next.length+" / "+textLimit+" · Enter — принять · Esc — отменить";
        }
        private function nameLetter(letter:String):Function
        {return function():void{editName(letter);};}
        private function submitNameInput():void
        {
            if(!nameField)return;
            if(pendingTextAt>0){editName(pendingText);pendingText="";pendingTextAt=0;}
            var title:String=nameField.text.replace(/^\s+|\s+$/g,"");
            if(textPurpose==0&&!title.length){nameCounter.text="Введите название колоды.";return;}
            var value:int=nameRevision,purpose:int=textPurpose;closeNameInput();
            if(value!=revision)return;
            if(purpose==0)send("OnBetaGwentDeckNameSubmit",[value,title]);
            else if(purpose==1){editorSearch=title;editorPage=0;render();}
            else {catalogSearch=title;catalogPage=0;render();}
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
            text(box,textPurpose==0?"Клавиатура или кнопки букв · RU / EN переключает язык ввода.\nПосле изменения названия сохраните колоду.":"Клавиатура или кнопки букв · RU / EN переключает язык ввода.\nПустая строка убирает поиск; Enter применяет фильтр.",30,580,940,20,0xB9B4A9).height=58;
            nameCounter.text=nameField.text.length+" / "+textLimit+" · Enter — принять · Esc — отменить";
        }
        private function editorTierColor(tier:int):uint
        { return tier==8?0xDCC078:tier==4?0xC5D4DC:0xAE8061; }
        private function editorOwnedToggle():Function
        { return function():void{editorOwnedOnly=!editorOwnedOnly;editorPage=0;render();}; }
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
        private function editorFactionIndex(faction:int):int
        {return faction==4?1:faction==8?2:faction==16?3:faction==32?4:0;}
        private function editorDeckPane(node:Object):Boolean
        {return node&&node.rect.x<440;}
        private function betaNine(parent:Sprite,id:int,w:Number,h:Number,x:Number=0,y:Number=0):Sprite
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
        private function betaWindow(parent:Sprite,x:Number,y:Number,w:Number,h:Number):Sprite
        {
            var p:Sprite=betaFrame(parent,x,y,w,h,-1414);
            panel(p,12,12,w-24,h-24,0x080A09,.5);return p;
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
            if(label.textWidth>w-24){if(skin==3)BetaGwentFonts.apply(label,BetaGwentFonts.BODY,Math.max(12,Math.floor(18*(w-24)/label.textWidth)),chosen?0xFFE6A0:0xE3D6BE);else label.setTextFormat(new TextFormat("$NormalFont",Math.max(12,Math.floor(18*(w-24)/label.textWidth)),chosen?0xFFE6A0:0xE3D6BE));}
            var buttonFormat:TextFormat=label.defaultTextFormat;buttonFormat.align="center";
            label.defaultTextFormat=buttonFormat;label.setTextFormat(buttonFormat);
            label.y=Math.round((h-label.textHeight)/2)-2;label.height=label.textHeight+4;
            if(enabled){
                controller.registerControl(p,title,callback,null,null,"control",null,new Rectangle(0,0,w,h));
                p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{hover.alpha=1;});
                p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{hover.alpha=0;});
            }return p;
        }

        private function showEditorCard(c:Object):void
        {
            if(!editorPreview||!c)return;
            if(editorPreviewId==c.templateId&&editorPreview.numChildren>0)return;
            // Rebuild only the side preview, never the collection or controller graph.
            editorPreviewId=c.templateId;
            while(editorPreview.numChildren)editorPreview.removeChildAt(0);
            if(skin==3){battlePreview=editorPreview;battlePreviewKey="";var view:Object={templateId:c.templateId,title:c.title,power:c.power,side:1,zone:64,tokens:0,description:c.description,timer:null};drawBetaSidePreview(view,{description:c.description});return;}
            editorPreview.graphics.clear();
            paintArt(editorPreview,-1250-editorFactionIndex(c.faction==1?editorState.faction:c.faction),420,58,0,0);
            text(editorPreview,c.title,16,10,388,24,0xF4E1B1).height=46;
            var editorPortrait:Sprite=new Sprite();editorPortrait.x=82;editorPortrait.y=80;editorPreview.addChild(editorPortrait);
            paintArt(editorPortrait,c.templateId,256,360);
            if(!reducedMotion){
                animations.push({sprite:editorPortrait,fromX:104,fromY:80,toX:82,toY:80,curve:"PREVIEW",duration:BetaGwentBetaMotion.duration("PREVIEW"),appear:true});
                editorPortrait.x=104;editorPortrait.alpha=0;
            }
            betaNine(editorPreview,-1412,260,364,80,78);
            editorPreview.graphics.lineStyle(3,editorTierColor(c.tier));editorPreview.graphics.drawRect(82,80,256,360);
            panel(editorPreview,86,84,52,40,0x090E10,.92);
            text(editorPreview,c.typeMask==4?String(c.power):"★",93,87,44,28,0xFFFFFF).height=40;
            var tier:String=c.tier==1?"Лидер":c.tier==8?"Золотая":c.tier==4?"Серебряная":"Бронзовая";
            text(editorPreview,tier+" · "+(c.typeMask==4?"Отряд":"Особая карта"),16,454,388,20,editorTierColor(c.tier)).height=32;
            text(editorPreview,BetaGwentCardTags.text(c.templateId)||"—",16,490,388,18,0xC9C3A9).height=55;
            paintArt(editorPreview,-1270,388,7,16,548);
            var original:Object=BetaGwentCardText.find(c.templateId);
            var description:String=readableText(original?original.description:c.description);
            if(original&&original.glossary.length)description+="\n\n"+original.glossary;
            if(original&&original.flavor.length)description+="\n\n«"+original.flavor+"»";
            var info:Sprite=new Sprite();editorPreview.addChild(info);
            paintArt(info,-1260-editorFactionIndex(c.faction==1?editorState.faction:c.faction),420,260,0,560);info.alpha=.65;info.mouseEnabled=false;
            inspection=text(editorPreview,description,16,574,388,22,0xE7DFCE);inspection.height=232;
            inspection.mouseEnabled=true;inspection.selectable=true;
            inspection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopImmediatePropagation();inspection.scrollV=Math.max(1,Math.min(inspection.maxScrollV,inspection.scrollV-e.delta*3));});
            var cap:int=entryMode==0?(c.tier==2?3:1):int(ownedCopies[c.templateId]);
            text(editorPreview,c.tier==1?"Лидер колоды":"В колоде: "+c.copies+" · доступно: "+cap,16,820,388,19,0xE8D3A6).height=32;
            text(editorPreview,"Колесо / правый стик — описание\nПКМ / X — полный просмотр",16,844,388,17,0xAEA994).height=42;
        }
        private function redrawEditorCollection():void
        {
            if(!editorCollection)return;
            if(skin==3){while(previewLayer.numChildren)previewLayer.removeChildAt(0);redrawBetaCollection();return;}
            while(editorCollection.numChildren)editorCollection.removeChildAt(0);
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            var filtered:Array=[];var query:String=editorSearch.toLowerCase();
            for each(var c:Object in editorCards){
                if(editorTier!=0&&editorTier!=c.tier)continue;
                if(editorType!=0&&editorType!=c.typeMask)continue;
                if(editorFactionOnly&&c.faction==1)continue;
                if(editorOwnedOnly&&int(ownedCopies[c.templateId])<=0)continue;
                if(query.length>0&&(c.title+" "+c.description+" "+BetaGwentCardTags.text(c.templateId)).toLowerCase().indexOf(query)<0)continue;
                filtered.push(c);
            }
            var pages:int=Math.max(1,Math.ceil(filtered.length/12));editorPage=Math.max(0,Math.min(editorPage,pages-1));
            for(var i:int=editorPage*12;i<Math.min(filtered.length,(editorPage+1)*12);i++){
                c=filtered[i];var n:int=i-editorPage*12;
                var tile:Sprite=betaFrame(editorCollection,(n%6)*154,int(n/6)*300,142,239,-1414);
                paintArt(tile,c.templateId,134,188,4,4);betaNine(tile,-1412,138,192,2,2);
                tile.graphics.lineStyle(2,editorTierColor(c.tier));tile.graphics.drawRect(1,1,140,237);
                tile.alpha=c.canAdd||c.copies>0?1:.68;
                panel(tile,4,4,38,29,0x090E10,.94);
                text(tile,c.typeMask==4?String(c.power):"★",8,4,32,21,0xFFFFFF).height=29;
                paintArt(tile,-1213,46,46,92,4);
                text(tile,"×"+c.copies,103,7,35,18,0xE8D3A6).height=30;
                panel(tile,4,148,134,44,0x080D0E,.9);
                text(tile,c.title,9,150,124,17,0xF0E5CE).height=41;
                var cap:int=entryMode==0?(c.tier==2?3:1):int(ownedCopies[c.templateId]);
                text(tile,c.copies+" / "+cap,7,208,54,17,0xE8D3A6).height=27;
                attachInspect(tile,c,{description:c.description},142,239);
                if(c.canAdd&&ready)attachEditorClick(tile,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
                editorBetaButton(tile,"−",67,204,31,29,ready&&c.copies>0,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorBetaButton(tile,"+",104,204,31,29,ready&&c.canAdd,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
            }
            if(filtered.length==0)text(editorCollection,"Карты по этим условиям не найдены.",16,80,888,26,0xD8D0BB).height=80;
            for(var shelf:int=0;shelf<2;shelf++)for(var beam:int=0;beam<3;beam++)paintArt(editorCollection,-1210,308,48,beam*308,244+shelf*300);
            editorBetaButton(editorCollection,"←",0,584,66,36,ready&&editorPage>0,function():void{editorPage--;redrawEditorCollection();});
            editorBetaButton(editorCollection,"→",78,584,66,36,ready&&editorPage+1<pages,function():void{editorPage++;redrawEditorCollection();});
            text(editorCollection,"Коллекция: "+filtered.length+" карт · страница "+(editorPage+1)+" / "+pages,168,588,748,19,0xE8D3A6).height=32;
        }
        // stage104-deckeditor
        // UIDBPrefab (deck builder) in the original arrangement.
        private function betaStatsWidget(fi:int,golds:int,silvers:int,bronzes:int,total:int,y:Number):void
        {
            paintArt(content,BetaGwentDeckArt104.stats(Math.min(4,fi)),371,108,52,y);
            var counters:Array=[[BetaGwentDeckArt104.DP_STAT_GOLD,golds+"/4",0xF6D36B],[BetaGwentDeckArt104.DP_STAT_SILVER,silvers+"/6",0xE6E6E6],[BetaGwentDeckArt104.DP_STAT_BRONZE,String(bronzes),0xE0B07A]];
            for(var k:int=0;k<3;k++){
                paintArt(content,counters[k][0],46,54,152+k*62,y+8);
                betaSlotLabel(content,counters[k][1],152+k*62,y+8,46,54,18,counters[k][2],BetaGwentFonts.BODY);
            }
            betaLabel(content,"КАРТЫ: "+total,52,y+72,371,18,total>=25?0xF2EEE4:0xF0B060,BetaGwentFonts.BODY,false,"center",1);
        }
        private function drawBetaDeckEditor():void
        {
            wideArt(content,BetaGwentDeckArt104.BG_BUILDER);
            betaPlaque("Редактор колоды");
            var fi:int=editorFactionIndex(editorState.faction);
            // left: DeckPicker / DeckCards
            paintArt(content,BetaGwentHud104.WOOD_PANEL,426,858,21,129);
            var bronzes:int=0;var selectedCards:Array=[];
            for each(var c:Object in editorCards)if(c.copies>0){selectedCards.push(c);if(c.tier==2)bronzes+=c.copies;}
            selectedCards.sort(sortEditorCards);
            betaStatsWidget(fi,editorState.golds,editorState.silvers,bronzes,editorState.total,146);
            var nameRow:Sprite=new Sprite();nameRow.x=46;nameRow.y=262;content.addChild(nameRow);
            paintArt(nameRow,BetaGwentDeckArt104.DP_NEWDECK,372,44,0,0);
            betaLabel(nameRow,String(editorName||"Новая колода").toUpperCase(),16,10,300,17,0xF2EEE4,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(nameRow,"✎",336,8,26,18,0xCFC8BA,BetaGwentFonts.BODY);
            attachEditorClick(nameRow,openNameInput);
            var picked:Object=leaderOption(editorState.leader);var factionLeaders:Array=leadersForFaction(editorState.faction);var leaderIndex:int=0;
            for(var li:int=0;li<factionLeaders.length;li++)if(factionLeaders[li].id==editorState.leader)leaderIndex=li;
            if(picked){
                var leaderCard:Object={templateId:picked.id,title:picked.title,description:picked.description,power:picked.power,tier:1,typeMask:4,faction:editorState.faction,copies:1,tokens:0,timer:-1,side:1};
                var lrow:Sprite=deckSlotRow(content,leaderCard,46,312,372,60,true);
                attachInspect(lrow,leaderCard,{description:picked.description},372,60);
                if(factionLeaders.length>1){
                    var previous:Object=factionLeaders[(leaderIndex+factionLeaders.length-1)%factionLeaders.length];
                    var next:Object=factionLeaders[(leaderIndex+1)%factionLeaders.length];
                    betaWideButton("‹",46,374,60,ready,editorAction("OnBetaGwentDeckEditorLeader",previous.id));
                    betaWideButton("›",358,374,60,ready,editorAction("OnBetaGwentDeckEditorLeader",next.id));
                    betaLabel(content,"Сменить лидера",110,384,244,15,0xCFC8BA,BetaGwentFonts.BODY,false,"center");
                }
            }
            var perPage:int=12;var pages:int=Math.max(1,Math.ceil(selectedCards.length/perPage));editorListPage=Math.max(0,Math.min(editorListPage,pages-1));
            var list:Sprite=new Sprite();content.addChild(list);
            list.graphics.beginFill(0,0);list.graphics.drawRect(46,428,372,perPage*40);list.graphics.endFill();
            for(var i:int=editorListPage*perPage;i<Math.min(selectedCards.length,(editorListPage+1)*perPage);i++){
                c=selectedCards[i];c.side=1;
                var row:Sprite=deckSlotRow(list,c,46,428+(i-editorListPage*perPage)*40,372,38);
                attachInspect(row,c,{description:c.description},372,38);
                if(ready)attachEditorClick(row,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
            }
            if(!selectedCards.length)betaLabel(content,"Нажмите на карту в коллекции,\nчтобы добавить её в колоду.",52,470,360,18,0xCFC8BA,BetaGwentFonts.BODY,false,"center").height=60;
            list.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();editorListPage=Math.max(0,editorListPage+(e.delta<0?1:-1));render();});
            if(pages>1){
                betaWideButton("‹",46,918,60,ready&&editorListPage>0,function():void{editorListPage--;render();});
                betaSlotLabel(content,(editorListPage+1)+" / "+pages,110,918,244,48,16,0xCFC8BA,BetaGwentFonts.BODY);
                betaWideButton("›",358,918,60,ready&&editorListPage+1<pages,function():void{editorListPage++;render();});
            }
            // centre: Collection with the filter bar
            paintArt(content,BetaGwentDeckArt104.WOOD_LARGE,1026,858,447,129);
            var tiers:Array=[0,2,4,8];var tierIcons:Array=[BetaGwentDeckArt104.TIER_ALL,BetaGwentDeckArt104.TIER_BRONZE,BetaGwentDeckArt104.TIER_SILVER,BetaGwentDeckArt104.TIER_GOLD];
            for(var ti:int=0;ti<4;ti++)betaFilterButton(tierIcons[ti],482+ti*72,156,editorTier==tiers[ti],editorFilterAction(tiers[ti],editorType,editorFactionOnly));
            var factions:Array=[2,8,4,16,32];
            for(var f:int=0;f<factions.length;f++){
                var fIndex:int=editorFactionIndex(factions[f]);
                betaFilterButton(BetaGwentDeckArt104.factionFilter(fIndex),1040+f*72,156,editorState.faction==factions[f],
                    editorFactionAvailable(factions[f])?editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(factions[f])):null);
            }
            betaWideButton("Все",482,226,96,ready,editorFilterAction(editorTier,0,editorFactionOnly));
            betaWideButton("Отряды",584,226,124,ready,editorFilterAction(editorTier,4,editorFactionOnly));
            betaWideButton("Особые",714,226,124,ready,editorFilterAction(editorTier,2,editorFactionOnly));
            betaWideButton(editorFactionOnly?"Без нейтральных":"С нейтральными",844,226,204,ready,editorFilterAction(editorTier,editorType,!editorFactionOnly));
            betaWideButton(editorOwnedOnly?"В наличии":"Все карты",1054,226,150,ready,editorOwnedToggle());
            var searchInput:TextField=editorInput(editorSearch,1212,224,234,64);
            searchInput.addEventListener(Event.CHANGE,function(e:Event):void{editorSearch=searchInput.text;editorPage=0;searchDeadline=getTimer()+160;});
            content.graphics.lineStyle(2,0x6A5A44,.8);content.graphics.moveTo(474,286);content.graphics.lineTo(1446,286);content.graphics.lineStyle();
            editorCollection=new Sprite();editorCollection.x=0;editorCollection.y=0;content.addChild(editorCollection);
            editorCollection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();if(!ready)return;editorPage=Math.max(0,editorPage+(e.delta<0?1:-1));redrawEditorCollection();});
            redrawEditorCollection();
            // right: SidePreview
            paintArt(content,BetaGwentHud104.WOOD_PANEL,426,858,1473,129);
            paintArt(content,BetaGwentHud104.PREVIEW_SLOT,285,398,1545,177);
            editorPreview=new Sprite();editorPreview.mouseEnabled=false;editorPreview.mouseChildren=false;content.addChild(editorPreview);
            var preview:Object=editorById[editorPreviewId];if(!preview&&picked)preview={templateId:picked.id,title:picked.title,description:picked.description,power:picked.power,tier:1,typeMask:4,faction:editorState.faction,copies:1};
            if(!preview&&editorCards.length)preview=editorCards[0];
            editorPreviewId=0;showEditorCard(preview);
            // bottom
            if(editorState.status)betaLabel(content,editorState.status,474,948,972,16,editorState.valid?0xA6D6AF:0xF0C080,BetaGwentFonts.BODY,false,"center");
            betaWideButton("Сохранить",560,1002,260,ready,editorAction("OnBetaGwentDeckEditorSave"));
            betaWideButton("Очистить",840,1002,240,ready&&editorState.total>0,editorAction("OnBetaGwentDeckEditorClear"));
            betaWideButton("Отмена",1100,1002,240,ready,editorAction("OnBetaGwentDeckEditorCancel"));
        }
        private function betaFilterButton(icon:int,x:Number,y:Number,on:Boolean,callback:Function):void
        {
            var b:Sprite=new Sprite();b.x=x;b.y=y;content.addChild(b);
            paintArt(b,BetaGwentDeckArt104.FILTER_BTN,66,56,0,0);paintArt(b,icon,40,40,13,8);
            if(on)paintArt(b,BetaGwentDeckArt104.FILTER_ON,66,56,0,0);
            b.alpha=callback!=null?1:.4;
            if(callback!=null&&ready){
                b.buttonMode=true;b.mouseChildren=false;
                b.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                controller.registerControl(b,"",callback,null,null,"control",null,new Rectangle(0,0,66,56));
            }
        }
        private function redrawBetaCollection():void
        {
            while(editorCollection.numChildren)editorCollection.removeChildAt(0);
            var filtered:Array=[];var query:String=editorSearch.toLowerCase();
            for each(var c:Object in editorCards){
                if(editorTier!=0&&editorTier!=c.tier)continue;
                if(editorType!=0&&editorType!=c.typeMask)continue;
                if(editorFactionOnly&&c.faction==1)continue;
                if(editorOwnedOnly&&int(ownedCopies[c.templateId])<=0)continue;
                if(query.length>0&&(c.title+" "+c.description+" "+BetaGwentCardTags.text(c.templateId)).toLowerCase().indexOf(query)<0)continue;
                filtered.push(c);
            }
            var perPage:int=10;var pages:int=Math.max(1,Math.ceil(filtered.length/perPage));editorPage=Math.max(0,Math.min(editorPage,pages-1));
            var cw:Number=164,ch:Number=Math.round(164/BETA_CARD_ASPECT);
            for(var i:int=editorPage*perPage;i<Math.min(filtered.length,(editorPage+1)*perPage);i++){
                c=filtered[i];var n:int=i-editorPage*perPage;c.side=1;
                var tile:Sprite=new Sprite();tile.x=500+(n%5)*186;tile.y=306+int(n/5)*318;editorCollection.addChild(tile);
                tile.graphics.beginFill(0,.45);tile.graphics.drawRect(4,6,cw,ch);tile.graphics.endFill();
                paintBetaFace(tile,c.templateId,cw,ch,1);
                if(c.typeMask==4)betaPowerField(tile,String(c.power),cw,ch,0xFFFFFF);
                var cap:int=entryMode==0?(c.tier==2?3:1):int(ownedCopies[c.templateId]);
                if(c.copies>0){
                    paintArt(tile,BetaGwentDeckArt104.DB_COPIES,44,44,cw-48,4);
                    betaSlotLabel(tile,"x"+c.copies,cw-48,4,44,44,17,0xF2EEE4,BetaGwentFonts.BODY);
                }
                tile.alpha=c.canAdd||c.copies>0?1:.5;
                var craftable:Boolean=!c.canAdd&&entryMode!=0&&int(ownedCopies[c.templateId])<(c.tier==2?3:1);
                var shelf:TextField=betaLabel(tile,craftable?"Создать: "+craftCost(c):c.copies+" / "+cap,0,ch+6,cw,16,craftable?(scraps>=craftCost(c)?0xF0D27A:0xB08A60):c.canAdd?0xF2EEE4:0xA49A88,BetaGwentFonts.BODY,false,"center");
                if(craftable)tile.alpha=.75;
                attachInspect(tile,c,{description:c.description},cw,ch);
                if(c.canAdd&&ready)attachEditorClick(tile,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
                // A card that is missing (or short of copies) offers crafting from scraps.
                else if(craftable&&ready)attachEditorClick(tile,editorCraftPrompt(c));
            }
            if(filtered.length==0)betaLabel(editorCollection,"Нет карт, подходящих под фильтры.",474,560,972,22,0xF2EEE4,BetaGwentFonts.BODY,false,"center");
            var prev:Function=function():void{editorPage--;redrawEditorCollection();};
            var next:Function=function():void{editorPage++;redrawEditorCollection();};
            var start:int=content.numChildren;
            betaWideButton("‹",474,896,70,ready&&editorPage>0,prev);
            betaWideButton("›",1376,896,70,ready&&editorPage+1<pages,next);
            while(content.numChildren>start)editorCollection.addChild(content.getChildAt(start));
            betaSlotLabel(editorCollection,"Коллекция: "+filtered.length+" · "+(editorPage+1)+" / "+pages+(entryMode!=0?" · Осколки: "+scraps:""),560,896,800,48,17,0xE8DCC4,BetaGwentFonts.BODY);
            if(editorCraft)drawEditorCraft();
        }
        private var editorCraft:Object=null;
        private function editorCraftPrompt(c:Object):Function
        { return function():void{editorCraft=c;redrawEditorCollection();}; }
        // Craft dialog over the deck editor collection (Beta popup frame).
        private function drawEditorCraft():void
        {
            var c:Object=editorCraft;var cost:int=craftCost(c);var id:int=int(c.templateId);
            var layer:Sprite=new Sprite();editorCollection.addChild(layer);
            layer.graphics.beginFill(0,.6);layer.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);layer.graphics.endFill();
            layer.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            paintArt(layer,BetaGwentHud104.POPUP,700,330,610,370);
            var bar:Sprite=new Sprite();layer.addChild(bar);paintArt(bar,BetaGwentHud104.POPUP_TITLE,660,52,630,388);
            betaLabel(layer,"СОЗДАТЬ КАРТУ",610,396,700,26,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",6);
            var rarityNames:Object={1:"обычная",2:"редкая",4:"эпическая",8:"легендарная"};
            var body:TextField=text(layer,c.title+" ("+rarityNames[cardRarity(c)]+")\nЦена: "+cost+" осколков · у вас "+scraps+
                "\nВ коллекции: "+int(ownedCopies[id])+" / "+(c.tier==2?3:1),650,462,620,20,0xE8E4DA);
            body.height=110;betaFace(BetaGwentFonts.BODY,body,20,0xE8E4DA,false,"center");
            var start:int=content.numChildren;
            betaWideButton("Создать",700,600,240,ready&&scraps>=cost,function():void{editorCraft=null;send("OnBetaGwentCollectionCraft",[id]);});
            betaWideButton("Отмена",980,600,240,true,function():void{editorCraft=null;redrawEditorCollection();});
            while(content.numChildren>start)layer.addChild(content.getChildAt(start));
        }
        private function drawDeckEditor():void
        {
            if(skin==3){drawBetaDeckEditor();return;}
            // Original Beta RectTransforms: DeckPicker on the left, Collection
            // in the centre, SidePreview on the right. Native safe-area adaptation.
            wideArt(content,BetaGwentDeckArt104.BG_SETUP);
            panel(content,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x050909,.15);
            betaFrame(content,44,88,388,884);
            panel(content,52,96,372,868,0x090A0A,.45);
            betaFrame(content,1440,88,436,930);
            panel(content,1448,96,420,914,0x090A0A,.5);
            for(var post:int=0;post<3;post++){paintArt(content,-1211,38,294,426,88+post*294);paintArt(content,-1211,38,294,1398,88+post*294);}
            paintArt(content,-1420-editorFactionIndex(editorState.faction),388,122,44,210);
            text(content,"РЕДАКТОР КОЛОДЫ",52,26,1200,30,0xE8D3A6).height=45;
            text(content,editorState.slot>8?"Стартовая колода":"Слот "+editorState.slot+" / 8",52,83,348,18,0xE8D3A6).height=30;
            var nameInput:TextField=editorInput(editorName,56,112,364,48);
            nameInput.addEventListener(Event.CHANGE,function(e:Event):void{editorName=nameInput.text;});
            editorBetaButton(content,"Изменить имя",56,166,174,36,ready,openNameInput);
            editorBetaButton(content,"Очистить",242,166,178,36,ready&&editorState.total>0,editorAction("OnBetaGwentDeckEditorClear"));
            var factions:Array=[2,8,4,16,32];var names:Array=["Чудовища","Север","Нильфгаард","Скоя’таэли","Скеллиге"];
            for(var f:int=0;f<factions.length;f++){
                var factionButton:Sprite=editorBetaButton(content,"       "+names[f],464+f*186,88,178,54,editorFactionAvailable(factions[f]),editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(factions[f])),editorState.faction==factions[f]);
                paintArt(factionButton,-1240-editorFactionIndex(factions[f]),36,42,7,5);
            }
            var picked:Object=leaderOption(editorState.leader);var factionLeaders:Array=leadersForFaction(editorState.faction);var leaderIndex:int=0;
            for(var li:int=0;li<factionLeaders.length;li++)if(factionLeaders[li].id==editorState.leader)leaderIndex=li;
            if(picked){
                var leaderTile:Sprite=panel(content,56,218,100,141,0x11191B,.5);
                paintArt(leaderTile,picked.id,100,141,0,0);
                var leaderCard:Object={templateId:picked.id,title:picked.title,description:picked.description,power:picked.power,tier:1,typeMask:4,faction:editorState.faction,copies:1,tokens:0,timer:-1};
                attachInspect(leaderTile,leaderCard,{description:picked.description},100,141);
                text(content,picked.title,172,220,248,24,0xE8D3A6).height=67;
                text(content,"Лидер · сила "+picked.power,172,299,248,19,0xCBC7BA).height=38;
            }
            var previous:Object=factionLeaders.length?factionLeaders[(leaderIndex+factionLeaders.length-1)%factionLeaders.length]:null;
            var next:Object=factionLeaders.length?factionLeaders[(leaderIndex+1)%factionLeaders.length]:null;
            editorBetaButton(content,"← Лидер",56,372,174,36,ready&&factionLeaders.length>1,editorAction("OnBetaGwentDeckEditorLeader",previous?previous.id:0));
            editorBetaButton(content,"Лидер →",242,372,178,36,ready&&factionLeaders.length>1,editorAction("OnBetaGwentDeckEditorLeader",next?next.id:0));
            text(content,editorState.total+" / 25–40 карт",56,424,364,27,editorState.valid?0xA6D6AF:0xE8D3A6).height=43;
            var units:int=0;var specials:int=0;var selectedCards:Array=[];
            for each(var c:Object in editorCards)if(c.copies>0){selectedCards.push(c);if(c.typeMask==4)units+=c.copies;else specials+=c.copies;}
            selectedCards.sort(sortEditorCards);
            text(content,"Золото "+editorState.golds+" / 4 · серебро "+editorState.silvers+" / 6\n"+units+" отрядов · "+specials+" особых",56,469,364,18,0xD8D0BB).height=51;
            var pages:int=Math.max(1,Math.ceil(selectedCards.length/12));editorListPage=Math.max(0,Math.min(editorListPage,pages-1));
            for(var i:int=editorListPage*12;i<Math.min(selectedCards.length,(editorListPage+1)*12);i++){
                c=selectedCards[i];var row:Sprite=panel(content,56,530+(i-editorListPage*12)*34,364,32,0x11191B,.95);
                var strip:Sprite=new Sprite();strip.mouseEnabled=false;strip.mouseChildren=false;strip.scrollRect=new Rectangle(0,0,356,30);row.addChild(strip);
                paintArt(strip,c.templateId,356,501,4,-110);panel(strip,0,0,364,32,0x05090B,.65);
                paintArt(row,c.tier==8?-1222:c.tier==4?-1221:-1220,364,32,0,0);
                text(row,"×"+c.copies+"  "+c.title,8,4,260,17,editorTierColor(c.tier)).height=27;
                attachInspect(row,c,{description:c.description},364,32);
                if(ready)attachEditorClick(row,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorBetaButton(row,"−",284,2,32,28,ready,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
                editorBetaButton(row,"+",324,2,32,28,ready&&c.canAdd,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
            }
            if(!selectedCards.length)text(content,"Добавляйте карты из коллекции кнопкой +.\nБронза: до3 копий, серебро и золото: по1.",56,545,364,22,0xB9B4A9).height=180;
            editorBetaButton(content,"←",56,942,62,30,ready&&editorListPage>0,function():void{editorListPage--;render();});
            editorBetaButton(content,"→",126,942,62,30,ready&&editorListPage+1<pages,function():void{editorListPage++;render();});
            text(content,"Состав: "+(editorListPage+1)+" / "+pages,204,944,218,18,0xB9B4A9).height=30;
            var tiers:Array=[0,2,4,8];var tierTitles:Array=["Все","Бронза","Серебро","Золото"];
            for(var ti:int=0;ti<tiers.length;ti++){
                var tierButton:Sprite=editorBetaButton(content,"      "+tierTitles[ti],464+ti*139,158,130,42,ready,editorFilterAction(tiers[ti],editorType,editorFactionOnly),editorTier==tiers[ti]);
                paintArt(tierButton,ti==0?-1214:-1230-(ti-1),ti==0?28:13,32,8,5);
            }
            editorBetaButton(content,"Все",1030,158,104,42,ready,editorFilterAction(editorTier,0,editorFactionOnly),editorType==0);
            editorBetaButton(content,"Отряды",1144,158,116,42,ready,editorFilterAction(editorTier,4,editorFactionOnly),editorType==4);
            editorBetaButton(content,"Особые",1270,158,118,42,ready,editorFilterAction(editorTier,2,editorFactionOnly),editorType==2);
            var searchInput:TextField=editorInput(editorSearch,464,218,528,64);
            editorBetaButton(content,editorOwnedOnly?"В наличии":"Все карты",1002,218,152,40,ready,editorOwnedToggle(),editorOwnedOnly);
            searchInput.addEventListener(Event.CHANGE,function(e:Event):void{editorSearch=searchInput.text;editorPage=0;searchDeadline=getTimer()+160;});
            editorBetaButton(content,editorFactionOnly?"Фракция":"Фракция + нейтральные",1164,218,224,40,ready,editorFilterAction(editorTier,editorType,!editorFactionOnly),editorFactionOnly);
            text(content,"Поиск по названию, способности и тегам",464,268,924,17,0xC5C0AC).height=26;
            editorCollection=new Sprite();editorCollection.x=464;editorCollection.y=310;content.addChild(editorCollection);
            editorCollection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();if(!ready)return;editorPage=Math.max(0,editorPage+(e.delta<0?1:-1));redrawEditorCollection();});
            redrawEditorCollection();
            editorPreview=new Sprite();editorPreview.x=1448;editorPreview.y=96;content.addChild(editorPreview);
            var preview:Object=editorById[editorPreviewId];if(!preview&&editorCards.length)preview=editorCards[0];showEditorCard(preview);
            text(content,editorState.status,464,947,924,19,editorState.valid?0xA6D6AF:0xE8D3A6).height=48;
            editorBetaButton(content,"Сохранить колоду",56,990,364,42,ready,editorAction("OnBetaGwentDeckEditorSave"),true);
            editorBetaButton(content,"Отменить",1448,990,420,42,ready,editorAction("OnBetaGwentDeckEditorCancel"));
            text(content,"Коллекция: добавить · состав: убрать · ПКМ / X: просмотр\nLT / RT: − / + · View: панели · LB / RB: страницы · Start: сохранить",464,990,924,17,0xD1CCBA).height=44;
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
        public function pushTemplateRules(id:int,kind:int,side:int,types:int,tiers:int,ignore:int,maximum:int,rowMask:int,geometry:String="0,0,0,0"):void
        { var shape:Array=geometry.split(",");templateRules[id]={kind:kind,side:side,types:types,tiers:tiers,ignore:ignore,maximum:maximum,rowMask:rowMask,scope:int(shape[0]),radius:int(shape[1]),traits:int(shape[2]),excludedTraits:int(shape[3])}; }
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
        // Card whose ability opened the current request (nested plays included), for the aiming arrow.
        public function setRequestSource(rev:int,id:int,templateId:int=0):void
        { if(!incoming||rev!=incoming.revision)return; incoming.requestSource=id;incoming.requestSourceTemplate=templateId; }
        public function pushRequestCard(id:int,title:String,templateId:int,factionId:int,revealed:Boolean,isSelected:Boolean):void
        {
            if(incoming&&incoming.requestId>0)incoming.requestCards.push({id:id,title:title,templateId:templateId,
                factionId:factionId,revealed:revealed,selected:isSelected,timer:-1});
        }
        public function setVisualCue(rev:int,kind:int,source:int,target:int,side:int,row:int,templateId:int,duration:int,title:String):void
        {
            if(!incoming||rev!=incoming.revision)return;
            // kind + 256 * targets: one original Beta attack may hit many cards at once.
            var attackCount:int=Math.max(1,kind>>8);kind=kind&255;
            incoming.cue={kind:kind,source:source,target:target,side:side,row:row,
                templateId:templateId,duration:duration,title:title,attackCount:attackCount};
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
            for each(var frame:Object in replayFrames)total+=Math.max(0,reducedMotion?320:frame.cue.duration);
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
            previousCrowns=crowns.concat();previousScores=scores.concat();previousEnemyHand=enemyHand;
            revision=frame.revision;round=frame.round;current=frame.current;scores=frame.scores;
            crowns=frame.crowns;flags=frame.flags;message=frame.message;cards=frame.cards;
            cardDetails=frame.cardDetails;playRules=frame.playRules;weatherRows=frame.weatherRows;selected=0;keyboardFocusId=0;focusedRow=0;
            enemyHand=frame.enemyHand;leaderOne=frame.leaderOne;leaderTwo=frame.leaderTwo;
            graves=frame.graves;deckCounts=frame.deckCounts;leaderTitle=frame.leaderTitle;
            leaderIds=frame.leaderIds;leaderNames=frame.leaderNames;placementCard=frame.placementCard;
            rowMode=frame.rowMode;rowRequest=(rowMode>0&&rowMode<5)||(rowMode>=8&&rowMode<=10);leaderRow=rowMode==2;templateChoice=rowMode==5||rowMode==7||rowMode==13;graveyardChoice=rowMode==6;handPowerChoice=rowMode==11;pileChoice=rowMode==12||rowMode==14;
            requestId=frame.requestId;requestPlayer=frame.requestPlayer;requestKind=frame.requestKind;requestSourceId=int(frame.requestSource);
            requestSourceTemplate=int(frame.requestSourceTemplate);
            requestMin=frame.requestMin;requestMax=frame.requestMax;requestCount=frame.requestCount;
            requestFinish=frame.requestFinish;requestMessage=frame.requestMessage;requestCards=frame.requestCards;
            activeCue=frame.cue;playing=replayFrames.length>0;ready=true;
            if(skin==3&&introStart==0&&current==1&&previousTurn!=1&&requestKind!=1&&(flags>>4)==0&&activeCue.kind!=6)turnBannerAt=getTimer();
            previousTurn=current;
            maybeStartIntro();
            if(activeCue.kind==6)lastRoundResult={round:round,scores:scores.concat(),crowns:crowns.concat(),flags:flags,title:activeCue.title};
            if(activeCue.kind==7||activeCue.kind==17)lastRoundResult=null;
            if(activeCue.kind>0&&activeCue.title){
                if(actionHistory.length==0||actionHistory[0]!=activeCue.title)actionHistory.unshift(activeCue.title);
                if(actionHistory.length>6)actionHistory.pop();
            }
            // Readability floors may exceed the8s target on unusually long chains.
            var minimum:Number=reducedMotion?320:cueMinimumDuration(activeCue.kind);
            frameDuration=playing?Math.max(reducedMotion?320:Math.max(220,minimum/animationTempo),(reducedMotion?320:frame.cue.duration)*visualTimeScale):360;
            frameDeadline=playing?getTimer()+frameDuration:0;
            // A drawing error must never stall the replay: report it and keep the duel going.
            try{render();}catch(renderError:Error){reportUIError("render r"+revision,renderError);}
            reportArtwork();
            audioCueAt=0;
            if(!skipAudio&&activeCue.kind>0){audioCueRevision=revision;audioCueAt=getTimer()+cueImpactDelay();}
            if(!playing){
                send("OnBetaGwentVisualDone",[serverRevision]);
                autoRoundAt=canNextRound()?getTimer()+1400:0;autoRoundRevision=revision;
            }else autoRoundAt=0;
        }
        private var uiErrorCount:int=0;
        private function reportUIError(where:String,error:Error):void
        {
            if(uiErrorCount++>20)return;
            var detail:String=where+": "+(error?error.toString():"?");
            try{if(error&&error.getStackTrace()!=null)detail+=" | "+error.getStackTrace().split("\n").slice(0,4).join(" / ");}catch(ignored:Error){}
            send("OnBetaGwentUIError",[detail]);
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
            if(connected&&betaAudioInstalled&&now>=audioTickAt){audioTickAt=now+250;send("OnBetaGwentAudioTick",[now]);}
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
        public function setAudioStatus(installed:Boolean,available:Boolean,tempo:int=0,reduced:Boolean=false):void
        { betaAudioInstalled=installed;betaAudioAvailable=available;if(tempo==10||tempo==15||tempo==20){animationTempo=tempo/10;reducedMotion=reduced;} }
        private function toggleSound():void
        { soundEnabled=!soundEnabled;send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);if(controllerMenuOpen){closeControllerMenu();render();openControllerMenu();}else render(); }
        private function toggleVoice():void
        { voiceEnabled=!voiceEnabled;send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled]);if(controllerMenuOpen){closeControllerMenu();render();openControllerMenu();}else render(); }

        private function cycleTempo():void
        {
            var old:Number=animationTempo;animationTempo=old==1?1.5:old==1.5?2:1;
            if(playing){
                var now:int=getTimer();frameDeadline=now+Math.max(0,frameDeadline-now)*old/animationTempo;
                frameDuration*=old/animationTempo;visualTimeScale*=old/animationTempo;
                if(audioCueAt>0)audioCueAt=now+Math.max(0,audioCueAt-now)*old/animationTempo;
            }
            if(tempoLabel)tempoLabel.text="Темп: "+animationTempo+"×";
            send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled,int(animationTempo*10),reducedMotion]);
        }
        private function toggleMotion():void
        {
            reducedMotion=!reducedMotion;
            if(motionLabel)motionLabel.text=reducedMotion?"Эффекты: кратко":"Эффекты: полно";
            send("OnBetaGwentAudioSettings",[soundEnabled,voiceEnabled,int(animationTempo*10),reducedMotion]);
            if(reducedMotion&&playing)frameDeadline=Math.min(frameDeadline,getTimer()+320);
        }
        private function changeSkin(value:int):void
        {
            skin=value;
            while(background.numChildren)background.removeChildAt(0);
            if(skin==3){wideArt(background,-1311,2160,-120);return;}
            // Stage 104 GUI budget: the DIY board bitmaps are no longer shipped.
            background.graphics.clear();background.graphics.beginFill(0x1A1712);background.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);background.graphics.endFill();
        }

        private function text(parent:Sprite,value:String,x:Number,y:Number,w:Number,size:int=22,color:uint=0xF1E8D3):TextField
        {
            var field:TextField=new TextField();
            field.defaultTextFormat=new TextFormat("$NormalFont",size,color);
            field.text=readableText(value); field.x=x; field.y=y; field.width=w; field.height=80;
            field.multiline=true; field.wordWrap=true; field.selectable=false; field.mouseEnabled=false;
            if(skin==3)BetaGwentFonts.apply(field,BetaGwentFonts.BODY,size,color);
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
            var p:Sprite=editorBetaButton(parent||content,title,x,y,w,48,enabled,callback);
            return p.getChildAt(p.numChildren-1) as TextField;
        }

        private function rowGeometry(side:int,zone:int):Object
        {
            var ordinal:int=side==1?(zone==1?0:zone==2?1:2):(zone==4?0:zone==2?1:2);
            if(skin==3){var row:Array=BetaGwentBoardLayout.rows[side+":"+zone];return {x:row[0],y:row[1],w:row[2],h:row[3]};}
            var top:Number=skin==1?(side==1?557:262):(side==1?552:224);
            var spacing:Number=skin==1?93:103;
            return {x:skin==1?565:548,y:top+ordinal*spacing,w:skin==1?793:846,h:skin==1?82:92};
        }
        private function rowLayout(side:int,zone:int,extra:int=0):Object
        {
            var g:Object=rowGeometry(side,zone);var count:int=extra;
            for each(var unit:Object in cards)if(unit.side==side&&unit.zone==zone)count++;
            var step:Number=Math.min((g.h-8)*(skin==3?BETA_CARD_ASPECT:256/360)+8,(g.w-24)/Math.max(1,count));
            return {x:g.x+(g.w-Math.max(1,count)*step+8)/2,step:step,w:step-8};
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
            placementMotions=[];
        }
        private function insertionTarget(side:int,zone:int):Object
        {
            var g:Object=rowGeometry(side,zone);var units:Array=[];
            for each(var c:Object in cards)if(c.side==side&&c.zone==zone)units.push(c);
            units.sortOn("index",Array.NUMERIC);var layout:Object=rowLayout(side,zone);var pending:Object=rowLayout(side,zone,1);
            for each(c in units)if(mouseX<layout.x+c.index*layout.step+layout.w/2)return {anchor:c.id,index:c.index,target:0,side:side,zone:zone,x:pending.x+c.index*pending.step,y:g.y,w:pending.w,h:g.h};
            return {anchor:0,index:units.length,target:0,side:side,zone:zone,x:pending.x+units.length*pending.step,y:g.y,w:pending.w,h:g.h};
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
            var layout:Object=rowLayout(target.side,target.zone,1);var step:Number=layout.step;var width:Number=layout.w;
            placementPreview=target;placementGhost=new Sprite();dragLayer.addChild(placementGhost);
            placementGhostAt=getTimer();
            placementGhost.mouseEnabled=false;placementGhost.mouseChildren=false;
            for each(unit in units){
                if(cardSprites[unit.id])cardSprites[unit.id].alpha=0;
                var u:Sprite=panel(placementGhost,layout.x+(unit.index>=index?unit.index+1:unit.index)*step,g.y+4,width,g.h-8,0x15343E,.95);
                if((int(unit.tokens)&8)!=0)paintCardBack(u,width,g.h-8,unit.side);else paintArt(u,unit.templateId,width-6,g.h-14);
                text(u,(int(unit.tokens)&8)!=0?"?":String(unit.power),5,1,width-8,21,powerColor(unit));
                var oldPose:Object=displayedCards[unit.id];
                if(oldPose)placementMotions.push({sprite:u,fromX:oldPose.x,toX:u.x,fromY:u.y,toY:u.y});
            }
            var x:Number=layout.x+index*step;
            var ghost:Sprite=panel(placementGhost,x,g.y+4,width,g.h-8,0x214C59,.95);
            paintArt(ghost,c.templateId,width-6,g.h-14);ghost.alpha=.52;
            placementMotions.push({sprite:ghost,fromX:x,toX:x,fromY:g.y-10,toY:g.y+4,ghost:true});
            paintBetaCorners(ghost,width,g.h-8,0xD9FFF5);
            placementGhost.graphics.lineStyle(3,0xD9FFF5,1);placementGhost.graphics.drawRect(x,g.y+4,width,g.h-8);
            placementGhost.graphics.moveTo(x+width/2,g.y-3);placementGhost.graphics.lineTo(x+width/2,g.y-15);
            var rowName:String=target.zone==1?"Ближний ряд":target.zone==2?"Дальний ряд":"Осадный ряд";
            var label:Sprite=panel(placementGhost,1536,842,332,58,0x10191F,.98);
            text(label,rowName+" · позиция "+(index+1)+" / "+(units.length+1)+" · "+c.title+" · нажмите, чтобы разместить",10,3,312,17,0xD9FFF5).height=54;
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
        // Ultrawide support: the movie is 1920x1080 (showAll); side bars outside the stage
        // are filled with mirrored copies of full-screen art instead of black.
        private static const WIDE_PAD:Number=960;
        private function wideArt(parent:Sprite,id:int,w:Number=1920,x:Number=0):void
        {
            paintArt(parent,id,w,1080,x,0);
            for(var side:int=-1;side<=1;side+=2){
                var wing:Sprite=BetaGwentCardArt.view(id,w,1080);if(!wing)continue;
                wing.scaleX=-wing.scaleX;wing.x=side<0?x:x+2*w;wing.y=0;parent.addChild(wing);
            }
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
            battlePreview=null;battlePreviewKey="";tempoLabel=null;motionLabel=null;
            animations=[];pendingImpacts=[];targetPulses=[];cardSprites={}; animationFrame=0;animationStarted=getTimer();
            aimLayer.graphics.clear();aimKey="";
            // Retain only weather removed by this snapshot; normal redraws do
            // not restart its birth clock or re-introduce the same effect.
            var activeWeather:Object={};
            for each(var rowWeather:Object in weatherRows)if(rowWeather.token!=0)activeWeather[rowWeather.side+":"+rowWeather.zone]=rowWeather.token;
            for each(var oldWeather:Object in weatherEffects)if(activeWeather[oldWeather.key]!=oldWeather.token&&!reducedMotion)
                weatherFades.push({sprite:oldWeather.sprite,effect:oldWeather,start:getTimer(),alpha:oldWeather.sprite.alpha});
            for(var weatherKey:String in weatherBirths)if(activeWeather[weatherKey]!=weatherBirths[weatherKey].token)delete weatherBirths[weatherKey];
            weatherEffects=[];
            if(kegOpen||browsingCatalog||editingDeck||selectingDecks||entryMode==1)weatherFades=[];
            hoverCardId=0;hoveredCard=null;hoveredDetail=null;hoverPreviewAt=0;
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(choiceLayer.numChildren)choiceLayer.removeChildAt(0);
            while(content.numChildren) content.removeChildAt(0);
            if(kegOpen){drawKeg();return;}
            if(browsingCatalog){drawCatalog();return;}
            if(editingDeck){drawDeckEditor();if(pendingKeg||entryMode==1&&unopenedKegs>0)editorSmallButton(content,pendingKeg?"Продолжить выбор":"Бочки · "+unopenedKegs,1588,28,276,42,ready,function():void{send("OnBetaGwentKegOpen",[revision]);});return;}
            if(selectingDecks){drawDeckSelection();return;}
            if(entryMode==1){text(content,"Открытие редактора колод…",96,88,1720,30,0xE8D3A6);return;}
            if(skin==3)drawFactionBoards();
            if(skin!=3)text(content,"Раунд "+round+"  ·  "+(templateChoice?(rowMode==13?"Выбор режима":rowMode==7?"Дагон":"Рассвет"):pileChoice?(rowMode==14?"Выбор карты для способности":"Выбор карты для розыгрыша"):handPowerChoice?"Выбор силы из руки":graveyardChoice?"Поглощение из сброса":requestKind==1?"Замена карт":current==1?"Ваш ход":current==2?"Ход соперника":"Ожидание"),skin==3?40:1320,skin==3?14:26,skin==3?360:560,24);
            if(skin==3)drawBetaBattleHud();else {profile(2,96,226,0x532723);profile(1,96,588,0x193E53);}
            drawRows();
            // Row weather sits above the row surface but below every card.
            for each(var fading:Object in weatherFades)content.addChild(fading.sprite);
            for each(var effect:Object in weatherEffects)content.addChild(effect.sprite);
            drawCards(); drawPendingPlacement();
            animateWeather(null);drawBacks();if(skin==3)drawBetaPassStrips();drawVisualCue();
            if(rewardMessage&&(flags>>4)>0)text(content,rewardMessage,510,820,970,25,0xE8D3A6).height=90;
            if(skin==3){
                battlePreview=new Sprite();battlePreview.mouseEnabled=false;battlePreview.mouseChildren=false;content.addChild(battlePreview);
                inspection=new TextField();drawBetaActions();
            }else{
            var panelTop:Number=skin==3?162:130;
            betaFrame(content,1504,panelTop,368,668-panelTop);
            panel(content,1512,panelTop+8,352,660-panelTop-8,0x070908,.55);
            battlePreview=new Sprite();battlePreview.x=1516;battlePreview.y=panelTop+10;content.addChild(battlePreview);
            inspection=text(content,"Наведите на карту.\nI или Shift + клик — полное описание.",1532,skin==3?556:520,312,19,0xD8D0BB);inspection.height=skin==3?104:134;
            inspection.mouseEnabled=true;
            inspection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();inspection.scrollV=Math.max(1,Math.min(inspection.maxScrollV,inspection.scrollV-e.delta*3));});
            var statusText:TextField=text(content,isCaranthirChoice()?"Мороз попадёт в ряд напротив Карантира. Можно переместить подсвеченный отряд или подтвердить этот ряд без перемещения. LB / RB — выбрать ряд.":requestId>0?requestMessage:message,1532,skin==3?668:684,312,20);
            statusText.height=skin==3?78:96;
            var actionY:Number=skin==3?754:790;
            if(playing)button("Пропустить анимацию",1532,actionY,312,true,skipReplay);
            else if(requestId>0&&requestFinish) button(isCaranthirChoice()?"Мороз без перемещения":templateChoice?"Выберите вариант":pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):handPowerChoice?"Выберите отряд":graveyardChoice?"Без поглощения":requestKind==1?"Начать раунд":leaderRow?"Отмена":"Без цели",1532,actionY,312,ready&&requestFinish&&(!rowRequest||leaderRow||rowMode==3||rowMode==1||rowMode>=8),requestAction("OnBetaGwentRequestFinish"));
            else if(requestId>0)text(content,"Выбор обязателен",1532,actionY+12,312,22,0xF5D77F).height=45;
            else button("Пас",1532,actionY,312,canAct(),function():void{submitBoard("OnBetaGwentBoardPass",[revision]);});
            button("Меню партии",1532,skin==3?810:850,312,true,openControllerMenu);
            button(entryMode==2&&(flags>>4)==0?"Сдаться":"Закрыть",1694,skin==3?868:912,150,connected,requestBoardClose);
            if(skin!=3)text(content,"P — пас · L — лидер · D — колода\nG / H — сброс · ПКМ / X — карта",1532,978,312,17,0xB9B4A9).height=54;
            }
            if(!playing&&requestId>0 && requestKind==1) drawChoices();
            updateFocusedInspection();
            if(!playing&&requestId>0&&!(skin==3&&requestKind==1)){
                if(skin==3){
                    var prompt:TextField=text(content,requestKind==2&&!rowRequest&&!canPlacePending()?"Нажмите подсвеченную карту, чтобы применить способность.":requestInstruction(),1536,778,332,21,0xF5D77F);
                    prompt.height=58;betaFace(BetaGwentFonts.BODY,prompt,21,0xF5D77F);prompt.mouseEnabled=false;
                }else{
                    betaNine(content,-1400,976,43,430,158);
                    var legacyPrompt:TextField=betaLabel(content,requestInstruction(),444,161,948,22,0xF5D77F,BetaGwentFonts.BODY,false,"center");legacyPrompt.height=28;legacyPrompt.mouseEnabled=false;
                }
            }
            if(focusedRow>0&&(canPlaceSelected()||canPlacePending())&&rowEnabled(focusedSide,focusedRow)){
                showPlacementGhost({anchor:0,index:0,target:0,side:focusedSide,zone:focusedRow});
            }
            // Delayed effects start invisible on the very first rendered frame,
            // before ENTER_FRAME gets a chance to initialise their alpha.
            for each(var queued:Object in animations)if(queued.hideBeforeDelay&&queued.delay>0)queued.sprite.alpha=0;
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
            tint=0x47BEFF;
            var mark:Sprite=new Sprite();mark.mouseEnabled=false;mark.mouseChildren=false;
            var halo:Sprite=betaVisual(-102,w+26,h+26,tint);
            if(halo){halo.x=w/2;halo.y=h/2;halo.alpha=focused? .6:.4;mark.addChild(halo);targetPulses.push({sprite:halo,base:focused? .6:.4,phase:parent.x*.009});}
            var inner:Sprite=betaVisual(-103,w*.95,h*.8,0x9ADFFF);
            if(inner){inner.x=w/2;inner.y=h*.64;inner.alpha=focused? .42:.26;mark.addChild(inner);}
            var frame:Sprite=betaVisual(-101,w+4,h+4,tint);
            if(frame){frame.x=w/2;frame.y=h/2;mark.addChild(frame);}
            mark.graphics.lineStyle(focused?3:2,tint,.95);mark.graphics.drawRect(1,1,w-2,h-2);
            parent.addChild(mark);
        }
        private function drawFactionBoards():void
        {
            for(var side:int=1;side<=2;side++){
                var faction:int=cardFaction(int(leaderIds[side-1]));
                var number:int=faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:-1;
                if(number<0){var option:Object=deckOption(side==1?ownPreset:enemyPreset);if(option)faction=cardFaction(option.leaderId);number=editorFactionIndex(faction);}
                var area:Array=BetaGwentBoardLayout.boardHalf[String(side)];
                var half:Sprite=BetaGwentCardArt.view(-1300-number*2-(side-1),area[2],area[3]);
                if(half){
                    // Match the camera's screen X convention: original Unity
                    // mesh export puts the score rail on the opposite edge.
                    half.scaleX=-1;half.x=area[0]+area[2];half.y=area[1];content.addChild(half);
                }
            }
        }
        private function showBattleCard(c:Object,detail:Object):void
        {
            if(!battlePreview||!c)return;
            var key:String=c.templateId+":"+c.power+":"+c.tokens;
            if(key==battlePreviewKey&&battlePreview.numChildren)return;battlePreviewKey=key;
            while(battlePreview.numChildren)battlePreview.removeChildAt(0);
            if(skin==3){drawBetaSidePreview(c,detail);return;}
            paintArt(battlePreview,-1250-editorFactionIndex(cardFaction(c.templateId)),336,50,0,0);
            text(battlePreview,c.title,12,10,312,22,0xF4E1B1).height=40;
            var portrait:Sprite=new Sprite();portrait.x=68;portrait.y=62;battlePreview.addChild(portrait);
            if(c.templateId>0)paintChoiceArt(portrait,c.templateId,200,282);else paintCardBack(portrait,200,282,2);
            if(!reducedMotion){
                animations.push({sprite:portrait,fromX:92,fromY:62,toX:68,toY:62,curve:"PREVIEW",duration:BetaGwentBetaMotion.duration("PREVIEW"),appear:true});
                portrait.x=92;portrait.alpha=0;
            }
            betaNine(battlePreview,-1412,204,286,66,60);
            text(battlePreview,BetaGwentCardTags.text(c.templateId)||"—",12,352,312,17,0xC9C3A9).height=32;
            if(inspection)inspection.text=cardReading(c,detail);
        }

        private function betaVisual(id:int,w:Number,h:Number,tint:uint=0xFFFFFF):Sprite
        {
            var image:Sprite=BetaGwentCardArt.view(id,w,h);if(!image)return null;
            var holder:Sprite=new Sprite();holder.mouseEnabled=false;holder.mouseChildren=false;
            image.x=-w/2;image.y=-h/2;holder.addChild(image);
            holder.transform.colorTransform=new ColorTransform(((tint>>16)&255)/255,((tint>>8)&255)/255,(tint&255)/255);
            return holder;
        }
        private function paintBetaCorners(parent:Sprite,w:Number,h:Number,tint:uint):void
        {
            var size:Number=Math.min(24,Math.min(w,h)*.3);
            for(var i:int=0;i<4;i++){
                var corner:Sprite=betaVisual(-107,size,size,tint);if(!corner)continue;
                corner.x=i==0||i==3?size/2:w-size/2;
                corner.y=i<2?size/2:h-size/2;corner.rotation=i==0?180:i==1?270:i==2?0:90;
                parent.addChild(corner);
            }
        }
        private function betaBurst(parent:Sprite,id:int,x:Number,y:Number,size:Number,tint:uint,delay:Number=0,duration:Number=300):void
        {
            if(reducedMotion)return;
            var burst:Sprite=betaVisual(id,size,size,tint);if(!burst)return;
            parent.addChild(burst);burst.x=x;burst.y=y;burst.alpha=0;
            animations.push({sprite:burst,fromX:x,fromY:y,toX:x,toY:y,fade:true,remove:true,duration:duration,
                delay:delay,hideBeforeDelay:true,fromScaleX:.35,fromScaleY:.35,toScaleX:1.35,toScaleY:1.35});
        }
        private function previewOutline(c:Object):void
        {
            var pose:Object=displayedCards[c.id];if(!pose)return;
            actionPreviewLayer.graphics.lineStyle(2,0x68DEEB,.95);
            actionPreviewLayer.graphics.beginFill(0x68DEEB,.10);
            actionPreviewLayer.graphics.drawRect(pose.x,pose.y,pose.width,pose.height);
            actionPreviewLayer.graphics.endFill();
        }
        private function updateActionPreview():void
        {
            var available:Boolean=ready&&!playing&&!detailOpen&&!pileOpen&&!editingDeck&&!selectingDecks&&!browsingCatalog&&!kegOpen&&!controllerMenuOpen;
            var c:Object=hoveredCard;var focus:Object=controller.active?controller.getFocus():null;
            if(focus)c=focus.card;
            var legal:Boolean=available&&c&&(canDirectTarget(c)||requestId>0&&requestKind==2&&!rowRequest&&!canPlacePending()&&findRequestCard(c.id)!=null);
            var side:int=0;var zone:int=0;
            if(available&&!canPlaceSelected()&&!canPlacePending()){
                if(focus&&focus.row){side=focus.row.side;zone=focus.row.zone;}
                else for(var player:int=1;player<=2;player++)for(var row:int=1;row<=4;row*=2){
                    var g:Object=rowGeometry(player,row);
                    if(mouseX>=g.x&&mouseX<=g.x+g.w&&mouseY>=g.y&&mouseY<=g.y+g.h){side=player;zone=row;}
                }
                if(zone>0&&!rowEnabled(side,zone)){side=0;zone=0;}
            }
            var rule:Object=requestId>0?templateRules[requestSourceTemplate]:playRules[selected];
            var key:String=revision+":"+available+":"+selected+":"+(legal?c.id:0)+":"+side+":"+zone+":"+requestCount+":"+(placementPreview?placementPreview.anchor+":"+placementPreview.zone:"none");
            if(key==actionPreviewKey)return;actionPreviewKey=key;
            actionPreviewLayer.graphics.clear();while(actionPreviewLayer.numChildren)actionPreviewLayer.removeChildAt(0);
            if(!available)return;
            var affected:int=0;var summary:String="";var scope:int=rule?int(rule.scope):0;
            if(legal){
                for each(var unit:Object in cards){
                    var hit:Boolean=unit.id==c.id;
                    if((scope==1||scope==2)&&unit.side==c.side&&unit.zone==c.zone&&Math.abs(unit.index-c.index)<=int(rule.radius)){
                        hit=scope==1||(int(unit.tokens)&8)==0;
                    }
                    if(hit&&(unit.zone&7)!=0){previewOutline(unit);affected++;}
                }
                summary="Целей в области: "+affected;
            }else if(zone>0){
                var rows:Array=[zone];if(scope==5&&zone<4)rows.push(zone*2);
                for each(var lane:int in rows){
                    var area:Object=rowGeometry(side,lane);
                    actionPreviewLayer.graphics.lineStyle(2,0x68DEEB,.9);actionPreviewLayer.graphics.drawRect(area.x+2,area.y+2,area.w-4,area.h-4);
                    if(scope==3||scope==6)for each(unit in cards){
                        if(unit.side!=side||unit.zone!=lane||(int(unit.tokens)&8)!=0)continue;
                        var detail:Object=cardDetails[unit.id];var targetRule:Object=templateRules[unit.templateId];
                        if(scope==3&&(!detail||(int(detail.tier)&int(rule.tiers))==0||(int(unit.tokens)&int(rule.ignore))!=0||targetRule&&(int(targetRule.traits)&int(rule.excludedTraits))!=0))continue;
                        if(scope==6&&unit.index!=0&&unit.index!=rowCards(side,lane).length-1)continue;
                        previewOutline(unit);affected++;
                    }
                }
                summary=scope==4||scope==5?"Погода: рядов "+rows.length:scope==3||scope==6?"Целей в области: "+affected:"Выбран ряд для способности";
            }
            if(requestId>0&&requestKind!=1&&!canPlacePending()&&!leaderRow){
                if(summary.length)summary+="\n";
                summary+="Осталось выбрать: "+Math.max(0,requestMax-requestCount);
                if(requestMin>requestCount)summary+=" · выбор обязателен";
            }
            if(summary.length&&!placementPreview){var label:TextField=text(actionPreviewLayer,summary,1536,842,332,19,0xA8EDF2);label.height=76;label.mouseEnabled=false;}
        }
        private function rowCards(side:int,zone:int):Array
        {var result:Array=[];for each(var c:Object in cards)if(c.side==side&&c.zone==zone)result.push(c);return result;}
        private function updateAimPreview():void
        {
            var c:Object=hoveredCard;
            if(controller.active){var focus:Object=controller.getFocus();c=focus?focus.card:null;}
            var legal:Boolean=c&&!detailOpen&&!pileOpen&&!playing&&!editingDeck&&!selectingDecks&&!browsingCatalog&&
                (canDirectTarget(c)||requestId>0&&requestKind==2&&!rowRequest&&!canPlacePending()&&findRequestCard(c.id)!=null);
            var target:Object=legal?displayedCards[c.id]:null;
            var source:Object=displayedCards[selected];
            if(!source&&requestId>0&&requestSourceId>0&&displayedCards[requestSourceId])source=displayedCards[requestSourceId];
            if(!source&&activeCue)source=displayedCards[activeCue.source];
            if(!source&&requestId>0&&aimSourceId>0)source=displayedCards[aimSourceId];
            if(!source&&requestId>0&&aimSourceId==-1){var seat:Array=betaLeaderRect(1);source={x:seat[0],y:seat[1],width:seat[2],height:seat[3]};}
            var key:String=target?revision+":"+c.id+":"+selected:"";if(key==aimKey)return;
            aimKey=key;aimLayer.graphics.clear();if(!target)return;
            var tx:Number=target.x+target.width/2,ty:Number=target.y+target.height/2;
            var sx:Number=source?source.x+source.width/2:960,sy:Number=source?source.y+source.height/2:210;
            var dx:Number=tx-sx,dy:Number=ty-sy,length:Number=Math.sqrt(dx*dx+dy*dy);if(length<25)return;
            dx/=length;dy/=length;var color:uint=0x48BFFF;
            if(source&&source.width>0)drawCueArrow(aimLayer,source.x,source.y,source.width,source.height,target.x,target.y,target.width,target.height,color);
            else drawCueArrow(aimLayer,sx-1,sy-1,2,2,target.x,target.y,target.width,target.height,color);
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
            pilePage=0;pilePicked=null;
        }
        public function pushPileCard(templateId:int,title:String,description:String,power:int,armor:int,tier:int,tokens:int,timer:int,typeMask:int):void
        {
            if(!pileView)return;
            pileView.cards.push({templateId:templateId,title:title,description:description,power:power,armor:armor,
                tier:tier,tokens:tokens,timer:timer,typeMask:typeMask,side:pileView.side,zone:pileView.zone});
        }
        public function finishPileView(rev:int):void
        {
            if(!pileView||rev!=revision||rev!=pileView.revision||pileView.cards.length!=pileView.count){closePileView();return;}
            // Stable within an opening; the server already shuffled a copy independently of gameplay.
            var grouped:Array=[];
            for each(var tier:int in [8,4,2])for each(var c:Object in pileView.cards)
                if((int(c.tier)&(tier==8?9:tier))!=0&&grouped.indexOf(c)<0)grouped.push(c);
            // Leaders count with gold; keep unfamiliar runtime tiers visible as well.
            for each(c in pileView.cards)if(grouped.indexOf(c)<0)grouped.push(c);
            pileView.cards=grouped;
            pileOpen=true;hoverCardId=0;
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            drawPileView();
        }
        public function pushPilePowerBase(normalPower:int):void
        { if(pileView&&pileView.cards.length>0)pileView.cards[pileView.cards.length-1].normalPower=normalPower; }
        private function closePileView():void
        {
            hoveredCard=null;hoveredDetail=null;hoverPreviewAt=0;hoverCardId=0;
            pileOpen=false;pileView=null;pilePicked=null;pileDetail=null;pilePicture=null;
            while(pileLayer.numChildren)pileLayer.removeChildAt(0);
        }
        // Shared horizontal browsers follow the local video at 02:03 and 40:00.
        // Card hit bounds exclude the reading area: reading cannot play/exchange a card.
        private function stripCard(parent:Sprite,c:Object,slot:int,shown:int,side:int,detail:Object):Sprite
        {
            var tile:Sprite=new Sprite();tile.x=(1920-(shown*330-50))/2+slot*330;tile.y=245;parent.addChild(tile);
            var glow:Sprite=betaVisual(-102,STRIP_CARD_W+46,STRIP_CARD_H+40,0x48C6FF);
            if(glow){glow.x=STRIP_CARD_W/2;glow.y=STRIP_CARD_H/2;glow.alpha=0;tile.addChild(glow);}
            c.stripGlow=glow;
            paintBetaFace(tile,c.templateId,STRIP_CARD_W,STRIP_CARD_H,side);
            paintStaticCardState(tile,c,STRIP_CARD_W,STRIP_CARD_H);
            if(c.typeMask==4||detail&&detail.typeMask==4)betaPowerField(tile,String(c.power),STRIP_CARD_W,STRIP_CARD_H,powerColor(c));
            var title:TextField=text(tile,c.title,0,356,STRIP_CARD_W,23,0xF4EFE4);title.height=66;
            betaFace(BetaGwentFonts.TITLE,title,23,0xF4EFE4,false,"center");
            var body:TextField=text(tile,readableText(detail?detail.description:c.description),4,434,STRIP_CARD_W-8,21,0xD7D4CB);body.height=235;
            betaFace(BetaGwentFonts.BODY,body,21,0xD7D4CB);body.mouseEnabled=true;c.stripBody=body;
            body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV-e.delta*3));e.stopPropagation();});
            body.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            attachInspect(tile,c,detail,STRIP_CARD_W,STRIP_CARD_H);
            return tile;
        }
        private function stripHeading(parent:Sprite,title:String,subtitle:String):void
        {
            panel(parent,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x030609,.93);
            betaLabel(parent,title.toUpperCase(),160,55,1600,36,0xEEECE5,BetaGwentFonts.TITLE,true,"center",5);
            betaLabel(parent,subtitle,140,131,1640,23,0xD1CEC5,BetaGwentFonts.BODY,false,"center");
        }
        // Fit the complete set in a fixed viewport; captions are part of the fit.
        private function overviewLayout(count:int,areaW:Number,areaH:Number,maxCols:int,limitW:Number,captionH:Number):Object
        {
            var rows:int=Math.max(1,Math.ceil(count/maxCols)),cols:int=Math.max(1,Math.ceil(count/rows));
            var w:Number=Math.floor(Math.min(limitW,(areaW-(cols-1)*18)/cols,((areaH-(rows-1)*18)/rows-captionH)*BETA_CARD_ASPECT));
            var h:Number=Math.floor(w/BETA_CARD_ASPECT);
            return {cols:cols,rows:rows,w:w,h:h,captionH:captionH,stepY:h+captionH+18,blockH:rows*(h+captionH)+(rows-1)*18};
        }
        private function compactOverviewCard(parent:Sprite,c:Object,detail:Object,x:Number,y:Number,w:Number,h:Number,captionH:Number):Sprite
        {
            var tile:Sprite=new Sprite();tile.x=x;tile.y=y;parent.addChild(tile);
            var glow:Sprite=betaVisual(-102,w+24,h+28,0x48C6FF);
            if(glow){glow.x=w/2;glow.y=h/2;glow.alpha=0;tile.addChild(glow);}c.stripGlow=glow;
            if(c.hidden)paintCardBack(tile,w,h,int(c.side));
            else if(c.templateId==113402)paintChoiceArt(tile,c.templateId,w,h);
            else paintBetaFace(tile,c.templateId,w,h,int(c.side));
            if(c.typeMask==4||detail&&detail.typeMask==4)betaPowerField(tile,String(c.power),w,h,powerColor(c));
            var size:Number=Math.max(13,Math.min(20,w*.11));
            var title:TextField=text(tile,c.title,0,h+6,w,int(size),0xF4EFE4);title.height=captionH-6;
            betaFace(BetaGwentFonts.TITLE,title,size,0xF4EFE4,false,"center");
            paintStaticCardState(tile,c,w,h);
            attachInspect(tile,c,detail,w,h);return tile;
        }
        private function drawOwnDeckPreview(c:Object):void
        {
            while(pilePicture.numChildren)pilePicture.removeChildAt(0);
            paintBetaFace(pilePicture,c.templateId,280,340,int(c.side));
            if(c.typeMask==4)betaPowerField(pilePicture,String(c.power),280,340,powerColor(c));
            var title:TextField=text(pilePicture,c.title,0,356,280,23,0xF4EFE4);title.height=66;
            betaFace(BetaGwentFonts.TITLE,title,23,0xF4EFE4,false,"center");
            pileDetail=text(pilePicture,readableText(c.description),0,432,280,21,0xD7D4CB);pileDetail.height=235;
            betaFace(BetaGwentFonts.BODY,pileDetail,21,0xD7D4CB);pileDetail.mouseEnabled=true;
            var body:TextField=pileDetail;
            body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV-e.delta*3));e.stopPropagation();});
            body.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
        }
        private function drawOwnDeckView():void
        {
            while(pileLayer.numChildren)pileLayer.removeChildAt(0);pilePage=0;
            var window:Sprite=new Sprite();pileLayer.addChild(window);
            stripHeading(window,"Ваша колода","Просмотр карт · "+pileView.count+" карт");
            betaLabel(window,"По цвету · порядок внутри групп случайный, порядок добора скрыт",200,185,1520,19,0xAAA69D,BetaGwentFonts.BODY,false,"center");
            var group:Array=pileView.cards,layout:Object=overviewLayout(group.length,1280,700,10,200,group.length>30?42:54);
            for(var i:int=0;i<group.length;i++){
                var c:Object=group[i];c.viewKey="pile:"+pileView.revision+":"+pileView.side+":"+pileView.zone+":"+i;
                var row:int=int(i/layout.cols),column:int=i%layout.cols,inRow:int=Math.min(layout.cols,group.length-row*layout.cols);
                var x:Number=80+(1280-(inRow*layout.w+(inRow-1)*18))/2+column*(layout.w+18);
                var tile:Sprite=compactOverviewCard(window,c,{description:c.description},x,220+row*layout.stepY,layout.w,layout.h,layout.captionH);
                pileCardInspect(tile,c);
            }
            pilePicture=new Sprite();pilePicture.x=1480;pilePicture.y=220;window.addChild(pilePicture);pileDetail=null;
            pilePicture.buttonMode=true;
            pilePicture.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();if(pilePicked)openCardDetail(pilePicked,{description:pilePicked.description});});
            pilePicture.addEventListener(RIGHT_CLICK_EVENT,function(e:MouseEvent):void{e.stopImmediatePropagation();if(pilePicked)openCardDetail(pilePicked,{description:pilePicked.description});});
            if(!pilePicked||group.indexOf(pilePicked)<0)pilePicked=group.length?group[0]:null;
            if(pilePicked)showPileCard(pilePicked);
            else betaLabel(window,"Колода пуста.",240,460,1100,28,0xD1CEC5,BetaGwentFonts.BODY,false,"center");
            editorBetaButton(window,"Осмотреть карту",1480,922,280,48,group.length>0,function():void{if(pilePicked)openCardDetail(pilePicked,{description:pilePicked.description});});
            editorBetaButton(window,"Вернуться к игре",795,978,330,48,true,closePileView);
        }
        private function stepPileCard(direction:int):void
        {
            if(!pileView||!pileView.cards.length)return;
            var index:int=pileView.cards.indexOf(pilePicked);if(index<0)index=pilePage*STRIP_PAGE_SIZE;
            index=Math.max(0,Math.min(pileView.cards.length-1,index+direction));
            if(pileView.zone==16){showPileCard(pileView.cards[index]);return;}
            pilePicked=pileView.cards[index];var page:int=int(index/STRIP_PAGE_SIZE);
            if(page!=pilePage){pilePage=page;drawPileView();}else showPileCard(pilePicked);
        }
        private function pileCardInspect(tile:Sprite,c:Object):void
        {
            controller.registerControl(tile,c.title,function():void{openCardDetail(c,{description:c.description});},c,{description:c.description},"card");
            tile.buttonMode=true;
            tile.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{showPileCard(c);});
            tile.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();showPileCard(c);openCardDetail(c,{description:c.description});});
        }
        private function showPileCard(c:Object):void
        {
            if(!pileOpen||!pileView||!c)return;
            var changed:Boolean=pilePicked!=c;pilePicked=c;
            for each(var other:Object in pileView.cards)if(other.stripGlow)other.stripGlow.alpha=other==c? .8:0;
            if(pileView.zone==16&&pilePicture){if(changed||!pilePicture.numChildren)drawOwnDeckPreview(c);}
            else pileDetail=c.stripBody as TextField;
        }
        private function drawPileView():void
        {
            if(!pileOpen||!pileView)return;
            if(pileView.zone==16){drawOwnDeckView();return;}
            while(pileLayer.numChildren)pileLayer.removeChildAt(0);
            var window:Sprite=new Sprite();pileLayer.addChild(window);
            var name:String=pileView.zone==16?"Ваша колода":pileView.side==1?"Ваш сброс":"Сброс соперника";
            stripHeading(window,name,"Просмотр карт · "+pileView.count+" карт");
            var group:Array=pileView.cards;
            var pages:int=Math.max(1,Math.ceil(group.length/STRIP_PAGE_SIZE));pilePage=Math.max(0,Math.min(pilePage,pages-1));
            var first:int=pilePage*STRIP_PAGE_SIZE,shown:int=Math.min(STRIP_PAGE_SIZE,group.length-first);
            for each(var old:Object in group){old.stripGlow=null;old.stripBody=null;}
            for(var i:int=first;i<first+shown;i++){
                var c:Object=group[i];c.viewKey="pile:"+pileView.revision+":"+pileView.side+":"+pileView.zone+":"+i;
                var tile:Sprite=stripCard(window,c,i-first,shown,int(c.side),{description:c.description});
                pileCardInspect(tile,c);
            }
            if(!pilePicked||group.indexOf(pilePicked)<first||group.indexOf(pilePicked)>=first+shown)pilePicked=shown>0?group[first]:null;
            showPileCard(pilePicked);
            if(!shown)betaLabel(window,pileView.zone==16?"Колода пуста.":"Сброс пуст.",240,460,1440,28,0xD1CEC5,BetaGwentFonts.BODY,false,"center");
            editorBetaButton(window,"‹ Назад",140,978,220,48,pilePage>0,function():void{pilePage--;pilePicked=null;drawPileView();});
            editorBetaButton(window,"Вперёд ›",1560,978,220,48,pilePage+1<pages,function():void{pilePage++;pilePicked=null;drawPileView();});
            betaLabel(window,(pilePage+1)+" / "+pages,825,946,270,20,0xBBB6AC,BetaGwentFonts.BODY,false,"center");
            editorBetaButton(window,"Вернуться к игре",795,978,330,48,true,closePileView);
            betaLabel(window,pileView.zone==16?"По цвету · порядок внутри групп случайный, порядок добора скрыт":"Просмотр не расходует ход · колода соперника скрыта",200,185,1520,19,0xAAA69D,BetaGwentFonts.BODY,false,"center");
            window.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();pilePage=Math.max(0,Math.min(pages-1,pilePage+(e.delta<0?1:-1)));pilePicked=null;drawPileView();});
        }

        private function drawBetaBattleHud():void
        {
            drawBetaTurnGlow();
            // Native level8 sprites, not stretched button or panel borders.
            for each(var divider:Array in BetaGwentBoardDetails120.DIVIDERS)
                paintArt(content,int(divider[0]),divider[3],divider[4],divider[1],divider[2]);
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
                    // Original: an unwon half is the ribbon's embossed outline (no sprite).
                    if(!won)continue;
                    var crown:Sprite=new Sprite();crown.x=slot[0];crown.y=slot[1];crown.mouseEnabled=false;crown.mouseChildren=false;content.addChild(crown);
                    paintArt(crown,(side==1?-1540:-1542)+(halfIndex-1),slot[2],slot[3],0,0);
                    if(won&&activeCue&&activeCue.kind==6&&halfIndex>previousCrowns[side-1]&&!reducedMotion){
                        animations.push({sprite:crown,fromX:slot[0],fromY:slot[1],toX:slot[0],toY:slot[1],appear:true,duration:480,delay:260,fromScaleX:1.7,fromScaleY:1.7,toScaleX:1,toScaleY:1});
                        crown.alpha=0;crown.scaleX=crown.scaleY=1.7;
                    }
                }
                var scoreBox:Array=BetaGwentBoardLayout.score[key];
                var scoreTint:uint=scores[side-1]>scores[2-side]?0xFFD52A:0xFFFFFF;
                var scoreX:Number=scoreBox[0]-18,scoreY:Number=scoreBox[1]+scoreBox[3]/2-76;
                var value:TextField=text(content,String(scores[side-1]),scoreX,scoreY,scoreBox[2]+36,120,scoreTint);value.height=160;value.filters=[new GlowFilter(0x000000,1,3,3,6)];
                if(!BetaGwentFonts.apply(value,BetaGwentFonts.NUMBERS,120,scoreTint,true,"center")){value.defaultTextFormat=new TextFormat("$NormalFont",120,scoreTint,true,null,null,null,null,"center");value.setTextFormat(value.defaultTextFormat);}
                centerBetaNumber(value,scoreBox[0]+scoreBox[2]/2,scoreBox[1]+scoreBox[3]/2,120);scoreX=value.x;scoreY=value.y;
                if(playing&&activeCue&&activeCue.kind==2&&previousScores[side-1]!=scores[side-1]&&!reducedMotion){
                    value.text=String(previousScores[side-1]);
                    animations.push({sprite:value,fromX:scoreX,fromY:scoreY,toX:scoreX,toY:scoreY,counter:value,fromValue:previousScores[side-1],toValue:scores[side-1],numberX:scoreBox[0]+scoreBox[2]/2,numberY:scoreBox[1]+scoreBox[3]/2,numberSize:120,duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:scores[side-1]>previousScores[side-1]?"POWER_UP":"POWER_DOWN",delay:cueImpactDelay()*animationTempo});
                }
                var seat:Array=betaLeaderRect(side);
                var leader:Sprite=new Sprite();leader.x=seat[0];leader.y=seat[1];content.addChild(leader);
                paintBetaFace(leader,int(leaderIds[side-1]),seat[2],seat[3],side);
                var leaderPower:Object=BetaGwentCardText.find(int(leaderIds[side-1]));
                if(leaderPower&&leaderPower.power>0)betaPowerField(leader,String(leaderPower.power),seat[2],seat[3],0xFFFFFF);
                var available:Boolean=side==1?leaderOne:leaderTwo;if(!available)leader.alpha=.45;
                var leaderText:Object=BetaGwentCardText.find(int(leaderIds[side-1]));
                var leaderView:Object={id:0,templateId:int(leaderIds[side-1]),title:leaderNames[side-1],side:side,zone:64,power:leaderText?leaderText.power:0,tokens:0};
                attachInspect(leader,leaderView,templateDetails[leaderIds[side-1]],seat[2],seat[3]);
                if(side==1&&available&&canAct()){
                    var playLeader:Function=function():void{submitBoard("OnBetaGwentBoardLeader",[revision]);};
                    // Leader is the leftmost card of the hand on a controller (same accept button).
                    controller.registerControl(leader,"Лидер · "+leaderTitle,playLeader,leaderView,templateDetails[leaderIds[side-1]],"hand",null,new Rectangle(0,0,seat[2],seat[3]));
                    leader.buttonMode=true;leader.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{if(!isInspectMouse(e))submitBoard("OnBetaGwentBoardLeader",[revision]);});
                }
                drawBetaProfile(side);
                var count:int=side==2?enemyHand:0;
                if(side==1)for each(var c:Object in cards)if(c.side==1&&c.zone==8)count++;if(available)count++;
                drawBetaCounter(-1522,count,456,side);
                drawBetaCounter(-1520,graves[side-1],1533,side);
                drawBetaCounter(-1521,deckCounts[side-1],1877,side);
                var grave:Array=BetaGwentBoardLayout.grave[key],deck:Array=BetaGwentBoardLayout.deck[key];
                drawBetaPile(side,32,grave[0],grave[1],graves[side-1],grave[2],grave[3]);
                drawBetaPile(side,16,deck[0],deck[1],deckCounts[side-1],deck[2],deck[3]);
            }
            var shown:int=current==1||current==2?current:coinSide;if(shown==0)shown=1;
            // CoinBase mesh (r=12.21) projected: centre (206.7,540.4), 135.8 x 131.3.
            var coinBox:Array=[138.8,474.8,135.8,131.3];
            var coin:Sprite=new Sprite();coin.x=coinBox[0]+coinBox[2]/2;coin.y=coinBox[1]+coinBox[3]/2;coin.mouseEnabled=false;coin.mouseChildren=false;content.addChild(coin);
            var faces:Array=[];var oldShown:int=coinSide==1||coinSide==2?coinSide:shown;
            for each(var faceSide:int in [oldShown,shown]){
                var face:Sprite=new Sprite();face.mouseEnabled=false;face.mouseChildren=false;coin.addChild(face);faces.push(face);
                var baseCoin:Sprite=new Sprite();face.addChild(baseCoin);paintArt(baseCoin,-1500,coinBox[2],coinBox[3],-coinBox[2]/2,-coinBox[3]/2);
                baseCoin.transform.colorTransform=new ColorTransform(faceSide==1?0.2:1,faceSide==1?0.68:0.2,faceSide==1?1:0.15);
                var iconW:Number=coinBox[2]*.55,iconH:Number=coinBox[3]*.55;
                paintArt(face,-1501-editorFactionIndex(cardFaction(int(leaderIds[faceSide-1]))),iconW,iconH,-iconW/2,-iconH/2);
            }
            faces[0].visible=false;
            if(shown!=coinSide&&!reducedMotion&&coinSide!=0){
                faces[0].visible=true;faces[1].visible=false;
                animations.push({sprite:coin,fromX:coin.x,fromY:coin.y,toX:coin.x,toY:coin.y,duration:420,coinFaces:faces});
            }
            coinSide=shown;
            drawBetaCoinControls(coin,coinBox);drawBetaMenuButton();
        }
        // stage104-hud: original Beta battle HUD (UIBattlePrefab, UIBoardPlayerControl,
        // UISidePreview, UIBoardMessagesPrefab/YourTurnBanner, UIPlayerPassPrefab).
        // stage104-hud
        private var betaOverlay:Sprite=new Sprite();
        private var turnBannerAt:int=0;
        private var turnFlash:Sprite;
        private static const TURN_BANNER_MS:int=1400;
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
            betaFace(face,field,size,color,bold,align,spacing);
            // Every label must fit its slot: drop tracking first, then shrink (never below 60%).
            if(value&&value.indexOf("\n")<0&&Math.max(field.textWidth,BetaGwentTextMetrics.width(value,face,size,spacing))>w-6){
                var fit:Number=size;
                if(spacing!=0){betaFace(face,field,fit,color,bold,align,0);spacing=0;}
                while(Math.max(field.textWidth,BetaGwentTextMetrics.width(value,face,fit))>w-6&&fit>size*0.35){fit-=1;betaFace(face,field,fit,color,bold,align,0);}
                field.y=y+(size-fit)*0.6;
            }
            return field;
        }
        private function betaSlotLabel(parent:Sprite,value:String,x:Number,y:Number,w:Number,h:Number,size:Number,color:uint,face:String):TextField
        {
            var field:TextField=betaLabel(parent,value,x,y,w,size,color,face,false,"center");
            field.y=y+(h-field.textHeight)/2-2;field.height=field.textHeight+4;return field;
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
            var name:String=side==1?"Геральт":String(leaderNames[1]||"Соперник");
            betaLabel(content,name,192,top-3,320,21,side==1?0x3EA9E0:0xD0383A,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(content,side==2?npcDeckLabel:String(leaderNames[side-1]||""),192,top+26,330,17,0xEDE7DA,BetaGwentFonts.BODY);
        }
        private function centerBetaNumber(field:TextField,cx:Number,cy:Number,size:Number):void
        {
            if(!field.embedFonts){field.y=cy-field.textHeight/2-2;return;}
            var offset:Array=BetaGwentTextMetrics.numberOffset(field.text,size);
            field.x=cx-field.width/(2*field.scaleX)-offset[0];field.y=cy-offset[1];
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
            if(!controller.active)paintArt(hint,BetaGwentHud104.KEY_LC,36,36,20,414);
            if(!controller.active)betaLabel(hint,"ЗАЖМИТЕ, ЧТОБЫ СПАСОВАТЬ",60,416,330,22,0xF2EEE4,BetaGwentFonts.BODY);
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
        private function cardById(id:int):Object
        { for each(var candidate:Object in cards)if(candidate.id==id)return candidate;return null; }
        private function inspectFocusedCard():void
        {
            var c:Object=hoveredCard;if(!c&&selected>0)c=cardById(selected);
            if(!c&&keyboardFocusId>0)c=cardById(keyboardFocusId);
            if(!c&&lastInspectedCard)c=lastInspectedCard;
            if(c)openCardDetail(c,cardDetails[c.id]||templateDetails[c.templateId]);
        }
        private function drawBetaActions():void
        {
            hintRight=1880;
            if(playing){drawBetaHint("Пропустить",controller.active?BetaGwentHud104.PAD_A:BetaGwentHud104.KEY_LC,skipReplay);return;}
            if(requestId>0&&requestFinish){
                drawBetaHint(isCaranthirChoice()?"Мороз без перемещения":templateChoice?"Выберите вариант":pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):handPowerChoice?"Выберите отряд":graveyardChoice?"Без поглощения":requestKind==1?"Закончить обмен":leaderRow?"Отмена":"Без цели",
                    controller.active?BetaGwentHud104.PAD_A:BetaGwentHud104.KEY_LC,requestAction("OnBetaGwentRequestFinish"),ready&&requestFinish&&(!rowRequest||leaderRow||rowMode==3||rowMode==1||rowMode>=8));
            }else if(requestId>0)drawBetaHint("Выбор обязателен",0,null,false);
            drawBetaHint("Осмотреть",controller.active?BetaGwentHud104.PAD_X:BetaGwentHud104.KEY_RC,inspectFocusedCard,true);
            // Pass is hold-only; the coin and controller/keyboard progress share the same action.
            if((flags>>4)>0&&ready){
                betaWideButton("Закрыть",840,640,240,connected,requestBoardClose);
            }
        }
        private function betaWideButton(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function):void
        {
            var b:Sprite=new Sprite();b.x=x;b.y=y;content.addChild(b);b.alpha=enabled?1:.5;
            paintArt(b,BetaGwentHud104.WIDE_IDLE,w,48,0,0);
            var hover:Sprite=new Sprite();hover.mouseEnabled=false;paintArt(hover,BetaGwentHud104.WIDE_HOVER,w,48,0,0);hover.alpha=0;b.addChild(hover);
            betaLabel(b,title.toUpperCase(),18,10,w-36,22,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",2).mouseEnabled=false;
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
            var previewX:Number=1477+(405-w)/2;
            var card:Sprite=new Sprite();card.x=previewX;card.y=572-h;battlePreview.addChild(card);
            if(c.templateId>0){
                paintBetaFace(card,c.templateId,w,h,side);
                var original:Object=BetaGwentCardText.find(c.templateId);
                if(c.power!=null&&(!original||original.typeMask==4||int(c.power)>0))betaPowerField(card,String(c.power),w,h,powerColor(c));
            }else paintCardBack(card,w,h,2);
            paintStaticCardState(card,c,w,h);
            card.filters=[new GlowFilter(side==2?0xE0402A:0x3AA8F0,.85,16,16,2,2)];
            if(!reducedMotion){
                animations.push({sprite:card,fromX:previewX+24,fromY:card.y,toX:previewX,toY:card.y,curve:"PREVIEW",duration:BetaGwentBetaMotion.duration("PREVIEW"),appear:true});
                card.x=previewX+24;card.alpha=0;
            }
            var entry:Object=BetaGwentFullCatalog.find(c.templateId);
            var faction:int=entry?int(entry.faction):1;
            var fi:int=(faction&62)==0?sideFaction(side):editorFactionIndex(faction);
            if(c.templateId<=0)fi=sideFaction(2);
            paintArt(battlePreview,BetaGwentHud104.titleBg(fi),312,76,previewX,586);
            paintArt(battlePreview,BetaGwentHud104.titleLine(fi),312,4,previewX,584);
            var title:String=String(c.title||"").toUpperCase();
            var name:TextField=betaLabel(battlePreview,title,previewX+14,592,284,20,0xFFFFFF,BetaGwentFonts.TITLE,true,null,3);
            if(name.textWidth>280)betaFace(BetaGwentFonts.TITLE,name,Math.max(13,Math.floor(20*276/name.textWidth)),0xFFFFFF,true,null,2);
            betaLabel(battlePreview,c.templateId>0?(BetaGwentCardTags.text(c.templateId)||""):"",previewX+14,626,284,16,0xE4E0D6,BetaGwentFonts.BODY);
            var hidden:Boolean=(c.zone&7)!=0&&(int(c.tokens)&8)!=0;
            var reading:String=hidden?ambushReading(c):readableText(detail?detail.description:c.description);
            if(c.timer!=null&&int(c.timer)>=0)reading+=(reading.length?"\n":"")+"Счётчик: "+int(c.timer);
            var info:Sprite=new Sprite();info.x=previewX;info.y=662;battlePreview.addChild(info);
            var body:TextField=text(info,reading,14,10,284,18,0xEDEAE2);body.wordWrap=true;body.multiline=true;
            body.height=Math.min(pileOpen?245:330,body.textHeight+10);
            if(browsingCatalog)catalogAbility=body;
            if(pileOpen){pileDetail=body;body.mouseEnabled=true;body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{body.scrollV-=e.delta;e.stopPropagation();});}
            var bh:Number=Math.max(56,body.height+20);
            var bg:Sprite=new Sprite();info.addChildAt(bg,0);paintArt(bg,BetaGwentHud104.infoBg(fi),312,bh,0,0);
            paintArt(info,BetaGwentHud104.titleLine(fi),312,4,0,bh-2);
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
            root.graphics.beginFill(winner==1?0x02121E:winner==2?0x1E0303:0x0E0E0E,.78);root.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);root.graphics.endFill();
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
            var b:Sprite=new Sprite();b.x=960;b.y=540;b.mouseEnabled=false;b.mouseChildren=false;betaOverlay.addChild(b);
            turnFlash=betaVisual(-103,1250,350,0x7BD7FF);
            if(turnFlash){turnFlash.x=960;turnFlash.y=540;betaOverlay.addChildAt(turnFlash,0);}
            paintArt(b,BetaGwentHud104.TURN_LEFT,145,75,-371,-46);
            paintArt(b,BetaGwentHud104.TURN_RIGHT,145,75,226,-46);
            paintArt(b,BetaGwentHud104.TURN_BG,522,128,-261,-64);
            betaLabel(b,"ВАШ ХОД!",-261,-26,522,38,0xFFFFFF,BetaGwentFonts.TITLE,true,"center",5);
        }
        private function animateBetaOverlay(e:Event):void
        {try{animateBetaOverlayBody(e);}catch(frameError:Error){reportUIError("animateBetaOverlay",frameError);}}
        private function animateBetaOverlayBody(e:Event):void
        {
            var now:int=getTimer();
            if(turnBannerAt>0){
                var t:int=now-turnBannerAt;
                if(t>TURN_BANNER_MS||skin!=3){turnBannerAt=0;turnFlash=null;while(betaOverlay.numChildren)betaOverlay.removeChildAt(0);}
                else{
                    if(!betaOverlay.numChildren)drawYourTurnBanner();
                    betaOverlay.alpha=1;
                    var b:Sprite=betaOverlay.getChildAt(betaOverlay.numChildren-1) as Sprite;
                    var opening:Number=Math.min(1,t/230),closing:Number=Math.min(1,Math.max(0,(TURN_BANNER_MS-t)/230));
                    b.alpha=Math.min(1,t/100)*closing;b.scaleY=1;
                    b.scaleX=reducedMotion?1:Math.max(.08,Math.min(opening,closing));
                    if(turnFlash){turnFlash.alpha=reducedMotion?0:.65*Math.sin(Math.PI*Math.min(1,t/800));turnFlash.scaleX=turnFlash.scaleY=.8+.2*Math.min(1,t/350);}
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
        // stage104-intro
        // UIGameIntroRootPrefab (handshake) presentation.
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
            var name:String=side==1?"Геральт":String(leaderNames[1]||"Соперник");
            betaLabel(info,name,212,6,300,21,side==1?0x3EA9E0:0xD0383A,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(info,side==1?"Ведьмак":npcDeckLabel,212,34,300,18,side==1?0xB9D84A:0xEDE7DA,BetaGwentFonts.BODY);
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
            introLayer.graphics.beginFill(0,1);introLayer.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);introLayer.graphics.endFill();
            introSide(2);introSide(1);
            var line:Sprite=new Sprite();introLayer.addChild(line);
            line.graphics.lineStyle(2,0x8A8A8A,.8);line.graphics.moveTo(0,540);line.graphics.lineTo(1920,540);introPart(line,0,350);
            var vs:Sprite=new Sprite();vs.x=960;vs.y=545;introLayer.addChild(vs);
            paintArt(vs,BetaGwentHud104.VS,196,127,-98,-63);introPart(vs,700,1000,0,0,2.2);
            introLayer.addEventListener(MouseEvent.CLICK,skipIntro);
            introStart=Math.max(1,getTimer());
            send("OnBetaGwentAudioIntro",[int(leaderIds[1]),int(leaderIds[0])]);
        }
        private var introSkipAt:int=0;
        // getTimer() starts with the movie: "now - INTRO_MS" can be <= 0 in the first seconds,
        // which used to leave the black intro layer on screen forever. Track the skip separately.
        private function skipIntro(e:MouseEvent=null):void
        { if(e)e.stopImmediatePropagation();if(introStart>0&&introSkipAt==0)introSkipAt=getTimer(); }
        private function finishIntro():void
        {
            introStart=0;introSkipAt=0;introParts=[];introLayer.removeEventListener(MouseEvent.CLICK,skipIntro);
            introLayer.graphics.clear();while(introLayer.numChildren)introLayer.removeChildAt(0);introLayer.mouseEnabled=false;
        }
        private function animateIntro(e:Event):void
        {try{animateIntroBody(e);}catch(frameError:Error){reportUIError("animateIntro",frameError);}}
        private function animateIntroBody(e:Event):void
        {
            if(introStart<=0){if(introLayer.numChildren>0)finishIntro();return;}
            var t:int=getTimer()-introStart;
            if(introSkipAt>0){var fade:int=getTimer()-introSkipAt;if(fade>=380){finishIntro();return;}introLayer.alpha=1-fade/380;return;}
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
        private function drawBetaPile(side:int,zone:int,x:Number,y:Number,count:int,w:Number=72,h:Number=101):void
        {
            // Card stack inside the original 25.2 x 30 collider (card aspect kept).
            var cw:Number=Math.min(w-8,(h-8)*256/360),ch:Number=cw*360/256;
            var pile:Sprite=new Sprite();pile.x=x+(w-cw)/2;pile.y=y+(h-ch)/2;content.addChild(pile);
            if(count>1&&skin==3)for(var stack:int=Math.min(3,count-1);stack>0;stack--){
                paintArt(pile,zone==32?BetaGwentHud104.cardBack(5):BetaGwentHud104.cardBack(sideFaction(side)),cw-6,ch-6,stack*2,stack*2);
            }
            if(zone==32&&skin==3){paintArt(pile,BetaGwentHud104.cardBack(5),cw-6,ch-6,0,0);pile.alpha=.85;}else paintCardBack(pile,cw-6,ch-6,side);
            var top:Object=null;
            if(zone==32)for each(var c:Object in cards)if(c.side==side&&c.zone==32&&(top==null||c.index>top.index))top=c;
            if(top)paintChoiceArt(pile,top.templateId,cw-6,ch-6);
            if(skin!=3)paintArt(pile,zone==32?-1520:-1521,32,32,cw-34,ch-36);
            var pileCount:TextField=text(pile,String(count),0,ch/2-20,cw,28);pileCount.height=40;
            if(skin==3)pileCount.visible=false;else if(!BetaGwentFonts.apply(pileCount,BetaGwentFonts.NUMBERS,28,0xFFFFFF,true,"center")){pileCount.defaultTextFormat=new TextFormat("$NormalFont",28,0xFFFFFF,true,null,null,null,null,"center");pileCount.setTextFormat(pileCount.defaultTextFormat);}
            if(count==0&&!(skin==3&&zone==32))pile.alpha=.45;
            var enabled:Boolean=canInspectPile()&&(zone==32||side==1);
            if(enabled){
                var action:Function=function():void{inspectPile(side,zone);};
                controller.registerControl(pile,(zone==32?"Сброс":"Колода")+" · "+(side==1?"Геральт":"Соперник"),action,null,null,"control",null,new Rectangle(0,0,cw,ch));
                pile.buttonMode=true;pile.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();action();});
            }
        }
        private function profile(side:int,x:Number,y:Number,color:uint):void
        {
            var p:Sprite=betaFrame(content,x,y,280,280);
            panel(p,8,8,264,264,0x070909,.5);
            paintArt(p,-1420-editorFactionIndex(cardFaction(int(leaderIds[side-1]))),280,66,0,0);
            text(p,side==1?"Геральт":"Соперник",18,14,250,25);
            text(p,"Счёт:",18,66,140,18);
            var scoreText:TextField=text(p,String(scores[side-1]),18,90,150,52);
            if(playing&&activeCue&&activeCue.kind==2&&previousScores[side-1]!=scores[side-1]&&!reducedMotion){
                scoreText.text=String(previousScores[side-1]);
                animations.push({sprite:scoreText,fromX:18,fromY:90,toX:18,toY:90,counter:scoreText,
                    fromValue:previousScores[side-1],toValue:scores[side-1],duration:BetaGwentBetaMotion.duration("POWER_UP"),
                    scaleCurve:scores[side-1]>previousScores[side-1]?"POWER_UP":"POWER_DOWN",
                    delay:cueImpactDelay()*animationTempo,remove:false});
            }
            text(p,"Раунды: "+crowns[side-1]+" / 2",18,156,172,18);
            for(var sealIndex:int=0;sealIndex<2;sealIndex++){
                var seal:Sprite=new Sprite();seal.mouseEnabled=false;seal.mouseChildren=false;p.addChild(seal);
                seal.x=34+sealIndex*29;seal.y=190;paintRoundSeal(seal,sealIndex<crowns[side-1],side==1?0x8BCFE6:0xE6AD86,10);
                if(activeCue&&activeCue.kind==6&&sealIndex>=previousCrowns[side-1]&&sealIndex<crowns[side-1]){
                    animations.push({sprite:seal,fromX:34+sealIndex*29,fromY:190,toX:34+sealIndex*29,toY:190,
                        fade:false,appear:true,remove:false,duration:480,delay:260,fromScaleX:2,fromScaleY:2,toScaleX:1,toScaleY:1});
                    seal.scaleX=seal.scaleY=2;seal.alpha=0;
                }
            }
            var pile:Sprite=new Sprite();pile.mouseEnabled=false;pile.mouseChildren=false;p.addChild(pile);
            pile.x=223;pile.y=244;paintCardBack(pile,25,23,side);
            paintArt(p,leaderIds[side-1],90,126,180,70);betaNine(p,-1412,94,130,178,68);
            editorSmallButton(p,"Сброс: "+graves[side-1]+((flags&(side==1?1:2))!=0?" · ПАС":"")+" · "+(side==1?"G":"H"),12,207,194,28,canInspectPile(),function():void{inspectPile(side,32);});
            if(side==1)editorSmallButton(p,"Колода: "+deckCounts[0]+" · D",12,242,194,27,canInspectPile(),function():void{inspectPile(1,16);});
            else text(p,"Колода: "+deckCounts[1]+" · скрыта",18,242,188,17).height=27;
            var available:Boolean=side==1?leaderOne:leaderTwo;
            if(side==1) button(available?leaderTitle:"Лидер использован",x,y+294,280,canAct()&&available,function():void{submitBoard("OnBetaGwentBoardLeader",[revision]);});
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
                    var betaWeather:Boolean=skin==3&&BetaGwentHDArt.has(BetaGwentWeather107.FROST_COVER);
                    if(!betaWeather){
                    var weather:Sprite=new Sprite();weather.x=geometry.x;weather.y=geometry.y;
                    weather.mouseEnabled=false;weather.mouseChildren=false;
                    weather.graphics.lineStyle(2,tint,.85);weather.graphics.beginFill(tint,.14);
                    weather.graphics.drawRect(0,0,geometry.w,geometry.h);weather.graphics.endFill();content.addChild(weather);
                    }
                    var title:String=hazard.token==1?"МОРОЗ":hazard.token==2?"ТУМАН":hazard.token==16?"ЖАРА":hazard.token==32?"РАГНАРЕК":hazard.token==64?"ШТОРМ":hazard.token==128?"ЗОЛОТАЯ ПЕНА":hazard.token==256?"ПОЛНАЯ ЛУНА":hazard.token==2048?"КРОВАВАЯ ЛУНА":hazard.token==512?"ВОЛЧЬЯ ЯМА":hazard.token==1024?"МЕЧТА ДРАКОНА":"ДОЖДЬ";
                    var suffix:String=hazard.token==256?" · +"+hazard.damage:hazard.token==512||hazard.token==2048?" · контакт −"+hazard.damage:hazard.token==1024?" · взрыв −"+hazard.damage:" · "+hazard.damage+(hazard.token==4?" × 2":"");
                    if(!betaWeather)text(content,title+suffix,geometry.x+8,geometry.y+2,geometry.w-16,13,tint);
                    if(!weatherBirths[key]||weatherBirths[key].token!=hazard.token)
                        weatherBirths[key]={token:hazard.token,start:getTimer()};
                    var particles:Sprite=new Sprite();particles.x=geometry.x;particles.y=geometry.y;
                    particles.mouseEnabled=false;particles.mouseChildren=false;
                    particles.scrollRect=new Rectangle(0,0,geometry.w,geometry.h);
                    weatherEffects.push({sprite:particles,w:geometry.w,h:geometry.h,token:hazard.token,
                        key:key,start:weatherBirths[key].start,phase:side*31+zone*19});
                    if(betaWeather)prepareBetaWeather(weatherEffects[weatherEffects.length-1]);
                    else if(hazard.token==1||hazard.token==2||hazard.token==4||hazard.token==64)prepareNativeWeather(weatherEffects[weatherEffects.length-1]);
                }
                if(focusedRow==zone&&focusedSide==side&&enabled){
                    hit.graphics.lineStyle(3,0xF5E6A7,.9);hit.graphics.drawRect(2,2,geometry.w-4,geometry.h-4);
                }
                attachRow(hit,side,zone,true);
                var total:int=0;
                for each(var c:Object in cards) if(c.side==side&&c.zone==zone&&(int(c.tokens)&8)==0) total+=c.power;
                var rowScore:Array=skin==3?BetaGwentBoardLayout.rowScore[side+":"+zone]:null;
                var rowTotal:TextField=text(content,String(total),skin==3?rowScore[0]+rowScore[2]/2-40:geometry.x-88,skin==3?rowScore[1]+rowScore[3]/2-24:geometry.y+24,skin==3?80:75,skin==3?76:26,0xFFFFFF);rowTotal.height=100;if(skin==3)rowTotal.filters=[new GlowFilter(0x000000,1,3,3,6)];
                if(skin==3&&!BetaGwentFonts.apply(rowTotal,BetaGwentFonts.NUMBERS,76,0xFFFFFF,true,"center")){rowTotal.defaultTextFormat=new TextFormat("$NormalFont",76,0xFFFFFF,true,null,null,null,null,"center");rowTotal.setTextFormat(rowTotal.defaultTextFormat);}
                if(skin==3)centerBetaNumber(rowTotal,rowScore[0]+rowScore[2]/2,rowScore[1]+rowScore[3]/2,76);
                if(skin==3 && playing && activeCue && activeCue.kind==2 && !reducedMotion){
                    var oldTotal:int=0;
                    for each(var previousUnit:Object in displayedCards)
                        if(previousUnit.side==side && previousUnit.zone==zone && (int(previousUnit.tokens)&8)==0)oldTotal+=previousUnit.power;
                    if(oldTotal!=total){
                        rowTotal.text=String(oldTotal);
                        animations.push({sprite:rowTotal,fromX:rowTotal.x,fromY:rowTotal.y,toX:rowTotal.x,toY:rowTotal.y,counter:rowTotal,
                            fromValue:oldTotal,toValue:total,numberX:rowScore[0]+rowScore[2]/2,numberY:rowScore[1]+rowScore[3]/2,numberSize:76,
                            duration:BetaGwentBetaMotion.duration("POWER_UP"),scaleCurve:total>oldTotal?"POWER_UP":"POWER_DOWN",delay:cueImpactDelay()*animationTempo});
                    }
                }
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
                    var rowTarget:Sprite=betaFrame(content,hit.x+hit.width-184,hit.y+hit.height-31,176,28,-1401);
                    rowTarget.mouseEnabled=false;rowTarget.mouseChildren=false;
                    text(rowTarget,isCaranthirChoice()?"МОРОЗ · без движения":"ВЫБРАТЬ РЯД",8,3,160,12,0xD5F6FF).height=25;
                    controller.registerControl(rowTarget,(side==1?"Ваш ":"Вражеский ")+(zone==1?"ближний ряд":zone==2?"дальний ряд":"осадный ряд"),action,null,null,"row",{rowOnly:true,side:side,zone:zone},new Rectangle(0,0,176,28));
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
            if(skin==3){
                // Beta: the summoned card is shown in the side preview; the plaque above the board
                // says where to put it (rows/allies are highlighted by the placement ghost).
                showBattleCard({templateId:c.templateId,title:c.title,power:c.power,side:1,zone:8,tokens:0,description:""},templateDetails[c.templateId]);
                return;
            }
            var p:Sprite=panel(content,skin==3?660:484,926,80,140,0x173340,.96);
            paintArt(p,c.templateId,74,134);
            p.graphics.lineStyle(2,c.tier==8?0xD9B557:c.tier==4?0xCBD1D8:0x99735D);p.graphics.drawRect(0,0,80,140);
            panel(p,3,3,34,34,0x101315,.85);text(p,String(c.power),7,2,40,28,powerColor(c));
            panel(p,3,104,74,33,0x101315,.84);
            var caption:TextField=text(p,c.title,7,106,68,12);caption.height=32;
            text(content,c.title+" · сила "+c.power,skin==3?752:586,932,skin==3?660:670,25,powerColor(c));
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
        private function handSortName():String
        {return ["Beta","сила","имя","добор"][handSortMode];}
        private function cycleHandSort():void
        {
            if(playing||dragId!=0)return;
            handSortMode=(handSortMode+1)%4;handSortReverse=handSortMode<2;
            refreshHandSorting();
        }
        private function reverseHandSort():void
        {
            if(playing||dragId!=0||handSortMode==3)return;
            handSortReverse=!handSortReverse;refreshHandSorting();
        }
        private function refreshHandSorting():void
        {
            var reopen:Boolean=controllerMenuOpen;if(reopen)closeControllerMenu();
            // Selection is an instance id, never a visual slot. Keep it while
            // rearranging the display; the authoritative hand is untouched.
            render();if(reopen)openControllerMenu();
        }
        private function isMulliganHand():Boolean
        {return requestId>0&&requestKind==1&&!pileChoice&&!templateChoice&&!handPowerChoice&&!graveyardChoice;}
        private function handMeta(c:Object):Object
        {return BetaGwentFullCatalog.find(int(c.templateId))||templateDetails[c.templateId]||cardDetails[c.id]||c;}
        private function compareBetaHand(a:Object,b:Object):Number
        {
            // Original CardSorter.DefaultHandSort: type, tier, template power,
            // template id, instance id. Direction is selected separately.
            var am:Object=handMeta(a),bm:Object=handMeta(b);
            var at:int=am.typeMask==4?3:am.tier==1?2:1,bt:int=bm.typeMask==4?3:bm.tier==1?2:1;
            if(at!=bt)return at-bt;
            if(int(am.tier)!=int(bm.tier))return int(am.tier)-int(bm.tier);
            var ap:int=am.power!=null?int(am.power):int(a.normalPower),bp:int=bm.power!=null?int(bm.power):int(b.normalPower);
            if(ap!=bp)return ap-bp;
            if(int(a.templateId)!=int(b.templateId))return int(a.templateId)-int(b.templateId);
            return int(a.id)-int(b.id);
        }
        private function compareHand(a:Object,b:Object):Number
        {
            if(handSortMode==3){var indexOrder:Number=int(a.index)-int(b.index);return indexOrder!=0?indexOrder:int(a.id)-int(b.id);}
            var order:Number=0;
            if(handSortMode==1){
                var am:Object=handMeta(a),bm:Object=handMeta(b);
                var ap:int=a.power!=null?int(a.power):int(am.power),bp:int=b.power!=null?int(b.power):int(bm.power);
                order=ap-bp;
            }else if(handSortMode==2){
                var an:String=String(a.title||handMeta(a).title||"").toLocaleLowerCase();
                var bn:String=String(b.title||handMeta(b).title||"").toLocaleLowerCase();
                order=an<bn?-1:an>bn?1:0;
            }
            if(order==0)order=compareBetaHand(a,b);
            return handSortReverse?-order:order;
        }
        private function sortedHand(values:Array):Array
        {var sorted:Array=values.concat();sorted.sort(compareHand);return sorted;}
        private function drawCards():void
        {
            var nextCards:Object={};
            var handCount:int=0;
            for each(var hand:Object in cards) if(hand.side==1&&hand.zone==8)handCount++;
            // Beta hand is a flat, evenly spaced row; slot by rank so index gaps never leave holes.
            var handSlots:Array=[];for each(var handCard:Object in cards) if(handCard.side==1&&handCard.zone==8)handSlots.push(handCard);
            handSlots=sortedHand(handSlots);var handRank:Object={};for(var hr:int=0;hr<handSlots.length;hr++)handRank[handSlots[hr].id]=hr;
            var handArea:Array=skin==3?BetaGwentBoardLayout.hand["1"]:null;
            var handLeft:Number=skin==3?handArea[0]:484;
            var handWidth:Number=skin==3?104:Math.min(112,970/Math.max(1,handCount))-8;
            var step:Number=skin==3?(handCount>1?Math.min(108,(handArea[2]-handWidth)/(handCount-1)):0):handWidth+8;
            if(skin==3)handLeft+=(handArea[2]-(handWidth+step*Math.max(0,handCount-1)))/2;
            for each(var c:Object in cards)
            {
                if(c.zone==8&&(c.side!=1||canPlacePending())) continue;
                if(c.zone!=8&&c.zone!=1&&c.zone!=2&&c.zone!=4) continue;
                var isHand:Boolean=c.zone==8;
                if(consumedVisualIds[c.id]&&!(activeCue&&activeCue.kind==11&&activeCue.target==c.id))continue;
                var handAngle:Number=0;var slot:int=isHand&&handRank[c.id]!=null?int(handRank[c.id]):int(c.index);
                var g:Object=isHand?{x:handLeft+slot*step,y:(skin==3?(selected==c.id?926:944):(selected==c.id?900:920))-Math.abs(handAngle)*1.5,h:skin==3?Math.round(104/BETA_CARD_ASPECT):140}:rowGeometry(c.side,c.zone);
                var layout:Object=isHand?null:rowLayout(c.side,c.zone);
                var x:Number=isHand?g.x:layout.x+c.index*layout.step;
                var cardWidth:Number=isHand?handWidth:layout.w;var cardHeight:Number=isHand?g.h:g.h-8;
                var p:Sprite=panel(content,x,g.y+4,cardWidth,cardHeight,0x171714,.96);
                p.rotation=handAngle;
                cardSprites[c.id]=p;
                if(isHand&&dragging&&c.id==dragId)p.alpha=.3;
                
                var concealed:Boolean=!isHand&&(int(c.tokens)&8)!=0;
                if(concealed)paintCardBack(p,cardWidth,cardHeight,c.side);else if(skin==3)paintBetaFace(p,c.templateId,cardWidth,cardHeight,c.side);else paintArt(p,c.templateId,cardWidth-6,cardHeight-6);
                var before:Object=displayedCards[c.id];
                nextCards[c.id]={x:p.x,y:p.y,rotation:handAngle,power:c.power,normalPower:c.normalPower,zone:c.zone,side:c.side,title:c.title,armor:c.armor,templateId:c.templateId,timer:c.timer,tokens:c.tokens,width:cardWidth,height:cardHeight,delta:before?c.power-before.power:0,armorDelta:before?c.armor-before.armor:0};
                var revealed:Boolean=before&&(int(before.tokens)&8)!=0&&!concealed&&!isHand;
                if(before && before.templateId==c.templateId&&!revealed) {
                    if(before.x!=p.x || before.y!=p.y || before.rotation!=handAngle) {
                        var flight:Boolean=before.zone==8&&!isHand;
                        animations.push({sprite:p,fromX:before.x,fromY:before.y,toX:p.x,toY:p.y,fade:false,remove:false,
                            duration:flight?600:isHand?160:280,arc:flight?36:0,betaFlight:flight,staged:flight,stageX:skin==3?BetaGwentBoardLayout.presentation[String(c.side)][0]:860,stageY:skin==3?BetaGwentBoardLayout.presentation[String(c.side)][1]:380,stageScaleX:(skin==3?BetaGwentBoardLayout.presentation[String(c.side)][2]:160)/cardWidth,stageScaleY:(skin==3?BetaGwentBoardLayout.presentation[String(c.side)][3]:225)/cardHeight,settle:false,tilt:flight?(p.x>before.x?5:-5):0,
                            fromRotation:before.rotation!=null?before.rotation:0,toRotation:handAngle,
                            fromScaleX:flight?before.width/cardWidth:1,fromScaleY:flight?before.height/cardHeight:1,toScaleX:1,toScaleY:1});
                        p.x=before.x;p.y=before.y;
                        if(flight){p.scaleX=before.width/cardWidth;p.scaleY=before.height/cardHeight;}
                    }
                    if(before.power!=c.power || before.armor!=c.armor) {
                        var hitDelay:Number=activeCue&&activeCue.kind==2?cueImpactDelay()*animationTempo:0;
                        var flash:Sprite=new Sprite();flash.mouseEnabled=false;
                        var flashTint:uint=c.power>before.power?0x71C496:c.power<before.power?0xDF705E:0x83C5E5;
                        var flashMatrix:Matrix=new Matrix();flashMatrix.createGradientBox(cardWidth,cardHeight,Math.PI/2);
                        flash.graphics.beginGradientFill(GradientType.LINEAR,[flashTint,flashTint,flashTint],[0,.32,0],[0,128,255],flashMatrix);
                        flash.graphics.drawRect(0,0,cardWidth,cardHeight);flash.graphics.endFill();
                        p.addChild(flash);
                        animations.push({sprite:flash,fromX:0,fromY:0,toX:0,toY:0,fade:true,remove:true,duration:220,delay:hitDelay,hideBeforeDelay:true});
                        var delta:int=c.power-before.power;var armorDelta:int=c.armor-before.armor;
                        var label:String=delta!=0?(delta>0?"+":"")+delta:"";
                        if(armorDelta!=0)label+=(label?" · ":"")+"Б "+(armorDelta>0?"+":"")+armorDelta;
                        var number:Sprite=new Sprite();number.mouseEnabled=false;number.mouseChildren=false;
                        var numberWidth:Number=Math.max(cardWidth,120);
                        betaLabel(number,label,-numberWidth/2,0,numberWidth,20,delta>0?0xA5F5B8:delta<0?0xFFB09B:0xBCEAFF,BetaGwentFonts.BODY,false,"center");
                        p.addChild(number);number.x=cardWidth/2;number.y=-8;
                        animations.push({sprite:number,fromX:cardWidth/2,fromY:-8,toX:cardWidth/2,toY:-38,fade:true,remove:true,duration:420,delay:hitDelay,hideBeforeDelay:true});
                        if((delta<0||armorDelta<0)&&!isHand&&!reducedMotion&&before.x==x&&before.y==g.y+4)
                            animations.push({sprite:p,fromX:x,fromY:g.y+4,toX:x,toY:g.y+4,shake:armorDelta<0&&delta==0?2:3,remove:false,duration:180,delay:hitDelay});
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
                    if(isHand&&activeCue&&activeCue.kind==14){originX=skin==3?betaDeckPoint(1)[0]:310;originY=skin==3?betaDeckPoint(1)[1]:776;}
                    if(!isHand){
                        var summoner:Object=activeCue?(displayedCards[activeCue.source]?displayedCards[activeCue.source]:previousPoses[activeCue.source]?previousPoses[activeCue.source]:departedPoses[activeCue.source]):null;
                        if(activeCue&&(activeCue.kind==15||activeCue.title.indexOf("Из колоды")>=0)){originX=skin==3?betaDeckPoint(c.side)[0]:310;originY=skin==3?betaDeckPoint(c.side)[1]:(c.side==1?776:426);}
                        else if(summoner&&activeCue.source!=c.id){originX=summoner.x;originY=summoner.y;}
                        else if(c.side==2){originX=skin==3?1039-23:630+Math.min(9,enemyHand)*54;originY=skin==3?24:96;}
                        else{originX=330;originY=730;}
                    }
                    animations.push({sprite:p,fromX:originX,fromY:originY,toX:p.x,toY:p.y,fade:false,remove:false,appear:true,
                        duration:isHand?260:480,arc:isHand?0:36,betaFlight:true,settle:!isHand,tilt:originX<p.x?5:-5,fromRotation:0,toRotation:handAngle,fromScaleX:.8,fromScaleY:.8,toScaleX:1,toScaleY:1});
                    p.x=originX;p.y=originY;p.alpha=0;
                }
                var detail:Object=cardDetails[c.id];
                if(detail){p.graphics.lineStyle(2,detail.tier==8?0xD9B557:detail.tier==4?0xCBD1D8:0x99735D);p.graphics.drawRect(1,1,cardWidth-2,cardHeight-2);}
                if(selected==c.id){p.graphics.lineStyle(3,0x80CBD5);p.graphics.drawRect(1.5,1.5,cardWidth-3,cardHeight-3);paintBetaCorners(p,cardWidth,cardHeight,0xC7FFF5);}
                else if(keyboardFocusId==c.id){p.graphics.lineStyle(4,0xF5E6A7);p.graphics.drawRect(2,2,cardWidth-4,cardHeight-4);}
                // Overlapping hand (original fan): the chosen card and its frame stay on top.
                if(isHand&&(selected==c.id||keyboardFocusId==c.id))content.addChild(p);
                if(isHand&&skin!=3){var band:Sprite=panel(p,3,cardHeight-36,cardWidth-6,33,0x101315,.84);band.mouseEnabled=false;}
                if(skin!=3){var badge:Sprite=panel(p,3,3,34,34,0x101315,.85);badge.mouseEnabled=false;}
                var powerValue:String=concealed?"?":c.power>0||!isHand?String(c.power):(skin==3?"":"★");
                var powerBadge:TextField=skin==3&&!concealed?betaPowerField(p,powerValue,cardWidth,cardHeight,powerColor(c)):text(p,powerValue,7,2,40,isHand?28:25,concealed?0xE9C46A:powerColor(c));
                if(before&&!concealed&&before.power!=c.power&&activeCue&&activeCue.kind==2&&!reducedMotion){
                    powerBadge.text=String(before.power);powerBadge.textColor=powerColor(before);
                    pendingImpacts.push({field:powerBadge,value:powerValue,tint:powerColor(c)});
                    animations.push({sprite:powerBadge,fromX:powerBadge.x,fromY:powerBadge.y,toX:powerBadge.x,toY:powerBadge.y,
                        scaleCurve:c.power>before.power?"POWER_UP":"POWER_DOWN",duration:BetaGwentBetaMotion.duration("POWER_UP"),delay:cueImpactDelay()*animationTempo});
                }
                if(isHand&&skin!=3){var caption:TextField=text(p,c.title,7,cardHeight-34,cardWidth-12,13);caption.height=32;}
                if(concealed){
                    var ambushBadge:Sprite=panel(p,2,cardHeight*.42,cardWidth-4,19,0x101315,.97);ambushBadge.mouseEnabled=false;ambushBadge.mouseChildren=false;
                    text(ambushBadge,"ЗАСАДА",3,1,cardWidth-8,12,0xF5D77F).height=17;
                }else if(!isHand&&isAmbush(c.templateId))text(p,"РАСКРЫТА",3,cardHeight*.42,cardWidth-6,11,0xA5F5B8).height=18;
                if(c.armor>0||before&&before.armor>0&&activeCue&&activeCue.kind==2&&!reducedMotion) {
                    var armorBadge:Sprite=new Sprite();p.addChild(armorBadge);armorBadge.mouseEnabled=false;paintArt(armorBadge,BetaGwentHud104.SHIELD,30,33,cardWidth-33,2);
                    var armorValue:TextField=betaLabel(p,c.armor>0?String(c.armor):"",cardWidth-33,2,30,26,0xFFF0CA,BetaGwentFonts.NUMBERS,false,"center");
                    armorValue.height=33;centerBetaNumber(armorValue,cardWidth-18,16,26);
                    if(before&&before.armor!=c.armor&&activeCue&&activeCue.kind==2&&!reducedMotion){
                        armorValue.text=before.armor>0?String(before.armor):"";
                        centerBetaNumber(armorValue,cardWidth-18,16,26);
                        pendingImpacts.push({field:armorValue,value:c.armor>0?String(c.armor):"",tint:0xFFF0CA,numberX:cardWidth-18,numberY:16,numberSize:26});
                        var armorDelay:Number=cueImpactDelay()*animationTempo;
                        animations.push({sprite:armorValue,fromX:armorValue.x,fromY:armorValue.y,toX:armorValue.x,toY:armorValue.y,
                            scaleCurve:c.armor>before.armor?"POWER_UP":"POWER_DOWN",numberX:cardWidth-18,numberY:16,numberSize:26,
                            duration:BetaGwentBetaMotion.duration("POWER_UP"),delay:armorDelay});
                        if(before.armor==0)animations.push({sprite:armorBadge,fromX:0,fromY:0,toX:0,toY:0,appear:true,duration:140,delay:armorDelay,hideBeforeDelay:true});
                        if(c.armor==0)animations.push({sprite:armorBadge,fromX:0,fromY:0,toX:0,toY:0,fade:true,remove:true,duration:180,delay:armorDelay});
                        if(c.armor<before.armor)drawArmorHit(p,cardWidth,c.armor,armorDelay);
                    }
                }
                if((int(c.tokens)&4)!=0)paintLock(p,cardWidth-25,31);
                if((int(c.tokens)&1)!=0)paintResilience(p,cardWidth,cardHeight);
                if((int(c.tokens)&512)!=0){
                    var doomedBadge:Sprite=panel(p,3,39,20,19,0x271715,.9);doomedBadge.mouseEnabled=false;
                    text(p,"×",6,38,18,18,0xF2AC86);
                }
                if(int(c.timer)>=0)paintTimer(p,3,40,int(c.timer),(int(c.tokens)&4)!=0);
                // Markers: hand card revealed to the opponent (eye) and spies (ribbon on the bottom edge).
                if(isHand&&(int(c.tokens)&64)!=0)paintRevealedMark(p,cardWidth-15,cardHeight-15);
                if(!concealed&&isSpyCard(c.templateId))paintSpyRibbon(p,cardWidth,cardHeight);
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
                var fading:Sprite=panel(content,previous.x,previous.y,previous.width,previous.height,0x171714,.9);
                fading.mouseEnabled=false;fading.mouseChildren=false;
                paintArt(fading,previous.templateId,previous.width-6,previous.height-6);
                // Preserve the actual portrait size during removal as during placement.
                text(fading,String(previous.power),8,4,68,26,powerColor(previous));
                
                var vanishes:Boolean=(int(previous.tokens)&512)!=0;
                betaBurst(content,-104,previous.x+40,previous.y+40,110,vanishes?0xB8B7DC:0xB7A69B,40,410);
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
            // Overlapping hand: stack left to right by slot, the chosen/focused card stays on top.
            for(var zi:int=0;zi<handSlots.length;zi++){var hs:Sprite=cardSprites[handSlots[zi].id] as Sprite;if(hs&&hs.parent==content&&handSlots[zi].id!=selected&&handSlots[zi].id!=keyboardFocusId)content.addChild(hs);}
            for each(var topId:int in [keyboardFocusId,selected]){var ts:Sprite=cardSprites[topId] as Sprite;if(ts&&ts.parent==content&&handRank[topId]!=null)content.addChild(ts);}
            displayedCards=nextCards;
            if(skin!=3)text(content,canPlacePending()?"Нажмите союзника: поставить перед ним. Пустое место своего ряда: поставить в конец.":rowRequest&&requestId>0?(leaderRow?"Выберите свой подсвеченный ряд для лидера.":"Выберите любой подсвеченный ряд."):requestId>0 && requestKind==2?"Нажмите подсвеченную карту, чтобы применить способность.":
                selected==0?"":canPlaceSelected()?"Нажмите свой отряд: поставить перед ним. Пустое место ряда: поставить в конец.":playRules[selected]&&playRules[selected].kind==1?"Нажмите подходящий отряд или перетащите особую карту прямо на него.":playRules[selected]&&playRules[selected].kind==2?"Нажмите подходящий ряд или перетащите особую карту прямо в ряд.":"Выберите свой ряд для выбранной карты",485,878,970,18);
        }
        private function animateCards(e:Event):void
        {try{animateCardsBody(e);}catch(frameError:Error){reportUIError("animateCards",frameError);}}
        private function animateCardsBody(e:Event):void
        {
            updateAimPreview();updateActionPreview();
            var now:int=getTimer();
            if(hoverPreviewAt>0&&now>=hoverPreviewAt){hoverPreviewAt=0;showHoverPreview();}
            for each(var pulse:Object in targetPulses)pulse.sprite.alpha=reducedMotion?pulse.base:pulse.base+.07*Math.sin(now*.004+pulse.phase);
            var placementProgress:Number=reducedMotion?1:Math.min(1,(now-placementGhostAt)/160);
            placementProgress=1-Math.pow(1-placementProgress,3);
            for each(var placementMotion:Object in placementMotions){
                placementMotion.sprite.x=placementMotion.fromX+(placementMotion.toX-placementMotion.fromX)*placementProgress;
                placementMotion.sprite.y=placementMotion.fromY+(placementMotion.toY-placementMotion.fromY)*placementProgress;
                if(placementMotion.ghost)placementMotion.sprite.alpha=.35+.2*placementProgress;
            }
            var complete:Boolean=true;var elapsed:Number=getTimer()-animationStarted;
            for(var impactIndex:int=pendingImpacts.length-1;impactIndex>=0;impactIndex--){
                var pending:Object=pendingImpacts[impactIndex];
                if(elapsed<cueImpactDelay())continue;
                pending.field.text=pending.value;pending.field.textColor=pending.tint;
                if(pending.numberSize)centerBetaNumber(pending.field,pending.numberX,pending.numberY,pending.numberSize);
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
                // Flight is a 2D adaptation; landing and preview use baked Beta curves.
                if(motion.betaFlight)eased=progress*progress*progress*(progress*(progress*6-15)+10);
                if(motion.curve)eased=BetaGwentBetaMotion.sample(motion.curve,progress);
                var sprite:Object=motion.sprite;
                // Capture one baseline per motion. Never multiply last frame's
                // scale: that made no-scale flights grow with the frame rate.
                if(motion.baseScaleX==null){motion.baseScaleX=sprite.scaleX;motion.baseScaleY=sprite.scaleY;motion.baseRotation=sprite.rotation;}
                sprite.x=motion.fromX+(motion.toX-motion.fromX)*eased;
                sprite.y=motion.fromY+(motion.toY-motion.fromY)*eased;
                if(motion.shake&&!reducedMotion)sprite.x+=Math.sin(progress*Math.PI*6)*motion.shake*(1-progress);
                if(motion.arc&&!reducedMotion)sprite.y-=Math.sin(Math.PI*progress)*motion.arc;
                var scaleX:Number=motion.fromScaleX!=null?motion.fromScaleX+(motion.toScaleX-motion.fromScaleX)*eased:motion.baseScaleX;
                var scaleY:Number=motion.fromScaleY!=null?motion.fromScaleY+(motion.toScaleY-motion.fromScaleY)*eased:motion.baseScaleY;
                if(motion.staged&&!reducedMotion){
                    var flightEnd:Number=Math.max(.25,1-BetaGwentBetaMotion.duration("LAND")/(motion.duration||700));
                    var landing:Boolean=progress>=flightEnd;
                    var stageProgress:Number=landing?(progress-flightEnd)/(1-flightEnd):progress/flightEnd;
                    var stageEase:Number=landing?BetaGwentBetaMotion.sample("LAND",stageProgress):1-Math.pow(1-stageProgress,3);
                    sprite.x=(landing?motion.stageX:motion.fromX)+((landing?motion.toX:motion.stageX)-(landing?motion.stageX:motion.fromX))*stageEase;
                    sprite.y=(landing?motion.stageY:motion.fromY)+((landing?motion.toY:motion.stageY)-(landing?motion.stageY:motion.fromY))*stageEase;
                    scaleX=(landing?motion.stageScaleX:motion.fromScaleX)+((landing?1:motion.stageScaleX)-(landing?motion.stageScaleX:motion.fromScaleX))*stageEase;
                    scaleY=(landing?motion.stageScaleY:motion.fromScaleY)+((landing?1:motion.stageScaleY)-(landing?motion.stageScaleY:motion.fromScaleY))*stageEase;
                }
                if(motion.scaleCurve&&!reducedMotion){var nativePulse:Number=BetaGwentBetaMotion.sample(motion.scaleCurve,progress);scaleX*=nativePulse;scaleY*=nativePulse;}
                if(motion.counter){
                    var counter:TextField=motion.counter;
                    counter.text=String(Math.round(motion.fromValue+(motion.toValue-motion.fromValue)*eased));
                }
                var angle:Number=motion.fromRotation!=null?motion.fromRotation+(motion.toRotation-motion.fromRotation)*eased:motion.baseRotation;
                if(motion.betaFlight&&!reducedMotion){
                    angle+=Math.sin(Math.PI*progress)*(motion.tilt!=null?motion.tilt:4);
                    var lift:Number=1+.055*Math.sin(Math.PI*progress);
                    scaleX*=lift;scaleY*=lift;
                    if(motion.settle&&progress>.82){
                        var landingWave:Number=Math.sin((progress-.82)/.18*Math.PI);
                        sprite.y+=landingWave*3;scaleX*=1+.025*landingWave;scaleY*=1-.035*landingWave;
                    }
                }
                if(motion.hitFrames){
                    var cell:int=Math.min(motion.hitFrames.length-1,int(progress*motion.hitFrames.length));
                    for(var frameIndex:int=0;frameIndex<motion.hitFrames.length;frameIndex++)
                        motion.hitFrames[frameIndex].visible=frameIndex==cell;
                }
                if(motion.coinFaces){
                    scaleX=Math.max(.03,Math.abs(Math.cos(progress*Math.PI)));
                    motion.coinFaces[0].visible=progress<.5;motion.coinFaces[1].visible=progress>=.5;
                }
                // A numeric pulse uses the glyph center as its pivot. Ordinary
                // card movement still uses the card's layout/flight coordinates.
                if(motion.numberSize && sprite is TextField){
                    centerBetaNumber(sprite as TextField,motion.numberX,motion.numberY,motion.numberSize);
                    sprite.x=motion.numberX-(motion.numberX-sprite.x)*scaleX;
                    sprite.y=motion.numberY-(motion.numberY-sprite.y)*scaleY;
                }else if(motion.scaleCurve && sprite is TextField){
                    sprite.x+=(sprite.width/sprite.scaleX)*(motion.baseScaleX-scaleX)/2;
                    sprite.y+=(sprite.height/sprite.scaleY)*(motion.baseScaleY-scaleY)/2;
                }
                sprite.scaleX=scaleX;sprite.scaleY=scaleY;sprite.rotation=angle;
                if(motion.fade)sprite.alpha=(motion.fromAlpha!=null?motion.fromAlpha:1)*(1-progress);
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
        private function cueMinimumDuration(kind:int):Number
        {
            switch(kind){
                case 1:return 700;case 2:return 930;case 3:return 460;
                case 4:return 120+1000*Math.max(BetaGwentVisualTimings.FROST_INTRO,BetaGwentVisualTimings.FOG_INTRO,BetaGwentVisualTimings.RAIN_INTRO);case 5:return 380;case 6:return 1050;
                case 7:return 120+1000*Math.max(BetaGwentVisualTimings.FROST_INTRO,BetaGwentVisualTimings.FOG_INTRO,BetaGwentVisualTimings.RAIN_INTRO);case 8:return 440;case 9:return 460;
                case 10:return 560;case 11:return 520;case 12:return 460;
                case 13:return 520;case 14:return 420;case 15:case 16:return 620;
                case 17:return 750;
            }
            return 120;
        }
        private function cueImpactDelay():Number
        {
            if(reducedMotion||!activeCue)return 0;
            var delay:Number=activeCue.kind==1?400:activeCue.kind==2?180:activeCue.kind==10?200:activeCue.kind==15||activeCue.kind==16?160:0;
            return Math.min(delay/animationTempo,Math.max(0,frameDuration-90/animationTempo));
        }
        private function poseW(p:Object):Number{return p&&p.width>0?Number(p.width):80;}
        private function poseH(p:Object):Number{return p&&p.height>0?Number(p.height):84;}
        private function poseX(p:Object):Number{return p.x+poseW(p)/2;}
        private function poseY(p:Object):Number{return p.y+poseH(p)/2;}
        // Arrow that leaves the acting card's edge and stops at the target's edge, so the source is unambiguous.
        private function drawCueArrow(fx:Sprite,ax:Number,ay:Number,aw:Number,ah:Number,bx:Number,by:Number,bw:Number,bh:Number,tint:uint):void
        {
            var scx:Number=ax+aw/2,scy:Number=ay+ah/2,tcx:Number=bx+bw/2,tcy:Number=by+bh/2;
            var dx:Number=tcx-scx,dy:Number=tcy-scy,len:Number=Math.sqrt(dx*dx+dy*dy);if(len<1)return;dx/=len;dy/=len;
            var ts:Number=Math.min(dx!=0?(aw/2+6)/Math.abs(dx):1e9,dy!=0?(ah/2+6)/Math.abs(dy):1e9);
            var te:Number=Math.min(dx!=0?(bw/2+8)/Math.abs(dx):1e9,dy!=0?(bh/2+8)/Math.abs(dy):1e9);
            var x0:Number=scx+dx*ts,y0:Number=scy+dy*ts,x1:Number=tcx-dx*te,y1:Number=tcy-dy*te;
            if((x1-x0)*dx+(y1-y0)*dy<30){x0=scx;y0=scy;}
            var head:Number=Math.min(30,Math.max(12,len*.15)),hx:Number=x1-dx*head,hy:Number=y1-dy*head;
            var g:Graphics=fx.graphics;
            g.lineStyle(2,0x073354,.9);g.beginFill(tint,.94);
            g.moveTo(x0-dy*5,y0+dx*5);g.lineTo(hx-dy*10,hy+dx*10);
            g.lineTo(hx-dy*22,hy+dx*22);g.lineTo(x1,y1);g.lineTo(hx+dy*22,hy-dx*22);
            g.lineTo(hx+dy*10,hy-dx*10);g.lineTo(x0+dy*5,y0-dx*5);g.lineTo(x0-dy*5,y0+dx*5);g.endFill();
            g.lineStyle(2,0xB7EEFF,.8);g.moveTo(x0,y0);g.lineTo(hx,hy);g.lineStyle();
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
            var sx:Number=origin?poseX(origin):960;var sy:Number=origin?poseY(origin):430;
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
                    // Make the acting card obvious (turn-end / timer triggers have no hand play).
                    var actor:Sprite=new Sprite();actor.mouseEnabled=false;fx.addChild(actor);
                    actor.graphics.lineStyle(4,0xFFE08A,1);actor.graphics.drawRect(origin.x-4,origin.y-4,poseW(origin)+8,poseH(origin)+8);
                    actor.filters=[new GlowFilter(0xFFC24A,.95,22,22,3,2)];
                    if(activeCue.title){
                        var tag:TextField=betaLabel(fx,activeCue.title,origin.x+poseW(origin)/2-150,Math.max(4,origin.y-30),300,15,0xFFF1C8,BetaGwentFonts.BODY,false,"center");
                        tag.filters=[new GlowFilter(0x000000,1,6,6,4,2)];
                    }
                }
                if(activeCue.source==0&&activeCue.row>0){
                    var weather:Object=rowGeometry(activeCue.side,activeCue.row);
                    sx=weather.x+weather.w/2;sy=weather.y+weather.h/2;
                }
                var hits:Array=[];
                if(activeCue.kind==2){
                    if(int(activeCue.attackCount)>1){for(var hitKey:String in displayedCards){var hitPose:Object=displayedCards[hitKey];if(hitPose&&(int(hitPose.delta)!=0||int(hitPose.armorDelta)!=0))hits.push(hitPose);}}
                    if(hits.length==0&&target)hits.push(target);
                }
                for each(target in hits){
                    var hurting:Boolean=int(target.delta)<0||int(target.armorDelta)<0;
                    var weatherHit:Boolean=activeCue.source==0&&activeCue.row>0;
                    tint=hurting?0xEE8B70:int(target.delta)>0?0x8FE0AE:0xA7DCEE;
                    var tx:Number=target.x+target.width/2;var ty:Number=target.y+target.height/2;
                    // A self-trigger has no incoming projectile. Selection arrows
                    // belong to aiming; resolving actions use a short, soft link.
                    var incoming:Boolean=origin&&origin!=target;
                    var impactDelay:Number=cueImpactDelay()*animationTempo;
                    if(incoming&&!weatherHit){
                        var link:Sprite=new Sprite();link.mouseEnabled=false;link.mouseChildren=false;fx.addChild(link);
                        link.graphics.lineStyle(1.5,tint,.38);link.graphics.moveTo(sx,sy);link.graphics.lineTo(tx,ty);
                        animations.push({sprite:link,fromX:0,fromY:0,toX:0,toY:0,fade:true,remove:true,duration:impactDelay+200});
                    }
                    if(!reducedMotion){
                        if(weatherHit)drawWeatherImpact(fx,target,impactDelay);
                        else if(hurting){
                            drawBetaHit(fx,tx,ty,Math.max(60,poseW(target)*1.2),0xFFD5C1,impactDelay);
                            if(incoming)drawDamageProjectile(fx,sx,sy,tx,ty,tint,impactDelay);
                        }else{
                            // Boost and armour are one arrival on the same card,
                            // rather than separate strength/armour projectiles.
                            betaBurst(fx,-103,tx,ty,poseW(target)*1.2,tint,impactDelay,360);
                            var aura:Sprite=betaVisual(-106,poseH(target)*.8,poseW(target)*.55,tint);
                            if(aura){
                                fx.addChild(aura);aura.x=tx;aura.y=ty+12;aura.rotation=-90;
                                animations.push({sprite:aura,fromX:tx,fromY:ty+12,toX:tx,toY:ty-18,fade:true,remove:true,duration:440,
                                    delay:impactDelay,hideBeforeDelay:true,fromScaleX:.8,fromScaleY:.6,toScaleX:1,toScaleY:1});
                            }
                        }
                    }
                }
            }
            if(activeCue.kind==1&&origin&&!reducedMotion){
                var definition:Object=cardDetails[activeCue.source];
                var landingTint:uint=definition&&definition.tier==8?0xE9C46A:definition&&definition.tier==4?0xDDE8F1:0xACD9E2;
                betaBurst(fx,definition&&definition.tier==8?-105:-103,poseX(origin),poseY(origin),100,landingTint,cueImpactDelay()*animationTempo,270);
                var landing:Sprite=new Sprite();landing.mouseEnabled=false;landing.mouseChildren=false;fx.addChild(landing);
                landing.x=poseX(origin);landing.y=poseY(origin);
                landing.graphics.lineStyle(3,landingTint,.85);landing.graphics.drawEllipse(-40,-28,80,56);
                for(var landingRay:int=0;landingRay<8;landingRay++){
                    var theta:Number=landingRay*Math.PI/4;
                    landing.graphics.moveTo(Math.cos(theta)*35,Math.sin(theta)*24);
                    landing.graphics.lineTo(Math.cos(theta)*48,Math.sin(theta)*35);
                }
                animations.push({sprite:landing,fromX:landing.x,fromY:landing.y,toX:landing.x,toY:landing.y,fade:true,remove:true,duration:200,
                    delay:cueImpactDelay()*animationTempo,hideBeforeDelay:true,fromScaleX:.7,fromScaleY:.7,toScaleX:1.25,toScaleY:1.25});
            }
            if(activeCue.kind==11)drawConsumeCue(fx,origin);
            if(activeCue.kind==8&&target&&(activeCue.row==0)&&!reducedMotion){
                var resilient:Sprite=new Sprite();resilient.mouseEnabled=false;resilient.mouseChildren=false;fx.addChild(resilient);
                resilient.x=poseX(target)-18;resilient.y=target.y+poseH(target)*.6;
                paintArt(resilient,-1890,36,38);
                animations.push({sprite:resilient,fromX:resilient.x,fromY:resilient.y,toX:resilient.x,toY:resilient.y-18,fade:true,remove:true,duration:420});
            }
            if(activeCue.kind==15||activeCue.kind==16)drawSummonCue(fx,origin,target);
            if(activeCue.kind==9&&target){
                var locked:Boolean=false;
                for each(var affected:Object in cards)if(affected.id==activeCue.target)locked=(int(affected.tokens)&4)!=0;
                var seal:Sprite=new Sprite();seal.mouseEnabled=false;seal.mouseChildren=false;fx.addChild(seal);
                seal.x=poseX(target)-12;seal.y=poseY(target)-24;paintLock(seal,0,0);
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
                    omen.x=poseX(departed);omen.y=poseY(departed);
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
            // Beta weather's native entry layers already animate in drawRows.
            // A second rectangle/sweep here caused a visible double cast.
            if(activeCue.kind==4&&activeCue.row>0&&skin!=3){
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
                var seat:Array=skin==3?betaLeaderRect(activeCue.side):null;
                var y:Number=skin==3?seat[1]:(activeCue.side==1?575:225);
                fx.graphics.lineStyle(4,0xCFB176,.95);fx.graphics.drawRoundRect(skin==3?seat[0]-2:98,y-2,skin==3?seat[2]+4:284,skin==3?seat[3]+4:229,8,8);
            }
            if(activeCue.kind==6)drawRoundBanner(fx,true);
            else if(activeCue.kind==7&&skin!=3){
                var startBanner:Sprite=panel(fx,650,396,650,148,0x101619,.97);
                text(startBanner,"РАУНД "+round,24,16,600,32,0xE9C46A);
                text(startBanner,current==1?"Ваш ход":"Ход соперника",24,66,600,26);
                text(startBanner,"Победы: "+crowns[0]+" : "+crowns[1],24,108,600,18,0xC8C7BB);
                animations.push({sprite:startBanner,fromX:650,fromY:420,toX:650,toY:396,appear:true,remove:false,duration:400});
                startBanner.y=420;startBanner.alpha=0;
            }else if(skin!=3){
                var strip:Sprite=panel(fx,610,160,820,46,0x101619,.94);
                var caption:String=activeCue.title;
                if(activeCue.sequenceSize>1)caption+="  ·  изменение "+activeCue.sequence+" / "+activeCue.sequenceSize;
                text(strip,caption,14,5,790,20,0xE9DBBE);
            }
        }
        private function paintRoundSeal(parent:Sprite,filled:Boolean,color:uint,r:Number):void
        {
            if(skin==3&&paintArt(parent,filled?(color==0xE9AB85?-1527:-1525):-1523,r*3,r*2.65,-r*1.5,-r*1.325))return;
            parent.graphics.lineStyle(2,filled?color:0x7A766C,.95);
            parent.graphics.beginFill(filled?color:0x20282D,filled?0.85:0.9);
            parent.graphics.moveTo(0,-r);parent.graphics.lineTo(r,0);parent.graphics.lineTo(0,r);parent.graphics.lineTo(-r,0);parent.graphics.lineTo(0,-r);parent.graphics.endFill();
            if(filled){parent.graphics.lineStyle(2,0xFFF0BA,.9);parent.graphics.moveTo(-r*.35,0);parent.graphics.lineTo(-r*.05,r*.3);parent.graphics.lineTo(r*.45,-r*.3);}
        }
        private function drawRoundBanner(parent:Sprite,animate:Boolean):void
        {
            if(skin==3){drawBetaRoundBanner(parent,animate);return;}
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
            betaBurst(fx,-108,x,y,130,tint,140,390);
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
                fx.graphics.lineStyle(2,tint,.55);fx.graphics.moveTo(poseX(source),poseY(source));fx.graphics.lineTo(x,y);
                fx.graphics.lineStyle(3,tint,.9);fx.graphics.drawRect(source.x-2,source.y-2,poseW(source)+4,poseH(source)+4);
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
        private function drawDamageProjectile(fx:Sprite,sx:Number,sy:Number,tx:Number,ty:Number,tint:uint,delay:Number):void
        {
            var bolt:Sprite=betaVisual(-106,48,14,tint);if(!bolt)return;
            fx.addChild(bolt);bolt.x=sx;bolt.y=sy;
            var angle:Number=Math.atan2(ty-sy,tx-sx)*180/Math.PI;
            animations.push({sprite:bolt,fromX:sx,fromY:sy,toX:tx,toY:ty,fade:false,remove:true,
                duration:delay,betaFlight:true,tilt:0,fromRotation:angle,toRotation:angle});
        }
        private function drawBetaHit(parent:Sprite,x:Number,y:Number,size:Number,tint:uint,delay:Number):void
        {
            // Original 2x2 impact sheet. Play all four cells in order; template
            // IDs must not select an arbitrary frozen cell of the animation.
            var root:Sprite=new Sprite();root.mouseEnabled=false;root.mouseChildren=false;
            root.x=x;root.y=y;parent.addChild(root);var frames:Array=[];
            for(var i:int=0;i<4;i++){
                var frame:Sprite=betaVisual(-250-i,size,size,tint);
                if(frame){frame.visible=i==0;root.addChild(frame);frames.push(frame);}
            }
            if(frames.length==0){parent.removeChild(root);return;}
            animations.push({sprite:root,fromX:x,fromY:y,toX:x,toY:y,hitFrames:frames,
                duration:260,delay:delay,hideBeforeDelay:true,fade:true,remove:true});
        }
        private function paintStaticCardState(parent:Sprite,c:Object,w:Number,h:Number):void
        {
            // Pile and preview faces use the same live snapshot as field cards.
            // In particular, ResetInGraveyard preserves Lock; never hide it here.
            if((int(c.tokens)&4)!=0)paintLock(parent,3,h*.4);
            if((int(c.tokens)&1)!=0)paintResilience(parent,w,h);
            if((int(c.tokens)&2)!=0)paintSpyRibbon(parent,w,h);
            if(c.armor!=null&&int(c.armor)>0){
                var sw:Number=Math.min(46,w*.25),sh:Number=sw*64/59;
                paintArt(parent,BetaGwentHud104.SHIELD,sw,sh,w-sw-3,3);
                var fontSize:Number=sh*1.05;
                var n:TextField=betaLabel(parent,String(c.armor),w-sw-3,3,sw,fontSize,0xFFF0CA,BetaGwentFonts.NUMBERS,false,"center");
                n.height=sh*2;centerBetaNumber(n,w-sw/2-3,3+sh*.47,fontSize);
            }
            if(c.timer!=null&&int(c.timer)>=0)paintTimer(parent,3,h*.55,int(c.timer),(int(c.tokens)&4)!=0);
        }
        private function drawWeatherImpact(fx:Sprite,target:Object,delay:Number):void
        {
            var token:int=0;
            for each(var hazard:Object in weatherRows)if(hazard.side==target.side&&hazard.zone==target.zone){token=hazard.token;break;}
            var x:Number=poseX(target),y:Number=poseY(target);
            if(token==1){
                betaBurst(fx,BetaGwentWeather107.FROST_SPIKES,x,y+poseH(target)*.25,poseW(target)*1.25,0xCDEFFF,delay,280);
                betaBurst(fx,BetaGwentWeather107.SPARKLE,x,y,poseW(target),0xBDE9FF,delay,320);return;
            }
            var id:int=token==2?BetaGwentWeather107.FOG_BODY:token==4?BetaGwentWeather107.RAIN_DROPS:-250;
            var mist:Sprite=betaVisual(id,token==4?22:poseW(target)*1.25,poseH(target)*.7,0xCADFEB);if(!mist)return;
            fx.addChild(mist);mist.x=x;mist.y=y;
            animations.push({sprite:mist,fromX:x,fromY:token==4?y-18:y+12,toX:x,toY:token==4?y+20:y-10,
                fade:true,remove:true,duration:token==4?220:400,delay:delay,hideBeforeDelay:true});
        }
        private function drawArmorHit(parent:Sprite,width:Number,remaining:int,delay:Number):void
        {
            var shield:Sprite=betaVisual(BetaGwentHud104.SHIELD,30,33);if(!shield)return;
            parent.addChild(shield);shield.x=width-18;shield.y=18.5;
            animations.push({sprite:shield,fromX:shield.x,fromY:18.5,toX:shield.x,toY:18.5,fade:true,remove:true,
                duration:220,delay:delay,hideBeforeDelay:true,fromScaleX:1,fromScaleY:1,toScaleX:1.2,toScaleY:1.2});
            // Only a fully depleted shield breaks; partial armour damage pulses.
            if(remaining>0)return;
            for(var piece:int=0;piece<3;piece++){
                var shard:Sprite=betaVisual(BetaGwentHud104.SHIELD,30,33);if(!shard)continue;
                parent.addChild(shard);shard.x=width-18;shard.y=18.5;
                var clip:Sprite=new Sprite();clip.mouseEnabled=false;shard.addChild(clip);
                clip.graphics.beginFill(0xFFFFFF);clip.graphics.drawRect(-15+piece*10,-16.5,10,33);clip.graphics.endFill();
                shard.getChildAt(0).mask=clip;
                animations.push({sprite:shard,fromX:width-18,fromY:18.5,toX:width-18+(piece-1)*18,toY:43+piece*4,
                    fade:true,remove:true,duration:340,delay:delay,hideBeforeDelay:true,fromRotation:0,toRotation:(piece-1)*55});
            }
        }
        // Beta small card (SmallCardFull: 17.64 x 21.46 units). Banner 4.4 x 8.2 at (0.12,0.33).
        private static const BETA_CARD_ASPECT:Number=17.64/21.46;
        private function betaBannerRect(w:Number,h:Number):Array{return [w*.12/17.64,h*.33/21.46,w*4.4/17.64,h*8.2/21.46];}
        private function paintBetaFace(p:Sprite,templateId:int,w:Number,h:Number,side:int=0):void
        {
            var size:Array=BetaGwentHDArt.size(templateId);
            if(size){
                var sw:Number=size[0],sh:Number=size[1];var ch:Number=Math.min(sh,sw*h/w);var cw:Number=Math.min(sw,ch*w/h);
                var art:Sprite=BetaGwentHDArt.clip(templateId,w,h,(sw-cw)/2,(sh-ch)*.25,cw,ch);
                if(art)p.addChild(art);else paintArt(p,templateId,w,h,0,0);
            }else paintArt(p,templateId,w,h,0,0);
            var entry:Object=BetaGwentFullCatalog.find(templateId);
            var tier:int=entry?int(entry.tier):2;var faction:int=entry?int(entry.faction):1;
            // Beta: neutral cards wear the banner of the deck (owner's leader) faction.
            if((faction&62)==0&&side>0&&leaderIds&&leaderIds.length>=side)faction=cardFaction(int(leaderIds[side-1]));
            paintArt(p,tier==8||tier==1?-1602:tier==4?-1601:-1600,w,h,0,0);
            var b:Array=betaBannerRect(w,h);
            paintArt(p,-1610-(faction==2?0:faction==4?1:faction==8?2:faction==16?3:faction==32?4:5),b[2],b[3],b[0],b[1]);
        }
        private function paintResilience(p:Sprite,w:Number,h:Number):void
        {
            paintArt(p,-1891,w*.86,h*.095,w*.07,h*.9);
            paintArt(p,-1892,w*.09,h*.17,w*.03,h*.86);paintArt(p,-1893,w*.09,h*.17,w*.88,h*.86);
            paintArt(p,-1890,w*.26,h*.27,w*.37,h*.77);
        }
        private function betaPowerField(p:Sprite,value:String,w:Number,h:Number,color:uint):TextField
        {
            var b:Array=betaBannerRect(w,h);var size:int=Math.max(14,Math.round(h*.2));
            var field:TextField=text(p,value,b[0]-4,b[1]+b[3]*.06,b[2]+8,size,color);field.height=size*1.5;
            if(!BetaGwentFonts.apply(field,BetaGwentFonts.NUMBERS,size,color,true,"center")){field.defaultTextFormat=new TextFormat("$NormalFont",size,color,true,null,null,null,null,"center");field.setTextFormat(field.defaultTextFormat);}
            field.filters=[new GlowFilter(0x000000,1,3,3,6,1)];
            return field;
        }
        private function isSpyCard(templateId:int):Boolean
        {
            // Same list as BetaGwentDuelSpying (duelCatalog.ws), which includes created spies such as Cow Carcass.
            if([132204,122105,122203,122206,112215,162101,162205,162210,162211,162212,162314,162315,200115,201580,162402,143301,142203,152104,152214,152401,152403,201572].indexOf(templateId)>=0)return true;
            var definition:Object=BetaGwentFullCatalog.find(templateId); return definition!=null&&definition.spy==true;
        }
        private function paintRevealedMark(p:Sprite,cx:Number,cy:Number):void
        {
            // Beta TokenVisibility (magnifying glass) for a hand card the opponent can see (atlas page 19).
            var m:Sprite=new Sprite();m.mouseEnabled=false;m.mouseChildren=false;p.addChild(m);
            paintArt(m,BetaGwentWeather107.TOKEN_VISIBILITY,34,34,cx-17,cy-17);
        }
        private function paintSpyRibbon(p:Sprite,w:Number,h:Number):void
        {
            // Beta spying token: TokenSpyingEye with the red TokenSpyingIris, at the top edge of the card (atlas page 19).
            var m:Sprite=new Sprite();m.mouseEnabled=false;m.mouseChildren=false;p.addChild(m);
            var ew:Number=Math.min(64,w*.5);paintArt(m,BetaGwentWeather107.TOKEN_SPYING,ew,ew/2,(w-ew)/2+w*.08,3);
        }
        private function paintCardBack(parent:Sprite,w:Number,h:Number,side:int):void
        {
            if(skin==3&&paintArt(parent,BetaGwentHud104.cardBack(sideFaction(side)),w,h,0,0))return;
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
                fx.graphics.lineStyle(4,0xBCA2DF,.4);fx.graphics.moveTo(x+(pose?poseW(pose):80)/2,y+(pose?poseH(pose):110)/2);fx.graphics.lineTo(sx,sy);
            }
        }
        // Continue original texture motion during clearing; no frozen weather frame.
        private function advanceWeatherTextures(fx:Object,now:int):void
        {
            if(!fx||!fx.nativeParts)return;
            var t:Number=(now-fx.start)/1000;
                    for each(var part:Object in fx.nativeParts){
                        var view:Sprite=part.sprite;
                        if(part.kind=="beta-fog-intro"){
                            updateFogIntro(part,t);continue;
                        }else if(part.kind=="frost-reveal"){
                            // Grow opacity across the whole row. A hard scrollRect
                            // wipe exposed a straight seam through cards/wood.
                            var growth:Number=BetaGwentBetaMotion.sample("PREVIEW",Math.max(0,Math.min(1,(t-Number(part.offset||0))/BetaGwentVisualTimings.FROST_INTRO)));
                            view.scrollRect=null;view.alpha=part.alpha*growth;
                        }else if(part.kind=="fog"){
                            view.x=(t*part.speed+part.phase)%(fx.w+part.width)-part.width;
                            view.y=part.y+Math.sin(t*.6+part.phase)*5;
                            view.alpha=part.alpha*(.8+.2*Math.sin(t*.7+part.phase));
                        }else if(part.kind=="rain"||part.kind=="rain-lower"){
                            view.x=part.x;view.y=(t*150+part.phase)%180-180+(part.kind=="rain-lower"?180:0);view.alpha=part.alpha;
                        }else if(part.kind=="scroll"){
                            view.x=-((t*part.speed+part.phase)%part.width)+part.offset;
                        }else if(part.kind=="pulse"){
                            var range:Number=part.range!=null?Number(part.range):.28;
                            view.alpha=part.alpha*(1-range+range*Math.sin(t*part.speed+part.phase));
                        }else if(part.kind=="twinkle"){
                            var tw:Number=Math.sin(t*part.speed+part.phase);view.alpha=tw>0?part.alpha*tw:0;
                            // Stable positions across board redraws, changed only
                            // while the sparkle is invisible between cycles.
                            var cycle:int=Math.floor((t*part.speed+part.phase)/(Math.PI*2));
                            view.x=((cycle*137+part.phase*97)%Math.max(1,fx.w-24));
                            view.y=((cycle*47+part.phase*37)%Math.max(1,fx.h-24));
                        }else if(part.kind=="fall"){
                            view.x=part.x+Math.sin(t*.35+part.phase)*7;view.y=(t*part.speed+part.phase)%(fx.h+part.height)-part.height;view.alpha=part.alpha;
                        }else if(part.kind=="rise"){
                            view.x=part.x+Math.sin(t*.9+part.phase)*6;view.y=fx.h-(t*part.speed+part.phase)%(fx.h+part.height);
                            view.alpha=part.alpha*Math.min(1,view.y/(fx.h*.4));
                        }else if(part.kind=="snow"){
                            view.x=(part.phase+t*14)%fx.w;view.y=(part.phase*.37+t*18)%(fx.h+24)-24;
                            view.rotation=Math.sin(t*.4+part.phase)*20;view.alpha=part.alpha;
                        }
                    }
        }
        private function animateWeather(e:Event):void
        {try{animateWeatherBody(e);}catch(frameError:Error){reportUIError("animateWeather",frameError);}}
        private function animateWeatherBody(e:Event):void
        {
            var now:int=getTimer();
            for(var fadeIndex:int=weatherFades.length-1;fadeIndex>=0;fadeIndex--){
                var fading:Object=weatherFades[fadeIndex];var fadeProgress:Number=reducedMotion?1:Math.min(1,(now-fading.start)/360);
                advanceWeatherTextures(fading.effect,now);
                fading.sprite.alpha=fading.alpha*(1-BetaGwentBetaMotion.sample("PREVIEW",fadeProgress));
                if(fadeProgress>=1){if(fading.sprite.parent)fading.sprite.parent.removeChild(fading.sprite);weatherFades.splice(fadeIndex,1);}
            }
            if(weatherEffects.length==0)return;
            if(reducedMotion){
                // Keep the weather state readable while disabling movement.
                for each(var quiet:Object in weatherEffects){
                    quiet.sprite.visible=true;quiet.sprite.alpha=1;quiet.sprite.graphics.clear();
                    if(quiet.accent)quiet.accent.graphics.clear();
                    for each(var still:Object in quiet.nativeParts){
                        still.sprite.visible=still.kind!="twinkle"&&still.kind!="fall"&&still.kind!="rise"&&still.kind!="snow"&&still.kind!="beta-fog-intro";
                        still.sprite.alpha=still.alpha;
                        if(still.kind=="frost-reveal")still.sprite.scrollRect=null;
                        if(still.kind=="scroll")still.sprite.x=still.offset;
                    }
                }return;
            }
            // Texture movement runs at movie rate; only procedural accents
            // redraw at 15 Hz. Native fog/rain no longer jump at 10 Hz.
            var redraw:Boolean=!e||now>=weatherRedrawAt;
            if(redraw)weatherRedrawAt=now+66;
            for each(var fx:Object in weatherEffects){
                var p:Sprite=fx.sprite;var t:Number=(now-fx.start)/1000;p.visible=true;
                var intro:Number=fx.token==1?BetaGwentVisualTimings.FROST_INTRO:fx.token==2?BetaGwentVisualTimings.FOG_INTRO:BetaGwentVisualTimings.RAIN_INTRO;
                p.alpha=BetaGwentBetaMotion.sample("PREVIEW",Math.min(1,t/intro));if(redraw)p.graphics.clear();
                if(fx.nativeParts){
                    advanceWeatherTextures(fx,now);
                    if(fx.beta&&redraw)drawBetaWeatherAccents(fx,p,t);
                    continue;
                }
                if(!redraw)continue;
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
            inspection.text=cardReading(c,detail);showBattleCard(c,detail);
        }
        // Original Beta row-weather layers (tools/ui/build_weather107.py, art page 19).
        private function betaWeatherLayer(fx:Object,id:int,x:Number,y:Number,w:Number,h:Number,alpha:Number,kind:String=null,extra:Object=null):Sprite
        {
            var art:Sprite=BetaGwentCardArt.view(id,w,h);if(!art)return null;
            art.x=x;art.y=y;art.alpha=alpha;art.mouseEnabled=false;art.mouseChildren=false;fx.sprite.addChild(art);
            if(kind){var part:Object={sprite:art,kind:kind,alpha:alpha,phase:fx.phase,speed:1};
                if(extra)for(var key:String in extra)part[key]=extra[key];fx.nativeParts.push(part);}
            return art;
        }
        private function betaScroll(fx:Object,id:int,y:Number,h:Number,alpha:Number,speed:Number):void
        {
            for(var copy:int=0;copy<2;copy++)
                betaWeatherLayer(fx,id,0,y,fx.w,h,alpha,"scroll",{width:fx.w,offset:copy*fx.w,speed:speed});
        }
        private function prepareBetaWeather(fx:Object):void
        {
            fx.nativeParts=[];fx.beta=true;var W:Number=fx.w,H:Number=fx.h;var i:int;var shade:Sprite;
            var holder:Sprite=fx.sprite;holder.mouseEnabled=false;holder.mouseChildren=false;
            var base:Sprite=new Sprite();base.mouseEnabled=false;holder.addChild(base);fx.base=base;
            var tintColor:uint=fx.token==1?0x163A55:fx.token==2?0x1C2226:fx.token==4?0x0E2B40:fx.token==16?0x3A2410:
                fx.token==32?0x2A0E06:fx.token==64?0x0B2630:fx.token==128?0x4A3A0A:fx.token==256?0x1A2240:
                fx.token==2048?0x3A0810:fx.token==1024?0x0E2A18:0x1E1A14;
            base.graphics.beginFill(tintColor,fx.token==2?0.22:0.25);base.graphics.drawRect(0,0,W,H);base.graphics.endFill();
            if(fx.token==1){
                betaWeatherLayer(fx,BetaGwentWeather107.FROST_RIM,0,0,W,H,.9,"pulse",{speed:.6,range:.06});
                betaWeatherLayer(fx,BetaGwentWeather107.FROST_SPIKES,0,0,W,H,.95,"frost-reveal",{offset:0});
                betaWeatherLayer(fx,BetaGwentWeather107.FROST_COVER,0,0,W,H,1,"frost-reveal",{offset:.08});
                for(i=0;i<10;i++)betaWeatherLayer(fx,BetaGwentWeather107.SPARKLE,(i*97+fx.phase)%(W-24),(i*37)%(H-24),22,22,.9,"twinkle",{speed:1.3+i%3*.4,phase:i*1.7});
            }else if(fx.token==2){
                betaScroll(fx,BetaGwentWeather107.FOG_BODY,0,H,.65,14);
                betaWeatherLayer(fx,BetaGwentWeather107.FOG_BODY,0,H*.15,W,H*.7,.25,"pulse",{speed:.35,range:.12});
                betaWeatherLayer(fx,BetaGwentWeather107.FOG_BODY,0,H*.12,W*.55,H*.78,.28,"fog",{width:W*.55,y:H*.12,speed:19});
            }else if(fx.token==4){
                betaWeatherLayer(fx,BetaGwentWeather107.RAIN_WET,0,0,W,H,.6,"pulse",{speed:.4,range:.035});
                for(i=0;i<18;i++){
                    var rain:Sprite=betaWeatherLayer(fx,BetaGwentWeather107.RAIN_DROPS,0,0,14,42,.55,"fall",{x:i*W/18+(i*13)%20,height:42,speed:150+i%4*30,phase:i*37});
                    if(rain)rain.rotation=9;
                }
            }else if(fx.token==16){
                betaWeatherLayer(fx,BetaGwentWeather107.DROUGHT_CRACKS,0,0,W,H,.85);
                betaScroll(fx,BetaGwentWeather107.DROUGHT_SAND,0,H,.75,22);
            }else if(fx.token==32){
                betaWeatherLayer(fx,BetaGwentWeather107.RAGH_ROCKS,0,0,W,H,0.5);
                betaWeatherLayer(fx,BetaGwentWeather107.RAGH_VEINS,0,0,W,H,.95,"pulse",{speed:2.1});
            }else if(fx.token==64){
                betaScroll(fx,BetaGwentWeather107.STORM_SEA,0,H,.8,30);
                fx.flashAt=1.2;
            }else if(fx.token==128){
                for(i=0;i<12;i++)betaWeatherLayer(fx,BetaGwentWeather107.FROTH_FOAM,0,0,30+i%3*8,30+i%3*8,.85,"rise",{x:i*W/12,height:40,speed:14+i%4*5,phase:i*29});
            }else if(fx.token==256||fx.token==2048){
                var moon:Sprite=betaWeatherLayer(fx,BetaGwentWeather107.MOON,W-H-12,4,H-8,H-8,.85,"pulse",{speed:.5});
                if(moon&&fx.token==2048)moon.transform.colorTransform=new ColorTransform(1,.45,.4,1,40,0,0,0);
            }else if(fx.token==512){
                betaWeatherLayer(fx,BetaGwentWeather107.PITFALL_WOOD,0,0,W,H,.9);
            }else if(fx.token==1024){
                betaWeatherLayer(fx,BetaGwentWeather107.DREAM_HEAD,6,0,H*.5,H,.9,"pulse",{speed:1.4});
                betaScroll(fx,BetaGwentWeather107.FOG_BODY,0,H,.35,18);
            }
            var accent:Sprite=new Sprite();accent.mouseEnabled=false;holder.addChild(accent);fx.accent=accent;
        }
        private function drawBetaWeatherAccents(fx:Object,p:Sprite,t:Number):void
        {
            var i:int;if(!fx.accent)return;p=fx.accent;p.graphics.clear();
            if(fx.token==4){
                for(i=0;i<7;i++){var life:Number=(t*.9+i*.37)%1;var rx:Number=(i*131+fx.phase*7)%fx.w;var ry:Number=fx.h*.25+(i*29)%int(fx.h*.6);
                    p.graphics.lineStyle(1,0xBFE6F5,.35*(1-life));p.graphics.drawEllipse(rx-12*life,ry-4*life,24*life,8*life);}
            }else if(fx.token==64){
                var phase:Number=(t+fx.phase*.01)%4.6;
                if(phase<.18){var lx:Number=(Math.floor(t/4.6)*317+fx.phase)%fx.w;
                    p.graphics.lineStyle(2,0xDDF0FF,.9-phase*4);p.graphics.moveTo(lx,0);
                    for(i=1;i<=5;i++)p.graphics.lineTo(lx+((i*53+fx.phase)%30)-15,fx.h*i/5);
                    p.graphics.lineStyle();p.graphics.beginFill(0xBFDFFF,.18-phase);p.graphics.drawRect(0,0,fx.w,fx.h);p.graphics.endFill();}
            }else if(fx.token==16||fx.token==32){
                for(i=0;i<10;i++){var ex:Number=(i*113+fx.phase+t*(fx.token==16?18:9))%fx.w;var ey:Number=fx.h-((t*(12+i%3*6)+i*23)%fx.h);
                    p.graphics.beginFill(fx.token==16?0xF3C27A:0xFF8A3A,.35*(ey/fx.h));p.graphics.drawCircle(ex,ey,1+i%2);p.graphics.endFill();}
            }
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
                    art=BetaGwentCardArt.view(-203,14+i%3*6,14+i%3*6);if(!art)continue;holder.addChild(art);
                    fx.nativeParts.push({sprite:art,kind:"snow",phase:i*83+fx.phase,alpha:.26});
                }
                for(i=0;i<3;i++){
                    width=260;art=BetaGwentCardArt.view(-240-i,width,fx.h*.65);if(!art)continue;holder.addChild(art);
                    fx.nativeParts.push({sprite:art,kind:"fog",width:width,y:fx.h*.22,speed:9,phase:i*230+fx.phase,alpha:.1});
                }
            }else if(fx.token==2){
                for(i=0;i<7;i++){
                    width=210+i%3*75;art=BetaGwentCardArt.view(-201,width,fx.h*.8);if(!art)continue;holder.addChild(art);
                    fx.nativeParts.push({sprite:art,kind:"fog",width:width,y:i%3*fx.h*.12,speed:12+i%3*5,phase:i*149+fx.phase,alpha:.16});
                }
                var wave:Sprite=new Sprite();wave.mouseEnabled=false;wave.mouseChildren=false;holder.addChild(wave);
                var frames:Array=[];
                for(i=0;i<30;i++){
                    art=BetaGwentCardArt.view(-210-i,fx.w,fx.h);if(!art)continue;
                    art.visible=false;wave.addChild(art);frames.push(art);
                }
                wave.alpha=.7;
                if(frames.length==30)fx.nativeParts.push({sprite:wave,kind:"beta-fog-intro",frames:frames,frame:-1});
            }else {
                for(i=0;i<16;i++){
                    width=Math.min(40,fx.w/16);
                    for(var layer:int=0;layer<2;layer++){
                        art=BetaGwentCardArt.view(-202,width,180);if(!art)continue;holder.addChild(art);
                        fx.nativeParts.push({sprite:art,kind:"rain",x:i*fx.w/16,phase:layer*180+fx.phase+i*17,width:width,alpha:fx.token==64 ? 0.6 : 0.45});
                        // Two neighbouring vertical copies keep the entire row covered.
                        if(layer==1)fx.nativeParts[fx.nativeParts.length-1].kind="rain-lower";
                    }
                }
            }
            holder.mouseEnabled=false;holder.mouseChildren=false;
        }
        private function updateFogIntro(part:Object,t:Number):void
        {
            var life:Number=BetaGwentVisualTimings.FOG_LIFE;
            part.sprite.visible=t>=0&&t<life;if(!part.sprite.visible)return;
            var sample:int=Math.min(119,Math.max(0,int(t/life*119)));
            var frame:int=BetaGwentVisualTimings.FOG_FRAMES[sample];
            if(part.frame==frame)return;
            if(part.frame>=0)part.frames[part.frame].visible=false;
            part.frames[frame].visible=true;part.frame=frame;
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
        private function cardReading(c:Object,detail:Object,complete:Boolean=false,skipHeader:Boolean=false):String
        {
            var hidden:Boolean=(c.zone&7)!=0&&(int(c.tokens)&8)!=0;
            var value:String=skipHeader?"":c.title+(c.created?" · сотворённая копия":"")+"\n";
            if(c.templateId>0){
                var original:Object=BetaGwentCardText.find(c.templateId);
                if(!skipHeader&&original&&original.typeMask==4)value+="Исходная сила: "+original.power+(c.power!=null?" · текущая: "+c.power:"")+"\n";
            }
            if(hidden)value+=ambushReading(c)+"\n\n";
            else if((c.zone&7)!=0&&isAmbush(c.templateId))value+="Засада уже раскрыта; её сила учитывается в счёте.\n\n";
            if(!skipHeader&&c.templateId>0)value+="Теги: "+(BetaGwentCardTags.text(c.templateId)||"—")+"\n\n";
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
            if(!c||c.hidden)return;clearDrag();clearPlacementGhost();detailOpen=true;
            setChildIndex(detailLayer,numChildren-1);
            while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            while(detailLayer.numChildren)detailLayer.removeChildAt(0);
            var shade:Sprite=panel(detailLayer,-WIDE_PAD,0,1920+2*WIDE_PAD,1080,0x080C10,.82);
            shade.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();closeCardDetail();});
            // UICardPreviewPrefab: full-screen dark backdrop, details on the left,
            // large original card on the right. Reuse Beta textures/fonts, no extra atlas.
            var box:Sprite=new Sprite();detailLayer.addChild(box);
            box.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopImmediatePropagation();});
            var entry:Object=BetaGwentFullCatalog.find(c.templateId);
            var original:Object=BetaGwentCardText.find(c.templateId);
            var side:int=int(c.side)||1,fi:int=entry?editorFactionIndex(entry.faction):sideFaction(side);
            var picture:Sprite=new Sprite();picture.x=1110;picture.y=170;box.addChild(picture);
            if(c.templateId>0){
                paintBetaFace(picture,c.templateId,440,616,side);
                if(original&&(original.typeMask==4||entry&&entry.leader))betaPowerField(picture,String(original.power),440,616,0xFFFFFF);
            }else paintCardBack(picture,440,616,2);
            var name:TextField=betaLabel(box,readableText(c.title).toUpperCase(),220,216,750,40,0xF5F0E7,BetaGwentFonts.TITLE,true,null,2);
            name.height=110;
            betaLabel(box,c.templateId>0?(BetaGwentCardTags.text(c.templateId)||""):"",220,326,750,22,0xD0C8B6,BetaGwentFonts.BODY).height=52;
            if(original&&original.typeMask==4&&c.power!=null&&int(c.power)!=int(original.power))
                betaLabel(box,"Исходная сила: "+original.power+" · текущая: "+c.power,220,379,750,20,0xD7C498,BetaGwentFonts.BODY).height=34;
            var body:TextField=text(box,cardReading(c,detail,true,true),220,420,750,25,0xEBE5D8);body.height=442;
            detailBody=body;body.mouseEnabled=true;body.selectable=true;
            body.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopImmediatePropagation();e.preventDefault();body.scrollV=Math.max(1,Math.min(body.maxScrollV,body.scrollV-e.delta*3));});
            betaLabel(box,"Колесо — прокрутить описание · Esc или I — закрыть",220,909,1050,19,0xB9B4A9,BetaGwentFonts.BODY).height=40;
            editorBetaButton(box,"Вернуться к игре",1110,909,440,52,true,closeCardDetail);
        }

        private function isInspectMouse(e:MouseEvent):Boolean
        {
            // GFx emits CLICK with buttonIdx=1; plain Flash events lack the
            // extension. Read it structurally without another SDK class load.
            return e.type==RIGHT_CLICK_EVENT || ("buttonIdx" in Object(e))&&int(Object(e)["buttonIdx"])==1;
        }
        private function attachInspect(p:Sprite,c:Object,detail:Object,bodyWidth:Number=0,bodyHeight:Number=0):void
        {
            // Stable card body bounds exclude text fields, halos and transient effects.
            var body:Rectangle=new Rectangle(0,0,bodyWidth>0?bodyWidth:p.width/p.scaleX,bodyHeight>0?bodyHeight:p.height/p.scaleY);
            controller.registerControl(p,c.title,null,c,detail,c.zone==8&&c.side==1?"hand":"card",null,body);
            var glow:Sprite=new Sprite();glow.mouseEnabled=false;glow.mouseChildren=false;
            glow.graphics.lineStyle(2,0xD6E8E6,.8);
            glow.graphics.drawRect(1,1,(bodyWidth>0?bodyWidth:p.width/p.scaleX)-2,(bodyHeight>0?bodyHeight:p.height/p.scaleY)-2);
            glow.alpha=0;p.addChild(glow);
            p.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{
                if(dragging||detailOpen)return;
                hoveredCard=c;hoveredDetail=detail;lastInspectedCard=c;
                glow.alpha=1;if(hoverCardId==(c.id!=null?c.id:c.templateId))return;hoverCardId=c.id!=null?c.id:c.templateId;
                if(editingDeck){showEditorCard(c);return;}
                if(inspection)inspection.text=cardReading(c,detail);showBattleCard(c,detail);
                while(previewLayer.numChildren)previewLayer.removeChildAt(0);
                hoverPreviewAt=getTimer()+240;
                hoverPreviewX=Math.min(1304,Math.max(16,mouseX+20));
                hoverPreviewY=Math.min(628,Math.max(90,mouseY-190));
            });
            p.addEventListener(MouseEvent.ROLL_OUT,function(e:MouseEvent):void{
                glow.alpha=0;hoverCardId=0;hoveredCard=null;hoveredDetail=null;hoverPreviewAt=0;if(skin==3&&keyboardFocusId==0&&selected==0)clearBattlePreview();updateFocusedInspection();
                while(previewLayer.numChildren)previewLayer.removeChildAt(0);
            });
            // Native GFx sends CLICK with MouseEventEx.buttonIdx, as stock
            // CardSlot does. RIGHT_CLICK alone works only in the Flash player.
            // Intercept before drag/play/target listeners: inspection cannot
            // spend a card or confirm an outstanding ability choice.
            p.addEventListener(MouseEvent.MOUSE_DOWN,function(e:MouseEvent):void{if(e.shiftKey||isInspectMouse(e)){e.stopImmediatePropagation();e.preventDefault();}},false,100);
            p.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{if(e.shiftKey||isInspectMouse(e)){e.stopImmediatePropagation();e.preventDefault();if(!detailOpen)openCardDetail(c,detail);}},false,100);
            p.addEventListener(RIGHT_CLICK_EVENT,function(e:MouseEvent):void{e.stopImmediatePropagation();e.preventDefault();if(!detailOpen)openCardDetail(c,detail);},false,100);
        }
        private function showHoverPreview():void
        {
            if(battlePreview||!hoveredCard||editingDeck||detailOpen||pileOpen||requestKind==1&&skin==3||dragging||playing||controller.active||canPlaceSelected()||canPlacePending())return;
            // Keep the board visible while aiming at units or rows. The right
            // reading pane and explicit full inspection remain available.
            if(requestId>0&&requestKind==2||selected>0&&playRules[selected]&&playRules[selected].kind>0)return;
            var c:Object=hoveredCard;var detail:Object=hoveredDetail;
            var large:Sprite=panel(previewLayer,hoverPreviewX,hoverPreviewY,600,416,0x101315,.98);
            if(c.templateId>0)paintChoiceArt(large,c.templateId,184,256);else paintCardBack(large,184,256,2);
            text(large,c.title,8,264,184,21,0xF5D77F).height=72;
            text(large,cardReading(c,detail),204,12,382,21).height=354;
            text(large,"I / Shift + клик — открыть и прокрутить",14,378,570,19,0xA7DCEE).height=30;
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
        private function attachRequestCard(p:Sprite,id:int,displayCard:Object=null,displayDetail:Object=null):void
        {
            p.buttonMode=ready;
            var action:Function=requestAction("OnBetaGwentRequestSelect",id);
            controller.registerControl(p,"",action,displayCard||findRequestCard(id),displayDetail||cardDetails[id],"target");
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
        // stage104-mulligan
        // stage118: complete-set browsers share a selected-card reading area.
        private var mulliganHidden:Boolean=false;
        private var mulliganConfirm:Boolean=false;
        private var mulliganPickedId:int=0;
        private var mulliganReading:TextField;
        private var mulliganTitle:TextField;
        private function showMulliganCard(c:Object,detail:Object):void
        {
            if(requestId<=0||requestKind!=1||skin!=3||!mulliganReading||!c)return;
            if(mulliganPickedId==c.id&&mulliganTitle.text==c.title)return;
            mulliganPickedId=c.id;keyboardFocusId=c.id;mulliganTitle.text=c.title;
            mulliganReading.text=readableText(detail?detail.description:"");mulliganReading.scrollV=1;
            for each(var other:Object in requestCards)if(other.mulliganGlow)other.mulliganGlow.alpha=other.id==c.id? .8:0;
        }
        private var mulliganAnswer:Boolean=false;
        private var mulliganDialog:Sprite=new Sprite();
        private function requestMulliganFinish():void
        {
            if(!ready||!requestFinish)return;
            if(requestCount<requestMax){mulliganAnswer=false;mulliganConfirm=true;render();}else finishMulligan();
        }
        private function finishMulligan():void
        {
            mulliganConfirm=false;mulliganHidden=false;
            var finish:Function=requestAction("OnBetaGwentRequestFinish");finish();
        }
        private function drawBetaMulligan():void
        {
            var choiceOrder:Array=sortedHand(requestCards);
            content.addChild(choiceLayer);choiceLayer.graphics.clear();choicePage=0;mulliganReading=null;mulliganTitle=null;
            var remaining:int=Math.max(0,requestMax-requestCount);
            if(mulliganHidden){
                var hiddenStart:int=content.numChildren;
                betaWideButton("Показать карты",75,858,255,true,function():void{mulliganHidden=false;render();});
                while(content.numChildren>hiddenStart)choiceLayer.addChild(content.getChildAt(hiddenStart));return;
            }
            stripHeading(choiceLayer,"Обмен карт","Выберите карту для замены · осталось замен: "+remaining);
            var layout:Object=overviewLayout(choiceOrder.length,1800,440,12,230,54);
            var titleY:Number=Math.max(600,220+layout.blockH+24);
            mulliganTitle=text(choiceLayer,"",260,titleY,1400,28,0xF4EFE4);mulliganTitle.height=50;
            betaFace(BetaGwentFonts.TITLE,mulliganTitle,28,0xF4EFE4,false,"center");
            mulliganReading=text(choiceLayer,"",300,titleY+58,1320,24,0xD7D4CB);mulliganReading.height=946-titleY-58;
            betaFace(BetaGwentFonts.BODY,mulliganReading,24,0xD7D4CB);mulliganReading.mouseEnabled=true;
            var reading:TextField=mulliganReading;
            reading.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{reading.scrollV=Math.max(1,Math.min(reading.maxScrollV,reading.scrollV-e.delta*3));e.stopPropagation();});
            reading.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            var picked:Object=null;
            for(var i:int=0;i<choiceOrder.length;i++){
                var c:Object=choiceOrder[i],handCard:Object=null;
                for each(var hc:Object in cards)if(hc.id==c.id){handCard=hc;break;}
                var view:Object=handCard||c;
                var detail:Object=cardDetails[c.id];if(!detail){var catalog:Object=BetaGwentCardText.find(c.templateId);detail={description:catalog?catalog.description:""};}
                var row:int=int(i/layout.cols),column:int=i%layout.cols,inRow:int=Math.min(layout.cols,choiceOrder.length-row*layout.cols);
                var x:Number=60+(1800-(inRow*layout.w+(inRow-1)*18))/2+column*(layout.w+18);
                var tile:Sprite=compactOverviewCard(choiceLayer,view,detail,x,220+row*layout.stepY,layout.w,layout.h,layout.captionH);
                c.stripBody=mulliganReading;c.mulliganGlow=view.stripGlow;c.displayCard=view;c.displayDetail=detail;
                attachMulliganReading(tile,c,detail);
                if(c.id==mulliganPickedId)picked=c;if(c.id==keyboardFocusId)picked=c;
                if(!c.revealed)paintCardBack(tile,layout.w,layout.h,1);
                attachRequestCard(tile,c.id,view,detail);
            }
            if(!picked&&choiceOrder.length)picked=choiceOrder[0];
            if(picked)showMulliganCard(picked,picked.displayDetail);
            editorBetaButton(choiceLayer,"Закончить обмен",682,978,278,48,ready&&requestFinish,requestMulliganFinish);
            editorBetaButton(choiceLayer,"Скрыть карты",1005,978,238,48,true,function():void{mulliganHidden=true;render();});
            if(mulliganConfirm)drawBetaConfirm("ОБМЕН КАРТ","Закончить обмен? Можно заменить ещё "+remaining+".",finishMulligan,function():void{mulliganConfirm=false;render();});
        }
        private function attachMulliganReading(tile:Sprite,c:Object,detail:Object):void
        {tile.addEventListener(MouseEvent.ROLL_OVER,function(e:MouseEvent):void{showMulliganCard(c,detail);});}
        // Ability lists use the same complete-set layout and reading area as mulligans.
        // Only presentation objects are enriched; request ids and legal choices stay intact.
        private function drawBetaAbilityChoices():void
        {
            content.addChild(choiceLayer);choiceLayer.graphics.clear();choicePage=0;mulliganReading=null;mulliganTitle=null;
            var heading:String=templateChoice?(rowMode==13?"Выберите вариант способности":rowMode==7?"Дагон · выберите погоду":"Рассвет · выберите вариант"):pileChoice?(rowMode==14?"Выберите карту для способности":"Выберите карту для розыгрыша"):handPowerChoice?"Выберите отряд в руке":"Поглощение · выберите отряд из сброса";
            var hint:String=readableText(requestMessage);
            if(!hint)hint=templateChoice?(rowMode==13?"Выберите вариант, затем подходящую цель.":rowMode==7?"Выберите погоду, затем ряд соперника.":"Чистое небо: убрать погоду. Сбор: разыграть случайный бронзовый отряд."):pileChoice?"Выберите карту из предложенного списка.":handPowerChoice?"Сила выбранного отряда определит эффект. Отряд останется в руке.":"Выберите отряд из сброса для поглощения.";
            hint+=" · Осталось выбрать: "+Math.max(0,requestMax-requestCount);
            stripHeading(choiceLayer,heading,hint);
            var layout:Object=overviewLayout(requestCards.length,1800,440,12,230,54);
            var titleY:Number=Math.max(600,220+layout.blockH+24);
            mulliganTitle=text(choiceLayer,"",260,titleY,1400,28,0xF4EFE4);mulliganTitle.height=50;
            betaFace(BetaGwentFonts.TITLE,mulliganTitle,28,0xF4EFE4,false,"center");
            mulliganReading=text(choiceLayer,"",300,titleY+58,1320,24,0xD7D4CB);mulliganReading.height=920-titleY-58;
            betaFace(BetaGwentFonts.BODY,mulliganReading,24,0xD7D4CB);mulliganReading.mouseEnabled=true;
            var reading:TextField=mulliganReading;
            reading.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{reading.scrollV=Math.max(1,Math.min(reading.maxScrollV,reading.scrollV-e.delta*3));e.stopPropagation();});
            reading.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            var picked:Object=null,pickedDetail:Object=null;
            for(var i:int=0;i<requestCards.length;i++){
                var c:Object=requestCards[i],live:Object=null;
                for each(var hc:Object in cards)if(hc.id==c.id){live=hc;break;}
                var catalog:Object=c.revealed?BetaGwentCardText.find(c.templateId):null;
                var detail:Object=c.revealed?(cardDetails[c.id]||catalog||{description:""}):{description:""};
                var view:Object={id:c.id,title:c.revealed?c.templateId==113402?"Сбор · случайный отряд":c.title:"Рубашка",templateId:c.revealed?c.templateId:0,
                    side:requestPlayer,hidden:!c.revealed,power:live?live.power:catalog?catalog.power:0,normalPower:live?live.normalPower:catalog?catalog.power:0,
                    typeMask:c.revealed?detail.typeMask:0,tokens:c.revealed&&live?live.tokens:0,timer:c.revealed&&live?live.timer:-1,stripBody:mulliganReading};
                var row:int=int(i/layout.cols),column:int=i%layout.cols,inRow:int=Math.min(layout.cols,requestCards.length-row*layout.cols);
                var x:Number=60+(1800-(inRow*layout.w+(inRow-1)*18))/2+column*(layout.w+18);
                var tile:Sprite=compactOverviewCard(choiceLayer,view,detail,x,220+row*layout.stepY,layout.w,layout.h,layout.captionH);
                c.mulliganGlow=view.stripGlow;c.stripBody=mulliganReading;c.displayCard=view;c.displayDetail=detail;
                attachMulliganReading(tile,view,detail);attachRequestCard(tile,c.id,view,detail);
                if(!picked||c.id==mulliganPickedId||c.id==keyboardFocusId){picked=view;pickedDetail=detail;}
            }
            if(picked)showMulliganCard(picked,pickedDetail);
            else{mulliganTitle.text="Подходящих карт нет";mulliganReading.text=hint;}
            if(requestFinish&&!templateChoice&&!handPowerChoice)
                editorBetaButton(choiceLayer,requestCards.length==0?"Продолжить":pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):"Не поглощать",795,978,330,48,ready,requestAction("OnBetaGwentRequestFinish"));
            else betaLabel(choiceLayer,"Выбор обязателен — укажите карту",260,962,1400,22,0xD1CEC5,BetaGwentFonts.BODY,false,"center");
        }
        private function drawBetaConfirm(title:String,body:String,yes:Function,no:Function):void
        {
            var layer:Sprite=new Sprite();mulliganDialog=layer;choiceLayer.addChild(layer);
            layer.graphics.beginFill(0,.6);layer.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);layer.graphics.endFill();
            layer.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            paintArt(layer,BetaGwentHud104.POPUP,700,260,610,410);
            var bar:Sprite=new Sprite();layer.addChild(bar);paintArt(bar,BetaGwentHud104.POPUP_TITLE,660,52,630,428);
            betaLabel(layer,title,610,436,700,26,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",6);
            var text1:TextField=text(layer,body,650,502,620,20,0xE8E4DA);text1.height=60;betaFace(BetaGwentFonts.BODY,text1,20,0xE8E4DA,false,"center");
            editorBetaButton(layer,"Нет",980,580,240,48,true,no,!mulliganAnswer);
            editorBetaButton(layer,"Да",700,580,240,48,true,yes,mulliganAnswer);
        }
        private function drawChoices():void
        {
            var choiceOrder:Array=isMulliganHand()?sortedHand(requestCards):requestCards;
            if(skin==3&&requestKind==1){if(isMulliganHand())drawBetaMulligan();else drawBetaAbilityChoices();return;}
            content.addChild(choiceLayer);
            // Opaque hit surface stops clicks reaching the board behind choices.
            choiceLayer.graphics.clear();choiceLayer.graphics.beginFill(0,0.30);choiceLayer.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);choiceLayer.graphics.endFill();
            var modal:Sprite=betaWindow(choiceLayer,450,185,1000,660);
            if(pileChoice&&choiceOrder.length==0){
                text(modal,"Способность · подходящих карт нет",24,20,950,28,0xE9C46A).height=65;
                text(modal,requestMessage,36,150,920,26).height=200;
                button("Продолжить",1124,775,290,ready&&requestFinish,requestAction("OnBetaGwentRequestFinish"),choiceLayer);
                return;
            }
            text(modal,templateChoice?(rowMode==13?"Выберите вариант способности":rowMode==7?"Дагон · выберите погоду":"Рассвет · выберите вариант"):pileChoice?(rowMode==14?"Выберите карту для способности":"Выберите карту для розыгрыша"):handPowerChoice?"Выберите отряд в руке":graveyardChoice?"Поглощение · выберите отряд из сброса":"Замена карт · осталось "+(requestMax-requestCount),24,16,950,26,0xE9C46A);
            text(modal,templateChoice?(rowMode==13?"Наведите на вариант, чтобы прочитать действие. После выбора появятся допустимые цели.":rowMode==7?"Создайте Густой туман или Проливной дождь. Затем выберите ряд соперника.":"Чистое небо: очистить погоду. Сбор: разыграть случайный бронзовый отряд из колоды."):pileChoice?(rowMode==14?requestMessage:"Выбранная карта будет разыграна из колоды или сброса. Для отряда затем выберите место в ряду."):handPowerChoice?"Изначальная сила выбранного отряда определит эффект. Отряд останется в руке.":graveyardChoice?"Выберите один бронзовый или серебряный отряд. Его сила усилит Гуля; карта исчезнет из сброса.":"Нажмите карту, чтобы сразу заменить её. Можно сохранить руку и начать раунд раньше.",24,57,950,19);
            var pages:int=Math.max(1,Math.ceil(choiceOrder.length/12));
            choicePage=Math.min(choicePage,pages-1);
            for(var i:int=choicePage*12;i<Math.min(choiceOrder.length,(choicePage+1)*12);i++)
            {
                var c:Object=choiceOrder[i];
                var slot:int=i-choicePage*12;var visibleColumns:int=Math.min(6,choiceOrder.length-choicePage*12);
                var p:Sprite=betaFrame(modal,(1000-(visibleColumns*158-18))/2+(slot%6)*158,108+int(slot/6)*210,140,198);
                if(c.revealed)paintChoiceArt(p,c.templateId,134,188);betaNine(p,-1412,138,192,1,1);
                var band:Sprite=panel(p,3,143,134,52,0x101315,.87);band.mouseEnabled=false;
                var name:TextField=text(p,c.templateId==113402?"Сбор · случайный отряд":c.title,8,146,124,15);name.height=46;
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
                    if((int(c.tokens)&1)!=0)paintResilience(p,142,199);
                    attachInspect(p,c,cardDetails[c.id],140,198);
                }
                if(c.selected||keyboardFocusId==c.id){p.graphics.lineStyle(4,keyboardFocusId==c.id?0xF5E6A7:0xE9C46A);p.graphics.drawRect(2,2,136,194);}
                attachRequestCard(p,c.id);
            }
            text(modal,templateChoice?(rowMode==13?"Вариант выбирается для этого розыгрыша.":rowMode==7?"Выберите одну карту погоды, затем ряд противника.":"Нажмите вариант; затем выберите свой ряд, если разыгрывается отряд."):pileChoice?(rowMode==14?(requestFinish?"Выберите карту для способности.   ·   Страница ":"Выбор обязателен — укажите карту.   ·   Страница "):(requestFinish?"Выберите карту для розыгрыша.   ·   Страница ":"Розыгрыш обязателен — выберите карту.   ·   Страница "))+(choicePage+1)+" / "+pages:handPowerChoice?"Выберите одну карту.   ·   Страница "+(choicePage+1)+" / "+pages:graveyardChoice?"Можно завершить без поглощения.   ·   Страница "+(choicePage+1)+" / "+pages:"Заменено: "+requestCount+" / "+requestMax+"   ·   Страница "+(choicePage+1)+" / "+pages,24,548,900,18);
            button("Назад",474,775,180,ready&&choicePage>0,function():void{choicePage--;render();},choiceLayer);
            button("Вперёд",670,775,180,ready&&choicePage+1<pages,function():void{choicePage++;render();},choiceLayer);
            if(requestFinish&&!templateChoice&&!handPowerChoice)button(pileChoice?(rowMode==14?"Без выбора":"Без розыгрыша"):graveyardChoice?"Не поглощать":"Начать раунд",1124,775,290,ready&&requestFinish,requestAction("OnBetaGwentRequestFinish"),choiceLayer);
        }
        private function drawBacks():void
        {
            var count:int=Math.max(0,enemyHand);
            var backHeight:Number=skin==3?116:68;
            var backWidth:Number=skin==3?Math.round(116*BETA_CARD_ASPECT):46;
            var spacing:Number=skin==3?Math.min(backWidth+2,(782-backWidth)/Math.max(1,count-1)):Math.min(54,750/Math.max(1,count));
            if(skin!=3)backWidth=Math.min(46,Math.max(8,spacing-4));
            var backsLeft:Number=skin==3?1039-(spacing*Math.max(0,count-1)+backWidth)/2:630,backsTop:Number=skin==3?8:96;
            for(var i:int=0;i<count;i++){
                var back:Sprite=new Sprite();back.mouseEnabled=false;back.mouseChildren=false;content.addChild(back);
                back.x=backsLeft+i*spacing;back.y=backsTop;
                var exposed:Object=null;for each(var hc:Object in cards)if(hc.side==2&&hc.zone==8&&hc.index==i&&(hc.tokens&64)!=0)exposed=hc;
                if(exposed&&skin==3){paintBetaFace(back,exposed.templateId,backWidth,backHeight,2);betaPowerField(back,String(exposed.power),backWidth,backHeight,powerColor(exposed));paintRevealedMark(back,backWidth-15,backHeight-15);back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,backHeight);}
                else if(exposed){paintChoiceArt(back,exposed.templateId,backWidth,68);if(backWidth>=24)text(back,String(exposed.power),2,2,backWidth-4,14,powerColor(exposed));back.mouseEnabled=true;back.mouseChildren=true;attachInspect(back,exposed,cardDetails[exposed.id],backWidth,68);}
                else paintCardBack(back,backWidth,backHeight,2);
                if(activeCue&&activeCue.kind==14&&i>=previousEnemyHand&&enemyHand>previousEnemyHand){
                    var finalX:Number=back.x;
                    var drawX:Number=skin==3?betaDeckPoint(2)[0]:310;var drawY:Number=skin==3?betaDeckPoint(2)[1]:426;
                    animations.push({sprite:back,fromX:drawX,fromY:drawY,toX:finalX,toY:backsTop,appear:true,remove:false,
                        duration:380,arc:36,fromScaleX:.6,fromScaleY:.6,toScaleX:1,toScaleY:1});
                    back.x=drawX;back.y=drawY;back.scaleX=back.scaleY=.6;back.alpha=0;
                }
            }
        }
    }
}

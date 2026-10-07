// Separate development menu; requires BetaGwentBoard CMenuResource registration.
class CR4BetaGwentBoardMenu extends CR4Menu
{
    private var session : CBetaGwentDuelSession;
    private var duel : CBetaGwentDuelSession;
    private var pushStatus, pushTimer : CScriptedFlashFunction;
    private var setDetails, pushDetails, pushPlayRules : CScriptedFlashFunction;
    private var setWeather : CScriptedFlashFunction;
    private var beginVisualBatch, setVisualCue, setVisualTarget : CScriptedFlashFunction;
    private var visualBusy : bool;
    private var requestFlow : CBetaGwentDevelopmentRequestFlow;
    private var setRequestHeader : CScriptedFlashFunction;
    private var setRequestSource : CScriptedFlashFunction;
    private var pushRequestCard : CScriptedFlashFunction;
    private var revision : int;
    private var configured : bool;
    private var mouseCursorOwned : bool;
    private var setHeader : CScriptedFlashFunction;
    private var setCounts : CScriptedFlashFunction;
    private var pushCard : CScriptedFlashFunction;
    private var finishState : CScriptedFlashFunction;
    private var beginDeckSelection, pushDeckOption, pushDeckCard, finishDeckSelection : CScriptedFlashFunction;
    private var selectingDecks : bool;
    private var ownPreset, enemyPreset : int;
    private var ownLeader, enemyLeader : int;
    private var pushLeaderOption, setBoardLeaders, setPlacementCard : CScriptedFlashFunction;

    private var deckLibrary : CBetaGwentDeckLibrary;
    private var deckDraft : CBetaGwentDeckDraft;
    private var beginDeckEditor, pushEditorCard, finishDeckEditor, pushEditorCopies : CScriptedFlashFunction;
    private var pushTemplateDetails, pushTemplateRules, pushLiveStats : CScriptedFlashFunction;
    private var editorPublishedFaction : int;
    private var publishedTemplates : array<int>;
    private var selectionPublished : bool;
    private var beginPileView, pushPileCard, pushPilePowerBase, finishPileView : CScriptedFlashFunction;
    private var pileViewSequence : int;
    private var audio : CBetaGwentDuelAudio;
    private var audioRevisions : array<int>;
    private var audioFrames : array<CBetaGwentDuelVisualFrame>;
    private var setAudioStatus : CScriptedFlashFunction;
    private var setEntryContext : CScriptedFlashFunction;
    private var npcMatch, libraryOnly, kegOnly : bool;
    private var forcedBetaFaction : int;
    private var deckNameInput : CBetaGwentDeckNameInput;
    private var setEditorName : CScriptedFlashFunction;
    private var setOwnedCopies, setRewardMessage : CScriptedFlashFunction;
    private var rewardGranted : bool;
    private var beginKegOpening, pushKegCard, finishKegOpening : CScriptedFlashFunction;
    private var setControllerDevice, setControllerInput : CScriptedFlashFunction;
    private var setUnopenedKegs : CScriptedFlashFunction;

    event OnConfigUI()
    {
        var preferredCards : array<int>; var preferredLeader : int;
        var gameplayInputExceptions : array<EInputActionBlock>;
        var entryMode : int;var pendingBefore, requestedBefore : bool;var kegInit : CBetaGwentKegMenuData;
        var manager : CR4GwintManager; var npcPreset : SBetaGwentDuelPreset; var nativePlayer : CR4Player; var entryDefinition : SBetaGwentDuelDefinition;
        if (configured) return false;
        setHeader = GetMenuFlash().GetMemberFlashFunction("setBoardHeader");
        setControllerDevice = GetMenuFlash().GetMemberFlashFunction("setControllerDevice");
        setControllerInput = GetMenuFlash().GetMemberFlashFunction("setControllerInput");
        setUnopenedKegs = GetMenuFlash().GetMemberFlashFunction("setUnopenedKegs");
        setCounts = GetMenuFlash().GetMemberFlashFunction("setBoardCounts");
        pushCard = GetMenuFlash().GetMemberFlashFunction("pushBoardCard");
        finishState = GetMenuFlash().GetMemberFlashFunction("finishBoardState");
        setRequestHeader = GetMenuFlash().GetMemberFlashFunction("setRequestHeader");
        setRequestSource = GetMenuFlash().GetMemberFlashFunction("setRequestSource");
        pushRequestCard = GetMenuFlash().GetMemberFlashFunction("pushRequestCard");
        setDetails = GetMenuFlash().GetMemberFlashFunction("setBoardDetails");
        pushDetails = GetMenuFlash().GetMemberFlashFunction("pushCardDetails");
        pushPlayRules = GetMenuFlash().GetMemberFlashFunction("pushCardPlayRules");
        pushStatus = GetMenuFlash().GetMemberFlashFunction("pushCardStatus");
        pushTimer = GetMenuFlash().GetMemberFlashFunction("pushCardTimer");
        setWeather = GetMenuFlash().GetMemberFlashFunction("setWeatherRow");
        beginVisualBatch = GetMenuFlash().GetMemberFlashFunction("beginVisualBatch");
        setVisualCue = GetMenuFlash().GetMemberFlashFunction("setVisualCue");
        setVisualTarget = GetMenuFlash().GetMemberFlashFunction("setVisualTarget");
        beginDeckSelection = GetMenuFlash().GetMemberFlashFunction("beginDeckSelection");
        pushDeckOption = GetMenuFlash().GetMemberFlashFunction("pushDeckOption");
        pushDeckCard = GetMenuFlash().GetMemberFlashFunction("pushDeckCard");
        finishDeckSelection = GetMenuFlash().GetMemberFlashFunction("finishDeckSelection");
        pushLeaderOption = GetMenuFlash().GetMemberFlashFunction("pushLeaderOption");
        setBoardLeaders = GetMenuFlash().GetMemberFlashFunction("setBoardLeaders");
        setPlacementCard = GetMenuFlash().GetMemberFlashFunction("setPlacementCard");
        beginDeckEditor = GetMenuFlash().GetMemberFlashFunction("beginDeckEditor");
        pushEditorCard = GetMenuFlash().GetMemberFlashFunction("pushEditorCard");
        finishDeckEditor = GetMenuFlash().GetMemberFlashFunction("finishDeckEditor");
        pushEditorCopies = GetMenuFlash().GetMemberFlashFunction("pushEditorCopies");
        pushTemplateDetails = GetMenuFlash().GetMemberFlashFunction("pushTemplateDetails");
        pushTemplateRules = GetMenuFlash().GetMemberFlashFunction("pushTemplateRules");
        pushLiveStats = GetMenuFlash().GetMemberFlashFunction("pushLiveStats");
        beginPileView = GetMenuFlash().GetMemberFlashFunction("beginPileView");
        pushPileCard = GetMenuFlash().GetMemberFlashFunction("pushPileCard");
        pushPilePowerBase = GetMenuFlash().GetMemberFlashFunction("pushPilePowerBase");
        finishPileView = GetMenuFlash().GetMemberFlashFunction("finishPileView");
        setAudioStatus = GetMenuFlash().GetMemberFlashFunction("setAudioStatus");
        if (!setControllerDevice || !setControllerInput || !beginPileView || !pushPileCard || !pushPilePowerBase || !finishPileView || !pushEditorCopies || !pushTemplateDetails || !pushTemplateRules || !pushLiveStats || !beginDeckEditor || !pushEditorCard || !finishDeckEditor || !setVisualTarget || !pushPlayRules || !setPlacementCard || !setHeader || !setCounts || !pushCard || !finishState || !setRequestHeader || !pushRequestCard || !setDetails || !pushDetails || !pushStatus || !pushTimer || !setWeather || !beginVisualBatch || !setVisualCue || !beginDeckSelection || !pushDeckOption || !pushDeckCard || !finishDeckSelection || !pushLeaderOption || !setBoardLeaders)
        {
            LogChannel('BetaGwent', "BOARD_MISSING_FLASH_FUNCTION");
            CloseMenu();
            return false;
        }
        duel = new CBetaGwentDuelSession in this;
        session = duel;
        requestFlow = new CBetaGwentDevelopmentRequestFlow in this;
        deckLibrary = new CBetaGwentDeckLibrary in this;
        manager=theGame.GetGwintManager();nativePlayer=thePlayer;
        pendingBefore=manager.betaNpcPending;requestedBefore=manager.gameRequested;
        kegInit=(CBetaGwentKegMenuData)GetMenuInitData();kegOnly=false;if(kegInit)kegOnly=true;
        entryMode=BetaGwentNativeEntryMode(GetMenuName(),pendingBefore,requestedBefore);
        if(kegOnly)entryMode=1;
        npcMatch=entryMode==2;libraryOnly=entryMode==1;
        deckLibrary.Initialize(entryMode==0);
        nativePlayer.betaPracticeRequested=false;
        forcedBetaFaction=BetaGwentNativeFaction(manager.GetForcedFaction());
        selectingDecks = true; ownPreset = 3; enemyPreset = 2;
        ownLeader = 200055; enemyLeader = 200158;
        ownPreset = deckLibrary.Preferred();
        if (deckLibrary.Resolve(ownPreset, preferredCards, preferredLeader)) ownLeader = preferredLeader;
        if(npcMatch){
            enemyPreset=BetaGwentNpcPreset(manager.betaEnemyDeckName);
            npcPreset=BetaGwentDuelPreset(enemyPreset);enemyLeader=npcPreset.leaderTemplateId;
            entryDefinition=BetaGwentDuelDefinition(ownLeader);if(forcedBetaFaction!=0 && entryDefinition.header.factionMask!=forcedBetaFaction){ownPreset=BetaGwentStarterPreset(forcedBetaFaction);npcPreset=BetaGwentDuelPreset(ownPreset);ownLeader=npcPreset.leaderTemplateId;}
            manager.gameRequested=false;thePlayer.SetGwintMinigameState(EMS_None);
        }
        revision = 0;
        configured = true;
        setOwnedCopies=GetMenuFlash().GetMemberFlashFunction("setOwnedCopies");
        setRewardMessage=GetMenuFlash().GetMemberFlashFunction("setRewardMessage");
        beginKegOpening=GetMenuFlash().GetMemberFlashFunction("beginKegOpening");
        pushKegCard=GetMenuFlash().GetMemberFlashFunction("pushKegCard");
        finishKegOpening=GetMenuFlash().GetMemberFlashFunction("finishKegOpening");
        setEditorName=GetMenuFlash().GetMemberFlashFunction("setEditorName");
        setEntryContext=GetMenuFlash().GetMemberFlashFunction("setEntryContext");
        if(setEntryContext)setEntryContext.InvokeSelfThreeArgs(FlashArgInt(BetaGwentNorthPick(npcMatch,2,BetaGwentNorthPick(libraryOnly,1,0))),FlashArgString(BetaGwentEntryOpponentLabel(npcMatch,enemyPreset,manager.betaEnemyDeckName)),FlashArgInt(forcedBetaFaction));
        audio = new CBetaGwentDuelAudio in this; audio.Initialize();
        if (setAudioStatus) setAudioStatus.InvokeSelfTwoArgs(FlashArgBool(BetaGwentAudioBankInstalled()), FlashArgBool(audio.IsBankReady()));

        // Beta Gwent owns the game audio state for the whole lifetime of this menu,
        // not only for NPC matches. This suppresses the normal world mix in the
        // same way as native Gwent while keeping Beta Gwent's own audio bridge alive.
        theSound.EnterGameState(ESGS_Gwent);

        // EMPTY_CONTEXT redirects menu input, but physical keys can still reach
        // CPlayerInput through their gameplay bindings. Explicitly lock all player
        // actions so quick-slot items, signs, attacks, etc. cannot fire behind UI.
        theInput.StoreContext('EMPTY_CONTEXT');
        if (thePlayer)
            thePlayer.BlockAllActions('BetaGwentBoard', true, gameplayInputExceptions, false);

        RefreshControllerDevice(theInput.LastUsedGamepad());
        LogChannel('BetaGwent', "BOARD_CONFIGURED schema=1 fixture=false previewDuel=true");
        LogChannel('BetaGwent', "BOARD_ENTRY name="+GetMenuName()+" editorOnly="+libraryOnly+" npc="+npcMatch+" pending="+pendingBefore+" requested="+requestedBefore+" lifecycle=81d");
        PublishCollection();Publish(session.GetMessage());
        if(((W3PlayerWitcher)thePlayer).BetaGwentKegPending())OnBetaGwentKegOpen(revision);
        // The pause-menu entry starts at the saved-deck library. Editing and
        // creating a draft are explicit player actions, never automatic.
        // CR4GwintBaseMenu does this after its menu setup. Our replacement does
        // not inherit that class: release the native story-scene start fade.
        if(GetMenuName() == 'DeckBuilder' || GetMenuName() == 'GwintGame')
        {
            theGame.ResetFadeLock("GwintStart");
            theGame.FadeInAsync(0.2);
            LogChannel('BetaGwent',"NATIVE_GWENT_MENU_READY name="+GetMenuName()+" npc="+npcMatch+" startFadeReleased=true");
        }
    }

    event OnBetaGwentInspectPile(value : int, side : int, zone : int)
    {
        var views : array<SBetaGwentDevelopmentCard>; var order : array<int>;
        var presentationRandom : CBetaGwentRandomGenerator;
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i : int;
        // Do not call AcceptRevision/Publish here: those may pump the opponent.
        if (!configured || deckDraft || selectingDecks || visualBusy || value != revision) return false;
        if (!duel.GetInspectablePile(side, zone, views))
        { LogChannel('BetaGwent', "PILE_VIEW_REJECT side=" + side + " zone=" + zone); return false; }
        for (i = 0; i < views.Size(); i += 1) order.PushBack(i);
        // A separate, short-lived presentation RNG never touches match RNG or location indices.
        pileViewSequence = (pileViewSequence + 1) % 10000;
        presentationRandom = new CBetaGwentRandomGenerator in this;
        presentationRandom.Initialize(pileViewSequence * 104729 + (revision % 10000) * 7919 + side * 31 + zone);
        presentationRandom.Shuffle(order);
        beginPileView.InvokeSelfFourArgs(FlashArgInt(revision), FlashArgInt(side), FlashArgInt(zone), FlashArgInt(views.Size()));
        for (i = 0; i < order.Size(); i += 1)
        {
            s = views[order[i]].card; d = duel.FindCard(s.instanceId).Definition();
            // No instance ID, location index, original deck, or draw-position fields cross this bridge.
            pushPileCard.InvokeSelfNineArgs(FlashArgInt(s.runtimeTemplate.templateId), FlashArgString(views[order[i]].title),
                FlashArgString(d.description), FlashArgInt(s.power.currentPower), FlashArgInt(s.power.armor),
                FlashArgInt(s.runtimeTierMask), FlashArgInt(s.tokenMask), FlashArgInt(s.timerValue), FlashArgInt(s.runtimeTemplate.typeMask));
            pushPilePowerBase.InvokeSelfOneArg(FlashArgInt(s.power.basePower + s.power.permanentPower));
        }
        finishPileView.InvokeSelfOneArg(FlashArgInt(revision));
        LogChannel('BetaGwent', "PILE_VIEW side=" + side + " zone=" + zone + " count=" + views.Size() + " revision=" + revision);
        return true;
    }

    private function AcceptRevision(value : int) : bool
    {
        if (visualBusy) { LogChannel('BetaGwent', "BOARD_REJECT_VISUAL_BUSY revision=" + value); return false; }
        if (configured && !deckDraft && !selectingDecks && value == revision && !session.IsFatal()) return true;
        LogChannel('BetaGwent', "BOARD_REJECT_REVISION requested=" + value + " current=" + revision);
        if (configured) Publish("Снимок обновлён после устаревшего действия.");
        return false;
    }

    private function AcceptBoardAction(value : int) : bool
    {
        if (!AcceptRevision(value)) return false;
        if (requestFlow.IsPending() || duel.IsPending())
        { LogChannel('BetaGwent', "REQUEST_FLOW_REJECT board action while pending"); return false; }
        return true;
    }

    private function LogIntent(action : string, value : int, instanceId : int, row : int)
    {
        LogChannel('BetaGwent', "BOARD_INTENT action=" + action + " revision=" + value + " card=" + instanceId + " row=" + row);
    }

    private function Publish(status : string)
    {
        var frames : array<CBetaGwentDuelVisualFrame>; var frame : CBetaGwentDuelVisualFrame; var i : int;
        if (!configured) return;
        audioRevisions.Clear(); audioFrames.Clear();
        if (deckDraft) { PublishDeckEditor(status); return; }
        if (selectingDecks) { PublishDeckSelection(); return; }
        duel.PumpOpponent();
        if (!requestFlow.IsPending()) status = duel.GetMessage();
        duel.TakeVisualFrames(frames); visualBusy = frames.Size() > 0;
        beginVisualBatch.InvokeSelfOneArg(FlashArgInt(frames.Size() + 1));
        for (i = 0; i < frames.Size(); i += 1) PublishFrame(frames[i], true);
        frame = duel.VisualSnapshot(); frame.status = status;
        PublishFrame(frame, false);
        if (visualBusy) LogChannel('BetaGwent', "BOARD_VISUAL_BATCH frames=" + frames.Size() + " finalRevision=" + revision);
    }
    event OnBetaGwentKegOpen(value : int)
    {
        var ordinary,offers : array<int>;var i : int;var player : W3PlayerWitcher;
        var items : array<SItemUniqueId>;
        player=(W3PlayerWitcher)thePlayer;
        if(!configured || value!=revision || !player || !beginKegOpening || !pushKegCard || !finishKegOpening)return false;
        if(!player.BetaGwentKegPending()) {
            if(!libraryOnly || npcMatch || player.IsInCombat())return false;
            player.inv.GetAllItems(items);
            for(i=0;i<items.Size();i+=1)if(player.inv.GetItemName(items[i])=='betagwent_keg') {
                if(player.BetaGwentOpenInventoryKeg(items[i]))break;
                if(player.BetaGwentKegRareRemaining()==0 && player.inv.RemoveItem(items[i],1)) {
                    player.AddMoney(150);Publish("Все редкие карты собраны. Возвращено 150 крон.");return true;
                }
            }
            if(!player.BetaGwentKegPending()){Publish("В инвентаре нет бочек для открытия.");return false;}
        }
        PublishKegInventory();
        player.BetaGwentKegContents(ordinary,offers);beginKegOpening.InvokeSelfOneArg(FlashArgInt(revision));
        for(i=0;i<ordinary.Size();i+=1)pushKegCard.InvokeSelfTwoArgs(FlashArgInt(ordinary[i]),FlashArgBool(true));
        for(i=0;i<offers.Size();i+=1)pushKegCard.InvokeSelfTwoArgs(FlashArgInt(offers[i]),FlashArgBool(false));
        finishKegOpening.InvokeSelfOneArg(FlashArgInt(revision));return true;
    }
    event OnBetaGwentKegChoose(value : int, id : int)
    {
        var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
        if(!configured || value!=revision || !player || !player.BetaGwentChooseKeg(id)) { OnBetaGwentKegOpen(revision);return false; }
        if(kegOnly){CloseMenu();return true;}
        ((W3PlayerWitcher)thePlayer).BetaGwentEnsureCollection();
        PublishCollection();Publish("Карта добавлена в коллекцию.");return true;
    }
    private function PublishCollection()
    {
        var ids,leaders : array<int>;var i : int;var player : W3PlayerWitcher;
        player=(W3PlayerWitcher)thePlayer;if(!setOwnedCopies || !player)return;
        PublishKegInventory();
        BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
        for(i=0;i<leaders.Size();i+=1)ids.PushBack(leaders[i]);
        for(i=0;i<ids.Size();i+=1)setOwnedCopies.InvokeSelfTwoArgs(FlashArgInt(ids[i]),FlashArgInt(player.BetaGwentOwned(ids[i])));
    }
    private function AwardMatchReward()
    {
        var result : SBetaGwentMatchSnapshot;var player : W3PlayerWitcher;var manager : CR4GwintManager;var earnedText : string;
        if(!npcMatch || rewardGranted || selectingDecks)return;
        result=session.Snapshot();if(result.matchWinnerMask!=1)return;
        manager=theGame.GetGwintManager();if(manager.testMatch)return;
        player=(W3PlayerWitcher)thePlayer;if(!player)return;
        rewardGranted=true;earnedText=player.BetaGwentWinReward(manager.betaEnemyDeckName,manager.betaMatchNpcId);
        PublishCollection();if(setRewardMessage)setRewardMessage.InvokeSelfOneArg(FlashArgString(earnedText));
    }
    private function PublishDeckCards(option : int, ids : array<int>)
    {
        var seen : array<int>; var d : SBetaGwentDuelDefinition; var i, j, copies : int;
        for (i = 0; i < ids.Size(); i += 1)
        {
            if (seen.Contains(ids[i])) continue; seen.PushBack(ids[i]); copies = 0;
            for (j = 0; j < ids.Size(); j += 1) if (ids[j] == ids[i]) copies += 1;
            d = BetaGwentDuelDefinition(ids[i]);
            pushDeckCard.InvokeSelfNineArgs(FlashArgInt(option), FlashArgInt(ids[i]), FlashArgString(d.title),
                FlashArgString(d.description), FlashArgInt(d.header.power), FlashArgInt(d.header.armor),
                FlashArgInt(d.header.tierMask), FlashArgInt(d.header.typeMask), FlashArgInt(copies));
        }
    }
    private function PublishDeckSelection()
    {
        var ids, leaders : array<int>; var preset : SBetaGwentDuelPreset;
        var leader : SBetaGwentDuelDefinition; var option, i : int;
        var storedDeck : CBetaGwentDeckDraft; var validation : SBetaGwentDeckValidation;
        if (!configured || !selectingDecks || deckDraft) return;
        revision += 1; visualBusy = false;
        beginDeckSelection.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(ownPreset), FlashArgInt(enemyPreset), FlashArgInt(ownLeader), FlashArgInt(enemyLeader));
        BetaGwentDuelLeaders(leaders);
        for (i = 0; i < leaders.Size(); i += 1)
        {
            leader = BetaGwentDuelDefinition(leaders[i]);
            pushLeaderOption.InvokeSelfFourArgs(FlashArgInt(leaders[i]), FlashArgString(leader.title), FlashArgString(leader.description), FlashArgInt(leader.header.power));
        }
        if (!selectionPublished)
        {
            for (option = 1; option <= BetaGwentDuelPresetCount(); option += 1)
            {
                if((npcMatch || libraryOnly) && (option<16 || option>20) && option!=enemyPreset)continue;
                preset = BetaGwentDuelPreset(option); leader = BetaGwentDuelDefinition(preset.leaderTemplateId);
                pushDeckOption.InvokeSelfNineArgs(FlashArgInt(option), FlashArgString(preset.title), FlashArgString(preset.description),
                    FlashArgInt(preset.leaderTemplateId), FlashArgString(leader.title), FlashArgInt(preset.unitCount),
                    FlashArgInt(preset.specialCount), FlashArgInt(preset.goldCount), FlashArgInt(preset.silverCount));
                BetaGwentDuelPresetDeck(option, ids); PublishDeckCards(option, ids);
            }
            for (option = 1001; option <= 1008; option += 1)
            {
                storedDeck = deckLibrary.Get(option); if (!storedDeck) continue;
                validation = storedDeck.Validation(); if (!validation.valid) continue;
                leader = BetaGwentDuelDefinition(storedDeck.leader);
                pushDeckOption.InvokeSelfNineArgs(FlashArgInt(option), FlashArgString(storedDeck.title), FlashArgString("Своя колода · слот " + storedDeck.slot),
                    FlashArgInt(storedDeck.leader), FlashArgString(leader.title), FlashArgInt(validation.units),
                    FlashArgInt(validation.specials), FlashArgInt(validation.gold), FlashArgInt(validation.silver));
                PublishDeckCards(option, storedDeck.cards);
            }
            selectionPublished = true;
        }
        PublishKegInventory();finishDeckSelection.InvokeSelfOneArg(FlashArgInt(revision));
        LogChannel('BetaGwent', "BOARD_DECK_SELECTION revision=" + revision + " ownPreset=" + ownPreset + " enemyPreset=" + enemyPreset);
    }
    private function PublishDeckEditor(status : string)
    {
        var ids, leaders : array<int>; var i : int; var d : SBetaGwentDuelDefinition; var validation : SBetaGwentDeckValidation;
        if (!configured || !deckDraft) return;
        PublishKegInventory();
        revision += 1; visualBusy = false; validation = deckDraft.Validation();
        beginDeckEditor.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(deckDraft.slot), FlashArgInt(deckDraft.faction),
            FlashArgInt(deckDraft.leader), FlashArgString(deckDraft.title), FlashArgInt(validation.total),
            FlashArgInt(validation.gold), FlashArgInt(validation.silver), FlashArgBool(validation.valid));
        BetaGwentDuelLeaders(leaders);
        for (i = 0; i < leaders.Size(); i += 1)
        {
            d = BetaGwentDuelDefinition(leaders[i]);
            pushLeaderOption.InvokeSelfFourArgs(FlashArgInt(leaders[i]), FlashArgString(d.title), FlashArgString(d.description), FlashArgInt(d.header.power));
        }
        // Collection definitions are sent once per faction instead of once per +/- click.
        if (editorPublishedFaction != deckDraft.faction)
        {
            BetaGwentDuelCollection(ids);
            for (i = 0; i < ids.Size(); i += 1)
            {
                d = BetaGwentDuelDefinition(ids[i]); if (d.header.factionMask != 1 && (d.header.factionMask & deckDraft.faction) == 0) continue;
                pushEditorCard.InvokeSelfNineArgs(FlashArgInt(ids[i]), FlashArgString(d.title), FlashArgString(d.description),
                    FlashArgInt(d.header.power), FlashArgInt(d.header.tierMask), FlashArgInt(d.header.typeMask),
                    FlashArgInt(d.header.factionMask), FlashArgInt(0), FlashArgBool(false));
            }
            editorPublishedFaction = deckDraft.faction;
        }
        ids.Clear();
        for (i = 0; i < deckDraft.cards.Size(); i += 1)
        {
            if (ids.Contains(deckDraft.cards[i])) continue; ids.PushBack(deckDraft.cards[i]);
            pushEditorCopies.InvokeSelfTwoArgs(FlashArgInt(deckDraft.cards[i]), FlashArgInt(deckDraft.Copies(deckDraft.cards[i])));
        }
        if (status == "") status = validation.message;
        finishDeckEditor.InvokeSelfTwoArgs(FlashArgInt(revision), FlashArgString(status));
    }
    event OnBetaGwentDeckEditorOpen(value : int, id : int)
    {
        if (!configured || !selectingDecks || deckDraft || value != revision) return false;
        editorPublishedFaction = 0; deckDraft = deckLibrary.Edit(id);
        if (!deckDraft) { LogChannel('BetaGwent', "DECK_EDITOR_OPEN_REJECT fullOrInvalid=true"); PublishDeckSelection(); return false; }
        PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckEditorChange(value : int, id : int, amount : int)
    {
        if (!configured || !deckDraft || value != revision || (amount != 1 && amount != -1)) return false;
        if (deckDraft.Change(id, amount)) PublishDeckEditor(""); else PublishDeckEditor("Достигнут лимит карты, редкости или размера колоды.");
        return true;
    }
    event OnBetaGwentDeckEditorLeader(value : int, id : int)
    {
        var d : SBetaGwentDuelDefinition; var i : int;
        if (!configured || !deckDraft || value != revision) return false;
        LogChannel('BetaGwent',"DECK_EDITOR_LEADER_REQUEST revision="+value+" leader="+id);
        if (!BetaGwentDuelIsLeader(id)) {
            LogChannel('BetaGwent',"DECK_EDITOR_LEADER_REJECT reason=notLeader leader="+id);
            PublishDeckEditor("Выберите доступного лидера.");return false;
        }
        if(deckDraft.limitedCollection && ((W3PlayerWitcher)thePlayer).BetaGwentOwned(id)<1) {
            LogChannel('BetaGwent',"DECK_EDITOR_LEADER_REJECT reason=unowned leader="+id);
            PublishDeckEditor("Этот лидер ещё не получен. Источник указан в каталоге.");return false;
        }
        d = BetaGwentDuelDefinition(id);
        if(npcMatch && forcedBetaFaction!=0 && d.header.factionMask!=forcedBetaFaction) {
            PublishDeckEditor("Этот квест требует колоду указанной фракции.");return false;
        }
        if (d.header.factionMask != deckDraft.faction)
        {
            deckDraft.faction = d.header.factionMask;
            for (i = deckDraft.cards.Size() - 1; i >= 0; i -= 1)
            { d = BetaGwentDuelDefinition(deckDraft.cards[i]); if (d.header.factionMask != 1 && d.header.factionMask != deckDraft.faction) deckDraft.cards.Erase(i); }
        }
        deckDraft.leader = id; PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckRename(value : int, title : string)
    {
        if (!configured || !deckDraft || value != revision || !setEditorName) return false;
        if (!deckNameInput) deckNameInput = new CBetaGwentDeckNameInput in this;
        if(!deckNameInput.Open(this, value, title, 0))return false;
        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(0),FlashArgString(title),FlashArgBool(true));
        return true;
    }
    event OnBetaGwentDeckNameSubmit(value : int, title : string)
    {
        if(!configured || !deckDraft || value!=revision || StrLen(title)==0)return false;
        ReceiveDeckName(value,title);return true;
    }
    private function PublishKegInventory()
    {
        var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
        if(setUnopenedKegs && player)setUnopenedKegs.InvokeSelfTwoArgs(FlashArgInt(player.inv.GetItemQuantityByName('betagwent_keg')),FlashArgBool(player.BetaGwentKegPending()));
    }
    public function RefreshControllerDevice(active : bool)
    {
        var config : CInGameConfigWrapper;var swapped : bool;
        if(!configured || !setControllerDevice)return;
        config=(CInGameConfigWrapper)theGame.GetInGameConfigWrapper();
        if(config)swapped=config.GetVarValue('Controls','SwapAcceptCancel');
        setControllerDevice.InvokeSelfThreeArgs(FlashArgUInt(theInput.GetLastUsedGamepadType()),FlashArgBool(active),FlashArgBool(swapped));
        // RequestMouseCursor is a reference count, not a visibility setter.
        // Device refreshes and keyboard returns must not accumulate requests.
        SetOwnedMouseCursor(!active);
    }
    private function SetOwnedMouseCursor(visible : bool)
    {
        if(mouseCursorOwned==visible)return;
        theGame.GetGuiManager().RequestMouseCursor(visible);
        mouseCursorOwned=visible;
    }
    event OnBetaGwentControllerDevice(active : bool)
    { RefreshControllerDevice(active || theInput.LastUsedGamepad());return true; }
    event OnBetaGwentControllerTrace(code : int, action : string, mode : string, focus : string)
    {
        LogChannel('BetaGwent',"CONTROLLER_INPUT code="+code+" action="+action+" mode="+mode+" focus="+focus);
        return true;
    }
    event OnBetaGwentControllerSearch(value : int, purpose : int, title : string)
    {
        if(!configured || value!=revision || !setControllerInput || (purpose!=1 && purpose!=2))return false;
        if(purpose==1 && !deckDraft)return false;
        if(!deckNameInput)deckNameInput=new CBetaGwentDeckNameInput in this;
        if(!deckNameInput.Open(this,value,title,purpose))return false;
        setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(purpose),FlashArgString(title),FlashArgBool(true));return true;
    }
    public function FinishControllerText(value : int, purpose : int, title : string)
    {
        if(purpose==0)ReceiveDeckName(value,title);
        if(configured && setControllerInput)setControllerInput.InvokeSelfFourArgs(FlashArgInt(value),FlashArgInt(purpose),FlashArgString(title),FlashArgBool(false));
        RefreshControllerDevice(theInput.LastUsedGamepad());
    }
    public function ReceiveDeckName(value : int, title : string)
    {
        if (!configured || !deckDraft || value != revision || StrLen(title)==0) return;
        title=StrLeft(title,48);deckDraft.title=title;
        setEditorName.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgString(title));
        LogChannel('BetaGwent',"DECK_RENAMED slot="+deckDraft.slot);
    }
    event OnBetaGwentDeckEditorSave(value : int, title : string)
    {
        if (!configured || !deckDraft || value != revision) return false;
        if (!deckLibrary.Save(deckDraft, title)) { PublishDeckEditor("Не удалось сохранить колоду. Проверьте состав и имя."); return false; }
        selectionPublished = false; ownPreset = 1000 + deckDraft.slot; ownLeader = deckDraft.leader; deckLibrary.Remember(ownPreset); deckDraft = NULL;
        selectingDecks = true; PublishDeckSelection(); return true;
    }
    event OnBetaGwentDeckEditorCancel(value : int)
    {
        if (!configured || !deckDraft || value != revision) return false;
        deckDraft = NULL; selectingDecks = true; PublishDeckSelection(); return true;
    }
    event OnBetaGwentDeckEditorClear(value : int)
    {
        if (!configured || !deckDraft || value != revision) return false;
        deckDraft.cards.Clear(); PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckSelect(value : int, side : int, presetId : int)
    {
        var cards : array<int>; var leader : int;var chosen : SBetaGwentDuelDefinition;
        if (!configured || !selectingDecks || deckDraft || value != revision || (side != 1 && side != 2)) return false;
        if (!deckLibrary.Resolve(presetId, cards, leader)) { PublishDeckSelection();return false; }
        if(side==1 && (npcMatch || libraryOnly) && !((W3PlayerWitcher)thePlayer).BetaGwentOwnsDeck(cards,leader)){PublishDeckSelection();return false;}
        chosen=BetaGwentDuelDefinition(leader);if(npcMatch && (side==2 || (forcedBetaFaction!=0 && chosen.header.factionMask!=forcedBetaFaction))){PublishDeckSelection();return false;}
        if (side == 1) { ownPreset = presetId; ownLeader = leader; deckLibrary.Remember(ownPreset); } else { enemyPreset = presetId; enemyLeader = leader; }
        PublishDeckSelection(); return true;
    }
    event OnBetaGwentLeaderSelect(value : int, side : int, templateId : int)
    {
        var cards : array<int>; var presetLeader : int; var chosen, original : SBetaGwentDuelDefinition;
        if (!configured || !selectingDecks || deckDraft || value != revision || (side != 1 && side != 2)) return false;
        if (!BetaGwentDuelIsLeader(templateId)) { PublishDeckSelection();return false; }
        if (side == 1) { if (!deckLibrary.Resolve(ownPreset,cards,presetLeader)) {PublishDeckSelection();return false;} } else { if (!deckLibrary.Resolve(enemyPreset,cards,presetLeader)) {PublishDeckSelection();return false;} }
        if(side==1 && (npcMatch || libraryOnly) && ((W3PlayerWitcher)thePlayer).BetaGwentOwned(templateId)<1){PublishDeckSelection();return false;}
        chosen = BetaGwentDuelDefinition(templateId); original = BetaGwentDuelDefinition(presetLeader);
        if(npcMatch && (side==2 || (forcedBetaFaction!=0 && chosen.header.factionMask!=forcedBetaFaction))){PublishDeckSelection();return false;}
        if (chosen.header.factionMask != original.header.factionMask) {PublishDeckSelection();return false;}
        if (side == 1) ownLeader = templateId; else enemyLeader = templateId;
        PublishDeckSelection(); return true;
    }
    private function StartSelectedDuel() : bool
    {
        var ownCards, enemyCards : array<int>; var leader : int;var chosen : SBetaGwentDuelDefinition;
        chosen=BetaGwentDuelDefinition(ownLeader);if(libraryOnly || (npcMatch && forcedBetaFaction!=0 && chosen.header.factionMask!=forcedBetaFaction))return false;
        if(npcMatch && ((W3PlayerWitcher)thePlayer).BetaGwentKegPending()){OnBetaGwentKegOpen(revision);return false;}
        if (audio) audio.Cancel(); audioRevisions.Clear(); audioFrames.Clear();
        requestFlow.Close(); visualBusy = false;
        if (!deckLibrary.Resolve(ownPreset, ownCards, leader) || !deckLibrary.Resolve(enemyPreset, enemyCards, leader)) return false;
        if(npcMatch && !((W3PlayerWitcher)thePlayer).BetaGwentOwnsDeck(ownCards,ownLeader))return false;
        if (!session.InitializeWithDecks(ownCards, enemyCards, ownLeader, enemyLeader, ownPreset, enemyPreset)) return false;
        selectingDecks = false; Publish(session.GetMessage()); return true;
    }
    event OnBetaGwentDeckStart(value : int)
    {
        if (!configured || !selectingDecks || deckDraft || value != revision) return false;
        if(StartSelectedDuel())return true;
        if(selectingDecks && !((W3PlayerWitcher)thePlayer).BetaGwentKegPending()) {
            LogChannel('BetaGwent',"DECK_START_REJECT returningToSelection=true");PublishDeckSelection();
        }
        return false;
    }
    private function PublishCardTemplate(id : int)
    {
        var d : SBetaGwentDuelDefinition; var side : int;
        if (publishedTemplates.Contains(id)) return;
        d = BetaGwentDuelDefinition(id); side = d.targetSide; if (d.weatherToken != 0) side = 2;
        pushTemplateDetails.InvokeSelfFourArgs(FlashArgInt(id), FlashArgString(d.description), FlashArgInt(d.header.tierMask), FlashArgInt(d.header.typeMask));
        pushTemplateRules.InvokeSelfEightArgs(FlashArgInt(id), FlashArgInt(duel.DirectSpecialKind(d)), FlashArgInt(side),
            FlashArgInt(d.targetTypes), FlashArgInt(d.targetTiers), FlashArgInt(d.targetIgnore), FlashArgInt(d.consumeMaximum), FlashArgInt(d.specialRowMask));
        publishedTemplates.PushBack(id);
    }

    private function PublishFrame(frame : CBetaGwentDuelVisualFrame, intermediate : bool)
    {
        var snapshot : SBetaGwentMatchSnapshot;
        var entries : array<SBetaGwentDevelopmentCard>;
        var cardView : SBetaGwentDevelopmentCard;
        var requestSnapshot : SBetaGwentRequestSnapshot;
        var requestCards : array<SBetaGwentDevelopmentRequestCard>;
        var requestView : SBetaGwentDevelopmentRequestCard;
        var flags : int;
        var i, side, row, weatherIndex, j : int;
        var cardDefinition : SBetaGwentDuelDefinition;
        var leaderDefinition : SBetaGwentDuelDefinition;
        var placement : CBetaGwentDuelCard; var placementState : SBetaGwentCardSnapshot;
        var details : string;
        if (!configured) return;
        revision += 1;
        if (frame.kind > 0) { audioRevisions.PushBack(revision); audioFrames.PushBack(frame); }
        snapshot = frame.matchState; flags = frame.flags;
        setHeader.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(snapshot.roundNumber),
            FlashArgInt(snapshot.currentPlayerId), FlashArgInt(frame.scoreOne), FlashArgInt(frame.scoreTwo),
            FlashArgInt(snapshot.playerOne.crowns), FlashArgInt(snapshot.playerTwo.crowns), FlashArgInt(flags), FlashArgString(frame.status));
        setCounts.InvokeSelfFiveArgs(FlashArgInt(frame.enemyHand), FlashArgBool(frame.leaderOne),
            FlashArgBool(frame.leaderTwo), FlashArgInt(frame.graveOne), FlashArgInt(frame.graveTwo));
        cardDefinition = BetaGwentDuelDefinition(ownLeader);
        leaderDefinition = BetaGwentDuelDefinition(enemyLeader);
        setBoardLeaders.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(ownLeader), FlashArgInt(enemyLeader),
            FlashArgString(cardDefinition.title), FlashArgString(leaderDefinition.title));
        if (!intermediate) placement = duel.PlacementCard();
        if (placement)
        {
            placementState = placement.Snapshot(); leaderDefinition = placement.Definition();
            setPlacementCard.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(placementState.runtimeTemplate.templateId),
                FlashArgString(leaderDefinition.title), FlashArgInt(placementState.power.currentPower), FlashArgInt(placementState.runtimeTierMask));
        }
        else setPlacementCard.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(0), FlashArgString(""), FlashArgInt(0), FlashArgInt(0));
        for (side = 1; side <= 2; side += 1)
            for (row = 1; row <= 4; row *= 2)
            {
                setWeather.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(side), FlashArgInt(row),
                    FlashArgInt(frame.weatherTokens[weatherIndex]), FlashArgInt(frame.weatherDamage[weatherIndex]));
                weatherIndex += 1;
            }
        entries = frame.cards;
        details = "Дуэль · перемешивание и замена 3/1/1";
        if (duel.IsRowRequest()) details = "Выбор ряда";
        row = 0; if (!intermediate) row = RowMode();
        if (setDetails) setDetails.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(frame.deckOne),
            FlashArgInt(frame.deckTwo), FlashArgString(cardDefinition.title), FlashArgInt(row));
        for (i = 0; i < entries.Size(); i += 1)
        {
            cardView = entries[i];
            // Hidden enemy hand is represented only by a count in the view.
            if (cardView.card.positionPlayerId == 2 && cardView.card.locationMask == 8 && (cardView.card.tokenMask&64)==0) continue;
            if (cardView.card.locationMask == 64 || cardView.card.locationMask == 32 || cardView.card.locationMask == 16
                || cardView.card.locationMask == 128 || cardView.card.locationMask == 256) continue;
            if (cardView.card.positionPlayerId==2 && (cardView.card.locationMask&7)!=0 && (cardView.card.tokenMask&8)!=0)
            {
                pushCard.InvokeSelfNineArgs(FlashArgInt(cardView.card.instanceId),FlashArgString("Засада"),FlashArgInt(0),FlashArgInt(0),
                    FlashArgInt(2),FlashArgInt(cardView.card.locationMask),FlashArgInt(cardView.card.locationIndex),FlashArgBool(false),FlashArgInt(0));
                pushStatus.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId),FlashArgInt(8));
                pushTimer.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId),FlashArgInt(-1));
                if(pushDetails)pushDetails.InvokeSelfFourArgs(FlashArgInt(cardView.card.instanceId),FlashArgString("Скрытая засада соперника."),FlashArgInt(0),FlashArgInt(4));
                continue;
            }
            PublishCardTemplate(cardView.card.runtimeTemplate.templateId);
            pushCard.InvokeSelfNineArgs(FlashArgInt(cardView.card.instanceId), FlashArgString(cardView.title),
                FlashArgInt(cardView.card.power.currentPower), FlashArgInt(cardView.card.power.armor),
                FlashArgInt(cardView.card.positionPlayerId), FlashArgInt(cardView.card.locationMask),
                FlashArgInt(cardView.card.locationIndex), FlashArgBool(cardView.card.canBePlayed), FlashArgInt(cardView.card.runtimeTemplate.templateId));
            pushLiveStats.InvokeSelfFiveArgs(FlashArgInt(cardView.card.instanceId), FlashArgInt(cardView.card.tokenMask), FlashArgInt(cardView.card.timerValue), FlashArgInt(cardView.card.power.basePower + cardView.card.power.permanentPower), FlashArgBool(cardView.createdCopy));
        }
        if (!intermediate)
        {
            if (duel.IsPending()) requestSnapshot = duel.GetRequestSnapshot();
            else requestSnapshot = requestFlow.Snapshot();
        }
        setRequestHeader.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(requestSnapshot.requestId),
            FlashArgInt(requestSnapshot.playerId), FlashArgInt((int)requestSnapshot.kind),
            FlashArgInt(requestSnapshot.limits.minimum), FlashArgInt(requestSnapshot.limits.maximum),
            FlashArgInt(requestSnapshot.selectedCount), FlashArgBool(!intermediate && (duel.IsPending() && requestSnapshot.limits.minimum == 0
                || !duel.IsPending() && requestFlow.CanFinish())), FlashArgString(frame.status));
        if (setRequestSource) setRequestSource.InvokeSelfTwoArgs(FlashArgInt(revision), FlashArgInt(duel.PendingSourceId()));
        if (!intermediate)
        {
            if (duel.IsPending()) duel.GetRequestViews(requestCards);
            else requestFlow.GetViews(requestCards);
        }
        for (i = 0; i < requestCards.Size(); i += 1)
        {
            requestView = requestCards[i];
            if (duel.IsTemplateChoice() || duel.IsGraveyardChoice() || duel.IsPileChoice())
            {
                cardDefinition = BetaGwentDuelViewDefinition(requestView.templateId);
                pushDetails.InvokeSelfFourArgs(FlashArgInt(requestView.id), FlashArgString(cardDefinition.description), FlashArgInt(cardDefinition.header.tierMask), FlashArgInt(cardDefinition.header.typeMask));
            }
            if (duel.IsGraveyardChoice() || duel.IsPileChoice())
            {
                // Stage only the pending own-pile candidates; never send the whole hidden deck.
                // AS3 skips Deck/Graveyard in field/hand rendering; these are choice-only views.
                for (j = 0; j < entries.Size(); j += 1)
                {
                    cardView = entries[j];
                    if (cardView.card.instanceId != requestView.id || !requestView.revealed || (cardView.card.locationMask != 32 && cardView.card.locationMask != 16)) continue;
                    if (cardView.card.positionPlayerId==2 && (cardView.card.locationMask&7)!=0 && (cardView.card.tokenMask&8)!=0)
            {
                pushCard.InvokeSelfNineArgs(FlashArgInt(cardView.card.instanceId),FlashArgString("Засада"),FlashArgInt(0),FlashArgInt(0),
                    FlashArgInt(2),FlashArgInt(cardView.card.locationMask),FlashArgInt(cardView.card.locationIndex),FlashArgBool(false),FlashArgInt(0));
                pushStatus.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId),FlashArgInt(8));
                pushTimer.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId),FlashArgInt(-1));
                if(pushDetails)pushDetails.InvokeSelfFourArgs(FlashArgInt(cardView.card.instanceId),FlashArgString("Скрытая засада соперника."),FlashArgInt(0),FlashArgInt(4));
                continue;
            }
            pushCard.InvokeSelfNineArgs(FlashArgInt(cardView.card.instanceId), FlashArgString(cardView.title),
                        FlashArgInt(cardView.card.power.currentPower), FlashArgInt(cardView.card.power.armor),
                        FlashArgInt(cardView.card.positionPlayerId), FlashArgInt(cardView.card.locationMask), FlashArgInt(cardView.card.locationIndex), FlashArgBool(false), FlashArgInt(requestView.templateId));
                    pushStatus.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId), FlashArgInt(cardView.card.tokenMask));
                    pushTimer.InvokeSelfTwoArgs(FlashArgInt(cardView.card.instanceId), FlashArgInt(cardView.card.timerValue));
                    pushLiveStats.InvokeSelfFiveArgs(FlashArgInt(cardView.card.instanceId), FlashArgInt(cardView.card.tokenMask), FlashArgInt(cardView.card.timerValue), FlashArgInt(cardView.card.power.basePower + cardView.card.power.permanentPower), FlashArgBool(cardView.createdCopy));
                    break;
                }
            }
            pushRequestCard.InvokeSelfSixArgs(FlashArgInt(requestView.id), FlashArgString(requestView.title),
                FlashArgInt(requestView.templateId), FlashArgInt(requestView.factionId),
                FlashArgBool(requestView.revealed), FlashArgBool(requestView.selected));
        }
        setVisualCue.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(frame.kind + 256 * Min(255, Max(1, frame.attackCount))), FlashArgInt(frame.sourceId),
            FlashArgInt(frame.targetId), FlashArgInt(frame.side), FlashArgInt(frame.row), FlashArgInt(frame.templateId),
            FlashArgInt(frame.duration), FlashArgString(frame.status));
        setVisualTarget.InvokeSelfFiveArgs(FlashArgInt(revision), FlashArgInt(frame.targetTemplateId), FlashArgInt(frame.targetPower),
            FlashArgInt(frame.targetSide), FlashArgInt(frame.targetZone));
        finishState.InvokeSelfOneArg(FlashArgInt(revision));
        LogChannel('BetaGwent', "REQUEST_FLOW_VIEW revision=" + revision + " id=" + requestSnapshot.requestId
            + " kind=" + (int)requestSnapshot.kind + " count=" + requestSnapshot.selectedCount);
        LogChannel('BetaGwent', "BOARD_VIEW revision=" + revision + " round=" + snapshot.roundNumber
            + " current=" + snapshot.currentPlayerId + " score=" + frame.scoreOne + ":" + frame.scoreTwo + " flags=" + flags);
    }
    event OnBetaGwentVisualDone(value : int)
    {
        if (!configured || selectingDecks || value != revision) return false;
        audioRevisions.Clear(); audioFrames.Clear();
        visualBusy = false;
        AwardMatchReward();LogChannel('BetaGwent', "BOARD_VISUAL_DONE revision=" + value); return true;
    }

    event OnBetaGwentAudioCue(value : int)
    {
        var i, kind, id, j, token, targetTokens, rowIndex : int; var frame : CBetaGwentDuelVisualFrame; var s : SBetaGwentCardSnapshot;
        if (!configured || !audio) return false;
        for (i = 0; i < audioRevisions.Size(); i += 1)
        {
            if (audioRevisions[i] != value) continue;
            frame = audioFrames[i]; audioRevisions.Erase(i); audioFrames.Erase(i);
            kind = frame.kind; if (frame.audioKind != 0) kind = frame.audioKind;
            id = frame.templateId;
            // Hidden enemy ambush never identifies itself through a sound or a spoken line.
            for (j = 0; j < frame.cards.Size(); j += 1)
            {
                s = frame.cards[j].card;
                if (s.instanceId == frame.targetId) targetTokens = s.tokenMask;
                if (s.instanceId == frame.sourceId && s.positionPlayerId == 2 && (s.tokenMask & 8) != 0) id = 0;
            }
            if (frame.side > 0 && frame.row > 0)
            {
                rowIndex = (frame.side - 1) * 3;
                if (frame.row == 2) rowIndex += 1; else if (frame.row == 4) rowIndex += 2;
                if (rowIndex < frame.weatherTokens.Size()) token = frame.weatherTokens[rowIndex];
            }
            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens); return true;
        }
        return false;
    }
    event OnBetaGwentAudioIntro(opponent : int, player : int)
    { if (!configured || !audio) return false; audio.Intro(opponent, player); return true; }
    event OnBetaGwentAudioUi(kind : int)
    { if (!configured || !audio) return false; audio.Ui(kind); return true; }
    event OnBetaGwentUIError(detail : string)
    { LogChannel('BetaGwent', "UI_ERROR " + detail); }
    event OnBetaGwentPerf(eventName : string, ms : int)
    { if (configured && duel) duel.AiPerfFeedback(ms); }
    event OnBetaGwentAudioTick(clock : int)
    { if (configured && audio) { if (clock > 0) audio.SetClock(clock); audio.Tick(); if(setAudioStatus)setAudioStatus.InvokeSelfTwoArgs(FlashArgBool(BetaGwentAudioBankInstalled()),FlashArgBool(audio.IsBankReady())); } }
    event OnBetaGwentAudioSettings(effects : bool, voices : bool)
    { if (configured && audio) audio.Configure(effects, voices); }
    event OnBetaGwentAudioCancel()
    {
        audioRevisions.Clear(); audioFrames.Clear();
        if (audio) audio.Cancel();
    }

    private function RowMode() : int
    {
        if (duel.IsCaranthirMoveRequest()) return 15 + duel.CaranthirRow();
        if (duel.IsLeaderRowRequest()) return 2;
        if (duel.IsRallyRowRequest()) return 4;
        if (duel.IsWeatherRowRequest()) return 3;
        if (duel.IsDagonChoice()) return 7;
        if (duel.IsFirstLightChoice()) return 5;
        if (duel.IsModeChoice()) return 13;
        if (duel.IsPileChoice()) { if (duel.IsPlayChoice()) return 12; return 14; }
        if (duel.IsHandPowerChoice()) return 11;
        if (duel.IsGraveyardChoice()) return 6;
        if (duel.SpecialRowMode() != 0) return duel.SpecialRowMode();
        if (duel.IsRowRequest()) return 1;
        return 0;
    }
    event OnBetaGwentArtworkFailure(reason : string)
    {
        LogChannel('BetaGwent', "BOARD_ARTWORK_FAILURE " + reason);
    }
    event OnBetaGwentArtworkStatus(decoded : int, failed : int)
    {
        LogChannel('BetaGwent', "BOARD_ARTWORK decoded=" + decoded + " failed=" + failed);
    }
    event OnBetaGwentBoardPlay(value : int, instanceId : int, row : int)
    {
        LogIntent("play", value, instanceId, row);
        if (!AcceptBoardAction(value)) return false;
        if (session.Play(1, instanceId, row)) Publish(session.GetMessage());
        else Publish("Размещение отклонено: проверьте ход, карту и ряд.");
    }
    event OnBetaGwentBoardPlayTarget(value : int, instanceId : int, targetId : int)
    {
        LogIntent("play_target", value, instanceId, targetId);
        if (!AcceptBoardAction(value)) return false;
        if (session.PlayOnTarget(1, instanceId, targetId)) Publish(session.GetMessage());
        else Publish("Особая карта: цель отклонена, выберите подходящий отряд.");
    }
    event OnBetaGwentBoardPlayRowTarget(value : int, instanceId : int, side : int, row : int)
    {
        LogIntent("play_row_target", value, instanceId, row);
        if (!AcceptBoardAction(value)) return false;
        if (session.PlayOnRow(1, instanceId, side, row)) Publish(session.GetMessage());
        else Publish("Особая карта: ряд отклонён.");
    }
    event OnBetaGwentBoardPlayBefore(value : int, instanceId : int, anchorId : int)
    {
        LogIntent("play_before", value, instanceId, anchorId);
        if (!AcceptBoardAction(value)) return false;
        if (session.PlayBefore(1, instanceId, anchorId)) Publish(session.GetMessage());
        else Publish("Нет места для отряда перед выбранной картой.");
    }
    event OnBetaGwentDuelPlaceBefore(value : int, requestId : int, anchorId : int)
    {
        LogIntent("pending_place_before", value, requestId, anchorId);
        if (!AcceptRevision(value)) return false;
        if (duel.SelectPlacementBefore(requestId, anchorId)) Publish(session.GetMessage());
        else Publish("Размещение отклонено: выберите живого союзника в незаполненном ряду.");
    }
    event OnBetaGwentBoardPass(value : int)
    {
        LogIntent("pass", value, 0, 0);
        if (!AcceptBoardAction(value)) return false;
        if (session.Pass(1)) Publish(session.GetMessage());
        else Publish("Пас отклонён.");
    }
    event OnBetaGwentBoardLeader(value : int)
    {
        LogIntent("leader", value, 0, 0);
        if (!AcceptBoardAction(value)) return false;
        if (session.UseLeader(1)) Publish(session.GetMessage());
        else Publish("DEV лидер недоступен.");
    }
    event OnBetaGwentBoardOpponentStep(value : int)
    {
        LogIntent("opponent", value, 0, 0);
        if (!AcceptBoardAction(value)) return false;
        if (session.OpponentStep()) Publish(session.GetMessage());
        else Publish("Шаг соперника отклонён.");
    }
    event OnBetaGwentBoardNextRound(value : int)
    {
        LogIntent("nextRound", value, 0, 0);
        if (!AcceptBoardAction(value)) return false;
        if (session.BeginNextRound()) Publish(session.GetMessage());
        else Publish("Переход в следующий раунд отклонён.");
    }
    event OnBetaGwentBoardRestart(value : int)
    {
        LogIntent("restart", value, 0, 0);
        // Restart is an explicit escape from presentation; queued rules are already complete.
        if (npcMatch || !configured || value != revision) return false;
        if (audio) audio.Cancel(); audioRevisions.Clear(); audioFrames.Clear();
        visualBusy = false;
        deckDraft = NULL; requestFlow.Close();
        selectingDecks = true;
        Publish(session.GetMessage());
    }
    event OnBetaGwentBoardRematch(value : int)
    {
        // Every new duel passes through deck selection/editor, keeping the previous selections.
        if (npcMatch || !configured || selectingDecks || value != revision) return false;
        if (audio) audio.Cancel(); audioRevisions.Clear(); audioFrames.Clear();
        visualBusy = false; requestFlow.Close(); deckDraft = NULL; selectingDecks = true;
        PublishDeckSelection(); return true;
    }
    private function BetaGwentEntryOpponentLabel(npc : bool, preset : int, deck : name) : string
    { if(npc && preset>=54)return BetaGwentAIArchetypeName(preset); return NameToString(deck); }
    event OnBetaGwentRequestBegin(value : int, kind : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>;
        if (!AcceptRevision(value)) return false;
        if (duel.IsPending()) return false;
        session.GetCards(cards);
        if (requestFlow.Begin(kind, cards)) Publish(requestFlow.GetMessage());
        else { LogChannel('BetaGwent', "REQUEST_FLOW_REJECT begin kind=" + kind); Publish("Действие запроса отклонено; снимок обновлён."); }
    }
    event OnBetaGwentRequestSelect(value : int, requestId : int, playerId : int, kind : int, itemId : int)
    {
        LogChannel('BetaGwent', "UI_REQUEST_SELECT revision=" + value + " id=" + requestId + " kind=" + kind + " item=" + itemId);
        if (!AcceptRevision(value)) return false;
        if (duel.IsPending())
        {
            if (playerId != 1) return false;
            if (duel.IsMulligan() && kind == 1) duel.SelectMulligan(requestId, itemId);
            else if (duel.IsTemplateChoice() && kind == 1) duel.SelectTemplateChoice(requestId, itemId);
            else if ((duel.IsGraveyardChoice() || duel.IsHandPowerChoice() || duel.IsPileChoice()) && kind == 1) duel.SelectTarget(requestId, itemId);
            else if (!duel.IsMulligan() && !duel.IsGraveyardChoice() && !duel.IsPileChoice() && kind == 2) duel.SelectTarget(requestId, itemId);
            else return false;
            Publish(session.GetMessage()); return true;
        }
        if (requestFlow.Select(requestId, playerId, kind, itemId)) Publish(requestFlow.GetMessage());
        else { LogChannel('BetaGwent', "REQUEST_FLOW_REJECT selection id=" + requestId + " item=" + itemId); Publish("Действие запроса отклонено; снимок обновлён."); }
    }
    event OnBetaGwentRequestFinish(value : int, requestId : int, playerId : int, kind : int)
    {
        LogChannel('BetaGwent', "UI_REQUEST_FINISH revision=" + value + " id=" + requestId + " kind=" + kind);
        if (!AcceptRevision(value)) return false;
        if (duel.IsPending())
        {
            if (playerId != 1) return false;
            if (duel.IsMulligan() && kind == 1) duel.FinishMulligan(requestId);
            else if ((duel.IsGraveyardChoice() || duel.IsPileChoice()) && kind == 1) duel.FinishTarget(requestId);
            else if (!duel.IsMulligan() && !duel.IsGraveyardChoice() && !duel.IsPileChoice() && kind == 2) duel.FinishTarget(requestId);
            else return false;
            Publish(session.GetMessage()); return true;
        }
        if (requestFlow.Finish(requestId, playerId, kind)) Publish(requestFlow.GetMessage());
        else { LogChannel('BetaGwent', "REQUEST_FLOW_REJECT finish id=" + requestId); Publish("Действие запроса отклонено; снимок обновлён."); }
    }
    event OnBetaGwentRequestAbort(value : int, requestId : int, playerId : int, kind : int)
    {
        if (!AcceptRevision(value)) return false;
        if (duel.IsPending()) { Publish("Сыгранная карта ожидает цель. Для новой партии нажмите Заново."); return false; }
        if (requestFlow.Abort(requestId, playerId, kind)) Publish(requestFlow.GetMessage());
        else { LogChannel('BetaGwent', "REQUEST_FLOW_REJECT abort id=" + requestId); Publish("Действие запроса отклонено; снимок обновлён."); }
    }
    event OnBetaGwentBoardChecks()
    {
        var runner : CBetaGwentCoreChecks;
        var boardRunner : CBetaGwentDevelopmentBoardChecks;
        var requestRunner : CBetaGwentRequestChecks;
        var flowRunner : CBetaGwentRequestFlowChecks;
        if (!configured || visualBusy) return false;
        runner = new CBetaGwentCoreChecks in this;
        runner.Run();
        boardRunner = new CBetaGwentDevelopmentBoardChecks in this;
        boardRunner.Run();
        requestRunner = new CBetaGwentRequestChecks in this;
        requestRunner.Run();
        flowRunner = new CBetaGwentRequestFlowChecks in this;
        flowRunner.Run();
        Publish(runner.GetDisplaySummary() + "\n" + boardRunner.GetDisplaySummary() + "\n" + requestRunner.GetDisplaySummary() + "\n" + flowRunner.GetDisplaySummary());
    }
    event OnBetaGwentDuelRowTarget(value : int, requestId : int, side : int, row : int)
    {
        LogIntent("ability_row", value, requestId, side * 8 + row);
        if (!AcceptRevision(value)) return false;
        duel.SelectRow(requestId, side, row); Publish(session.GetMessage());
    }
    event OnCloseMenu()
    {
        var safeBack : CScriptedFlashFunction;
        safeBack=GetMenuFlash().GetMemberFlashFunction("requestCloseFromGame");
        if(safeBack)safeBack.InvokeSelfOneArg(FlashArgInt(0));
    }
    event OnBetaGwentBoardClose() { CloseMenu(); }
    event OnClosingMenu()
    {
        var manager : CR4GwintManager; var result : SBetaGwentMatchSnapshot;var inventoryParent : CR4InventoryMenu;
        var gameplayInputExceptions : array<EInputActionBlock>;
        if(npcMatch){
            AwardMatchReward();manager=theGame.GetGwintManager();if(!selectingDecks)result=session.Snapshot();
            if(!selectingDecks && result.matchWinnerMask==1)thePlayer.SetGwintMinigameState(EMS_End_PlayerWon);
            else if(!selectingDecks && result.matchWinnerMask!=0)thePlayer.SetGwintMinigameState(EMS_End_PlayerLost);
            else thePlayer.SetGwintMinigameState(EMS_End_PlayerLost | EMS_End_PlayerForfeited);
            manager.gameRequested=false;manager.betaNpcPending=false;manager.SetHasDoneTutorial(true);manager.SetHasDoneDeckTutorial(true);
            if(!manager.testMatch && theGame.isUserSignedIn()){theGame.FadeOutAsync(0);theGame.SetFadeLock("Gwint_EndFadeOut");}
            manager.testMatch=false;manager.SetForcedFaction(GwintFaction_Neutral);
            LogChannel('BetaGwent',"NATIVE_GWENT_RESULT deck="+manager.betaEnemyDeckName+" winner="+result.matchWinnerMask+" state="+thePlayer.GetGwintMinigameState());
        }
        if (audio) audio.Close(); audio = NULL; audioRevisions.Clear(); audioFrames.Clear();
        if (configured)
        {
            deckDraft = NULL; requestFlow.Close();

            // Always restore gameplay input before returning to the world.
            if (thePlayer)
                thePlayer.BlockAllActions('BetaGwentBoard', false, gameplayInputExceptions, false);
            theInput.RestoreContext('EMPTY_CONTEXT', true);

            // Balanced with EnterGameState() in OnConfigUI for every entry mode.
            theSound.LeaveGameState(ESGS_Gwent);
            theSound.SoundEvent("system_resume");

            SetOwnedMouseCursor(false);
            configured = false;
        }
        if(kegOnly) {
            inventoryParent=(CR4InventoryMenu)GetParent();
            if(inventoryParent) inventoryParent.UpdateAllItemData();
            ((W3PlayerWitcher)thePlayer).BetaGwentEnsureCollection();
        }
        LogChannel('BetaGwent', "BOARD_CLOSED revision=" + revision);
    }
}

exec function bgboard_open()
{
    var nativePlayer : CR4Player;
    if (theGame.GetGuiManager().IsAnyMenu())
    {
        LogChannel('BetaGwent', "BOARD_OPEN_SKIPPED existing menu");
        return;
    }
    LogChannel('BetaGwent', "BOARD_OPEN_REQUEST name=BetaGwentBoard");
    nativePlayer=thePlayer;nativePlayer.betaPracticeRequested=true;
    theGame.RequestMenu('BetaGwentBoard');
}

exec function bgboard_close()
{
    var menu : CR4BetaGwentBoardMenu;
    menu = (CR4BetaGwentBoardMenu)theGame.GetGuiManager().GetRootMenu();
    if (menu) menu.CloseMenu();
}

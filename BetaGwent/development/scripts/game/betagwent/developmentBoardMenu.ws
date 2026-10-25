struct SBetaGwentClearedDeck
{
    var cards : array<int>;
    var faction : int;
}
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
    // Stage 131: the opponent thinks after the player's move has been shown, not before it,
    // so placing a card never stalls on the AI's simulations.
    private var deferredOpponent : bool;
    private var deferredVoiceAt : float;
    private var opponentPreparationBusy : bool;
    private var opponentPreparationFinished : bool;
    private var opponentPreparationMs, opponentPreparationPeakMs : int;
    private var originalOpponent, originalFailure : bool;
    private var originalRuntime : CBetaOriginalRuntime;
    private var originalPersonality : CBetaOriginalPersonality;
    private var originalController : CBetaOriginalTurnController;
    private var originalStartedAt : float;
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
    private var pushDestination : CScriptedFlashFunction;
    private var finishState : CScriptedFlashFunction;
    private var beginDeckSelection, pushDeckOption, pushDeckCard, finishDeckSelection : CScriptedFlashFunction;
    private var markDeckEdited : CScriptedFlashFunction; // optional: starter deck has a saved override
    private var markDeckInvalid : CScriptedFlashFunction; // optional: why a listed deck cannot start
    private var selectingDecks : bool;
    private var ownPreset, enemyPreset : int;
    private var ownLeader, enemyLeader : int;
    private var pushLeaderOption, setBoardLeaders, setPlacementCard : CScriptedFlashFunction;

    private var deckLibrary : CBetaGwentDeckLibrary;
    private var deckDraft : CBetaGwentDeckDraft;
    private var beginDeckEditor, pushEditorCard, finishDeckEditor, pushEditorCopies : CScriptedFlashFunction;
    private var pushTemplateDetails, pushTemplateRules, pushLiveStats : CScriptedFlashFunction;
    private var editorPublishedFaction : int;
    private var deckClearHistory : array<SBetaGwentClearedDeck>;
    private var finishKegChoice : CScriptedFlashFunction;
    private var kegCanOpenNext : bool;
    private var effectGallery : bool;
    private var startEffectGallery : CScriptedFlashFunction;
    private var publishedTemplates : array<int>;
    private var setCollectionNew : CScriptedFlashFunction;
    private var selectionPublished : bool;
    private var deckOptionCount : int;
    private var beginPileView, pushPileCard, pushPilePowerBase, finishPileView : CScriptedFlashFunction;
    private var pileViewSequence : int;
    private var audio : CBetaGwentDuelAudio;
    private var audioRevisions : array<int>;
    private var audioFrames : array<CBetaGwentDuelVisualFrame>;
    private var spellLaunchRevisions : array<int>;
    private var setAudioStatus : CScriptedFlashFunction;
    private var setLeaderMotion : CScriptedFlashFunction;
    private var setBoardHelp : CScriptedFlashFunction;
    private var setIntroAudioState : CScriptedFlashFunction;
    private var setIntroVoiceStart : CScriptedFlashFunction;
    private var introAudioSerial : int;
    private var setTutorialSeen : CScriptedFlashFunction;
    private var setTextLanguage : CScriptedFlashFunction;
    private var setLanguageSettings : CScriptedFlashFunction;
    private var presentationTempo : int;
    private var presentationReduced : bool;
    private var presentationAiPause : int;
    private var presentationDifficulty : int;
    private var setEntryContext : CScriptedFlashFunction;
    private var npcMatch, libraryOnly, kegOnly, kegNested, kegSwitch : bool;
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
        var presentationPlayer : W3PlayerWitcher;
        var gameplayInputExceptions : array<EInputActionBlock>;
        var entryMode : int;var pendingBefore, requestedBefore : bool;var kegInit : CBetaGwentKegMenuData;
        var manager : CR4GwintManager; var npcPreset : SBetaGwentDuelPreset; var nativePlayer : CR4Player; var entryDefinition : SBetaGwentDuelDefinition;
        if (configured) return false;
        LogChannel('BetaGwent', "MENU_CONFIG_BEGIN menu="+GetMenuName());
        setHeader = GetMenuFlash().GetMemberFlashFunction("setBoardHeader");
        setControllerDevice = GetMenuFlash().GetMemberFlashFunction("setControllerDevice");
        setControllerInput = GetMenuFlash().GetMemberFlashFunction("setControllerInput");
        setUnopenedKegs = GetMenuFlash().GetMemberFlashFunction("setUnopenedKegs");
        setCounts = GetMenuFlash().GetMemberFlashFunction("setBoardCounts");
        pushCard = GetMenuFlash().GetMemberFlashFunction("pushBoardCard");
        pushDestination = GetMenuFlash().GetMemberFlashFunction("pushCardDestination");
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
        markDeckEdited = GetMenuFlash().GetMemberFlashFunction("markDeckEdited");
        markDeckInvalid = GetMenuFlash().GetMemberFlashFunction("markDeckInvalid");
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
        setCollectionNew=GetMenuFlash().GetMemberFlashFunction("setCollectionNew");
        beginPileView = GetMenuFlash().GetMemberFlashFunction("beginPileView");
        pushPileCard = GetMenuFlash().GetMemberFlashFunction("pushPileCard");
        pushPilePowerBase = GetMenuFlash().GetMemberFlashFunction("pushPilePowerBase");
        finishPileView = GetMenuFlash().GetMemberFlashFunction("finishPileView");
        setAudioStatus = GetMenuFlash().GetMemberFlashFunction("setAudioStatus");
        setLeaderMotion = GetMenuFlash().GetMemberFlashFunction("setLeaderMotion");
        setBoardHelp = GetMenuFlash().GetMemberFlashFunction("setBoardHelp");
        setIntroAudioState = GetMenuFlash().GetMemberFlashFunction("setIntroAudioState");
        setIntroVoiceStart = GetMenuFlash().GetMemberFlashFunction("setIntroVoiceStart");
        setTutorialSeen = GetMenuFlash().GetMemberFlashFunction("setTutorialSeen");
        setTextLanguage = GetMenuFlash().GetMemberFlashFunction("setTextLanguage");
        setLanguageSettings = GetMenuFlash().GetMemberFlashFunction("setLanguageSettings");
        if (!setControllerDevice || !setControllerInput || !beginPileView || !pushPileCard || !pushPilePowerBase || !finishPileView || !pushEditorCopies || !pushTemplateDetails || !pushTemplateRules || !pushLiveStats || !beginDeckEditor || !pushEditorCard || !finishDeckEditor || !setVisualTarget || !pushPlayRules || !setPlacementCard || !setHeader || !setCounts || !pushCard || !pushDestination || !finishState || !setRequestHeader || !pushRequestCard || !setDetails || !pushDetails || !pushStatus || !pushTimer || !setWeather || !beginVisualBatch || !setVisualCue || !beginDeckSelection || !pushDeckOption || !pushDeckCard || !finishDeckSelection || !pushLeaderOption || !setBoardLeaders)
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
        effectGallery=(bool)((CBetaGwentEffectGalleryData)GetMenuInitData());
        startEffectGallery=GetMenuFlash().GetMemberFlashFunction("startEffectGallery");
        kegInit=(CBetaGwentKegMenuData)GetMenuInitData();kegOnly=false;kegNested=false;if(kegInit)kegOnly=true;
        // Opened over the deck editor: the parent menu already owns input, audio state and the cursor.
        if(kegOnly && (CR4BetaGwentBoardMenu)GetParent())kegNested=true;
        entryMode=BetaGwentNativeEntryMode(GetMenuName(),pendingBefore,requestedBefore);
        if(nativePlayer.betaPracticeRequested)entryMode=0;
        if(kegOnly)entryMode=1;
        if(effectGallery)entryMode=0;
        npcMatch=entryMode==2;libraryOnly=entryMode==1;
        deckLibrary.Initialize(entryMode==0);
        nativePlayer.betaPracticeRequested=false;
        forcedBetaFaction=BetaGwentNativeFaction(manager.GetForcedFaction());
        selectingDecks = true; ownPreset = 3; enemyPreset = 2;
        ownLeader = 200055; enemyLeader = 200158;
        ownPreset = deckLibrary.Preferred();
        if (deckLibrary.Resolve(ownPreset, preferredCards, preferredLeader)) ownLeader = preferredLeader;
        if(entryMode==0 && !effectGallery){
            enemyPreset=manager.betaDebugEnemyPreset;manager.betaDebugEnemyPreset=0;
            if(!BetaGwentDebugOpponentAllowed(enemyPreset))enemyPreset=BetaGwentAIRandomPreset();
            npcPreset=BetaGwentDuelPreset(enemyPreset);enemyLeader=npcPreset.leaderTemplateId;
            LogChannel('BetaGwent',"DEBUG_OPPONENT_SELECTED preset="+enemyPreset+" archetype="+BetaGwentAIArchetypeName(enemyPreset)+" source=practice_entry");
        }
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
        finishKegChoice=GetMenuFlash().GetMemberFlashFunction("finishKegChoice");
        pushKegCard=GetMenuFlash().GetMemberFlashFunction("pushKegCard");
        finishKegOpening=GetMenuFlash().GetMemberFlashFunction("finishKegOpening");
        setEditorName=GetMenuFlash().GetMemberFlashFunction("setEditorName");
        setEntryContext=GetMenuFlash().GetMemberFlashFunction("setEntryContext");
        if(setEntryContext)setEntryContext.InvokeSelfThreeArgs(FlashArgInt(BetaGwentNorthPick(npcMatch,2,BetaGwentNorthPick(libraryOnly,1,0))),FlashArgString(BetaGwentEntryOpponentLabel(npcMatch,enemyPreset,manager.betaEnemyDeckName)),FlashArgInt(forcedBetaFaction));
        audio = new CBetaGwentDuelAudio in this; audio.Initialize();
        presentationPlayer=(W3PlayerWitcher)thePlayer;presentationTempo=10;presentationAiPause=1;presentationDifficulty=3;
        if(presentationPlayer){presentationTempo=presentationPlayer.BetaGwentAnimationTempo();presentationReduced=presentationPlayer.BetaGwentReducedEffects();presentationAiPause=presentationPlayer.BetaGwentAiPause();presentationDifficulty=presentationPlayer.BetaGwentDifficulty();}
        if (setAudioStatus) setAudioStatus.InvokeSelfSixArgs(FlashArgBool(BetaGwentAudioBankInstalled()), FlashArgBool(audio.IsBankReady()),FlashArgInt(presentationTempo),FlashArgBool(presentationReduced),FlashArgInt(presentationAiPause),FlashArgInt(presentationDifficulty));
        if(setLeaderMotion)setLeaderMotion.InvokeSelfOneArg(FlashArgBool(FactsQueryLatestValue("bg_static_leaders")==0));
        if(setBoardHelp)setBoardHelp.InvokeSelfOneArg(FlashArgBool(FactsQueryLatestValue("bg_hide_help")==0));
        // The tutorial is offered once before the first game; the flag lives in facts, so it survives saves made without the mod.
        BetaGwentInitializeLanguages();
        PublishLanguageSettings();
        if (setTutorialSeen) setTutorialSeen.InvokeSelfOneArg(FlashArgBool(FactsQueryLatestValue("bg_tutorial_seen") > 0));

        // Beta Gwent owns the game audio state for the whole lifetime of this menu,
        // not only for NPC matches. This suppresses the normal world mix in the
        // same way as native Gwent while keeping Beta Gwent's own audio bridge alive.
        if(!kegNested)theSound.EnterGameState(ESGS_Gwent);

        // EMPTY_CONTEXT redirects menu input, but physical keys can still reach
        // CPlayerInput through their gameplay bindings. Explicitly lock all player
        // actions so quick-slot items, signs, attacks, etc. cannot fire behind UI.
        if(!kegNested){
            theInput.StoreContext('EMPTY_CONTEXT');
            if (thePlayer)
                thePlayer.BlockAllActions('BetaGwentBoard', true, gameplayInputExceptions, false);
        }

        RefreshControllerDevice(theInput.LastUsedGamepad());
        LogChannel('BetaGwent', "BOARD_CONFIGURED schema=1 fixture=false previewDuel=true");
        LogChannel('BetaGwent', "BOARD_ENTRY name="+GetMenuName()+" editorOnly="+libraryOnly+" npc="+npcMatch+" pending="+pendingBefore+" requested="+requestedBefore+" lifecycle=81d");
        if(effectGallery && startEffectGallery)startEffectGallery.InvokeSelfOneArg(FlashArgBool(true));
        else {PublishCollection();Publish(session.GetMessage());}
        if(kegOnly && ((W3PlayerWitcher)thePlayer).BetaGwentKegPending())OnBetaGwentKegOpen(revision);
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

    private function OpponentTurnWaiting() : bool
    {
        var m : SBetaGwentMatchSnapshot;
        if(originalOpponent)return OriginalNeedsStep();
        if (duel.IsPending() || duel.IsWaitingRound() || duel.IsFatal()) return false;
        m = duel.Snapshot(); return m.currentPlayerId == 2 && m.matchWinnerMask == 0;
    }
    private function OriginalPrivateRequest() : bool
    { return originalOpponent && duel && duel.IsPending() && duel.RequestDecisionSide()==2; }
    private function EmptyHandPassWaiting() : bool
    {
        var m : SBetaGwentMatchSnapshot;
        if(!duel || !duel.match || duel.IsFatal() || duel.IsWaitingRound() || duel.IsPending())return false;
        m=duel.Snapshot();return m.matchWinnerMask==0 && m.turnActive && m.currentPlayerId==1
            && !m.playerOne.hasPassed && duel.CountLocation(1,8)==0 && !duel.LeaderAvailable(1);
    }
    private function OriginalNeedsStep() : bool
    {
        var m : SBetaGwentMatchSnapshot;
        if(!originalOpponent || originalFailure || !duel || duel.IsFatal() || duel.IsWaitingRound())return false;
        if(originalController && !originalController.finished && !originalController.failed)return true;
        if(duel.IsPending())return duel.RequestDecisionSide()==2;
        m=duel.Snapshot();return m.currentPlayerId==2 && m.matchWinnerMask==0;
    }
    private function OriginalDifficultyChangeAllowed(level : int) : bool
    {
        var m : SBetaGwentMatchSnapshot;
        if(selectingDecks || !duel || !duel.match)return true;
        m=duel.Snapshot();if(m.matchWinnerMask!=0)return true;
        // Existing1..3 may still change during a match. Enter/leave the new
        // policy only at a new duel boundary, never midway through a search.
        return level<=3 && !originalOpponent;
    }
    private function StopOriginalOpponent(detail : string)
    {
        originalFailure=true;deferredOpponent=false;opponentPreparationBusy=false;
        LogChannel('BetaGwent',"ORIGINAL_BETA_FAILURE "+detail);
        duel.message="Ошибка ИИ беты. Подробности записаны в scriptslog.txt.";
        Publish(duel.GetMessage(),true);
    }
    private function ResumeOriginalOpponent()
    {
        var picker : CBetaOriginalMulligan;var result : SBetaOriginalLiveStep;var elapsed : int;var now : float;
        if(originalFailure || !OriginalNeedsStep())return;
        opponentPreparationBusy=true;
        if(duel.mulligan && duel.RequestDecisionSide()==2 && !originalController) {
            picker=new CBetaOriginalMulligan in this;picker.personality=originalPersonality;
            if(!picker.Step(duel)){StopOriginalOpponent("Original live mulligan rejected");return;}
            deferredOpponent=OriginalNeedsStep();opponentPreparationBusy=false;Publish(duel.GetMessage(),true);return;
        }
        now=theGame.GetEngineTimeAsSeconds();if(audio)now=audio.CurrentTime();
        if(!originalController) {
            originalStartedAt=now;originalController=new CBetaOriginalTurnController in this;
            if(!originalController.Start(duel,originalRuntime,originalPersonality)){StopOriginalOpponent(originalController.error);return;}
            opponentPreparationBusy=false;return;
        }
        elapsed=Max(0,(int)((now-originalStartedAt)*1000.0f));result=originalController.Step(elapsed);
        if(originalController.failed){StopOriginalOpponent(originalController.error);return;}
        if(result.finished) {
            LogChannel('BetaGwent',"ORIGINAL_BETA_TURN callbacks="+originalController.searchCallbacks+" forced="+originalController.forceRequested+" playmaker="+originalController.playmakerError);
            originalController=NULL;opponentPreparationFinished=true;
        }
        deferredOpponent=OriginalNeedsStep();opponentPreparationBusy=false;
        // Search is read-only. Publish only actual live replay/mulligan steps;
        // the existing audio tick/visual-done boundary schedules the next one.
        if(result.phase=="replay" && result.mutations>0)Publish(duel.GetMessage(),true);
    }
    private function Publish(status : string, optional opponentPumped : bool)
    {
        var frames : array<CBetaGwentDuelVisualFrame>; var frame : CBetaGwentDuelVisualFrame; var i : int;
        if (!configured) return;
        audioRevisions.Clear(); audioFrames.Clear();
        if (deckDraft) { PublishDeckEditor(status); return; }
        if (selectingDecks) { PublishDeckSelection(); return; }
        if(opponentPumped)duel.ClearAiPreparation();
        else if (originalOpponent) { if(OriginalNeedsStep())deferredOpponent=true; }
        else if (OpponentTurnWaiting() && (duel.visualFrames.Size() > 0 || !duel.AiPreparationIsReady()))
        { deferredOpponent = true; LogChannel('BetaGwent', "AI_TURN_DEFERRED frames=" + duel.visualFrames.Size()); }
        else {duel.PumpOpponent();duel.ClearAiPreparation();}
        if(OpponentTurnWaiting())deferredOpponent=true;
        if(EmptyHandPassWaiting())deferredOpponent=true;
        if (!requestFlow.IsPending()) status = duel.GetMessage();
        if(originalOpponent && OriginalNeedsStep())status="Ход соперника";
        duel.TakeVisualFrames(frames); visualBusy = frames.Size() > 0;
        beginVisualBatch.InvokeSelfOneArg(FlashArgInt(frames.Size() + 1));
        for (i = 0; i < frames.Size(); i += 1) PublishFrame(frames[i], true);
        frame = duel.VisualSnapshot(); frame.status = status;
        PublishFrame(frame, false);
        if (visualBusy) LogChannel('BetaGwent', "BOARD_VISUAL_BATCH frames=" + frames.Size() + " finalRevision=" + revision);
    }
    event OnBetaGwentKegOpen(value : int)
    {
        var ordinary,offers : array<int>;var i,kegScraps : int;var player : W3PlayerWitcher;
        var items : array<SItemUniqueId>;
        player=(W3PlayerWitcher)thePlayer;
        if(!configured || value!=revision || !player || !beginKegOpening || !pushKegCard || !finishKegOpening)return false;
        if(!player.BetaGwentKegPending()) {
            if(!libraryOnly || npcMatch || player.IsInCombat() || (kegOnly && !kegCanOpenNext))return false;
            kegCanOpenNext=false;
            player.BetaGwentOpenKeg();
            if(!player.BetaGwentKegPending()){
                PublishKegInventory();
                if(kegOnly && finishKegChoice)finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(true));
                else Publish("Нет неоткрытых бочек.");return false;
            }
        }
        if(!kegOnly) {
            // Stage 110: kegs open only from the deck editor. Two ~55 MiB menus cannot be
            // resident together, so the editor closes, BetaGwentKeg opens as the root menu
            // and reopens the editor when it closes (see OnClosingMenu).
            if(npcMatch)return false;
            kegSwitch=true;LogChannel('BetaGwent',"KEG_MENU_SWITCH from="+GetMenuName());CloseMenu();return true;
        }
        revision+=1;kegCanOpenNext=false;player.BetaGwentBackupProfile();PublishCollection();
        player.BetaGwentKegContents(ordinary,offers);beginKegOpening.InvokeSelfOneArg(FlashArgInt(revision));
        for(i=0;i<ordinary.Size();i+=1)pushKegCard.InvokeSelfThreeArgs(FlashArgInt(ordinary[i]),FlashArgBool(true),FlashArgInt(player.BetaGwentKegReceivedScraps(i)));
        for(i=0;i<offers.Size();i+=1){kegScraps=0;if(player.BetaGwentOwned(offers[i])>=BetaGwentCollectionCap(offers[i]))kegScraps=BetaGwentMillValue(offers[i]);pushKegCard.InvokeSelfThreeArgs(FlashArgInt(offers[i]),FlashArgBool(false),FlashArgInt(kegScraps));}
        finishKegOpening.InvokeSelfOneArg(FlashArgInt(revision));return true;
    }
    event OnBetaGwentKegChoose(value : int, id : int)
    {
        var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
        if(!configured || value!=revision || !player || !finishKegChoice || !player.BetaGwentKegPending())return false;
        if(!player.BetaGwentChooseKeg(id)){
            finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(false));return false;
        }
        revision+=1;kegCanOpenNext=true;player.BetaGwentBackupProfile();
        if(kegOnly){PublishCollection();finishKegChoice.InvokeSelfTwoArgs(FlashArgInt(revision),FlashArgBool(true));return true;}
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
        for(i=0;i<ids.Size();i+=1){
            setOwnedCopies.InvokeSelfTwoArgs(FlashArgInt(ids[i]),FlashArgInt(player.BetaGwentOwned(ids[i])));
            if(setCollectionNew)setCollectionNew.InvokeSelfTwoArgs(FlashArgInt(ids[i]),FlashArgBool(player.BetaGwentCardIsNew(ids[i])));
        }
        // Id -1 carries the scraps balance; it is sent last so the catalog can refresh once.
        setOwnedCopies.InvokeSelfTwoArgs(FlashArgInt(-1),FlashArgInt(player.BetaGwentScraps()));
    }
    // Catalog crafting: create a card from scraps, or mill a spare copy into scraps.
    event OnBetaGwentCollectionSeen(id : int)
    {
        var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
        if(!configured || effectGallery || !selectingDecks || !player || !setCollectionNew)return false;
        player.BetaGwentCardSeen(id);setCollectionNew.InvokeSelfTwoArgs(FlashArgInt(id),FlashArgBool(player.BetaGwentCardIsNew(id)));
        return true;
    }
    event OnBetaGwentCollectionCraft(id : int)
    {
        var player : W3PlayerWitcher;var d : SBetaGwentDuelDefinition;player=(W3PlayerWitcher)thePlayer;
        // The NPC deck-selection screen also hosts the collection and deck editor.
        // Crafting is allowed there, but never after the battle has started.
        if(!configured || !player || !selectingDecks) {
            LogChannel('BetaGwent',"COLLECTION_CRAFT_REJECT card="+id+" configured="+configured+" selectingDecks="+selectingDecks+" npcMatch="+npcMatch);
            return false;
        }
        LogChannel('BetaGwent',"COLLECTION_CRAFT_REQUEST card="+id+" npcMatch="+npcMatch+" copies="+player.BetaGwentOwned(id)+" scraps="+player.BetaGwentScraps());
        d=BetaGwentDuelDefinition(id);
        if(player.BetaGwentCraft(id)){PublishCollection();CollectionStatus("Создана карта: "+d.title+" (−"+BetaGwentCraftCost(id)+" осколков).");return true;}
        PublishCollection();CollectionStatus("Не хватает осколков или карта уже собрана.");return false;
    }
    event OnBetaGwentCollectionMill(id : int)
    {
        var player : W3PlayerWitcher;var d : SBetaGwentDuelDefinition;player=(W3PlayerWitcher)thePlayer;
        if(!configured || !player || npcMatch)return false;
        d=BetaGwentDuelDefinition(id);
        if(player.BetaGwentMill(id)){PublishCollection();CollectionStatus("Распылена карта: "+d.title+" (+"+BetaGwentMillValue(id)+" осколков).");return true;}
        PublishCollection();CollectionStatus("Эта копия нужна сохранённой колоде.");return false;
    }
    // Stage 110: crafting keeps the current screen. The deck editor refreshes in place (same
    // slot keeps filters and page); the "All cards" catalog is refreshed by PublishCollection
    // alone - a full Publish there rebuilt the deck list and closed the catalog.
    private function CollectionStatus(status : string)
    {
        if(deckDraft){Publish(status);return;}
        LogChannel('BetaGwent',"COLLECTION_STATUS "+status);
    }
    private function AwardMatchReward()
    {
        var result : SBetaGwentMatchSnapshot;var player : W3PlayerWitcher;var manager : CR4GwintManager;var earnedText : string;
        if(!npcMatch || rewardGranted || selectingDecks)return;
        result=session.Snapshot();
        manager=theGame.GetGwintManager();if(manager.testMatch)return;
        player=(W3PlayerWitcher)thePlayer;if(!player)return;
        if(result.matchWinnerMask==2) {
            // A lost match still pays a little: +5 scraps.
            if(!player.BetaGwentEnsureCollection())return;
            rewardGranted=true;player.BetaGwentAddScraps(5);
            PublishCollection();if(setRewardMessage)setRewardMessage.InvokeSelfOneArg(FlashArgString("Поражение: +5 осколков (всего "+player.BetaGwentScraps()+")."));
            return;
        }
        if(result.matchWinnerMask!=1)return;
        rewardGranted=true;earnedText=player.BetaGwentWinReward(manager.betaEnemyDeckName,manager.betaMatchNpcId,manager.betaMatchRewardActorKey);
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
        var reason : string; var player : W3PlayerWitcher;
        if (!configured || !selectingDecks || deckDraft) return;
        if(audio)audio.SetEditorMusic(false);
        player = (W3PlayerWitcher)thePlayer;
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
            deckOptionCount = 0;
            for (option = 1; option <= BetaGwentDuelPresetCount(); option += 1)
            {
                if((npcMatch || libraryOnly) && (option<16 || option>20) && option!=enemyPreset)continue;
                if(!npcMatch && !libraryOnly && !BetaGwentDebugDeckVisible(option,ownPreset))continue;
                preset = BetaGwentDuelPreset(option); BetaGwentDuelPresetDeck(option, ids);
                storedDeck = deckLibrary.Get(option);
                if (storedDeck)
                {
                    ids = storedDeck.cards; validation = storedDeck.Validation();
                    preset.title = storedDeck.title; preset.description = validation.message; preset.leaderTemplateId = storedDeck.leader;
                    preset.unitCount = validation.units; preset.specialCount = validation.specials;
                    preset.goldCount = validation.gold; preset.silverCount = validation.silver;
                }
                leader = BetaGwentDuelDefinition(preset.leaderTemplateId);
                pushDeckOption.InvokeSelfNineArgs(FlashArgInt(option), FlashArgString(preset.title), FlashArgString(preset.description),
                    FlashArgInt(preset.leaderTemplateId), FlashArgString(leader.title), FlashArgInt(preset.unitCount),
                    FlashArgInt(preset.specialCount), FlashArgInt(preset.goldCount), FlashArgInt(preset.silverCount));
                PublishDeckCards(option, ids); deckOptionCount += 1;
                if (storedDeck && markDeckEdited) markDeckEdited.InvokeSelfOneArg(FlashArgInt(option));
                reason = "";
                if (storedDeck && !validation.valid) reason = validation.message;
                else if ((npcMatch || libraryOnly) && player && !player.BetaGwentOwnsDeck(ids, preset.leaderTemplateId)) reason = "Не хватает карт в коллекции.";
                if (reason != "" && markDeckInvalid) markDeckInvalid.InvokeSelfTwoArgs(FlashArgInt(option), FlashArgString(reason));
            }
            for (option = 1001; option <= 1008; option += 1)
            {
                storedDeck = deckLibrary.Get(option); if (!storedDeck) continue;
                // Invalid custom decks stay listed with their reason, so they can be fixed.
                validation = storedDeck.Validation();
                leader = BetaGwentDuelDefinition(storedDeck.leader);
                pushDeckOption.InvokeSelfNineArgs(FlashArgInt(option), FlashArgString(storedDeck.title), FlashArgString("Своя колода · слот " + storedDeck.slot),
                    FlashArgInt(storedDeck.leader), FlashArgString(leader.title), FlashArgInt(validation.units),
                    FlashArgInt(validation.specials), FlashArgInt(validation.gold), FlashArgInt(validation.silver));
                PublishDeckCards(option, storedDeck.cards); deckOptionCount += 1;
                reason = "";
                if (!validation.valid) reason = validation.message;
                else if ((npcMatch || libraryOnly) && player && !player.BetaGwentOwnsDeck(storedDeck.cards, storedDeck.leader)) reason = "Не хватает карт в коллекции.";
                if (reason != "" && markDeckInvalid) markDeckInvalid.InvokeSelfTwoArgs(FlashArgInt(option), FlashArgString(reason));
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
        if(audio)audio.SetEditorMusic(true);
        PublishKegInventory();
        revision += 1; visualBusy = false; validation = deckDraft.Validation();
        LogChannel('BetaGwent',"DECK_VALIDATION slot="+deckDraft.slot+" total="+validation.total+" valid="+validation.valid+" reason="+validation.message);
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
    private function PublishDeckExchange(code : string, message : string, accepted : bool)
    {
        var reply : CScriptedFlashFunction;
        reply=GetMenuFlash().GetMemberFlashFunction("setDeckExchange");
        if(reply)reply.InvokeSelfFourArgs(FlashArgInt(revision),FlashArgString(code),FlashArgString(message),FlashArgBool(accepted));
    }
    event OnBetaGwentDeckExport(value : int)
    {
        var code : string;
        if(!configured || !deckDraft || value!=revision)return false;
        code=BetaGwentExportDeckExchange(deckDraft.cards,deckDraft.faction,deckDraft.leader);
        if(code==""){PublishDeckExchange("","Нужна допустимая колода из 25–40 карт.",false);return false;}
        LogChannel('BetaGwent',"BG1_EXPORT "+code);
        PublishDeckExchange(code,"",false);return true;
    }
    // 0.9.0: missing cards are published as a list for a card grid. Crafting (one card
    // or all) never imports, and import is refused while anything is missing.
    private function ExchangeParse(value : int, code : string, out parsed : SBetaGwentDeckExchange) : bool
    {
        var player : W3PlayerWitcher;
        if(!configured || !selectingDecks || value!=revision)return false;
        parsed=BetaGwentParseDeckExchange(code);
        if(!parsed.valid){PublishDeckExchange("",parsed.message,false);return false;}
        if(npcMatch && forcedBetaFaction!=0 && parsed.faction!=forcedBetaFaction) {
            PublishDeckExchange("","Для квеста нужна другая фракция.",false);return false;
        }
        player=(W3PlayerWitcher)thePlayer;
        if((libraryOnly || npcMatch) && (!player || !player.BetaGwentEnsureCollection())) {
            PublishDeckExchange("","Коллекция недоступна.",false);return false;
        }
        return true;
    }
    private function ExchangeMissing(parsed : SBetaGwentDeckExchange, out missing : array<int>, out counts : array<int>) : int
    {
        var player : W3PlayerWitcher;
        missing.Clear();counts.Clear();
        player=(W3PlayerWitcher)thePlayer;
        if(!(libraryOnly || npcMatch) || !player)return 0;
        return player.BetaGwentExchangeMissing(parsed.cards,parsed.leader,missing,counts);
    }
    private function PublishExchangeMissing(parsed : SBetaGwentDeckExchange, message : string)
    {
        var reply : CScriptedFlashFunction;var player : W3PlayerWitcher;
        var missing,counts : array<int>;var cost,i,balance : int;var ids,copies : string;var blocked : bool;
        cost=ExchangeMissing(parsed,missing,counts);
        player=(W3PlayerWitcher)thePlayer;
        if(player){balance=player.BetaGwentScraps();blocked=missing.Size()>0 && player.BetaGwentKegPending();}
        for(i=0;i<missing.Size();i+=1){if(i>0){ids+=",";copies+=",";}ids+=IntToString(missing[i]);copies+=IntToString(counts[i]);}
        reply=GetMenuFlash().GetMemberFlashFunction("setDeckExchangeMissing");
        if(reply)reply.InvokeSelfSixArgs(FlashArgInt(revision),FlashArgString(ids),FlashArgString(copies),FlashArgInt(cost),FlashArgInt(balance),FlashArgBool(blocked));
        PublishDeckExchange("",message,false);
    }
    event OnBetaGwentDeckImportCheck(value : int, code : string)
    {
        var parsed : SBetaGwentDeckExchange;
        if(!ExchangeParse(value,code,parsed))return false;
        PublishExchangeMissing(parsed,"");return true;
    }
    event OnBetaGwentDeckImportCraft(value : int, code : string, id : int)
    { return ImportCraft(value,code,id); }
    // id 0 creates every missing copy at once (price and caps checked first).
    private function ImportCraft(value : int, code : string, id : int) : bool
    {
        var parsed : SBetaGwentDeckExchange;var player : W3PlayerWitcher;
        var missing,counts : array<int>;var crafted : bool;
        if(!ExchangeParse(value,code,parsed))return false;
        player=(W3PlayerWitcher)thePlayer;
        if(!(libraryOnly || npcMatch) || !player){PublishExchangeMissing(parsed,"");return false;}
        ExchangeMissing(parsed,missing,counts);
        if(player.BetaGwentKegPending())crafted=false;
        else if(id==0)crafted=missing.Size()>0 && player.BetaGwentCraftExchange(parsed.cards,parsed.faction,parsed.leader);
        else if(missing.Contains(id) && player.BetaGwentCraft(id)) {
            crafted=true;player.BetaGwentUpdateCollectionProgress();player.BetaGwentSyncTournamentAccess();player.BetaGwentBackupProfile();
        }
        LogChannel('BetaGwent',"IMPORT_CRAFT card="+id+" ok="+crafted+" scraps="+player.BetaGwentScraps());
        PublishCollection();
        if(crafted)PublishExchangeMissing(parsed,"");
        else PublishExchangeMissing(parsed,"Не хватает осколков или карта уже собрана.");
        return crafted;
    }
    event OnBetaGwentDeckImport(value : int, code : string, craft : bool)
    {
        var parsed : SBetaGwentDeckExchange;var missing,counts : array<int>;
        if(craft)return ImportCraft(value,code,0);
        if(!ExchangeParse(value,code,parsed))return false;
        if(!deckDraft && deckLibrary.FirstEmpty()==0){PublishDeckExchange("","Нет свободного слота. Откройте колоду для замены.",false);return false;}
        ExchangeMissing(parsed,missing,counts);
        if(missing.Size()>0){PublishExchangeMissing(parsed,"Сначала создайте недостающие карты.");return false;}
        if(!deckDraft)deckDraft=deckLibrary.Edit(0);
        if(!deckDraft){PublishDeckExchange("","Нет свободного слота.",false);return false;}
        deckDraft.cards=parsed.cards;deckDraft.faction=parsed.faction;deckDraft.leader=parsed.leader;
        deckClearHistory.Clear();editorPublishedFaction=0;
        PublishCollection();PublishDeckEditor("Колода импортирована. Сохраните изменения.");
        PublishDeckExchange("","Колода импортирована.",true);return true;
    }

    event OnBetaGwentDeckCreate(value : int, id : int)
    {
        var d : SBetaGwentDuelDefinition; var player : W3PlayerWitcher;
        if (!configured || !selectingDecks || deckDraft || value != revision || !BetaGwentDuelIsLeader(id)) return false;
        player = (W3PlayerWitcher)thePlayer;
        if ((libraryOnly || npcMatch) && (!player || player.BetaGwentOwned(id) < 1)) return false;
        d = BetaGwentDuelDefinition(id);
        if (npcMatch && forcedBetaFaction != 0 && d.header.factionMask != forcedBetaFaction) return false;
        deckDraft = deckLibrary.Edit(0);
        if (!deckDraft) { PublishDeckSelection(); return false; }
        deckClearHistory.Clear(); editorPublishedFaction = 0;
        deckDraft.leader = id; deckDraft.faction = d.header.factionMask;
        PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckEditorOpen(value : int, id : int)
    {
        if (!configured || !selectingDecks || deckDraft || value != revision) return false;
        deckClearHistory.Clear();editorPublishedFaction = 0; deckDraft = deckLibrary.Edit(id);
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
            PublishDeckEditor("Для квеста нужна другая фракция.");return false;
        }
        if (d.header.factionMask != deckDraft.faction)
        {
            deckDraft.faction = d.header.factionMask;
            for (i = deckDraft.cards.Size() - 1; i >= 0; i -= 1)
            { d = BetaGwentDuelDefinition(deckDraft.cards[i]); if (d.header.factionMask != 1 && d.header.factionMask != deckDraft.faction) deckDraft.cards.Erase(i); }
        }
        deckClearHistory.Clear();deckDraft.leader = id; PublishDeckEditor(""); return true;
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
    public function BetaGwentKegMenuClosed()
    {
        if(!configured)return;
        PublishKegInventory();PublishCollection();
        if(((W3PlayerWitcher)thePlayer).BetaGwentKegPending())Publish(session.GetMessage());else Publish("Карта добавлена в коллекцию.");
        LogChannel('BetaGwent',"KEG_MENU_RETURNED to="+GetMenuName());
    }
    private function PublishKegInventory()
    {
        var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
        if(setUnopenedKegs && player)setUnopenedKegs.InvokeSelfTwoArgs(FlashArgInt(player.BetaGwentKegCount()),FlashArgBool(player.BetaGwentKegPending()));
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
        var validation : SBetaGwentDeckValidation;
        if (!configured || !deckDraft || value != revision) return false;
        validation=deckDraft.Validation();
        if(!validation.valid){PublishDeckEditor(validation.message);return false;}
        title=StrLeft(title,48);
        if (!deckLibrary.Save(deckDraft, title)) { LogChannel('BetaGwent',"DECK_SAVE_REJECT slot="+deckDraft.slot+" reason=profileStorage");PublishDeckEditor("Не удалось записать колоду в сохранение."); return false; }
        selectionPublished = false; ownPreset = 1000 + deckDraft.slot;
        if (deckDraft.slot >= 9 && deckDraft.slot <= 13) ownPreset = deckDraft.slot + 7;
        ownLeader = deckDraft.leader; deckLibrary.Remember(ownPreset); deckDraft = NULL;
        selectingDecks = true; PublishDeckSelection(); return true;
    }
    event OnBetaGwentDeckEditorCancel(value : int)
    {
        if (!configured || !deckDraft || value != revision) return false;
        deckDraft = NULL; selectingDecks = true; PublishDeckSelection(); return true;
    }
    event OnBetaGwentDeckEditorLeave(value : int, save : bool, title : string, nextKeg : bool)
    {
        if(!configured || !deckDraft || value!=revision)return false;
        if(save){if(!OnBetaGwentDeckEditorSave(value,title))return false;}
        else if(!OnBetaGwentDeckEditorCancel(value))return false;
        if(nextKeg)OnBetaGwentKegOpen(revision);
        return true;
    }
    event OnBetaGwentDeckEditorClear(value : int)
    {
        var snapshot : SBetaGwentClearedDeck;
        if (!configured || !deckDraft || value != revision || deckDraft.cards.Size()==0) return false;
        snapshot.cards=deckDraft.cards;snapshot.faction=deckDraft.faction;
        deckClearHistory.PushBack(snapshot);if(deckClearHistory.Size()>20)deckClearHistory.Erase(0);
        deckDraft.cards.Clear(); PublishDeckEditor(""); return true;
    }
    event OnBetaGwentDeckEditorRestore(value : int)
    {
        var snapshot : SBetaGwentClearedDeck;var index : int;
        if(!configured || !deckDraft || value!=revision || deckDraft.cards.Size()!=0 || deckClearHistory.Size()==0)return false;
        index=deckClearHistory.Size()-1;snapshot=deckClearHistory[index];
        if(snapshot.faction!=deckDraft.faction)return false;
        deckDraft.cards=snapshot.cards;deckClearHistory.Erase(index);PublishDeckEditor("");return true;
    }
    event OnBetaGwentDeckSelect(value : int, side : int, presetId : int)
    {
        var cards : array<int>; var leader : int;var chosen : SBetaGwentDuelDefinition;
        if (!configured || !selectingDecks || deckDraft || value != revision || (side != 1 && side != 2)) return false;
        if (side == 1) { if (!deckLibrary.Resolve(presetId, cards, leader)) { PublishDeckSelection();return false; } }
        else { if (!deckLibrary.ResolveOpponent(presetId, cards, leader)) { PublishDeckSelection();return false; } }
        if(side==1 && (npcMatch || libraryOnly) && !((W3PlayerWitcher)thePlayer).BetaGwentOwnsDeck(cards,leader)){PublishDeckSelection();return false;}
        chosen=BetaGwentDuelDefinition(leader);if(npcMatch && (side==2 || (forcedBetaFaction!=0 && chosen.header.factionMask!=forcedBetaFaction))){PublishDeckSelection();return false;}
        if (side == 1) { ownPreset = presetId; ownLeader = leader; deckLibrary.Remember(ownPreset); } else { enemyPreset = presetId; enemyLeader = leader; }
        if(side==2)LogChannel('BetaGwent',"DEBUG_OPPONENT_SELECTED preset="+enemyPreset+" archetype="+BetaGwentAIArchetypeName(enemyPreset)+" source=deck_picker");
        PublishDeckSelection(); return true;
    }
    event OnBetaGwentDeckDelete(value : int, presetId : int)
    {
        var cards : array<int>; var leader : int;
        if (!configured || !selectingDecks || deckDraft || value != revision) return false;
        if ((presetId >= 1001 && deckOptionCount <= 1) || !deckLibrary.Delete(presetId))
        { LogChannel('BetaGwent',"DECK_DELETE_REJECT id="+presetId+" decks="+deckOptionCount); PublishDeckSelection(); return false; }
        LogChannel('BetaGwent',"DECK_DELETED id="+presetId);
        selectionPublished = false;
        if (ownPreset == presetId && presetId >= 16 && presetId <= 20)
        { if (deckLibrary.Resolve(ownPreset, cards, leader)) ownLeader = leader; }
        else if (ownPreset == presetId)
        { ownPreset = deckLibrary.Preferred(); if (deckLibrary.Resolve(ownPreset, cards, leader)) ownLeader = leader; deckLibrary.Remember(ownPreset); }
        if (enemyPreset == presetId)
        { enemyPreset = 2; if (deckLibrary.ResolveOpponent(enemyPreset, cards, leader)) enemyLeader = leader; }
        PublishDeckSelection(); return true;
    }
    event OnBetaGwentLeaderSelect(value : int, side : int, templateId : int)
    {
        var cards : array<int>; var presetLeader : int; var chosen, original : SBetaGwentDuelDefinition;
        if (!configured || !selectingDecks || deckDraft || value != revision || (side != 1 && side != 2)) return false;
        if (!BetaGwentDuelIsLeader(templateId)) { PublishDeckSelection();return false; }
        if (side == 1) { if (!deckLibrary.Resolve(ownPreset,cards,presetLeader)) {PublishDeckSelection();return false;} } else { if (!deckLibrary.ResolveOpponent(enemyPreset,cards,presetLeader)) {PublishDeckSelection();return false;} }
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
        if (audio) audio.Cancel(); audioRevisions.Clear(); audioFrames.Clear();
        requestFlow.Close(); visualBusy = false; deferredOpponent = false;
        if (!deckLibrary.Resolve(ownPreset, ownCards, leader) || !deckLibrary.ResolveOpponent(enemyPreset, enemyCards, leader)) return false;
        if(npcMatch && !((W3PlayerWitcher)thePlayer).BetaGwentOwnsDeck(ownCards,ownLeader))return false;
        originalOpponent=BetaGwentDifficultyLevel()==4;originalFailure=false;originalController=NULL;
        duel.externalPolicyMask=0;
        if(originalOpponent) {
            originalRuntime=new CBetaOriginalRuntime in this;originalPersonality=new CBetaOriginalPersonality in this;
            chosen=BetaGwentDuelDefinition(enemyLeader);if(!originalPersonality.InitializeForDeck(enemyPreset,chosen.header.factionMask))return false;
            duel.externalPolicyMask=2;
            LogChannel('BetaGwent',"DUEL_ORIGINAL_BETA profile="+originalPersonality.profileName+" privateHand=true privateDeck=true source=direct_ws");
        }
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
        if(duel.DirectSpecialKind(d)==3 && side!=2)side=1;
        pushTemplateDetails.InvokeSelfFourArgs(FlashArgInt(id), FlashArgString(d.description), FlashArgInt(d.header.tierMask), FlashArgInt(d.header.typeMask));
        pushTemplateRules.InvokeSelfNineArgs(FlashArgInt(id), FlashArgInt(duel.DirectSpecialKind(d)), FlashArgInt(side),
            FlashArgInt(d.targetTypes), FlashArgInt(d.targetTiers), FlashArgInt(d.targetIgnore), FlashArgInt(d.consumeMaximum), FlashArgInt(d.specialRowMask), FlashArgString(duel.ActionPreviewGeometry(d)));
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
        if (!intermediate && !OriginalPrivateRequest()) placement = duel.PlacementCard();
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
        for (i = 0; i < frame.destinationIds.Size(); i += 1)
            pushDestination.InvokeSelfThreeArgs(FlashArgInt(frame.destinationIds[i]), FlashArgInt(frame.destinationSides[i]), FlashArgInt(frame.destinationZones[i]));
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
            if (duel.IsPending() && !OriginalPrivateRequest()) requestSnapshot = duel.GetRequestSnapshot();
            else requestSnapshot = requestFlow.Snapshot();
        }
        setRequestHeader.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(requestSnapshot.requestId),
            FlashArgInt(requestSnapshot.playerId), FlashArgInt((int)requestSnapshot.kind),
            FlashArgInt(requestSnapshot.limits.minimum), FlashArgInt(requestSnapshot.limits.maximum),
            FlashArgInt(requestSnapshot.selectedCount), FlashArgBool(!OriginalPrivateRequest() && !intermediate && (duel.IsPending() && requestSnapshot.limits.minimum == 0
                || !duel.IsPending() && requestFlow.CanFinish())), FlashArgString(frame.status));
        if (setRequestSource && !OriginalPrivateRequest()) {
            cardDefinition=BetaGwentDuelDefinition(0);
            if(duel.FindCard(duel.PendingSourceId()))cardDefinition=duel.FindCard(duel.PendingSourceId()).Definition();
            if(cardDefinition.header.templateId>0)PublishCardTemplate(cardDefinition.header.templateId);
            setRequestSource.InvokeSelfThreeArgs(FlashArgInt(revision), FlashArgInt(duel.PendingAimSourceId()), FlashArgInt(cardDefinition.header.templateId));
        } else if(setRequestSource)setRequestSource.InvokeSelfThreeArgs(FlashArgInt(revision),FlashArgInt(0),FlashArgInt(0));
        if (!intermediate)
        {
            if (duel.IsPending() && !OriginalPrivateRequest()) duel.GetRequestViews(requestCards);
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
        setVisualCue.InvokeSelfNineArgs(FlashArgInt(revision), FlashArgInt(frame.kind + 256 * Min(255, Max(1, frame.attackCount)) + 65536 * frame.audioKind), FlashArgInt(frame.sourceId),
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
        visualBusy = false; if(audio)deferredVoiceAt=audio.CurrentTime();
        LogChannel('BetaGwent', "BOARD_VISUAL_DONE revision=" + value);
        ResumeOpponentAfterVoice();
        AwardMatchReward(); return true;
    }

    private function ResumeOpponentAfterVoice()
    {
        var prepared : bool;
        // A spoken card line delays the opponent briefly, never for its whole length:
        // after 1 s the turn continues and the line keeps playing over it.
        if(!configured || visualBusy || !deferredOpponent || opponentPreparationBusy)return;
        if(audio && audio.IsVoiceActive() && audio.CurrentTime()-deferredVoiceAt<1.0f)return;
        if(EmptyHandPassWaiting()){
            deferredOpponent=false;
            if(duel.Pass(1)){LogChannel('BetaGwent',"DUEL_AUTO_PASS side=1 reason=empty_hand_and_spent_leader");Publish(duel.GetMessage(),true);}
            return;
        }
        if(originalOpponent){ResumeOriginalOpponent();return;}
        opponentPreparationBusy=true;prepared=duel.AiPreparationStep();
        if(!prepared){opponentPreparationBusy=false;return;}
        duel.PumpOpponent();
        if(duel.aiPreparationStage==7 && !duel.aiPreparationReady){opponentPreparationBusy=false;return;}
        deferredOpponent=false;
        if(!duel.IsPending())Publish(duel.GetMessage(),true);
        opponentPreparationFinished=true;opponentPreparationBusy=false;
    }

    event OnBetaGwentAudioSpellLaunch(value : int, clock : int)
    {
        var i,j,kind : int;var frame : CBetaGwentDuelVisualFrame;var card : SBetaGwentCardSnapshot;
        if(!configured || !audio || spellLaunchRevisions.Contains(value))return false;
        for(i=0;i<audioRevisions.Size();i+=1)if(audioRevisions[i]==value){
            frame=audioFrames[i];kind=frame.audioKind;if(kind==0)kind=22;
            // Crow collapses power/death snapshots under the final death revision.
            // The authoritative source/template still identifies the same spell.
            if(frame.kind==3 && frame.templateId==200224)kind=22;
            if(frame.kind!=2 && !(frame.kind==3 && frame.templateId==200224))return false;
            if(frame.sourceId<=0 || frame.sourceId==frame.targetId)return false;
            if(BetaGwentAudioElement164(frame.templateId,kind,true)=="")return false;
            for(j=0;j<frame.cards.Size();j+=1){
                card=frame.cards[j].card;
                if(card.instanceId==frame.sourceId && card.positionPlayerId==2 && (card.tokenMask & 8)!=0)return false;
            }
            spellLaunchRevisions.PushBack(value);if(spellLaunchRevisions.Size()>64)spellLaunchRevisions.Erase(0);
            if(clock>0)audio.SetClock(clock);audio.SpellLaunch(frame.templateId,kind);return true;
        }
        return false;
    }
    event OnBetaGwentEffectGalleryAudio(id : int, kind : int, token : int, clock : int)
    {
        var definition : SBetaGwentDuelDefinition;
        if(!configured || !effectGallery || !audio || kind<1 || kind>133)return false;
        definition=BetaGwentDuelDefinition(id);if(definition.header.templateId!=id)return false;
        audio.SetClock(clock);
        if(kind>=100)audio.SpellLaunch(id,kind-100);
        else audio.Cue(kind,id,0,0,0,token,0,definition.header.typeMask==4 && definition.header.tierMask==8 && !BetaGwentAudioIsLeader(id));
        return true;
    }
    event OnBetaGwentAudioCue(value : int)
    {
        var i, kind, id, j, token, targetTokens, rowIndex, landingTemplate : int; var frame : CBetaGwentDuelVisualFrame; var s : SBetaGwentCardSnapshot;var landing : SBetaGwentDuelDefinition;var goldLanding : bool;
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
                if((s.locationMask&7)!=0 && (s.tokenMask&8)==0
                    && (frame.kind==1 && s.instanceId==frame.sourceId
                        || (frame.kind==15 || frame.kind==16) && s.instanceId==frame.targetId))landingTemplate=s.runtimeTemplate.templateId;
                if (s.instanceId == frame.sourceId && s.positionPlayerId == 2 && (s.tokenMask & 8) != 0) id = 0;
            }
            if (frame.side > 0 && frame.row > 0)
            {
                rowIndex = (frame.side - 1) * 3;
                if (frame.row == 2) rowIndex += 1; else if (frame.row == 4) rowIndex += 2;
                if (rowIndex < frame.weatherTokens.Size()) token = frame.weatherTokens[rowIndex];
            }
            // Weather ticks have no unit source. Keep placement sounds separate
            // and include armour-only hits (the weather still landed).
            if (frame.kind == 2 && frame.sourceId == 0 && frame.row > 0 && token != 0 && (kind == 20 || kind == 22)) kind = 33;
            landing=BetaGwentDuelDefinition(landingTemplate);
            goldLanding=landing.header.typeMask==4 && landing.header.tierMask==8 && !BetaGwentAudioIsLeader(landingTemplate);
            audio.Cue(kind, id, frame.flags, frame.scoreOne, frame.scoreTwo, token, targetTokens, goldLanding); return true;
        }
        return false;
    }
    event OnBetaGwentAudioIntro(opponent : int, player : int, optional serial : int, optional clock : int)
    {
        introAudioSerial=serial;
        if(configured && audio){audio.SetClock(clock);audio.Intro(opponent,player);}
        PublishIntroAudio();return true;
    }
    private function PublishIntroAudio()
    {
        var pending : bool;
        if(configured && audio)pending=audio.IsIntroActive();
        if(setIntroAudioState && introAudioSerial>0)setIntroAudioState.InvokeSelfTwoArgs(FlashArgInt(introAudioSerial),FlashArgBool(pending));
        if(setIntroVoiceStart && introAudioSerial>0 && audio && audio.IntroVoiceSide()>0)
            setIntroVoiceStart.InvokeSelfFourArgs(FlashArgInt(introAudioSerial),FlashArgInt(audio.IntroVoiceSide()),FlashArgInt(audio.IntroVoiceTemplate()),FlashArgInt(audio.IntroVoiceClock()));
    }
    event OnBetaGwentAudioLeaderEntrance(templateId : int, side : int, serial : int, clock : int)
    { if(configured && audio && serial>0 && serial==introAudioSerial){audio.SetClock(clock);audio.MarkIntroReady(side);audio.LeaderEntrance(templateId,side);} }
    event OnBetaGwentAudioIntroCancel(serial : int)
    { if(serial==introAudioSerial){if(audio)audio.CancelIntro();introAudioSerial=0;} }
    event OnBetaGwentAudioKeg(kind : int)
    { if (audio) audio.Keg(kind); }
    event OnBetaGwentAudioUi(kind : int)
    { if (!configured || !audio) return false; audio.Ui(kind); return true; }
    event OnBetaGwentUIError(detail : string)
    { LogChannel('BetaGwent', "UI_ERROR " + detail); }
    event OnBetaGwentPerf(eventName : string, ms : int)
    {
        if(!configured || !duel)return false;
        // Flash getTimer measures the synchronous call, including the final play.
        if(eventName=="OnBetaGwentAudioTick" || eventName=="OnBetaGwentVisualDone"){
            opponentPreparationMs+=Max(0,ms);opponentPreparationPeakMs=Max(opponentPreparationPeakMs,ms);
            if(opponentPreparationFinished){
                duel.AiPerfFeedback(opponentPreparationMs,opponentPreparationPeakMs);
                LogChannel('BetaGwent',"AI_PREPARATION totalMs="+opponentPreparationMs+" peakStepMs="+opponentPreparationPeakMs);
                opponentPreparationMs=0;opponentPreparationPeakMs=0;opponentPreparationFinished=false;
            }
        }else duel.AiPerfFeedback(ms);
    }
    event OnBetaGwentAudioTick(clock : int)
    { if (configured && audio) { if (clock > 0) audio.SetClock(clock); audio.Tick(); PublishIntroAudio(); ResumeOpponentAfterVoice(); if(setAudioStatus)setAudioStatus.InvokeSelfSixArgs(FlashArgBool(BetaGwentAudioBankInstalled()),FlashArgBool(audio.IsBankReady()),FlashArgInt(presentationTempo),FlashArgBool(presentationReduced),FlashArgInt(presentationAiPause),FlashArgInt(presentationDifficulty)); } }
    event OnBetaGwentTextLanguage(language:int)
    {
        if(language<0||language>13)return false;
        FactsSet("bg_text_language",language);
        PublishLanguageSettings();
    }
    private function PublishLanguageSettings()
    {
        if(setLanguageSettings)setLanguageSettings.InvokeSelfSixArgs(FlashArgInt(BetaGwentTextPreference()),FlashArgInt(BetaGwentVoicePreference()),FlashArgInt(BetaGwentVoiceLanguage()),FlashArgInt(BetaGwentGameTextLanguage()),FlashArgInt(BetaGwentResolvedTextLanguage()),FlashArgString(BetaGwentGameVoiceName()));
    }
    event OnBetaGwentVoiceLanguage(language : int)
    {
        if(language<0 || language>5)return false;
        if(audio)audio.Cancel();
        FactsSet("bg_voice_language",language);
        PublishLanguageSettings();
        LogChannel('BetaGwent',"AUDIO_LANGUAGE requested="+language+" resolved="+BetaGwentVoiceLanguage());
    }
    event OnBetaGwentTutorialSeen()
    { FactsSet("bg_tutorial_seen", 1); LogChannel('BetaGwent', "TUTORIAL_OFFERED"); }
    event OnBetaGwentAudioSettings(effects : bool, voices : bool, optional tempo : int, optional reduced : bool, optional aiPause : int, optional difficulty : int)
    { var player : W3PlayerWitcher;if (configured && audio) audio.Configure(effects, voices);player=(W3PlayerWitcher)thePlayer;if(player && (tempo==10 || tempo==15 || tempo==20)){presentationTempo=tempo;presentationReduced=reduced;player.BetaGwentSetPresentation(tempo,reduced);}
      if(player && aiPause>=1 && aiPause<=4){presentationAiPause=aiPause;player.BetaGwentSetAiPause(aiPause);}
      if(player && difficulty>=1 && difficulty<=4 && OriginalDifficultyChangeAllowed(difficulty)){presentationDifficulty=difficulty;player.BetaGwentSetDifficulty(difficulty);LogChannel('BetaGwent',"AI_DIFFICULTY level="+difficulty);} }
    event OnBetaGwentLeaderMotion(dynamic : bool)
    { if(!configured)return false;if(dynamic)FactsSet("bg_static_leaders",0);else FactsSet("bg_static_leaders",1);return true; }
    event OnBetaGwentBoardHelp(visible : bool)
    { if(!configured)return false;if(visible)FactsSet("bg_hide_help",0);else FactsSet("bg_hide_help",1);return true; }
    event OnBetaGwentAudioCancel()
    {
        audioRevisions.Clear(); audioFrames.Clear();
        spellLaunchRevisions.Clear();
        if (audio) audio.Cancel();
    }

    private function RowMode() : int
    {
        if(OriginalPrivateRequest())return 0;
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
    {
        var manager : CR4GwintManager;var label : string;
        if(!npc)return "Соперник";
        manager=theGame.GetGwintManager();label=manager.betaMatchNpcName;if(StrLen(label)==0)label="Соперник";
        return label;
    }
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
        var swaps : int;
        LogChannel('BetaGwent', "UI_REQUEST_SELECT revision=" + value + " id=" + requestId + " kind=" + kind + " item=" + itemId);
        if (!AcceptRevision(value)) return false;
        if (duel.IsPending())
        {
            if (playerId != 1) return false;
            if (duel.IsMulligan() && kind == 1)
            {
                swaps=duel.MulliganSwapCount();duel.SelectMulligan(requestId, itemId);
                if(audio && duel.MulliganSwapCount()>swaps)audio.Ui(5);
            }
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
        var gameplayInputExceptions : array<EInputActionBlock>;var boardParent : CR4BetaGwentBoardMenu;var kegMenuInit : CBetaGwentKegMenuData;
        var backupPlayer : W3PlayerWitcher;
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
        // Mirror collection, scraps, kegs and decks into facts (survives a save made without the mod).
        backupPlayer=(W3PlayerWitcher)thePlayer;if(backupPlayer && !effectGallery)backupPlayer.BetaGwentBackupProfile();
        if (audio) audio.Close(); audio = NULL; audioRevisions.Clear(); audioFrames.Clear();
        if (configured)
        {
            deckDraft = NULL; requestFlow.Close();

            if(!kegNested){
                // Always restore gameplay input before returning to the world.
                if (thePlayer)
                    thePlayer.BlockAllActions('BetaGwentBoard', false, gameplayInputExceptions, false);
                theInput.RestoreContext('EMPTY_CONTEXT', true);

                // Balanced with EnterGameState() in OnConfigUI for every entry mode.
                theSound.LeaveGameState(ESGS_Gwent);
                theSound.SoundEvent("system_resume");

                SetOwnedMouseCursor(false);
            }
            configured = false;
        }
        if(kegOnly) {
            inventoryParent=(CR4InventoryMenu)GetParent();
            if(inventoryParent) inventoryParent.UpdateAllItemData();
            ((W3PlayerWitcher)thePlayer).BetaGwentEnsureCollection();
            boardParent=(CR4BetaGwentBoardMenu)GetParent();
            if(boardParent) boardParent.BetaGwentKegMenuClosed();
        }
        LogChannel('BetaGwent', "BOARD_CLOSED revision=" + revision);
        if(kegSwitch){kegSwitch=false;kegMenuInit=new CBetaGwentKegMenuData in theGame;theGame.RequestMenu('BetaGwentKeg',kegMenuInit);}
        else if(kegOnly && !kegNested){LogChannel('BetaGwent',"KEG_MENU_RETURN_TO_EDITOR");theGame.RequestMenu('DeckBuilder');}
    }
}

class CBetaGwentEffectGalleryData extends IScriptable {}
exec function bgboard_effects()
{
    var data : CBetaGwentEffectGalleryData;var nativePlayer : CR4Player;
    if(theGame.GetGuiManager().IsAnyMenu())return;
    data=new CBetaGwentEffectGalleryData in theGame;
    nativePlayer=thePlayer;nativePlayer.betaPracticeRequested=true;
    theGame.RequestMenu('BetaGwentBoard',data);
}
exec function bgboard_open(optional enemyPreset : int)
{
    var nativePlayer : CR4Player;
    var manager : CR4GwintManager;
    if(enemyPreset!=0 && !BetaGwentDebugOpponentAllowed(enemyPreset))
    {
        LogChannel('BetaGwent',"DEBUG_OPPONENT_REJECT preset="+enemyPreset+" reason=inactive_preset use=bgboard_decks()");
        return;
    }
    if (theGame.GetGuiManager().IsAnyMenu())
    {
        LogChannel('BetaGwent', "BOARD_OPEN_SKIPPED existing menu");
        return;
    }
    LogChannel('BetaGwent', "BOARD_OPEN_REQUEST name=BetaGwentBoard");
    manager=theGame.GetGwintManager();manager.betaDebugEnemyPreset=enemyPreset;
    nativePlayer=thePlayer;nativePlayer.betaPracticeRequested=true;
    theGame.RequestMenu('BetaGwentBoard');
}

exec function bgboard_close()
{
    var menu : CR4BetaGwentBoardMenu;
    menu = (CR4BetaGwentBoardMenu)theGame.GetGuiManager().GetRootMenu();
    if (menu) menu.CloseMenu();
}

function BetaGwentConsoleMessage(message : string)
{
    LogChannel('BetaGwent',message);
    if(theGame)theGame.GetGuiManager().ShowNotification(message,8.0);
}
function BetaGwentConsolePlayer() : W3PlayerWitcher
{
    var player : W3PlayerWitcher;
    if(!theGame)return NULL;
    player=(W3PlayerWitcher)thePlayer;
    if(!player){BetaGwentConsoleMessage(BetaGwentConsoleText(1));return NULL;}
    if(theGame.GetGuiManager().IsAnyMenu()){BetaGwentConsoleMessage(BetaGwentConsoleText(2));return NULL;}
    if(!player.BetaGwentEnsureCollection()){BetaGwentConsoleMessage(BetaGwentConsoleText(3));return NULL;}
    return player;
}
exec function bg_allcards()
{
    var player : W3PlayerWitcher;var granted : int;
    player=BetaGwentConsolePlayer();if(!player)return;
    granted=player.BetaGwentGrantAllCards();
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(4,""+granted));
}
exec function bg_kegs(count : int)
{
    var player : W3PlayerWitcher;var before : int;
    if(count<1 || count>1000000){BetaGwentConsoleMessage(BetaGwentConsoleText(5));return;}
    player=BetaGwentConsolePlayer();if(!player)return;before=player.BetaGwentKegCount();
    if(before<0 || before>2000000000-count){BetaGwentConsoleMessage(BetaGwentConsoleText(6));return;}
    player.BetaGwentAddKegs(count);player.BetaGwentBackupProfile();
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(7,""+(player.BetaGwentKegCount()-before),""+player.BetaGwentKegCount()));
}
exec function bg_scraps(count : int)
{
    var player : W3PlayerWitcher;var before : int;
    if(count<1 || count>1000000){BetaGwentConsoleMessage(BetaGwentConsoleText(8));return;}
    player=BetaGwentConsolePlayer();if(!player)return;before=player.BetaGwentScraps();
    if(before>2000000000-count){BetaGwentConsoleMessage(BetaGwentConsoleText(9));return;}
    player.BetaGwentAddScraps(count);player.BetaGwentBackupProfile();
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(10,""+(player.BetaGwentScraps()-before),""+player.BetaGwentScraps()));
}
exec function bg_card(id : int, count : int)
{
    var player : W3PlayerWitcher;var granted : int;var d : SBetaGwentDuelDefinition;
    if(count<1 || count>1000 || BetaGwentCollectionCap(id)<1){BetaGwentConsoleMessage(BetaGwentConsoleText(11));return;}
    player=BetaGwentConsolePlayer();if(!player)return;
    granted=player.BetaGwentConsoleGrant(id,count);d=BetaGwentDuelDefinition(id);
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(12,d.title,""+id,""+granted,""+player.BetaGwentOwned(id),""+BetaGwentCollectionCap(id)));
}
exec function bg_find(query : string)
{
    var ids,leaders : array<int>;var i,total : int;var d : SBetaGwentDuelDefinition;var line,summary : string;
    if(StrLen(query)<2 || StrLen(query)>80){BetaGwentConsoleMessage(BetaGwentConsoleText(13));return;}
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    for(i=0;i<leaders.Size();i+=1)if(!ids.Contains(leaders[i]))ids.PushBack(leaders[i]);
    query=StrLowerUTF(query);
    for(i=0;i<ids.Size();i+=1) {
        d=BetaGwentDuelDefinition(ids[i]);
        if(StrFindFirst(StrLowerUTF(d.title),query)<0)continue;
        line=d.title+" = "+ids[i];LogChannel('BetaGwent',line);total+=1;
        if(total<=8)summary+=line+"\n";
    }
    BetaGwentConsoleMessage(summary+BetaGwentConsoleFormat(14,""+total));
}
function BetaGwentConsoleFactionMask(value : string) : int
{
    value=StrLower(value);
    if(value=="neutral")return 1;if(value=="monsters")return 2;if(value=="nilfgaard")return 4;
    if(value=="north")return 8;if(value=="scoiatael")return 16;if(value=="skellige")return 32;return 0;
}
exec function bg_faction(value : string)
{
    var player : W3PlayerWitcher;var faction,granted : int;
    faction=BetaGwentConsoleFactionMask(value);
    if(faction==0){BetaGwentConsoleMessage(BetaGwentConsoleText(15));return;}
    player=BetaGwentConsolePlayer();if(!player)return;
    granted=player.BetaGwentConsoleFaction(faction,false);
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(16,""+granted,value));
}
exec function bg_leaders()
{
    var player : W3PlayerWitcher;var granted : int;
    player=BetaGwentConsolePlayer();if(!player)return;granted=player.BetaGwentConsoleFaction(0,true);
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(17,""+granted));
}
exec function bg_status()
{
    var player : W3PlayerWitcher;var ids,leaders : array<int>;var i,distinct,total : int;
    player=(W3PlayerWitcher)thePlayer;if(!theGame || !player)return;
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    for(i=0;i<leaders.Size();i+=1)if(!ids.Contains(leaders[i]))ids.PushBack(leaders[i]);
    for(i=0;i<ids.Size();i+=1){if(player.BetaGwentOwned(ids[i])>0)distinct+=1;total+=player.BetaGwentOwned(ids[i]);}
    BetaGwentConsoleMessage(BetaGwentConsoleFormat(18,""+distinct,""+ids.Size(),""+total,""+player.BetaGwentKegCount(),""+player.BetaGwentScraps(),""+player.BetaGwentKegPending(),""+FactsQuerySum("NewGamePlus")));
}
exec function bg_shopcheck()
{
    var menu : CR4InventoryMenu;
    if(!theGame)return;menu=(CR4InventoryMenu)theGame.GetGuiManager().GetRootMenu();
    if(!menu){BetaGwentConsoleMessage(BetaGwentConsoleText(19));return;}
    BetaGwentConsoleMessage(menu.BetaGwentShopDiagnostic(0,false));
}
exec function bg_shoprefill(target : int)
{
    var menu : CR4InventoryMenu;
    if(target<1 || target>99){BetaGwentConsoleMessage(BetaGwentConsoleText(20));return;}
    if(!theGame)return;menu=(CR4InventoryMenu)theGame.GetGuiManager().GetRootMenu();
    if(!menu){BetaGwentConsoleMessage(BetaGwentConsoleText(21));return;}
    BetaGwentConsoleMessage(menu.BetaGwentShopDiagnostic(target,true));
}
exec function bg_help()
{
    BetaGwentConsoleMessage(BetaGwentConsoleHelp());
}

function BetaGwentTextLanguage137(value:int):int
{
    if(BetaGwentCleanupBlocked())return 1;
    if(FactsQueryLatestValue("bg_text_language_package")!=1002)
    { FactsSet("bg_text_language_package",1002);FactsSet("bg_text_language",1);LogChannel('BetaGwent',"TEXT_LANGUAGE_PACKAGE_DEFAULT package=1002 language=1");return 1; }
    if(value>=1&&value<=13)return value;return 1;
}
// Build 12: console and notification texts in the mod text language (top-left setting).
function BetaGwentConsoleLanguage() : int
{
    var language : int;
    language=BetaGwentResolvedTextLanguage();
    if(language<1 || language>13)language=2;
    if(language>=10 && BetaGwentGameTextLanguage()!=language)language=2;
    return language;
}
function BetaGwentConsoleText(key : int) : string
{
    var l : int;
    l=BetaGwentConsoleLanguage();
    if(key==1){
        if(l==1)return "Загрузите сохранение игры.";
        if(l==3)return "Lade zuerst einen Spielstand.";
        if(l==4)return "Chargez d’abord une sauvegarde.";
        if(l==5)return "Carica prima un salvataggio.";
        if(l==6)return "Najpierw wczytaj zapis gry.";
        if(l==7)return "Carga primero una partida guardada.";
        if(l==8)return "Carga primero una partida guardada.";
        if(l==9)return "Carregue um jogo salvo primeiro.";
        if(l==10)return "先にセーブデータをロードしてください。";
        if(l==11)return "먼저 저장된 게임을 불러오세요.";
        if(l==12)return "请先读取存档。";
        if(l==13)return "請先讀取存檔。";
        return "Load a saved game first.";
    }
    if(key==2){
        if(l==1)return "Закройте меню перед выдачей ресурсов.";
        if(l==3)return "Schließe alle Menüs, bevor du Ressourcen vergibst.";
        if(l==4)return "Fermez tous les menus avant d’accorder des ressources.";
        if(l==5)return "Chiudi tutti i menu prima di assegnare risorse.";
        if(l==6)return "Zamknij wszystkie menu przed przyznaniem zasobów.";
        if(l==7)return "Cierra todos los menús antes de otorgar recursos.";
        if(l==8)return "Cierra todos los menús antes de otorgar recursos.";
        if(l==9)return "Feche todos os menus antes de conceder recursos.";
        if(l==10)return "リソースを付与する前にすべてのメニューを閉じてください。";
        if(l==11)return "자원을 지급하기 전에 모든 메뉴를 닫으세요.";
        if(l==12)return "发放资源前请关闭所有菜单。";
        if(l==13)return "發放資源前請關閉所有選單。";
        return "Close all menus before granting resources.";
    }
    if(key==3){
        if(l==1)return "Коллекция недоступна.";
        if(l==3)return "Sammlung nicht verfügbar.";
        if(l==4)return "Collection indisponible.";
        if(l==5)return "Collezione non disponibile.";
        if(l==6)return "Kolekcja niedostępna.";
        if(l==7)return "Colección no disponible.";
        if(l==8)return "Colección no disponible.";
        if(l==9)return "Coleção indisponível.";
        if(l==10)return "コレクションを利用できません。";
        if(l==11)return "카드 수집 목록을 사용할 수 없습니다.";
        if(l==12)return "收藏不可用。";
        if(l==13)return "收藏無法使用。";
        return "Collection unavailable.";
    }
    if(key==4){
        if(l==1)return "bg_allcards: добавлено {0} копий карт и лидеров.";
        if(l==3)return "bg_allcards: {0} Kopien von Karten und Anführern hinzugefügt.";
        if(l==4)return "bg_allcards : {0} exemplaires de cartes et de chefs ajoutés.";
        if(l==5)return "bg_allcards: aggiunte {0} copie di carte e comandanti.";
        if(l==6)return "bg_allcards: dodano {0} kopii kart i dowódców.";
        if(l==7)return "bg_allcards: se añadieron {0} copias de cartas y líderes.";
        if(l==8)return "bg_allcards: se agregaron {0} copias de cartas y líderes.";
        if(l==9)return "bg_allcards: {0} cópias de cartas e líderes adicionadas.";
        if(l==10)return "bg_allcards：カードとリーダーを{0}枚追加しました。";
        if(l==11)return "bg_allcards: 카드와 지휘관 {0}장을 추가했습니다.";
        if(l==12)return "bg_allcards：已添加{0}张卡牌和领袖。";
        if(l==13)return "bg_allcards：已新增{0}張卡牌與領袖。";
        return "bg_allcards: added {0} copies of cards and leaders.";
    }
    if(key==5){
        if(l==1)return "bg_kegs(10): количество от 1 до 1000000.";
        if(l==3)return "bg_kegs(10): Menge von 1 bis 1000000.";
        if(l==4)return "bg_kegs(10) : quantité de 1 à 1000000.";
        if(l==5)return "bg_kegs(10): quantità da 1 a 1000000.";
        if(l==6)return "bg_kegs(10): liczba od 1 do 1000000.";
        if(l==7)return "bg_kegs(10): cantidad de 1 a 1000000.";
        if(l==8)return "bg_kegs(10): cantidad de 1 a 1000000.";
        if(l==9)return "bg_kegs(10): quantidade de 1 a 1000000.";
        if(l==10)return "bg_kegs(10)：数量は1～1000000です。";
        if(l==11)return "bg_kegs(10): 수량은 1~1000000입니다.";
        if(l==12)return "bg_kegs(10)：数量为1到1000000。";
        if(l==13)return "bg_kegs(10)：數量為1到1000000。";
        return "bg_kegs(10): amount from 1 to 1000000.";
    }
    if(key==6){
        if(l==1)return "Переполнение счётчика бочек.";
        if(l==3)return "Überlauf des Fasszählers.";
        if(l==4)return "Dépassement du compteur de barils.";
        if(l==5)return "Overflow del contatore dei barili.";
        if(l==6)return "Przepełnienie licznika beczek.";
        if(l==7)return "Desbordamiento del contador de barriles.";
        if(l==8)return "Desbordamiento del contador de barriles.";
        if(l==9)return "Estouro do contador de barris.";
        if(l==10)return "タルのカウンターが上限を超えました。";
        if(l==11)return "카드통 카운터가 한도를 넘었습니다.";
        if(l==12)return "卡桶计数溢出。";
        if(l==13)return "卡桶計數溢位。";
        return "Keg counter overflow.";
    }
    if(key==7){
        if(l==1)return "bg_kegs: добавлено {0}, всего {1}.";
        if(l==3)return "bg_kegs: {0} hinzugefügt, insgesamt {1}.";
        if(l==4)return "bg_kegs : {0} ajoutés, total {1}.";
        if(l==5)return "bg_kegs: aggiunti {0}, totale {1}.";
        if(l==6)return "bg_kegs: dodano {0}, łącznie {1}.";
        if(l==7)return "bg_kegs: se añadieron {0}, total {1}.";
        if(l==8)return "bg_kegs: se agregaron {0}, total {1}.";
        if(l==9)return "bg_kegs: {0} adicionados, total {1}.";
        if(l==10)return "bg_kegs：{0}個追加、合計{1}個。";
        if(l==11)return "bg_kegs: {0}개 추가, 총 {1}개.";
        if(l==12)return "bg_kegs：已添加{0}，共{1}。";
        if(l==13)return "bg_kegs：已新增{0}，共{1}。";
        return "bg_kegs: added {0}, total {1}.";
    }
    if(key==8){
        if(l==1)return "bg_scraps(1000): количество от 1 до 1000000.";
        if(l==3)return "bg_scraps(1000): Menge von 1 bis 1000000.";
        if(l==4)return "bg_scraps(1000) : quantité de 1 à 1000000.";
        if(l==5)return "bg_scraps(1000): quantità da 1 a 1000000.";
        if(l==6)return "bg_scraps(1000): liczba od 1 do 1000000.";
        if(l==7)return "bg_scraps(1000): cantidad de 1 a 1000000.";
        if(l==8)return "bg_scraps(1000): cantidad de 1 a 1000000.";
        if(l==9)return "bg_scraps(1000): quantidade de 1 a 1000000.";
        if(l==10)return "bg_scraps(1000)：数量は1～1000000です。";
        if(l==11)return "bg_scraps(1000): 수량은 1~1000000입니다.";
        if(l==12)return "bg_scraps(1000)：数量为1到1000000。";
        if(l==13)return "bg_scraps(1000)：數量為1到1000000。";
        return "bg_scraps(1000): amount from 1 to 1000000.";
    }
    if(key==9){
        if(l==1)return "Переполнение счётчика осколков.";
        if(l==3)return "Überlauf des Fetzenzählers.";
        if(l==4)return "Dépassement du compteur de fragments.";
        if(l==5)return "Overflow del contatore dei frammenti.";
        if(l==6)return "Przepełnienie licznika skrawków.";
        if(l==7)return "Desbordamiento del contador de fragmentos.";
        if(l==8)return "Desbordamiento del contador de fragmentos.";
        if(l==9)return "Estouro do contador de fragmentos.";
        if(l==10)return "紙片のカウンターが上限を超えました。";
        if(l==11)return "조각 카운터가 한도를 넘었습니다.";
        if(l==12)return "碎片计数溢出。";
        if(l==13)return "碎片計數溢位。";
        return "Scraps counter overflow.";
    }
    if(key==10){
        if(l==1)return "bg_scraps: добавлено {0}, всего {1}.";
        if(l==3)return "bg_scraps: {0} hinzugefügt, insgesamt {1}.";
        if(l==4)return "bg_scraps : {0} ajoutés, total {1}.";
        if(l==5)return "bg_scraps: aggiunti {0}, totale {1}.";
        if(l==6)return "bg_scraps: dodano {0}, łącznie {1}.";
        if(l==7)return "bg_scraps: se añadieron {0}, total {1}.";
        if(l==8)return "bg_scraps: se agregaron {0}, total {1}.";
        if(l==9)return "bg_scraps: {0} adicionados, total {1}.";
        if(l==10)return "bg_scraps：{0}追加、合計{1}。";
        if(l==11)return "bg_scraps: {0} 추가, 총 {1}.";
        if(l==12)return "bg_scraps：已添加{0}，共{1}。";
        if(l==13)return "bg_scraps：已新增{0}，共{1}。";
        return "bg_scraps: added {0}, total {1}.";
    }
    if(key==11){
        if(l==1)return "bg_card(132102,1): нужен ID коллекционной карты/лидера и количество 1–1000.";
        if(l==3)return "bg_card(132102,1): Benötigt die ID einer Sammelkarte oder eines Anführers und eine Menge von 1 bis 1000.";
        if(l==4)return "bg_card(132102,1) : il faut l’ID d’une carte à collectionner ou d’un chef et une quantité de 1 à 1000.";
        if(l==5)return "bg_card(132102,1): serve l’ID di una carta collezionabile o di un comandante e una quantità da 1 a 1000.";
        if(l==6)return "bg_card(132102,1): wymagany identyfikator karty kolekcjonerskiej lub dowódcy i liczba od 1 do 1000.";
        if(l==7)return "bg_card(132102,1): se necesita el ID de una carta coleccionable o de un líder y una cantidad de 1 a 1000.";
        if(l==8)return "bg_card(132102,1): se necesita el ID de una carta coleccionable o de un líder y una cantidad de 1 a 1000.";
        if(l==9)return "bg_card(132102,1): é preciso o ID de uma carta colecionável ou de um líder e uma quantidade de 1 a 1000.";
        if(l==10)return "bg_card(132102,1)：収集カードまたはリーダーのIDと、1～1000の数量が必要です。";
        if(l==11)return "bg_card(132102,1): 수집 카드 또는 지휘관 ID와 1~1000 사이의 수량이 필요합니다.";
        if(l==12)return "bg_card(132102,1)：需要可收集卡牌或领袖的ID，以及1到1000的数量。";
        if(l==13)return "bg_card(132102,1)：需要可收集卡牌或領袖的ID，以及1到1000的數量。";
        return "bg_card(132102,1): needs a collectible card or leader ID and an amount from 1 to 1000.";
    }
    if(key==12){
        if(l==1)return "{0} ({1}): добавлено {2}, в наличии {3} / {4}.";
        if(l==3)return "{0} ({1}): {2} hinzugefügt, im Besitz {3} / {4}.";
        if(l==4)return "{0} ({1}) : {2} ajoutés, possédés {3} / {4}.";
        if(l==5)return "{0} ({1}): aggiunte {2}, possedute {3} / {4}.";
        if(l==6)return "{0} ({1}): dodano {2}, posiadane {3} / {4}.";
        if(l==7)return "{0} ({1}): se añadieron {2}, en posesión {3} / {4}.";
        if(l==8)return "{0} ({1}): se agregaron {2}, en posesión {3} / {4}.";
        if(l==9)return "{0} ({1}): {2} adicionadas, possui {3} / {4}.";
        if(l==10)return "{0}（{1}）：{2}枚追加、所持{3} / {4}。";
        if(l==11)return "{0} ({1}): {2}장 추가, 보유 {3} / {4}.";
        if(l==12)return "{0}（{1}）：已添加{2}，持有{3} / {4}。";
        if(l==13)return "{0}（{1}）：已新增{2}，持有{3} / {4}。";
        return "{0} ({1}): added {2}, owned {3} / {4}.";
    }
    if(key==13){
        if(l==1)return "bg_find('Имлерих'): введите от 2 до 80 символов.";
        if(l==3)return "bg_find('Imlerith'): Gib 2 bis 80 Zeichen ein.";
        if(l==4)return "bg_find('Imlerith') : saisissez de 2 à 80 caractères.";
        if(l==5)return "bg_find('Imlerith'): inserisci da 2 a 80 caratteri.";
        if(l==6)return "bg_find('Imlerith'): wpisz od 2 do 80 znaków.";
        if(l==7)return "bg_find('Imlerith'): escribe de 2 a 80 caracteres.";
        if(l==8)return "bg_find('Imlerith'): escribe de 2 a 80 caracteres.";
        if(l==9)return "bg_find('Imlerith'): digite de 2 a 80 caracteres.";
        if(l==10)return "bg_find('Imlerith')：2～80文字を入力してください。";
        if(l==11)return "bg_find('Imlerith'): 2~80자를 입력하세요.";
        if(l==12)return "bg_find('Imlerith')：请输入2到80个字符。";
        if(l==13)return "bg_find('Imlerith')：請輸入2到80個字元。";
        return "bg_find('Imlerith'): enter 2 to 80 characters.";
    }
    if(key==14){
        if(l==1)return "Найдено: {0}. Полный список — в журнале BetaGwent.";
        if(l==3)return "Gefunden: {0}. Die vollständige Liste steht im BetaGwent-Log.";
        if(l==4)return "Trouvés : {0}. La liste complète est dans le journal BetaGwent.";
        if(l==5)return "Trovate: {0}. L’elenco completo è nel registro BetaGwent.";
        if(l==6)return "Znaleziono: {0}. Pełna lista jest w dzienniku BetaGwent.";
        if(l==7)return "Encontradas: {0}. La lista completa está en el registro de BetaGwent.";
        if(l==8)return "Encontradas: {0}. La lista completa está en el registro de BetaGwent.";
        if(l==9)return "Encontradas: {0}. A lista completa está no log do BetaGwent.";
        if(l==10)return "見つかった数：{0}。全リストはBetaGwentのログにあります。";
        if(l==11)return "찾은 항목: {0}. 전체 목록은 BetaGwent 로그에 있습니다.";
        if(l==12)return "找到：{0}。完整列表见BetaGwent日志。";
        if(l==13)return "找到：{0}。完整清單見BetaGwent記錄。";
        return "Found: {0}. The full list is in the BetaGwent log.";
    }
    if(key==15){
        if(l==1)return "Фракции: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==3)return "Fraktionen: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==4)return "Factions : neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==5)return "Fazioni: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==6)return "Frakcje: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==7)return "Facciones: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==8)return "Facciones: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==9)return "Facções: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
        if(l==10)return "勢力：neutral, monsters, nilfgaard, north, scoiatael, skellige";
        if(l==11)return "진영: neutral, monsters, nilfgaard, north, scoiatael, skellige";
        if(l==12)return "阵营：neutral, monsters, nilfgaard, north, scoiatael, skellige";
        if(l==13)return "陣營：neutral, monsters, nilfgaard, north, scoiatael, skellige";
        return "Factions: neutral, monsters, nilfgaard, north, scoiatael, skellige.";
    }
    if(key==16){
        if(l==1)return "bg_faction: добавлено {0} копий до лимита фракции {1}.";
        if(l==3)return "bg_faction: {0} Kopien bis zum Limit der Fraktion {1} hinzugefügt.";
        if(l==4)return "bg_faction : {0} exemplaires ajoutés jusqu’à la limite de la faction {1}.";
        if(l==5)return "bg_faction: aggiunte {0} copie fino al limite della fazione {1}.";
        if(l==6)return "bg_faction: dodano {0} kopii do limitu frakcji {1}.";
        if(l==7)return "bg_faction: se añadieron {0} copias hasta el límite de la facción {1}.";
        if(l==8)return "bg_faction: se agregaron {0} copias hasta el límite de la facción {1}.";
        if(l==9)return "bg_faction: {0} cópias adicionadas até o limite da facção {1}.";
        if(l==10)return "bg_faction：勢力{1}の上限まで{0}枚追加しました。";
        if(l==11)return "bg_faction: {1} 진영 한도까지 {0}장을 추가했습니다.";
        if(l==12)return "bg_faction：已按{1}阵营上限添加{0}张。";
        if(l==13)return "bg_faction：已依{1}陣營上限新增{0}張。";
        return "bg_faction: added {0} copies up to the {1} faction limit.";
    }
    if(key==17){
        if(l==1)return "bg_leaders: добавлено {0} лидеров.";
        if(l==3)return "bg_leaders: {0} Anführer hinzugefügt.";
        if(l==4)return "bg_leaders : {0} chefs ajoutés.";
        if(l==5)return "bg_leaders: aggiunti {0} comandanti.";
        if(l==6)return "bg_leaders: dodano {0} dowódców.";
        if(l==7)return "bg_leaders: se añadieron {0} líderes.";
        if(l==8)return "bg_leaders: se agregaron {0} líderes.";
        if(l==9)return "bg_leaders: {0} líderes adicionados.";
        if(l==10)return "bg_leaders：リーダーを{0}人追加しました。";
        if(l==11)return "bg_leaders: 지휘관 {0}명을 추가했습니다.";
        if(l==12)return "bg_leaders：已添加{0}名领袖。";
        if(l==13)return "bg_leaders：已新增{0}名領袖。";
        return "bg_leaders: added {0} leaders.";
    }
    if(key==18){
        if(l==1)return "Коллекция: {0} / {1}, копий: {2}; бочки: {3}; осколки: {4}; выбор бочки: {5}; NG+: {6}";
        if(l==3)return "Sammlung: {0} / {1}, Kopien: {2}; Fässer: {3}; Fetzen: {4}; Fassauswahl: {5}; NG+: {6}";
        if(l==4)return "Collection : {0} / {1}, exemplaires : {2} ; barils : {3} ; fragments : {4} ; choix de baril : {5} ; NG+ : {6}";
        if(l==5)return "Collezione: {0} / {1}, copie: {2}; barili: {3}; frammenti: {4}; scelta barile: {5}; NG+: {6}";
        if(l==6)return "Kolekcja: {0} / {1}, kopie: {2}; beczki: {3}; skrawki: {4}; wybór z beczki: {5}; NG+: {6}";
        if(l==7)return "Colección: {0} / {1}, copias: {2}; barriles: {3}; fragmentos: {4}; elección de barril: {5}; NG+: {6}";
        if(l==8)return "Colección: {0} / {1}, copias: {2}; barriles: {3}; fragmentos: {4}; elección de barril: {5}; NG+: {6}";
        if(l==9)return "Coleção: {0} / {1}, cópias: {2}; barris: {3}; fragmentos: {4}; escolha de barril: {5}; NG+: {6}";
        if(l==10)return "コレクション：{0} / {1}、枚数：{2}、タル：{3}、紙片：{4}、タルの選択：{5}、NG+：{6}";
        if(l==11)return "카드 수집: {0} / {1}, 사본: {2}; 카드통: {3}; 조각: {4}; 카드통 선택: {5}; NG+: {6}";
        if(l==12)return "收藏：{0} / {1}，张数：{2}；卡桶：{3}；碎片：{4}；卡桶选择：{5}；NG+：{6}";
        if(l==13)return "收藏：{0} / {1}，張數：{2}；卡桶：{3}；碎片：{4}；卡桶選擇：{5}；NG+：{6}";
        return "Collection: {0} / {1}, copies: {2}; kegs: {3}; scraps: {4}; keg choice: {5}; NG+: {6}";
    }
    if(key==19){
        if(l==1)return "Откройте магазин продавца.";
        if(l==3)return "Öffne den Laden eines Händlers.";
        if(l==4)return "Ouvrez la boutique d’un marchand.";
        if(l==5)return "Apri il negozio di un mercante.";
        if(l==6)return "Otwórz sklep kupca.";
        if(l==7)return "Abre la tienda de un mercader.";
        if(l==8)return "Abre la tienda de un comerciante.";
        if(l==9)return "Abra a loja de um mercador.";
        if(l==10)return "商人の店を開いてください。";
        if(l==11)return "상인의 상점을 여세요.";
        if(l==12)return "请打开商人的商店。";
        if(l==13)return "請打開商人的商店。";
        return "Open a merchant's shop.";
    }
    if(key==20){
        if(l==1)return "bg_shoprefill(5): целевой запас от 1 до 99.";
        if(l==3)return "bg_shoprefill(5): Zielbestand von 1 bis 99.";
        if(l==4)return "bg_shoprefill(5) : stock cible de 1 à 99.";
        if(l==5)return "bg_shoprefill(5): scorta desiderata da 1 a 99.";
        if(l==6)return "bg_shoprefill(5): docelowy zapas od 1 do 99.";
        if(l==7)return "bg_shoprefill(5): existencias objetivo de 1 a 99.";
        if(l==8)return "bg_shoprefill(5): existencias objetivo de 1 a 99.";
        if(l==9)return "bg_shoprefill(5): estoque desejado de 1 a 99.";
        if(l==10)return "bg_shoprefill(5)：目標在庫は1～99です。";
        if(l==11)return "bg_shoprefill(5): 목표 재고는 1~99입니다.";
        if(l==12)return "bg_shoprefill(5)：目标库存为1到99。";
        if(l==13)return "bg_shoprefill(5)：目標庫存為1到99。";
        return "bg_shoprefill(5): target stock from 1 to 99.";
    }
    if(key==21){
        if(l==1)return "Откройте магазин корчмаря.";
        if(l==3)return "Öffne den Laden eines Wirts.";
        if(l==4)return "Ouvrez la boutique d’un aubergiste.";
        if(l==5)return "Apri il negozio di un oste.";
        if(l==6)return "Otwórz sklep karczmarza.";
        if(l==7)return "Abre la tienda de un posadero.";
        if(l==8)return "Abre la tienda de un posadero.";
        if(l==9)return "Abra a loja de um estalajadeiro.";
        if(l==10)return "宿屋の主人の店を開いてください。";
        if(l==11)return "여관 주인의 상점을 여세요.";
        if(l==12)return "请打开旅店老板的商店。";
        if(l==13)return "請打開旅店老闆的商店。";
        return "Open an innkeeper's shop.";
    }
    if(key==22){
        if(l==1)return "Фракции: neutral, monsters, nilfgaard, north, scoiatael, skellige. Выдача ресурсов — при закрытых меню; магазин — при открытом магазине.";
        if(l==3)return "Fraktionen: neutral, monsters, nilfgaard, north, scoiatael, skellige. Ressourcen nur bei geschlossenen Menüs; Ladenbefehle bei geöffnetem Laden.";
        if(l==4)return "Factions : neutral, monsters, nilfgaard, north, scoiatael, skellige. Ressources avec les menus fermés ; commandes de boutique avec une boutique ouverte.";
        if(l==5)return "Fazioni: neutral, monsters, nilfgaard, north, scoiatael, skellige. Risorse con i menu chiusi; comandi del negozio con un negozio aperto.";
        if(l==6)return "Frakcje: neutral, monsters, nilfgaard, north, scoiatael, skellige. Zasoby przy zamkniętych menu; polecenia sklepu przy otwartym sklepie.";
        if(l==7)return "Facciones: neutral, monsters, nilfgaard, north, scoiatael, skellige. Recursos con los menús cerrados; comandos de tienda con una tienda abierta.";
        if(l==8)return "Facciones: neutral, monsters, nilfgaard, north, scoiatael, skellige. Recursos con los menús cerrados; comandos de tienda con una tienda abierta.";
        if(l==9)return "Facções: neutral, monsters, nilfgaard, north, scoiatael, skellige. Recursos com os menus fechados; comandos de loja com uma loja aberta.";
        if(l==10)return "勢力：neutral, monsters, nilfgaard, north, scoiatael, skellige。リソースはメニューを閉じた状態で、店のコマンドは店を開いた状態で使用します。";
        if(l==11)return "진영: neutral, monsters, nilfgaard, north, scoiatael, skellige. 자원은 메뉴를 닫은 상태에서, 상점 명령은 상점을 연 상태에서 사용합니다.";
        if(l==12)return "阵营：neutral, monsters, nilfgaard, north, scoiatael, skellige。发放资源时需关闭菜单；商店命令需打开商店。";
        if(l==13)return "陣營：neutral, monsters, nilfgaard, north, scoiatael, skellige。發放資源時需關閉選單；商店指令需打開商店。";
        return "Factions: neutral, monsters, nilfgaard, north, scoiatael, skellige. Resources are granted with menus closed; shop commands need an open shop.";
    }
    if(key==23){
        if(l==1)return "Инвентарь продавца недоступен.";
        if(l==3)return "Händlerinventar nicht verfügbar.";
        if(l==4)return "Inventaire du marchand indisponible.";
        if(l==5)return "Inventario del mercante non disponibile.";
        if(l==6)return "Ekwipunek kupca niedostępny.";
        if(l==7)return "Inventario del mercader no disponible.";
        if(l==8)return "Inventario del comerciante no disponible.";
        if(l==9)return "Inventário do mercador indisponível.";
        if(l==10)return "商人の所持品を利用できません。";
        if(l==11)return "상인 인벤토리를 사용할 수 없습니다.";
        if(l==12)return "商人库存不可用。";
        if(l==13)return "商人庫存無法使用。";
        return "Merchant inventory unavailable.";
    }
    if(key==24){
        if(l==1)return "Запас бочек должен быть от 1 до 99.";
        if(l==3)return "Der Fassbestand muss zwischen 1 und 99 liegen.";
        if(l==4)return "Le stock de barils doit être de 1 à 99.";
        if(l==5)return "La scorta di barili deve essere da 1 a 99.";
        if(l==6)return "Zapas beczek musi wynosić od 1 do 99.";
        if(l==7)return "Las existencias de barriles deben ser de 1 a 99.";
        if(l==8)return "Las existencias de barriles deben ser de 1 a 99.";
        if(l==9)return "O estoque de barris deve ser de 1 a 99.";
        if(l==10)return "タルの在庫は1～99にしてください。";
        if(l==11)return "카드통 재고는 1~99여야 합니다.";
        if(l==12)return "卡桶库存必须为1到99。";
        if(l==13)return "卡桶庫存必須為1到99。";
        return "Keg stock must be from 1 to 99.";
    }
    if(key==25){
        if(l==1)return " · Пополнение доступно у корчмаря.";
        if(l==3)return " · Auffüllen ist nur bei Wirten möglich.";
        if(l==4)return " · Le réapprovisionnement n’est possible que chez les aubergistes.";
        if(l==5)return " · Il rifornimento è disponibile solo dagli osti.";
        if(l==6)return " · Uzupełnianie jest dostępne tylko u karczmarzy.";
        if(l==7)return " · Reabastecer solo es posible con posaderos.";
        if(l==8)return " · Reabastecer solo es posible con posaderos.";
        if(l==9)return " · Reabastecer só é possível com estalajadeiros.";
        if(l==10)return " · 補充は宿屋の主人でのみ可能です。";
        if(l==11)return " · 보충은 여관 주인에게서만 가능합니다.";
        if(l==12)return " · 只能在旅店老板处补货。";
        if(l==13)return " · 只能在旅店老闆處補貨。";
        return " · Refill is available only at innkeepers.";
    }
    if(key==26){
        if(l==1)return " · Предмет не создан: проверьте установку DLC с определением бочки.";
        if(l==3)return " · Gegenstand nicht erstellt: Prüfe, ob das DLC des Mods mit der Fassdefinition installiert ist.";
        if(l==4)return " · Objet non créé : vérifiez que le DLC du mod contenant la définition du baril est installé.";
        if(l==5)return " · Oggetto non creato: verifica che il DLC della mod con la definizione del barile sia installato.";
        if(l==6)return " · Przedmiot nie został utworzony: sprawdź, czy DLC moda z definicją beczki jest zainstalowane.";
        if(l==7)return " · No se creó el objeto: comprueba que el DLC del mod con la definición del barril esté instalado.";
        if(l==8)return " · No se creó el objeto: verifica que el DLC del mod con la definición del barril esté instalado.";
        if(l==9)return " · O item não foi criado: verifique se o DLC do mod com a definição do barril está instalado.";
        if(l==10)return " · アイテムが作成されませんでした：タルの定義を含むModのDLCがインストールされているか確認してください。";
        if(l==11)return " · 아이템이 생성되지 않았습니다: 카드통 정의가 포함된 모드 DLC가 설치되어 있는지 확인하세요.";
        if(l==12)return " · 未创建物品：请检查包含卡桶定义的模组DLC是否已安装。";
        if(l==13)return " · 未建立物品：請檢查包含卡桶定義的模組DLC是否已安裝。";
        return " · The item was not created: check that the mod's DLC with the keg definition is installed.";
    }
    if(key==27){
        if(l==1)return "Колода {0}";
        if(l==3)return "Deck {0}";
        if(l==4)return "Deck {0}";
        if(l==5)return "Mazzo {0}";
        if(l==6)return "Talia {0}";
        if(l==7)return "Mazo {0}";
        if(l==8)return "Mazo {0}";
        if(l==9)return "Baralho {0}";
        if(l==10)return "デッキ{0}";
        if(l==11)return "덱 {0}";
        if(l==12)return "牌组{0}";
        if(l==13)return "牌組{0}";
        return "Deck {0}";
    }
    if(key==28){
        if(l==1)return "Gwent Beta Classic: резервную копию профиля гвинта применить не удалось, начат новый профиль.";
        if(l==3)return "Gwent Beta Classic: Die Sicherung des Gwent-Profils konnte nicht angewendet werden, ein neues Profil wurde begonnen.";
        if(l==4)return "Gwent Beta Classic : la sauvegarde du profil de Gwynt n’a pas pu être appliquée, un nouveau profil a été créé.";
        if(l==5)return "Gwent Beta Classic: impossibile applicare il backup del profilo di Gwent, è stato avviato un nuovo profilo.";
        if(l==6)return "Gwent Beta Classic: nie udało się zastosować kopii profilu gwinta, rozpoczęto nowy profil.";
        if(l==7)return "Gwent Beta Classic: no se pudo aplicar la copia del perfil de Gwent; se inició un perfil nuevo.";
        if(l==8)return "Gwent Beta Classic: no se pudo aplicar la copia del perfil de Gwent; se inició un perfil nuevo.";
        if(l==9)return "Gwent Beta Classic: não foi possível aplicar o backup do perfil de Gwent; um novo perfil foi iniciado.";
        if(l==10)return "Gwent Beta Classic：グウェントのプロフィールのバックアップを適用できませんでした。新しいプロフィールを開始しました。";
        if(l==11)return "Gwent Beta Classic: 궨트 프로필 백업을 적용할 수 없어 새 프로필을 시작했습니다.";
        if(l==12)return "Gwent Beta Classic：无法应用昆特牌档案备份，已开始新档案。";
        if(l==13)return "Gwent Beta Classic：無法套用昆特牌檔案備份，已開始新檔案。";
        return "Gwent Beta Classic: the Gwent profile backup could not be applied, a new profile was started.";
    }
    if(key==29){
        if(l==1)return " · Бочек в запасе нет; создание предмета не проверено.";
        if(l==3)return " · Keine Fässer auf Lager; Erstellung des Gegenstands nicht geprüft.";
        if(l==4)return " · Aucun baril en stock ; création de l’objet non vérifiée.";
        if(l==5)return " · Nessun barile in scorta; creazione dell’oggetto non verificata.";
        if(l==6)return " · Brak beczek w zapasie; tworzenia przedmiotu nie sprawdzono.";
        if(l==7)return " · No hay barriles en existencia; no se comprobó la creación del objeto.";
        if(l==8)return " · No hay barriles en existencia; no se verificó la creación del objeto.";
        if(l==9)return " · Não há barris em estoque; a criação do item não foi verificada.";
        if(l==10)return " · タルの在庫がありません。アイテムの作成は未確認です。";
        if(l==11)return " · 카드통 재고가 없습니다. 아이템 생성은 확인되지 않았습니다.";
        if(l==12)return " · 没有卡桶库存；未检查物品创建。";
        if(l==13)return " · 沒有卡桶庫存；未檢查物品建立。";
        return " · No kegs in stock; item creation was not checked.";
    }
    if(key==30){
        if(l==1)return " · Предмет бочки присутствует в запасе.";
        if(l==3)return " · Der Fassgegenstand ist auf Lager.";
        if(l==4)return " · L’objet baril est en stock.";
        if(l==5)return " · L’oggetto barile è in scorta.";
        if(l==6)return " · Przedmiot beczki jest w zapasie.";
        if(l==7)return " · El objeto barril está en existencia.";
        if(l==8)return " · El objeto barril está en existencia.";
        if(l==9)return " · O item barril está em estoque.";
        if(l==10)return " · タルのアイテムは在庫にあります。";
        if(l==11)return " · 카드통 아이템이 재고에 있습니다.";
        if(l==12)return " · 卡桶物品有库存。";
        if(l==13)return " · 卡桶物品有庫存。";
        return " · The keg item is in stock.";
    }
    return "";
}
function BetaGwentConsoleFormat(key : int, optional a : string, optional b : string, optional c : string, optional d : string, optional e : string, optional f : string, optional g : string) : string
{
    var s : string;
    s=BetaGwentConsoleText(key);
    s=StrReplace(s,"{0}",a);s=StrReplace(s,"{1}",b);s=StrReplace(s,"{2}",c);s=StrReplace(s,"{3}",d);
    s=StrReplace(s,"{4}",e);s=StrReplace(s,"{5}",f);s=StrReplace(s,"{6}",g);
    return s;
}
function BetaGwentConsoleHelp() : string
{
    var find : string;
    if(BetaGwentConsoleLanguage()==1)find="Имлерих";else find="Imlerith";
    return StrReplace("bg_kegs(10) · bg_scraps(1000) · bg_card(132102,1) · bg_find('{find}')\nbg_faction('monsters') · bg_leaders() · bg_allcards() · bg_status()\nbg_shopcheck() · bg_shoprefill(5) · bg_help()\nbg_clean_preview() · bg_clean_confirm('DELETE_BETA_GWENT')\n","{find}",find)+BetaGwentConsoleText(22);
}

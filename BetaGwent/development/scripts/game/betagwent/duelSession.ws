// Closed Beta-card preview with seeded shuffle and mulligan. General scheduler is separate.
class CBetaGwentDuelSession extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var events : CBetaGwentDuelEvents;
    public var drainingDeaths : bool;
    public var effects : CBetaGwentDuelEffectRuntime;
    public var playStack : array<CBetaGwentDuelCard>;
    public var match : CBetaGwentMatchState;
    public var registry : CBetaGwentDuelRegistry;
    public var live : array<CBetaGwentDuelCard>;
    public var dying : array<CBetaGwentDuelCard>;
    public var pendingConsumeVisuals : array<int>;
    public var message : string;
    public var waiting, fatal : bool;
    public var pendingCard : CBetaGwentDuelCard;
    public var pendingLeader : CBetaGwentDuelCard;
    public var pendingRally : CBetaGwentDuelCard;
    public var pendingChoice : bool;
    public var weather : CBetaGwentDuelWeather;
    public var specials : CBetaGwentDuelSpecials;
    public var monsters : CBetaGwentDuelMonsters;
    public var monsterMinimum, monsterMaximum : int;
    public var specialHitsLeft, handPowerTarget : int;
    public var pendingHandPower : bool;
    public var pendingPileChoice : bool;
    public var pendingIds : array<int>;
    public var requestId : int;
    public var pendingRow : bool;
    public var random : CBetaGwentRandomGenerator;
    public var mulligan : bool;
    public var mulliganBudget, mulliganUsed, roundStarter : int;
    public var blacklistedTemplates, reservedCards : array<int>;
    public var visualFrames : array<CBetaGwentDuelVisualFrame>;
    public var recordVisuals, visualOverflow : bool;
    public var visualSourceId, visualTemplateId, visualSide, visualRow : int;
    public var visualAttack : int;
    public var presetOne, presetTwo : int;
    public var leaderTemplateOne, leaderTemplateTwo : int;
    public var nilfJobs : array<CBetaGwentNilfReaction>;
    public var nilfJob : CBetaGwentNilfReaction;
    public var nilfEndingTurn : bool;
    public var mulliganReactions : bool;
    public var nilfInitialOne, nilfInitialTwo : array<int>;
    public var nilfSpellOne, nilfSpellTwo, nilfLastMovedUnit : int;
    public var weatherAI : CBetaGwentWeatherAI;
    public var weatherProfile : bool;
    public var archetypeAI : CBetaGwentArchetypeAI;
    public var aiChaseRound, aiChaseInitialHand : int;
    public var aiObservedRound, aiObservedEnemyScore, aiPublicTempo : int;
    public var aiRoundHandOne, aiRoundHandTwo : int;
    public var aiPlacing : SBetaGwentDuelDefinition;
    public var aiSimulating : bool; public var aiCloneEpoch : int; public var aiSimCloner : CBetaGwentCloner;
    public var aiSimDamp : int;

    public function InitializeFixture()
    { InitializeWithPresets(1, 1); }
    public function PresetId(side : int) : int
    { if (side == 1) return presetOne; if (side == 2) return presetTwo; return 0; }
    public function LeaderTemplateId(side : int) : int
    { if (side == 1) return leaderTemplateOne; if (side == 2) return leaderTemplateTwo; return 0; }
    public function InitializeWithPresets(ownPreset : int, enemyPreset : int, optional ownLeader : int, optional enemyLeader : int) : bool
    {
        var ownCards, enemyCards : array<int>; var own, enemy : SBetaGwentDuelPreset;
        own = BetaGwentDuelPreset(ownPreset); enemy = BetaGwentDuelPreset(enemyPreset);
        if (own.id == 0 || enemy.id == 0) return false;
        if (ownLeader == 0) ownLeader = own.leaderTemplateId;
        if (enemyLeader == 0) enemyLeader = enemy.leaderTemplateId;
        if (!BetaGwentDuelPresetDeck(ownPreset, ownCards) || !BetaGwentDuelPresetDeck(enemyPreset, enemyCards)) return false;
        return InitializeWithDecks(ownCards, enemyCards, ownLeader, enemyLeader, ownPreset, enemyPreset);
    }
    public function InitializeWithDecks(ownCards : array<int>, enemyCards : array<int>, ownLeader : int, enemyLeader : int,
        optional ownPreset : int, optional enemyPreset : int) : bool
    {
        var ids : array<int>; var i, side, id, starter : int;
        var card : CBetaGwentDuelCard; var definition : SBetaGwentDuelDefinition;
        var validation : SBetaGwentDeckValidation;
        definition = BetaGwentDuelDefinition(ownLeader);
        validation = BetaGwentValidateDeck(ownCards, definition.header.factionMask, ownLeader); if (!validation.valid) return false;
        definition = BetaGwentDuelDefinition(enemyLeader);
        validation = BetaGwentValidateDeck(enemyCards, definition.header.factionMask, enemyLeader); if (!validation.valid) return false;
        leaderTemplateOne = ownLeader; leaderTemplateTwo = enemyLeader;
        aiChaseRound=0;aiChaseInitialHand=0;
        nilfInitialOne=ownCards;nilfInitialTwo=enemyCards;nilfJobs.Clear();nilfJob=NULL;nilfEndingTurn=false;mulliganReactions=false;
        nilfSpellOne=0;nilfSpellTwo=0;nilfLastMovedUnit=0;
        presetOne = ownPreset; presetTwo = enemyPreset;
        weatherAI=new CBetaGwentWeatherAI in this;weatherAI.Initialize(this);weatherProfile=weatherAI.Matches(enemyCards);
        archetypeAI=new CBetaGwentArchetypeAI in this;archetypeAI.Initialize(this,enemyCards,enemyPreset,enemyLeader);
        BetaGwentLog("DUEL_AI_ARCHETYPE id="+archetypeAI.ProfileId()+" title="+archetypeAI.Title()+" policy=rules88");
        BetaGwentLog("DUEL_AI_PROFILE weather="+weatherProfile+" enemyPreset="+enemyPreset+" privatePlayerCardsRead=false");
        recordVisuals = false; visualFrames.Clear(); visualOverflow = false; pendingConsumeVisuals.Clear();
        SetVisualSource(0, 0, 0, 0);
        match = new CBetaGwentMatchState in this; match.Initialize();
        registry = new CBetaGwentDuelRegistry in this; registry.Initialize();
        weather = new CBetaGwentDuelWeather in this; weather.Initialize(this);
        specials = new CBetaGwentDuelSpecials in this; specials.Initialize(this, weather);
        monsters = new CBetaGwentDuelMonsters in this; monsters.Initialize(this);
        effects = new CBetaGwentDuelEffectRuntime in this; effects.Initialize(this); playStack.Clear();
        events = new CBetaGwentDuelEvents in this; events.Initialize(this); drainingDeaths = false;
        pendingRally = NULL; pendingChoice = false; pendingHandPower = false; pendingPileChoice = false; handPowerTarget = 0; specialHitsLeft = 0;
        live.Clear(); dying.Clear(); pendingLeader = NULL; pendingCard = NULL; pendingIds.Clear();
        waiting = false; fatal = false; pendingRow = false;
        aiChaseRound=0;aiChaseInitialHand=0;aiObservedRound=0;aiObservedEnemyScore=0;aiPublicTempo=14;aiSimDamp=40;
        mulligan = false; blacklistedTemplates.Clear(); reservedCards.Clear();
        random = new CBetaGwentRandomGenerator in this;
        random.Initialize(RandRange(2147483647));
        // Keep request IDs increasing across Restart to reject old clicks.
        for (side = 1; side <= 2; side += 1)
        {
            ids.Clear();
            if (side == 1) { for (i = 0; i < ownCards.Size(); i += 1) ids.PushBack(ownCards[i]); }
            else { for (i = 0; i < enemyCards.Size(); i += 1) ids.PushBack(enemyCards[i]); }
            random.Shuffle(ids);
            for (i = 0; i < ids.Size(); i += 1)
            {
                if (!registry.Allocate(id) || id == 0 || registry.Find(id)) { fatal = true; return false; }
                card = new CBetaGwentDuelCard in this; card.Setup(this, id, ids[i], side, 16, i);
                registry.Put(id, card); live.PushBack(card);
            }
            if (!registry.Allocate(id) || id == 0 || registry.Find(id)) { fatal = true; return false; }
            card = new CBetaGwentDuelCard in this;
            if (side == 1) card.Setup(this, id, leaderTemplateOne, side, 64, 0);
            else card.Setup(this, id, leaderTemplateTwo, side, 64, 0);
            registry.Put(id, card); live.PushBack(card);
            NorthBeginGame(side); Draw(side, 10);
        }
        starter = 1 + random.NextBounded(2);
        Require(match.ApplyRoundStarted(starter)); BeginMulligan(starter, 3);
        BetaGwentLog("DUEL_STARTED schema=4 cards=" + live.Size() + " hand=10 fixedOrder=false mulligan=true ownPreset=" + presetOne + " enemyPreset=" + presetTwo + " ownLeader=" + leaderTemplateOne + " enemyLeader=" + leaderTemplateTwo + " seed="
            + random.InitialSeed() + " draws=" + random.DrawCount() + " starter=" + starter);
        recordVisuals = true;
        return !fatal;
    }
    public function GetVisualSource() : SBetaGwentDuelCueContext
    {
        var value : SBetaGwentDuelCueContext;
        value.id = visualSourceId; value.templateId = visualTemplateId; value.side = visualSide; value.row = visualRow; return value;
    }
    public function PendingEventCount() : int { return events.Count(); }
    public function NextEventBatchSerial() : int { return events.NextBatchSerial(); }
    public function PopDuelEvent() : CBetaGwentDuelEvent { return events.Pop(); }
    public function SetVisualSource(id : int, templateId : int, side : int, row : int)
    { visualSourceId = id; visualTemplateId = templateId; visualSide = side; visualRow = row; }
    public var effectSourceDepth, savedSourceId, savedSourceTemplate, savedSourceSide, savedSourceRow : int;
    public function BeginEffectSource(card : CBetaGwentDuelCard) : bool
    {
        var s : SBetaGwentCardSnapshot;
        if (!card || !recordVisuals) return false;
        s = card.Snapshot(); if ((s.locationMask & 7) == 0) return false;
        if (effectSourceDepth == 0) { savedSourceId = visualSourceId; savedSourceTemplate = visualTemplateId; savedSourceSide = visualSide; savedSourceRow = visualRow; }
        effectSourceDepth += 1;
        SetVisualSource(s.instanceId, s.runtimeTemplate.templateId, s.positionPlayerId, s.locationMask);
        return true;
    }
    public function EndEffectSource()
    {
        effectSourceDepth = Max(0, effectSourceDepth - 1);
        if (effectSourceDepth == 0) SetVisualSource(savedSourceId, savedSourceTemplate, savedSourceSide, savedSourceRow);
    }
    public function VisualSnapshot() : CBetaGwentDuelVisualFrame
    {
        var frame : CBetaGwentDuelVisualFrame; var side, row, i : int;
        var v : SBetaGwentDevelopmentCard; var d : SBetaGwentDuelDefinition;
        frame = new CBetaGwentDuelVisualFrame in this;
        frame.matchState = match.Snapshot();
        // One pass computes display totals and copies only visible cards / pending choices.
        for (i = 0; i < live.Size(); i += 1)
        {
            v.card = live[i].Snapshot(); side = v.card.positionPlayerId;
            if ((v.card.locationMask & 7) != 0 && (v.card.tokenMask & 8) == 0)
            { if (side == 1) frame.scoreOne += v.card.power.currentPower; if (side == 2) frame.scoreTwo += v.card.power.currentPower; }
            if (v.card.locationMask == 8 && side == 2) frame.enemyHand += 1;
            if (v.card.locationMask == 32) { if (side == 1) frame.graveOne += 1; if (side == 2) frame.graveTwo += 1; }
            if (v.card.locationMask == 16) { if (side == 1) frame.deckOne += 1; if (side == 2) frame.deckTwo += 1; }
            if (v.card.locationMask == 64 && v.card.canBePlayed) { if (side == 1) frame.leaderOne = true; if (side == 2) frame.leaderTwo = true; }
            if ((v.card.locationMask & 7) == 0 && !(v.card.locationMask == 8 && (side == 1 || (v.card.tokenMask & 64) != 0))
                && !((v.card.locationMask == 16 || v.card.locationMask == 32) && pendingIds.Contains(v.card.instanceId))) continue;
            d = live[i].Definition(); v.title = d.title; frame.cards.PushBack(v);
        }
        frame.flags = frame.matchState.matchWinnerMask * 16;
        if (frame.matchState.playerOne.hasPassed) frame.flags = frame.flags | 1;
        if (frame.matchState.playerTwo.hasPassed) frame.flags = frame.flags | 2;
        if (waiting) frame.flags = frame.flags | 4;
        if (fatal) frame.flags = frame.flags | 8;
        for (side = 1; side <= 2; side += 1)
            for (row = 1; row <= 4; row *= 2)
            {
                frame.weatherTokens.PushBack(weather.Token(side, row));
                frame.weatherDamage.PushBack(weather.Damage(side, row));
            }
        frame.status = message; return frame;
    }
    public function SetVisualAttack(id : int) : int { var previous : int; previous = visualAttack; visualAttack = id; return previous; }
    public function RecordVisual(kind : int, targetId : int, caption : string, duration : int, optional audioType : int)
    {
        var frame, merged : CBetaGwentDuelVisualFrame; var target : CBetaGwentDuelCard; var t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!recordVisuals || visualOverflow) return;
        // Same attack, same kind: the original applies all targets at once. Keep one
        // frame (first cue, latest snapshot) instead of one frame per target.
        if (visualAttack != 0 && visualFrames.Size() > 0)
        {
            merged = visualFrames[visualFrames.Size() - 1];
            if (merged.attackId == visualAttack && merged.kind == kind)
            {
                frame = VisualSnapshot(); frame.kind = merged.kind; frame.targetId = merged.targetId; frame.audioKind = merged.audioKind;
                frame.sourceId = merged.sourceId; frame.templateId = merged.templateId; frame.side = merged.side; frame.row = merged.row;
                frame.targetTemplateId = merged.targetTemplateId; frame.targetPower = merged.targetPower; frame.targetSide = merged.targetSide; frame.targetZone = merged.targetZone;
                frame.attackId = merged.attackId; frame.attackCount = merged.attackCount + 1; frame.duration = Max(merged.duration, duration);
                d = BetaGwentDuelDefinition(merged.templateId);
                if (d.header.templateId != 0) frame.status = d.title + ": целей " + frame.attackCount; else frame.status = merged.status;
                visualFrames[visualFrames.Size() - 1] = frame; return;
            }
        }
        // Bound presentation memory; final live snapshot still follows on overflow.
        if (visualFrames.Size() >= 128)
        { visualOverflow = true; BetaGwentLog("DUEL_VISUAL_TRUNCATED limit=128"); return; }
        frame = VisualSnapshot(); frame.kind = kind; frame.targetId = targetId; frame.audioKind = audioType;
        frame.attackId = visualAttack; frame.attackCount = 1;
        frame.sourceId = visualSourceId; frame.templateId = visualTemplateId;
        frame.side = visualSide; frame.row = visualRow;
        target = registry.Find(targetId);
        if (target)
        {
            t = target.Snapshot();
            if (audioType == 25) frame.templateId = t.runtimeTemplate.templateId;
            // Presentation-only metadata, never an enemy hand/deck identity.
            if ((t.locationMask & 7) != 0 || t.locationMask == 32 || t.locationMask == 512 || (t.positionPlayerId == 1 && t.locationMask == 8))
            { frame.targetTemplateId = t.runtimeTemplate.templateId; frame.targetPower = t.power.currentPower; frame.targetSide = t.positionPlayerId; frame.targetZone = t.locationMask; }
        }
        frame.status = caption; frame.duration = duration; visualFrames.PushBack(frame);
    }
    public function RecordPowerVisual(card : CBetaGwentDuelCard, oldPower : int, oldArmor : int)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = card.Snapshot(); if ((s.locationMask & 7) == 0) return;
        d = card.Definition();
        RecordVisual(2, s.instanceId, d.title + ": " + oldPower + " → " + s.power.currentPower
            + ", броня " + oldArmor + " → " + s.power.armor, 260);
        if (visualFrames.Size() > 0 && !visualOverflow)
        {
            if (s.power.currentPower < oldPower) visualFrames[visualFrames.Size()-1].audioKind = 20;
            else if (s.power.currentPower > oldPower) visualFrames[visualFrames.Size()-1].audioKind = 21;
            else if (s.power.armor < oldArmor) visualFrames[visualFrames.Size()-1].audioKind = 22;
            else if (s.power.armor > oldArmor) visualFrames[visualFrames.Size()-1].audioKind = 23;
        }
    }
    public function RecordRowVisual(side : int, row : int, caption : string)
    {
        var previousSide, previousRow : int;
        previousSide = visualSide; previousRow = visualRow;
        visualSide = side; visualRow = row; RecordVisual(4, 0, caption, 380);
        visualSide = previousSide; visualRow = previousRow;
    }
    public function TakeVisualFrames(out frames : array<CBetaGwentDuelVisualFrame>)
    {
        var i : int; frames.Clear();
        for (i = 0; i < visualFrames.Size(); i += 1) frames.PushBack(visualFrames[i]);
        visualFrames.Clear(); visualOverflow = false;
    }
    private function Require(result : EBetaGwentStateResult) : bool
    {
        if (result == BG_StateOK) return true;
        fatal = true; message = "Ошибка партии: " + result; BetaGwentLog("DUEL_STATE_ERROR " + result); return false;
    }
    public function Snapshot() : SBetaGwentMatchSnapshot { return match.Snapshot(); }
    public function GetMessage() : string { return message; }
    public function IsWaitingRound() : bool { return waiting; }
    public function IsFatal() : bool { return fatal; }
    public function IsPending() : bool { return mulligan || (bool)pendingCard || (bool)pendingLeader; }
    public function PendingSourceId() : int { var s : SBetaGwentCardSnapshot; if (!pendingCard) return 0; s = pendingCard.Snapshot(); return s.instanceId; }
    public function IsLeaderRowRequest() : bool { return (bool)pendingLeader; }
    public function IsRallyRowRequest() : bool { return (bool)pendingRally; }
    public function PlacementCard() : CBetaGwentDuelCard
    { if (pendingLeader) return pendingLeader; if (IsCaranthirMoveRequest()) return pendingCard; return pendingRally; }
    public function IsCaranthirMoveRequest() : bool
    { return (bool)pendingCard && pendingCard.MonsterMode() == 16 && !pendingRow && IsPending(); }
    public function CaranthirRow() : int
    { var s : SBetaGwentCardSnapshot; if (!IsCaranthirMoveRequest()) return 0; s = pendingCard.Snapshot(); return s.locationMask; }
    public function IsFirstLightChoice() : bool
    { var d : SBetaGwentDuelDefinition; if (!pendingChoice || !pendingCard) return false; d = pendingCard.Definition(); return d.effect == 9; }
    public function IsTemplateChoice() : bool { return pendingChoice; }
    public function IsModeChoice() : bool
    { var d : SBetaGwentDuelDefinition; if (!pendingChoice || !pendingCard) return false; d = pendingCard.Definition(); return d.effect == 33 || d.effect == 34; }
    public function IsDagonChoice() : bool
    { var d : SBetaGwentDuelDefinition; if (!pendingChoice || !pendingCard) return false; d = pendingCard.Definition(); return d.effect == 24; }
    public function IsWeatherRowRequest() : bool
    { var d : SBetaGwentDuelDefinition; if (!pendingCard) return false; d = pendingCard.Definition(); return pendingRow && d.weatherToken != 0; }
    public function SpecialRowMode() : int
    {
        var d : SBetaGwentDuelDefinition;
        if (!pendingRow || !pendingCard) return 0; d = pendingCard.Definition();
        if (d.effect == 34) { if(d.header.templateId==201523)return 1;if(d.header.templateId==200532)return 8; if (d.specialMode == 148) return 1; return 9; }
        if (d.effect != 28) return 0;
        if (d.specialRowMask == 3) return 10;
        if (d.targetSide == 1) return 8; if (d.targetSide == 2) return 9; return 1;
    }
    public function IsPileChoice() : bool { return pendingPileChoice; }
    public function IsPlayChoice() : bool
    { return pendingPileChoice && pendingCard && (!pendingCard.IsMonsterAbility() || BetaGwentDuelPlayChoice(pendingCard.TemplateId())); }
    public function IsHandPowerChoice() : bool { return pendingHandPower; }
    public function IsGraveyardChoice() : bool
    {
        var d : SBetaGwentDuelDefinition;
        if (!pendingCard) return false; d = pendingCard.Definition(); return d.consumeLocation == 32;
    }
    public function IsMulligan() : bool { return mulligan; }
    public function IsRowRequest() : bool { return (pendingRow || (bool)pendingLeader || (bool)pendingRally) && IsPending(); }
    public function FindCard(id : int) : CBetaGwentDuelCard { return registry.Find(id); }
    public function NorthActingSide(card : CBetaGwentDuelCard) : int
    { var s : SBetaGwentCardSnapshot; s = card.Snapshot(); if (BetaGwentDuelSpying(card.TemplateId()) && (s.locationMask & 7) != 0) return BetaGwentOpponentId(s.positionPlayerId); return s.positionPlayerId; }
    public function NorthPile(side : int, zone : int, out ids : array<int>)
    { var cards : array<CBetaGwentDuelCard>; var i : int; var s : SBetaGwentCardSnapshot; ids.Clear(); LocationCards(side, zone, cards); for (i=0;i<cards.Size();i+=1) { s=cards[i].Snapshot();ids.PushBack(s.instanceId); } }
    public function NorthMoveInactive(card : CBetaGwentDuelCard, side : int, zone : int, reset : bool)
    {
        var cards : array<CBetaGwentDuelCard>; var old, t : SBetaGwentCardSnapshot; var i, index : int;
        if (!card) return; old = card.Snapshot();
        if (old.locationMask == zone && old.positionPlayerId == side) card.Move(side,128,0);
        Reindex(old.positionPlayerId,old.locationMask); LocationCards(side,zone,cards); index=cards.Size();
        if(zone==16) index=RandomIndex(cards.Size()+1);
        for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.locationIndex>=index)cards[i].Move(side,zone,t.locationIndex+1);}
        card.Move(side,zone,index);card.SetPlayable(zone==8);if(reset)card.ResetInHand();Reindex(old.positionPlayerId,old.locationMask);
        MonsterMoved(old);
        RecordVisual(14,old.instanceId,"Карта перемещена",380);
    }
    public function NorthSwap(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var ids, valid : array<int>;var i, side : int;var child : CBetaGwentDuelCard;var t : SBetaGwentCardSnapshot;
        t=target.Snapshot();side=t.positionPlayerId;NorthPile(side,16,ids);
        for(i=0;i<ids.Size();i+=1)if(!source.monsterIds.Contains(ids[i]))valid.PushBack(ids[i]);
        if(valid.Size()==0)return;child=FindCard(valid[RandomIndex(valid.Size())]);source.monsterIds.PushBack(t.instanceId);
        NorthMoveInactive(target,side,16,true);NorthMoveInactive(child,side,8,false);NilfSwapped(target);
    }
    public function NorthExchange(hand : CBetaGwentDuelCard, deck : CBetaGwentDuelCard)
    { var h, d : SBetaGwentCardSnapshot;if(!hand || !deck)return;h=hand.Snapshot();d=deck.Snapshot();hand.Move(h.positionPlayerId,16,d.locationIndex);hand.SetPlayable(false);deck.Move(h.positionPlayerId,8,h.locationIndex);deck.SetPlayable(true);MonsterMoved(h);MonsterMoved(d);NilfSwapped(hand);RecordVisual(14,d.instanceId,"Обмен карты",400); }
    public function NorthSummonCopies(source : CBetaGwentDuelCard, templateId : int)
    { var ids : array<int>;var i : int;var s, t : SBetaGwentCardSnapshot;s=source.Snapshot();s.locationIndex=-4;NorthPile(s.positionPlayerId,16,ids);for(i=0;i<ids.Size();i+=1){t=FindCard(ids[i]).Snapshot();if(t.runtimeTemplate.templateId==templateId)MonsterSummon(s,FindCard(ids[i]));} }
    public function NorthRandomSummon(card : CBetaGwentDuelCard)
    { var s, pos : SBetaGwentCardSnapshot;var rows : array<int>;var row : int;s=card.Snapshot();for(row=1;row<=4;row*=2)if(CountLocation(s.positionPlayerId,row)<9)rows.PushBack(row);if(rows.Size()==0)return;pos=s;pos.locationMask=rows[RandomIndex(rows.Size())];pos.locationIndex=-3;MonsterSummon(pos,card); }
    public function NorthClearRow(side : int, row : int){weather.ClearRow(side,row);}
    public function NorthClearHazard(side : int, row : int)
    { if(MonsterIsHazard(weather.Token(side,row)))weather.ClearRow(side,row); }
    public function NorthDeathRow(id : int) : int
    { var card : CBetaGwentDuelCard;card=FindCard(id);if(card)return card.lastActiveRow;return 0; }
    public function NorthRepeatPlay(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { var s : SBetaGwentCardSnapshot;var i : int;if(playStack.Size()>=16){FailAbility("Слишком глубокая повторная способность.");return;}for(i=0;i<playStack.Size();i+=1)if(playStack[i]==target){MonsterComplete(source);return;}source.StorePlayedChild(target);s=target.Snapshot();target.playFromLocation=s.locationMask;target.ResetModeChoice();playStack.PushBack(target);ResolvePlayed(target,s.positionPlayerId); }
    public function NorthPhantom(source : CBetaGwentDuelCard)
    { var before, i : int;var pos : SBetaGwentCardSnapshot;pos=source.Snapshot();pos.locationIndex+=1;before=live.Size();QueueSpawn(pos,201624,1);if(!FlushEffects())return;for(i=before;i<live.Size();i+=1)if(live[i].TemplateId()==201624)live[i].AddTokens(512); }
    public function NorthResurrect(source : CBetaGwentDuelCard, power : int, row : int, index : int, resetBase : bool)
    {
        var s : SBetaGwentCardSnapshot;var rows : array<int>;var r : int;s=source.Snapshot();if(s.locationMask!=32)return;
        if(row==0){for(r=1;r<=4;r*=2)if(CountLocation(s.positionPlayerId,r)<9)rows.PushBack(r);if(rows.Size()==0)return;row=rows[RandomIndex(rows.Size())];}
        if(!CanInsertUnit(s.positionPlayerId,row,index))return;
        if(resetBase){source.Power().ResetTemplatePower(power,0);source.northernCrew=true;}
        source.SetWaiting(false);if(!InsertUnit(source,s.positionPlayerId,row,index))return;Reindex(s.positionPlayerId,32);source.SetPlayable(false);RecordVisual(15,s.instanceId,"Возвращение из сброса",480);
    }
    private function NorthBeginGame(side : int)
    { var ids : array<int>;var i : int;NorthPile(side,16,ids);for(i=0;i<ids.Size();i+=1)if(FindCard(ids[i]).TemplateId()==122102){MonsterDeckCopies(side,122311,1);NorthMoveInactive(live[live.Size()-1],side,16,false);} }
    private function NorthTurn(kind : int, side : int)
    { var cause : SBetaGwentCardSnapshot;cause.positionPlayerId=side;events.NorthTrigger(kind,cause); }
    public function NorthArmorBroken(card : CBetaGwentDuelCard)
    { if(events)events.NorthTrigger(6,card.Snapshot()); }

    public function NilfMatch() : SBetaGwentMatchSnapshot { return match.Snapshot(); }
    public function NilfTruce() : bool { var s : SBetaGwentMatchSnapshot;s=match.Snapshot();return !s.playerOne.hasPassed && !s.playerTwo.hasPassed; }
    public function NilfAlchemy(side : int) : int
    {var ids : array<int>;var i,count : int;ids=nilfInitialOne;if(side==2)ids=nilfInitialTwo;for(i=0;i<ids.Size();i+=1)if(BetaGwentNorthernCategory(ids[i],11))count+=1;return count;}
    public function NeutralInitial(side : int, out ids : array<int>){ids=nilfInitialOne;if(side==2)ids=nilfInitialTwo;}
    public function NeutralFaction(side : int) : int{var c : CBetaGwentDuelCard;var d : SBetaGwentDuelDefinition;c=Leader(side);if(c){d=c.Definition();return d.header.factionMask;}return 0;}
    public function NeutralCopy(side : int, templateId : int, zone : int)
    {var id : int;var child : CBetaGwentDuelCard;var d : SBetaGwentDuelDefinition;d=BetaGwentDuelDefinition(templateId);if(d.header.templateId==0 || !registry.Allocate(id)){FailAbility("Не удалось создать базовую копию.");return;}child=new CBetaGwentDuelCard in this;child.Setup(this,id,templateId,side,zone,CountLocation(side,zone));child.createdCopy=true;child.SetPlayable(zone==8);if(!registry.Put(id,child)){FailAbility("ID базовой копии занят.");return;}live.PushBack(child);RecordVisual(16,id,"Создана базовая копия",400);}
    public function NeutralReset(card : CBetaGwentDuelCard){if(!card)return;card.NeutralReset();RecordVisual(12,0,"Отряд восстановлен",400);}
    public function NeutralDrain(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, amount : int){var old : SBetaGwentCardSnapshot;old=target.Snapshot();target.ChangePower(-amount,true);NilfPowerChanged(source,target,old,target.Snapshot(),1);MonsterDamaged(source,target);}
    public function NilfInitialPool(side : int, out ids : array<int>)
    {var deck : array<int>;var d : SBetaGwentDuelDefinition;var i : int;ids.Clear();deck=nilfInitialOne;if(side==2)deck=nilfInitialTwo;for(i=0;i<deck.Size();i+=1){d=BetaGwentDuelDefinition(deck[i]);if(d.header.typeMask==4 && (d.header.tierMask&6)!=0 && deck[i]!=162210 && deck[i]!=132204 && deck[i]!=122203 && deck[i]!=142203 && deck[i]!=152214 && !ids.Contains(deck[i]))ids.PushBack(deck[i]);}}
    // Dwarven Agitator: bronze dwarves from the deck the side started with, not what is left in it.
    public function AgitatorPool(side : int, out ids : array<int>)
    {var deck : array<int>;var d : SBetaGwentDuelDefinition;var i : int;ids.Clear();deck=nilfInitialOne;if(side==2)deck=nilfInitialTwo;for(i=0;i<deck.Size();i+=1){if(deck[i]==200293 || !BetaGwentNilfDwarf(deck[i]))continue;d=BetaGwentDuelDefinition(deck[i]);if((d.header.typeMask&12)!=0 && (d.header.tierMask&2)!=0)ids.PushBack(deck[i]);}}
    public function NilfLastSpell(side : int) : int {if(side==1)return nilfSpellOne;return nilfSpellTwo;}
    public function NilfLastUnit() : int {return nilfLastMovedUnit;}
    public function NilfSwapped(card : CBetaGwentDuelCard) {monsters.NilfTrigger(10,card.Snapshot());}
    public function NilfSpyingAdded(cause : SBetaGwentCardSnapshot) {monsters.NilfTrigger(11,cause);}
    public function NilfPowerChanged(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, old : SBetaGwentCardSnapshot, current : SBetaGwentCardSnapshot, operation : int)
    {
        var cards : array<SBetaGwentDevelopmentCard>;var i : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        monsters.AddedPowerChanged(target,old,current);
        if(operation==9 || operation==18 || (old.power.currentPower==current.power.currentPower && old.power.basePower==current.power.basePower))return;
        if((current.locationMask&7)!=0 && current.runtimeTemplate.templateId==200042 && (current.tokenMask&12)==0 && source!=target && !current.isWaitingToDie)MonsterPower(target,target,2);
        if(current.power.currentPower>old.power.currentPower && (current.locationMask&15)!=0)
        {GetCards(cards);m=match.Snapshot();for(i=0;i<cards.Size();i+=1){s=cards[i].card;if(s.instanceId!=current.instanceId && s.runtimeTemplate.templateId==200136 && (s.locationMask&7)!=0 && s.positionPlayerId==current.positionPlayerId && s.positionPlayerId==m.currentPlayerId && (s.tokenMask&12)==0)FindCard(s.instanceId).SetNilfCounter(1);}}
    }
    public function NilfReactionKind() : int {if(nilfJob)return nilfJob.kind;return 0;}
    private function NilfDecisionSide() : int {var m : SBetaGwentMatchSnapshot;if(nilfJob)return nilfJob.side;m=match.Snapshot();return m.currentPlayerId;}
    public function NilfReveal(card : CBetaGwentDuelCard, reveal : bool)
    {var s : SBetaGwentCardSnapshot;if(!card)return;s=card.Snapshot();if(s.locationMask!=8 || ((s.tokenMask&64)!=0)==reveal)return;card.SetRevealed(reveal);RecordVisual(8,s.instanceId,BetaGwentNilfText(reveal),400);if(reveal)monsters.NilfTrigger(1,s);BetaGwentLog("DUEL_REVEAL card="+s.instanceId+" side="+s.positionPlayerId+" revealed="+reveal);}
    public function NilfTake(card : CBetaGwentDuelCard, side : int)
    {var s : SBetaGwentCardSnapshot;if(!card)return;s=card.Snapshot();NorthMoveInactive(card,side,8,false);monsters.NilfTrigger(2,card.Snapshot());RecordVisual(14,s.instanceId,"Взята карта",400);}
    public function NilfDraw(side : int, tier : int, reveal : bool)
    {var ids : array<int>;var i : int;var s : SBetaGwentCardSnapshot;NorthPile(side,16,ids);for(i=0;i<ids.Size();i+=1){s=FindCard(ids[i]).Snapshot();if((s.runtimeTierMask&tier)==0)continue;NilfTake(FindCard(ids[i]),side);if(reveal)NilfReveal(FindCard(ids[i]),true);return;}}
    public function NilfBottom(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;if(!card)return;s=card.Snapshot();card.Move(s.positionPlayerId,128,0);Reindex(s.positionPlayerId,s.locationMask);card.Move(s.positionPlayerId,16,CountLocation(s.positionPlayerId,16));card.SetPlayable(false);card.ResetInHand();RecordVisual(14,s.instanceId,"Карта в низ колоды",350);}
    public function NilfDiscard(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;s=card.Snapshot();NorthMoveInactive(card,s.positionPlayerId,32,false);BetaGwentLog("DUEL_DISCARD card="+s.instanceId);}
    public function NilfBanish(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;s=card.Snapshot();card.Move(s.positionPlayerId,512,CountLocation(s.positionPlayerId,512));Reindex(s.positionPlayerId,s.locationMask);RecordVisual(4,s.instanceId,"Карта удалена",420,12);}
    public function NilfQueueReaction(card : CBetaGwentDuelCard, kind : int, side : int)
    {var job : CBetaGwentNilfReaction;if(nilfJobs.Size()>=128){FailAbility("Слишком много реакций Нильфгаарда.");return;}job=new CBetaGwentNilfReaction in this;job.source=card;job.kind=kind;job.side=side;nilfJobs.PushBack(job);}
    private function NilfNextReaction() : bool
    {
        var s : SBetaGwentCardSnapshot;var card : CBetaGwentDuelCard;var row : int;
        while(nilfJobs.Size()>0)
        {
            nilfJob=nilfJobs[0];nilfJobs.Erase(0);card=nilfJob.source;s=card.Snapshot();
            if(s.isWaitingToDie || (s.tokenMask&12)!=0 || (s.locationMask&63)==0 || ((nilfJob.kind==7 || nilfJob.kind==8) && s.locationMask!=32) || (nilfJob.kind==2 && s.locationMask!=8) || (nilfJob.kind==6 && s.locationMask!=16))continue;
            BetaGwentLog("DUEL_NILF_REACTION kind="+nilfJob.kind+" card="+s.instanceId+" side="+nilfJob.side);
            if(nilfJob.kind==8){card.playFromLocation=32;card.Move(s.positionPlayerId,256,0);Reindex(s.positionPlayerId,32);card.SetPlayable(false);StartPlayResolution(card,s.positionPlayerId);return true;}
            if(nilfJob.kind==2 || nilfJob.kind==6 || nilfJob.kind==7)
            {row=BestOwnRow(s.positionPlayerId);if(row==0)continue;card.playFromLocation=s.locationMask;InsertUnit(card,s.positionPlayerId,row,-3);Reindex(s.positionPlayerId,s.locationMask);card.SetPlayable(false);StartPlayResolution(card,s.positionPlayerId);return true;}
            playStack.PushBack(card);SetVisualSource(s.instanceId,s.runtimeTemplate.templateId,s.positionPlayerId,s.locationMask);monsters.NilfReaction(card,nilfJob.kind);return true;
        }
        nilfJob=NULL;return false;
    }

    public function MonsterComplete(card : CBetaGwentDuelCard) { CompletePlay(card); }
    public function MonsterPlaySide(card : CBetaGwentDuelCard, side : int) : int
    { var s : SBetaGwentCardSnapshot; s = card.Snapshot(); if (BetaGwentDuelSpying(card.TemplateId()) && (s.locationMask & 7) == 0) return BetaGwentOpponentId(side); return side; }
    private function NilfDynamicSpawnAllowed(source : CBetaGwentDuelCard, id : int) : bool
    {var ids : array<int>;var varIndex : int;if(source.MonsterMode()>=800){if(source.TemplateId()==112112 || source.TemplateId()==200079 || source.TemplateId()==201773)return source.monsterStored==id;}if(source.TemplateId()==201601)return NilfLastSpell(NorthActingSide(source))==id;if(source.TemplateId()==200022)return NilfLastUnit()==id;
        if(source.TemplateId()==142107)return source.monsterStage==2 && source.monsterStored==id;
        if(source.TemplateId()==200144)return id==152406;
        if(source.TemplateId()==200293){AgitatorPool(NorthActingSide(source),ids);if(ids.Contains(id))return true;}if(source.TemplateId()==200102){NilfInitialPool(BetaGwentOpponentId(NorthActingSide(source)),ids);return ids.Contains(id);}if(source.TemplateId()==201639){NilfInitialPool(BetaGwentOpponentId(NorthActingSide(source)),ids);return ids.Contains(id);}return false;}
    public function MonsterCreationAllowed(source : CBetaGwentDuelCard, templateId : int) : bool
    { if(!source)return false; return BetaGwentMonsterSpawnAllowed(source.TemplateId(),templateId) || NilfDynamicSpawnAllowed(source,templateId); }
    public function MonsterCreate(card : CBetaGwentDuelCard, templateId : int) { BeginCreatedPlay(card, templateId); }
    public function MonsterPower(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard, amount : int)
    { if (card && !effects.Enqueue(card, 1, amount, false, source)) FailAbility("Не удалось поставить способность Чудовищ в очередь."); }
    public function MonsterOperation(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard, operation : int, amount : int, locations : int)
    { if (card && !effects.Enqueue(card, operation, amount, false, source, locations)) FailAbility("Не удалось изменить изначальную силу."); }
    public function MonsterRequest(source : CBetaGwentDuelCard, ids : array<int>, kind : int, minimum : int, maximum : int)
    {
        var s, t : SBetaGwentCardSnapshot; var d, option : SBetaGwentDuelDefinition;
        var m : SBetaGwentMatchSnapshot; var i, best, value, score, rowSide : int; var card : CBetaGwentDuelCard;
        if (fatal || !source) return; s = source.Snapshot(); d = source.Definition(); m = match.Snapshot();
        pendingCard = source; pendingIds = ids; pendingChoice = kind == 1; pendingRow = kind == 3; pendingPileChoice = kind == 2;
        pendingRally = NULL; pendingHandPower = false; requestId += 1; monsterMinimum = minimum; monsterMaximum = maximum;
        // A play-from-pile choice must resolve when at least one legal card exists.
        // Empty pools still take the normal no-card branch below.
        if (kind == 2 && BetaGwentDuelPlayChoice(d.header.templateId) && ids.Size() > 0) monsterMinimum = Max(1, monsterMinimum);
        if (d.specialMode == 18) monsterMaximum = d.specialCount;
        // Beta deploy abilities are mandatory whenever a legal target exists.
        if (ids.Size() > 0 && kind != 3 && d.specialMode != 18) monsterMinimum = Max(1, monsterMinimum);
        message = d.title + ": выберите подсвеченную цель.";
        if (kind == 1) message = d.title + ": выберите создаваемую карту или вариант способности.";
        if (kind == 2) message = d.title + ": выберите карту из предложенного списка.";
        if (kind == 3) message = d.title + ": выберите ряд соперника.";
        if (kind == 0) message = d.title + ": выберите подсвеченный отряд для способности.\n" + d.description;
        if (d.header.templateId == 200124) message = d.title + ": укажите отряд противника, которому нужно нанести урон.\n" + d.description;
        if (kind == 2 && BetaGwentDuelPlayChoice(d.header.templateId) && ids.Size() > 0) message = d.title + ": обязательно выберите карту для розыгрыша. Отряд затем нужно разместить в ряду.";
        if (d.specialMode == 18) message += " Выбрано " + source.monsterIds.Size() + " / " + d.specialCount + ". Можно завершить выбор.";
        BetaGwentLog("DUEL_ABILITY_CHOICE source=" + d.header.templateId + " kind=" + kind + " candidates=" + ids.Size());
        if (ids.Size() == 0)
        {
            if (d.header.templateId == 201780 && NilfDecisionSide() == 1)
            {
                monsterMinimum = 0;
                message = d.title + ": в сбросе противника нет подходящего бронзового или серебряного солдата. Нажмите «Продолжить».";
                return;
            }
            monsters.Select(source, 0); return;
        }
        if (NilfDecisionSide() != 2) return;
        archetypeAI.Refresh();
        rowSide=BetaGwentOpponentId(NorthActingSide(source));
        if(kind==3 && SpecialRowMode()==8)rowSide=NorthActingSide(source);
        score = -2147483647; best = ids[0];
        for (i = 0; i < ids.Size(); i += 1)
        {
            value = 0;
            if (kind == 1) { option = BetaGwentDuelViewDefinition(ids[i]); value = option.header.power; if (option.header.typeMask == 2) value += 5; }
            else if (kind == 3) value = CountLocation(rowSide, ids[i]);
            else
            {
                card = registry.Find(ids[i]); if (!card) continue; t = card.Snapshot(); value = AiAbilityChoiceValue(source,card,kind);
                if (kind == 0 && t.positionPlayerId == s.positionPlayerId && (d.specialMode == 11 || d.specialMode == 22)) value = -value;
                if (t.runtimeTemplate.typeMask == 2) value += 5;
                if(t.locationMask==8 && t.positionPlayerId!=NilfDecisionSide() && (t.tokenMask&64)==0)value=0;
            }
            if(weatherProfile)value=weatherAI.ChoiceValue(source,ids[i],kind);
            if(kind==0 && card && (source.TemplateId()==200170 || source.TemplateId()==122307 || source.TemplateId()==200026))value=archetypeAI.CopyValue(source.TemplateId()==200170,card,true);
            if(kind==1)value+=archetypeAI.ChoiceBonus(option);
            else if(kind==2 && card && !(t.locationMask==8 && t.positionPlayerId!=2 && (t.tokenMask&64)==0)){
                if(archetypeAI.IsDiscard(source))value=archetypeAI.DiscardValue(card);
                else value+=archetypeAI.ChoiceBonus(card.Definition());
            }
            // Calveit chooses only among the three actual revealed deck cards.
            // When catching a pass, prefer current tempo over future engines.
            if(kind==2 && source.TemplateId()==200164 && card)value=AiCardTempo(card,m.playerOne.hasPassed,BestVranAnchor(2),AiPublicClearRisk());
            if (value > score) { score = value; best = ids[i]; }
        }
        // Generation 3: pick card targets by playing each option on a cloned session.
        if (kind == 0 && BetaGwentAIStrength() >= 3 && !aiSimulating && ids.Size() > 1 && ids.Size() <= 14)
        {
            value = AiSimChoice(source, ids);
            if (value != 0) best = value;
        }
        if (kind == 3) monsters.Row(source, rowSide, best); else monsters.Select(source, best);
    }
    private function AiSimChoice(source : CBetaGwentDuelCard, ids : array<int>) : int
    {
        var g : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot; var i, best, value, maximum, before : int;
        s = source.Snapshot(); maximum = -2147483647;
        BetaGwentAISimEnter();
        for (i = 0; i < ids.Size(); i += 1)
        {
            g = AiSimClone(); if (!g) continue;
            before = g.Score(2) - g.Score(1);
            g.monsters.Select(g.FindCard(s.instanceId), ids[i]); g.FlushDeaths();
            if (g.IsFatal()) continue;
            value = g.Score(2) - g.Score(1) - before;
            if (value > maximum) { maximum = value; best = ids[i]; }
        }
        BetaGwentAISimLeave();
        return best;
    }
    public function MonsterPlayExisting(source : CBetaGwentDuelCard, child : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var m : SBetaGwentMatchSnapshot; var row : int;
        if (!source) return;
        // A queued reaction may invalidate a chosen pile card before its play.
        // Resolve that graph without submitting an impossible child action.
        if (!ExistingChildAvailable(source,child))
        { BetaGwentLog("DUEL_NESTED_UNAVAILABLE source="+source.TemplateId());CompletePlay(source);return; }
        s = child.Snapshot(); d = child.Definition(); m = match.Snapshot();
        pendingCard = source; pendingChoice = false; pendingRow = false; pendingPileChoice = false; pendingIds.Clear();
        if (d.header.typeMask != 4) { PlayFromPile(source, child, 0, -3); return; }
        row = BestOwnRow(MonsterPlaySide(child, s.positionPlayerId)); if (row == 0) { CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        if (NilfDecisionSide() == 2) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
        message = d.title + ": выберите место разыгрываемого отряда.";
    }
    public function MonsterDraw(side : int, unitOnly : bool)
    {
        var cards : array<CBetaGwentDuelCard>; var i : int; var s : SBetaGwentCardSnapshot;
        if (!unitOnly) { Draw(side, 1); return; } LocationCards(side, 16, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); if (s.runtimeTemplate.typeMask != 4) continue;
            cards[i].Move(side, 8, CountLocation(side, 8)); cards[i].SetPlayable(true); Reindex(side, 16);
            RecordVisual(14, s.instanceId, "Взят отряд", 400); return;
        }
    }
    public function MonsterDeckCopies(side : int, templateId : int, count : int)
    {
        var i, id : int; var child : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition;
        d = BetaGwentDuelDefinition(templateId); if (d.header.typeMask != 4 || d.header.tierMask != 2 || count > 3) { FailAbility("Недопустимая копия Накера-воина."); return; }
        for (i = 0; i < count; i += 1)
        {
            if (!registry.Allocate(id)) { FailAbility("Не удалось создать копию в колоде."); return; }
            child = new CBetaGwentDuelCard in this; child.Setup(this, id, templateId, side, 16, CountLocation(side, 16)); child.createdCopy=true;
            registry.Put(id, child); live.PushBack(child);
        }
        RecordVisual(8, 0, "Копии добавлены в низ колоды: " + count, 380);
    }
    public function MonsterTopDeck(card : CBetaGwentDuelCard)
    {
        var cards : array<CBetaGwentDuelCard>; var s, t : SBetaGwentCardSnapshot; var i : int;
        if (!card) return; s = card.Snapshot(); if (s.locationMask != 16) return;
        LocationCards(s.positionPlayerId, 16, cards);
        card.Move(s.positionPlayerId, 16, 0);
        for (i = 0; i < cards.Size(); i += 1)
        { t = cards[i].Snapshot(); if (cards[i] != card) cards[i].Move(s.positionPlayerId, 16, i + 1); }
        Reindex(s.positionPlayerId, 16);
    }
    public function MonsterForceDeathwish(card : CBetaGwentDuelCard)
    { var cards : array<SBetaGwentCardSnapshot>; if (!card) return; cards.PushBack(card.Snapshot()); events.Killed(cards); }
    public function MonsterSummon(destination : SBetaGwentCardSnapshot, card : CBetaGwentDuelCard)
    { if (card && !effects.EnqueueDeckMove(destination, card)) FailAbility("Не удалось призвать отряд из колоды."); }
    public function MonsterResurrect(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard)
    {
        var s, t : SBetaGwentCardSnapshot; var index : int;
        if (!source || !card) return; s = source.Snapshot(); t = card.Snapshot();
        if (t.locationMask != 32 || CountLocation(s.positionPlayerId, s.locationMask) >= 9) return;
        QueueTransform(source, card, 200457); if (!FlushEffects()) return;
        s = source.Snapshot(); index = s.locationIndex + 1;
        if (!InsertUnit(card, s.positionPlayerId, s.locationMask, index)) { FailAbility("Не удалось воскресить Драугира."); return; }
        Reindex(t.positionPlayerId, 32); card.SetPlayable(false); RecordVisual(15, t.instanceId, "Драугир воскрес", 480);
    }
    public function MonsterDuel(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, heal : int, armor : int)
    { if (!effects.EnqueueMonsterDuel(source, target, false, heal, armor)) FailAbility("Не удалось начать дуэль отрядов."); }
    public function MonsterMoved(old : SBetaGwentCardSnapshot)
    { var moved : SBetaGwentCardSnapshot;if (events && monsters) { events.MonsterTrigger(4, old); events.NorthTrigger(4, old); monsters.NilfTrigger(3,old);
        if(FindCard(old.instanceId)){moved=FindCard(old.instanceId).Snapshot();if((moved.locationMask&7)==0 && moved.runtimeTemplate.templateId==162308)FindCard(moved.instanceId).SetNilfCounter(0);if((moved.locationMask&7)!=0 && moved.runtimeTemplate.typeMask==4 && (moved.runtimeTierMask&6)!=0 && !BetaGwentNilfAgent(moved.runtimeTemplate.templateId))nilfLastMovedUnit=moved.runtimeTemplate.templateId;} } }
    public function MonsterWeather(side : int, row : int, token : int) { weather.ApplyHazard(side, row, token); }
    public function MonsterWeatherChanged(side : int, row : int, oldToken : int, token : int)
    {
        var cause : SBetaGwentCardSnapshot;
        if (!events || !monsters || oldToken == token || token == 0) return;
        cause.positionPlayerId = side; cause.locationMask = row; cause.timerValue = token; events.MonsterTrigger(3, cause);
    }
    public function MonsterIsHazard(token : int) : bool { return token != 0 && (token & 384) == 0; }
    public function MonsterMoveWeather(side : int, fromRow : int, toRow : int)
    { var token : int; token = weather.Token(side, fromRow); weather.ClearRow(side, fromRow); if (MonsterIsHazard(token)) weather.ApplyHazard(side, toRow, token); }
    public function MonsterDamaged(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { var cause : SBetaGwentCardSnapshot; if (source) cause = source.Snapshot(); events.MonsterDamaged(target, cause); monsters.NilfTrigger(8,target.Snapshot()); }
    public function RandomIndex(count : int) : int { return random.NextBounded(count); }
    public function ShuffleIds(out ids : array<int>) { random.Shuffle(ids); }
    public function FailAbility(reason : string)
    {
        BetaGwentLog("DUEL_ABILITY_ERROR " + reason);
        // Keep the first failure visible; cleanup errors must not erase its cause.
        if(fatal)return;
        fatal = true; message = reason;
    }
    public function QueueTimer(card : CBetaGwentDuelCard, operation : int, value : int)
    { if (!effects.EnqueueTimer(card, operation, value)) FailAbility("Не удалось поставить изменение счётчика в очередь."); }
    public function RecordTimerVisual(card : CBetaGwentDuelCard, old : int, operation : int)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = card.Snapshot(); d = card.Definition();
        RecordVisual(8, s.instanceId, d.title + ": счётчик " + old + " → " + s.timerValue, 350, 32);
        BetaGwentLog("DUEL_TIMER_CHANGE card=" + s.instanceId + " old=" + old + " current=" + s.timerValue + " operation=" + operation);
    }
    public function TimerExpired(card : CBetaGwentDuelCard)
    { if (card && !fatal) events.TimerExpired(card.Snapshot()); }
    private function BeforeTurnWithEvents(side : int)
    {
        // Vran priority0 is before weather -5/-10/-15. More general merged trigger scheduling is pending.
        var cause : SBetaGwentCardSnapshot;cause.positionPlayerId=side;monsters.NilfTrigger(5,cause);NorthTurn(1, side); events.BeforeTurn(side); if (!events.Flush()) return; DrainDeaths();
        if (!fatal) { weather.CaptureDreamRows(); weather.BeforeTurn(side); }
    }
    private function ConsumeRight(card : CBetaGwentDuelCard)
    {
        var s, t : SBetaGwentCardSnapshot; var i, amount : int; var d : SBetaGwentDuelDefinition;
        s = card.Snapshot(); d = card.Definition();
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot();
            // Source GetCardsInShape(mask32768,pivot4,1) has no targeted Ignore/tier filter.
            if (t.positionPlayerId != s.positionPlayerId || t.locationMask != s.locationMask || t.locationIndex != s.locationIndex + 1) continue;
            amount = t.power.currentPower; QueueConsume(card, live[i]); QueuePower(card, amount, false);
            BetaGwentLog("DUEL_VRAN_CONSUME source=" + s.instanceId + " target=" + t.instanceId + " cachedPower=" + amount);
            return;
        }
        BetaGwentLog("DUEL_VRAN_EMPTY source=" + s.instanceId + " row=" + s.locationMask);
    }
    public function QueuePower(card : CBetaGwentDuelCard, amount : int, ignoreArmor : bool)
    { if (!effects.Enqueue(card, 1, amount, ignoreArmor, registry.Find(visualSourceId))) FailAbility("Не удалось поставить изменение силы в очередь."); }
    public function QueueLockToggle(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { if (!effects.Enqueue(target, 6, 4, false, source)) FailAbility("Не удалось поставить блокировку в очередь."); }
    public function QueueMultiplyPower(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, multiplier : int)
    { if (!effects.Enqueue(target, 7, multiplier, true, source)) FailAbility("Не удалось поставить умножение силы в очередь."); }
    public function RecordLockVisual(card : CBetaGwentDuelCard, oldTokens : int)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var caption : string;
        s = card.Snapshot(); d = card.Definition(); caption = "Блокировка снята: ";
        if ((s.tokenMask & 4) != 0) caption = "Блокировка: ";
        RecordVisual(9, s.instanceId, caption + d.title, 440);
        BetaGwentLog("DUEL_LOCK_TOGGLE target=" + s.instanceId + " old=" + oldTokens + " current=" + s.tokenMask);
    }
    public function QueueTransform(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, templateId : int)
    { if (!effects.Enqueue(target, 8, templateId, false, source)) FailAbility("Не удалось поставить превращение в очередь."); }
    public function RecordTransformVisual(card : CBetaGwentDuelCard, oldTemplate : int)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = card.Snapshot(); d = card.Definition(); weather.Contact(card);
        RecordVisual(10, s.instanceId, "Превращение: " + d.title, 550, 25);
        BetaGwentLog("DUEL_TRANSFORM target=" + s.instanceId + " old=" + oldTemplate + " current=" + d.header.templateId
            + " power=" + s.power.currentPower + " tokens=" + s.tokenMask + " reset=255 killed=false");
    }
    private function MatchesCardTarget(s : SBetaGwentCardSnapshot, d : SBetaGwentDuelDefinition) : bool
    { var targetDefinition : SBetaGwentDuelDefinition; targetDefinition = BetaGwentDuelDefinition(s.runtimeTemplate.templateId); return (targetDefinition.unitTraits & d.targetExcludedTraits) == 0 && (d.effect != 28 || d.pileTraitMask == 0 || (targetDefinition.unitTraits & d.pileTraitMask) != 0) && (s.locationMask & 7) != 0 && (s.runtimeTemplate.typeMask & d.targetTypes) != 0
        && (s.runtimeTierMask & d.targetTiers) != 0 && !s.isWaitingToDie && (s.tokenMask & d.targetIgnore) == 0
        && (s.runtimeTemplate.factionMask & d.targetExcludedFaction) == 0; }
    public function QueueSetPower(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, value : int)
    { if (!effects.Enqueue(target, 11, value, true, source)) FailAbility("Не удалось поставить установку силы в очередь."); }
    public function QueueResetPower(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { if (!effects.Enqueue(target, 9, 0, true, source)) FailAbility("Не удалось поставить сброс силы в очередь."); }
    public function QueueResilienceToggle(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { if (!effects.Enqueue(target, 10, 1, false, source)) FailAbility("Не удалось поставить Стойкость в очередь."); }
    public function RecordResilienceVisual(card : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var caption : string;
        s = card.Snapshot(); d = card.Definition(); caption = "Стойкость снята: ";
        if ((s.tokenMask & 1) != 0) caption = "Стойкость: ";
        RecordVisual(8, s.instanceId, caption + d.title, 500, 26);
        BetaGwentLog("DUEL_RESILIENCE target=" + s.instanceId + " tokens=" + s.tokenMask);
    }
    public function QueueArmor(card : CBetaGwentDuelCard, amount : int)
    { if (!effects.Enqueue(card, 2, amount, false)) FailAbility("Не удалось поставить броню в очередь."); }
    public function QueueDestroy(card : CBetaGwentDuelCard)
    { if (!effects.Enqueue(card, 3, 0, false)) FailAbility("Не удалось поставить уничтожение в очередь."); }
    public function QueueConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var operation : int;
        s = target.Snapshot(); operation = 4; if (s.locationMask == 32 || s.locationMask == 8) operation = 5;
        if (!effects.Enqueue(target, operation, 0, false, source)) FailAbility("Не удалось поставить поглощение в очередь.");
    }
    public function BeforeConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    { if (source && target && !fatal) events.BeforeConsume(source.Snapshot(), target.Snapshot()); }
    public function RecordConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var a, t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; a = source.Snapshot(); t = target.Snapshot(); d = target.Definition();
        pendingConsumeVisuals.PushBack(t.instanceId);
        RecordVisual(11, t.instanceId, "Поглощение: " + d.title, 460);
        BetaGwentLog("DUEL_CONSUME source=" + a.instanceId + " target=" + t.instanceId + " removalType=1");
    }
    public function BanishConsumed(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var s, t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (fatal || !source || !target) return false; s = source.Snapshot(); t = target.Snapshot(); d = target.Definition();
        if ((s.locationMask & 7) == 0 || s.isWaitingToDie || (t.locationMask != 32 && t.locationMask != 8) || t.isWaitingToDie) return false;
        // CardBanishAttack calls Banish, not Kill: no second Killed/deathwish batch.
        target.Move(t.positionPlayerId, 512, 0); target.SetPlayable(false); Reindex(t.positionPlayerId, t.locationMask);
        RecordVisual(11, t.instanceId, "Поглощение: " + d.title, 460);
        BetaGwentLog("DUEL_BANISH_CONSUME source=" + s.instanceId + " target=" + t.instanceId
            + " template=" + d.header.templateId + " from=" + t.locationMask + " to=512 removalType=1 deathwish=false");
        return true;
    }
    public function AfterConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, optional banished : bool) : bool
    {
        if (fatal || !source || !target) return false;
        events.AfterConsume(source.Snapshot(), target.Snapshot(), banished); events.MonsterTrigger(6, source.Snapshot()); return events.Flush();
    }
    public function BanishOrdinary(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i : int;
        if (fatal || !source || !target) return false; t = target.Snapshot(); d = target.Definition();
        if ((t.locationMask & 7) == 0) return true;
        // Banish resolves before KillWaitingToDie: this target never emits Killed.
        for (i = dying.Size() - 1; i >= 0; i -= 1) if (dying[i] == target) dying.Erase(i);
        target.Move(t.positionPlayerId, 512, 0); target.SetWaiting(false); target.SetPlayable(false); Reindex(t.positionPlayerId, t.locationMask);
        RecordVisual(12, t.instanceId, "Удалён: " + d.title, 460);
        BetaGwentLog("DUEL_BANISH card=" + t.instanceId + " from=" + t.locationMask + " removalType=0 killed=false"); return true;
    }
    private function QueuePassivePower(card : CBetaGwentDuelCard, amount : int)
    { if (!effects.Enqueue(card, 1, amount, false, NULL, 31)) FailAbility("Не удалось поставить пассивное усиление в очередь."); }
    private function QueueDeckSummon(fromPosition : SBetaGwentCardSnapshot, templateId : int)
    {
        var candidates, cards : array<CBetaGwentDuelCard>; var s : SBetaGwentCardSnapshot; var i : int;
        LocationCards(fromPosition.positionPlayerId, 16, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot();
            if (s.runtimeTemplate.templateId == templateId && s.runtimeTemplate.typeMask == 4 && (s.runtimeTierMask & 14) != 0)
                candidates.PushBack(cards[i]);
        }
        if (candidates.Size() == 0)
        { BetaGwentLog("DUEL_SUMMON_EMPTY source=" + fromPosition.instanceId + " template=" + templateId); return; }
        // CardListGetRandomElement runs before MoveCards capacity filtering, even with one candidate.
        i = random.NextBounded(candidates.Size());
        if (CountLocation(fromPosition.positionPlayerId, fromPosition.locationMask) >= 9)
        { BetaGwentLog("DUEL_SUMMON_SKIPPED source=" + fromPosition.instanceId + " reason=full"); return; }
        if (!effects.EnqueueDeckMove(fromPosition, candidates[i])) FailAbility("Не удалось поставить призыв из колоды в очередь.");
    }
    private function CollectDeploySummon(side : int, templateId : int, otherTemplate : int, ignore : int, linked : int,
        excludedId : int, out cards : array<CBetaGwentDuelCard>)
    {
        var ordered : array<CBetaGwentDuelCard>; var t : SBetaGwentCardSnapshot; var i : int;
        cards.Clear(); LocationCards(side, 16, ordered);
        for (i = 0; i < ordered.Size(); i += 1)
        {
            t = ordered[i].Snapshot();
            if (t.instanceId == excludedId || (t.runtimeTemplate.templateId != templateId && (otherTemplate == 0 || t.runtimeTemplate.templateId != otherTemplate))
                || t.runtimeTemplate.typeMask != 4 || (t.runtimeTierMask & 14) == 0 || (t.tokenMask & ignore) != 0 || t.isWaitingToDie) continue;
            // SummonCardsNode inserts linked templates at the FRONT before capacity selection.
            if (linked != 0) cards.Insert(0, ordered[i]); else cards.PushBack(ordered[i]);
        }
    }
    public function QueueDeployCopies(source : CBetaGwentDuelCard, templateId : int)
    {
        var cards : array<CBetaGwentDuelCard>; var s, t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i, available, queued : int;
        s = source.Snapshot(); d = source.Definition(); available = 9 - CountLocation(s.positionPlayerId, s.locationMask);
        CollectDeploySummon(s.positionPlayerId, templateId, d.deploySummonOtherTemplate, d.deploySummonIgnore, d.deploySummonLinked, s.instanceId, cards);
        s.locationIndex = -4;
        for (i = 0; i < cards.Size() && queued < available; i += 1)
        {
            t = cards[i].Snapshot();
            // The candidate list already includes the canonical definition/ignore/order filters.
            if (!effects.EnqueueDeckMove(s, cards[i])) { FailAbility("Не удалось поставить копии в очередь призыва."); return; }
            queued += 1;
        }
        BetaGwentLog("DUEL_DEPLOY_SUMMON source=" + s.instanceId + " template=" + templateId + " count=" + queued + " random=false");
    }
    public function ApplyDeckSummon(destination : SBetaGwentCardSnapshot, card : CBetaGwentDuelCard) : bool
    {
        var s, summoner : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var source : CBetaGwentDuelCard; var index, count : int;
        if (fatal || !card || (destination.locationMask != 1 && destination.locationMask != 2 && destination.locationMask != 4)) return false;
        s = card.Snapshot(); d = card.Definition();
        if (s.locationMask != 16 || s.positionPlayerId != destination.positionPlayerId || s.isWaitingToDie) return false;
        count = CountLocation(destination.positionPlayerId, destination.locationMask);
        if (count >= 9)
        { BetaGwentLog("DUEL_SUMMON_SKIPPED source=" + destination.instanceId + " reason=full"); return true; }
        index = Min(count, Max(0, destination.locationIndex));
        if (destination.locationIndex == -4)
        {
            // Original CalculateSummonPosition: live SummonedBy index+1; fallback LastIndex(-3).
            index = count; source = registry.Find(destination.instanceId);
            if (source)
            {
                summoner = source.Snapshot();
                if (summoner.positionPlayerId == destination.positionPlayerId && summoner.locationMask == destination.locationMask)
                    index = Min(count, summoner.locationIndex + 1);
            }
        }
        if (!InsertUnit(card, destination.positionPlayerId, destination.locationMask, index)) return false;
        card.SetPlayable(false); Reindex(s.positionPlayerId, 16);
        RecordVisual(15, s.instanceId, "Из колоды призван " + d.title, 520);
        BetaGwentLog("DUEL_DECK_SUMMON source=" + destination.instanceId + " card=" + s.instanceId + " template=" + d.header.templateId
            + " row=" + destination.locationMask + " index=" + index + " power=" + s.power.currentPower + " deploy=false");
        return true;
    }
    public function QueueRandomRowSpawn(fromPosition : SBetaGwentCardSnapshot, templateId : int, count : int)
    {
        var rows : array<int>; var row : int;
        // GetAvailableLocations walks active flags1,2,4; singleton still consumes RNG.
        for (row = 1; row <= 4; row *= 2)
            if (CountLocation(fromPosition.positionPlayerId, row) < 9) rows.PushBack(row);
        if (rows.Size() == 0) { BetaGwentLog("DUEL_SPAWN_EMPTY reason=no_available_row"); return; }
        fromPosition.locationMask = rows[random.NextBounded(rows.Size())]; fromPosition.locationIndex = -3;
        QueueSpawn(fromPosition, templateId, count);
    }
    public function QueueSpawn(fromPosition : SBetaGwentCardSnapshot, templateId : int, count : int)
    {
        var requests : array<int>; var d : SBetaGwentDuelDefinition; var id, i : int;
        d = BetaGwentDuelDefinition(templateId);
        if (d.header.templateId == 0 || d.header.typeMask != 4 || ((d.tokens & 512) == 0 && templateId != 201624 && templateId != 201610 && templateId != 201636 && templateId != 152406) || count < 1 || count > 16)
        { FailAbility("Неизвестный призываемый токен."); return; }
        // Original node allocates every request before SpawnCardsAction checks capacity.
        for (i = 0; i < count; i += 1)
        {
            if (!registry.Allocate(id) || id == 0 || registry.Find(id))
            { FailAbility("Не удалось выделить ID токена."); return; }
            requests.PushBack(id);
        }
        if (!effects.EnqueueSpawn(fromPosition, templateId, requests)) FailAbility("Не удалось поставить призыв в очередь.");
    }
    public function ApplySpawnRequest(fromPosition : SBetaGwentCardSnapshot, templateId : int, id : int) : bool
    {
        var card : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition; var index, count, i : int; var other : SBetaGwentCardSnapshot;
        if (fatal || id == 0 || registry.Find(id)) return false;
        d = BetaGwentDuelDefinition(templateId);
        if (d.header.templateId == 0 || ((d.tokens & 512) == 0 && templateId != 201624 && templateId != 201610 && templateId != 201636 && templateId != 152406) || (fromPosition.locationMask != 1 && fromPosition.locationMask != 2 && fromPosition.locationMask != 4)
            || (fromPosition.positionPlayerId != 1 && fromPosition.positionPlayerId != 2)) return false;
        count = CountLocation(fromPosition.positionPlayerId, fromPosition.locationMask);
        if (count >= 9)
        { BetaGwentLog("DUEL_SPAWN_SKIPPED id=" + id + " row=" + fromPosition.locationMask + " reason=full"); return true; }
        index = count;
        if (fromPosition.locationIndex >= 0) index = Min(count, fromPosition.locationIndex);
        for (i = 0; i < live.Size(); i += 1)
        {
            other = live[i].Snapshot();
            if (other.positionPlayerId == fromPosition.positionPlayerId && other.locationMask == fromPosition.locationMask && other.locationIndex >= index)
                live[i].Move(other.positionPlayerId, other.locationMask, other.locationIndex + 1);
        }
        card = new CBetaGwentDuelCard in this;
        card.Setup(this, id, templateId, fromPosition.positionPlayerId, fromPosition.locationMask, index); card.createdCopy=true;
        if (templateId == 201624 || templateId == 201610 || templateId == 201636) card.AddTokens(512);
        if (!registry.Put(id, card)) { FailAbility("Не удалось зарегистрировать токен."); return false; }
        live.PushBack(card);
        weather.Contact(card);
        if(BetaGwentDuelSpying(templateId))card.AddTokens(128);
        MonsterMoved(card.Snapshot()); events.MonsterSpawn(card.Snapshot());monsters.NilfTrigger(12,card.Snapshot());
        RecordVisual(16, id, "Создан " + d.title + ": сила " + d.header.power, 500);
        BetaGwentLog("DUEL_SPAWN source=" + fromPosition.instanceId + " card=" + id + " template=" + templateId
            + " player=" + fromPosition.positionPlayerId + " row=" + fromPosition.locationMask + " index=" + index);
        return true;
    }
    public function FlushEffects() : bool { if (fatal) return false; return effects.Flush(); }
    public function QueueRowAbility(kind : int, token : int, side : int, row : int, templateId : int, targets : array<int>)
    { events.RowAbility(kind, token, side, row, templateId, targets); }
    public function TokensRemoved(card : CBetaGwentDuelCard, removed : int)
    { if ((removed & 8) != 0) weather.Contact(card); }
    public function FlushDeaths() { if (FlushEffects()) DrainDeaths(); }
    public function GetZoneCards(side : int, row : int, out cards : array<CBetaGwentDuelCard>) { LocationCards(side, row, cards); }
    public function WeatherToken(side : int, row : int) : int { return weather.Token(side, row); }
    public function WeatherDamage(side : int, row : int) : int { return weather.Damage(side, row); }
    // Expected cost of putting a unit with this definition into the row (AI generation 2).
    // Positive = bad. Hazards tick once per own turn for the rest of the round; boons pay.
    public function AiRowPlacementCost(side : int, row : int, d : SBetaGwentDuelDefinition) : int
    {
        var m : SBetaGwentMatchSnapshot; var turns, hazard, boon, token, count, enemy : int;
        if (BetaGwentAIStrength() < 2) return weather.Damage(side, row) * 3 + CountLocation(side, row) * 2;
        m = match.Snapshot(); enemy = BetaGwentOpponentId(side); count = CountLocation(side, row);
        turns = CountLocation(side, 8);
        if (!((enemy == 1 && m.playerOne.hasPassed) || (enemy == 2 && m.playerTwo.hasPassed))) turns = Min(turns, CountLocation(enemy, 8) + 1);
        turns = Max(1, Min(5, turns));
        token = weather.Token(side, row); hazard = weather.Hazard(side, row); boon = weather.Boon(side, row);
        if (token == 512 || token == 2048 || token == 1024) return hazard * 3 + count;
        if (token == 256 && (d.unitTraits & 288) == 0) boon = 0;
        if (hazard > 0) return hazard * turns + 4 + count;
        if (boon > 0) return count - boon * turns * Min(2, count + 1) / (count + 1);
        return count;
    }
    public function GetCards(out output : array<SBetaGwentDevelopmentCard>)
    {
        var i : int;
        var view : SBetaGwentDevelopmentCard;
        var cardDefinition : SBetaGwentDuelDefinition;
        output.Clear();
        for (i = 0; i < live.Size(); i += 1)
        { view.card = live[i].Snapshot(); cardDefinition = live[i].Definition(); view.title = cardDefinition.title; view.createdCopy=live[i].createdCopy; output.PushBack(view); }
    }
    // Presentation-only policy: both graveyards and the player's remaining deck.
    // Never export enemy deck/hand through this API, including forged UI events.
    public function GetInspectablePile(side : int, zone : int, out output : array<SBetaGwentDevelopmentCard>) : bool
    {
        var i : int; var view : SBetaGwentDevelopmentCard; var d : SBetaGwentDuelDefinition;
        output.Clear();
        if (!((zone == 32 && (side == 1 || side == 2)) || (zone == 16 && side == 1))) return false;
        for (i = 0; i < live.Size(); i += 1)
        {
            view.card = live[i].Snapshot();
            if (view.card.positionPlayerId != side || view.card.locationMask != zone) continue;
            d = live[i].Definition(); view.title = d.title; output.PushBack(view);
        }
        return true;
    }
    public function CountLocation(side : int, zone : int) : int
    {
        var i, total : int; var cardState : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1) { cardState = live[i].Snapshot(); if (cardState.positionPlayerId == side && cardState.locationMask == zone) total += 1; }
        return total;
    }
    public function Score(side : int) : int
    {
        var i, total : int; var cardState : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        { cardState = live[i].Snapshot(); if (cardState.positionPlayerId == side && (cardState.locationMask & 7) != 0 && (cardState.tokenMask&8)==0) total += cardState.power.currentPower; }
        return total;
    }
    private function Leader(side : int) : CBetaGwentDuelCard
    {
        var i : int; var s : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (s.positionPlayerId == side && s.locationMask == 64 && s.canBePlayed) return live[i]; }
        return NULL;
    }
    public function LeaderAvailable(side : int) : bool { return (bool)Leader(side); }
    private function CanAct(side : int) : bool
    {
        var s : SBetaGwentMatchSnapshot; s = match.Snapshot();
        if (fatal || waiting || IsPending() || s.matchWinnerMask != 0 || !s.turnActive || s.currentPlayerId != side) return false;
        if (side == 1) return !s.playerOne.hasPassed;
        if (side == 2) return !s.playerTwo.hasPassed;
        return false;
    }
    private function Reindex(side : int, zone : int)
    {
        var ordered : array<CBetaGwentDuelCard>;
        var i, j : int; var s, other : SBetaGwentCardSnapshot; var card : CBetaGwentDuelCard;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId != side || s.locationMask != zone) continue;
            j = 0;
            while (j < ordered.Size()) { other = ordered[j].Snapshot(); if (other.locationIndex > s.locationIndex) break; j += 1; }
            ordered.Insert(j, live[i]);
        }
        for (i = 0; i < ordered.Size(); i += 1) ordered[i].Move(side, zone, i);
    }
    private function LocationCards(side : int, zone : int, out ordered : array<CBetaGwentDuelCard>)
    {
        var i, j : int; var s, other : SBetaGwentCardSnapshot;
        ordered.Clear();
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId != side || s.locationMask != zone) continue;
            j = 0;
            while (j < ordered.Size()) { other = ordered[j].Snapshot(); if (other.locationIndex > s.locationIndex) break; j += 1; }
            ordered.Insert(j, live[i]);
        }
    }
    private function Draw(side : int, amount : int)
    {
        var ordered : array<CBetaGwentDuelCard>; var i : int; var drawn : SBetaGwentCardSnapshot;
        LocationCards(side, 16, ordered);
        for (i = 0; i < ordered.Size() && i < amount; i += 1)
        {
            ordered[i].Move(side, 8, CountLocation(side, 8)); ordered[i].SetPlayable(true); monsters.NilfTrigger(2,ordered[i].Snapshot());
            if (side == 1) { drawn = ordered[i].Snapshot(); RecordVisual(14, drawn.instanceId, "Вы добрали карту", 400); }
            else RecordVisual(14, 0, "Соперник добрал карту", 300);
        }
        Reindex(side, 16); BetaGwentLog("DUEL_DRAW player=" + side + " cards=" + i);
    }
    private function AiMulligan(budget : int)
    {
        var hand, deck : array<CBetaGwentDuelCard>; var blacklist, reserved : array<int>;
        var outgoing, incoming : CBetaGwentDuelCard; var s, t : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i, j, pass, used, index, outgoingId, priority, maximum : int;
        while (used < budget && !fatal)
        {
            outgoing = NULL; incoming = NULL; LocationCards(2, 8, hand);
            archetypeAI.Refresh();maximum=0;
            for(i=0;i<hand.Size();i+=1){s=hand[i].Snapshot();if(reserved.Contains(s.instanceId))continue;
                priority=archetypeAI.Mulligan(hand[i]);if(priority>maximum){maximum=priority;outgoing=hand[i];}}
            if(weatherProfile && !outgoing)for(i=0;i<hand.Size();i+=1){t=hand[i].Snapshot();if(hand[i].TemplateId()==113302 && !reserved.Contains(t.instanceId)){outgoing=hand[i];break;}}
            for (i = 0; i < hand.Size() && !outgoing; i += 1)
            {
                s=hand[i].Snapshot();if(reserved.Contains(s.instanceId))continue;
                d = hand[i].Definition(); if (d.deploySummonTemplate == 0) continue;
                for (j = 0; j < i; j += 1)
                {
                    t = hand[j].Snapshot();
                    if (t.runtimeTemplate.templateId == d.header.templateId || t.runtimeTemplate.templateId == d.deploySummonTemplate
                        || (d.deploySummonOtherTemplate != 0 && t.runtimeTemplate.templateId == d.deploySummonOtherTemplate)) { outgoing = hand[i]; break; }
                }
            }
            if (!outgoing && BetaGwentAIStrength() >= 3) outgoing = AiMulliganWorst(hand, reserved, blacklist);
            if (!outgoing) break; s = outgoing.Snapshot(); outgoingId = s.instanceId;
            if (!blacklist.Contains(s.runtimeTemplate.templateId)) blacklist.PushBack(s.runtimeTemplate.templateId);
            LocationCards(2, 16, deck);
            for (pass = 0; pass < 2 && !incoming; pass += 1)
                for (i = 0; i < deck.Size(); i += 1)
                {
                    t = deck[i].Snapshot(); if (reserved.Contains(t.instanceId)) continue;
                    if (pass == 0 && blacklist.Contains(t.runtimeTemplate.templateId)) continue;
                    incoming = deck[i]; break;
                }
            if (!incoming) break; t = incoming.Snapshot(); reserved.PushBack(t.instanceId);
            index = random.NextBounded(deck.Size());
            incoming.Move(2, 8, s.locationIndex); incoming.SetPlayable(true);MonsterMoved(t);
            outgoing.Move(2, 256, 0); Reindex(2, 16); LocationCards(2, 16, deck);
            for (i = 0; i < deck.Size(); i += 1)
            { t = deck[i].Snapshot(); if (t.locationIndex >= index) deck[i].Move(2, 16, t.locationIndex + 1); }
            outgoing.Move(2, 16, index); Reindex(2, 16);MonsterMoved(s);NilfSwapped(outgoing); used += 1;
            // Diagnostic stays server-side: no hidden replacement identity in the UI.
            BetaGwentLog("DUEL_AI_MULLIGAN outgoing=" + outgoingId + " used=" + used + " weather="+weatherProfile+" profile="+archetypeAI.ProfileId()+" priority="+maximum+" policy=rules88");
        }
    }
    // Generation 3 mulligan: replace the weakest card when the deck's expected card is
    // clearly better (worth = measured average swing of the card in self-play).
    private function AiCardKeepValue(card : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition; var value : int;
        d = card.Definition(); value = BetaGwentAICardWorth(d.header.templateId, d.header.power);
        if (BetaGwentDuelSpying(d.header.templateId)) value = Max(value, 11);
        if (d.header.typeMask != 4) value = Max(value, 10);
        value += Max(0, archetypeAI.Priority(d)) / 2;
        return value;
    }
    private function AiMulliganWorst(hand : array<CBetaGwentDuelCard>, reserved : array<int>, blacklist : array<int>) : CBetaGwentDuelCard
    {
        var deck : array<CBetaGwentDuelCard>; var worst : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i, total, count, value, lowest : int;
        LocationCards(2, 16, deck);
        for (i = 0; i < deck.Size(); i += 1)
        {
            d = deck[i].Definition(); if (blacklist.Contains(d.header.templateId)) continue;
            total += BetaGwentAICardWorth(d.header.templateId, d.header.power); count += 1;
        }
        if (count == 0) return NULL;
        lowest = 2147483647;
        for (i = 0; i < hand.Size(); i += 1)
        {
            s = hand[i].Snapshot(); if (reserved.Contains(s.instanceId)) continue;
            d = hand[i].Definition(); if (d.header.tierMask == 8) continue;
            value = AiCardKeepValue(hand[i]);
            if (value < lowest) { lowest = value; worst = hand[i]; }
        }
        if (!worst || lowest * count + BetaGwentAITune(6) * count >= total) return NULL;
        return worst;
    }
    private function BeginMulligan(starter : int, budget : int)
    {
        aiRoundHandOne = CountLocation(1, 8); aiRoundHandTwo = CountLocation(2, 8);
        AiMulligan(budget);
        roundStarter = starter; mulliganBudget = budget; mulliganUsed = 0;
        blacklistedTemplates.Clear(); reservedCards.Clear(); pendingIds.Clear();
        mulligan = true; requestId += 1; RefreshMulligan();
        BetaGwentLog("DUEL_MULLIGAN_BEGIN request=" + requestId + " choices=" + budget + " ai=summon_group");
        if (pendingIds.Size() == 0 || CountLocation(1, 16) == 0) FinishMulligan(requestId);
    }
    private function RefreshMulligan()
    {
        var ordered : array<CBetaGwentDuelCard>; var i : int; var s : SBetaGwentCardSnapshot;
        pendingIds.Clear(); LocationCards(1, 8, ordered);
        for (i = 0; i < ordered.Size(); i += 1) { s = ordered[i].Snapshot(); pendingIds.PushBack(s.instanceId); }
        message = "Замена карт: осталось " + (mulliganBudget - mulliganUsed)
            + ". Нажмите карту для замены или начните раунд с этой рукой.";
    }
    public function SelectMulligan(id : int, item : int) : bool
    {
        var outgoing, incoming : CBetaGwentDuelCard;
        var ordered : array<CBetaGwentDuelCard>;
        var s, t : SBetaGwentCardSnapshot; var i, pass, deckIndex, incomingId : int;
        if (fatal || !mulligan || id != requestId || mulliganUsed >= mulliganBudget
            || !BetaGwentRequestContains(pendingIds, item)) return false;
        outgoing = registry.Find(item); if (!outgoing) return false; s = outgoing.Snapshot();
        if (s.positionPlayerId != 1 || s.locationMask != 8) return false;
        if (!BetaGwentRequestContains(blacklistedTemplates, s.runtimeTemplate.templateId))
            blacklistedTemplates.PushBack(s.runtimeTemplate.templateId);
        LocationCards(1, 16, ordered);
        // Original GetNextValidCard: blacklist pass, then reserved-only fallback.
        for (pass = 0; pass < 2 && !incoming; pass += 1)
        {
            for (i = 0; i < ordered.Size(); i += 1)
            {
                t = ordered[i].Snapshot();
                if (BetaGwentRequestContains(reservedCards, t.instanceId)) continue;
                if (pass == 0 && BetaGwentRequestContains(blacklistedTemplates, t.runtimeTemplate.templateId)) continue;
                incoming = ordered[i]; break;
            }
        }
        if (!incoming) return FinishMulligan(id);
        t = incoming.Snapshot(); incomingId = t.instanceId; reservedCards.PushBack(incomingId);
        // RNG bound uses deck count BEFORE removing incoming (original Mulligan).
        deckIndex = random.NextBounded(ordered.Size());
        incoming.Move(1, 8, s.locationIndex); incoming.SetPlayable(true);MonsterMoved(t);
        outgoing.Move(1, 256, 0); Reindex(1, 16);
        LocationCards(1, 16, ordered);
        for (i = 0; i < ordered.Size(); i += 1)
        { t = ordered[i].Snapshot(); if (t.locationIndex >= deckIndex) ordered[i].Move(1, 16, t.locationIndex + 1); }
        outgoing.Move(1, 16, deckIndex); Reindex(1, 16);MonsterMoved(s);NilfSwapped(outgoing); mulliganUsed += 1;
        BetaGwentLog("DUEL_MULLIGAN_SWAP request=" + requestId + " outgoing=" + item
            + " incoming=" + incomingId + " index=" + deckIndex + " used=" + mulliganUsed + " draws=" + random.DrawCount());
        RefreshMulligan();
        if (mulliganUsed >= mulliganBudget) FinishMulligan(id);
        return !fatal;
    }
    public function FinishMulligan(id : int) : bool
    {
        if (fatal || !mulligan || id != requestId) return false;
        mulligan = false; pendingIds.Clear();
        Require(match.ApplyTurnStarted(roundStarter));
        SetVisualSource(0, 0, roundStarter, 0);
        RecordVisual(7, 0, "Начало раунда", 650);
        BeforeTurnWithEvents(roundStarter);
        if(nilfJobs.Size()>0){mulliganReactions=true;if(!NilfNextReaction())mulliganReactions=false;}
        message = "Замена завершена. Выберите карту в руке и ряд на поле.";
        BetaGwentLog("DUEL_MULLIGAN_END request=" + id + " used=" + mulliganUsed + " starter=" + roundStarter);
        return !fatal;
    }
    public function Play(side : int, instanceId : int, row : int) : bool
    { return PlayAtIndex(side, instanceId, row, -3); }
    // UI hint only; the authoritative methods below validate before ClaimInitialMove.
    public function DirectSpecialKind(d : SBetaGwentDuelDefinition) : int
    {
        if (d.header.typeMask != 2) return 0;
        if (d.effect == 28) return d.specialRequest;
        if (d.weatherToken != 0 || d.effect == 4) return 2;
        if (d.effect == 1 || d.effect == 2 || d.effect == 3 || d.effect == 6
            || d.effect == 18 || d.effect == 19 || d.effect == 20 || d.effect == 22) return 1;
        return 0;
    }
    public function PlayOnTarget(side : int, instanceId : int, targetId : int) : bool
    {
        var card, target : CBetaGwentDuelCard; var s, t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!CanAct(side) || side != 1) return false;
        card = registry.Find(instanceId); target = registry.Find(targetId); if (!card || !target) return false;
        s = card.Snapshot(); t = target.Snapshot(); d = card.Definition();
        if (s.positionPlayerId != side || s.locationMask != 8 || !s.canBePlayed || DirectSpecialKind(d) != 1
            || !MatchesCardTarget(t, d) || (d.targetSide == 1 && t.positionPlayerId != side)
            || (d.targetSide == 2 && t.positionPlayerId != BetaGwentOpponentId(side))
            || (d.consumeMaximum > 0 && t.power.currentPower > d.consumeMaximum)) return false;
        // One native event: create the normal request and resolve that exact request.
        // No client-supplied request ID and no intermediate UI publication.
        if (!Play(side, instanceId, t.locationMask) || pendingCard != card) return false;
        BetaGwentLog("DUEL_DIRECT_TARGET source=" + instanceId + " target=" + targetId + " request=" + requestId);
        return SelectTarget(requestId, targetId);
    }
    public function PlayOnRow(side : int, instanceId : int, targetSide : int, row : int) : bool
    {
        var card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!CanAct(side) || side != 1 || (targetSide != 1 && targetSide != 2) || (row != 1 && row != 2 && row != 4)) return false;
        card = registry.Find(instanceId); if (!card) return false; s = card.Snapshot(); d = card.Definition();
        if (s.positionPlayerId != side || s.locationMask != 8 || !s.canBePlayed || DirectSpecialKind(d) != 2
            || (d.weatherToken != 0 && targetSide != BetaGwentOpponentId(side))
            || (d.effect == 28 && !specials.ValidRow(d, side, targetSide, row))) return false;
        if (!Play(side, instanceId, row) || pendingCard != card) return false;
        BetaGwentLog("DUEL_DIRECT_ROW source=" + instanceId + " side=" + targetSide + " row=" + row + " request=" + requestId);
        return SelectRow(requestId, targetSide, row);
    }
    private function CanInsertUnit(side : int, row : int, requestedIndex : int) : bool
    {
        var count, index : int;
        if ((side != 1 && side != 2) || (row != 1 && row != 2 && row != 4)) return false;
        count = CountLocation(side, row); index = requestedIndex;
        if (index == -3) index = count;
        return count < 9 && index >= 0 && index <= count;
    }
    private function ReadPlacementAnchor(side : int, anchorId : int, out a : SBetaGwentCardSnapshot) : bool
    {
        var anchor : CBetaGwentDuelCard;
        anchor = registry.Find(anchorId); if (!anchor) return false; a = anchor.Snapshot();
        return a.positionPlayerId == side && (a.locationMask & 7) != 0 && a.runtimeTemplate.typeMask == 4
            && !a.isWaitingToDie && a.power.currentPower > 0 && a.locationIndex >= 0
            && CanInsertUnit(side, a.locationMask, a.locationIndex);
    }
    private function InsertUnit(card : CBetaGwentDuelCard, side : int, row : int, requestedIndex : int) : bool
    {
        var s, other : SBetaGwentCardSnapshot; var i, index : int;
        if (!card) return false;
        s = card.Snapshot();
        if (s.positionPlayerId != side || s.runtimeTemplate.typeMask != 4 || (s.locationMask & 7) != 0) return false;
        if (BetaGwentDuelSpying(card.TemplateId())) { side = BetaGwentOpponentId(side); card.AddTokens(128); }
        if (!CanInsertUnit(side, row, requestedIndex)) return false;
        index = requestedIndex; if (index == -3) index = CountLocation(side, row);
        for (i = 0; i < live.Size(); i += 1)
        {
            other = live[i].Snapshot();
            if (other.positionPlayerId == side && other.locationMask == row && other.locationIndex >= index)
                live[i].Move(side, row, other.locationIndex + 1);
        }
        card.Move(side, row, index); weather.Contact(card); MonsterMoved(s); return true;
    }
    public function PlayBefore(side : int, instanceId : int, anchorId : int) : bool
    {
        var card : CBetaGwentDuelCard; var a : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var placementSide : int;
        if (!CanAct(side)) return false; card = registry.Find(instanceId); if (!card) return false;
        placementSide = MonsterPlaySide(card, side); if (!ReadPlacementAnchor(placementSide, anchorId, a)) return false;
        if (!card) return false; d = card.Definition();
        // The client supplies a stable anchor ID, never a trusted side/row/index.
        if (d.header.typeMask != 4) return false;
        return PlayAtIndex(side, instanceId, a.locationMask, a.locationIndex);
    }
    private function PlayAtIndex(side : int, instanceId : int, row : int, requestedIndex : int) : bool
    {
        var card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var index, placementSide : int;
        if (!CanAct(side) || (row != 1 && row != 2 && row != 4)) return false;
        card = registry.Find(instanceId); if (!card) return false;
        s = card.Snapshot(); d = card.Definition();
        if (s.positionPlayerId != side || s.locationMask != 8 || !s.canBePlayed) return false;
        placementSide = MonsterPlaySide(card, side); index = CountLocation(placementSide, row);
        if (requestedIndex != -3) index = requestedIndex;
        if (d.header.typeMask == 4 && !CanInsertUnit(placementSide, row, index)) return false;
        if (!Require(match.ClaimInitialMove(side))) return false;
        card.playFromLocation = s.locationMask; card.SetPlayable(false);
        if (d.header.typeMask == 4)
        {
            if (!InsertUnit(card, side, row, index)) { FailAbility("Не удалось разместить отряд."); return false; }
        }
        else card.Move(side, 256, 0);
        Reindex(side, 8); message = d.title;
        SetVisualSource(instanceId, d.header.templateId, side, row);
        if (side == 1) RecordVisual(1, instanceId, "Вы: " + d.title, 480);
        else RecordVisual(1, instanceId, "Соперник: " + d.title, 480);
        BetaGwentLog("DUEL_PLAY player=" + side + " template=" + d.header.templateId + " row=" + row + " index=" + index);
        StartPlayResolution(card, side);
        return !fatal;
    }
    public function UseLeader(side : int) : bool
    {
        var card : CBetaGwentDuelCard; var row : int;
        if (!CanAct(side)) return false;
        card = Leader(side); if (!card) return false;
        row = BestOwnRow(MonsterPlaySide(card,side)); if (row == 0) return false;
        if (side == 1)
        {
            pendingLeader = card; pendingIds.Clear(); requestId += 1;
            message = "Выберите место лидера: нажмите союзника, чтобы встать перед ним, или пустое место своего ряда. До размещения можно отменить.";
            BetaGwentLog("DUEL_LEADER_ROW_BEGIN request=" + requestId);
            return true;
        }
        return PlaceLeader(card, side, row, -3);
    }
    private function PlaceLeader(card : CBetaGwentDuelCard, side : int, row : int, requestedIndex : int) : bool
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!card || !CanInsertUnit(MonsterPlaySide(card,side), row, requestedIndex)) return false;
        s = card.Snapshot();
        if (s.positionPlayerId != side || s.locationMask != 64 || !s.canBePlayed) return false;
        if (!Require(match.ClaimInitialMove(side))) return false;
        // InsertUnit accepts the acting side and applies opposing-only placement once.
        if (!InsertUnit(card, side, row, requestedIndex)) { FailAbility("Не удалось разместить лидера."); return false; }
        card.SetPlayable(false);
        s = card.Snapshot(); d = card.Definition(); SetVisualSource(s.instanceId, d.header.templateId, side, row);
        RecordVisual(1, s.instanceId, d.title + ": лидер выходит на поле", 480);
        BetaGwentLog("DUEL_LEADER_PLACE player=" + side + " row=" + row + " index=" + s.locationIndex);
        StartPlayResolution(card, side); return !fatal;
    }
    private function StartPlayResolution(card : CBetaGwentDuelCard, side : int)
    {
        var s : SBetaGwentCardSnapshot; var cancelled : bool;
        if (playStack.Size() >= 16) { FailAbility("Превышена глубина вложенного розыгрыша."); return; }
        card.ResetModeChoice(); s = card.Snapshot(); playStack.PushBack(card);
        BetaGwentLog("DUEL_PLAY_PUSH depth=" + playStack.Size() + " card=" + s.instanceId);
        // Contact passives resolve on the actual move, before the played graph.
        FlushDeaths(); if (fatal) return; s = card.Snapshot();
        if (s.runtimeTemplate.typeMask == 4 && ((s.locationMask & 7) == 0 || s.isWaitingToDie)) { CompletePlay(card); return; }
        // BeforePlayed cancels the Played graph; AfterPlayed reactions still fire.
        cancelled=monsters.ScoiaBeforePlayed(card);monsters.ScoiaHistory(card);
        // PlayCardAction.AfterApplyTriggers emits AfterPlayed independently of mode/target requests.
        weather.AfterPlayed(card); monsters.AfterPlayed(card); events.NorthTrigger(5, card.Snapshot()); monsters.NilfTrigger(4,card.Snapshot()); FlushDeaths(); if (fatal) return;
        s = card.Snapshot();
        if (s.runtimeTemplate.typeMask == 4 && ((s.locationMask & 7) == 0 || s.isWaitingToDie)) { CompletePlay(card); return; }
        if(cancelled){CompletePlay(card);return;}
        ResolvePlayed(card, side);
    }
    private function PlayFromPile(parentCard : CBetaGwentDuelCard, card : CBetaGwentDuelCard, row : int, requestedIndex : int)
    {
        var s, p : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var i : int;
        if (fatal || !parentCard || !card || playStack.Size() == 0) return;
        if (playStack[playStack.Size() - 1] != parentCard) { FailAbility("Нарушен порядок вложенного розыгрыша."); return; }
        s = card.Snapshot(); p = parentCard.Snapshot(); d = card.Definition();
        if ((s.locationMask != 16 && s.locationMask != 32 && s.locationMask != 128 && s.locationMask != 8) || s.positionPlayerId != NorthActingSide(parentCard))
        { FailAbility("Карта вложенного розыгрыша отсутствует в своей колоде или сбросе."); return; }
        for (i = 0; i < playStack.Size(); i += 1)
            if (playStack[i] == card) { FailAbility("Повторный розыгрыш той же карты в стеке."); return; }
        if (d.header.typeMask == 4 && !CanInsertUnit(MonsterPlaySide(card, s.positionPlayerId), row, requestedIndex))
        { FailAbility("Нет места для вложенного отряда."); return; }
        pendingCard = NULL; pendingRally = NULL; pendingChoice = false; pendingRow = false; pendingPileChoice = false; pendingIds.Clear();
        d = parentCard.Definition(); if (d.effect == 29 || d.effect == 34) parentCard.StorePlayedChild(card); d = card.Definition();
        card.playFromLocation = s.locationMask; card.SetPlayable(false);
        if (d.header.typeMask == 4)
        { if (!InsertUnit(card, s.positionPlayerId, row, requestedIndex)) { FailAbility("Не удалось разместить вложенный отряд."); return; } }
        else card.Move(s.positionPlayerId, 256, 0);
        Reindex(s.positionPlayerId, s.locationMask); SetVisualSource(s.instanceId, d.header.templateId, s.positionPlayerId, row);
        if (s.locationMask == 32) RecordVisual(1, s.instanceId, "Из сброса → " + d.title, 480);
        else if (s.locationMask == 128) RecordVisual(1, s.instanceId, "Создан → " + d.title, 480);
        else if (s.locationMask == 8) RecordVisual(1, s.instanceId, "Повторный розыгрыш → " + d.title, 480);
        else RecordVisual(1, s.instanceId, "Из колоды → " + d.title, 480);
        s = card.Snapshot();
        BetaGwentLog("DUEL_NESTED_PLAY parentCard=" + p.instanceId + " card=" + s.instanceId + " template=" + d.header.templateId + " row=" + s.locationMask + " index=" + s.locationIndex);
        // Only the original hand/leader play claims the move. Child requests keep this turn suspended.
        StartPlayResolution(card, s.positionPlayerId);
    }
    private function IsPlayAncestor(card : CBetaGwentDuelCard) : bool
    {
        var i : int;
        for(i=0;i<playStack.Size();i+=1)if(playStack[i]==card)return true;
        return false;
    }
    private function ExistingChildAvailable(source : CBetaGwentDuelCard, child : CBetaGwentDuelCard) : bool
    {
        var s : SBetaGwentCardSnapshot;
        if(!source || !child || IsPlayAncestor(child))return false;
        s=child.Snapshot();
        return !s.isWaitingToDie && s.positionPlayerId==NorthActingSide(source)
            && (s.locationMask==16 || s.locationMask==32 || s.locationMask==128 || s.locationMask==8);
    }
    private function BeginPilePlay(source : CBetaGwentDuelCard, side : int)
    {
        var cards : array<CBetaGwentDuelCard>; var candidate : CBetaGwentDuelCard; var ids : array<int>; var s : SBetaGwentCardSnapshot;
        var d, unitDefinition : SBetaGwentDuelDefinition; var i, extreme, best, bestValue, value : int;
        d = source.Definition(); pendingCard = source; pendingChoice = false; pendingRow = false;
        pendingPileChoice = true; pendingIds.Clear(); requestId += 1;
        LocationCards(side, d.pileLocation, cards);
        extreme = -2147483647; if (d.pilePickMode == 2) extreme = 2147483647;
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); unitDefinition = cards[i].Definition();
            if ((s.runtimeTemplate.typeMask & d.targetTypes) == 0 || (s.runtimeTierMask & d.targetTiers) == 0
                || s.isWaitingToDie || IsPlayAncestor(cards[i]) || (s.tokenMask & d.targetIgnore) != 0 || (d.consumeMaximum > 0 && s.power.currentPower > d.consumeMaximum)) continue;
            if (d.pileTraitMask != 0 && (unitDefinition.unitTraits & d.pileTraitMask) == 0) continue;
            ids.PushBack(s.instanceId);
            if (d.pilePickMode == 1) extreme = Max(extreme, s.power.currentPower);
            if (d.pilePickMode == 2) extreme = Min(extreme, s.power.currentPower);
        }
        if (d.pilePickMode == 3)
        {
            if (ids.Size() > 0) pendingIds.PushBack(ids[random.NextBounded(ids.Size())]);
        }
        else if (d.pilePickMode != 0)
        {
            for (i = 0; i < ids.Size(); i += 1)
            { candidate = registry.Find(ids[i]); s = candidate.Snapshot(); if (s.power.currentPower == extreme) pendingIds.PushBack(ids[i]); }
            if (pendingIds.Size() > 0) { best = pendingIds[random.NextBounded(pendingIds.Size())]; pendingIds.Clear(); pendingIds.PushBack(best); }
        }
        else
        {
            if (d.pileShuffle != 0) ShuffleIds(ids);
            for (i = 0; i < ids.Size(); i += 1)
            { if (d.pileCandidateLimit != 0 && i >= d.pileCandidateLimit) break; pendingIds.PushBack(ids[i]); }
        }
        BetaGwentLog("DUEL_PILE_CHOICE source=" + d.header.templateId + " player=" + side + " zone=" + d.pileLocation + " candidates=" + pendingIds.Size());
        if (pendingIds.Size() == 0) { message = d.title + ": подходящих карт нет."; CompletePlay(source); return; }
        if (d.pilePickMode != 0) { SelectPileCard(pendingIds[0]); return; }
        if (side == 2)
        {
            bestValue = -2147483647;
            for (i = 0; i < pendingIds.Size(); i += 1)
            { candidate = registry.Find(pendingIds[i]); s = candidate.Snapshot(); value = s.power.currentPower; if (s.runtimeTemplate.typeMask == 2) value += 5;
              if (value > bestValue) { bestValue = value; best = pendingIds[i]; } }
            SelectPileCard(best); return;
        }
        message = d.title + ": выберите карту для розыгрыша. Для отряда затем укажите место в своём ряду.";
    }
    private function SelectPileCard(id : int)
    {
        var source, child : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var row : int;
        if (!pendingPileChoice || !pendingCard || !pendingIds.Contains(id)) return;
        source = pendingCard; child = registry.Find(id);
        if (!child) { BeginPilePlay(source,NorthActingSide(source));return; }
        s = child.Snapshot(); d = source.Definition();
        if (s.locationMask != d.pileLocation || s.positionPlayerId != NorthActingSide(source) || s.isWaitingToDie)
        {
            BetaGwentLog("DUEL_PILE_REFRESH source="+source.TemplateId()+" target="+id);
            BeginPilePlay(source,NorthActingSide(source));return;
        }
        pendingPileChoice = false; pendingIds.Clear();
        if (s.runtimeTemplate.typeMask != 4) { PlayFromPile(source, child, 0, -3); return; }
        row = BestOwnRow(MonsterPlaySide(child,s.positionPlayerId));
        if (row == 0) { message = "Нет места для выбранного отряда."; CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        if (NilfDecisionSide() == 2) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
        d = child.Definition(); message = "Выберите место для " + d.title + ": союзника для вставки перед ним или пустое место своего ряда.";
    }
    private function BeginCreatedPlay(source : CBetaGwentDuelCard, templateId : int)
    {
        var id : int; var child : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var row : int; var m : SBetaGwentMatchSnapshot;
        s = source.Snapshot();
        // A unit creator can leave the board while its first child resolves.
        // Finish the remaining graph rather than preparing an invalid creation.
        if(s.runtimeTemplate.typeMask==4 && ((s.locationMask&7)==0 || s.isWaitingToDie))
        { CompletePlay(source);return; }
        if (!registry.Allocate(id) || !effects.EnqueueCreatedCard(source, templateId, id) || !FlushEffects())
        { FailAbility("Не удалось создать карту для розыгрыша."); return; }
        child = registry.Find(id); if (!child) { FailAbility("Созданная карта не найдена."); return; }
        d = child.Definition(); pendingIds.Clear(); pendingChoice = false; pendingRow = false; pendingCard = source;
        if (d.header.typeMask != 4) { PlayFromPile(source, child, 0, -3); return; }
        s = child.Snapshot(); row = BestOwnRow(MonsterPlaySide(child, s.positionPlayerId));
        if (row == 0) { child.Move(s.positionPlayerId, 512, 0); CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        m = match.Snapshot(); if (NilfDecisionSide() == 2) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
        message = "Выберите место созданного отряда: " + d.title + ".";
    }
    private function ResolveExpandedTarget(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var s, t : SBetaGwentCardSnapshot; var rows : array<int>; var row, side, i : int;
        d = source.Definition(); s = source.Snapshot(); side = s.positionPlayerId;
        if (!target) { CompletePlay(source); return; } t = target.Snapshot();
        if (d.specialMode == 31 || d.specialMode == 32)
        {
            if (d.specialMode == 31 || (d.powerMultiplier != 0 && t.power.currentPower < t.power.basePower + t.power.permanentPower)) QueueResetPower(source, target);
            else if (d.powerMultiplier == 0 && !effects.Enqueue(target, 13, 99, true, source)) { FailAbility("Не удалось поставить лечение в очередь."); return; }
            if (!effects.Enqueue(target, 12, d.amount, true, source)) { FailAbility("Не удалось поставить изменение изначальной силы в очередь."); return; }
            CompletePlay(source); return;
        }
        if (d.specialMode == 35) { QueueDestroy(target); CompletePlay(source); return; }
        if (d.specialMode == 34)
        {
            QueuePower(target, -d.amount, false); if (!FlushEffects()) return; t = target.Snapshot();
            if (t.power.currentPower <= 0 && !effects.Enqueue(target, 14, 0, true, source)) { FailAbility("Не удалось поставить удаление в очередь."); return; }
            CompletePlay(source); return;
        }
        if (d.specialMode == 25)
        { QueueDestroy(target); if (!FlushEffects()) return; DrainDeaths(); if (!fatal) BeginCreatedPlay(source, d.playTemplateId); return; }
        if (d.specialMode == 27)
        {
            QueuePower(target, -d.amount, false); if (!FlushEffects()) return;
            for (row = 1; row <= 4; row *= 2) if (CountLocation(side, row) < 9) rows.PushBack(row);
            if (rows.Size() > 0)
            { row = rows[random.NextBounded(rows.Size())]; s.locationMask = row; s.locationIndex = CountLocation(side, row);
              QueueSpawn(s, d.deploySpawnTemplate, d.deploySpawnCount); }
            CompletePlay(source); return;
        }
        if (d.specialMode == 28)
        {
            QueuePower(target, -d.amount, false); if (!FlushEffects()) return; t = target.Snapshot();
            if (!t.isWaitingToDie && t.locationMask != 4)
            { row = t.locationMask * 2; if (CountLocation(t.positionPlayerId, row) >= 9) QueueDestroy(target);
              else QueueRelocation(target, t.positionPlayerId, row, false); }
            CompletePlay(source); return;
        }
        if (d.specialMode == 29)
        { QueueRelocation(target, side, t.locationMask, false); CompletePlay(source); return; }
        if (d.specialMode == 30)
        {
            QueueRelocation(target, side, 8, true); if (!FlushEffects()) return; t = target.Snapshot();
            if (t.locationMask != 8) { CompletePlay(source); return; }
            if (!effects.Enqueue(target, 1, d.amount, false, source, 31) || !FlushEffects()) return;
            pendingCard = source; pendingRally = target; pendingIds.Clear(); requestId += 1;
            row = BestOwnRow(MonsterPlaySide(target,side)); if (row == 0) { target.SetPlayable(true); CompletePlay(source); return; }
            if (NilfDecisionSide() == 2) { PlaceRally(side, BestNestedRow(target), AiAdjacencyIndex(target, BestNestedRow(target))); return; }
            d = target.Definition(); message = "Повторный розыгрыш: выберите новое место для " + d.title + "."; return;
        }
        CompletePlay(source);
    }
    public function QueueRelocation(card : CBetaGwentDuelCard, side : int, row : int, resetHand : bool)
    { if (!effects.EnqueueRelocation(card, side, row, resetHand)) FailAbility("Не удалось поставить перемещение в очередь."); }
    public function ApplyRelocation(card : CBetaGwentDuelCard, side : int, row : int, resetHand : bool) : bool
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var index : int;
        if (!card) return false; s = card.Snapshot(); d = card.Definition();
        if ((s.locationMask & 7) == 0 || s.isWaitingToDie || (side != 1 && side != 2)) return true;
        if (row != 8 && CountLocation(side, row) >= 9) return true;
        index = CountLocation(side, row);
        card.Move(side, row, index); Reindex(s.positionPlayerId, s.locationMask);
        weather.Contact(card); MonsterMoved(s);
        if (resetHand) { card.ResetInHand(); card.SetPlayable(false); }
        RecordVisual(8, s.instanceId, "Перемещён: " + d.title, 450);
        BetaGwentLog("DUEL_RELOCATE card=" + s.instanceId + " oldSide=" + s.positionPlayerId + " oldRow=" + s.locationMask + " side=" + side + " row=" + row + " replay=" + resetHand);
        return true;
    }
    private function ResolveDeckSpecial(source : CBetaGwentDuelCard)
    {
        var cards, candidates : array<CBetaGwentDuelCard>; var s, child : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i : int;
        s = source.Snapshot(); d = source.Definition(); LocationCards(s.positionPlayerId, 16, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            child = cards[i].Snapshot();
            if (child.runtimeTemplate.templateId == d.playTemplateId && child.runtimeTemplate.typeMask == 2
                && (child.runtimeTierMask & 14) != 0) candidates.PushBack(cards[i]);
        }
        if (candidates.Size() == 0)
        { message = d.title + ": в колоде нет Мороза."; CompletePlay(source); return; }
        // Original random-element node draws even for one candidate; no copy is created.
        PlayFromPile(source, candidates[random.NextBounded(candidates.Size())], 0, -3);
    }
    private function MatchesGraveConsume(s : SBetaGwentCardSnapshot, side : int, d : SBetaGwentDuelDefinition) : bool
    {
        return d.consumeLocation == 32 && s.locationMask == d.consumeLocation && s.positionPlayerId == side
            && s.runtimeTemplate.typeMask == 4 && (s.runtimeTierMask & d.consumeTierMask) != 0 && !s.isWaitingToDie;
    }
    private function ResolveGraveChoice(card : CBetaGwentDuelCard, side : int)
    {
        var cards : array<CBetaGwentDuelCard>; var i : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        d = card.Definition(); LocationCards(side, d.consumeLocation, cards);
        for (i = 0; i < cards.Size(); i += 1)
        { s = cards[i].Snapshot(); if (MatchesGraveConsume(s, side, d)) pendingIds.PushBack(s.instanceId); }
        BetaGwentLog("DUEL_GRAVE_CHOICE source=" + d.header.templateId + " player=" + side + " candidates=" + pendingIds.Size() + " min=0 max=1");
        if (pendingIds.Size() == 0) { ApplyCardTarget(0); return; }
        if (side == 2) { ApplyCardTarget(BestTarget(side, d.effect, 0)); return; }
        message = d.title + ": выберите бронзовый или серебряный отряд из своего сброса либо завершите без поглощения.";
    }
    private function ResolvePlayed(card : CBetaGwentDuelCard, side : int)
    {
        var cardDefinition : SBetaGwentDuelDefinition;
        var i, chosenSide, chosenRow, specialValue : int; var s : SBetaGwentCardSnapshot;
        cardDefinition = card.Definition();
        if (cardDefinition.effect == 34) { monsters.Played(card); return; }
        if (cardDefinition.effect == 10) { weather.ClearSkies(side, cardDefinition.amount); CompletePlay(card); return; }
        if (cardDefinition.effect == 33)
        {
            pendingCard = card; pendingChoice = true; pendingRow = false; pendingIds.Clear(); requestId += 1;
            BetaGwentDuelModeChoices(cardDefinition.header.templateId, pendingIds);
            message = cardDefinition.title + ": выберите режим, затем допустимую цель.";
            if (side == 2) ResolveModeChoice(BestModeChoice(cardDefinition, side));
            return;
        }
        if (cardDefinition.effect == 29) { BeginPilePlay(card, side); return; }
        if (cardDefinition.effect == 28 && cardDefinition.specialMode == 24)
        { if (Score(side) < Score(BetaGwentOpponentId(side))) BeginCreatedPlay(card, cardDefinition.playTemplateId);
          else BeginCreatedPlay(card, cardDefinition.deploySpawnTemplate); return; }
        if (cardDefinition.effect == 24)
        {
            pendingCard = card; pendingIds.Clear(); pendingChoice = true; pendingRow = false; requestId += 1;
            pendingIds.PushBack(113305); pendingIds.PushBack(113312);
            message = "Дагон: создайте Густой туман или Проливной дождь, затем выберите ряд соперника.";
            if (side == 2) ResolveDagonChoice(ChooseDagonWeather(side));
            return;
        }
        if (cardDefinition.effect == 23)
        {
            QueueTimer(card, 2, cardDefinition.timerPeriod); if (!FlushEffects()) return;
            ConsumeRight(card); CompletePlay(card); return;
        }
        if (cardDefinition.effect == 21)
        {
            s = card.Snapshot(); // GetCardPositionOnLeft is this row and the same index.
            QueueSpawn(s, cardDefinition.deploySpawnTemplate, cardDefinition.deploySpawnCount);
            CompletePlay(card); return;
        }
        if (cardDefinition.effect == 26)
        { QueueDeployCopies(card, cardDefinition.deploySummonTemplate); CompletePlay(card); return; }
        if (cardDefinition.effect == 28 && cardDefinition.specialRequest == 0)
        { specials.Auto(card); message = cardDefinition.title + ": эффект применён."; CompletePlay(card); return; }
        if (cardDefinition.effect == 0) { CompletePlay(card); return; }
        if (cardDefinition.effect == 5) { Epidemic(); CompletePlay(card); return; }
        if (cardDefinition.effect == 14) { ResolveDeckSpecial(card); return; }
        if (cardDefinition.effect == 15)
        {
            s = card.Snapshot(); weather.ClearRow(side, s.locationMask);
            message = cardDefinition.title + ": свой ряд очищен."; CompletePlay(card); return;
        }
        if (cardDefinition.effect < 1 || cardDefinition.effect > 32 || cardDefinition.effect == 10 || cardDefinition.effect == 11)
        { FailAbility("Неизвестная способность разыгранной карты."); return; }
        specialHitsLeft = cardDefinition.specialCount; pendingHandPower = false; pendingPileChoice = false; handPowerTarget = 0;
        pendingCard = card; pendingIds.Clear(); pendingRow = cardDefinition.effect == 4 || cardDefinition.weatherToken != 0 || (cardDefinition.effect == 28 && cardDefinition.specialRequest == 2); requestId += 1;
        if (cardDefinition.effect == 9)
        {
            pendingChoice = true; pendingIds.PushBack(113401); pendingIds.PushBack(113402);
            message = "Рассвет: выберите Чистое небо или случайный бронзовый отряд из колоды.";
            if (side == 2) ResolveFirstLight(ChooseFirstLight(side));
            return;
        }
        if (cardDefinition.consumeLocation == 32) { ResolveGraveChoice(card, side); return; }
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (MatchesCardTarget(s, cardDefinition))
            {
                if (cardDefinition.targetSide == 2 && s.positionPlayerId != BetaGwentOpponentId(side)) continue;
                if (cardDefinition.targetSide == 1 && s.positionPlayerId != side) continue;
                if (cardDefinition.consumeMaximum > 0 && s.power.currentPower > cardDefinition.consumeMaximum) continue;
                if (cardDefinition.effect == 28 && cardDefinition.specialMode == 29 && CountLocation(side, s.locationMask) >= 9) continue;
                pendingIds.PushBack(s.instanceId);
            }
        }
        if (side == 2)
        {
            if (cardDefinition.effect == 28 && pendingRow)
            {
                specialValue = specials.BestRow(cardDefinition, side, chosenSide, chosenRow);
                if (cardDefinition.targetMinimum == 0 && specialValue <= 0 && cardDefinition.header.templateId != 113206) CompletePlay(card);
                else ApplyRowTarget(chosenSide, chosenRow);
            }
            else if (cardDefinition.weatherToken != 0) ApplyRowTarget(BetaGwentOpponentId(side), BestWeatherRow(side, cardDefinition.weatherToken));
            else if (pendingRow) ApplyRowTarget(BetaGwentOpponentId(side), BestEnemyRow(side));
            else ApplyCardTarget(BestTarget(side, cardDefinition.effect, cardDefinition.amount));
        }
        else if (!pendingRow && pendingIds.Size() == 0) ApplyCardTarget(0);
        else if (cardDefinition.effect == 28 && pendingRow)
        {
            message = cardDefinition.title + ": выберите подсвеченный ряд.";
            if (cardDefinition.targetMinimum == 0) message += " Можно завершить без цели.";
        }
        else if (cardDefinition.weatherToken != 0)
        {
            message = cardDefinition.title + ": выберите ряд соперника.";
            if (cardDefinition.targetMinimum == 0) message += " Можно сыграть без цели.";
        }
        else if (pendingRow) message = "Разрыв: нажмите любой ряд, чтобы нанести всем отрядам в нём " + cardDefinition.amount + " урона.";
        else
        {
            message = cardDefinition.title + ": выберите подсвеченный отряд.";
            if (cardDefinition.effect == 22) message += " Истощение: до " + cardDefinition.amount + " силы без расхода брони. Можно завершить без цели.";
            if (cardDefinition.consumeMaximum > 0) message += " Поглощение: сила не выше " + cardDefinition.consumeMaximum + ". Можно завершить без цели.";
        }
    }
    private function CompletePlay(card : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var parentCard, child : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition;
        if (fatal || !card || !FlushEffects()) return;
        if (playStack.Size() == 0 || playStack[playStack.Size() - 1] != card)
        { FailAbility("Нарушен порядок завершения розыгрыша."); return; }
        pendingCard = NULL; pendingIds.Clear(); pendingRow = false;
        pendingRally = NULL; pendingChoice = false; pendingHandPower = false; pendingPileChoice = false; handPowerTarget = 0; specialHitsLeft = 0;
        DrainDeaths(); if (fatal) return; s = card.Snapshot();
        if (s.runtimeTemplate.typeMask == 2 && !(nilfJob && nilfJob.source==card && nilfJob.kind!=8)) card.Move(s.positionPlayerId, 32, CountLocation(s.positionPlayerId, 32));
        playStack.Erase(playStack.Size() - 1);
        if(nilfJob && nilfJob.source==card && playStack.Size()==0)
        {if(nilfJob.kind==2)MonsterDraw(nilfJob.side,false);nilfJob=NULL;if(NilfNextReaction())return;effects.Report();SetVisualSource(0,0,0,0);FinishTurn();return;}
        if(card.TemplateId()!=201601 && s.runtimeTemplate.typeMask==2 && (s.runtimeTierMask&6)!=0 && BetaGwentNilfSpell(s.runtimeTemplate.templateId))
        {if(s.positionPlayerId==1)nilfSpellOne=s.runtimeTemplate.templateId;else nilfSpellTwo=s.runtimeTemplate.templateId;}
        BetaGwentLog("DUEL_PLAY_POP depth=" + playStack.Size() + " card=" + s.instanceId);
        if (playStack.Size() > 0)
        {
            parentCard = playStack[playStack.Size() - 1]; s = parentCard.Snapshot(); d = parentCard.Definition();
            SetVisualSource(s.instanceId, d.header.templateId, s.positionPlayerId, s.locationMask);
            // Resume only supported parent graphs; tutors apply their boost after the child resolves.
            if (d.effect != 9 && d.effect != 14 && d.effect != 24 && d.effect != 29 && d.effect != 34 && !(d.effect == 28 && (d.specialMode == 24 || d.specialMode == 25 || d.specialMode == 30))) { FailAbility("Неизвестное продолжение родительской способности."); return; }
            if (d.effect == 29)
            {
                child = parentCard.TakePlayedChild();
                if (child && d.amount > 0)
                { s = child.Snapshot(); if ((s.locationMask & 7) != 0 && !s.isWaitingToDie) QueuePower(child, d.amount, false); }
                BetaGwentLog("DUEL_PILE_RETURN source=" + d.header.templateId + " postBoost=" + d.amount);
            }
            if (d.effect == 34 && monsters.ChildReturned(parentCard)) return;
            CompletePlay(parentCard); return;
        }
        if(NilfNextReaction())return;effects.Report(); SetVisualSource(0, 0, 0, 0); FinishTurn();
    }
    public function GetRequestSnapshot() : SBetaGwentRequestSnapshot
    {
        var s : SBetaGwentRequestSnapshot; var d : SBetaGwentDuelDefinition;
        if (!IsPending()) return s;
        if (mulligan)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId;
            s.playerId = 1; s.targetPlayerId = 1; s.kind = BG_RequestChoices;
            s.limits.minimum = 0; s.limits.maximum = mulliganBudget; s.selectedCount = mulliganUsed;
            return s;
        }
        if (pendingLeader)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId;
            s.playerId = 1; s.targetPlayerId = 1; s.kind = BG_RequestTargets;
            s.limits.minimum = 0; s.limits.maximum = 1; return s;
        }
        if (pendingCard && pendingCard.IsMonsterAbility() && !pendingRally)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId; s.playerId = 1; s.targetPlayerId = 1;
            s.kind = BG_RequestTargets; if (pendingChoice || pendingPileChoice) s.kind = BG_RequestChoices;
            s.limits.minimum = monsterMinimum; s.limits.maximum = monsterMaximum; s.selectedCount = pendingCard.monsterIds.Size();
            if (pendingCard.MonsterMode() != 18) s.selectedCount = 0;
            return s;
        }
        if (pendingChoice)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId;
            s.playerId = 1; s.targetPlayerId = 1; s.kind = BG_RequestChoices;
            s.limits.minimum = 1; s.limits.maximum = 1; return s;
        }
        d = pendingCard.Definition(); s.initialized = true; s.applied = true; s.requestId = requestId;
        s.playerId = 1; s.targetPlayerId = 1; s.kind = BG_RequestTargets; s.limits.maximum = 1;
        s.limits.minimum = 1;
        if (d.effect == 28 || d.effect == 1 || d.effect == 2 || d.effect == 31 || d.effect == 32) s.limits.minimum = d.targetMinimum;
        if (pendingPileChoice) { s.kind = BG_RequestChoices; s.limits.minimum = 1; return s; }
        if (pendingHandPower) { s.kind = BG_RequestChoices; s.limits.minimum = 1; return s; }
        if (d.consumeLocation == 32)
        { s.kind = BG_RequestChoices; s.limits.minimum = d.targetMinimum; return s; }
        if (d.effect == 3 || d.effect == 6 || d.effect == 7 || d.effect == 22 || pendingIds.Size() == 0) s.limits.minimum = 0;
        if ((d.effect == 18 || d.effect == 19 || d.effect == 20 || d.effect == 22) && pendingIds.Size() > 0) s.limits.minimum = d.targetMinimum;
        if (d.weatherToken != 0 || d.targetSide != 0 || d.consumeMaximum > 0) s.limits.minimum = d.targetMinimum;
        if (pendingRally) s.limits.minimum = 1;
        // Beta abilities are mandatory: a legal target (or a weather row) must be chosen.
        if (!pendingRow && pendingIds.Size() > 0 && !IsCaranthirMoveRequest()) s.limits.minimum = Max(1, s.limits.minimum);
        if (IsWeatherRowRequest() && SpecialRowMode() == 0 && d.header.templateId != 113206 && !IsCaranthirMoveRequest()) s.limits.minimum = 1;
        // Kind2 uses existing card highlight bridge. Row requests carry a view-only flag separately.
        return s;
    }
    public function GetRequestViews(out output : array<SBetaGwentDevelopmentRequestCard>)
    {
        var i : int; var v : SBetaGwentDevelopmentRequestCard; var c : CBetaGwentDuelCard; var d : SBetaGwentDuelDefinition;
        var s : SBetaGwentCardSnapshot;
        output.Clear(); if (pendingRow || pendingLeader || pendingRally) return;
        for (i = 0; i < pendingIds.Size(); i += 1)
        {
            if (pendingChoice) d = BetaGwentDuelViewDefinition(pendingIds[i]);
            else { c = registry.Find(pendingIds[i]); if (!c) continue; d = c.Definition(); s=c.Snapshot(); }
            v.id = pendingIds[i]; v.title = d.title; v.templateId = d.header.templateId;
            v.factionId = d.header.factionMask; v.revealed = !(s.locationMask==8 && s.positionPlayerId==2 && (s.tokenMask&64)==0); v.selected = false;if(!v.revealed){v.title="Скрытая карта противника";v.templateId=0;v.factionId=0;}output.PushBack(v);
        }
    }
    public function SelectTarget(id : int, item : int) : bool
    {
        if (!IsPending() || mulligan || pendingChoice || pendingRally || pendingLeader || pendingRow || id != requestId || !BetaGwentRequestContains(pendingIds, item)) return false;
        if (pendingCard.IsMonsterAbility()) monsters.Select(pendingCard, item);
        else if (pendingPileChoice) SelectPileCard(item); else ApplyCardTarget(item); return !fatal;
    }
    public function FinishTarget(id : int) : bool
    {
        var s : SBetaGwentRequestSnapshot; var d : SBetaGwentDuelDefinition;
        if (pendingLeader && id == requestId && !fatal)
        {
            pendingLeader = NULL; message = "Выбор лидера отменён. Можно сыграть карту или выбрать лидера снова.";
            BetaGwentLog("DUEL_LEADER_ROW_CANCEL request=" + id); return true;
        }
        s = GetRequestSnapshot();
        if (pendingCard && pendingCard.IsMonsterAbility() && !pendingRally && id == requestId && monsterMinimum == 0)
        { monsters.Select(pendingCard, 0); return !fatal; }
        if (!IsPending() || mulligan || pendingChoice || pendingRally || id != requestId || s.limits.minimum != 0) return false;
        if (pendingPileChoice) { CompletePlay(pendingCard); return !fatal; }
        if (IsWeatherRowRequest()) { CompletePlay(pendingCard); return !fatal; }
        if (pendingRow)
        {
            if (!pendingCard) return false;
            // White Frost's empty selection takes the source graph's false branch (Ranged + Siege).
            d = pendingCard.Definition(); if (d.header.templateId == 113206) ApplyRowTarget(2, 2);
            else CompletePlay(pendingCard);
            return !fatal;
        }
        ApplyCardTarget(0); return !fatal;
    }
    public function SelectPlacementBefore(id : int, anchorId : int) : bool
    {
        var card : CBetaGwentDuelCard; var a, s : SBetaGwentCardSnapshot;
        var m : SBetaGwentMatchSnapshot;
        if (fatal || waiting || id != requestId || (!pendingLeader && !pendingRally)) return false;
        m = match.Snapshot();
        if (!m.turnActive || m.currentPlayerId != 1 || m.matchWinnerMask != 0) return false;
        if (pendingLeader)
        {
            if (!ReadPlacementAnchor(MonsterPlaySide(pendingLeader,1), anchorId, a)) return false;
            card = pendingLeader; s = card.Snapshot();
            if (m.playerOne.hasMadeInitialMoveForCurrentTurn || s.positionPlayerId != 1 || s.locationMask != 64 || !s.canBePlayed) return false;
            pendingLeader = NULL;
            return PlaceLeader(card, 1, a.locationMask, a.locationIndex);
        }
        s = pendingRally.Snapshot();
        if (!ReadPlacementAnchor(MonsterPlaySide(pendingRally, 1), anchorId, a)) return false;
        if (!pendingCard || playStack.Size() == 0 || playStack[playStack.Size() - 1] != pendingCard
            || s.positionPlayerId != 1 || (s.locationMask != 16 && s.locationMask != 32 && s.locationMask != 128 && s.locationMask != 8) || s.runtimeTemplate.typeMask != 4) return false;
        PlaceRally(1, a.locationMask, a.locationIndex); return !fatal;
    }
    public function SelectRow(id : int, side : int, row : int) : bool
    {
        var card : CBetaGwentDuelCard; var m : SBetaGwentMatchSnapshot; var d : SBetaGwentDuelDefinition; var caranthir : SBetaGwentCardSnapshot;
        // Confirm the already fixed opposite row without the optional move.
        // This never lets Caranthir choose a different row than his own.
        if (IsCaranthirMoveRequest() && !fatal && id == requestId)
        {
            caranthir = pendingCard.Snapshot();
            if (side != BetaGwentOpponentId(caranthir.positionPlayerId) || row != caranthir.locationMask) return false;
            return FinishTarget(id);
        }
        if (!IsRowRequest() || fatal || id != requestId || (side != 1 && side != 2) || (row != 1 && row != 2 && row != 4)) return false;
        if (pendingLeader)
        {
            m = match.Snapshot();
            if (side != MonsterPlaySide(pendingLeader,1) || CountLocation(side, row) >= 9 || !m.turnActive || m.currentPlayerId != 1) return false;
            card = pendingLeader; pendingLeader = NULL;
            return PlaceLeader(card, 1, row, -3);
        }
        if (pendingRally)
        {
            if (side != MonsterPlaySide(pendingRally, 1) || CountLocation(side, row) >= 9) return false;
            PlaceRally(1, row, -3); return !fatal;
        }
        d = pendingCard.Definition();
        if (d.effect == 34 && pendingRow)
        {
            // Use the same side mask advertised by the UI. Row reset and row
            // movement can target either side; allied weather targets our row.
            if(!ValidMonsterRow(side,row))return false;
            monsters.Row(pendingCard, side, row);return !fatal;
        }
        if (IsWeatherRowRequest() && side != BetaGwentOpponentId(NorthActingSide(pendingCard))) return false;
        if (d.effect == 28 && !specials.ValidRow(d, 1, side, row)) return false;
        ApplyRowTarget(side, row); return !fatal;
    }
    private function ApplyCardTarget(id : int)
    {
        var source, target : CBetaGwentDuelCard; var cardDefinition, targetDefinition : SBetaGwentDuelDefinition;
        var s, t : SBetaGwentCardSnapshot; var amount, i, offset : int;
        source = pendingCard; if (!source) return;
        cardDefinition = source.Definition(); s = source.Snapshot(); target = registry.Find(id);
        if (cardDefinition.effect == 34) { monsters.Select(source, id); return; }
        if (cardDefinition.effect == 28 && cardDefinition.specialMode >= 25 && cardDefinition.specialMode <= 35)
        { ResolveExpandedTarget(source, target); return; }
        if (cardDefinition.effect == 28 && pendingHandPower)
        {
            if (!target) { CompletePlay(source); return; }
            t = target.Snapshot(); amount = t.power.basePower;
            target = registry.Find(handPowerTarget); if (target)
            { if (cardDefinition.specialMode == 22) QueuePower(target, amount, false); else QueuePower(target, -amount, false); }
            CompletePlay(source); return;
        }
        if (target && cardDefinition.effect == 28 && (cardDefinition.specialMode == 22 || cardDefinition.specialMode == 23))
        { BeginHandPower(source, target); return; }
        if (target)
        {
            t = target.Snapshot();
            if (cardDefinition.effect == 28) specials.Target(source, target);
            else if (cardDefinition.effect == 1) QueuePower(target, -cardDefinition.amount, false);
            else if (cardDefinition.effect == 31)
            { if (!effects.Enqueue(target, 12, -cardDefinition.amount, false, source)) FailAbility("Не удалось ослабить изначальную силу."); }
            else if (cardDefinition.effect == 32) QueueMultiplyPower(source, target, cardDefinition.powerMultiplier);
            else if (cardDefinition.effect == 27)
            {
                // Read the target row hazard before applying damage or death cleanup.
                amount = cardDefinition.amount;
                if ((weather.Token(t.positionPlayerId, t.locationMask) & cardDefinition.conditionalWeatherToken) != 0)
                    amount = cardDefinition.conditionalDamage;
                QueuePower(target, -amount, false);
                BetaGwentLog("DUEL_CONDITIONAL_DAMAGE source=" + s.instanceId + " target=" + t.instanceId + " amount=" + amount);
            }
            else if (cardDefinition.effect == 25)
            {
                QueuePower(target, -cardDefinition.amount, false); if (!FlushEffects()) return;
                t = target.Snapshot();
                // FilterCurrentPower==0 is read before death cleanup resets inactive power.
                if (t.power.currentPower == 0 || weather.Token(t.positionPlayerId, t.locationMask) == cardDefinition.conditionalWeatherToken)
                {
                    QueuePower(source, cardDefinition.conditionalBoost, false);
                    BetaGwentLog("DUEL_WARRIOR_BOOST source=" + s.instanceId + " target=" + t.instanceId + " killed=" + (t.power.currentPower == 0) + " boost=" + cardDefinition.conditionalBoost);
                }
            }
            else if (cardDefinition.effect == 2) QueuePower(target, cardDefinition.amount, false);
            else if (cardDefinition.effect == 6) QueuePower(target, -CountLocation(s.positionPlayerId, 8), false);
            else if (cardDefinition.effect == 7)
            {
                amount = t.power.currentPower / 2;
                QueuePower(target, -amount, true); QueuePower(source, amount, true);
            }
            else if (cardDefinition.effect == 22)
            {
                if (!MatchesCardTarget(t, cardDefinition)) { FailAbility("Недопустимая цель истощения."); return; }
                // The source graph stores Drain before the two ChangePower actions.
                amount = Min(t.power.currentPower, cardDefinition.amount);
                QueuePower(target, -amount, true); QueuePower(source, amount, false);
                BetaGwentLog("DUEL_DRAIN source=" + s.instanceId + " target=" + t.instanceId
                    + " cached=" + amount + " ignoreArmor=true consume=false");
            }
            else if (cardDefinition.effect == 16)
            {
                if (t.power.currentPower > cardDefinition.consumeMaximum || t.isWaitingToDie || (t.locationMask & 7) == 0 || (t.tokenMask & 264) != 0)
                { FailAbility("Недопустимая цель поглощения."); return; }
                // Graph caches current power before DestroyCards(Consume), then boosts owner.
                amount = t.power.currentPower;
                QueueConsume(source, target); if (!FlushEffects()) return;
                QueuePower(source, amount, false);
                BetaGwentLog("DUEL_CONSUME_BOOST source=" + s.instanceId + " cachedPower=" + amount);
            }
            else if (cardDefinition.effect == 17)
            {
                if (!MatchesGraveConsume(t, s.positionPlayerId, cardDefinition))
                { FailAbility("Недопустимая карта для поглощения из сброса."); return; }
                amount = t.power.currentPower;
                QueueConsume(source, target); if (!FlushEffects()) return;
                QueuePower(source, amount, false);
                BetaGwentLog("DUEL_CONSUME_BOOST source=" + s.instanceId + " cachedPower=" + amount + " fromGrave=true");
            }
            else if (cardDefinition.effect == 18 || cardDefinition.effect == 19)
            {
                if ((t.locationMask & 7) == 0 || t.runtimeTemplate.typeMask != 4 || t.isWaitingToDie || (t.tokenMask & cardDefinition.targetIgnore) != 0)
                { FailAbility("Недопустимая цель блокировки."); return; }
                // Graph flow: toggle resolves before the opponent filter/power action.
                QueueLockToggle(source, target); if (!FlushEffects()) return;
                t = target.Snapshot();
                if (t.positionPlayerId == BetaGwentOpponentId(s.positionPlayerId))
                {
                    if (cardDefinition.effect == 18) QueueMultiplyPower(source, target, cardDefinition.powerMultiplier);
                    else QueuePower(target, -cardDefinition.amount, false);
                }
            }
            else if (cardDefinition.effect == 20)
            {
                if (!MatchesCardTarget(t, cardDefinition) || cardDefinition.transformResetMode != 255)
                { FailAbility("Недопустимая цель превращения."); return; }
                QueueTransform(source, target, cardDefinition.transformTemplate);
            }
            else if (cardDefinition.effect == 3)
            {
                // Shape mask57344, pivot4: selected unit and immediate neighbours.
                for (i = 0; i < live.Size(); i += 1)
                {
                    s = live[i].Snapshot(); offset = s.locationIndex - t.locationIndex;
                    if (s.positionPlayerId != t.positionPlayerId || s.locationMask != t.locationMask || offset < -1 || offset > 1) continue;
                    QueuePower(live[i], cardDefinition.amount, false); QueueArmor(live[i], cardDefinition.addedArmor);
                }
            }
            targetDefinition = target.Definition();
            message = cardDefinition.title + " → " + targetDefinition.title;
        }
        else message = cardDefinition.title + ": нет выбранной цели.";
        if (cardDefinition.effect == 28 && cardDefinition.specialMode == 17 && specialHitsLeft > 1)
        { specialHitsLeft -= 1; ContinueSpecialHits(source); return; }
        CompletePlay(source);
    }
    private function ContinueSpecialHits(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var a, s : SBetaGwentCardSnapshot; var i : int;
        if (!FlushEffects()) return; DrainDeaths(); if (fatal) return;
        d = source.Definition(); a = source.Snapshot(); pendingIds.Clear(); requestId += 1;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (s.positionPlayerId == BetaGwentOpponentId(a.positionPlayerId) && MatchesCardTarget(s, d)) pendingIds.PushBack(s.instanceId); }
        message = d.title + ": выберите цель второго удара.";
        if (pendingIds.Size() == 0) CompletePlay(source);
        else if (a.positionPlayerId == 2) ApplyCardTarget(BestTarget(2, 28, d.amount));
    }
    private function BeginHandPower(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var a, s, t : SBetaGwentCardSnapshot;
        var i, bestId, bestPower : int; var cards : array<CBetaGwentDuelCard>; var maximize : bool;
        d = source.Definition(); a = source.Snapshot(); t = target.Snapshot(); handPowerTarget = t.instanceId;
        pendingIds.Clear(); pendingHandPower = true; requestId += 1;
        GetZoneCards(a.positionPlayerId, 8, cards);
        maximize = (d.specialMode == 22 && t.positionPlayerId == a.positionPlayerId) || (d.specialMode == 23 && t.positionPlayerId != a.positionPlayerId);
        bestPower = 2147483647; if (maximize) bestPower = -1;
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); if (s.runtimeTemplate.typeMask != 4 || (s.runtimeTierMask & 6) == 0) continue;
            pendingIds.PushBack(s.instanceId);
            if ((maximize && s.power.basePower > bestPower) || (!maximize && s.power.basePower < bestPower))
            { bestId = s.instanceId; bestPower = s.power.basePower; }
        }
        message = d.title + ": выберите бронзовый или серебряный отряд в своей руке. Карта останется в руке.";
        if (pendingIds.Size() == 0) CompletePlay(source);
        else if (a.positionPlayerId == 2) ApplyCardTarget(bestId);
    }
    private function ApplyRowTarget(side : int, row : int)
    {
        var source : CBetaGwentDuelCard; var cardDefinition : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot; var i : int;
        source = pendingCard; if (!source) return; cardDefinition = source.Definition();
        if (cardDefinition.effect == 28 && cardDefinition.specialMode == 26)
        {
            s = source.Snapshot(); s.positionPlayerId = side; s.locationMask = row; s.locationIndex = CountLocation(side, row);
            QueueSpawn(s, cardDefinition.deploySpawnTemplate, cardDefinition.deploySpawnCount);
            CompletePlay(source); return;
        }
        if (cardDefinition.effect == 28)
        { specials.Row(source, side, row); message = cardDefinition.title + ": эффект применён к ряду."; CompletePlay(source); return; }
        if (cardDefinition.weatherToken != 0)
        {
            weather.ApplyHazard(side, row, cardDefinition.weatherToken); message = cardDefinition.title + ": погода наложена на ряд соперника.";
            CompletePlay(source); return;
        }
        RecordRowVisual(side, row, cardDefinition.title + ": удар по ряду");
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId == side && s.locationMask == row && s.runtimeTemplate.typeMask == 4)
                QueuePower(live[i], -cardDefinition.amount, false);
        }
        message = cardDefinition.title + ": ряд получил " + cardDefinition.amount + " урона."; CompletePlay(source);
    }
    public function SelectFirstLight(id : int, choice : int) : bool
    {
        if (fatal || !IsFirstLightChoice() || id != requestId || !BetaGwentRequestContains(pendingIds, choice)) return false;
        ResolveFirstLight(choice); return !fatal;
    }
    public function SelectTemplateChoice(id : int, choice : int) : bool
    {
        if (fatal || !pendingChoice || id != requestId || !BetaGwentRequestContains(pendingIds, choice)) return false;
        if (pendingCard.IsMonsterAbility()) monsters.Select(pendingCard, choice);
        else if (IsDagonChoice()) ResolveDagonChoice(choice);
        else if (IsModeChoice()) ResolveModeChoice(choice);
        else return SelectFirstLight(id, choice);
        return !fatal;
    }
    private function ResolveModeChoice(choice : int)
    {
        var source : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        source = pendingCard; if (!source || !source.SelectMode(choice)) { FailAbility("Недопустимый режим особой карты."); return; }
        s = source.Snapshot(); d = BetaGwentDuelViewDefinition(choice);
        pendingChoice = false; pendingIds.Clear(); pendingRow = false;
        RecordVisual(8, s.instanceId, "Выбран режим: " + d.title, 350);
        BetaGwentLog("DUEL_MODE_CHOICE source=" + s.runtimeTemplate.templateId + " choice=" + choice);
        ResolvePlayed(source, s.positionPlayerId);
    }
    private function ModeValue(base : SBetaGwentDuelDefinition, choice : int, side : int) : int
    {
        var d, targetDefinition : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot; var i, value, maximum, count, total : int;
        d = BetaGwentDuelModeDefinition(base, choice); maximum = -2147483647;
        if (d.specialRequest == 2) return specials.BestRow(d, side, i, count);
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); targetDefinition = live[i].Definition();
            if (d.effect == 29)
            {
                if (s.positionPlayerId != side || s.locationMask != d.pileLocation || s.isWaitingToDie || s.runtimeTemplate.typeMask != 4
                    || (s.runtimeTierMask & d.targetTiers) == 0 || (s.tokenMask & d.targetIgnore) != 0
                    || (d.pileTraitMask != 0 && (targetDefinition.unitTraits & d.pileTraitMask) == 0)) continue;
                value = s.power.currentPower; count += 1; total += value; maximum = Max(maximum, value);
            }
            else
            {
                if (!MatchesCardTarget(s, d) || (d.targetSide == 1 && s.positionPlayerId != side)
                    || (d.targetSide == 2 && s.positionPlayerId != BetaGwentOpponentId(side))) continue;
                if (d.specialMode == 36 && s.power.currentPower % 2 != d.specialToken) continue;
                if (d.specialMode == 36) { value = DamageValue(s, side, d.amount); total += value; }
                else value = specials.TargetValue(d, s, side);
                maximum = Max(maximum, value);
            }
        }
        if (d.specialMode == 36) return total;
        if (d.pilePickMode == 3 && count > 0) return total / count;
        if (maximum == -2147483647) return 0; return maximum;
    }
    private function BestModeChoice(base : SBetaGwentDuelDefinition, side : int) : int
    {
        var ids : array<int>; var i, best, value, maximum : int;
        BetaGwentDuelModeChoices(base.header.templateId, ids); maximum = -2147483647;
        for (i = 0; i < ids.Size(); i += 1) { value = ModeValue(base, ids[i], side); if (value > maximum) { best = ids[i]; maximum = value; } }
        return best;
    }
    private function ChooseDagonWeather(side : int) : int
    {
        if (WeatherValue(side, BestWeatherRow(side, 2), 2) >= WeatherValue(side, BestWeatherRow(side, 4), 4)) return 113305;
        return 113312;
    }
    private function ResolveDagonChoice(choice : int)
    {
        var source, child : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var id : int; var d : SBetaGwentDuelDefinition;
        source = pendingCard; if (!source || (choice != 113305 && choice != 113312)) return;
        s = source.Snapshot();
        if (!registry.Allocate(id) || id == 0 || registry.Find(id)) { FailAbility("Не удалось выделить ID погоды Дагона."); return; }
        if (!effects.EnqueueCreatedCard(source, choice, id) || !FlushEffects()) { FailAbility("Не удалось создать погоду Дагона."); return; }
        child = registry.Find(id); if (!child) { FailAbility("Созданная погода не найдена."); return; }
        pendingChoice = false; pendingIds.Clear(); pendingCard = NULL;
        child.SetPlayable(false); child.Move(s.positionPlayerId, 256, 0);
        SetVisualSource(id, choice, s.positionPlayerId, 0);
        d = child.Definition(); RecordVisual(1, id, "Дагон → " + d.title, 480);
        BetaGwentLog("DUEL_DAGON_CHOICE player=" + s.positionPlayerId + " template=" + choice + " newCard=" + id);
        // SpawnCards converts Stack256 to Spawn128; PlayCards then plays this new instance.
        // The leader remains on the parent stack; only its root finishes the turn.
        StartPlayResolution(child, s.positionPlayerId);
    }
    public function CreationAllowed(source : CBetaGwentDuelCard, templateId : int) : bool
    {
        var s : SBetaGwentCardSnapshot;var d,child : SBetaGwentDuelDefinition;
        if(!source)return false;s=source.Snapshot();d=source.Definition();child=BetaGwentDuelDefinition(templateId);
        if(s.isWaitingToDie || child.header.templateId==0)return false;
        if(d.effect==24)return (s.locationMask&7)!=0 && (templateId==113305 || templateId==113312);
        if(d.effect==28 && d.specialMode==24)return s.locationMask==256 && (templateId==d.playTemplateId || templateId==d.deploySpawnTemplate);
        if(d.effect==28 && d.specialMode==25)return s.locationMask==256 && templateId==d.playTemplateId;
        if(d.effect==34)return ((s.locationMask&7)!=0 || s.locationMask==256) && MonsterCreationAllowed(source,templateId);
        return false;
    }
    public function ApplyCreatedCard(source : CBetaGwentDuelCard, templateId : int, id : int) : bool
    {
        var s : SBetaGwentCardSnapshot; var child : CBetaGwentDuelCard;
        // Preparation and application share the exact creator whitelist.
        if (!CreationAllowed(source,templateId) || id == 0 || registry.Find(id)) return false;
        s = source.Snapshot(); child = new CBetaGwentDuelCard in this;
        child.Setup(this, id, templateId, NorthActingSide(source), 128, 0); child.createdCopy=true; child.SetPlayable(true);
        if (!registry.Put(id, child)) return false; live.PushBack(child);
        BetaGwentLog("DUEL_CREATED_WEATHER source=" + s.instanceId + " card=" + id + " template=" + templateId + " location=128 spawnType=3");
        return true;
    }
    private function ResolveFirstLight(choice : int)
    {
        var source, card : CBetaGwentDuelCard; var s, unitState : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var candidates, ordered : array<CBetaGwentDuelCard>; var i, row, anchor : int;
        source = pendingCard; if (!source) return; s = source.Snapshot(); d = source.Definition();
        pendingChoice = false; pendingIds.Clear();
        BetaGwentLog("DUEL_FIRST_LIGHT_CHOICE side=" + s.positionPlayerId + " template=" + choice);
        if (choice == 113401)
        {
            weather.ClearSkies(s.positionPlayerId, d.amount);
            message = "Чистое небо: погода снята, повреждённые союзники под погодой усилены на " + d.amount + ".";
            CompletePlay(source); return;
        }
        if (choice != 113402) { fatal = true; message = "Неизвестный вариант Рассвета."; return; }
        LocationCards(s.positionPlayerId, 16, ordered);
        for (i = 0; i < ordered.Size(); i += 1)
        {
            unitState = ordered[i].Snapshot();
            if (unitState.runtimeTemplate.typeMask == 4 && unitState.runtimeTierMask == 2) candidates.PushBack(ordered[i]);
        }
        if (candidates.Size() == 0)
        { message = "Рассвет: в колоде нет бронзового отряда."; CompletePlay(source); return; }
        card = candidates[random.NextBounded(candidates.Size())]; d = card.Definition();
        row = BestCardRow(s.positionPlayerId, d);
        if (row == 0) { message = "Нет места для отряда Рассвета."; CompletePlay(source); return; }
        pendingRally = card; requestId += 1;
        message = "Рассвет → " + d.title + ": нажмите союзника для размещения перед ним или пустое место своего ряда.";
        if (s.positionPlayerId == 2)
        {
            if (d.effect == 23) anchor = BestVranAnchor(2);
            if (anchor > 0)
            { unitState = registry.Find(anchor).Snapshot(); PlaceRally(2, unitState.locationMask, unitState.locationIndex); }
            else PlaceRally(2, row, -3);
        }
    }
    private function PlaceRally(side : int, row : int, requestedIndex : int)
    {
        var source, card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot;
        source = pendingCard; card = pendingRally; if (!source || !card) return;
        s = card.Snapshot();
        BetaGwentLog("DUEL_RALLY_PLACE side=" + side + " card=" + s.instanceId + " row=" + row);
        PlayFromPile(source, card, row, requestedIndex);
    }
    // Cards that affect units on both sides of themselves go to the middle of the row.
    public function AiAdjacencyIndex(card : CBetaGwentDuelCard, row : int) : int
    {
        var s : SBetaGwentCardSnapshot; var id, count : int;
        if (!card) return -3; s = card.Snapshot(); id = s.runtimeTemplate.templateId;
        if (!AiAdjacencyCard(id)) return -3;
        count = CountLocation(MonsterPlaySide(card, s.positionPlayerId), row);
        if (count < 2) return -3;
        return count / 2;
    }
    // Units whose ability works on neighbours: they belong in the middle of a full row.
    private function AiAdjacencyCard(id : int) : bool { return id == 112403 || id == 142204; }
    private function AiAdjacencyRow(card : CBetaGwentDuelCard, side : int, fallback : int) : int
    {
        var row, best, value, maximum : int; var d : SBetaGwentDuelDefinition;
        d = card.Definition(); best = fallback; maximum = -2147483647;
        for (row = 1; row <= 4; row *= 2)
        {
            if (CountLocation(side, row) >= 9) continue;
            value = Min(4, CountLocation(side, row)) * 6 - AiRowPlacementCost(side, row, d);
            if (value > maximum) { maximum = value; best = row; }
        }
        return best;
    }
    private function BestNestedRow(card : CBetaGwentDuelCard) : int
    {
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var row,side : int;
        s=card.Snapshot();d=card.Definition();side=MonsterPlaySide(card,s.positionPlayerId);
        row=BestCardRow(s.positionPlayerId,d);
        if(BetaGwentAIStrength()>=2 && AiAdjacencyCard(d.header.templateId))row=AiAdjacencyRow(card,side,row);
        // Archetype preferences are suggestions: a full preferred row must
        // not strand an obligatory tutor/resurrection or a created unit.
        if(!CanInsertUnit(side,row,-3))row=BestOwnRow(side);
        return row;
    }
    private function ValidMonsterRow(side : int,row : int) : bool
    {
        var mode,actor : int;
        if(!pendingCard || !pendingRow || !pendingIds.Contains(row))return false;
        mode=SpecialRowMode();actor=NorthActingSide(pendingCard);
        return mode==1 || (mode==8 && side==actor) || (mode==9 && side==BetaGwentOpponentId(actor));
    }
    private function BestDeployRow(side : int, effect : int) : int
    {
        var row, best, value, maximum : int;
        best = BestOwnRow(side); if (effect != 15) return best;
        maximum = -1;
        for (row = 1; row <= 4; row *= 2)
        {
            if (CountLocation(side, row) >= 9) continue;
            value = weather.Damage(side, row) * 3;
            if (weather.Token(side, row) == 4) value *= 2;
            if (value > maximum) { maximum = value; best = row; }
        }
        return best;
    }
    private function BestCardRow(side : int, d : SBetaGwentDuelDefinition) : int
    {
        var row, value, best, maximum : int;
        aiPlacing = d;
        if(side==2 && weatherProfile && d.header.typeMask==4)return weatherAI.BestRow(d);
        if (BetaGwentDuelSpying(d.header.templateId)) side = BetaGwentOpponentId(side);
        best = BestDeployRow(side, d.effect);
        if (d.deploySummonTemplate > 0)
        {
            maximum = -2147483647;
            for (row = 1; row <= 4; row *= 2)
            {
                if (CountLocation(side, row) >= 9) continue;
                value = DeckCopiesValue(side, d.deploySummonTemplate, row, 0, d.deploySummonOtherTemplate, d.deploySummonIgnore, d.deploySummonLinked) - weather.Damage(side, row); if(BetaGwentAIStrength()>=2)value+=weather.Damage(side, row)-AiRowPlacementCost(side,row,d)+CountLocation(side,row);
                if (value > maximum) { maximum = value; best = row; }
            }
            return best;
        }
        if (d.deploySpawnCount > 0)
        {
            maximum = -2147483647;
            for (row = 1; row <= 4; row *= 2)
            {
                if (CountLocation(side, row) >= 9) continue;
                value = Min(d.deploySpawnCount, Max(0, 8 - CountLocation(side, row))) * 2 - weather.Damage(side, row); if(BetaGwentAIStrength()>=2)value+=weather.Damage(side, row)-AiRowPlacementCost(side,row,d)+CountLocation(side,row);
                if (value > maximum) { maximum = value; best = row; }
            }
            return best;
        }
        if (d.deathwishSpawnCount > 0)
        {
            maximum = -2147483647;
            for (row = 1; row <= 4; row *= 2)
            {
                if (CountLocation(side, row) >= 9) continue;
                value = Min(d.deathwishSpawnCount, 9 - CountLocation(side, row)) * 4 - weather.Damage(side, row); if(BetaGwentAIStrength()>=2)value+=weather.Damage(side, row)-AiRowPlacementCost(side,row,d)+CountLocation(side,row);
                if (value > maximum) { maximum = value; best = row; }
            }
            return best;
        }
        if (d.deathwishDamage == 0) {if(side==2)return archetypeAI.Row(d,best);return best;}
        maximum = -2147483647;
        for (row = 1; row <= 4; row *= 2)
        {
            if (CountLocation(side, row) >= 9) continue;
            value = RowEffectValue(side, BetaGwentOpponentId(side), row, d.deathwishDamage); if(BetaGwentAIStrength()>=2)value-=AiRowPlacementCost(side,row,d);
            if (value > maximum) { maximum = value; best = row; }
        }
        return best;
    }
    public function HasWeather(token : int) : bool
    {
        var side, row : int;
        for (side = 1; side <= 2; side += 1)
            for (row = 1; row <= 4; row *= 2) if ((weather.Token(side, row) & token) != 0) return true;
        return false;
    }
    private function HasDeckTemplate(side : int, templateId : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>; var s : SBetaGwentCardSnapshot; var i : int;
        LocationCards(side, 16, cards);
        for (i = 0; i < cards.Size(); i += 1)
        { s = cards[i].Snapshot(); if (s.runtimeTemplate.templateId == templateId) return true; }
        return false;
    }
    private function DeckSummonValue(side : int, templateId : int, optional excludeId : int) : int
    {
        var i, total, count : int; var s : SBetaGwentCardSnapshot;
        if (side == 1) return AiPublicSummonEstimate(templateId);
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (s.instanceId != excludeId && s.positionPlayerId == side && s.locationMask == 16 && s.runtimeTemplate.templateId == templateId)
            { total += s.power.currentPower; count += 1; }
        }
        if (count == 0) return 0; return total / count;
    }
    private function ConsumePassiveValue(side : int, excludeId : int) : int
    {
        var i, value : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); d = live[i].Definition();
            if (s.instanceId == excludeId || s.positionPlayerId != side || d.consumePassiveBoost == 0
                || (s.locationMask & d.consumePassiveLocations) == 0 || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0) continue;
            value += d.consumePassiveBoost;
        }
        return value;
    }
    private function RallyValue(side : int, optional immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>; var i, total, count, value, lowest : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        lowest=2147483647;
        if (BestOwnRow(side) == 0) return 0; LocationCards(side, 16, cards);
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot();
            if (s.runtimeTemplate.typeMask == 4 && s.runtimeTierMask == 2)
            {
                d = cards[i].Definition(); value = s.power.currentPower;
                if(BetaGwentDuelSpying(d.header.templateId))value=-value;
                if (d.effect == 1 || d.effect == 17) value += Max(0, BestEffectValue(side, d.effect, d.amount, d.targetSide, d.header.templateId, immediate));
                if (!immediate && d.effect == 14 && HasDeckTemplate(side, d.playTemplateId)) value += WeatherValue(side, BestWeatherRow(side, 1), 1);
                if (!immediate && d.effect == 15) value += weather.Damage(side, BestDeployRow(side, d.effect)) * 3;
                if (d.deploySummonTemplate > 0) value += DeckCopiesValue(side, d.deploySummonTemplate, BestCardRow(side, d), s.instanceId, d.deploySummonOtherTemplate, d.deploySummonIgnore, d.deploySummonLinked);
                if (d.effect == 25 || d.effect == 27) value += Max(0, BestEffectValue(side, d.effect, d.amount, d.targetSide, d.header.templateId, immediate));
                if (!immediate && d.timerPeriod > 0) value += 2;
                if (!immediate && d.passiveBoost != 0 && HasWeather(d.passiveWeatherToken)) value += d.passiveBoost * 3;
                if (!immediate && d.deathwishDamage != 0) value += Max(0, RowEffectValue(side, BetaGwentOpponentId(side), BestCardRow(side, d), d.deathwishDamage)) / 2;
                if (!immediate && d.deathwishSummonTemplate > 0) value += DeckSummonValue(side, d.deathwishSummonTemplate, s.instanceId) / 2;
                lowest=Min(lowest,value);total += value; count += 1;
            }
        }
        if (count == 0) return 0; if(immediate)return lowest; return total / count;
    }
    private function DeckCopiesValue(side : int, templateId : int, row : int, excludedId : int, optional otherTemplate : int, optional ignore : int, optional linked : int) : int
    {
        var cards : array<CBetaGwentDuelCard>; var t : SBetaGwentCardSnapshot; var i, value, count, available : int;
        if (row == 0) return 0; available = Max(0, 8 - CountLocation(side, row));
        CollectDeploySummon(side, templateId, otherTemplate, ignore, linked, excludedId, cards);
        for (i = 0; i < cards.Size() && count < available; i += 1)
        {
            t = cards[i].Snapshot();
            // Count the same ordered candidates as the actual summon.
            value += t.power.currentPower; count += 1;
        }
        return value;
    }
    private function ChooseFirstLight(side : int) : int
    {
        var d : SBetaGwentDuelDefinition;var immediate : bool; d = BetaGwentDuelDefinition(113303);immediate=AiHorizon(side)==0;
        if (weather.ClearValue(side, d.amount, immediate) >= RallyValue(side,immediate)) return 113401;
        return 113402;
    }
    private function AiHorizon(side : int) : int
    {
        var m : SBetaGwentMatchSnapshot; var enemy : int;
        m = match.Snapshot(); enemy = BetaGwentOpponentId(side);
        if ((enemy == 1 && m.playerOne.hasPassed) || (enemy == 2 && m.playerTwo.hasPassed)) return 0;
        return Max(1, Min(3, Min(CountLocation(side, 8), CountLocation(enemy, 8) + 1)));
    }
    // Public repertoire prior, updated by public field/grave cards. Never reads
    // playerOne's hidden hand/deck templates or the private selected preset.
    private function AiPublicClearRisk() : int
    {
        var ids : array<int>; var observed : array<int>; var d : SBetaGwentDuelDefinition;
        var t : SBetaGwentCardSnapshot; var i, j, option, weight, totalWeight, risk, copies, seenClear, pool : int;
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot();
            if (t.positionPlayerId != 1 || ((t.locationMask & 7) == 0 && t.locationMask != 32 && t.locationMask != 512)
                || (t.tokenMask & 512) != 0 || (t.runtimeTierMask & 14) == 0) continue;
            observed.PushBack(t.runtimeTemplate.templateId);
            if (t.runtimeTemplate.templateId == 113303) seenClear += 1;
        }
        // Only public pile sizes: custom decks may contain up to40 cards.
        pool = Max(1, CountLocation(1, 8) + CountLocation(1, 16));
        for (option = 1; option <= BetaGwentDuelPresetCount(); option += 1)
        {
            BetaGwentDuelPresetDeck(option, ids); weight = 1; copies = 0;
            for (j = 0; j < observed.Size(); j += 1) if (ids.Contains(observed[j])) weight += 2;
            for (j = 0; j < ids.Size(); j += 1) if (ids[j] == 113303) copies += 1;
            copies = Max(0, copies - seenClear);
            risk += weight * Min(80, copies * CountLocation(1, 8) * 100 / pool); totalWeight += weight;
        }
        if (totalWeight == 0) return 0; return risk / totalWeight;
    }
    private function AiPublicSummonEstimate(templateId : int) : int
    {
        var ids, observed : array<int>; var t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var i, j, option, seen, copies, weight, totalWeight, chance, pool : int;
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot();
            if (t.positionPlayerId != 1 || ((t.locationMask & 7) == 0 && t.locationMask != 32 && t.locationMask != 512)
                || (t.tokenMask & 512) != 0 || (t.runtimeTierMask & 14) == 0) continue;
            observed.PushBack(t.runtimeTemplate.templateId);
            if (t.runtimeTemplate.templateId == templateId) seen += 1;
        }
        pool = Max(1, CountLocation(1, 8) + CountLocation(1, 16));
        for (option = 1; option <= BetaGwentDuelPresetCount(); option += 1)
        {
            BetaGwentDuelPresetDeck(option, ids); weight = 1; copies = 0;
            for (j = 0; j < observed.Size(); j += 1) if (ids.Contains(observed[j])) weight += 2;
            for (j = 0; j < ids.Size(); j += 1) if (ids[j] == templateId) copies += 1;
            copies = Max(0, copies - seen);
            chance += weight * Min(100, copies * CountLocation(1, 16) * 100 / pool); totalWeight += weight;
        }
        d = BetaGwentDuelDefinition(templateId);
        if (totalWeight == 0) return 0; return d.header.power * chance / totalWeight / 100;
    }
    private function AiSetupBonus(d : SBetaGwentDuelDefinition) : int
    {
        var i, consumers, engines, weatherCards, frostPayoffs, spies, value : int; var s : SBetaGwentCardSnapshot; var held : SBetaGwentDuelDefinition;
        if (AiHorizon(2) <= 1) return 0;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId != 2 || s.locationMask != 8) continue; held = live[i].Definition();
            if(BetaGwentDuelSpying(held.header.templateId))spies+=1;
            if (held.effect == 16 || held.effect == 23 || held.effect == 17) consumers += 1;
            if (held.consumePassiveBoost > 0) engines += 1;
            if (held.effect == 27 || held.effect == 25) frostPayoffs += 1;
            if ((held.weatherToken & d.passiveWeatherToken) != 0
                || (held.effect == 14 && d.passiveWeatherToken == 1 && HasDeckTemplate(2, held.playTemplateId))) weatherCards += 1;
        }
        // Prefer setup before the payoff; these bonuses estimate future utility.
        if (d.consumePassiveBoost > 0) value += d.consumePassiveBoost * Min(3, consumers);
        if(d.header.templateId==162307)value+=Min(3,spies)*2;
        if (d.effect == 16 || d.effect == 23 || d.effect == 17) value -= Min(4, engines * 2);
        if (d.passiveBoost > 0 && !HasWeather(d.passiveWeatherToken) && weatherCards > 0) value += d.passiveBoost * 2;
        if ((d.weatherToken == 1 || (d.effect == 14 && d.playTemplateId == 113302)) && frostPayoffs > 0) value += Min(4, frostPayoffs * 2);
        return value;
    }
    private function AiReserveCost(d : SBetaGwentDuelDefinition) : int
    {
        var cost : int; var m : SBetaGwentMatchSnapshot; m = match.Snapshot();
        if (d.header.tierMask == 8) cost = 5; else if (d.header.tierMask == 4) cost = 2;
        // Reactive specials are useful later; do not cash them in for one point.
        if (d.header.typeMask == 2 && (d.effect == 20 || d.effect == 19 || d.effect == 1)) cost += 2;
        if (m.roundNumber >= 3) return 0; return cost+archetypeAI.Reserve(d);
    }
    private function WeatherValue(side : int, row : int, token : int) : int
    {
        var enemy, count, targets, previousTargets, gain : int;var m : SBetaGwentMatchSnapshot;enemy = BetaGwentOpponentId(side);m=match.Snapshot();
        if((enemy==1 && m.playerOne.hasPassed) || (enemy==2 && m.playerTwo.hasPassed))return 0;
        count = CountLocation(enemy, row);
        if (weather.Token(enemy, row) == token || count == 0) return 0;
        targets = 1; if (token == 4) targets = Min(2, count);
        previousTargets = 1; if (weather.Token(enemy, row) == 4) previousTargets = Min(2, count);
        gain = weather.DamageFor(enemy, row, token) * targets - weather.Damage(enemy, row) * previousTargets;
        return Max(0, gain) * AiHorizon(side);
    }
    private function BestWeatherRow(side : int, token : int) : int
    {
        var row, best, value, maximum : int; best = 1; maximum = -1;
        for (row = 1; row <= 4; row *= 2)
        { value = WeatherValue(side, row, token); if (value > maximum) { maximum = value; best = row; } }
        return best;
    }
    private function Epidemic()
    {
        var i, lowest : int; var s : SBetaGwentCardSnapshot;
        lowest = 2147483647;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if ((s.locationMask & 7) != 0 && s.power.currentPower < lowest) lowest = s.power.currentPower; }
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if ((s.locationMask & 7) != 0 && s.power.currentPower == lowest) QueueDestroy(live[i]); }
        message = "Эпидемия: уничтожены все слабейшие отряды (" + lowest + ").";
    }
    public function ResolveDuelEvent(item : CBetaGwentDuelEvent)
    {
        var sourceCard, consumeAttacker : CBetaGwentDuelCard; var targets : array<CBetaGwentDuelCard>;
        var s, targetState : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var oldId, oldTemplate, oldSide, oldRow, i, eventMask, attackerBoost : int; var spawnPosition : SBetaGwentCardSnapshot;
        if (fatal || !item) return;
        if (item.kind == 8 || item.kind == 9) { weather.ResolveRowAbility(item); return; }
        sourceCard = registry.Find(item.source.instanceId); if (!sourceCard) { FailAbility("Источник события не найден."); return; }
        d = sourceCard.Definition(); s = sourceCard.Snapshot();
        if (item.kind == 10 || item.kind == 11) { monsters.Event(item); return; }
        if (item.kind == 2 && d.header.templateId == 200038) { monsters.Deathwish(sourceCard, item.source); return; }
        if (item.kind == 1)
        {
            if (d.passiveBoost == 0) { FailAbility("Неизвестная пассивная способность."); return; }
            if ((s.locationMask & 7) == 0 || s.isWaitingToDie || (s.tokenMask & 12) != 0 || !HasWeather(d.passiveWeatherToken)) return;
        }
        else if (item.kind == 2)
        {
            if (d.deathwishDamage == 0 && d.deathwishSpawnCount == 0 && d.deathwishSummonTemplate == 0) { FailAbility("Неизвестная предсмертная способность."); return; }
            if ((item.source.locationMask & 7) == 0 || (s.tokenMask & 4) != 0) return;
            // Graph uses FromPosition once the dead owner has left its active row.
            s = item.source;
        }
        else if (item.kind == 3)
        {
            eventMask = 1; if (item.banishedConsume) eventMask = 2;
            if (d.consumePassiveBoost == 0 || (d.consumePassiveEvents & eventMask) == 0)
            { FailAbility("Неизвестная реакция на поглощение."); return; }
            if ((s.locationMask & d.consumePassiveLocations) == 0 || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 12) != 0
                || s.positionPlayerId != item.cause.positionPlayerId) return;
        }
        else if (item.kind == 6 || item.kind == 7)
        {
            if (d.timerPeriod == 0 || (s.tokenMask & 4) != 0) return;
            if (item.kind == 6 && ((s.locationMask & 7) == 0 || s.isWaitingToDie || s.power.currentPower <= 0 || (s.tokenMask & 8) != 0)) return;
        }
        else if (item.kind == 4 || item.kind == 5)
        {
            attackerBoost = d.beforeConsumeAttackerBoost; if (item.kind == 5) attackerBoost = d.banishedConsumeAttackerBoost;
            if (attackerBoost <= 0 || (s.tokenMask & 12) != 0 || s.isWaitingToDie || s.power.currentPower <= 0) return;
            if (item.kind == 4 && (s.locationMask & 63) == 0) return;
            if (item.kind == 5 && s.locationMask != 512) return;
            sourceCard.StoreConsumeAttacker(item.cause.instanceId);
            consumeAttacker = registry.Find(sourceCard.ConsumeAttackerId()); if (!consumeAttacker) return;
        }
        else { FailAbility("Неизвестный тип события."); return; }
        oldId = visualSourceId; oldTemplate = visualTemplateId; oldSide = visualSide; oldRow = visualRow;
        SetVisualSource(s.instanceId, d.header.templateId, s.positionPlayerId, s.locationMask);
        if (item.kind == 6) QueueTimer(sourceCard, 0, 1);
        else if (item.kind == 7)
        {
            QueueTimer(sourceCard, 2, d.timerPeriod); ConsumeRight(sourceCard);
            BetaGwentLog("DUEL_VRAN_TIMER_TRIGGER card=" + s.instanceId + " reset=" + d.timerPeriod);
        }
        else if (item.kind == 4 || item.kind == 5)
        {
            RecordVisual(8, item.cause.instanceId, d.title + ": поглотитель усилен на " + attackerBoost, 420);
            QueuePower(consumeAttacker, attackerBoost, false);
            BetaGwentLog("DUEL_EGG_ATTACKER_BOOST egg=" + s.instanceId + " attacker=" + item.cause.instanceId
                + " amount=" + attackerBoost + " beforeDestroyed=" + (item.kind == 4));
        }
        else if (item.kind == 3)
        {
            // Hidden hand/deck reactions must not reveal an enemy card or its artwork.
            if ((s.locationMask & 7) != 0 || (s.positionPlayerId == 1 && s.locationMask == 8))
                RecordVisual(8, s.instanceId, d.title + ": +" + d.consumePassiveBoost + " при поглощении", 380);
            QueuePassivePower(sourceCard, d.consumePassiveBoost);
            BetaGwentLog("DUEL_PASSIVE_CONSUME card=" + s.instanceId + " source=" + item.cause.instanceId
                + " location=" + s.locationMask + " boost=" + d.consumePassiveBoost + " afterBanished=" + item.banishedConsume);
        }
        else if (item.kind == 1)
        {
            RecordVisual(8, s.instanceId, d.title + ": усиление в конце своего хода", 420);
            QueuePower(sourceCard, d.passiveBoost, false);
            BetaGwentLog("DUEL_PASSIVE_AFTER_TURN card=" + s.instanceId + " boost=" + d.passiveBoost);
        }
        else
        {
            RecordVisual(13, s.instanceId, d.title + ": Завещание", 450);
            if (d.deathwishSummonTemplate > 0) QueueDeckSummon(s, d.deathwishSummonTemplate);
            if (d.deathwishSpawnCount > 0)
            {
                spawnPosition = s; spawnPosition.locationIndex = -3;
                if (d.deathwishSpawnMode == 1) QueueRandomRowSpawn(spawnPosition, d.deathwishSpawnTemplate, d.deathwishSpawnCount);
                else QueueSpawn(spawnPosition, d.deathwishSpawnTemplate, d.deathwishSpawnCount);
            }
            if (d.deathwishDamage > 0) LocationCards(BetaGwentOpponentId(s.positionPlayerId), s.locationMask, targets);
            for (i = 0; i < targets.Size(); i += 1)
            {
                targetState = targets[i].Snapshot();
                if (targetState.runtimeTemplate.typeMask != 4 || targetState.isWaitingToDie || (targetState.tokenMask & d.deathwishIgnore) != 0) continue;
                QueuePower(targets[i], -d.deathwishDamage, false);
            }
            BetaGwentLog("DUEL_DEATHWISH card=" + s.instanceId + " fromSide=" + s.positionPlayerId
                + " row=" + s.locationMask + " damage=" + d.deathwishDamage + " spawn=" + d.deathwishSpawnCount + " summon=" + d.deathwishSummonTemplate);
        }
        FlushEffects(); SetVisualSource(oldId, oldTemplate, oldSide, oldRow);
    }
    public function MarkDeath(card : CBetaGwentDuelCard)
    {
        var s, other : SBetaGwentCardSnapshot; var i : int;
        s = card.Snapshot(); if (s.isWaitingToDie) return; card.SetWaiting(true);
        i = 0;
        while (i < dying.Size())
        {
            other = dying[i].Snapshot();
            if (s.locationMask > other.locationMask || (s.locationMask == other.locationMask && s.locationIndex > other.locationIndex)) break;
            i += 1;
        }
        dying.Insert(i, card);
    }
    private function TakeConsumeVisual(id : int) : bool
    {
        var i : int;
        for(i=pendingConsumeVisuals.Size()-1;i>=0;i-=1)
        { if(pendingConsumeVisuals[i]==id){pendingConsumeVisuals.Erase(i);return true;} }
        return false;
    }
    private function DrainDeaths(optional suppressAbilities : bool)
    {
        var batch : array<CBetaGwentDuelCard>; var fromPositions, killedPositions : array<SBetaGwentCardSnapshot>;
        var i, wave : int; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition; var consumed : bool;
        if (drainingDeaths || fatal) return; drainingDeaths = true;
        while (dying.Size() > 0 && !fatal && wave < 64)
        {
            batch.Clear(); fromPositions.Clear(); killedPositions.Clear();
            for (i = 0; i < dying.Size(); i += 1) { batch.PushBack(dying[i]); fromPositions.PushBack(dying[i].Snapshot()); }
            dying.Clear();
            // Move the whole ordered death batch before emitting Killed events.
            for (i = 0; i < batch.Size(); i += 1)
            {
                s = fromPositions[i];
                consumed = TakeConsumeVisual(s.instanceId);
                d = batch[i].Definition();
                if (s.runtimeTemplate.typeMask != 2 && s.power.basePower + s.power.permanentPower <= 0)
                {
                    // Original KillWaitingToDie banishes zero effective-base units instead of Kill.
                    batch[i].Move(s.positionPlayerId, 512, 0); batch[i].SetPlayable(false); batch[i].SetWaiting(false);
                    Reindex(s.positionPlayerId, s.locationMask);
                    if (!suppressAbilities && !consumed) RecordVisual(12, s.instanceId, d.title + ": изначальная сила исчерпана", 380);
                    BetaGwentLog("DUEL_BANISH_WEAKENED card=" + s.instanceId + " removalType=0 killed=false");
                    continue;
                }
                batch[i].lastActiveRow = s.locationMask; killedPositions.PushBack(s);
                if ((s.tokenMask & 512) != 0)
                {
                    // Void512, not SpawningPool128. Keep a non-reusable visual tombstone.
                    batch[i].Move(s.positionPlayerId, 512, 0); batch[i].SetPlayable(false);
                    Reindex(s.positionPlayerId, s.locationMask);
                    if (!suppressAbilities && !consumed) RecordVisual(3, s.instanceId, d.title + ": исчез", 320);
                    BetaGwentLog("DUEL_TOKEN_REMOVED card=" + s.instanceId + " location=512 grave=false");
                }
                else if (s.locationMask != 32)
                {
                    batch[i].Move(s.positionPlayerId, 32, CountLocation(s.positionPlayerId, 32)); batch[i].ResetInGraveyard();
                    Reindex(s.positionPlayerId, s.locationMask); if (!suppressAbilities && !consumed) RecordVisual(3, s.instanceId, d.title + ": в сброс", 320);
                }
                batch[i].SetWaiting(false); BetaGwentLog("DUEL_DEATH card=" + s.instanceId + " wave=" + wave);
            }
            if (!suppressAbilities)
            { for (i = 0; i < killedPositions.Size(); i += 1) { MonsterMoved(killedPositions[i]); events.NorthTrigger(7, killedPositions[i]); monsters.NilfTrigger(9,killedPositions[i]); } events.Killed(killedPositions); events.Flush(); }
            // Effect callbacks may have marked another batch, including another Rotfiend.
            wave += 1;
        }
        if (dying.Size() > 0 && !fatal) FailAbility("Превышен лимит цепной смерти.");
        drainingDeaths = false;
    }
    private function EndTurnWithEvents() : bool
    {
        var s : SBetaGwentMatchSnapshot;var cause : SBetaGwentCardSnapshot; s = match.Snapshot();
        if(nilfEndingTurn){nilfEndingTurn=false;mulliganReactions=false;return Require(match.ApplyTurnEnded());}
        events.BeforeTurnEnd(s.currentPlayerId);
        // Original TurnEndGameState does not emit AfterTurn when both players passed.
        if (!BetaGwentAllPlayersPassed(s.playerOne, s.playerTwo))
        { cause.positionPlayerId=s.currentPlayerId;monsters.NilfTrigger(6,cause);NorthTurn(2, s.currentPlayerId); events.AfterTurn(s.currentPlayerId); if (!events.Flush()) return false; DrainDeaths(); }
        if (fatal) return false;if(nilfJobs.Size()>0){nilfEndingTurn=true;if(NilfNextReaction())return false;nilfEndingTurn=false;mulliganReactions=false;} return Require(match.ApplyTurnEnded());
    }
    public function Pass(side : int) : bool
    {
        var cause : SBetaGwentCardSnapshot;
        if (!CanAct(side)) return false;
        if (!Require(match.ClaimInitialMove(side)) || !Require(match.ApplyPlayerPassed(side))) return false;
        SetVisualSource(0, 0, side, 0);
        message = "Вы спасовали."; if (side == 2) message = "Соперник спасовал.";
        cause.positionPlayerId=side;monsters.NilfTrigger(7,cause);FlushDeaths();RecordVisual(5, 0, message, 550); FinishTurn(); return !fatal;
    }
    private function FinishTurn()
    {
        var s : SBetaGwentMatchSnapshot;var rounds : array<SBetaGwentRoundResult>;var cause : SBetaGwentCardSnapshot; var next : int;
        if(mulliganReactions){mulliganReactions=false;return;}
        if (!EndTurnWithEvents()) return; s = match.Snapshot();
        if (BetaGwentAllPlayersPassed(s.playerOne, s.playerTwo))
        {
            Require(match.RecordRoundResult(Score(1), Score(2))); s = match.Snapshot(); waiting = s.matchWinnerMask == 0;match.GetRoundResults(rounds);cause.timerValue=rounds[rounds.Size()-1].winnerMask;monsters.NilfTrigger(14,cause);FlushDeaths();
            message = "Раунд: " + Score(1) + ":" + Score(2) + ".";
            if (s.matchWinnerMask == 1) message = "Вы победили! Счёт по раундам " + s.playerOne.crowns + ":" + s.playerTwo.crowns;
            else if (s.matchWinnerMask == 2) message = "Соперник победил. Счёт по раундам " + s.playerOne.crowns + ":" + s.playerTwo.crowns;
            else if (s.matchWinnerMask == 3) message = "Ничья.";
            SetVisualSource(0, 0, 0, 0); RecordVisual(6, 0, message, 1250);
            return;
        }
        next = BetaGwentOpponentId(s.currentPlayerId); Require(match.ApplyTurnStarted(next)); BeforeTurnWithEvents(next);
        if ((next == 1 && s.playerOne.hasPassed) || (next == 2 && s.playerTwo.hasPassed))
        { if (!EndTurnWithEvents()) return; Require(match.ApplyTurnStarted(BetaGwentOpponentId(next))); BeforeTurnWithEvents(BetaGwentOpponentId(next)); }
    }
    private function BestOwnRow(side : int) : int
    {
        var row, best, count, penalty, minimum : int; minimum = 2147483647;
        for (row = 1; row <= 4; row *= 2)
        {
            count = CountLocation(side,row);if(count>=9)continue;
            penalty=count*2+weather.Damage(side,row)*3;
            if(BetaGwentAIStrength()>=2){penalty=AiRowPlacementCost(side,row,aiPlacing)*2;}
            if(AiLanePower(side,row)>=25)penalty+=8;
            if(penalty<minimum){minimum=penalty;best=row;}
        }
        return best;
    }
    private function AiLanePower(side : int, row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var i,value : int;var s : SBetaGwentCardSnapshot;
        LocationCards(side,row,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();if(!s.isWaitingToDie)value+=s.power.currentPower;}
        return value;
    }
    private function AiSpawnValue(d : SBetaGwentDuelDefinition, side : int, row : int) : int
    {
        var token : SBetaGwentDuelDefinition;token=BetaGwentDuelDefinition(d.deploySpawnTemplate);
        return Min(d.deploySpawnCount,Max(0,8-CountLocation(side,row)))*token.header.power;
    }
    private function AiDuelTarget(source : CBetaGwentDuelCard, target : SBetaGwentCardSnapshot, immediate : bool) : int
    {
        var own : SBetaGwentCardSnapshot; var value : int; own=source.Snapshot();
        value=BetaGwentAIDuelSwing(own.power.currentPower,own.power.armor,target.power.currentPower,target.power.armor);
        if(!immediate && own.power.currentPower>=target.power.currentPower+target.power.armor)
            value+=AiEngineValue(target,own.positionPlayerId);
        return value;
    }
    private function AiDuelGain(source : CBetaGwentDuelCard, immediate : bool) : int
    {
        var i,best : int;var own,t : SBetaGwentCardSnapshot;own=source.Snapshot();best=-2147483647;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.positionPlayerId==own.positionPlayerId || (t.locationMask&7)==0 || t.isWaitingToDie || (t.tokenMask&264)!=0 || t.runtimeTemplate.typeMask!=4)continue;
            best=Max(best,AiDuelTarget(source,t,immediate));}
        if(best==-2147483647)return 0;return Max(0,best);
    }
    private function AiTimingReserve(card : CBetaGwentDuelCard, gain : int) : int
    {
        var d : SBetaGwentDuelDefinition;var s : SBetaGwentCardSnapshot;var useful : int;
        d=card.Definition();s=card.Snapshot();useful=gain-s.power.currentPower;
        // A reactive gold's body alone is not a reason to spend its ability.
        if(d.effect==34 && (d.specialMode==137 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132))
            return Max(0,8-useful)*2;
        if(d.header.tierMask==8 && d.effect==1)return Max(0,d.amount-useful);
        return 0;
    }
    private function AiManagedDeployValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int
    {
        var id,amount,enemy,value,i,count : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        id=d.header.templateId;enemy=BetaGwentOpponentId(side);
        if(d.effect!=34)return 0;
        if(d.specialMode==102)return Max(0,BestEffectValue(side,1,d.amount,2,d.header.templateId,immediate));
        if(id==162315 || id==162313){amount=5;if(id==162315)amount=12;return Max(0,BestEffectValue(side,2,amount,1));}
        if(id==162306)amount=5;else if(id==162308)amount=2;else if(id==152304)amount=3;
        else if(id==162209 || id==162310)amount=7;else if(id==152207)amount=6;else if(id==142103)amount=8;
        else if(id==200124)amount=NilfAlchemy(side);
        if(amount>0)return Max(0,BestEffectValue(side,1,amount,2,0,immediate));
        if(id==200159){
            LocationCards(side,16,cards);
            for(i=0;i<cards.Size() && count<3;i+=1){s=cards[i].Snapshot();
                if(s.runtimeTemplate.templateId==152209 || s.runtimeTemplate.templateId==152316){value+=s.power.currentPower+1;count+=1;}}
            return value;
        }
        if(id==200164 && side==2){
            LocationCards(side,16,cards);
            for(i=0;i<cards.Size() && i<3;i+=1){
                s=cards[i].Snapshot();if(s.isWaitingToDie)continue;
                if(s.runtimeTemplate.typeMask==4 && BestCardRow(side,cards[i].Definition())==0)continue;
                value=Max(value,AiCardTempo(cards[i],immediate,BestVranAnchor(side),AiPublicClearRisk()));
            }
            return value;
        }
        return 0;
    }
    private function AiDrawUtility(d : SBetaGwentDuelDefinition, side : int) : int
    {
        var m : SBetaGwentMatchSnapshot;var id : int;m=match.Snapshot();id=d.header.templateId;
        if(m.roundNumber>=3 || CountLocation(side,16)==0)return 0;
        if(id==162210 || id==142203 || id==152214 || id==132204)return 18;
        return 0;
    }
    // The horizon changes valuation, never the actual strength or damage.
    private function AiEngineValue(s : SBetaGwentCardSnapshot, side : int) : int
    {
        var d : SBetaGwentDuelDefinition;var value,horizon : int;
        if((s.tokenMask&4)!=0 || s.isWaitingToDie)return 0;
        d=BetaGwentDuelDefinition(s.runtimeTemplate.templateId);horizon=AiHorizon(side);
        if(d.timerPeriod>0)value+=horizon*2;
        if(d.consumePassiveBoost>0)value+=d.consumePassiveBoost*horizon;
        if(d.passiveBoost>0 && HasWeather(d.passiveWeatherToken))value+=d.passiveBoost*horizon;
        if(s.runtimeTemplate.templateId==162307 || s.runtimeTemplate.templateId==200040)value+=horizon*2;
        value=Max(value,archetypeAI.EngineThreat(s,horizon));return Min(12,value);
    }
    private function AiDamageChoice(s : SBetaGwentCardSnapshot, side : int, amount : int, optional immediate : bool) : int
    {
        var value,deathwish : int;var d,token : SBetaGwentDuelDefinition;
        value=DamageValue(s,side,amount);
        if(s.positionPlayerId==side || s.power.currentPower>Max(0,amount-s.power.armor))return value;
        d=BetaGwentDuelDefinition(s.runtimeTemplate.templateId);
        if(!immediate)value+=AiEngineValue(s,side);
        if((s.tokenMask&4)==0){
            if(d.deathwishSummonTemplate>0)deathwish+=DeckSummonValue(s.positionPlayerId,d.deathwishSummonTemplate);
            if(d.deathwishSpawnCount>0){token=BetaGwentDuelDefinition(d.deathwishSpawnTemplate);deathwish+=d.deathwishSpawnCount*token.header.power;}
            if(d.deathwishDamage>0)deathwish+=Max(0,RowEffectValue(s.positionPlayerId,side,s.locationMask,d.deathwishDamage));
        }
        return value-deathwish;
    }
    private function AiAbilityChoiceValue(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, kind : int) : int
    {
        var s,t : SBetaGwentCardSnapshot;var d,td : SBetaGwentDuelDefinition;
        var id,side,value,amount : int;
        s=source.Snapshot();t=target.Snapshot();side=NilfDecisionSide();
        if(t.locationMask==8 && t.positionPlayerId!=side && (t.tokenMask&64)==0)return 0;
        d=source.Definition();td=target.Definition();id=source.TemplateId();value=t.power.currentPower;
        if(kind==2){
            // Bran discards cards: choose cards that return themselves first,
            // then low-utility bronze, preserving gold and expensive tutors.
            if(id==200159){if(t.runtimeTemplate.templateId==152209 || t.runtimeTemplate.templateId==152316)return 100;
                return -value-AiReserveCost(td)*4;}
            if(BetaGwentDuelSpying(t.runtimeTemplate.templateId))value=-value+12;
            value+=AiManagedDeployValue(td,side)+archetypeAI.PileGain(td)+archetypeAI.PublicDeployGain(td);
            if(td.effect==1 || td.effect==2 || td.effect==17 || td.effect==19 || td.effect==25 || td.effect==27)
                value+=Max(0,BestEffectValue(side,td.effect,td.amount,td.targetSide,td.header.templateId));
            if(td.effect==28)value+=specials.Value(target);
            if(td.deploySummonTemplate>0)value+=DeckCopiesValue(side,td.deploySummonTemplate,BestCardRow(side,td),t.instanceId,td.deploySummonOtherTemplate,td.deploySummonIgnore,td.deploySummonLinked);
            if(td.deploySpawnCount>0)value+=AiSpawnValue(td,side,BestCardRow(side,td));
            return value+AiSetupBonus(td);
        }
        if((t.locationMask&7)==0)return value;
        if(d.effect==34 && d.specialMode==137)return AiDuelTarget(source,t,false);
        // Northern targeted damage and repeat shots.
        if(d.specialMode==102 || d.specialMode==117 || d.specialMode==118 || d.specialMode==143 || d.specialMode==144)
            return AiDamageChoice(t,side,d.amount);
        if(d.specialMode==114 || id==162204){
            value=t.power.basePower+t.power.permanentPower-t.power.currentPower;
            if(t.positionPlayerId!=side)value=-value;
            if(id==162204)value+=3;else value+=LockToggleValue(t,side);
            return value;
        }
        if(id==162208 || id==152204)return LockToggleValue(t,side);
        if(id==201644)return Max(0,t.power.basePower+t.power.permanentPower-t.power.currentPower)*2;
        // Known targeted damage amounts from the implemented Beta consumers.
        if(id==142103)amount=8;
        else if(id==162209 || id==162310)amount=7;
        else if(id==152207)amount=6;
        else if(id==162306)amount=5;
        else if(id==162308 || id==200028)amount=2;
        else if(id==152304)amount=3;
        else if(id==200124)amount=NilfAlchemy(side);
        else if(id==162305){amount=3;if((t.tokenMask&128)!=0)amount=6;}
        if(amount>0)return AiDamageChoice(t,side,amount);
        if(id==162313 || id==162315 || id==152311)return AiEngineValue(t,side)+Max(0,4-weather.Damage(t.positionPlayerId,t.locationMask));
        return value;
    }
    private function DamageValue(cardState : SBetaGwentCardSnapshot, side : int, amount : int) : int
    {
        var damage : int; damage = amount - cardState.power.armor;
        if (damage < 0) damage = 0;
        if (damage > cardState.power.currentPower) damage = cardState.power.currentPower;
        if (cardState.positionPlayerId == side) return -damage;
        return damage;
    }
    private function LockToggleValue(cardState : SBetaGwentCardSnapshot, side : int) : int
    {
        var d, tokenDefinition : SBetaGwentDuelDefinition; var value : int;
        if(AiHorizon(side)==0)return 0;
        d = BetaGwentDuelDefinition(cardState.runtimeTemplate.templateId);
        // Closed-deck heuristic: future passive/deathwish utility, never gameplay RNG.
        if (d.timerPeriod > 0) value += 5;
        if (d.consumePassiveBoost > 0) value += d.consumePassiveBoost * 3;
        if (d.passiveBoost > 0 && HasWeather(d.passiveWeatherToken)) value += d.passiveBoost * 3;
        if (cardState.runtimeTemplate.templateId == 132310 && weather.Token(BetaGwentOpponentId(cardState.positionPlayerId), cardState.locationMask) == 1) value += 3;
        value=Max(value,BetaGwentAIEngine(cardState.runtimeTemplate.templateId)*AiHorizon(side));
        if (d.deathwishDamage > 0) value += 2;
        if (d.deathwishSummonTemplate > 0) value += DeckSummonValue(cardState.positionPlayerId, d.deathwishSummonTemplate);
        if (d.deathwishSpawnCount > 0)
        { tokenDefinition = BetaGwentDuelDefinition(d.deathwishSpawnTemplate); value += d.deathwishSpawnCount * tokenDefinition.header.power; }
        if (cardState.positionPlayerId == side) value = -value;
        if ((cardState.tokenMask & 4) != 0) value = -value;
        return value;
    }
    private function TargetValue(cardState : SBetaGwentCardSnapshot, side : int, effect : int, amount : int, optional immediate : bool) : int
    {
        var i, value, offset : int; var other : SBetaGwentCardSnapshot; var d, tokenDefinition : SBetaGwentDuelDefinition;
        if (effect == 25)
        {
            value = DamageValue(cardState, side, amount); d = BetaGwentDuelDefinition(132309);
            if (cardState.power.currentPower <= Max(0, amount - cardState.power.armor)
                || weather.Token(cardState.positionPlayerId, cardState.locationMask) == d.conditionalWeatherToken) value += d.conditionalBoost;
            if(!immediate && weatherProfile && side==2)value+=weatherAI.KillBonus(cardState,amount);
            return value;
        }
        if (effect == 27)
        {
            d = BetaGwentDuelDefinition(132102);
            if ((weather.Token(cardState.positionPlayerId, cardState.locationMask) & d.conditionalWeatherToken) != 0) amount = d.conditionalDamage;
            if(!immediate && weatherProfile && side==2)return DamageValue(cardState,side,amount)+weatherAI.KillBonus(cardState,amount);
            return DamageValue(cardState, side, amount);
        }
        if (effect == 1 || effect == 6) return AiDamageChoice(cardState, side, amount, immediate);
        if (effect == 31)
        { value = Min(Max(0, amount - cardState.power.armor), Max(0, cardState.power.basePower + cardState.power.permanentPower));
          if (cardState.positionPlayerId == side) return -value; return value; }
        if (effect == 32)
        { value = cardState.power.currentPower / 2; if (cardState.positionPlayerId == side) return value; return -value; }
        if (effect == 20)
        {
            d = BetaGwentDuelDefinition(200053);
            if (!MatchesCardTarget(cardState, d)) return -2147483647;
            if (cardState.runtimeTemplate.templateId == d.transformTemplate) return 0;
            tokenDefinition = BetaGwentDuelDefinition(d.transformTemplate);
            value = cardState.power.currentPower - tokenDefinition.header.power;
            if (cardState.positionPlayerId == side) value = -value;
            if (!immediate && (cardState.tokenMask & 4) == 0) value += LockToggleValue(cardState, side);
            return value;
        }
        if (effect == 18 || effect == 19)
        {
            value = 0; if(!immediate)value = LockToggleValue(cardState, side);
            if (cardState.positionPlayerId != side)
            {
                if (effect == 18) value += cardState.power.currentPower - FloorF((float)cardState.power.currentPower * 0.5f);
                else value += DamageValue(cardState, side, amount);
            }
            return value;
        }
        if (effect == 17)
        {
            d = BetaGwentDuelDefinition(132306);
            if (!MatchesGraveConsume(cardState, side, d)) return -2147483647;
            // Banish removes a grave card; it does not score enemy death or replay deathwish.
            return cardState.power.currentPower + ConsumePassiveValue(side, 0);
        }
        if (effect == 16)
        {
            if (pendingCard) { other = pendingCard.Snapshot(); if (other.instanceId == cardState.instanceId) return -2147483647; }
            if (cardState.power.currentPower > amount) return -2147483647;
            d = BetaGwentDuelDefinition(cardState.runtimeTemplate.templateId);
            value = ConsumePassiveValue(side, cardState.instanceId);
            if ((cardState.tokenMask & 12) == 0) value += d.beforeConsumeAttackerBoost;
            if (cardState.positionPlayerId != side) value += cardState.power.currentPower * 2;
            if (d.deathwishSummonTemplate > 0 && (cardState.tokenMask & 4) == 0)
            {
                offset = DeckSummonValue(cardState.positionPlayerId, d.deathwishSummonTemplate);
                if (cardState.positionPlayerId == side) value += offset; else value -= offset;
            }
            if (d.deathwishSpawnCount > 0 && (cardState.tokenMask & 4) == 0)
            {
                tokenDefinition = BetaGwentDuelDefinition(d.deathwishSpawnTemplate);
                offset = Min(d.deathwishSpawnCount, Max(0, 10 - CountLocation(cardState.positionPlayerId, cardState.locationMask)));
                if (d.deathwishSpawnMode == 1) offset = d.deathwishSpawnCount;
                if (cardState.positionPlayerId == side) value += offset * tokenDefinition.header.power;
                else value -= offset * tokenDefinition.header.power;
            }
            if (d.deathwishDamage > 0 && (cardState.tokenMask & 4) == 0)
                value += RowEffectValue(side, BetaGwentOpponentId(cardState.positionPlayerId), cardState.locationMask, d.deathwishDamage);
            return value;
        }
        if (effect == 22)
        { if (cardState.positionPlayerId == side) return 0; return Min(cardState.power.currentPower, amount) * 2; }
        if (effect == 7)
        { if (cardState.positionPlayerId == side) return 0; return (cardState.power.currentPower / 2) * 2; }
        if (effect == 2) { if (cardState.positionPlayerId == side) return amount; return -amount; }
        if (effect == 3)
        {
            for (i = 0; i < live.Size(); i += 1)
            {
                other = live[i].Snapshot(); offset = other.locationIndex - cardState.locationIndex;
                if (other.positionPlayerId != cardState.positionPlayerId || other.locationMask != cardState.locationMask
                    || offset < -1 || offset > 1) continue;
                value += amount;
            }
            if (cardState.positionPlayerId != side) value = -value;
            return value;
        }
        return 0;
    }
    private function RowEffectValue(side : int, targetSide : int, row : int, amount : int) : int
    {
        var i, value : int; var cardState : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        {
            cardState = live[i].Snapshot();
            if (cardState.positionPlayerId == targetSide && cardState.locationMask == row)
                value += DamageValue(cardState, side, amount);
        }
        return value;
    }
    private function BestEnemyRow(side : int) : int
    {
        var row, best, value, maximum : int; best = 1; maximum = -1;
        for (row = 1; row <= 4; row *= 2)
        { value = RowEffectValue(side, BetaGwentOpponentId(side), row, 3); if (value > maximum) { maximum = value; best = row; } }
        return best;
    }
    private function BestTarget(side : int, effect : int, amount : int) : int
    {
        var i, best, value, maximum : int; var c : CBetaGwentDuelCard; var cardState : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        maximum = -2147483647;
        if (effect == 6) amount = CountLocation(side, 8);
        if (effect == 16 && pendingCard) { d = pendingCard.Definition(); amount = d.consumeMaximum; }
        for (i = 0; i < pendingIds.Size(); i += 1)
        {
            c = registry.Find(pendingIds[i]); cardState = c.Snapshot(); value = TargetValue(cardState, side, effect, amount);
            if(effect==1 || effect==6)value=AiDamageChoice(cardState,side,amount);
            if (effect == 28 && pendingCard) { d = pendingCard.Definition(); value = specials.TargetValue(d, cardState, side); }
            if (value > maximum) { maximum = value; best = cardState.instanceId; }
        }
        if ((effect == 3 || effect == 6 || effect == 7 || effect == 16 || effect == 17 || effect == 18 || effect == 22) && maximum <= 0) return 0;
        if (effect == 28 && pendingCard) { d = pendingCard.Definition(); if (d.targetMinimum == 0 && maximum <= 0) return 0; }
        return best;
    }
    private function BestEffectValue(side : int, effect : int, amount : int, optional targetSide : int, optional definitionId : int, optional immediate : bool) : int
    {
        var i, value, maximum : int; var cardState : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        maximum = -2147483647; if (effect == 17) d = BetaGwentDuelDefinition(132306);
        if (effect == 22) d = BetaGwentDuelDefinition(132313);
        if (effect == 20) d = BetaGwentDuelDefinition(200053);
        if (definitionId != 0) d = BetaGwentDuelDefinition(definitionId);
        for (i = 0; i < live.Size(); i += 1)
        {
            cardState = live[i].Snapshot();
            if ((cardState.runtimeTemplate.factionMask & d.targetExcludedFaction) != 0) continue;
            if (effect == 17) { if (!MatchesGraveConsume(cardState, side, d)) continue; }
            else if (effect == 20 || effect == 22) { if (!MatchesCardTarget(cardState, d)) continue; }
            else
            {
                if ((cardState.locationMask & 7) == 0 || cardState.isWaitingToDie) continue;
                if (effect == 18 || effect == 19) { if ((cardState.tokenMask & 256) != 0) continue; }
                else if ((cardState.tokenMask & 264) != 0) continue;
            }
            if (targetSide == 2 && cardState.positionPlayerId != BetaGwentOpponentId(side)) continue;
            if (targetSide == 1 && cardState.positionPlayerId != side) continue;
            value = TargetValue(cardState, side, effect, amount, immediate); if (value > maximum) maximum = value;
        }
        return maximum;
    }
    private function EpidemicValue(side : int) : int
    {
        var i, lowest, value : int; var cardState : SBetaGwentCardSnapshot;
        lowest = 2147483647;
        for (i = 0; i < live.Size(); i += 1)
        { cardState = live[i].Snapshot(); if ((cardState.locationMask & 7) != 0 && cardState.power.currentPower < lowest) lowest = cardState.power.currentPower; }
        for (i = 0; i < live.Size(); i += 1)
        {
            cardState = live[i].Snapshot(); if ((cardState.locationMask & 7) == 0 || cardState.power.currentPower != lowest) continue;
            if (cardState.positionPlayerId == side) value -= lowest; else value += lowest;
        }
        return value;
    }
    private function BestVranAnchor(side : int) : int
    {
        var i, best, value, maximum : int; var s : SBetaGwentCardSnapshot;
        maximum = 0;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (s.positionPlayerId != side || (s.locationMask & 7) == 0 || s.runtimeTemplate.typeMask != 4
                || s.isWaitingToDie || s.power.currentPower <= 0 || CountLocation(side, s.locationMask) >= 9) continue;
            // Heuristic only; the actual right-neighbour graph has no Kayran power cap.
            value = TargetValue(s, side, 16, 2147483647);
            if (value > maximum) { maximum = value; best = s.instanceId; }
        }
        return best;
    }
    // Tempo is the immediate score swing; forecasts only rank normal turns.
    // This reads snapshots and own/public zones, never executes a play or RNG.
    private function AiCardTempo(card : CBetaGwentDuelCard, immediate : bool, vranAnchor : int, clearRisk : int) : int
    {
        var s,vranTarget : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var d : SBetaGwentDuelDefinition;var value,effectValue,row : int;
        s=card.Snapshot();m=match.Snapshot();
        d = card.Definition(); value = s.power.currentPower;
        if(BetaGwentDuelSpying(d.header.templateId))value=-value;
        value+=AiManagedDeployValue(d,2,immediate);
        if(d.effect==34 && d.specialMode==137)value+=AiDuelGain(card,immediate);
        value+=archetypeAI.PileGain(d,immediate);
        value+=archetypeAI.PublicDeployGain(d);
        if (d.effect == 1 || d.effect == 2 || d.effect == 3 || d.effect == 6 || d.effect == 16 || d.effect == 17 || d.effect == 18 || d.effect == 19 || d.effect == 20 || d.effect == 22 || d.effect == 25 || d.effect == 27)
        {
            effectValue = d.amount; if (d.effect == 16) effectValue = d.consumeMaximum;
            if (d.effect == 6) effectValue = CountLocation(2, 8) - 1;
            effectValue = BestEffectValue(2, d.effect, effectValue, d.targetSide, d.header.templateId, immediate);
            if (effectValue == -2147483647)
            {
                if (d.effect == 1 && d.header.typeMask == 4 && d.targetSide == 0 && d.targetExcludedFaction == 0) effectValue = -d.amount;
                else effectValue = 0;
            }
            if ((d.effect == 3 || d.effect == 6 || d.effect == 16 || d.effect == 17 || d.effect == 18) && effectValue < 0) effectValue = 0;
            value += effectValue;
        }
        if (d.deploySpawnCount > 0)
        {
            row = BestCardRow(2, d);
            value += AiSpawnValue(d,2,row);
        }
        if (d.deploySummonTemplate > 0) value += DeckCopiesValue(2, d.deploySummonTemplate, BestCardRow(2, d), s.instanceId, d.deploySummonOtherTemplate, d.deploySummonIgnore, d.deploySummonLinked);
        if (d.effect == 28) value += specials.Value(card);
        if (d.effect == 33) value += ModeValue(d, BestModeChoice(d, 2), 2);
        if (d.effect == 4) value += RowEffectValue(2, 1, BestEnemyRow(2), d.amount);
        if (d.effect == 5) value += EpidemicValue(2);
        if (!immediate && d.weatherToken != 0) value += WeatherValue(2, BestWeatherRow(2, d.weatherToken), d.weatherToken) * (100 - clearRisk / 2) / 100;
        if (d.effect == 9) {
            if(immediate){if(ChooseFirstLight(2)==113401)value+=weather.ClearValue(2,d.amount,true);else value+=RallyValue(2,true);}
            else value+=Max(weather.ClearValue(2,d.amount),RallyValue(2));
        }
        if (!immediate && d.effect == 14 && HasDeckTemplate(2, d.playTemplateId)) value += WeatherValue(2, BestWeatherRow(2, 1), 1);
        if (!immediate && d.effect == 15) value += weather.Damage(2, BestDeployRow(2, d.effect)) * AiHorizon(2);
        if (!immediate && d.timerPeriod > 0 && !m.playerOne.hasPassed)
        {
            value += 2;
            if (vranAnchor != 0) { vranTarget = FindCard(vranAnchor).Snapshot(); value += Max(0, TargetValue(vranTarget, 2, 16, 2147483647)); }
        }
        if (!immediate && d.passiveBoost != 0 && HasWeather(d.passiveWeatherToken)) value += d.passiveBoost * AiHorizon(2);
        if (!immediate && d.deathwishDamage != 0 && !m.playerOne.hasPassed) value += Max(0, RowEffectValue(2, 1, BestCardRow(2, d), d.deathwishDamage)) / 2;
        if (!immediate && d.deathwishSummonTemplate > 0 && !m.playerOne.hasPassed) value += DeckSummonValue(2, d.deathwishSummonTemplate) / 2;
        if(weatherProfile)value=weatherAI.Gain(d,s.power.currentPower,false,s.locationMask==8,immediate);
        return value;
    }
    // Exact immediate tempo of playing this card now (row as chosen by BestCardRow).
    // Implemented by the simulation clone; -2147483647 when unavailable.
    // ---- Generation 3/4 lookahead on cloned sessions (own cards only; the opponent's
    // hidden hand and deck are never read by these evaluations).
    public function AiSimClone() : CBetaGwentDuelSession
    {
        var cloner : CBetaGwentCloner; var g : CBetaGwentDuelSession;
        aiCloneEpoch += 1; cloner = new CBetaGwentCloner in this;
        g = cloner.CloneSession(this, aiCloneEpoch);
        if (!g) return NULL;
        g.aiSimulating = true; g.recordVisuals = false; g.random.Initialize(RandRange(2147483647));
        g.aiSimCloner = cloner;
        return g;
    }
    // Plays `id` for side 2 on this session (normally a clone) and returns the score swing.
    public function AiSimPlay(id : int) : int
    {
        var card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var before, row, anchor : int; var ok : bool;
        card = FindCard(id); if (!card) return -2147483647;
        s = card.Snapshot(); d = card.Definition(); before = Score(2) - Score(1) + AiSimBanked();
        if (s.locationMask == 64) ok = UseLeader(2);
        else
        {
            if (s.locationMask != 8 || !s.canBePlayed) return -2147483647;
            row = BestCardRow(2, d); if (row == 0) row = 1;
            if (d.effect == 23) anchor = BestVranAnchor(2);
            if (anchor == 0) anchor = archetypeAI.PlacementAnchor(d);
            if (anchor != 0) ok = PlayBefore(2, id, anchor); else ok = Play(2, id, row);
        }
        if (!ok || fatal || IsPending()) return -2147483647;
        return Score(2) - Score(1) + AiSimBanked() - before;
    }
    // Value side 2 banked outside the score: boosts on units in hand (full) and deck
    // (half), and face-down ambushes on the board (their power is revealed later).
    private function AiSimBanked() : int
    {
        var i, total : int; var t : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot(); if (t.positionPlayerId != 2 || t.isWaitingToDie) continue;
            if (t.locationMask == 8 && t.runtimeTemplate.typeMask == 4) total += t.power.currentPower - t.power.basePower;
            else if (t.locationMask == 16 && t.runtimeTemplate.typeMask == 4) total += (t.power.currentPower - t.power.basePower) / 2;
            else if ((t.locationMask & 7) != 0 && (t.tokenMask & 8) != 0) total += t.power.currentPower;
        }
        return total;
    }
    // Real decision time measured by the UI (synchronous native call). Slow machines
    // simulate fewer candidates; the cap recovers when decisions become fast again.
    public function AiPerfFeedback(ms : int)
    {
        if (ms > 2500) aiSimDamp = Min(70, aiSimDamp + 25);
        else if (ms < 900) aiSimDamp = Max(0, aiSimDamp - 10);
        BetaGwentLog("AI_PERF ms=" + ms + " damp=" + aiSimDamp);
    }
    private function AiSimCap(tune : int) : int
    { return Max(2, BetaGwentAITune(tune) * (100 - aiSimDamp) / 100); }
    // Opponent "does nothing" in a simulation: end its turn so side 2 acts again.
    public function AiSimSkipTurn() : bool
    {
        var m : SBetaGwentMatchSnapshot;
        if (!aiSimulating) return false;
        m = match.Snapshot(); if (m.currentPlayerId != 1 || !m.turnActive) return false;
        FinishTurn(); m = match.Snapshot();
        return !fatal && !IsPending() && m.currentPlayerId == 2 && m.turnActive;
    }
    public function AiExactTempo(card : CBetaGwentDuelCard) : int
    {
        var g : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot; var result : int;
        if (aiSimulating || !card) return -2147483647;
        BetaGwentAISimEnter();
        s = card.Snapshot(); g = AiSimClone(); result = -2147483647;
        if (g) result = g.AiSimPlay(s.instanceId);
        BetaGwentAISimLeave();
        return result;
    }
    // Generation 4: how much better our other cards become after playing `card` first
    // (setup before payoff). Compares exact follow-up plays with their exact value now.
    public function AiSequenceUplift(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>) : int
    {
        var result : int;
        if (aiSimulating || !card) return 0;
        BetaGwentAISimEnter(); result = AiSequenceUpliftInner(card, ids, values); BetaGwentAISimLeave();
        return result;
    }
    private function AiSequenceUpliftInner(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>) : int
    {
        var g, h : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot; var i, best, after, first : int;
        if (aiSimulating || !card) return 0;
        s = card.Snapshot(); g = AiSimClone(); if (!g) return 0;
        first = g.AiSimPlay(s.instanceId); if (first == -2147483647) return 0;
        if (!g.AiSimSkipTurn()) return 0;
        for (i = 0; i < ids.Size() && i < BetaGwentAITune(7); i += 1)
        {
            if (ids[i] == s.instanceId || values[i] == -2147483647) continue;
            h = g.AiSimClone(); if (!h) continue;
            after = h.AiSimPlay(ids[i]); if (after == -2147483647) continue;
            best = Max(best, after - values[i]);
        }
        return best;
    }
    public function OpponentStep() : bool
    {
        var i, best, value, maximum, row, effectValue, vranAnchor, reserve, deficit, catchBest, catchCost, cost, bestGain, bestUtility, tempo, clearRisk : int;
        var s, vranTarget : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var d : SBetaGwentDuelDefinition;
        var leaderCard : CBetaGwentDuelCard;
        var actions : array<SBetaGwentAIChaseAction>;var action : SBetaGwentAIChaseAction;
        var plan : SBetaGwentAIChasePlan;var planner : CBetaGwentAIChasePlanner;
        var ownHand, enemyHand, spent, reason, burst, leaderBurst, highest, burn, total, biggest, lane : int;
        var earlyState : SBetaGwentCardSnapshot; var bestTempoAll, roundDecision, exact, j, leaderExact : int;
        var simIds, simOrder, exactIds, exactValues, upliftIds, upliftValues : array<int>;
        if (!CanAct(2)) return false; m = match.Snapshot();archetypeAI.Refresh();
        if(archetypeAI.DryPass()){BetaGwentLog("DUEL_AI_PASS reason=save_long_deciding_round profile="+archetypeAI.ProfileId());return Pass(2);}
        if (m.playerOne.hasPassed && Score(2) > Score(1)) return Pass(2);
        ownHand=CountLocation(2,8);enemyHand=CountLocation(1,8);
        if(m.playerOne.hasPassed && Score(2)==Score(1) && m.playerOne.crowns==0)
        { BetaGwentLog("DUEL_AI_PASS reason=accept_tie");return Pass(2); }
        if(m.playerOne.hasPassed && aiChaseRound!=m.roundNumber){aiChaseRound=m.roundNumber;aiChaseInitialHand=ownHand;}
        spent=Max(0,aiChaseInitialHand-ownHand);
        maximum = -2147483647; catchCost = 2147483647; deficit = Max(1, Score(1) - Score(2) + 1);
        row = BestOwnRow(2); vranAnchor = BestVranAnchor(2); clearRisk = AiPublicClearRisk();
        // Learn a conservative tempo envelope from visible score changes.
        // Keep the estimate across rounds; no hidden hand/deck templates.
        if(aiObservedRound==m.roundNumber)aiPublicTempo=Max(aiPublicTempo,Min(40,Max(0,Score(1)-aiObservedEnemyScore)));
        aiObservedRound=m.roundNumber;aiObservedEnemyScore=Score(1);
        burst=Max(14,aiPublicTempo);highest=0;burn=0;
        for(lane=1;lane<=4;lane*=2)
        {
            total=0;biggest=0;
            for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
                if(earlyState.positionPlayerId!=2 || earlyState.locationMask!=lane || (earlyState.tokenMask&8)!=0)continue;
                total+=earlyState.power.currentPower;biggest=Max(biggest,earlyState.power.currentPower);
                highest=Max(highest,earlyState.power.currentPower);}
            if(total>=25){value=0;for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
                if(earlyState.positionPlayerId==2 && earlyState.locationMask==lane && earlyState.power.currentPower==biggest && (earlyState.tokenMask&8)==0)value+=biggest;}
                burst=Max(burst,value+5);}
            burst=Max(burst,CountLocation(2,lane)*3);
        }
        for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
            if(earlyState.positionPlayerId==2 && (earlyState.locationMask&7)!=0 && earlyState.power.currentPower==highest && (earlyState.tokenMask&8)==0)burn+=highest;}
        burst=Max(burst,burn);leaderBurst=0;if(LeaderAvailable(1))leaderBurst=20;
        if(!m.playerOne.hasPassed && BetaGwentAIEarlyPass(Score(2)-Score(1),burst,leaderBurst,ownHand,enemyHand,m.playerOne.crowns))
        { BetaGwentLog("DUEL_AI_PASS reason=force_multiple_replies burst="+burst+" leaderBurst="+leaderBurst+" ownHand="+ownHand+" enemyHand="+enemyHand);return Pass(2); }
        // Generation 3: simulate the most promising plays on a cloned session and use the
        // exact immediate result instead of the heuristic estimate (own cards only).
        if(BetaGwentAIStrength()>=3)
        {
            for(i=0;i<live.Size();i+=1)
            {
                s=live[i].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || !s.canBePlayed)continue;
                d=live[i].Definition();if(d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
                value=AiCardTempo(live[i],false,vranAnchor,clearRisk)*10-AiReserveCost(d)*4+archetypeAI.Priority(d)*10;
                j=0;while(j<simOrder.Size() && simOrder[j]>=value)j+=1;
                simOrder.Insert(j,value);simIds.Insert(j,i);
            }
            for(j=0;j<simIds.Size() && j<AiSimCap(5);j+=1)
            {
                exact=AiExactTempo(live[simIds[j]]);s=live[simIds[j]].Snapshot();
                exactIds.PushBack(s.instanceId);exactValues.PushBack(exact);
            }
            if(BetaGwentAIStrength()>=4 && !m.playerOne.hasPassed && CountLocation(2,8)>=2)
                for(j=0;j<simIds.Size() && j<AiSimCap(9);j+=1)
                {
                    s=live[simIds[j]].Snapshot();upliftIds.PushBack(s.instanceId);
                    upliftValues.PushBack(AiSequenceUplift(live[simIds[j]],exactIds,exactValues));
                }
        }
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId != 2 || s.locationMask != 8 || !s.canBePlayed) continue;
            d=live[i].Definition();
            if(d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
            value=AiCardTempo(live[i],false,vranAnchor,clearRisk);
            tempo=AiCardTempo(live[i],true,vranAnchor,clearRisk);
            for(j=0;j<exactIds.Size();j+=1)if(exactIds[j]==s.instanceId && exactValues[j]!=-2147483647){value+=exactValues[j]-tempo;tempo=exactValues[j];}
            for(j=0;j<upliftIds.Size();j+=1)if(upliftIds[j]==s.instanceId)value+=upliftValues[j]*BetaGwentAITune(8)/10;
            reserve = AiReserveCost(d)+AiTimingReserve(live[i],value);
            if(weatherProfile && (d.header.templateId==112102 || d.header.templateId==200218 || d.header.templateId==132104) && value<=s.power.currentPower+3 && m.roundNumber<3)reserve+=6;
            action.id=s.instanceId;action.gain=tempo;action.cards=1;action.reserve=reserve;actions.PushBack(action);
            bestTempoAll=Max(bestTempoAll,tempo);
            if (m.playerOne.hasPassed && tempo >= deficit)
            {
                cost = reserve * 10 + Max(0, tempo - deficit);
                if (cost < catchCost) { catchCost = cost; catchBest = s.instanceId; }
            }
            effectValue = (value+AiDrawUtility(d,2)) * 10 + AiSetupBonus(d) * 10 - reserve * 4;
            effectValue+=archetypeAI.Priority(d)*10;
            effectValue+=BetaGwentAITrainingBias(presetTwo,d,m.roundNumber,ownHand,Score(2)-Score(1),m.playerOne.hasPassed,tempo,value,reserve,archetypeAI.Priority(d));
            if(weatherProfile)effectValue+=weatherAI.Setup(d)*10;
            if (effectValue > maximum) { maximum = effectValue; bestGain = tempo; bestUtility=value+AiDrawUtility(d,2); best = s.instanceId; }
        }
        if (catchBest != 0)
        {
            best = catchBest;
            BetaGwentLog("DUEL_AI_CATCHUP card=" + best + " deficit=" + deficit + " cost=" + catchCost + " publicClearRisk=" + clearRisk);
        }
        if(!m.playerOne.hasPassed && BetaGwentAIConcedeOptionalRound(Score(1)-Score(2),bestGain,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns))
        {BetaGwentLog("DUEL_AI_PASS reason=preserve_deciding_hand deficit="+deficit+" tempo="+bestGain+" ownHand="+ownHand+" enemyHand="+enemyHand);return Pass(2);}
        if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed)
        {
            roundDecision=BetaGwentAIRoundDecision(m.roundNumber,m.playerTwo.crowns,m.playerOne.crowns,Score(2)-Score(1),ownHand,enemyHand,
                bestTempoAll,BetaGwentAICardValue(Score(1),aiRoundHandOne-enemyHand),LeaderAvailable(1));
            if(roundDecision!=0)
            {
                BetaGwentLog("DUEL_AI_PASS reason=round_economy"+roundDecision+" lead="+(Score(2)-Score(1))+" ownHand="+ownHand+" enemyHand="+enemyHand+" best="+bestTempoAll);
                return Pass(2);
            }
        }
        leaderCard = Leader(2);
        if (leaderCard && BestOwnRow(2) != 0)
        {
            d = leaderCard.Definition();
            s = leaderCard.Snapshot(); value = AiCardTempo(leaderCard,false,vranAnchor,clearRisk);
            value+=archetypeAI.LeaderGain(d);
            if(weatherProfile)value=weatherAI.Gain(d,s.power.currentPower);
            if (d.effect == 24) value += Max(WeatherValue(2, BestWeatherRow(2, 2), 2), WeatherValue(2, BestWeatherRow(2, 4), 4));
            leaderExact=-2147483647;
            if(BetaGwentAIStrength()>=3)
            {
                leaderExact=AiExactTempo(leaderCard);
                if(leaderExact!=-2147483647)value+=leaderExact-(AiCardTempo(leaderCard,true,vranAnchor,clearRisk)+archetypeAI.LeaderGain(d));
            }
            cost = BetaGwentAILeaderReserve(m.roundNumber);
            // Preserve a once-per-match leader unless its actual ability has
            // useful targets, it sets up the deck, or no hand play is left.
            reserve=cost+AiTimingReserve(leaderCard,value);
            if(m.roundNumber<3 && value<=s.power.currentPower+2 && archetypeAI.LeaderPriority(d)<=0 && ownHand>0)reserve+=12;
            if (catchBest == 0 && BetaGwentAILeaderUseful(d.header.templateId,m.roundNumber,ownHand,s.power.currentPower,value,archetypeAI.LeaderPriority(d),false,deficit) && value * 10 - reserve * 10 + archetypeAI.LeaderPriority(d)*10 + BetaGwentAITrainingBias(presetTwo,d,m.roundNumber,ownHand,Score(2)-Score(1),m.playerOne.hasPassed,value,value,reserve,archetypeAI.LeaderPriority(d)) > maximum && !m.playerOne.hasPassed) {BetaGwentLog("DUEL_AI_LEADER template="+d.header.templateId+" gain="+value+" body="+s.power.currentPower+" reserve="+reserve+" setup="+archetypeAI.LeaderPriority(d)+" reason=useful95");return UseLeader(2);}
            tempo=AiCardTempo(leaderCard,true,vranAnchor,clearRisk)+archetypeAI.LeaderGain(d);
            if(leaderExact!=-2147483647)tempo=leaderExact;
            if(BetaGwentAILeaderUseful(d.header.templateId,m.roundNumber,ownHand,s.power.currentPower,tempo,0,m.playerOne.hasPassed,deficit)){
                action.id=-1;action.gain=tempo;action.cards=0;action.reserve=cost;
                // Generation 2+: the leader is a strong once-per-match card, not a free answer.
                // Before the deciding round it costs like a hand card plus its reserve.
                if(BetaGwentAIStrength()>=2 && m.roundNumber<3){action.cards=1;action.reserve=cost+6;}
                actions.PushBack(action);
            }
        }
        if(m.playerOne.hasPassed)
        {
            planner=new CBetaGwentAIChasePlanner in this;plan=planner.Plan(actions,deficit);
            reason=BetaGwentAIChasePassReason(plan.reachable,plan.cards,spent,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns);
            BetaGwentLog("DUEL_AI_CHASE round="+m.roundNumber+" deficit="+deficit+" reachable="+plan.reachable+" needed="+plan.cards+" actions="+plan.actions+" spent="+spent+" ownHand="+ownHand+" enemyHand="+enemyHand+" passReason="+reason);
            if(reason!=0)return Pass(2);
            // A hand card that alone covers the deficit beats spending the once-per-match leader.
            if(plan.firstId==-1 && catchBest!=0 && m.roundNumber<3)plan.firstId=catchBest;
            if(plan.firstId==-1)return UseLeader(2);
            best=plan.firstId;catchBest=best;
            for(i=0;i<actions.Size();i+=1)if(actions[i].id==best)bestGain=actions[i].gain;
        }
        // A low ordering score is a reason to save a gold, not to pass away a
        // mandatory round. If every remaining card is reactive, still play
        // the least wasteful legal body rather than concede by score cutoff.
        if (best != 0)
        {
            d = registry.Find(best).Definition();
            BetaGwentLog("DUEL_AI_TACTIC card=" + best + " gain=" + bestGain + " evaluation=" + maximum
                + " horizon=" + AiHorizon(2) + " publicClearRisk=" + clearRisk + " weather="+weatherProfile+" profile="+archetypeAI.ProfileId()+" order="+archetypeAI.Priority(d)+" planner=tempo94");
            if (d.effect == 23 && vranAnchor != 0) return PlayBefore(2, best, vranAnchor);
            vranAnchor=archetypeAI.PlacementAnchor(d);if(vranAnchor!=0)return PlayBefore(2,best,vranAnchor);
            row = BestCardRow(2, d);
            if (row == 0) row = 1; return Play(2, best, row);
        }
        // Only use the emergency leader when there is no legal hand play.
        if (!m.playerOne.hasPassed && best==0 && ownHand==0 && LeaderAvailable(2) && BestOwnRow(2) != 0) {BetaGwentLog("DUEL_AI_LEADER reason=empty_hand95");return UseLeader(2);}
        BetaGwentLog("DUEL_AI_PASS reason=no_legal_hand_or_useful_chase hand="+ownHand);
        return Pass(2);
    }
    public function PumpOpponent()
    {
        var budget : int; var s : SBetaGwentMatchSnapshot;
        while (budget < 64 && !fatal && !waiting && !IsPending())
        {
            s = match.Snapshot(); if (s.matchWinnerMask != 0) return;
            if (s.currentPlayerId == 1)
            {
                if (CountLocation(1, 8) == 0 && !LeaderAvailable(1)) { Pass(1); budget += 1; continue; }
                return;
            }
            if (!OpponentStep()) return; budget += 1;
        }
    }
    public function BeginNextRound() : bool
    {
        var history : array<SBetaGwentRoundResult>; var s : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var i, starter : int;
        if (!waiting || fatal || IsPending()) return false; match.GetRoundResults(history);
        if (history.Size() == 0) return false;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if ((s.locationMask & 7) == 0) continue;
            if ((s.tokenMask & 1) == 0) MarkDeath(live[i]);
            else
            {
                QueueResilienceToggle(NULL, live[i]);
                // Original ClearBoard compares current against BASE (not base + permanent).
                if (s.power.currentPower > s.power.basePower) QueueResetPower(NULL, live[i]);
                if (s.power.armor > 0) QueueArmor(live[i], -s.power.armor);
            }
        }
        if (!FlushEffects()) return false;
        // ClearBoard is cleanup, not a normal Killed/Deathwish event.
        DrainDeaths(true); if (fatal) return false; starter = BetaGwentNextStartingPlayer(history[history.Size() - 1]);
        weather.Reset();
        SetVisualSource(0, 0, 0, 0); RecordVisual(17, 0, "Следующий раунд · Стойкие отряды остаются", 850);
        if (!Require(match.ApplyRoundStarted(starter))) return false; m = match.Snapshot();monsters.NilfTrigger(15,s);FlushDeaths();
        for (i = 0; i < live.Size(); i += 1) if (live[i].TemplateId() == 112207) live[i].monsterOnce = 0;
        if (m.roundNumber == 2) { Draw(1, 2); Draw(2, 2); }
        else { Draw(1, 1); Draw(2, 1); }
        waiting = false; BeginMulligan(starter, 1);
        return !fatal;
    }
}

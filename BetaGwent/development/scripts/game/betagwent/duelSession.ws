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
    // Stand/controller hook. Zero preserves the shipped human1/internal-AI2
    // behavior. External policies must supply every decision for selected seats.
    public var externalPolicyMask, mulliganSide : int;
    public var blacklistedTemplates, reservedCards : array<int>;
    public var visualFrames : array<CBetaGwentDuelVisualFrame>;
    public var recordVisuals, visualOverflow : bool;
    public var visualSourceId, visualTemplateId, visualSide, visualRow : int;
    public var visualAttack : int;
    public var visualAttackTargets : array<int>;
    public var presetOne, presetTwo : int;
    public var leaderTemplateOne, leaderTemplateTwo : int;
    // Highest difficulty: announced starting lists, captured before shuffle.
    // Never refreshed from the hidden hand or remaining draw pile.
    public var aiStartingDeckOne, aiStartingDeckTwo : array<int>;
    public var nilfJobs : array<CBetaGwentNilfReaction>;
    public var nilfJob : CBetaGwentNilfReaction;
    public var nilfEndingTurn : bool;
    public var mulliganReactions : bool;
    public var nilfInitialOne, nilfInitialTwo : array<int>;
    public var nilfSpellOne, nilfSpellTwo, nilfLastMovedUnit : int;
    public var weatherAI : CBetaGwentWeatherAI;
    public var weatherProfile : bool;
    public var archetypeAI : CBetaGwentArchetypeAI;
    public var aiChaseRound, aiChaseInitialHand, aiChaseSpent : int;
    public var aiObservedRound, aiObservedEnemyScore, aiPublicTempo : int;
    public var aiEnemyRowPlays : array<int>; // public: rows (1,2,4) the opponent placed its own units in
    public var aiRoundHandOne, aiRoundHandTwo : int;
    public var aiPlacing : SBetaGwentDuelDefinition;
    public var aiSimulating : bool; public var aiNeighbourProbeActive : bool;
    public var aiSpySlotRevision : string;
    public var aiSpySlotKeys, aiSpySlotRows, aiSpySlotIndices, aiSpySlotGains : array<int>; public var aiCloneEpoch : int; public var aiSimCloner : CBetaGwentCloner;
    public var aiSimDamp : int;
    // 094b measurement only: never set by the game. The JS bench can let the
    // ordinary Hard search see real hidden cards to estimate the ceiling of
    // hidden information. Classic and its profiles are unaffected.
    public var aiOpenInfoBench : bool;
    public var aiDecisionSerial : int;
    public var aiStrategyJob096 : CBetaGwentStrategyResourceJob096;
    public var aiPreparationEndgameJob097 : CBetaGwentAIEndgame097;
    public var aiEndgameReady097, aiEndgameComplete097 : bool;
    public var aiEndgameId097, aiEndgameValue097, aiEndgameNodes097 : int;
    public var aiEndgameRevision097 : string;
    public var aiStrategyIds096, aiStrategyPenalties096 : array<int>;
    public var aiStrategyRevision096 : string;
    public var aiStrategyReady096 : bool;
    // Presentation-time search jobs. Every job evaluates the same unchanged turn.
    public var aiPreparationStage, aiPreparationIndex, aiPreparationRound, aiPreparationTurn, aiPreparationStrength, aiPreparationDamp : int;
    public var aiPreparationReady : bool;
    public var aiPreparationIds, aiPreparationSequences, aiPreparationSpies : array<int>;
    public var aiPreparedIds, aiPreparedValues, aiPreparedStrategic, aiPreparedUpliftIds, aiPreparedUplifts : array<int>;
    public var aiPreparedSpyIds, aiPreparedSpyDraw, aiPreparedSpyRisk, aiPreparedSpyTempo : array<int>;
    public var aiPreparedSpyUnsafe : array<bool>;
    public var aiPreparedLeader, aiPreparedCounterRisk : int;
    public var aiPreparationSequenceJob : CBetaGwentAISequence188;
    public var aiPreparationChaseJob : CBetaGwentAIChase188;
    public var aiPreparationSpyJob : CBetaGwentAISpy188;
    public var aiPreparedChase : SBetaGwentAIChasePlan;
    public var aiPreparedChaseReady : bool;

    public function ClearAiPreparation()
    {
        aiPreparationStage=0;aiPreparationIndex=0;aiPreparationReady=false;aiPreparedLeader=0;aiPreparedCounterRisk=0;
        aiPreparationEndgameJob097=NULL;aiEndgameReady097=false;aiEndgameComplete097=false;
        aiStrategyJob096=NULL;aiStrategyIds096.Clear();aiStrategyPenalties096.Clear();aiStrategyReady096=false;aiStrategyRevision096="";
        aiPreparationSequenceJob=NULL;aiPreparationChaseJob=NULL;aiPreparationSpyJob=NULL;aiPreparedChaseReady=false;
        aiPreparationIds.Clear();aiPreparationSequences.Clear();aiPreparationSpies.Clear();
        aiPreparedIds.Clear();aiPreparedValues.Clear();aiPreparedStrategic.Clear();aiPreparedUpliftIds.Clear();aiPreparedUplifts.Clear();
        aiPreparedSpyIds.Clear();aiPreparedSpyDraw.Clear();aiPreparedSpyRisk.Clear();aiPreparedSpyTempo.Clear();aiPreparedSpyUnsafe.Clear();
    }
    public function AiPreparationIsReady() : bool
    {
        var m : SBetaGwentMatchSnapshot;m=match.Snapshot();
        return aiPreparationReady && aiPreparationRound==m.roundNumber && aiPreparationTurn==m.turnSequence && aiPreparationStrength==BetaGwentAIStrength();
    }
    // One candidate per UI tick, with no live play or live RNG consumption.
    public function AiPreparationStep() : bool
    {
        var m : SBetaGwentMatchSnapshot;var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var order : array<int>;var i,j,value,anchor,risk,tempo,draw : int;var unsafe : bool;
        var card : CBetaGwentDuelCard;var model : CBetaGwentPublicResponseAI;
        if(aiSimulating || !CanAct(2))return true;m=match.Snapshot();
        if(aiPreparationStage>0 && (aiPreparationRound!=m.roundNumber || aiPreparationTurn!=m.turnSequence || aiPreparationStrength!=BetaGwentAIStrength()))ClearAiPreparation();
        if(aiPreparationReady)return true;
        if(aiPreparationStage==0){
            ClearAiPreparation();aiPreparationRound=m.roundNumber;aiPreparationTurn=m.turnSequence;
            aiPreparationStrength=BetaGwentAIStrength();aiPreparationDamp=aiSimDamp;archetypeAI.Refresh();
            if(aiObservedRound==m.roundNumber)aiPublicTempo=Max(aiPublicTempo,Min(40,Max(0,Score(1)-aiObservedEnemyScore)));
            aiObservedRound=m.roundNumber;aiObservedEnemyScore=Score(1);
            if(aiPreparationStrength<2){aiPreparationStage=6;return false;}
            anchor=BestVranAnchor(2);risk=AiPublicClearRisk();
            for(i=0;i<live.Size();i+=1){
                s=live[i].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || !s.canBePlayed)continue;
                d=live[i].Definition();if(AiDrawingSpy(live[i])){aiPreparationSpies.PushBack(s.instanceId);continue;}
                if(AiUselessDecoy(live[i]) || AiDeferEmptyDuel(d,2) || d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
                value=AiCardTempo(live[i],false,anchor,risk)*10-AiReserveCost(d)*4+archetypeAI.Priority(d)*10;
                j=0;while(j<order.Size() && order[j]>=value)j+=1;order.Insert(j,value);aiPreparationIds.Insert(j,i);
            }
            AiDiversifySearch(aiPreparationIds,AiSimCap(5));aiPreparationSequences=aiPreparationIds;
            AiDiversifySearch(aiPreparationSequences,AiSimCap(9));aiPreparationStage=1;return false;
        }
        if(aiPreparationStage==1){
            if(aiPreparationIndex<aiPreparationIds.Size() && aiPreparationIndex<AiSimCap(5)){
                card=live[aiPreparationIds[aiPreparationIndex]];value=AiExactTempo(card);
                s=card.Snapshot();aiPreparedIds.PushBack(s.instanceId);aiPreparedValues.PushBack(value);aiPreparedStrategic.PushBack(aiLastStrategicValue);
                aiPreparationIndex+=1;return false;
            }
            aiPreparationStage=2;aiPreparationIndex=0;
        }
        if(aiPreparationStage==2){
            if(aiPreparationStrength>=2 && !m.playerOne.hasPassed && CountLocation(2,8)>=2 && aiPreparationIndex<aiPreparationSequences.Size() && aiPreparationIndex<AiSimCap(9)){
                card=live[aiPreparationSequences[aiPreparationIndex]];s=card.Snapshot();
                if(!aiPreparationSequenceJob){
                    if(aiPreparationDamp<50 || AiPlainLastReply() || AiCriticalShortReply()){model=new CBetaGwentPublicResponseAI in this;model.Initialize(this,AiReplyLimit097());}
                    aiPreparationSequenceJob=new CBetaGwentAISequence188 in this;
                    aiPreparationSequenceJob.Initialize(this,s.instanceId,aiPreparedIds,aiPreparedValues,model);
                    return false;
                }
                if(!aiPreparationSequenceJob.Step())return false;
                aiPreparedUpliftIds.PushBack(s.instanceId);aiPreparedUplifts.PushBack(aiPreparationSequenceJob.result);
                aiPreparationSequenceJob=NULL;aiPreparationIndex+=1;return false;
            }
            aiPreparationStage=3;aiPreparationIndex=0;
        }
        if(aiPreparationStage==3){
            if(aiPreparationIndex<aiPreparationSpies.Size()){
                card=FindCard(aiPreparationSpies[aiPreparationIndex]);s=card.Snapshot();
                if(!aiPreparationSpyJob){aiPreparationSpyJob=new CBetaGwentAISpy188 in this;aiPreparationSpyJob.Initialize(this,s.instanceId);return false;}
                if(!aiPreparationSpyJob.Step())return false;
                aiPreparedSpyIds.PushBack(s.instanceId);aiPreparedSpyDraw.PushBack(aiPreparationSpyJob.result);aiPreparedSpyRisk.PushBack(aiPreparationSpyJob.risk);
                aiPreparedSpyTempo.PushBack(aiPreparationSpyJob.tempo);aiPreparedSpyUnsafe.PushBack(aiPreparationSpyJob.unsafe);
                aiPreparationSpyJob=NULL;aiPreparationIndex+=1;return false;
            }
            aiPreparationStage=4;
        }
        if(aiPreparationStage==4){
            card=Leader(2);aiPreparationStage=5;
            if(card && BestOwnRow(2)!=0){
                s=card.Snapshot();aiPreparedLeader=s.instanceId;value=AiExactTempo(card);
                aiPreparedIds.PushBack(aiPreparedLeader);aiPreparedValues.PushBack(value);aiPreparedStrategic.PushBack(aiLastStrategicValue);return false;
            }
        }
        if(aiPreparationStage==5){
            if(aiPreparedLeader!=0 && aiPreparationStrength>=3 && !m.playerOne.hasPassed && (aiPreparationDamp<50 || AiCriticalShortReply())){
                if(!aiPreparationSequenceJob){
                    model=new CBetaGwentPublicResponseAI in this;model.Initialize(this,AiReplyLimit097());
                    aiPreparationSequenceJob=new CBetaGwentAISequence188 in this;
                    aiPreparationSequenceJob.Initialize(this,aiPreparedLeader,aiPreparedIds,aiPreparedValues,model,!AiLeaderSequencePlanning());return false;
                }
                if(!aiPreparationSequenceJob.Step())return false;
                if(AiLeaderSequencePlanning()){
                    aiPreparedUpliftIds.PushBack(aiPreparedLeader);aiPreparedUplifts.PushBack(aiPreparationSequenceJob.result);
                }else aiPreparedCounterRisk=aiPreparationSequenceJob.result;
                aiPreparationSequenceJob=NULL;
            }
            aiPreparationStage=6;return false;
        }
        if(aiPreparationStage==7){
            if(!aiPreparationChaseJob.Step())return false;
            aiPreparedChase=aiPreparationChaseJob.best;aiPreparedChaseReady=true;aiPreparationChaseJob=NULL;aiPreparationStage=6;
        }

        if(aiPreparationStage==6 || aiPreparationStage==8){
            if(!AiStrategyPreparationStep096()){aiPreparationStage=8;return false;}
            aiPreparationStage=9;
        }
        if(aiPreparationStage==9){if(!AiEndgamePreparation097())return false;aiPreparationStage=6;}
        aiPreparationReady=true;return true;
    }

    // Diagnostics use existing evaluations; they never run extra lookahead or consume RNG.
    public function AiExplain(eventName : string, details : string)
    {
        if (aiSimulating) return;
        if(aiPreparationStage>0 && !aiPreparationReady)BetaGwentLog("AI_REASON schema=1 decision="+(aiDecisionSerial+1)+" event="+eventName+" "+details);
        else BetaGwentLog("AI_REASON schema=1 decision="+aiDecisionSerial+" event="+eventName+" "+details);
    }
    // One guard for every pass rule: a pass that concedes the match is replaced by
    // the best immediate legal play (or the leader). Losing points keeps the match alive.
    private function AiExplainedPass(reason : string) : bool
    {
        var id : int;var d : SBetaGwentDuelDefinition;var row,anchor : int;
        if(AiPassConcedesMatch()){
            id=AiEmergencyCard();
            if(id!=0){
                d=registry.Find(id).Definition();
                BetaGwentLog("DUEL_AI_KEEP reason=pass_guard original="+reason+" card="+id+" lead="+AiPublicPassLead(true));
                AiExplain("SELECT","action=card card="+id+" template="+d.header.templateId+" reason=pass_would_concede_match original="+reason);
                row=BestCardRow(2,d);if(row==0)row=1;
                // A rejected play (no legal target after all) must never stall the match.
                if(d.effect==23)anchor=BestVranAnchor(2);if(anchor==0)anchor=AiPlacementAnchor(d);
                if(anchor!=0){if(PlayBefore(2,id,anchor))return true;}
                else if(Play(2,id,row))return true;
                BetaGwentLog("DUEL_AI_KEEP_FAILED reason=play_rejected card="+id+" original="+reason);
            }
            else if(LeaderAvailable(2) && BestOwnRow(2)!=0){
                BetaGwentLog("DUEL_AI_KEEP reason=pass_guard_leader original="+reason);
                AiExplain("SELECT","action=leader reason=pass_would_concede_match original="+reason+" template="+leaderTemplateTwo);
                if(UseLeader(2))return true;
                BetaGwentLog("DUEL_AI_KEEP_FAILED reason=leader_rejected original="+reason);
            }
        }
        AiExplain("PASS", "reason="+reason+" ownScore="+Score(2)+" enemyScore="+Score(1)+" ownHand="+CountLocation(2,8)+" enemyHand="+CountLocation(1,8)); return Pass(2);
    }
    // Losing this round loses the match (the opponent already holds a crown) and the
    // resolved pass does not keep the lead; a tie also loses while we hold no crown.
    // Gain of our own pending timers (Miruna, Vran, Sappers, Revenant, ...) that a pass
    // forfeits. Only when the opponent has already passed: our pass then ends the round.
    // While the opponent still plays, our timers keep firing during its turns after our pass.
    public function AiOwnTimerGain(ownHand : int) : int
    {
        var i,total : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();if(!m.playerOne.hasPassed)return 0;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId!=2 || (s.locationMask&7)==0 || s.isWaitingToDie || (s.tokenMask&4)!=0)continue;
            // The engine forecast is horizon-based and drops to zero after an enemy pass;
            // a timer that still fires on our turns is worth at least a small payoff.
            if(s.timerValue>0 && s.timerValue<=Max(1,ownHand))total+=Max(3,AiEngineValue(s,2));}
        return total;
    }
    private function AiHeldFinishers() : int
    {
        var i,count : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==2 && s.locationMask==8 && archetypeAI.Reserve(live[i].Definition())>0)count+=1;}
        return count;
    }
    // Full decision position for tools/ai/log_to_test092.py: every live card
    // id:template:side:owner:zone:index:power:base:armor:tokens:timer:tier:playable, plus match,
    // weather and the starting list the AI may know. Diagnostic only; no decision reads it.
    private function AiFlag(value : bool) : string {if(value)return "1";return "0";}
    private function AiLogPosition()
    {
        var i,side,row,part,count : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;var cards,known,rows : string;
        if(aiSimulating)return;m=match.Snapshot();
        for(i=0;i<aiStartingDeckOne.Size();i+=1){if(i>0)known+=",";known+=aiStartingDeckOne[i];}
        for(side=1;side<=2;side+=1)for(row=1;row<=4;row*=2)rows+=weather.Token(side,row)+",";
        BetaGwentLog("AI_POSITION schema=1 decision="+aiDecisionSerial+" strength="+BetaGwentAIStrength()+" presetOne="+presetOne+" presetTwo="+presetTwo
            +" round="+m.roundNumber+" current="+m.currentPlayerId+" crowns="+m.playerOne.crowns+","+m.playerTwo.crowns
            +" passed="+AiFlag(m.playerOne.hasPassed)+","+AiFlag(m.playerTwo.hasPassed)+" leaders="+AiFlag(LeaderAvailable(1))+","+AiFlag(LeaderAvailable(2))
            +" weather="+rows+" cardCount="+live.Size()+" known="+known);
        // Short lines: the native log truncates very long entries.
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            cards+=" "+s.instanceId+":"+s.runtimeTemplate.templateId+":"+s.positionPlayerId+":"+s.ownerId+":"+s.locationMask+":"+s.locationIndex+":"+s.power.currentPower+":"+s.power.basePower+":"+s.power.armor+":"+s.tokenMask+":"+s.timerValue+":"+s.runtimeTierMask+":"+AiFlag(s.canBePlayed);
            count+=1;
            if(count==12 || i==live.Size()-1){BetaGwentLog("AI_POSITION_CARDS decision="+aiDecisionSerial+" part="+part+cards);part+=1;count=0;cards="";}
        }
    }
    public function AiPassConcedesMatch() : bool
    {
        var m : SBetaGwentMatchSnapshot;var lead : int;
        m=match.Snapshot();if(m.playerOne.crowns==0)return false;
        lead=AiPublicPassLead(true);
        return lead<0 || lead==0 && m.playerTwo.crowns==0;
    }
    private function AiEmergencyCard() : int
    {
        var i,best,value,maximum,anchor,risk,exact : int;var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();
        maximum=-2147483647;anchor=BestVranAnchor(2);risk=AiPublicClearRisk();
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || !s.canBePlayed)continue;
            d=live[i].Definition();if(d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
            // Only a play the rules accept: the exact simulation proves it resolves (Decoy without target does not).
            exact=AiExactTempo(live[i]);if(exact==-2147483647)continue;
            // The pass guard must not undo the normal weather rejection. A
            // passed opponent gets no further weather ticks. Keep a filler
            // only if the resolved turn or an own pending timer can pay for it.
            if(m.playerOne.hasPassed && AiWeatherCardToken(d)>0 && exact<=0 && AiOwnTimerGain(CountLocation(2,8))<=0)continue;
            value=AiCardTempo(live[i],true,anchor,risk);if(value>maximum){maximum=value;best=s.instanceId;}}
        return best;
    }
    private function AiExplainPlacement(card : CBetaGwentDuelCard, chosen : int, anchor : int)
    {
        var d : SBetaGwentDuelDefinition; var side,row : int;var s : SBetaGwentCardSnapshot;
        if(aiSimulating || !card)return;d=card.Definition();s=card.Snapshot();side=2;
        if(BetaGwentDuelSpying(d.header.templateId))side=1;
        for(row=1;row<=4;row*=2)AiExplain("ROW", "card="+s.instanceId+" side="+side+" row="+row+" occupied="+CountLocation(side,row)+" weather="+weather.Token(side,row)+" placementCost="+AiRowPlacementCost(side,row,d)+" selected="+(row==chosen)+" anchor="+anchor+" reason=weather_capacity_adjacency_and_deploy");
    }

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
        aiStartingDeckOne.Clear();aiStartingDeckTwo.Clear();
        if(BetaGwentAIStrength()>=4){
            for(i=0;i<ownCards.Size();i+=1)aiStartingDeckOne.PushBack(ownCards[i]);
            for(i=0;i<enemyCards.Size();i+=1)aiStartingDeckTwo.PushBack(enemyCards[i]);
        }
        aiDecisionSerial=0;ClearAiPreparation();
        aiChaseRound=0;aiChaseInitialHand=0;aiChaseSpent=0;
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
        aiChaseRound=0;aiChaseInitialHand=0;aiChaseSpent=0;aiObservedRound=0;aiObservedEnemyScore=0;aiPublicTempo=14;aiSimDamp=40;
        aiEnemyRowPlays.Clear();aiEnemyRowPlays.PushBack(0);aiEnemyRowPlays.PushBack(0);aiEnemyRowPlays.PushBack(0);
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
            + random.InitialSeed() + " draws=" + random.DrawCount() + " starter=" + starter + " engineRngTape=" + random.UsesEngineTape());
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
            // Public destinations only: never expose hidden hand/deck identities.
            if (v.card.locationMask == 32 || v.card.locationMask == 512)
            { frame.destinationIds.PushBack(v.card.instanceId); frame.destinationSides.PushBack(side); frame.destinationZones.PushBack(v.card.locationMask); }
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
        if(kind==18){
            target=registry.Find(targetId);
            if(target){t=target.Snapshot();d=target.Definition();
                BetaGwentLog("DUEL_NO_TARGETS template="+t.runtimeTemplate.templateId+" card="+targetId+" player="+t.positionPlayerId
                    +" zone="+t.locationMask+" pile="+d.pileLocation+" types="+d.targetTypes+" tiers="+d.targetTiers+" traits="+d.pileTraitMask);}
        }
        // Same attack, same kind: the original applies all targets at once. Keep one
        // frame (first cue, latest snapshot) instead of one frame per target.
        if (kind != 11 && kind != 19 && visualAttack != 0 && visualFrames.Size() > 0)
        {
            merged = visualFrames[visualFrames.Size() - 1];
            if (merged.attackId == visualAttack && merged.kind == kind && merged.sourceId == visualSourceId)
            {
                frame = VisualSnapshot(); frame.kind = merged.kind; frame.targetId = merged.targetId; frame.audioKind = merged.audioKind;
                frame.sourceId = merged.sourceId; frame.templateId = merged.templateId; frame.side = merged.side; frame.row = merged.row;
                frame.targetTemplateId = merged.targetTemplateId; frame.targetPower = merged.targetPower; frame.targetSide = merged.targetSide; frame.targetZone = merged.targetZone;
                frame.attackId = merged.attackId; frame.attackCount = merged.attackCount;
                if(!visualAttackTargets.Contains(targetId)){visualAttackTargets.PushBack(targetId);frame.attackCount+=1;} frame.duration = Max(merged.duration, duration);
                d = BetaGwentDuelDefinition(merged.templateId);
                if (d.header.templateId != 0) frame.status = d.title + ": целей " + frame.attackCount; else frame.status = merged.status;
                visualFrames[visualFrames.Size() - 1] = frame; return;
            }
        }
        // Bound presentation memory; final live snapshot still follows on overflow.
        if (visualFrames.Size() >= 128)
        { visualOverflow = true; BetaGwentLog("DUEL_VISUAL_TRUNCATED limit=128"); return; }
        frame = VisualSnapshot(); frame.kind = kind; frame.targetId = targetId; frame.audioKind = audioType;
        frame.attackId = visualAttack; frame.attackCount = 1;visualAttackTargets.Clear();visualAttackTargets.PushBack(targetId);
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
            else if (s.power.armor > oldArmor && visualFrames[visualFrames.Size()-1].audioKind!=21) visualFrames[visualFrames.Size()-1].audioKind = 23;
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
    // A created special lives on the resolution stack, not on the board.
    // Aim from its nearest visible caster without changing the actual request.
    public function PendingAimSourceId() : int
    {
        var i : int; var s : SBetaGwentCardSnapshot;
        if(!pendingCard)return 0;s=pendingCard.Snapshot();
        if((s.locationMask & 7)!=0 || s.locationMask==64)return s.instanceId;
        for(i=playStack.Size()-1;i>=0;i-=1){s=playStack[i].Snapshot();
            if((s.locationMask & 7)!=0 || s.locationMask==64)return s.instanceId;}
        return PendingSourceId();
    }
    public function IsLeaderRowRequest() : bool { return (bool)pendingLeader; }
    public function IsRallyRowRequest() : bool { return (bool)pendingRally; }
    public function PlacementCard() : CBetaGwentDuelCard
    { if (pendingLeader) return pendingLeader; if (IsCaranthirMoveRequest()) return pendingCard; return pendingRally; }
    public function IsCaranthirMoveRequest() : bool
    { return (bool)pendingCard && pendingCard.IsMonsterAbility() && pendingCard.MonsterMode() == 16 && !pendingRow && IsPending(); }
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
    public function IsExternalPolicy(side : int) : bool
    { return (side == 1 || side == 2) && (externalPolicyMask & side) != 0; }
    private function UsesInternalPolicy(side : int) : bool
    { return side == 2 && !IsExternalPolicy(side); }
    private function IsManualDecisionSide(side : int) : bool
    { return side == 1 || IsExternalPolicy(side); }
    public function RequestDecisionSide() : int
    {
        var s : SBetaGwentCardSnapshot;
        if (mulligan) return mulliganSide;
        if (pendingLeader) { s = pendingLeader.Snapshot(); return s.positionPlayerId; }
        if (IsReactionPlacement()) return match.currentPlayerId;
        return NilfDecisionSide();
    }
    private function FirstOpenRow(side : int) : int
    {
        var row : int;
        for (row = 1; row <= 4; row *= 2) if (CountLocation(side, row) < 9) return row;
        return 0;
    }
    private function RequestedPlacementRow(card : CBetaGwentDuelCard, side : int) : int
    {
        side = MonsterPlaySide(card, side);
        if (IsExternalPolicy(NilfDecisionSide())) return FirstOpenRow(side);
        return BestOwnRow(side);
    }
    public function MulliganSwapCount() : int { return mulliganUsed; }
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
        card.Move(side,zone,index);card.SetPlayable(zone==8);if(reset){if(zone==16)card.ResetInDeck();else card.ResetInHand();}Reindex(old.positionPlayerId,old.locationMask);
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
    { var s, pos : SBetaGwentCardSnapshot;var rows : array<int>;var row : int;s=card.Snapshot();for(row=1;row<=4;row*=2)if(CountLocation(s.positionPlayerId,row)+effects.PendingDeckMoves(s.positionPlayerId,row)<9)rows.PushBack(row);if(rows.Size()==0)return;pos=s;pos.locationMask=rows[RandomIndex(rows.Size())];pos.locationIndex=-3;MonsterSummon(pos,card); }
    public function NorthSummonPending(card : CBetaGwentDuelCard) : bool
    {var s : SBetaGwentCardSnapshot;if(!card)return false;s=card.Snapshot();return effects.PendingDeckMoves(0,0,s.instanceId)>0;}
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
        if(!resetBase && s.power.basePower+s.power.permanentPower<=0)
        {
            source.Move(s.positionPlayerId,512,0);source.SetPlayable(false);source.SetWaiting(false);Reindex(s.positionPlayerId,32);
            RecordVisual(12,s.instanceId,"Изначальная сила исчерпана",380);
            BetaGwentLog("DUEL_BANISH_WEAKENED card="+s.instanceId+" removalType=0 killed=false");return;
        }
        if(!resetBase && s.power.currentPower<=0)source.ResetCurrentPower();
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
    public function NeutralReset(card : CBetaGwentDuelCard){var s : SBetaGwentCardSnapshot;if(!card)return;card.NeutralReset();s=card.Snapshot();RecordVisual(12,s.instanceId,"Отряд восстановлен",400);}
    // Presentation only: Geralt: Yrden's board sign on the chosen row (Beta [201525]PowerBoardPhysical).
    public function YrdenVisual(side : int, row : int){var oldSide, oldRow : int;oldSide=visualSide;oldRow=visualRow;visualSide=side;visualRow=row;RecordVisual(12,0,"Ирден",400);visualSide=oldSide;visualRow=oldRow;}
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
    {var s : SBetaGwentCardSnapshot;if(!card)return;s=card.Snapshot();card.Move(s.positionPlayerId,128,0);Reindex(s.positionPlayerId,s.locationMask);card.Move(s.positionPlayerId,16,CountLocation(s.positionPlayerId,16));card.SetPlayable(false);card.ResetInDeck();RecordVisual(14,s.instanceId,"Карта в низ колоды",350);}
    public function NilfDiscard(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;s=card.Snapshot();NorthMoveInactive(card,s.positionPlayerId,32,false);BetaGwentLog("DUEL_DISCARD card="+s.instanceId);}
    public function NilfBanish(card : CBetaGwentDuelCard)
    {var s : SBetaGwentCardSnapshot;s=card.Snapshot();card.Move(s.positionPlayerId,512,CountLocation(s.positionPlayerId,512));Reindex(s.positionPlayerId,s.locationMask);RecordVisual(4,s.instanceId,"Карта удалена",420,12);}
    public function NilfQueueReaction(card : CBetaGwentDuelCard, kind : int, side : int)
    {var job : CBetaGwentNilfReaction;if(nilfJobs.Size()>=128){FailAbility("Слишком много реакций Нильфгаарда.");return;}job=new CBetaGwentNilfReaction in this;job.source=card;job.kind=kind;job.side=side;nilfJobs.PushBack(job);}
    private function NilfNextReaction() : bool
    {
        var s : SBetaGwentCardSnapshot;var card : CBetaGwentDuelCard;var row : int;var rows : array<int>;
        while(nilfJobs.Size()>0)
        {
            nilfJob=nilfJobs[0];nilfJobs.Erase(0);card=nilfJob.source;s=card.Snapshot();
            if(s.isWaitingToDie || (s.tokenMask&12)!=0 || (s.locationMask&63)==0 || ((nilfJob.kind==7 || nilfJob.kind==8) && s.locationMask!=32) || (nilfJob.kind==2 && s.locationMask!=8) || (nilfJob.kind==6 && s.locationMask!=16))continue;
            BetaGwentLog("DUEL_NILF_REACTION kind="+nilfJob.kind+" card="+s.instanceId+" side="+nilfJob.side);
            if(nilfJob.kind==8){card.playFromLocation=32;card.Move(s.positionPlayerId,256,0);Reindex(s.positionPlayerId,32);card.SetPlayable(false);StartPlayResolution(card,s.positionPlayerId);return true;}
            // Daerlan/Wardancer use MoveCards + GetRandomLastAvailablePosition,
            // not PlayCards and not a policy placement request.
            if(nilfJob.kind==2 || nilfJob.kind==6)
            {
                rows.Clear();for(row=1;row<=4;row*=2)if(CountLocation(s.positionPlayerId,row)<9)rows.PushBack(row);
                if(rows.Size()>0)
                {
                    row=rows[random.NextBounded(rows.Size())];card.playFromLocation=s.locationMask;
                    InsertUnit(card,s.positionPlayerId,row,-3);Reindex(s.positionPlayerId,s.locationMask);card.SetPlayable(false);
                }
                if(nilfJob.kind==2)MonsterDraw(s.positionPlayerId,false);
                continue;
            }
            if(nilfJob.kind==7)
            {
                if(IsExternalPolicy(NilfDecisionSide()))
                {
                    row=FirstOpenRow(MonsterPlaySide(card,s.positionPlayerId));if(row==0)continue;
                    pendingCard=card;pendingRally=card;pendingRow=false;pendingChoice=false;pendingPileChoice=false;pendingIds.Clear();requestId+=1;
                    message="Выберите место отряда, разыгрываемого реакцией.";return true;
                }
                row=BestOwnRow(s.positionPlayerId);if(row==0)continue;card.playFromLocation=s.locationMask;InsertUnit(card,s.positionPlayerId,row,-3);Reindex(s.positionPlayerId,s.locationMask);card.SetPlayable(false);StartPlayResolution(card,s.positionPlayerId);return true;
            }
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
    { if(!source)return false; if(source.TemplateId()==162302)return templateId==162402;if(source.TemplateId()==142304)return templateId==143301; return BetaGwentMonsterSpawnAllowed(source.TemplateId(),templateId) || NilfDynamicSpawnAllowed(source,templateId); }
    public function MonsterCreate(card : CBetaGwentDuelCard, templateId : int) { BeginCreatedPlay(card, templateId); }
    public function MonsterPower(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard, amount : int)
    { if (card && !effects.Enqueue(card, 1, amount, false, source)) FailAbility("Не удалось поставить способность Чудовищ в очередь."); }
    public function MonsterOperation(source : CBetaGwentDuelCard, card : CBetaGwentDuelCard, operation : int, amount : int, locations : int)
    { if (card && !effects.Enqueue(card, operation, amount, false, source, locations)) FailAbility("Не удалось изменить изначальную силу."); }
    // Only the initial selection is optional. Follow-up choices (e.g. Saskia's
    // replacement cards) must still resolve the number already committed.
    private function OptionalChoiceLimit(source : CBetaGwentDuelCard) : int
    {
        var limit, i : int;var s : SBetaGwentCardSnapshot;
        if (!source || source.monsterStage != 0) return 0;
        limit=BetaGwentDuelOptionalChoiceLimit(source.TemplateId());
        if(limit>=0)return limit;
        // Any number, including zero; keep the total stable as picks conceal.
        limit=source.monsterIds.Size();
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.locationMask==8 && !s.isWaitingToDie && (s.tokenMask&64)!=0
                && (s.runtimeTierMask&14)!=0 && (s.runtimeTemplate.typeMask&12)!=0)limit+=1;}
        return Max(1,limit);
    }
    private function AiRowTicks(actor : int) : int
    { return AiWeatherTicks(actor); }
    private function AiHazardMoveValue(actor : int, side : int, fromRow : int, toRow : int) : int
    {
        var token,ticks,value : int;if(fromRow==toRow)return -2147483647;
        token=weather.Token(side,fromRow);if(!MonsterIsHazard(token))return -2147483647;
        ticks=AiRowTicks(actor);
        value=weather.ForecastTokenLoss(side,toRow,token,ticks)-weather.ForecastTokenLoss(side,toRow,weather.Token(side,toRow),ticks)
            -weather.ForecastTokenLoss(side,fromRow,token,ticks);
        if(side==actor)value=-value;return value;
    }
    private function AiRowAbilityValue(source : CBetaGwentDuelCard, side : int, row : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s,t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var actor,id,i,j,total,highest,value,ticks,next,best,loss,destinations,penalty : int;
        d=source.Definition();actor=NorthActingSide(source);id=source.TemplateId();ticks=AiRowTicks(actor);
        GetZoneCards(side,row,cards);
        if(id==112102){
            if(side==actor)return -2147483647;
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&8)!=0)continue;total+=t.power.currentPower;highest=Max(highest,t.power.currentPower);}
            if(total<25)return 0;
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&8)==0 && t.power.currentPower==highest)value+=AiDamageChoice(t,actor,t.power.currentPower+t.power.armor);}
            return value;
        }
        if(id==201523){
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&8)!=0)continue;
                // NeutralReset keeps permanent power and clears lock/resilience/spying.
                loss=t.power.basePower+t.power.permanentPower-t.power.currentPower;
                if((t.tokenMask&4)!=0){s=t;s.tokenMask=s.tokenMask&-5;loss+=AiEngineValue(s,actor);}
                if((t.tokenMask&1)!=0 && match.roundNumber<3)loss-=Max(0,t.power.basePower)/2;
                if(side!=actor)loss=-loss;value+=loss;
            }return value;
        }
        if(side==actor && id!=200089)return -2147483647;
        if(id==152105){
            if(weather.Token(side,row)==64)return 0;
            return weather.ForecastTokenLoss(side,row,64,ticks)-weather.ForecastTokenLoss(side,row,weather.Token(side,row),ticks);
        }
        if(id==162302 || id==142304){
            if(CountLocation(side,row)>=9)return -2147483647;
            if(id==162302){
                highest=2147483647;for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.isWaitingToDie || (t.tokenMask&264)!=0)continue;highest=Min(highest,t.power.currentPower);}
                for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&264)==0 && t.power.currentPower==highest)value+=AiDamageChoice(t,actor,t.power.currentPower+t.power.armor);}
            }else for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(!t.isWaitingToDie && (t.tokenMask&8)==0)value+=AiDamageChoice(t,actor,3);}
            if(ticks==0)return -1;return value-1;
        }
        if(id==201700){
            if(source.monsterStage>0)return AiHazardMoveValue(actor,side,source.monsterStored,row);
            best=-2147483647;for(next=1;next<=4;next*=2)if(next!=row)best=Max(best,AiHazardMoveValue(actor,side,row,next));return best;
        }
        if(id==200089){
            // Evacuating an enemy weather row gives away its future damage.
            loss=weather.ForecastTokenLoss(side,row,weather.Token(side,row),ticks);destinations=0;
            for(next=1;next<=4;next*=2)if(next!=row && CountLocation(side,next)<9){destinations+=1;penalty+=weather.Damage(side,next)*Min(3,CountLocation(side,row));}
            if(destinations==0)return 0;value=penalty*ticks/(10*destinations)-loss;if(side==actor)value=-value;return value;
        }
        return CountLocation(side,row);
    }

    public function MonsterRequest(source : CBetaGwentDuelCard, ids : array<int>, kind : int, minimum : int, maximum : int)
    {
        var s, t : SBetaGwentCardSnapshot; var d, option, picked : SBetaGwentDuelDefinition;
        var m : SBetaGwentMatchSnapshot; var i, best, value, score, rowSide, bestSide, candidateSide : int; var card : CBetaGwentDuelCard;var visibleTargets : bool;
        if (fatal || !source) return; s = source.Snapshot(); d = source.Definition(); m = match.Snapshot();
        if (kind == 0) for (i=ids.Size()-1;i>=0;i-=1) if (!CanDeployTarget(source,registry.Find(ids[i]))) ids.Erase(i);
        // Mixed-zone abilities (Sweers, Serrit, Vrihedd Brigade, ...) use the
        // board/visible-hand arrow when every legal target is already visible.
        // Preserve the original candidate pool; tutors and private piles keep their picker.
        if(kind==2 && IsManualDecisionSide(NilfDecisionSide()) && ids.Size()>0 && !BetaGwentDuelPlayChoice(d.header.templateId)){
            visibleTargets=true;
            for(i=0;i<ids.Size();i+=1){card=registry.Find(ids[i]);if(!card){visibleTargets=false;break;}t=card.Snapshot();
                if((t.locationMask&7)==0 && !(t.locationMask==8 && (t.positionPlayerId==NorthActingSide(source) || (t.tokenMask&64)!=0))){visibleTargets=false;break;}}
            if(visibleTargets)kind=0;
        }
        pendingCard = source; pendingIds = ids; pendingChoice = kind == 1; pendingRow = kind == 3; pendingPileChoice = kind == 2;
        pendingRally = NULL; pendingHandPower = false; requestId += 1; monsterMinimum = minimum; monsterMaximum = maximum;
        // A play-from-pile choice must resolve when at least one legal card exists.
        // Empty pools still take the normal no-card branch below.
        if (kind == 2 && BetaGwentDuelPlayChoice(d.header.templateId) && ids.Size() > 0) monsterMinimum = Max(1, monsterMinimum);
        if (d.specialMode == 18) { t=source.Snapshot(); monsterMaximum = Min(d.specialCount,Max(0,9-CountLocation(BetaGwentOpponentId(t.positionPlayerId),t.locationMask))); }
        // Beta deploy abilities are mandatory whenever a legal target exists.
        if (ids.Size() > 0 && kind != 3 && d.specialMode != 18 && OptionalChoiceLimit(source) == 0) monsterMinimum = Max(1, monsterMinimum);
        if (OptionalChoiceLimit(source) > 0 && kind != 1 && kind != 3)
        { monsterMinimum = 0; monsterMaximum = OptionalChoiceLimit(source); }
        message = d.title + ": выберите подсвеченную цель.";
        if (kind == 1) message = d.title + ": выберите создаваемую карту или вариант способности.";
        if (kind == 2) message = d.title + ": выберите карту из предложенного списка.";
        if (kind == 3) message = d.title + ": выберите ряд соперника.";
        if (kind == 0) message = d.title + ": выберите подсвеченный отряд для способности.\n" + d.description;
        if (d.header.templateId == 200124) message = d.title + ": укажите отряд, которому нужно нанести урон.\n" + d.description;
        if (kind == 2 && BetaGwentDuelPlayChoice(d.header.templateId) && ids.Size() > 0) message = d.title + ": обязательно выберите карту для розыгрыша. Отряд затем нужно разместить в ряду.";
        if (d.specialMode == 18) message += " Выбрано " + source.monsterIds.Size() + " / " + d.specialCount + ". Можно завершить выбор.";
        if (OptionalChoiceLimit(source) > 0) message += " Выбрано " + source.monsterIds.Size() + " / " + monsterMaximum + ". Можно завершить выбор.";
        BetaGwentLog("DUEL_ABILITY_CHOICE source=" + d.header.templateId + " kind=" + kind + " candidates=" + ids.Size());
        if (ids.Size() == 0)
        {
            if (d.header.templateId == 201780 && IsManualDecisionSide(NilfDecisionSide()))
            {
                monsterMinimum = 0;
                message = d.title + ": в сбросе противника нет подходящего бронзового или серебряного солдата. Нажмите «Продолжить».";
                return;
            }
            s = source.Snapshot(); RecordVisual(18, s.instanceId, d.title + ": нет целей", 620, 8);
            monsters.Select(source, 0); return;
        }
        if (!UsesInternalPolicy(NilfDecisionSide())) return;
        archetypeAI.Refresh();
        rowSide=BetaGwentOpponentId(NorthActingSide(source));
        if(kind==3 && SpecialRowMode()==8)rowSide=NorthActingSide(source);
        score = -2147483647; best = 0; bestSide=rowSide;
        for (i = 0; i < ids.Size(); i += 1)
        {
            value = 0;
            if (kind == 1) { option = BetaGwentDuelViewDefinition(ids[i]); value = AiCreatedOptionValue(option,NilfDecisionSide(),AiHorizon(NilfDecisionSide())==0); }
            else if (kind == 3) {
                for(candidateSide=1;candidateSide<=2;candidateSide+=1){
                    if(SpecialRowMode()!=1 && candidateSide!=rowSide)continue;
                    value=AiRowAbilityValue(source,candidateSide,ids[i]);
                    AiExplain("ROW_OPTION","source="+source.TemplateId()+" side="+candidateSide+" row="+ids[i]+" value="+value);
                    if(value>score){score=value;best=ids[i];bestSide=candidateSide;}
                }
                continue;
            }
            else
            {
                card = registry.Find(ids[i]); if (!card) continue; t = card.Snapshot();
                if(kind==2 && BetaGwentDuelPlayChoice(source.TemplateId()) && !HasRequiredPlayTargetForSide(card.Definition(),NilfDecisionSide()))
                {AiExplain("TARGET_REJECT","source="+source.TemplateId()+" target="+ids[i]+" reason=no_legal_child_play_target");continue;}
                value = AiAbilityChoiceValue(source,card,kind);
                if (kind == 0 && t.positionPlayerId == s.positionPlayerId && (d.specialMode == 11 || d.specialMode == 22)) value = -value;
                // A special is preferred only when it does something: an empty deck
                // tutor (Reinforcement with no unit left) is worth nothing.
                if(!AiRevealingChoice(source)){
                    picked = card.Definition();
                    if (t.runtimeTemplate.typeMask == 2 && (picked.effect != 29 || value > 0)) value += 5;
                }
                if(t.locationMask==8 && t.positionPlayerId!=NilfDecisionSide() && (t.tokenMask&64)==0 && !AiRevealingChoice(source))value=0;
                if(kind==0 && AiReturningSpy(t,NilfDecisionSide()))value=-Max(1,Max(value,-value));
            }
            if(weatherProfile && kind!=1 && !AiRevealingChoice(source))value=weatherAI.ChoiceValue(source,ids[i],kind);
            if(source.TemplateId()==201615 && source.monsterStage==0 && kind==1)value=AiOutlawBranchValue(ids[i],NilfDecisionSide(),AiHorizon(NilfDecisionSide())==0);
            if(source.TemplateId()==201615 && source.monsterStored==201715 && kind==2 && card)value=AiPileCandidateValue(card,NilfDecisionSide(),AiHorizon(NilfDecisionSide())==0,1);
            if(kind==0 && card && d.effect==34 && d.specialMode==9)value=AiDeckCopyChoiceValue(card,d.specialCount);
            if(kind==0 && card && (source.TemplateId()==200170 || source.TemplateId()==122307 || source.TemplateId()==200026))value=archetypeAI.CopyValue(source.TemplateId()==200170,card,true);
            if(kind==1)value+=archetypeAI.ChoiceBonus(option);
            else if(kind==2 && card && !AiRevealingChoice(source) && !(t.locationMask==8 && t.positionPlayerId!=2 && (t.tokenMask&64)==0)){
                if(archetypeAI.IsDiscard(source))value=archetypeAI.DiscardValue(card);
                else value+=archetypeAI.ChoiceBonus(card.Definition());
            }
            // Calveit chooses only among the three actual revealed deck cards.
            // When catching a pass, prefer current tempo over future engines.
            if(kind==2 && source.TemplateId()==200164 && card)value=AiCardTempo(card,m.playerOne.hasPassed,BestVranAnchor(2),AiPublicClearRisk());
            AiExplain("TARGET_OPTION", "source="+source.TemplateId()+" request="+requestId+" kind="+kind+" target="+ids[i]+" value="+value);
            if (value > score) { score = value; best = ids[i]; }
        }
        // Generation 3: pick card targets by playing each option on a cloned session.
        if (kind == 0 && source.TemplateId()!=162206 && BetaGwentAIStrength() >= 3 && !aiSimulating && ids.Size() > 1 && ids.Size() <= 14)
        {
            value = AiSimChoice(source, ids, best);
            if (value != 0) best = value;
        }
        if(best==0){AiExplain("TARGET_FINISH","source="+source.TemplateId()+" reason=no_legal_child_play");monsters.Select(source,0);return;}
        if (OptionalChoiceLimit(source) > 0 && score <= 0)
        { AiExplain("TARGET_FINISH", "source="+source.TemplateId()+" request="+requestId+" reason=no_positive_optional_choice"); monsters.Select(source, 0); return; }
        AiExplain("TARGET_SELECT", "source="+source.TemplateId()+" request="+requestId+" kind="+kind+" target="+best+" reason=highest_choice_value_with_exact_target_simulation");
        if (kind == 3) monsters.Row(source, bestSide, best); else monsters.Select(source, best);
    }
    private function AiSimChoice(source : CBetaGwentDuelCard, ids : array<int>, preferred : int) : int
    {
        var g : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot; var i, best, value, maximum, before : int;
        s = source.Snapshot(); maximum = -2147483647;
        BetaGwentAISimEnter();
        for (i = 0; i < ids.Size(); i += 1)
        {
            g = AiSimClone(); if (!g) continue;
            before = g.AiProjectedLead()+g.AiResilientCarry()+g.AiOwnSpyKeepTotal();
            g.monsters.Select(g.FindCard(s.instanceId), ids[i]); g.FlushDeaths();
            if (g.IsFatal()) continue;
            // Future correction is a PRE-action delta (damage/lock/setup), not another attack on the resolved clone.
            value = g.AiProjectedLead()+g.AiResilientCarry()+g.AiOwnSpyKeepTotal() - before + AiChoiceFutureValue(source,FindCard(ids[i]));
            // Equal immediate scores retain the strategic choice. Adding deck
            // copies has zero board tempo, but can prepare a deathwish chain.
            if (value > maximum || (value == maximum && ids[i] == preferred)) { maximum = value; best = ids[i]; }
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
        row = RequestedPlacementRow(child, s.positionPlayerId); if (row == 0) { CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        if (UsesInternalPolicy(NilfDecisionSide())) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
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
        Reindex(t.positionPlayerId, 32); card.SetPlayable(false); RecordVisual(15, t.instanceId, "Из сброса → Драугир", 480);
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
    // The opponent's ambush is placed face down: its play never names the card.
    private function HiddenAmbushPlay(side : int, d : SBetaGwentDuelDefinition) : bool
    { return side == 2 && d.header.typeMask == 4 && (d.tokens & 8) != 0; }
    public function QueueTimer(card : CBetaGwentDuelCard, operation : int, value : int)
    { if (!effects.EnqueueTimer(card, operation, value)) FailAbility("Не удалось поставить изменение счётчика в очередь."); }
    public function RecordTimerVisual(card : CBetaGwentDuelCard, old : int, operation : int)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        s = card.Snapshot(); d = card.Definition();
        // A face-down enemy ambush counts down silently: no caption, glow or sound.
        if (s.positionPlayerId == 2 && (s.tokenMask & 8) != 0 && (s.locationMask & 7) != 0)
        { BetaGwentLog("DUEL_TIMER_CHANGE card=" + s.instanceId + " hidden=true"); return; }
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
            amount = t.power.currentPower; if (!QueueConsume(card, live[i])) return; QueuePower(card, amount, false);
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
    public function CanDeployTarget(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var d : SBetaGwentDuelDefinition;
        // A chosen deploy target is another instance. Explicit self effects
        // enqueue their actions directly and never use this selection pool.
        if (!source || !target) return false;
        if (source != target) return true;
        d=source.Definition();
        // Lock toggles and leaders can deliberately select themselves; this is
        // not a boost/damage deploy and is also a safe choice for Radovid.
        return d.effect==18 || d.effect==34 && d.specialMode==404 || BetaGwentDuelIsLeader(d.header.templateId);
    }
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
    public function QueueArmor(card : CBetaGwentDuelCard, amount : int, optional source : CBetaGwentDuelCard)
    { if (!source) source = registry.Find(visualSourceId); if (!effects.Enqueue(card, 2, amount, false, source)) FailAbility("Не удалось поставить броню в очередь."); }
    public function QueueDestroy(card : CBetaGwentDuelCard, optional source : CBetaGwentDuelCard)
    { if (!effects.Enqueue(card, 3, 0, false, source)) FailAbility("Не удалось поставить уничтожение в очередь."); }
    public function CanConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var s, t : SBetaGwentCardSnapshot;
        if (!source || !target || source == target) return false;
        s = source.Snapshot(); t = target.Snapshot();
        // Compare instances, not templates: another copy of the same unit is a legal meal.
        return s.instanceId != t.instanceId;
    }
    public function QueueConsume(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : bool
    {
        var s : SBetaGwentCardSnapshot; var operation : int;
        if (!CanConsume(source, target))
        { BetaGwentLog("DUEL_CONSUME_REJECT reason=self_or_missing_target"); return false; }
        s = target.Snapshot(); operation = 4; if (s.locationMask == 32 || s.locationMask == 8) operation = 5;
        if (!effects.Enqueue(target, operation, 0, false, source))
        { FailAbility("Не удалось поставить поглощение в очередь."); return false; }
        return true;
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
        var cue : CBetaGwentDuelVisualFrame;
        if (fatal || !source || !target) return false; s = source.Snapshot(); t = target.Snapshot(); d = target.Definition();
        if ((s.locationMask & 7) == 0 || s.isWaitingToDie || (t.locationMask != 32 && t.locationMask != 8) || t.isWaitingToDie) return false;
        // CardBanishAttack calls Banish, not Kill: no second Killed/deathwish batch.
        target.Move(t.positionPlayerId, 512, 0); target.SetPlayable(false); Reindex(t.positionPlayerId, t.locationMask);
        RecordVisual(11, t.instanceId, "Поглощение: " + d.title, 460);
        if(recordVisuals && !visualOverflow && visualFrames.Size()>0){
            cue=visualFrames[visualFrames.Size()-1];
            // The class is shared by reference. Retain the ORIGIN zone for the pile consume animation.
            if(cue.kind==11 && cue.targetId==t.instanceId){cue.targetZone=t.locationMask;cue.targetPower=t.power.currentPower;}
        }
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
        index = count;
        if(destination.locationIndex>=0)index=Min(count,destination.locationIndex);
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
        if(AiClearsOwnRow(d) && MonsterIsHazard(token))return count-weather.ClearRowForecast(side,row)-Min(2,AiHorizon(side));
        if(d.effect==15 && boon>0)return count+boon*turns;
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
        { view.card = live[i].Snapshot(); cardDefinition = live[i].Definition(); view.title = cardDefinition.title; view.createdCopy=live[i].createdCopy;
          if(!mulligan && view.card.locationMask==8 && !HasRequiredPlayTarget(live[i]))view.card.canBePlayed=false;
          output.PushBack(view); }
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
    public function Leader(side : int) : CBetaGwentDuelCard
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
                priority=Max(archetypeAI.Mulligan(hand[i]),AiTutorMulliganPriority(hand[i]));AiExplain("MULLIGAN_OPTION", "card="+s.instanceId+" template="+s.runtimeTemplate.templateId+" replacePriority="+priority+" reason=archetype_duplicates_and_legal_tutor_pool");if(priority>maximum){maximum=priority;outgoing=hand[i];}}
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
    private function AiMulliganTutorCandidate(sourceId : int, s : SBetaGwentCardSnapshot) : bool
    {
        if(s.positionPlayerId!=2 || s.locationMask!=16 || s.isWaitingToDie || (s.runtimeTierMask&2)==0)return false;
        if(sourceId==162314)return s.runtimeTemplate.typeMask==4;
        if(sourceId==201617)return (s.runtimeTemplate.typeMask&12)!=0 && s.runtimeTemplate.templateId!=201617
            && BetaGwentNorthernCategory(s.runtimeTemplate.templateId,2);
        return false;
    }
    // Own remaining deck only: exclude each played instance before following
    // the chain. Emissary sees a random pair; Recruit plays a random soldier.
    // Neither estimate consumes gameplay RNG or reads the opponent's cards.
    private function AiMulliganTutorTempo(card : CBetaGwentDuelCard, excluded : array<int>) : int
    {
        var s,t : SBetaGwentCardSnapshot;var i,j,value,total,count : int;var values : array<int>;
        if(!card)return 0;s=card.Snapshot();value=s.power.currentPower;
        if(BetaGwentDuelSpying(s.runtimeTemplate.templateId))value=-value;
        // Other bronzes keep their researched deploy/engine value; their body
        // alone must not make a useful low-power ability look like a dead end.
        if(s.runtimeTemplate.templateId!=162314 && s.runtimeTemplate.templateId!=201617)
            return Max(value,BetaGwentAICardWorth(s.runtimeTemplate.templateId,value));
        if(excluded.Contains(s.instanceId) || excluded.Size()>=6)return value;
        excluded.PushBack(s.instanceId);
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(excluded.Contains(t.instanceId) || !AiMulliganTutorCandidate(s.runtimeTemplate.templateId,t))continue;
            values.PushBack(AiMulliganTutorTempo(live[i],excluded));}
        if(values.Size()==0)return value;
        if(values.Size()==1)return value+values[0];
        if(s.runtimeTemplate.templateId==201617){
            for(i=0;i<values.Size();i+=1)total+=values[i];
            return value+total/values.Size();
        }
        for(i=0;i<values.Size();i+=1)for(j=i+1;j<values.Size();j+=1){total+=Max(values[i],values[j]);count+=1;}
        return value+total/count;
    }
    private function AiCardKeepValue(card : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition;var kept : SBetaGwentCardSnapshot; var value,targets : int;var excluded : array<int>;
        d = card.Definition(); value = BetaGwentAICardWorth(d.header.templateId, d.header.power);
        if (BetaGwentDuelSpying(d.header.templateId)) value = Max(value, 11);
        if (d.header.typeMask != 4) value = Max(value, 10);
        // Neighbour boosts need bodies in this round, not their lifetime average.
        // At mulligan the board is empty; count own known deploys and summons.
        value += Max(0, archetypeAI.Priority(d)) / 2;
        value += archetypeAI.MulliganKeepBonus(card);
        if(d.effect==3){targets=AiMulliganBodies(card);value=Min(value,Min(3,targets)*d.amount);}
        if(AiTutorTargetCount(card)==0){kept=card.Snapshot();value=Min(value,Max(0,kept.power.currentPower));}
        // Positive chains keep their researched synergy value. Empty or losing
        // spy chains must not inherit the generic eleven-point spy floor.
        if(d.header.templateId==162314 || d.header.templateId==201617){
            targets=AiMulliganTutorTempo(card,excluded);if(targets<=0)value=Min(value,targets);}
        return value;
    }
    // Return -1 for non-tutors. Managed tutors use the same type/tier filters
    // as their live request, including Elven Mercenary's bronze special pool.
    private function AiTutorTargetCount(card : CBetaGwentDuelCard) : int
    {
        var d,td : SBetaGwentDuelDefinition;var s : SBetaGwentCardSnapshot;var cards : array<CBetaGwentDuelCard>;
        var i,count : int;var natalis : bool;
        d=card.Definition();
        natalis=d.effect==34 && d.specialMode==103 && d.header.templateId!=200033;
        if(d.effect!=29){
            d.pileLocation=16;d.targetTypes=14;d.targetTiers=15;d.targetIgnore=0;
            if(d.header.templateId==142308){d.targetTypes=10;d.targetTiers=2;}
            else if(d.header.templateId==162314){d.targetTypes=4;d.targetTiers=2;}
            else if(d.header.templateId==201617){d.targetTypes=12;d.targetTiers=2;}
            else if(d.header.templateId==142207){d.targetTypes=4;d.targetTiers=6;}
            else if(d.header.templateId==201676){d.targetTiers=6;}
            else if(natalis){d.targetTiers=6;}
            else return -1;
        }
        LocationCards(2,d.pileLocation,cards);
        for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();td=cards[i].Definition();
            if(cards[i]==card || s.isWaitingToDie || (s.runtimeTemplate.typeMask&d.targetTypes)==0 || (s.runtimeTierMask&d.targetTiers)==0
                || (s.tokenMask&d.targetIgnore)!=0 || (d.consumeMaximum>0 && s.power.currentPower>d.consumeMaximum))continue;
            if((d.header.templateId==162314 || d.header.templateId==201617) && !AiMulliganTutorCandidate(d.header.templateId,s))continue;
            if(d.pileTraitMask!=0 && (td.unitTraits&d.pileTraitMask)==0)continue;
            if(d.header.templateId==142207 && !BetaGwentNilfDwarf(td.header.templateId))continue;
            if(d.header.templateId==201676 && !BetaGwentNorthernCategory(td.header.templateId,12))continue;
            if(natalis && (!BetaGwentNorthernCategory(td.header.templateId,8) || AiPileCandidateValue(cards[i],2,false,1)<=0))continue;
            count+=1;
        }
        return count;
    }
    private function AiTutorMulliganPriority(card : CBetaGwentDuelCard) : int
    {
        var count,tempo : int;var excluded : array<int>;count=AiTutorTargetCount(card);
        if(count>0 && (card.TemplateId()==162314 || card.TemplateId()==201617)){
            tempo=AiMulliganTutorTempo(card,excluded);
            if(tempo<=0){AiExplain("MULLIGAN_WEAK_TUTOR","template="+card.TemplateId()+" eligibleTargets="+count+" expectedTempo="+tempo+" reason=remaining_tutor_chain_has_no_positive_tempo");return 30;}}
        if(count!=0)return 0;
        AiExplain("MULLIGAN_EMPTY_TUTOR","template="+card.TemplateId()+" eligibleTargets=0 reason=ability_cannot_play_from_remaining_pile");
        return 30;
    }
    private function AiMulliganBodies(exclude : CBetaGwentDuelCard) : int
    {
        var i,j,count,copies : int;var s,t : SBetaGwentCardSnapshot;var d,spawn : SBetaGwentDuelDefinition;
        for(i=0;i<live.Size();i+=1){
            s=live[i].Snapshot();if(live[i]==exclude || s.positionPlayerId!=2 || s.isWaitingToDie)continue;
            if((s.locationMask&7)!=0 && s.runtimeTemplate.typeMask==4 && (s.tokenMask&8)==0){count+=1;continue;}
            if((s.locationMask!=8 && s.locationMask!=64) || !s.canBePlayed)continue;
            d=live[i].Definition();if(d.header.typeMask!=4 || BetaGwentDuelSpying(d.header.templateId))continue;
            count+=1;
            if(d.deploySpawnCount>0){spawn=BetaGwentDuelDefinition(d.deploySpawnTemplate);if(!BetaGwentDuelSpying(spawn.header.templateId))count+=d.deploySpawnCount;}
            if(d.deploySummonTemplate>0){copies=0;for(j=0;j<live.Size();j+=1){t=live[j].Snapshot();
                if(t.positionPlayerId==2 && t.locationMask==16 && t.runtimeTemplate.templateId==d.deploySummonTemplate)copies+=1;}
                count+=copies;}
        }
        return Min(3,count);
    }
    private function AiMulliganWorst(hand : array<CBetaGwentDuelCard>, reserved : array<int>, blacklist : array<int>) : CBetaGwentDuelCard
    {
        var deck : array<CBetaGwentDuelCard>; var worst : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var i, total, count, value, lowest : int;
        LocationCards(2, 16, deck);
        for (i = 0; i < deck.Size(); i += 1)
        {
            d = deck[i].Definition(); if (blacklist.Contains(d.header.templateId)) continue;
            total += AiCardKeepValue(deck[i]); count += 1;
        }
        if (count == 0) return NULL;
        lowest = 2147483647;
        for (i = 0; i < hand.Size(); i += 1)
        {
            s = hand[i].Snapshot(); if (reserved.Contains(s.instanceId)) continue;
            d = hand[i].Definition(); if (d.header.tierMask == 8) continue;
            if(d.header.templateId==132305 || d.effect==23)continue; // Keep the consume core; archetype rules handle duplicates.
            // Held finishers (Mourntart, Scorch, ...) look weak by printed power; never trade them away.
            if(BetaGwentAIFinisher(d.header.templateId) || archetypeAI.Reserve(d)>0)continue;
            value = AiCardKeepValue(hand[i]);
            if (value < lowest) { lowest = value; worst = hand[i]; }
        }
        if (!worst || lowest * count + BetaGwentAITune(6) * count >= total) return NULL;
        return worst;
    }
    private function BeginMulligan(starter : int, budget : int)
    {
        aiRoundHandOne = CountLocation(1, 8); aiRoundHandTwo = CountLocation(2, 8);
        mulliganSide = 1;
        if (IsExternalPolicy(2)) mulliganSide = 2;
        else AiMulligan(budget);
        roundStarter = starter; mulliganBudget = budget; mulliganUsed = 0;
        blacklistedTemplates.Clear(); reservedCards.Clear(); pendingIds.Clear();
        mulligan = true; requestId += 1; RefreshMulligan();
        BetaGwentLog("DUEL_MULLIGAN_BEGIN request=" + requestId + " choices=" + budget + " ai=summon_group");
        if (pendingIds.Size() == 0 || CountLocation(mulliganSide, 16) == 0) FinishMulligan(requestId);
    }
    private function RefreshMulligan()
    {
        var ordered : array<CBetaGwentDuelCard>; var i : int; var s : SBetaGwentCardSnapshot;
        pendingIds.Clear(); LocationCards(mulliganSide, 8, ordered);
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
        if (s.positionPlayerId != mulliganSide || s.locationMask != 8) return false;
        if (!BetaGwentRequestContains(blacklistedTemplates, s.runtimeTemplate.templateId))
            blacklistedTemplates.PushBack(s.runtimeTemplate.templateId);
        LocationCards(mulliganSide, 16, ordered);
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
        incoming.Move(mulliganSide, 8, s.locationIndex); incoming.SetPlayable(true);MonsterMoved(t);
        outgoing.Move(mulliganSide, 256, 0); Reindex(mulliganSide, 16);
        LocationCards(mulliganSide, 16, ordered);
        for (i = 0; i < ordered.Size(); i += 1)
        { t = ordered[i].Snapshot(); if (t.locationIndex >= deckIndex) ordered[i].Move(mulliganSide, 16, t.locationIndex + 1); }
        outgoing.Move(mulliganSide, 16, deckIndex); Reindex(mulliganSide, 16);MonsterMoved(s);NilfSwapped(outgoing); mulliganUsed += 1;
        BetaGwentLog("DUEL_MULLIGAN_SWAP request=" + requestId + " outgoing=" + item
            + " incoming=" + incomingId + " index=" + deckIndex + " used=" + mulliganUsed + " draws=" + random.DrawCount());
        RefreshMulligan();
        if (mulliganUsed >= mulliganBudget) FinishMulligan(id);
        return !fatal;
    }
    public function FinishMulligan(id : int) : bool
    {
        if (fatal || !mulligan || id != requestId) return false;
        if (mulliganSide == 2)
        {
            mulliganSide = 1; mulliganUsed = 0;
            blacklistedTemplates.Clear(); reservedCards.Clear(); pendingIds.Clear();
            requestId += 1; RefreshMulligan();
            if (pendingIds.Size() == 0 || CountLocation(1, 16) == 0) return FinishMulligan(requestId);
            return !fatal;
        }
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
    public function HasRequiredPlayTarget(card : CBetaGwentDuelCard) : bool
    {
        var d : SBetaGwentDuelDefinition;var source,target : SBetaGwentCardSnapshot;var i : int;
        if(!card)return false;if(card.TemplateId()!=113201)return true;
        d=card.Definition();source=card.Snapshot();
        return HasRequiredPlayTargetForSide(d,source.positionPlayerId);
    }
    public function HasRequiredPlayTargetForSide(d : SBetaGwentDuelDefinition, side : int) : bool
    {
        var target : SBetaGwentCardSnapshot;var i : int;
        if(d.header.templateId!=113201)return true;
        for(i=0;i<live.Size();i+=1){target=live[i].Snapshot();
            if(target.positionPlayerId==side && MatchesCardTarget(target,d))return true;}
        return false;
    }
    // UI hint only; the authoritative methods below validate before ClaimInitialMove.
    public function DirectSpecialKind(d : SBetaGwentDuelDefinition) : int
    {
        if (d.header.typeMask != 2) return 0;
        if (d.effect == 28) {
            // Automatic enemy-wide effects are cast onto the enemy half.
            // Kind 3 is a cast area hint, never a new row restriction.
            if(d.specialRequest==0)return 3;
            return d.specialRequest;
        }
        if (d.weatherToken != 0 || d.effect == 4) return 2;
        if (d.effect == 29 || d.effect == 10 || d.effect == 9 || d.effect == 14) return 3;
        if (d.effect == 1 || d.effect == 2 || d.effect == 3 || d.effect == 6
            || d.effect == 18 || d.effect == 19 || d.effect == 20 || d.effect == 22) return 1;
        return 0;
    }
    // Static public geometry only. No RNG, mutation, hidden target or resolved score.
    public function ActionPreviewGeometry(d : SBetaGwentDuelDefinition) : string
    {
        var scope,radius : int;
        if(d.effect==3){scope=1;radius=1;}
        if(d.effect==4)scope=3;
        if(d.weatherToken!=0)scope=4;
        if(d.effect==28){
            if(d.specialMode==7 || d.specialMode==8){scope=2;radius=d.specialRadius;}
            if(d.specialMode==9 || d.specialMode==10 || d.specialMode==13)scope=3;
            if(d.specialMode==20)scope=6;
            if(d.specialMode==37 || d.specialMode==15)scope=4;
            if(d.specialMode==15 && d.specialCount==2)scope=5;
        }
        return ""+scope+","+radius+","+d.unitTraits+","+d.targetExcludedTraits;
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
        if (s.positionPlayerId != side || s.locationMask != 8 || !s.canBePlayed || !HasRequiredPlayTarget(card)) return false;
        placementSide = MonsterPlaySide(card, side); index = CountLocation(placementSide, row);
        if (requestedIndex != -3) index = requestedIndex;
        if (d.header.typeMask == 4 && !CanInsertUnit(placementSide, row, index)) return false;
        if (!Require(match.ClaimInitialMove(side))) return false;
        RecordChaseHandPlay(side);
        card.playFromLocation = s.locationMask; card.SetPlayable(false);
        if (d.header.typeMask == 4)
        {
            if (!InsertUnit(card, side, row, index)) { FailAbility("Не удалось разместить отряд."); return false; }
        }
        else card.Move(side, 256, 0);
        Reindex(side, 8); message = d.title;
        SetVisualSource(instanceId, d.header.templateId, side, row);
        if (side == 1) RecordVisual(1, instanceId, "Вы: " + d.title, 480);
        else if (HiddenAmbushPlay(side, d)) { SetVisualSource(instanceId, 0, side, row); RecordVisual(1, instanceId, "Соперник: засада", 480); }
        else RecordVisual(1, instanceId, "Соперник: " + d.title, 480);
        BetaGwentLog("DUEL_PLAY player=" + side + " template=" + d.header.templateId + " row=" + row + " index=" + index);
        if(side==1 && placementSide==1 && d.header.typeMask==4 && aiEnemyRowPlays.Size()==3){
            if(row==1)aiEnemyRowPlays[0]=aiEnemyRowPlays[0]+1;else if(row==2)aiEnemyRowPlays[1]=aiEnemyRowPlays[1]+1;else if(row==4)aiEnemyRowPlays[2]=aiEnemyRowPlays[2]+1;}
        if(UsesInternalPolicy(side) && !aiSimulating && d.header.typeMask==4)
            BetaGwentLog("DUEL_AI_PLACEMENT template="+d.header.templateId+" row="+row+" cost="+AiRowPlacementCost(placementSide,row,d)
                +" hazards="+weather.Hazard(placementSide,1)+":"+weather.Hazard(placementSide,2)+":"+weather.Hazard(placementSide,4));
        StartPlayResolution(card, side);
        return !fatal;
    }
    public function UseLeader(side : int) : bool
    {
        var card : CBetaGwentDuelCard; var row : int;
        if (!CanAct(side)) return false;
        card = Leader(side); if (!card) return false;
        if (IsExternalPolicy(side)) row = FirstOpenRow(MonsterPlaySide(card,side));
        else row = BestCardRow(side, card.Definition());
        if (row == 0) return false;
        if(UsesInternalPolicy(side))AiExplainPlacement(card,row,0);
        if (IsManualDecisionSide(side))
        {
            pendingLeader = card; pendingIds.Clear(); requestId += 1;
            message = "Выберите место лидера: нажмите союзника, чтобы встать перед ним, или пустое место своего ряда. До размещения можно отменить.";
            BetaGwentLog("DUEL_LEADER_ROW_BEGIN request=" + requestId);
            return true;
        }
        return PlaceLeader(card, side, row, -3);
    }
    private function RecordChaseHandPlay(side : int)
    {
        var m : SBetaGwentMatchSnapshot;m=match.Snapshot();
        if(side!=2 || !m.playerOne.hasPassed)return;
        if(aiChaseRound!=m.roundNumber){aiChaseRound=m.roundNumber;aiChaseSpent=0;}
        aiChaseSpent+=1;
    }
    private function PlaceLeader(card : CBetaGwentDuelCard, side : int, row : int, requestedIndex : int) : bool
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!card || !CanInsertUnit(MonsterPlaySide(card,side), row, requestedIndex)) return false;
        s = card.Snapshot();
        if (s.positionPlayerId != side || s.locationMask != 64 || !s.canBePlayed) return false;
        if (!Require(match.ClaimInitialMove(side))) return false;
        card.playFromLocation=64;
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
        if(!HasRequiredPlayTarget(card)){BetaGwentLog("DUEL_NESTED_SKIP template=113201 reason=no_legal_decoy_target");CompletePlay(parentCard);return;}
        if ((s.locationMask != 16 && s.locationMask != 32 && s.locationMask != 128 && s.locationMask != 8) || s.positionPlayerId != NorthActingSide(parentCard))
        { FailAbility("Карта вложенного розыгрыша отсутствует в своей колоде или сбросе."); return; }
        for (i = 0; i < playStack.Size(); i += 1)
            if (playStack[i] == card) { FailAbility("Повторный розыгрыш той же карты в стеке."); return; }
        if (d.header.typeMask == 4 && !CanInsertUnit(MonsterPlaySide(card, s.positionPlayerId), row, requestedIndex))
        { FailAbility("Нет места для вложенного отряда."); return; }
        pendingCard = NULL; pendingRally = NULL; pendingChoice = false; pendingRow = false; pendingPileChoice = false; pendingIds.Clear();
        d = parentCard.Definition(); if (d.effect == 29 || d.effect == 34) parentCard.StorePlayedChild(card); d = card.Definition();
        card.playFromLocation = s.locationMask; card.SetPlayable(false);
        // Emhyr spends a hand card inside his leader action. A tutor from deck
        // or grave does not; Dandelion's draw/play is already one hand action.
        if(s.locationMask==8 && parentCard.TemplateId()==200162)RecordChaseHandPlay(s.positionPlayerId);
        if (d.header.typeMask == 4)
        { if (!InsertUnit(card, s.positionPlayerId, row, requestedIndex)) { FailAbility("Не удалось разместить вложенный отряд."); return; } }
        else card.Move(s.positionPlayerId, 256, 0);
        Reindex(s.positionPlayerId, s.locationMask); SetVisualSource(s.instanceId, d.header.templateId, s.positionPlayerId, row);
        if (s.locationMask == 32) RecordVisual(1, s.instanceId, "Из сброса → " + d.title, 480);
        else if (s.locationMask == 128) RecordVisual(1, s.instanceId, "Создан → " + d.title, 480);
        else if (s.locationMask == 8) RecordVisual(1, s.instanceId, "Повторный розыгрыш → " + d.title, 480);
        else if (HiddenAmbushPlay(s.positionPlayerId, d)) { SetVisualSource(s.instanceId, 0, s.positionPlayerId, row); RecordVisual(1, s.instanceId, "Из колоды → засада", 480); }
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
        if (pendingIds.Size() == 0)
        {
            // Stage 127: a fizzled ability gets its own visual beat (silent: audio kind 8).
            message = d.title + ": подходящих карт нет."; s = source.Snapshot(); RecordVisual(18, s.instanceId, d.title + ": нет целей", 620, 8);
            CompletePlay(source); return;
        }
        if (d.pilePickMode != 0) { SelectPileCard(pendingIds[0]); return; }
        if (UsesInternalPolicy(side))
        {
            bestValue = -2147483647;
            for (i = 0; i < pendingIds.Size(); i += 1)
            { candidate = registry.Find(pendingIds[i]); s = candidate.Snapshot(); value = AiPileCandidateValue(candidate,side,false,0);
              AiExplain("PILE_OPTION","source="+source.TemplateId()+" target="+s.instanceId+" template="+candidate.TemplateId()+" value="+value+" reason=legal_targets_and_nested_effect");
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
        row = RequestedPlacementRow(child,s.positionPlayerId);
        if (row == 0) { message = "Нет места для выбранного отряда."; CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        if (UsesInternalPolicy(NilfDecisionSide())) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
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
        s = child.Snapshot(); row = RequestedPlacementRow(child, s.positionPlayerId);
        if (row == 0) { child.Move(s.positionPlayerId, 512, 0); CompletePlay(source); return; }
        pendingRally = child; requestId += 1;
        m = match.Snapshot(); if (UsesInternalPolicy(NilfDecisionSide())) { PlaceRally(s.positionPlayerId, BestNestedRow(child), AiAdjacencyIndex(child, BestNestedRow(child))); return; }
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
            row = RequestedPlacementRow(target,side); if (row == 0) { target.SetPlayable(true); CompletePlay(source); return; }
            if (UsesInternalPolicy(NilfDecisionSide())) { PlaceRally(side, BestNestedRow(target), AiAdjacencyIndex(target, BestNestedRow(target))); return; }
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
    private function RecordNoTargets(source : CBetaGwentDuelCard)
    {
        var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        if (!source) return;
        s = source.Snapshot(); d = source.Definition();
        message = d.title + ": подходящих карт нет.";
        RecordVisual(18, s.instanceId, d.title + ": нет целей", 620, 8);
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
        { RecordNoTargets(source); CompletePlay(source); return; }
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
        if (pendingIds.Size() == 0) { RecordNoTargets(card); ApplyCardTarget(0); return; }
        if (UsesInternalPolicy(side)) { ApplyCardTarget(BestTarget(side, d.effect, 0)); return; }
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
            if (UsesInternalPolicy(side)) ResolveModeChoice(BestModeChoice(cardDefinition, side));
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
            if (UsesInternalPolicy(side)) ResolveDagonChoice(ChooseDagonWeather(side));
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
            if (UsesInternalPolicy(side)) ResolveFirstLight(ChooseFirstLight(side));
            return;
        }
        if (cardDefinition.consumeLocation == 32) { ResolveGraveChoice(card, side); return; }
        if (cardDefinition.effect == 28 && (cardDefinition.specialMode == 22 || cardDefinition.specialMode == 23))
        { BeginHandPower(card); return; }
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (MatchesCardTarget(s, cardDefinition))
            {
                if (!CanDeployTarget(card, live[i])) continue;
                if ((cardDefinition.effect == 16 || cardDefinition.effect == 17) && !CanConsume(card, live[i])) continue;
                if (cardDefinition.targetSide == 2 && s.positionPlayerId != BetaGwentOpponentId(side)) continue;
                if (cardDefinition.targetSide == 1 && s.positionPlayerId != side) continue;
                if (cardDefinition.consumeMaximum > 0 && s.power.currentPower > cardDefinition.consumeMaximum) continue;
                if (cardDefinition.effect == 28 && cardDefinition.specialMode == 29 && CountLocation(side, s.locationMask) >= 9) continue;
                pendingIds.PushBack(s.instanceId);
            }
        }
        // Initial empty pool only: voluntarily finishing an optional choice or
        // running out of targets after a successful hit is not a failed ability.
        if (!pendingRow && pendingIds.Size() == 0)
        { RecordNoTargets(card); ApplyCardTarget(0); return; }
        if (UsesInternalPolicy(side))
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
        if (s.runtimeTemplate.typeMask == 2 && !(nilfJob && nilfJob.source==card && nilfJob.kind!=8))
        {
            if((s.tokenMask&512)!=0)card.Move(s.positionPlayerId,512,0);
            else
            {
                card.Move(s.positionPlayerId,32,CountLocation(s.positionPlayerId,32));
                RecordVisual(19,s.instanceId,"",440);
            }
        }
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
            s.playerId = RequestDecisionSide(); s.targetPlayerId = s.playerId; s.kind = BG_RequestChoices;
            s.limits.minimum = 0; s.limits.maximum = mulliganBudget; s.selectedCount = mulliganUsed;
            return s;
        }
        if (pendingLeader)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId;
            s.playerId = RequestDecisionSide(); s.targetPlayerId = s.playerId; s.kind = BG_RequestTargets;
            s.limits.minimum = 0; s.limits.maximum = 1; return s;
        }
        if (pendingCard && pendingCard.IsMonsterAbility() && !pendingRally)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId; s.playerId = RequestDecisionSide(); s.targetPlayerId = s.playerId;
            s.kind = BG_RequestTargets; if (pendingChoice || pendingPileChoice) s.kind = BG_RequestChoices;
            s.limits.minimum = monsterMinimum; s.limits.maximum = monsterMaximum; s.selectedCount = pendingCard.monsterIds.Size();
            if (pendingCard.MonsterMode() != 18) s.selectedCount = 0;
            if (OptionalChoiceLimit(pendingCard) > 0) s.selectedCount = pendingCard.monsterIds.Size();
            // Saskia's original follow-up requests the replacement set once.
            // UI SelectTarget drains it one card at a time; expose the actual
            // still-required count so an external policy can choose that set.
            if(pendingCard.TemplateId()==200209 && pendingCard.monsterStage==1)
            { s.limits.minimum=pendingCard.monsterRemaining;s.limits.maximum=pendingCard.monsterRemaining; }
            return s;
        }
        if (pendingChoice)
        {
            s.initialized = true; s.applied = true; s.requestId = requestId;
            s.playerId = RequestDecisionSide(); s.targetPlayerId = s.playerId; s.kind = BG_RequestChoices;
            s.limits.minimum = 1; s.limits.maximum = 1; return s;
        }
        d = pendingCard.Definition(); s.initialized = true; s.applied = true; s.requestId = requestId;
        s.playerId = RequestDecisionSide(); s.targetPlayerId = s.playerId; s.kind = BG_RequestTargets; s.limits.maximum = 1;
        s.limits.minimum = 1;
        if(d.effect==28 && d.specialMode==17)s.limits.maximum=Max(1,specialHitsLeft);
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
        if(d.header.templateId==113201)s.limits.minimum=1;
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
            v.factionId = d.header.factionMask; v.revealed = pendingChoice || !(s.locationMask==8 && s.positionPlayerId==2 && (s.tokenMask&64)==0); v.selected = false;if(!v.revealed){v.title="Скрытая карта противника";v.templateId=0;v.factionId=0;}output.PushBack(v);
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
        if (!fatal && IsPending() && pendingCard && pendingCard.IsMonsterAbility() && !pendingRally && id == requestId && monsterMinimum == 0)
        { monsters.Select(pendingCard, 0); return !fatal; }
        if (!IsPending() || mulligan || pendingChoice || pendingRally || id != requestId || s.limits.minimum != 0) return false;
        if (pendingPileChoice) { CompletePlay(pendingCard); return !fatal; }
        if (IsWeatherRowRequest()) { CompletePlay(pendingCard); return !fatal; }
        if (pendingRow)
        {
            if (!pendingCard) return false;
            // White Frost's empty selection takes the source graph's false branch (Ranged + Siege).
            d = pendingCard.Definition(); if (d.header.templateId == 113206) ApplyRowTarget(BetaGwentOpponentId(NorthActingSide(pendingCard)), 2);
            else CompletePlay(pendingCard);
            return !fatal;
        }
        ApplyCardTarget(0); return !fatal;
    }
    public function SelectPlacementBefore(id : int, anchorId : int) : bool
    {
        var card : CBetaGwentDuelCard; var a, s : SBetaGwentCardSnapshot;
        var m : SBetaGwentMatchSnapshot;
        var actor : int;
        if (fatal || waiting || id != requestId || (!pendingLeader && !pendingRally)) return false;
        m = match.Snapshot();
        if (!m.turnActive || m.matchWinnerMask != 0 || !IsManualDecisionSide(RequestDecisionSide())) return false;
        if (pendingLeader)
        {
            card = pendingLeader; s = card.Snapshot();
            actor = s.positionPlayerId;
            if (m.currentPlayerId != actor || !ReadPlacementAnchor(MonsterPlaySide(card,actor), anchorId, a)
                || s.locationMask != 64 || !s.canBePlayed) return false;
            if ((actor == 1 && m.playerOne.hasMadeInitialMoveForCurrentTurn) || (actor == 2 && m.playerTwo.hasMadeInitialMoveForCurrentTurn)) return false;
            pendingLeader = NULL;
            return PlaceLeader(card, actor, a.locationMask, a.locationIndex);
        }
        s = pendingRally.Snapshot();
        actor = s.positionPlayerId;
        if (!IsManualDecisionSide(actor) || !ReadPlacementAnchor(MonsterPlaySide(pendingRally, actor), anchorId, a)) return false;
        if ((!IsReactionPlacement() && (!pendingCard || playStack.Size() == 0 || playStack[playStack.Size() - 1] != pendingCard))
            || (s.locationMask != 16 && s.locationMask != 32 && s.locationMask != 128 && s.locationMask != 8) || s.runtimeTemplate.typeMask != 4) return false;
        PlaceRally(actor, a.locationMask, a.locationIndex); return !fatal;
    }
    // Read-only authoritative pool for external controllers. Keep validation
    // shared with SelectRow instead of reconstructing a second set of rules.
    public function CanSelectRow(id : int, side : int, row : int) : bool
    {
        var m : SBetaGwentMatchSnapshot; var d : SBetaGwentDuelDefinition;
        var cardState : SBetaGwentCardSnapshot; var actor : int;
        if (fatal || id != requestId || (side != 1 && side != 2) || (row != 1 && row != 2 && row != 4)) return false;
        if (IsCaranthirMoveRequest())
        { cardState = pendingCard.Snapshot(); return side == BetaGwentOpponentId(cardState.positionPlayerId) && row == cardState.locationMask; }
        if (!IsRowRequest()) return false;
        if (pendingLeader)
        {
            m = match.Snapshot(); actor = RequestDecisionSide();
            return IsManualDecisionSide(actor) && side == MonsterPlaySide(pendingLeader,actor)
                && CountLocation(side,row) < 9 && m.turnActive && m.currentPlayerId == actor;
        }
        if (pendingRally)
        {
            cardState = pendingRally.Snapshot(); actor = cardState.positionPlayerId;
            return IsManualDecisionSide(RequestDecisionSide()) && IsManualDecisionSide(actor)
                && side == MonsterPlaySide(pendingRally,actor) && CountLocation(side,row) < 9;
        }
        d = pendingCard.Definition();
        if (d.effect == 34 && pendingRow) return ValidMonsterRow(side,row);
        if (IsWeatherRowRequest() && side != BetaGwentOpponentId(NorthActingSide(pendingCard))) return false;
        if (d.effect == 28 && !specials.ValidRow(d,NorthActingSide(pendingCard),side,row)) return false;
        return true;
    }
    public function SelectRow(id : int, side : int, row : int) : bool
    {
        var card : CBetaGwentDuelCard; var cardState : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition; var actor : int;
        if (!CanSelectRow(id,side,row)) return false;
        if (IsCaranthirMoveRequest()) return FinishTarget(id);
        if (pendingLeader)
        { actor = RequestDecisionSide(); card = pendingLeader; pendingLeader = NULL; return PlaceLeader(card,actor,row,-3); }
        if (pendingRally)
        { cardState = pendingRally.Snapshot(); PlaceRally(cardState.positionPlayerId,row,-3); return !fatal; }
        d = pendingCard.Definition();
        if (d.effect == 34 && pendingRow) { monsters.Row(pendingCard,side,row); return !fatal; }
        ApplyRowTarget(side,row); return !fatal;
    }
    private function ApplyCardTarget(id : int)
    {
        var source, target : CBetaGwentDuelCard; var cardDefinition, targetDefinition : SBetaGwentDuelDefinition;
        var s, t : SBetaGwentCardSnapshot; var amount, i, offset : int;
        source = pendingCard; if (!source) return;
        cardDefinition = source.Definition(); s = source.Snapshot(); target = registry.Find(id);
        if (target && !CanDeployTarget(source, target)) { CompletePlay(source); return; }
        if (target && (cardDefinition.effect == 16 || cardDefinition.effect == 17) && !CanConsume(source, target))
        { CompletePlay(source); return; }
        if (cardDefinition.effect == 34) { monsters.Select(source, id); return; }
        if (cardDefinition.effect == 28 && cardDefinition.specialMode >= 25 && cardDefinition.specialMode <= 35)
        { ResolveExpandedTarget(source, target); return; }
        if (cardDefinition.effect == 28 && (cardDefinition.specialMode == 22 || cardDefinition.specialMode == 23))
        {
            if (!target) { CompletePlay(source); return; }
            if (pendingHandPower)
            { handPowerTarget = id; BeginHandPowerBoard(source); return; }
            t = registry.Find(handPowerTarget).Snapshot(); amount = t.power.basePower;
            if (cardDefinition.specialMode == 23) amount = -amount;
            QueuePower(target, amount, false); CompletePlay(source); return;
        }
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
                if (!QueueConsume(source, target)) { CompletePlay(source); return; } if (!FlushEffects()) return;
                QueuePower(source, amount, false);
                BetaGwentLog("DUEL_CONSUME_BOOST source=" + s.instanceId + " cachedPower=" + amount);
            }
            else if (cardDefinition.effect == 17)
            {
                if (!MatchesGraveConsume(t, s.positionPlayerId, cardDefinition))
                { FailAbility("Недопустимая карта для поглощения из сброса."); return; }
                amount = t.power.currentPower;
                if (!QueueConsume(source, target)) { CompletePlay(source); return; } if (!FlushEffects()) return;
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
        else if (UsesInternalPolicy(a.positionPlayerId)) ApplyCardTarget(BestTarget(2, 28, d.amount));
    }
    private function BeginHandPower(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var a, s : SBetaGwentCardSnapshot;
        var i, bestId, bestPower : int; var cards : array<CBetaGwentDuelCard>;
        d = source.Definition(); a = source.Snapshot(); handPowerTarget = 0;
        pendingIds.Clear(); pendingHandPower = true; pendingPileChoice = false; requestId += 1;
        GetZoneCards(a.positionPlayerId, 8, cards); bestPower = -1;
        for (i = 0; i < cards.Size(); i += 1)
        {
            s = cards[i].Snapshot(); if (s.runtimeTemplate.typeMask != 4 || (s.runtimeTierMask & 6) == 0) continue;
            pendingIds.PushBack(s.instanceId);
            if (s.power.basePower > bestPower) { bestId = s.instanceId; bestPower = s.power.basePower; }
        }
        message = d.title + ": выберите бронзовый или серебряный отряд в своей руке. Карта останется в руке.";
        if (pendingIds.Size() == 0) { RecordNoTargets(source); CompletePlay(source); }
        else if (UsesInternalPolicy(a.positionPlayerId)) ApplyCardTarget(bestId);
    }
    private function BeginHandPowerBoard(source : CBetaGwentDuelCard)
    {
        var d : SBetaGwentDuelDefinition; var a, s : SBetaGwentCardSnapshot; var i : int;
        d = source.Definition(); a = source.Snapshot(); pendingHandPower = false; pendingIds.Clear(); requestId += 1;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (!MatchesCardTarget(s,d) || !CanDeployTarget(source,live[i])) continue;
            if (d.targetSide == 2 && s.positionPlayerId != BetaGwentOpponentId(a.positionPlayerId)) continue;
            if (d.targetSide == 1 && s.positionPlayerId != a.positionPlayerId) continue;
            pendingIds.PushBack(s.instanceId);
        }
        message = d.title + ": выберите отряд на поле.";
        if (pendingIds.Size() == 0) { RecordNoTargets(source); CompletePlay(source); }
        else if (UsesInternalPolicy(a.positionPlayerId)) ApplyCardTarget(BestTarget(2,28,d.amount));
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
    private function ModeValue(base : SBetaGwentDuelDefinition, choice : int, side : int, optional immediate : bool) : int
    {
        var d, targetDefinition : SBetaGwentDuelDefinition; var s : SBetaGwentCardSnapshot; var i, value, maximum, count, total : int;
        d = BetaGwentDuelModeDefinition(base, choice); maximum = -2147483647;
        if(immediate && d.specialMode==37 && d.specialToken==256)return 0;
        if(d.effect==10)return weather.ClearValue(side,d.amount,AiHorizon(side)==0);
        if (d.specialRequest == 2) return specials.BestRow(d, side, i, count);
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); targetDefinition = live[i].Definition();
            if (d.effect == 29)
            {
                if (s.positionPlayerId != side || s.locationMask != d.pileLocation || s.isWaitingToDie || (s.runtimeTemplate.typeMask&d.targetTypes)==0
                    || (d.consumeMaximum>0 && s.power.currentPower>d.consumeMaximum)
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
        if (IsExternalPolicy(s.positionPlayerId)) row = FirstOpenRow(MonsterPlaySide(card,s.positionPlayerId));
        else row = BestCardRow(s.positionPlayerId, d);
        if (row == 0) { message = "Нет места для отряда Рассвета."; CompletePlay(source); return; }
        pendingRally = card; requestId += 1;
        message = "Рассвет → " + d.title + ": нажмите союзника для размещения перед ним или пустое место своего ряда.";
        if (UsesInternalPolicy(s.positionPlayerId))
        {
            if (d.effect == 23) anchor = BestVranAnchor(2);
            if (anchor > 0)
            { unitState = registry.Find(anchor).Snapshot(); PlaceRally(2, unitState.locationMask, unitState.locationIndex); }
            else PlaceRally(2, row, AiAdjacencyIndex(card,row));
        }
    }
    private function IsReactionPlacement() : bool
    { return nilfJob && pendingRally && pendingCard==pendingRally && nilfJob.source==pendingRally && playStack.Size()==0; }
    private function PlaceRally(side : int, row : int, requestedIndex : int)
    {
        var source, card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot;
        source = pendingCard; card = pendingRally; if (!source || !card) return;
        s = card.Snapshot();
        BetaGwentLog("DUEL_RALLY_PLACE side=" + side + " card=" + s.instanceId + " row=" + row);
        if (IsReactionPlacement())
        {
            pendingCard=NULL;pendingRally=NULL;pendingIds.Clear();
            card.playFromLocation=s.locationMask;
            if(!InsertUnit(card,side,row,requestedIndex)){FailAbility("Нет места для отряда реакции.");return;}
            Reindex(s.positionPlayerId,s.locationMask);card.SetPlayable(false);StartPlayResolution(card,side);return;
        }
        PlayFromPile(source, card, row, requestedIndex);
    }
    // Cards that affect units on both sides of themselves go to the middle of the row.
    public function AiAdjacencyIndex(card : CBetaGwentDuelCard, row : int) : int
    {
        var s,t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;var id, count,supportRow,supportIndex : int;var victim : CBetaGwentDuelCard;
        if (!card) return -3; s = card.Snapshot(); id = s.runtimeTemplate.templateId;
        if(id==162205 && AiFringillaSlot(s.positionPlayerId,supportRow,supportIndex,count) && supportRow==row)return supportIndex;
        d=card.Definition();if(AiFringillaSetup(s.positionPlayerId,d,supportRow,supportIndex,count) && supportRow==row)return supportIndex;
        if(id==200115){victim=AiAssassinVictim(s.positionPlayerId);if(victim){t=victim.Snapshot();if(t.locationMask==row)return t.locationIndex+1;}return -3;}
        d=card.Definition();if(AiSpyDisruptionSlot(s.positionPlayerId,d,row,supportRow,supportIndex,count))return supportIndex;
        d=card.Definition();if(d.effect==23){count=BestVranAnchor(s.positionPlayerId);if(count>0){t=FindCard(count).Snapshot();if(t.locationMask==row)return t.locationIndex;}return -3;}
        if(AiVranFoodSlot(s.positionPlayerId,d,supportRow,supportIndex) && supportRow==row)return supportIndex;
        if(AiShipSlot(s.positionPlayerId,d,supportRow,supportIndex) && supportRow==row)return supportIndex;
        if(AiSupportSlot(s.positionPlayerId,d,supportRow,supportIndex) && supportRow==row)return supportIndex;
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
        var s,t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var row,side : int;
        s=card.Snapshot();d=card.Definition();side=MonsterPlaySide(card,s.positionPlayerId);
        row=BestCardRow(s.positionPlayerId,d);
        if(d.effect==23){side=BestVranAnchor(s.positionPlayerId);if(side>0){t=FindCard(side).Snapshot();row=t.locationMask;}side=MonsterPlaySide(card,s.positionPlayerId);}
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
    private function BestDeployRow(side : int, effect : int, optional definitionId : int) : int
    {
        var row, best, value, maximum : int;
        best = BestOwnRow(side,definitionId); if (effect != 15) return best;
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
    // Damage to the left neighbour requires choosing both the row and insertion index.
    private function AiAssassinVictim(side : int) : CBetaGwentDuelCard
    {
        var i, value, maximum : int; var target, best : CBetaGwentDuelCard; var t : SBetaGwentCardSnapshot;
        maximum = -2147483647;
        for(i=0;i<live.Size();i+=1){
            target=live[i];t=target.Snapshot();
            if(t.positionPlayerId==side || (t.locationMask&7)==0 || t.isWaitingToDie || (t.tokenMask&264)!=0 || CountLocation(t.positionPlayerId,t.locationMask)>=9)continue;
            value=DamageValue(t,side,10)*10;
            if(t.power.currentPower<=Max(0,10-t.power.armor))value+=Max(0,LockToggleValue(t,side))*3;
            if(value>maximum){maximum=value;best=target;}
        }
        return best;
    }
    // Olgierd returns at turn end through North mode146, not the generic
    // deathwish fields. Feed him directly to an active Vran when this is better
    // than the existing right-hand meal. Shared by normal and simulated plays.
    private function AiVranFoodSlot(side : int, d : SBetaGwentDuelDefinition, out bestRow : int, out bestIndex : int) : bool
    {
        var placed,v,t : SBetaGwentCardSnapshot;var vd : SBetaGwentDuelDefinition;
        var i,j,value,maximum,food,existing : int;var m : SBetaGwentMatchSnapshot;
        if(d.header.templateId!=112207 || d.header.typeMask!=4 || BetaGwentDuelSpying(d.header.templateId))return false;
        placed.runtimeTemplate=d.header;placed.runtimeTierMask=d.header.tierMask;placed.positionPlayerId=side;
        placed.instanceId=-1;placed.tokenMask=d.tokens;placed.power.currentPower=d.header.power;placed.power.basePower=d.header.power;
        m=match.Snapshot();maximum=0;
        for(i=0;i<live.Size();i+=1){v=live[i].Snapshot();vd=live[i].Definition();
            if(v.positionPlayerId!=side || vd.effect!=23 || (v.locationMask&7)==0
                || (v.tokenMask&12)!=0 || v.isWaitingToDie || v.timerValue<=0 || CountLocation(side,v.locationMask)>=9)continue;
            if(v.timerValue>1 && (m.playerOne.hasPassed || AiHorizon(side)<v.timerValue))continue;
            placed.locationMask=v.locationMask;placed.locationIndex=v.locationIndex+1;
            food=TargetValue(placed,side,16,2147483647)+d.header.power;existing=0;
            for(j=0;j<live.Size();j+=1){t=live[j].Snapshot();
                if(t.positionPlayerId==side && t.locationMask==v.locationMask && t.locationIndex==v.locationIndex+1)
                    existing=TargetValue(t,side,16,2147483647);
            }
            value=(food-existing)*4-AiRowPlacementCost(side,v.locationMask,d)*4;
            if(value>maximum){maximum=value;bestRow=v.locationMask;bestIndex=v.locationIndex+1;}
        }
        return maximum>0;
    }
    // Dimun needs a unit on its right; Holger also strengthens the unit on its left.
    // Use the same row/index in simulation, ordinary plays and nested summons.
    private function AiShipRightGain(t : SBetaGwentCardSnapshot, side : int) : int
    {
        var value : int;
        if(t.isWaitingToDie || (t.tokenMask&8)!=0)return 0;
        value=DamageValue(t,side,1);
        if((t.tokenMask&4)==0 && (t.runtimeTemplate.templateId==200040 || t.runtimeTemplate.templateId==200042))value+=2;
        if(t.power.currentPower<=Max(0,1-t.power.armor))value-=AiEngineValue(t,side);
        return value;
    }
    private function AiShipSlot(side : int, d : SBetaGwentDuelDefinition, out bestRow : int, out bestIndex : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var l,r : SBetaGwentCardSnapshot;
        var row,i,value,maximum,horizon : int;
        if(d.header.templateId!=152309 && d.header.templateId!=152109)return false;
        maximum=-2147483647;horizon=Min(3,AiHorizon(side));
        for(row=1;row<=4;row*=2){
            LocationCards(side,row,cards);if(cards.Size()>=9)continue;
            for(i=0;i<=cards.Size();i+=1){
                value=-AiRowPlacementCost(side,row,d)*4+cards.Size()*3;
                if(i<cards.Size()){
                    r=cards[i].Snapshot();
                    if((r.tokenMask&8)==0)value+=(AiShipRightGain(r,side)+BetaGwentNorthPick(d.header.templateId==152309,2,0))*horizon*4;
                }
                if(i>0){
                    l=cards[i-1].Snapshot();
                    if(d.header.templateId==152109 && (l.tokenMask&8)==0)value+=horizon*4;
                    // Do not replace an existing ship's profitable right-hand partner with this engine.
                    if(l.runtimeTemplate.templateId==152309 && (l.tokenMask&12)==0 && i<cards.Size())value-=Max(0,AiShipRightGain(r,side))*horizon*4;
                }
                if(value>maximum){maximum=value;bestRow=row;bestIndex=i;}
            }
        }
        return maximum!=-2147483647;
    }
    // Score every insertion slot, including the empty slot to either side of
    // an armoured Redanian Knight. Do not separate two consuming engines.
    private function AiSupportSlot(side : int, d : SBetaGwentDuelDefinition, out bestRow : int, out bestIndex : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var l,r,placed : SBetaGwentCardSnapshot;
        var ld,rd : SBetaGwentDuelDefinition;var row,i,value,maximum,horizon,bonus,j : int;var found,thunder : bool;
        maximum=-2147483647;horizon=Max(1,Min(3,AiHorizon(side)));
        placed.runtimeTemplate=d.header;placed.positionPlayerId=side;placed.power.currentPower=d.header.power;placed.power.armor=d.header.armor;
        if(d.header.typeMask!=4 || BetaGwentDuelSpying(d.header.templateId) || d.effect==23 || AiAdjacencyCard(d.header.templateId) || d.header.templateId==152309 || d.header.templateId==152109)return false;
        for(j=0;j<live.Size();j+=1){l=live[j].Snapshot();if(l.positionPlayerId==side && l.locationMask==8 && l.runtimeTemplate.templateId==113311)thunder=true;}
        for(row=1;row<=4;row*=2){
            LocationCards(side,row,cards);if(cards.Size()>=9)continue;
            for(i=0;i<=cards.Size();i+=1){
                value=-AiRowPlacementCost(side,row,d)*4+cards.Size()*4-cards.Size()/3;bonus=0;
                if(thunder){bonus+=Min(3,cards.Size()+1)*6;found=true;if(AiLanePower(side,row)+d.header.power>=25)bonus-=8;}
                if(i>0){l=cards[i-1].Snapshot();ld=cards[i-1].Definition();
                    if(l.runtimeTemplate.templateId==123301 && l.power.armor>0 && (l.tokenMask&12)==0){bonus+=horizon*4;if(i<cards.Size())bonus-=horizon*4;found=true;}
                    if(d.header.templateId==123301 && (l.tokenMask&8)==0){bonus+=horizon*4;found=true;}
                    if(l.runtimeTemplate.templateId==152309 && (l.tokenMask&12)==0){
                        bonus+=(2+AiShipRightGain(placed,side))*horizon*4;
                        if(i<cards.Size())bonus-=(2+AiShipRightGain(cards[i].Snapshot(),side))*horizon*4;
                        found=true;
                    }
                }
                if(i<cards.Size()){r=cards[i].Snapshot();rd=cards[i].Definition();
                    if(r.runtimeTemplate.templateId==123301 && r.power.armor>0 && (r.tokenMask&12)==0){bonus+=horizon*4;if(i>0)bonus-=horizon*4;found=true;}
                    if(d.header.templateId==123301 && (r.tokenMask&8)==0){bonus+=horizon*4;found=true;}
                    if(rd.effect==23 && (r.tokenMask&4)==0 && d.header.templateId!=132305 && d.deathwishDamage==0 && d.deathwishSpawnCount==0 && d.deathwishSummonTemplate==0)bonus-=40;
                }
                value+=bonus;if(value>maximum){maximum=value;bestRow=row;bestIndex=i;}
            }
        }
        return found;
    }
    private function AiPlacementAnchor(d : SBetaGwentDuelDefinition) : int
    {
        var victim : CBetaGwentDuelCard;var t,n : SBetaGwentCardSnapshot;var i,row,index,anchor,gain : int;
        if(d.header.templateId==162205 && AiFringillaSlot(2,row,index,gain)){
            for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==1 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
            return 0;
        }
        // Stage 127: a spy placed directly left of the strongest enemy unit sets up Fringilla.
        if(AiFringillaSetup(2,d,row,index,gain)){
            for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==1 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
            return 0;
        }
        if(BetaGwentDuelSpying(d.header.templateId)){
            row=BestCardRow(2,d);
            if(AiSpyDisruptionSlot(2,d,row,row,index,gain))for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();
                if(n.positionPlayerId==1 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
        }
        // A general archetype/crew anchor must not override the cleansing row.
        if(AiVranFoodSlot(2,d,row,index)){
            for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==2 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
            return 0;
        }
        if(AiClearsOwnRow(d))return 0;
        if(AiShipSlot(2,d,row,index)){
            for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==2 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
            return 0;
        }
        if(d.header.templateId!=200115){
            anchor=archetypeAI.PlacementAnchor(d);
            if(anchor!=0){
                t=FindCard(anchor).Snapshot();row=BestCardRow(2,d);
                // Crew/adjacency is worthwhile only when it pays for the weather exposure.
                // Clear-weather units and consuming engines keep their purposeful placement.
                if(d.effect==15 || d.effect==23 || weather.Hazard(2,t.locationMask)==0
                    || AiRowPlacementCost(2,t.locationMask,d)<=AiRowPlacementCost(2,row,d)+4)return anchor;
            }
            if(AiSupportSlot(2,d,row,index))for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==2 && n.locationMask==row && n.locationIndex==index)return n.instanceId;}
            return 0;
        }
        victim=AiAssassinVictim(2);if(!victim)return 0;t=victim.Snapshot();
        for(i=0;i<live.Size();i+=1){n=live[i].Snapshot();if(n.positionPlayerId==t.positionPlayerId && n.locationMask==t.locationMask && n.locationIndex==t.locationIndex+1)return n.instanceId;}
        return 0; // Last victim: insert at the end of its row.
    }
    private function BestCardRow(side : int, d : SBetaGwentDuelDefinition) : int
    {
        var row,preferred,actualSide,value,best : int;
        if(AiVranFoodSlot(side,d,preferred,best))return preferred;
        // Harald's ten shots hit the OPPOSING row where he is placed.
        // Empty-row spreading must not send the whole volley into an empty lane.
        if(d.header.templateId==200161){
            best=-2147483647;
            for(row=1;row<=4;row*=2){
                if(CountLocation(side,row)>=9)continue;
                value=AiRowVolleyValue(side,row,10)-AiRowPlacementCost(side,row,d);
                if(value>best){best=value;preferred=row;}
            }
            return preferred;
        }
        if(d.header.templateId==132108)return AiBestMirunaRow(side,d);
        // Woodland's wolves always enter melee; his own row chooses the Fog.
        // Evaluate that Fog even when a deck profile supplies ordinary row AI.
        if (d.header.templateId == 132103) {
            best = -2147483647;
            for (row=1;row<=4;row*=2) {
                if (CountLocation(side,row)>=9) continue;
                value=WeatherValue(side,row,2)-AiRowPlacementCost(side,row,d);
                if (CountLocation(BetaGwentOpponentId(side),row)>0 && weather.Token(BetaGwentOpponentId(side),row)!=2) value+=3;
                if (value>best) {best=value;preferred=row;}
            }
            return preferred;
        }
        if(AiClearsOwnRow(d))return AiBestClearingRow(side,d);
        preferred=EvaluateCardRow(side,d);actualSide=side;
        if(BetaGwentDuelSpying(d.header.templateId))return preferred;
        if(d.header.typeMask!=4 || preferred==0 || weather.Hazard(actualSide,preferred)==0)return preferred;
        // Do not sacrifice an ordinary unit/engine merely for an archetype row preference.
        // Clearing weather, feeding a consumer, and row-bound deathwish abilities are exceptions.
        if(d.effect==15 || d.effect==23 || d.deathwishDamage!=0 || AiAdjacencyCard(d.header.templateId))return preferred;
        for(row=1;row<=4;row*=2){
            if(CountLocation(actualSide,row)>=9 || weather.Hazard(actualSide,row)>0)continue;
            if(AiRowPlacementCost(actualSide,row,d)<AiRowPlacementCost(actualSide,preferred,d))preferred=row;
        }
        return preferred;
    }
    // Public material estimate for a fixed volley, not damage to EVERY unit.
    public function AiRowVolleyValue(side : int, row : int, shots : int) : int
    {
        var i,power,armor : int;var t : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.positionPlayerId==side || t.locationMask!=row || t.isWaitingToDie
                || (t.tokenMask&8)!=0 || t.runtimeTemplate.typeMask!=4)continue;
            power+=Max(0,t.power.currentPower);armor+=Max(0,t.power.armor);
        }
        if(power+armor==0)return 0;
        return Min(shots,power+armor)*power/(power+armor);
    }
    // Only public, legal charm targets count; do not assume the opponent will
    // later populate a row chosen for its empty-row placement bonus.
    public function AiMirunaTargetPower(side : int, row : int) : int
    {
        var i,highest : int; var s : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==BetaGwentOpponentId(side) && s.locationMask==row && !s.isWaitingToDie
                && (s.tokenMask&8)==0 && s.runtimeTemplate.typeMask==4 && (s.runtimeTierMask&15)!=0)
                highest=Max(highest,s.power.currentPower);}
        return highest;
    }
    public function AiBestMirunaRow(side : int, d : SBetaGwentDuelDefinition) : int
    {
        var row,best,value,maximum : int;maximum=-2147483647;
        for(row=1;row<=4;row*=2){
            if(CountLocation(side,row)>=9)continue;
            value=-AiRowPlacementCost(side,row,d);
            // Miruna occupies one slot, and the charmed unit needs another.
            if(CountLocation(side,row)<8)value+=AiMirunaTargetPower(side,row)*2;
            if(value>maximum){maximum=value;best=row;}}
        return best;
    }
    public function AiClearsOwnRow(d : SBetaGwentDuelDefinition) : bool
    {
        // Match the mechanics dispatched by ResolvePlayed, North, Nilf,
        // Skellige and the movement router; applies to created/tutored copies too.
        if(d.header.templateId==142302)return CountLocation(1,1)+CountLocation(1,2)+CountLocation(1,4)+CountLocation(2,1)+CountLocation(2,2)+CountLocation(2,4)>0;
        return d.effect==15 || (d.effect==34 && d.specialMode==116)
            || d.header.templateId==162309 || d.header.templateId==200147;
    }
    public function AiClearDeployGain(d : SBetaGwentDuelDefinition, side : int) : int
    { if(!AiClearsOwnRow(d))return 0;return weather.ClearRowForecast(side,BestCardRow(side,d)); }
    private function AiBestClearingRow(side : int, d : SBetaGwentDuelDefinition) : int
    {
        var row,best,value,maximum : int;
        maximum=-2147483647;
        for(row=1;row<=4;row*=2){
            if(CountLocation(side,row)>=9)continue;
            value=-AiRowPlacementCost(side,row,d);
            if(value>maximum){maximum=value;best=row;}
        }
        return best;
    }
    // Compare public neighbour engines with the same spy appended or inserted.
    // No enemy hand is played: only real turn-start/end queues are advanced on clones.
    // This covers ship damage/healing, Vran meals/deathwishes and repeated adjacent boosts.
    private function AiSpyInsertionForecast(actor : int, d : SBetaGwentDuelDefinition, row : int, index : int, optional summonTemplate : int, optional copies : int) : int
    {
        var g : CBetaGwentDuelSession;var probe : CBetaGwentDuelCard;var m : SBetaGwentMatchSnapshot;var i,limit,result,seeded : int;var t : SBetaGwentCardSnapshot;
        if(actor!=2)return -2147483647;
        BetaGwentAISimEnter();g=AiSimClone();result=-2147483647;
        if(g){
            g.aiNeighbourProbeActive=true;m=match.Snapshot();g.random.Initialize(17041+m.roundNumber*101+row*7919);
            // Hypotheses replace anonymized deck slots, never inspect their real identities.
            if(summonTemplate>0 && copies>0)for(i=0;i<g.live.Size() && seeded<copies;i+=1){t=g.live[i].Snapshot();
                if(t.positionPlayerId==1 && t.locationMask==16 && (t.tokenMask&64)==0){g.live[i].Setup(g,t.instanceId,summonTemplate,1,16,t.locationIndex);seeded+=1;}}
            g.pendingCard=NULL;g.pendingLeader=NULL;g.pendingRally=NULL;g.pendingIds.Clear();g.pendingChoice=false;g.pendingRow=false;g.pendingPileChoice=false;g.playStack.Clear();
            g.NeutralCopy(actor,d.header.templateId,8);probe=g.live[g.live.Size()-1];
            if(g.InsertUnit(probe,actor,row,index)){
                g.FlushDeaths();limit=Min(4,Max(2,AiHorizon(actor)*2));
                for(i=0;i<limit;i+=1){m=g.match.Snapshot();if(g.fatal || g.IsPending() || g.waiting || m.matchWinnerMask!=0)break;g.FinishTurn();}
                if(!g.fatal && !g.IsPending())result=g.Score(actor)-g.Score(BetaGwentOpponentId(actor));
            }
        }
        BetaGwentAISimLeave();return result;
    }
    // Probability of zero/one/two unseen copies in the deck, conditioned only
    // on public copies, the permitted starting list and public hand/deck sizes.
    private function AiSpySummonChances(victim : CBetaGwentDuelCard, out summon : int, out one : int, out two : int) : bool
    {
        var t,s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var i,remaining,deck,hand,slots,none,den : int;
        one=0;two=0;summon=0;if(!victim)return false;t=victim.Snapshot();d=victim.Definition();
        if((t.tokenMask&12)!=0 || t.positionPlayerId!=1 || d.deathwishSummonTemplate==0)return false;
        summon=d.deathwishSummonTemplate;deck=CountLocation(1,16);if(deck==0)return false;
        remaining=BetaGwentNorthPick(t.runtimeTierMask==2,3,1);
        if(BetaGwentAIStrength()>=4 && aiStartingDeckOne.Size()>0){remaining=0;for(i=0;i<aiStartingDeckOne.Size();i+=1)if(aiStartingDeckOne[i]==summon)remaining+=1;}
        hand=CountLocation(1,8);
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0)hand-=1;
            if(s.ownerId!=1 || live[i].createdCopy)continue;
            if((s.locationMask&39)==0 && s.locationMask!=512 && !(s.locationMask==8 && (s.tokenMask&64)!=0))continue;
            if((s.tokenMask&8)==0 && s.runtimeTemplate.templateId==summon)remaining-=1;
        }
        remaining=Min(2,Max(0,remaining));slots=deck+Max(0,hand);if(remaining==0 || slots==0)return false;
        if(remaining==1){one=100*deck/slots;return one>0;}
        den=Max(1,slots*(slots-1));two=100*deck*Max(0,deck-1)/den;
        none=100*Max(0,hand)*Max(0,hand-1)/den;one=Max(0,100-none-two);return one+two>0;
    }
    private function AiSpyDisruptionSlot(actor : int, d : SBetaGwentDuelDefinition, onlyRow : int,
        out bestRow : int, out bestIndex : int, out gain : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var l,r : SBetaGwentCardSnapshot;var ld : SBetaGwentDuelDefinition;
        var side,row,i,value,baseline,horizon,summon,one,two,baseOne,baseTwo,deltaOne,deltaTwo,key : int;
        var m : SBetaGwentMatchSnapshot;var relevant : bool;var observer : CBetaGwentStrategyObserve096;var view : SBetaGwentStrategyView096;
        gain=0;if(actor!=2 || aiNeighbourProbeActive || !BetaGwentDuelSpying(d.header.templateId) || d.header.templateId==162205 || d.header.templateId==200115)return false;
        side=BetaGwentOpponentId(actor);m=match.Snapshot();if(m.playerOne.hasPassed)return false;
        horizon=AiHorizon(actor);if(horizon<=0)return false;
        observer=new CBetaGwentStrategyObserve096 in this;view=observer.Capture(this,actor,true);
        if(aiSpySlotRevision!=view.revision){aiSpySlotRevision=view.revision;aiSpySlotKeys.Clear();aiSpySlotRows.Clear();aiSpySlotIndices.Clear();aiSpySlotGains.Clear();}
        key=d.header.templateId*8+onlyRow;
        for(i=0;i<aiSpySlotKeys.Size();i+=1)if(aiSpySlotKeys[i]==key){bestRow=aiSpySlotRows[i];bestIndex=aiSpySlotIndices[i];gain=aiSpySlotGains[i];return gain>0;}
        for(row=1;row<=4;row*=2){
            if(onlyRow!=0 && row!=onlyRow)continue;
            LocationCards(side,row,cards);if(cards.Size()>=9)continue;baseline=-2147483647;
            for(i=1;i<cards.Size();i+=1){l=cards[i-1].Snapshot();r=cards[i].Snapshot();ld=cards[i-1].Definition();
                if(l.isWaitingToDie || r.isWaitingToDie)continue;
                relevant=(l.tokenMask&12)==0 && (ld.effect==23 && l.timerValue>0 || l.runtimeTemplate.templateId==152309 || l.runtimeTemplate.templateId==152109 || l.runtimeTemplate.templateId==123301);
                relevant=relevant || (r.tokenMask&12)==0 && r.runtimeTemplate.templateId==123301;if(!relevant)continue;
                if(baseline==-2147483647)baseline=AiSpyInsertionForecast(actor,d,row,-3);if(baseline==-2147483647)continue;
                value=AiSpyInsertionForecast(actor,d,row,i);if(value==-2147483647)continue;value-=baseline;
                if(ld.effect==23 && (l.tokenMask&12)==0 && AiSpySummonChances(cards[i],summon,one,two)){
                    baseOne=AiSpyInsertionForecast(actor,d,row,-3,summon,1);baseTwo=AiSpyInsertionForecast(actor,d,row,-3,summon,2);
                    deltaOne=AiSpyInsertionForecast(actor,d,row,i,summon,1);deltaTwo=AiSpyInsertionForecast(actor,d,row,i,summon,2);
                    if(baseOne!=-2147483647 && baseTwo!=-2147483647 && deltaOne!=-2147483647 && deltaTwo!=-2147483647)
                        value=(value*(100-one-two)+(deltaOne-baseOne)*one+(deltaTwo-baseTwo)*two)/100;
                }
                if(value>gain){gain=value;bestRow=row;bestIndex=i;}
            }
        }
        aiSpySlotKeys.PushBack(key);aiSpySlotRows.PushBack(bestRow);aiSpySlotIndices.PushBack(bestIndex);aiSpySlotGains.PushBack(gain);
        return gain>0;
    }
    public function AiBestSpyRow(actor : int, d : SBetaGwentDuelDefinition) : int
    {
        var side,row,best,value,maximum,contact,pull,i,token,index,gain : int;var t,spy : SBetaGwentCardSnapshot;
        if(d.header.templateId==162205 && AiFringillaSlot(actor,row,index,gain))return row;
        if(AiFringillaSetup(actor,d,row,index,gain))return row;
        side=BetaGwentOpponentId(actor);maximum=-2147483647;
        for(row=1;row<=4;row*=2){
            if(CountLocation(side,row)>=9)continue;
            token=weather.Token(side,row);contact=0;
            if(token==512 || token==2048)contact=Max(0,weather.Hazard(side,row)-d.header.armor);
            value=Min(d.header.power,contact)*4+weather.Hazard(side,row)*Min(2,AiHorizon(actor));
            if(token==256 && (d.unitTraits&288)!=0)value-=weather.Boon(side,row)*Min(2,AiHorizon(actor));
            if(d.header.templateId==122206){spy.runtimeTemplate=d.header;spy.positionPlayerId=side;spy.locationMask=row;
                value+=AiSpyDeathwishValue(spy,actor)*4;}
            if(actor==2 && archetypeAI)value+=archetypeAI.SpyRowBonus(d,row);
            if(AiSpyDisruptionSlot(actor,d,row,i,index,gain))value+=gain*4;
            // Pugach moves an enemy into its row. Contact hazards hit both arrivals.
            // Only publicly visible units contribute to this estimate.
            if(d.header.templateId==132204 && (token==512 || token==2048) && CountLocation(side,row)<8){
                pull=0;
                for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                    if(t.positionPlayerId!=side || (t.locationMask&7)==0 || t.locationMask==row || t.isWaitingToDie)continue;
                    pull=Max(pull,Min(t.power.currentPower,Max(0,weather.Hazard(side,row)-t.power.armor)));
                }
                value+=pull*4;
            }
            if(value>maximum){maximum=value;best=row;}
        }
        return best;
    }
    // Fringilla copies the left neighbour's power to the right neighbour.
    // As a spy she should reduce a large enemy, never strengthen it by accident.
    // Any revealed unit can be the weak left neighbour, regardless of its template or owner.
    // If no useful pair exists, a weaker spy in hand can prepare one on the enemy board.
    // Fringilla lands between the neighbours and copies left power to the right.
    private function AiFringillaSetup(actor : int, d : SBetaGwentDuelDefinition, out bestRow : int, out bestIndex : int, out gain : int) : bool
    {
        var i, enemy, held : int; var s : SBetaGwentCardSnapshot;
        gain = 0;
        // The Assassin already has its own target on the left: killing it now beats a later Fringilla setup.
        if (d.header.templateId == 162205 || d.header.templateId == 200115 || d.header.typeMask != 4 || !BetaGwentDuelSpying(d.header.templateId)) return false;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (s.positionPlayerId == actor && s.locationMask == 8 && s.runtimeTemplate.templateId == 162205) held += 1; }
        if (held == 0) return false;
        enemy = BetaGwentOpponentId(actor);
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (s.positionPlayerId != enemy || (s.locationMask & 7) == 0 || s.isWaitingToDie || (s.tokenMask & 8) != 0
                || s.runtimeTemplate.typeMask != 4 || CountLocation(enemy, s.locationMask) >= 8) continue;
            if (s.power.currentPower - d.header.power > gain) { gain = s.power.currentPower - d.header.power; bestRow = s.locationMask; bestIndex = s.locationIndex; }
        }
        return gain >= 4;
    }
    private function AiFringillaSlot(actor : int, out bestRow : int, out bestIndex : int, out gain : int) : bool
    {
        var cards : array<CBetaGwentDuelCard>;var l,r : SBetaGwentCardSnapshot;var row,i,value,maximum,enemy : int;
        enemy=BetaGwentOpponentId(actor);maximum=-2147483647;gain=0;
        for(row=1;row<=4;row*=2){LocationCards(enemy,row,cards);if(cards.Size()>=9)continue;
            for(i=0;i<=cards.Size();i+=1){
                value=0;
                if(i>0 && i<cards.Size()){
                    l=cards[i-1].Snapshot();r=cards[i].Snapshot();
                    if(!l.isWaitingToDie && !r.isWaitingToDie && l.runtimeTemplate.typeMask==4 && r.runtimeTemplate.typeMask==4
                        && (l.runtimeTierMask&15)!=0 && (r.runtimeTierMask&15)!=0 && (l.tokenMask&8)==0 && (r.tokenMask&8)==0)
                        value=r.power.currentPower-l.power.currentPower;
                    if(AiReturningSpy(r,actor))value=-value;
                }
                if(value>maximum){maximum=value;bestRow=row;bestIndex=i;gain=value;}
            }
        }
        return maximum!=-2147483647;
    }
    private function EvaluateCardRow(side : int, d : SBetaGwentDuelDefinition) : int
    {
        var row, value, best, maximum,supportRow,supportIndex : int;var victim : CBetaGwentDuelCard;var t : SBetaGwentCardSnapshot;
        aiPlacing = d;
        // The Assassin is a spy, but its row is the row of its victim (it hits the unit on its left).
        if(d.header.templateId==200115){victim=AiAssassinVictim(side);if(victim){t=victim.Snapshot();return t.locationMask;}}
        if(BetaGwentDuelSpying(d.header.templateId))return AiBestSpyRow(side,d);
        if(AiShipSlot(side,d,supportRow,supportIndex))return supportRow;
        if(side==2 && weatherProfile && d.header.typeMask==4)return weatherAI.BestRow(d);
        if (BetaGwentDuelSpying(d.header.templateId)) side = BetaGwentOpponentId(side);
        if(AiSupportSlot(side,d,supportRow,supportIndex))return supportRow;
        best = BestDeployRow(side, d.effect, d.header.templateId);
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
        if (d.deathwishDamage == 0) {
            if(side==2)best=archetypeAI.Row(d,best);
            // A plain body has no reason to take a harmful row over an open safe one.
            // Weather engines, neighbours and row abilities keep their tactical choice.
            if(weather.Hazard(side,best)>0 && d.passiveWeatherToken==0 && d.passiveBoost==0 && d.effect!=15 && d.effect!=23 && !AiAdjacencyCard(d.header.templateId) && !BetaGwentDuelSpying(d.header.templateId)){
                for(row=1;row<=4;row*=2)if(CountLocation(side,row)<9 && weather.Hazard(side,row)==0){best=row;break;}
            }
            return best;
        }
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
    // A board consume triggers charged Behemoths even when the victim has no deathwish.
    // Inserting a consumer and eating one unit leaves the original number of open slots.
    private function AiConsumeSpawnValue(side : int, excludeId : int) : int
    {
        var i, slots, spawns : int; var s : SBetaGwentCardSnapshot; var d, child : SBetaGwentDuelDefinition;
        slots = Max(0, 27 - CountLocation(side,1) - CountLocation(side,2) - CountLocation(side,4));
        for(i=0;i<live.Size();i+=1)
        {
            s=live[i].Snapshot();
            if(s.instanceId==excludeId || s.positionPlayerId!=side || (s.locationMask&7)==0
                || s.runtimeTemplate.templateId!=132201 || s.isWaitingToDie || s.power.currentPower<=0
                || (s.tokenMask&12)!=0 || s.timerValue<=0)continue;
            d=live[i].Definition();child=BetaGwentDuelDefinition(d.deploySpawnTemplate);
            if(slots>0){spawns+=child.header.power;slots-=1;}
        }
        return spawns;
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
                if (!immediate && d.effect == 14 && HasDeckTemplate(side, d.playTemplateId)) value += AiPlayedWeatherValue(side, d.playTemplateId);
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
        return Max(1, Min(BetaGwentAITune(24), Min(CountLocation(side, 8), CountLocation(enemy, 8) + 1)));
    }
    // Public repertoire prior, updated by public field/grave cards. Never reads
    // playerOne's hidden hand/deck templates or the private selected preset.
    public function AiPublicClearRisk() : int
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
        var i, consumers, engines, weatherCards, frostPayoffs, spies, value, setupRow, setupIndex, setupGain : int; var s : SBetaGwentCardSnapshot; var held : SBetaGwentDuelDefinition;
        if (AiHorizon(2) <= 1) return 0;
        if (AiFringillaSetup(2, d, setupRow, setupIndex, setupGain)) value += Min(8, setupGain / 2);
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
        // Impera Enforcers deal 2 at turn end for every own spy that lands that turn.
        if(d.header.templateId==162308)value+=Min(3,spies)*2;
        if (d.effect == 16 || d.effect == 23 || d.effect == 17) value -= Min(4, engines * 2);
        if (d.passiveBoost > 0 && !HasWeather(d.passiveWeatherToken) && weatherCards > 0) value += d.passiveBoost * 2;
        if ((d.weatherToken == 1 || (d.effect == 14 && d.playTemplateId == 113302)) && frostPayoffs > 0) value += Min(4, frostPayoffs * 2);
        return value;
    }
    public function AiWeatherCardToken(d : SBetaGwentDuelDefinition) : int
    {
        var token : int;token=d.weatherToken;
        if(d.effect==28 && (d.specialMode==14 || d.specialMode==15))token=d.specialToken;
        if(token==1 || token==2 || token==4 || token==16 || token==32 || token==64)return token;
        return 0;
    }
    public function AiReserveCost(d : SBetaGwentDuelDefinition) : int
    {
        var cost,i,weatherCards : int;var s : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; m = match.Snapshot();
        if (d.header.tierMask == 8) cost = BetaGwentAITune(13); else if (d.header.tierMask == 4) cost = BetaGwentAITune(14);
        // Reactive specials are useful later; do not cash them in for one point.
        if (d.header.typeMask == 2 && (d.effect == 20 || d.effect == 19 || d.effect == 1)) cost += BetaGwentAITune(30);
        // A passed opponent cannot answer. Even when we must win this round,
        // choose the least expensive winning line and keep the final's resources.
        // This cost orders reachable lines; it never forbids a necessary catch.
        if (m.roundNumber >= 3 || m.playerOne.crowns>=1 && !m.playerOne.hasPassed) return 0;
        cost+=archetypeAI.Reserve(d)+archetypeAI.PassedRoundReserve(d);
        // Several weather cards compete for the same round/rows. Keep one
        // reserve, rather than saving every global weather for the final round.
        if(AiWeatherCardToken(d)>0){
            for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                if(s.positionPlayerId==2 && s.locationMask==8 && AiWeatherCardToken(live[i].Definition())>0)weatherCards+=1;}
            if(weatherCards>1)cost/=Min(3,weatherCards);
            // Stage 127: holding weather does not dodge Clear Skies; the opponent's single
            // clear is better spent on this weather than on the one saved for later.
            cost=cost*(100-AiPublicClearRisk()*BetaGwentAITune(17)/100)/100;
        }
        // Weather already discounts its reserve by public Clear Skies risk.
        if(!m.playerOne.hasPassed && AiWeatherCardToken(d)==0)cost+=BetaGwentAIResourcePressure(m.roundNumber,m.playerTwo.crowns,m.playerOne.crowns,CountLocation(2,8),CountLocation(1,8),cost);
        return cost;
    }
    // Stage 127: Draug turns every own graveyard unit into a 1-power Draugir.
    private function AiDraugTargets(side : int) : int
    {
        var i, count : int; var s : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (s.positionPlayerId == side && s.locationMask == 32 && !s.isWaitingToDie && (s.runtimeTemplate.typeMask & 4) != 0) count += 1; }
        return count;
    }
    // Stage 127: a decisive round (final round, or the enemy already holds a crown) is
    // played out; nothing is saved. Cards that lose value with every turn they wait go
    // first: weather loses a tick per turn, a boost special loses bodies that the enemy
    // weather is wearing down. The bonus only orders plays, it never forces a weak card.
    public function AiDecisiveRound() : bool
    { var m : SBetaGwentMatchSnapshot; m = match.Snapshot(); return m.roundNumber >= 3 || m.playerOne.crowns >= 1; }
    private function AiDecayUrgency(d : SBetaGwentDuelDefinition, value : int, ownHand : int) : int
    {
        var m : SBetaGwentMatchSnapshot; var row, worn : int; m = match.Snapshot();
        if (m.playerOne.hasPassed || !AiDecisiveRound() || value <= 0 || ownHand <= 1) return 0;
        if (AiWeatherCardToken(d) > 0) return Min(6, value / Max(1, ownHand - 1) + 1);
        if (d.header.typeMask == 2 && (d.effect == 2 || d.effect == 3))
        {
            for (row = 1; row <= 4; row *= 2) if (weather.Damage(2, row) > 0 && CountLocation(2, row) > 0) worn += 1;
            if (worn > 0) return Min(4, 1 + worn);
        }
        return 0;
    }
    // Stage 110: weather is a damage-over-time card. It ticks at the start of every enemy
    // turn, so an early weather is worth more the longer the round lasts - but only while
    // the enemy keeps playing. Expected ticks (tenths): the first tick always lands (the
    // enemy's next turn starts before it can pass); each further tick needs the enemy to
    // stay in the round. An enemy that leads, holds fewer cards or already won a round can
    // simply pass, which ends the damage.
    private function AiWeatherTicks(side : int) : int
    {
        var m : SBetaGwentMatchSnapshot; var enemy, turns, stay, lead, ownHand, enemyHand, k, chance, total, enemyCrowns : int;
        m = match.Snapshot(); enemy = BetaGwentOpponentId(side);
        if ((enemy == 1 && m.playerOne.hasPassed) || (enemy == 2 && m.playerTwo.hasPassed)) return 0;
        ownHand = CountLocation(side, 8); enemyHand = CountLocation(enemy, 8);
        enemyCrowns = m.playerTwo.crowns; if (enemy == 1) enemyCrowns = m.playerOne.crowns;
        // After this card we have ownHand-1 cards: the enemy gets about one turn per card we keep.
        turns = Max(1, Min(6, Min(enemyHand + 1, ownHand)));
        lead = Score(enemy) - Score(side);
        stay = BetaGwentAITune(25);
        if (lead > 0) stay -= 25;                                  // ahead: passing costs it nothing
        if (lead > 10) stay -= 15;
        if (enemyHand + 1 < ownHand) stay -= 10;                   // card-down enemy likes to pass early
        if (m.roundNumber == 2 && enemyCrowns > 0) stay -= 15;     // round already won: can dry pass
        if (m.roundNumber == 3 && lead < 0) stay = 95;             // final round and behind: must keep playing
        stay = Max(20, Min(95, stay));
        chance = 100;
        for (k = 0; k < turns; k += 1) { total += chance; chance = chance * stay / 100; }
        return total / 10;
    }
    public function AiClearWeatherTicks(side : int) : int
    {
        if(AiHorizon(side)==0)return 0;
        return Min(AiHorizon(side)*10,AiWeatherTicks(BetaGwentOpponentId(side)));
    }
    private function WeatherValue(side : int, row : int, token : int) : int
    {
        var enemy, count, targets, previousTargets, perTick, ticks, power, i, value, share : int; var t : SBetaGwentCardSnapshot;
        enemy = BetaGwentOpponentId(side);
        ticks = AiWeatherTicks(side); if (ticks == 0) return 0;
        if (weather.Token(enemy, row) == token) return 0;
        count = CountLocation(enemy, row);
        if(token==64 && count>0)return (weather.ForecastTokenLoss(enemy,row,token,ticks)-weather.ForecastTokenLoss(enemy,row,weather.Token(enemy,row),ticks))*BetaGwentAITune(11)/10;
        for (i = 0; i < live.Size(); i += 1)
        { t = live[i].Snapshot(); if (t.positionPlayerId == enemy && t.locationMask == row && !t.isWaitingToDie && (t.tokenMask & 8) == 0) power += t.power.currentPower; }
        targets = 1; if (token == 4) targets = Max(1, Min(2, count)); if (token == 64) targets = Max(1, Min(3, count));
        previousTargets = 1; if (weather.Token(enemy, row) == 4) previousTargets = Min(2, count);
        perTick = weather.DamageFor(enemy, row, token) * targets; if (token == 64) perTick = 2 + Max(0, Min(3, count) - 1);
        if(weather.Token(enemy,row)==64)perTick-=2+Max(0,Min(3,count)-1);
        else if(weather.Boon(enemy,row)==0)perTick -= weather.Damage(enemy, row) * previousTargets;
        if (perTick <= 0) return perTick*ticks/10;
        value = perTick * ticks / 10;
        // A unit cannot lose more than its power. An empty row only pays if the enemy is
        // forced to use it later (it will avoid the row while it can).
        if (count == 0) { share = AiEnemyRowShare(enemy, row); value = Min(value * (3 + share / 25) / 10, 4 + share / 25); }
        else value = Min(value, power + (ticks / 10) * 2);
        return value * BetaGwentAITune(11) / 10;
    }
    // Stage 127: preventive weather. An empty row still pays when the opponent keeps
    // placing its units there (public placements this match, 0..100 percent). The
    // opponent can avoid a weathered row, so the share only lifts the empty-row cap.
    private function AiEnemyRowShare(enemy : int, row : int) : int
    {
        var total, own : int;
        if (enemy != 1 || aiEnemyRowPlays.Size() != 3) return 0;
        total = aiEnemyRowPlays[0] + aiEnemyRowPlays[1] + aiEnemyRowPlays[2]; if (total < 3) return 0;
        if (row == 1) own = aiEnemyRowPlays[0]; else if (row == 2) own = aiEnemyRowPlays[1]; else if (row == 4) own = aiEnemyRowPlays[2];
        return own * 100 / total;
    }
    // A card that plays a weather card from the deck (Wild Hunt Hound -> Biting Frost)
    // is valued with the same damage-over-time forecast as the weather itself.
    private function AiPlayedWeatherValue(side : int, templateId : int) : int
    {
        var token : int; var played : SBetaGwentDuelDefinition;
        played = BetaGwentDuelDefinition(templateId); token = played.weatherToken; if (token == 0) return 0;
        if (side != 2) return WeatherValue(side, BestWeatherRow(side, token), token);
        return WeatherValue(side, BestWeatherRow(side, token), token) * (100 - AiPublicClearRisk() * BetaGwentAITune(17) / 100) / 100;
    }
    // Weather archetype AI (duelWeatherAI.ws) uses the same forecast for its frost rows.
    public function AiWeatherForecast(side : int, row : int, token : int) : int
    { return WeatherValue(side, row, token); }
    private function BestWeatherRow(side : int, token : int) : int
    {
        var row, best, value, maximum : int; best = 1; maximum = -1;
        for (row = 1; row <= 4; row *= 2)
        { value = WeatherValue(side, row, token); if (value > maximum) { maximum = value; best = row; } }
        return best;
    }
    // Original query ignores concealed ambush (8), but includes immune units (256).
    private function EpidemicEligible(s : SBetaGwentCardSnapshot) : bool
    { return (s.locationMask&7)!=0 && (s.runtimeTemplate.typeMask&4)!=0 && (s.tokenMask&8)==0 && !s.isWaitingToDie; }
    private function Epidemic()
    {
        var i, lowest : int; var s : SBetaGwentCardSnapshot;
        lowest = 2147483647;
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (EpidemicEligible(s) && s.power.currentPower < lowest) lowest = s.power.currentPower; }
        if(lowest==2147483647){message="Эпидемия: нет подходящих целей.";return;}
        for (i = 0; i < live.Size(); i += 1)
        { s = live[i].Snapshot(); if (EpidemicEligible(s) && s.power.currentPower == lowest) QueueDestroy(live[i]); }
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
        card.deathCue = GetVisualSource();
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
    private function RecordDeathVisual(card : CBetaGwentDuelCard, kind : int, caption : string, duration : int)
    {
        var previous, cause : SBetaGwentDuelCueContext; var s : SBetaGwentCardSnapshot;
        previous=GetVisualSource();cause=card.deathCue;s=card.Snapshot();
        SetVisualSource(cause.id,cause.templateId,cause.side,cause.row);
        RecordVisual(kind,s.instanceId,caption,duration);
        SetVisualSource(previous.id,previous.templateId,previous.side,previous.row);
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
                    if (!suppressAbilities && !consumed) RecordDeathVisual(batch[i],12, d.title + ": изначальная сила исчерпана", 380);
                    BetaGwentLog("DUEL_BANISH_WEAKENED card=" + s.instanceId + " removalType=0 killed=false");
                    continue;
                }
                batch[i].lastActiveRow = s.locationMask; killedPositions.PushBack(s);
                if ((s.tokenMask & 512) != 0)
                {
                    // Void512, not SpawningPool128. Keep a non-reusable visual tombstone.
                    batch[i].Move(s.positionPlayerId, 512, 0); batch[i].SetPlayable(false);
                    Reindex(s.positionPlayerId, s.locationMask);
                    if (!suppressAbilities && !consumed) RecordDeathVisual(batch[i],3, d.title + ": исчез", 320);
                    BetaGwentLog("DUEL_TOKEN_REMOVED card=" + s.instanceId + " location=512 grave=false");
                }
                else if (s.locationMask != 32)
                {
                    batch[i].Move(s.positionPlayerId, 32, CountLocation(s.positionPlayerId, 32)); batch[i].ResetInGraveyard();
                    Reindex(s.positionPlayerId, s.locationMask); if (!suppressAbilities && !consumed) RecordDeathVisual(batch[i],3, d.title + ": в сброс", 320);
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
    private function BestOwnRow(side : int, optional definitionId : int) : int
    {
        var row, best, count, penalty, minimum : int;var placing : SBetaGwentDuelDefinition;
        minimum = 2147483647;placing=BetaGwentDuelDefinition(definitionId);
        for (row = 1; row <= 4; row *= 2)
        {
            count = CountLocation(side,row);if(count>=9)continue;
            penalty=count*2+weather.Damage(side,row)*3;
            if(BetaGwentAIStrength()>=2){penalty=AiRowPlacementCost(side,row,placing)*2;}
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
    private function AiUselessDecoy(source : CBetaGwentDuelCard) : bool
    {
        var d : SBetaGwentDuelDefinition;var s,a : SBetaGwentCardSnapshot;var i : int;
        if(!source || source.TemplateId()!=113201)return false;
        d=source.Definition();a=source.Snapshot();
        for(i=0;i<live.Size();i+=1){
            s=live[i].Snapshot();
            if(s.positionPlayerId!=a.positionPlayerId || !MatchesCardTarget(s,d))continue;
            if(specials.TargetValue(d,s,a.positionPlayerId)>0)return false;
        }
        return true;
    }
    private function AiDeferEmptyDuel(d : SBetaGwentDuelDefinition, side : int) : bool
    {
        var i : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;var alternative : bool;
        if(d.effect!=34 || d.specialMode!=137)return false;
        m=match.Snapshot();
        // A body-only duel may still be the cheapest proven catch after a pass.
        if((side==2 && m.playerOne.hasPassed) || (side==1 && m.playerTwo.hasPassed))return false;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId!=side && (s.locationMask&7)!=0 && s.runtimeTemplate.typeMask==4 && !s.isWaitingToDie && (s.tokenMask&264)==0)return false;
            if(s.positionPlayerId==side && s.locationMask==8 && s.canBePlayed && s.runtimeTemplate.templateId!=d.header.templateId)alternative=true;
        }
        return alternative;
    }
    private function AiAglaisHasTarget(side : int) : bool
    {
        var i : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==BetaGwentOpponentId(side) && s.locationMask==32 && s.runtimeTemplate.typeMask==2
                && (s.runtimeTierMask&6)!=0 && !s.isWaitingToDie && (s.tokenMask&512)==0)return true;}
        return false;
    }
    // Ordering only: with two actions left, a reactive answer can improve after
    // the last enemy play. No hidden hand identity or draw order is inspected.
    public function AiLateOrderWindow() : bool
    {
        var m : SBetaGwentMatchSnapshot;var actions : int;m=match.Snapshot();
        if(aiSimulating || BetaGwentAIStrength()<4 || !AiDecisiveRound() || m.playerOne.hasPassed
            || CountLocation(1,8)<1 || CountLocation(1,8)>3)return false;
        actions=CountLocation(2,8);if(LeaderAvailable(2))actions+=1;
        return actions==2;
    }
    private function AiLateControlReserve(card : CBetaGwentDuelCard, gain : int) : int
    {
        var i : int;var s,t : SBetaGwentCardSnapshot;var d,other,choice : SBetaGwentDuelDefinition;
        var pool : array<int>;var spells : bool;
        if(!AiLateOrderWindow() || !card)return 0;s=card.Snapshot();d=card.Definition();
        if(s.locationMask==64){
            BetaGwentNilfPool(d.header.templateId,pool);if(pool.Size()==0)BetaGwentMonsterTemplates(d.header.templateId,pool);spells=pool.Size()>1;
            for(i=0;i<pool.Size();i+=1){choice=BetaGwentDuelDefinition(pool[i]);if(choice.header.typeMask!=2)spells=false;}
            if(!spells || gain<=s.power.currentPower+2)return 0;
        }else if(AiAbilityDamage(card,NULL)<=0)return 0;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.positionPlayerId!=2 || t.locationMask!=8 || t.instanceId==s.instanceId || !t.canBePlayed)continue;
            other=live[i].Definition();if(other.header.typeMask!=4 || BetaGwentDuelSpying(other.header.templateId))continue;
            if(s.locationMask==64){if(AiAbilityDamage(live[i],NULL)>0)return 6;}
            else if(AiAbilityDamage(live[i],NULL)==0 && !BetaGwentAIControlCard(other))return 3;
        }
        return 0;
    }
    private function AiTimingReserve(card : CBetaGwentDuelCard, gain : int) : int
    {
        var d : SBetaGwentDuelDefinition;var s,t : SBetaGwentCardSnapshot;var useful,i : int;var m : SBetaGwentMatchSnapshot;
        d=card.Definition();s=card.Snapshot();useful=gain-s.power.currentPower;
        if(d.header.templateId==162205)return Max(0,d.header.power-AiManagedDeployValue(d,2))*3;
        // An empty enemy grave leaves Aglais as a legal body, but preserve her
        // resurrection before the deciding round. A proven catch remains legal.
        if(d.header.templateId==142106){m=match.Snapshot();
            if(m.roundNumber<3 && m.playerOne.crowns==0 && !m.playerOne.hasPassed && !AiAglaisHasTarget(2))
                return 8*BetaGwentAITune(31)+AiGrowthReserve(card)*BetaGwentAITune(12)/10;}
        // Draug resurrects only what the graveyard already holds: wait for it to fill
        // before the deciding round instead of spending the ability on an empty grave.
        if(d.header.templateId==132101){m=match.Snapshot();if(m.roundNumber>=3 || m.playerOne.crowns>=1)return 0;return Max(0,5-AiDraugTargets(2))*2;}
        // Reactive damage is worth keeping when no enemy can receive it.
        // Includes Roche and other managed deploy abilities, not just effect 1.
        if(AiAbilityDamage(card,NULL)>0 && CountLocation(1,1)+CountLocation(1,2)+CountLocation(1,4)==0 && CountLocation(2,8)>1){
            m=match.Snapshot();
            // A dry pass needs a body, not every identical Bronze removal kept
            // for later. Preserve one copy's response and save the gold finisher.
            if(m.playerOne.hasPassed && m.roundNumber<3 && s.runtimeTierMask==2){
                for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                    if(t.positionPlayerId==2 && t.locationMask==8 && t.instanceId!=s.instanceId
                        && t.runtimeTemplate.templateId==s.runtimeTemplate.templateId)return 0;}
            }
            return Max(12,AiAbilityDamage(card,NULL)*3);
        }
        // A reactive gold's body alone is not a reason to spend its ability.
        if(d.effect==34 && (d.specialMode==137 || d.specialMode==114 || d.specialMode==125 || d.specialMode==132)){
            m=match.Snapshot();if(d.header.tierMask==2 && m.playerOne.hasPassed)return 0;
            return Max(0,8-useful)*BetaGwentAITune(31);
        }
        if(d.header.tierMask==8 && d.effect==1)return Max(0,d.amount-useful);
        useful=AiGrowthReserve(card);
        return useful*BetaGwentAITune(12)/10+AiLateControlReserve(card,gain);
    }
    // Stage 110: cards that grow in hand, deck and on the board (Dol Blathanna Sentry:
    // +1 for every special card you play; Bloody Baron: +1 for every destroyed enemy unit).
    // On the board they still grow, but only until the round ends; kept in hand they carry
    // every boost into the deciding round as a finisher. Cost of playing one now:
    // the triggers it would miss in later rounds plus half of the boosts already banked.
    // In the last round the Sentry waits until the specials in hand have been played.
    private function AiGrowthReserve(card : CBetaGwentDuelCard) : int
    {
        var s, t : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var i, handSpecials, deckSpecials, banked, later : int;
        s = card.Snapshot(); m = match.Snapshot();
        if (s.runtimeTemplate.templateId != 200039 && s.runtimeTemplate.templateId != 122101) return 0;
        banked = Max(0, s.power.currentPower - s.power.basePower);
        if (s.runtimeTemplate.templateId == 122101)
        { if (m.roundNumber >= 3 || m.playerOne.crowns>=1) return 0; return 2 + banked / 2; }
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot(); if (t.positionPlayerId != 2 || t.instanceId == s.instanceId || t.runtimeTemplate.typeMask != 2) continue;
            if (t.locationMask == 8) handSpecials += 1; else if (t.locationMask == 16) deckSpecials += 1;
        }
        if (m.roundNumber >= 3 || m.playerOne.crowns>=1) return handSpecials;
        // About one more special this round; the rest of the hand and a share of the deck come later.
        later = Max(0, handSpecials - 1) + deckSpecials / 3;
        // Stage 131: the Sentry is the deck's finisher. Opening a round with it on an empty board
        // spends all the specials it would collect; a special, a body or even a pass comes first.
        if (handSpecials + deckSpecials >= 3 && CountLocation(2, 1) + CountLocation(2, 2) + CountLocation(2, 4) == 0)
            return Min(24, 2 * (handSpecials + deckSpecials / 2) + banked);
        return Min(12, later + banked / 2);
    }
    private function AiManagedDeployValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int
    {
        var id,amount,enemy,value,i,count : int;var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;
        id=d.header.templateId;enemy=BetaGwentOpponentId(side);
        if(d.effect!=34)return 0;
        if(id==200161)return AiRowVolleyValue(side,BestCardRow(side,d),10);
        if(id==152105){
            if(immediate)return 0;
            for(i=1;i<=4;i*=2)value=Max(value,weather.ForecastTokenLoss(enemy,i,64,AiWeatherTicks(side))-weather.ForecastTokenLoss(enemy,i,weather.Token(enemy,i),AiWeatherTicks(side)));
            return value;
        }
        if(id==201615)return Max(AiOutlawBranchValue(201715,side,immediate),AiOutlawBranchValue(201716,side,immediate));
        if(id==162205){AiFringillaSlot(side,value,count,amount);return amount;}
        if(id==132101)return Min(8,AiDraugTargets(side));
        if(d.specialMode==105 || id==142202 || id==152206)return AiCreatedPoolValue(d,side,immediate);
        if(d.specialMode==102)return Max(0,BestEffectValue(side,1,d.amount,2,d.header.templateId,immediate));
        // Stage 127: Jan Natalis plays a bronze/silver tactic from the deck. Its ability is
        // worth the best tactic it can actually pull; nothing when no tactic would act.
        if(d.specialMode==103 && id!=200033){
            LocationCards(side,16,cards);
            for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();
                if(s.isWaitingToDie || (s.runtimeTierMask&6)==0 || (s.runtimeTemplate.typeMask&14)==0 || !BetaGwentNorthernCategory(s.runtimeTemplate.templateId,8))continue;
                value=Max(value,AiPileCandidateValue(cards[i],side,immediate,1));}
            return value;
        }
        if(id==162315 || id==162313){amount=5;if(id==162315)amount=12;return Max(0,BestEffectValue(side,2,amount,1));}
        if(id==162306)amount=5;else if(id==162308)amount=2;else if(id==152304)amount=3;
        else if(id==162209 || id==162310)amount=7;else if(id==152207)amount=6;else if(id==142103)amount=8;
        else if(id==200124){
            amount=NilfAlchemy(side);value=BestEffectValue(side,1,amount,0,0,immediate);
            if(value==-2147483647)return -Min(amount,d.header.power);return value;
        }
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
    // Use the same action value for a created option and the card creating it.
    // Keep the pool bounded: nested creators are valued by their body here.
    // Choice-only template IDs have no body/ability definition. Estimate the
    // actual branch, without drawing RNG or looking at the opponent's hand.
    public function AiOutlawBranchValue(branch : int, side : int, immediate : bool) : int
    {
        var cards : array<CBetaGwentDuelCard>;var ids,values : array<int>;
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var i,j,k,best,total,count : int;
        if(branch==201715){
            best=-1000000;LocationCards(side,16,cards);
            for(i=0;i<cards.Size();i+=1){s=cards[i].Snapshot();d=cards[i].Definition();
                if(s.isWaitingToDie || IsPlayAncestor(cards[i]) || (s.runtimeTierMask&6)==0 || s.runtimeTemplate.typeMask!=2 || !HasRequiredPlayTargetForSide(d,side))continue;
                best=Max(best,AiPileCandidateValue(cards[i],side,immediate,1));
            }
            return best;
        }
        if(branch!=201716)return -1000000;
        BetaGwentScoiaPool(201615,ids);
        for(i=0;i<ids.Size();i+=1){d=BetaGwentDuelViewDefinition(ids[i]);values.PushBack(AiCreatedOptionValue(d,side,immediate));}
        // Create offers three distinct random candidates. Average the best
        // result over the 56 possible triples; never assume the best of all 8.
        for(i=0;i<values.Size();i+=1)for(j=i+1;j<values.Size();j+=1)for(k=j+1;k<values.Size();k+=1)
        {total+=Max(values[i],Max(values[j],values[k]));count+=1;}
        if(count>0)return total/count;
        if(values.Size()==0)return -1000000;
        best=values[0];for(i=1;i<values.Size();i+=1)best=Max(best,values[i]);return best;
    }
    private function AiExpectedBestThree(values : array<int>) : int
    {
        var i,j,t,total,n : int;n=values.Size();if(n==0)return 0;
        for(i=1;i<n;i+=1){j=i;while(j>0 && values[j]<values[j-1]){t=values[j];values[j]=values[j-1];values[j-1]=t;j-=1;}}
        if(n<3)return values[n-1];
        // C(i,2) triples have sorted entry i as their maximum. This is the
        // exact average of all distinct triples, without enumerating them.
        for(i=2;i<n;i+=1)total+=values[i]*i*(i-1)*3;
        return total/(n*(n-1)*(n-2));
    }
    private function AiCreatedLeaderValue(d : SBetaGwentDuelDefinition, side : int, immediate : bool) : int
    {
        var id,i,row,value,best,second,gain,deckBoost,highest,total,count : int;
        var ids,values : array<int>;var cards : array<CBetaGwentDuelCard>;
        var t : SBetaGwentCardSnapshot;var child : SBetaGwentDuelDefinition;
        id=d.header.templateId;value=d.header.power;
        if(id==131101 || id==201587 || id==201595 || id==201597 || id==201589){
            if(id==131101 || id==201587)BetaGwentMonsterTemplates(id,ids);
            else if(id==201595)BetaGwentNorthernPool(id,ids);else BetaGwentNilfPool(id,ids);
            for(i=0;i<ids.Size();i+=1){child=BetaGwentDuelDefinition(ids[i]);
                // Only this leader layer is expanded. Its actual pools contain
                // ordinary units/options, not recursively created leaders.
                if(BetaGwentDuelIsLeader(ids[i]))continue;
                gain=AiCreatedOptionValue(child,side,immediate);values.PushBack(gain);best=Max(best,gain);
            }
            if(id==201587 || id==201589)best=AiExpectedBestThree(values);
            return value+best;
        }
        if(id==200168){
            for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                if(t.positionPlayerId!=side || t.isWaitingToDie || (t.tokenMask&8)!=0
                    || t.runtimeTemplate.typeMask!=4 || (t.runtimeTierMask&14)==0)continue;
                if((t.locationMask&7)!=0)value+=d.amount;
                else if(!immediate && !BetaGwentDuelSpying(t.runtimeTemplate.templateId)){
                    if(t.locationMask==8)value+=d.amount;else if(t.locationMask==16)deckBoost+=d.amount;
                }
            }
            return value+deckBoost*BetaGwentAITune(27)/100;
        }
        if(id==200169){
            for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                if((t.locationMask&7)==0 || t.isWaitingToDie || (t.tokenMask&264)!=0 || t.runtimeTemplate.typeMask!=4)continue;
                gain=0;if(!immediate)gain=LockToggleValue(t,side);
                if(t.positionPlayerId!=side)gain+=AiDamageChoice(t,side,d.amount,true);
                if(gain>best){second=best;best=gain;}else second=Max(second,gain);
            }
            return value+best+second;
        }
        if(id==200160 || id==200166 || id==200167){
            if(id==200166)LocationCards(side,32,cards);else LocationCards(side,16,cards);
            highest=-2147483647;
            for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();
                if(t.isWaitingToDie || IsPlayAncestor(cards[i]))continue;
                if(id==200160 && ((t.runtimeTierMask&6)==0 || t.runtimeTemplate.typeMask!=4 || BetaGwentDuelSpying(t.runtimeTemplate.templateId)))continue;
                if(id==200166 && ((t.runtimeTierMask&6)==0 || t.runtimeTemplate.typeMask!=2))continue;
                if(id==200167 && (BetaGwentDuelSpying(t.runtimeTemplate.templateId) || (t.runtimeTemplate.typeMask&12)==0
                    || !(t.runtimeTierMask==4 || t.runtimeTierMask==2 && BetaGwentNilfDwarf(t.runtimeTemplate.templateId))))continue;
                gain=AiPileCandidateValue(cards[i],side,immediate,0);
                if(id==200160){
                    if(t.power.currentPower<highest)continue;
                    if(t.power.currentPower>highest){highest=t.power.currentPower;total=0;count=0;}
                    total+=gain+2;count+=1;
                }else best=Max(best,gain);
            }
            // Crach resolves equal strongest candidates randomly, not as a
            // free choice of whichever deploy is best on this board.
            if(id==200160 && count>0)best=total/count;
            return value+best;
        }
        return -2147483647;
    }
    public function AiCreatedOptionValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int
    {
        var value,effectValue,row,count : int;
        value=d.header.power;if(BetaGwentDuelSpying(d.header.templateId))value=-value;
        if(BetaGwentDuelIsLeader(d.header.templateId)){
            effectValue=AiCreatedLeaderValue(d,side,immediate);if(effectValue!=-2147483647)return effectValue;
        }
        if(d.effect==29)return value+AiPilePlayValue(d,side,immediate,0);
        if(d.effect==10)return value+weather.ClearValue(side,d.amount,immediate);
        if(d.effect==9)return value+Max(weather.ClearValue(side,d.amount,immediate),RallyValue(side,immediate));
        if(d.effect==33)return value+ModeValue(d,BestModeChoice(d,side),side,immediate);
        if(d.weatherToken!=0){if(immediate)return value;return value+WeatherValue(side,BestWeatherRow(side,d.weatherToken),d.weatherToken);}
        if(d.effect==28 && d.specialMode==14){
            if(immediate)return value;
            for(row=1;row<=4;row*=2)value+=WeatherValue(side,row,d.specialToken);
            return value;
        }
        if(d.effect==28 && immediate && (d.specialMode==15 || (d.specialMode==37 && d.specialToken==256)))return value;
        // Created and pile-played specials must retain their signed real effect.
        // In particular, Scorch may destroy only our own strongest units.
        if(d.effect==28)return value+specials.DefinitionValue(d,side,immediate);
        if(d.specialRequest==2)return value+Max(0,specials.BestRow(d,side,row,count));
        if(d.effect==1 || d.effect==2 || d.effect==3 || d.effect==17 || d.effect==19 || d.effect==25 || d.effect==27){
            effectValue=BestEffectValue(side,d.effect,d.amount,d.targetSide,d.header.templateId,immediate);
            return value+Max(0,effectValue);
        }
        if(d.effect==34 && d.specialMode!=105)return value+AiManagedDeployValue(d,side,immediate);
        if(d.header.typeMask==2)value+=5;
        return value;
    }
    private function AiPileCandidateValue(card : CBetaGwentDuelCard, side : int, immediate : bool, depth : int) : int
    {
        var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var value : int;
        if(!card)return 0;s=card.Snapshot();d=card.Definition();
        if(!HasRequiredPlayTargetForSide(d,side))return -1000000;
        value=s.power.currentPower;
        if(BetaGwentDuelSpying(d.header.templateId))value=-value;
        if(d.effect==29)return value+AiPilePlayValue(d,side,immediate,depth+1);
        // Same archetype corrections as a hand play: a card pulled from the deck or grave
        // keeps its resurrection payoff (PileGain) and public deploy gains (Pugach under a
        // waiting Miruna, Impera with allied spies).
        if(side==2 && archetypeAI)value+=archetypeAI.PileGain(d,immediate)+archetypeAI.PublicDeployGain(d);
        if(BetaGwentDuelSpying(d.header.templateId))return value+AiCreatedOptionValue(d,side,immediate)+d.header.power;
        return value+AiCreatedOptionValue(d,side,immediate)-d.header.power;
    }
    private function AiPilePlayValue(d : SBetaGwentDuelDefinition, side : int, immediate : bool, depth : int) : int
    {
        var cards : array<CBetaGwentDuelCard>;var s : SBetaGwentCardSnapshot;var td : SBetaGwentDuelDefinition;
        var i,value,best,extreme,count,total : int;
        if(depth>=3)return 0;
        LocationCards(side,d.pileLocation,cards);best=-2147483647;
        extreme=-2147483647;if(d.pilePickMode==2)extreme=2147483647;
        for(i=0;i<cards.Size();i+=1){
            s=cards[i].Snapshot();td=cards[i].Definition();
            if(s.isWaitingToDie || IsPlayAncestor(cards[i]) || !HasRequiredPlayTargetForSide(td,side) || (s.runtimeTemplate.typeMask&d.targetTypes)==0 || (s.runtimeTierMask&d.targetTiers)==0 || (s.tokenMask&d.targetIgnore)!=0 || (d.consumeMaximum>0 && s.power.currentPower>d.consumeMaximum))continue;
            if(d.pileTraitMask!=0 && (td.unitTraits&d.pileTraitMask)==0)continue;
            value=AiPileCandidateValue(cards[i],side,immediate,depth);
            if(d.pilePickMode==1 && s.power.currentPower<extreme || d.pilePickMode==2 && s.power.currentPower>extreme)continue;
            if(d.pilePickMode==1 && s.power.currentPower>extreme || d.pilePickMode==2 && s.power.currentPower<extreme){best=-2147483647;extreme=s.power.currentPower;}
            best=Max(best,value);total+=value;count+=1;
        }
        if(count==0)return 0;
        if(d.pilePickMode==3)return total/count;
        return best;
    }
    public function AiCreatedPoolValue(d : SBetaGwentDuelDefinition, side : int, optional immediate : bool) : int
    {
        var ids : array<int>;var i,value : int;var option : SBetaGwentDuelDefinition;
        BetaGwentNorthernPool(d.header.templateId,ids);
        if(ids.Size()==0)BetaGwentNilfPool(d.header.templateId,ids);
        if(ids.Size()==0)BetaGwentScoiaPool(d.header.templateId,ids);
        if(ids.Size()==0)BetaGwentSkelligePool(d.header.templateId,ids);
        if(ids.Size()==0)BetaGwentNeutralPool(d.header.templateId,ids);
        for(i=0;i<ids.Size();i+=1){option=BetaGwentDuelViewDefinition(ids[i]);value=Max(value,AiCreatedOptionValue(option,side,immediate));}
        return value;
    }
    private function AiCanRegainLead(remaining : int) : bool
    {
        var job : CBetaGwentAIRegain188;job=new CBetaGwentAIRegain188 in this;job.Initialize(this,remaining);
        while(!job.Step()){}return job.result;
    }
    private function AiDrawSpy(id : int) : bool
    { return id==122203 || id==132204 || id==142203 || id==152214 || id==162210; }
    private function AiDrawingSpy(card : CBetaGwentDuelCard) : bool
    {
        var s : SBetaGwentCardSnapshot;if(!card || !AiDrawSpy(card.TemplateId()))return false;
        s=card.Snapshot();return s.timerValue>0;
    }
    // Forecast an unknown draw from the remaining OWN deck, never its hidden
    // order. Only disposable clones are shuffled; live cards/RNG stay untouched.
    public function AiSpyForecastDeck(sample : int)
    {
        var ids : array<int>;var i,j,id : int;var m : SBetaGwentMatchSnapshot;
        if(!aiSimulating)return;
        NorthPile(2,16,ids);
        // Canonical instance order makes the forecast independent of deck order.
        for(i=1;i<ids.Size();i+=1){id=ids[i];j=i-1;while(j>=0 && ids[j]>id){ids[j+1]=ids[j];j-=1;}ids[j+1]=id;}
        m=match.Snapshot();random.Initialize(17041+sample*7919+m.roundNumber*101);
        ShuffleIds(ids);
        for(i=0;i<ids.Size();i+=1)FindCard(ids[i]).Move(2,16,i);
    }
    private function AiSpyDrawForecast(card : CBetaGwentDuelCard, out unsafe : bool, out risk : int, out tempo : int) : int
    {
        var job : CBetaGwentAISpy188;var i,cardId : int;var own : SBetaGwentCardSnapshot;
        unsafe=false;risk=0;tempo=0;
        if(aiSimulating || !AiDrawingSpy(card))return 0;own=card.Snapshot();cardId=own.instanceId;
        if(AiPreparationIsReady())for(i=0;i<aiPreparedSpyIds.Size();i+=1)if(aiPreparedSpyIds[i]==cardId){unsafe=aiPreparedSpyUnsafe[i];risk=aiPreparedSpyRisk[i];tempo=aiPreparedSpyTempo[i];return aiPreparedSpyDraw[i];}
        job=new CBetaGwentAISpy188 in this;job.Initialize(this,cardId);
        while(!job.Step()){}unsafe=job.unsafe;risk=job.risk;tempo=job.tempo;
        AiExplain("SPY_FORECAST","card="+cardId+" template="+card.TemplateId()+" samples="+job.count+" tempo="+tempo+" drawnFollowup="+job.result+" recoveries="+job.recovered+" risk="+risk+" rejected="+unsafe+" reason=unordered_own_deck_and_actual_followup");
        return job.result;
    }
    // A drawing spy keeps the hand size while the opponent's points grow: +1 card.
    // Its gift matters only if it changes who takes the round. When the round
    // stays ours by a wide margin the opponent must keep chasing (two extra cards);
    // in a round we will concede the points cost nothing. Never in a deciding round.
    private function AiSpyCardEdge(gift : int) : int
    {
        var m : SBetaGwentMatchSnapshot;var lead,edge : int;
        m=match.Snapshot();
        if(m.roundNumber>=3 || m.playerOne.hasPassed || CountLocation(2,16)==0)return 0;
        lead=Score(2)-Score(1);edge=4;
        if(lead-gift>=10)edge+=gift/2;
        else if(!AiDecisiveRound() && lead<=-15)edge+=gift/2;
        AiExplain("SPY_CARD_EDGE","gift="+gift+" lead="+lead+" edge="+edge+" round="+m.roundNumber);
        return edge;
    }
    // In an optional first round, a drawing spy can convert itself into a
    // usable card before we concede with an intact hand balance. Requiring
    // an immediate one-card catch confuses that plan with a mandatory chase.
    // This is a developed round with at least three own cards already spent,
    // never a fresh opening. Smaller hands, a required round and concealed
    // enemy traps retain the strict recovery test. Only public counts are read.
    public function AiSpyConcessionWindow() : bool
    {
        var m : SBetaGwentMatchSnapshot;var i,hand : int;var s : SBetaGwentCardSnapshot;
        m=match.Snapshot();hand=CountLocation(2,8);
        if(aiSimulating || m.roundNumber!=1 || m.playerOne.crowns!=0 || m.playerTwo.crowns!=0
            || m.playerOne.hasPassed || hand<4 || hand<CountLocation(1,8) || aiRoundHandTwo-hand<3 || Score(2)>Score(1))return false;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&8)!=0)return false;}
        return true;
    }
    private function AiSpyUnrecoverable(card : CBetaGwentDuelCard) : bool
    {
        var g : CBetaGwentDuelSession;var turns,risk,tempo : int;var result : bool;var s : SBetaGwentCardSnapshot;
        if(aiSimulating || !card || !BetaGwentDuelSpying(card.TemplateId()) || CountLocation(2,8)>2 || Score(2)<=Score(1))return false;
        if(AiDrawingSpy(card)){AiSpyDrawForecast(card,result,risk,tempo);return result;}
        turns=CountLocation(2,8);s=card.Snapshot();BetaGwentAISimEnter();g=AiSimClone();
        if(g && g.AiSimPlay(s.instanceId)!=-2147483647)result=!g.AiCanRegainLead(turns);
        BetaGwentAISimLeave();return result;
    }
    // Power False Ciri brings back to her owner when the opponent passes, with
    // at least one start-of-turn growth while she spies.
    // False Ciri spying on a side moves to the opposite side when that side's
    // player passes: her power is a deferred swing of twice her power.
    private function AiReturningSpyPower(side : int) : int
    {
        var i,total : int;var t : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();
        if((side==1 && m.playerOne.hasPassed) || (side==2 && m.playerTwo.hasPassed))return 0;
        for(i=0;i<live.Size();i+=1){
            t=live[i].Snapshot();
            if(t.positionPlayerId==side && (t.locationMask&7)!=0 && !t.isWaitingToDie && t.runtimeTemplate.templateId==162212 && (t.tokenMask&128)!=0 && (t.tokenMask&12)==0)total+=t.power.currentPower;
        }
        return total;
    }
    // Resilient units keep their power into the next round: half of that carry-over
    // (own minus opponent) is strategic value while another round remains.
    public function AiResilientCarry() : int
    {
        var i,total : int;var t : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();if(m.roundNumber>=3)return 0;
        for(i=0;i<live.Size();i+=1){
            t=live[i].Snapshot();
            if((t.locationMask&7)==0 || t.isWaitingToDie || (t.tokenMask&1)==0 || (t.tokenMask&8)!=0)continue;
            if(t.positionPlayerId==2)total+=t.power.currentPower;else total-=t.power.currentPower;
        }
        return total/2;
    }
    // Our spy spying for the opponent keeps feeding Impera Brigade (+2 per spy for each
    // copy still in hand or deck) and spy synergies; removing it is a last resort.
    private function AiOwnSpyKeep(t : SBetaGwentCardSnapshot, side : int) : int
    {
        var i,brigades : int;var c : SBetaGwentCardSnapshot;
        if(t.positionPlayerId==side || (t.tokenMask&128)==0 || (t.locationMask&7)==0 || t.isWaitingToDie)return 0;
        if(t.runtimeTemplate.templateId==162212 || AiDeathwishSpy(t.runtimeTemplate.templateId))return 0;
        for(i=0;i<live.Size();i+=1){c=live[i].Snapshot();if(c.positionPlayerId==side && (c.locationMask==8 || c.locationMask==16) && c.runtimeTemplate.templateId==162307)brigades+=1;}
        return 4+2*brigades;
    }
    public function AiOwnSpyKeepTotal() : int
    {
        var i,total : int;
        for(i=0;i<live.Size();i+=1)total+=AiOwnSpyKeep(live[i].Snapshot(),2);
        return total;
    }
    // Lead as it will stand once returning spies have moved; used by exact simulations.
    public function AiProjectedLead() : int
    { return Score(2)-Score(1)+2*AiReturningSpyPower(1)-2*AiReturningSpyPower(2); }
    // True for a spying False Ciri on the opponent's side of `actor` that will return to `actor`.
    private function AiReturningSpy(t : SBetaGwentCardSnapshot, actor : int) : bool
    {
        var m : SBetaGwentMatchSnapshot;m=match.Snapshot();
        if(t.runtimeTemplate.templateId!=162212 || (t.tokenMask&128)==0 || (t.tokenMask&12)!=0 || t.isWaitingToDie || (t.locationMask&7)==0 || t.positionPlayerId==actor)return false;
        return !((t.positionPlayerId==1 && m.playerOne.hasPassed) || (t.positionPlayerId==2 && m.playerTwo.hasPassed));
    }
    private function AiFalseCiriReturn(s : SBetaGwentCardSnapshot) : int
    { return s.power.currentPower+Min(2,Max(1,CountLocation(1,8))); }
    private function AiDeathwishSpy(id : int) : bool
    { return id==112215 || id==122206; }
    // Test a real activation, including placement, target choice, damage and
    // death queues. No value is awarded merely for putting a spy on the table.
    private function AiSpyActivationValue(card : CBetaGwentDuelCard) : int
    {
        var g : CBetaGwentDuelSession;var s : SBetaGwentCardSnapshot;var first,end,base : int;
        if(aiSimulating || !card || !AiDeathwishSpy(card.TemplateId()))return -2147483647;
        s=card.Snapshot();base=Score(2)-Score(1);
        BetaGwentAISimEnter();g=AiSimClone();end=-2147483647;
        if(g){first=g.AiSimPlay(s.instanceId);if(first!=-2147483647)end=g.AiSpyActivationEnd(s.instanceId,2);}
        BetaGwentAISimLeave();
        if(end!=-2147483647)end-=base;
        AiExplain("SPY_ACTIVATION","card="+s.instanceId+" template="+card.TemplateId()+" sequenceGain="+end+" reason=actual_deathwish_with_up_to_two_own_followups");
        return end;
    }
    private function AiSpyActivationEnd(spyId : int, remaining : int) : int
    {
        var spy,card : CBetaGwentDuelCard;var s,t : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var g : CBetaGwentDuelSession;var i,value,best : int;
        spy=FindCard(spyId);if(!spy)return -2147483647;s=spy.Snapshot();
        if(!AiDeathwishSpy(spy.TemplateId()) || (s.tokenMask&4)!=0)return -2147483647;
        if(s.locationMask==32)return Score(2)-Score(1);
        if((s.locationMask&7)==0 || remaining<=0 || AiSpyDeathwishValue(s,2)<=0)return -2147483647;
        m=match.Snapshot();if(m.currentPlayerId==1 && !AiSimSkipTurn())return -2147483647;
        // A turn-start hazard can activate the spy without another card.
        s=spy.Snapshot();if(s.locationMask==32)return Score(2)-Score(1);
        m=match.Snapshot();if(m.currentPlayerId!=2 || !m.turnActive)return -2147483647;
        best=-2147483647;
        for(i=0;i<live.Size();i+=1){card=live[i];t=card.Snapshot();
            if(t.positionPlayerId!=2 || !t.canBePlayed || (t.locationMask!=8 && t.locationMask!=64) || !AiSpyFinisherCandidate(card,spy))continue;
            g=AiSimClone();if(!g || g.AiSimPlay(t.instanceId)==-2147483647)continue;
            value=g.AiSpyActivationEnd(spyId,remaining-1);best=Max(best,value);
        }
        return best;
    }
    private function AiDrawUtility(d : SBetaGwentDuelDefinition, side : int, optional card : CBetaGwentDuelCard) : int
    {
        var m : SBetaGwentMatchSnapshot;var s : SBetaGwentCardSnapshot;var id : int;m=match.Snapshot();id=d.header.templateId;
        if(card && AiDrawSpy(id)){s=card.Snapshot();if(s.timerValue==0)return 0;}
        if(m.roundNumber>=3 || CountLocation(side,16)==0)return 0;
        if(d.effect==29 && AiPilePlayValue(d,side,false,0)<=0)return 0;
        if(AiDrawSpy(id)){
            if((side==2 && m.playerOne.hasPassed) || (side==1 && m.playerTwo.hasPassed))return 0;
            return Min(10,Min(CountLocation(side,8),CountLocation(BetaGwentOpponentId(side),8))*2);
        }
        // Plays a card from the deck or summons from it: synergy plus a thinner deck for later draws.
        if((d.pileLocation&16)!=0 || d.deploySummonTemplate!=0 || d.deploySummonOtherTemplate!=0)return BetaGwentAITune(10)*2;
        return 0;
    }
    // The horizon changes valuation, never the actual strength or damage.
    private function AiMirunaThreat(s : SBetaGwentCardSnapshot, side : int) : int
    {
        var i,highest : int;var t : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        if(s.runtimeTemplate.templateId!=132108 || (s.locationMask&7)==0 || s.timerValue<=0
            || s.isWaitingToDie || (s.tokenMask&12)!=0 || s.timerValue>AiHorizon(side))return 0;
        m=match.Snapshot();
        if((s.positionPlayerId==1 && m.playerOne.hasPassed) || (s.positionPlayerId==2 && m.playerTwo.hasPassed)
            || CountLocation(s.positionPlayerId,s.locationMask)>=9)return 0;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.positionPlayerId!=s.positionPlayerId && t.locationMask==s.locationMask && !t.isWaitingToDie
                && (t.tokenMask&8)==0 && t.runtimeTemplate.typeMask==4 && (t.runtimeTierMask&15)!=0)
                highest=Max(highest,t.power.currentPower);}
        // Charm both removes and gains the victim's power; it fires only once.
        return highest*2;
    }
    // Public, deferred material swing. One target per row is credited even
    // if copies share that row, so the same prospective victim is not sold twice.
    public function AiPendingCharmValue(side : int) : int
    {
        var i,row,best,total : int;var s : SBetaGwentCardSnapshot;
        for(row=1;row<=4;row*=2){
            best=0;
            for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                if(s.positionPlayerId==side && s.locationMask==row && s.runtimeTemplate.templateId==132108)
                    best=Max(best,AiMirunaThreat(s,side));}
            total+=best;
        }
        return total;
    }
    public function AiEngineValue(s : SBetaGwentCardSnapshot, side : int) : int
    {
        var d : SBetaGwentDuelDefinition;var value,horizon,i,neighbours : int;var t : SBetaGwentCardSnapshot;
        if(s.positionPlayerId!=side && (s.tokenMask&8)!=0)return 0;
        if((s.tokenMask&4)!=0 || s.isWaitingToDie)return 0;
        d=BetaGwentDuelDefinition(s.runtimeTemplate.templateId);horizon=AiHorizon(side);
        if((s.locationMask&7)!=0){
            // A spent charge cannot produce another token/copy without a new
            // card. Generic template priors must not resurrect this ability.
            if((s.runtimeTemplate.templateId==132201 || s.runtimeTemplate.templateId==201624) && s.timerValue<=0)return 0;
            if(s.runtimeTemplate.templateId==152309){
                for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                    if(t.positionPlayerId==s.positionPlayerId && t.locationMask==s.locationMask && t.locationIndex==s.locationIndex+1 && !t.isWaitingToDie)neighbours+=1;}
                if(neighbours==0)return 0;
            }
        }
        if(s.runtimeTemplate.templateId==132108)return AiMirunaThreat(s,side);
        if(d.timerPeriod>0)value+=horizon*2;
        if(d.consumePassiveBoost>0)value+=d.consumePassiveBoost*horizon;
        if(d.passiveBoost>0 && HasWeather(d.passiveWeatherToken))value+=d.passiveBoost*horizon;
        if(s.runtimeTemplate.templateId==162307 || s.runtimeTemplate.templateId==200040)value+=horizon*2;
        // Armour is the switch for this engine: breaking the last point stops
        // every adjacent boost even when the unit survives the hit.
        if(s.runtimeTemplate.templateId==123301){
            if(s.power.armor==0)return 0;
            if((s.locationMask&7)!=0){
                neighbours=0;
                for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                    if(t.positionPlayerId==s.positionPlayerId && t.locationMask==s.locationMask && Abs(t.locationIndex-s.locationIndex)==1 && !t.isWaitingToDie)neighbours+=1;}
                return Min(12,Min(2,neighbours)*horizon);
            }
        }
        if(s.runtimeTemplate.templateId==201624 && s.timerValue>0)value=Max(value,4*Min(2,horizon));
        // Stage 127: Skellige longships. Dimun grows by 2 and pings 1 every turn; An Craite
        // fires 2 damage per discard, which a discard deck does almost every turn.
        if(s.runtimeTemplate.templateId==152309 || s.runtimeTemplate.templateId==152314)value=Max(value,3*horizon);
        value=Max(value,archetypeAI.EngineThreat(s,horizon));return Min(12,value);
    }
    private function AiDamageChoice(s : SBetaGwentCardSnapshot, side : int, amount : int, optional immediate : bool) : int
    {
        var value,deathwish,lost : int;var d,token : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
        if(s.positionPlayerId!=side && (s.tokenMask&8)!=0)return 0;
        value=DamageValue(s,side,amount);
        // Resilient power is also next round's power; a returning spy is our own.
        m=match.Snapshot();
        if(m.roundNumber<3 && (s.tokenMask&1)!=0){lost=Min(s.power.currentPower,Max(0,amount-s.power.armor))/2;if(s.positionPlayerId!=side)value+=lost;else value-=lost;}
        if(AiReturningSpy(s,side))return -Max(1,Max(value,-value));
        // Our own spy is rarely worth removing: prefer real enemy units.
        if(AiOwnSpyKeep(s,side)>0){if(s.power.currentPower<=Max(0,amount-s.power.armor))value-=AiOwnSpyKeep(s,side);else value-=2;}
        if(s.power.currentPower<=Max(0,amount-s.power.armor))value+=AiSpyDeathwishValue(s,side);
        else if(!immediate && s.positionPlayerId!=side && AiDeathwishSpy(s.runtimeTemplate.templateId) && AiHorizon(side)>1)
            value+=Max(0,AiSpyDeathwishValue(s,side))*Max(0,amount-s.power.armor)/Max(1,s.power.currentPower);
        if(!immediate && s.positionPlayerId!=side && s.runtimeTemplate.templateId==123301
            && s.power.armor>0 && amount>=s.power.armor && s.power.currentPower>Max(0,amount-s.power.armor))value+=AiEngineValue(s,side);
        if(s.positionPlayerId!=side && (s.tokenMask&4)==0 && s.power.armor>0 && amount>=s.power.armor && s.power.currentPower>Max(0,amount-s.power.armor)){
            if(s.runtimeTemplate.templateId==122317)value-=5;
            if(!immediate && s.runtimeTemplate.templateId==122308)value-=2;
        }
        if(!immediate)value-=AiRegenerationLoss(s,side,amount);
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
    private function AiRegenerationLoss(s : SBetaGwentCardSnapshot, side : int, amount : int) : int
    {
        var damage,base,restored,enabled,horizon : int;
        if(s.positionPlayerId==side || s.runtimeTemplate.templateId!=200040 || (s.locationMask&7)==0
            || (s.tokenMask&4)!=0 || s.timerValue<=0)return 0;
        damage=Max(0,amount-s.power.armor);
        if(damage==0 || damage>=s.power.currentPower)return 0;
        horizon=AiHorizon(side);if(horizon==0)return 0;
        base=s.power.basePower+s.power.permanentPower;
        restored=Min(damage,Max(0,base-s.power.currentPower+damage)-Max(0,base-s.power.currentPower));
        if(restored==0)return 0;
        if(s.power.currentPower>=base)enabled=2;
        // Due next turn: healing is public and immediate. With two timer ticks,
        // discount only when another exchange is possible, retaining tempo value.
        if(s.timerValue==1)return restored+enabled;
        // Two ticks are two owner turn starts. Log 26.10: a Cyclops hit at timer 2
        // healed back (+2) after the AI's next turn. With two cards left the owner
        // reaches the heal; credit the full loss, half with one card.
        if(s.timerValue==2 && CountLocation(s.positionPlayerId,8)>=2)return restored+enabled;
        if(s.timerValue==2 && horizon>=2)return Max(1,(restored+enabled)/2);
        return 0;
    }
    private function AiDeckCopyChoiceValue(target : CBetaGwentDuelCard, copies : int) : int
    {
        var t,c : SBetaGwentCardSnapshot;var d,cd : SBetaGwentDuelDefinition;
        var i,value,consumers : int;
        t=target.Snapshot();d=target.Definition();
        // Copies use the template, not the buffed body currently on the board.
        value=d.header.power*copies;
        for(i=0;i<live.Size();i+=1){
            c=live[i].Snapshot();if(c.positionPlayerId!=t.positionPlayerId || (c.locationMask&15)==0)continue;
            if((c.locationMask&7)!=0 && (c.tokenMask&4)!=0)continue;
            cd=live[i].Definition();
            if(cd.effect==23 || cd.effect==16 || (cd.effect==34 && cd.specialMode==11))consumers+=1;
        }
        // Self-replacing units convert added deck copies into playable bodies
        // without spending another hand card. This is setup value, not tempo.
        if(d.deathwishSummonTemplate==d.header.templateId && consumers>0 && (t.tokenMask&4)==0)
            value+=copies*(12+d.consumePassiveBoost*Min(4,consumers+AiHorizon(t.positionPlayerId)));
        AiExplain("DECK_COPY_OPTION","target="+t.instanceId+" template="+d.header.templateId+" copies="+copies+" consumers="+consumers+" setup_value="+value);
        return value;
    }
    // 0.9.1b: cards that can kill an own deathwish spy indirectly (targeted specials,
    // duels, created Thunder, tutors into Flails). The exact clone decides the result.
    private function AiSpyFinisherCandidate(card : CBetaGwentDuelCard, spy : CBetaGwentDuelCard) : bool
    {
        var id : int;var d : SBetaGwentDuelDefinition;
        if(AiAbilityDamage(card,spy)>0)return true;
        id=card.TemplateId();d=card.Definition();
        if(d.effect==28 && d.amount>0)return true;
        return id==201618 || id==122207 || id==201628 || id==122307 || id==122103 || id==200019 || id==122108 || id==112106;
    }
    private function AiAbilityDamage(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition;var t : SBetaGwentCardSnapshot;var id : int;
        if(!source)return 0;d=source.Definition();id=source.TemplateId();
        if(d.effect==1 || d.effect==6 || d.effect==25 || d.effect==27)return d.amount;
        if(d.effect!=34)return 0;
        // Cyclops second stage: the stored power of the destroyed ally is the damage.
        if(d.specialMode==22 && source.monsterStage==1)return source.monsterStored;
        // Madman Lugos' second stage deals the discarded unit's base power.
        if(id==152106 && source.monsterStage==1)return source.monsterStored;
        if(d.specialMode==102 || d.specialMode==117 || d.specialMode==118 || d.specialMode==143 || d.specialMode==144)return d.amount;
        if(id==142310)return BetaGwentNorthPick(source.monsterStage==0,3,1);
        if(id==200535 || id==142209){t=source.Snapshot();return t.power.currentPower;}
        if(id==142103)return 8;
        if(id==162209 || id==162310 || id==200139)return 7;
        if(id==152207)return 6;
        if(id==162306)return 5;
        if(id==162308 || id==200028 || id==142314)return 2;
        if(id==132409)return 4;
        if(id==162305){if(target){t=target.Snapshot();if((t.tokenMask&128)!=0)return 6;}return 3;}
        if(id==152304)return 3;
        if(id==152203)return 1;
        if(id==200124)return NilfAlchemy(NorthActingSide(source));
        return 0;
    }
    private function AiAbilityBoost(source : CBetaGwentDuelCard) : int
    {
        var d : SBetaGwentDuelDefinition;var id : int;
        if(!source)return 0;d=source.Definition();id=source.TemplateId();
        if(d.effect==2)return d.amount;
        if(id==162315)return 12;
        if(id==162313)return 5;
        if(id==162309)return 3;
        if(id==152311)return 2;
        return 0;
    }
    private function AiSpyDeathwishValue(s : SBetaGwentCardSnapshot, side : int) : int
    {
        var i,least,value,count,beneficiary : int;var t : SBetaGwentCardSnapshot;
        if((s.tokenMask&4)!=0)return 0;
        if(s.runtimeTemplate.templateId==112215){
            beneficiary=BetaGwentOpponentId(s.positionPlayerId);
            for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();if(t.positionPlayerId==beneficiary && (t.locationMask&7)!=0 && !t.isWaitingToDie && (t.tokenMask&8)==0 && t.runtimeTemplate.typeMask==4)count+=1;}
            value=Min(5,count)*5;if(beneficiary!=side)value=-value;return value;
        }
        // Undvik's deathwish boosts every living opposing Hjalmar by ten.
        // This is immediate resolved power, including after the enemy passed.
        if(s.runtimeTemplate.templateId==152401){
            beneficiary=BetaGwentOpponentId(s.positionPlayerId);
            for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
                if(t.positionPlayerId==beneficiary && t.runtimeTemplate.templateId==152101
                    && (t.locationMask&7)!=0 && !t.isWaitingToDie)value+=10;}
            if(beneficiary!=side)value=-value;return value;
        }
        if(s.runtimeTemplate.templateId!=122206)return 0;
        least=2147483647;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.instanceId==s.instanceId || t.positionPlayerId!=s.positionPlayerId || t.locationMask!=s.locationMask || t.isWaitingToDie || (t.tokenMask&8)!=0)continue;
            least=Min(least,t.power.currentPower);}
        if(least==2147483647)return 0;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();
            if(t.instanceId==s.instanceId || t.positionPlayerId!=s.positionPlayerId || t.locationMask!=s.locationMask || t.isWaitingToDie || (t.tokenMask&8)!=0)continue;
            value+=t.power.currentPower-least;}
        if(s.positionPlayerId==side)value=-value;return value;
    }
    // Sweers mills copies; current target strength is not the payoff. Anonymized
    // enemy deck placeholders must never be mistaken for real matching copies.
    private function AiSweersTargetValue(target : CBetaGwentDuelCard) : int
    {
        var t,s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var i,remaining,deck,hiddenHand,future : int;
        if(!target)return 0;t=target.Snapshot();d=target.Definition();
        if(t.positionPlayerId!=1)return 0;deck=CountLocation(1,16);if(deck==0)return 0;
        remaining=BetaGwentNorthPick(t.runtimeTierMask==2,3,1);
        if(BetaGwentAIStrength()>=4 && aiStartingDeckOne.Size()>0){remaining=0;for(i=0;i<aiStartingDeckOne.Size();i+=1)if(aiStartingDeckOne[i]==t.runtimeTemplate.templateId)remaining+=1;}
        hiddenHand=CountLocation(1,8);
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0)hiddenHand-=1;
            if(s.ownerId!=1 || live[i].createdCopy)continue;
            if((s.locationMask&39)==0 && s.locationMask!=512 && !(s.locationMask==8 && (s.tokenMask&64)!=0))continue;
            if((s.tokenMask&8)==0 && s.runtimeTemplate.templateId==t.runtimeTemplate.templateId)remaining-=1;
        }
        remaining=Max(0,remaining);if(remaining==0)return 0;
        future=Max(3,Min(14,d.header.power+BetaGwentAIEngine(t.runtimeTemplate.templateId)*2));
        return remaining*future*deck/Max(1,deck+Max(0,hiddenHand));
    }
    // Future value of the actual instance returned by Emhyr. Once-only drawing
    // spies keep timer=0 in hand; replaying one gives the body to the opponent.
    private function AiEmhyrReplayValue(target : CBetaGwentDuelCard, side : int) : int
    {
        var t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;var value : int;
        if(!target)return 0;t=target.Snapshot();d=target.Definition();
        value=t.power.basePower+t.power.permanentPower;
        if(BetaGwentDuelSpying(d.header.templateId))value=-value;
        if(AiDrawSpy(d.header.templateId) && t.timerValue==0)return value;
        return value+AiManagedDeployValue(d,side)+archetypeAI.PublicDeployGain(d)+AiDrawUtility(d,side);
    }
    private function AiAbilityChoiceValue(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard, kind : int) : int
    {
        var s,t : SBetaGwentCardSnapshot;var d,td : SBetaGwentDuelDefinition;
        var id,side,value,amount : int;var m : SBetaGwentMatchSnapshot;
        s=source.Snapshot();t=target.Snapshot();side=NilfDecisionSide();
        if(AiRevealingChoice(source))return AiRevealValue(t,side);
        if(t.locationMask==8 && t.positionPlayerId!=side && (t.tokenMask&64)==0)return 0;
        d=source.Definition();td=target.Definition();id=source.TemplateId();value=t.power.currentPower;
        if(id==162206)return AiSweersTargetValue(target);
        // Ability-graph boosters need the same public reset/Menno protection
        // as direct boost spells. A constant tie used to pick the first spy.
        if(kind==0 && (id==162313 || id==162315))return TargetValue(t,side,2,AiAbilityBoost(source))+AiEngineValue(t,side);
        // Mixed-zone requests are effects on existing instances, not tutors.
        // Serrit deals seven on the field, but sets a revealed hand unit to one.
        if(id==162209){
            if(t.locationMask==8){m=match.Snapshot();if(m.playerOne.hasPassed)return 0;
                value=Max(0,t.power.currentPower-1);
                if(BetaGwentDuelSpying(td.header.templateId) && td.header.templateId!=162212)value=-value;
                return value;}
            return AiDamageChoice(t,side,7);
        }
        // Brigade boosts by three. A held spy would give that boost away;
        // field targets retain the normal reset/Menno exposure correction.
        if(id==162309){
            if(t.locationMask==8){if(BetaGwentDuelSpying(td.header.templateId) && td.header.templateId!=162212)return -3;return 3;}
            return TargetValue(t,side,2,3);
        }
        if(kind==0 && id==152107)return TargetValue(t,side,20,0);
        // Stage 131: Kaedweni Cavalry strips armour and gains it. Stopping an enemy armour
        // engine (Redanian Knight-Elect) is the best use. A Redanian Elite gains 5 when its armour
        // reaches zero and a Redanian Knight rebuilds: good on an own card, bad on an enemy one.
        if(id==122314){
            amount=t.power.armor;
            if(t.runtimeTemplate.templateId==122317)value=5;else if(t.runtimeTemplate.templateId==122308)value=2;else value=0;
            if(t.positionPlayerId!=side)return amount+amount/2+AiEngineValue(t,side)-value;
            if(value>0)return amount+value;
            return amount-AiEngineValue(t,side)-amount/2-4;
        }
        // Draig Bon-Dhu strengthens what the Priestesses of Freya will raise: bronze soldiers.
        if(id==152205 && (t.locationMask&32)!=0){if(t.runtimeTierMask==2 && BetaGwentSkelligeCategory(t.runtimeTemplate.templateId,4))return value+10;return value;}
        if(kind==0 && id==152203)return AiDamageChoice(t,side,1)+AiFriendlyDamageSetup(t,side,1);
        if(kind==2){
            // Bran discards cards: choose cards that return themselves first,
            // then low-utility bronze, preserving gold and expensive tutors.
            if(id==200159){if(t.runtimeTemplate.templateId==152209 || t.runtimeTemplate.templateId==152316)return 100;
                return -value-AiReserveCost(td)*4;}
            if(td.effect==29)return AiPileCandidateValue(target,side,AiHorizon(side)==0,0);
            if(side==2 && BetaGwentDuelPlayChoice(id))return AiCardTempo(target,AiHorizon(side)==0,BestVranAnchor(side),AiPublicClearRisk());
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
        amount=AiAbilityDamage(source,target);
        if(kind==0 && amount>0)return AiDamageChoice(t,side,amount)+AiFriendlyDamageSetup(t,side,amount);
        // Friendly consume requests negate this score: preserve live engines,
        // especially Behemoths whose remaining charges create token points.
        if(d.specialMode==11 && t.positionPlayerId==side){
            if(t.runtimeTemplate.templateId==132201 && (t.tokenMask&4)==0 && t.timerValue>0)return value+24+t.timerValue*3;
            return value+AiEngineValue(t,side)*2;
        }
        if(d.effect==34 && d.specialMode==137)return AiDuelTarget(source,t,false);
        if(id==200162 && source.monsterStage>=1){
            value=AiEmhyrReplayValue(target,side)-t.power.currentPower;
            m=match.Snapshot();if(m.playerOne.hasPassed)value+=weather.Hazard(side,t.locationMask)*3;
            return value;
        }
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
        // Radovid V (lock toggle, damage to enemies) and Ciaran (lock toggle, move):
        // value the lock change itself, never the target's raw power.
        if(d.specialMode==134){if(t.positionPlayerId!=side)return LockToggleValue(t,side)+AiDamageChoice(t,side,d.amount);return LockToggleValue(t,side);}
        if(d.specialMode==404 || id==132205){value=LockToggleValue(t,side);if(id==132205 && t.positionPlayerId!=side)value+=t.power.currentPower/2;return value;}
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
    // Future-only corrections for exact choices: never count the immediate swing twice.
    private function AiChoiceFutureValue(source : CBetaGwentDuelCard, target : CBetaGwentDuelCard) : int
    {
        var s,t : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;var side,damage,boost,future : int;
        if(!source || !target)return 0;
        s=source.Snapshot();t=target.Snapshot();d=source.Definition();side=NilfDecisionSide();
        damage=AiAbilityDamage(source,target);
        // Exact target simulation already counts removing the body from the board;
        // add only its future replay value, including a spent spy's negative body.
        if(source.TemplateId()==200162 && source.monsterStage>=1)return AiEmhyrReplayValue(target,side);
        if(side==2 && archetypeAI && t.positionPlayerId==2 && (d.specialMode==11 || d.effect==16 || d.effect==23) && archetypeAI.FoodPenalty(t)!=0)return -archetypeAI.FoodPenalty(t);
        // Exact boost choices see only the immediate points; a boost on a unit the
        // opponent can still destroy (spy vs Menno) or reset is mostly lost later.
        boost=AiAbilityBoost(source);
        if(side==2 && t.positionPlayerId==2 && boost>0)return -AiBoostExposure(t,2,boost);
        // A one-tick enemy Miruna resolves at the next turn start inside the
        // exact choice simulation. Do not add her prevented charm a second time.
        if(t.runtimeTemplate.templateId==132108 && t.timerValue==1 && t.positionPlayerId!=s.positionPlayerId)return 0;
        if(damage>0){
            future=AiDamageChoice(t,side,damage)-AiDamageChoice(t,side,damage,true)+AiFriendlyDamageSetup(t,side,damage);
            // A due enemy swordsman heals during the exact choice's next-turn
            // transition. Retain the heuristic correction, but never debit it twice.
            if(t.positionPlayerId!=side && t.timerValue==1)future+=AiRegenerationLoss(t,side,damage);
            return future;
        }
        if(d.specialMode==114 || d.specialMode==134 || d.specialMode==404 || source.TemplateId()==162208 || source.TemplateId()==152204)return LockToggleValue(t,side);
        if(source.TemplateId()==152107)return TargetValue(t,side,20,0)-TargetValue(t,side,20,0,true);
        if(source.TemplateId()==152203)return AiFriendlyDamageSetup(t,side,1);
        if(d.specialMode==11 && t.positionPlayerId==side && (t.tokenMask&4)==0 && BetaGwentAIEngine(t.runtimeTemplate.templateId)>0 && t.runtimeTemplate.templateId!=132305)
            return -AiEngineValue(t,side)*2;
        return 0;
    }
    private function AiRevealingChoice(source : CBetaGwentDuelCard) : bool
    { return source && (source.TemplateId()==162316 || source.TemplateId()==200163); }
    private function AiRevealValue(t : SBetaGwentCardSnapshot, side : int) : int
    {
        var i,value,total,count,enemy,remaining,unknown,deck : int;var s : SBetaGwentCardSnapshot;
        if(t.locationMask!=8 || (t.tokenMask&64)!=0)return 0;
        enemy=BetaGwentOpponentId(side);
        // An unrevealed opposing identity is never inspected. Information and
        // our own known golem pool are enough to value the legal reveal.
        if(t.positionPlayerId==enemy){
            value=2;
            if(BestOwnRow(side)!=0){
                for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                    if(s.positionPlayerId==side && s.locationMask==16 && s.runtimeTemplate.templateId==132407 && (s.tokenMask&264)==0 && !NorthSummonPending(live[i])){total+=s.power.currentPower;count+=1;}}
                if(count>0)value+=total/count;
            }
            return value;
        }
        value=-2;
        if((t.tokenMask&4)==0){
            if(t.runtimeTemplate.templateId==162301)value+=t.power.currentPower;
            if(t.runtimeTemplate.templateId==162306)value+=Max(0,BestEffectValue(side,1,5,2));
        }
        // Own reveals can release an opposing golem. Estimate only from the
        // public starting list/spent cards and pile sizes, never hidden templates.
        deck=CountLocation(enemy,16);unknown=CountLocation(enemy,8);
        if(side==2 && deck>0 && BestOwnRow(enemy)!=0){
            if(BetaGwentAIStrength()>=4 && aiStartingDeckOne.Size()>0){
                for(i=0;i<aiStartingDeckOne.Size();i+=1)if(aiStartingDeckOne[i]==132407)remaining+=1;
                for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                    if(s.positionPlayerId==enemy && s.locationMask==8 && (s.tokenMask&64)!=0)unknown-=1;
                    if(s.ownerId==enemy && !live[i].createdCopy && (s.tokenMask&8)==0
                        && ((s.locationMask&39)!=0 || s.locationMask==512 || s.locationMask==8 && (s.tokenMask&64)!=0)
                        && s.runtimeTemplate.templateId==132407)remaining-=1;}
            }else remaining=1;
            value-=Min(3,Max(0,remaining)*3*deck/Max(1,deck+Max(0,unknown)));
        }
        return value;
    }
    private function AiFriendlyDamageSetup(t : SBetaGwentCardSnapshot, side : int, amount : int) : int
    {
        var damage,base : int;
        if(t.positionPlayerId!=side || t.runtimeTemplate.templateId!=200040 || (t.tokenMask&4)!=0 || AiHorizon(side)==0)return 0;
        damage=Max(0,amount-t.power.armor);base=t.power.basePower+t.power.permanentPower;
        if(damage==0 || damage>=t.power.currentPower || t.power.currentPower<base)return 0;
        // Only newly enabled healing/strengthening matters. Already damaged swordsmen
        // will trigger anyway. A timer of one is the nearest reliable payoff.
        if(t.timerValue==1)return damage+2;
        if(t.timerValue==2 && AiHorizon(side)>=2)return damage+1;
        return 0;
    }
    private function DamageValue(cardState : SBetaGwentCardSnapshot, side : int, amount : int) : int
    {
        var damage : int;
        if(cardState.positionPlayerId!=side && (cardState.tokenMask&8)!=0)return 0;
        damage = amount - cardState.power.armor;
        if (damage < 0) damage = 0;
        if (damage > cardState.power.currentPower) damage = cardState.power.currentPower;
        if (cardState.positionPlayerId == side) return -damage;
        return damage;
    }
    private function LockToggleValue(cardState : SBetaGwentCardSnapshot, side : int) : int
    {
        var d, tokenDefinition : SBetaGwentDuelDefinition; var value : int;var active : SBetaGwentCardSnapshot;
        if(AiHorizon(side)==0)return 0;
        // Locking a face-down ambush is legal, but its identity/ability is unknown.
        if(cardState.positionPlayerId!=side && (cardState.tokenMask&8)!=0)return 2;
        d = BetaGwentDuelDefinition(cardState.runtimeTemplate.templateId);
        // Evaluate the active instance for both lock and unlock. In particular,
        // template priors must not restore spent charges, missing neighbours
        // or destroyed armour after the instance evaluator removed that value.
        active=cardState;if((active.tokenMask&4)!=0)active.tokenMask-=4;
        value=AiEngineValue(active,side);
        if (cardState.runtimeTemplate.templateId == 132310 && weather.Token(BetaGwentOpponentId(cardState.positionPlayerId), cardState.locationMask) == 1) value += 3;
        if (d.deathwishDamage > 0) value += 2;
        if (d.deathwishSummonTemplate > 0) value += DeckSummonValue(cardState.positionPlayerId, d.deathwishSummonTemplate);
        if (d.deathwishSpawnCount > 0)
        { tokenDefinition = BetaGwentDuelDefinition(d.deathwishSpawnTemplate); value += d.deathwishSpawnCount * tokenDefinition.header.power; }
        if (cardState.positionPlayerId == side) value = -value;
        if ((cardState.tokenMask & 4) != 0) value = -value;
        return value;
    }
    // Value only newly activated armour engines, using the actual eligible neighbours.
    // The immediate estimate stays separate: exact play simulation processes turn-end events.
    private function AiArmorRestoreValue(s : SBetaGwentCardSnapshot, addedArmor : int) : int
    {
        var i, neighbours : int;var t : SBetaGwentCardSnapshot;
        if(addedArmor<=0 || s.runtimeTemplate.templateId!=123301 || s.power.armor>0
            || (s.tokenMask&12)!=0 || s.isWaitingToDie || (s.locationMask&7)==0)return 0;
        for(i=0;i<live.Size();i+=1){
            t=live[i].Snapshot();
            if(t.positionPlayerId==s.positionPlayerId && t.locationMask==s.locationMask
                && Abs(t.locationIndex-s.locationIndex)==1 && (t.runtimeTierMask&15)!=0
                && (t.runtimeTemplate.typeMask&4)!=0 && (t.tokenMask&8)==0 && !t.isWaitingToDie)neighbours+=1;
        }
        // Even after the opponent passes, the restored engine ticks at this turn's end.
        return neighbours*Max(1,AiHorizon(s.positionPlayerId));
    }
    private function TargetValue(cardState : SBetaGwentCardSnapshot, side : int, effect : int, amount : int, optional immediate : bool, optional addedArmor : int) : int
    {
        var i, value, offset : int; var other : SBetaGwentCardSnapshot; var d, tokenDefinition : SBetaGwentDuelDefinition;
        if(cardState.positionPlayerId!=side && (cardState.tokenMask&8)!=0){
            if(!immediate && (effect==18 || effect==19))return LockToggleValue(cardState,side);
            return 0;
        }
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
            value = ConsumePassiveValue(side, cardState.instanceId) + AiConsumeSpawnValue(side, cardState.instanceId);
            if ((cardState.tokenMask & 12) == 0) value += d.beforeConsumeAttackerBoost;
            if (cardState.positionPlayerId != side)
            {
                value += cardState.power.currentPower * 2;
                // A consumed enemy engine or pending Miruna charm is removed too, as for damage kills.
                if (!immediate) value += AiEngineValue(cardState, side);
            }
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
            if (side == 2 && archetypeAI) value -= archetypeAI.FoodPenalty(cardState);
            // Archespore deathwish: 4 damage to a random enemy unit.
            if (cardState.runtimeTemplate.templateId == 200038 && (cardState.tokenMask & 4) == 0)
            { if (cardState.positionPlayerId == side) value += 4; else value -= 4; }
            return value;
        }
        if (effect == 22)
        { if (cardState.positionPlayerId == side) return 0; return Min(cardState.power.currentPower, amount) * 2; }
        if (effect == 7)
        { if (cardState.positionPlayerId == side) return 0; return (cardState.power.currentPower / 2) * 2; }
        if (effect == 2) { if (cardState.positionPlayerId == side) return amount-AiBoostExposure(cardState,side,amount); return -amount; }
        if (effect == 3)
        {
            for (i = 0; i < live.Size(); i += 1)
            {
                other = live[i].Snapshot(); offset = other.locationIndex - cardState.locationIndex;
                if (other.positionPlayerId != cardState.positionPlayerId || other.locationMask != cardState.locationMask
                    || offset < -1 || offset > 1) continue;
                value += amount;
                if(!immediate)value+=AiArmorRestoreValue(other,addedArmor);
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
        if(effect==3 && pendingCard)d=pendingCard.Definition();
        if (effect == 6) amount = CountLocation(side, 8);
        if (effect == 16 && pendingCard) { d = pendingCard.Definition(); amount = d.consumeMaximum; }
        for (i = 0; i < pendingIds.Size(); i += 1)
        {
            c = registry.Find(pendingIds[i]); cardState = c.Snapshot(); value = TargetValue(cardState, side, effect, amount, false, d.addedArmor);
            if(effect==1 || effect==6)value=AiDamageChoice(cardState,side,amount);
            if (effect == 28 && pendingCard) { d = pendingCard.Definition(); value = specials.TargetValue(d, cardState, side); }
            AiExplain("TARGET_OPTION", "request="+requestId+" target="+cardState.instanceId+" effect="+effect+" amount="+amount+" value="+value);
            if (value > maximum) { maximum = value; best = cardState.instanceId; }
        }
        if ((effect == 3 || effect == 6 || effect == 7 || effect == 16 || effect == 17 || effect == 18 || effect == 22) && maximum <= 0) return 0;
        if (effect == 28 && pendingCard) { d = pendingCard.Definition(); if (d.header.templateId!=113201 && d.targetMinimum == 0 && maximum <= 0) return 0; }
        AiExplain("TARGET_SELECT", "request="+requestId+" target="+best+" effect="+effect+" value="+maximum+" reason=highest_legal_target_value");
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
            value = TargetValue(cardState, side, effect, amount, immediate, d.addedArmor); if (value > maximum) maximum = value;
        }
        return maximum;
    }
    private function EpidemicValue(side : int) : int
    {
        var i, lowest, value : int; var cardState : SBetaGwentCardSnapshot;
        lowest = 2147483647;
        for (i = 0; i < live.Size(); i += 1)
        { cardState = live[i].Snapshot(); if (EpidemicEligible(cardState) && cardState.power.currentPower < lowest) lowest = cardState.power.currentPower; }
        for (i = 0; i < live.Size(); i += 1)
        {
            cardState = live[i].Snapshot(); if (!EpidemicEligible(cardState) || cardState.power.currentPower != lowest) continue;
            if (cardState.positionPlayerId == side) value -= lowest; else value += lowest;
        }
        return value;
    }
    public function BestVranAnchor(side : int) : int
    {
        var i,j,k,best,value,maximum,horizon : int; var s,t : SBetaGwentCardSnapshot;var d,td : SBetaGwentDuelDefinition;
        maximum = 0;
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot();
            if (s.positionPlayerId != side || (s.locationMask & 7) == 0 || s.runtimeTemplate.typeMask != 4
                || s.isWaitingToDie || s.power.currentPower <= 0 || CountLocation(side, s.locationMask) >= 9) continue;
            d=live[i].Definition();if(d.effect==23 || ((s.tokenMask&4)==0 && BetaGwentAIEngine(s.runtimeTemplate.templateId)>0 && s.runtimeTemplate.templateId!=132305))continue;
            // Keep separate consuming engines; consume fodder and deathwish units.
            value = TargetValue(s, side, 16, 2147483647);
            // Vran eats to its right. Prefer an uninterrupted chain of food,
            // so placing between two eggs does not strand the left egg.
            horizon=Min(2,AiHorizon(side)/2);
            for(k=1;k<=horizon;k+=1)for(j=0;j<live.Size();j+=1){
                t=live[j].Snapshot();
                if(t.positionPlayerId!=side || t.locationMask!=s.locationMask || t.locationIndex!=s.locationIndex+k || t.isWaitingToDie)continue;
                td=live[j].Definition();
                if(td.effect==23 || ((t.tokenMask&4)==0 && BetaGwentAIEngine(t.runtimeTemplate.templateId)>0 && t.runtimeTemplate.templateId!=132305)){horizon=0;break;}
                value+=Max(0,TargetValue(t,side,16,2147483647))/(k+1);
            }
            if (value > maximum) { maximum = value; best = s.instanceId; }
        }
        return best;
    }
    // Tempo is the immediate score swing; forecasts only rank normal turns.
    // This reads snapshots and own/public zones, never executes a play or RNG.
    // Conditional future utility only; never counted as already earned catch-up points.
    private function AiNeighbourEngineUtility(card : CBetaGwentDuelCard) : int
    {
        var s,t : SBetaGwentCardSnapshot;var cards : array<CBetaGwentDuelCard>;
        var d : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
        var row,index,horizon,i,count,value : int;
        s=card.Snapshot();d=card.Definition();m=match.Snapshot();
        if(m.playerOne.hasPassed || CountLocation(1,8)==0 || (s.tokenMask&4)!=0)return 0;
        horizon=Min(3,AiHorizon(2));
        if(d.header.templateId==152309){
            if(!AiShipSlot(2,d,row,index))return 0;LocationCards(2,row,cards);
            if(index>=cards.Size())return 0;
            return Max(0,2+AiShipRightGain(cards[index].Snapshot(),2))*Max(0,horizon-1);
        }
        if(d.header.templateId==123301 && s.power.armor>0){
            if(!AiSupportSlot(2,d,row,index))return 0;LocationCards(2,row,cards);
            if(index>0)count+=1;if(index<cards.Size())count+=1;
            return count*Max(0,horizon-1);
        }
        if(d.header.templateId!=142204 && d.header.templateId!=142208)return 0;
        if(d.header.templateId==142208){
            // Enemy hand size is public; its card types and future targets are unknown.
            value=Max(0,BestEffectValue(2,1,7,2));
            return Min(7,Max(3,value))*Min(3,CountLocation(1,8))/3;
        }
        if((s.locationMask&7)!=0)row=s.locationMask;else row=AiAdjacencyRow(card,2,BestOwnRow(2));
        LocationCards(2,row,cards);
        for(i=0;i<cards.Size();i+=1){t=cards[i].Snapshot();if(t.instanceId!=s.instanceId && !t.isWaitingToDie && (t.tokenMask&8)==0 && t.runtimeTemplate.typeMask==4)count+=1;}
        return Min(4,count)*2;
    }
    public function AiCardTempo(card : CBetaGwentDuelCard, immediate : bool, vranAnchor : int, clearRisk : int) : int
    {
        var s,vranTarget : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var d : SBetaGwentDuelDefinition;var value,effectValue,row : int;
        s=card.Snapshot();m=match.Snapshot();
        d = card.Definition(); value = s.power.currentPower;
        if(!immediate)value+=AiNeighbourEngineUtility(card);
        if(BetaGwentDuelSpying(d.header.templateId))value=-value;
        if(AiDrawSpy(d.header.templateId) && s.timerValue==0)return value;
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
        if (d.effect == 28) value += specials.Value(card,immediate);
        if (d.effect == 33) value += ModeValue(d, BestModeChoice(d, 2), 2, immediate);
        if (d.effect == 4) value += RowEffectValue(2, 1, BestEnemyRow(2), d.amount);
        if (d.effect == 5) value += EpidemicValue(2);
        if (!immediate && d.weatherToken != 0) value += WeatherValue(2, BestWeatherRow(2, d.weatherToken), d.weatherToken) * (100 - clearRisk * BetaGwentAITune(17) / 100) / 100;
        if (d.effect == 9) {
            if(immediate){if(ChooseFirstLight(2)==113401)value+=weather.ClearValue(2,d.amount,true);else value+=RallyValue(2,true);}
            else value+=Max(weather.ClearValue(2,d.amount),RallyValue(2));
        }
        if(d.effect==10)value+=weather.ClearValue(2,d.amount,immediate);
        if (!immediate && d.effect == 14 && HasDeckTemplate(2, d.playTemplateId)) value += AiPlayedWeatherValue(2, d.playTemplateId);
        if(!immediate)value+=AiClearDeployGain(d,2);
        if(d.effect==23 && vranAnchor!=0)
        { vranTarget=FindCard(vranAnchor).Snapshot();value+=Max(0,TargetValue(vranTarget,2,16,2147483647,immediate)); }
        if (!immediate && d.timerPeriod > 0 && !m.playerOne.hasPassed) value += 2;
        if (!immediate && d.passiveBoost != 0 && HasWeather(d.passiveWeatherToken)) value += d.passiveBoost * AiHorizon(2);
        if (!immediate && d.deathwishDamage != 0 && !m.playerOne.hasPassed) value += Max(0, RowEffectValue(2, 1, BestCardRow(2, d), d.deathwishDamage)) * BetaGwentAITune(26) / 100;
        if (!immediate && d.deathwishSummonTemplate > 0 && !m.playerOne.hasPassed) value += DeckSummonValue(2, d.deathwishSummonTemplate) * BetaGwentAITune(26) / 100;
        // The profile supplies a complete estimate only for its own supported
        // weather/Hunt cards. Ordinary removal, armour and tutors keep theirs.
        if(weatherProfile && weatherAI.Handles(d))value=weatherAI.Gain(d,s.power.currentPower,false,s.locationMask==8,immediate);
        return value;
    }
    // Exact immediate tempo of playing this card now (row as chosen by BestCardRow).
    // Implemented by the simulation clone; -2147483647 when unavailable.
    // ---- Generation 3/4 lookahead on cloned sessions (own cards only; the opponent's
    // hidden hand and deck are never read by these evaluations).
    public function AiSimClone() : CBetaGwentDuelSession
    {
        var cloner : CBetaGwentCloner; var g : CBetaGwentDuelSession;
        var seed,i : int; var m : SBetaGwentMatchSnapshot;
        aiCloneEpoch += 1; cloner = new CBetaGwentCloner in this;
        g = cloner.CloneSession(this, aiCloneEpoch);
        if (!g) return NULL;
        // Search must not consume the game's global RNG. All candidates at the
        // same decision use the same independent random stream.
        m = match.Snapshot();seed = random.InitialSeed() % 1000000 + random.DrawCount() * 97 + m.roundNumber * 1009;
        g.aiSimulating = true; g.externalPolicyMask = 0; g.recordVisuals = false; g.random.Initialize(Max(1, seed));
        g.aiSimCloner = cloner;g.nilfInitialOne.Clear();g.presetOne=0;
        for(i=0;i<g.live.Size();i+=1)g.live[i].HideUnknownFromAi();
        // The source cache may predate the previous simulated action. Bind
        // every new node to its current cards, including generated units.
        g.archetypeAI.Refresh();
        return g;
    }
    // Disposable shadow seat: run the same side-2 rules as a plausible player reply.
    public function AiReverseClone() : CBetaGwentDuelSession
    {
        var cloner : CBetaGwentCloner; var g : CBetaGwentDuelSession;
        if(!aiSimulating)return NULL;
        aiCloneEpoch+=1;cloner=new CBetaGwentCloner in this;
        g=cloner.CloneSession(this,aiCloneEpoch,true);if(!g)return NULL;
        g.aiSimCloner=cloner;g.recordVisuals=false;g.aiSimulating=true;g.externalPolicyMask=0;
        g.weatherAI.Initialize(g);g.weatherProfile=g.weatherAI.Matches(g.nilfInitialTwo);
        g.archetypeAI.Initialize(g,g.nilfInitialTwo,g.presetTwo,g.leaderTemplateTwo);
        // Swapping cards/seats does not swap the meaning of a cached own
        // hand/board. Rebuild it before evaluating a plausible response.
        g.archetypeAI.Refresh();
        return g;
    }
    public function AiCounterRisk(card : CBetaGwentDuelCard, model : CBetaGwentPublicResponseAI) : int
    {
        var g,h : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot;var result,first : int;
        if(aiSimulating || !card || !model)return 0;
        s=card.Snapshot();if(AiPreparationIsReady() && s.instanceId==aiPreparedLeader && !AiLeaderSequencePlanning())return aiPreparedCounterRisk;
        BetaGwentAISimEnter();g=AiSimClone();s=card.Snapshot();
        if(g){first=g.AiSimPlay(s.instanceId);if(first!=-2147483647){h=model.Apply(g);result=model.penalty;}}
        BetaGwentAISimLeave();return result;
    }
    public var aiLastStrategicValue : int;
    // Only resolved board points may authorize a catch-up after a pass.
    // Banked boosts and thinning are returned separately for normal ordering.
    public function AiSimPlay(id : int) : int
    {
        var card : CBetaGwentDuelCard; var s : SBetaGwentCardSnapshot; var d : SBetaGwentDuelDefinition;
        var before, banked, row, anchor, deck, pulled : int; var ok : bool; var m : SBetaGwentMatchSnapshot;
        aiLastStrategicValue = 0;
        // Callers must not have to repair private caches between actions.
        archetypeAI.Refresh();
        card = FindCard(id); if (!card) return -2147483647;
        s = card.Snapshot(); d = card.Definition(); before = AiProjectedLead(); banked = AiSimBanked(s.instanceId)+AiResilientCarry(); deck = CountLocation(2, 16);
        if (s.locationMask == 64) ok = UseLeader(2);
        else
        {
            if (s.locationMask != 8 || !s.canBePlayed) return -2147483647;
            row = BestCardRow(2, d); if (row == 0) row = 1;
            if (d.effect == 23) anchor = BestVranAnchor(2);
            if (anchor == 0) anchor = AiPlacementAnchor(d);
            if (anchor != 0) ok = PlayBefore(2, id, anchor); else ok = Play(2, id, row);
        }
        if (!ok || fatal || IsPending()) return -2147483647;
        // Cards that pull other cards out of the deck (summons, "play from deck", draws) thin it:
        // later draws find the strong cards more often. Worth something while rounds remain.
        pulled = deck - CountLocation(2, 16); m = match.Snapshot();
        if (pulled > 0 && m.roundNumber < 3) {
            // Bran discards three cards; this is not three free plays/draws.
            if(d.header.templateId==200159)pulled=(pulled+2)/3;
            pulled = pulled * BetaGwentAITune(10);
        } else pulled = 0;
        aiLastStrategicValue = AiSimBanked(s.instanceId) + AiResilientCarry() - banked + pulled;
        return AiProjectedLead() - before;
    }
    // Value side 2 banked outside the score: boosts on units in hand (full) and deck
    // (half), and face-down ambushes on the board (their power is revealed later).
    private function AiSimBanked(optional playedId : int) : int
    {
        var i, total, deckBoost, boost : int; var t : SBetaGwentCardSnapshot;
        for (i = 0; i < live.Size(); i += 1)
        {
            t = live[i].Snapshot(); if (t.positionPlayerId != 2 || t.isWaitingToDie) continue;
            // The played unit's full current power is already in the resolved
            // board swing. Removing its stored hand boost must not cancel that
            // boost a second time (or refund a hand debuff as imaginary points).
            if(t.instanceId==playedId && (t.locationMask==8 || t.locationMask==16))continue;
            boost=t.power.currentPower-t.power.basePower;
            // A stronger held spy is a larger gift when replayed. False Ciri
            // is the returning-body exception, as in the target evaluator.
            if(BetaGwentDuelSpying(t.runtimeTemplate.templateId) && t.runtimeTemplate.templateId!=162212)boost=-boost;
            if (t.locationMask == 8 && t.runtimeTemplate.typeMask == 4) total += boost;
            else if (t.locationMask == 16 && t.runtimeTemplate.typeMask == 4) deckBoost += boost;
            else if ((t.locationMask & 7) != 0 && (t.tokenMask & 8) != 0) total += t.power.currentPower + AiAmbushPayoff(t);
        }
        // Apply the discount after summing: half of ten +1 boosts is five,
        // whereas integer rounding each card separately incorrectly gives zero.
        return total+deckBoost*BetaGwentAITune(27)/100+AiPendingCharmValue(2);
    }
    // 0.9.1b: a face-down ambush is worth its trigger, not only its body.
    // Public estimate: enemy board and hand size only, discounted for delay.
    private function AiAmbushPayoff(t : SBetaGwentCardSnapshot) : int
    {
        var i, best, id, neighbours : int; var e : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot;
        id = t.runtimeTemplate.templateId; m = match.Snapshot();
        if (id == 142204) {
            for (i = 0; i < live.Size(); i += 1) { e = live[i].Snapshot();
                if (e.positionPlayerId == 2 && e.locationMask == t.locationMask && e.instanceId != t.instanceId && Abs(e.locationIndex - t.locationIndex) <= 2 && !e.isWaitingToDie) neighbours += 1; }
            return Min(4, neighbours) * 2;
        }
        if (m.playerOne.hasPassed) return 0;
        if (id == 142208) { if (CountLocation(1, 8) > 0) return 5; return 0; }
        if (id == 201779) { if (CountLocation(1, 8) > 0) return 3; return 0; }
        if (id == 142210) {
            for (i = 0; i < live.Size(); i += 1) { e = live[i].Snapshot();
                if (e.positionPlayerId == 1 && (e.locationMask & 7) != 0 && !e.isWaitingToDie && (e.tokenMask & 8) == 0
                    && (e.runtimeTierMask & 6) != 0 && e.runtimeTemplate.typeMask == 4 && e.power.currentPower <= 5) best = Max(best, e.power.currentPower); }
            return Max(3, best);
        }
        return 0;
    }
    // Real decision time measured by the UI (synchronous native call). Slow machines
    // simulate fewer candidates; the cap recovers when decisions become fast again.
    public function AiPerfFeedback(ms : int, optional peakMs : int)
    {
        var totalLimit : int;
        if(aiPreparationStage>0 && !aiPreparationReady)return;
        totalLimit=2500;
        // Longer thought is acceptable when the UI measured short individual
        // calls. Missing/slow step measurements keep the conservative limit.
        if(BetaGwentAIStrength()>=4 && peakMs>0 && peakMs<25)totalLimit=8000;
        if (ms > totalLimit || peakMs > 50) aiSimDamp = Min(70, aiSimDamp + 25);
        else if (ms < 900 && peakMs < 25) aiSimDamp = Max(0, aiSimDamp - 10);
        BetaGwentLog("AI_PERF ms=" + ms + " peakMs="+peakMs+" damp=" + aiSimDamp);
    }
    // Keep the highest-ranked action, then cover different strategic roles within
    // the same simulation budget. A low-body engine must get a chance to resolve.
    public function AiSearchRole(d : SBetaGwentDuelDefinition) : int
    {
        if(BetaGwentAIEngine(d.header.templateId)>0 || d.passiveBoost>0 || d.initialTimer>0)return 1;
        if(d.effect==1 || d.effect==4 || d.effect==5 || d.effect==6 || d.effect==13 || d.effect==19 || d.effect==25 || d.effect==27)return 2;
        if(AiDrawSpy(d.header.templateId) || AiDrawUtility(d,2)>0)return 3;
        if(d.effect==2 || d.effect==3 || d.effect==16 || d.effect==17 || d.effect==23 || d.effect==29 || d.consumePassiveBoost>0)return 4;
        return 0;
    }
    public function AiDiversifySearch(out ids : array<int>, limit : int)
    {
        var chosen, roles : array<int>;var i,role,found,cheap,cost,bestCost : int;
        var d : SBetaGwentDuelDefinition;var m : SBetaGwentMatchSnapshot;
        if(ids.Size()<=1 || limit<=1)return;
        chosen.PushBack(ids[0]);roles.PushBack(AiSearchRole(live[ids[0]].Definition()));
        // After a pass, a low-body tutor/replay can be the cheapest winning
        // action. Give one such ability an exact trial inside the SAME budget:
        // printed-power ranking must not hide it behind expensive finishers.
        m=match.Snapshot();cheap=-1;bestCost=2147483647;
        if(m.playerOne.hasPassed && m.roundNumber<3){
            for(i=0;i<ids.Size();i+=1){d=live[ids[i]].Definition();
                if(d.effect!=34 && d.effect!=29 && d.pileLocation==0)continue;
                cost=AiReserveCost(d);
                if(cost<bestCost){cheap=i;bestCost=cost;}
            }
            if(cheap>=0 && !chosen.Contains(ids[cheap])){
                chosen.PushBack(ids[cheap]);roles.PushBack(AiSearchRole(live[ids[cheap]].Definition()));}
        }
        while(chosen.Size()<limit && chosen.Size()<ids.Size()){
            found=-1;
            for(i=1;i<ids.Size();i+=1){
                role=AiSearchRole(live[ids[i]].Definition());
                if(!chosen.Contains(ids[i]) && role>0 && !roles.Contains(role)){found=i;break;}
            }
            if(found<0)break;
            chosen.PushBack(ids[found]);roles.PushBack(AiSearchRole(live[ids[found]].Definition()));
        }
        for(i=0;i<ids.Size();i+=1)if(!chosen.Contains(ids[i]))chosen.PushBack(ids[i]);
        ids=chosen;
    }
    private function AiSimCap(tune : int) : int
    {
        var limit : int;limit=Max(2,BetaGwentAITune(tune)*(100-aiSimDamp)/100);
        if(tune==9 && AiShortRoundPlanning())limit=Max(limit,CountLocation(2,8));
        return limit;
    }
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
        var g : CBetaGwentDuelSession; var s : SBetaGwentCardSnapshot; var result,i : int; var ms : SBetaGwentMatchSnapshot;
        aiLastStrategicValue = 0;
        if (aiSimulating || !card) return -2147483647;
        s = card.Snapshot(); ms = match.Snapshot();
        if(AiPreparationIsReady())for(i=0;i<aiPreparedIds.Size();i+=1)if(aiPreparedIds[i]==s.instanceId){aiLastStrategicValue=aiPreparedStrategic[i];return aiPreparedValues[i];}
        if (s.runtimeTemplate.templateId == 162212 && s.positionPlayerId == 2 && !ms.playerOne.hasPassed) return AiFalseCiriReturn(s);
        BetaGwentAISimEnter();
        g = AiSimClone(); result = -2147483647;
        if (g) { result = g.AiSimPlay(s.instanceId); aiLastStrategicValue = g.aiLastStrategicValue; }
        BetaGwentAISimLeave();
        return result;
    }
    // Generation 4: how much better our other cards become after playing `card` first
    // (setup before payoff). Compares exact follow-up plays with their exact value now.
    // A complete, public two-card endgame: one ordinary Bronze body and
    // Scorch against one revealed ordinary Bronze body. No leaders, hazards,
    // active abilities or hidden target identities can create another reply.
    public function AiPlainLastReply() : bool
    {
        var cards : array<CBetaGwentDuelCard>;var i : int;var s : SBetaGwentCardSnapshot;
        var d : SBetaGwentDuelDefinition;var body,control : bool;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();
        if(m.roundNumber!=3 || m.playerOne.hasPassed || CountLocation(2,8)!=2 || CountLocation(1,8)!=1 || LeaderAvailable(1) || LeaderAvailable(2))return false;
        for(i=0;i<weather.hazards.Size();i+=1)if(weather.hazards[i]!=0)return false;
        if(weather.dreamRows.Size()>0)return false;
        GetZoneCards(1,8,cards);s=cards[0].Snapshot();
        if((s.tokenMask&64)==0)return false;
        d=cards[0].Definition();if(d.effect!=0 || d.header.typeMask!=4 || d.header.tierMask!=2)return false;
        GetZoneCards(2,8,cards);
        for(i=0;i<cards.Size();i+=1){d=cards[i].Definition();
            if(d.effect==28 && d.specialMode==6)control=true;
            else if(d.effect==0 && d.header.typeMask==4 && d.header.tierMask==2)body=true;
            else return false;
        }
        if(!body || !control)return false;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();if((s.locationMask&7)==0)continue;
            if((s.tokenMask&136)!=0 || s.timerValue>0)return false;
            d=live[i].Definition();
            if(d.effect!=0 || d.passiveBoost!=0 || d.deathwishDamage!=0 || d.deathwishSpawnCount!=0 || d.deathwishSummonTemplate!=0 || d.consumePassiveBoost!=0)return false;
        }
        return true;
    }
    public function AiSequenceUplift(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>, optional model : CBetaGwentPublicResponseAI) : int
    {
        var result,i : int;var s : SBetaGwentCardSnapshot;
        if (aiSimulating || !card) return 0;
        s=card.Snapshot();if(AiPreparationIsReady())for(i=0;i<aiPreparedUpliftIds.Size();i+=1)if(aiPreparedUpliftIds[i]==s.instanceId)return aiPreparedUplifts[i];
        BetaGwentAISimEnter(); result = AiSequenceUpliftInner(card, ids, values, model); BetaGwentAISimLeave();
        if(model)BetaGwentLog("DUEL_AI_RESPONSE card="+card.TemplateId()+" profiles="+model.eligibleProfiles+" replies="+model.evaluated+" rejected="+model.rejected+" risk="+model.penalty+" uplift="+result);
        return result;
    }
    // A setup leader changes the value of our next hand play just as a setup
    // card does. The old leader path stopped after the opposing reply and
    // never evaluated the resurrection/tutor/boost continuation it enabled.
    // Concealed enemy traps retain the conservative counter-only path.
    public function AiLeaderSequencePlanning() : bool
    {
        var i : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        m=match.Snapshot();
        if(aiSimulating || BetaGwentAIStrength()<3 || aiSimDamp>=50 || m.playerOne.hasPassed || CountLocation(2,8)==0)return false;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&8)!=0)return false;}
        return true;
    }
    private function AiSequenceUpliftInner(card : CBetaGwentDuelCard, ids : array<int>, values : array<int>, model : CBetaGwentPublicResponseAI) : int
    {
        var job : CBetaGwentAISequence188;var s : SBetaGwentCardSnapshot;
        if(aiSimulating || !card)return 0;s=card.Snapshot();
        job=new CBetaGwentAISequence188 in this;job.Initialize(this,s.instanceId,ids,values,model);
        while(!job.Step()){}return job.result;
    }
    // Resolve the actual sequence on one changing position: tutors cannot reuse
    // the same deck card, and attacks cannot spend the same dead target twice.
    private function AiChaseActual(actions : array<SBetaGwentAIChaseAction>, deficit : int) : SBetaGwentAIChasePlan
    {
        var job : CBetaGwentAIChase188;
        job=new CBetaGwentAIChase188 in this;job.Initialize(this,actions,deficit,AiSimCap(5));
        while(!job.Step()){}return job.best;
    }
    // 094b: copies of an ambush that may still be face down on the enemy
    // board. Uses only the separately authorized starting list (strength 4)
    // minus public originals and revealed hand cards; never hidden identities.
    public function AiAmbushCopiesLeft(templateId : int) : int
    {
        var i,remaining : int;var s : SBetaGwentCardSnapshot;
        if(BetaGwentAIStrength()<4 || aiStartingDeckOne.Size()==0)return 1;
        for(i=0;i<aiStartingDeckOne.Size();i+=1)if(aiStartingDeckOne[i]==templateId)remaining+=1;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.ownerId!=1 || live[i].createdCopy || s.runtimeTemplate.templateId!=templateId)continue;
            if((s.locationMask&39)!=0 && (s.tokenMask&8)==0 || s.locationMask==8 && (s.tokenMask&64)!=0)remaining-=1;
        }
        return Max(0,remaining);
    }
    // Flattened hypotheses: for hypothesis k, entries k*n..k*n+n-1 of
    // templates/timers belong to cards[0..n-1]. Timed ambushes (Malena,
    // Sappers) count down secretly, so both remaining timers are modelled.
    // Returns 0 when the old conservative behaviour must be kept.
    public function AiAmbushHypotheses(out cards : array<int>, out templates : array<int>, out timers : array<int>, out weights : array<int>) : int
    {
        var pool,optT,optTimer,optW,optC,pairFirst,pairSecond,pairWeight : array<int>;var i,j,k,n,cap,c,count,w,at : int;var s : SBetaGwentCardSnapshot;
        cards.Clear();templates.Clear();timers.Clear();weights.Clear();
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&8)!=0)cards.PushBack(s.instanceId);}
        n=cards.Size();
        if(n==0 || n>2 || BetaGwentAIStrength()<3 || aiSimDamp>=70){cards.Clear();return 0;}
        cap=2;if(BetaGwentAIStrength()>=4)cap=4;if(aiSimDamp>=50)cap=1;
        // Fixed order breaks weight ties toward the more punishing trigger.
        pool.PushBack(142208);pool.PushBack(142210);pool.PushBack(201779);pool.PushBack(142204);pool.PushBack(142307);
        for(i=0;i<pool.Size();i+=1){c=AiAmbushCopiesLeft(pool[i]);if(c<=0)continue;
            if(pool[i]==142210 || pool[i]==142307){
                for(j=1;j<=2;j+=1){w=c;k=0;while(k<optW.Size() && optW[k]>=w)k+=1;
                    optT.Insert(k,pool[i]);optTimer.Insert(k,j);optW.Insert(k,w);optC.Insert(k,c);}
            }else{w=2*c;k=0;while(k<optW.Size() && optW[k]>=w)k+=1;
                optT.Insert(k,pool[i]);optTimer.Insert(k,-1);optW.Insert(k,w);optC.Insert(k,c);}
        }
        if(optT.Size()==0){cards.Clear();return 0;}
        if(n==1){
            for(k=0;k<optT.Size() && count<cap;k+=1){templates.PushBack(optT[k]);timers.PushBack(optTimer[k]);weights.PushBack(optW[k]);count+=1;}
        }else{
            // Public copies are sampled without replacement. Both card order
            // and timer order matter: two Malenas allow (1,1),(1,2),(2,1),(2,2).
            // Rank the at-most49 legal pairs, then retain the existing1/2/4 cap.
            // This enumerates metadata only; simulated-action budget is unchanged.
            for(k=0;k<optT.Size();k+=1)for(j=0;j<optT.Size();j+=1){
                if(optT[k]==optT[j] && optC[k]<2)continue;
                w=optW[k]*optW[j];
                if(optT[k]==optT[j])w=w*(optC[k]-1)/optC[k];
                w=Max(1,w);at=0;while(at<pairWeight.Size() && pairWeight[at]>=w)at+=1;
                pairFirst.Insert(at,k);pairSecond.Insert(at,j);pairWeight.Insert(at,w);
            }
            for(at=0;at<pairFirst.Size() && count<cap;at+=1){
                k=pairFirst[at];j=pairSecond[at];
                templates.PushBack(optT[k]);timers.PushBack(optTimer[k]);templates.PushBack(optT[j]);timers.PushBack(optTimer[j]);
                weights.PushBack(pairWeight[at]);count+=1;
            }
        }
        if(count==0)cards.Clear();
        return count;
    }
    // Board swing of a hypothesised trap: own score minus enemy score, where
    // revealed hypothesis bodies are excluded (they reveal sooner or later and
    // are not the price of this particular move).
    public function AiTrapBalance(cards : array<int>) : int
    {
        var i,total : int;var c : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        total=Score(2)-Score(1);
        for(i=0;i<cards.Size();i+=1){c=FindCard(cards[i]);if(!c)continue;s=c.Snapshot();
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&8)==0 && !s.isWaitingToDie)total+=s.power.currentPower;}
        return total;
    }
    public function AiApplyAmbushHypothesis(cards : array<int>, templates : array<int>, timers : array<int>, offset : int)
    {
        var i : int;var c : CBetaGwentDuelCard;
        if(!aiSimulating)return;
        for(i=0;i<cards.Size();i+=1){c=FindCard(cards[i]);if(c)c.AiAssumeAmbush(templates[offset+i],timers[offset+i]);}
        archetypeAI.Refresh();
    }
    // A face-down enemy unit can be Toruviel. Only public position and
    // visible neighbours count, never its concealed template, power or timer.
    public function AiPublicAmbushPassRisk() : int
    {
        var i,j,risk,neighbours : int;var s,t : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId!=1 || (s.locationMask&7)==0 || s.isWaitingToDie || (s.tokenMask&12)!=8)continue;
            neighbours=0;
            for(j=0;j<live.Size();j+=1){t=live[j].Snapshot();
                if(t.positionPlayerId==1 && t.locationMask==s.locationMask && !t.isWaitingToDie && (t.tokenMask&24)==0
                    && t.runtimeTemplate.typeMask==4 && Abs(t.locationIndex-s.locationIndex)<=2)neighbours+=1;}
            risk+=6+Min(4,neighbours)*2;
        }
        return risk;
    }
    // Maximum difficulty knows the starting list, never private draws/order.
    // Public original copies leave the unseen pool; revealed generated copies
    // can still prove a card is available. With an unknown list stay cautious.
    // A boost is lost with its unit: a spy on our side dies to Menno Coehoorn, and
    // a reset (Peter, Mardroeme, Toxin, ...) removes all accumulated boosts.
    // Only cards the opponent may still hold count (starting list at maximum).
    private function AiBoostExposure(t : SBetaGwentCardSnapshot, side : int, amount : int) : int
    {
        var boosted,risk,other,i,base,before,after : int;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        if(side!=2 || t.positionPlayerId!=2 || CountLocation(1,8)==0 || amount<=0)return 0;
        m=match.Snapshot();if(m.playerOne.hasPassed)return 0;
        if((t.tokenMask&128)!=0 && AiEnemyMayHold(162102))return amount-Max(1,amount/4);
        base=t.power.basePower+t.power.permanentPower;boosted=Max(0,t.power.currentPower-base);
        risk=0;
        if(AiEnemyResetThreat()){
            for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                if(s.instanceId==t.instanceId || s.positionPlayerId!=side || (s.locationMask&7)==0 || s.isWaitingToDie || (s.tokenMask&8)!=0)continue;
                other=Max(other,Max(0,s.power.currentPower-s.power.basePower-s.power.permanentPower));}
            before=Max(other,boosted);after=Max(other,Max(0,t.power.currentPower+amount-base));
            risk=Max(0,after-before)/2;
        }
        // Making (or keeping) a unit the strongest on the board feeds Scorch/Schirru;
        // Scorch destroys gold units too (Beta targetTiers 15).
        if(t.power.currentPower+amount>=AiBoardHighestExcept(t.instanceId)
            && (AiEnemyMayHold(113309) || AiEnemyMayHold(142108)))risk=Max(risk,amount/2);
        return risk;
    }
    private function AiBoardHighestExcept(id : int) : int
    {
        var i,highest : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            // Face-down ambushes are not Scorch targets (targetIgnore 8).
            if(s.instanceId==id || (s.locationMask&7)==0 || s.isWaitingToDie || s.runtimeTemplate.typeMask!=4 || (s.tokenMask&8)!=0)continue;
            highest=Max(highest,s.power.currentPower);}
        return highest;
    }
    private function AiEnemyResetThreat() : bool
    {
        return AiEnemyMayHold(162204) || AiEnemyMayHold(113320) || AiEnemyMayHold(200223) || AiEnemyMayHold(200233)
            || AiEnemyMayHold(122211) || AiEnemyMayHold(200132) || AiEnemyMayHold(201523) || AiEnemyMayHold(113404)
            || AiEnemyMayHold(201563) || AiEnemyMayHold(113205);
    }
    public function AiEnemyMayHold(templateId : int) : bool
    {
        var i,remaining,knownHand : int;var s : SBetaGwentCardSnapshot;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0){
                knownHand+=1;if(s.runtimeTemplate.templateId==templateId)return true;}
        }
        if(knownHand>=CountLocation(1,8))return false;
        if(BetaGwentAIStrength()<4 || aiStartingDeckOne.Size()==0)return true;
        for(i=0;i<aiStartingDeckOne.Size();i+=1)if(aiStartingDeckOne[i]==templateId)remaining+=1;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.ownerId==1 && (s.locationMask&39)!=0 && (s.tokenMask&8)==0 && !live[i].createdCopy
                && s.runtimeTemplate.templateId==templateId)remaining-=1;
        }
        return remaining>0;
    }
    // Public pass reactions can reverse a visible lead (False Ciri returns).
    // Ordinary positions keep the cheap score path. Search copies anonymize
    // opposing hidden cards before resolving the authoritative pass rules.
    public function AiPublicPassLead(optional resolveTurn : bool) : int
    {
        var i,lead : int;var s : SBetaGwentCardSnapshot;var g : CBetaGwentDuelSession;var reacts : bool;
        lead=Score(2)-Score(1);
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if((s.locationMask&7)!=0 && !s.isWaitingToDie && (s.tokenMask&12)==0
                && (s.timerValue>0 || s.positionPlayerId==2 && s.runtimeTemplate.templateId==162212 && (s.tokenMask&128)!=0))reacts=true;}
        if(!reacts && !resolveTurn)return lead-AiPublicAmbushPassRisk();
        BetaGwentAISimEnter();g=AiSimClone();
        if(g && g.Pass(2) && !g.IsFatal())lead=g.Score(2)-g.Score(1);else lead=Min(0,lead);
        BetaGwentAISimLeave();return lead-AiPublicAmbushPassRisk();
    }
    // An empty opposing hand is not the same as a pass: a leader may remain.
    // With no such action, resolve public end-of-turn effects on a private clone
    // before deciding that another hand card would only be wasted.
    private function AiWinsByPassingExhaustedOpponent() : bool
    {
        var i, beforeCrowns : int;var t : SBetaGwentCardSnapshot;var g : CBetaGwentDuelSession;var m : SBetaGwentMatchSnapshot;
        if(CountLocation(1,8)!=0 || LeaderAvailable(1) || Score(2)<=Score(1))return false;
        for(i=0;i<live.Size();i+=1){t=live[i].Snapshot();if(t.positionPlayerId==1 && (t.locationMask&7)!=0 && (t.tokenMask&8)!=0)return false;}
        m=match.Snapshot();beforeCrowns=m.playerTwo.crowns;g=AiSimClone();if(!g)return false;
        if(!g.Pass(2) || g.IsFatal())return false;m=g.Snapshot();
        if(m.roundActive && !m.playerOne.hasPassed){if(!g.Pass(1) || g.IsFatal())return false;m=g.Snapshot();}
        return m.playerTwo.crowns>beforeCrowns;
    }
    // Safe upper bound for ordinary hands. Any engine/compound ability makes
    // the bound unknown; it must never authorize conceding a possible combo.
    private function AiSimpleHandUpperBound() : int
    {
        var i,total,gain : int;var s : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();d=live[i].Definition();
            if(s.isWaitingToDie || (s.locationMask&95)==0)continue;
            if((s.locationMask&7)!=0){
                if((s.tokenMask&4)==0 && (d.timerPeriod>0 || d.passiveBoost!=0 || d.deathwishDamage!=0 || d.deathwishSummonTemplate>0
                    || d.deathwishSpawnCount>0 || d.consumePassiveBoost>0 || BetaGwentAIEngine(d.header.templateId)>0 || AiDeathwishSpy(d.header.templateId)))return -1;
                continue;
            }
            if(s.positionPlayerId!=2 || !s.canBePlayed || (s.locationMask!=8 && s.locationMask!=64))continue;
            if(BetaGwentDuelSpying(d.header.templateId) || d.deploySpawnCount>0 || d.deploySummonTemplate>0 || d.timerPeriod>0 || d.passiveBoost!=0
                || d.consumePassiveBoost>0 || d.deathwishDamage!=0 || d.deathwishSummonTemplate>0 || d.deathwishSpawnCount>0 || BetaGwentAIEngine(d.header.templateId)>0)return -1;
            gain=Max(0,s.power.currentPower);
            if(d.effect==1 || d.effect==2 || d.effect==27)gain+=Max(d.amount,d.conditionalDamage);
            else if(d.effect==3)gain+=d.amount*3+d.addedArmor*3;
            else if(d.effect!=0)return -1;
            total+=gain;
        }
        if(weather.Token(1,1)!=0 || weather.Token(1,2)!=0 || weather.Token(1,4)!=0
            || weather.Token(2,1)!=0 || weather.Token(2,2)!=0 || weather.Token(2,4)!=0)return -1;
        return total;
    }
    // Search the whole remaining hand, not only the next two plays. Exhausting
    // the node budget returns unknown and therefore keeps playing.
    private function AiWholeHandCatch(remaining : int, out nodes : int) : int
    {
        var g : CBetaGwentDuelSession;var s : SBetaGwentCardSnapshot;var m : SBetaGwentMatchSnapshot;
        var i,result : int;var uncertain : bool;
        if(Score(2)>=Score(1))return 1;
        if(nodes>=64)return -1;nodes+=1;
        m=match.Snapshot();if(m.currentPlayerId==1 && !AiSimSkipTurn())return -1;
        if(Score(2)>=Score(1))return 1;
        if(remaining<=0)return 0;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId!=2 || !s.canBePlayed || (s.locationMask!=8 && s.locationMask!=64))continue;
            g=AiSimClone();if(!g || g.AiSimPlay(s.instanceId)==-2147483647){uncertain=true;continue;}
            result=g.AiWholeHandCatch(remaining-1,nodes);if(result==1)return 1;if(result<0)uncertain=true;
        }
        if(uncertain)return -1;
        return 0;
    }
    private function AiRoundOneUnreachable() : bool
    {
        var m : SBetaGwentMatchSnapshot;var g : CBetaGwentDuelSession;var gap,upper,result,nodes,remaining : int;
        m=match.Snapshot();gap=Score(1)-Score(2);
        if(aiSimulating || m.roundNumber!=1 || gap<20)return false;
        upper=AiSimpleHandUpperBound();
        if(upper>=0){AiExplain("WHOLE_HAND","gap="+gap+" upperBound="+upper+" reason=all_hand_cards_and_available_leader");return upper<gap;}
        remaining=CountLocation(2,8);if(LeaderAvailable(2))remaining+=1;
        // Larger combo hands remain uncertain; never discard their potential
        // on a shallow or timed-out search.
        if(remaining>5)return false;
        BetaGwentAISimEnter();g=AiSimClone();result=-1;
        if(g)result=g.AiWholeHandCatch(remaining,nodes);
        BetaGwentAISimLeave();
        AiExplain("WHOLE_HAND","gap="+gap+" reachable="+result+" nodes="+nodes+" reason=complete_remaining_hand_unknown_keeps_playing");
        return result==0;
    }
    public function AiEndgamePreparation097() : bool
    {
        if(aiSimulating || aiEndgameReady097)return true;
        if(!aiPreparationEndgameJob097){aiPreparationEndgameJob097=new CBetaGwentAIEndgame097 in this;aiPreparationEndgameJob097.Initialize(this);return false;}
        if(!aiPreparationEndgameJob097.Step())return false;
        aiEndgameReady097=true;aiEndgameComplete097=aiPreparationEndgameJob097.complete && !aiPreparationEndgameJob097.invalidated;
        aiEndgameId097=aiPreparationEndgameJob097.firstId;aiEndgameValue097=aiPreparationEndgameJob097.result;
        aiEndgameNodes097=aiPreparationEndgameJob097.nodes;aiEndgameRevision097=aiPreparationEndgameJob097.before.revision;
        aiPreparationEndgameJob097=NULL;return true;
    }
    private function AiEnsureEndgame097()
    {
        var o : CBetaGwentStrategyObserve096;var v : SBetaGwentStrategyView096;
        if(aiSimulating)return;o=new CBetaGwentStrategyObserve096 in this;v=o.Capture(this,2,true);
        if(aiEndgameReady097 && aiEndgameRevision097==v.revision)return;
        aiEndgameReady097=false;aiPreparationEndgameJob097=NULL;while(!AiEndgamePreparation097()){}
    }
    public function AiReplyLimit097() : int
    {
        var limit,i,revealed : int;var s : SBetaGwentCardSnapshot;
        limit=Max(1,Min(BetaGwentAIStrength()-1,3-aiSimDamp/25));
        // A small completely revealed hand has actual legal replies, not
        // frequency hypotheses. Do not discard its last card by storage order.
        if(BetaGwentAIStrength()>=4){
            for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
                if(s.positionPlayerId==1 && s.locationMask==8 && (s.tokenMask&64)!=0)revealed+=1;}
            if(revealed>0 && revealed<=4 && revealed==CountLocation(1,8))limit=Max(limit,revealed);
        }
        return limit;
    }
    // The reduced budget still considers one public reply in a short round
    // that must be won. Large hands retain the cheaper fallback on slow devices.
    public function AiCriticalShortReply() : bool
    {
        var m : SBetaGwentMatchSnapshot;m=match.Snapshot();
        return !m.playerOne.hasPassed && AiDecisiveRound() && CountLocation(2,8)>=2
            && (CountLocation(2,8)<=3 || CountLocation(2,8)==4 && BetaGwentAIStrength()>=3 && aiSimDamp<50)
            && CountLocation(1,8)>0 && CountLocation(1,8)<=3;
    }
    public function AiShortRoundPlanning() : bool
    {
        var i : int;var s : SBetaGwentCardSnapshot;var hidden : bool;
        var hc,ht,hm,hw : array<int>;
        if(BetaGwentAIStrength()<3 || !AiCriticalShortReply() || LeaderAvailable(1) || LeaderAvailable(2))return false;
        for(i=0;i<live.Size();i+=1){s=live[i].Snapshot();
            if(s.positionPlayerId==1 && (s.locationMask&7)!=0 && (s.tokenMask&8)!=0)hidden=true;
            if(s.positionPlayerId==2 && s.locationMask==8 && AiDrawingSpy(live[i]))return false;
        }
        // 094b: a face-down enemy card no longer forbids complete-line
        // comparison when the reply tree can search it under public
        // hypotheses. Without one, the old conservative exit stays.
        if(hidden)return !aiSimulating && AiAmbushHypotheses(hc,ht,hm,hw)>0;
        return true;
    }
    public function AiDelayCost097(id : int, later : CBetaGwentDuelSession) : int
    {
        var c : CBetaGwentDuelCard;var d : SBetaGwentDuelDefinition;var nowValue,laterValue : int;
        if(!AiDecisiveRound())return 0;c=FindCard(id);if(!c)return 0;d=c.Definition();
        if(AiWeatherCardToken(d)==0 && !(d.header.typeMask==2 && (d.effect==2 || d.effect==3)))return 0;
        nowValue=AiCardTempo(c,false,BestVranAnchor(2),AiPublicClearRisk());c=later.FindCard(id);
        if(c)laterValue=later.AiCardTempo(c,false,later.BestVranAnchor(2),later.AiPublicClearRisk());
        return Min(6,Max(0,nowValue-laterValue));
    }
    public function AiStrategyOrder096(id : int) : int
    {
        var c : CBetaGwentDuelCard;var d : SBetaGwentDuelDefinition;
        c=FindCard(id);if(!c)return -2147483647;d=c.Definition();
        return AiCardTempo(c,false,BestVranAnchor(2),AiPublicClearRisk())*10-AiReserveCost(d)*4;
    }
    public function AiStrategyPreparationStep096() : bool
    {
        var observer : CBetaGwentStrategyObserve096;var v : SBetaGwentStrategyView096;var i : int;
        if(aiSimulating)return true;
        if(aiStrategyReady096)return true;
        if(!aiStrategyJob096){aiStrategyJob096=new CBetaGwentStrategyResourceJob096 in this;aiStrategyJob096.Initialize(this);return false;}
        if(!aiStrategyJob096.Step())return false;
        if(!aiStrategyJob096.invalidated){
            aiStrategyIds096.Clear();aiStrategyPenalties096.Clear();
            for(i=0;i<aiStrategyJob096.penalties.Size();i+=1){
                aiStrategyIds096.PushBack(aiStrategyJob096.ids[i]);aiStrategyPenalties096.PushBack(aiStrategyJob096.penalties[i]);}
            aiStrategyRevision096=aiStrategyJob096.before.revision;aiStrategyReady096=true;
        }
        aiStrategyJob096=NULL;return true;
    }
    private function AiEnsureStrategy096()
    {
        var observer : CBetaGwentStrategyObserve096;var v : SBetaGwentStrategyView096;var ticks : int;
        if(aiSimulating)return;
        observer=new CBetaGwentStrategyObserve096 in this;v=observer.Capture(this,2,true);
        if(aiStrategyReady096 && aiStrategyRevision096==v.revision)return;
        aiStrategyReady096=false;aiStrategyJob096=NULL;aiStrategyIds096.Clear();aiStrategyPenalties096.Clear();
        while(!AiStrategyPreparationStep096()){
            ticks+=1;if(ticks>=160){aiStrategyJob096=NULL;aiStrategyReady096=false;return;}
        }
    }
    public function AiStrategyPenalty096(id : int) : int
    {
        var i : int;var m : SBetaGwentMatchSnapshot;m=match.Snapshot();
        if(aiSimulating || !aiStrategyReady096 || m.roundNumber>=3 || m.playerOne.crowns>0)return 0;
        for(i=0;i<aiStrategyIds096.Size();i+=1)if(aiStrategyIds096[i]==id)return aiStrategyPenalties096[i];
        return 0;
    }
    public function OpponentStep() : bool
    {
        var i, best, value, maximum, row, effectValue, vranAnchor, reserve, bestReserve, deficit, catchBest, catchCost, cost, bestGain, bestUtility, tempo, clearRisk : int;
        var s, vranTarget : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var d : SBetaGwentDuelDefinition;
        var leaderCard : CBetaGwentDuelCard;var publicResponses : CBetaGwentPublicResponseAI;
        var actions : array<SBetaGwentAIChaseAction>;var action : SBetaGwentAIChaseAction;
        var plan : SBetaGwentAIChasePlan;var planner : CBetaGwentAIChasePlanner;
        var ownHand, enemyHand, spent, reason, burst, leaderBurst, highest, burn, total, biggest, lane, resourceRound, passTempo, leaderBanked : int;
        var earlyState : SBetaGwentCardSnapshot; var bestTempoAll, bestValueAll, bestHandNet, roundDecision, exact, j, leaderExact, leaderSequence, leaderEvaluation : int; var handNetSeen : bool;
        var simIds, simOrder, sequenceIds, exactIds, exactValues, exactStrategic, upliftIds, upliftValues : array<int>;
        var leaderPlay,drawSpy,spyUnsafe,bestSpyRecovery,shortPlanning : bool;var spyDraw,spyRisk,spyTempo,spyActivation,pressureDiscount,passLead : int;var possibleScorch,possibleIgni,possibleSchirru : bool;
        if (IsExternalPolicy(2) || !CanAct(2)) return false; m = match.Snapshot();archetypeAI.Refresh();AiEnsureStrategy096();
        aiDecisionSerial+=1;AiExplain("BEGIN", "round="+m.roundNumber+" profile="+archetypeAI.ProfileId()+" preset="+presetTwo+" ownScore="+Score(2)+" enemyScore="+Score(1)+" ownHand="+CountLocation(2,8)+" enemyHand="+CountLocation(1,8)+" ownCrowns="+m.playerTwo.crowns+" enemyCrowns="+m.playerOne.crowns+" enemyPassed="+m.playerOne.hasPassed+" leader="+LeaderAvailable(2)+" seed="+random.InitialSeed()+" draws="+random.DrawCount());
        AiLogPosition();
        resourceRound=m.roundNumber;if(m.playerOne.crowns>=1)resourceRound=3;
        if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed){
            publicResponses=new CBetaGwentPublicResponseAI in this;
            publicResponses.Initialize(this,AiReplyLimit097());
        }
        archetypeAI.PlanTurn(publicResponses);
        if(archetypeAI.DryPass()){BetaGwentLog("DUEL_AI_PASS reason=save_long_deciding_round profile="+archetypeAI.ProfileId());return AiExplainedPass("save_long_deciding_round");}
        if (m.playerOne.hasPassed && AiPublicPassLead() > 0) return AiExplainedPass("already_ahead_after_pass");
        AiEnsureEndgame097();
        if(aiEndgameComplete097 && aiEndgameValue097>=0){
            AiExplain("PUBLIC_ENDGAME_TREE","first="+aiEndgameId097+" result="+aiEndgameValue097+" nodes="+aiEndgameNodes097+" reason=complete_supported_public_subgame");
            if(aiEndgameId097==0)return AiExplainedPass("complete_public_endgame");
            d=registry.Find(aiEndgameId097).Definition();row=BestCardRow(2,d);if(row==0)row=1;
            AiExplain("SELECT","action=card card="+aiEndgameId097+" template="+d.header.templateId+" reason=complete_public_endgame");
            return Play(2,aiEndgameId097,row);
        }
        ownHand=CountLocation(2,8);enemyHand=CountLocation(1,8);
        if(BetaGwentAIStrength()>=2 && AiRoundOneUnreachable())return AiExplainedPass("first_round_whole_hand_cannot_catch");
        if(enemyHand==0 && AiWinsByPassingExhaustedOpponent())return AiExplainedPass("opponent_exhausted_round_already_won");
        if(m.playerOne.hasPassed && AiPublicPassLead()==0 && m.playerTwo.crowns>=1 && m.playerOne.crowns==0)
        { BetaGwentLog("DUEL_AI_PASS reason=accept_tie");return AiExplainedPass("accept_tie"); }
        if(m.playerOne.hasPassed && aiChaseRound!=m.roundNumber){aiChaseRound=m.roundNumber;aiChaseInitialHand=ownHand;aiChaseSpent=0;}
        spent=aiChaseSpent;
        maximum = -2147483647; catchCost = 2147483647; deficit = Max(1, -AiPublicPassLead() + 1);
        vranAnchor = BestVranAnchor(2); clearRisk = AiPublicClearRisk();
        // Learn a conservative tempo envelope from visible score changes.
        // Keep the estimate across rounds; no hidden hand/deck templates.
        if(aiObservedRound==m.roundNumber)aiPublicTempo=Max(aiPublicTempo,Min(40,Max(0,Score(1)-aiObservedEnemyScore)));
        aiObservedRound=m.roundNumber;aiObservedEnemyScore=Score(1);
        burst=Max(14,aiPublicTempo);if(publicResponses)burst=Max(burst,publicResponses.publicBurst);highest=0;burn=0;
        possibleSchirru=AiEnemyMayHold(142108);possibleScorch=AiEnemyMayHold(113309) || possibleSchirru;possibleIgni=AiEnemyMayHold(112102);
        for(lane=1;lane<=4;lane*=2)
        {
            total=0;biggest=0;
            for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
                if(earlyState.positionPlayerId!=2 || earlyState.locationMask!=lane || (earlyState.tokenMask&8)!=0)continue;
                total+=earlyState.power.currentPower;biggest=Max(biggest,earlyState.power.currentPower);
                highest=Max(highest,earlyState.power.currentPower);}
            if(possibleIgni && total>=25){value=0;for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
                if(earlyState.positionPlayerId==2 && earlyState.locationMask==lane && earlyState.power.currentPower==biggest && (earlyState.tokenMask&8)==0)value+=biggest;}
                burst=Max(burst,value+5);}
            burst=Max(burst,CountLocation(2,lane)*3);
        }
        for(i=0;i<live.Size();i+=1){earlyState=live[i].Snapshot();
            if(earlyState.positionPlayerId==2 && (earlyState.locationMask&7)!=0 && earlyState.power.currentPower==highest && (earlyState.tokenMask&8)==0)burn+=highest;}
        if(possibleScorch)burst=Max(burst,burn);if(possibleSchirru)burst=Max(burst,burn+4);leaderBurst=0;if(LeaderAvailable(1))leaderBurst=20;passLead=AiPublicPassLead();
        if(!m.playerOne.hasPassed && BetaGwentAIEarlyPass(AiPublicPassLead(),burst,leaderBurst,ownHand,enemyHand,m.playerOne.crowns))
        { BetaGwentLog("DUEL_AI_PASS reason=force_multiple_replies burst="+burst+" leaderBurst="+leaderBurst+" ownHand="+ownHand+" enemyHand="+enemyHand);return AiExplainedPass("force_multiple_replies"); }
        // Public planning does not authorize extra simulations at a reduced
        // preparation budget. Preserve the existing reply-search limit.
        if(aiSimDamp>=50 && !AiPlainLastReply() && !AiCriticalShortReply())publicResponses=NULL;
        if(publicResponses && publicResponses.templates.Size()>0)shortPlanning=AiShortRoundPlanning();
        // Generation 3: simulate the most promising plays on a cloned session and use the
        // exact immediate result instead of the heuristic estimate (own cards only).
        if(BetaGwentAIStrength()>=2)
        {
            for(i=0;i<live.Size();i+=1)
            {
                s=live[i].Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || !s.canBePlayed)continue;
                d=live[i].Definition();if(AiDrawingSpy(live[i]) || AiUselessDecoy(live[i]) || AiDeferEmptyDuel(d,2) || d.header.typeMask==4 && BestCardRow(2,d)==0)continue;
                value=AiCardTempo(live[i],false,vranAnchor,clearRisk)*10-AiReserveCost(d)*4+archetypeAI.Priority(d)*10;
                j=0;while(j<simOrder.Size() && simOrder[j]>=value)j+=1;
                simOrder.Insert(j,value);simIds.Insert(j,i);
            }
            AiDiversifySearch(simIds,AiSimCap(5));
            for(j=0;j<simIds.Size() && j<AiSimCap(5);j+=1)
            {
                exact=AiExactTempo(live[simIds[j]]);s=live[simIds[j]].Snapshot();
                exactIds.PushBack(s.instanceId);exactValues.PushBack(exact);exactStrategic.PushBack(aiLastStrategicValue);
            }
            sequenceIds=simIds;AiDiversifySearch(sequenceIds,AiSimCap(9));
            if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed && CountLocation(2,8)>=2)
                for(j=0;j<sequenceIds.Size() && j<AiSimCap(9);j+=1)
                {
                    s=live[sequenceIds[j]].Snapshot();upliftIds.PushBack(s.instanceId);
                    upliftValues.PushBack(AiSequenceUplift(live[sequenceIds[j]],exactIds,exactValues,publicResponses));
                }
        }
        for (i = 0; i < live.Size(); i += 1)
        {
            s = live[i].Snapshot(); if (s.positionPlayerId != 2 || s.locationMask != 8 || !s.canBePlayed) continue;
            d=live[i].Definition();
            spyActivation=-2147483647;
            if(!aiSimulating && AiDeathwishSpy(d.header.templateId)){
                spyActivation=AiSpyActivationValue(live[i]);
                if(spyActivation==-2147483647 || spyActivation<=0){AiExplain("REJECT","card="+s.instanceId+" template="+d.header.templateId+" reason=no_profitable_deathwish_activation");continue;}
            }
            // A last card is still played when the pass itself would concede the match.
            if(d.effect==29 && d.header.typeMask==2 && AiPilePlayValue(d,2,false,0)<=0
                && !(ownHand==1 && m.playerOne.crowns>0 && AiPublicPassLead(true)<=0)){AiExplain("REJECT","card="+s.instanceId+" template="+d.header.templateId+" reason=no_useful_legal_pile_target");continue;}
            drawSpy=!aiSimulating && AiDrawingSpy(live[i]);
            // False Ciri returns to her owner when the side she spies for passes:
            // useless once that player has passed, a delayed body before that.
            if(d.header.templateId==162212 && m.playerOne.hasPassed){AiExplain("REJECT","card="+s.instanceId+" template=162212 reason=false_ciri_cannot_return_after_pass");continue;}
            if(!drawSpy && d.header.templateId!=162212 && AiSpyUnrecoverable(live[i])){AiExplain("REJECT","card="+s.instanceId+" template="+d.header.templateId+" reason=late_spy_cannot_recover_lead_with_followups");continue;}
            if(AiUselessDecoy(live[i])){AiExplain("REJECT","card="+s.instanceId+" template=113201 reason=no_profitable_decoy_target");continue;}
            if(AiDeferEmptyDuel(d,2)){AiExplain("REJECT", "card="+s.instanceId+" template="+d.header.templateId+" reason=no_duel_target_and_other_card_available");continue;}
            if(d.header.typeMask==4 && BestCardRow(2,d)==0){AiExplain("REJECT", "card="+s.instanceId+" template="+d.header.templateId+" reason=no_legal_row");continue;}
            value=AiCardTempo(live[i],false,vranAnchor,clearRisk);
            tempo=AiCardTempo(live[i],true,vranAnchor,clearRisk);
            if(drawSpy){
                spyDraw=AiSpyDrawForecast(live[i],spyUnsafe,spyRisk,spyTempo);
                if(spyUnsafe){AiExplain("REJECT","card="+s.instanceId+" template="+d.header.templateId+" reason=draw_spy_cannot_recover_after_pass");continue;}
                value+=spyTempo-tempo+spyDraw-spyRisk+AiSpyCardEdge(-spyTempo);tempo=spyTempo;
                if(spyDraw>0 && AiSpyConcessionWindow()){
                    // Gifted board points disappear with the conceded round;
                    // they are still real tempo and never authorize a catch.
                    value=Max(value,spyDraw+AiSpyCardEdge(-spyTempo));
                    AiExplain("SPY_CONCESSION_OPTION","card="+s.instanceId+" draw="+spyDraw+" ownHand="+ownHand+" enemyHand="+enemyHand+" reason=convert_spy_and_concede_without_spending_the_hand_balance");
                }
                if(archetypeAI)value+=archetypeAI.MirunaSpyReturn(d);
            }else{
                for(j=0;j<exactIds.Size();j+=1)if(exactIds[j]==s.instanceId && exactValues[j]!=-2147483647){value+=exactValues[j]-tempo;if(!m.playerOne.hasPassed)value+=exactStrategic[j];tempo=exactValues[j];}
                for(j=0;j<upliftIds.Size();j+=1)if(upliftIds[j]==s.instanceId)value+=upliftValues[j]*BetaGwentAITune(8)/10;
            }
            if(d.header.templateId==162212){value=Max(value,AiFalseCiriReturn(s));tempo=Max(tempo,AiFalseCiriReturn(s));}
            if(AiWeatherCardToken(d)>0 && value<=0){AiExplain("REJECT","card="+s.instanceId+" template="+d.header.templateId+" reason=weather_has_no_marginal_value");continue;}
            reserve = AiReserveCost(d)+AiTimingReserve(live[i],value);
            cost=AiStrategyPenalty096(s.instanceId);reserve+=cost;
            if(cost>0)AiExplain("STRATEGY_RESOURCE","card="+s.instanceId+" penalty="+cost+" reason=remaining_combo_after_actual_play_and_public_reply");
            if(spyActivation!=-2147483647){
                // The following card's body belongs to that card, not this spy.
                // Credit only the deathwish payoff beyond its deploy penalty.
                vranTarget=s;vranTarget.positionPlayerId=1;vranTarget.locationMask=BestCardRow(2,d);
                value=Max(value,-s.power.currentPower+AiSpyDeathwishValue(vranTarget,2));
            }
            if(weatherProfile && (d.header.templateId==112102 || d.header.templateId==200218 || d.header.templateId==132104) && value<=s.power.currentPower+3 && m.roundNumber<3)reserve+=6;
            action.id=s.instanceId;action.gain=tempo;action.cards=1;action.reserve=reserve;actions.PushBack(action);
            bestTempoAll=Max(bestTempoAll,tempo);bestValueAll=Max(bestValueAll,value);
            if(!handNetSeen || Max(tempo,value)>bestHandNet){bestHandNet=Max(tempo,value);handNetSeen=true;}
            if (m.playerOne.hasPassed && tempo >= deficit)
            {
                cost = reserve * 10 + Max(0, tempo - deficit);
                if (cost < catchCost) { catchCost = cost; catchBest = s.instanceId; }
            }
            effectValue = (value+AiDrawUtility(d,2,live[i])) * 10 + AiSetupBonus(d) * 10 - reserve * 4;
            // A short mandatory line already resolves the remaining card's
            // ability. Do not charge an empty tutor a second profile penalty
            // when its body is the disposable opening that preserves the answer.
            if(!shortPlanning || !upliftIds.Contains(s.instanceId))effectValue+=archetypeAI.Priority(d)*10;
            effectValue+=archetypeAI.TacticalPriority(d,value)*10;
            effectValue+=AiDecayUrgency(d,value,ownHand)*10;
            pressureDiscount=0;
            if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed && m.playerOne.crowns==0 && m.roundNumber<3
                && ownHand>=3 && enemyHand>=2 && !drawSpy && archetypeAI.publicThreat<5
                && BetaGwentAIEngine(d.header.templateId)<=0 && d.timerPeriod==0 && d.passiveBoost==0){
                pressureDiscount=BetaGwentAIPressureDiscount(passLead,tempo,burst,leaderBurst);
                effectValue-=pressureDiscount*10;
                if(pressureDiscount>0)AiExplain("PRESSURE_VALUE","card="+s.instanceId+" tempo="+tempo+" excess="+pressureDiscount+" reason=same_number_of_public_replies");
            }
            // Three unordered own-deck forecasts must all recover the gift.
            // Prefer opening that extra action before the remaining finisher;
            // this bonus never inflates actual tempo or authorizes a catch.
            if(drawSpy && AiLateOrderWindow() && ownHand==2 && spyDraw>0 && spyRisk==0 && CountLocation(2,16)>0){
                effectValue+=Min(18,spyDraw+3)*10;
                AiExplain("DRAW_ORDER","card="+s.instanceId+" forecast="+spyDraw+" risk=0 reason=safe_draw_before_last_followup");
            }
            effectValue+=BetaGwentAITrainingBias(presetTwo,d,m.roundNumber,ownHand,Score(2)-Score(1),m.playerOne.hasPassed,tempo,value,reserve,archetypeAI.Priority(d));
            if(weatherProfile)effectValue+=weatherAI.Setup(d)*10;
            if(shortPlanning && upliftIds.Contains(s.instanceId)){
                // This frontier compares complete immediate reply/follow-up
                // lines. Setup priorities, reserve multipliers and training
                // biases must not charge the same opportunity cost again.
                effectValue=0;
                for(j=0;j<upliftIds.Size();j+=1)if(upliftIds[j]==s.instanceId)effectValue+=upliftValues[j]*BetaGwentAITune(8);
                AiExplain("SHORT_LINE","card="+s.instanceId+" evaluation="+effectValue+" reason=resolved_frontier_from_common_source");
            }
            AiExplain("OPTION", "card="+s.instanceId+" template="+d.header.templateId+" tempo="+tempo+" utility="+value+" reserve="+reserve+" draw="+AiDrawUtility(d,2,live[i])+" setup="+AiSetupBonus(d)+" priority="+archetypeAI.Priority(d)+" evaluation="+effectValue+" exact="+exactIds.Contains(s.instanceId)+" sequence="+upliftIds.Contains(s.instanceId));
            // Equal evaluations preserve the card with greater value in reserve.
            if (effectValue > maximum || (effectValue == maximum && reserve < bestReserve)) { maximum = effectValue; bestReserve=reserve; bestGain = tempo; bestUtility=value+AiDrawUtility(d,2,live[i]); best = s.instanceId;bestSpyRecovery=drawSpy && ownHand<=2 && spyRisk==0 && spyDraw>0; }
        }
        if (catchBest != 0)
        {
            best = catchBest;
            BetaGwentLog("DUEL_AI_CATCHUP card=" + best + " deficit=" + deficit + " cost=" + catchCost + " publicClearRisk=" + clearRisk);
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
                leaderBanked=aiLastStrategicValue;
                if(leaderExact!=-2147483647){value+=leaderExact-(AiCardTempo(leaderCard,true,vranAnchor,clearRisk)+archetypeAI.LeaderGain(d));if(!m.playerOne.hasPassed)value+=aiLastStrategicValue;}
            }
            if(publicResponses && leaderExact!=-2147483647){
                if(AiLeaderSequencePlanning()){
                    leaderSequence=AiSequenceUplift(leaderCard,exactIds,exactValues,publicResponses);
                    value+=leaderSequence*BetaGwentAITune(8)/10;
                    AiExplain("LEADER_SEQUENCE","template="+d.header.templateId+" uplift="+leaderSequence+" reason=leader_reply_and_actual_hand_continuation");
                }else value-=AiCounterRisk(leaderCard,publicResponses);
            }
            tempo=AiCardTempo(leaderCard,true,vranAnchor,clearRisk)+archetypeAI.LeaderGain(d);
            if(leaderExact!=-2147483647)tempo=leaderExact;
            if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed && m.playerOne.crowns==0 && m.roundNumber<3
                && ownHand>=3 && enemyHand>=2 && archetypeAI.publicThreat<5
                && BetaGwentAIEngine(d.header.templateId)<=0 && d.timerPeriod==0 && d.passiveBoost==0){
                pressureDiscount=BetaGwentAIPressureDiscount(passLead,tempo,burst,leaderBurst);
                value-=pressureDiscount;
                if(pressureDiscount>0)AiExplain("PRESSURE_VALUE","action=leader template="+d.header.templateId+" tempo="+tempo+" excess="+pressureDiscount+" reason=same_number_of_public_replies");
            }
            cost = BetaGwentAILeaderReserve(resourceRound);
            if(!m.playerOne.hasPassed)cost+=BetaGwentAIResourcePressure(m.roundNumber,m.playerTwo.crowns,m.playerOne.crowns,ownHand,enemyHand,cost);
            // Preserve a once-per-match leader unless its actual ability has
            // useful targets, it sets up the deck, or no hand play is left.
            cost+=AiStrategyPenalty096(s.instanceId);
            // Foltest banks hand/deck boosts for later rounds immediately.
            // Do not reserve that already retained value as if it vanished
            // with this round's board; delaying risks losing unboosted units.
            if(d.header.templateId==200168 && leaderExact!=-2147483647)cost=Max(0,cost-Max(0,leaderBanked));
            reserve=cost+AiTimingReserve(leaderCard,value);
            if(resourceRound<3 && value<=s.power.currentPower+2 && archetypeAI.LeaderPriority(d)<=0 && ownHand>0)reserve+=BetaGwentAITune(28);
            leaderEvaluation=value*10-reserve*10+archetypeAI.LeaderPriority(d)*10+AiDecayUrgency(d,value,ownHand)*10+BetaGwentAITrainingBias(presetTwo,d,m.roundNumber,ownHand,Score(2)-Score(1),m.playerOne.hasPassed,value,value,reserve,archetypeAI.LeaderPriority(d));
            if(catchBest==0 && !m.playerOne.hasPassed && BetaGwentAILeaderUseful(d.header.templateId,resourceRound,ownHand,s.power.currentPower,value,archetypeAI.LeaderPriority(d),false,deficit)
                && (leaderEvaluation>maximum || leaderEvaluation==maximum && leaderSequence>0 && archetypeAI.LeaderPriority(d)>0))leaderPlay=true;
            bestTempoAll=Max(bestTempoAll,tempo);
            AiExplain("LEADER_OPTION", "template="+d.header.templateId+" body="+s.power.currentPower+" tempo="+tempo+" utility="+value+" reserve="+reserve+" priority="+archetypeAI.LeaderPriority(d)+" chosenBeforeChase="+leaderPlay+" useful="+BetaGwentAILeaderUseful(d.header.templateId,resourceRound,ownHand,s.power.currentPower,value,archetypeAI.LeaderPriority(d),false,deficit)+" reason=ability_value_resource_reserve_and_hand_alternatives");
            BetaGwentLog("DUEL_AI_LEADER_EVAL template="+d.header.templateId+" body="+s.power.currentPower+" actual="+tempo+" future="+leaderBanked+" deficit="+deficit+" passed="+m.playerOne.hasPassed);
            if(m.playerOne.hasPassed || BetaGwentAILeaderUseful(d.header.templateId,resourceRound,ownHand,s.power.currentPower,tempo,0,false,deficit)){
                action.id=-1;action.gain=tempo;action.cards=0;action.reserve=cost;
                // Generation 2+: the leader is a strong once-per-match card, not a free answer.
                // Before the deciding round preserve the resource, without
                // pretending its deployment removed a card from the hand.
                if(BetaGwentAIStrength()>=2 && resourceRound<3)action.reserve=cost+BetaGwentAITune(29);
                actions.PushBack(action);
            }
        }
        if(BetaGwentAIStrength()>=2 && !m.playerOne.hasPassed){
            if(BetaGwentAIStrength()>=4 && m.roundNumber==1 && m.playerOne.crowns==0 && passLead<= -14 && ownHand>=4 && !bestSpyRecovery){
                planner=new CBetaGwentAIChasePlanner in this;plan=planner.Plan(actions,1-passLead);
                AiExplain("ROUND_BUDGET","lead="+passLead+" reachable="+plan.reachable+" cards="+plan.cards+" reserve="+plan.reserve+" ownAfter="+(ownHand-plan.cards)+" enemyHand="+enemyHand+" bestFuture="+bestValueAll+" reason=optimistic_current_hand_commitment");
                if(BetaGwentAIInvestmentPass(m.roundNumber,m.playerTwo.crowns,m.playerOne.crowns,passLead,ownHand,enemyHand,
                    plan.reachable,plan.cards,bestTempoAll,bestValueAll))return AiExplainedPass("optional_round_costs_card_advantage");
            }
            if(archetypeAI.EndPressure(bestTempoAll,bestValueAll) && !bestSpyRecovery)
                return AiExplainedPass("tactical_plan_preserve_remaining_hand");
            // A negative play may lose fewer points than a pass because both
            // advance public timers. If passing still keeps the lead in an
            // optional round, preserve the hand rather than buy extra margin.
            if(m.roundNumber<3 && m.playerOne.crowns==0 && handNetSeen && bestHandNet<=0
                && bestTempoAll<=0 && !leaderPlay && !bestSpyRecovery && AiPublicPassLead(true)>0)
                return AiExplainedPass("no_positive_play_pass_keeps_lead");
            // Every hand card is worth more later (held finishers, empty tutors, a
            // targetless Slyzard): when an optional round is being lost, concede it
            // instead of dumping a card that the deciding rounds need.
            if(m.roundNumber<3 && m.playerOne.crowns==0 && handNetSeen && maximum<0 && !leaderPlay && !bestSpyRecovery
                && AiPublicPassLead(true)<0 && ownHand>=enemyHand){
                BetaGwentLog("DUEL_AI_PASS reason=every_card_held_for_later best="+maximum+" ownHand="+ownHand+" enemyHand="+enemyHand);
                return AiExplainedPass("every_card_held_for_later");
            }
            // Round one, clearly behind, no single play retakes the lead and the hand holds
            // reserved finishers: concede the round with the card count intact.
            if(m.roundNumber==1 && m.playerOne.crowns==0 && m.playerTwo.crowns==0 && !leaderPlay && !bestSpyRecovery
                && AiPublicPassLead(true)<-15 && Max(bestTempoAll,bestValueAll)<deficit && ownHand>=enemyHand && AiHeldFinishers()>0){
                BetaGwentLog("DUEL_AI_PASS reason=concede_round_keep_finishers deficit="+deficit+" best="+bestTempoAll+" held="+AiHeldFinishers()+" ownHand="+ownHand+" enemyHand="+enemyHand);
                return AiExplainedPass("concede_round_keep_finishers");
            }
            roundDecision=BetaGwentAIRoundDecision(m.roundNumber,m.playerTwo.crowns,m.playerOne.crowns,AiPublicPassLead(),ownHand,enemyHand,
                bestTempoAll,burst,LeaderAvailable(1),archetypeAI.LongRound(),archetypeAI.LiveEngines(),bestValueAll);
            if(roundDecision!=0 && !bestSpyRecovery){BetaGwentLog("DUEL_AI_PASS reason=researched_economy"+roundDecision+" profile="+archetypeAI.ProfileId()+" actualBest="+bestTempoAll);return AiExplainedPass("researched_round_economy");}
            if(leaderPlay){AiExplain("SELECT", "action=leader reason=useful_ability_and_best_evaluation template="+leaderTemplateTwo);BetaGwentLog("DUEL_AI_LEADER reason=researched_useful profile="+archetypeAI.ProfileId());return UseLeader(2);}
        }
        if(m.playerOne.hasPassed)
        {
            if(AiPreparationIsReady()){
                if(!aiPreparedChaseReady){
                    aiPreparationChaseJob=new CBetaGwentAIChase188 in this;
                    aiPreparationChaseJob.Initialize(this,actions,deficit,AiSimCap(5));
                    aiPreparationReady=false;aiPreparationStage=7;return false;
                }
                plan=aiPreparedChase;
            }else plan=AiChaseActual(actions,deficit);
            // A leader plus a hand card is a two-action investment in an
            // optional round. A lone free leader still costs no hand card.
            cost=plan.cards;if(m.playerOne.crowns==0 && plan.actions>1)cost=Max(cost,plan.actions);
            reason=BetaGwentAIChasePassReason(plan.reachable,cost,spent,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns);
            BetaGwentLog("DUEL_AI_CHASE round="+m.roundNumber+" deficit="+deficit+" reachable="+plan.reachable+" needed="+plan.cards+" actions="+plan.actions+" spent="+spent+" ownHand="+ownHand+" enemyHand="+enemyHand+" passReason="+reason);
            if(reason!=0){AiExplain("CHASE", "reachable="+plan.reachable+" cards="+plan.cards+" gain="+plan.gain+" deficit="+deficit+" spent="+spent+" reasonCode="+reason);return AiExplainedPass("chase_resource_budget");}
            // A hand-card substitute must satisfy the same resource budget.
            // The accepted leader plan costs zero hand cards; it cannot grant
            // permission to spend an extra card that budget would reject.
            if(plan.firstId==-1 && catchBest!=0 && m.roundNumber<3){
                reason=BetaGwentAIChasePassReason(true,1,spent,ownHand,enemyHand,m.playerTwo.crowns,m.playerOne.crowns);
                if(reason==0)plan.firstId=catchBest;
                else AiExplain("CHASE_RESOURCE","action=keep_leader_plan replacementCards=1 reasonCode="+reason+" reason=hand_substitute_exceeds_accepted_budget");
            }
            if(plan.firstId==-1){AiExplain("SELECT", "action=leader reason=reachable_chase gain="+plan.gain+" deficit="+deficit+" cards="+plan.cards);return UseLeader(2);}
            if(plan.firstId!=0)best=plan.firstId;catchBest=best;
            for(i=0;i<actions.Size();i+=1)if(actions[i].id==best)bestGain=actions[i].gain;
        }
        // Preserve the final hand card in an optional round when even its
        // resolved play cannot tie. This includes medics with empty/poor graves.
        // A decisive round is never conceded by this rule; a usable leader may
        // still turn the card into a winning continuation.
        if(!m.playerOne.hasPassed && m.playerOne.crowns==0 && ownHand==1 && !LeaderAvailable(2) && best!=0 && Score(1)>Score(2) && !bestSpyRecovery){
            exact=AiExactTempo(registry.Find(best));
            if(exact!=-2147483647 && exact+AiOwnTimerGain(ownHand)<Score(1)-Score(2)){
                BetaGwentLog("DUEL_AI_PASS reason=save_last_unreachable_card actual="+exact+" gap="+(Score(1)-Score(2))+" card="+best);
                return AiExplainedPass("save_last_unreachable_card");
            }
        }
        // Stage 131: when every hand play loses points now and later (Scorch that hits our own
        // unit, an emptied tutor, a draw spy whose expected card is weaker than the spy), a pass
        // keeps more points. The card stays in hand. A chase or leader plan was decided above.
        if(best!=0 && best!=catchBest && handNetSeen && bestHandNet<0 && !bestSpyRecovery){
            exact=AiExactTempo(registry.Find(best));
            // A timer (e.g. Miruna) may take points after either action. Compare
            // against a resolved pass, not a frozen board before the turn ends.
            passTempo=AiPublicPassLead(true)-(Score(2)-Score(1));
            // Never when the pass itself concedes the match: losing points
            // still keeps a draw or a later answer alive, a pass does not.
            if(m.playerOne.crowns>0 && AiPublicPassLead(true)<=0)
                BetaGwentLog("DUEL_AI_KEEP reason=pass_concedes_match best="+best+" net="+bestHandNet+" lead="+AiPublicPassLead(true));
            // A pass also forfeits our own pending timers that would fire on later turns.
            else if(exact==-2147483647 || exact+AiOwnTimerGain(ownHand)<passTempo && bestHandNet+AiOwnTimerGain(ownHand)<passTempo){
                BetaGwentLog("DUEL_AI_PASS reason=every_play_loses_points best="+best+" net="+bestHandNet+" exact="+exact+" passTempo="+passTempo);
                return AiExplainedPass("every_play_loses_points");
            }
        }
        // A low ordering score is a reason to save a gold, not to pass away a
        // mandatory round. If every remaining card is reactive, still play
        // the least wasteful legal body rather than concede by score cutoff.
        if (best != 0)
        {
            d = registry.Find(best).Definition();
            AiExplain("SELECT", "action=card card="+best+" template="+d.header.templateId+" gain="+bestGain+" reason=best_evaluation_or_reachable_chase evaluationWinner="+maximum+" chase="+m.playerOne.hasPassed);
            BetaGwentLog("DUEL_AI_TACTIC card=" + best + " gain=" + bestGain + " evaluation=" + maximum
                + " horizon=" + AiHorizon(2) + " publicClearRisk=" + clearRisk + " weather="+weatherProfile+" profile="+archetypeAI.ProfileId()+" order="+archetypeAI.Priority(d)+" planner=tempo94");
            if (d.effect == 23 && vranAnchor != 0){s=registry.Find(vranAnchor).Snapshot();AiExplainPlacement(registry.Find(best),s.locationMask,vranAnchor);return PlayBefore(2, best, vranAnchor);}
            vranAnchor=AiPlacementAnchor(d);if(vranAnchor!=0){s=registry.Find(vranAnchor).Snapshot();AiExplainPlacement(registry.Find(best),s.locationMask,vranAnchor);return PlayBefore(2,best,vranAnchor);}
            row = BestCardRow(2, d);
            if (row == 0) row = 1; AiExplainPlacement(registry.Find(best),row,0);return Play(2, best, row);
        }
        // Only use the emergency leader when there is no legal hand play.
        if (!m.playerOne.hasPassed && best==0 && ownHand==0 && LeaderAvailable(2) && BestOwnRow(2) != 0) {AiExplain("SELECT", "action=leader reason=no_hand_card template="+leaderTemplateTwo);BetaGwentLog("DUEL_AI_LEADER reason=empty_hand95");return UseLeader(2);}
        BetaGwentLog("DUEL_AI_PASS reason=no_legal_hand_or_useful_chase hand="+ownHand);
        return AiExplainedPass("no_legal_hand_or_useful_chase");
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
            // A visible action is shown before another AI search. An exhausted
            // human hand still passes above, so yielding cannot strand the turn.
            if(recordVisuals && visualFrames.Size()>0)return;
            if (!OpponentStep()) return; budget += 1;
        }
    }
    public function BeginNextRound() : bool
    {
        var history : array<SBetaGwentRoundResult>; var s,roundCause : SBetaGwentCardSnapshot; var m : SBetaGwentMatchSnapshot; var i, starter : int;
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
        if (!Require(match.ApplyRoundStarted(starter))) return false; m = match.Snapshot();monsters.NilfTrigger(15,roundCause);FlushDeaths();
        for (i = 0; i < live.Size(); i += 1) if (live[i].TemplateId() == 112207) live[i].monsterOnce = 0;
        if (m.roundNumber == 2) { Draw(1, 2); Draw(2, 2); }
        else { Draw(1, 1); Draw(2, 1); }
        waiting = false; BeginMulligan(starter, 1);
        return !fatal;
    }
}

// Disposable presentation-time jobs. Each Step resolves at most one search play.
// No job mutates the live match, its RNG, visual queue or requests.
class CBetaGwentAISequence188 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source, position : CBetaGwentDuelSession;
    public var model : CBetaGwentPublicResponseAI;
    public var ids, values : array<int>;
    public var cardId, phase, index, followLimit, best, risk, delayCost, result : int;
    public var counterOnly : bool;
    public var replyTree097 : CBetaGwentAIReplyTree097;
    public var provenEndgame, passWins, lineWins : bool;
    public function Initialize(game : CBetaGwentDuelSession, id : int, followIds : array<int>, followValues : array<int>, response : CBetaGwentPublicResponseAI, optional counter : bool)
    { source=game;cardId=id;ids=followIds;values=followValues;model=response;counterOnly=counter;followLimit=BetaGwentAITune(7);if(model)followLimit=Min(3,followLimit);
        // Short-round ordering consumes a complete-line score. The legacy
        // last-reply helper returns a per-card uplift and cannot supply it.
        provenEndgame=!counter && response && game.AiPlainLastReply() && !game.AiShortRoundPlanning();
        if(response && !counter && !provenEndgame){replyTree097=new CBetaGwentAIReplyTree097 in this;replyTree097.Initialize(game,id,followIds,followValues,response);}
    }
    public function Step() : bool
    {
        var h : CBetaGwentDuelSession;var m : SBetaGwentMatchSnapshot;var follow : CBetaGwentDuelCard;
        var d : SBetaGwentDuelDefinition;var after,beforeValue,laterValue,finalPass : int;
        if(replyTree097){if(!replyTree097.Step())return false;result=replyTree097.result;return true;}
        BetaGwentAISimEnter();
        if(phase==0){
            position=source.AiSimClone();phase=1;
            if(!position || position.AiSimPlay(cardId)==-2147483647){result=0;phase=4;}
            else {
                if(provenEndgame){
                    h=position.AiSimClone();
                    if(h && h.Pass(1)){h.Pass(2);m=h.Snapshot();passWins=m.matchWinnerMask==2;}
                }
                if(model)model.BeginApply(position);
            }
            BetaGwentAISimLeave();return phase==4;
        }
        if(phase==1){
            if(model){
                if(!model.ApplyStep(position)){BetaGwentAISimLeave();return false;}
                h=model.FinishApply();risk=model.penalty;if(h)position=h;
            }
            if(counterOnly){result=risk;phase=4;BetaGwentAISimLeave();return true;}
            m=position.match.Snapshot();
            if(m.currentPlayerId==1 && !position.AiSimSkipTurn()){result=-risk;phase=4;}
            else {m=position.match.Snapshot();if(m.currentPlayerId!=2 || !m.turnActive){result=-risk;phase=4;}else phase=2;}
            BetaGwentAISimLeave();return phase==4;
        }
        if(phase==2 && index<ids.Size() && index<followLimit){
            after=index;index+=1;
            if(ids[after]!=cardId && values[after]!=-2147483647){
                follow=source.FindCard(ids[after]);m=position.match.Snapshot();
                if(source.AiDecisiveRound() && follow && !m.playerOne.hasPassed){
                    d=follow.Definition();
                    if(source.AiWeatherCardToken(d)>0 || d.header.typeMask==2 && (d.effect==2 || d.effect==3)){
                        beforeValue=source.AiCardTempo(follow,false,source.BestVranAnchor(2),source.AiPublicClearRisk());
                        follow=position.FindCard(ids[after]);laterValue=0;
                        if(follow)laterValue=position.AiCardTempo(follow,false,position.BestVranAnchor(2),position.AiPublicClearRisk());
                        delayCost=Max(delayCost,beforeValue-laterValue);
                    }
                }
                h=position.AiSimClone();if(h){laterValue=h.AiSimPlay(ids[after]);if(laterValue!=-2147483647){
                    best=Max(best,laterValue-values[after]);
                    if(provenEndgame && passWins){
                        for(finalPass=0;finalPass<2;finalPass+=1){m=h.Snapshot();
                            if(m.matchWinnerMask!=0 || !m.turnActive || h.CountLocation(m.currentPlayerId,8)>0 || h.LeaderAvailable(m.currentPlayerId))break;
                            if(!h.Pass(m.currentPlayerId))break;
                        }
                        m=h.Snapshot();if(m.matchWinnerMask==2)lineWins=true;
                    }
                }}
            }
            BetaGwentAISimLeave();return false;
        }
        result=best/2-risk-Min(6,Max(0,delayCost));
        if(lineWins && passWins){result+=1000;source.AiExplain("PROVEN_LAST_SAY","card="+cardId+" passWins=true replyWins=true reason=both_legal_public_continuations_resolved");}
        phase=4;
        BetaGwentAISimLeave();return true;
    }
}

class CBetaGwentAIChase188 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source, position : CBetaGwentDuelSession;
    public var ordered, next : array<SBetaGwentAIChaseAction>;
    public var planner : CBetaGwentAIChasePlanner;
    public var best : SBetaGwentAIChasePlan;
    public var deficit, base, limit, index, followIndex, phase : int;
    public var beamPositions : array<CBetaGwentDuelSession>;
    public var beamPlans : array<SBetaGwentAIChasePlan>;
    public var beamIndex, beamWidth, thirdLimit : int;
    // Keep distinct first actions: reversed permutations of the same pair
    // must not crowd every alternative out of the bounded third-play beam.
    public function KeepContinuation(g : CBetaGwentDuelSession, plan : SBetaGwentAIChasePlan)
    {
        var i,j : int;
        for(i=0;i<beamPlans.Size();i+=1)if(beamPlans[i].firstId==plan.firstId){
            if(beamPlans[i].gain>plan.gain || beamPlans[i].gain==plan.gain && beamPlans[i].reserve<=plan.reserve)return;
            beamPlans.Erase(i);beamPositions.Erase(i);break;
        }
        j=0;while(j<beamPlans.Size() && (beamPlans[j].gain>plan.gain
            || beamPlans[j].gain==plan.gain && beamPlans[j].reserve<=plan.reserve))j+=1;
        beamPlans.Insert(j,plan);beamPositions.Insert(j,g);
        if(beamPlans.Size()>beamWidth){beamPlans.Erase(beamWidth);beamPositions.Erase(beamWidth);}
    }
    public function FindNext(g : CBetaGwentDuelSession)
    {
        var k,j : int;var t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var m : SBetaGwentMatchSnapshot;var item : SBetaGwentAIChaseAction;
        next.Clear();followIndex=0;
        for(k=0;k<g.live.Size();k+=1){
            t=g.live[k].Snapshot();if(t.positionPlayerId!=2 || !t.canBePlayed || t.locationMask!=8 && t.locationMask!=64)continue;
            d=g.live[k].Definition();item.id=t.instanceId;item.cards=1;item.reserve=g.AiReserveCost(d);
            if(t.locationMask==64){item.cards=0;m=g.match.Snapshot();item.reserve=BetaGwentAILeaderReserve(m.roundNumber);if(m.playerOne.crowns>=1)item.reserve=0;}
            item.gain=g.AiCardTempo(g.live[k],true,g.BestVranAnchor(2),g.AiPublicClearRisk());
            j=0;while(j<next.Size() && next[j].gain>=item.gain)j+=1;next.Insert(j,item);
        }
    }
    public function Initialize(game : CBetaGwentDuelSession, actions : array<SBetaGwentAIChaseAction>, gap : int, cap : int)
    {
        var i,j,cheap : int;var item : SBetaGwentAIChaseAction;
        source=game;ordered=actions;deficit=gap;planner=new CBetaGwentAIChasePlanner in this;
        beamWidth=3;thirdLimit=Max(2,Min(4,BetaGwentAIStrength()));
        for(i=1;i<ordered.Size();i+=1){item=ordered[i];j=i-1;while(j>=0 && ordered[j].gain<item.gain){ordered[j+1]=ordered[j];j-=1;}ordered[j+1]=item;}
        cheap=-1;
        for(i=0;i<ordered.Size();i+=1){
            if(ordered[i].gain<deficit)continue;
            if(cheap<0 || ordered[i].reserve<ordered[cheap].reserve || ordered[i].reserve==ordered[cheap].reserve && ordered[i].gain<ordered[cheap].gain)cheap=i;
        }
        if(cheap>0){item=ordered[cheap];ordered.Erase(cheap);ordered.Insert(0,item);}
        limit=Min(ordered.Size(),cap);base=game.AiPublicPassLead();
    }
    public function Step() : bool
    {
        var h : CBetaGwentDuelSession;var t : SBetaGwentCardSnapshot;var d : SBetaGwentDuelDefinition;
        var m : SBetaGwentMatchSnapshot;var candidate : SBetaGwentAIChasePlan;var item : SBetaGwentAIChaseAction;
        var id,k,j,value : int;
        if(index>=limit && phase<3 && !best.reachable && beamPositions.Size()>0){phase=3;beamIndex=0;}
        if(phase==3){
            if(beamIndex>=beamPositions.Size()){
                if(!best.reachable && ordered.Size()>0){best.firstId=ordered[0].id;best.cards=ordered[0].cards;best.actions=1;best.gain=ordered[0].gain;}
                return true;
            }
            position=beamPositions[beamIndex];FindNext(position);phase=4;return false;
        }
        if(phase==4){
            if(followIndex>=next.Size() || followIndex>=thirdLimit){beamIndex+=1;phase=3;return false;}
            value=followIndex;followIndex+=1;BetaGwentAISimEnter();h=position.AiSimClone();
            if(h && h.AiSimPlay(next[value].id)!=-2147483647){
                candidate=beamPlans[beamIndex];candidate.cards=Max(0,h.aiChaseSpent-source.aiChaseSpent);
                candidate.reserve+=next[value].reserve;candidate.actions=3;candidate.gain=h.AiPublicPassLead()-base;
                candidate.reachable=candidate.gain>=deficit;
                if(candidate.reachable && planner.Better(candidate,best))best=candidate;
            }
            BetaGwentAISimLeave();return false;
        }
        if(index>=limit){
            if(!best.reachable && ordered.Size()>0){best.firstId=ordered[0].id;best.cards=ordered[0].cards;best.actions=1;best.gain=ordered[0].gain;}
            return true;
        }
        BetaGwentAISimEnter();
        if(phase==0){
            position=source.AiSimClone();id=ordered[index].id;
            if(position && id==-1){if(position.Leader(2)){t=position.Leader(2).Snapshot();id=t.instanceId;}else position=NULL;}
            if(!position || position.AiSimPlay(id)==-2147483647){index+=1;BetaGwentAISimLeave();return false;}
            candidate.firstId=ordered[index].id;candidate.cards=Max(0,position.aiChaseSpent-source.aiChaseSpent);candidate.reserve=ordered[index].reserve;candidate.actions=1;
            candidate.gain=position.AiPublicPassLead()-base;candidate.reachable=candidate.gain>=deficit;
            if(candidate.reachable && planner.Better(candidate,best))best=candidate;
            if(best.reachable && best.cards<=1 || index>=4)index+=1;else phase=1;
            BetaGwentAISimLeave();return false;
        }
        if(phase==1){
            FindNext(position);
            phase=2;BetaGwentAISimLeave();return false;
        }
        if(followIndex<next.Size() && followIndex<4){
            value=followIndex;followIndex+=1;h=position.AiSimClone();
            if(h && h.AiSimPlay(next[value].id)!=-2147483647){
                candidate.firstId=ordered[index].id;candidate.cards=Max(0,h.aiChaseSpent-source.aiChaseSpent);candidate.reserve=ordered[index].reserve+next[value].reserve;candidate.actions=2;
                candidate.gain=h.AiPublicPassLead()-base;candidate.reachable=candidate.gain>=deficit;
                if(candidate.reachable && planner.Better(candidate,best))best=candidate;
                // Only resolve a third action when no one/two-action catch is
                // known. The normal resource budget still decides whether to
                // spend those cards; a search line never forces an optional chase.
                if(!candidate.reachable && !best.reachable && !h.IsFatal() && !h.IsPending())KeepContinuation(h,candidate);
            }
            BetaGwentAISimLeave();return false;
        }
        index+=1;phase=0;position=NULL;BetaGwentAISimLeave();return false;
    }
}

class CBetaGwentAIRegain188 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var positions : array<CBetaGwentDuelSession>;
    public var depths, indices : array<int>;
    public var entered : array<bool>;
    public var result : bool;
    public function Initialize(game : CBetaGwentDuelSession, depth : int)
    { positions.PushBack(game);depths.PushBack(depth);indices.PushBack(0);entered.PushBack(false); }
    public function Step() : bool
    {
        var g,h : CBetaGwentDuelSession;var m : SBetaGwentMatchSnapshot;var t : SBetaGwentCardSnapshot;
        var top,i : int;var valid : bool;
        if(positions.Size()==0)return true;top=positions.Size()-1;g=positions[top];
        valid=true;
        if(!entered[top]){
            if(g.Score(2)>g.Score(1)){result=true;return true;}
            valid=depths[top]>0;m=g.match.Snapshot();
            if(valid && m.currentPlayerId==1)valid=g.AiSimSkipTurn();
            m=g.match.Snapshot();valid=valid && m.currentPlayerId==2 && m.turnActive;entered[top]=true;
        }
        if(valid)for(i=indices[top];i<g.live.Size();i+=1){
            indices[top]=i+1;t=g.live[i].Snapshot();
            if(t.positionPlayerId!=2 || t.locationMask!=8 && t.locationMask!=64 || !t.canBePlayed)continue;
            h=g.AiSimClone();
            if(h && h.AiSimPlay(t.instanceId)!=-2147483647){positions.PushBack(h);depths.PushBack(depths[top]-1);indices.PushBack(0);entered.PushBack(false);}
            return false;
        }
        positions.Erase(top);depths.Erase(top);indices.Erase(top);entered.Erase(top);return positions.Size()==0;
    }
}

class CBetaGwentAISpy188 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source, position, passPosition : CBetaGwentDuelSession;
    public var recovery : CBetaGwentAIRegain188;
    public var oldHand : array<int>;
    public var cardId, sample, phase, index, best, count, total, recovered, hand, tempo, risk, result : int;
    public var late, opening, unsafe : bool;
    public function Initialize(game : CBetaGwentDuelSession, id : int)
    {
        var m : SBetaGwentMatchSnapshot;
        source=game;cardId=id;game.NorthPile(2,8,oldHand);hand=oldHand.Size();late=hand<=2;
        m=game.match.Snapshot();opening=m.roundNumber==1 && m.playerOne.crowns==0 && m.playerTwo.crowns==0 && !m.playerOne.hasPassed;
    }
    public function Step() : bool
    {
        var h : CBetaGwentDuelSession;var m : SBetaGwentMatchSnapshot;var t : SBetaGwentCardSnapshot;var value : int;var valid : bool;
        if(sample>=3){
            if(count>0){
                tempo/=count;result=total/count;
                if(opening || late){risk=(count-recovered)*4;unsafe=recovered==0 && (opening || source.Score(2)>source.Score(1));}
                // Three usable unordered own-deck forecasts support a separate
                // concession plan; this is not a claim that the spy can catch.
                if(opening && count==3 && total>0 && source.AiSpyConcessionWindow()){risk=0;unsafe=false;}
            }
            return true;
        }
        BetaGwentAISimEnter();
        if(phase==0){
            position=source.AiSimClone();
            if(!position){sample+=1;BetaGwentAISimLeave();return false;}
            position.AiSpyForecastDeck(sample);value=position.AiSimPlay(cardId);
            if(value==-2147483647){sample+=1;position=NULL;BetaGwentAISimLeave();return false;}
            count+=1;tempo+=value;m=position.match.Snapshot();valid=true;
            // A drawing spy must survive the opponent's cheapest reply: pass.
            // Evaluate this BEFORE selecting the spy, without increasing the
            // optional chase budget after it has already been played.
            if(opening){
                passPosition=position.AiSimClone();
                if(passPosition && m.currentPlayerId==1 && !passPosition.Pass(1))passPosition=NULL;
                if(passPosition && (passPosition.IsFatal() || passPosition.IsPending()))passPosition=NULL;
            }
            if(m.currentPlayerId==1)valid=position.AiSimSkipTurn();
            best=0;index=0;phase=1;
            if(!valid)phase=3;
            BetaGwentAISimLeave();return false;
        }
        if(phase==1){
            m=position.match.Snapshot();
            if(m.currentPlayerId==2 && m.turnActive)while(index<position.live.Size()){
                t=position.live[index].Snapshot();index+=1;
                if(t.positionPlayerId!=2 || t.locationMask!=8 || !t.canBePlayed || oldHand.Contains(t.instanceId))continue;
                h=position.AiSimClone();if(h){value=h.AiSimPlay(t.instanceId);if(value!=-2147483647)best=Max(best,value);}
                BetaGwentAISimLeave();return false;
            }
            if(opening && passPosition){
                recovery=new CBetaGwentAIRegain188 in this;recovery.Initialize(passPosition,1);phase=2;
            }else if(!opening && late){
                recovery=new CBetaGwentAIRegain188 in this;recovery.Initialize(position,hand);phase=2;
            }else phase=3;
            BetaGwentAISimLeave();return false;
        }
        if(phase==2){
            if(!recovery.Step()){BetaGwentAISimLeave();return false;}
            if(recovery.result)recovered+=1;recovery=NULL;phase=3;BetaGwentAISimLeave();return false;
        }
        total+=best;sample+=1;phase=0;position=NULL;passPosition=NULL;BetaGwentAISimLeave();return false;
    }
}

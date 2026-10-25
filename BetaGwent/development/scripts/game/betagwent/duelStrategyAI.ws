// Strategy 096: observation boundary and remaining-combination ordering.
// Integrated into optional-round reserves, never a proof of forced results.
struct SBetaGwentStrategyCard096
{
    var id, templateId, side, zone, index, tokens, timerValue : int;
    var power, basePower, armor : int;
    var playable, dying : bool;
}
struct SBetaGwentStrategyView096
{
    var valid, canAct, ownPassed, enemyPassed : bool;
    var ownLeader, enemyLeader, knowsStartingList : bool;
    var actor, round, turn, winner, ownCrowns, enemyCrowns : int;
    var ownScore, enemyScore, ownHandCount, enemyHandCount : int;
    var ownDeckCount, enemyDeckCount, hiddenEnemyBoard : int;
    var ownHand, ownBoard, ownGrave, enemyPublic, enemyRevealedHand : array<SBetaGwentStrategyCard096>;
    var startingList, hazards, dreamRows : array<int>;
    var revision : string;
}
struct SBetaGwentStrategyResources096
{
    var cards, bodyPower, bankedPower, engines, finishers, control : int;
    var independentBodies, activeLinks, heldLinks, noVisibleSetup : int;
    // Comparative, uncalibrated resource units. Never a win probability.
    var estimate : int;
}
struct SBetaGwentStrategyAction096
{
    // 1=pass; 2=explicit unit row; 3=leader; 4=ordinary AI play with abilities.
    var kind, sourceId, row : int;
}
struct SBetaGwentStrategyResult096
{
    var action : SBetaGwentStrategyAction096;
    // 1=estimated frontier; 2=terminal; 3=unsupported; 4=illegal.
    var status, winner, scoreChange, cardsSpent, resourceChange : int;
    var needsEnemyReply, waitingRound : bool;
    var reason : string;
    var remaining : SBetaGwentStrategyResources096;
}
// One candidate is evaluated over three unordered own-deck forecasts.
// A modeled counter only adds a bounded cost; it never proves a forced loss.
class CBetaGwentStrategyResourceJob096 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source, position : CBetaGwentDuelSession;
    public var observer : CBetaGwentStrategyObserve096;
    public var evaluator : CBetaGwentStrategyHand096;
    public var response : CBetaGwentPublicResponseAI;
    public var before : SBetaGwentStrategyView096;
    public var baseline : SBetaGwentStrategyResources096;
    public var ids, penalties, replyCounts : array<int>;
    public var index, phase, directLoss, baseLinks, samples : int;
    public var currentPenalty, sampleIndex : int;
    public var finished, invalidated : bool;
    private function Loss(v : SBetaGwentStrategyView096) : int
    {
        return Max(0,baseLinks-evaluator.PersistentLinks(v,0));
    }
    private function Save()
    {
        penalties.PushBack(Min(8,currentPenalty));replyCounts.PushBack(samples);
        index+=1;phase=0;position=NULL;response=NULL;
    }
    public function Initialize(game : CBetaGwentDuelSession)
    {
        var i,j,cap,id,weight : int;var weights : array<int>;
        var c : CBetaGwentDuelCard;var d : SBetaGwentDuelDefinition;var leaderState : SBetaGwentCardSnapshot;
        source=game;observer=new CBetaGwentStrategyObserve096 in this;
        evaluator=new CBetaGwentStrategyHand096 in this;
        before=observer.Capture(source,2,true);ids.Clear();penalties.Clear();replyCounts.Clear();
        index=0;phase=0;finished=false;invalidated=false;position=NULL;response=NULL;
        if(!before.canAct || before.round>=3 || before.enemyCrowns>0 || before.ownHandCount<3
            || before.hiddenEnemyBoard>0 || game.aiSimDamp>=70){finished=true;return;}
        cap=Max(2,BetaGwentAIStrength()*(100-game.aiSimDamp)/100);
        for(i=0;i<before.ownHand.Size();i+=1){
            if(!before.ownHand[i].playable)continue;id=before.ownHand[i].id;
            c=source.FindCard(id);if(!c)continue;d=c.Definition();
            weight=source.AiStrategyOrder096(id);
            j=0;while(j<weights.Size() && weights[j]>=weight)j+=1;
            weights.Insert(j,weight);ids.Insert(j,id);
        }
        while(ids.Size()>cap)ids.Erase(ids.Size()-1);
        c=source.Leader(2);if(c){leaderState=c.Snapshot();ids.PushBack(leaderState.instanceId);}
    }
    public function Step() : bool
    {
        var current,v : SBetaGwentStrategyView096;var h : CBetaGwentDuelSession;
        var gain,risk : int;
        if(finished)return true;
        current=observer.Capture(source,2,true);
        if(current.revision!=before.revision){invalidated=true;finished=true;return true;}
        if(index>=ids.Size()){finished=true;return true;}
        if(phase==0){
            baseline=evaluator.EvaluateExcluding(before,ids[index]);baseLinks=evaluator.PersistentLinks(before,ids[index]);
            samples=0;currentPenalty=0;sampleIndex=0;
            if(baseLinks==0){Save();return false;}
            phase=1;return false;
        }
        if(phase==1){
            BetaGwentAISimEnter();position=source.AiSimClone();gain=-2147483647;
            if(position){position.AiSpyForecastDeck(sampleIndex);gain=position.AiSimPlay(ids[index]);}
            BetaGwentAISimLeave();
            if(gain==-2147483647 || !position || position.IsFatal() || position.IsPending()){
                currentPenalty=0;Save();return false;
            }
            v=observer.Capture(position,2,true);directLoss=Loss(v)*2;
            if(sampleIndex==0)currentPenalty=directLoss;else currentPenalty=Min(currentPenalty,directLoss);
            sampleIndex+=1;
            if(sampleIndex<3){phase=1;return false;}
            if(before.enemyPassed || position.IsWaitingRound() || v.winner!=0){Save();return false;}
            response=new CBetaGwentPublicResponseAI in this;
            response.Initialize(position,Max(1,BetaGwentAIStrength()-2));response.BeginApply(position);
            phase=2;return false;
        }
        if(phase==2){
            BetaGwentAISimEnter();response.ApplyStep(position);BetaGwentAISimLeave();samples=response.evaluated;
            if(!response.applyDone)return false;
            h=response.FinishApply();
            if(h){v=observer.Capture(h,2,true);
                risk=Max(0,Loss(v)*2-directLoss)*response.controlChance/100;
                currentPenalty+=Min(4,risk);
            }
            Save();return false;
        }
        finished=true;return true;
    }
}
class CBetaGwentStrategyObserve096 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public function Card(s : SBetaGwentCardSnapshot) : SBetaGwentStrategyCard096
    {
        var c : SBetaGwentStrategyCard096;
        c.id=s.instanceId;c.templateId=s.runtimeTemplate.templateId;
        c.side=s.positionPlayerId;c.zone=s.locationMask;c.index=s.locationIndex;
        c.tokens=s.tokenMask;c.timerValue=s.timerValue;c.power=s.power.currentPower;
        c.basePower=s.power.basePower;c.armor=s.power.armor;
        c.playable=s.canBePlayed;c.dying=s.isWaitingToDie;return c;
    }
    private function SortCards(out cards : array<SBetaGwentStrategyCard096>)
    {
        var i,j : int;var c : SBetaGwentStrategyCard096;
        for(i=1;i<cards.Size();i+=1){c=cards[i];j=i-1;
            while(j>=0 && cards[j].id>c.id){cards[j+1]=cards[j];j-=1;}cards[j+1]=c;}
    }
    private function SortIds(out ids : array<int>)
    {
        var i,j,value : int;
        for(i=1;i<ids.Size();i+=1){value=ids[i];j=i-1;
            while(j>=0 && ids[j]>value){ids[j+1]=ids[j];j-=1;}ids[j+1]=value;}
    }
    private function CardsKey(cards : array<SBetaGwentStrategyCard096>) : string
    {
        var i : int;var key : string;var c : SBetaGwentStrategyCard096;
        for(i=0;i<cards.Size();i+=1){c=cards[i];
            key+=";"+c.id+","+c.templateId+","+c.side+","+c.zone+","+c.index+","+c.tokens+","+c.timerValue
                +","+c.power+","+c.basePower+","+c.armor+","+c.playable+","+c.dying;}
        return key;
    }
    public function Capture(game : CBetaGwentDuelSession, actor : int, allowStartingList : bool) : SBetaGwentStrategyView096
    {
        var v : SBetaGwentStrategyView096;var m : SBetaGwentMatchSnapshot;
        var s : SBetaGwentCardSnapshot;var c : SBetaGwentStrategyCard096;
        var enemy,i : int;var key : string;
        if(!game || !BetaGwentIsPlayerId(actor))return v;
        m=game.Snapshot();enemy=BetaGwentOpponentId(actor);
        v.valid=m.initialized && !game.IsFatal();v.actor=actor;v.round=m.roundNumber;
        v.turn=m.turnSequence;v.winner=m.matchWinnerMask;
        if(actor==1){v.ownCrowns=m.playerOne.crowns;v.enemyCrowns=m.playerTwo.crowns;
            v.ownPassed=m.playerOne.hasPassed;v.enemyPassed=m.playerTwo.hasPassed;}
        else{v.ownCrowns=m.playerTwo.crowns;v.enemyCrowns=m.playerOne.crowns;
            v.ownPassed=m.playerTwo.hasPassed;v.enemyPassed=m.playerOne.hasPassed;}
        v.canAct=v.valid && m.turnActive && m.currentPlayerId==actor && !v.ownPassed
            && v.winner==0 && !game.IsPending() && !game.IsWaitingRound();
        v.ownScore=game.Score(actor);v.enemyScore=game.Score(enemy);
        v.ownHandCount=game.CountLocation(actor,8);v.enemyHandCount=game.CountLocation(enemy,8);
        v.ownDeckCount=game.CountLocation(actor,16);v.enemyDeckCount=game.CountLocation(enemy,16);
        // Explicit assignment also enforces a primitive in the translated
        // host, whose reference-to-bool cast otherwise keeps the object.
        if(game.LeaderAvailable(actor))v.ownLeader=true;
        if(game.LeaderAvailable(enemy))v.enemyLeader=true;
        // Identity is read only AFTER selecting a permitted visible zone.
        // Hidden enemy placeholders preserve public location, never their value.
        for(i=0;i<game.live.Size();i+=1){s=game.live[i].Snapshot();
            if(s.positionPlayerId==actor){
                if(s.locationMask==8)v.ownHand.PushBack(Card(s));
                else if((s.locationMask&7)!=0)v.ownBoard.PushBack(Card(s));
                else if(s.locationMask==32)v.ownGrave.PushBack(Card(s));
            }else if(s.positionPlayerId==enemy){
                if((s.locationMask&7)!=0 && (s.tokenMask&8)!=0){
                    v.hiddenEnemyBoard+=1;
                    c.id=s.instanceId;c.templateId=0;c.side=enemy;c.zone=s.locationMask;
                    c.index=s.locationIndex;c.tokens=8;c.timerValue=-1;c.power=0;c.basePower=0;
                    c.armor=0;c.playable=false;c.dying=false;v.enemyPublic.PushBack(c);
                }else if((s.locationMask&7)!=0 || s.locationMask==32)v.enemyPublic.PushBack(Card(s));
                else if(s.locationMask==8 && (s.tokenMask&64)!=0)v.enemyRevealedHand.PushBack(Card(s));
            }
        }
        // The initial list is an unordered, separately authorized observation.
        // Own remaining deck order and enemy private hand/deck are never exported.
        if(allowStartingList && BetaGwentAIStrength()>=4){
            if(enemy==1){for(i=0;i<game.aiStartingDeckOne.Size();i+=1)v.startingList.PushBack(game.aiStartingDeckOne[i]);}
            else{for(i=0;i<game.aiStartingDeckTwo.Size();i+=1)v.startingList.PushBack(game.aiStartingDeckTwo[i]);}
            v.knowsStartingList=v.startingList.Size()>0;SortIds(v.startingList);
        }
        if(game.weather){
            for(i=0;i<game.weather.hazards.Size();i+=1)v.hazards.PushBack(game.weather.hazards[i]);
            for(i=0;i<game.weather.dreamRows.Size();i+=1)v.dreamRows.PushBack(game.weather.dreamRows[i]);
        }
        SortCards(v.ownHand);SortCards(v.ownBoard);SortCards(v.ownGrave);
        SortCards(v.enemyPublic);SortCards(v.enemyRevealedHand);
        key="v1:"+v.actor+":"+v.round+":"+v.turn+":"+v.winner+":"+v.canAct
            +":"+v.ownCrowns+":"+v.enemyCrowns+":"+v.ownPassed+":"+v.enemyPassed
            +":"+v.ownScore+":"+v.enemyScore+":"+v.ownHandCount+":"+v.enemyHandCount
            +":"+v.ownDeckCount+":"+v.enemyDeckCount+":"+v.ownLeader+":"+v.enemyLeader;
        key+="|h"+CardsKey(v.ownHand)+"|b"+CardsKey(v.ownBoard)+"|g"+CardsKey(v.ownGrave)
            +"|e"+CardsKey(v.enemyPublic)+"|r"+CardsKey(v.enemyRevealedHand);
        for(i=0;i<v.hazards.Size();i+=1)key+="|w"+v.hazards[i];
        for(i=0;i<v.dreamRows.Size();i+=1)key+="|d"+v.dreamRows[i];
        for(i=0;i<v.startingList.Size();i+=1)key+="|s"+v.startingList[i];
        v.revision=key;return v;
    }
}
class CBetaGwentStrategyHand096 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    private function Count(cards : array<SBetaGwentStrategyCard096>, id : int, active : bool) : int
    {
        var i,total : int;
        for(i=0;i<cards.Size();i+=1){
            if(cards[i].templateId!=id || cards[i].dying || (cards[i].tokens&4)!=0)continue;
            if(active && (cards[i].tokens&8)!=0)continue;total+=1;}
        return total;
    }
    // A one-shot setup (Draig's grave boost, for example) has already delivered
    // its effect. Losing that body is not losing a persistent engine.
    public function PersistentLinks(v : SBetaGwentStrategyView096, excluded : int) : int
    {
        var pairs : array<SBetaGwentAICombo>;var d : SBetaGwentDuelDefinition;
        var i,j,best,total : int;BetaGwentAICombos(pairs);
        for(i=0;i<v.ownHand.Size();i+=1){
            if(v.ownHand[i].id==excluded || v.ownHand[i].dying || (v.ownHand[i].tokens&4)!=0)continue;
            best=0;
            for(j=0;j<pairs.Size();j+=1){
                if(pairs[j].payoff!=v.ownHand[i].templateId)continue;
                d=BetaGwentDuelDefinition(pairs[j].setup);
                if(BetaGwentAIEngine(pairs[j].setup)<=0 && d.passiveBoost<=0 && d.timerPeriod<=0)continue;
                if(Count(v.ownBoard,pairs[j].setup,true)>0 || Count(v.ownHand,pairs[j].setup,false)>0)
                    best=Max(best,pairs[j].weight);
            }
            total+=best;
        }
        return total;
    }
    public function Evaluate(v : SBetaGwentStrategyView096) : SBetaGwentStrategyResources096
    { return EvaluateExcluding(v,0); }
    // Exclude the committed payoff but keep its availability as a setup.
    public function EvaluateExcluding(v : SBetaGwentStrategyView096, excluded : int) : SBetaGwentStrategyResources096
    {
        var f : SBetaGwentStrategyResources096;var i,j,id,active,held : int;
        var bestActive,bestHeld : int;var related : bool;
        var c : SBetaGwentStrategyCard096;var d : SBetaGwentDuelDefinition;
        var pairs : array<SBetaGwentAICombo>;
        if(!v.valid)return f;BetaGwentAICombos(pairs);
        for(i=0;i<v.ownHand.Size();i+=1){c=v.ownHand[i];if(c.dying || c.id==excluded)continue;
            d=BetaGwentDuelDefinition(c.templateId);id=c.templateId;f.cards+=1;
            if(d.header.typeMask==4){f.bodyPower+=Max(0,c.power);f.bankedPower+=Max(0,c.power-c.basePower);}
            if((c.tokens&4)==0){
                if(BetaGwentAIEngine(id)>0 || d.passiveBoost>0 || d.timerPeriod>0)f.engines+=1;
                if(BetaGwentAIFinisher(id))f.finishers+=1;
                if(BetaGwentAIControlCard(d))f.control+=1;
            }
            if(d.header.typeMask==4 && d.effect==0 && BetaGwentAIEngine(id)==0
                && d.passiveBoost==0 && d.timerPeriod==0)f.independentBodies+=1;
            bestActive=0;bestHeld=0;related=false;
            if((c.tokens&4)==0)for(j=0;j<pairs.Size();j+=1){
                if(pairs[j].payoff!=id)continue;related=true;
                active=Count(v.ownBoard,pairs[j].setup,true);
                held=Count(v.ownHand,pairs[j].setup,false);
                if(pairs[j].setup==id)held=Max(0,held-1);
                if(active>0)bestActive=Max(bestActive,pairs[j].weight);
                if(held>0)bestHeld=Max(bestHeld,pairs[j].weight);
            }
            // A payoff with several alternative setups is counted once.
            // These catalogue links are features, not proven legal combo lines.
            if(bestActive>0)f.activeLinks+=bestActive;
            else if(bestHeld>0)f.heldLinks+=bestHeld;
            else if(related)f.noVisibleSetup+=1;
        }
        // Banked power is already part of bodyPower. Missing a visible setup
        // is diagnostic only: a future draw may still supply it.
        f.estimate=f.bodyPower+f.engines*2+f.finishers*2+f.control*2+f.activeLinks*2+f.heldLinks;
        return f;
    }
}
class CBetaGwentStrategyProbe096 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source : CBetaGwentDuelSession;
    public var observer : CBetaGwentStrategyObserve096;
    public var evaluator : CBetaGwentStrategyHand096;
    public var before : SBetaGwentStrategyView096;
    public var initialResources : SBetaGwentStrategyResources096;
    public var actions : array<SBetaGwentStrategyAction096>;
    public var results : array<SBetaGwentStrategyResult096>;
    public var index, candidateCount, unsupportedCards : int;
    public var invalidated, truncated, finished : bool;
    private function Add(a : SBetaGwentStrategyAction096, cap : int)
    { candidateCount+=1;if(actions.Size()<cap)actions.PushBack(a);else truncated=true; }
    public function Initialize(game : CBetaGwentDuelSession, cap : int)
    {
        var a : SBetaGwentStrategyAction096;var i,row : int;var d : SBetaGwentDuelDefinition;
        var leader : CBetaGwentDuelCard;var leaderState : SBetaGwentCardSnapshot;
        source=game;index=0;candidateCount=0;unsupportedCards=0;invalidated=false;truncated=false;finished=false;
        actions.Clear();results.Clear();observer=new CBetaGwentStrategyObserve096 in this;
        evaluator=new CBetaGwentStrategyHand096 in this;
        before=observer.Capture(source,2,true);initialResources=evaluator.Evaluate(before);
        if(!before.canAct){finished=true;return;}cap=Max(1,Min(64,cap));
        a.kind=1;a.sourceId=0;a.row=0;Add(a,cap);
        for(i=0;i<before.ownHand.Size();i+=1){
            d=BetaGwentDuelDefinition(before.ownHand[i].templateId);
            if(!before.ownHand[i].playable)continue;
            a.kind=4;a.sourceId=before.ownHand[i].id;a.row=0;Add(a,cap);
            if(d.header.typeMask==4 && d.effect==0){
                a.kind=2;for(row=1;row<=4;row*=2){a.row=row;Add(a,cap);}
            }
        }
        leader=source.Leader(2);if(leader){leaderState=leader.Snapshot();a.kind=3;a.sourceId=leaderState.instanceId;a.row=0;Add(a,cap);}
    }
    // One action per Step. No continuation silently skips an active opponent.
    // This first slice reports resources; it does not choose a live game move.
    public function Step() : bool
    {
        var current,after : SBetaGwentStrategyView096;var r : SBetaGwentStrategyResult096;
        var g : CBetaGwentDuelSession;var ok : bool;var gain : int;
        if(finished)return true;
        current=observer.Capture(source,2,true);
        if(current.revision!=before.revision){invalidated=true;finished=true;return true;}
        if(index>=actions.Size()){finished=true;return true;}
        r.action=actions[index];index+=1;
        // The anonymous six-point placeholder is not a model of Toruviel.
        // Until a trap hypothesis exists, these branches stay unsupported.
        if(before.hiddenEnemyBoard>0){r.status=3;r.reason="unmodelled_hidden_board";results.PushBack(r);return false;}
        BetaGwentAISimEnter();g=source.AiSimClone();ok=false;
        if(g){
            g.AiSpyForecastDeck(0);
            if(r.action.kind==1)ok=g.Pass(2);
            else if(r.action.kind==2)ok=g.Play(2,r.action.sourceId,r.action.row);
            else if(r.action.kind==3 || r.action.kind==4){gain=g.AiSimPlay(r.action.sourceId);ok=gain!=-2147483647;}
        }
        if(!g){r.status=3;r.reason="clone_unavailable";}
        else if(!ok){r.status=4;r.reason="action_rejected_by_rules";}
        else if(g.IsFatal() || g.IsPending()){r.status=3;r.reason="unresolved_action";}
        else{
            after=observer.Capture(g,2,true);r.remaining=evaluator.Evaluate(after);
            r.winner=after.winner;r.status=1;r.reason="one_action_frontier";
            if(after.winner!=0){r.status=2;r.reason="actual_terminal_result";}
            r.scoreChange=(after.ownScore-after.enemyScore)-(before.ownScore-before.enemyScore);
            r.cardsSpent=before.ownHandCount-after.ownHandCount;
            r.resourceChange=r.remaining.estimate-initialResources.estimate;
            r.needsEnemyReply=!before.enemyPassed && after.winner==0 && !g.IsWaitingRound();
            r.waitingRound=g.IsWaitingRound();
        }
        BetaGwentAISimLeave();results.PushBack(r);return false;
    }
}

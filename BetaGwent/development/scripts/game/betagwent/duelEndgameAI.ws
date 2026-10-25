// Complete alternating search only in a checked deterministic public subgame.
// A budget cutoff or unsupported rule is UNKNOWN, never a losing/winning proof.
class CBetaGwentAIEndNode097 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var game : CBetaGwentDuelSession;
    public var actions : array<int>;
    public var actor, index, best, bestId, pendingId : int;
    public var alpha, beta : int;
    public var entered : bool;
}
class CBetaGwentAIEndgame097 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source : CBetaGwentDuelSession;
    public var observer : CBetaGwentStrategyObserve096;
    public var before : SBetaGwentStrategyView096;
    public var stack : array<CBetaGwentAIEndNode097>;
    public var nodes, limit, result, firstId : int;
    public var finished, complete, invalidated, supported : bool;
    private function Plain(d : SBetaGwentDuelDefinition) : bool
    {
        return d.header.typeMask==4 && d.header.tierMask!=8 && d.effect==0 && d.specialMode==0
            && d.passiveBoost==0 && d.timerPeriod==0 && d.initialTimer<0 && d.deathwishDamage==0
            && d.deathwishSpawnCount==0 && d.deathwishSummonTemplate==0 && d.consumePassiveBoost==0
            && d.passiveWeatherToken==0 && (d.unitTraits&32)==0 && (d.tokens&136)==0
            && BetaGwentAIEngine(d.header.templateId)==0;
    }
    public function CanSolve(v : SBetaGwentStrategyView096) : bool
    {
        var i : int;var c : SBetaGwentStrategyCard096;var d : SBetaGwentDuelDefinition;
        if(!v.canAct || v.round!=3 || v.ownLeader || v.enemyLeader || v.hiddenEnemyBoard>0
            || v.ownHandCount<1 || v.ownHandCount>6 || !v.enemyPassed && v.ownHandCount+v.enemyHandCount>6
            || !v.enemyPassed && v.enemyRevealedHand.Size()!=v.enemyHandCount)return false;
        for(i=0;i<v.hazards.Size();i+=1)if(v.hazards[i]!=0)return false;
        if(v.dreamRows.Size()>0)return false;
        for(i=0;i<v.ownHand.Size()+v.enemyRevealedHand.Size()+v.ownBoard.Size()+v.enemyPublic.Size();i+=1){
            if(i<v.ownHand.Size())c=v.ownHand[i];
            else if(i<v.ownHand.Size()+v.enemyRevealedHand.Size())c=v.enemyRevealedHand[i-v.ownHand.Size()];
            else if(i<v.ownHand.Size()+v.enemyRevealedHand.Size()+v.ownBoard.Size())c=v.ownBoard[i-v.ownHand.Size()-v.enemyRevealedHand.Size()];
            else c=v.enemyPublic[i-v.ownHand.Size()-v.enemyRevealedHand.Size()-v.ownBoard.Size()];
            // Graves do not get a hidden identity lookup; no supported action resurrects.
            if(c.zone==32)continue;
            if(c.dying || (c.tokens&136)!=0 || c.timerValue>=0)return false;
            d=BetaGwentDuelDefinition(c.templateId);
            if(c.zone==8 && c.templateId==113309)continue;
            if(!Plain(d))return false;
        }
        return true;
    }
    public function Initialize(game : CBetaGwentDuelSession)
    {
        var n : CBetaGwentAIEndNode097;
        source=game;observer=new CBetaGwentStrategyObserve096 in this;before=observer.Capture(game,2,true);
        supported=CanSolve(before);finished=!supported;complete=false;invalidated=false;
        if(!supported)return;
        limit=32;if(BetaGwentAIStrength()>=3)limit=64;if(BetaGwentAIStrength()>=4)limit=256;
        limit=Max(16,limit*(100-game.aiSimDamp)/100);
        n=new CBetaGwentAIEndNode097 in this;n.game=game.AiSimClone();n.alpha=-2;n.beta=2;stack.PushBack(n);
    }
    private function ReturnValue(value : int)
    {
        var top : int;var n,previous : CBetaGwentAIEndNode097;
        top=stack.Size()-1;n=stack[top];stack.Erase(top);
        if(stack.Size()==0){result=value;firstId=n.bestId;finished=true;complete=true;return;}
        previous=stack[stack.Size()-1];
        if(previous.actor==2 && value>previous.best || previous.actor==1 && value<previous.best){previous.best=value;previous.bestId=previous.pendingId;}
        if(previous.actor==2)previous.alpha=Max(previous.alpha,previous.best);
        else previous.beta=Min(previous.beta,previous.best);
    }
    // Original-beta move ordering adapted only to the verified public rules.
    // This ranks children; every legal action remains in the search.
    private function ActionValue(n : CBetaGwentAIEndNode097, id : int) : int
    {
        var s : SBetaGwentCardSnapshot;var i,highest,value : int;
        s=n.game.FindCard(id).Snapshot();
        if(s.runtimeTemplate.templateId!=113309)return s.power.currentPower;
        for(i=0;i<n.game.live.Size();i+=1){s=n.game.live[i].Snapshot();
            if((s.locationMask&7)!=0 && !s.isWaitingToDie)highest=Max(highest,s.power.currentPower);}
        for(i=0;i<n.game.live.Size();i+=1){s=n.game.live[i].Snapshot();
            if((s.locationMask&7)!=0 && !s.isWaitingToDie && s.power.currentPower==highest){
                if(s.positionPlayerId==n.actor)value-=s.power.currentPower;else value+=s.power.currentPower;}}
        return value;
    }
    public function Step() : bool
    {
        var v : SBetaGwentStrategyView096;var n,child : CBetaGwentAIEndNode097;
        var g,reverse : CBetaGwentDuelSession;var m : SBetaGwentMatchSnapshot;
        var s : SBetaGwentCardSnapshot;var i,j,id,value : int;var ok : bool;var priorities : array<int>;
        if(finished)return true;v=observer.Capture(source,2,true);
        if(v.revision!=before.revision){invalidated=true;finished=true;return true;}
        if(nodes>=limit){finished=true;stack.Clear();return true;}
        n=stack[stack.Size()-1];m=n.game.Snapshot();
        if(m.matchWinnerMask!=0){value=0;if(m.matchWinnerMask==2)value=1;else if(m.matchWinnerMask==1)value=-1;ReturnValue(value);return finished;}
        if(n.game.IsWaitingRound() || !m.turnActive || n.game.IsFatal() || n.game.IsPending()){finished=true;stack.Clear();return true;}
        if(!n.entered){
            n.entered=true;n.actor=m.currentPlayerId;n.best=-2;if(n.actor==1)n.best=2;
            // Prefer ending a won subgame to spending another equally winning card.
            n.actions.PushBack(0);
            priorities.PushBack(0);
            for(i=0;i<n.game.live.Size();i+=1){s=n.game.live[i].Snapshot();
                if(s.positionPlayerId==n.actor && s.locationMask==8 && s.canBePlayed){
                    value=ActionValue(n,s.instanceId);j=n.actions.Size();
                    n.actions.PushBack(s.instanceId);priorities.PushBack(value);
                    // Keep pass first and stable ordering among equal material.
                    while(j>1 && priorities[j-1]<value){n.actions[j]=n.actions[j-1];priorities[j]=priorities[j-1];j-=1;}
                    n.actions[j]=s.instanceId;priorities[j]=value;}}
            return false;
        }
        // The original beta also prunes branches with inherited alpha/beta
        // bounds. Here the budget and checked public subgame stay unchanged.
        // A pruned child is only a bound; it cannot replace a better root move.
        if(n.index>=n.actions.Size() || n.alpha>=n.beta || n.actor==2 && n.best==1 || n.actor==1 && n.best==-1){ReturnValue(n.best);return finished;}
        id=n.actions[n.index];n.index+=1;n.pendingId=id;nodes+=1;
        BetaGwentAISimEnter();g=n.game.AiSimClone();ok=false;
        if(g){
            if(id==0)ok=g.Pass(n.actor);
            else if(n.actor==2)ok=g.AiSimPlay(id)!=-2147483647;
            else{reverse=g.AiReverseClone();if(reverse && reverse.AiSimPlay(id)!=-2147483647){g=reverse.AiReverseClone();ok=true;}}
        }
        BetaGwentAISimLeave();
        if(!ok || !g || g.IsFatal() || g.IsPending()){finished=true;stack.Clear();return true;}
        child=new CBetaGwentAIEndNode097 in this;child.game=g;child.alpha=n.alpha;child.beta=n.beta;stack.PushBack(child);return false;
    }
}

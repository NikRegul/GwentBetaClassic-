// Alternating frontier: our move -> each public plausible reply -> our best continuation.
// Unknown replies are hypotheses, not knowledge of the hidden hand or forced proofs.
class CBetaGwentAIReplyTree097 extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
    public var source, root, branch, passProbe : CBetaGwentDuelSession;
    public var model : CBetaGwentPublicResponseAI;
    public var observer : CBetaGwentStrategyObserve096;
    public var before : SBetaGwentStrategyView096;
    public var ids, values, branchOrder : array<int>;
    public var cardId, phase, index, followLimit, branchBest, branchRisk, branchWeight : int;
    public var totalWeight, weightedResult, worstResult, passResult, result, branches, follows : int;
    public var passBranch, knownHand, finished, invalidated, shortRound : bool;
    public var commonBaseline : int;
    public var branchBestId, branchTemplate : int;
    public var branchDrawId, settlementId, settlementDelta : int;
    public var settlementFollow : bool;
    public var replyTemplates, continuationIds, branchScores : array<int>;
    // 094b: face-down enemy cards are searched under public ambush hypotheses.
    public var hypCards, hypTemplates, hypTimers, hypWeights : array<int>;
    public var hypCount, hypIndex, hypTotal, hypWeighted, hypWorst : int;
    public var hypBase, hypTrap : int;public var hypBaseReady : bool;
    public function Initialize(game : CBetaGwentDuelSession, id : int, followIds : array<int>, followValues : array<int>, response : CBetaGwentPublicResponseAI)
    {
        var i : int;
        source=game;cardId=id;model=response;
        shortRound=source.AiShortRoundPlanning();
        for(i=0;i<followValues.Size();i+=1)commonBaseline=Max(commonBaseline,followValues[i]);
        for(i=0;i<followIds.Size() && i<followValues.Size();i+=1)if(followIds[i]!=id){ids.PushBack(followIds[i]);values.PushBack(followValues[i]);}
        observer=new CBetaGwentStrategyObserve096 in this;before=observer.Capture(source,2,true);
        knownHand=before.enemyHandCount>0 && before.enemyRevealedHand.Size()==before.enemyHandCount;
        followLimit=Min(BetaGwentAITune(7),Max(2,BetaGwentAIStrength()-1));
        worstResult=2147483647;phase=0;hypWorst=2147483647;
        if(before.hiddenEnemyBoard>0)hypCount=source.AiAmbushHypotheses(hypCards,hypTemplates,hypTimers,hypWeights);
    }
    private function NextHypothesis()
    {
        root=NULL;branch=NULL;passProbe=NULL;totalWeight=0;weightedResult=0;worstResult=2147483647;
        passResult=0;branches=0;replyTemplates.Clear();continuationIds.Clear();branchScores.Clear();
        model.keepBranches097=false;phase=0;
    }
    private function StartBranch(g : CBetaGwentDuelSession, weight : int, risk : int, passing : bool)
    {
        branch=g;passProbe=NULL;branchWeight=Max(1,weight);branchRisk=risk;passBranch=passing;
        branchBest=-2147483647;branchBestId=0;branchDrawId=-1;index=0;phase=2;OrderContinuations();
        // An opponent pass does not force another hand play. Resolve our
        // answering pass on its own callback before evaluating continuations.
        // Use the actual rules: a visible lead can disappear to a pass timer.
        settlementFollow=false;settlementId=0;
        if(CanResolvePass(branch))BeginPassProbe(branch);
    }
    private function CanResolvePass(g : CBetaGwentDuelSession) : bool
    {
        var m : SBetaGwentMatchSnapshot;m=g.Snapshot();
        return m.turnActive && m.matchWinnerMask==0
            && (m.currentPlayerId==2 && m.playerOne.hasPassed
                || g.CountLocation(1,8)==0 && !g.LeaderAvailable(1));
    }
    private function BeginPassProbe(g : CBetaGwentDuelSession)
    {
        var m : SBetaGwentMatchSnapshot;m=g.Snapshot();phase=5;
        if(m.currentPlayerId==1){passProbe=g.AiSimClone();phase=6;}
    }
    private function CompletePassProbe(outcome : int)
    {
        if(outcome==2){branch=passProbe;branchBestId=settlementId;FinishBranch();}
        else{
            // A guaranteed draw is a floor, not a reason to stop seeking a
            // winning continuation. Prefer a drawing pass to an equal score.
            if(outcome==3 && (branchDrawId<0 || settlementId==0))branchDrawId=settlementId;
            if(settlementFollow && settlementDelta>branchBest){branchBest=settlementDelta;branchBestId=settlementId;}
            phase=2;
        }
        passProbe=NULL;
    }
    // Keep the original best continuation, then spend the remaining fixed
    // budget on cards whose targets or combo payoff improved after this reply.
    // This scans only our hand and the anonymized public branch; it adds no plays.
    private function OrderContinuations()
    {
        var i,j,gain,anchor,clearRisk : int;
        var scores : array<int>;var card : CBetaGwentDuelCard;var s : SBetaGwentCardSnapshot;
        branchOrder.Clear();anchor=branch.BestVranAnchor(2);clearRisk=branch.AiPublicClearRisk();
        for(i=0;i<ids.Size();i+=1){
            card=branch.FindCard(ids[i]);if(!card || values[i]==-2147483647)continue;
            s=card.Snapshot();if(s.positionPlayerId!=2 || s.locationMask!=8 || !s.canBePlayed)continue;
            gain=branch.AiCardTempo(card,true,anchor,clearRisk)-values[i];
            // The first legal source candidate remains a control against a
            // misleading heuristic. Exact branch results still choose the move.
            if(branchOrder.Size()==0){branchOrder.PushBack(i);scores.PushBack(gain);}
            else{
                j=1;while(j<branchOrder.Size() && scores[j]>=gain)j+=1;
                branchOrder.Insert(j,i);scores.Insert(j,gain);
            }
        }
    }
    private function FinishBranch()
    {
        var value : int;var m : SBetaGwentMatchSnapshot;
        if(branchBest==-2147483647)branchBest=0;
        value=branchBest/2-branchRisk/2;
        // In a short mandatory round compare the whole two-own-move line.
        // A per-card baseline rewards spending the only answer too early;
        // every first move must instead share the same opportunity cost.
        // A resolved frontier already contains both the opposing body and its
        // ability. Subtracting a separate reply-risk estimate would debit it twice.
        if(shortRound)value=branchBest*10/Max(1,BetaGwentAITune(8));
        m=branch.Snapshot();
        // A terminal under a hypothesis is still just a modeled branch.
        if(m.matchWinnerMask==1)value=-30;
        else if(m.matchWinnerMask==2)value=30;
        if(branchDrawId>=0 && value<=0){value=0;branchBestId=branchDrawId;}
        if(passBranch){passResult=value;phase=4;}
        else{
            replyTemplates.PushBack(branchTemplate);continuationIds.PushBack(branchBestId);branchScores.PushBack(value);
            branches+=1;totalWeight+=branchWeight;weightedResult+=value*branchWeight;
            worstResult=Min(worstResult,value);phase=1;
        }
        branch=NULL;
    }
    public function Step() : bool
    {
        var current : SBetaGwentStrategyView096;var m : SBetaGwentMatchSnapshot;
        var h : CBetaGwentDuelSession;var i,gain,delta,aggregate : int;
        if(finished)return true;
        current=observer.Capture(source,2,true);
        if(current.revision!=before.revision){invalidated=true;finished=true;result=0;passProbe=NULL;model.keepBranches097=false;return true;}
        // Hidden board identities need a trap hypothesis, never a harmless placeholder.
        // Without a usable public hypothesis keep the old conservative exit.
        if(before.hiddenEnemyBoard>0 && hypCount==0){finished=true;result=0;return true;}
        BetaGwentAISimEnter();
        if(phase==0 && hypCount>0 && !hypBaseReady){
            // Control line once per tree: the same first move against the
            // anonymous placeholder. Its own callback keeps one action each.
            hypBaseReady=true;h=source.AiSimClone();hypBase=-2147483647;
            if(h){h.AiSpyForecastDeck(0);if(h.AiSimPlay(cardId)!=-2147483647 && !h.IsFatal() && !h.IsPending())hypBase=h.AiTrapBalance(hypCards);}
        }else if(phase==0){
            root=source.AiSimClone();gain=-2147483647;
            if(root && hypCount>0)root.AiApplyAmbushHypothesis(hypCards,hypTemplates,hypTimers,hypIndex*hypCards.Size());
            if(root){root.AiSpyForecastDeck(0);gain=root.AiSimPlay(cardId);}
            if(gain==-2147483647 || !root || root.IsFatal() || root.IsPending()){
                // One illegal hypothesis must not erase the others' evidence.
                if(hypCount>0){phase=4;totalWeight=0;hypTrap=0;}else{finished=true;result=0;}
            }
            else{
                hypTrap=0;if(hypCount>0 && hypBase!=-2147483647)hypTrap=root.AiTrapBalance(hypCards)-hypBase;
                model.keepBranches097=true;model.BeginApply(root);phase=1;
            }
        }else if(phase==1){
            model.ApplyStep(root);
            if(model.lastReply097){
                h=model.lastReply097.AiReverseClone();
                if(h){branchTemplate=model.lastTemplate097;StartBranch(h,model.lastWeight097,model.lastExtra097,false);}
            }else if(model.applyDone)phase=3;
        }else if(phase==2){
            m=branch.Snapshot();
            if(m.matchWinnerMask!=0 || branch.IsWaitingRound() || !m.turnActive || m.currentPlayerId!=2){FinishBranch();}
            else if(index>=branchOrder.Size() || index>=followLimit){FinishBranch();}
            else{
                i=branchOrder[index];index+=1;
                if(ids[i]!=cardId && i<values.Size() && values[i]!=-2147483647){
                    h=branch.AiSimClone();gain=-2147483647;
                    if(h){h.AiSpyForecastDeck(0);gain=h.AiSimPlay(ids[i]);}
                    if(gain!=-2147483647 && !h.IsFatal() && !h.IsPending()){
                        follows+=1;delta=gain-values[i]-source.AiDelayCost097(ids[i],branch)*2;
                        if(shortRound){
                            // Compare complete resulting positions from the SAME
                            // source, including timer events during the enemy turn.
                            // A follow-up's local gain loses that earlier material.
                            delta=h.AiProjectedLead()-source.AiProjectedLead()
                                +h.AiPendingCharmValue(2)-h.AiPendingCharmValue(1)
                                -commonBaseline-source.AiDelayCost097(ids[i],branch);
                        }
                        m=h.Snapshot();
                        if(m.matchWinnerMask!=0 || CanResolvePass(h)){
                            // The next card may turn a drawing pass into a
                            // victory. Resolve its settlement before retaining
                            // the draw floor; never compare a win by raw tempo.
                            passProbe=h;settlementFollow=true;settlementId=ids[i];settlementDelta=delta;
                            if(m.matchWinnerMask!=0)CompletePassProbe(m.matchWinnerMask);else BeginPassProbe(h);
                        }else if(delta>branchBest){branchBest=delta;branchBestId=ids[i];}
                    }
                }
            }
        }else if(phase==5){
            if(!passProbe)passProbe=branch.AiSimClone();phase=2;
            if(passProbe && passProbe.Pass(2) && !passProbe.IsFatal() && !passProbe.IsPending()){
                m=passProbe.Snapshot();
                // Empty hand alone does not settle the round. Only when no
                // leader remains is the opponent's next action forced to pass.
                // Resolve it on a separate callback, including turn reactions.
                if(m.matchWinnerMask==0 && m.turnActive && m.currentPlayerId==1
                    && !m.playerOne.hasPassed && passProbe.CountLocation(1,8)==0 && !passProbe.LeaderAvailable(1))phase=6;
                else CompletePassProbe(m.matchWinnerMask);
            }else CompletePassProbe(0);
        }else if(phase==6){
            if(passProbe && passProbe.Pass(1) && !passProbe.IsFatal() && !passProbe.IsPending()){
                m=passProbe.Snapshot();
                // After our follow-up it is the exhausted opponent who passes
                // first. Our answering pass still needs its own callback.
                if(m.matchWinnerMask==0 && m.turnActive && m.currentPlayerId==2 && !m.playerTwo.hasPassed)phase=5;
                else CompletePassProbe(m.matchWinnerMask);
            }else CompletePassProbe(0);
        }else if(phase==3){
            // Passing is a legal opponent action, not a skipped opponent turn.
            h=root.AiSimClone();
            if(h){m=h.Snapshot();if(m.currentPlayerId==1 && h.Pass(1))StartBranch(h,1,0,true);else phase=4;}
            else phase=4;
        }else{
            aggregate=0;
            if(totalWeight>0){
                if(knownHand)aggregate=Min(worstResult,passResult);
                else aggregate=((3*(weightedResult/totalWeight)+worstResult)/4*(100-model.applyPassChance)+passResult*model.applyPassChance)/100;
                if(shortRound)aggregate=Max(-80,Min(80,aggregate));
                else aggregate=Max(-24,Min(24,aggregate));
            }
            // Short rounds already compare complete lines from the source,
            // which include the trap. Elsewhere add the first move's own price.
            if(hypCount>0 && !shortRound)aggregate=Max(-24,Min(24,aggregate+hypTrap));
            if(hypCount>0){
                // The same blend as public replies: mostly expectation,
                // with a quarter of the most punishing plausible ambush.
                hypTotal+=hypWeights[hypIndex];hypWeighted+=aggregate*hypWeights[hypIndex];
                hypWorst=Min(hypWorst,aggregate);hypIndex+=1;
                if(hypIndex<hypCount){NextHypothesis();BetaGwentAISimLeave();return false;}
                aggregate=(3*(hypWeighted/Max(1,hypTotal))+hypWorst)/4;
            }
            result=aggregate;
            model.keepBranches097=false;finished=true;
            source.AiExplain("REPLY_TREE","card="+cardId+" replies="+branches+" continuations="+follows+" knownHand="+knownHand+" ambushHypotheses="+hypCount+" adjustment="+result+" reason=separate_best_continuation_for_each_public_reply");
        }
        BetaGwentAISimLeave();return finished;
    }
}

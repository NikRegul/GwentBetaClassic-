// Shared round economy for every archetype. Gains are heuristic estimates of
// immediate tempo, not a simulation of hidden cards or future weather ticks.
struct SBetaGwentAIChaseAction
{
    var id : int;
    var gain : int;
    var cards : int;
    var reserve : int;
}
struct SBetaGwentAIChasePlan
{
    var reachable : bool;
    var firstId : int;
    var cards : int;
    var actions : int;
    var reserve : int;
    var gain : int;
}
// 0=continue; positive reason=pass. Remember all cards spent AFTER the pass,
// so a sequence of locally cheap decisions cannot become an expensive chase.
function BetaGwentAIChasePassReason(reachable : bool, cards : int, spent : int,
    ownHand : int, enemyHand : int, ownCrowns : int, enemyCrowns : int) : int
{
    if (!reachable) return 1;
    // Losing at 0:1 or 1:1 ends the match. Leading 1:0 is different:
    // round two can be conceded to preserve the hand for the deciding round.
    if (enemyCrowns >= 1) return 0;
    if (cards == 0) return 0;
    if (ownHand - cards < 2 && enemyHand >= 3) return 3;
    if (spent + cards <= 1) return 0;
    if (ownCrowns >= 1 && spent + cards <= 2 && ownHand - cards >= 4 && ownHand - cards - enemyHand >= 1) return 0;
    if (spent + cards <= 2 && ownHand - cards >= 4 && ownHand - cards - enemyHand >= 2) return 0;
    return 2;
}
function BetaGwentAIConcedeOptionalRound(deficit : int, bestTempo : int,
    ownHand : int, enemyHand : int, ownCrowns : int, enemyCrowns : int) : bool
{
    if(enemyCrowns>=1 || deficit<=0 || ownHand>enemyHand || ownHand<2)return false;
    if(ownCrowns>=1 && ownHand<=3 && deficit>Max(10,bestTempo))return true;
    return ownHand<=4 && deficit>Max(18,bestTempo*2);
}
function BetaGwentAIEarlyPass(lead : int, burst : int, leaderBurst : int,
    ownHand : int, enemyHand : int, enemyCrowns : int) : bool
{
    var needed : int;
    if (enemyCrowns >= 1 || lead <= 0 || burst <= 0 || ownHand < 3) return false;
    needed = (Max(0, lead + 1 - leaderBurst) + burst - 1) / burst;
    return needed >= 2 && enemyHand >= needed && ownHand - (enemyHand - needed) >= 1;
}
class CBetaGwentAIChasePlanner extends IScriptable
{
    private function Better(candidate : SBetaGwentAIChasePlan, best : SBetaGwentAIChasePlan) : bool
    {
        if (!best.reachable) return true;
        if (candidate.cards != best.cards) return candidate.cards < best.cards;
        if (candidate.reserve != best.reserve) return candidate.reserve < best.reserve;
        return candidate.gain < best.gain;
    }
    public function Plan(actions : array<SBetaGwentAIChaseAction>, deficit : int) : SBetaGwentAIChasePlan
    {
        var best, candidate : SBetaGwentAIChasePlan;
        var i,j,k,index,total,biggest : int;var used : array<int>;
        // Prefer a cheap direct answer, then evaluate all two-action answers.
        // Re-evaluate after each actual resolution; targets/tutors can change.
        for(i=0;i<actions.Size();i+=1)
        {
            if(actions[i].gain<=0)continue;
            candidate.reachable=true;candidate.firstId=actions[i].id;
            candidate.cards=actions[i].cards;candidate.actions=1;
            candidate.reserve=actions[i].reserve;candidate.gain=actions[i].gain;
            if(candidate.gain>=deficit && Better(candidate,best))best=candidate;
            for(j=i+1;j<actions.Size();j+=1)
            {
                if(actions[j].gain<=0 || actions[i].gain+actions[j].gain<deficit)continue;
                candidate.cards=actions[i].cards+actions[j].cards;candidate.actions=2;
                candidate.reserve=actions[i].reserve+actions[j].reserve;
                candidate.gain=actions[i].gain+actions[j].gain;
                candidate.firstId=actions[i].id;
                if(actions[j].gain>actions[i].gain)candidate.firstId=actions[j].id;
                if(Better(candidate,best))best=candidate;
            }
        }
        if(best.reachable)return best;
        // Only a rough optimistic bound for longer chases, used when the match
        // is at stake. It never authorizes spending three cards in round one.
        for(k=0;k<actions.Size();k+=1)
        {
            biggest=0;index=-1;
            for(i=0;i<actions.Size();i+=1)
                if(!used.Contains(i) && actions[i].gain>biggest){biggest=actions[i].gain;index=i;}
            if(index<0)break;used.PushBack(index);
            if(best.actions==0)best.firstId=actions[index].id;
            best.actions+=1;best.cards+=actions[index].cards;best.reserve+=actions[index].reserve;
            total+=biggest;best.gain=total;
            if(total>=deficit){best.reachable=true;break;}
        }
        return best;
    }
}

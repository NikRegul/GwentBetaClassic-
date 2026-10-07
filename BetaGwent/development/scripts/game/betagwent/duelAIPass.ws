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
// Round economy (AI generation 2). Called only while the opponent has not passed.
// Tunables are fixed here; self-play hosts may override BetaGwentAITune for search.
function BetaGwentAITune(index : int) : int
{
    switch(index)
    {
    case 0: return 6;   // R1: extra lead over one enemy card before passing ahead
    case 1: return 0;   // R1: concede when one card cannot take the lead (0=off, else extra deficit)
    case 2: return 0;   // R2 with a crown: dry pass (0=off, 1=on)
    case 3: return 0;   // R2 with a crown: concede when behind (0=off, 1=on)
    case 4: return 1;   // R1: pass ahead also with more cards than the opponent
    case 5: return 10;  // Generation 3: cards simulated per decision
    case 6: return 3;   // Generation 3 mulligan: required gain of the average deck card
    case 7: return 6;   // Generation 4: follow-up cards checked after each candidate
    case 8: return 5;   // Generation 4: weight of the follow-up uplift (tenths)
    case 9: return 4;   // Generation 4: candidates checked for follow-up uplift
    }
    return 0;
}
// Average public value of an opponent card this round, with a prior of 10.
function BetaGwentAICardValue(points : int, played : int) : int
{ return (Max(0,points)+20)/(Max(0,played)+2); }
// 0 = keep playing; 1 = pass while ahead (opponent must overspend); 2 = concede
// the round to keep cards; 3 = dry pass with the round lead in crowns.
function BetaGwentAIRoundDecision(round : int, ownCrowns : int, enemyCrowns : int, lead : int,
    ownHand : int, enemyHand : int, bestTempo : int, enemyValue : int, enemyLeader : bool) : int
{
    var margin : int;
    if(ownHand==0)return 0;
    margin=enemyValue+BetaGwentAITune(0);if(enemyLeader)margin+=3;
    // Deciding round, or the opponent already holds a crown: every round must be won.
    if(enemyCrowns>=1)return 0;
    if(ownCrowns>=1)
    {
        // We won a round. Make the opponent spend cards for this one.
        if(BetaGwentAITune(2)!=0 && lead>=0 && ownHand+1>=enemyHand)return 3;
        if(BetaGwentAITune(3)!=0 && lead<0 && ownHand>=enemyHand)return 2;
        return 0;
    }
    // First round: win it without falling behind in cards.
    if(lead>0)
    {
        if(ownHand>=enemyHand && lead>=margin)return 1;
        if(BetaGwentAITune(4)!=0 && ownHand>enemyHand && lead>=enemyValue/2+BetaGwentAITune(0)/2)return 1;
        return 0;
    }
    if(bestTempo+lead>0)return 0;
    // One card cannot take the lead: the opponent's last plays outvalue ours.
    if(BetaGwentAITune(1)>0 && ownHand<=enemyHand+1 && -lead>bestTempo+BetaGwentAITune(1) && ownHand>=3)return 2;
    return 0;
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
    // A small lead is vulnerable to an unseen tutor/control gold. Never infer
    // a safe two-card tax from just a low observed opening bronze.
    burst = Max(25, burst);
    needed = (Max(0, lead + 1 - leaderBurst) + burst - 1) / burst;
    return lead >= 26 && needed >= 2 && enemyHand >= needed && ownHand - (enemyHand - needed) >= 2;
}
// Bounded estimate of the actual alternating duel: live power, armor and
// first strike. No state mutation, random choice or enemy-hand information.
function BetaGwentAIDuelSwing(ownPower : int, ownArmor : int, enemyPower : int, enemyArmor : int) : int
{
    var ownStart, enemyStart, strike, armorHit, turn : int;
    ownStart=ownPower;enemyStart=enemyPower;
    while(ownPower>0 && enemyPower>0 && turn<32)
    {
        if(turn%2==0){strike=ownPower;armorHit=Min(enemyArmor,strike);enemyArmor-=armorHit;enemyPower=Max(0,enemyPower-strike+armorHit);}
        else {strike=enemyPower;armorHit=Min(ownArmor,strike);ownArmor-=armorHit;ownPower=Max(0,ownPower-strike+armorHit);}
        turn+=1;
    }
    return enemyStart-enemyPower-(ownStart-ownPower);
}
class CBetaGwentAIChasePlanner extends IScriptable
{
    // BG_CLONE_FIELDS
    public var bgCloneEpoch : int; public var bgCloneRef : IScriptable;
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

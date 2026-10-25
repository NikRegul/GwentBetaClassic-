// A complete, save-backed rotation. Every active archetype appears once per cycle.
// Prefer different factions, leaders and families without weighting away rare decks.
@addField(W3PlayerWitcher)
private saved var betaGwentOpponentBag : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentOpponentRecent : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentOpponentPoolSize : int;

@addMethod(W3PlayerWitcher)
public function BetaGwentNextOpponent() : int
{
    var pool,seen,eligible : array<int>; var i,j,picked,score,best,faction,leader,family,last : int;
    var valid : bool; var p,q : SBetaGwentDuelPreset;
    BetaGwentAIOrdinaryPresets(pool);valid=true;
    // Expand an existing save's partially consumed46-deck cycle immediately.
    if(betaGwentOpponentPoolSize!=pool.Size()){betaGwentOpponentBag.Clear();betaGwentOpponentPoolSize=pool.Size();}
    for(i=0;i<betaGwentOpponentBag.Size();i+=1) {
        picked=betaGwentOpponentBag[i];
        if(!pool.Contains(picked) || seen.Contains(picked))valid=false;
        seen.PushBack(picked);
    }
    if(!valid)betaGwentOpponentBag.Clear();
    if(betaGwentOpponentBag.Size()==0)betaGwentOpponentBag=pool;
    best=-2147483647;last=0;
    if(betaGwentOpponentRecent.Size()>0)last=betaGwentOpponentRecent[betaGwentOpponentRecent.Size()-1];
    for(i=0;i<betaGwentOpponentBag.Size();i+=1) {
        picked=betaGwentOpponentBag[i];p=BetaGwentDuelPreset(picked);
        faction=BetaGwentPresetFaction(picked);leader=p.leaderTemplateId;
        family=BetaGwentAIProfileFamily(BetaGwentAIPresetProfile(picked));score=0;
        if(picked!=last)score+=32;
        if(last==0 || faction!=BetaGwentPresetFaction(last))score+=8;
        for(j=0;j<betaGwentOpponentRecent.Size();j+=1) {
            q=BetaGwentDuelPreset(betaGwentOpponentRecent[j]);
            if(q.leaderTemplateId==leader)score-=4;
            if(BetaGwentAIProfileFamily(BetaGwentAIPresetProfile(q.id))==family)score-=2;
        }
        if(score>best){best=score;eligible.Clear();}
        if(score==best)eligible.PushBack(i);
    }
    i=eligible[RandRange(eligible.Size())];picked=betaGwentOpponentBag[i];betaGwentOpponentBag.Erase(i);
    betaGwentOpponentRecent.PushBack(picked);
    while(betaGwentOpponentRecent.Size()>3)betaGwentOpponentRecent.Erase(0);
    LogChannel('BetaGwent',"DUEL_AI_POOL preset="+picked+" remaining="+betaGwentOpponentBag.Size()+" pool="+pool.Size()+" policy=saved_rotation123");
    return picked;
}

function BetaGwentChooseDiversePreset() : int
{
    var player : W3PlayerWitcher;player=(W3PlayerWitcher)thePlayer;
    if(player)return player.BetaGwentNextOpponent();
    return 54;
}

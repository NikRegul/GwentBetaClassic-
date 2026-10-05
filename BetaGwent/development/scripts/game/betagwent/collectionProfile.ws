// Save-backed Beta ownership. The original game collection and eight deck slots
// stay separate. Unknown schemas are preserved, never silently reinitialized.
@addField(W3PlayerWitcher)
private saved var betaGwentCollectionSchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentOwnedIds : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentOwnedCopies : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentProgressionSeed : int;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardedNpcs : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardedQuests : array<name>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterSetRevision : int;
@addField(W3PlayerWitcher)
private var betaGwentCollectionSeeding : bool;

function BetaGwentCollectionCap(id : int) : int
{
    var d : SBetaGwentDuelDefinition;
    if (BetaGwentDuelIsLeader(id)) return 1;
    if (!BetaGwentDuelCollectible(id)) return 0;
    d=BetaGwentDuelDefinition(id); if(d.header.tierMask==2) return 3; return 1;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentOwned(id : int) : int
{
    var i : int;
    if(betaGwentCollectionSchema!=1 || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size()) return 0;
    for(i=0;i<betaGwentOwnedIds.Size();i+=1) if(betaGwentOwnedIds[i]==id) return betaGwentOwnedCopies[i];
    return 0;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentGrant(id : int) : bool
{
    var i, cap : int;
    cap=BetaGwentCollectionCap(id);
    if(betaGwentCollectionSchema!=1 || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size() || cap==0) return false;
    for(i=0;i<betaGwentOwnedIds.Size();i+=1) if(betaGwentOwnedIds[i]==id) {
        if(betaGwentOwnedCopies[i]>=cap) return false;
        betaGwentOwnedCopies[i]+=1; return true;
    }
    betaGwentOwnedIds.PushBack(id);betaGwentOwnedCopies.PushBack(1);
    if(!betaGwentCollectionSeeding)BetaGwentUpdateCollectionProgress();return true;
}
// Additive starter migration: never removes cards, saved deck slots or reward claims.
@addMethod(W3PlayerWitcher)
private function BetaGwentApplyStarterSet()
{
    var ids : array<int>;var i,j,k,needed : int;var preset : SBetaGwentDuelPreset;
    for(k=16;k<=20;k+=1) {
        preset=BetaGwentDuelPreset(k);BetaGwentGrant(preset.leaderTemplateId);
        BetaGwentDuelPresetDeck(k,ids);
        for(i=0;i<ids.Size();i+=1) {
            needed=0;for(j=0;j<ids.Size();j+=1)if(ids[j]==ids[i])needed+=1;
            while(BetaGwentOwned(ids[i])<needed)if(!BetaGwentGrant(ids[i]))break;
        }
    }
    betaGwentStarterSetRevision=BetaGwentStarterRevision();
    LogChannel('BetaGwent',"STARTER_SET_GRANTED revision="+betaGwentStarterSetRevision+" distinct="+betaGwentOwnedIds.Size());
}
@addMethod(W3PlayerWitcher)
public function BetaGwentEnsureCollection() : bool
{
    var ids : array<int>; var i,j,k,needed,leader,faction : int; var title : string;var preset : SBetaGwentDuelPreset;var validation : SBetaGwentDeckValidation;
    if(betaGwentCollectionSchema!=0) {
        if(betaGwentCollectionSchema!=1 || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size())return false;
        if(!betaGwentCollectionSeeding) {
            // Paid offers retain their reservation until the player chooses.
            if(betaGwentStarterSetRevision<BetaGwentStarterRevision() && !BetaGwentKegPending()) {
                betaGwentCollectionSeeding=true;BetaGwentApplyStarterSet();betaGwentCollectionSeeding=false;
            }
            BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();
        }return true;
    }
    if(betaGwentOwnedIds.Size()!=0 || betaGwentOwnedCopies.Size()!=0) return false;
    betaGwentCollectionSeeding=true;betaGwentCollectionSchema=1;
    BetaGwentApplyStarterSet();
    // One-time migration of valid saved DEV decks, preserving existing work.
    for(k=1;k<=8;k+=1) if(BetaGwentLoadDeck(k,ids,title,faction,leader)) {
        validation=BetaGwentValidateDeck(ids,faction,leader);if(!validation.valid)continue;
        BetaGwentGrant(leader);
        for(i=0;i<ids.Size();i+=1) {
            needed=0;for(j=0;j<ids.Size();j+=1) if(ids[j]==ids[i])needed+=1;
            while(BetaGwentOwned(ids[i])<needed) if(!BetaGwentGrant(ids[i]))break;
        }
    }
    betaGwentCollectionSeeding=false;BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();
    LogChannel('BetaGwent',"COLLECTION_INITIALIZED schema=1 starters=5 distinct="+betaGwentOwnedIds.Size());return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentOwnsDeck(ids : array<int>, leader : int) : bool
{
    var i,j,count : int;
    if(!BetaGwentEnsureCollection() || BetaGwentOwned(leader)<1) return false;
    for(i=0;i<ids.Size();i+=1) {
        count=0;for(j=0;j<ids.Size();j+=1)if(ids[j]==ids[i])count+=1;
        if(count>BetaGwentOwned(ids[i])) return false;
    }
    return true;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentProgressionPick(maximum : int) : int
{
    var next : int;
    // Park-Miller/Schrage, positive31-bit arithmetic, no match/presentation RNG.
    if(betaGwentProgressionSeed<=0)betaGwentProgressionSeed=RandRange(1000000)+1;
    next=16807*(betaGwentProgressionSeed%127773)-2836*(betaGwentProgressionSeed/127773);
    if(next<=0)next+=2147483647;betaGwentProgressionSeed=next;
    if(maximum<=0)return 0;return next%maximum;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentWinReward(deck : name, npcId : int) : string
{
    var ids,pool : array<int>;var i,id,gold,rewarded : int;var d : SBetaGwentDuelDefinition;
    if(!BetaGwentEnsureCollection())return "Коллекция недоступна: неизвестная схема сохранения.";
    gold=BetaGwentQuestGold(deck);
    if(gold!=0) {
        if(betaGwentRewardedQuests.Contains(deck))return "Квестовая награда от этого игрока уже получена.";
        betaGwentRewardedQuests.PushBack(deck);
        d=BetaGwentDuelDefinition(gold);
        if(BetaGwentGrant(gold)) {
            LogChannel('BetaGwent',"COLLECTION_REWARD quest="+deck+" card="+gold);
            return "Новая золотая карта: "+d.title;
        }
        AddMoney(300);LogChannel('BetaGwent',"COLLECTION_REWARD quest="+deck+" duplicateGold="+gold+" crowns=300");
        return "Золотая карта уже есть в коллекции. Награда:300 крон.";
    }
    if(npcId==0) {
        LogChannel('BetaGwent',"COLLECTION_REWARD_DEFERRED npc="+deck+" reason=missingActorIdentity");
        return "Не удалось определить персонажа для первой награды.";
    }
    // Each saved occurrence is one rewarded win. Old saves contain one occurrence.
    for(i=0;i<betaGwentRewardedNpcs.Size();i+=1)if(betaGwentRewardedNpcs[i]==npcId)rewarded+=1;
    if(rewarded>=4)return "Все четыре награды этого игрока уже получены.";
    BetaGwentDuelCollection(ids);
    for(i=0;i<ids.Size();i+=1) {
        d=BetaGwentDuelDefinition(ids[i]);
        if((d.header.tierMask==2 || d.header.tierMask==4) && BetaGwentOwned(ids[i])<BetaGwentCollectionCap(ids[i]))pool.PushBack(ids[i]);
    }
    if(pool.Size()==0)return "Все бронзовые и серебряные карты уже собраны.";
    id=pool[BetaGwentProgressionPick(pool.Size())];if(!BetaGwentGrant(id))return "Награда уже получена.";
    betaGwentRewardedNpcs.PushBack(npcId);
    d=BetaGwentDuelDefinition(id);LogChannel('BetaGwent',"COLLECTION_REWARD npc="+deck+" card="+id+" copies="+BetaGwentOwned(id)+" rewardedWins="+(rewarded+1));
    return "Новая карта: "+d.title+" ("+BetaGwentOwned(id)+"/"+BetaGwentCollectionCap(id)+") · Награда "+(rewarded+1)+"/4";
}

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
private saved var betaGwentRewardActors : array<EntityHandle>;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardActorWins : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardedQuests : array<name>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterSetRevision : int;
@addField(W3PlayerWitcher)
private var betaGwentCollectionSeeding : bool;
// Independent additive save extension: ownership schema 1 remains unchanged.
@addField(W3PlayerWitcher)
private saved var betaGwentNewCardsSchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentNewCardIds : array<int>;

@addMethod(W3PlayerWitcher)
private function BetaGwentEnsureNewCards()
{
    // Existing collections have no unseen cards on their first upgraded load.
    if(betaGwentNewCardsSchema==0 && betaGwentNewCardIds.Size()==0)betaGwentNewCardsSchema=1;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCardIsNew(id : int) : bool
{ return betaGwentNewCardsSchema==1 && betaGwentNewCardIds.Contains(id) && BetaGwentOwned(id)>0; }
@addMethod(W3PlayerWitcher)
private function BetaGwentMarkNewCard(id : int)
{
    BetaGwentEnsureNewCards();
    if(!betaGwentCollectionSeeding && betaGwentNewCardsSchema==1 && BetaGwentOwned(id)>0 && !betaGwentNewCardIds.Contains(id))betaGwentNewCardIds.PushBack(id);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCardSeen(id : int) : bool
{
    var at : int;
    if(betaGwentNewCardsSchema!=1 || BetaGwentOwned(id)<1)return false;
    at=betaGwentNewCardIds.FindFirst(id);if(at<0)return false;
    betaGwentNewCardIds.Erase(at);return true;
}

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
        betaGwentOwnedCopies[i]+=1;BetaGwentMarkNewCard(id);return true;
    }
    betaGwentOwnedIds.PushBack(id);betaGwentOwnedCopies.PushBack(1);BetaGwentMarkNewCard(id);
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
            BetaGwentEnsureNewCards();
            // Paid offers retain their reservation until the player chooses.
            if(betaGwentStarterSetRevision<BetaGwentStarterRevision() && !BetaGwentKegPending()) {
                betaGwentCollectionSeeding=true;BetaGwentApplyStarterSet();betaGwentCollectionSeeding=false;
            }
            BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();
        }return true;
    }
    if(betaGwentOwnedIds.Size()!=0 || betaGwentOwnedCopies.Size()!=0) return false;
    // Profile fields lost by a save made without the mod: restore from the facts mirror.
    if(BetaGwentRestoreProfile()){BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();return true;}
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
    betaGwentCollectionSeeding=false;BetaGwentEnsureNewCards();BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();
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
public function BetaGwentWinReward(deck : name, npcId : int, optional actorKey : int) : string
{
    var ids,pool : array<int>;var i,id,gold,rewarded,scraps : int;var d : SBetaGwentDuelDefinition;
    if(!BetaGwentEnsureCollection())return "Коллекция недоступна: неизвестная схема сохранения.";
    gold=BetaGwentQuestGold(deck);
    if(gold!=0) {
        // Repeat wins against quest and tournament players: +50 scraps.
        // Stage 136: the facts mirror also counts, so a restored profile is not paid twice.
        if(betaGwentRewardedQuests.Contains(deck) || BetaGwentMirroredQuestReward(deck)){
            if(!betaGwentRewardedQuests.Contains(deck))betaGwentRewardedQuests.PushBack(deck);
            BetaGwentAddScraps(50);return "Победа: +50 осколков (всего "+BetaGwentScraps()+").";}
        betaGwentRewardedQuests.PushBack(deck);BetaGwentMirrorQuestReward(deck);
        d=BetaGwentDuelDefinition(gold);
        if(BetaGwentGrant(gold)) {
            LogChannel('BetaGwent',"COLLECTION_REWARD quest="+deck+" card="+gold);
            return "Новая золотая карта: "+d.title;
        }
        scraps=BetaGwentReceive(gold);LogChannel('BetaGwent',"COLLECTION_REWARD quest="+deck+" duplicateGold="+gold+" scraps="+scraps);
        return "Золотая карта уже есть в коллекции: +"+scraps+" осколков (всего "+BetaGwentScraps()+").";
    }
    if(npcId==0) {
        LogChannel('BetaGwent',"COLLECTION_REWARD_DEFERRED npc="+deck+" reason=missingActorIdentity");
        BetaGwentAddScraps(20);return "Победа: +20 осколков (всего "+BetaGwentScraps()+").";
    }
    // EntityHandle is the engine's save-backed entity reference. A runtime
    // GuidHash is only a legacy migration key, never the new actor identity.
    if(actorKey<=0 || actorKey>betaGwentRewardActorWins.Size() || betaGwentRewardActors.Size()!=betaGwentRewardActorWins.Size()) {
        LogChannel('BetaGwent',"COLLECTION_REWARD_DEFERRED npc="+npcId+" reason=missingPersistentActor");
        BetaGwentAddScraps(20);return "Победа: +20 осколков (всего "+BetaGwentScraps()+").";
    }
    rewarded=betaGwentRewardActorWins[actorKey-1];
    // After the four card rewards every further win is worth 20 scraps.
    if(rewarded>=4){BetaGwentAddScraps(20);return "Победа: +20 осколков (всего "+BetaGwentScraps()+").";}
    BetaGwentDuelCollection(ids);
    for(i=0;i<ids.Size();i+=1) {
        d=BetaGwentDuelDefinition(ids[i]);
        // Beta economy: duplicates can drop; a copy above the limit becomes scraps.
        if(d.header.tierMask==2 || d.header.tierMask==4)pool.PushBack(ids[i]);
    }
    if(pool.Size()==0)return "Награда недоступна.";
    id=pool[BetaGwentProgressionPick(pool.Size())];scraps=BetaGwentReceive(id);
    betaGwentRewardedNpcs.PushBack(npcId);
    betaGwentRewardActorWins[actorKey-1]=Min(4,rewarded+1);BetaGwentMirrorNpcWins(npcId,betaGwentRewardActorWins[actorKey-1]);
    LogChannel('BetaGwent',"COLLECTION_REWARD_COUNTER actorKey="+actorKey+" runtimeId="+npcId+" wins="+betaGwentRewardActorWins[actorKey-1]);
    d=BetaGwentDuelDefinition(id);
    if(scraps>0){LogChannel('BetaGwent',"COLLECTION_REWARD npc="+deck+" card="+id+" duplicateScraps="+scraps+" rewardedWins="+(rewarded+1));
        return "Дубль: "+d.title+" → +"+scraps+" осколков (всего "+BetaGwentScraps()+") · Награда "+(rewarded+1)+"/4";}
    d=BetaGwentDuelDefinition(id);LogChannel('BetaGwent',"COLLECTION_REWARD npc="+deck+" card="+id+" copies="+BetaGwentOwned(id)+" rewardedWins="+(rewarded+1));
    return "Новая карта: "+d.title+" ("+BetaGwentOwned(id)+"/"+BetaGwentCollectionCap(id)+") · Награда "+(rewarded+1)+"/4";
}

@addMethod(W3PlayerWitcher)
public function BetaGwentRewardActorKey(actor : CEntity) : int
{
    var i,legacyWins,runtimeId : int;var handle : EntityHandle;
    if(!actor || betaGwentRewardActors.Size()!=betaGwentRewardActorWins.Size())return 0;
    for(i=0;i<betaGwentRewardActors.Size();i+=1)
        if(EntityHandleGet(betaGwentRewardActors[i])==actor)return i+1;
    runtimeId=actor.GetGuidHash();
    // Carry forward old recorded wins when their original identity is available.
    // Never clear this legacy ledger or rebuild counts on loading a save.
    for(i=0;i<betaGwentRewardedNpcs.Size();i+=1)
        if(betaGwentRewardedNpcs[i]==runtimeId)legacyWins+=1;
    // After a restore from the facts mirror the saved ledger is gone; use the mirrored count.
    legacyWins=Max(legacyWins,BetaGwentMirroredNpcWins(runtimeId));
    EntityHandleSet(handle,actor);betaGwentRewardActors.PushBack(handle);
    betaGwentRewardActorWins.PushBack(Min(4,legacyWins));
    LogChannel('BetaGwent',"COLLECTION_REWARD_ACTOR key="+betaGwentRewardActors.Size()+" runtimeId="+runtimeId+" migratedWins="+Min(4,legacyWins));
    return betaGwentRewardActors.Size();
}

// Debug acquisition uses normal collection caps without spending or rewarding.
@addMethod(W3PlayerWitcher)
public function BetaGwentGrantAllCards() : int
{
    var ids, leaders, received : array<int>;var i,id,total : int;
    if(!BetaGwentEnsureCollection())return -1;
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    for(i=0;i<leaders.Size();i+=1)if(!ids.Contains(leaders[i]))ids.PushBack(leaders[i]);
    betaGwentCollectionSeeding=true;
    for(i=0;i<ids.Size();i+=1){id=ids[i];
        while(BetaGwentOwned(id)<BetaGwentCollectionCap(id)){
            if(!BetaGwentGrant(id))break;
            total+=1;if(!received.Contains(id))received.PushBack(id);
        }
    }
    betaGwentCollectionSeeding=false;
    for(i=0;i<received.Size();i+=1)BetaGwentMarkNewCard(received[i]);
    BetaGwentUpdateCollectionProgress();BetaGwentSyncTournamentAccess();BetaGwentBackupProfile();
    LogChannel('BetaGwent',"COLLECTION_DEBUG_ALL granted="+total+" distinct="+betaGwentOwnedIds.Size());return total;
}

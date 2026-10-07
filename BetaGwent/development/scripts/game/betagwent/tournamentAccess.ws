// The native quests used weighted legacy-card tags. Beta admission uses a
// valid owned25-card deck. Stakes, scripted rounds and quest outputs stay native.
function BetaGwentSetAdmissionFact(fact : string, enabled : bool)
{
    if(enabled && !FactsDoesExist(fact))FactsAdd(fact,1,-1);
    if(!enabled && FactsDoesExist(fact))FactsRemove(fact);
}
@addMethod(W3PlayerWitcher)
private function BetaGwentStarterReady(presetId : int) : bool
{
    var ids : array<int>;var i,j,count : int;var p : SBetaGwentDuelPreset;var d : SBetaGwentDuelDefinition;var validation : SBetaGwentDeckValidation;
    p=BetaGwentDuelPreset(presetId);if(BetaGwentOwned(p.leaderTemplateId)<1)return false;
    if(!BetaGwentDuelPresetDeck(presetId,ids))return false;
    d=BetaGwentDuelDefinition(p.leaderTemplateId);validation=BetaGwentValidateDeck(ids,d.header.factionMask,p.leaderTemplateId);
    if(!validation.valid)return false;
    for(i=0;i<ids.Size();i+=1) {
        count=0;for(j=0;j<ids.Size();j+=1)if(ids[j]==ids[i])count+=1;
        if(BetaGwentOwned(ids[i])<count)return false;
    }
    return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentSyncTournamentAccess()
{
    var anyDeck,skelligeDeck : bool;var i : int;
    if(betaGwentCollectionSchema!=1 || betaGwentCollectionSeeding || betaGwentOwnedIds.Size()!=betaGwentOwnedCopies.Size())return;
    // A starter-ready collection cannot lose copies in the current economy.
    // Cached readiness avoids revalidating five decks on every menu/award call.
    if(FactsDoesExist("betagwent_tournament_access_ready")) {
        BetaGwentSetAdmissionFact("HasGwentTournamentDeck",true);
        BetaGwentSetAdmissionFact("HasEP2TournamentDeck",true);
        BetaGwentSetAdmissionFact("GwentTournamentObjective1",true);BetaGwentSetAdmissionFact("GwentTournamentObjective2",true);
        BetaGwentSetAdmissionFact("GwentTournamentObjective3",true);BetaGwentSetAdmissionFact("GwentTournamentObjective4",true);
        BetaGwentSetAdmissionFact("EP2TournamentObjective1",true);BetaGwentSetAdmissionFact("EP2TournamentObjective2",true);
        BetaGwentSetAdmissionFact("EP2TournamentObjective3",true);BetaGwentSetAdmissionFact("EP2TournamentObjective4",true);return;
    }
    for(i=16;i<=20;i+=1)if(BetaGwentStarterReady(i)){anyDeck=true;if(i==20)skelligeDeck=true;}
    BetaGwentSetAdmissionFact("HasGwentTournamentDeck",anyDeck);
    BetaGwentSetAdmissionFact("HasEP2TournamentDeck",skelligeDeck);
    if(anyDeck) {
        BetaGwentSetAdmissionFact("GwentTournamentObjective1",true);BetaGwentSetAdmissionFact("GwentTournamentObjective2",true);
        BetaGwentSetAdmissionFact("GwentTournamentObjective3",true);BetaGwentSetAdmissionFact("GwentTournamentObjective4",true);
    }
    if(skelligeDeck) {
        BetaGwentSetAdmissionFact("EP2TournamentObjective1",true);BetaGwentSetAdmissionFact("EP2TournamentObjective2",true);
        BetaGwentSetAdmissionFact("EP2TournamentObjective3",true);BetaGwentSetAdmissionFact("EP2TournamentObjective4",true);
    }
    if(anyDeck && skelligeDeck)FactsAdd("betagwent_tournament_access_ready",1,-1);
}
@wrapMethod(W3PlayerWitcher)
function CheckGwentTournamentDeck()
{
    wrappedMethod();if(BetaGwentEnsureCollection())BetaGwentSyncTournamentAccess();
}
@wrapMethod(W3PlayerWitcher)
function CheckEP2TournamentDeck()
{
    wrappedMethod();if(BetaGwentEnsureCollection())BetaGwentSyncTournamentAccess();
}

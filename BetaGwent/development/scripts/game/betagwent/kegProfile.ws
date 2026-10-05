// Closed kegs live in the native inventory. Consume one only when opening.
// Persist the automatic cards and distinct rare offers; resuming never consumes
// another keg or rerolls the paid choice. Legacy paid openings remain valid.
class CBetaGwentKegMenuData extends IScriptable {}
@addField(W3PlayerWitcher)
private saved var betaGwentKegAutomatic : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentKegOffers : array<int>;

@addMethod(W3PlayerWitcher)
public function BetaGwentKegPending() : bool { return betaGwentKegOffers.Size()>0; }
@addMethod(W3PlayerWitcher)
public function BetaGwentKegContents(out ordinary : array<int>, out offers : array<int>)
{ ordinary=betaGwentKegAutomatic;offers=betaGwentKegOffers; }
@addMethod(W3PlayerWitcher)
public function BetaGwentKegRareRemaining() : int
{
    var ids,leaders : array<int>;var i,count : int;var d : SBetaGwentDuelDefinition;
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    for(i=0;i<leaders.Size();i+=1)ids.PushBack(leaders[i]);
    for(i=0;i<ids.Size();i+=1) {
        d=BetaGwentDuelDefinition(ids[i]);
        if((d.header.tierMask==4 || d.header.tierMask==8 || d.header.tierMask==1) && BetaGwentOwned(ids[i])<BetaGwentCollectionCap(ids[i]))count+=1;
    }
    return count;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentKegPurchaseCapacity() : int
{
    var remaining : int;
    if(!BetaGwentEnsureCollection())return 0;
    remaining=BetaGwentKegRareRemaining()-inv.GetItemQuantityByName('betagwent_keg');
    if(BetaGwentKegPending())remaining-=1;
    if(remaining<0)return 0;return remaining;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentOpenInventoryKeg(item : SItemUniqueId) : bool
{
    var ids,leaders,pool,automatic,offers,silvers,golds : array<int>;
    var i,j,k,id,reserved : int;var d : SBetaGwentDuelDefinition;
    if(!BetaGwentEnsureCollection())return false;
    if(BetaGwentKegPending())return true;
    if(!inv || !inv.IsIdValid(item) || inv.GetItemName(item)!='betagwent_keg' || inv.GetItemQuantity(item)<1)return false;
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    for(k=0;k<4;k+=1) {
        pool.Clear();
        for(i=0;i<ids.Size();i+=1) {
            d=BetaGwentDuelDefinition(ids[i]);if(d.header.tierMask!=2)continue;
            reserved=0;for(j=0;j<automatic.Size();j+=1)if(automatic[j]==ids[i])reserved+=1;
            if(BetaGwentOwned(ids[i])+reserved<3)pool.PushBack(ids[i]);
        }
        // When bronze is exhausted, the paid rare choice remains available.
        // Never manufacture duplicates to fill the four ordinary positions.
        if(pool.Size()==0)break;
        automatic.PushBack(pool[BetaGwentProgressionPick(pool.Size())]);
    }
    for(i=0;i<leaders.Size();i+=1)ids.PushBack(leaders[i]);
    for(i=0;i<ids.Size();i+=1) {
        d=BetaGwentDuelDefinition(ids[i]);if(BetaGwentOwned(ids[i])>=BetaGwentCollectionCap(ids[i]))continue;
        if(d.header.tierMask==4)silvers.PushBack(ids[i]);
        else if(d.header.tierMask==8 || d.header.tierMask==1)golds.PushBack(ids[i]);
    }
    if(silvers.Size()+golds.Size()==0)return false;
    for(k=0;k<3;k+=1) {
        if(silvers.Size()+golds.Size()==0)break;
        if(silvers.Size()>0 && (golds.Size()==0 || BetaGwentProgressionPick(2)==0)) {
            i=BetaGwentProgressionPick(silvers.Size());id=silvers[i];silvers.Erase(i);
        }else { i=BetaGwentProgressionPick(golds.Size());id=golds[i];golds.Erase(i); }
        offers.PushBack(id);
    }
    // No latent call between consuming the physical keg, reservation and grants.
    if(!inv.RemoveItem(item,1))return false;
    betaGwentKegAutomatic=automatic;betaGwentKegOffers=offers;
    for(i=0;i<automatic.Size();i+=1)BetaGwentGrant(automatic[i]);
    LogChannel('BetaGwent',"KEG_OPENED consumed=1 ordinary="+automatic.Size()+" offers="+offers.Size());return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentChooseKeg(id : int) : bool
{
    if(!betaGwentKegOffers.Contains(id) || !BetaGwentGrant(id))return false;
    betaGwentKegOffers.Clear();betaGwentKegAutomatic.Clear();
    LogChannel('BetaGwent',"KEG_CHOSEN card="+id);return true;
}

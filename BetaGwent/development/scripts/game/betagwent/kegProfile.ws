// Stage 110: closed kegs are a counter in the save, not inventory items. The 5.0 engine
// drops Geralt's ENTIRE inventory on load if one saved item has no definition, so a
// mod-only item in his inventory would wipe it if the mod is ever removed. Kegs bought
// with older versions are moved from the inventory into the counter on load.
// Consume one only when opening.
// Persist the automatic cards and distinct rare offers; resuming never consumes
// another keg or rerolls the paid choice. Legacy paid openings remain valid.
class CBetaGwentKegMenuData extends IScriptable {}
@addField(W3PlayerWitcher)
private saved var betaGwentKegAutomatic : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentKegOffers : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentKegAutomaticScraps : array<int>;

@addField(W3PlayerWitcher)
private saved var betaGwentKegsUnopened : int;

@addMethod(W3PlayerWitcher)
public function BetaGwentKegPending() : bool { return betaGwentKegOffers.Size()>0; }
@addMethod(W3PlayerWitcher)
public function BetaGwentKegCount() : int { BetaGwentMigrateInventoryKegs(); return betaGwentKegsUnopened; }
@addMethod(W3PlayerWitcher)
public function BetaGwentAddKegs(count : int) { if(count>0)betaGwentKegsUnopened+=count; }
@addMethod(W3PlayerWitcher)
public function BetaGwentMigrateInventoryKegs()
{
    var items : array<SItemUniqueId>;var i,quantity,moved : int;
    if(!inv)return;
    quantity=inv.GetItemQuantityByName('betagwent_keg');if(quantity<=0)return;
    inv.GetAllItems(items);
    for(i=0;i<items.Size();i+=1)if(inv.GetItemName(items[i])=='betagwent_keg') {
        quantity=inv.GetItemQuantity(items[i]);
        if(quantity>0 && inv.RemoveItem(items[i],quantity)){betaGwentKegsUnopened+=quantity;moved+=quantity;}
    }
    if(moved>0)LogChannel('BetaGwent',"KEG_INVENTORY_MIGRATED kegs="+moved+" unopened="+betaGwentKegsUnopened);
}
@wrapMethod(W3PlayerWitcher)
function OnSpawned(spawnData : SEntitySpawnData)
{
    wrappedMethod(spawnData);
    BetaGwentMigrateInventoryKegs();
}
@addMethod(W3PlayerWitcher)
public function BetaGwentKegContents(out ordinary : array<int>, out offers : array<int>)
{ ordinary=betaGwentKegAutomatic;offers=betaGwentKegOffers; }
@addMethod(W3PlayerWitcher)
public function BetaGwentKegReceivedScraps(index : int) : int
{
    // Older paid openings did not record per-card results; do not invent them.
    if(index<0 || index>=betaGwentKegAutomaticScraps.Size())return -1;
    return betaGwentKegAutomaticScraps[index];
}
@addMethod(W3PlayerWitcher)
public function BetaGwentKegRareRemaining() : int
{
    // Duplicates are allowed (Beta economy): extra copies turn into scraps, so a keg never runs dry.
    var ids,leaders : array<int>;var i,count : int;var d : SBetaGwentDuelDefinition;
    BetaGwentDuelCollection(ids);BetaGwentDuelLeaders(leaders);
    count=leaders.Size();
    for(i=0;i<ids.Size();i+=1){d=BetaGwentDuelDefinition(ids[i]);if(d.header.tierMask==4 || d.header.tierMask==8)count+=1;}
    return count;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentKegPurchaseCapacity() : int
{
    if(!BetaGwentEnsureCollection())return 0;
    return 99;
}
// Rarity of one keg position: 1 common, 2 rare, 4 epic, 8 legendary.
@addMethod(W3PlayerWitcher)
private function BetaGwentKegRoll(offer : bool) : int
{
    var roll : int;roll=BetaGwentProgressionPick(1000);
    if(offer){if(roll<100)return 8;if(roll<400)return 4;return 2;}
    if(roll<20)return 8;if(roll<80)return 4;if(roll<300)return 2;return 1;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentKegPool(rarity : int, out pool : array<int>)
{
    var ids,leaders : array<int>;var i : int;
    pool.Clear();BetaGwentDuelCollection(ids);
    if(rarity==8){BetaGwentDuelLeaders(leaders);for(i=0;i<leaders.Size();i+=1)pool.PushBack(leaders[i]);}
    for(i=0;i<ids.Size();i+=1)if(BetaGwentCardRarity(ids[i])==rarity)pool.PushBack(ids[i]);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentOpenKeg() : bool
{
    var pool,automatic,offers : array<int>;
    var i,k,id,rarity,scraps : int;
    if(!BetaGwentEnsureCollection())return false;
    if(BetaGwentKegPending())return true;
    BetaGwentMigrateInventoryKegs();
    if(betaGwentKegsUnopened<1)return false;
    // Beta keg: four cards with a chance of higher rarity, then a choice of three of one rarity (rare or better).
    for(k=0;k<4;k+=1){BetaGwentKegPool(BetaGwentKegRoll(false),pool);if(pool.Size()>0)automatic.PushBack(pool[BetaGwentProgressionPick(pool.Size())]);}
    rarity=BetaGwentKegRoll(true);BetaGwentKegPool(rarity,pool);
    for(k=0;k<3 && pool.Size()>0;k+=1){i=BetaGwentProgressionPick(pool.Size());offers.PushBack(pool[i]);pool.Erase(i);}
    if(offers.Size()==0)return false;
    // No latent call between consuming the keg, reservation and grants.
    betaGwentKegsUnopened-=1;
    betaGwentKegAutomatic=automatic;betaGwentKegOffers=offers;
    betaGwentKegAutomaticScraps.Clear();
    for(i=0;i<automatic.Size();i+=1){id=BetaGwentReceive(automatic[i]);betaGwentKegAutomaticScraps.PushBack(id);scraps+=id;}
    LogChannel('BetaGwent',"KEG_OPENED consumed=1 ordinary="+automatic.Size()+" offers="+offers.Size()+" offerRarity="+rarity+" duplicateScraps="+scraps);return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentChooseKeg(id : int) : bool
{
    if(!betaGwentKegOffers.Contains(id))return false;
    BetaGwentReceive(id);
    betaGwentKegOffers.Clear();betaGwentKegAutomatic.Clear();betaGwentKegAutomaticScraps.Clear();
    LogChannel('BetaGwent',"KEG_CHOSEN card="+id);return true;
}

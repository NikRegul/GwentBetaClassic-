// Card scraps (Beta 0.9.24 economy). Rarity comes from the original Beta catalog:
// bronze is common or rare, silver epic, gold and leaders legendary.
// Prices from the Beta price list: craft 30/80/200/800, mill 10/20/50/200.
// Copies above the deck limit are milled automatically when received.
@addField(W3PlayerWitcher)
private saved var betaGwentScraps : int;

function BetaGwentRareBronze(id : int) : bool
{
    return id == 113204 || id == 113307 || id == 113308 || id == 113319 || id == 113320 || id == 122302 || id == 122304 || id == 122307 || id == 122309 || id == 122311 || id == 122313 || id == 122314 || id == 122316 || id == 122317 || id == 122403 || id == 132201 || id == 132211 || id == 132212 || id == 132302 || id == 132305 || id == 132308 || id == 132313 || id == 132315 || id == 132402 || id == 132407 || id == 132409 || id == 133301 || id == 142302 || id == 142304 || id == 142306 || id == 142307 || id == 142308 || id == 142309 || id == 142312 || id == 142315 || id == 142317 || id == 152210 || id == 152301 || id == 152304 || id == 152306 || id == 152307 || id == 152310 || id == 152312 || id == 152314 || id == 152316 || id == 152318 || id == 153301 || id == 162301 || id == 162303 || id == 162304 || id == 162307 || id == 162309 || id == 162311 || id == 162313 || id == 162314 || id == 200008 || id == 200009 || id == 200021 || id == 200026 || id == 200033 || id == 200036 || id == 200037 || id == 200038 || id == 200039 || id == 200040 || id == 200042 || id == 200044 || id == 200046 || id == 200048 || id == 200049 || id == 200067 || id == 200081 || id == 200105 || id == 200112 || id == 200114 || id == 200115 || id == 200118 || id == 200124 || id == 200132 || id == 200135 || id == 200136 || id == 200138 || id == 200139 || id == 200144 || id == 200145 || id == 200146 || id == 200149 || id == 200224 || id == 200233 || id == 200293 || id == 200294 || id == 200295 || id == 200296 || id == 200299 || id == 200300 || id == 200301 || id == 200518 || id == 200519 || id == 200528 || id == 200535 || id == 200539 || id == 200540 || id == 201559 || id == 201578 || id == 201598 || id == 201599 || id == 201600 || id == 201606 || id == 201609 || id == 201610 || id == 201612 || id == 201616 || id == 201617 || id == 201619 || id == 201622 || id == 201624 || id == 201625 || id == 201628 || id == 201630 || id == 201631 || id == 201633 || id == 201636 || id == 201638 || id == 201643 || id == 201645 || id == 201647 || id == 201656 || id == 201659 || id == 201661 || id == 201700 || id == 201701 || id == 201744 || id == 201749 || id == 201753;
}
function BetaGwentCardRarity(id : int) : int
{
    var d : SBetaGwentDuelDefinition;
    if (BetaGwentDuelIsLeader(id)) return 8;
    d = BetaGwentDuelDefinition(id);
    if (d.header.tierMask == 8) return 8;
    if (d.header.tierMask == 4) return 4;
    if (BetaGwentRareBronze(id)) return 2;
    return 1;
}
function BetaGwentCraftCost(id : int) : int
{
    switch (BetaGwentCardRarity(id)) { case 8: return 800; case 4: return 200; case 2: return 80; }
    return 30;
}
function BetaGwentMillValue(id : int) : int
{
    switch (BetaGwentCardRarity(id)) { case 8: return 200; case 4: return 50; case 2: return 20; }
    return 10;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentScraps() : int { if (betaGwentScraps < 0) return 0; return betaGwentScraps; }
@addMethod(W3PlayerWitcher)
public function BetaGwentAddScraps(amount : int)
{
    betaGwentScraps = Max(0, betaGwentScraps + amount);
    LogChannel('BetaGwent', "SCRAPS change=" + amount + " total=" + betaGwentScraps);
}
// A received card: added to the collection, or milled when the copy limit is already reached.
// Returns the scraps gained (0 when the card was added).
@addMethod(W3PlayerWitcher)
public function BetaGwentReceive(id : int) : int
{
    var value : int;
    if (BetaGwentGrant(id)) return 0;
    if (BetaGwentCollectionCap(id) == 0) return 0;
    value = BetaGwentMillValue(id); BetaGwentAddScraps(value);
    LogChannel('BetaGwent', "COLLECTION_DUPLICATE card=" + id + " scraps=" + value);
    return value;
}
// Copies the saved deck slots need, so milling never breaks a saved deck.
@addMethod(W3PlayerWitcher)
public function BetaGwentDeckNeed(id : int) : int
{
    var ids : array<int>; var title : string; var faction, leader, k, i, count, need : int;
    for (k = 1; k <= 8; k += 1)
    {
        if (!BetaGwentLoadDeck(k, ids, title, faction, leader)) continue;
        count = 0; if (leader == id) count = 1;
        for (i = 0; i < ids.Size(); i += 1) if (ids[i] == id) count += 1;
        need = Max(need, count);
    }
    return need;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCanCraft(id : int) : bool
{
    if (!BetaGwentEnsureCollection()) return false;
    return BetaGwentCollectionCap(id) > 0 && BetaGwentOwned(id) < BetaGwentCollectionCap(id) && BetaGwentScraps() >= BetaGwentCraftCost(id);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCraft(id : int) : bool
{
    var cost : int;
    if (!BetaGwentCanCraft(id)) return false;
    cost = BetaGwentCraftCost(id);
    if (!BetaGwentGrant(id)) return false;
    BetaGwentAddScraps(-cost);
    LogChannel('BetaGwent', "COLLECTION_CRAFT card=" + id + " cost=" + cost + " copies=" + BetaGwentOwned(id));
    return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentCanMill(id : int) : bool
{
    if (!BetaGwentEnsureCollection()) return false;
    // Only spare copies: a full set (3 bronze, 1 silver, 1 gold or leader) always stays.
    return BetaGwentOwned(id) > Max(BetaGwentCollectionCap(id), BetaGwentDeckNeed(id));
}
@addMethod(W3PlayerWitcher)
public function BetaGwentMill(id : int) : bool
{
    var i, value : int;
    if (!BetaGwentCanMill(id)) return false;
    for (i = 0; i < betaGwentOwnedIds.Size(); i += 1) if (betaGwentOwnedIds[i] == id)
    {
        betaGwentOwnedCopies[i] -= 1;
        if (betaGwentOwnedCopies[i] <= 0) { betaGwentOwnedIds.Erase(i); betaGwentOwnedCopies.Erase(i); }
        value = BetaGwentMillValue(id); BetaGwentAddScraps(value);
        BetaGwentUpdateCollectionProgress();
        LogChannel('BetaGwent', "COLLECTION_MILL card=" + id + " scraps=" + value + " copies=" + BetaGwentOwned(id));
        return true;
    }
    return false;
}

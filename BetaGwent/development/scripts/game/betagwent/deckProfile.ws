// Separate saved profile fields: no changes to vanilla Gwent collection/decks.
// Eight slots,40 template IDs per slot; shape checked before every read/write.
@addField(W3PlayerWitcher)
private saved var betaGwentDeckSchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckNames : array<string>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckLeaders : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckFactions : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckLengths : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckCards : array<int>;

@addMethod(W3PlayerWitcher)
private function BetaGwentDeckProfileValid() : bool
{
    return betaGwentDeckSchema == 1 && betaGwentDeckNames.Size() == 8 && betaGwentDeckLeaders.Size() == 8
        && betaGwentDeckFactions.Size() == 8 && betaGwentDeckLengths.Size() == 8 && betaGwentDeckCards.Size() == 320;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentLoadDeck(slot : int, out cards : array<int>, out title : string, out faction : int, out leader : int) : bool
{
    var i, length, index : int;
    cards.Clear(); if (slot < 1 || slot > 8 || !BetaGwentDeckProfileValid()) return false;
    index = slot - 1; length = betaGwentDeckLengths[index];
    if (length < 25 || length > 40) return false;
    for (i = 0; i < length; i += 1) cards.PushBack(betaGwentDeckCards[index * 40 + i]);
    title = betaGwentDeckNames[index]; faction = betaGwentDeckFactions[index]; leader = betaGwentDeckLeaders[index]; return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentStoreDeck(slot : int, cards : array<int>, title : string, faction : int, leader : int) : bool
{
    var i, index : int; var validation : SBetaGwentDeckValidation;
    validation = BetaGwentValidateDeck(cards, faction, leader);
    if (slot < 1 || slot > 8 || !validation.valid || StrLen(title) > 48) return false;
    if (betaGwentDeckSchema == 0)
    {
        betaGwentDeckNames.Clear(); betaGwentDeckLeaders.Clear(); betaGwentDeckFactions.Clear();
        betaGwentDeckLengths.Clear(); betaGwentDeckCards.Clear();
        for (i = 0; i < 8; i += 1)
        { betaGwentDeckNames.PushBack(""); betaGwentDeckLeaders.PushBack(0); betaGwentDeckFactions.PushBack(0); betaGwentDeckLengths.PushBack(0); }
        for (i = 0; i < 320; i += 1) betaGwentDeckCards.PushBack(0);
        betaGwentDeckSchema = 1;
    }
    if (!BetaGwentDeckProfileValid()) return false; // Never overwrite an unknown/corrupt schema.
    index = slot - 1; betaGwentDeckNames[index] = title; betaGwentDeckFactions[index] = faction;
    betaGwentDeckLeaders[index] = leader; betaGwentDeckLengths[index] = cards.Size();
    for (i = 0; i < 40; i += 1)
    { betaGwentDeckCards[index * 40 + i] = 0; if (i < cards.Size()) betaGwentDeckCards[index * 40 + i] = cards[i]; }
    LogChannel('BetaGwent', "DECK_PROFILE_SAVED slot=" + slot + " cards=" + cards.Size() + " leader=" + leader + " schema=1");
    return true;
}

// Selection is stored with the same Witcher save as the eight deck slots.
@addField(W3PlayerWitcher)
private saved var betaGwentPreferredDeck : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentPreferredDeck() : int { return betaGwentPreferredDeck; }
@addMethod(W3PlayerWitcher)
public function BetaGwentRememberDeck(id : int) { betaGwentPreferredDeck = id; }

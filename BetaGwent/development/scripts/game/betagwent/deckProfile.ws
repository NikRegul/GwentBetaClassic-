// Separate saved profile fields: no changes to vanilla Gwent collection/decks.
// Eight slots,40 template IDs per slot; shape checked before every read/write.
@addField(W3PlayerWitcher)
private saved var betaGwentAnimationTempo : int;
@addField(W3PlayerWitcher)
private saved var betaGwentReducedEffects : bool;
@addMethod(W3PlayerWitcher)
public function BetaGwentAnimationTempo() : int
{ if(betaGwentAnimationTempo==15 || betaGwentAnimationTempo==20)return betaGwentAnimationTempo;return 10; }
@addMethod(W3PlayerWitcher)
public function BetaGwentReducedEffects() : bool { return betaGwentReducedEffects; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetPresentation(tempo : int, reduced : bool)
{ if(tempo!=10 && tempo!=15 && tempo!=20)return;betaGwentAnimationTempo=tempo;betaGwentReducedEffects=reduced; }
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
    if (slot >= 9 && slot <= 13) return BetaGwentLoadStarterDeck(slot - 9, cards, title, faction, leader);
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
    if (slot >= 9 && slot <= 13) return BetaGwentStoreStarterDeck(slot - 9, cards, title, faction, leader);
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

// Independent overrides for the five starter decks. Preserve all eight existing
// custom slots and their schema. Missing overrides use the original starter.
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckSchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckNames : array<string>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckLeaders : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckFactions : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckLengths : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentStarterDeckCards : array<int>;
@addMethod(W3PlayerWitcher)
private function BetaGwentStarterDeckProfileValid() : bool
{
    return betaGwentStarterDeckSchema == 1 && betaGwentStarterDeckNames.Size() == 5
        && betaGwentStarterDeckLeaders.Size() == 5 && betaGwentStarterDeckFactions.Size() == 5
        && betaGwentStarterDeckLengths.Size() == 5 && betaGwentStarterDeckCards.Size() == 200;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentLoadStarterDeck(index : int, out cards : array<int>, out title : string, out faction : int, out leader : int) : bool
{
    var i, length : int;
    cards.Clear(); if (index < 0 || index >= 5 || !BetaGwentStarterDeckProfileValid()) return false;
    length = betaGwentStarterDeckLengths[index]; if (length < 25 || length > 40) return false;
    for (i = 0; i < length; i += 1) cards.PushBack(betaGwentStarterDeckCards[index * 40 + i]);
    title = betaGwentStarterDeckNames[index]; faction = betaGwentStarterDeckFactions[index];
    leader = betaGwentStarterDeckLeaders[index]; return true;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentStoreStarterDeck(index : int, cards : array<int>, title : string, faction : int, leader : int) : bool
{
    var i : int; var validation : SBetaGwentDeckValidation;
    validation = BetaGwentValidateDeck(cards, faction, leader);
    if (index < 0 || index >= 5 || !validation.valid || StrLen(title) > 48) return false;
    if (betaGwentStarterDeckSchema == 0)
    {
        betaGwentStarterDeckNames.Clear(); betaGwentStarterDeckLeaders.Clear(); betaGwentStarterDeckFactions.Clear();
        betaGwentStarterDeckLengths.Clear(); betaGwentStarterDeckCards.Clear();
        for (i = 0; i < 5; i += 1)
        { betaGwentStarterDeckNames.PushBack(""); betaGwentStarterDeckLeaders.PushBack(0); betaGwentStarterDeckFactions.PushBack(0); betaGwentStarterDeckLengths.PushBack(0); }
        for (i = 0; i < 200; i += 1) betaGwentStarterDeckCards.PushBack(0);
        betaGwentStarterDeckSchema = 1;
    }
    if (!BetaGwentStarterDeckProfileValid()) return false;
    betaGwentStarterDeckNames[index] = title; betaGwentStarterDeckLeaders[index] = leader;
    betaGwentStarterDeckFactions[index] = faction; betaGwentStarterDeckLengths[index] = cards.Size();
    for (i = 0; i < 40; i += 1)
    { betaGwentStarterDeckCards[index * 40 + i] = 0; if (i < cards.Size()) betaGwentStarterDeckCards[index * 40 + i] = cards[i]; }
    LogChannel('BetaGwent', "STARTER_DECK_SAVED preset=" + (index + 16) + " cards=" + cards.Size()); return true;
}

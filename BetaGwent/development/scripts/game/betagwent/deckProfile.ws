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
// Stage 131: opponent difficulty. 1 = easy, 2 = normal, 3 = hard (0 = never set: hard,
// the behaviour of earlier versions).
@addField(W3PlayerWitcher)
private saved var betaGwentDifficulty : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentDifficulty() : int { if(betaGwentDifficulty>=1 && betaGwentDifficulty<=4)return betaGwentDifficulty;return 3; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetDifficulty(level : int) { if(level>=1 && level<=4)betaGwentDifficulty=level; }
// Pause before each opponent move: 1=none, 2=0.4 s, 3=0.8 s, 4=1.2 s (0 = never set).
@addField(W3PlayerWitcher)
private saved var betaGwentAiPause : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentAiPause() : int { if(betaGwentAiPause>=1 && betaGwentAiPause<=4)return betaGwentAiPause;return 1; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetAiPause(pause : int) { if(pause>=1 && pause<=4)betaGwentAiPause=pause; }
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
// Preserve the original damaged arrays once, before any shape repair. Facts
// cannot store names; this quarantine keeps surviving strings/records available.
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoverySchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryOriginalSchema : int;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryNames : array<string>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryLeaders : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryFactions : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryLengths : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentDeckRecoveryCards : array<int>;
@addMethod(W3PlayerWitcher)
private function BetaGwentRepairDeckProfile() : bool
{
    if (BetaGwentDeckProfileValid()) return true;
    return BetaGwentRecoverDeckProfile();
}
@addMethod(W3PlayerWitcher)
private function BetaGwentRecoverDeckProfile() : bool
{
    var names : array<string>; var leaders, factions, lengths, cards, deck : array<int>;
    var i, j, slot, n, kept, mirrored, cur, bank, pass, f, l : int;
    var title : string; var validation : SBetaGwentDeckValidation;
    var first, second, backup : SBetaGwentProfileBackup; var firstValid, secondValid, recovered, empty : bool;
    if (betaGwentDeckSchema != 0 && betaGwentDeckSchema != 1)
    { LogChannel('BetaGwent', "DECK_PROFILE_REPAIR_REJECT reason=unknownSchema schema=" + betaGwentDeckSchema); return false; }
    if (betaGwentDeckRecoverySchema == 0 && (betaGwentDeckCards.Size() > 0 || betaGwentDeckNames.Size() > 0 || betaGwentDeckLengths.Size() > 0))
    {
        betaGwentDeckRecoveryOriginalSchema = betaGwentDeckSchema;
        betaGwentDeckRecoveryNames = betaGwentDeckNames; betaGwentDeckRecoveryLeaders = betaGwentDeckLeaders;
        betaGwentDeckRecoveryFactions = betaGwentDeckFactions; betaGwentDeckRecoveryLengths = betaGwentDeckLengths;
        betaGwentDeckRecoveryCards = betaGwentDeckCards; betaGwentDeckRecoverySchema = 1;
    }
    cur = FactsQueryLatestValue("bg_b2_cur");
    if (cur != 1 && cur != 2) cur = 1;
    firstValid = BetaGwentVerifiedBackupBank(cur, first);
    secondValid = BetaGwentVerifiedBackupBank(3 - cur, second);
    LogChannel('BetaGwent', "DECK_PROFILE_SHAPE names=" + betaGwentDeckNames.Size() + " leaders=" + betaGwentDeckLeaders.Size()
        + " factions=" + betaGwentDeckFactions.Size() + " lengths=" + betaGwentDeckLengths.Size() + " cards=" + betaGwentDeckCards.Size());
    for (slot = 1; slot <= 8; slot += 1)
    {
        i = slot - 1; deck.Clear(); title = ""; n = 0; recovered = false; empty = false;
        if (betaGwentDeckLengths.Size() > i && betaGwentDeckLeaders.Size() > i && betaGwentDeckFactions.Size() > i)
        {
            n = betaGwentDeckLengths[i];
            empty = n == 0 && betaGwentDeckLeaders[i] == 0 && betaGwentDeckFactions[i] == 0 && betaGwentDeckCards.Size() >= (i + 1) * 40;
            if (empty) for (j = 0; j < 40; j += 1) if (betaGwentDeckCards[i * 40 + j] != 0) empty = false;
        }
        if (n >= 25 && n <= 40 && betaGwentDeckCards.Size() >= i * 40 + n)
        {
            for (j = 0; j < n; j += 1) deck.PushBack(betaGwentDeckCards[i * 40 + j]);
            validation = BetaGwentValidateDeck(deck, betaGwentDeckFactions[i], betaGwentDeckLeaders[i]);
            if (validation.valid) { recovered = true; f = betaGwentDeckFactions[i]; l = betaGwentDeckLeaders[i]; kept += 1; }
        }
        if (betaGwentDeckNames.Size() > i) title = betaGwentDeckNames[i];
        // Complete banks only, with the same whole-bank validation used by restore.
        for (pass = 0; pass < 2 && !recovered && !empty; pass += 1)
        {
            if (pass == 0) { if (!firstValid) continue; backup = first; } else { if (!secondValid) continue; backup = second; }
            n = backup.lengths[i]; if (n == 0) break; // Committed deletion/empty slot must not resurrect an older deck.
            if (n < 25 || n > 40) continue;
            deck.Clear(); bank = 0;
            for (j = 0; j < i; j += 1) bank += backup.lengths[j];
            for (j = 0; j < n; j += 1) deck.PushBack(backup.cards[bank + j]);
            f = backup.factions[i]; l = backup.leaders[i]; validation = BetaGwentValidateDeck(deck, f, l);
            if (validation.valid) { recovered = true; mirrored += 1; }
        }
        if (recovered)
        {
            if (StrLen(title) == 0 || StrLen(title) > 48) title = BetaGwentConsoleFormat(27, IntToString(slot));
            names.PushBack(title); leaders.PushBack(l); factions.PushBack(f); lengths.PushBack(deck.Size());
            for (j = 0; j < 40; j += 1) { if (j < deck.Size()) cards.PushBack(deck[j]); else cards.PushBack(0); }
        }
        else
        {
            names.PushBack(""); leaders.PushBack(0); factions.PushBack(0); lengths.PushBack(0);
            for (j = 0; j < 40; j += 1) cards.PushBack(0);
        }
    }
    betaGwentDeckNames = names; betaGwentDeckLeaders = leaders; betaGwentDeckFactions = factions;
    betaGwentDeckLengths = lengths; betaGwentDeckCards = cards; betaGwentDeckSchema = 1;
    LogChannel('BetaGwent', "DECK_PROFILE_REPAIRED kept=" + kept + " fromMirror=" + mirrored + " quarantined=" + betaGwentDeckRecoverySchema + " valid=" + BetaGwentDeckProfileValid());
    return BetaGwentDeckProfileValid();
}
@addMethod(W3PlayerWitcher)
public function BetaGwentLoadDeck(slot : int, out cards : array<int>, out title : string, out faction : int, out leader : int) : bool
{
    var i, length, index : int; var validation : SBetaGwentDeckValidation; var empty : bool;
    if (slot >= 9 && slot <= 13) return BetaGwentLoadStarterDeck(slot - 9, cards, title, faction, leader);
    cards.Clear(); if (slot < 1 || slot > 8 || !BetaGwentRepairDeckProfile()) return false;
    index = slot - 1; length = betaGwentDeckLengths[index];
    empty = length == 0 && betaGwentDeckLeaders[index] == 0 && betaGwentDeckFactions[index] == 0;
    if (empty) for (i = 0; i < 40; i += 1) if (betaGwentDeckCards[index * 40 + i] != 0) empty = false;
    if (empty) return false;
    if (length >= 25 && length <= 40)
    {
        for (i = 0; i < length; i += 1) cards.PushBack(betaGwentDeckCards[index * 40 + i]);
        validation = BetaGwentValidateDeck(cards, betaGwentDeckFactions[index], betaGwentDeckLeaders[index]);
    }
    if (!validation.valid)
    {
        if (!BetaGwentRecoverDeckProfile()) { cards.Clear(); return false; }
        cards.Clear(); length = betaGwentDeckLengths[index]; if (length < 25 || length > 40) return false;
        for (i = 0; i < length; i += 1) cards.PushBack(betaGwentDeckCards[index * 40 + i]);
    }
    title = betaGwentDeckNames[index]; faction = betaGwentDeckFactions[index]; leader = betaGwentDeckLeaders[index]; return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentStoreDeck(slot : int, cards : array<int>, title : string, faction : int, leader : int) : bool
{
    var i, index : int; var validation : SBetaGwentDeckValidation;
    if (slot >= 9 && slot <= 13) return BetaGwentStoreStarterDeck(slot - 9, cards, title, faction, leader);
    validation = BetaGwentValidateDeck(cards, faction, leader);
    if (slot < 1 || slot > 8 || !validation.valid || StrLen(title) > 48) return false;
    if (!BetaGwentRepairDeckProfile()) return false; // Never overwrite an unknown schema; repair a damaged one.
    index = slot - 1; betaGwentDeckNames[index] = title; betaGwentDeckFactions[index] = faction;
    betaGwentDeckLeaders[index] = leader; betaGwentDeckLengths[index] = cards.Size();
    for (i = 0; i < 40; i += 1)
    { betaGwentDeckCards[index * 40 + i] = 0; if (i < cards.Size()) betaGwentDeckCards[index * 40 + i] = cards[i]; }
    LogChannel('BetaGwent', "DECK_PROFILE_SAVED slot=" + slot + " cards=" + cards.Size() + " leader=" + leader + " schema=1");
    BetaGwentBackupProfile();
    return true;
}

@addMethod(W3PlayerWitcher)
public function BetaGwentClearDeck(slot : int) : bool
{
    var i, index : int;
    if (slot >= 9 && slot <= 13)
    {
        if (!BetaGwentStarterDeckProfileValid()) return false;
        index = slot - 9; betaGwentStarterDeckNames[index] = ""; betaGwentStarterDeckLeaders[index] = 0;
        betaGwentStarterDeckFactions[index] = 0; betaGwentStarterDeckLengths[index] = 0;
        for (i = 0; i < 40; i += 1) betaGwentStarterDeckCards[index * 40 + i] = 0;
        LogChannel('BetaGwent', "STARTER_DECK_RESET preset=" + (index + 16)); BetaGwentBackupProfile(); return true;
    }
    if (slot < 1 || slot > 8 || !BetaGwentRepairDeckProfile()) return false;
    index = slot - 1; betaGwentDeckNames[index] = ""; betaGwentDeckFactions[index] = 0;
    betaGwentDeckLeaders[index] = 0; betaGwentDeckLengths[index] = 0;
    for (i = 0; i < 40; i += 1) betaGwentDeckCards[index * 40 + i] = 0;
    LogChannel('BetaGwent', "DECK_PROFILE_DELETED slot=" + slot); BetaGwentBackupProfile();
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
    LogChannel('BetaGwent', "STARTER_DECK_SAVED preset=" + (index + 16) + " cards=" + cards.Size()); BetaGwentBackupProfile(); return true;
}

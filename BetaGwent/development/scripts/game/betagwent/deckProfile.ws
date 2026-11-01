// Separate saved profile fields: no changes to vanilla Gwent collection/decks.
// Eight slots,40 template IDs per slot; shape checked before every read/write.
@addField(W3PlayerWitcher)
private var betaGwentAnimationTempo : int;
@addField(W3PlayerWitcher)
private var betaGwentReducedEffects : bool;
@addMethod(W3PlayerWitcher)
public function BetaGwentAnimationTempo() : int
{ BetaGwentStoreLoad();if(betaGwentAnimationTempo==15 || betaGwentAnimationTempo==20)return betaGwentAnimationTempo;return 10; }
@addMethod(W3PlayerWitcher)
public function BetaGwentReducedEffects() : bool { BetaGwentStoreLoad();return betaGwentReducedEffects; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetPresentation(tempo : int, reduced : bool) : bool
{ if (!BetaGwentStoreReady()) return false;
    if(tempo!=10 && tempo!=15 && tempo!=20)return false;betaGwentAnimationTempo=tempo;betaGwentReducedEffects=reduced;return BetaGwentStoreCommit(); }
// Stage 131: opponent difficulty. 1 = easy, 2 = normal, 3 = hard (0 = never set: hard,
// the behaviour of earlier versions).
@addField(W3PlayerWitcher)
private var betaGwentDifficulty : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentDifficulty() : int { BetaGwentStoreLoad(); if(betaGwentDifficulty>=1 && betaGwentDifficulty<=4)return betaGwentDifficulty;return 3; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetDifficulty(level : int) { if (!BetaGwentStoreReady()) return;
    if(level>=1 && level<=4){betaGwentDifficulty=level;BetaGwentStoreCommit();} }
// Pause before each opponent move: 1=none, 2=0.4 s, 3=0.8 s, 4=1.2 s (0 = never set).
@addField(W3PlayerWitcher)
private var betaGwentAiPause : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentAiPause() : int { BetaGwentStoreLoad(); if(betaGwentAiPause>=1 && betaGwentAiPause<=4)return betaGwentAiPause;return 1; }
@addMethod(W3PlayerWitcher)
public function BetaGwentSetAiPause(pause : int) { if (!BetaGwentStoreReady()) return;
    if(pause>=1 && pause<=4){betaGwentAiPause=pause;BetaGwentStoreCommit();} }
@addField(W3PlayerWitcher)
private var betaGwentDeckSchema : int;
@addField(W3PlayerWitcher)
private var betaGwentDeckNames : array<string>;
@addField(W3PlayerWitcher)
private var betaGwentDeckLeaders : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckFactions : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckLengths : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckCards : array<int>;

@addMethod(W3PlayerWitcher)
private function BetaGwentDeckProfileValid() : bool
{
    return betaGwentDeckSchema == 1 && betaGwentDeckNames.Size() == 8 && betaGwentDeckLeaders.Size() == 8
        && betaGwentDeckFactions.Size() == 8 && betaGwentDeckLengths.Size() == 8 && betaGwentDeckCards.Size() == 320;
}
// Preserve the original damaged arrays once, before any shape repair. Facts
// cannot store names; this quarantine keeps surviving strings/records available.
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoverySchema : int;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryOriginalSchema : int;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryNames : array<string>;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryLeaders : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryFactions : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryLengths : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentDeckRecoveryCards : array<int>;
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
    var i, j, slot, n, kept, mirrored, cur, bank, pass, f, l, generation : int;
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
    cur = BetaGwentSelectBackupBank(generation);
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
// A whole-profile restore may repair missing ownership while deck fields survive.
// Include explicit empty slots, so an older mirror cannot undo a saved deletion.
@addMethod(W3PlayerWitcher)
private function BetaGwentPrimaryDeckSlotIntact(slot : int) : bool
{
    var cards, stored : array<int>; var i, index, length, faction, leader : int; var validation : SBetaGwentDeckValidation;
    if (slot >= 1 && slot <= 8)
    {
        if (!BetaGwentDeckProfileValid()) return false;
        index = slot - 1; length = betaGwentDeckLengths[index]; faction = betaGwentDeckFactions[index]; leader = betaGwentDeckLeaders[index];
        stored = betaGwentDeckCards;
    }
    else if (slot >= 9 && slot <= 13)
    {
        if (!BetaGwentStarterDeckProfileValid()) return false;
        index = slot - 9; length = betaGwentStarterDeckLengths[index]; faction = betaGwentStarterDeckFactions[index]; leader = betaGwentStarterDeckLeaders[index];
        stored = betaGwentStarterDeckCards;
    }
    else return false;
    if (length == 0)
    {
        if (faction != 0 || leader != 0) return false;
        for (i = 0; i < 40; i += 1) if (stored[index * 40 + i] != 0) return false;
        return true;
    }
    if (length < 25 || length > 40) return false;
    for (i = 0; i < length; i += 1) cards.PushBack(stored[index * 40 + i]);
    validation = BetaGwentValidateDeck(cards, faction, leader); return validation.valid;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentLoadDeck(slot : int, out cards : array<int>, out title : string, out faction : int, out leader : int) : bool
{
    var i, length, index : int; var validation : SBetaGwentDeckValidation; var empty : bool;
    if (!BetaGwentStoreReady()) return false;
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
    if (!BetaGwentStoreReady()) return false;
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
    if (!BetaGwentStoreReady()) return false;
    if (slot >= 9 && slot <= 13)
    {
        if (!BetaGwentRepairStarterDeckProfile()) return false;
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
private var betaGwentPreferredDeck : int;
@addMethod(W3PlayerWitcher)
public function BetaGwentPreferredDeck() : int { BetaGwentStoreLoad(); return betaGwentPreferredDeck; }
@addMethod(W3PlayerWitcher)
public function BetaGwentRememberDeck(id : int) { if (!BetaGwentStoreReady()) return;
    betaGwentPreferredDeck = id; BetaGwentStoreCommit(); }

// Independent overrides for the five starter decks. Preserve all eight existing
// custom slots and their schema. Missing overrides use the original starter.
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckSchema : int;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckNames : array<string>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckLeaders : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckFactions : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckLengths : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckCards : array<int>;
// Preserve starter override fragments before any repair, including Unicode names.
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoverySchema : int;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryOriginalSchema : int;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryNames : array<string>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryLeaders : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryFactions : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryLengths : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStarterDeckRecoveryCards : array<int>;
@addMethod(W3PlayerWitcher)
private function BetaGwentStarterDeckProfileValid() : bool
{
    return betaGwentStarterDeckSchema == 1 && betaGwentStarterDeckNames.Size() == 5
        && betaGwentStarterDeckLeaders.Size() == 5 && betaGwentStarterDeckFactions.Size() == 5
        && betaGwentStarterDeckLengths.Size() == 5 && betaGwentStarterDeckCards.Size() == 200;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentRepairStarterDeckProfile() : bool
{
    if (BetaGwentStarterDeckProfileValid()) return true;
    return BetaGwentRecoverStarterDeckProfile();
}
@addMethod(W3PlayerWitcher)
private function BetaGwentRecoverStarterDeckProfile() : bool
{
    var names : array<string>; var leaders, factions, lengths, cards, deck : array<int>;
    var i, j, n, pass, offset, cur, generation, f, l, kept, mirrored : int;
    var title : string; var validation : SBetaGwentDeckValidation;
    var first, second, backup : SBetaGwentProfileBackup; var firstValid, secondValid, recovered, empty : bool;
    if (betaGwentStarterDeckSchema != 0 && betaGwentStarterDeckSchema != 1)
    { LogChannel('BetaGwent', "STARTER_DECK_REPAIR_REJECT reason=unknownSchema schema=" + betaGwentStarterDeckSchema); return false; }
    if (betaGwentStarterDeckRecoverySchema == 0 && (betaGwentStarterDeckCards.Size() > 0 || betaGwentStarterDeckNames.Size() > 0
        || betaGwentStarterDeckLengths.Size() > 0 || betaGwentStarterDeckLeaders.Size() > 0 || betaGwentStarterDeckFactions.Size() > 0))
    {
        betaGwentStarterDeckRecoveryOriginalSchema = betaGwentStarterDeckSchema;
        betaGwentStarterDeckRecoveryNames = betaGwentStarterDeckNames; betaGwentStarterDeckRecoveryLeaders = betaGwentStarterDeckLeaders;
        betaGwentStarterDeckRecoveryFactions = betaGwentStarterDeckFactions; betaGwentStarterDeckRecoveryLengths = betaGwentStarterDeckLengths;
        betaGwentStarterDeckRecoveryCards = betaGwentStarterDeckCards; betaGwentStarterDeckRecoverySchema = 1;
    }
    cur = BetaGwentSelectBackupBank(generation); if (cur != 1 && cur != 2) cur = 1;
    firstValid = BetaGwentVerifiedBackupBank(cur, first); secondValid = BetaGwentVerifiedBackupBank(3 - cur, second);
    for (i = 0; i < 5; i += 1)
    {
        deck.Clear(); title = ""; n = 0; recovered = false; empty = false;
        if (betaGwentStarterDeckLengths.Size() > i && betaGwentStarterDeckLeaders.Size() > i && betaGwentStarterDeckFactions.Size() > i)
        {
            n = betaGwentStarterDeckLengths[i];
            empty = n == 0 && betaGwentStarterDeckLeaders[i] == 0 && betaGwentStarterDeckFactions[i] == 0 && betaGwentStarterDeckCards.Size() >= (i + 1) * 40;
            if (empty) for (j = 0; j < 40; j += 1) if (betaGwentStarterDeckCards[i * 40 + j] != 0) empty = false;
            if (n >= 25 && n <= 40 && betaGwentStarterDeckCards.Size() >= i * 40 + n)
            {
                for (j = 0; j < n; j += 1) deck.PushBack(betaGwentStarterDeckCards[i * 40 + j]);
                validation = BetaGwentValidateDeck(deck, betaGwentStarterDeckFactions[i], betaGwentStarterDeckLeaders[i]);
                if (validation.valid) { recovered = true; f = betaGwentStarterDeckFactions[i]; l = betaGwentStarterDeckLeaders[i]; kept += 1; }
            }
        }
        if (betaGwentStarterDeckNames.Size() > i) title = betaGwentStarterDeckNames[i];
        for (pass = 0; pass < 2 && !recovered && !empty; pass += 1)
        {
            if (pass == 0) { if (!firstValid) continue; backup = first; } else { if (!secondValid) continue; backup = second; }
            n = backup.lengths[8 + i]; if (n == 0) break; // A committed reset must not resurrect the older override.
            if (n < 25 || n > 40) continue;
            offset = 0; for (j = 0; j < 8 + i; j += 1) offset += backup.lengths[j];
            deck.Clear(); for (j = 0; j < n; j += 1) deck.PushBack(backup.cards[offset + j]);
            f = backup.factions[8 + i]; l = backup.leaders[8 + i]; validation = BetaGwentValidateDeck(deck, f, l);
            if (validation.valid) { recovered = true; mirrored += 1; }
        }
        if (recovered)
        {
            if (StrLen(title) == 0 || StrLen(title) > 48) title = BetaGwentConsoleFormat(27, IntToString(i + 9));
            names.PushBack(title); leaders.PushBack(l); factions.PushBack(f); lengths.PushBack(deck.Size());
            for (j = 0; j < 40; j += 1) { if (j < deck.Size()) cards.PushBack(deck[j]); else cards.PushBack(0); }
        }
        else
        {
            names.PushBack(""); leaders.PushBack(0); factions.PushBack(0); lengths.PushBack(0);
            for (j = 0; j < 40; j += 1) cards.PushBack(0);
        }
    }
    betaGwentStarterDeckNames = names; betaGwentStarterDeckLeaders = leaders; betaGwentStarterDeckFactions = factions;
    betaGwentStarterDeckLengths = lengths; betaGwentStarterDeckCards = cards; betaGwentStarterDeckSchema = 1;
    LogChannel('BetaGwent', "STARTER_DECK_REPAIRED kept=" + kept + " fromMirror=" + mirrored + " quarantined=" + betaGwentStarterDeckRecoverySchema);
    return BetaGwentStarterDeckProfileValid();
}
@addMethod(W3PlayerWitcher)
private function BetaGwentLoadStarterDeck(index : int, out cards : array<int>, out title : string, out faction : int, out leader : int) : bool
{
    var i, length : int; var validation : SBetaGwentDeckValidation; var empty : bool;
    cards.Clear(); if (index < 0 || index >= 5 || !BetaGwentRepairStarterDeckProfile()) return false;
    length = betaGwentStarterDeckLengths[index];
    empty = length == 0 && betaGwentStarterDeckLeaders[index] == 0 && betaGwentStarterDeckFactions[index] == 0;
    if (empty) for (i = 0; i < 40; i += 1) if (betaGwentStarterDeckCards[index * 40 + i] != 0) empty = false;
    if (empty) return false;
    if (length >= 25 && length <= 40)
    {
        for (i = 0; i < length; i += 1) cards.PushBack(betaGwentStarterDeckCards[index * 40 + i]);
        validation = BetaGwentValidateDeck(cards, betaGwentStarterDeckFactions[index], betaGwentStarterDeckLeaders[index]);
    }
    if (!validation.valid)
    {
        if (!BetaGwentRecoverStarterDeckProfile()) { cards.Clear(); return false; }
        cards.Clear(); length = betaGwentStarterDeckLengths[index]; if (length < 25 || length > 40) return false;
        for (i = 0; i < length; i += 1) cards.PushBack(betaGwentStarterDeckCards[index * 40 + i]);
    }
    title = betaGwentStarterDeckNames[index]; faction = betaGwentStarterDeckFactions[index];
    leader = betaGwentStarterDeckLeaders[index]; return true;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentStoreStarterDeck(index : int, cards : array<int>, title : string, faction : int, leader : int) : bool
{
    var i : int; var validation : SBetaGwentDeckValidation;
    validation = BetaGwentValidateDeck(cards, faction, leader);
    if (index < 0 || index >= 5 || !validation.valid || StrLen(title) > 48) return false;
    if (!BetaGwentRepairStarterDeckProfile()) return false;
    betaGwentStarterDeckNames[index] = title; betaGwentStarterDeckLeaders[index] = leader;
    betaGwentStarterDeckFactions[index] = faction; betaGwentStarterDeckLengths[index] = cards.Size();
    for (i = 0; i < 40; i += 1)
    { betaGwentStarterDeckCards[index * 40 + i] = 0; if (i < cards.Size()) betaGwentStarterDeckCards[index * 40 + i] = cards[i]; }
    LogChannel('BetaGwent', "STARTER_DECK_SAVED preset=" + (index + 16) + " cards=" + cards.Size()); BetaGwentBackupProfile(); return true;
}

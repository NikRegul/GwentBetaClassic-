// 0.9.4: one save-backed store for the whole Beta Gwent profile.
// Next-Gen 5.x writes at most 45 @addField saved properties of W3PlayerWitcher,
// shared by ALL installed mods; later ones are dropped when saving, even empty
// ones (tools/saveprobe094). Facts keep only signed 16-bit values. The profile
// therefore lives in the few saved fields below, declared first (this file sorts
// first). All other profile fields are working copies filled from the store.
// Layout: magic, format, payload length, Adler A, Adler B, commit number, then
// tagged sections. Format 2 includes recovery evidence and verified paired text.
// Format 1 is read for migration; unknown formats remain read-only.
@addField(W3PlayerWitcher)
private saved var betaGwentStore : array<int>;
@addField(W3PlayerWitcher)
private saved var betaGwentStoreText : array<string>;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardActors : array<EntityHandle>;
@addField(W3PlayerWitcher)
private saved var betaGwentRewardedQuests : array<name>;
@addField(W3PlayerWitcher)
private var betaGwentStoreLoaded : bool;
@addField(W3PlayerWitcher)
private var betaGwentStoreReadOnly : bool;

@addField(W3PlayerWitcher)
private var betaGwentStoreWritable : bool;
@addField(W3PlayerWitcher)
private var betaGwentStoreRecovering : bool;
@addField(W3PlayerWitcher)
private var betaGwentStoreRecoverySchema : int;
@addField(W3PlayerWitcher)
private var betaGwentStoreRecoveryData : array<int>;
@addField(W3PlayerWitcher)
private var betaGwentStoreRecoveryText : array<string>;

function BetaGwentStoreMagic() : int { return 4719; }
function BetaGwentStoreFormat() : int { return 2; }
function BetaGwentStoreAdd(out data : array<int>, tag : int, values : array<int>)
{
    var i : int;
    data.PushBack(tag); data.PushBack(values.Size());
    for (i = 0; i < values.Size(); i += 1) data.PushBack(values[i]);
}
function BetaGwentStoreBool(value : bool) : int { if (value) return 1; return 0; }
// Retail 1.32 mishandles "%" on large values and the ?: operator (the RNG
// in 0.9.3 hit the same bug). Division-based remainder behaves like C++ "%"
// on every platform, so Next-Gen results are unchanged.
function BetaGwentProfileMod(value : int, maximum : int) : int
{
    var quotient : int;
    quotient = value / maximum;
    return value - quotient * maximum;
}
function BetaGwentStoreSum(data : array<int>, start : int, out a : int, out b : int)
{
    var i, v : int;
    a = 1; b = 0;
    for (i = start; i < data.Size(); i += 1)
    {
        v = BetaGwentProfileMod(data[i], 65521); if (v < 0) v += 65521;
        a = BetaGwentProfileMod(a + v, 65521); b = BetaGwentProfileMod(b + a, 65521);
    }
}

// Paired exact strings avoid platform-dependent text hashes. The numeric
// checksum protects their lengths; the first string binds them to this commit.
function BetaGwentStoreAppendText(out text : array<string>, out lengths : array<int>, values : array<string>)
{
    var i : int;
    for (i = 0; i < values.Size(); i += 1)
    { lengths.PushBack(StrLen(values[i])); text.PushBack(values[i]); text.PushBack(values[i]); }
}
@addMethod(W3PlayerWitcher)
public function BetaGwentStoreReady() : bool
{
    if (!betaGwentStoreLoaded) BetaGwentStoreLoad();
    return !betaGwentStoreReadOnly && (betaGwentStoreWritable || betaGwentStoreRecovering);
}
@addMethod(W3PlayerWitcher)
private function BetaGwentStoreRecoverProfile() : bool
{
    var recovered : bool; var raw : array<int>; var text : array<string>;
    if (betaGwentStoreReadOnly || betaGwentStoreRecovering) return false;
    if (betaGwentStoreWritable) return true;
    // Preserve the rejected source before any successful recovery can replace it.
    raw = betaGwentStore; text = betaGwentStoreText;
    if (raw.Size() > 1000000 || text.Size() > 32768) return false;
    betaGwentStoreRecovering = true;
    if (betaGwentCollectionSchema == 0 || betaGwentCollectionSchema == 1)
    {
        if (BetaGwentCollectionEntriesValid()) { betaGwentCollectionSchema = 1; recovered = true; }
        else if (betaGwentCollectionSchema == 0 && betaGwentOwnedIds.Size() == 0 && betaGwentOwnedCopies.Size() == 0)
            recovered = BetaGwentRestoreProfile();
        else recovered = BetaGwentRecoverCollectionProfile();
    }
    betaGwentStoreRecovering = false;
    if (!recovered) return false;
    if (betaGwentStoreRecoverySchema == 0)
    { betaGwentStoreRecoverySchema = 1; betaGwentStoreRecoveryData = raw; betaGwentStoreRecoveryText = text; }
    betaGwentStoreWritable = true;
    if (!BetaGwentStoreCommit())
    { betaGwentStoreWritable = false; return false; }
    return true;
}
@addMethod(W3PlayerWitcher)
public function BetaGwentStoreCommit() : bool
{
    var data, scalars, lengths, next : array<int>; var text : array<string>; var i, a, b, commit : int;
    if (!betaGwentStoreLoaded) BetaGwentStoreLoad();
    if (!betaGwentStoreWritable || betaGwentStoreReadOnly || betaGwentStoreRecovering) return false;
    if (betaGwentDeckNames.Size() > 8 || betaGwentStarterDeckNames.Size() > 5
        || betaGwentDeckRecoveryNames.Size() > 8192 || betaGwentStarterDeckRecoveryNames.Size() > 8192
        || betaGwentStoreRecoveryText.Size() > 32768) return false;
    scalars.PushBack(betaGwentCollectionSchema);
    scalars.PushBack(betaGwentProgressionSeed);
    scalars.PushBack(betaGwentStarterSetRevision);
    scalars.PushBack(betaGwentNewCardsSchema);
    scalars.PushBack(betaGwentAnimationTempo);
    scalars.PushBack(BetaGwentStoreBool(betaGwentReducedEffects));
    scalars.PushBack(betaGwentDifficulty);
    scalars.PushBack(betaGwentAiPause);
    scalars.PushBack(betaGwentDeckSchema);
    scalars.PushBack(betaGwentPreferredDeck);
    scalars.PushBack(betaGwentStarterDeckSchema);
    scalars.PushBack(betaGwentKegsUnopened);
    scalars.PushBack(betaGwentOpponentPoolSize);
    scalars.PushBack(BetaGwentStoreBool(betaGwentCleanupPending090));
    scalars.PushBack(betaGwentScraps);
    scalars.PushBack(betaGwentDeckNames.Size());
    scalars.PushBack(betaGwentStarterDeckNames.Size());
    scalars.PushBack(betaGwentCollectionRecoverySchema);
    scalars.PushBack(betaGwentCollectionRecoveryOriginalSchema);
    scalars.PushBack(betaGwentDeckRecoverySchema);
    scalars.PushBack(betaGwentDeckRecoveryOriginalSchema);
    scalars.PushBack(betaGwentDeckRecoveryNames.Size());
    scalars.PushBack(betaGwentStarterDeckRecoverySchema);
    scalars.PushBack(betaGwentStarterDeckRecoveryOriginalSchema);
    scalars.PushBack(betaGwentStarterDeckRecoveryNames.Size());
    scalars.PushBack(betaGwentStoreRecoverySchema);
    scalars.PushBack(betaGwentStoreRecoveryText.Size());
    BetaGwentStoreAdd(data, 1, scalars);
    BetaGwentStoreAdd(data, 2, betaGwentOwnedIds);
    BetaGwentStoreAdd(data, 3, betaGwentOwnedCopies);
    BetaGwentStoreAdd(data, 4, betaGwentRewardedNpcs);
    BetaGwentStoreAdd(data, 5, betaGwentRewardActorWins);
    BetaGwentStoreAdd(data, 6, betaGwentNewCardIds);
    BetaGwentStoreAdd(data, 7, betaGwentDeckLeaders);
    BetaGwentStoreAdd(data, 8, betaGwentDeckFactions);
    BetaGwentStoreAdd(data, 9, betaGwentDeckLengths);
    BetaGwentStoreAdd(data, 10, betaGwentDeckCards);
    BetaGwentStoreAdd(data, 11, betaGwentStarterDeckLeaders);
    BetaGwentStoreAdd(data, 12, betaGwentStarterDeckFactions);
    BetaGwentStoreAdd(data, 13, betaGwentStarterDeckLengths);
    BetaGwentStoreAdd(data, 14, betaGwentStarterDeckCards);
    BetaGwentStoreAdd(data, 15, betaGwentKegAutomatic);
    BetaGwentStoreAdd(data, 16, betaGwentKegOffers);
    BetaGwentStoreAdd(data, 17, betaGwentKegAutomaticScraps);
    BetaGwentStoreAdd(data, 18, betaGwentOpponentBag);
    BetaGwentStoreAdd(data, 19, betaGwentOpponentRecent);
    BetaGwentStoreAdd(data, 20, betaGwentCollectionRecoveryIds);
    BetaGwentStoreAdd(data, 21, betaGwentCollectionRecoveryCopies);
    BetaGwentStoreAdd(data, 22, betaGwentDeckRecoveryLeaders);
    BetaGwentStoreAdd(data, 23, betaGwentDeckRecoveryFactions);
    BetaGwentStoreAdd(data, 24, betaGwentDeckRecoveryLengths);
    BetaGwentStoreAdd(data, 25, betaGwentDeckRecoveryCards);
    BetaGwentStoreAdd(data, 26, betaGwentStarterDeckRecoveryLeaders);
    BetaGwentStoreAdd(data, 27, betaGwentStarterDeckRecoveryFactions);
    BetaGwentStoreAdd(data, 28, betaGwentStarterDeckRecoveryLengths);
    BetaGwentStoreAdd(data, 29, betaGwentStarterDeckRecoveryCards);
    BetaGwentStoreAdd(data, 30, betaGwentStoreRecoveryData);
    commit = 1;
    if (betaGwentStore.Size() >= 6 && betaGwentStore[0] == BetaGwentStoreMagic()) commit = BetaGwentProfileMod(Max(0, betaGwentStore[5]), 1000000) + 1;
    text.PushBack(IntToString(commit));
    BetaGwentStoreAppendText(text, lengths, betaGwentDeckNames);
    BetaGwentStoreAppendText(text, lengths, betaGwentStarterDeckNames);
    BetaGwentStoreAppendText(text, lengths, betaGwentDeckRecoveryNames);
    BetaGwentStoreAppendText(text, lengths, betaGwentStarterDeckRecoveryNames);
    BetaGwentStoreAppendText(text, lengths, betaGwentStoreRecoveryText);
    BetaGwentStoreAdd(data, 31, lengths);
    if (data.Size() > 1000000) return false;
    BetaGwentStoreSum(data, 0, a, b);
    next.PushBack(BetaGwentStoreMagic()); next.PushBack(BetaGwentStoreFormat());
    next.PushBack(data.Size()); next.PushBack(a); next.PushBack(b); next.PushBack(commit);
    for (i = 0; i < data.Size(); i += 1) next.PushBack(data[i]);
    betaGwentStore = next; betaGwentStoreText = text;
    return true;
}

function BetaGwentStoreSlice(data : array<int>, start : int, length : int, out values : array<int>)
{
    var i : int;
    values.Clear();
    for (i = 0; i < length; i += 1) values.PushBack(data[start + i]);
}
function BetaGwentStoreScalar(values : array<int>, index : int) : int
{ if (index < values.Size()) return values[index]; return 0; }

@addMethod(W3PlayerWitcher)
private function BetaGwentStoreReject(reason : string) : bool
{
    betaGwentStoreWritable = false;
    LogChannel('BetaGwent', "PROFILE_STORE_REJECTED reason=" + reason + " size=" + betaGwentStore.Size());
    return false;
}

// Attempted, writable, recovering and unknown/read-only are distinct states.
// A failed read must never authorize an autosave to replace the rejected bytes.
@addMethod(W3PlayerWitcher)
public function BetaGwentStoreLoad() : bool
{
    var values, scalars, seen, lengths : array<int>; var text : array<string>;
    var i, n, tag, length, pos, a, b, format, names, starterNames, deckNames, starterRecoveryNames, rawNames, total, sectionCount, scalarCount : int;
    if (betaGwentStoreLoaded) return betaGwentStoreWritable;
    betaGwentStoreLoaded = true;
    if (betaGwentStore.Size() == 0)
    {
        betaGwentStoreWritable = true;
        LogChannel('BetaGwent', "PROFILE_STORE_EMPTY legacySchema=" + betaGwentCollectionSchema + " distinct=" + betaGwentOwnedIds.Size());
        return false;
    }
    if (betaGwentStore.Size() < 6 || betaGwentStore[0] != BetaGwentStoreMagic()) return BetaGwentStoreReject("header");
    format = betaGwentStore[1];
    if (format != 1 && format != BetaGwentStoreFormat())
    { betaGwentStoreReadOnly = true; return BetaGwentStoreReject("format" + format); }
    n = betaGwentStore[2];
    if (n < 0 || n > 1000000 || betaGwentStore.Size() != 6 + n) return BetaGwentStoreReject("length");
    if (betaGwentStore[5] < 1 || betaGwentStore[5] > 1000000) return BetaGwentStoreReject("commit");
    BetaGwentStoreSlice(betaGwentStore, 6, n, values); BetaGwentStoreSum(values, 0, a, b);
    if (a != betaGwentStore[3] || b != betaGwentStore[4]) return BetaGwentStoreReject("checksum");
    sectionCount = 31; scalarCount = 27;
    if (format == 1) { sectionCount = 19; scalarCount = 17; }
    pos = 6;
    while (pos < betaGwentStore.Size())
    {
        if (pos + 2 > betaGwentStore.Size()) return BetaGwentStoreReject("section");
        tag = betaGwentStore[pos]; length = betaGwentStore[pos + 1];
        if (tag <= 0 || length < 0 || length > betaGwentStore.Size() - pos - 2) return BetaGwentStoreReject("sectionLength");
        if (tag <= sectionCount)
        { if (seen.Contains(tag)) return BetaGwentStoreReject("duplicateSection"); seen.PushBack(tag); }
        if (tag == 1) BetaGwentStoreSlice(betaGwentStore, pos + 2, length, scalars);
        if (tag == 31) BetaGwentStoreSlice(betaGwentStore, pos + 2, length, lengths);
        pos += 2 + length;
    }
    if (seen.Size() != sectionCount || scalars.Size() != scalarCount)
    {
        LogChannel('BetaGwent', "PROFILE_STORE_SECTIONS seen=" + seen.Size() + "/" + sectionCount + " scalars=" + scalars.Size() + "/" + scalarCount + " format=" + format);
        return BetaGwentStoreReject("sections");
    }
    names = scalars[15]; starterNames = scalars[16];
    if (names < 0 || names > 8 || starterNames < 0 || starterNames > 5) return BetaGwentStoreReject("names");
    if (format == 2)
    {
        deckNames = scalars[21]; starterRecoveryNames = scalars[24]; rawNames = scalars[26];
        if (deckNames < 0 || deckNames > 8192 || starterRecoveryNames < 0 || starterRecoveryNames > 8192 || rawNames < 0 || rawNames > 32768)
            return BetaGwentStoreReject("recoveryNames");
    }
    total = names + starterNames + deckNames + starterRecoveryNames + rawNames;
    if (format == 1)
    { if (betaGwentStoreText.Size() != total) return BetaGwentStoreReject("textCount"); text = betaGwentStoreText; }
    else
    {
        if (lengths.Size() != total || betaGwentStoreText.Size() != 1 + total * 2) return BetaGwentStoreReject("textCount");
        if (betaGwentStoreText[0] != IntToString(betaGwentStore[5])) return BetaGwentStoreReject("textCommit");
        for (i = 0; i < total; i += 1)
        {
            if (lengths[i] < 0 || StrLen(betaGwentStoreText[1 + i * 2]) != lengths[i]
                || betaGwentStoreText[1 + i * 2] != betaGwentStoreText[2 + i * 2]) return BetaGwentStoreReject("textIntegrity");
            text.PushBack(betaGwentStoreText[1 + i * 2]);
        }
    }
    // All validation precedes mutation of working fields.
    pos = 6;
    while (pos < betaGwentStore.Size())
    {
        tag = betaGwentStore[pos]; length = betaGwentStore[pos + 1];
        BetaGwentStoreSlice(betaGwentStore, pos + 2, length, values); pos += 2 + length;
        switch (tag)
        {
            case 2: betaGwentOwnedIds = values; break;
            case 3: betaGwentOwnedCopies = values; break;
            case 4: betaGwentRewardedNpcs = values; break;
            case 5: betaGwentRewardActorWins = values; break;
            case 6: betaGwentNewCardIds = values; break;
            case 7: betaGwentDeckLeaders = values; break;
            case 8: betaGwentDeckFactions = values; break;
            case 9: betaGwentDeckLengths = values; break;
            case 10: betaGwentDeckCards = values; break;
            case 11: betaGwentStarterDeckLeaders = values; break;
            case 12: betaGwentStarterDeckFactions = values; break;
            case 13: betaGwentStarterDeckLengths = values; break;
            case 14: betaGwentStarterDeckCards = values; break;
            case 15: betaGwentKegAutomatic = values; break;
            case 16: betaGwentKegOffers = values; break;
            case 17: betaGwentKegAutomaticScraps = values; break;
            case 18: betaGwentOpponentBag = values; break;
            case 19: betaGwentOpponentRecent = values; break;
            case 20: betaGwentCollectionRecoveryIds = values; break;
            case 21: betaGwentCollectionRecoveryCopies = values; break;
            case 22: betaGwentDeckRecoveryLeaders = values; break;
            case 23: betaGwentDeckRecoveryFactions = values; break;
            case 24: betaGwentDeckRecoveryLengths = values; break;
            case 25: betaGwentDeckRecoveryCards = values; break;
            case 26: betaGwentStarterDeckRecoveryLeaders = values; break;
            case 27: betaGwentStarterDeckRecoveryFactions = values; break;
            case 28: betaGwentStarterDeckRecoveryLengths = values; break;
            case 29: betaGwentStarterDeckRecoveryCards = values; break;
            case 30: betaGwentStoreRecoveryData = values; break;
        }
    }
    betaGwentCollectionSchema = scalars[0];
    betaGwentProgressionSeed = scalars[1];
    betaGwentStarterSetRevision = scalars[2];
    betaGwentNewCardsSchema = scalars[3];
    betaGwentAnimationTempo = scalars[4];
    betaGwentReducedEffects = scalars[5] == 1;
    betaGwentDifficulty = scalars[6];
    betaGwentAiPause = scalars[7];
    betaGwentDeckSchema = scalars[8];
    betaGwentPreferredDeck = scalars[9];
    betaGwentStarterDeckSchema = scalars[10];
    betaGwentKegsUnopened = scalars[11];
    betaGwentOpponentPoolSize = scalars[12];
    betaGwentCleanupPending090 = scalars[13] == 1;
    betaGwentScraps = scalars[14];
    if (format == 2) betaGwentCollectionRecoverySchema = scalars[17];
    if (format == 2) betaGwentCollectionRecoveryOriginalSchema = scalars[18];
    if (format == 2) betaGwentDeckRecoverySchema = scalars[19];
    if (format == 2) betaGwentDeckRecoveryOriginalSchema = scalars[20];
    if (format == 2) betaGwentStarterDeckRecoverySchema = scalars[22];
    if (format == 2) betaGwentStarterDeckRecoveryOriginalSchema = scalars[23];
    if (format == 2) betaGwentStoreRecoverySchema = scalars[25];
    pos = 0;
    betaGwentDeckNames.Clear();
    for (i = 0; i < names; i += 1) { betaGwentDeckNames.PushBack(text[pos]); pos += 1; }
    betaGwentStarterDeckNames.Clear();
    for (i = 0; i < starterNames; i += 1) { betaGwentStarterDeckNames.PushBack(text[pos]); pos += 1; }
    if (format == 2)
    {
        betaGwentDeckRecoveryNames.Clear();
        for (i = 0; i < deckNames; i += 1) { betaGwentDeckRecoveryNames.PushBack(text[pos]); pos += 1; }
        betaGwentStarterDeckRecoveryNames.Clear();
        for (i = 0; i < starterRecoveryNames; i += 1) { betaGwentStarterDeckRecoveryNames.PushBack(text[pos]); pos += 1; }
        betaGwentStoreRecoveryText.Clear();
        for (i = 0; i < rawNames; i += 1) { betaGwentStoreRecoveryText.PushBack(text[pos]); pos += 1; }
    }
    betaGwentStoreWritable = true;
    LogChannel('BetaGwent', "PROFILE_STORE_LOADED format=" + format + " commit=" + betaGwentStore[5] + " ints=" + betaGwentStore.Size());
    return true;
}

// Catch-all: the store is current whenever the game writes a save.
@wrapMethod(CR4Game)
function OnSaveStarted(type : ESaveGameType)
{
    var player : W3PlayerWitcher;
    player = (W3PlayerWitcher)thePlayer;
    if (player) player.BetaGwentStoreCommit();
    wrappedMethod(type);
}

// Stage 131: mirror of the Beta Gwent profile in the game's facts database.
// Fields added with @addField are written to a save only while the mod is installed: a save
// made without the mod (for example while testing another Gwent mod) loses them. Facts are part
// of the base game and survive such a save, so the profile is restored from this mirror when
// the profile fields come back empty.
// Stage 136 (format 2): two banks written alternately. A bank is marked complete only after
// its content and checksum are written, and becomes current last, so the previous complete
// copy is never touched while a new one is written. Restore reads the whole bank into locals,
// validates it (count limits, unique card IDs, copy limits, deck shapes, checksum) and changes
// the profile only after every check has passed. A mirror that exists but fails validation is
// never applied and never overwritten in this save line ("bg_b2_hold").
// The mirror also covers settings, the opponent rotation, the progression seed and an
// unfinished paid keg choice. Reward ledgers are mirrored by separate monotonic facts:
// card rewards per NPC ("bg_bkn_<runtime id>") and quest rewards ("bg_bkq_<deck>").
// Deck names are text and cannot be stored as facts; restored decks get default names.
@addField(W3PlayerWitcher)
private var betaGwentBkA : int;
@addField(W3PlayerWitcher)
private var betaGwentBkB : int;

@addMethod(W3PlayerWitcher)
private function BetaGwentBkMix(value : int)
{
    var v : int;
    v = value % 65521; if (v < 0) v += 65521;
    betaGwentBkA = (betaGwentBkA + v) % 65521; betaGwentBkB = (betaGwentBkB + betaGwentBkA) % 65521;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentBkPut(key : string, value : int) { FactsSet(key, value); BetaGwentBkMix(value); }
@addMethod(W3PlayerWitcher)
private function BetaGwentBkGet(key : string) : int
{ var value : int; value = FactsQueryLatestValue(key); BetaGwentBkMix(value); return value; }

// Monotonic reward ledgers: a value is only ever raised, never lowered.
@addMethod(W3PlayerWitcher)
public function BetaGwentMirrorNpcWins(npcId : int, wins : int)
{
    var key : string;
    if(BetaGwentCleanupPending())return;
    if (npcId == 0) return;
    key = "bg_bkn_" + npcId;
    if (FactsQueryLatestValue(key) - 1 < Min(4, wins)) FactsSet(key, Min(4, wins) + 1);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentMirroredNpcWins(npcId : int) : int
{
    // Used only after a restore from the mirror: in ordinary play the saved ledger decides.
    if (npcId == 0 || FactsQueryLatestValue("bg_b2_restored") <= 0) return 0;
    return Clamp(FactsQueryLatestValue("bg_bkn_" + npcId) - 1, 0, 4);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentMirrorQuestReward(deck : name) {
    if(BetaGwentCleanupPending())return; FactsSet("bg_bkq_" + NameToString(deck), 1); }
@addMethod(W3PlayerWitcher)
public function BetaGwentMirroredQuestReward(deck : name) : bool { return FactsQueryLatestValue("bg_bkq_" + NameToString(deck)) > 0; }
@addMethod(W3PlayerWitcher)
private function BetaGwentBackupRewardLedger()
{
    var seen, counts : array<int>; var i, k : int;
    for (i = 0; i < betaGwentRewardedNpcs.Size(); i += 1)
    {
        k = seen.FindFirst(betaGwentRewardedNpcs[i]);
        if (k < 0) { seen.PushBack(betaGwentRewardedNpcs[i]); counts.PushBack(1); } else counts[k] += 1;
    }
    for (i = 0; i < seen.Size(); i += 1) BetaGwentMirrorNpcWins(seen[i], counts[i]);
    for (i = 0; i < betaGwentRewardedQuests.Size(); i += 1)
        if (!BetaGwentMirroredQuestReward(betaGwentRewardedQuests[i])) BetaGwentMirrorQuestReward(betaGwentRewardedQuests[i]);
}

@addMethod(W3PlayerWitcher)
public function BetaGwentBackupProfile()
{
    var ids : array<int>; var i, slot, faction, leader, bank, generation : int; var title, p, d : string;
    if(BetaGwentCleanupPending())return;
    if (betaGwentCollectionSchema != 1 || betaGwentCollectionSeeding || betaGwentOwnedIds.Size() != betaGwentOwnedCopies.Size()) return;
    if (FactsQueryLatestValue("bg_b2_hold") > 0) { LogChannel('BetaGwent', "PROFILE_BACKUP_HELD reason=invalidMirrorKept"); return; }
    BetaGwentEnsureNewCards();
    // Preserve an unknown auxiliary schema rather than replacing its mirror.
    if(betaGwentNewCardsSchema!=1)return;
    BetaGwentBackupRewardLedger();
    bank = 3 - FactsQueryLatestValue("bg_b2_cur"); if (bank != 1 && bank != 2) bank = 1;
    p = "bg_b2_" + bank + "_";
    FactsSet(p + "done", 0);
    generation = Max(0, FactsQueryLatestValue("bg_b2_gen")) + 1;
    betaGwentBkA = 1; betaGwentBkB = 0;
    BetaGwentBkPut(p + "gen", generation);
    BetaGwentBkPut(p + "sc", Max(0, betaGwentScraps));
    BetaGwentBkPut(p + "kg", Max(0, betaGwentKegsUnopened));
    BetaGwentBkPut(p + "pf", betaGwentPreferredDeck);
    BetaGwentBkPut(p + "sd", betaGwentProgressionSeed);
    BetaGwentBkPut(p + "tm", betaGwentAnimationTempo);
    if (betaGwentReducedEffects) BetaGwentBkPut(p + "re", 1); else BetaGwentBkPut(p + "re", 0);
    BetaGwentBkPut(p + "df", betaGwentDifficulty);
    BetaGwentBkPut(p + "ap", betaGwentAiPause);
    BetaGwentBkPut(p + "cn", betaGwentOwnedIds.Size());
    for (i = 0; i < betaGwentOwnedIds.Size(); i += 1)
    { BetaGwentBkPut(p + "ci" + i, betaGwentOwnedIds[i]); BetaGwentBkPut(p + "cc" + i, betaGwentOwnedCopies[i]); }
    for (slot = 1; slot <= 13; slot += 1)
    {
        d = p + "d" + slot + "_";
        if (!BetaGwentLoadDeck(slot, ids, title, faction, leader)) { BetaGwentBkPut(d + "n", 0); continue; }
        BetaGwentBkPut(d + "n", ids.Size()); BetaGwentBkPut(d + "l", leader); BetaGwentBkPut(d + "f", faction);
        for (i = 0; i < ids.Size(); i += 1) BetaGwentBkPut(d + i, ids[i]);
    }
    BetaGwentBkPut(p + "ka", betaGwentKegAutomatic.Size());
    for (i = 0; i < betaGwentKegAutomatic.Size(); i += 1) BetaGwentBkPut(p + "ka" + i, betaGwentKegAutomatic[i]);
    BetaGwentBkPut(p + "ks", betaGwentKegAutomaticScraps.Size());
    for (i = 0; i < betaGwentKegAutomaticScraps.Size(); i += 1) BetaGwentBkPut(p + "ks" + i, betaGwentKegAutomaticScraps[i]);
    BetaGwentBkPut(p + "ko", betaGwentKegOffers.Size());
    for (i = 0; i < betaGwentKegOffers.Size(); i += 1) BetaGwentBkPut(p + "ko" + i, betaGwentKegOffers[i]);
    BetaGwentBkPut(p + "ob", betaGwentOpponentBag.Size());
    for (i = 0; i < betaGwentOpponentBag.Size(); i += 1) BetaGwentBkPut(p + "ob" + i, betaGwentOpponentBag[i]);
    BetaGwentBkPut(p + "or", betaGwentOpponentRecent.Size());
    for (i = 0; i < betaGwentOpponentRecent.Size(); i += 1) BetaGwentBkPut(p + "or" + i, betaGwentOpponentRecent[i]);
    // Format 3 extends the same two transactional banks. Format 2 has fm=0.
    BetaGwentBkPut(p + "fm", 3);
    BetaGwentBkPut(p + "fg", generation);
    BetaGwentBkPut(p + "nc", betaGwentNewCardIds.Size());
    for(i=0;i<betaGwentNewCardIds.Size();i+=1)BetaGwentBkPut(p + "ni" + i,betaGwentNewCardIds[i]);
    FactsSet(p + "sa", betaGwentBkA); FactsSet(p + "sb", betaGwentBkB);
    // Completion marker, then the bank switch: both strictly last.
    FactsSet(p + "done", generation);
    FactsSet("bg_b2_gen", generation);
    FactsSet("bg_b2_cur", bank);
    LogChannel('BetaGwent', "PROFILE_BACKUP format=3 bank=" + bank + " generation=" + generation + " distinct=" + betaGwentOwnedIds.Size() + " scraps=" + betaGwentScraps + " kegs=" + betaGwentKegsUnopened + " kegChoice=" + betaGwentKegOffers.Size());
}

@addMethod(W3PlayerWitcher)
public function BetaGwentHasProfileBackup() : bool
{
    var cur : int; cur = FactsQueryLatestValue("bg_b2_cur");
    if (cur == 1 || cur == 2) return true;
    return FactsQueryLatestValue("bg_bk_schema") == 1 && FactsQueryLatestValue("bg_bk_cn") > 1;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentBackupRejected(source : string, reason : string) : bool
{ LogChannel('BetaGwent', "PROFILE_RESTORE_REJECTED source=" + source + " reason=" + reason); return false; }
@addMethod(W3PlayerWitcher)
private function BetaGwentHoldBackup()
{
    // Keep the invalid mirror untouched; the player starts a new profile in this save line.
    FactsSet("bg_b2_hold", 1);
    LogChannel('BetaGwent', "PROFILE_RESTORE_FAILED mirror kept, new profile started");
    if (theGame && theGame.GetGuiManager())
        theGame.GetGuiManager().ShowNotification("Gwent Beta Classic: резервная копия профиля гвинта повреждена и не применена. Начат новый профиль, копия не перезаписывается. Чтобы вернуть прогресс, загрузите сохранение, сделанное с модом.", 12.0);
}
@addMethod(W3PlayerWitcher)
public function BetaGwentRestoreProfile() : bool
{
    var cur : int;
    if(BetaGwentCleanupPending())return false;
    if (betaGwentCollectionSchema != 0 || betaGwentOwnedIds.Size() != 0 || betaGwentOwnedCopies.Size() != 0) return false;
    if (FactsQueryLatestValue("bg_b2_hold") > 0) return false;
    cur = FactsQueryLatestValue("bg_b2_cur");
    if (cur == 1 || cur == 2)
    {
        // The other bank holds the previous complete generation, if any.
        if (BetaGwentRestoreBank(cur) || BetaGwentRestoreBank(3 - cur)) return true;
        BetaGwentHoldBackup(); return false;
    }
    if (FactsQueryLatestValue("bg_bk_schema") == 1 && FactsQueryLatestValue("bg_bk_cn") > 1)
    {
        if (BetaGwentRestoreLegacyProfile()) return true;
        BetaGwentHoldBackup(); return false;
    }
    return false;
}
@addMethod(W3PlayerWitcher)
private function BetaGwentRestoreBank(bank : int) : bool
{
    var ids, copies, lengths, leaders, factions, cards, deck, automatic, automaticScraps, offers, bag, recent, unseen : array<int>;
    var i, n, slot, offset, value, count, cap, generation, scraps, kegs, preferred, seed, tempo, reduced, difficulty, pause, restoredDecks, format : int;
    var p, d, source : string;
    p = "bg_b2_" + bank + "_"; source = "bank" + bank;
    generation = FactsQueryLatestValue(p + "done");
    if (generation <= 0) return BetaGwentBackupRejected(source, "incomplete");
    betaGwentBkA = 1; betaGwentBkB = 0;
    if (BetaGwentBkGet(p + "gen") != generation) return BetaGwentBackupRejected(source, "generation");
    scraps = BetaGwentBkGet(p + "sc"); kegs = BetaGwentBkGet(p + "kg"); preferred = BetaGwentBkGet(p + "pf");
    seed = BetaGwentBkGet(p + "sd"); tempo = BetaGwentBkGet(p + "tm"); reduced = BetaGwentBkGet(p + "re");
    difficulty = BetaGwentBkGet(p + "df"); pause = BetaGwentBkGet(p + "ap");
    if (scraps < 0 || kegs < 0 || kegs > 100000 || preferred < 0 || seed < 0 || reduced < 0 || reduced > 1) return BetaGwentBackupRejected(source, "values");
    n = BetaGwentBkGet(p + "cn");
    if (n < 1 || n > 1000) return BetaGwentBackupRejected(source, "collectionSize");
    for (i = 0; i < n; i += 1)
    {
        value = BetaGwentBkGet(p + "ci" + i); count = BetaGwentBkGet(p + "cc" + i); cap = BetaGwentCollectionCap(value);
        if (value <= 0 || cap <= 0 || ids.Contains(value) || count < 1 || count > cap) return BetaGwentBackupRejected(source, "collectionEntry" + i);
        ids.PushBack(value); copies.PushBack(count);
    }
    for (slot = 1; slot <= 13; slot += 1)
    {
        d = p + "d" + slot + "_"; n = BetaGwentBkGet(d + "n"); lengths.PushBack(n);
        if (n == 0) { leaders.PushBack(0); factions.PushBack(0); continue; }
        if (n < 25 || n > 40) return BetaGwentBackupRejected(source, "deck" + slot);
        leaders.PushBack(BetaGwentBkGet(d + "l")); factions.PushBack(BetaGwentBkGet(d + "f"));
        for (i = 0; i < n; i += 1) cards.PushBack(BetaGwentBkGet(d + i));
    }
    n = BetaGwentBkGet(p + "ka");
    if (n < 0 || n > 16) return BetaGwentBackupRejected(source, "kegCards");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ka" + i); if (BetaGwentCollectionCap(value) <= 0) return BetaGwentBackupRejected(source, "kegCard"); automatic.PushBack(value); }
    n = BetaGwentBkGet(p + "ks");
    if (n < 0 || (n != 0 && n != automatic.Size())) return BetaGwentBackupRejected(source, "kegScraps");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ks" + i); if (value < 0) return BetaGwentBackupRejected(source, "kegScrap"); automaticScraps.PushBack(value); }
    n = BetaGwentBkGet(p + "ko");
    if (n < 0 || n > 8) return BetaGwentBackupRejected(source, "kegOffers");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ko" + i); if (BetaGwentCollectionCap(value) <= 0 || offers.Contains(value)) return BetaGwentBackupRejected(source, "kegOffer"); offers.PushBack(value); }
    n = BetaGwentBkGet(p + "ob");
    if (n < 0 || n > 256) return BetaGwentBackupRejected(source, "opponentBag");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ob" + i); if (value <= 0) return BetaGwentBackupRejected(source, "opponent"); bag.PushBack(value); }
    n = BetaGwentBkGet(p + "or");
    if (n < 0 || n > 8) return BetaGwentBackupRejected(source, "opponentRecent");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "or" + i); if (value <= 0) return BetaGwentBackupRejected(source, "opponent"); recent.PushBack(value); }
    format=FactsQueryLatestValue(p + "fm");
    // Old mod versions reuse these banks without clearing extension keys.
    // Match the extension to its generation before interpreting it.
    if(FactsQueryLatestValue(p + "fg")!=generation)format=0;
    if(format!=0 && format!=3)return BetaGwentBackupRejected(source,"format");
    if(format==3){
        if(BetaGwentBkGet(p + "fm")!=3)return BetaGwentBackupRejected(source,"format");
        if(BetaGwentBkGet(p + "fg")!=generation)return BetaGwentBackupRejected(source,"formatGeneration");
        n=BetaGwentBkGet(p + "nc");
        if(n<0 || n>ids.Size())return BetaGwentBackupRejected(source,"newCardCount");
        for(i=0;i<n;i+=1){value=BetaGwentBkGet(p + "ni" + i);
            if(!ids.Contains(value) || unseen.Contains(value))return BetaGwentBackupRejected(source,"newCardEntry");
            unseen.PushBack(value);
        }
    }
    if (FactsQueryLatestValue(p + "sa") != betaGwentBkA || FactsQueryLatestValue(p + "sb") != betaGwentBkB) return BetaGwentBackupRejected(source, "checksum");

    // Every check passed: apply. Fields that are already set are never overwritten.
    betaGwentCollectionSeeding = true; betaGwentCollectionSchema = 1;
    betaGwentOwnedIds = ids; betaGwentOwnedCopies = copies;
    betaGwentNewCardsSchema=1;betaGwentNewCardIds=unseen;
    betaGwentStarterSetRevision = BetaGwentStarterRevision();
    if (betaGwentScraps <= 0) betaGwentScraps = scraps;
    if (betaGwentKegsUnopened <= 0) betaGwentKegsUnopened = kegs;
    if (betaGwentProgressionSeed <= 0 && seed > 0) betaGwentProgressionSeed = seed;
    if (betaGwentAnimationTempo == 0) betaGwentAnimationTempo = tempo;
    if (!betaGwentReducedEffects && reduced == 1) betaGwentReducedEffects = true;
    if (betaGwentDifficulty == 0) betaGwentDifficulty = difficulty;
    if (betaGwentAiPause == 0) betaGwentAiPause = pause;
    for (slot = 1; slot <= 13; slot += 1)
    {
        n = lengths[slot - 1]; if (n == 0) continue;
        deck.Clear(); for (i = 0; i < n; i += 1) deck.PushBack(cards[offset + i]);
        offset += n;
        if (BetaGwentStoreDeck(slot, deck, "Колода " + slot, factions[slot - 1], leaders[slot - 1])) restoredDecks += 1;
    }
    // The paid keg choice is restored with the cards it already granted.
    if (betaGwentKegOffers.Size() == 0 && offers.Size() > 0)
    { betaGwentKegAutomatic = automatic; betaGwentKegAutomaticScraps = automaticScraps; betaGwentKegOffers = offers; }
    if (betaGwentOpponentBag.Size() == 0 && betaGwentOpponentRecent.Size() == 0) { betaGwentOpponentBag = bag; betaGwentOpponentRecent = recent; }
    if (preferred > 0 && betaGwentPreferredDeck == 0) betaGwentPreferredDeck = preferred;
    betaGwentCollectionSeeding = false;
    FactsSet("bg_b2_restored", 1);
    LogChannel('BetaGwent', "PROFILE_RESTORED format="+(format==3?3:2)+" bank=" + bank + " generation=" + generation + " distinct=" + betaGwentOwnedIds.Size() + " decks=" + restoredDecks + " scraps=" + betaGwentScraps + " kegs=" + betaGwentKegsUnopened + " kegChoice=" + betaGwentKegOffers.Size());
    return true;
}
// Format 1 (0.5.1–0.5.4): no checksum or completion marker. Same validation, staged apply.
@addMethod(W3PlayerWitcher)
private function BetaGwentRestoreLegacyProfile() : bool
{
    var ids, copies, deck : array<int>; var i, count, slot, length, value, cap, restoredDecks : int; var prefix : string;
    count = FactsQueryLatestValue("bg_bk_cn") - 1;
    if (count < 1 || count > 1000) return BetaGwentBackupRejected("legacy", "collectionSize");
    for (i = 0; i < count; i += 1)
    {
        value = FactsQueryLatestValue("bg_bk_ci_" + i); cap = BetaGwentCollectionCap(value); length = FactsQueryLatestValue("bg_bk_cc_" + i);
        if (value <= 0 || cap <= 0 || ids.Contains(value) || length < 1 || length > cap) return BetaGwentBackupRejected("legacy", "collectionEntry" + i);
        ids.PushBack(value); copies.PushBack(length);
    }
    betaGwentCollectionSeeding = true; betaGwentCollectionSchema = 1;
    betaGwentOwnedIds = ids; betaGwentOwnedCopies = copies;
    betaGwentStarterSetRevision = BetaGwentStarterRevision();
    if (betaGwentScraps <= 0) betaGwentScraps = Max(0, FactsQueryLatestValue("bg_bk_scraps") - 1);
    if (betaGwentKegsUnopened <= 0) betaGwentKegsUnopened = Max(0, FactsQueryLatestValue("bg_bk_kegs") - 1);
    for (slot = 1; slot <= 13; slot += 1)
    {
        prefix = "bg_bk_d" + slot + "_"; length = FactsQueryLatestValue(prefix + "n") - 1;
        if (length < 25 || length > 40) continue;
        deck.Clear(); for (i = 0; i < length; i += 1) deck.PushBack(FactsQueryLatestValue(prefix + i));
        if (BetaGwentStoreDeck(slot, deck, "Колода " + slot, FactsQueryLatestValue(prefix + "f"), FactsQueryLatestValue(prefix + "l"))) restoredDecks += 1;
    }
    value = FactsQueryLatestValue("bg_bk_pref") - 1; if (value > 0 && betaGwentPreferredDeck == 0) betaGwentPreferredDeck = value;
    betaGwentNewCardsSchema=1;betaGwentNewCardIds.Clear();
    betaGwentCollectionSeeding = false;
    FactsSet("bg_b2_restored", 1);
    LogChannel('BetaGwent', "PROFILE_RESTORED format=1 distinct=" + betaGwentOwnedIds.Size() + " decks=" + restoredDecks + " scraps=" + betaGwentScraps + " kegs=" + betaGwentKegsUnopened);
    return true;
}

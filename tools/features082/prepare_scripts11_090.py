"""0.9.0 build 11 scripts: profile backup that can always recover.

Player report (0.8.1, Next-Gen with W3MM + Script Merger + Brothers in Arms):
the collection resets to the starter set on every load. Log: the profile
fields come back empty on each load (COLLECTION_INITIALIZED every session)
and the facts mirror never helps because an earlier failed restore froze it
for good ("PROFILE_BACKUP_HELD reason=invalidMirrorKept" on every backup).

* No permanent freeze: a failed restore logs the reason, starts a new profile
  and backups continue (overwriting the invalid banks). A freeze flag left by an
  older version is cleared on the first backup and ignored by restore.
* Tolerant restore: an unknown card or extra copies (catalog changed between
  versions) no longer reject the whole bank. Such entries are dropped or
  clamped to the copy limit, invalid decks are skipped by BetaGwentStoreDeck,
  a damaged keg choice is not restored. Structure, counts and the checksum
  stay strict.
* One diagnostic line when the profile fields are found empty.
* The failure notification is bilingual (it was Russian only).
Output: BetaGwent/build/release090-scripts11/scripts.
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'BetaGwent/build/release090-final7/scripts'
OUT = ROOT / 'BetaGwent/build/release090-scripts11'
BACKUP = 'game/betagwent/profileBackup.ws'
COLLECTION = 'game/betagwent/collectionProfile.ws'
NL = '\n'

RESTORE_BANK = r'''private function BetaGwentRestoreBank(bank : int) : bool
{
    var ids, copies, lengths, leaders, factions, cards, deck, automatic, automaticScraps, offers, bag, recent, unseen : array<int>;
    var i, n, slot, offset, value, count, cap, generation, scraps, kegs, preferred, seed, tempo, reduced, difficulty, pause, restoredDecks, format, automaticCount, dropped : int;
    var kegValid : bool;
    var p, d, source : string;
    p = "bg_b2_" + bank + "_"; source = "bank" + bank;
    generation = FactsQueryLatestValue(p + "done");
    if (generation <= 0) return BetaGwentBackupRejected(source, "incomplete");
    betaGwentBkA = 1; betaGwentBkB = 0;
    if (BetaGwentBkGet(p + "gen") != generation) return BetaGwentBackupRejected(source, "generation");
    scraps = BetaGwentBkGet(p + "sc"); kegs = BetaGwentBkGet(p + "kg"); preferred = BetaGwentBkGet(p + "pf");
    seed = BetaGwentBkGet(p + "sd"); tempo = BetaGwentBkGet(p + "tm"); reduced = BetaGwentBkGet(p + "re");
    difficulty = BetaGwentBkGet(p + "df"); pause = BetaGwentBkGet(p + "ap");
    // Settings are optional: out-of-range values fall back to defaults instead of rejecting the bank.
    if (scraps < 0) scraps = 0;
    if (kegs < 0 || kegs > 100000) kegs = 0;
    if (preferred < 0) preferred = 0;
    if (seed < 0) seed = 0;
    if (reduced < 0 || reduced > 1) reduced = 0;
    n = BetaGwentBkGet(p + "cn");
    if (n < 1 || n > 1000) return BetaGwentBackupRejected(source, "collectionSize");
    for (i = 0; i < n; i += 1)
    {
        value = BetaGwentBkGet(p + "ci" + i); count = BetaGwentBkGet(p + "cc" + i); cap = BetaGwentCollectionCap(value);
        // Catalog changes between versions: drop unknown cards and clamp extra copies.
        if (value <= 0 || cap <= 0 || count < 1 || ids.Contains(value)) { dropped += 1; continue; }
        if (count > cap) { count = cap; dropped += 1; }
        ids.PushBack(value); copies.PushBack(count);
    }
    if (ids.Size() == 0) return BetaGwentBackupRejected(source, "collectionEmpty");
    for (slot = 1; slot <= 13; slot += 1)
    {
        d = p + "d" + slot + "_"; n = BetaGwentBkGet(d + "n");
        if (n < 0 || n > 1000) return BetaGwentBackupRejected(source, "deck" + slot);
        if (n == 0) { lengths.PushBack(0); leaders.PushBack(0); factions.PushBack(0); continue; }
        leaders.PushBack(BetaGwentBkGet(d + "l")); factions.PushBack(BetaGwentBkGet(d + "f"));
        for (i = 0; i < n; i += 1) cards.PushBack(BetaGwentBkGet(d + i));
        lengths.PushBack(n);
    }
    kegValid = true;
    automaticCount = BetaGwentBkGet(p + "ka");
    if (automaticCount < 0 || automaticCount > 16) return BetaGwentBackupRejected(source, "kegCards");
    for (i = 0; i < automaticCount; i += 1) { value = BetaGwentBkGet(p + "ka" + i); if (BetaGwentCollectionCap(value) <= 0) kegValid = false; automatic.PushBack(value); }
    n = BetaGwentBkGet(p + "ks");
    if (n < 0 || n > 16) return BetaGwentBackupRejected(source, "kegScraps");
    if (n != 0 && n != automaticCount) kegValid = false;
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ks" + i); if (value < 0) kegValid = false; automaticScraps.PushBack(value); }
    n = BetaGwentBkGet(p + "ko");
    if (n < 0 || n > 8) return BetaGwentBackupRejected(source, "kegOffers");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ko" + i); if (BetaGwentCollectionCap(value) <= 0 || offers.Contains(value)) kegValid = false; offers.PushBack(value); }
    n = BetaGwentBkGet(p + "ob");
    if (n < 0 || n > 256) return BetaGwentBackupRejected(source, "opponentBag");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "ob" + i); if (value > 0) bag.PushBack(value); }
    n = BetaGwentBkGet(p + "or");
    if (n < 0 || n > 8) return BetaGwentBackupRejected(source, "opponentRecent");
    for (i = 0; i < n; i += 1) { value = BetaGwentBkGet(p + "or" + i); if (value > 0) recent.PushBack(value); }
    format=FactsQueryLatestValue(p + "fm");
    // Old mod versions reuse these banks without clearing extension keys.
    // Match the extension to its generation before interpreting it.
    if(FactsQueryLatestValue(p + "fg")!=generation)format=0;
    if(format!=0 && format!=3)return BetaGwentBackupRejected(source,"format");
    if(format==3){
        if(BetaGwentBkGet(p + "fm")!=3)return BetaGwentBackupRejected(source,"format");
        if(BetaGwentBkGet(p + "fg")!=generation)return BetaGwentBackupRejected(source,"formatGeneration");
        n=BetaGwentBkGet(p + "nc");
        if(n<0 || n>1000)return BetaGwentBackupRejected(source,"newCardCount");
        for(i=0;i<n;i+=1){value=BetaGwentBkGet(p + "ni" + i);
            if(ids.Contains(value) && !unseen.Contains(value))unseen.PushBack(value);
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
        // BetaGwentStoreDeck validates the deck; an invalid one is skipped, not fatal.
        if (BetaGwentStoreDeck(slot, deck, "Колода " + slot, factions[slot - 1], leaders[slot - 1])) restoredDecks += 1;
    }
    // The paid keg choice is restored with the cards it already granted, only if intact.
    if (kegValid && betaGwentKegOffers.Size() == 0 && offers.Size() > 0)
    { betaGwentKegAutomatic = automatic; betaGwentKegAutomaticScraps = automaticScraps; betaGwentKegOffers = offers; }
    if (betaGwentOpponentBag.Size() == 0 && betaGwentOpponentRecent.Size() == 0) { betaGwentOpponentBag = bag; betaGwentOpponentRecent = recent; }
    if (preferred > 0 && betaGwentPreferredDeck == 0) betaGwentPreferredDeck = preferred;
    betaGwentCollectionSeeding = false;
    FactsSet("bg_b2_restored", 1);
    LogChannel('BetaGwent', "PROFILE_RESTORED format="+(format==3?3:2)+" bank=" + bank + " generation=" + generation + " distinct=" + betaGwentOwnedIds.Size() + " decks=" + restoredDecks + " scraps=" + betaGwentScraps + " kegs=" + betaGwentKegsUnopened + " kegChoice=" + betaGwentKegOffers.Size() + " dropped=" + dropped + " kegValid=" + (kegValid?1:0));
    return true;
}
'''

HOLD = r'''private function BetaGwentHoldBackup()
{
    // 0.9.0: no permanent freeze. The invalid banks are rejected, a new profile
    // starts, and the next backups overwrite them so later loads can recover.
    LogChannel('BetaGwent', "PROFILE_RESTORE_FAILED new profile started, backups continue");
    if (theGame && theGame.GetGuiManager())
        theGame.GetGuiManager().ShowNotification("Gwent Beta Classic: the Gwent profile backup could not be applied, a new profile was started. / Резервную копию профиля гвинта применить не удалось, начат новый профиль.", 12.0);
}
'''


def patch_backup(s):
    old = '    if (FactsQueryLatestValue("bg_b2_hold") > 0) { LogChannel(\'BetaGwent\', "PROFILE_BACKUP_HELD reason=invalidMirrorKept"); return; }\n'
    assert s.count(old) == 1
    s = s.replace(old, '    // Older versions froze the mirror forever after a failed restore; lift that freeze.\n'
                       '    if (FactsQueryLatestValue("bg_b2_hold") > 0) { FactsRemove("bg_b2_hold"); LogChannel(\'BetaGwent\', "PROFILE_BACKUP_HOLD_CLEARED"); }\n')
    old = '    if (FactsQueryLatestValue("bg_b2_hold") > 0) return false;\n'
    assert s.count(old) == 1
    s = s.replace(old, '')
    a = s.index('private function BetaGwentRestoreBank(bank : int) : bool')
    b = s.index('// Format 1 (0.5.1', a)
    s = s[:a] + RESTORE_BANK + s[b:]
    a = s.index('private function BetaGwentHoldBackup()')
    b = s.index('@addMethod', a)
    s = s[:a] + HOLD + s[b:]
    old = '// never applied and never overwritten in this save line ("bg_b2_hold").'
    assert s.count(old) == 1
    s = s.replace(old, '// never applied; since 0.9.0 it is overwritten by the next backup (no "bg_b2_hold" freeze).')
    assert 'PROFILE_BACKUP_HELD' not in s and s.count('bg_b2_hold') == 3
    return s


def patch_collection(s):
    old = '    // Profile fields lost by a save made without the mod: restore from the facts mirror.\n'
    assert s.count(old) == 1
    s = s.replace(old, old + '    LogChannel(\'BetaGwent\',"PROFILE_FIELDS_EMPTY cur="+FactsQueryLatestValue("bg_b2_cur")+" gen="+FactsQueryLatestValue("bg_b2_gen")+" hold="+FactsQueryLatestValue("bg_b2_hold")+" legacy="+FactsQueryLatestValue("bg_bk_schema"));\n')
    return s


def main():
    assert not OUT.exists(), 'Fresh output folder required'
    shutil.copytree(SOURCE, OUT / 'scripts')
    for name, fix in [(BACKUP, patch_backup), (COLLECTION, patch_collection)]:
        p = OUT / 'scripts' / name
        raw = p.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); crlf = b'\r\n' in raw
        s = fix(raw.decode('utf-8-sig').replace('\r\n', '\n'))
        if crlf: s = s.replace('\n', '\r\n')
        p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.encode('utf8'))
    print('Prepared build 11 scripts: recoverable profile backup.')


if __name__ == '__main__':
    main()

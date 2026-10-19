# Gwent Beta Classic 0.9.0 — Changelog

## Deck sharing

- Clipboard import and export using BG1 codes. Codes are language-independent and contain the faction, leader and card list for sharing between players.
- Import from the deck list or editor; export from the editor. Copy writes the code directly to the Windows clipboard (optional Optional-CopyButton folder, see below).
- Added Windows → game paste: Import reads the code on opening, with Paste and with Ctrl+V. Requires the updated GwentBetaClipboard.asi from Optional-CopyButton. Busy clipboards and invalid codes preserve the entered text.
- Import and Export appear only when Optional-CopyButton is installed; without it both buttons are hidden.
- Invalid codes leave decks, collection and balance unchanged. Validation covers card IDs, faction, leader, deck size and composition limits.
- Missing cards, including the leader, are shown as cards with copy counts: craft each one, or all at once for the total scrap cost. Import stays locked until nothing is missing; an unfinished paid keg choice blocks crafting.
- Import creates a draft. Save it with the usual button; occupied custom slots are never overwritten automatically.

## Console

- Added help, collection status, card search, card/leader/faction grants, keg and scrap grants, and innkeeper keg stock diagnostics and refill.
- Normal copy limits are enforced; invalid parameters and counter overflow are rejected. Resource grants are blocked in menus and matches; shop commands require an open shop.

## Interface and controller

- Card inspection now follows Beta: a full screen with name, tags, flavour text, power and ability on the left, the large card on the right and Back below. In the collection and editor, ←/→ browse neighbouring cards.
- Card inspection uses the original Beta 0.9.24 faction banners on the large card (factions, neutral cards and leaders), shows the base power in white and a readable flavour line. Deck screens show the same banner.
- Tutorial expanded to 10 pages (mulligan and draws, rows and neighbours, card statuses) with more space around the content.
- Fixed stray lines from the screen corner when previewing area targets; doomed units no longer show a cross badge.
- Myrgtabrakke deals 2 damage three times and Harald the Cripple's ability hits ten times, as in the Beta 0.9.24 card data.
- New deck exchange labels and messages translated into all 13 text languages, with missing Japanese, Korean and Chinese font glyphs added.
- Deck-list Import moved into the bottom action bar. Editor actions are aligned; deck status, counters and Undo have dedicated space and padding.
- Updated spacing in match menus, exit and exchange dialogs, confirmation titles and controller hints.
- Down from the bottom visible shelf row moves focus to actions, including Save; Up returns to cards. LB/RB and the right stick still scroll.
- Fixed opening Import and Export directly from the deck editor.

## Visuals and audio

- Dead cards that go to the graveyard now fly toward their actual side's graveyard; special cards do the same after resolution. Played units remain on the board as required by the rules. Banish, dissolve and consume effects are preserved.
- Leader portraits continue their normal animation after the one-shot VS entrance. Temporary page-load failures can retry.
- Arachas Queen's entrance is synchronized with the actual start of her voice, including seat order, queued lines, skipping and disabled voices.
- Classic 1.32 includes the accepted fixes for persistent frost, visible projectiles and impacts.

## Saves and compatibility

- Integrated 203 missing legacy Redux item definitions for normal games and New Game+, preserving 197 native definitions. This protects loading old inventory; it neither recovers already lost data nor converts Redux collections.
- All 13 text languages, five voice languages and independent text/voice selection are retained. Classic 1.32 and Next-Gen 5.0+ use separate packages.

## AI and interface update

- Row choice and armour/weather forecasts, catch-up economy, translated button fitting after font loading, multiline history and input/history window spacing.

## Isengrim: Outlaw

Isengrim: Outlaw now compares the actual special-card and Create branches, including when pulled by Royal Decree. The AI rejects Decoy without a legal allied Bronze or Silver target and estimates Create from its random three-card offer, without reading future random choices.

## Built-in cleanup before uninstalling

Cleanup is included in the main 0.9.0 mod. No separate cleaner download is needed. Back up your save, finish Gwent, leave combat and close all menus. With the main mod still installed, bg_clean_preview() shows instructions without changing data. Explicitly confirm with:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

This clears the Beta collection, decks, scraps, kegs, settings, known reward ledgers, both backup banks and betagwent_* items in the player's current inventory. A saved uninstall flag prevents starter grants and backup restoration, including after reloading with the mod still installed. Save to a NEW slot, exit the game, remove this mod's folders (including its Classic DLC), rebuild affected Script Merger merges, load the new slot and save again. To cancel, load your original backup. If some Beta item stacks cannot be removed, cleanup reports INCOMPLETE instead of success: drop or sell them and run the command again. When uninstalling, also delete the Optional-CopyButton files if you installed them: bin\…\plugins\GwentBetaClipboard.asi and the dinput8.dll from this mod (not another mod's).

Completed quests, achievements and spent crowns are not rolled back. The command does not traverse unloaded merchants, stash or world containers; retrieve Beta items first. Orphaned reward facts can require the included read-only save_fact_index.py and bg_clean_keys('…') after confirmation. See BetaGwentDocs/CLEANUP_EN.md. This is profile cleanup, not a certification that every historical byte of an arbitrary save has been erased.

## BG1

Export shows a language-independent BG1 code. Copy puts it into the Windows clipboard. To paste into the game, copy the complete code in Windows and open Import: it reads the code on opening, while Paste or Ctrl+V reads it again. Pasting validates the code; Import and Save remain separate actions. Invalid codes or a busy clipboard leave the entered text unchanged.

Both buttons need the optional Optional-CopyButton folder from the archive: copy its bin folder into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe). Update an older GwentBetaClipboard.asi: previous versions only copied from the game. The mod itself works without it. If another mod already has its own dinput8.dll, keep it and let that mod's ASI loader load GwentBetaClipboard.asi. Without these files the Import and Export buttons are hidden. With them, codes can also be typed manually.

Missing cards, including the leader, are shown as cards: craft each one or all at once for the total scrap cost. Import stays locked until nothing is missing. Import builds a draft: use Save Deck to keep it. Import from the deck list uses a free custom slot and does not overwrite occupied slots. In training, the existing unrestricted collection is used.

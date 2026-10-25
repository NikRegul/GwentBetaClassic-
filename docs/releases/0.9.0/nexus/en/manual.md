# Gwent Beta Classic 0.9.0 — English

> Version 0.9.0 — separate packages for Classic 1.32 and Next-Gen 5.0+.

## Important

Back up your saves before installing and before every update. The mod is in active development, so use a separate save for your first matches.

Card texts use the official Beta localization. The mod interface includes AI-assisted translations and may contain wording errors. Deck exchange messages are available in all 13 text languages; some older hints still fall back to English. Suggestions for better translations are welcome.

**Steam Deck:** the mod works on Steam Deck (tested by the author).

## New in 0.9.0

- Export displays a language-independent BG1 text code.
- Console commands for collection resources, card lookup, faction collections and innkeeper keg stock.
- Cards sent to the graveyard now fly toward their actual graveyard; resolved special cards do the same. Banish and dissolve effects are preserved.
- Built-in definitions for legacy Redux inventory items help prevent inventory/body loss when loading an older save after switching mods. They cannot recover inventory already lost and saved.
- Reworked menu spacing, deck status text and action buttons; controller navigation can reach Save from the visible card shelf and return to cards.
- Leader portraits continue animating after their VS entrance. Arachas Queen's entrance starts with her voice playback. Classic 1.32 includes the frost and attack effect fixes.
- Full card view in the Beta style: a large card with the original Beta 0.9.24 faction banner (factions, neutral cards and leaders), base power, readable flavour text, highlighted keywords and ←/→ browsing.
- Paste a deck code from the Windows clipboard on the Import screen (Paste button or Ctrl+V; requires Optional-CopyButton).
- Tutorial expanded to 10 pages: mulligan and draws, rows and neighbours, card statuses.
- Card fixes matching Beta: Myrgtabrakke deals 2 damage three times, Harald the Cripple's ability hits ten times.
- Improved backup handling for the collection and decks. This may help with some cases of lost progress; recovery depends on the data available in the backup.


## AI and interface

The AI has revised Igni and Yrden evaluation, Birna weather forecasts and armour interactions, including the Redanian Knight, Elite and Squire. After the opponent passes, catch-up follows real plays, deaths, armour and turn boundaries; a final pass does not grant an extra engine tick. Forecasts consider the available turns, rather than treating every weather card as guaranteed full-duration damage. An armour break that gives the enemy +5 can be a bad target.

In round one, a one-card disadvantage can be worthwhile; two cards require context, and optional post-pass chasing stops before a three-card disadvantage. Avoiding match defeat takes priority. Opponents' future cards are unknown: these are improved decisions, not a guarantee of perfect play. Translated buttons now fit again after fonts load; editor actions, history and input windows have revised spacing.

Isengrim: Outlaw now compares the actual special-card and Create branches, including when pulled by Royal Decree. The AI rejects Decoy without a legal allied Bronze or Silver target and estimates Create from its random three-card offer, without reading future random choices.

## About the mod

Gwent Beta Classic replaces vanilla Gwent in The Witcher 3 with the cards, rules and board of standalone Gwent Beta 0.9.24. Matches stay part of the Witcher world: play against NPCs, finish quests, buy kegs and build your own decks.

## Features

- 479 collectible cards, including 21 leaders, across all five factions
- Beta board, HUD, fonts, card frames, weather and effects; animated leaders
- Deck builder: five editable starter decks plus eight custom slots, filters and search
- Opponents with 46 Beta deck archetypes and three AI difficulty levels
- Kegs for 200 crowns from every innkeeper, opened Beta-style
- Scraps: craft cards for 30 / 80 / 200 / 800 by rarity; extra copies are milled automatically
- Tutorial, mulligan, graveyard and deck viewers, full card inspection
- Mouse, keyboard and controller support

## Sharing decks

Export shows a language-independent BG1 code. Copy puts it straight into the Windows clipboard; paste it anywhere with Ctrl+V. This needs the optional Optional-CopyButton folder from the archive: copy its bin folder into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe). The mod itself works without it. If another mod already has its own dinput8.dll, keep it and let that mod's ASI loader load GwentBetaClipboard.asi. Without these files the Import and Export buttons are hidden. Import accepts the complete BG1 code in its text field.

Missing cards, including the leader, are shown as cards: craft each one or all at once for the total scrap cost. Import stays locked until nothing is missing. Import builds a draft: use Save Deck to keep it. Import from the deck list uses a free custom slot and does not overwrite occupied slots. In training, the existing unrestricted collection is used.

## Console commands

Use bg_help() for help and bg_status() for your collection, kegs and scraps. bg_find('Imlerith') searches card names and IDs; bg_card(132102,1) grants a card, bg_faction('monsters') grants a faction, and bg_leaders() / bg_allcards() fill the leader/full collection up to normal copy limits. bg_kegs(10) and bg_scraps(1000) add resources. Resource grants require a loaded save outside menus and matches; save the game normally afterward. With an innkeeper's shop open, bg_shopcheck() diagnoses keg stock and bg_shoprefill(5) brings it up to five rather than adding five on every call. The game console must already be enabled.

```text
bg_help()
bg_status()
bg_find('Imlerith')
bg_card(132102,1)
bg_faction('monsters')
bg_leaders()
bg_allcards()
bg_kegs(10)
bg_scraps(1000)
bg_shopcheck()
bg_shoprefill(5)
```

## Languages

Text: English, Russian, German, French, Italian, Polish, Spanish (Spain), Spanish (Latin America), Portuguese (Brazil), Japanese, Korean, Simplified Chinese and Traditional Chinese. Switch any time with the text language button at the top left of the deck and collection menus or in the battle settings; your choice is saved.

Each package includes RU, EN, DE, IT and PT-BR voices. Select Text and Voice independently using the two separate buttons in the mod's deck/collection menu; the choices are also available in the match settings. Switching voices does not require reinstalling files. Auto follows the game's current text and speech languages separately; if a language is unavailable, English is used. Save the game normally after choosing: preferences belong to that save and remain when the mod files are updated. An existing manual text choice is preserved. In DE and IT, some keg-troll lines retain the Russian fallback from the source recordings. Native item names still follow the game language, and some notifications outside the mod UI remain RU/EN.

## Installation

1. Close the game and back up your saves. Download the package for your game branch: 1.32 or Next-Gen (5.0+). Install only one Beta Gwent version.

2. When updating, move the previous Beta Gwent mod folder outside Mods first. Do not remove the entire Mods folder or mix files from different versions.

3. Copy Mods from the archive into the game directory, next to bin and content. Optional: copy bin from Optional-CopyButton (Copy button). For Classic 1.32, also copy the included DLC folder. Paths: Mods/modBetaGwentClassic132/content and DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items for 1.32; Mods/modBetaGwent0924/content for Next-Gen. Replace only this mod's previous folders, keeping your other mods and DLC.

4. Load your save. Open the normal Gwent deck menu to edit decks and choose text/voices, or talk to a Gwent-playing NPC to start a match. Save normally to retain your preferences.

## Why Classic 1.32 is larger and needs the DLC folder

Download one package for your game version. Classic is about 623 MB, Next-Gen about 448 MB; both have the same cards and AI. Classic uses a different native resource format and an older loader with an approximately 32 MiB limit per asynchronously loaded resource. Its graphics need separate pages and texture bindings; ZIP compression cannot bypass that limit.

Classic must include both Mods/modBetaGwentClassic132 and DLC/dlcBetaGwentClassic132Assets + DLC/dlcBetaGwentClassic132Items. The DLC folder supplies essential graphics and loader registration, including leader entrance pages; it adds no story content and does not replace either official expansion. About 105 MB of the Classic download belongs to this folder; the remaining size difference comes from resource preparation for the old engine. Next-Gen uses Mods/modBetaGwent0924. Players do not need REDkit, Wwise or build tools.

## Requirements

The Witcher 3 on PC. Choose the separate build for Classic 1.32 or Next-Gen (package labelled 5.0+). REDkit, Wwise and an EXE installer are not needed to play.

## Compatibility

Legacy Redux item definitions are included for save loading; remove the obsolete modBetaGwentReduxCompat folder. When switching from Redux, use a backed-up save from before any inventory/body loss: definitions cannot restore data already lost. Redux cards are not converted into the Beta collection, and this is not a promise of compatibility with every Redux/Redo Expansion feature. Other Gwent overhauls and mods changing its menus, trading or rewards may conflict. After changing mods, rebuild conflicting script merges with Script Merger.

## Redux: what the compatibility layer does

The audited list contains 400 legacy item names: 197 keep their native definitions and 203 missing definitions are supplied as inert placeholders, for both normal games and New Game+. They are hidden, weightless and have no value, equipment slots or abilities. This helps the engine recognize old inventory entries after switching mods. It does not convert Redux cards into the Beta collection, recover inventory already lost and saved, or establish compatibility with every Redux/Redo feature. Use a save from before any loss; remove the obsolete modBetaGwentReduxCompat folder. If legacy Redux items remain when uninstalling, restore their original definition provider before loading.

## Built-in cleanup before uninstalling

Cleanup is included in the main 0.9.0 mod. No separate cleaner download is needed. Back up your save, finish Gwent, leave combat and close all menus. With the main mod still installed, bg_clean_preview() shows instructions without changing data. Explicitly confirm with:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

This clears the Beta collection, decks, scraps, kegs, settings, known reward ledgers, both backup banks and betagwent_* items in the player's current inventory. A saved uninstall flag prevents starter grants and backup restoration, including after reloading with the mod still installed. Save to a NEW slot, exit the game, remove this mod's folders (including its Classic DLC), rebuild affected Script Merger merges, load the new slot and save again. To cancel, load your original backup. If some Beta item stacks cannot be removed, the game shows INCOMPLETE instead of success: drop or sell them and run the command again. When uninstalling, also delete the Optional-CopyButton files if you installed them: bin\…\plugins\GwentBetaClipboard.asi and the dinput8.dll from this mod (not another mod's).

**After uninstalling:** copy the folder from the archive's After-Uninstall folder into the game directory (Next-Gen: Mods/modBetaGwentKeepItems; 1.32: DLC/dlcBetaGwentClassic132KeepItems). It keeps hidden definitions of the mod's items, so merchants, your stash and containers that still hold Beta cards or kegs don't lose their whole inventory. Do not install it together with the mod.

Completed quests, achievements and spent crowns are not rolled back. The command does not traverse unloaded merchants, stash or world containers; retrieve Beta items first. Orphaned reward facts can require the included read-only save_fact_index.py and bg_clean_keys('…') after confirmation. See BetaGwentDocs/CLEANUP_EN.md. This is profile cleanup, not a certification that every historical byte of an arbitrary save has been erased.

## Towards 1.0

The releases leading to 1.0 will focus on translation corrections, bug fixes and further AI and interface refinement. Native compilation and automated scenarios do not replace in-game checks at your resolution or a real save/load test after cleanup. Please report reproducible problems.

## Bug reports

Found a problem? Please include the mod and exact game versions, selected text and voice languages (including Auto), whether this is New Game+, other mods, the cards/leaders and steps to reproduce. A screenshot and a save from before the problem are helpful. For a translation issue, name the language and screen and suggest a better wording.

### How to enable the log

1. Add -debugscripts after the closing quote in the shortcut target for the actual witcher3.exe. In Steam, use Properties → General → Launch Options. For GOG you can use a direct shortcut to witcher3.exe.

2. Start the game, reproduce the problem and close it. Copy scriptslog.txt immediately: the next launch overwrites it. If it contains only a header, mention that; extra logging configuration may be needed for that build.

3. If Windows created a crash dump, attach the latest relevant .dmp as well.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

## Credits

Thanks to CD Projekt for The Witcher and Gwent, LegacyGwent DIY for card and board assets, the Beta Gwent community for preserving historical material and archetype ideas, and everyone who tests the mod and sends detailed reports.

Unofficial fan project. Original mod code is GPL-3.0-only; original game assets belong to their owners.

[GitHub — Gwent Beta Classic](https://github.com/NikRegul/GwentBetaClassic-)

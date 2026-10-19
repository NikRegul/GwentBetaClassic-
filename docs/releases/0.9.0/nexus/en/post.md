**Gwent Beta Classic 0.9.0**

**English**

**Classic 1.32 and Next-Gen**
Choose one archive for your game version. Each contains all 13 text languages and all five voice languages: EN, RU, DE, IT and PT-BR. Text and voices can be selected independently in the mod menu; Auto follows the game's settings, with English as fallback. Works on Steam Deck as well (tested by the author).

For Next-Gen, replace the previous modBetaGwent0924 folder and copy Mods into the game directory. Optionally copy bin from Optional-CopyButton for the Copy button. For Classic 1.32, install BOTH Mods and DLC. Its DLC/dlcBetaGwentClassic132Assets folder is required for graphics and leader entrances. Classic is larger because the old loader needs a different resource layout; the cards and AI are the same.

**AI improvements**
Revised Igni and Yrden choices, Birna's weather forecast, armour breaks and the three Redanian armour abilities. Catch-up after a pass now follows real plays and turn boundaries. The AI can concede round one to preserve resources, but gives survival priority when another lost round would end the match. Automated scenarios cover all 46 opponent deck archetypes; unusual decisions are still worth reporting.

Isengrim: Outlaw now compares the actual special-card and Create branches, including when pulled by Royal Decree. The AI rejects Decoy without a legal allied Bronze or Silver target and estimates Create from its random three-card offer, without reading future random choices.

**Deck sharing and interface**
Import and Export use BG1 text codes. Missing cards appear as cards you can craft one by one or all at once; import unlocks when nothing is missing. Import creates a draft: save the deck afterward. Added console commands, improved translated buttons, editor spacing and controller navigation, and revised graveyard flights and leader animation timing.

Copy now puts the BG1 code straight into the Windows clipboard. Optional: copy the bin folder from Optional-CopyButton into the game directory (dinput8.dll and plugins/GwentBetaClipboard.asi beside witcher3.exe); the mod works without it; if another mod already has a dinput8.dll, keep it and load the ASI with that mod's loader. Without these files the Import and Export buttons are hidden.

**Card view and tutorial**
The full card view now follows Beta: a large card with the original Beta 0.9.24 faction banner, base power in white, readable flavour text and highlighted keywords. Deck screens use the same banner. The tutorial has 10 pages, including mulligan and draws, rows and neighbours, and card statuses. A deck code can also be pasted from the Windows clipboard (Paste or Ctrl+V; requires Optional-CopyButton).

**Card fixes**
Myrgtabrakke now deals 2 damage three times and Harald the Cripple's ability hits ten times, matching the Beta 0.9.24 card data.

**Installing after Redux**
Legacy item definitions are included: 203 missing names are recognized without replacing 197 native definitions, for normal games and NG+. This helps load old inventory after switching mods. It does not recover inventory already lost and saved or convert Redux cards into the Beta collection. Use a backup from before any loss. Remove the obsolete modBetaGwentReduxCompat folder and update Script Merger merges.

**Built-in cleanup**
No separate cleaner mod is needed. Back up your save; finish Gwent, leave combat and close menus. bg_clean_preview() shows instructions. To erase the Beta profile, run:

```text
bg_clean_confirm('DELETE_BETA_GWENT')
```

Save to a NEW slot, exit, remove this mod's folders, update affected script merges, load the new slot and save again. The uninstall flag blocks profile restoration while the mod is still installed. Cleanup does not undo quests, achievements or spent crowns, and does not traverse unloaded merchants or world containers. Read BetaGwentDocs/CLEANUP_EN.md first.

**What's next**
Until 1.0, the focus will be translation corrections, bug fixes and further AI and interface refinement.

**Found a problem? Please post it here.**
Bug reports, logs and translation suggestions are welcome. Include mod and exact game versions, text and voice languages, other mods, involved cards and steps to reproduce. A screenshot and a save from before the issue help.

**How to enable the log**

1. Add **-debugscripts** to the game's launch options. In Steam: Properties → General → Launch Options.
2. Start the game and reproduce the issue, then close it.
3. Copy the log before another launch overwrites it:

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

4. If Windows created a crash dump, attach the latest relevant .dmp from:

```text
%LOCALAPPDATA%\CrashDumps
```

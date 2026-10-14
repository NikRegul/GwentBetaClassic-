# Gwent Beta Classic 0.6.5

Adds the original mulligan replacement sound and the Arachas Queen creature call for both the introduction and card play, respecting voice settings. Includes all 0.6.4 AI and animation fixes. Standard premium illustrations remain excluded.

The obsolete Redux compatibility layer is excluded. Remove the separate `modBetaGwentReduxCompat` companion if installed.

**Back up your saves before installation and every update. Use a separate test save for your first matches with a new version.**

Recreates Gwent Beta 0.9.24 inside The Witcher 3: 479 cards, 21 leaders, five factions, editable saved decks, NPC matches, quests and collecting. Install only one language package. REDkit and Wwise are not required to play. Targets PC game version 5.01. The new build still needs in-game verification.

## Installation

1. Close the game and back up your saves.
2. Remove the old `Mods/modBetaGwent0924` folder and extract `Mods` into the game directory.
3. The resulting path is `Mods/modBetaGwent0924/content`.
4. Open the Gwent deck menu for saved decks; talk to an NPC to start a match.

The five starter decks can be edited directly and saved; this does not use any of the eight additional custom slots. 

Mods that change Gwent, menus, card trading or rewards may conflict.

## Obtaining cards

Five starter decks are available immediately. Quest opponents award an assigned gold card; owning it already gives 200 scraps instead. Further wins against that opponent give 50 scraps. Ordinary NPCs draw from 46 deck archetypes: the first four wins against each give one bronze or silver card per win, then 20 scraps per win. A loss gives 5 scraps.

Card merchants sell kegs for 200 crowns, with a replenishing stock of five. Kegs are stored in the mod's saved stock and opened one at a time from the deck/keg menu. Legacy inventory kegs migrate into that stock. A keg contains four automatic cards and a choice of one of three cards. Duplicates can appear; excess copies automatically become scraps. Limits: three bronze copies; one silver, gold or leader. There is no manual milling of cards you need.

Craft missing cards in the full catalog. Crafting costs by rarity: 30 / 80 / 200 / 800 scraps; excess copies yield 10 / 20 / 50 / 200. Collect 'Em All requires one copy of every card and leader. Specific quest sources appear in the catalog; these cards can also come from kegs or crafting.

Controls: `CONTROLS_EN.md`. Training and editing AI: `docs/AI_TRAINING_RU.md` in the source repository. Source: https://github.com/NikRegul/GwentBetaClassic-

## Bug reports

Include mod/game version, package language, installed game or REDkit, other mods, decks/leaders, card names and steps to reproduce. Attach a screenshot, `Documents/The Witcher 3/scriptslog.txt` if available, and a separate copy of a save before the issue. Preserve logs promptly: a later launch may replace them. Remove personal information.

Next: verify new placements, leaders and complex chains; longer AI comparisons across all archetypes; refine board and animations against original Beta references; compatibility and quest playthroughs. Exact visual parity with the original is not claimed.

## Languages and animations in 0.6.4

Every package contains all 13 text languages: English, Russian, German, French, Italian, Polish, Spanish (Spain), Spanish (Latin America), Portuguese (Brazil), Japanese, Korean, Simplified Chinese and Traditional Chinese. Use the language button at the top left of the deck/collection menu or the battle settings. The preference persists with your game save.

Download only one complete package with the voices you want: EN, RU, DE, IT or PT-BR. Every text language is included in every package. EN is the main universal download with English voices. Changing text does not change voices. The keg troll speaks Russian in DE/IT.

This is a translation preview. Card texts are based on official Beta localization; AI-translated interface text needs native-speaker feedback. ES-MX and ZH-TW adapt ES and SC interface text with official card names. Native vendor card items follow the game's language; some service messages outside the mod interface still use RU/EN.

The 21 leader card portraits are animated on the board, in hand and in the right-side preview. They use full motion cycles at 24 fps with a blended loop seam. A large two-dimensional leader play scene uses existing artwork. Original three-dimensional entrances and animated illustrations for ordinary cards are excluded. Reduced effects disables animated portraits. Static artwork remains on loading failure.


# Gwent Beta Classic 0.4.1

**Back up your saves before installation and every update. Use a separate test save for your first matches with a new version.**

Recreates Gwent Beta 0.9.24 inside The Witcher 3: 479 cards, 21 leaders, five factions, editable saved decks, NPC matches, quests and collecting. Install only one language package. REDkit and Wwise are not required to play. Targets PC game version 5.01. The new build still needs in-game verification.

## Installation

1. Close the game and back up your saves.
2. Remove the old `Mods/modBetaGwent0924` folder and extract `Mods` into the game directory.
3. The resulting path is `Mods/modBetaGwent0924/content`.
4. Open the Gwent deck menu for saved decks; talk to an NPC to start a match.

The five starter decks can be edited directly and saved; this does not use any of the eight additional custom slots. The mod has complete Russian and English card text. Other game text languages receive English vendor item descriptions.

Mods that change Gwent, menus, card trading or rewards may conflict.

## Obtaining cards

Five starter decks are available immediately. Quest opponents award an assigned gold card; owning it already gives 200 scraps instead. Further wins against that opponent give 50 scraps. Ordinary NPCs draw from 40 deck archetypes: the first four wins against each give one bronze or silver card per win, then 20 scraps per win. A loss gives 5 scraps.

Card merchants sell kegs for 200 crowns, with a replenishing stock of five. Kegs are stored in the mod's saved stock and opened one at a time from the deck/keg menu. Legacy inventory kegs migrate into that stock. A keg contains four automatic cards and a choice of one of three cards. Duplicates can appear; excess copies automatically become scraps. Limits: three bronze copies; one silver, gold or leader. There is no manual milling of cards you need.

Craft missing cards in the full catalog. Crafting costs by rarity: 30 / 80 / 200 / 800 scraps; excess copies yield 10 / 20 / 50 / 200. Collect 'Em All requires one copy of every card and leader. Specific quest sources appear in the catalog; these cards can also come from kegs or crafting.

Controls: `CONTROLS_EN.md`. Training and editing AI: `docs/AI_TRAINING_RU.md` in the source repository. Source: https://github.com/NikRegul/GwentBetaClassic-

## Bug reports

Include mod/game version, package language, installed game or REDkit, other mods, decks/leaders, card names and steps to reproduce. Attach a screenshot, `Documents/The Witcher 3/scriptslog.txt` if available, and a separate copy of a save before the issue. Preserve logs promptly: a later launch may replace them. Remove personal information.

Next: verify new placements, leaders and complex chains; longer AI comparisons across all archetypes; refine board and animations against original Beta references; compatibility and quest playthroughs. Exact visual parity with the original is not claimed.

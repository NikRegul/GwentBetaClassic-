# Gwent Beta Classic 0.9.2 — changelog

For Classic 1.32 and Next-Gen 5.0+. This release consolidates the 0.9.1a–i development updates. Changes below are relative to the original 0.9.1; its controller, audio and opponent-deck fixes are retained.

## AI: passing, hand management and search

- Improved evaluation of safe leads, the cards required to catch a score and resources needed for the final round. Points gifted by a spy should no longer encourage unnecessary hand depletion.
- The AI can concede an expensive first-round chase and chooses between second-round pressure and a longer final using its engines, timers and standalone cards.
- After an opponent passes, exact simulation includes cheap cards with complex abilities, helping save a finisher when a cheaper card can win the necessary round.
- A spare reactive bronze can take an empty round instead of reserving every duplicate at the cost of a gold finisher.
- Supported whole-hand reachability checks account for interactions and several orders of the AI's own plays. Optional-round decisions also consider the cost of breaking a combination.
- New search considers an own play, several plausible enemy replies and a separate best continuation for each reply.
- Exact simulation of promising cards and bounded continuation analysis now also run on easy and medium. Search width and budget depend on difficulty.
- A bounded solver can finish small public final-round subgames with plain units and Scorch: up to six available cards, without active leaders, weather or unsupported abilities. An incomplete search is never a winning proof. A winning pass takes priority over spending another card.
- Search runs in small steps and reduces its budget when calculation becomes expensive.

## Information available to the AI

- Maximum difficulty uses the originally declared deck list and publicly seen copies when estimating threats such as Scorch, Igni and Schirrú.
- Easy and medium do not use the exact original list.
- The real hidden hand, actual remaining deck and future draw order are not revealed. Modeled replies remain hypotheses.
- A face-down ambush is treated as a risk, including possible Toruviel, without reading its concealed identity.
- No starting five-point bonus has been added.

## Combos and individual decisions

- Foltest values combined hand/deck boosts before units are spent. Fixed per-card rounding and double subtraction of a played unit's hand boost; keeping a leader is not itself a reason to pass.
- Adda's Curse counts consecutive Kaedweni Revenant triggers from spells/items and Tortured Mages, bounded by remaining turns and actual deck targets.
- Short mandatory rounds retain bounded public counterplay with a reduced search budget and compare complete lines without charging reserve twice.
- Card inspection uses corrected silver/bronze power-number placement and size while preserving the accepted gold design.
- Aretuza uses the separately confirmed Kaedweni Knight/Swallow variant; other night rosters have guarded permanent generation recipes.
- Fixed Miruna placement and Frightener preparation, including spy return after a pass and remaining timer requirements.
- Improved Nekker Deathwish sequencing in the deciding round and preparation with Nekker Warrior before consumption.
- Between-round mulligans retain reserved finishers. Slyzard avoids useless targets; Alzur's Double Cross accounts for the Miruna/Frightener interaction.
- A final draw/tutor card is not rejected solely for a weak immediate target when passing would concede the match.
- Retains 0.9.1 fixes for Brewess: Ritual, Archespore, spies, Arachas Swarm and Adda's Curse.

## Cards and interface

- Panther uses the normal board targeting arrow. The target row must contain fewer than four units; a row with four or more is ineligible.
- Henry var Attre can finish selection immediately, after some eligible cards or after all of them.
- Mangonel triggers on reveals in either hand during its owner's turn. Reveals during the opponent's turn and concealing cards do not trigger it.
- Dimeritium Shackles can target a face-down enemy ambush while preserving the remaining effect restrictions.
- Corrected Ida Emean and Vanghemar creation pools, related-card previews and the Russian Create keyword tooltip.
- Related-card previews use the original Beta graphs, including internal ability variants without adding them to the collection, with controller access.
- Retains 0.9.1 controller focus, preview, pile-navigation and created-spell targeting fixes.

## Music and audio

- The deck builder plays the original Gwent Beta main menu theme, looped through the music bus. It stops when leaving the builder.
- Matches retain the existing The Witcher 3 music. The separate `Mods/modBetaGwentMenuMusic` folder is optional. Without it, the game's normal music continues in the deck builder.
- Retains the Classic 1.32 Seven Cats loading fix and on-demand language sound banks introduced in 0.9.1.

## AI and decks: fixes from playtests

- Boosts no longer go to a unit the opponent can still erase. The AI does not boost its own-side spy (for example a Cantarella planted by the opponent) while the opponent may hold Menno Coehoorn, and gives lower priority to an already heavily boosted unit while a reset is possible (Peter, Mardroeme, Mandrake, Toxin, Extract, Dimeritium Bomb, Geralt: Yrden and others), spreading boosts instead. At maximum difficulty the known starting list minus played copies is used.
- Dryads rebuilt around Ciri: Nova: 26 cards with exactly two copies of every bronze, so Nova enters with 22 power; the AI holds her for the deciding round. Ambushes via Isengrim, spells via Ithlinne and Elven Mercenaries. In the mulligan the AI keeps one Wardancer and summons the other from the deck.
- Cursed Ships prepares the graveyard: a Longship becomes the Corsairs' target instead of discarding the resurrectors, and Cerys comes earlier with enough resurrections.
- Adda's Curse: Kaedweni Revenant is played before the item or spell that triggers it.
- One guard against passes that concede the match: when the opponent already holds a crown, the AI is behind and has a legal play, it plays instead of passing, whatever rule wanted the pass.
- A card played from the deck or graveyard (Double Cross, Isengrim, resurrections) keeps the same archetype corrections as from hand.
- After the opponent has passed, an AI pass ends the round and forfeits its pending timers (Miruna, Vran, Sappers, Revenant); this is now accounted for. While the opponent still plays, the timers keep firing after the AI's pass.
- Boosts account for Scorch and Schirru: the AI avoids making any unit, gold included, the board's strongest while Scorch is possible: Scorch destroys gold units too.
- In a hopeless first round the AI concedes and keeps its held finishers.
- For playtest analysis every AI decision logs its full position (`AI_POSITION`); `tools/ai/log_to_test092.py` turns it into a regression test.
- Decks: Slave Infantry and Cursed Ships now fill all four gold slots; Adda's Curse, Aretuza and Usurper rosters changed. All 46 AI decks were checked for complete rosters.

## Validation

The new search is checked against an independent solver for authored public endgames, hidden-information tests, unchanged live state/RNG and agreement between synchronous and staged execution. All 552 control matches against h and 736 additional matches against four fixed behavioural styles finished without harness errors. These samples do not establish an overall win-rate increase or a new complete deck ranking.

The build checks immutable sources through 66 regression groups, 1,426 tactical cases, 414 row-choice checks and 5,632 additional scenarios. Both platforms undergo native compilation; archive contents, CRC and SHA-256 are checked. Compilation and automated matches do not replace manual testing of this version in the game.

## Updating

Close the game and choose the correct platform archive. Replace the previous main mod folder. Install `modBetaGwentMenuMusic` only if desired. On Classic, also copy both required DLC folders. Keep unrelated mods and DLC. Rebuild affected Script Merger merges against the new version when applicable. `After-Uninstall` is only for removing the mod.

All 13 text languages, five independently selectable voice languages, the collection and existing saved preferences remain supported.

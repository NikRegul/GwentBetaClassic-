# Gwent Beta Classic 0.4.3

Changes since 0.4.2.

## Rules and AI

- Units cannot consume themselves. Both target selection and effect execution enforce this rule; abilities finish safely when no other target exists.
- Improved Coral and Djenge Frett target evaluation, accounting for ownership, friendly engines and Greatsword preparation.
- Vran considers subsequent targets to its right when setting up a consume chain through multiple eggs.
- Late spies check whether available follow-up plays can recover the lead. Draw value decreases as the hand runs out.
- Spy placement considers Blood Moon contact damage, including the unit moved by Frightener. Boons are not treated as damaging weather.
- Nested card choices consider eligible deck and graveyard targets. Ointment without a valid target no longer receives artificial ability value.
- Replacing weather includes prevented damage, allowing Moonlight to remove a harmful Skellige Storm from a friendly row.
- Random opponent rotation persists in saves and includes all 46 archetypes, each once per cycle. Selection favours a change of faction, leader and strategy.
- Cursed Adda now includes Marching Orders alongside Reinforcement; Natalis strategy notes have been updated. Saved player deck overrides are preserved.

- Fixed Morkvarg: resurrection happens before weakening. Once his strength is exhausted, he disappears instead of remaining on the board at 0. A failed resurrection onto a full board no longer weakens him.
- Returning a card to the deck and drawing it again preserves its weakened strength; shuffling no longer heals it.

## Interface and effects

- Moved Craft directly onto cards in the collection and deck editor. It stays visible below the copy cap, shows the cost and does not disappear when the cursor moves. Clicking creates that card without also adding it to the deck.
- Fixed crafting leaders and regular cards from the collection and deck editor before NPC matches. The game handler no longer rejects requests because of NPC mode. Scraps are charged only on success; ownership and available cards refresh on the current screen.
- Ability choices use the mulligan layout: up to ten cards per page, at most five per row, with a full hover preview. Ten choices use two rows of five.
- Mandatory choices can be temporarily hidden to inspect the board without cancelling the ability: View board button, Tab, or controller Y.
- Fixed controller focus scope in the end-mulligan confirmation dialog.
- Vertical navigation enters the nearest row before choosing a card, avoiding jumps over sparsely populated middle rows.
- Aligned timer numbers and switched them to the card number font.
- Added light frost mist using an existing atlas.
- Extended rain across the full row width.
- Shrike and similar automatic enemy-wide specials are cast on the enemy half. Their global effect area is preserved.

## Build and validation

- Russian and English packages; editable PowerShell entry point: `D:\w3mod\tools\Build-0.4.3.ps1`.
- The build runner retries REDkit's known 0xC0000008 shutdown failure a limited number of times; repeated failures and other errors are not ignored.
- Added regression scenarios for consume, AI targets, spies, empty Ointment, weather replacement, all 46 opponent rosters and controller navigation.
- Reviewed the completed 0.4.2 versus 0.4.1 AI comparison: 1,840 games, no simulation errors, 50.35% score. Overall superiority was not established; 0.4.3 has not yet been benchmarked against 0.4.2.

Automated rule checks and compilation do not replace visual, save/load and controller testing in the retail game.

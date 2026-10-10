# Gwent Beta Classic 0.4.3 validation

Targets The Witcher 3 PC 5.01. Install one language package at a time. The build does not install itself into the running retail game.

Automated scenarios execute translated WitcherScript rules for self-consume, Coral and Djenge Frett targets, Vran chains, late spies, contact weather, empty Ointment, Full Moon replacing Storm, and the Adda roster. Rotation tests cover four complete cycles of 46 opponents with a mocked save/load roundtrip. Extracted ActionScript handlers are checked for Craft button persistence, mulligan confirmation and row navigation. Native compilation, menu bindings, resource budgets, source correspondence and ZIP integrity are checked by the build.

Retail testing remains necessary:

1. Click Craft directly on a card in the collection and editor. Confirm it is visible without hovering and ownership and scraps update. Insufficient scraps disable the button; reaching the copy cap removes it. The click must not also add the card to the deck.
   Repeat before an ordinary NPC match, from both the collection and deck editor, with a leader and a regular card. The editor should make the new copy available without closing; crafting beyond the copy limit must not charge scraps.
2. Inspect an ability choice, hide it with View board / Tab / Y, examine the board, then return to the still-pending choice. Ten options should fit in two rows of five.
3. Confirm the end of mulligan with a controller. Navigate through a sparse middle row between dense outer rows.
4. Check frost mist, rain edges and card readability. Visual fidelity and sound are not established by automated tests.
5. Check AI Moonlight under a friendly Storm, Ointment without a valid graveyard target, and Vran placement near multiple eggs. Preserve scriptslog.txt immediately after a problematic match.
6. Save and reload after several random ordinary opponents. Their rotation should continue. Authored quest opponents and manually selected debug decks are outside the random rotation.

7. Morkvarg: destroy him repeatedly until his strength is exhausted and he disappears; separately test discarding a damaged Morkvarg. Shuffle a weakened card into the deck and check that its strength is preserved when drawn again.

Self-consume is forbidden; consuming a different copy of the same unit remains legal. Shrike is cast on the enemy half while retaining its global effect area. Player-saved deck overrides are preserved when the AI Adda roster changes.

The completed 0.4.2 versus 0.4.1 comparison scored 50.35% over 1,840 games and did not establish overall superiority. The 0.4.3 regression checks establish corrected cases, not an overall strength improvement.

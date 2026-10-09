# Gwent Beta Classic 0.2.9 — world pause and original Beta board layout

**Back up your saves and replace the whole Mods/modBetaGwent0924 folder.**

## Fixed: the world kept running during a match

Players reported that key presses during a match made Geralt drink potions,
guards turned hostile and Geralt could die mid-match. Cause: the menu resources
(`betagwent_board.menu`, `r4gwint_game.menu`, `r4deck_builder.menu`) had an empty
`CMenuPauseParam`; vanilla TW3 Gwent menus set `pauseType = MPT_FullPause`.
All three menus now fully pause the world like vanilla Gwent. Player action
blocking (`EMPTY_CONTEXT` + `BlockAllActions`) is kept as a second layer.

## Board layout from the original Beta scene

Positions come from the original client's battle scene (`level8`), projected
through its perspective camera (FOV 60°, at 0,0,−185) to 1920×1080.

- Turn/pass coin centred at (207, 540) between the two halves.
- Crown made of two halves on the score ribbon (original sprites); an unwon half is dimmed.
- Score ribbons, total score and row scores at the original positions.
- Rows 904×118 (were 742×96); board halves at original scale.
- Leader left of the hand; hand within the original hand zone; opponent hand centred on top.
- Deck and graveyard in the right corners; preview panel moved below the top piles.
- A played card pauses in the original presentation spot before landing.

## Please check in game

1. NPC match: potion/attack/sign keys do nothing, NPCs do not move; control returns after the match.
2. Deck editor from the pause menu.
3. Coin and crown halves after a won round.
4. Mouse and controller: rows, hand, leader, deck/graveyard, pass.

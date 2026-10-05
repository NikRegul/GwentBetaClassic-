# Gwent Beta Classic 0.2.1

**Back up your saves before installation and every update. Bugs can still occur.
Use a separate test save for your first matches.**

## Changes

- HD target highlights preserve transparency instead of covering card artwork with black rectangles.
- Full right-click inspection handles native Scaleform button events without playing a card or confirming a target; I and Shift + click remain available. Before placement, RMB cancels the selected leader or hand card.
- Aglais transfers the opponent graveyard special before adding Doomed: replay resolves, then the special is banished and the turn continues.

- Separate ordinary death, fire destruction and consume sounds. Consumed units
  no longer play a second death animation. Banish no longer flies into a consumer.
- White Frost shows one application on each of the two adjacent rows.
- AI estimates Seltkirk's first-strike duel using power and armor, preserves
  reactive cards without worthwhile targets, and reserves leader abilities.
- A low card-ordering score no longer causes a needless pass. Early passes are
  more conservative; deliberate card-economy passes and round-two dry passes remain.
- Card illustrations: 384×540, replacing old 128×180 thumbnails. Ten original
  Beta board halves: 2048×708 with shared scale and correct faction proportions.
- Original Beta backgrounds, wooden panels, buttons, frames and deck-builder
  shelves. Proportional portraits, a right reading pane and match settings under Start.
- 49 original Beta hit/weather images and flipbook frames at source resolution,
  retaining extracted intro timings and the fog frame curve.
- Controller: ←→ hand, ↑ nearest field unit; ←→ insertion, ↑↓ / LB/RB row,
  A confirm, B back. Card/target navigation stays separate from panel buttons.
  Start opens match actions; existing inspection, deck/grave and hold-to-pass remain.

## Install

Close the game. Install one full RU or EN package by extracting Mods into the
Witcher 3 directory and replacing `Mods/modBetaGwent0924`. Do not keep multiple
versions installed. Players do not need REDkit or Wwise. Target game version: 5.0.
Your collection and saved decks are preserved; a new game is not required.

## One combined acceptance pass

Check the deck builder's portrait, descriptions, factions, renaming and saving.
In battle, compare White Frost on two rows, ordinary death, consume and banish.
With a controller, insert a unit between neighbors, target a unit, apply frost
on an empty row, complete a mandatory choice and return to the hand.
Play against Northern Realms and report wasteful Seltkirk/leader/pass decisions
with the exact board and hand situation.

## Limitations and reports

Compilation and packaging are checked; visual/controller and battle acceptance
of this version are still pending. AI uses bounded estimates and 40 profiles,
not a full search of all reaction chains. The duel estimate omits passive reactions.
Unity lighting, perspective and premium animations are not fully reproduced.
Controller flow is closer to classic Gwent, but exact parity is not claimed.
HD artwork may increase graphics-memory use.

Reports should include game/mod version and language, other mods, input device,
decks/leaders, round/scores/hands/passes, recent actions and expected behavior,
plus screenshots/video, available game/REDkit logs and an optional test save.
Do not share license keys or authentication tokens.

## Next

Installed-game acceptance; refine deck selection/catalog layout, original Beta
icons and score counters, weather/light/shadows/transitions, improve tactical
chain estimates and archetypes from real matches, optimize HD resource memory.

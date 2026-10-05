# Gwent Beta Classic 0.2.4

**Back up saves before every update.**

- Fixed Roar creating its Bear; audited neighboring nested-play transitions.
- Refreshed stale deck/graveyard choices; excluded active play ancestors.
- Free-row fallback and spy-side handling for nested units.
- Row validation agrees with allied/enemy/any-side highlighting.
- Balanced cursor ownership and input-context restoration.
- Restored inline HD textures; native bundle is stored uncompressed.
- Matching RU/EN code, fresh script blobs and build/AI documentation.

Installed-game rendering and input acceptance of this revision remain pending.
0.2.3 opened menus but did not render external textures. Replace the whole
Mods/modBetaGwent0924 folder; do not mix package versions. See UPDATE.md.

## 0.2.2

Improve shipping-GFx startup compatibility: remove the early MouseEvent.RIGHT_CLICK lookup and detect native RMB without an additional SDK class. Installed-game acceptance of the blank-editor/NPC-loading fix is pending.

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


# 0.2.0

- Full English package: original English card texts, translated UI/gameplay
  messages/item strings, original English battle recordings; 1418 audio media.
- Separate Russian package with the same mechanics and Russian recordings.
- Card-choice modal isolates focus and mouse input from board rows, fixing
  Dandelion: Poet choice interference. Existing mandatory choices remain required.
- Ordinary NPC decks are randomized each match; quest opponents retain fixed decks.
- Four rewarded victories per ordinary NPC, one eligible bronze/silver per win.
  Earlier first-win rewards count as one; no save schema reset. Quest rewards unchanged.
- Shared 40-profile archetype AI and pass/card-economy layer from 0.1.1.
- Source distribution and developer build/AI guides prepared for community work.

Compilation, bridge and archive checks pass. The latest fixes and English
presentation still require installed-game acceptance. Board/animation fidelity,
AI strategy refinement and broader compatibility are the next stages.

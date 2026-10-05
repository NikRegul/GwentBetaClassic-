# Stage 95 — RU 0.2.2 acceptance package

Only the Russian package was built for this stage. No stage95 English release
has been compiled or accepted. Do not label the previous English archive 0.2.2.

Changes: safe ESC/back navigation with explicit forfeit confirmation; pause-menu
entry shows saved decks without opening a new draft; non-battle start button and
redundant battle branding removed; hand/header/keg positions adjusted.

Leaders require useful ability value. Calveit evaluates the actual top three
cards; ordinary opponents use a shuffled pool of 40 active archetypes without
repeats until a new cycle in the current session. Quest presets stay fixed.

The previous cook logged fatal writer-buffer assertions despite exit code zero.
Opaque pages now use BC1 without reducing card dimensions (384x540); editor-only
SWF data is removed from shipping copies. All three cooked resources passed CRC,
native GFx and pixel-block comparison. Source REDkit resources retain authoring
SWF. These checks do not establish installed-game runtime success.

Back up saves before installation. Confirm pause deck-list entry, NPC startup,
ESC/back, RMB preview/controller, leader decisions and screen edges in game.
Git/Nexus publication and Steam submission follow user acceptance.

AI editing instructions: docs/AI_MANUAL95_RU.md.

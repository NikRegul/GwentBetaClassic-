# Gwent Beta Classic 0.7.1

Deck editor: position filters, strength sorting, reset filters, undo for clearing the deck, and Save / Discard / Cancel when leaving a changed draft. Kegs can be opened consecutively after the fifth card is committed.

Presentation: removed the late rainbow boost wave and recovery symbols; reduced projectile trails for Parasite and Jotunn; compact simultaneous Wild Hunt Drakkar boosts; corrected hail atlas sampling; original Clear Skies light shafts, including generated Clear Skies. The field-message option hides effect captions while keeping controls and acceleration hints visible.

Confirmed review fixes: last-position deck summons, Doomed special-card cleanup, ordinary ability estimates in weather AI decks, current-card row evaluation, and the no-target Epidemic message. Previous armour and Assassin fixes are preserved.

Debug console: `bgboard_effects()` opens 301 presentation samples. Left/right or LB/RB change samples; Enter/Space or the focused A/cross button repeats; Escape or B/circle closes. Samples use the combat renderer without playing a real match or awarding cards.

Each voice package contains all 13 selectable text languages. GUI loading limit remains 65 MiB. Automated regression, compilation and package verification do not replace in-game visual and controller testing.

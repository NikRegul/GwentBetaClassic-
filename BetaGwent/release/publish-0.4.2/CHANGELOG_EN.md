# Gwent Beta Classic 0.4.2

Changes since 0.4.1:

- Mulligan: two rows of five cards for a full hand, larger artwork and a detailed hover preview. Cards no longer reorder during exchanges; replacements stay in the exchanged slot. Controller navigation follows both rows.
- AI values weather removal for Clear Skies, First Light, their creators and tutors. Prevented future damage is kept separate from immediate points used to catch up after a pass.
- Units that clear their own row choose an appropriate weather-affected row. Archetype and support placement preferences cannot override that cleansing ability.
- Vran Warrior values Arachas Hatchlings spawned by consuming. It can consume ordinary fodder from the middle of a row while preserving other consuming engines and Arachas Behemoths.
- Nekker Warrior now values self-replacing deathwish chains when choosing deck copies. Exact target simulations preserve the strategic choice when immediate scores tie. Both added Nekkers were tested through actual consume and deathwish resolution.
- Golden Froth now uses the original 36-frame Beta animation instead of an incorrectly cropped texture. Removed disconnected square fragments; reduced effects keep the foam still.
- Fixed the Skellige Storm join: horizontal mask fading no longer repeats with every moving sea tile. Texture edges match, with a small overlap to prevent a filtering gap.
- Viper Witcher can damage units on either side. Its mandatory ability still chooses a legal friendly target when the opposing board is empty; the AI includes that friendly damage in its evaluation.
- AI passes an already-won round against a player with no cards or available leader when resolving round-ending effects confirms the win.
- The four ordinary-NPC card rewards now use a saved entity reference. Matching legacy records migrate; subsequent wins award scraps.
- The Scoia’tael starter replaces Isengrim with ordinary Iorveth, removing its dependency on an absent Ambush card. Existing saves receive Iorveth without losing Isengrim or overwriting customized decks.
- Added `tools/Build-0.4.2.ps1`. Build preparation explicitly regenerates starter progression and runs the new checks with `-CheckAI`.

Vendor keg restocking remains intentional.

Back up your saves before updating. Compilation and automated scenarios do not verify native UI, controller input or save loading. NPC-reference persistence has been checked with a simulated save round trip; an actual in-game save/reload is still required to verify the engine serializer.

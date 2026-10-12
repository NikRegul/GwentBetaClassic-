# Stage 126 — changes prepared for 0.4.6

Sources prepared and scenario-tested. The user authorized a full RU + EN 0.4.6 build on 11 October 2026; final build evidence will be recorded below. The editable entry point is `tools/Build-0.4.6.ps1`.

## Implemented

- Fixed both sides' victory crown selection. The second half now uses the next negative atlas ID (`-1541` / `-1543`), instead of selecting the cloth ribbon or the other side's crown. Updated the live HUD and layout/preview scripts.
- Placement previews, displaced row cards, dragged cards and the old face during transformation share the full Beta card renderer, including frame, power banner and state icons. Concealed ambushes retain their hidden face.
- Weather replay uses the same timing for each row. Removed whole-batch compression and the first-hit/subsequent-hit speed difference. Fast animation settings scale all ordinary hits consistently.
- Repeated damage produces separate visual frames. The real Dimun Warship ability yields four hits; combined boost + armour remains one presentation per target.
- Mass consumption and intervening Nekker reactions retain the accelerated presentation, without accelerating later weather.
- Weather forecasts include global weather, existing weather replacement and Full Moon's current and conservative future eligible units. Added full AI-turn regressions for early global weather, holding redundant weather and replacing Frost with Moonlight.
- Roach requires a gold unit played from hand by its own player onto its own half; an enemy spy placed there does not trigger it.
- Revival preserves an instance's lock. Added the original Beta chain/padlock assets and original show/hide clip durations; the source Unity assets remain unchanged.
- Controller navigation can reach choice footers, match exit and empty deck-editor panes. Threat scoring includes armed Revenants and armour-dependent support.

## Verification

- `tools/ui/check_card_presentation126.js`: 23 checks passed, including both crown halves for both players and all card-preview entry points.
- `tools/ui/check_timing126.js`: 12 checks passed.
- `tools/ui/check_controller126.js`: 37 checks passed.
- `tools/ai/check_engines126.js`, `tools/ai/check_weather_visual126.js`, `tools/ai/check_consume_self.js`, `tools/ai/scenarios114.js` and `tools/ai/scenarios121.js`: passed against frozen snapshot `BetaGwent/build/fixes126/snapshot-final2`.
- ActionScript compiler completed successfully after the crown and card-renderer changes: `BetaGwent/build/fixes126/ui-syntax-check.swf`, 192691424 bytes. This is an isolated syntax check, not a release build.
- Both PowerShell build scripts parsed without errors. Original crown atlas composed locally for inspection: `BetaGwent/build/fixes126/crown-preview.png`.

These checks do not substitute for testing the updated interface with a controller and the native game renderer.

## Completed follow-ups

- Contextual mulligan in all three rounds: exhausted generic pile tutors and managed Elven Mercenary, Dwarf and Item tutor pools; Thunder value capped by bodies available from the hand, leader and known summons. Archetype bonuses cannot override that cap.
- First-round concession checks all remaining cards and the available leader. Ordinary hands use an upper bound; small compound hands use a bounded complete-hand simulation. Budget exhaustion stays unknown and does not force concession. The new policy never applies in rounds 2–3.
- Iris/Sabrina require an actual profitable activation within two own follow-ups. Added partial damage planning and useful Sabrina row selection. Corrected Iris's beneficiary count (CountLocation expects one exact zone, not a row mask).
- Fringilla searches ordered neighbour pairs and uses the same insertion position in real play and simulation. It avoids copying a higher left value into a weaker right unit for the opponent.
- Global own specials cast onto one half surface, including row gaps, with a single controller target and consistent drag/keyboard behavior. True row/target spells retain their requests.
- Skellige collection journal counter repairs itself when opening the quest journal from permanent native NPC reward claims. It does not infer wins from starter ownership, duplicate rewards or ordinary NPC farming; it does not alter tournament admission or completed quests. Native quest counters/completion remain under the original graph.

Additional verification: `check_followups126.js` 36 checks; `check_halfcast126.js` 26 checks; `check_quest126.py` 8 checks, plus scenarios123 (41), scenarios124 (193), scenarios125 (39), and the presentation/controller/timing regressions. Snapshot: `snapshot-release` (`83611d1e61e7b04a94d1bf7a120217ecaaf25f2fa70635360a6aab6e208b043a`). Native gameplay, gamepad feel and quest-HUD refresh still require testing in-game.

Native compilation: corrected reserved `quest` local and wrapper declaration (`function`, not `event`). RU succeeded in `board-compile126ru-20261011-154232-495`; an earlier successful-output attempt encountered the known REDkit 0xC0000008 shutdown and was retried. Menu exports reused after script-only fixes.

## Later source-only follow-ups (stage 128)

The native compilation above predates these changes. No new native/UI build or release package was started after the user's stop instruction.

- Final source snapshot: `BetaGwent/build/decks128-final`, fingerprint `70688d538a0760d8388a79f5931ca99d29eac5126fb65428764f31d29b10ecd0`.
- Generic weak-left Fringilla setup, Draig/Priestess follow-up and Sabrina activation are covered by actual AI action tests. Fringilla, Draig and Sabrina remain in their original decks.
- Added future engine/Ambush scoring, Thunder clustering, trigger-held pile views, single-page ability choices and horizontal row wrapping.
- Editable deck patches preserve player presets 1–53 and the exact Eredin deck 80. Four clone lists now use previously absent leaders.
- The deck comparison contains 640 mirrored games across 16 roster candidates with the same AI engine. It is candidate selection, not an independent estimate of all-archetype balance or a comparison of AI versions. See [the full review](decks128-review.md).
- Re-run source checks with `powershell -NoProfile -ExecutionPolicy Bypass -File tools/Check-0.4.6.ps1 -Snapshot BetaGwent/build/decks128-final`. In-game rendering and physical controller checks remain required.

# Gwent Beta Classic 0.4.1 — changes since 0.3.4

Back up saves before installation and every update. The cumulative changes below include 0.4.1 and the intermediate versions after 0.3.4.

## New in 0.4.1

- Rebaked all ten original Beta board halves with correct nearest-surface depth selection, restoring gold ornaments, metal fittings and trim previously covered by rear faces.
- Preserved one horizontal reflection: score rails left, row symbols right. Each player's half retains its faction board.
- Added original hand/leader separators from level8.
- Larger visible row/total digits based on Gwent Numbers glyph metrics, dark outlines, and a yellow leading total.
- Separate weather-impact audio, distinct from placement and generic physical hits, using original ice, magic, physical, lightning and fire events in existing RU/EN banks. The causing weather wins over overlapping row tokens.
- Hits play all four original impact-sheet cells in sequence instead of a template-selected still. Frost impacts include an original ice texture.
- Graveyard/previews show Lock. Added death/round-cleanup preservation checks; rules already retained the status. Snapshot armour, resilience and timers are shown too.
- Atlas dimensions, card resolution and texture memory have not increased.
- Added editable Build-0.4.1.ps1 for RU/EN packages.

Compilation, menu bindings, resource limits and archive integrity are checked during the build. Installed-game audio, visuals and controls still need verification. Exact Unity effect parity and perfect AI play are not claimed.

# Gwent Beta Classic 0.4.0

- Linked AI explanations: candidate evaluations, leader/card selection, rows, targets and explicit pass reasons. Lookahead simulations do not flood the gameplay log.
- Synergy checks across all 46 archetypes: safe rows, booster adjacency, unreachable catch-up and complete play resolution; summons, discard setup and engine preservation where applicable.
- Reproducible old/new AI comparisons with shared rosters, raw deal and RNG. Per-archetype statistics, saved games/failures and a replay tool.
- Fixed the comparison host to use exported training weights by default. Gameplay already used these weights.
- Persistent animation pace and reduced-effects preferences. Reduced effects retain source/target cues and value changes.
- Public target/area/weather previews before selection, plus remaining selections. Hidden and random results are not revealed.
- Editable PowerShell build/comparison scripts, instructions in UPDATE.md and separate Russian/English packages.
- Includes the single-screen mulligan, own-deck and ability-choice views, created-spy trigger fix and editor alignment from 0.3.5-preview.5.

The host verifies rules; preview positioning and input still need in-game verification. Back up your saves before updating.

# Gwent Beta Classic 0.3.5-preview.1

- Eredin's FrostWraiths opponent uses the complete approved Wild Hunt starter, including its leader and copy counts.
- Deck and graveyard viewers use a unified grid without tabs, collection styling, strength banners and a detailed right-side preview.

Test build: armour digits, correct reactive ship source, combined power/armour impacts, Dimun placement and early Bran setup. Cerys keeps her discard priority. See PREVIEW.md for details and in-game checks. Back up saves before installation.


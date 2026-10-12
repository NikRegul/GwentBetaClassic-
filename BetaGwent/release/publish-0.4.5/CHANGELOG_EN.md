# Gwent Beta Classic 0.4.5

Changes since 0.4.4.

- Improved evaluation of 13-power draw spies: Thaler, Frightener, Yaevinn, Udalryk and Cantarella. The AI considers the drawn card's playable value and its ability to recover the points given to the opponent, helping it use valuable spies earlier and protect a lead from poor late draws.
- Draw forecasts use the AI's remaining deck composition without inspecting its order. Forecasts do not modify the real deck or match RNG.
- Added spy forecast details to the AI decision log.
- Improved controller row navigation: preserved horizontal position, empty-row inspection stops, and consistent physical row order for the stick, D-pad and placement shoulder buttons.
- Cancelling placement and returning from board inspection restore the previous hand focus. Horizontal navigation stays in its row, with reduced diagonal stick jitter.
- Added an editable `tools/Build-0.4.5.ps1` build script for RU, EN or both, with regression checks enabled by default.

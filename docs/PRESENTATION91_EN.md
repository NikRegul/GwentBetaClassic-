# 0.2.1-preview.1: Beta board and effects

This is a preview following 0.2.0. In-game acceptance is pending.
Back up saves before installing or updating. Use a separate test save.

The Beta board is the default. Your faction determines the bottom half and
the opponent's faction determines the top half. All five factions use their
original textures projected from the original mesh UVs. This is a GFx
adaptation; Unity lighting has not been ported. “Beta board” restores this
layout; “DIY board” cycles the two previous DIY layouts.

Original target corners/glow and an aiming pointer make legal targets clearer
with mouse or controller. A translucent placement preview opens the gap
between neighbours smoothly. The hand has a gentle fan layout. Impacts,
trails, physical slashes, disappearance smoke and summons use original Beta
textures. Score changes follow impact timing.

Fog uses original clouds and its 30-frame opening wave with the original
frame curve. Frost and rain use original particle textures; intro durations
come from the original clips. Some frost ground graphics still come from
TW3. Full Unity particle systems, materials and shaders need further adaptation.
Large hover previews have a short delay and stay out of the way while aiming;
the reading pane and explicit full-card inspection remain available.

The previous AI pass is included: immediate catch-up points are separated
from future strategic utility. Gameplay acceptance is still pending.

## Installation and grouped check

Close the game, then copy `Mods` from one language archive into the Witcher 3
installation, replacing `modBetaGwent0924`. Install only one language.
REDkit and Wwise are not needed to play. To roll back, restore 0.2.0 and
your backed-up save.

Check mixed-faction and mirror matches; change your own faction as well.
Try insertion at the start/middle/end of a row, unit targeting and frost on
an empty row with mouse and controller. Check damage, boosts, death/banish,
summons and the three weather effects at different speeds, with reduced
effects and animation skipping.

For a report include factions/leaders, card/action, input device, expected
versus actual result, screenshot and the latest BetaGwent log.

Further extraction includes 28 board/background textures, 38 board meshes,
329 configured particle systems, 30 clips and 114 effect textures. For 81
stripped MonoBehaviour components, raw binary data is preserved for further
layout decoding. Original client files remain unchanged.

Next: accept board/row alignment, extend damage/weather/ambush effects,
adapt remaining curves and shader transitions, then continue the AI plan.

# Local HD interface preview — 0.2.1-preview.3

Publication is postponed pending visual acceptance. Both battle and deck
building are being updated. No GitHub or Nexus publication is performed.

Original Beta faction meshes, UVs and textures now produce ten 2048×708
board halves, using common world-space bounds. Earlier halves were 512×180
and were stretched disproportionately. Full-size UI sprites/backgrounds
use separate HD pages; 562 illustration bindings use 256×360 without the
previous palette reduction. This includes tokens and ability views, not
562 collectible cards. Identical native texture aliases share their DDS page.

Battle uses wooden controls and faction panels, centred proportional unit
portraits and a persistent card-reading pane. Settings/history move into
the match menu. Aiming, insertion previews and controller positions share
the new row geometry. The primary pass/choice action remains visible.

The deck builder retains its three-column layout, saved slots, naming,
search, filters and controls. Original shelves/buttons/frames now retain
their source detail. Saved-deck selection, the catalog, mulligans, piles
and kegs share the wooden style. Choice/keg portraits retain their aspect.

Back up your saves, close the game and replace `Mods/modBetaGwent0924`
with one language package. RU development resources are installed into
the REDkit project; restart REDkit to reload them. The installed game is
not modified automatically. HD resources increase package size and memory.

Check the editor once and play one match: mixed factions, insertion,
empty-row weather/controller choice, mulligans, right-side inspection,
match menu and a completed round. Report language/version, resolution,
input device, final actions, a screenshot and the session log if needed.

This is a GFx adaptation, with orthographic unlit boards. Original Unity
lighting, perspective, premium animations and full picker/catalog layout
are still pending, as are further interface transitions/weather and AI.
File/compile validation does not constitute in-game visual acceptance.

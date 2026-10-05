# Build 0.2.4 / stage97

Use a new stage, version and compile directories for future revisions. Commands
run from `D:\w3mod`; source-only clones also need the asset inputs documented
in BUILD_RU.md / BUILD_EN.md. Original game media and license keys are excluded
from GitHub. Wcc terms must have been personally accepted before using the flag.

```powershell
python -X utf8 tools/ui/prepare_board_scripts.py
python -X utf8 tools/recon/run_redkit_compile.py --out BetaGwent/build/board-compile97ru-final --patch BetaGwent/build/board-patch --timeout 120 --terms-already-accepted
python -X utf8 tools/build_presentation94.py --stage 97
python -X utf8 tools/recon/run_redkit_compile.py --out BetaGwent/build/board-compile97en-final --patch BetaGwent/build/stage97/en/en-source/scripts --timeout 120 --terms-already-accepted
python -X utf8 tools/core-check/check_turn_liveness97.py
python -X utf8 tools/core-check/check_aglais94.py
python -X utf8 tools/core-check/check_pass_policy.py
python -X utf8 tools/core-check/check_ai_rules.py
python -X utf8 tools/package_presentation94.py --stage 97 --version 0.2.4 --language ru --compiled BetaGwent/build/board-compile97ru-final
python -X utf8 tools/package_presentation94.py --stage 97 --version 0.2.4 --language en --compiled BetaGwent/build/board-compile97en-final
python -X utf8 tools/prepare_distribution97.py
python -X utf8 tools/prepare_github97.py
```

Six native movies: EN first, RU last so the active REDkit project stays Russian.
The language-specific audio catalog must come from the verified EN base.
Every package script hash must match its fresh compiled blob. Item strings and
1418-media sound cache are reused only after hash/database checks.

For stage97 and later, strip authoring SWF only in shipping copies, keep inline
CSwfTexture chunks, and pack with `-compression=None`. Verify native GFx,
all texture pixels/properties, table/chunk CRC, raw bundle payload equality,
metadata and ZIP integrity. Menus remain under the observed 100 MiB writer
limit. Never accept Wcc exit0 when its log contains writer assertions.
Stage96 externalization is retained only for historical reproduction: it
loaded menus but did not render textures in the user's installed game.

The uncompressed bundle approach still needs installed-game acceptance; do not
treat a clean cook as proof of rendering or sound. Distribution preparation
copies verified outputs; it does not upload to Nexus or Steam.

## Relevant seams and AI

`BetaGwent/development/scripts/game/betagwent/duelSession.ws`: CreationAllowed,
ApplyCreatedCard, BestNestedRow, ValidMonsterRow, IsPlayAncestor, BeginPilePlay,
SelectPileCard and BeginCreatedPlay. Queue validation in duelEffectRuntime.ws
calls the same creation whitelist. First fatal cause remains visible; genuine
engine faults are not silently skipped.

Cursor ownership: developmentBoardMenu.ws / deckNameInput.ws.
Manual AI editing guide: [AI_MANUAL95_RU.md](AI_MANUAL95_RU.md).
Strategies: duelArchetypeAI.ws; forecasts/placement: duelSession.ws;
pass/card economy: duelAIPass.ws; tunable values: duelAITuning.ws generated
from data/beta924/ai/tuning95.json. Never count uncertain future combo points
as already realized score. Confirmed immediate Impera boosts are counted.

Push only the audited source tree with the current remote parent and a ref
lease. Keep original assets, compiled packages, installed game files, editor
logs, credentials and Wwise keys outside the public source repository.

# Gwent Beta Classic 0.4.0

Back up your saves before installation and updates. Install one language package only. Remove the previous `Mods/modBetaGwent0924` folder and copy the new Mods folder into the game directory.

## Changes

- Linked `AI_REASON` events explain decision context, candidate card evaluations, card/leader selection, passes, rows and targets. Lookahead simulations do not flood the gameplay log.
- Reproducible checks cover all 46 archetypes: safe rows, adjacency to boosters, unreachable catch-up, complete play resolution and simulation isolation. Applicable rosters also test summons, discard preparation and engine protection. These complement earlier card-specific checks; they do not establish perfect strategy for every roster.
- Frozen old/new AI comparisons share rosters, raw deal and RNG state. Both versions play both decks in both seats; each chooses its own mulligans. Statistics are recorded per archetype.
- The comparison host now loads actual exported training weights from `duelAITraining.ws` when no external policy is supplied. The previous host path returned zero weights. The game already used the exported weights.
- Animation pace (1×, 1.5×, 2×) and reduced effects persist in the player profile. Reduced effects retain source/target cues and value changes, with a minimum 320 ms action display.
- Before selection, public affected targets, supported ability areas, weather rows and remaining selections are highlighted. Placement previews show the insertion point. Hidden identities, random targets and random draw results remain hidden.

## Build

Developer workspace: `D:\w3mod`. Building requires configured REDkit, Python, Node.js and the project's local dependencies. Players do not need these tools.

```powershell
powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-0.4.0.ps1 -Language both -CheckAI
```

This editable wrapper calls `D:\w3mod\tools\Build-GwentBeta.ps1`: generate catalogues/profiles, run checks, export four menus, validate bindings, compile WitcherScript, cook resources, package strings/audio and verify ZIPs. Output: `D:\w3mod\BetaGwent\release`. It does not install into retail. The REDkit project is restored to Russian menus afterward.

Individual steps: `-Step prepare`, `scripts`, `menus`, `package`. Recompile changed scripts/menus before packaging. `-Compiled` requires one language and a fresh matching compilation. Existing archives with the same name are moved to `old`.

## Compare AI overnight

```powershell
powershell -ExecutionPolicy Bypass -File D:\w3mod\tools\Compare-AI.ps1 -Cycles 20 -Seed 119
```

Each cycle runs 184 matches: all 46 archetypes paired with another roster, four mirrored games per pair. The opponent offset changes each cycle; 45 cycles cover every other opponent for every roster. Twenty cycles run 3,680 games. Runtime depends on hardware and card complexity. Ctrl+C stops the run; finished match files survive, and summaries update after each four-game block. Use a new output directory for each run.

The candidate defaults to current frozen sources; the baseline defaults to `D:\w3mod\BetaGwent\training\stage118-check\snapshot`. Override with `-Candidate`, `-Baseline`, `-Output`. Preserve both snapshots, Seed and Cycles to reproduce a run. Comparison does not train, replace or install a policy.

Outputs: `REPORT.md`, `report.json`, `archetypes.csv`, `games.jsonl`, compressed replays in `matches`, and failure replays with the exact pre-error state in `errors`.

```powershell
node D:\w3mod\tools\ai\replay119.js D:\w3mod\BetaGwent\training\comparison119-acceptance2\matches\game-000001.json.gz
python -X utf8 D:\w3mod\tools\ai\explain_log119.py D:\w3mod\BetaGwent\training\comparison119-acceptance2\matches\game-000001.json.gz
```

The explanation tool also reads retail/REDkit text logs. OPTION records tempo, utility, reserve, setup and evaluation; SELECT records the chosen play, ROW compares placement/weather costs, TARGET events compare targets, PASS names the pass condition. Detailed simulation is budgeted; not every legal play receives the same search depth.

`confirmedBetter` requires a complete error-free run, at least 46 blocks and a lower 99% normal-approximation confidence bound above 50%. This is a host benchmark indicator, not a guarantee against humans. Test retail gameplay separately.

## Editable AI

- `D:\w3mod\BetaGwent\development\scripts\game\betagwent\duelSession.ws`: play, target, row, lookahead and logging.
- `D:\w3mod\BetaGwent\development\scripts\game\betagwent\duelArchetypeAI.ws`: synergy, engines, consume/discard values.
- `D:\w3mod\BetaGwent\development\scripts\game\betagwent\duelAIPass.ws`: pass and round economy.
- `D:\w3mod\data\beta924\ai\researched115.json`: researched roster/strategy inputs; run generators after edits. Generated catalogues alone are overwritten during builds.
- `D:\w3mod\BetaGwent\development\scripts\game\betagwent\duelAITraining.ws`: exported weights; after replacing, recompile, verify and package.

The host executes actual WitcherScript rules but does not verify in-game FPS, preview positioning, saved settings or controller input. Bug reports should include version, language, logs, rosters and the last actions before the problem.

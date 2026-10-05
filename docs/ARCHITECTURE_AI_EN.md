# Modifying the AI

The AI runs in WitcherScript; AS3 presents its decisions and choices. There are
40 active adapted profiles from 46 user descriptions; six unsupported leader
profiles are skipped. There are 93 presets in total. Ordinary NPCs sample 55
presets (1–15 and 54–93); quest opponents use fixed presets. Reward identity
comes from the NPC's native deckName/actor, never the randomized preset.

## Layers

| Layer | Source | Responsibility |
|---|---|---|
| Card rules | duelSession / effect runtime / faction WS | Legal actions, actual execution, required choices |
| Shared evaluation | OpponentStep, TargetValue, AiAbilityChoiceValue in duelSession | Immediate gains, damage, healing, summons, target quality |
| Archetype strategy | CBetaGwentArchetypeAI in duelArchetypeAI.ws | Combo priorities, reserved finishers, mulligan, discards, graveyard choices, copies and placement |
| Passing and card economy | duelAIPass.ws | Catch-up cost, lead, rounds and hand advantage |
| Weather specialization | duelWeatherAI.ws | Frost setup/control decisions |
| Generated data | duelAICatalog.ws | Profiles, families, 70 combo dependencies, engine weights and roles |

Initialize identifies the profile by preset or leader plus multiset deck overlap.
Refresh caches own hand/deck/board and public enemy zones. OpponentStep evaluates
legal plays, combines immediate evaluation with strategy priorities and reserve
penalties, then resolves subsequent ability requests with actual legal filters.
The enemy's hidden hand/deck are not read. The current AI uses heuristics and
dependencies, not a complete 25–30 second game-tree search.

Priority describes future strategic value. It must not be counted as immediate
score when deciding to catch up after the player passes. Actual Deploy gains
must be counted: an Impera unit with base 6 and five public Spies gains 10,
for 16 immediate points, so it can close a 10-point deficit in one card.
PublicDeployGain implements this. Hypothetical future Spies cannot count as
already scored points. Some multi-stage card forecasts are still conservative.

CopyValue separates immediate copy bodies from combo forecasts. PileGain checks
real eligible graveyard cards. Face-down Ambush power does not count as scored.

## Editing a profile

1. Edit deck_rules.txt: leader, counts, plan, mulligan, early/final plays,
   control targets, passing conditions, counters and typical mistakes.
2. Update explicit aliases/replacements, family assignments and combo/role
   tables in build_ai_rules.py as needed. No fuzzy guesses for missing cards.
3. Run build_ai_rules.py → build_duel_catalog.py → build_full_catalog.py.
   Review rules.json and ai_rules88_adaptation.md for substitutions and removals.
4. For special behavior edit Priority, KeyReserve, MulliganPriority, DiscardValue,
   PileGain, PlacementAnchor or row distribution in duelArchetypeAI.ws.
   New immediate effect forecasts belong in the shared duelSession evaluation.
5. Synchronize patch/project sources, compile natively, package and play the
   specific preset before trying randomized NPC matches.

Keep presets1–53 stable: saved/quest identities depend on them. Presets54–93
correspond to the current imported profiles. Handwritten strategy belongs in
the generator or runtime class, not the generated duelAICatalog.ws.

For bad pass decisions inspect duelAIPass and the actual action gain supplied
by OpponentStep. For wrong target choices inspect EngineThreat/TargetValue.
For incorrect card effects fix the card runtime rather than compensating with
AI weights. The BetaGwent log channel records AI/pass and card-chain decisions.
Focused checks: tools/core-check/check_ai_rules.py and check_pass_policy.py.
These are not exhaustive gameplay validation.

A useful report contains deck, round, score, hand sizes, public board, recent
actions and the expected decision. Concrete cases are more useful than blanket
weight increases. BUILD_EN.md contains the full packaging sequence.


0.2.1 / stage94: see [BUILD_POLISH94.md](BUILD_POLISH94.md), [Russian changes](PRESENTATION94_RU.md) and [English changes](PRESENTATION94_EN.md).

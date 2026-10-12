# Local build inputs for 0.6.1

The public repository is source-only. These dependencies are intentionally not committed; a clone cannot reproduce release archives without them.

| Local input | Purpose |
|---|---|
| Original beta client / LegacyGwent / DIY inputs | Card data references, original media and leader capture source |
| `depot/` and configured REDkit project/native templates | Native script/menu compilation, cooking and packing |
| `tools/vendor/` | Configured SDKs and local Python/Node/ActionScript tooling |
| `BetaGwent/ui/assets/` | Original UI and card art |
| `BetaGwent/build/languages137/ui/*.json` | Runtime location of prepared dictionaries; reviewed source copies are published under `data/beta924/localization137/ui/` |
| `BetaGwent/build/languages137/fonts/` | Font sources/coverage used by the language builder |
| `BetaGwent/build/languages137/README_RU.md` | Preparation inventory and caveats |
| Local Wwise projects and original audio | One voice package per language; licenses are never committed |
| Captured leader frames and generated native resources | The 21-leader animation pipeline; ordinary premium cards excluded |
| Stage 114 fixtures required by existing checks | Historical reference data; preserve when cleaning build folders |

Preparation tools are under `tools/languages137/`, `tools/ui/capture_leaders136.py`, `tools/ui/build_leaders137.py`, `tools/ui/build_languages137.py` and `tools/ui/build_voice137.py`. Their paths reflect the current local workspace. Recreating translations can overwrite reviewed output: preserve the prepared dictionaries and treat regeneration as a separate, reviewed task.

The public source snapshot includes the 11 new reviewed dictionary JSON files under `data/beta924/localization137/ui/`. RU is the source text; EN uses the existing `english89.json`/`localization89.py` path. Together these provide the 13 text languages. For a new configured workspace, copy the 11 dictionaries to `BetaGwent/build/languages137/ui/` before building. Do not overwrite dictionaries in an existing workspace without comparing local corrections first. Fonts, voices and other binary dependencies remain external.

Release instructions: [BUILD_0.6.1_RU.md](BUILD_0.6.1_RU.md). Cleanup candidates: [project cleanup review](reviews/2026-10-12-project-cleanup.md). A cleanup inventory is not authorization to delete inputs. Never clean or regenerate dependencies during an active build.

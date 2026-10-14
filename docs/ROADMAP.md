# Roadmap to 1.0

Updated 13 October 2026. Crashes, data loss, blocked actions and match softlocks are fixed immediately regardless of the milestone theme.

[RU 0.6.6](PRESENTATION142_RU.md) is packaged and verified: the first special-effect adaptation, unified weather casts, simultaneous triggered boosts, leader entrances, continuous right-side leader previews, history/target hints, kegs at all innkeepers and combined AI fixes. Research covers 85 special cards; the first effect pass routes 48 cards. Twelve leaders use original one-shot entrance clips and nine retain their animated loops. Fifty regression suites, 70 native scripts, four menus and package verification passed; in-game acceptance remains open. Complete beta visual fidelity and ordinary premium artwork are not included.

The user checked 0.6.2 without noticing problems and selected AI, card effects and movement as the next focus. Languages stay unchanged; ordinary premium artwork is excluded for now. Version 0.6.3 fixes a reproduced AI resource-spending defect and improves card movement, flips and effect/audio timing. Its paired AI comparison ended 92:92 across 184 games with no errors, which does not establish an overall strength improvement. New visual behavior still requires in-game acceptance. The release retains 21 animated leader portraits, 13 text languages and five voice packages (EN/RU/DE/IT/PT-BR); original 3D leader entrances remain a separate feature.

Stage 140 checks round/pass planning and mulligan/combinations. Two user logs exposed deciding-round leader conservation and comparing a play against an unchanged board instead of the resolved pass; both are corrected. A readable opponent pass, corrected leader proportions and grouped death/consume effects are included in the RU 0.6.4 test build. Ordinary premium artwork remains excluded due to its resource size. See [the implementation and acceptance notes](AI_ANIMATIONS_0.6.4_RU.md). The completed 184-game comparison ended 93:90 with one draw and no errors; overall strength improvement remains unconfirmed. [RU 0.6.5](AUDIO_0.6.5_RU.md) adds successful mulligan replacement audio and the original Arachas Queen call for the introduction and play.

| Milestone | Focus |
|---|---|
| 0.6.0+ | Card effects and movement, leader animation continuity/resource lifecycle, and AI: mulligan/combinations, card and target evaluation, round/pass/leader planning, available information and decision time |
| 0.7.0+ | Finish localization: native-speaker proofreading, grammar templates, fonts/layout, external text, voice coverage/timing and clear fallback behavior |
| 0.8.0+ | UI/UX: mouse/keyboard/controller, focus and choices, tutorial, accessibility, resolutions and all languages |
| 0.9.0 | Remaining beta effects and animation fidelity, including large leader entrances; compare reference scenes and document engine limits |
| 1.0 | Complete supported languages, final rules/quest/save acceptance, and a separate branch and packages for The Witcher 3 1.32 |

Early translation feedback in 0.6.1 does not replace the dedicated localization milestone. Current support targets PC Next-Gen 5.01; 1.32 support is planned, not implemented.

Before 1.0, validate profile upgrades/NG+, all custom slots, single-charge purchases and rewards, pending keg choices, quests/tournaments, card interaction rules, hidden information, long-session performance and tested mod combinations. Compare AI changes with frozen versions, matched seeds and mirrored sides; keep roster changes and algorithm changes separate. Artifact checks must bind to the exact shipped source snapshot and fresh archives.

- [Detailed plan (RU)](ROADMAP_1.0_RU.md)
- [Manual acceptance checklist (RU)](TESTING_0.6.1_RU.md)
- [Current repository state (RU)](REPOSITORY_CURRENT_RU.md)
- [AI, animations and manual checks for 0.6.3 (RU)](AI_ANIMATIONS_0.6.3_RU.md)
- [Build instructions (RU)](BUILD_0.6.3_RU.md)

Release acceptance requires no known data loss, duplicate rewards, crashes or blocked supported matches/quests; successful compilation alone does not establish that. Preserve the all-card premium experiment separately: the current release permits only leader portraits.

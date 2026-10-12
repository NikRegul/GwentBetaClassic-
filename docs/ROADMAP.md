# Roadmap to 1.0

Updated 12 October 2026. Crashes, data loss, blocked actions and match softlocks are fixed immediately regardless of the milestone theme.

The current line is 0.6.1: animated portraits for 21 leaders, a preview of 13 text languages and five complete voice packages (EN/RU/DE/IT/PT-BR). The user confirmed the leader crash hotfix on RU. Full multi-package acceptance is still required. Ordinary card portraits remain static; large character entrance animations are a separate feature.

| Milestone | Focus |
|---|---|
| 0.6.0+ | Leader animation continuity/resource lifecycle and AI: mulligan/combinations, card and target evaluation, round/pass/leader planning, available information and decision time |
| 0.7.0+ | Finish localization: native-speaker proofreading, grammar templates, fonts/layout, external text, voice coverage/timing and clear fallback behavior |
| 0.8.0+ | UI/UX: mouse/keyboard/controller, focus and choices, tutorial, accessibility, resolutions and all languages |
| 0.9.0 | Remaining beta effects and animation fidelity, including large leader entrances; compare reference scenes and document engine limits |
| 1.0 | Complete supported languages, final rules/quest/save acceptance, and a separate branch and packages for The Witcher 3 1.32 |

Early translation feedback in 0.6.1 does not replace the dedicated localization milestone. Current support targets PC Next-Gen 5.01; 1.32 support is planned, not implemented.

Before 1.0, validate profile upgrades/NG+, all custom slots, single-charge purchases and rewards, pending keg choices, quests/tournaments, card interaction rules, hidden information, long-session performance and tested mod combinations. Compare AI changes with frozen versions, matched seeds and mirrored sides; keep roster changes and algorithm changes separate. Artifact checks must bind to the exact shipped source snapshot and fresh archives.

- [Detailed plan (RU)](ROADMAP_1.0_RU.md)
- [Manual acceptance checklist (RU)](TESTING_0.6.1_RU.md)
- [Current repository state (RU)](REPOSITORY_CURRENT_RU.md)
- [Build instructions (RU)](BUILD_0.6.1_RU.md)

Release acceptance requires no known data loss, duplicate rewards, crashes or blocked supported matches/quests; successful compilation alone does not establish that. Preserve the all-card premium experiment separately: the current release permits only leader portraits.

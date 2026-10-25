# Gwent Beta Classic 0.7.3a — AI and gold unit presentation

This revision includes the current 0.7.3 source changes. The separate Witcher 3 1.32 work is outside this revision.

- Gold units play the original GoldLanding sound alongside their own deployment SFX. Summons use the arriving unit's rarity. Leaders retain their existing entrance behavior. Effect muting, voice settings, missing-bank fallback and consumed audio revisions are respected.
- Intermediate target-choice snapshots no longer suppress the gold landing particles by already showing the unit on the board. The existing Beta particle materials and blending modes are preserved.
- AI damage choices count the Lord of Undvik deathwish: a lethal hit adds ten points per living allied Hjalmar. Locked units, nonlethal damage and missing beneficiaries are handled separately.
- In optional rounds, a chase requiring both a hand card and the leader is budgeted as a two-action investment. A lone leader still costs no hand card, and match-point defense remains available.
- Sequence search, public replies, chase branches and spy draw/recovery forecasts yield between individual simulated plays. A comparison against the frozen previous sources retained the same resolved decisions and total search plays in six control positions, while reducing the maximum plays per UI callback from 6–7 to one. Load adaptation also considers the longest blocking step.

Five voice packages: RU, EN, DE, IT and PT-BR. Each includes 13 selectable text languages. DE and IT keep their existing Russian keg-troll fallback. Voice banks are unchanged.

Automated checks and native compilation do not confirm in-game frame times or the final visual/audio result. Please check gold deployment and summons, gold SFX with voices disabled, Undvik targeting, resource preservation after a pass, and AI turn transitions. Compare the new `AI_PREPARATION peakStepMs` with the previous 88–190 ms blocking steps. Complete elimination of in-game hitches is not claimed before this check.

# Gwent Beta Classic 0.7.4-block1 — statuses and armour

First 0.7.4 block based on 0.7.3a, prepared for in-game verification.

- Resilience, spying and reveal badges use the original beta show/hide animation curves with existing HUD artwork.
- The spying badge follows the live instance flag, including charm and removal by lock.
- Visible, unlocked timer decrements use CardTimerVFX; the real timer numeral changes at the shared impact time. Timer resets and hidden ambushes do not trigger this effect.
- Armour gain uses ArmorIncrease. Only complete depletion uses ArmorDecrease fragments; partial damage retains the shield pulse. Original material UV regions and one-live-particle limits are preserved for the three principal fragments.
- Material-specific additive/alpha blending, reduced motion and a shared 600-particle budget are retained. The effect gallery includes acquisition/removal and partial/full armour damage scenarios.

This is a 2D adaptation: 3D rotations, material dissolve on badges and independent iris movement inside the composite spying badge are not emulated. Card rules, AI and saved profiles are unchanged. In-game appearance, timing and performance still require verification.

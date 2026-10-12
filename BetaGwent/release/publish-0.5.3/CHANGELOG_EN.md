# Gwent Beta Classic 0.5.3 — changelog

- The introduction waits for both leader voice lines to finish. A long first line no longer removes the second from the queue. Skipping the introduction stops its voices.
- Speeding up an active replay keeps card movement, number changes and sound synchronized while preserving animation progress. The hint switches to Skip without redrawing the board.
- Grouped area hits preserve separate reveal and status-change frames.
- Epidemic excludes concealed ambush cards when finding and destroying the weakest units. Immunity and armor do not prevent this area destruction. AI evaluation follows the same rules and does not depend on concealed ambush power.
- AI accounts for hand-size differences and the value of preserving cards and the leader for the next round. This additional reserve is disabled in deciding rounds.
- Public reply estimates adapt to already seen cards and include the possibility of a pass. A rare worst-case reply is no longer treated as the inevitable continuation.
- Bounded lookahead covers different action roles: engines, control, draw and combos, without increasing the simulation budget.
- Added reproducible decision checks with acceptable alternatives and independent seeds, plus regressions for the reported bugs.
- Preserved the current tutorial and Tutorial button, translations, False Ciri and deck deletion fixes.
- Included the final 0.5.2 deck changes: Slave Infantry replaces Vicovaro Novices with Alba Armored Cavalry; Arethusa replaces Thunder with Redanian Knights; Dryads replaces Sages with Mahakam Guards. These changes were selected in the second agent's paired trials.

Requires The Witcher 3 / REDkit 5.01. The obsolete Redux compatibility layer is excluded.
Automated source checks do not replace in-game animation and audio verification.

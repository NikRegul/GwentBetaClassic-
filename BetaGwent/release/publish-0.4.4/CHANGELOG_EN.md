# Gwent Beta Classic 0.4.4

Changes since 0.4.3.

- Cards saying “up to N cards” allow finishing after any number of selections, including zero: Ves, Vattier de Rideaux, Morvran Voorhis, King Bran and Saskia.
- Added Finish selection controls and a selected-card counter. The maximum no longer forces selecting every available card.
- Vattier reveals as many enemy cards as selected friendly cards. Bran strengthens and discards only the chosen cards. Saskia gives a replacement for each committed card; that follow-up cannot be skipped.
- AI can stop an optional selection when remaining choices have no positive value. Mandatory target counts retain their rules.
- Corrected Geralt: Aard movement: melee → ranged → siege. Siege units stay in place. A full destination row prevents movement while damage still applies.
- Added editable `tools/Build-0.4.4.ps1` for RU, EN or both packages, with automated checks enabled by default.

Rules were exercised through actual WitcherScript logic in the test harness. In-game interaction still needs acceptance testing.

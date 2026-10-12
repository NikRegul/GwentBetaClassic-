# 0.5.1

### Interface
- Collection: the owned count and rarity line moved below the card description and no longer overlaps the filter buttons.
- In-battle settings menu realigned inside its frame; the "Beta board" button was removed. AI difficulty and Tutorial were added.
- Round-loss banner: scores fit inside the frame.
- The card detail view shows related cards that the card creates or summons. Thumbnails open their own detail, and "Back to card" returns. Cards with generic wording are not affected.
- Automatic acceleration of consume and similar mass effects was removed. A "Speed up" control was added: the first press speeds up playback, the second skips it. Works with keyboard (Space/Enter) and controller (A).
- New Beta-style effects for Execution (Scorch), Geralt: Igni and Epidemic.
- A short six-page tutorial: cards and rounds, tutors, weather, summons, spies, leaders and ambushes. Example cards open in the detail view.

### Difficulty
- Three AI difficulty levels: easy, medium and hard (default). The choice is saved in the profile.

### Fixes
- Removed the short freeze after placing a card: the opponent's turn is computed after the player's animation is shown.
- The opponent's hidden ambush counter is no longer shown, highlighted or voiced on the board.
- The battle log no longer reveals which ambush the opponent played.
- The profile (decks, scraps, collection, kegs) is mirrored into separate save storage. If a save was made without the mod, the profile is restored the next time the mod is loaded. Restored decks are named "Deck N". Data lost before 0.5.1 cannot be recovered.

### AI
- The AI passes when every available play loses points, such as an empty Isengrim or a Scorch that would destroy only its own unit. The same applies to a drawing spy when the expected card is weaker than the strength given away.
- Kaedweni Cavalry removes armor from its own Redanian Elites and Knights only to stop an enemy engine; it no longer strips armor in a way that benefits the opponent's card more than its own.
- Spell-heavy elf deck: Dol Blathanna Sentry is no longer played first on an empty board when many special cards remain.
- Usurper: Vanhemar and Ehgan were replaced by Scorch and Vreemde (9/36 wins vs 4/36 in paired trials).

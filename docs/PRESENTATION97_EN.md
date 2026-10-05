# Gwent Beta Classic 0.2.4 — installed-game verification build

**Back up your saves before installation and every update. Use a separate test save.**

Unified creation checks fix Bloodcurdling Roar rejecting its Bear after killing
Whispering Hillock. Preparation and application now use the same whitelist.
Nested units fall back to a free row, including spies. Pile choices refresh
when cards have moved; active parent cards cannot resurrect themselves.
A unit creator that died during a previous child cannot prepare another
invalid creation. Row validation now agrees with allied/enemy/any-side hints.
Logs preserve the first failure instead of replacing it with cleanup errors.

Cursor requests are owned and balanced: repeated device refreshes and returns
from deck-name input no longer accumulate visibility requests. Closing the
menu releases its cursor request and restores the input context.

The owner confirmed 0.2.3 opened menus in the installed game, but its external
textures did not render. 0.2.4 restores inline textures and stores the native
bundle uncompressed, preserving resolution. This is a new loading hypothesis:
installed-game rendering and input acceptance remain pending. Game configuration
is unchanged. Update public downloads after an installed-game check.

## Acceptance sequence

1. Close the game and back up saves. Replace the entire previous
   `Mods/modBetaGwent0924` folder with one language package; do not mix versions.
2. Open the deck editor from pause: artwork, wood panels and descriptions
   must appear. After closing, the cursor must disappear and ESC must work.
3. Start an NPC match: no endless loading; textures, RMB/X inspection,
   card/empty-row selection and return to gameplay must work.
4. Check Hillock → Roar → Bear and turn completion; then Aglais,
   resurrection, repeated creation and a full preferred row.
5. Check English menus, descriptions and voices. User-created deck names
   retain the text entered by the player when changing language packages.

Source checks cover 68 creation/row/cycle/cursor cases, 10 Aglais cases,
34 pass-policy cases and 12 archetype cases plus boosted Impera chase.
Compilation and archive checks do not certify all 479-card interactions.

Bug reports: version/language, retail game or REDkit, round/scores/hands,
card names and preceding actions, screenshot and log if available. REDkit log:
`D:\GOG Galaxy\Games\The Witcher 3 REDkit\bin\editor.log`.

# Gwent Beta Classic 0.2.6

**Back up saves before installation and every update. Bugs can still occur.**

The user confirmed installed-game editor and NPC startup in Russian 0.2.5.
Compact artwork remains unchanged: cards 288×405, faction board halves
1536×531. Game memory settings are untouched. Each native GUI must stay below
55 MiB; the failed external-texture approach from 0.2.3 is not used.

0.2.6 draws a destination rectangle from the atlas when native BitmapData is
available, with a half-texel sampling inset to avoid filtering neighbouring
images. If GFx does not expose BitmapData, the native Bitmap path uses a physical
pixel crop, one scale and no page pixel snapping. Flicker reduction still
needs visual confirmation in this build; English startup also needs acceptance.

Selection borders now follow the battlefield card dimensions. Controller focus
uses the card body instead of text/effect extents and follows rotated hand cards.
Buttons, row controls and choice cards have fixed body bounds. Gameplay, AI,
sound media and saved data are unchanged. English voice-duration constants
are synchronized with the English bank using a fresh script compilation.

Close the game and replace the entire `Mods/modBetaGwent0924` folder. Install
only RU or EN. Check pause-menu editor, NPC startup, card and board images,
mouse hover, controller selection borders, flight/hit/weather, right-click/X
inspection and cursor release after closing. Compare flicker against 0.2.5.

Bug reports: mod version/language, game version, other mods, retail or REDkit,
input device, card names and actions, expected result, screenshot and available
log. For flicker, include screen resolution and a short video if possible.

Source publication and distribution-file preparation are separate from Nexus
and Steam uploads. These files do not automatically publish either platform.

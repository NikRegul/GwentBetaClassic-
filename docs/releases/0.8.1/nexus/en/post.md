# Gwent Beta Classic 0.8.1 — English

> Version 0.8.1 for Next-Gen 5.0+ has been tested in-game. Classic 1.32 is being fixed and tested separately; its current archive is a test candidate.

Gwent Beta Classic 0.8.1 brings the five voice languages together in one download for each game branch. There are two separate packages: Next-Gen (5.0+) and Classic 1.32. Installation stays simple: copy Mods into the game folder.

Text and voices now have separate adjacent buttons inside the mod. Auto follows the game's text and speech settings independently, with English as the fallback for unavailable languages. Manual choices are saved with your game save, so updating mod files does not require choosing them again.

This update also includes the New Game+ keg fix, revised card/status effects and smaller interface resources. Some Beta animations are adapted to the game's interface limits, and I will keep polishing them.

Next I will focus on stability, bug fixes, AI and translation feedback.

Found a problem? Please include the mod and exact game versions, selected text and voice languages (including Auto), whether this is New Game+, other mods, the cards/leaders and steps to reproduce. A screenshot and a save from before the problem are helpful. For a translation issue, name the language and screen and suggest a better wording.

### How to enable the log

1. Add -debugscripts after the closing quote in the shortcut target for the actual witcher3.exe. In Steam, use Properties → General → Launch Options. For GOG you can use a direct shortcut to witcher3.exe.

2. Start the game, reproduce the problem and close it. Copy scriptslog.txt immediately: the next launch overwrites it. If it contains only a header, mention that; extra logging configuration may be needed for that build.

3. If Windows created a crash dump, attach the latest relevant .dmp as well.

```text
%USERPROFILE%\Documents\The Witcher 3\scriptslog.txt
```

```text
%LOCALAPPDATA%\CrashDumps
```

@echo off
rem Copy-button bridge r7: Import reads the code without calling the game setData ~1300 times (15 s stall on 5.01, freeze on 1.32).
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py
if not exist BetaGwent\build\clipboard090-r7\GwentBetaClipboard.asi (
  %PY% -X utf8 tools\features082\build_clipboard090.py --out BetaGwent\build\clipboard090-r7 || goto :fail
)
echo Running tests (they write a BG1 code to your Windows clipboard)...
BetaGwent\build\clipboard090-r7\clipboard_bridge_test.exe --image "D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\witcher3.exe" --image "F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe" --clipboard || goto :fail
echo Installing r7 into both games (only GwentBetaClipboard.asi changes)...
copy /y BetaGwent\build\clipboard090-r7\GwentBetaClipboard.asi "D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\plugins\GwentBetaClipboard.asi" || goto :fail
copy /y BetaGwent\build\clipboard090-r7\GwentBetaClipboard.asi "F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\plugins\GwentBetaClipboard.asi" || goto :fail
echo DONE. Test: Decks - Import deck (code from the clipboard), on 1.32 and 5.01.
pause
exit /b 0
:fail
echo FAILED
pause
exit /b 1

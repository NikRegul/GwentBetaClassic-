@echo off
rem Copy-button bridge r5: clipboard owner on its own message thread (fixes the save-load hang after Copy).
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py
%PY% -X utf8 tools\features082\build_clipboard090.py --out BetaGwent\build\clipboard090-r5 || goto :fail
echo Running tests (they write a BG1 code to your Windows clipboard)...
BetaGwent\build\clipboard090-r5\clipboard_bridge_test.exe --image "D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\witcher3.exe" --image "F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe" --clipboard || goto :fail
echo Installing r5 into both games (only GwentBetaClipboard.asi changes)...
copy /y BetaGwent\build\clipboard090-r5\GwentBetaClipboard.asi "D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\plugins\GwentBetaClipboard.asi" || goto :fail
copy /y BetaGwent\build\clipboard090-r5\GwentBetaClipboard.asi "F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\plugins\GwentBetaClipboard.asi" || goto :fail
echo DONE. Test: Export, Copy, then load a save from the running game.
pause
exit /b 0
:fail
echo FAILED
pause
exit /b 1

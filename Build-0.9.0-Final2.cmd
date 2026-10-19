@echo off
rem Gwent Beta Classic 0.9.0 final 2: import with crafting + copy-button hang fix (bridge r5).
rem Nothing is installed into the games and nothing is published.
setlocal
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py
set BG_FINAL=release090-final2
set B=BetaGwent\build

echo [1/11] Copy-button bridge r5
if not exist %B%\clipboard090-r5\GwentBetaClipboard.asi (
  %PY% -X utf8 tools\features082\build_clipboard090.py --out %B%\clipboard090-r5 || goto :fail
)
%B%\clipboard090-r5\clipboard_bridge_test.exe --image "D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt\bin\x64\witcher3.exe" --image "F:\Steam\steamapps\common\The Witcher 3\bin\x64_dx12\witcher3.exe" || goto :fail

echo [2/11] Beta banner meshes, native pages, UI and script sources
if not exist %B%\banners090-seamfix-input\banners.json %PY% -X utf8 tools\features082\extract_banners090.py || goto :fail
if not exist %B%\banners090-native\banners-report.json %PY% -X utf8 tools\features082\build_banners090.py || goto :fail
%PY% -X utf8 tools\features082\prepare_import090.py || goto :fail

echo [3/11] Final scripts and Classic preparation
%PY% -X utf8 tools\features082\prepare_final090.py --out %B%\%BG_FINAL% --scripts-from %B%\release090-bannersUI\scripts --phase scripts || goto :fail

echo [4/11] Classic menus (about 3 min)
%PY% -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\%BG_FINAL%\classic-prepared-final --out %B%\release090-bannersUI\classic\menus --source-ui %B%\release090-bannersUI\classic\ui --input-manifest %B%\release090-bannersUI\classic\ui-inputs.json || goto :fail

echo [5/11] Next-Gen menus (about 3 min)
%PY% -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\%BG_FINAL%\classic-prepared-final --out %B%\release090-bannersUI\nextgen\menus --source-ui %B%\release090-bannersUI\nextgen\ui --input-manifest %B%\release090-bannersUI\nextgen\ui-inputs.json || goto :fail

echo [6/11] Import UI checks
node tools\features082\check_import090.js || goto :fail
node tools\features082\check_banners090.js || goto :fail

echo [7/11] Stage menus and native files
%PY% -X utf8 tools\features082\prepare_final090.py --out %B%\%BG_FINAL% --phase stage --menus %B%\release090-bannersUI --native %B%\clipboard090-r5 --banners %B%\banners090-native || goto :fail

echo [8/11] Classic 1.32 script compile
%PY% -X utf8 tools\classic132\native_compile.py --probe-root %B%\universal081\classic-runtime --prepared %B%\%BG_FINAL%\classic-prepared-final --label release090-final2-import --compiler-feedback || goto :fail

echo [9/11] Next-Gen script compile
%PY% -X utf8 tools\features082\compile_nextgen_final090.py || goto :fail

echo [10/11] Archives
%PY% -X utf8 tools\features082\package_final090.py classic --classic-compile %B%\universal081\classic-runtime\runs\release090-final2-import\result.json || goto :fail
%PY% -X utf8 tools\features082\package_final090.py nextgen --classic-compile %B%\universal081\classic-runtime\runs\release090-final2-import\result.json || goto :fail

echo [11/11] Optional-CopyButton repack and checks
%PY% -X utf8 tools\features082\repack_optional090.py || goto :fail
%PY% -X utf8 tools\features082\verify_final090.py || goto :fail
%PY% -X utf8 tools\features082\verify_banners090.py || goto :fail

echo.
echo DONE. Archives: %B%\%BG_FINAL%\package-candidate\archives-optional
pause
exit /b 0

:fail
echo.
echo FAILED at the step above. Send me the last lines; output folders are kept.
pause
exit /b 1

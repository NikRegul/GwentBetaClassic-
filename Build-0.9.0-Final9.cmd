@echo off
rem 0.9.0 release build: build 8 UI without the visible banner test text,
rem clipboard bridge r7 in Optional-CopyButton, Import/Export hidden without bin. Build 7 scripts and both compiles
rem are reused after SHA checks. Result is collected in BetaGwent\release\GwentBetaClassic-0.9.0.
setlocal
cd /d "%~dp0"
set B=BetaGwent\build
set BG_SOURCE=release090-final7
set BG_FINAL=release090-final9
set BG_UI=release090-ui9
set BG_BANNERS=banners090-sdk-fix5
set BG_BANNER_INPUT=banners090-rays-input
set BG_CLASSIC_LABEL=release090-final7
set C=%B%\universal081\classic-runtime\runs\%BG_CLASSIC_LABEL%\result.json
if not exist %B%\clipboard090-r7\GwentBetaClipboard.asi (echo Bridge r7 missing: run Build-Clipboard-r7.cmd first & goto :fail)
echo [1/7] UI patch and checks
python -X utf8 tools\features082\prepare_ui9_090.py || goto :fail
node tools\features082\check_ui9_banners090.js || goto :fail
rem Nexus description is regenerated before packaging: README_EN/RU in the archives are copied from it.
python -X utf8 tools\features082\refresh_showcase090.py || goto :fail
echo [2/7] Menus (about 6 min)
for %%P in (classic nextgen) do (
 python -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\%BG_SOURCE%\classic-prepared-final --out %B%\%BG_UI%\%%P\menus --source-ui %B%\%BG_UI%\%%P\ui --input-manifest %B%\%BG_UI%\%%P\ui-inputs.json || goto :fail
)
echo [3/7] Stage (reuse build 7 compiles)
python -X utf8 tools\features082\stage_build8_090.py || goto :fail
echo [4/7] Archives
python -X utf8 tools\features082\package_final090.py classic --classic-compile %C% || goto :fail
python -X utf8 tools\features082\package_final090.py nextgen --classic-compile %C% || goto :fail
echo [5/7] Optional-CopyButton repack
python -X utf8 tools\features082\repack_optional090.py || goto :fail
echo [6/7] Checks
python -X utf8 tools\features082\verify_final090.py || goto :fail
python -X utf8 tools\features082\verify_banners090.py || goto :fail
echo [7/7] Release folder
python -X utf8 tools\features082\assemble_release090.py || goto :fail
echo.
echo DONE. Everything for Nexus: BetaGwent\release\GwentBetaClassic-0.9.0
echo Install both archives once more (Mods and, for 1.32, DLC) and check in game.
pause
exit /b 0
:fail
echo.
echo FAILED at the step above. Output folders are kept; send me the last lines.
pause
exit /b 1

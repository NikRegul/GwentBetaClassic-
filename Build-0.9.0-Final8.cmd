@echo off
rem 0.9.0 build 8: centred power numbers in deck lists. UI only: build 7 scripts
rem and both compiles are reused after SHA checks. Nothing is installed or published.
setlocal
cd /d "%~dp0"
set B=BetaGwent\build
set BG_SOURCE=release090-final7
set BG_FINAL=release090-final8
set BG_UI=release090-ui8
set BG_BANNERS=banners090-sdk-fix5
set BG_BANNER_INPUT=banners090-rays-input
set BG_CLASSIC_LABEL=release090-final7
set C=%B%\universal081\classic-runtime\runs\%BG_CLASSIC_LABEL%\result.json
echo [1/6] UI patch and checks
python -X utf8 tools\features082\prepare_ui8_090.py || goto :fail
node tools\features082\check_ui7_banners090.js || goto :fail
echo [2/6] Menus (about 6 min)
for %%P in (classic nextgen) do (
 python -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\%BG_SOURCE%\classic-prepared-final --out %B%\%BG_UI%\%%P\menus --source-ui %B%\%BG_UI%\%%P\ui --input-manifest %B%\%BG_UI%\%%P\ui-inputs.json || goto :fail
)
echo [3/6] Stage (reuse build 7 compiles)
python -X utf8 tools\features082\stage_build8_090.py || goto :fail
echo [4/6] Archives
python -X utf8 tools\features082\package_final090.py classic --classic-compile %C% || goto :fail
python -X utf8 tools\features082\package_final090.py nextgen --classic-compile %C% || goto :fail
echo [5/6] Optional-CopyButton repack
python -X utf8 tools\features082\repack_optional090.py || goto :fail
echo [6/6] Checks
python -X utf8 tools\features082\verify_final090.py || goto :fail
python -X utf8 tools\features082\verify_banners090.py || goto :fail
echo.
echo DONE. Archives: %B%\%BG_FINAL%\package-candidate\archives-optional
echo For 1.32 update Mods (DLC unchanged since build 7, updating it is harmless).
pause
exit /b 0
:fail
echo.
echo FAILED at the step above. Output folders are kept; send me the last lines.
pause
exit /b 1

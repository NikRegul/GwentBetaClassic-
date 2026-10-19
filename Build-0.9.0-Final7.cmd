@echo off
rem 0.9.0 build 7: UI review of build 6 + two card fixes (Myrgtabrakke, Harald).
rem Scripts change, so both script compiles run again. Nothing is installed or published.
setlocal
cd /d "%~dp0"
set B=BetaGwent\build
set BG_FINAL=release090-final7
set BG_BANNERS=banners090-sdk-fix5
set BG_BANNER_INPUT=banners090-rays-input
set BG_UI=release090-ui7
echo [1/9] UI patch and checks
python -X utf8 tools\features082\prepare_ui7_090.py || goto :fail
node tools\features082\check_ui7_banners090.js || goto :fail
echo [2/9] Scripts with card fixes and Classic preparation
python -X utf8 tools\features082\prepare_scripts7_090.py || goto :fail
python -X utf8 tools\features082\prepare_final090.py --out %B%\%BG_FINAL% --scripts-from %B%\release090-scripts7\scripts --phase scripts || goto :fail
echo [3/9] Menus (about 6 min)
for %%P in (classic nextgen) do (
 python -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\%BG_FINAL%\classic-prepared-final --out %B%\%BG_UI%\%%P\menus --source-ui %B%\%BG_UI%\%%P\ui --input-manifest %B%\%BG_UI%\%%P\ui-inputs.json || goto :fail
)
echo [4/9] Stage menus, bridge r6b and banner pages
python -X utf8 tools\features082\prepare_final090.py --out %B%\%BG_FINAL% --phase stage --menus %B%\%BG_UI% --native %B%\clipboard090-r6b --banners %B%\%BG_BANNERS% || goto :fail
echo [5/9] Classic 1.32 script compile
python -X utf8 tools\classic132\native_compile.py --probe-root %B%\universal081\classic-runtime --prepared %B%\%BG_FINAL%\classic-prepared-final --label release090-final7 --compiler-feedback || goto :fail
echo [6/9] Next-Gen script compile
python -X utf8 tools\features082\compile_nextgen_final090.py --input %B%\%BG_FINAL% || goto :fail
echo [7/9] Archives
python -X utf8 tools\features082\package_final090.py classic --classic-compile %B%\universal081\classic-runtime\runs\release090-final7\result.json || goto :fail
python -X utf8 tools\features082\package_final090.py nextgen --classic-compile %B%\universal081\classic-runtime\runs\release090-final7\result.json || goto :fail
echo [8/9] Optional-CopyButton repack
python -X utf8 tools\features082\repack_optional090.py || goto :fail
echo [9/9] Checks
python -X utf8 tools\features082\verify_final090.py || goto :fail
python -X utf8 tools\features082\verify_banners090.py || goto :fail
echo Nexus description (13 languages) from updated manual.md
python -X utf8 tools\features082\refresh_showcase090.py || goto :fail
echo.
echo DONE. Archives: %B%\%BG_FINAL%\package-candidate\archives-optional
echo For 1.32 update BOTH Mods and DLC from the archive.
pause
exit /b 0
:fail
echo.
echo FAILED at the step above. Output folders are kept; send me the last lines.
pause
exit /b 1

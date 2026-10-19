@echo off
rem 0.9.0 build 6: banner pages with ExporterInfo first, tolerant banner loading with
rem a visible failure reason, no tick above the row placement preview. UI-only:
rem gameplay scripts and both compiles are reused from build 5 (checked by SHA).
rem Nothing is installed into the games and nothing is published.
setlocal
cd /d "%~dp0"
set B=BetaGwent\build
set BG_UI=release090-banner-runtime3
set BG_FINAL=release090-final6
set BG_BANNERS=banners090-sdk-fix5
set BG_BANNER_INPUT=banners090-rays-input
set C=%B%\universal081\classic-runtime\runs\release090-final2-import-unrestricted\result.json
echo [1/8] UI patch
python -X utf8 tools\features082\prepare_banner_runtime3_090.py || goto :fail
node tools\features082\check_banner_runtime3_090.js || goto :fail
echo [2/8] Banner pages (GFxExport, about 2 min)
python -X utf8 tools\features082\build_banners090.py --out %B%\%BG_BANNERS% --input %B%\%BG_BANNER_INPUT% || goto :fail
echo [3/8] Menus
for %%P in (classic nextgen) do (
 python -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\release090-final2\classic-prepared-final --out %B%\%BG_UI%\%%P\menus --source-ui %B%\%BG_UI%\%%P\ui --input-manifest %B%\%BG_UI%\%%P\ui-inputs.json || goto :fail
)
echo [4/8] Stage
python -X utf8 tools\features082\stage_build6_090.py || goto :fail
echo [5/8] Classic 1.32 archive
python -X utf8 tools\features082\package_final090.py classic --classic-compile %C% || goto :fail
echo [6/8] Next-Gen archive
python -X utf8 tools\features082\package_final090.py nextgen --classic-compile %C% || goto :fail
echo [7/8] Optional-CopyButton repack
python -X utf8 tools\features082\repack_optional090.py || goto :fail
echo [8/8] Checks
python -X utf8 tools\features082\verify_final090.py || goto :fail
python -X utf8 tools\features082\verify_banners090.py || goto :fail
echo.
echo DONE. Archives: %B%\%BG_FINAL%\package-candidate\archives-optional
echo For 1.32 update BOTH Mods and DLC from the archive.
pause
exit /b 0
:fail
echo.
echo FAILED at the step above. Output folders are kept; rename them before a rerun.
pause
exit /b 1

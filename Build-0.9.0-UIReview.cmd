@echo off
rem UI-only candidate. Requires the completed, compiled release090-final2.
rem Uses fresh output directories; never installs or publishes the result.
setlocal
cd /d "%~dp0"
set BG_UI=release090-ui-review2
set BG_FINAL=release090-final3
set B=BetaGwent\build
set C=%B%\universal081\classic-runtime\runs\release090-final2-import-unrestricted\result.json

python -X utf8 tools\features082\prepare_import090.py --out %B%\%BG_UI% || goto :fail
node tools\features082\check_import090.js || goto :fail
node tools\features082\check_banners090.js || goto :fail
node tools\features082\check_ui_review090.js || goto :fail
python -X utf8 tools\features082\preview_ui_review090.py || goto :fail

for %%P in (classic nextgen) do (
 python -X utf8 tools\universal\build_menus.py --stage 202 --prepared %B%\release090-final2\classic-prepared-final --out %B%\%BG_UI%\%%P\menus --source-ui %B%\%BG_UI%\%%P\ui --input-manifest %B%\%BG_UI%\%%P\ui-inputs.json || goto :fail
)
python -X utf8 tools\features082\stage_ui_review090.py || goto :fail
python -X utf8 tools\features082\package_final090.py classic --classic-compile %C% || goto :fail
python -X utf8 tools\features082\package_final090.py nextgen --classic-compile %C% || goto :fail
python -X utf8 tools\features082\repack_optional090.py || goto :fail
python -X utf8 tools\features082\verify_final090.py || goto :fail
python -X utf8 tools\features082\verify_banners090.py || goto :fail
echo Candidate: %B%\%BG_FINAL%\package-candidate\archives-optional
exit /b 0
:fail
echo Build failed. The last output and candidate folders are preserved.
exit /b 1

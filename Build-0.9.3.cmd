@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>&1 && (set PY=python) || (set PY=py -3)
%PY% -X utf8 tools\features093\build_release.py %*
if errorlevel 1 goto fail
echo DONE. Release folder and build path are printed above.
if not defined CODEX_NO_PAUSE pause
exit /b 0
:fail
echo FAILED. Read the printed log; existing outputs are retained.
if not defined CODEX_NO_PAUSE pause
exit /b 1

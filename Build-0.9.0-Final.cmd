@echo off
rem Gwent Beta Classic 0.9.0 final: scripts, both native compiles, both archives, checks.
rem Nothing is installed into the games and nothing is published.
setlocal
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py

echo [1/6] Prepare inputs (cleaner fix, menus with copy and Classic crash fix, native files)
%PY% -X utf8 tools\features082\prepare_final090.py || goto :fail

echo [2/6] Classic 1.32 script compile (game exe, verify-and-exit, about 1 min)
%PY% -X utf8 tools\classic132\native_compile.py --probe-root BetaGwent\build\universal081\classic-runtime --prepared BetaGwent\build\release090-final\classic-prepared-final --label release090-final-cleaner --compiler-feedback || goto :fail

echo [3/6] Next-Gen script compile (REDkit wcc_lite, about 1 min)
%PY% -X utf8 tools\features082\compile_nextgen_final090.py || goto :fail

echo [4/6] Classic 1.32 archive
%PY% -X utf8 tools\features082\package_final090.py classic --classic-compile BetaGwent\build\universal081\classic-runtime\runs\release090-final-cleaner\result.json || goto :fail

echo [5/6] Next-Gen archive
%PY% -X utf8 tools\features082\package_final090.py nextgen --classic-compile BetaGwent\build\universal081\classic-runtime\runs\release090-final-cleaner\result.json || goto :fail

echo [6/6] Move copy files to Optional-CopyButton, check archives
%PY% -X utf8 tools\features082\repack_optional090.py || goto :fail
%PY% -X utf8 tools\features082\verify_final090.py || goto :fail

echo.
echo DONE. Archives: BetaGwent\build\release090-final\package-candidate\archives-optional
pause
exit /b 0

:fail
echo.
echo FAILED at the step above. Output folders are kept; rerun needs a fresh BetaGwent\build\release090-final
echo (rename the old one) and a new Classic compile label.
pause
exit /b 1

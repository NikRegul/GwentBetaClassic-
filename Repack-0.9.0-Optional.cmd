@echo off
rem Repack the finished 0.9.0 archives: copy button files into Optional-CopyButton.
cd /d "%~dp0"
set PY=python
where %PY% >nul 2>nul || set PY=py
%PY% -X utf8 tools\features082\repack_optional090.py || goto :fail
%PY% -X utf8 tools\features082\verify_final090.py || goto :fail
echo DONE: BetaGwent\build\release090-final\package-candidate\archives-optional (newest -N)
pause
exit /b 0
:fail
echo FAILED
pause
exit /b 1

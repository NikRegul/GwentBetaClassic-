@echo off
chcp 65001 >nul
setlocal
set "HERE=%~dp0"
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('MyDocuments')"`) do set "DOCS=%%D"
set "LOG=%DOCS%\The Witcher 3\scriptslog.txt"
if not exist "%LOG%" (echo [ОШИБКА] Нет "%LOG%". Игру нужно запускать с -debugscripts. & exit /b 1)
findstr /C:"SAVEPROBE" "%LOG%" > "%HERE%last_result.txt"
type "%HERE%last_result.txt"
echo.
echo Сохранено в "%HERE%last_result.txt"

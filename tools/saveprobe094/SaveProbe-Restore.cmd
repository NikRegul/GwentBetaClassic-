@echo off
chcp 65001 >nul
setlocal EnableExtensions
set "HERE=%~dp0"
if not exist "%HERE%game_path.txt" (echo [ОШИБКА] Нет game_path.txt: зонд не устанавливался. & exit /b 1)
set /p GAME=<"%HERE%game_path.txt"
set "USED=%GAME%\Mods.saveprobe-off\used-%RANDOM%%RANDOM%"
mkdir "%USED%" || exit /b 1
if exist "%GAME%\Mods\modBetaGwentSaveProbe" move "%GAME%\Mods\modBetaGwentSaveProbe" "%USED%\" >nul
if exist "%HERE%keepitems_added.txt" if exist "%GAME%\Mods\modBetaGwentKeepItems" (
  move "%GAME%\Mods\modBetaGwentKeepItems" "%USED%\" >nul && move "%HERE%keepitems_added.txt" "%USED%\" >nul
)
if exist "%GAME%\Mods.saveprobe-off\modBetaGwent0924" (
  if exist "%GAME%\Mods\modBetaGwent0924" (echo [ОШИБКА] В Mods уже есть modBetaGwent0924, оставляю как есть. & exit /b 1)
  move "%GAME%\Mods.saveprobe-off\modBetaGwent0924" "%GAME%\Mods\" >nul || exit /b 1
)
echo Beta Gwent возвращён. Зонд перенесён в "%USED%" (ничего не удалено).

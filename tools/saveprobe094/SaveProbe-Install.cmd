@echo off
chcp 65001 >nul
setlocal EnableExtensions
set "HERE=%~dp0"
set "GAME=%~1"
if "%GAME%"=="" if exist "%HERE%game_path.txt" set /p GAME=<"%HERE%game_path.txt"
if "%GAME%"=="" set /p "GAME=Папка Next-Gen версии игры (в ней bin\x64_dx12): "
set "GAME=%GAME:"=%"
if not exist "%GAME%\bin\x64_dx12\witcher3.exe" (
  echo [ОШИБКА] Не найден "%GAME%\bin\x64_dx12\witcher3.exe". Зонд только для Next-Gen 4.0+/5.x.
  exit /b 1
)
>"%HERE%game_path.txt" echo %GAME%
if exist "%GAME%\Mods\modBetaGwentSaveProbe" (
  xcopy /E /I /Y /Q "%HERE%mod\modBetaGwentSaveProbe" "%GAME%\Mods\modBetaGwentSaveProbe\" >nul || exit /b 1
  echo Зонд уже был установлен: скрипт обновлён. Запускай игру.
  exit /b 0
)
if not exist "%GAME%\Mods.saveprobe-off" mkdir "%GAME%\Mods.saveprobe-off" || exit /b 1
if exist "%GAME%\Mods\modBetaGwent0924" (
  if exist "%GAME%\Mods.saveprobe-off\modBetaGwent0924" (
    echo [ОШИБКА] В Mods.saveprobe-off уже лежит modBetaGwent0924. Сначала запусти SaveProbe-Restore.cmd.
    exit /b 1
  )
  move "%GAME%\Mods\modBetaGwent0924" "%GAME%\Mods.saveprobe-off\" >nul || (echo [ОШИБКА] Не удалось отключить modBetaGwent0924 & exit /b 1)
  echo Мод Beta Gwent временно перенесён в "%GAME%\Mods.saveprobe-off".
)
xcopy /E /I /Y /Q "%HERE%mod\modBetaGwentSaveProbe" "%GAME%\Mods\modBetaGwentSaveProbe\" >nul || exit /b 1
if not exist "%GAME%\Mods\modBetaGwentKeepItems" (
  xcopy /E /I /Y /Q "%HERE%mod\modBetaGwentKeepItems" "%GAME%\Mods\modBetaGwentKeepItems\" >nul || exit /b 1
  >"%HERE%keepitems_added.txt" echo 1
)
echo.
echo Готово. Дальше:
echo  1. Запусти игру с параметром -debugscripts. Игра перекомпилирует скрипты.
echo  2. Загрузи любой сейв. Зонд запишет этап 1.
echo  3. Сделай РУЧНОЕ сохранение в НОВЫЙ слот и загрузи именно его.
echo     Зонд проверит этап и запишет следующий. Повторяй сохранение и загрузку,
echo     пока в логе не появится DONE или LOSS. Всего до 5 циклов,
echo     на последних загрузка может подвиснуть на несколько секунд.
echo  4. Выйди из игры и запусти SaveProbe-Show.cmd.
echo  5. Верни мод: SaveProbe-Restore.cmd.
echo Сейвы, сделанные с зондом, тестовые: на них дальше не играй.

# Самостоятельная сборка 0.3.4

Главный редактируемый скрипт: `D:\w3mod\tools\Build-GwentBeta.ps1`.
Короткий запуск текущего этапа: `D:\w3mod\tools\Build-Stage113.ps1`.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage113.ps1 -Language ru
```

Оба языка:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage113.ps1 -Language both
```

Архивы появятся в `D:\w3mod\BetaGwent\release\GwentBetaClassic-0.3.4-RU.zip` и `GwentBetaClassic-0.3.4-EN.zip`. Скрипт меняет рабочие ресурсы проекта REDkit; установку в основную игру и публикацию выполняйте отдельно. Перед установкой сохраните резервную копию сейвов. REDkit не должен одновременно экспортировать этот проект.

## Что выполняется

1. Подготовка каталога, атласа Лавка, метрик шрифта, копирования состояний ИИ и WitcherScript.
2. Компиляция четырёх меню выбранного языка, экспорт DDS/GFx, проверка 46 связей меню со скриптами и лимита памяти.
3. Нативная компиляция WitcherScript через установленный REDkit. Пустой файл или один код завершения не считаются успехом.
4. Замораживание исходников сборки, cooking ресурсов, таблиц предметов и аудио; упаковка зависимостей и метаданных.
5. Создание ZIP, списка файлов и SHA-256. Рабочий проект возвращается к русским меню, если они собраны для текущего этапа.

Уже существующий архив с тем же именем перемещается в `release\old` с датой запуска. Старые версии не перезаписываются. Логи: `BetaGwent\build\stage113\powershell` и `BetaGwent\build\stage113\logs`; отчёты: `docs\evidence`.

## Изменяемые параметры

`-Language ru/en/both`, `-Version 0.3.4`, `-Step full/prepare/scripts/menus/package`. `-CheckAI` добавляет проверки публичной модели ответа и безопасного размещения; обычная сборка не запускает длительное самообучение.

Для новых версий поменяйте параметр версии, а для отдельной папки этапа используйте главный скрипт:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-GwentBeta.ps1 -Stage 114 -Version 0.3.5 -Language ru -CheckAI
```

После правки только игрового ИИ:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage113.ps1 -Language ru -Step scripts
powershell -NoProfile -ExecutionPolicy Bypass -File D:\w3mod\tools\Build-Stage113.ps1 -Language ru -Step package
```

После правки интерфейса сначала выполните `-Step menus`. Если менялись и интерфейс, и скрипты, запускайте полную сборку. Частичная упаковка использует последнее успешное `-Step scripts`; несовпадение его исходников с текущими блокирует упаковку.

Для явного выбора компиляции одного языка есть `-Compiled D:\w3mod\BetaGwent\build\board-compile113ru-final` — путь к папке с `result.json`, а не к одному blob. Для повторного извлечения видео Лавка: `-KegVideo "C:\Users\NikR\Videos\Captures\Gwent 2026-10-08 00-12-24.mp4"`.

## Зависимости

PowerShell 5.1, Python с Pillow и NumPy, Node.js для проверок/обучения, JDK и Apache Royale из `tools\vendor`, установленный REDkit с принятой пользователем лицензией, подготовленные исходные игровые ресурсы и аудиобанк. Пути инструментов заданы в вызываемых Python-скриптах; при переносе на другой компьютер их нужно изменить. Пользователю готового мода эти инструменты не нужны.

Wwise заново при каждой сборке не запускается: используется подготовленный лицензированный банк. Исходные ресурсы CD Projekt не заменяются пустыми файлами при отсутствии — сборка должна остановиться и сообщить об ошибке.

Скрипты предыдущих этапов отражают прежний процесс; для текущих исходников используйте этот вход, чтобы случайно не назвать новый ИИ версией 0.3.3.

В текущей проверенной сборке упаковка RU/EN выполнена самим PowerShell-входом `-Step package`; отдельные компиляции меню и WitcherScript завершены до неё и зафиксированы в отчётах этапа. Полный вход соединяет эти же команды.

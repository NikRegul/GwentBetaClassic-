# Classic fix8: штатные пути для двух входных меню

## Полученное свидетельство

Пользователь запустил Classic132-Capture-Scaleform.cmd, открыл колоды до
зависания и закрыл игру. Сбор завершился без тайм-аута, exit 0. Отчёт:
BetaGwent/build/classic132-scaleform-feedback/20261016-143620-932893.
758 событий, включая 62 FILE_OPEN, 62 FILE_RESULT, 44 RESOURCE_RESOLVED
и 76 ранее скрытых GFX_MESSAGE. Установленные файлы за время сбора прежние.

На 82.264 секунде:

- FILE_OPEN: content/content0/betagwent/betagwent_decks.swf;
- RESOURCE_RESOLVED: resourceFound=false;
- FILE_RESULT: opened=false;
- GFX_MESSAGE: Loader failed to open '<тот же полный путь>'.

В штатных меню и HUD тот же маршрут получает resourceFound=true/opened=true.
В этом запуске меню колод не дошло до регистрации Flash. Текст .swf сам по
себе не является ошибкой: в exe функция 0x140689870 заменяет .swf на .redswf
перед запросом в depot. Три глобальные строки расширений и их инициализаторы
сверены в depot-resolver.txt. Поэтому переименование самого packed-файла в
.swf было бы необоснованной правкой.

resourceFound=false означает отказ получить CSwfResource. Это не позволяет
по одному событию отличить отсутствие записи depot от неудачи загрузки или
приведения ресурса. Точная внутренняя причина пока не подтверждена. В частности,
не объявляются доказанными запрет новых каталогов или исчерпание бюджета.

## Кандидат

Два входа направлены на существующие штатные Classic пути:

| Ресурс мода | Штатный путь |
| --- | --- |
| betagwent/betagwent_decks.redswf | gameplay/gui_new/swf/gwint/deck_builder.redswf |
| betagwent/betagwent_npc00.redswf | gameplay/gui_new/swf/gwint/gwint_game.redswf |

В двух .menu меняется только soft import. Все export chunks/определения меню
побайтово сохранены. В bundle два SWF переименованы без изменений payload,
GUID взяты из установленного native r4gui.bundle. Все пути/имена/директории/
FNV64 metadata согласованы с переименованием, file ID и offsets сохранены.
Размеры/CRC двух обновлённых .menu пересчитаны. Две GUID-записи dep.cache
заменены на native; индексные массивы и pool не менялись.

350 из 352 payload побайтово совпадают с fix7; отличаются только два .menu.
Flash/AS3/графика/444 текстуры, WS, аудио и остальные пути не менялись.
Максимум GUI 62.883685 МиБ. Полный bundle проверен по CRC и SHA каждого файла;
архив — по ZIP CRC, составу и SHA установочных файлов. 36 тестов Classic,
включая no-op, коллизии и согласованность нового вложенного пути/хеша/ID,
прошли. 14 структурных проверок кандидата и уже установленного fix8 прошли.

Генератор tools/universal/build_classic_stock_paths.py, bounded metadata
adapter tools/classic132/remap_depot.py. Артефакты:
BetaGwent/build/classic081-stock-paths-fix8/verification.json,
structural-audit.json, installed-audit.json.
Patch ZIP 258528951 байт, SHA cf2f612701af12bfacd1cbad4bba5dac5a78c1af6bbdecb441717f961f826161.

## Установка и незавершённая проверка

Fix8 установлен агентом в закрытую игру, четыре файла атомарно заменены
tools/classic132/install_stock_paths_fix8.ps1 после проверки исходных SHA.
Резервная копия fix7 — classic081-stock-paths-fix8/installed-before.
Bundle SHA 4d3eb67dbb205b6c91ef5aafe48bd63d4383373d0633aad597539270d4cb5fd4.
Установленная версия 0.8.1-classic-stock-paths-fix8; installation.json содержит
SHA всех четырёх файлов. Игра агентом не запускалась, Computer Use не применялся.

Первая попытка остановилась на разборе PowerShell 5 до изменения файлов:
UTF-8 без BOM прочитан как ANSI. Установщику сохранены UTF-8 BOM/CRLF,
разбор проверен через PowerShell 5 Parser::ParseFile, повторная установка
завершена. Проверка SHA и полный аудит после установки успешны.

Следующая ручная проверка пользователя — тем же сборщиком Scaleform:
колоды, редактор, выход; если этот этап успешен — NPC/выбор колоды/партия.
Важно увидеть не только FILE_RESULT, но и MENU_CONFIG/AS_BRIDGE_READY и
фактический интерфейс. До этого fix8 остаётся кандидатом, Classic не принят.

## Проверка fix8: отказ сохраняется

Пользователь проверил установленный fix8 и сообщил, что поведение прежнее.
Сбор 20261016-145455-726002 завершён: exit 0, без тайм-аута, файлы установки
не изменились. На 164.117 и 183.074 секунде запрошен уже штатный
gameplay/gui_new/swf/gwint/deck_builder.swf; оба раза resourceFound=false,
opened=false, Loader failed to open. Перенос пути не устранил отказ.
Утверждение, что виноват именно новый путь/каталог, не подтверждается.

Подготовлен отдельный профиль --profile resource в capture_scaleform.py,
ручной launcher Classic132-Capture-Resource.cmd. Четыре аппаратные точки:

- RVA 0x88826: после FindFile в depot, путь из RBP, результат RAX;
- RVA 0x91566: после GetOrLoad, CResource* из [RDI+0x10];
- RVA 0x95b68: результат ReadHeader, исходные 160 байт CR2W и имя root class;
- RVA 0x68b14c: отформатированные сообщения GFx.

ReadHeader в этом exe допускает версии до 163 включительно. Табличные reader
читают строки/имена/imports/exports привычных ширин; сами по себе статические
CRCs не показывают, был ли фактически прочитан этот файл в игре. Новый профиль
отделяет отсутствие файла от отказа загрузки объекта. Сигнатуры и SHA exe
зафиксированы в resource-trace-points.json. RTTI/строки читаются с ограничением
размеров; неизвестный объект сохраняется без попытки вызвать его методы.
Повторный self-test аппаратных точек, двух потоков, штатного завершения и
безопасного detach прошёл. Игра агентом не запускалась. Новых изменений
установки после пользовательского результата не сделано; fix8 остаётся
неработающим кандидатом, новый игровой fix не объявлен.

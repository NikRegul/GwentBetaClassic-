# Classic fix5: отрицательные ID в hash lookup metadata.store

Пользователь сообщил, что и fix4, и минимальная диагностическая накладка
оставляют игру на паузе без интерфейса. Свежий лог сохранён в
`BetaGwent/build/classic081-probe-feedback/scriptslog.txt` (718461 байт).
Накладка установлена; в логе нет MINIMAL_MOVIECLIP_PROBE и MENU_CONFIG.
Успешное замещение ресурсов этим не подтверждается.

При сравнении metadata выявлена конкретная ошибка упаковки. В нативной
metadata.store установленной Classic 1.32 все 118121 записи hash lookup
содержат положительный int64 ID файла. У fix4 351 из 352 записей содержат
верхнее слово FFFFFFFF. Предыдущая проверка ошибочно трактовала его отдельным
полем flags и проверяла лишь нижнее слово индекса. Например:

| Ресурс | ID | Старый int64 |
| --- | ---: | ---: |
| r4deck_builder.menu | 232 | -4294967064 |
| betagwent_decks.redswf | 240 | -4294967056 |

Формат `(int64 hash, int64 file_id)` подтверждается независимым парсером
[w3edit metadata.rs](https://github.com/Systemcluster/w3edit/blob/main/src/metadata.rs).
[WolvenKit-7 Metadata_Store.cs](https://github.com/WolvenKit/WolvenKit-7/blob/main/WolvenKit.Bundles/Metadata_Store.cs)
также читает второе поле целиком как Int64, хотя называет его Unk2.
Это свидетельство неверных cross-index в конвертере; причинная связь именно
с наблюдаемым зависанием ещё требует запуска пользователем.

Добавлен bounded-конвертер classic_metadata_hash_rows: принимает только
наблюдавшиеся верхние слова 0/FFFFFFFF, проверяет нижний индекс в пределах
fileInfoList и пишет положительный int64. Он используется при сборке Classic
ресурсов и будущих диагностических накладок. FNV64 путей, порядок записей,
остальные таблицы и размеры файлов не меняются.

fix5 построен из неизменяемого fix4. В игровом содержимом исправлена только
metadata.store; info.json и сопроводительные сведения обновлены. Каждый из
352 ID проверен по строковому пути и его FNV64, множество индексов полное
и уникальное. Для штатной metadata конвертер побайтово тождественен.
Все 27 тестов Classic проходят, включая регрессию отрицательного int64 и
проверку отказа на неизвестной кодировке/невалидном индексе.

Генератор: tools/universal/package_classic_metadata_fix.py. Малый патч
MetadataPatch предназначен только поверх fix4, содержит metadata.store,
info.json и README. Полный AllLanguages также собирается для чистой установки.
Перед проверкой нужно убрать mod000BetaGwentClassic132Probe, иначе в случае
успешной загрузки она покажет диагностическое окно вместо настоящих колод.
Игра агентом не запускалась; игровая приёмка отсутствует.

Обратная связь после fix5: зависание осталось. Установленный info.json содержит
0.8.1-classic-metadata-fix5, SHA-256 metadata совпадает с построенным патчем,
диагностической накладки в Mods нет. Лог сохранён в
BetaGwent/build/classic081-fix5-feedback/scriptslog.txt (718448 байт).
Впервые появилась строка BOARD_CLOSED revision=0, соответствующая
OnClosingMenu пользовательского CR4BetaGwentBoardMenu. Это свидетельствует
о создании скриптового объекта меню, но не об успешной загрузке GFx. Отметок
AS_BRIDGE_READY и MENU_CONFIG_BEGIN нет. fix5 не устранил наблюдаемый дефект;
следующий шаг — native log при ручном запуске пользователем через сборщик.

Подготовлен резервный сборщик native OutputDebugString:
tools/classic132/capture_menu_log.py и release/Classic132-Capture-Menu-Log.cmd.
Self-test успешно захватил ANSI и Unicode сообщения от собственного Python
процесса. Игру self-test не запускает. Сборщик запускается только пользователем,
не меняет исполняемый файл/моды/сохранения и не ставит compiler breakpoints.

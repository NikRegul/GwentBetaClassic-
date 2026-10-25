# Системный лог fix5 и повтор контрольной накладки

Пользователь вручную запустил Classic132-Capture-Menu-Log.cmd и повторил
зависание. Сбор завершён: exitCode=0, timedOut=false, свежий scriptslog,
installedFilesUnchanged=true. Данные находятся в
BetaGwent/build/classic132-native-feedback/20261016-083849-492039.
native-engine.txt содержит 23926 байт системных сообщений Windows и поиска
PDB через DBGHELP, без диагностической ошибки GFx/SWF/ActionScript.
Отсутствие PDB само по себе не объясняет дефект меню. В scriptslog снова
BOARD_CLOSED revision=0 без MENU_CONFIG_BEGIN или AS_BRIDGE_READY.

Повторное статическое сравнение родного DeckBuilder.redswf и пользовательского
movie: оба ExporterInfo имеют версию 4.1 и image format 14; ABC version 46.16
также совпадает. Полное меню — CFX14 и корневой Sprite, контрольный movie —
CFX12 и MovieClip, как родной Classic. Это различия для проверки, а не
установленная причина зависания.

Первая минимальная накладка оказалась непригодной для выводов о выполнении
ActionScript: оба её hash lookup ID также были отрицательными int64.
Подготовлена Probe2, где изменены только metadata.store (оба ID исправлены)
и version в info.json. blob0.bundle с минимальным MovieClip сохранён
побайтово. Все два пути сверены с FNV64, ZIP CRC и полный состав проверены.
Архив: BetaGwent/release/GwentBetaClassic-1.32-MinimalMenu-Probe2.zip,
8058 байт. Не является игровым исправлением. Основной fix5 оставляют на месте,
накладку копируют в Mods и проверяют обычное открытие колод. Ожидается простой
экран CLASSIC PROBE, затем MENU_CONFIG completed. После теста накладку удаляют.

Успешный показ сузит проблему до полного movie и его ресурсов/инициализации.
При отсутствии окна нельзя автоматически заключать, что простейший AS не
поддерживается: нужно проверять подмену ресурса, а затем контроль с родным
неизменённым CSwfResource. Игру агент не запускал, Computer Use не использовал.

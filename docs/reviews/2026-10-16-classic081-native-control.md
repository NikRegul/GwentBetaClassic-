# Probe2 не открылось; контроль неизменённого штатного movie

Пользователь повторно сообщил о паузе без окна. Установлены Probe2 и fix5;
info.json накладки и SHA-256 metadata.store совпадают с построенной Probe2.
Свежий scriptslog (718151 байт) сохранён в
BetaGwent/build/classic081-probe2-feedback/scriptslog.txt. В нём нет
MINIMAL_MOVIECLIP_PROBE, MENU_CONFIG_BEGIN, AS_BRIDGE_READY и BOARD_CLOSED.
Отсутствие отметок не доказывает, что корневой MovieClip был создан.

Повторно проверены hash lookup обеих metadata: сортировка по unsigned FNV64
совпадает с нативной; ID положительны, ссылки на bundle/entries/init paths
корректны. Native DeckBuilder ABC извлечён и прочитан из установленной 1.32:
registerMenu использует ExternalInterface.call("registerMenu", menuName,
this), что соответствует текущему вызову. Версия ABC и ExporterInfo также
совпадают. Эти проверки не локализуют отказ загрузки пользовательского movie.

Подготовлен NativeMenu-Control, в котором НЕТ нашего ActionScript или SWF.
Единственный ресурс — r4deck_builder.menu. В нём сохранены все исходные
свойства родного CMenuResource/CMenuDef и дочерних параметров 1.32, включая
renderGameWorld=false, паузу и soft import штатного SWF. Изменён только
menuClass на CR4BetaGwentBoardMenu; контейнер перенесён из v162 в поддерживаемый
сборщиком v163 с пересчётом таблиц/CRC. Flash читается непосредственно из
gameplay/gui_new/swf/gwint/deck_builder.redswf установленной игры, неизменённым.

При успешной регистрации штатного movie наш OnConfigUI запишет
MENU_CONFIG_BEGIN, затем BOARD_MISSING_FLASH_FUNCTION и закроет меню (после
этого ожидается BOARD_CLOSED). Проверка намеренно завершается раньше
инициализации колод/сессии: штатный Flash не имеет функций нашего интерфейса.
Визуально окно может лишь мелькнуть, поэтому scriptslog обязателен для вывода.

Пакет заменяет прежнюю mod000BetaGwentClassic132Probe; основной fix5 остаётся.
Архив BetaGwent/release/GwentBetaClassic-1.32-NativeMenu-Control.zip, 3966 байт.
Генератор tools/universal/build_classic_native_control.py проверяет
неизменность import и дочерних chunks, семантическое равенство прочих root
свойств, наличие исходного SWF в r4gui.bundle, SHA-256 исходного movie,
единственность ресурса и положительный ID в metadata, ZIP CRC.

minimal_metadata обобщён на любое положительное количество исходных ресурсов
вместо прежних двух; новый однофайловый пакет проверен round trip. Три теста
metadata hash converter проходят. Игра агентом не запускалась, Computer Use
не использовался. Это диагностический контроль, не объявленное исправление.

## Результат пользователя и следующая изоляция

Пользователь подтвердил краткое открытие и автоматическое закрытие.
Свежий scriptslog сохранён в classic081-native-control-feedback; в нём два
повтора MENU_CONFIG_BEGIN menu=DeckBuilder, BOARD_MISSING_FLASH_FUNCTION,
BOARD_CLOSED revision=0. Тем самым подтверждено создание нашего WS-класса,
регистрация со штатным SWF и прохождение до первой проверки Flash-функций.
Это не подтверждает всю игровую логику нашего интерфейса.

Построен NativeMenu-CustomPath-Control. .menu имеет побайтово те же export
chunks, что успешный контроль; меняется только import path с штатного пути
на betagwent/betagwent_decks.redswf. Сам CSwfResource вместе с movie, всеми
штатными текстурами и заголовком взят из установленной игры побайтово, SHA-256
b1c9e997cc81e94e04a3a66aac7eba0826f11df19b82c900c4c9b0105545e000.
Теперь он упакован в мод по нашему пути, а не читается из базового r4gui.bundle.
Это контролирует поиск пользовательского ресурса отдельно от его кода.

Генератор tools/universal/build_classic_native_alias.py. Два metadata ID
положительны; пути/FNV64 и ZIP CRC проверены. Архив
GwentBetaClassic-1.32-NativeMenu-CustomPath-Control.zip, 1304010 байт.
Накладка заменяет прежнюю в той же папке mod000BetaGwentClassic132Probe;
основной fix5 остаётся. Ожидание — та же цепочка лога и автоматическое закрытие.
При успехе последующий тест может контролировать оболочку CSwfResource;
при отказе сначала нужно проверить чтение custom path/dependencies.

Дополнительно минимальный SWF экспортирован установленным официальным
gfxexport_mult4fix (GFxExport v4.01 / SDK v4.3.27) в workspace. Экспорт успешен,
ABC побайтово сохранён; он убирает ScriptLimits и создаёт ExporterInfo под
именем probe. В первой ручной упаковке сохранялся ExporterInfo от board.
Это наблюдаемые отличия, не доказанная причина дефекта. Игра не запускалась.

> **Этап85: исправления контроллера/бочек и начало улучшения общего ИИ.**
> Этап84 не прошёл игровую проверку. Теперь исправлена доставка событий Stage,
> добавлены переход через край и оси TW3; действие бочки задаётся в итоговых
> данных инвентаря, купленные бочки также открываются из меню колод.
> ИИ бережёт руку во втором раунде, оценивает часть целей/движков, шпионов и сброс Брана.
> Новая игровая приёмка ожидается. Далее тестовый пакет86, полный Wwise/архетипы87.
> [Изменения и короткая проверка85](D:/w3mod/docs/controller_and_ai85.md) · [План](D:/w3mod/docs/plan.md).

> **Текущий этап84: управление с контроллера и исправление Use бочек.**
> Бой, точная вставка, цели, обязательные выборы, муллиган, карта/сбросы,
> редактор, каталог, бочки и штатный ввод имени/поиска. Видимый фокус,
> защита удержания кнопок, пас удержанием, Xbox/PlayStation и смена устройства.
> Wcc84a и все три UI/43 связи проверены и установлены; ввод ждёт игровой приёмки.
> Далее тестовый релиз85 с текущим звуком/ИИ, полный Wwise/архетипы после него.
> [Кнопки и проверка84](D:/w3mod/docs/controller84.md) · [План](D:/w3mod/docs/plan.md).

> **Обновление79d: после Reload банк всё ещё не находился.**
> Исправлено имя betagwent79.bnk в скрипте/автозагрузке; дополнительный банк
> установлен в папку звуков REDkit. Исходные739 банков не изменены.
> Требуется полностью перезапустить редактор и проверить одну фразу.
> [Текущий шаг](D:/w3mod/docs/audio79d.md). Ниже — исторический статус79c.

> **Этап79c: исправления способностей и отображения силы.**
> Офицер «Врихедд», Итлина, Дрессировщик и таймер мечника; случайный первый
> ход, белая/красная/зелёная сила. UI/native34 функции; скрипты в workspace.
> Звук79b пока не работает: лог подтверждает незагруженный банк. Требуется
> ручной Tools → Sound → Reload soundbanks; пакет без Init подготовлен.
> [Изменения/проверка](D:/w3mod/docs/combat_fixes79c.md) · [План](D:/w3mod/docs/plan.md).
> Ниже сохранены исторические статусы.

> **Этап79b: первый банк звуков беты установлен.**
> 125 русских фраз +75 эффектов;140 voice/77 effect bindings.
> Wwise2023.1.19 собрал200 медиа/202 события без предупреждений; Wcc79b успешен.
> Озвучка включена в скриптах. После перезапуска REDkit нужен один общий
> проход: голоса, эффекты, переключатели и skip/close. Слышимый звук ещё не принят.
> Trial ограничивает проект200 медиа; полное покрытие требует подходящей лицензии.
> [Проверка](D:/w3mod/docs/audio79.md) · [План](D:/w3mod/docs/plan.md).
> Ниже сохранены исторические статусы предыдущих этапов.

> **Этап79a: добавлен звуковой слой, импорт беты подготовлен.**
> Штатные TW3 эффекты следуют анимациям; отдельные переключатели звука/фраз.
> Пользователь подтвердил78b и исчезновение лагов. Wcc79a/native/33 функции
> собраны; игровое проигрывание79a ещё не принято.240 WAV готовы,140 voice/
> 117 effect bindings; Wwise2023.1.19 надо установить, оригинальный банк
> пока не собран/не установлен («Фразы: ждут банк»).
> [Подробности](D:/w3mod/docs/audio79.md) · [План](D:/w3mod/docs/plan.md).
> Ниже сохранена история предыдущих этапов.

# BetaGwent: самостоятельная сборка UI probe

> **Текущий статус 2026-10-03: версия63 — призыв, массовые действия и раунды.**
> Призыв из колоды/создание токенов, порядок массовых изменений, отдельная
> потеря брони, единая очистка поля, крупный итог счёта и отметки побед.
> Имлерих и Адда: стрыга; пятая сборка «Мороз и контроль» и её тактика ИИ.
> 45 definitions/art,34 .ws,5 сборок Monsters,2 лидера. Другие фракции впереди.
> Wcc63c/AS3/GFx/native/bridge успешны;63 установлена, игровая проверка позже.
> [План](D:/w3mod/docs/plan.md), [Изменения63](D:/w3mod/docs/animations_control63.md).
> Ниже история; прежние статусы не являются текущим статусом.

Рабочий результат: AS3 → SWF14 → GFx. Компилятор Apache Royale0.9.12, открытые compile-time Flash API typedefs Apache Royale0.9.12, bundled REDkit GFxExport4.01/SDK4.3.27. Java18 уже установлен. Adobe Animate, AIR installer и Flash Player runtime не устанавливались. Инструменты лежат в D:\w3mod\tools\vendor; PATH/registry не менялись.

```powershell
python D:\w3mod\tools\ui\build_probe.py
```

Итог: [SWF](D:/w3mod/tools/ui/build/betagwent_ui_probe.swf), [GFx](D:/w3mod/tools/ui/build/betagwent_ui_probe.gfx), [build evidence](D:/w3mod/docs/evidence/ui-probe-build.json). Проверены header lengths, AS3 flag, DoABC, SymbolClass0=BetaGwentUIProbe. Это не screenshot или runtime проверка. Поле exported=true не означает redswfCreated/nativeMenuRegistered/runtimeBridgeVerified.

Для восстановления инструментов: fetch_royale.py и fetch_player_api.py скачивают конкретные официальные artifacts, проверяют опубликованные SHA512/SHA1 и сохраняют SHA256 evidence. Нужен сетевой доступ. Установочные/postinstall scripts не запускаются. Apache LICENSE/NOTICE сохранены рядом с dependencies. Ранний Flex4.16.1 сохранён как неудавшийся альтернативный компилятор; build_probe его не использует. С его импортом Royale SWC возникали missing method/prototype errors.

## Протокол эксперимента

1. AS при добавлении на stage вызывает ExternalInterface.registerMenu("BetaGwentUIProbe",this), как CoreMenu.onCoreInit/registerMenu. Затем ждёт injected _NATIVE_callGameEvent и сообщает OnConfigUI. Это предполагаемый минимальный native contract; в игре ещё не проверен.
2. WitcherScript получает setProbeState и передаёт counter0/message; UI должен показать сообщение подключения.
3. Click отправляет OnBetaGwentProbeIntent(counter+1). Script проверяет последовательность, меняет counter и возвращает setProbeState(counter,message). Ответ отображает число; UI сам его не повышает. Это позволяет наблюдать обе стороны bridge.
4. Esc отправляет OnBetaGwentProbeClose. OnClosingMenu восстанавливает EMPTY_CONTEXT/mouse cursor, пишет UI_PROBE_CLOSED. Console bgui_close — запасной выход именно из этого меню.

Script находится в [bridge source](D:/w3mod/tools/ui/bridge/scripts/game/betagwent/uiProbeMenu.ws). Отдельная сборка bridge-compile02 прошла: exit0, Success message, blob1644 bytes, SHA2561C3CD59E5824A36F9FE417110D765AEB478D582D879A8596E5E6DCD368FD8A78. [Compile result](D:/w3mod/tools/ui/build/bridge-compile02/result.json). Первый compile выявил void return в event; ранние выходы заменены на return false. Это compile evidence, не проверка mouse/input lifecycle в игре.

Отдельная сборка не включает старый capabilityProbe и не изменяет active project patch. После регистрации resource/menu понадобятся обе sources в проекте и повторная compile. До регистрации bgui_open не использовать: script command не создаёт menu resource.

Ожидаемые logs: UI_PROBE_CONFIGURED → RESPONSE counter0 → INTENT counter1 → RESPONSE counter1 → INTENT counter2 → RESPONSE counter2 → CLOSED counter2. Для приёмки нужны и logs, и обновление числа на экране, и возвращение управления Геральтом. Сохраняемые данные/коллекция/награды в этом эксперименте не затрагиваются.

## Оставшийся этап: resource и native menu registration

В installed sources найдены бинарные CMenuResource:

- gameplay/gui_new/guirsrc/r4gwint_game.menu: menuClass=CR4GwintGameMenu, menuFlashSwf soft:CSwfResource, menuDef ptr:CMenuDef.
- gameplay/gui_new/guirsrc/r4test.menu: menuClass=CR4TestMenu.
- gameplay/gui_new/guirsrc/r4default.guiconfig: CGuiConfigResource; registration graph ещё не декодирован.

Для отдельного probe нужен CMenuResource с menuClass=CR4BetaGwentUIProbeMenu, своим menuFlashSwf и registration name BetaGwentUIProbe. Не заменять vanilla GwintGame без доказанной обратимости/cleanup. Binary config не патчился по строкам; authoring/registration выполнять штатно через REDkit после проверки его resource workflow. Официальный tutorial12 UI modding доступен через [индекс видео CDPR](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/28737537/Video+tutorials).

CLI импорт исследован в isolated output directory tools/ui/build/import-depot:

- swfimport запускает CFlashImporter, который сам вызывает GFxExport. Нужен raw SWF, GFx нельзя подменять входным SWF.
- С raw FWS удалось получить importer log magicCFX, затем ошибка diskFile.cpp2633: corrupted internal loaded flag. Выход0, .redswf не создан.
- Общий import вернул1 без сохранённого resource; он не доказал рабочую альтернативу.
- -help у swfimport не показал usage; пробный вызов с пустым input завершился без artifact. Не использовать этот запуск как безопасную универсальную help-команду.

Попытки/логи сохранены в ui-probe-import-attempt01..03.json и import-wcc-attempt01..03.log. Последний successful SWF build мог быть новее импортируемой версии; manifest каждой попытки содержит её input hash. CLI import не закрывает UI gate. Следующий шаг: проверить редакторский Import .swf и создать/подключить отдельный CMenuResource, затем выполнить описанный runtime round trip.

GFxExport может вернуть0 с Error в тексте; build runner проверяет и log, и output/tag invariants. Royale по умолчанию создал LZMA ZWS, который bundled exporter не прочитал; probe-config задаёт compress=false/FWS. Это совместимость tool pipeline, не отказ от поддержки сжатого CFX ресурса игры.

## Актуальный путь: поле DIY — 2026-10-02

Исторический probe выше не является текущим меню. Новое поле: BetaGwent/ui; GUI importer создал .redswf, .menu сохранён с CR4BetaGwentBoardMenu. GUI registration проверена на диске и применена в project overlay. Screenshot подтверждает native отображение DIY-доски. Native DisplayObject receiver assert исправлен; ABC установлен в существующий .redswf без UI. Пользователь и editor.log подтвердили bridge/поле,116/104 checks failed0. Версия15 дала123 request checks failed0 и switch128 diagnostic.18 исправляет default и добавляет interactive choices/targets/FLOW43; её native проверка ещё предстоит. Native importer удачно обошёл прежний CLI loaded-flag blocker.

- `python tools/ui/register_board.py`: read-only audit config/menu/movie; `--apply` копирует валидную конфигурацию в project overlay и отказывается перезаписывать отличающийся пользовательский файл.
- `python tools/ui/check_registration.py`:6 checks guards целостности прежних menus и других GUI полей.
- `python tools/ui/prepare_board_scripts.py`: UTF-8 BOM, известные sources, active vs previous patch guard. При ручном изменении active sources остановится до записи; сначала нужно разобрать эти изменения.
- `python tools/ui/capture_board_preparation.py`: текущая board-compile26/artifact/source hashes и resource audit; проверяет соответствие recorded before/after compile inputs.
- `python tools/ui/capture_board_runtime.py`: latest attempt, callback/view/check summaries и relevant errors. Visual rendering и restored input остаются пользовательскими наблюдениями.
- `python tools/ui/check_runtime_capture.py`:15 synthetic parser checks, включая native receiver errors без имени мода, границы до close, failed/skipped повторное открытие после старой успешной сессии. Проверяет также отсутствие нового REQUEST batch и REQUEST failure при успешных старых summaries. Не пишет поддельные игровые результаты в evidence.

Ручная инструкция: [BOARD_CHECK.md](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md). План: [plan.md](D:/w3mod/docs/plan.md). Installed sources и TW3 не менялись.

- `python tools/ui/check_board_bridge.py`: проверяет compiled ABC нового SWF: handshake через общий send, native Function.call с receiver getlocal0/this, отсутствие getglobalscope в этих методах. Сохраняет компактные snippets и board-bridge-bytecode.json; native импорт/runtime не заявляет.

- `python tools/ui/update_board_resource.py`: строгая file-only замена DoABC и stored raw SWF в текущем CSwfResource v164. Допускает только SWF с теми же non-ABC tags; сохраняет native image tags/root props/textуры, обновляет offsets/CRC. Без флага создаёт candidate; `--apply` сохраняет backup и атомарно устанавливает ресурс. Не заменяет importer для изменений досок/ресурсов.
- `python tools/ui/check_resource_update.py`:5 checks установленного кода/сохранности ресурсов и отклонения header/table/root/texture corruption. Native runtime не подменяет.

- `python tools/ui/check_request_bridge.py`:8 checks фактического ABC — public signatures, request-key activation capture, four context wire values и ожидание authoritative snapshot. Native interaction не заявляет.
- Runtime capture учитывает FLOW_CHECK и REQUEST_FLOW, не принимает REQUEST_FIXTURE за UI interaction и блокирует clean acceptance при mod script errors.

Текущая script patch28:24 active sources, blob142099bytes, POWER55 pending.
Исторический этап28: Flash/resource тогда не изменялись.
Manager26 принят отдельно. Новый manual command: bgpower_check(), combined200
assertions39/20/86/55. Import/menuResource edits не нужны.

## Исправление иллюстраций39

В38 динамический BitmapData decoder не загрузил ни одного арта в игре.
В39 build_card_art.py создаёт PNG atlas768×360 и AS3 Embed; build_board.py
экспортирует DXT5 DDS штатным GFxExport. install_native_atlas.py --apply
выполнил одноразовую миграцию4→6 CSwfTexture, сохранив прежние доски побайтно.
В41 installer расширен: обновляет существующий atlas в ресурсе с6 textures,
принимает atlas768×360/540 и сохраняет4 board chunks побайтно.
Дальнейшие изменения только ABC устанавливаются update_board_resource.py.
При изменениях изображений он откажет; потребуется новая миграция/import.
Default capture_board_preparation —39. Лог теперь содержит текст ошибки
BOARD_ARTWORK_FAILURE. В39 движок отклонил atlas-v1.dds: swfLinkageName .gfx
missing. Repair40 меняет filename в обеих ImageInfo и CSwfTexture на
movie linkage prefix + _i6.dds. repair_atlas_linkage.py --apply уже выполнен,
повторно не запускать. Будущий installer тоже выводит это имя.
capture/update проверяют parent linkage всех DDS; отображение40 подтверждено.
Default capture — board-compile41-final,31 active sources. В41 atlas768×540,
16 bindings; добавлен setWeatherRow(rev,side,zone,active,damage). Row modes:
1any,2own leader,3enemy Frost,4own Rally,5First Light choices (без row request).

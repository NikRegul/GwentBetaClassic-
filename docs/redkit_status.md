# REDkit: установленная версия и точки интеграции

Дата: 2026-10-01. Установка: `D:\GOG Galaxy\Games\The Witcher 3 REDkit`. Пользователь подтвердил готовность **depot `D:\w3mod\depot`** и создал проект. Найден `D:\w3mod\GwentB\myproject1\myproject1.w3edit`; manifest depot1.6 содержит 41306 records. Полный editor Depot-is-valid audit не повторялся.

## Проверенные результаты

| Проверка | Результат |
|---|---|
| editor.exe FileVersion | 5.0.0.1042178(Build Machine) |
| witcher3Release.exe REDkit | 5.0.0.1040524(Build Machine) |
| witcher3.exe TW3, DX12 | 5.0.0.1044392(Build Machine) |
| Установленный r4data | 232114 файлов в последнем снимке; .download=0 |
| .ws REDkit → TW3 | 1527 путей, 1524 побайтово одинаковы, отсутствующих=0 |
| Различающиеся .ws | commonMenu.ws, startupExperienceMenu.ws, states/meditation/meditation.ws |
| Проверенные Gwent hooks | gwintManager/BaseMenu/GameMenu/Menu, deckBuilderMenu, r4Player, playerWitcher, inventoryComponent, quest_function совпадают побайтово |
| Современный ActionScript Gwent | 30 файлов в gameplay/gui_new/actionscript/red/game/witcher3/menus/gwint |
| XML Gwent | Пять пар items/items_plus; все пары побайтово одинаковы |
| Колоды | 56 deck_collection, по 3 difficulty variants: 168 записей в одном def_gwint_decks.xml |
| Rewards | 38 выбранных записей из base/ep1/bob rewards.xml |

Различия scripts касаются звука медитации и marketing consent, diff сохранён. Сверка двух наборов не доказывает чистоту всех модов/bundles. Доступность installed r4data не означает готовность user depot.

[Официальный changelog REDkit](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/12058625/Changelog) для 5.0 от 29.09.2026 описывает scope-based overrides, script blobs, CLI-компиляцию и расширение Gwent XML/name-based modding. Эти возможности ещё требуют локального smoke test.

## Правильный ActionScript reference

Контейнерный разбор SWF SymbolClass подтвердил:

- gameplay/gui_new/swf/gwint/gwint_game.swf → root red.game.witcher3.menus.gwint.GwintGameMenu.
- .../deck_builder.swf → root red.game.witcher3.menus.gwint.DeckBuilderMenu.

Длины совпали с header, теги в границах, найден End. Сохранены symbols/DoABC metadata; AVM2 не декомпилировался. Root/callback matching связывает современный source с SWF, но не доказывает эквивалентность каждого метода source и compiled ABC.

Другой каталог gameplay/gui_new/gwint/Engine — старый AIR project: root Gwint, output Panel_Gwint.swf, callback OnBattleResults(lives,lives). В текущем .ws используется OnMatchResult(bool). Старый Engine не выбирать integration baseline.

Современные FLA: gameplay/gui_new/fla/witcher3/gwint/{GwintGame,DeckBuilder}.fla. Python zipfile на обоих вернул Bad magic number for central directory; SHA256/header/EOCD записаны. Это не проверка Adobe authoring tool и не доказательство повреждения всего depot. UI rebuild пока не подтверждён.

## Цепочка UI и логики

Пути ниже относительно gameplay/gui_new/actionscript/red/game/witcher3/menus/gwint.

| Участок | Источник |
|---|---|
| Templates | GwintBaseMenu.as:21 → gwint.card.templates → CardManager.onGetCardTemplates |
| Матчевые данные | GwintGameMenu.as:115+ registers player.deck, enemy.deck, cardValues, toggleAI |
| FSM | GwintGameFlowController.as:61–72: Initializing, Tutorials, SpawnLeaders, CoinToss, Mulligan, RoundStart, PlayerTurn, ChangingPlayer, ShowingRoundResult, ClearingBoard, ShowingFinalResult, Reset |
| Контроллеры | HumanPlayerController / AIPlayerController |
| Runtime карт | CardManager lists/instances/decks, CardInstance state/power, CardTransaction moves |
| Эффекты | CardManager.applyCardEffects:1283 → CardInstance.updateEffectsApplied:1337; CardEffectManager хранит active effects по lists |
| Завершение | FlowController.OnEndGameResult:1005 → closeMenuFunctor(bool) → GameMenu.onGameFlowDone:409 → OnMatchResult(bool) → closeMenu |

shouldDisallowStateChangeFunc ожидает messages/FX/choice/tweens. Beta logical resolution следует отделить от UI timing.

**Vanilla draw раскрыт:** EndGameDialog.closeButtonPressedOrTapped:275 отправляет EndDefeat для PLAYER_INVALID. FlowController преобразует его в false; .ws при закрытии устанавливает EMS_End_PlayerLost. Replay делает Reset внутри меню и ещё не сообщает quest результат. Beta core должен хранить Draw отдельно; RPG policy выбирать явно.

## Quest/deck/reward references

56 collections включают starting factions, tutorial, signature opponents и generic decks; они не равны 56 NPC. dynamicCards содержит item names, например gwint_card_scorch, и difficulty, тогда как fixed cards используют definition names. Native алгоритм добавления ещё не раскрыт. Полные записи и compact CSV сохранены.

69 бинарных ресурсов содержат CQuestGraphMinigameBlock; 39 также содержат CGwintMinigame. Это candidate index, не декодированный graph. Среди остальных есть fistfight/другие minigames.

Приоритетные пути относительно r4data:

- quests/sidequests/novigrad/sq306_maverick.w2phase: High Stakes candidates, Tournament decks, HasGwentTournamentDeck, victory/reward strings.
- quests/generic_quests/card_minigame_all_hubs/cg_card_minigame_meta.w2phase: GwintWon/GwintLost, Zoltan/Roche/Lambert/Thaler и rewards.
- quests/generic_quests/{no_mans_land,novigrad,skellige}/cg*.w2phase: regional chains.
- dlc/bob/data/quests/minor_quests/quest_files/cg700_card_game/*.w2quest: CGwintMinigame, UnlockSkelligeGwentDeck.
- dlc/ep1/data/quests/q602_wedding.w2phase: CGwintMinigame; конкретное соответствие ещё читать в graph.

В base gameplay/rewards/rewards.xml:300–303 sq306_01..04_defeated_* дают Foltest/Emhyr/Francesca/Eredin gold items, XP 25/50/50/80; у Tybalt achievement=30. BoW отдельно определяет tournament_win, alternate, wager_sword, tournament_card. cg_zoltan содержит XP, но не card item: reward XML не единственный путь получения карты.

Для NPC → deck → reward нужны свойства/связи конкретных nodes; строки в одном файле их не доказывают.

## Следующий проверяемый шаг

Проект создан самим REDkit; metadata MyProject1/idSpace10000000/useLooseScripts=false сохранена. Installed r4data содержит scripts/SWF/quest samples, которых физически нет в user depot; это отдельные слои virtual filesystem, а не признак незавершённого uncook. См. resourceLookup в redkit-project.json и [официальное описание слоёв](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6328326/Collaborating+on+mods).

**Script compile подтверждён:** capability-06, exitCode0, compilerErrors0, blob.rsblob1774 bytes, SHA256 `CD2D8024E494B5AA176C969166248CB33F72D8C22FE3D5E76F4953D455817ED4`. В логе есть Success! Patch scripts blob saved. Собрались addField(saved int/array), addMethod и wrapMethod Gwent request/end/SetPlayerStarts. @wrapMethod требует function без public; addMethod public принят. [Официальные аннотации](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/36241598/WS+Script+Compilation+Errors+overrides).

Wcc сначала ожидал EULA без вывода; пользователь лично принял условия. После этого -agreetoterms отражает уже сделанный выбор, не заменяет его. Второй препятствующий фактор: запуск из build-каталога ищет ../gameconf.cfg там же; исправлено cwd=bin/x64_RedKit и -wcclog с абсолютным workspace path. Runner ограничивает время, останавливает только свой PID и сохраняет result/stdout/stderr/log. Failed runs сохранены; capability-02 остановлен нами вручную. Лог также содержит startup CRC warnings и аудио errors при shutdown; Wcc compiler success установлен независимо от них, runtime compatibility не утверждается.

Runtime probe выполнен пользователем. Editor.log подтверждает seed17→increment18→seed skipped, ручной save completed, load и последующий read counter18/ids2/valid=true без reseed. Два request/end для NilfPrologue; один outcome явно EMS_End_PlayerWon, другой state пустой. Screenshot показывает breakpoint hit OnGwintGameEnded. Другие исходы подтверждены пользователем, отдельные значения в логе не видны. SetPlayerStarts log отсутствует, новую SWF authoring не проверяли. Basic flat saved fields gate пройден; это не проверка полного BetaProfile/NG+/migration/large collection.

Runtime editor.log/scriptstudio.log сначала имели нулевую длину, затем стали доступны без закрытия приложений. Не делать вывод об отсутствии trace по первоначальному размеру. Сохранены hash/selected trace и error families; editor.log содержит ошибки vanilla/resource/engine paths (missing files, streaming asserts, XML redefinitions, tutorials). На snapshot нет Error lines со ссылкой на capabilityProbe/BetaGwent; это не доказательство чистоты всей среды. Evidence — capability-runtime-result.json и capability-runtime-trace.txt.

Аудит: tools/recon/inspect_redkit.py и inspect_redkit_project.py; evidence redkit-*. Исходные TW3/scripts/depot не патчились, metadata проекта не изменялась; добавлен один .ws в project workspace и compiler outputs. Установленная TW3 не получает мод автоматически.

## Новый UI pipeline: build gate пройден, resource/runtime открыт

У пользователя нет Animate/Flex. Apache tools размещены в tools/vendor, системная установка/PATH не менялись. Java18 уже доступен. Рабочая связка: Apache Royale0.9.12 + открытые compile-time player API typedefs0.9.12 → SWF14 FWS → bundled GFxExport4.01/SDK4.3.27. Проверены lengths, AS3 flag, DoABC/root SymbolClass. Latest probe SWF2157/GFx2183 bytes. Counter меняет WitcherScript, frontend отправляет intent и отображает ответ; Esc close предусмотрен, но в игре ещё не исполнен.

Отдельный uiProbeMenu.ws собран Wcc: bridge-compile02 exit0/Success/blob1644, SHA2561C3CD59E5824A36F9FE417110D765AEB478D582D879A8596E5E6DCD368FD8A78. Source/blob вне active project. CMenuResource/CGuiConfigResource найдены в gameplay/gui_new/guirsrc; binary config не менялся.

CLI swfimport требует raw SWF и сам вызывает GFxExport. В temp появляется CFX, затем assert diskFile.cpp2633 corrupted loaded flag; .redswf не сохраняется при exit0. Общий import тоже не дал resource (exit1). Нужны editor import и native menu registration. [Эксперимент](D:/w3mod/tools/ui/README.md), evidence ui-probe-build.json/ui-probe-import-attempt01..03.json и bridge-compile02/result.json.

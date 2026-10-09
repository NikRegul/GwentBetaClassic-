> **Текущий этап93: HD-оформление боя и редактора колоды.**
> Доски2048×708, крупные карты256×360, оригинальные фон/полки/рамки/кнопки.
> Общий стиль выбора колод, каталога, замены карт, бочек и сбросов.
> Локальные RU/EN preview.3; публикация отложена до игровой приёмки.
> [Изменения](../docs/PRESENTATION93_RU.md) · [Сборка](../docs/HD_PRESENTATION_PIPELINE93.md) · [План](../docs/plan.md).
> Native/архивные проверки прошли; внешний вид и управление в игре ещё
> не подтверждены. Релиз0.2.0 и предыдущие preview сохранены.

> **Предыдущий этап88: первый проход ИИ по deck_rules.**
>40 адаптированных профилей,70 связок,93 состава; исходные53 сохранены.
> Муллиган, порядок движков, резерв, сброс/воскрешение, позиции и общий пас.
> Импера с пятью шпионами оценивается в16: планировщик выбирает одну карту.
> Wcc88e:60 источников. Проверки правил прошли; игровая приёмка ожидается.
> [Полный тестовый ZIP0.1.1](D:/w3mod/BetaGwent/release/BetaGwent0924-0.1.1-alpha-RU.zip),117.1MiB; CRC/SHA-256 проверены.
> [Изменения и проверка](D:/w3mod/docs/ai_rules88.md) · [Замены](D:/w3mod/docs/ai_rules88_adaptation.md) · [План](D:/w3mod/docs/plan.md).

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

> **Предыдущий этап83e: новые стартеры, редактор и бочки из инвентаря.**
> Пять согласованных колод по25+лидер, включая Брана и Ютту; недостающие
> копии добавляются в старые сейвы. Исправлен отказ лидера, блокировавший ввод.
> Бочки покупаются пачкой за150 крон каждая и открываются по одной из инвентаря.
> Wcc83h успешен; три UI/41 binding установлены. Новая игровая приёмка впереди.
> Далее: контроллер → тестовый релиз → полный Wwise и ИИ остальных колод.
> [План](D:/w3mod/docs/plan.md) · [Изменения83e](D:/w3mod/docs/starters_and_kegs83e.md).

> **Предыдущий этап83: коллекция Beta, книга учёта, квесты и турниры.**
> Одна копия каждой из479 карт/лидеров для «Собрать их все»;33 разных
> фиксированных NPC-состава и награды, включая четыре запроса Туссента.
> Всего53 пресета; допуск к турнирам по колодам Beta, старое обучение пропущено.
> Бочка150 работает и после заполнения бронзы: остаётся редкий выбор.
> Wcc83d успешен;57+probe=58 WS, три UI/41 функция. Новая игровая приёмка
> ожидается. Следующий шаг84: анимации/полный звук; требуется применить
> лицензию к нашему Wwise-проекту. Cook и проверка обычной TW3 впереди.
> [План](D:/w3mod/docs/plan.md) · [Этап83](D:/w3mod/docs/integration83.md).

> Ниже сохранены исторические статусы.

> **Текущий этап82: коллекция, награды, торговцы, бочки и авто-раунды.**
> Пять стартовых колод; сохранённое владение3/1/1;29 назначенных золотых
> наград и первая победа обычного NPC.197 замен старых товаров, бочка150
> у квартирмейстера Барона с сохраняемым выбором50/50серебро/золото+лидер.
> Три UI/41 функция установлены, Wcc82e успешен; игровая приёмка ожидается.
> Полный звук1332медиа подготовлен, но лицензия ещё не применена к проекту
> Wwise; рабочий банк200 сохранён. Опись выпуска готова, cook ещё предстоит.
> [План](D:/w3mod/docs/plan.md) · [Изменения82](D:/w3mod/docs/progression82.md).
> Ниже исторические статусы.

> **Этап80: Мороз Эредина и первый ИИ по архетипу.**
> Добавлен согласованный состав25+Эредин, preset15, профиль замен/подготовки/
> контроля/Ирис/перемещений/выборов и паса. Новые UX, погода из TW3,
> просмотр карты и полёт подготовлены;35 функций UI согласованы.
> Новые DeckBuilder/GwintGame подключены в workspace проекта; обычный
> NPC-квестовый возврат ещё требует игровой приёмки. Установленная TW3
> не патчилась. Звук79d подтверждён пользователем отдельно.
> [План](D:/w3mod/docs/plan.md) · [Стратегия](D:/w3mod/docs/ai_weather80.md)
> · [Управление](D:/w3mod/docs/interaction79e.md) · [Входы](D:/w3mod/docs/native_gwent79f.md).
> Ниже сохранены исторические статусы, включая уже исправленные проблемы.

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

> **Этап78: просмотр сбросов и своей колоды установлен.**
> D — своя колода; G/H — свой/вражеский сброс; Esc — закрыть просмотр.
> Три группы по цвету, рисунки/теги/описания; случайный порядок показа
> не меняет добор. Колода врага закрыта в UI и WitcherScript.
> Wcc78b и32 функции моста собраны; runtime78 ожидает одного прохода.
> Следом звуки из беты, архетипы/ИИ, коллекция/бочки150крон с лимитами3/1/1,
> NPC и анимации/погода. Подробный текущий план: docs/plan.md.

> **Этап 77: управление, производительность и теги.**
> Обязательные розыгрыши, кэш редактора/составов/боевых описаний,
> яркие цели и инструкции, исходные категории карт, запоминание колоды.
> Новая и повторная Beta-партия проходят через экран колод; 8 слотов
> сохраняются вместе с обычным игровым сохранением.
> Сборка проверена; фактический FPS и загрузка сохранений ещё не приняты.
> [Общий проход](D:/w3mod/docs/interaction77.md) · [План](D:/w3mod/docs/plan.md).
>
> Далее сохранена история предыдущих этапов.

> **Текущий этап 76: весь набор карт установлен.**
> Добавлены 111 обычных: 60 Скеллиге+51 нейтральная. Теперь 458/458 обычных,
>21/21 лидеров,85/85 особых; остаток 0. Редактор Скеллиге и три новые
> сборки, всего 14. Галерея 479/479 рисунков,562 арт-привязки.
> Wcc 76f/AS3/GFx/native/bridge прошли,45 исходников (44 обновляемых и неизменённый capabilityProbe) совпадают.
> Проверка новых способностей в игре ещё впереди; ИИ/награды/полная
> точность общего scheduler остаются в плане.
> [Изменения и общий проход](D:/w3mod/docs/cards76.md) · [План](D:/w3mod/docs/plan.md).
>
> Далее сохранена история предыдущих этапов; прежние статусы не текущие.

> **Текущий этап74: исправлен пропуск карт с «Обречённостью».**
> Добавлены Кагыр, Шани, Ключник и Кухарка: ритуал. В редактор возвращены
> Медик из Виковаро, Хаттори, Паулье и Призрак Сабрины. Каталог479;
> Нильфгаард71+4, Север67+4, Чудовища74+5, Скоя’таэли66+4.
> Всего347/458 обычных карт,21 лидер; осталось111. Компиляция74a и UI/native
> прошли; runtime74 впереди. [Исправление74](D:/w3mod/docs/cards74.md) · [План](D:/w3mod/docs/plan.md).
> Ниже история; прежние числа исключали14 коллекционных карт с Doomed.

> **Текущий статус70 — все карты Чудовищ и все пять лидеров; версия установлена.**
> Чудовища72/72 +5/5 лидеров. Добавлены47 обычных,3 лидера и4 служебных
> отряда; Эредин, Шепчущий холм и Королева главоглазов доступны в выборе.
> Редактор127 карт,162 definitions,144/444 обычных и5/21 лидеров всех фракций.
> Особые67/85; оставшиеся18 входят в300 недобавленных обычных карт.
> Wcc70c/AS3/GFx/native/bridge и39-source equality проверены; runtime70 впереди.
> Атлас491 bindings; DIY-доски сохранены. Получение пока не назначено.
> Следующий шаг — полноценные колоды Чудовищ по архетипам, затем другие фракции.
> [Изменения и пакет проверки](D:/w3mod/docs/monsters70.md) · [План](D:/w3mod/docs/plan.md).
> Ниже история; её прежние статусы не являются текущими.

> **Текущий статус69 — Луны и контактные бедствия; версия установлена.**
> Лунный свет/Волчья яма/Мечта дракона, события рядов и их подписи/эффекты.
> 97/444 обычных (остаток347),2/21 лидеров (остаток19), особые65/85
> (остаток20 входит в347).108definitions,13display-only views,80Monsters-compatible.
> Wcc69b/AS3/GFx/native/bridge и37-source equality проверены, runtime69 впереди.
> Волчья яма — Скоя’таэли; их редактор колод ещё не включён. AI после всех карт.
> [Изменения/один просмотр позже](D:/w3mod/docs/rows69.md) · [План](D:/w3mod/docs/plan.md).
> Ниже история; прежние статусы не являются текущими.

> **Текущий статус68 — пять особых с выбором режима; версия установлена.**
> Мардрём/Мандрагора/Костяной талисман/Сигилль/Меч Вандергрифта.
> 94/444 коллекционных (остаток350),2/21 лидеров (остаток19); особые62/85
> (23 оставшихся входят в350).105 definitions, отдельно11 display-only вариантов.
> Monsters-редактор78; атлас483 bindings. Wcc68b/AS3/GFx/native/bridge и
> equality37 sources проверены; runtime68 впереди. Большой AI после всех карт.
> [Изменения/один просмотр позже](D:/w3mod/docs/modes68.md) · [План](D:/w3mod/docs/plan.md).
> Ниже история; её прежние статусы не являются текущими.

> **Текущий статус67 — особые и связанные отряды; версия установлена.**
> Добавлено8 особых+6 коллекционных отрядов+3 служебных.100 definitions,
> 89/444 коллекционных (остаток355),2/21 лидеров (остаток19); особые57/85
> (остаток28, входит в355).75 карт текущего Monsters-редактора; атлас472 bindings.
> Wcc67b/AS3/GFx/native/bridge и equality37 sources проверены; runtime67 впереди.
> [Изменения и один просмотр позже](D:/w3mod/docs/cards67.md), [план](D:/w3mod/docs/plan.md).
> Ниже история; её прежние статусы не являются текущими.

> **Текущий статус66 — полный каталог и девять новых особых.**
> Меню «Все карты»:465 кандидатов,463 иллюстрации, поиск/фильтры/описания,
> «Способ получения: не назначен».75 обычных и2 лидера реализованы;369+19
> осталось. Особые49/85, остаток36.83 definitions,37 .ws,68 карт Monsters-редактора.
> Wcc66c/AS3/GFx/native/bridge успешны,66 установлена; игровой просмотр66 впереди.
> Пользователь принял редактор/создал колоду/поиграл; save/reload отдельно не подтверждён.
> Большой AI поиск отложен до всех карт и колод, анимаций пока достаточно.
> [Изменения и один просмотр66](D:/w3mod/docs/catalog_specials66.md).
> Ниже история предыдущих этапов; прежние статусы не являются текущими.

# BetaGwent — исходники core

> **Текущий статус65: особые карты — 40/85.** Добавлено29 новых конкретных
> эффектов (4gold/11silver/14bronze), арт и управление; прежний редактор64
> сохранён. Оставшиеся45 требуют колоды/сброса, созданий и дополнительных
> механик. [Подробности65](D:/w3mod/docs/specials65.md). Runtime65 ещё впереди;
> принятая63 сохранена коммитом4362dc5.

> **Текущий статус 2026-10-03: версия64 — редактор колод.**
> Принятая63 сохранена коммитом4362dc5. Создание/копирование/редактирование,
> имя/лидер, поиск/фильтры, арт, копии и строгие лимиты Beta25–40/4gold/6silver.
> Восемь saved слотов; свои составы можно назначить любой стороне партии.
> 37 карт коллекции,2 лидера Чудовищ,45 definitions/art,36 .ws. Другие фракции впереди.
> Wcc64c/AS3/GFx/native/bridge успешны;64 установлена, editor/save-reload ещё не проверены в игре.
> [План](D:/w3mod/docs/plan.md), [Редактор64](D:/w3mod/docs/deck_builder64.md).
> Ниже история; прежние статусы не являются текущим статусом.

Цель: строгая **Beta 0.9.24.3.432**. Поле и его116 core/104 development-session checks подтверждены editor.log и пользователем. Typed requests/continuation и123 checks исполнены в версии15. В20 ACTION39 и116/104/123/43 прошли; живые DEV choices/targets/abort подтверждены логом. Direct Apply20 приняты в21. Manager26 suite39/20/86 принят. Numeric28/POWER55 скомпилирован и установлен; native прогон предстоит. Новое поле использует две оригинальные доски DIY; правила остаются strict Beta.

Исходники: `D:\w3mod\BetaGwent\scripts\game\betagwent`. Development session/menu/checks находятся в `development/scripts`. Последняя board-compile28: exit0, blob142099bytes, compiler errors0;24 active sources совпадают с patch и authoritative sources. Новые файлы уже перенесены в проект. Прежний capability probe не менялся. Native Flash/меню и обе DIY-доски приняты; новый ручной шаг — [BOARD_CHECK.md](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md). NPC интеграция ожидает resolution и canonical slice.

## Что написано

Пользователь вернулся; проверки возобновлены. Numeric40 exact original прошёл;55 native checks ждут `bgpower_check()`. ID allocator original16 тоже прошёл, WS [registry draft](D:/w3mod/BetaGwent/drafts/README.md) пока не установлен. [План](D:/w3mod/docs/first_playable_plan.md).

| Файл | Назначение |
|---|---|
| [types.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/types.ws) | Оригинальные phase/player/location значения; минимальный template header, runtime card/power, player, round и match snapshots |
| [roundRules.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/roundRules.ws) | Чистые расчёты корон, маски победителя и следующего стартующего игрока |
| [cardRules.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/cardRules.ws) | Location predicates, стабильная фильтрация одного location, predicate play-request и расчёт power reset |
| [turnRules.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/turnRules.ws) | Решение о начальных play requests или automatic pass с учётом руки, лидера и authority |
| [triggerOrder.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/triggerOrder.ws) | Pure location priorities и insertion index локального trigger batch; не scheduler |
| [requestState.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/requestState.ws) | Typed choices/targets, PlayerId/TargetPlayer, hidden views, mapping, min/max, ordered shape и lifecycle |
| [requestContinuation.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/requestContinuation.ws) | Per-instance pause/resume и local request store; first-ID shadowing, одна обработка за Update |
| [actionManager.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionManager.ws) | ApplyAction policy, services,64-bit delay, fault latch и bounded queue driver; actual handlers pending |
| [actionApply.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionApply.ws) | Direct Apply/After, mutable context; bool failures, местный Prepare; без production sink |
| [actionQueue.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionQueue.ws) | Global/local one-step queues, Before guard, front authority policy; dispatch sink без эффекта |
| [powerNumbers.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/powerNumbers.ws) | Numeric setters/restore/armor/multiply; final raw setter fail closed, events/death pending |
| [matchState.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/matchState.ws) | Закрытое состояние двух игроков, snapshots/history, изменения на границах turn/pass/round |

## Контракт coordinator

`CBetaGwentMatchState` создаётся будущим владельцем через `new CBetaGwentMatchState in this`, затем вызывается `Initialize`. Отдельный объект на каждый матч; повторный Initialize отклоняется. Runtime profile/save ещё не реализован.

1. После ChoosePlayer/AdvanceRound coordinator вызывает `ApplyRoundStarted(starterId)`. Первый starter поступает из settings или оригинального RNG; после последующих раундов проверяется рассчитанный starter.
2. На OnTurnStarted вызывается `ApplyTurnStarted`. Passed игрок также получает эту границу; state не перескакивает через его ход.
3. `ClaimInitialMove` — внутренняя операция после проверки запроса. Это **не** полный ValidateAction. Manual AskPass и automatic PassPlayer имеют разные пути и не должны объединяться в один вызов.
4. После BeforePassed и отметки play-request вызывается `ApplyPlayerPassed` на границе OnPlayerPassed. Затем coordinator разрешает AfterPassed.
5. На OnTurnEnded вызывается `ApplyTurnEnded`; initial-move flag текущего игрока сбрасывается.
6. После завершения ходов обоих passed игроков передаются уже рассчитанные board scores в `RecordRoundResult`. Результат и короны записываются один раз. Затем отдельно идут AfterRoundTrigger → OnRoundEnded → EndGame либо ClearBoard.

Эти API-guards — ограничения текущего черновика, а не копия полного original action validity. Номер раунда и turnSequence здесь локальные, one-based; они не заявлены как точный перенос оригинальных counters. Объект пока не содержит phase machine, scheduler или флага завершения игры: наличие winner mask не заменяет EndGameAction.

## Карты и источники

Template header — небольшой набор полей, не импорт всех карт. `originTemplateId` и `runtimeTemplate.templateId` разделены для будущих превращений; owner/controller/position side также раздельны. Registry, movement, damage, transform, эффекты и общая legality ещё не написаны.

`BetaGwentFilterLocationCards` сохраняет порядок входного массива **одного** Location. Board traversal обязан сохранить порядок BoardSides/Locations оригинала; нельзя передать произвольный registry scan. `withTokens` означает наличие любого пересекающегося бита. Play-request predicate сам по себе не подтверждает законность действия. Power reset вычисляет только числа: event delivery/SetPowerAndArmor и другие Reset flags нужны в resolution.

`BetaGwentDecideTurnEntry` проверяет только наличие подходящей карты на стороне игрока в Hand|Leader. Порядок кандидатов для этого bool-решения несущественен; функция не выдаёт упорядоченный список legal actions. При passed/без authority запрос не создаётся; автоматический пас также пока только возвращаемое решение, без выполнения trigger chain.

Основание: [round/pass IL](D:/w3mod/docs/evidence/beta-flow-il.txt), [starter IL](D:/w3mod/docs/evidence/beta-legality-rounds-il.txt), [card/filter/reset IL](D:/w3mod/docs/evidence/beta-card-rules-il.txt). Прежние20 pure IL checks относятся к исходным методам, **не** к новым `.ws`.

## Requests и проверка следующей версии

Локальный request отделяет владельца PlayerId от получателя TargetPlayer. Views не содержат original instance IDs; synthetic choice IDs1000+i сохраняют mapping при стабильной группировке сторон. Store воспроизводит first-ID shadowing и player0 wildcard. Дубликат ключа отклоняется дополнительным локальным guard; это не буквальный AddRequest оригинала.

Continuation принадлежит отдельной ability instance: PauseOn отключает AutoDestroy, ResumeFor принимает только её fulfilled request, CompleteRequestNode копирует результат до Destroy и не повторяет Setup. Эти классы моделируют границы узла; полного graph interpreter, eventbus, authority/mirror доставки, timeout и canonical cancel/rollback ещё нет.

[developmentRequestChecks.ws](D:/w3mod/BetaGwent/development/scripts/game/betagwent/developmentRequestChecks.ws) содержит123 подготовленных checks, из них18 ожиданий получены исполнением original IL methods. Кнопка «Проверить ядро» запускает116/104/123/43 на отдельных объектах.123 прошли в15, но обнаружена отдельная switch128 diagnostic; explicit default добавлен в18. В20 FLOW43 и live choices/targets/abort прошли; очередь39/39 принята. Native Apply20 приняты21; manager86/queue regression ещё не исполнялись. [Результат подготовки](D:/w3mod/docs/evidence/request-flow-development-result.json).

## Следующий шаг

Native suite39/20/86 → numeric power fixtures/registry/service adapters (original manager56/56 готов) → production AbilityInstance/ExecutionStack → небольшой canonical slice и effect primitives. RNG original23 methods/37 fixtures проверены отдельно; WitcherScript RNG и полное consumption parity ещё предстоят. Подробности: [requests](D:/w3mod/docs/beta_requests.md), [RNG](D:/w3mod/docs/beta_rng.md), [план](D:/w3mod/docs/plan.md).

Интерактивный слой: developmentRequestFlow.ws + developmentRequestFlowChecks.ws + menu/AS3. Он выбирает synthetic fixture cards и не исполняет canonical effects. Контракт/ограничения: [request_ui.md](D:/w3mod/docs/request_ui.md).

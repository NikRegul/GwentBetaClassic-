# Карта Beta и DIY

## Оригинальный клиент

Корень: `D:\w3mod\Gwent 0.9.24.3.432`.

`Gwent_Data/Managed/Assembly-CSharp.dll` содержит полноценный GwentGameplay: GameController, FiniteStateMachine, ActionManager, AbilityManager, RequestManager, ExecutionStack, PlayStack, RoundManager, CardManager, PlayerManager. Это подтверждено metadata и IL, а не только строками имён.

Фактический путь данных: ZIP data_definitions → Templates/Abilities/Personalities/Summations → runtime templates/abilities → GameController. Полная цепочка загрузчика ещё не прослежена; прямую загрузку каждого файла из названия не предполагать.

Разделение модели в metadata: CardTemplate, RuntimeCardTemplate, CardDefinition, Card. Способности в XML — графы Nodes/Connections с временными и постоянными переменными. `CardAbility.Template` связывает граф с Template.Id. `LocationTokenAbility.LocationToken` задаёт эффекты рядов.

GameController предоставляет SetupHumanVsAI, SetupHumanVsHuman, SetupAIvsAI, Clone, Step. Это перспективно для oracle и симуляций; работоспособный headless запуск без Unity ещё не доказан.

RNG в контроллере: GwentCore.MersenneTwisterRandom. DIY System.Random не эквивалентен ему по seed/sequence.

Assets: StreamingAssets/AssetBundles/cardassets, gui/prefabs/deckbuilder_base, localization, Audio/GeneratedSoundBanks. Их существование подтверждено; формат конвертации в TW3 ещё не выбран.

## Неофициальный сервер

Корень: `D:\w3mod\Unofficial-Gwent-Beta-0.9.24.3.432-Private-Server-main`.

| Компонент | Реальная роль |
|---|---|
| deploy/server.py | HTTP services: аккаунты, данные коллекции/колод, экономика, matchmaking и др. |
| deploy/db.py | SQLite persistence; совместимость с JSON |
| deploy/broker.py | Notifications, protobuf/WebSocket messages и rewards |
| deploy/relay.py | Lobby handshake, player IDs/decks, ACK/ping/time, пересылка игровых команд |
| nginx + proxies | Подмена маршрута запросов клиента |
| GwentBetaRestorationMod/GwentBetaModMain.cs | Harmony patches исходного client flow, authority, connector, decks и progression |
| deploy/extract_data_definitions.py | Извлекает XML/CSV из собственного клиента; не содержит официальной game logic |

Подтверждённый путь multiplayer: mod patch BattleSetupFactory.CreateClientConnector → оригинальный GameInstance/GameController → модифицированный connector → relay. Relay.py описывает и реализует пересылку subsequent messages с переписыванием BundleID. Он не заменяет AbilityManager оригинала.

Мод вызывает SetupHumanVsHuman или SetupHumanVsAI и меняет GameInstance.get_HasAuthority / get_GameMode. Есть patch AGameState.HandleDirtyGameController, влияющий на завершение хода. Поэтому oracle должен записывать режим и активные patches; restored multiplayer нельзя автоматически считать нетронутым оригинальным поведением.

В установленном клиенте есть Mods/GwentBetaRestorationMod.dll. Исходники .cs из server repo не гарантированно совпадают с установленной DLL — отдельная проверка нужна.

Для TW3 полезны: понимание протокола, запуск reference client, capture decks/scenarios. Не переносить аккаунты, nginx, broker, kegs/crafting в RPG-мод.

## DIY: рабочее ядро — Cynthia.Card

Корень: `D:\w3mod\LegacyGwent-diy(1)\LegacyGwent-diy`.

Основная цепочка:

```text
Unity client → SignalR /hub/gwent → GwentHub → GwentServerService
→ GwentMatchs → new GwentServerGame(player1, player2, ...)
→ Play → PlayGame → PlayerBigRound → PlayerRound → RoundPlayCard
→ CardEffect.Play/CardUse → SendEvent/RaiseEvent → operations к players
```

Проверенные места: Startup.cs endpoint/DI, Hubs/GwentHub.cs, GwentServerModels/GwentMatchs.cs:36–48, GwentServerGame.cs:76,147,360,384,1832.

Common содержит GwentCard (definition), CardStatus (runtime fields с fallback в definition), GameCard, CardEffect, GameEvent, RowEffect, GwentMap. GwentMap использует DIY string IDs вроде `12004`; оригинал использует Template ID `112103` для Geralt. Эти ID нельзя склеивать напрямую.

`src/LegacyGwent/LegacyGwent.Core` — отдельная маленькая экспериментальная инфраструктура эффектов. Рабочий Common.csproj её не references; фактический сервер использует копию `Common/TempCore`. Не принять красивое имя LegacyGwent.Core за готовое основное ядро.

DIY правила связаны с transport/presentation: ClientDelay, выборы через операции, вызовы Show* из CardEffect. Effects распределены по классам, но definitions лежат в большой C# CardMap; это не готовый переносимый графовый interpreter Beta.

События: SendEvent перечисляет unlocked cards, затем row effects; при IsRunning исполняет вложенное событие непосредственно. RaiseEvent делает snapshot effects.ToList; EffectSet хранит HashSet. Это другой механизм ordering, чем у оригинального AbilityManager.

AI: AIPlayer обрабатывает server operations, RandomAutoAIPlayer выбирает из предложенных мест/целей случайно, не делает mulligan. Есть GeraltNova, ReaverHunter, SoldierTrain, Mill, AuberonKing, IronFalcon; часть pass logic — фиксированные пороги и sequencing. Это reference сценариев, не готовая архитектура стратегического AI для 60–70 NPC.

AITest/Tools.cs уже запускает один AI-vs-AI матч, но не собирает batch statistics; winner print сравнивает BlueWinCount с самим собой. Это ошибка отчёта, не доказательство неправильного результата матча.

## Что переиспользовать

Концептуально: definition/runtime split, именованные before/after events, механические primitives, row effects, пример headless AI-vs-AI transport. Для tooling возможны ID/name/assets candidates и parser DIY deck codes с pin версии CardMap.

Непосредственный runtime перенос C#/Unity/SignalR в WitcherScript не подтверждён. Предпочтение — самостоятельный Beta core под TW3, с oracle/testing tools вне игры. Если копировать DIY-код, учесть GPL, указанную README; условия для распространяемого мода ещё не исследованы.

## Найденные проблемы для будущей работы

1. `GwentHub.AddDeckCodeWithName` меняет локальный deck.Name, затем повторно декодирует исходный code при AddDeck — заданное имя теряется.
2. `TempCore/Pipeline.Execute` не сбрасывает IsRunning через finally при exception — очередь может остаться помеченной running.
3. `RoundPlayCard` индексирует hand по ответу; GetSelectRow/GetPlayCard возвращают ответ напрямую; GetSelectPlaceCards разрешает returned locations без локальной проверки membership/count в показанной цепочке. Нужен аудит всей валидации; для нового core централизовать её обязательно.
4. Matchmaking допускает IsSpecialDeck наряду с IsBasicDeck; это отдельный DIY режим с другими gold limits.
5. DIY карта Ciri: Dash имеет Strength=13, original Template 112110 Power=11; Geralt: Aard DIY=5, original 112111=6. Сверены initializer и оригинальные names/IDs. Автоматический audit нашёл 73 различия среди art-derived candidates, но это НЕ 73 доказанных ребаланса: часть art reused для другой карты.

В исходники этих компонентов изменения не внесены.

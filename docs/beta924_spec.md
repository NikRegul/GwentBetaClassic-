# Beta 0.9.24: спецификация, первый проход

Статус: **частичная спецификация**. Основание — original data ZIP и IL Assembly-CSharp.dll, SHA256 в evidence. DIY/PDF не задают canonical rules. 20 checks на извлечённых оригинальных pure IL methods пройдены; полный клиент/scheduler oracle ещё не запускался.

## Данные и идентичность

Template.Id — canonical ID definition; отдельный runtime instance ID должен жить в MatchState. Store/API CardDefinition ID, Template ID, ArtId, localization key, premium и instance ID не взаимозаменяемы.

Поля Templates: DebugName, Availability, Rarity, Kind, ArtDefinition, LinkedTemplateId/Order, FactionId, Tier, Type, Tokens, Power, Armor, InitialTimer, ResetInInactive, Placement.PlayerSide/OpponentSide, Categories и SemanticTags. BitArray хранит UInt64[]; e0/e1/e2 содержат64-битные words bitmask. У Template152214 также e3=0; все words должны сохраняться. См. [каталог](D:/w3mod/docs/beta_catalog.md). нельзя трактовать число вроде 2147483648 как category ID.

Enum values подтверждены DLL:

| Свойство | Значения |
|---|---|
| Faction | Neutral=1, Monsters=2, Nilfgaard=4, NorthernRealms=8, Scoiatael=16, Skellige=32 (точные enum names в evidence) |
| Tier | Leader=1, Bronze=2, Silver=4, Gold=8 |
| Rarity | Common=1, Rare=2, Epic=4, Legendary=8 |
| Type | Event=2, Unit=4, UnitEvent=8 |
| Kind | Normal=1, Weapon=2, Banner=4, Trinket=8 |
| Availability | NonOwnable=0, BaseSet=1, Tutorial=2, Campaign1=3 |
| Power target | CurrentPower=0, BasePower=1, PermanentPower=2, Armor=3 |
| Power operation | Add=0, Remove=1, Set=2, Multiply=3, Restore=4 |

Реальная модель power богаче «base + boost»: сохранить отдельные Base/Current/Permanent/Armor и проверить reset/inactive правила.

Zones ELocation: Melee=1, Ranged=2, Siege=4, Hand=8, Deck=16, Graveyard=32, Leader=64, SpawningPool=128, PlayStack=256, Void=512; Active=7, Inactive=248. SpawningPool и PlayStack — служебные зоны, не новые отображаемые ряды.

Tokens включают Resilience=1, Lock=4, Ambush=8, ImmuneToWeather=16, RevealedOnHand=64, Disloyal=128, NotTargetable=256, Doomed=512, Stubborn=1024, Mark=2048, Berserk=4096. Их точную семантику ещё нужно читать по action/node IL.

## State machine

Оригинальный EGameStateId:

```text
Init=1, Mulligan=2, ChoosePlayer=4, RoundStart=8,
TurnStart=16, Turn=32, TurnEnd=64, RoundEnd=128,
ClearBoard=256, Results=512, DrawCards=1024
```

GameController.Start вызывает TransitionTo(Init). GameController constructor регистрирует все эти state classes. DrawCards.OnFinished → Mulligan; RoundStart.OnFinished → TurnStart. RoundEnd.SetResult → AfterRoundTrigger → OnRoundEnded; OnFinished либо EndGameAction при HasWinner, либо ClearBoard. Полный граф с условиями turn/pass/draw пока не завершён.

В DrawCards.DrawCards подтверждено: во втором раунде DrawAction count=2, в третьем count=1, FireTriggers=true. InitialDrawSettings.DEFAULT_HAND_SIZE=10; default Mode=DrawUpToDefault, Count=10. DrawPlayerHandsAction при этом добирает до 10 с учётом уже заданной руки и mandatory draws; queued MoveAction initial draw имеет FireTriggers=false. Это не общий hard cap размера руки. Дополнительные settings modes позволяют draw заданного количества или до заданного размера.

MulliganSettings constructor задаёт Choices **3/1/1** для GameStart/First/Second. Default PlayerSettings включает leader и shuffle. В рекурсивном static scan DLL записи в Choices/InitialDraw.Mode/Count найдены только в этих constructors; это не исключает reflection/data/network initialization. Проверка полного standard setup/oracle ещё нужна. DIY 3/2/1 нельзя копировать как original default.

Источники: [defaults IL](D:/w3mod/docs/evidence/beta-defaults-il.txt), [settings writers](D:/w3mod/docs/evidence/beta-settings-writers-il.txt). RequestMulliganAction.Reset очищает blacklist для нового request. AskMulligan добавляет outgoing Template.Id в blacklist. GetNextValidCard проходит deck по порядку, исключая blacklisted templates и reserved instance IDs; если таких карт нет, делает второй проход с исключением только reserved IDs. Значит blacklist имеет fallback, а не безусловно запрещает получение этих templates.

Mulligan применяет MoveAction: incoming в прежнюю позицию outgoing в Hand, outgoing в Deck на индекс, полученный через RandomGenerator.Next(0, deck.NumCards). Сначала добавляется incoming move, затем outgoing; ActionManager.ApplyAction применяется непосредственно. Затем обновляются asked/valid lists и NumMulligans, вызываются OnCardMulligan и OnMulligan. При fulfilled request authority вызывает AfterMulliganTrigger, затем OnMulliganEnded. Утверждение о конечной permutation требует ещё проверки MoveAction semantics/RNG, а точное interleaving с другими triggers — scheduler trace.

## Подтверждённый порядок resolution

Источник: evidence/beta-core-il.txt, GameController.Step, AbilityManager.Trigger/AddAbilityInstance/Add, ActionManager.PushAction/PushActionImpl.

Один Step:

1. При authority и неприостановленном CurrentInstance обновляет AbilityManager; иначе ActionManager.
2. Затем RequestManager.Update.
3. При authority и отсутствии queued actions/ability instances обновляет ExecutionStack, затем PlayStack.
4. Обновляет local players. UI/таймеры управляются отдельно в GameController.Update.

`AbilityManager.Trigger` берёт matching active passive triggers, проверяет CanTrigger, создаёт AbilityInstances. Вставка в локальный список:

1. Больший ETriggerPriority раньше: Highest 15 → VeryHigh 10 → High 5 → Normal 0 → Low -5 → VeryLow -10 → Lowest -15.
2. При равном priority — больший LocationPriority раньше.
3. При одинаковых zone priority и player — меньший GetIndex раньше.
4. Для разных players — owner текущего игрока вставляется раньше.

LocationPriority из constructor: Melee 9, Ranged 8, Siege 7, Hand 6, Leader 5, Deck 4, Graveyard 3, PlayStack 2, Ignore 1, Void 0. Нет отдельной записи SpawningPool: проверять достижимость и ограничения перед обобщением.

Затем Trigger проходит отсортированные instances в обратном порядке и Add(instance,true) вставляет спереди; это сохраняет рассчитанный порядок на входе активного списка. Equal owner/index cases, reentrant triggers, abort/cancel, mutation между capture и execution требуют отдельного доказательства. Это comparator конкретного сбора triggers, не универсальная сортировка всех событий матча.

ActionManager.PushAction отправляет non-request actions внутрь текущего AbilityInstance при определённых состояниях instance; иначе PushActionImpl помещает action в конец либо в начало при pushFront, с проверкой authority. Поэтому замена всего исполнения одной FIFO-очередью недостаточна.

## Графы эффектов

Abilities содержит 183 node types. Частые: GetVarNode, SetVarNode, GetAbilityOwnerCardNode, GetCardsNode, FilterCardListNode, ChangePowerNode, RequestCardTargetsNode, RequestCardChoiceNode, RequestTemplateChoiceNode, SpawnCardNode, PlayCardsNode, MoveCardsNode, CardListShuffleNode, CardListGetRandomElementNode, PlayedTrigger, AfterMovedTrigger.

Граф сохраняет typed variables, persistent/temporary state, connectors, priority, ActionOnTrigger, owner location. Все должны иметь mapping/coverage до полного переноса. Tooltip не является исполняемым effect definition.

Create в original localization keyword_create: выбор из трёх случайных карт заданного faction/neutral, Agents исключаются, если card-specific rule не задаёт иное. Это текстовое свидетельство; algorithm/RNG/order ещё проверить в nodes. Определения consume/resurrect/discard/lock/reset/weather также нельзя фиксировать только по привычным названиям.

## Deck legality: original default rule set

Прочитан original `GwentCore.ADeckValidatorRuleSet`: TOTAL_CARDS_MIN=25, MAX=40, Gold total4, Silver6, Bronze=-1 (unlimited); copies Bronze3/Silver1/Gold1; leader total/copies1; non-neutral faction limit1. DefaultDeckValidatorRuleSet не переопределяет эти getters. Arena отдельно убирает Silver/Gold/faction caps через -1: не смешивать его с целевой обычной Beta.

DeckValidator.Validate считает копии по Template.Id, использует ValidateCard и DeckValidatorResult.IsDeckValid. Последний проверяет total/tier/copies/non-neutral faction, но не содержит отдельной проверки leader count. GwentVisuals.GwentDeckValidator.Validate(CollectionDeck) отдельно требует ненулевой LeaderCard и добавляет его template в список. Формат persisted deck, обязательная доступность лидера/карт и обработка неизвестных ID ещё нуждаются в дополнительной проверке; raw getter LEADER_MAX=1 сам по себе не доказывает rejection двух лидеров во всех входах. Эти ограничения теперь имеют original IL evidence, а не только DIY reference.

Источник: [beta-legality-rounds-il.txt](D:/w3mod/docs/evidence/beta-legality-rounds-il.txt), hash DLL совпадает с предыдущим аудитом.

## Winner и старт следующего раунда

RoundInfo.SetResult(PlayerManager) снимает TotalScore из BoardSides и передаёт массив в overload SetResult(PlayerManager,int[]). Overload копирует значения в PlayerScores, находит максимум и добавляет одну корону каждому игроку с таким счётом; WinnerId объединяет их IDs через OR. При ничьей, включая 0:0, оба получают корону. RoundManager.GetWinner формирует EPlayerId mask всех игроков с Crowns>=2; HasWinner проверяет mask!=0. IDs: Player1=1, Player2=2, AllPlayers=3.

Подтверждено исполнением извлечённого IL: 1:0 по коронам + ничья → 2:1 и победа Player1; 1:1 + ничья → 2:2 и match winner mask3; две последовательные ничьи также дают mask3. Для RPG adapter нужна отдельная политика draw: vanilla bool callback сам по себе этот исход не передаёт.

ChoosePlayerGameState.OnEnterState перед первым RoundInfo использует BattleSettings.StartingPlayer; random ветка вызывает RNG.Next(1,3), затем OnCoinToss и SetCurrentPlayerAction. При существующем CurrentRound: если WinnerId=3 (оба игрока), выбирается opponent предыдущего StartingPlayerId; иначе выбирается WinnerId. RoundStart затем AdvanceRound и записывает текущего игрока как StartingPlayer нового RoundInfo. Это static IL evidence; выбор стартующего не входит в pure-method harness.

## Pass и переходы ходов

AskPassPlayerAction.IsValid требует base validity и отсутствия HasMadeInitialMoveForCurrentTurn. ApplyImpl на authority отбрасывает запрос, если первый ход уже сделан или Status>=Finished; иначе отмечает initial move и ставит PassPlayerAction(player,true,false). PassPlayerAction automatic пропускает дополнительную проверку play-request; manual ветка требует незавершённый RequestPlayCardAction. Полный base legality contract ещё не восстановлен.

PassPlayerAction вызывает BeforePassedTrigger, затем помечает существующий play-request и посылает OnPlayerPassed; Player.OnPass устанавливает HasPassed, далее вызывается AfterPassedTrigger. Player.OnRoundStart сбрасывает HasPassed; OnTurnEnd сбрасывает HasMadeInitialMoveForCurrentTurn. AllPlayersPassed требует passed для всех элементов Players; это проверено для четырёх комбинаций двух игроков. Невалидные/missing player slots не являются нормальным standard match fixture.

Turn.OnEnter повышает TurnIndex и вызывает OnTurnStarted. Для authority и ещё не passed игрока ищет карты Hand|Leader (mask72), all types14/tiers15, с последним bool=true. При ненулевом списке создаёт пару связанных initial play requests для двух сторон, при пустом — automatic pass. Значит пустая рука сама по себе недостаточна для вывода об automatic pass: leader включён в запрос. Последний bool — includeOnlyCardsThatCanBePlayed, проверяет Data.CanBePlayed; см. уточнение фильтров ниже. Точный путь изменения доступности использованного лидера ещё восстановить.

Turn.OnUpdate после IsFinished(false) вызывает BeforeTurnEndTrigger, если не все passed. TurnEnd.OnFinished: все passed → RoundEnd; иначе переключает current player на opponent и переходит в TurnStart. Здесь нет прямого пропуска passed игрока: его следующий Turn не создаёт play-request; порядок before-turn/turn-start effects нужно сохранить и проверить scheduler trace.

RoundEnd: SetResult → AfterRoundTrigger → OnRoundEnded; OnFinished при HasWinner ставит EndGameAction(mask,Normal), иначе ClearBoard. ClearBoard вызывает BeforeClearedBoardTrigger, затем после resolution начинает cleanup: non-resilient cards ждут death; resilient survivors теряют Resilience, boosted power сбрасывается, armor обнуляется; очищаются row tokens и выполняется KillWaitingToDie. OnFinished → DrawCards. Reentrant death/reset effects и точная семантика power reset ещё не доказаны полной трассой.

Источники: [flow IL](D:/w3mod/docs/evidence/beta-flow-il.txt), [структурированные методы](D:/w3mod/docs/evidence/beta-flow-methods.json). [Извлечение](D:/w3mod/docs/evidence/beta-flow-extraction.json) проверяет одинаковые instruction texts 24 методов; [fixtures](D:/w3mod/docs/evidence/beta-flow-fixtures.json) содержит 20/20 passed. Harness исполняет overload с заданными scores и minimal data holders, без оригинального module initializer, Unity, board calculation, event bus, scheduler или сети. Это узкая проверка правил, не полная parity.

## Приоритет неизвестных

1. Standard battle setup подтвердить oracle; initial hand и mulligan defaults/blacklist IL уже извлечены. Полный illegal action rejection ещё проверить.
2. End-to-end winner/starter/pass trace: pure crown/tie/pass-reset cases уже проверены; board filter прочитан, остаются leader availability action и interleaving triggers.
3. Nested ordering: death/consume/resurrect/weather, simultaneous damage, lock/unlock, transform и cleanup.
4. Power reset численно прочитан; остаются death/event ordering, shield/armor взаимодействия и reset inactive.
5. RNG seed/state, shuffle и порядок потребления random numbers.
6. Categories/semantic masks и исключения Create, gold immunity/targeting, row capacity.
7. Classification полного card pool и coverage 183 nodes.

M1 не завершать, пока обязательные сценарии не имеют source-backed expected results и проверенных traces.


## Уточнение: фильтры карт, play request и reset

Источник: [card rules IL](D:/w3mod/docs/evidence/beta-card-rules-il.txt), [metadata](D:/w3mod/docs/evidence/beta-card-rules-methods.json).47 methods/1722 IL lines, только static read оригинальной DLL, без запуска её кода или тестов.

BoardManager.GetCardsInLocation обходит BoardSides и их Locations в порядке массивов, применяет player/location masks и вызывает Location.GetCards. Последняя перебирает Cards по индексу; всегда исключает IsInExecutionStack и IsWaitingToDie. Type применяется по Template.Type, tier — по Data.Tier; All14/15 обходят соответствующий фильтр. EnumExtensions.Contains(value,mask) означает `(value & mask) != 0`: достаточно любого общего бита. Поэтому withTokens требует хотя бы один запрошенный token, withoutTokens исключает при наличии любого запрещённого. Нулевой token mask отключает этот фильтр; нулевые type/tier не являются wildcard. Последний bool дополнительно требует Data.CanBePlayed. Результат сохраняет порядок обхода, а не произвольного registry/hash set.

CanBePlayed — отдельное mutable поле. Setter при изменении вызывает OnCanBePlayedChanged; ClearLeaderState устанавливает true. Найдены setter callers Register, Copy, SpawnCardsAction, SetCanBePlayedAction и network read. Сам фильтр не проверяет leaderUsed отдельным условием. Card.Play прослежен: при authority и Template.Tier=Leader ставит SpawnRequest в Leader64 с canBePlayed=false и новым instance ID. SpawnCardsAction передаёт это в Register. Полный replacement/cleanup trace ещё нужен; подробнее beta_resolution.md.

RequestPlayCardAction.CanPlayCard при CardIdToPlay=0 требует CanBePlayed, Hand|Leader и совпадение Position.PlayerId. При конкретном CardIdToPlay проверяет только этот instance ID и location Hand либо PlayStack. Нельзя добавить owner/CanBePlayed в эту ветку и назвать её точной копией; полный legal action contract содержит дополнительные проверки вне этого метода.

CardPower.Reset(false) передаёт BasePower+PermanentPower и текущую Armor в SetPowerAndArmor. При true предварительно восстанавливает BasePower из Template.Power, обнуляет PermanentPower и передаёт Template.Armor. SetPowerAndArmor ограничивает новые CurrentPower/Armor снизу нулём; Base/Permanent этим clamp не меняются. При изменении значений идут OnPowerChanged и проверки Kill/banish. Расчёт чисел без этих последствий — только pure helper, не завершённый reset action.

Card.Reset отдельно обрабатывает flags: Power1, Promotion2, LeaderUsed4, Tokens8, TemplatePower16 (модификатор Power), Timer32, Armor64, Categories128. Нельзя реализовать любой reset как восстановление всех полей карты.

KillWaitingToDie(false,false) при cleanup не выполняет простой bulk move: уже Graveyard/banished пропускает; non-Event с Base+Permanent<=0 добавляет в banish attack, остальных — в ExecutionStack entries с To=текущая сторона/Graveyard/index-3, TriggerAbilities=true, CanRollback=false, MoveReason4. PutCardInExecutionStack FireTriggers=false в ClearBoard, auto-pop отсутствует; waiting flags/list затем очищаются. Это не доказательство отключения всех ability triggers: entry TriggerAbilities остаётся true, позднейшее stack resolution ещё нужно разобрать.

## Черновик реализации M4

В [BetaGwent](D:/w3mod/BetaGwent/README.md) записаны pure расчёты и state storage. Новые .ws скомпилированы и перенесены в project workspace (board-compile09); runtime ожидает проверки нового поля пользователем. Существующие20 checks относятся к ранее извлечённому IL; full FSM/scheduler/card parity не заявляется.

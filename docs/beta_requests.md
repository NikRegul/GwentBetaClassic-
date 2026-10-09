# Requests и продолжение узла Beta 0.9.24

Обновлено:2026-10-02. Статическое чтение оригинального клиента через Cecil;
373 methods/6450 IL lines; дополнительно cancel/RNG77 methods/2379 lines и rollback13 methods/534 lines. Исполнены18 fixtures выделенных original limits/finish методов; полный карточный oracle trace не получен.
[Manifest](D:/w3mod/docs/evidence/beta-requests-summary.json),
[IL](D:/w3mod/docs/evidence/beta-requests-il.txt),
[structured methods](D:/w3mod/docs/evidence/beta-requests-methods.json).

## Пауза и владение request

EAbilityInstanceState: Started0, Running1, Finished2, Paused3, Aborted4.
IsPaused проверяет State==Paused3, не наличие любого request.
AbilityInstance.Tick сначала проверяет смерть card owner в активной позиции;
на Started повторно проверяет trigger abortion/CanTrigger, затем Init и Running.
При HasActions выполняет один ExecuteNextAction; иначе Running исполняет узел.

SetupImpl у ARequestChoiceNode и ARequestTargetsNode:

1. Выбирает current player и создаёт его request с requestId0 (allocate new).
2. Если CreateAction вернул null, возвращается без установки Paused.
3. У request выставляет AutoDestroy=false, сохраняет его ссылку в
   AbilityInstance.RequestAction, ставит action в очередь и Paused3.
4. Создаёт request для opponent с тем же request ID и ставит в очередь.
   Это часть двухсторонней original доставки, не два независимых выбора.

RequestManager.AddRequest вставляет в начало списка. Update обходит его по
индексам, но за вызов удаляет/fulfills не более одного request:
destroyed→Remove и true; fulfilled→HandleFulfilled→Remove и true. После этого
возвращается, не продолжая обход со старым count. Remove уничтожает объект
только при force или AutoDestroy. Request узла остаётся живым после снятия из
manager: результат ещё должен прочитать node.

CanProcess возвращает true при отсутствии authority либо TargetPlayer==PlayerId.
Authority ветка с разными сторонами не применяет request как целевой экземпляр.
Сеть не нужно буквально переносить в одиночную TW3: локальные роли ещё определить.

## Resume того же узла

HandleFulfilled у choices/targets возвращает связанную ability instance в
Running1. Card targets затем посылает OnTargetingEnded, choices — OnChoiceEnded.

AFlowNode.Setup ставит IsCurrentNodeSetup=true, обновляет inputs и выполняет
SetupImpl. Execute повторяет Setup только если флага ещё нет; при Paused не
вызывает ExecuteImpl, но сохраняет node state. После resume тот же request узел
исполняется без повторного Setup и второго request.

CardChoice.ExecuteImpl читает SelectedChoices и преобразует choice ID через
GetOriginalFromChoiceId в исходные карты. CardTargets.ExecuteImpl отдельно
записывает SelectedTargets и TargetsInShape. UI choice ID не равен исходному
instance ID без этого mapping. Затем базовый request node при true Execute
обнуляет Instance.RequestAction и вызывает DestroyAction. Результат читается
до уничтожения request.

AAbility.Tick временно устанавливает CurrentInstance/CurrentOwner и variable
buffers, восстанавливает FlowState при смене контекста, исполняет один узел.
Только при Execute=true меняет CurrentNode на Next; setter сбрасывает
IsCurrentNodeSetup. Перед возвратом восстанавливает предыдущий owner/instance и
buffers. Shared definitions не могут содержать единственный mutable request
state без привязки к конкретному instance/flow state.

## Истечение времени и RNG

IsFulfilled у choices/targets проверяет PlayerFinishedTargeting. Наличие
SelectedTargets само по себе не заменяет эту границу.

RequestManager.Update при !Expired, HasElapsed текущего game state и authority
вызывает HandleExpired, затем Expired=true. Не делает немедленный
HandleFulfilled/Remove: ForceResolve ставит select actions, которые ещё должны
примениться. Базовый HandleExpired вызывает ForceResolve.

CardTargets.ForceResolve копирует выбранные IDs в локальный список и, пока не
набран MinTargets и остаются valid candidates, берёт Random.Next(0,validCount).
Повторный ID пропускает и повторяет попытку; новый добавляет в локальный список
и ставит SelectTargetCardAction(...,true) в очередь. Это не shuffle+first-N:
duplicate attempt тоже расходует RNG. Порядок ValidTargets влияет на результат.

CardChoices.ForceResolve аналогично дополняет до MinChoices и ставит
SelectChoiceCardAction(...,true); при MinChoices!=MaxChoices добавляет
FinishChoiceAction. Здесь нет аналогичной targets проверки exhaustion;
допустимые min/max и построение choices ещё проверить по Init. Не придумывать
fallback-семантику. Original seeded RNG23 methods/37 fixtures проверен исполнением;
[семантика](D:/w3mod/docs/beta_rng.md). WitcherScript seed/state и точное
consumption в requests ещё не реализованы.

## Изменение и завершение выбора

AskSelect/AskFinish при authority создают соответствующий Select/Finish action
и передают его напрямую в ActionManager.ApplyAction. Select actions ищут request
через Get<T>(requestId,playerId); при отсутствии пишут error и возвращаются.
Этот lookup сначала выбирает **первый request по ID**, затем проверяет тип и
PlayerId. Если они не совпали, поздний подходящий request не ищется: действует
first-ID shadowing. PlayerId0 означает wildcard. PlayerId владельца отличается
от TargetPlayer получателя; по одному target side запрос не идентифицировать.
UI event нельзя направлять только по card ID или в «последний pending request».

AddTarget отказывает для null, повторного ID, ID вне ValidTargets и при заполнении
MaxTargets. AddChoice сначала проверяет MaxChoices, затем GetChoiceFromId и
дубликаты. Успешное добавление при count==max выставляет PlayerFinishedTargeting;
finish отдельно разрешён при min<=count<=max. FinishChoiceAction дополнительно
требует существующий ещё не finished choice request. Общая проверка APlayerAction
для IUserAction также учитывает ValidWhenBlocked и Player.Status<Blocked4.

Снятие выбора удаляет ID и посылает deselect event, но в прочитанных RemoveChoice/
RemoveTarget нет сброса PlayerFinishedTargeting. Не добавлять такой reset под
видом копии оригинала: manager обычно уже закрывает fulfilled request. Нужен
trace допустимого interleaving select/deselect/finish до следующего Step.

Target shape обрабатывается отдельно от SelectedTargets: AddTarget добавляет
карты области в TargetsInShape, RemoveTarget пересчитывает shape для текущей
позиции и удаляет его IDs по одному. Нельзя заменить TargetsInShape множеством
или предположить, что повторяющиеся области не влияют на порядок/кратность.

## Создание, скрытые сведения и финальный clamp

CardChoice.CreateAction возвращает null при пустом ValidChoices или max==0.
InitCommon ограничивает MaxChoices числом valid choices, а MinChoices — сначала
нулём снизу, затем их числом сверху. Это не clamp min к max. При MaxChoices<=0
сразу ставит PlayerFinishedTargeting=true.

Choice-копии получают отдельные ushort IDs1000+i. Из исходной карты клонируется
полная копия, если её сторона совпадает с TargetPlayer либо RevealChoices=true
и TargetPlayer==request.PlayerId; иначе создаётся скрытая faction placeholder-карта.
AddChoiceSorted ставит choices TargetPlayer перед другими сторонами, сохраняя
порядок внутри группы, и одновременно поддерживает OriginalChoices mapping.
Параметры original Init и Card.GetPlayerId отдельно сверены в
[roles IL](D:/w3mod/docs/evidence/beta-choice-roles-il.txt): reveal условие
использует владельца request, дополнительного viewer аргумента нет.
Поэтому сортировка карт для удобства UI или раскрытие чужой Definition меняет
семантику исходного request и может выдавать hidden information.

CardTargets.CreateAction возвращает null при пустом ValidTargets, ограничивает
min снизу нулём/сверху max и возвращает null при max<=0. Но окончательные числа
меняются позже: CardTargets.ApplyImpl удаляет уже умершие valid cards, затем
вызывает ARequestTargetsAction.ApplyImpl. Этот метод делает
`MaxTargets=min(MaxTargets,GetNumValidTargets())` и **MinTargets=MaxTargets**,
затем OnTargetAdded. Не сохранять первоначальный min после этой границы под
видом точной копии original targets. При max0 OnTargetAdded сразу завершает
выбор, хотя OnTargetingStarted отправляется после этого. Сценарий с умирающей
целью между Setup и Apply требует отдельной проверенной трассы.

CanCancel card targets: если нет RequestPlayCardAction для player — false;
при наличии true, если play request CanCancel либо attacker не Event(type2).
Одного этого bool недостаточно для полного cancel/rollback; прочитанные цепочки ниже.

## Отмена и rollback: прочитанные границы

[Cancel/RNG IL](D:/w3mod/docs/evidence/beta-cancel-rng-il.txt),
[rollback IL](D:/w3mod/docs/evidence/beta-rollback-il.txt),
[manifest](D:/w3mod/docs/evidence/beta-rollback-summary.json).
Это static source observations, без исполнения полного rollback trace.

- AskCancelRequestAction при authority ищет ARequestAction по ID/PlayerId,
  проверяет CanCancel и напрямую применяет CancelRequestAction.
- RequestManager.CancelRequest вызывает **HandleCancelled до Remove(force=true)**.
  Force уничтожает request даже при AutoDestroy=false. Missing request даёт
  error и return. Это отдельная граница от normal fulfillment.
- Targets HandleCancelled ставит AbilityInstance в Aborted4; card targets
  затем отправляет OnTargetingEnded со selected cards. Choices отправляет
  OnChoiceEnded с выбранными **choice copies**, не mapped original cards.
- CancelPlayCardAction отдельно вызывает ClearCardToPlay. Этот метод очищает
  CardIdToPlay, при CanCancel сбрасывает HasMadeInitialMoveForCurrentTurn и
  возвращает существующую карту через ReturnToHandOrLeader.
- ReturnToHandOrLeader разрешает только FromPosition.Location=Hand8 или
  Leader64; иначе error/return. Вызывает Move_Internal в сохранённую позицию
  и восстанавливает FromPosition после движения. Его ignored bool result
  нельзя трактовать как доказательство всегда успешного движения.
- RequestPlayCardAction.HandleCancelled при authority, CardIdToPlay0 и
  !Expired ставит новый primary play request и opponent mirror с тем же новым
  ID. В этом методе нет восстановления RNG; общий rollback RNG пока не доказан.

ExecutionStack.Rollback требует существующую entry и CanRollback. Если есть
play request: waiting-to-die карта приводит к AbortRequest; отменяемый play
request — к ClearCardToPlay; иначе AbortRequest и новая front PlayStackEntry.
Затем удаляется execution entry и вызывается HandleRollback. При отсутствии
play request entry всё равно удаляется. Missing/non-rollback entry даёт error.

HandleRollback очищает card execution flags, вызывает OnChanged текущей
location, если она существует, затем OnRollback(entry). Recursive scan всех
типов и nested types DLL нашёл прямые визуальные подписки:
LocalPlayerTurnHandlerComponent вызывает TryReturnCardBeingPlayed;
BattleMovementManager переносит view к текущей позиции, пропуская location256.
Reflection/external subscribers и downstream effects не закрыты этим scan.

## Что реализовано сейчас

[requestState.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/requestState.ws):
choices/targets, раздельные PlayerId/TargetPlayer, synthetic1000+i mapping,
stable target-side grouping, hidden template0/faction view, min/max/finish,
ordered shape с повторениями, remove по текущей shape, dead-before-Apply clamp,
result copy и lifecycle. Views не содержат original IDs и выдаются только
TargetPlayer. Это ограниченная view metadata, не clone полной original Card.

[requestContinuation.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/requestContinuation.ws):
отдельное mutable состояние ability instance, binding к точному request,
Paused→Running, результат до Destroy, Setup не повторяется; local store
front insertion/first-ID shadowing/player0/одна обработка за Update.
Local initialization/duplicate guards и Abort cleanup — собственные ограничения,
**не полная копия original cancellation**. Registry/events, authority/mirror,
owner-death, timeout scheduler и rollback пока отсутствуют.

[Original limits oracle](D:/w3mod/docs/evidence/beta-request-limit-fixtures.json):
18/18 passed,18 exact copied methods; два explicit provider shims возвращают
заданные valid/selected counts. Остальной клиент не запускается. Shapes,
lookup, hidden view и continuation ещё не исполнялись как original oracle.

[developmentRequestChecks.ws](D:/w3mod/BetaGwent/development/scripts/game/betagwent/developmentRequestChecks.ws):
123 подготовленных native checks, включая18 ожиданий этого oracle. Последняя
версия15 исполнила123 native checks failed0; зафиксирован отдельный switch128 diagnostic. В18 исправлен default, добавлен interactive requestFlow и43 checks. В20 RequestFlow43 и ACTION39 прошли, live DEV choices/targets/end/abort наблюдались. Direct Apply20 принят в21. Текущие22 sources/compile26 включают manager/driver; suite39/20/86 пока не исполнен, новые проверки отложены. Кнопка запускает116/104/123/43 на отдельных объектах. [UI protocol](D:/w3mod/docs/request_ui.md).

## Следующая работа

1. Перезапуск REDkit и ACTION39/interactive checks по
   [BOARD_CHECK.md](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md).
2. Подготовленный interactive presentation проверить; затем подключить
   continuation к production action scheduler. Snapshot/revision/key guards
   реализованы в development flow, полноценного graph execution пока нет.
3. Original fixtures для shapes, скрытых choices, lookup/interleaving,
   pause/resume, nested owner death и отмены до Destroy.
4. WitcherScript RNG по exact vectors; затем timeout с duplicate draws,
   cancel/play rollback, nested death/reset/consume и small canonical slice.

Этот слой не закрывает M1/M4 и не доказывает полную legality действий.

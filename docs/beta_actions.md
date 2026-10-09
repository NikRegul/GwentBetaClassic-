# Очередь действий: проверенный boundary port

Обновлено: 2026-10-02. Цель — строгая Beta0.9.24.3.432. Это первый участок
исполнения действий; полное применение эффектов и scheduler ещё отсутствуют.

## Оригинальный oracle

[Extractor](D:/w3mod/tools/oracle/extract_beta_actions.ps1) копирует21 метод
оригинальной DLL: глобальные Step/PushActionImpl, локальный ExecuteNextAction,
BeforeApplyTrigger и необходимые accessors. Тексты инструкций после записи
проверены на точное совпадение. Original DLL/Unity/module initializer не
загружаются в CLR. [Manifest](D:/w3mod/docs/evidence/beta-action-extraction.json)
содержит hashes, методы и пять явных shims:

- authority — поле harness вместо GameInstance/network policy;
- IsValid — delegate вместо реальной карточной валидности;
- BeforeApplyTriggerImpl — synthetic callback;
- ApplyAction — dispatch delegate, без оригинального применения эффекта;
- ExceptionHelper — объект Exception с тестовым сообщением.

[Harness](D:/w3mod/tools/oracle/beta-action-ref/Program.cs) исполнил36/36
проверок. [Результат](D:/w3mod/docs/evidence/beta-action-fixtures.json) сохраняет
expected/actual traces. Это executable oracle выбранных инструкций с
искусственными callbacks, не trace полного матча.

## Подтверждённый порядок

1. Global Step захватывает actions[0]. При authority, unfired Before и IsValid
   вызывает BeforeApplyTrigger, сохраняя action в очереди. В следующем шаге
   удаляет захваченный объект через Remove(action), затем dispatch.
2. Local ExecuteNextAction имеет такой же разрыв Before/dispatch, но удаляет
   индекс0. Его условие проверяет validity до authority; global — после.
3. BeforeApplyTrigger повторно проверяет validity и ставит fired flag **до**
   callback. Повторный/reentrant вызов не повторяет Before.
4. FireTriggers=false заставляет getter HasFiredBefore вернутьtrue, не меняя
   stored flag. Вновь включённые триггеры могут вернуть action в unfired state.
5. Nested front insertion во время Before выполняется раньше исходного action.
   Во время IsValid она раскрывает различие Remove(object)/RemoveAt(0):
   synthetic fixture оставляет вставленный элемент в global queue, но исходный
   элемент в local queue. Это observation IL, не требование мутировать очереди
   из production validation.
6. Global front без authority требует IPriorityAction. Append разрешён.
   BreakOnChange ставит controller debug flag после push и непустого шага.

Invalid action здесь **dispatch-ится** без Before. Это не доказательство
применения эффекта: оригинальный ApplyAction имеет отдельную политику validity,
authority/network, delivery, initialized actions и cache destruction.

## WitcherScript

[actionQueue.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionQueue.ws):
CBetaGwentQueuedAction хранит FireTriggers/Before flag и предоставляет IsValid/
BeforeApplyImpl callbacks. CBetaGwentActionQueue обслуживает global/local
варианты по одному шагу. Consumer CBetaGwentActionSink принимает dispatch;
он ещё не реализует production ApplyAction.

Guard differences явно отделены от parity: front rejection и пустой local
Step возвращаютfalse вместо CLR exceptions. Added initialization/null/index
guards локальны. PriorityAction bool представляет интерфейсный признак;
debug break не переносится. Local Push реализует вставку, но не CancelPlayedTrigger
side effect полной AbilityInstance.PushAction.

[Native checks](D:/w3mod/BetaGwent/development/scripts/game/betagwent/developmentActionQueueChecks.ws)
содержат39 assertions:31 с IDs original observations, два явных guard differences,
шесть дополнительных guards. Три debug observations не перенесены.
[Preparation manifest](D:/w3mod/docs/evidence/action-check-preparation.json)
связывает IDs и source hash; он не подтверждает native исполнение.

## Историческая сборка20 и приёмка

Board-compile20: exit0, blob80738bytes,18 active sources. До/после компиляции
записаны hashes всех18 patch inputs; они совпадают с установленными файлами.
Прежние16 файлов board18 и Flash не менялись. Board18 принят по четырём
batches116/104/123/43 без ошибок мода; в той сессии нет живых request intents.
[Текущая подготовка](D:/w3mod/docs/evidence/action-queue-development-result.json).

Перезапустить REDkit, загрузить тестовый сейв с Геральтом/HUD и выполнить:

```text
bgactions_check()
```

Ожидается уведомление «Очередь:39/39, ошибок:0» и
`ACTION_CHECK_DONE checks=39 passed=39 failed=0`. Тест создаёт отдельные
объекты, не меняет руку/поле/сейв. [Полная инструкция](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md).

```powershell
powershell -NoProfile -File D:\w3mod\tools\oracle\extract_beta_actions.ps1
dotnet run --project D:\w3mod\tools\oracle\beta-action-ref -- D:\w3mod
python D:\w3mod\tools\core-check\prepare_action_queue_checks.py
python D:\w3mod\tools\core-check\capture_action_runtime.py
```

Последний parser принимает только последний BEGIN→DONE batch, проверяет
все39 IDs в порядке источника, counters и отсутствие mod script errors.
Native ACTION39 прошли 2026-10-02 13:07:57, failed0. Два batches116/104/123/43
и live DEV requests также прошли. [Приёмка20](D:/w3mod/docs/evidence/native20-acceptance.json).
Action/Apply parser12 synthetic checks passed.

## Следующая очередь разработки

Отдельно уже исполнены14/14 original AAction.Apply fixtures: пять exact copied
methods, четыре field/delegate seams. [Manifest](D:/w3mod/docs/evidence/beta-apply-extraction.json),
[результат](D:/w3mod/docs/evidence/beta-apply-fixtures.json),
[harness](D:/w3mod/tools/oracle/beta-apply-ref/Program.cs).
Initialized field задаётся напрямую, Init не исполняется. Before/After callback
не является настоящим эффектом. Original runtime references отсутствуют.

Подтверждено: ApplyImpl выполняется первым; authority и FireTriggers читаются
**после** него. Изменение этих флагов внутри callback влияет на AfterApplyTriggers.
Исключение ApplyImpl пропускает After; исключение After не отменяет уже применённый
callback. Uninitialized action бросает исключение до effect. Null controller
вызывает ошибку после effect даже при FireTriggers=false: authority читается
раньше fire flag. WS direct Apply wrapper теперь установлен в21; snapshot authority до ApplyImpl
был бы неверным переносом этого control flow.

Политика ActionManager.ApplyAction теперь исполнена в отдельном oracle56/56.
WS manager policy и sink boundary теперь написаны в26. Далее добавить реальные services/handlers,
привязать registry/power actions и запросы к настоящей ability instance.
GameController.Step, AbilityManager interleaving, waiting-to-die drain,
ExecutionStack/PlayStack и bounded resolution budget остаются отдельными
частями scheduler. RNG и canonical cancel/rollback ещё не перенесены.

## Manager branches: original executable oracle

Полный ApplyAction сохранён в beta-resolution-il.txt; oracle56/56 подтверждает
нижеследующие branches. [Manifest](D:/w3mod/docs/evidence/beta-manager-apply-extraction.json),
[fixtures](D:/w3mod/docs/evidence/beta-manager-apply-fixtures.json).
Четыре метода скопированы точно:171 instruction ApplyAction, LastKnownNetworkID
get/set и base controller getter.24 внешних метода заменены callbacks, включая
Apply, IsValid, CanProcess, AddRequest, delivery, logger, send, pause, destroy.
Environments flattened; marker interfaces и Request→Action inheritance сохранены.
RedLogger.dll прочитан только для enum/type metadata, его код не запускается.
Actual effects/serialization/network/cache/pool и весь scheduler не проверены:

- unfired Before создаёт diagnostic exception через helper, затем pop, **без throw**;
- положительный NetworkId non-priority action обновляет LastKnownNetworkID до
  IsValid; меньший ID логируется, но не останавливает ветку;
- invalid action пропускает эффект и уничтожается;
- valid request с CanProcess сначала регистрируется, затем исполняется и
  уведомляет Player.OnRequestReceived; CanProcess вызывается повторно перед Apply;
- StateChanging flag ставит IsDirty до Apply, включая valid request без processing;
- valid request сохраняется, даже если CanProcess=false; valid non-request уничтожается;
- main-controller send/delay — отдельная ветка после request delivery.

Новый consumer CBetaGwentActionManager реализует эти branches через explicit services; реальные adapters ещё отсутствуют. Executable fixtures56/56 и их seams теперь сохранены отдельно; queue/request
checks сами по себе не подтверждают production manager policy.


Дополнительные наблюдения oracle: CanProcess true→false доставляет request без
Apply; false→true исполняет Apply без Add/Received. Валидность и delivery flag
снимком сохраняются до effect. Valid unprocessable request на main всё равно
отправляется/ставит pause и сохраняется. Out-of-order ID логируется и понижает
LastKnownNetworkID даже у invalid action. Delay читается дважды: условие и
аргумент PushPause; между чтениями значение может измениться. Main проверяется
после effect/Received. Исключения в Apply/Received/send/pause пропускают
последующие шаги, включая Destroy; finally cleanup отсутствует.

## Direct Apply port21

[actionApply.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionApply.ws)
добавляет applicable action и mutable context. Apply проверяет подготовленность,
вызывает ApplyImpl, после успеха читает текущий context/authority/fire и
вызывает AfterApplyImpl. Context может меняться в callback; повторный Apply
разрешён, поскольку original не имеет one-shot guard. Before/IsValid здесь
не вызываются: это отдельные queue/manager обязанности.

Prepare — местный setup initialized state, не перенос original Init. Он допускает
NULL context, чтобы сохранить эффект→ошибка порядок оригинала. Шесть original
exception cases возвращают false; ApplyImpl/AfterApplyImpl также сообщают
failure через bool. Это явное отличие от CLR exception propagation, а не полная
паритетность обработки ошибок. Реальные карточные handlers и production sink
ещё отсутствуют. Класс не подключён к интерактивному полю.

[Preparation20](D:/w3mod/docs/evidence/apply-check-preparation.json) связывает
14 original trace observations и шесть native-only checks с исходниками.
Board-compile21 exit0/blob85867bytes,20 sources; accepted18 files/Flash unchanged.
Native APPLY20 исполнены и приняты в21,20/20 failed0. Перезапустить REDkit и выполнить
`bgapply_check()` в тестовой сессии: ожидается
`APPLY_CHECK_DONE checks=20 passed=20 failed=0`.

Следующий этап — перенести manager policy на реальные action/request/registry
контракты, соединить queue dispatch с sink и power primitives. Не подменять
дважды читаемые CanProcess/Delay и после-effect context/Main сохранёнными
ранними снимками. Production scheduler/death drain/RNG/cancel остаются открытыми.


## Manager/driver port26

[actionManager.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/actionManager.ws)
содержит typed managed action/request, services, mutable context, ActionManager
sink и bounded driver. После ошибки manager сохраняет fault; driver не снимает
следующее действие и не принимает новые push. Native failure contracts — bool,
original CLR exceptions не воспроизводятся. Это явное отличие, не откат effects.

Missing effect возвращает false по умолчанию; missing service также fail closed.
TrySend имеет отдельные handled и sent: sent=false не препятствует pause,
handled=false останавливает ветку как exception seam. EmitBeforeDiagnostic
сам по себе не throw, как original Create+pop. IsDirty ставится до Apply.
Default service для MarkDirty записывает контекст; registry/request/cache/clock
adapters ещё предстоят. Abstract defaults не заменяют настоящие handlers.

Delay64 представлен high signed word/low raw word. Positive: high>0 либо
high==0/low!=0; Int64Min/Max и unsigned low cases не обрезаются. Перед pause
getter вызывается второй раз и argument не проверяется повторно. Original
oracle расширен49→56 семью long boundary cases; все56 passed.

Queue.BindAuthority optional; прежний bool остаётся fallback. Global читает
authority до validity, local после неё. Driver связывает текущий context и
ограничивает RunBudget диапазоном1–256. Это bounded action queue drain, не
GameController/AbilityManager/ExecutionStack/waiting-to-die scheduler.

Native86:56 original observations+30 guards/integration. Recipes задают inputs,
expected traces берутся из original oracle; код fixtures не воспроизводит
готовый expected trace. Шесть/пять failure classes на разных слоях обозначены
через bool+fault. [Manifest](D:/w3mod/docs/evidence/manager-check-preparation.json),
[generator](D:/w3mod/tools/core-check/generate_manager_checks.py).

Команда bgmanager_check сама вызывает queue39, Apply20 и manager86. Capture
требует latest versioned SuiteBegin, совпадение contractKey, порядок трёх batches,
все IDs/counters, SuiteEnd и отсутствие mod errors/failures.16 synthetic guards
passed; native26 suite ещё не запускалась. Old accepted21 evidence не заменяет
новую проверку изменившейся queue dependency.

Compile22 выявила запрет struct property на временном return; generator берёт
LastPause в локальную переменную. Compile23 исчерпала parser stack у длинной Run;
original cases разделены на семь маленьких функций.24/25 успешны;26 добавила
fail-closed missing-effect guard. Финальная26 exit0/blob121531bytes,22 sources,
19 accepted21 copies+GUI/Flash unchanged; actionQueue — единственная prior правка.

Следующий independent этап уже начат: [power111 static methods](D:/w3mod/docs/beta_power.md).
После numeric fixtures — registry/events/death drain и реальные services.

## Native26 принят; numeric28

Fresh log20:26:05 подтвердил queue39/Apply20/manager86, current version key,
failed0/no mod errors.22 exact sources/log/GUI hashes frozen в native26-acceptance.
Numeric28 добавляет55 tests. Из prior26 изменены два файла: удалён identical
ApplyImpl duplicate в actionManager; manager check entry вынесен в ordinary
BetaGwentRunManagerChecks, console exec wrapper сохранён. Manager policy не
переписана, но source/key изменились: regressions входят в bgpower_check.
Original numeric40 подтверждает raw setters; новый native55 ещё не исполнялся.
Bool numeric failure latches manager before following action; это проверяется
тремя extra integrations, не actual card effect/death acceptance.

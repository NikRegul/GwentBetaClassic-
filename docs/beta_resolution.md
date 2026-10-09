# Очереди и вложенные эффекты Beta 0.9.24

Обновлено: 2026-10-02. Это разбор статического IL оригинального клиента,
а не запись исполненного матча. Извлечены438 методов,9593 строки IL и2514
call sites. Оригинальная DLL не загружалась в CLR и не исполнялась.
Источник и SHA256: [manifest](D:/w3mod/docs/evidence/beta-resolution-summary.json).
Полные инструкции: [IL](D:/w3mod/docs/evidence/beta-resolution-il.txt),
[методы](D:/w3mod/docs/evidence/beta-resolution-methods.json),
[вызовы](D:/w3mod/docs/evidence/beta-resolution-calls.json).

## Один шаг coordinator

`GameController.Step` сначала выбирает ветку: при authority и существующей
неприостановленной CurrentInstance вызывает `AbilityManager.Update`, иначе
`ActionManager.Update`. Далее **в обоих случаях** вызывает RequestManager.Update.
При authority, отсутствии actions и instances вызывает ExecutionStack.Update,
затем PlayStack.Update; после этого обновляет локальных игроков. Нельзя заменить
этот порядок независимым полным опустошением всех очередей за один вызов.
Этот метод уже сохранён в [core IL](D:/w3mod/docs/evidence/beta-core-il.txt).

`ActionManager.Step` берёт actions[0]. При authority, валидном action и ещё
неотправленном Before вызывает BeforeApplyTrigger, оставляя action в очереди.
В другом шаге снимает **тот же объект** через Remove(action), затем ApplyAction.
Не RemoveAt(0): Before может добавить другие действия перед текущим.
`AbilityInstance.ExecuteNextAction` также отделяет Before от Apply, но на ветке
Apply снимает локальный actions[0] через RemoveAt(0) и передаёт ActionManager.
`AAction.BeforeApplyTrigger` помечает HasFiredBeforeApplyTrigger до вызова Impl.
`AAction.Apply` вызывает ApplyImpl, затем AfterApplyTriggers только при authority
и FireTriggers. Полная validity/request/network политика остаётся отдельно.

`PushActionImpl(front=true)` вставляет в начало; без authority требует
IPriorityAction, иначе бросает exception. false добавляет в конец.
У AbilityInstance есть собственная очередь и аналогичный front/end выбор.
Её первый PushAction может отменить PlayedTrigger, если начальный trigger —
BeforePlayedTrigger с CancelPlayedTrigger=true. Даже action, ещё не применённый,
имеет последствия на этой границе; нельзя откладывать всю семантику до Apply.

## Порядок способностей

`AbilityManager.Step` обрабатывает ActiveInstances[0]. `Add(front=true)` вставляет
перед **первым ещё не finished** instance; finished prefix пропускает. false
добавляет в конец. Это не обыкновенный LIFO для всех элементов.

`Trigger` сначала собирает подходящие passive instances в локальный список.
`AddAbilityInstance` вставляет каждого кандидата в этот список по следующим
условиям, затем Trigger передаёт список в Add(front=true) **с конца к началу**:

1. Больший ETriggerPriority раньше меньшего: Highest15, VeryHigh10, High5,
   Normal0, Low−5, VeryLow−10, Lowest−15.
2. При одинаковом priority больший location priority идёт раньше:
   Melee1→9, Ranged2→8, Siege4→7, Hand8→6, Leader64→5, Deck16→4,
   Graveyard32→3, PlayStack256→2, **точный ключ Ignore767→1**, Void512→0.
3. При одинаковой стороне owner — меньший GetIndex раньше. Равные index
   сохраняют порядок регистрации; сравнения instance ID в этом методе нет.
4. При разных сторонах раньше идёт owner текущего игрока. Индекс между
   разными сторонами не сравнивается.
5. Кандидат без owner вообще не проходит этот scan и добавляется в конец.

Не считать таблицу location масочным фильтром. Например, SpawningPool128
не имеет ключа в этой dictionary. Порядок исходной регистрации passive triggers
нужно ещё сохранить и проверить на карточных fixtures; одинаковые ключи зависят
от него. ActionOnTrigger1/2 после завершения способности с добавленными actions
вызывает AbortForAbility/AbortForAll. Это тоже часть будущего scheduler.

Написан [triggerOrder.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/triggerOrder.ws):
таблица и pure insertion index для заранее собранных tickets. Он не регистрирует
живые triggers и не разрешает эффекты. Guard−1 для неизвестного location/нужного
owner — ограничение черновика; оригинальная dictionary/dereference могла бы
бросить исключение. Подготовлены24 runtime проверки helper. Сравнение нового
WitcherScript с исполняемым original oracle пока не выполнено.

## ExecutionStack и смерть

ExecutionStack.Update ставит PopCardFromExecutionStackAction в очередь только
при authority, наличии entries и отсутствии actions/ability instances. Копирует
CardId/MoveReason entries в порядке списка. FireTriggers ставит false в
ClearBoard phase256, иначе true. Это отдельный слой от entry.TriggerAbilities.

HandlePush впервые записывает entry, помечает карту в execution stack,
вызывает OnWillMove и OnPush. Уже имеющийся entry заменяется и возвращается
после warning. При TriggerAbilities и authority могут начаться PlayedAbilityInstance
либо PlayCardAction; прежде чем описывать всё как перемещение, нужно разрешить
эти способности и requests.

HandlePop снимает in-execution flag и проверяет фактическую текущую позицию.
При переходе в Graveyard из другого location и token512 собирает banish attack;
при From.IsActive и текущем Graveyard собирает KillCardsAction. Затем вызывает
BoardManager.AfterMoved и Location.OnChanged; OnPop не вызывается для умершей
карты с ранее активной позицией. PopCard собирает эти последствия по entries,
затем ставит KillCardsAction и banish attack в очередь. У Kill action FireTriggers
также зависит от ClearBoard phase. Это не доказательство отключения всех
death abilities: entry flags и AbilityManager.OnCardKilled остаются отдельными.

## Лидер и цепочка Play

`RequestPlayCardAction.PlayCard` проверяет выбранный ID и повторное исполнение,
записывает CardIdPlayed, затем вызывает Card.Play(playerId). Последний ставит
PlayedBy и при authority + **Template.Tier=Leader1** создаёт SpawnRequest с той
же Definition в Leader64 на стороне PlayedBy, index−3, canBePlayed=false,
spawner=сыгранная карта, toCopy=null. Новый instance ID выделяется в ctor
SpawnRequest; SpawnCardsAction передаёт canBePlayed в CardManager.Register.
OnPlayedCard отправляется после постановки spawn action в очередь.

Это новый непригодный для повторной игры instance в зоне лидера, а не найденный
в универсальном Play коде SetCanBePlayedAction(false) для исходного instance.
SetCanBePlayedAction(false) обнаружен также в setup при LeaderEnabled=false.
Очистку исходного played instance и view/replacement нужно ещё связать с полным
ExecutionStack/PlayStack trace. DEV лидер намеренно остаётся простым флагом,
поэтому не считается переносом этой механики.

## Следующая реализация и приёмка

- Снять точный RequestAction pause/resume contract и node continuation; один
  незавершённый request должен удерживать нужную ability instance.
- Восстановить регистрацию/отписку passive triggers при Move/Transform/Lock.
- Создать изолированные original fixtures для порядка equal priority, same
  location, двух сторон, ownerless, nested Before и смерти во время Before.
- После oracle fixtures добавить coordinator/queues и карточные primitives;
  RNG/shuffle/target выбора не подменять приблизительными реализациями.

M1 и M4 остаются частичными. Новое поле можно проверять отдельно от этих задач.

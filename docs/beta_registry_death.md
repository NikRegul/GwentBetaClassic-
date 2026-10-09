# Registry IDs и pending death

> **Текущий статус 2026-10-02:** native28 принят (200 успешных assertions).
> Active38 —12 иллюстраций/hover preview и выбор своего ряда для лидера.
> Предыдущая37 наблюдалась до результата с заменами/бронёй/смертью/лидерами.
> Compile38 установлен, текущие арты/row choice native ещё не наблюдались.
> Generic scheduler впереди; новые suites отложены.
> См. [план](D:/w3mod/docs/plan.md), [сборку](D:/w3mod/docs/evidence/duel-development-result.json).
> Ниже сохранены прежние этапы и контракты; их номера не являются current status.


Обновлено2026-10-02. Это следующий участок после numeric power.
[Static IL](D:/w3mod/docs/evidence/beta-death-boundaries-il.txt) и
[manifest](D:/w3mod/docs/evidence/beta-death-boundaries.json) содержат26 методов
CardManager/Card/position predicates с original DLL hash. Это metadata,
не исполненный полный death drain.

## Instance IDs

Оригинальные Card.Id и CardManager.m_NextInstanceId — **UInt16**, template IDs
отдельно Int32. Начальное next1, AllCards64, recycled Stack<UInt16>.
Allocate сначала Pop recycled LIFO. Если стек пуст и next==AllCards.Length,
массив растёт на64, старые references копируются. Затем возвращается next и
увеличивается с conv.u2: после65535 появляется0. Exhaustion guard в этом методе
не найден. GetCard возвращает ту же reference либо null для отсутствующего/
выходящего за массив ID. Использование int в WS должно сохранять0..65535.

[Изолированный extractor](D:/w3mod/tools/oracle/extract_beta_registry_ids.ps1)
скопировал4 точных метода: AllocateInstanceId/GetCard/AllCards accessors,
без shims. [16/16 original fixtures](D:/w3mod/docs/evidence/beta-registry-id-fixtures.json)
прошли: sequences, рост64/128, reference сохранность, LIFO, duplicate recycled
inputs, wrap и null/boundary paths. Initial fields назначены напрямую; Card —
opaque stub. Constructor/Register/Unregister/Copy/events этим не проверены.

[registryIds.ws](D:/w3mod/BetaGwent/drafts/scripts/game/betagwent/registryIds.ws)
написан в drafts, не установлен и не компилировался. Guard для int input/local
Initialize — adapter difference; Recycle/WriteSlot только protected seams.
Нельзя считать этот allocator полноценным registry или связывать unsupported
ID exhaustion с playable match без явного решения.

Unregister по IL: AllCards[card.Id]=null → recycled.Push(card.Id) →
OnCardUnregistered(card). Проверки повторного unregister в этом методе нет.
Event subscribers видят уже освобождённый slot и доступный recycled ID.
Будущий generation/session identity UI должен защищать stale intents при reuse;
не объявлять instance ID уникальным навсегда.

## CanDie, Kill и MarkAsWaitingToDie

CanDie: Template.Type строго Unit4 и (location intersects7 или ExecutionStack).
Kill: если waiting уже true, no-op; иначе для Unit4 с CurrentPower>0 вызывает
SetPower(0), затем MarkAsWaitingToDie через Data.Card. Getter Data.Card читается
отдельно для выбора manager и аргумента, не один cached card.

MarkAsWaitingToDie имеет собственные guards: waiting и authority. При допуске
сначала устанавливает waiting=true, затем вставляет в список. Порядок —
**location numeric descending, затем index descending**, equal pairs stable.
PlayerId в сравнении отсутствует. Это другой comparator, чем trigger priority.
Position/get-list/Count читаются повторно. Reentrant Kill может вызвать Mark
дважды; второй Mark обычно отсекается собственным waiting guard. Non-authority
Mark не выставляет waiting. Эти утверждения пока static IL, не full oracle.

## Drain требует coordinator

KillWaitingToDie выполняется только при authority. Пропускает Graveyard32 и
already banished. Для non-Event2 с Base+Permanent<=0 собирает общий banish
action; остальные получают ExecutionStackEntry для Graveyard с index-3,
CanRollback=false, TriggerAbilities=true и MoveReason4. Banish создаётся с
element0 — это отличается от inactive power setter, где Physical1.

Порядок очереди: optional Banish → PutCardInExecutionStack → optional Pop.
Put получает FireTriggers после Push по текущей phase: в ClearBoard256 false.
Затем всем pending cards снимается waiting и список очищается. Даже пустой
список не имеет отдельного раннего return перед Put; не оптимизировать этот
край без fixtures. Это не непосредственное удаление карты в момент силы0.

Следующий шаг: exact Card.CanDie/Kill/Mark/drain boundary fixtures, затем
live-card events и registry/coordinator integration. Active28 содержит только
numeric raw setter boundary; death handlers ещё не подключены.

[Power](D:/w3mod/docs/beta_power.md),
[план](D:/w3mod/docs/first_playable_plan.md).

# Интерактивные requests: development field18

Обновлено:2026-10-02. Версия15 исполнила CORE116/BOARD104/REQUEST123 checks
без failed. При этом engine сообщил unhandled switch для location128;
в18 добавлен default-return в triggerOrder. Новый native18 прогон подтвердил
три116/104/123/43 batches без ошибок мода; switch128 diagnostic отсутствует.
[Принятая трасса15 с диагностикой](D:/w3mod/docs/evidence/request-runtime-accepted-20261002.json).

## Что добавлено

[developmentRequestFlow.ws](D:/w3mod/BetaGwent/development/scripts/game/betagwent/developmentRequestFlow.ws)
соединяет requestState, continuation и локальный store с menu. «Выбор(DEV)»
строит choices из обеих тестовых рук: своя открыта, чужая — скрытые копии.
«Цели(DEV)» допускает только видимые карты: свою руку и карты в рядах обеих
сторон. После завершения результат копируется до Destroy, связанный узел
завершается один раз. Current board/score не изменяются этим fixture.

События UI несут revision,requestId,playerId,kind и для Select ещё itemId.
Menu проверяет revision; flow проверяет остальные поля. Старый ID, другая
сторона/тип и недопустимая карта отклоняются. Старые callbacks Flash захватывают
ключи показанного snapshot и отказываются отправлять intent после его смены.
После Select UI ждёт новый authoritative snapshot, не меняет selection сам.

Choices показываются отдельным окном,12 на страницу; hidden card не получает
original ID, template или title. Targets выделяются непосредственно на поле
и в своей руке; жёлтая рамка означает выбранную цель. Повторный клик снимает
выбор. Счётчик/доступность Finish поступают из core. Max завершает запрос
автоматически; choices можно завершить раньше после min.

Во время запроса обычные Play/Pass/Leader/OpponentStep/NextRound/Restart
отклоняются. Checks работают на отдельных объектах. «Прервать DEV» и закрытие
меню очищают только fixture request и continuation; это не original play
rollback. Меню затем восстанавливает input context и cursor как прежде.

## Протокол snapshot

После setBoardHeader и board cards menu вызывает:

- setRequestHeader:9 аргументов — revision,id,player,kind,min,max,count,
  canFinish,message. ID0 означает отсутствие pending request.
- pushRequestCard:6 аргументов — UI id,title,templateId,factionId,revealed,
  selected. Для choices это synthetic ID; для targets — ID видимой карты.
- finishBoardState(revision) коммитит весь board/request snapshot одним render.

Core GetChoiceViews и GetTargetViews проверяют тип запроса и получателя.
Rejected request intents возвращают текущий snapshot для снятия ожидания UI.
Failed/stale intents не меняют игровую руку, расположение карт или счёт;
presentation revision при resync может измениться.

## Проверки и состояние установки

Историческая board-compile18: exit0/blob71006bytes,16 sources с UTF8 BOM;
compiler errors0. Native .redswf обновлён file-only; non-ABC tags, native image
tags, properties и4 texture chunks сохранены, CRC/offsets проверены.
Backup принятого ресурса e19bc1…070ff — BetaGwent/build/resource-backups.

[FLOW43 preparation](D:/w3mod/docs/evidence/request-flow-check-preparation.json):
hidden views/mapping, select/deselect, min/max/auto completion, fresh IDs,
wrong/stale keys, close/abort и неизменность fixture board. Native43 прошли в18,
а в20 уже есть живые request BEGIN/SELECT/END/ABORT: choices/targets и abort.
[Чистая приёмка18](D:/w3mod/docs/evidence/request-flow-runtime-accepted-20261002.json).
Изолированные checks пишут REQUEST_FIXTURE_*; они не считаются
реальными UI intents. Capture требует все116/104/123/43 и отсутствие script errors.

[Request ABC checks](D:/w3mod/docs/evidence/request-bridge-bytecode.json):8/8,
signatures/context activation/wire construction. Bound native sender checks3/3,
resource guards5/5, parser guards15/15. Это compiled/file/synthetic checks,
не executed AS3/native interaction. Ручной шаг:
[BOARD_CHECK.md](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md).

Текущая script версия26:22 active sources, manager/driver и suite39/20/86
ожидают native прогон. ACTION39 принят в20, direct Apply20 в21. При добавлении
manager изменён authority binding очереди;19 prior21 sources и Flash сохранены.
Новые проверки отложены до возвращения. [Очередь](D:/w3mod/docs/deferred_checks.md).

## Граница production переноса

Этот слой использует synthetic cards и локальные IDs, не canonical card effects.
Нет graph interpreter, full Before/Apply scheduler, authority/mirror, таймеров,
живого registry, RNG consumption или canonical cancellation. Shape fixture
single-card; AoE/movement/death во время pending нужно подключить к реальному
coordinator. Полный session identity между повторными открытиями и production
request allocator также предстоят. Local node1 — граница теста, не импорт NId.

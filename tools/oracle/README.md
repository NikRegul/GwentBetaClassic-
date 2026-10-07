# Проверки выделенных оригинальных методов

> **Текущий статус 2026-10-02:** native28 принят (200 успешных assertions).
> Active38 —12 иллюстраций/hover preview и выбор своего ряда для лидера.
> Предыдущая37 наблюдалась до результата с заменами/бронёй/смертью/лидерами.
> Compile38 установлен, текущие арты/row choice native ещё не наблюдались.
> Generic scheduler впереди; новые suites отложены.
> См. [план](D:/w3mod/docs/plan.md), [сборку](D:/w3mod/docs/evidence/duel-development-result.json).
> Ниже сохранены прежние этапы и контракты; их номера не являются current status.


Harness запускают отдельные DLL, созданные Cecil из оригинальных IL методов
Beta0.9.24.3.432. Клиент Gwent, Unity и original module initializer не
запускаются. Exact-instruction manifests и hashes проверяются перед исполнением.
Fixtures не заменяют игровой trace всего клиента.

| Extractor / harness | Результат | Граница |
|---|---|---|
| extract_beta_flow.ps1 / beta-flow-ref |20/20|Коронные результаты/победитель/pass reset;24 скопированных метода|
| extract_beta_requests.ps1 / beta-request-ref |18/18|Limits, Apply clamp и finish;18 методов, два provider shims для counts|
| extract_beta_rng.ps1 / beta-rng-ref |37/37|Seeded RNG overloads/copy/counter/rewind;23 метода, четыре stubs сообщений исключений|
| extract_beta_actions.ps1 / beta-action-ref |36/36|Global/local queue and Before guard;21 copied methods, пять boundary shims; dispatch без эффекта|
| extract_beta_apply.ps1 / beta-apply-ref |14/14|AAction.Apply и четыре accessors; четыре seams, initialized field задан напрямую; manager policy вне oracle|
| extract_beta_manager_apply.ps1 / beta-manager-apply-ref |56/56|ApplyAction +три accessors;24 callback seams; actual effects/network/cleanup вне oracle|
| extract_beta_power_numeric.ps1 / beta-power-numeric-ref |40/40|18 numeric/accessor methods;1 raw setter seam; no live events/death; native55 pending28|
| extract_beta_registry_ids.ps1 / beta-registry-id-ref |16/16|4 allocate/lookup/accessor methods, no shims; initial state assigned, opaque Card; no Register/Unregister/event acceptance|

```powershell
powershell -NoProfile -File D:\w3mod\tools\oracle\extract_beta_requests.ps1
dotnet run --project D:\w3mod\tools\oracle\beta-request-ref -- D:\w3mod
python D:\w3mod\tools\core-check\generate_request_limits.py
```

Последняя команда переносит18 подтверждённых observations в native
developmentRequestChecks.ws и фиксирует ожидаемое число123 checks.
Эти123 assertions уже прошли в REDkit на версии15; в том запуске была
отдельная switch128 diagnostic. Версия18 исправила её; в20 interactive
DEV UI/FLOW43 и очередь39 приняты. Direct Apply20 принят в21. Повторная генерация
fixtures сама по себе не подтверждает runtime изменённых источников.
Проекты используют установленный net7 SDK и локальный NuGet.Config без
package sources. Evidence пишутся внутри D:\w3mod.

Результаты: docs/evidence/beta-flow-fixtures.json,
beta-request-limit-fixtures.json, beta-rng-fixtures.json. Подробности:
[beta_rng.md](D:/w3mod/docs/beta_rng.md),
[beta_requests.md](D:/w3mod/docs/beta_requests.md).

Очереди: [beta_actions.md](D:/w3mod/docs/beta_actions.md). Original36 прошли;
native39 исполнены и приняты в20. Полный scheduler
не входит в эти oracle. ActionManager.ApplyAction отдельно проверен в manager56. Дополнительный Apply14
подтвердил чтение authority/fire после ApplyImpl; WS direct Apply20 принят21. Manager/driver26 готов,39/20/86 native suite предстоит.

Пользователь вернулся: manager26 принят по native log, original numeric40 и
registry ID16 исполнены. Active28/POWER55 compile success; native ещё предстоит.
[Очередь](D:/w3mod/docs/deferred_checks.md).

# Native core checks

> **Текущий статус 2026-10-02:** native28 принят (200 успешных assertions).
> Active34 — новый visible DEV duel:25-card decks, targets/effects/armor/death,
> автоматический соперник и раунды/добор. Fixed order, no mulligan/complete scheduler.
> Новые тесты отложены пользователем; duel runtime ещё не наблюдался.
> См. [план](D:/w3mod/docs/plan.md), [сборку](D:/w3mod/docs/evidence/duel-development-result.json).
> Ниже сохранены прежние этапы и контракты; их номера не являются current status.


Native checks выполняются в WitcherScript, их source expectations не заменяют
запуск в REDkit. Подготовка: UTF-8 BOM через tools/ui/prepare_board_scripts.py,
Wcc compile, restart редактора и тестовый сейв.

- `bgcore_test()`:116 checks pure helpers.
- «Проверить ядро» на поле:116/104/123/43, отдельные fixture объекты.
- `bgactions_check()`:39 queue boundary checks, отдельные объекты без поля.

`prepare_action_queue_checks.py` связывает31 native IDs с executed original
observations, отмечает два exception/guard differences, шесть added guards и
три неперенесённых debug observations. Ничего не исполняет в игре.
`capture_action_runtime.py` читает latest ACTION BEGIN→DONE, требует все case
IDs/counts и блокирует при failed/mod script errors. `check_action_capture.py`
проверяет10 synthetic сценариев parser, не создавая fake runtime evidence.

[Action port](D:/w3mod/docs/beta_actions.md),
[manual check](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md),
[план](D:/w3mod/docs/plan.md).


`bgactions_check()` принят в20,39/39. `bgapply_check()` — новая isolated
команда в21,20 checks. prepare_apply_checks.py связывает14 original traces
с native expectations, выделяет шесть exception→false differences и шесть
native-only guards. capture_apply_runtime.py использует собственный APPLY
BEGIN→DONE и проверяет hashes runner/base. Native20 pending.
Shared Action/Apply parser12 synthetic checks passed; original manager49/49
исполняется отдельно в tools/oracle/beta-manager-apply-ref, не в TW3.


Актуально26: bgapply_check20 принят21. bgmanager_check запускает регрессию
queue39/Apply20 и manager86. generate_manager_checks.py:56 recipe inputs,
oracle expectations,30 native guards/integration и versioned contractKey.
capture_manager_runtime.py не принимает прошлый suite после нового unfinished/
wrong-key запуска. check_manager_capture.py16 synthetic tests passed.
MANAGER suite не доказывает real effects/services/full scheduler.

## Текущая numeric версия28

Native26 manager39/20/86 принят; frozen evidence в native26-acceptance.json.
Original power40/registry ID16 прошли. Numeric55=40 original+12 guards+3 manager
integrations сгенерирован, active24 sources/compile28 successful. bgpower_check
запускает39/20/86/55; live final setter/events/death отсутствуют. Power parser22
synthetic guards, Manager16/Action12 прошли отдельно. Capture требует current keys
и exact markers через outer END; late extra passes и newer SKIPPED отвергаются.
Preparation: generate_manager_checks.py → generate_power_number_checks.py →
prepare_board_scripts.py → compile → capture_board_preparation.py →
audit_power_number_preparation.py. Старый manager audit относится к active26.
[Ручная инструкция](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md).

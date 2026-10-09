# Отложенные проверки

2026-10-02 пользователь прямо попросил: «меньше тестов, больше результата»,
«Тесты будет делать потом». Не требовать новые ручные suites до его готовности.

Native28 numeric55 + manager86/Apply20/queue39 принят по fresh log21:05:45;
native26/21/20 сохранены отдельно. Registry22 command был подготовлен до
смены приоритета и остаётся опциональным; новая REGISTRY suite не исполнялась.
Death-entry extractor5/10 seams написан, exact IL checked, harness не создавался
и original death methods этим не были исполнены. Продолжение oracle отложено.

Сейчас установлен visible duel38. Когда вернёмся к проверкам, сначала открыть
`bgboard_open()` и сыграть обычную дуэль: карты/цели, броня/смерть, пас/добор,
следующий раунд/результат/перезапуск/закрытие. Потом запускать только suites,
нужные для обнаруженных проблем. No blanket native acceptance from compile.

Исторические audit_manager_preparation.py и audit_power_number_preparation.py
привязаны к активным26/28 и после обновления38 неприменимы как current audit.
Frozen accepted JSON/log/sources остаются историческими доказательствами.
Текущий artifact manifest: docs/evidence/duel-development-result.json.

Compile37: позже проверить RNG overflow/logical shifts по уже существующим vectors,
blacklist fallback/повторную замену incoming/границы раундов и native animations.
Отдельные новые suites в этом этапе не создавались.

Ordinary37 наблюдалась до результата партии (duel37-observed-20261002.json).
Для38 позже сначала увидеть12 artwork decode/hover/leader own-row/cancel.
Нет новых наборов тестов: Wcc/AS3 compile и artifact association выполнены.

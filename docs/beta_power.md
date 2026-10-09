# Power primitives: следующий участок переноса

> **Текущий статус 2026-10-02:** native28 принят (200 успешных assertions).
> Active38 —12 иллюстраций/hover preview и выбор своего ряда для лидера.
> Предыдущая37 наблюдалась до результата с заменами/бронёй/смертью/лидерами.
> Compile38 установлен, текущие арты/row choice native ещё не наблюдались.
> Generic scheduler впереди; новые suites отложены.
> См. [план](D:/w3mod/docs/plan.md), [сборку](D:/w3mod/docs/evidence/duel-development-result.json).
> Ниже сохранены прежние этапы и контракты; их номера не являются current status.


Обновлено2026-10-02. [IL report](D:/w3mod/docs/evidence/beta-power-primitives.json)
содержит111 методов шести типов плюс Card.CanDie/Kill/get_IsWaitingToDie.
[Текст IL](D:/w3mod/docs/evidence/beta-power-primitives-il.txt) связан hash с
оригинальной DLL0F77D0…D5B42F. Это read-only metadata, **не исполнявшийся oracle**.

Типы: SetArmorAction, SetPowerAction, CardPowerAttack, ApplyChangePowerAction,
ChangePowerAction и CardPower. EPowerType: Current0/Base1/Permanent2/Armor3;
ECardPowerOp: Add0/Remove1/Set2/Multiply3/Restore4. Unit type — строго4.

## Числовые поля и порядок side effects

SetPowerAndArmor сначала ограничивает оба аргумента снизу нулём, сохраняет
старые currentPower/currentArmor, записывает изменения. При отсутствии
изменений весь дальнейший блок пропускается, даже если сила уже0.

После изменения вызывается Card.OnPowerChanged(card,oldPower,oldArmor), затем
**повторно читается** CurrentPower. При <=0 и Card.CanDie вызывается Kill.
CanDie требует Template.Type==Unit4 и (активную позицию либо ExecutionStack).
Проверка на type mask с любым пересечением здесь была бы неверной.

После Kill снова читаются card/current/base/permanent/controller/position.
При CurrentPower==0, Base+Permanent<=0, authority и пересечении location с248
(Hand/Deck/Graveyard/Leader/SpawningPool) создаётся CardBanishAttackAction:
attackerNULL, Direct0, Physical1, removal0; Add(card), PushAction(front=false).
Card.CanDie относится к Kill; последующая inactive Banish ветка отдельна.
Subscriber OnPowerChanged и Kill могут менять поля/позицию между чтениями.

Kill сначала проверяет IsWaitingToDie. Для Unit с положительной силой вызывает
SetPower(0), затем MarkAsWaitingToDie. Между ними возможен reentrant setter/
OnPowerChanged/Kill; повторного IsWaitingToDie guard перед Mark нет. Удаление
карты из registry или immediate Graveyard move этим методом не доказано.

## Set base/permanent

| Метод | Важная последовательность |
|---|---|
| SetPower(value) | SetPowerAndArmor(value,currentArmor) |
| SetArmor(value) | SetPowerAndArmor(currentPower,value) |
| SetBasePowerAndArmor(value,armor) | delta=value-oldBase **до clamp**; Base=max(0,value); Permanent=max(-Base,oldPermanent); SetPowerAndArmor(oldCurrent+delta,armor) |
| SetPermanentPowerAndArmor(value,armor) | delta=value-oldPermanent **до clamp**; Permanent=max(-Base,value); SetPowerAndArmor(oldCurrent+delta,armor) |

Эти операции используют signed int32 add/sub, без checked overflow в IL.
Нельзя заменить raw requested delta разностью уже ограниченных полей.
Reset(false) сохраняет base/permanent/armor и ставит current=base+permanent;
Reset(true) сначала читает templatePower, обнуляет permanent и использует
templateArmor. Он также проходит через setter/event/death policy.

## Attack/action boundary

SetPowerAction работает по CardIds в порядке списка; EPowerType0/1/2 вызывает
соответствующий setter, остальные значения бросают NotImplementedException.
SetArmorAction вызывает SetArmor для каждого CardIds. Сам registry lookup и
изменение списка во время callbacks ещё должны быть проверены oracle.

CardPowerAttack.OnApply идёт по Targets с повторным чтением Count. Для каждого
target сохраняет четыре old values, выполняет Set/Add/Multiply/Restore и читает
фактические resulting values. Authority записывает current/permanent/base/armor
deltas, другая сторона сравнивает current/armor с переданными deltas и логирует
расхождение. После всех targets вызывается OnCardPowerAttack. Это не равно
простому изменению единственного поля currentPower.

Attack Multiply PermanentPower только пишет diagnostic, не выполняет setter.
Restore для current/base/permanent ведёт к RestorePower; Armor — RestoreArmor.
SetTargetPower включает Armor3, в отличие от прямого SetPowerAction. Не смешивать
эти две dispatch таблицы при генерации handlers.

## Numeric boundary28

[powerNumbers.ws](D:/w3mod/BetaGwent/scripts/game/betagwent/powerNumbers.ws)
перенесён в active28 и скомпилирован. Current/base/permanent setters, restore,
armor add/multiply; финальный SetPowerAndArmor fail closed, пока нет live card.
Отказ сохраняет prior base/permanent writes; InitFromFields — local seam.

[Extractor18](D:/w3mod/tools/oracle/extract_beta_power_numeric.ps1) исполнился с
exact IL match; [40/40 fixtures](D:/w3mod/docs/evidence/beta-power-numeric-fixtures.json)
прошли. Один raw setter seam, no clamp/current updates/events/death. Native55:
40 original+12 guards+3 manager integrations; current suite key59af251c490c2f86.
Native pending: `bgpower_check()` запускает также39/20/86 regressions.

Float product вне Int32 диапазона явно отвергается: native FloorF и CLR conv.i4
не объявляются эквивалентными на этом краю. Native int wrapping/float precision
требуют actual55. Callback exceptions отображаются false без rollback.
Таким образом numeric40 не доказывает реальный power attack или смерть карты.

## Следующий участок

Exact SetPowerAndArmor/event/reentrant-death fixtures, затем real registry
и coordinator. [Registry/death](D:/w3mod/docs/beta_registry_death.md) содержит
новые26 static methods и original UInt16 ID16 checks. Banish element у setter1,
у death drain0; не объединять эти different paths. Full death/armor absorption
handlers ещё не подключены.

[BOARD_CHECK](D:/w3mod/GwentB/myproject1/BOARD_CHECK.md),
[план](D:/w3mod/docs/first_playable_plan.md).

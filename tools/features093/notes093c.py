"""Release text derived from the completed, accepted 0.9.3c trial."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write_notes(proof):
    assert proof['accepted'] and proof['version'] == '0.9.3c'
    h = proof['holdout']
    assert h['games'] == 3680 and h['errors'] == 0
    rate = f"{100 * h['scoreRate']:.2f}"
    low, high = f"{100 * h['lower99']:.2f}", f"{100 * h['upper99']:.2f}"
    cluster = f"{100 * h['clusterLower99']:.2f}"
    ru_changes = '''- Лидер учитывает следующую карту своей руки после ответа соперника. Это помогает оценить подготовку сброса, воскрешения и усиления. При скрытой вражеской засаде и сниженном бюджете сохраняется прежний осторожный поиск.
- В развитом первом раунде ИИ может разыграть доборного шпиона перед уступкой раунда, сохранив число карт в руке. Свежая раздача, меньшая или короткая рука и обязательный раунд сохраняют строгие ограничения. Бюджет последующего догоняющего хода не ослаблен.
- В обязательных коротких окончаниях с четырьмя картами в руке против одной–трёх карт соперника ИИ сравнивает ветви «свой ход → возможный ответ → своё продолжение» от общей исходной позиции. Это ограниченный поиск двух своих ходов, а не перебор всех четырёх карт до конца партии. Расширение действует после использования лидеров и при нормальном вычислительном бюджете; ограничения для медленного устройства сохранены. За шаг подготовки моделируется не более одного действия.'''
    en_changes = '''- Leaders consider their own next hand play after an opponent reply, improving evaluation of discard, resurrection and boost setup. Concealed opposing traps and reduced computation budgets retain the conservative fallback.
- In a developed optional first round, a drawing spy may be played before conceding while preserving hand size. Fresh openings, smaller or short hands and mandatory rounds retain strict recovery checks. The subsequent chase budget is unchanged.
- Mandatory short endings with four own hand cards against one to three opposing cards compare own move → plausible reply → own continuation from a common starting position. This is a bounded two-own-move frontier, not an exhaustive search through all four cards to the end of the match. The expansion requires both leaders used and the normal computation budget; slow-device limits are preserved. Each preparation step simulates at most one action.'''
    ru_trial = f'''Адресный пример из записанной development-партии: при счёте 32:11 два хода немедленно давали одинаковые 10 очков. Старый ИИ выбирал Учителя из Бан Арда, новый — «Ласточку». При одной и той же политике 0.9.3b на всех последующих ходах первая ветвь проиграла 37:38, вторая выиграла 50:46. Так проверен сам порядок карт; этот пример не заменяет оценку общей силы.

Проверка против 0.9.3b: **3680 партий на 92 уникальных составах**, 10 заранее зафиксированных случайных сеток пар и зеркальные стороны. Кандидат: {h['wins']} побед, {h['losses']} поражений, {h['draws']} ничьих, 0 ошибок; **{rate}% очков** с учётом ничьей за 0,5. Приближённый 99% интервал по парным блокам — {low}–{high}%; нижняя 99% граница по кластерам составов — {cluster}%. Оба заранее заданных порога выше 50% пройдены.

Раздачи, RNG и правила карт общие; муллиганы независимые, обе версии играют обе колоды и обе стороны. Отрицательный контроль с одинаковым ИИ дал ровно 50% в каждом из 92 блоков, всего 368 партий. Результат относится к этой выборке стенда и не обещает превосходства на любой колоде или против человека. Доказательство включено в `BetaGwentDocs/AI_Validation_0.9.3c.json`.'''
    en_trial = f'''A recorded development-game witness began at 32:11 with two plays worth the same immediate ten points. The old AI chose Ban Ard Tutor; the new AI chose Swallow. With the same unchanged 0.9.3b policy making every subsequent decision, the first branch lost 37:38 and the second won 50:46. This isolates the opening choice; the witness does not replace a general strength comparison.

Comparison against 0.9.3b: **3,680 games across 92 unique compositions**, ten fixed random matchup grids and mirrored sides. Candidate: {h['wins']} wins, {h['losses']} losses, {h['draws']} draws, zero errors; **{rate}% score**, with draws worth 0.5. Approximate 99% paired-block interval: {low}–{high}%; composition-cluster 99% lower bound: {cluster}%. Both predeclared thresholds above 50% passed.

Deals, RNG and card mechanics are shared; mulligans are independent and both policies play both decks and sides. The identical-policy negative control scored exactly 50% in each of 92 blocks, across 368 games. This supports the measured stand sample, not universal superiority or strength against humans. Evidence is included in `BetaGwentDocs/AI_Validation_0.9.3c.json`.'''
    ru_limits = '''Поиск требует больше вычислений: в принятом сравнении среднее время решения на JS-стенде составило около 108 мс против 95 мс у 0.9.3b. Это не замер FPS или задержки интерфейса в игре. Подготовка остаётся пошаговой, прежние ограничения сниженного бюджета сохранены.

Сохранены исправления блокировки и «Стойкости», видимая кнопка сложности в выборе колоды и редакторе, одобренные колоды и исходная «Классическая» с 24 профилями и 109 назначениями. «Классическая» по-прежнему видит скрытую руку и колоду; обычный Hard сохраняет прежние ограничения информации. Старый турнир на неизменной 0.9.3 не измеряет силу этой версии.

Для готовых архивов обязательны полные регрессии, оба нативных компилятора WitcherScript, профильные партии, проверки управления, меню не более 65 МиБ и независимые SHA/CRC. Нативная игровая приёмка интерфейса и RNG остаётся открытой. Автоматическая установка и публикация не выполняются.'''
    en_limits = '''The search costs more computation: mean decision time in the accepted JS-stand comparison was approximately 108 ms, versus 95 ms for 0.9.3b. This does not measure retail FPS or interface latency. Preparation remains cooperative and the reduced-budget limits are preserved.

Includes the lock/resilience fixes, visible deck-selection and deck-editor difficulty button, approved decks and unchanged original Classic mode with 24 profiles and 109 bindings. Classic retains hidden-hand and deck access; ordinary Hard retains its information limits. The completed frozen 0.9.3 tournament does not measure this version.

Ready archives require full regressions, both native WitcherScript compilers, profile games, input checks, menus within 65 MiB and independent SHA/CRC verification. Native in-game UI and RNG acceptance remains pending. Nothing is automatically installed or published.'''
    directory = ROOT / 'docs/releases'
    for lang, changes, trial, limits, intro in [
        ('RU', ru_changes, ru_trial, ru_limits, 'Улучшения обычного ИИ поверх полной 0.9.3b для Classic 1.32 и Next-Gen 5.0+.'),
        ('EN', en_changes, en_trial, en_limits, 'Ordinary AI improvements over the complete 0.9.3b release, for Classic 1.32 and Next-Gen 5.0+.'),
    ]:
        body = f'# Gwent Beta Classic 0.9.3c\n\n{intro}\n\n{changes}\n\n{trial}\n\n{limits}\n'
        for kind in ('CHANGELOG', 'DESCRIPTION', 'POST'):
            (directory / f'0.9.3c_{kind}_{lang}.md').write_text(body, encoding='utf8')
    nexus = directory / '0.9.3c/nexus'
    nexus.mkdir(parents=True, exist_ok=True)
    (nexus / 'README_RU.md').write_text('Пакет 0.9.3c подготовлен локально. Публикация не выполнялась. Описания, посты и изменения находятся в docs/releases/0.9.3c_*.md.\n', encoding='utf8')

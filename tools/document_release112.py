from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
release=ROOT/'BetaGwent/release'
notes={
 'RU':'''# Gwent Beta Classic 0.3.3

**Перед обновлением сделайте бэкап сейвов. Устанавливайте только один язык. Сначала используйте отдельное тестовое сохранение.**

- Убраны видимые переводы строки из заголовков. Противник подписан лидером и названием колоды, имя NPC видно перед боем.
- Счёт рядов и общий счёт центрированы по исходным цифрам Beta. Длинные подписи кнопок подогнаны с отступами от рамок.
- Пас через удержание монеты, P или Y / △; мгновенный клик больше не пасует. Сохранён индикатор удержания.
- Поиск и переименование используют общее окно ввода с Unicode и выбранной RU/EN-клавиатурой. Пустой поиск снимает фильтр.
- Сохранение колоды сообщает конкретную причину отказа; длинные исходные названия ограничиваются 48 символами. Старые сейвы сохраняют прежнюю структуру.
- ИИ учитывает безопасные ряды после предпочтений архетипа и соседней поддержки. Заполненные ряды исключаются; тактические исключения и правила призыва сохранены.
- Добавлены данные размещения ИИ и причины валидации колод в лог.

Компиляция и упаковка проверяются автоматически; работу новой графики, ввода и сохранений в основной игре нужно подтвердить отдельно. Новая модель ответов игрока и новые обученные веса в эту версию не включены.

''',
 'EN':'''# Gwent Beta Classic 0.3.3

**Back up your saves before updating. Install one language only. Start with a separate test save.**

- Removed visible escaped line breaks in headings. Opponent profiles show the leader and deck name; the NPC name remains on the setup screen.
- Row and total scores are centred using the original Beta numeral bounds. Long button labels fit inside their frames with padding.
- Hold the coin, P or Y / triangle to pass. A quick click no longer passes; the progress animation remains.
- Search and renaming share a text dialog with Unicode input and a selectable RU/EN keyboard. An empty search clears the filter.
- Deck saving reports the specific reason for rejection; long initial names are limited to 48 characters. Existing save schemas are unchanged.
- AI placement checks safe rows after archetype and neighbour preferences. Full rows are excluded; tactical exceptions and summon rules are preserved.
- Added AI row-placement details and deck-validation reasons to the log.

Compilation and packaging are checked automatically. Visuals, input and save persistence still need verification in the installed game. The experimental opponent-response model and new trained weights are not included in this release.

'''}
for lang in ('RU','EN'):
    p=release/f'CHANGELOG_{lang}.md';old=p.read_text('utf-8-sig')
    if not old.startswith('# Gwent Beta Classic 0.3.3'):p.write_text(notes[lang]+old,'utf8')
    p=release/f'README_{lang}.md';s=p.read_text('utf-8-sig').replace('0.3.2','0.3.3');p.write_text(s,'utf8')
    p=release/f'CONTROLS_{lang}.md';s=p.read_text('utf-8-sig')
    s=s.replace('P — пас','удерживать P — пас').replace('P passes','hold P to pass')
    extra='\nПоиск и переименование: нажмите поле, выберите RU/EN, напечатайте текст и подтвердите Enter / «Принять». Пустая строка сбрасывает поиск.\nПас мышью: удерживать монету; короткий клик отменяет удержание.\n' if lang=='RU' else '\nSearch and rename: click the field, choose RU/EN, type and confirm with Enter / Apply. An empty query clears the search.\nMouse pass: hold the coin; a quick click cancels the hold.\n'
    if extra not in s:s+=extra
    p.write_text(s,'utf8')
plan=ROOT/'docs/plan.md';s=plan.read_text('utf-8-sig')
head='''## Текущий шаг — 0.3.3 / Stage 112 (09.10.2026)

Исправления обратной связи 0.3.2 внесены; идёт сборка RU/EN. [Изменения и единая проверка](CHANGESET_033_RU.md), [сборка](BUILD_033_RU.md).
Прочитан и сохранён последний игровой scriptslog. Проверены безопасные и заполненные ряды ИИ, стартовые/пользовательские слоты. Новая модель ответов игрока остаётся прототипом симулятора.
Далее: закончить упаковку → проверить ввод/подписи/счёт/пас и сохранение в основной игре → перенос оценки возможного ответа игрока → сравнение 40 колод → дальнейшая сверка анимаций с Beta.

'''
if not s.startswith('## Текущий шаг — 0.3.3'):plan.write_text(head+s,'utf8')
print('0.3.3 release documentation updated')

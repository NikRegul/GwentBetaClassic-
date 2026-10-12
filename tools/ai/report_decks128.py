"""Summarise immutable paired roster trials, including rejected candidates."""
import hashlib,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
rules=read(ROOT/'data/beta924/ai/rules.json')
presets={p['id']:p for p in read(ROOT/'data/beta924/duel/presets.json')['presets']}
full={c['templateId']:c for c in read(ROOT/'data/beta924/planning/full_catalog.json')['cards']}
rows=[];files=[];fingerprints=set()
for suffix in 'abcdefghij':
    path=ROOT/f'docs/evidence/deck-candidates128-{suffix}.json'
    report=read(path);fingerprints.add(json.loads(report['signature'])['fingerprint'])
    files.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    for ident,deck in report['decks'].items():
        assert len(deck['games'])==40 and not deck['errors']
        assert Counter(g['newOnLeft'] for g in deck['games'])=={True:20,False:20}
        old,new=Counter(deck['oldCards']),Counter(deck['newCards'])
        describe=lambda counts:', '.join(full[i]['title']+(f' ×{n}' if n>1 else '') for i,n in counts.items())
        rows.append(dict(preset=int(ident),candidate=suffix,remove=describe(old-new),add=describe(new-old),wins=deck['newWins'],losses=deck['oldWins'],draws=deck['draws'],selected=new==Counter(presets[int(ident)]['templateIds'])))
assert len(fingerprints)==1 and len(rows)==16
summary=dict(games=640,trials=rows,files=files,engineFingerprint=next(iter(fingerprints)),strength=4,simulationDamp=40,seeds=list(range(128000,128020)),nativeGameTested=False,selectionTrialsNotIndependentEvaluation=True)
(ROOT/'docs/evidence/decks128-comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n','utf-8')
lines=['# Правки колод и проверка связок — 11 октября 2026','',
 'Сборка остановлена по запросу. Здесь изменения исходников и результаты локального исполнения переведённого WitcherScript; проверки в обычной игре и на физическом контроллере не выполнены.','',
 '## Связки','',
 '- Фрингилья сохранена. Между **любым слабым отрядом слева и сильным справа** она уменьшает силу правого. Эмиссар не является обязательным условием. Проверены обычные отряды, другие шпионы, изменённая сила и настоящий выбор хода ИИ.',
 '- Драйг сохранён: укрепление двух будущих целей, затем воскрешение жрицей. Проверены категории целей и сохранение усиления.',
 '- Сабрина сохранена: слабый отряд в выбранном чужом ряду, положительная выгода Завещания и доступный способ убить Сабрину. Проверена вся последовательность; без активации карта отвергается.',
 '- Драккар получает будущую ценность от соседа справа; Гром стимулирует собрать тройку в безопасном ряду; засады имеют ограниченную оценку будущего срабатывания до паса противника. Эти оценки не являются гарантированными очками догона.','',
 '## Подбор составов','',
 '640 партий: 16 вариантов по 40. Для каждого варианта 20 одинаковых seed и обе стороны. Старый и новый состав играют друг против друга одной и той же замороженной версией ИИ (strength 4, damp 40). Это подбор вариантов на одном наборе условий, а не независимое подтверждение общего роста силы или баланс всех 46 колод. Небольшая разница побед может быть случайной.','',
 '| Колода | Убрано | Добавлено | Победы / поражения / ничьи нового | В итоговом составе |',
 '|---|---|---|---|---|']
for row in sorted(rows,key=lambda r:(r['preset'],r['candidate'])):
    lines.append(f"| {row['preset']} | {row['remove']} | {row['add']} | {row['wins']} / {row['losses']} / {row['draws']} | {'да' if row['selected'] else 'нет'} |")
lines+=['','94: Последнее желание оставлено как исправление пустого Подкрепления. Прирост побед в этом сравнении **не подтверждён**. Альзур: Двойной крест также не превзошёл исходный состав.',
 '87: все четыре варианта с дополнительным золотом уступили исходному; замены отклонены, медик сохранён. Три золотые карты допустимы: четыре — максимум, не обязательный минимум.',
 '74: вместо предложенной Ирис выбрана Плотва. 83: сохранена Бурая Хоругвь, заменён только Охотник за ведьмами; теперь два Каэдвенских рыцаря.','',
 '## Разнообразие и защита данных','',
 '| Пресет | Новая колода |','|---|---|',
 '| 60 | Дагон: туман и утопцы |','| 76 | Филавандрель: эльфы и заклинания |',
 '| 77 | Радовид: броня и контроль |','| 95 | Узурпатор: имперский контроль |','',
 'У четырёх новых составов максимум 18 общих карт с любой другой колодой ИИ. Восемь полных пробных партий (обе стороны против пресета 54) завершились без ошибок; этого недостаточно для оценки их силы.',
 'Сохранены 46 профилей и их номера. Пресеты игрока/квестов 1–53 и Морозные призраки 80 защищены от этой правки. Перед применением замены проверяются исходный состав и лидер: неожиданная пользовательская правка вызывает остановку генератора вместо молчаливой перезаписи.',
 'Составы и стратегии: [AI_DECKS115_RU.md](D:/w3mod/docs/AI_DECKS115_RU.md). Редактируемые правки: [deck_patch128.json](D:/w3mod/data/beta924/ai/deck_patch128.json), [deck_variety128.json](D:/w3mod/data/beta924/ai/deck_variety128.json).','',
 '## Интерфейс и дальнейшая проверка','',
 '- Удержание LT: свой сброс; RT: своя колода; оба курка: сброс противника. Отпускание возвращает к незавершённому выбору.',
 '- Выбор способностей помещается на одну страницу: до трёх рядов; справа полный предпросмотр. Горизонтальный переход с края продолжает выбор на следующем/предыдущем ряду и зацикливается.',
 '- Исправлены история одинаковых карт, отдельные записи погоды и независимая пауза ИИ при уменьшенных эффектах.',
 '- Итоговые проверки исходников прошли: 50 проверок связок Фрингильи/Драйга/Сабрины, 12 проверок движков/Грома/засад, 45 проверок контроллера, 240 проверок интерфейсных продолжений и регрессии остальных карт. Лог: `BetaGwent/build/source-check128-final.log`.',
 '- Исходники синхронизированы с проектом REDkit без запуска компиляции. Итоговый снимок `decks128-final`: `70688d538a0760d8388a79f5931ca99d29eac5126fb65428764f31d29b10ecd0`.',
 '- Проверки исходников: `powershell -ExecutionPolicy Bypass -File D:\\w3mod\\tools\\Check-0.4.6.ps1`. Скрипт не собирает и не упаковывает мод.',
 '- Следующий этап: независимые seed и разные соперники для оценки баланса, затем проверка ощущения управления и визуальной компоновки в REDkit/обычной игре.']
(ROOT/'docs/decks128-review.md').write_text('\n'.join(lines)+'\n','utf-8')
print('640 paired games, 16 completed candidates; report docs/decks128-review.md')

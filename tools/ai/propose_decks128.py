"""Seed the editable, explicit deck revisions once. Does not build the mod."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / 'data/beta924/ai/deck_patch128.json'
if path.exists():
    raise SystemExit('Patch already exists; edit its JSON instead of overwriting it.')
research = json.loads((ROOT / 'data/beta924/ai/researched115.json').read_text('utf-8'))
profiles = {p['presetId']: p for p in research['profiles']}
changes = [
    (94, [123201], [113102], 'Убрать пустое Подкрепление; Последнее желание имеет цели, Наталис сохраняет Приказ о выступлении.'),
    (74, [113305, 132313, 132217], [200221, 112215, 201698], 'Заполнить 4 золотых и 6 серебряных: воскрешение Завещаний и поглощение сброса.'),
    (85, [112405, 132204], [200218, 200052], 'Шестая серебряная карта; Йотун и Голиаф поддерживают тему огроидов.'),
    (87, [162304], [162107], 'Четвёртое золото: Тибор как поздний финишер вместо одиночного медика.'),
    (89, [201704], [152106], 'Четвёртое золото: Лугос даёт целевой сброс и удаление.'),
    (69, [122212], [122209], 'Трололо вместо Неннеке: бронированное тело для колоды машин.'),
    (97, [122212], [122209], 'Трололо вместо Неннеке: броня и поддержка оруженосцев.'),
    (99, [122212], [122209], 'Трололо вместо Неннеке: броня и поддержка оруженосцев.'),
    (83, [200132, 122313], [201622, 201622], 'Три Каэдвенских рыцаря под вызов из колоды вместо карт без надёжных условий.'),
]
titles = {
    55: 'Вампиры: иссушение', 57: 'Машины Хенсельта', 58: 'Проклятие Адды',
    59: 'Темп Кальвейта', 61: 'Яйца и поглощение', 62: 'Засады и Огонь',
    64: 'Кровавая луна', 65: 'Ветераны Тиршаха', 66: 'Краснолюды, эльфы и Огонь',
    68: 'Мечники ан Крайт', 73: 'Мазь и пехота', 77: 'Усиление колоды Лирии',
    82: 'Брувер и Шуп', 83: 'Сорок карт Фольтеста', 84: 'Шахтёры и Ксавьер',
    88: 'Усиление руки Нильфгаарда', 91: "Заклинания скоя'таэлей",
}
data = dict(schema=1, protectedPresets=list(range(1, 54))+[80],
    retainedCards={'54': [162205], '65': [152205], '58': [122206]},
    decks=[dict(presetId=i, expectedLeader=profiles[i]['leader'], expectedTemplateIds=profiles[i]['templateIds'], remove=remove, add=add, reason=reason)
           for i, remove, add, reason in changes],
    titles={str(i): title for i, title in titles.items()})
path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print('Created', path)

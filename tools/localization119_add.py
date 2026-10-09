"""Complete the English strings introduced by the researched rosters and previews."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
path=root/'data/beta924/design/english89.json'
dictionary=json.loads(path.read_text('utf8'))
dictionary.update({
    'Целей в области: ': 'Affected targets: ',
    'Погода: рядов ': 'Weather rows: ',
    'Выбран ряд для способности': 'Ability row selected',
    'Осталось выбрать: ': 'Selections remaining: ',
    ' · выбор обязателен': ' · selection required',
    ' · Осталось выбрать: ': ' · Selections remaining: ',
    'Аретуза: магический контроль Фольтеста': 'Aretuza: Foltest spell control',
    'Солдаты Эмгыра': "Emhyr's soldiers",
    'Бран: раны и мечники': 'Bran: wounds and Greatswords',
    'Солдаты и рыцари Фольтеста': "Foltest's soldiers and knights",
    'Харальд: дождь и топорники': 'Harald: rain and Axemen',
    'Фольтест: усиление колоды': 'Foltest: deck boosts',
})
names={
    'Шпионы':'Spies', 'Рой главоглазов':'Arachas Swarm',
    'Мороз Дикой Охоты':'Wild Hunt Frost', 'Алхимия':'Alchemy',
    'Накеры и поглощение':'Nekkers and Consume', 'Лирийские машины':'Lyrian machines',
    'Королевская гвардия':'Queensguard', 'Темерцы':'Temerians',
    'Вскрытие Морврана':'Morvran Reveal', 'Завещания':'Deathwish',
    'Сброс карт':'Discard', 'Обмены':'Swap', 'Ледяные тролли':'Ice Trolls',
    'Усиление руки Эитнэ':'Eithné hand boosts', 'Морозные призраки':'Frost Wraiths',
    'Усиление руки Францески':'Francesca hand boosts', 'Великаны и огры':'Giants and Ogres',
    'Броня':'Armour', 'Невольничья пехота':'Slave Infantry',
    'Проклятые корабли':'Cursed Ships', 'Усиление руки Брувера':'Brouver hand boosts',
    'Топорники':'Axemen', 'Дриады':'Dryads',
}
names.update({name:dictionary[name] for name in (
    'Аретуза: магический контроль Фольтеста','Солдаты Эмгыра','Бран: раны и мечники',
    'Солдаты и рыцари Фольтеста','Харальд: дождь и топорники','Фольтест: усиление колоды')})
missing=json.loads((root/'BetaGwent/build/stage119/en/untranslated.json').read_text('utf8'))
for name in missing:
    if name.startswith('ИИ · '): dictionary[name]='AI · '+names[name[len('ИИ · '):]]
    elif name.startswith('Исследованный состав Beta 0.9.24; '):
        dictionary[name]='Researched Beta 0.9.24 deck; '+name.split('; ',1)[1]
assert not (set(missing)-set(dictionary)), set(missing)-set(dictionary)
path.write_text(json.dumps(dictionary,ensure_ascii=False,indent=2)+'\n','utf8')
print('Translated',len(missing),'previously missing literals')

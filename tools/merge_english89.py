from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'data/beta924/design/english89.json'
lookup=json.loads(p.read_text('utf8'))
if not (ROOT/'BetaGwent/build/release89/translation-index.json').exists():
    print('Initial indexed import not present; use the checked-in english89.json.')
    raise SystemExit(0)
index=json.loads((ROOT/'BetaGwent/build/release89/translation-index.json').read_text('utf8'))
for line in (ROOT/'data/beta924/design/english89-indexed.txt').read_text('utf8').splitlines():
    if not line:continue
    i,text=line.split('|',1);lookup[index[int(i)]]=text.replace('\\n','\n')
lookup[index[146]]=index[146] # Optional Russian on-screen keyboard stays available.
names={'Талер':'Thaler','Ольгерд фон Эверек':'Olgierd von Everec','Ламберт':'Lambert','Хадко':'Haddy','Лодочник из Рудника':'Boatwright of Oreton','Граф Тибальт':'Count Tybalt','Вернон Роше':'Vernon Roche','Бернард Тулле':'Bernard Tulle','Кровавый Барон':'Bloody Baron','Сигизмунд Дийкстра':'Sigismund Dijkstra','Шани':'Shani','Главарь пуристов после турнира в Туссенте':'Purist leader after the Toussaint tournament','Золтан Хивай':'Zoltan Chivay','Финнеас':'Finneas','Сьюста':'Sjusta','Гремист':'Gremist','Лугос Безумный':'Madman Lugos','Мышовур':'Ermion','Крах ан Крайт':'Crach an Craite'}
lookup.update(names)
for value in index:
    if value.startswith('ИИ · '):lookup[value]=value.replace('ИИ · ','AI · ')
    elif value.startswith('Адаптация пользовательского deck_rules к строгой Beta 0.9.24. '):lookup[value]=value.replace('Адаптация пользовательского deck_rules к строгой Beta 0.9.24. ','User deck_rules adapted to strict Beta 0.9.24. ')
    elif 'Бочка у торговца в крепости Барона' in value or 'Победить: ' in value:
        prefix='Starter set. ' if value.startswith('Стартовый набор. ') else ''
        body=value.removeprefix('Стартовый набор. ')
        if body.startswith('Победить: '):
            name=body.removeprefix('Победить: ').split('. Также',1)[0]
            text=prefix+'Defeat: '+lookup.get(name,name)+". Also available from a keg at Crow's Perch."
        elif ';' in body:
            text=prefix+"Keg at Crow's Perch; one random card for each of the first four wins against an ordinary player/merchant. Some cards are also sold by merchants."
        else:text=prefix+"Keg from the merchant at Crow's Perch."
        lookup[value]=text
p.write_text(json.dumps(lookup,ensure_ascii=False,indent=2)+'\n','utf8')
print('English mappings:',len(lookup))

"""Generate starter decks and verified native deck-key assignments."""
import json
from pathlib import Path
from collections import Counter
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text(encoding='utf8'))
cards={t['templateId']:t for t in catalog['templates']}
loc=catalog['localization']['ru_ru']
path=ROOT/'data/beta924/duel/presets.json'
document=json.loads(path.read_text(encoding='utf8'))
starter_document=json.loads((ROOT/'data/beta924/design/starter_decks.json').read_text(encoding='utf8'))
starters=starter_document['decks']
assert len(starters)==5 and {p['id'] for p in starters}==set(range(16,21))
assert {p['faction'] for p in starters}=={2,4,8,16,32}
ai_presets=[p for p in document['presets'] if p.get('aiRulesProfile')]
document['presets']=[p for p in document['presets'] if p['id']<16]
for p in starters:
 ident,faction,leader,title=p['id'],p['faction'],p['leader'],p['title']
 ids=[c['templateId'] for c in p['cards'] for _ in range(c['copies'])]
 counts=Counter(ids)
 assert len(ids)==25 and all(cards[c]['fields']['FactionId'] in (1,faction) for c in ids)
 assert cards[leader]['fields']['Tier']==1 and cards[leader]['fields']['FactionId']==faction
 assert all(cards[c]['attributes']['Availability']=='1' and n <= (3 if cards[c]['fields']['Tier']==2 else 1) for c,n in counts.items())
 assert sum(n for c,n in counts.items() if cards[c]['fields']['Tier']==8)==4
 assert sum(n for c,n in counts.items() if cards[c]['fields']['Tier']==4)==6
 document['presets'].append(dict(id=ident,key='starter-'+str(faction),title='Стартовая · '+title,
  description='Стартовый состав по выбору игрока: 25 карт, четыре золотые, шесть серебряных. Недостающие копии добавляются в коллекцию.',
  faction=faction,leader=leader,templateIds=ids,starter=True,starterRevision=starter_document['revision']))
native_path=Path('D:/GOG Galaxy/Games/The Witcher 3 REDkit/r4data/gameplay/items/def_gwint_decks.xml')
native={e.attrib['name'] for e in ET.parse(native_path).iter('deck_collection')}
# Designed Beta rewards, keyed by the actual stock NPC deck names, not NPC guesses.
assignments=[
 ('Baron','Кровавый Барон',122101,6),('Roche','Вернон Роше',122102,21),
 ('Dijkstra','Сигизмунд Дийкстра',122105,6),('Zoltan','Золтан Хивай',142105,9),
 ('Lambert','Ламберт',200235,6),('Thaler','Талер',112103,8),
 ('VimmeVivaldi','Вимме Вивальди',200080,9),('ScoiaTrader','Торговец скоя’таэлей',142103,10),
 ('Stjepan','Степан',112106,8),('CrossroadsInnkeeper','Корчмарь на распутье',112108,1),
 ('Olivier','Оливер',112112,8),('BoatBuilder','Лодочник из Рудника',132102,1),
 ('CardProdigy','Хадко',131102,15),('Hermit','Старый мудрец',132103,2),
 ('Sjusta','Сьюста',142101,10),('Gremista','Гремист',152107,12),
 ('Crach','Крах ан Крайт',152101,14),('LugosTheMad','Лугос Безумный',152106,13),
 ('Mousesack','Мышовур',152103,12),('MarkizaSerenity','Маркиза Серенити',142104,10),
 ('Shani','Шани',122106,6),('Olgierd','Ольгерд фон Эверек',132215,1),
 ('Gambler','Борец за права животных',112107,1),('Halflings','Низушки на свадьбе',132107,1),
 ('CircusGwentAddict','Торговец бродячего цирка',200209,10),
 ('NKTournament','Бернард Тулле',201618,6),('NilfTournament','Саша',162104,8),
 ('ScoiaTournament','Финнеас',142102,11),('NMLTournament','Граф Тибальт',132104,15),
 ('NMLTournament2','Первый соперник турнира в Туссенте',132101,15),
 ('NilfTournament2','Второй соперник турнира в Туссенте',162103,8),
 ('SkelTournament2','Финалист турнира в Туссенте',152104,14),
 ('ScoiaTournament2','Главарь пуристов после турнира в Туссенте',142106,11),
]
# Roche's Blue Stripes get a dedicated composition now; advanced tactics remain deferred.
roche=[122102,201777,122103,112106,122211,122212,122208,122209,201748,112201]+[122301]*3+[122308]*3+[122310]*3+[122311]*3+[122307]*3
document['presets'].append(dict(id=21,key='roche-blue-stripes',title='Синие Полоски Роше',description='Фиксированная колода Вернона Роше. Синие Полоски, разведчики и темерские отряды.',faction=8,leader=200168,templateIds=roche))
records=[]
base_presets={p['id']:p for p in document['presets']}
signatures={tuple(sorted(roche))}
for key,name,gold,preset in assignments:
 assert key in native and cards[gold]['fields']['Tier']==8 and cards[gold]['attributes']['Availability']=='1'
 base=base_presets[preset];faction=base['faction'];ids=list(base['templateIds'])
 assert cards[gold]['fields']['FactionId'] in (1,faction)
 if key!='Roche':
  # Keep the underlying archetype and give every named opponent a fixed,
  # distinct list. One bronze replacement retains existing combo packages.
  if gold not in ids:
   previous=next((i for i in ids if cards[i]['fields']['Tier']==8),ids[0]);ids.remove(previous);ids.append(gold)
  candidates=sorted(t['templateId'] for t in cards.values() if t['attributes']['Availability']=='1'
    and t['fields']['Kind']==1 and t['fields']['Tier']==2 and t['fields']['Type']==4
    and t['fields']['FactionId']==faction and t['templateId'] not in ids)
  original=min((i for i in ids if cards[i]['fields']['Tier']==2 and cards[i]['fields']['Type']==4),key=lambda i:(cards[i]['fields']['Power'],i))
  candidates.sort(key=lambda i:(abs(cards[i]['fields']['Power']-cards[original]['fields']['Power']),i))
  for candidate in candidates:
   variant=list(ids);variant.remove(original);variant.append(candidate)
   if tuple(sorted(variant)) not in signatures:ids=variant;break
  else:raise RuntimeError('No unique legal NPC variation for '+key)
  signatures.add(tuple(sorted(ids)))
  ident=len(document['presets'])+1
  document['presets'].append(dict(id=ident,key='npc-'+key.lower(),title=name,
    description=base['description'],faction=faction,leader=base['leader'],templateIds=ids,npcDeck=key,basePreset=preset))
 else:ident=21
 counts=Counter(ids)
 assert len(ids)==25 and all(n <= (3 if cards[i]['fields']['Tier']==2 else 1) for i,n in counts.items())
 assert sum(n for i,n in counts.items() if cards[i]['fields']['Tier']==8)<=4
 assert sum(n for i,n in counts.items() if cards[i]['fields']['Tier']==4)<=6
 records.append(dict(deckName=key,character=name,goldTemplateId=gold,goldTitle=loc[str(gold)+'_name'],preset=ident,basePreset=preset))
assert len({r['goldTemplateId'] for r in records})==len(records)
assert all(p['id']==54+i for i,p in enumerate(ai_presets)), 'Regenerate AI rules after changing NPC identities'
document['presets'].extend(ai_presets)
path.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
target=ROOT/'data/beta924/design/npc_rewards.json'
target.write_text(json.dumps(dict(stage=83,source=str(native_path),assignments=records,
  ordinaryReward='One random collectible bronze or silver below its owned-copy cap on the first victory over each actual NPC.',
  questReward='Assigned gold, or300 crowns if already owned.',
  note='Designed Beta rewards and fixed unique lists. Four actual Tournament2 requests confirmed by native-tournament83.json; NKTournament2 exists in definitions but is not requested by this quest. Character roles identify the precise tournament stages; actor personal names not inferred. Advanced AI for variations deferred.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
lines=['// Generated by tools/build_progression.py; native names validated from stock XML.',
 f"function BetaGwentStarterRevision() : int {{ return {starter_document['revision']}; }}",
 'function BetaGwentStarterPreset(faction : int) : int {', '    switch(faction) {']
lines += [f"    case {p['faction']}: return {p['id']};" for p in starters]
lines+=['    default: return16;', '    }', '}',
 'function BetaGwentQuestGold(deck : name) : int {', '    switch(deck) {']
lines += [f"    case '{r['deckName']}': return {r['goldTemplateId']};" for r in records]
lines+=['    default: return0;', '    }','}',
 'function BetaGwentQuestPreset(deck : name) : int {','    switch(deck) {']
lines += [f"    case '{r['deckName']}': return {r['preset']};" for r in records]
lines+=['    default: return0;', '    }','}']
(ROOT/'BetaGwent/development/scripts/game/betagwent/progressionCatalog.ws').write_text('\n'.join(lines).replace('return16','return 16').replace('return0','return 0')+'\n',encoding='utf8')
print(f'Five25-card starters; {len(records)} distinct named NPC decks/rewards; Toussaint forced-Skellige flow assigned; {len(document["presets"])} presets.')

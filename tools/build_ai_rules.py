"""Import user archetypes and generate legal Beta decks and deterministic AI tables.

No fuzzy name matching: aliases and role substitutions are explicit and audited.
Run after build_progression.py, before build_duel_catalog.py.
"""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from ws_codegen import bounded_helpers

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8-sig'))
def norm(text):
    return re.sub(r'[^a-zа-я0-9]', '', ''.join(c for c in unicodedata.normalize('NFKD', text.lower().replace('ё','е')) if not unicodedata.combining(c)))

catalog = read('data/beta924/normalized/catalog.json')
full = {c['templateId']: c for c in read('data/beta924/planning/full_catalog.json')['cards']}
names = {norm(catalog['localization'][lang][str(i)+'_name']): i for i in full for lang in ('en_us','ru_ru')}
english = {i: catalog['localization']['en_us'][str(i)+'_name'] for i in full}
aliases = {
    'Urygheff': 'Vrygheff', 'Vryhedd Officer': 'Vrihedd Officer', 'Uran Warrior':'Vran Warrior',
    'Vahnemar':'Vanhemar', 'Vandermar':'Vaedermakar', 'Griffins':'Griffin', 'Fog':'Impenetrable Fog',
    'She-Troll':'She-Troll of Vergen', 'Dao':"D'ao", 'Roche':'Vernon Roche',
    'Branen':'Braenn', 'Germant':'Germain Piquant', 'Eibhear Hattori':'Éibhear Hattori',
    'Isengrim: Faoiltiarna':'Isengrim Faoiltiarna', 'Urihedo Sappers':'Vrihedd Sappers',
    'Urihedo Brigade':'Vrihedd Brigade', 'Urihedo Dragoon':'Vrihedd Dragoon',
    'Urihedo Officer':'Vrihedd Officer', 'Urihedo Neophyte':'Vrihedd Neophyte',
    'Urihedo Vanguard':'Vrihedd Vanguard', 'Trapper':'Dol Blathanna Bomber',
    'Scout':'Reconnaissance', 'Роач':'Roach', 'Морвран Воорхис':'Morvran Voorhis',
}
# Similar roles, NOT new DIY abilities. The report preserves both names.
substitutions = {
    'Detlaff: Higher Vampire':'Regis: Higher Vampire', 'Lady of the Lake: Advent':"Avallac'h: Sage",
    'Count Caldwell':'False Ciri', 'Azar Javed':'Menno Coehoorn', 'Orianna':'Imlerith: Sabbath',
    'Detlaff: Crimson Curse':'Ragh Nar Roog', 'Colossal Ifrit':'Ifrit', 'Katakan':'Nekurat',
    'Gael':'Nekurat', 'Protofleder':'Wyvern', 'Fleder':'Ekimmara', 'Garkain':'Ancient Foglet',
    'Plumard':'Lamia', 'Kikimore Worker':'Arachas Behemoth', 'Natural Selection':'Arachas Venom',
    'Imperial Cavalry':'Kaedweni Cavalry', 'Feign Death':'Decoy', 'Hammond':'Hjalmar an Craite',
    'Knickers':'Roach', 'Coen of Povis':'Iorveth', 'Lyrian Cavalry':'Kaedweni Cavalry',
    'Meve':'Keira Metz', 'Knut the Callous':'Djenge Frett', 'Drummond Pillager':'Drummond Warmonger',
    'Terror Crew':'An Craite Warrior', 'Endrega Eggs':'Celaeno Harpy', 'Sukrus':'Holger Blackhand',
    'An Craite Warlord':'An Craite Warrior', 'Vernossiel':'Iorveth',
    'Vernossiel’s Commando':'Vrihedd Brigade', 'Vissgerd':'Vernon Roche', 'Reavers':'Reaver Hunter',
    'Cloud Giant':'Ice Giant', 'Cave Troll':'Ice Troll', 'Red Rider':'Wild Hunt Rider',
    'Nekker Swarm':'Nekker', 'The Apiarian Phantom':'Nithral', 'Quen':'Thunderbolt',
    'Shupe’s Bizarre Adventure':"Shupe's Day Off", 'Temerian Magus':'Tormented Mage',
    'Zoltan’s Company':'Zoltan: Scoundrel', 'Dwarf Miner':'Mahakam Guard', 'Giant’s Belt':'Mandrake',
    'Ogre Warrior':'Fiend', 'Palmerin de Launfal':'Vreemde', 'Sigvald':'Blueboy Lugos',
    'Svalblod Ravager':'Berserker Marauder', 'Carlo Varese':'Sheldon Skaggs', 'Magic Lamp':"Uma's Curse",
    'White Raffard’s Decoction':'Swallow', 'Giga Scorpion Decoction':"Alzur's Thunder",
    'Urihedo Saboteur':'Dol Blathanna Sentry', 'Dryad Grovekeeper':'Hawker Healer',
    'Ozak':'Éibhear Hattori', 'Frexienet':'Isengrim Faoiltiarna', 'Etienne':'Aglaïs',
    'Noonwraith':'Rotfiend', 'Highwaymen':'Alba Pikeman',
    'Cintrian Royal Guard':'Kaedweni Knight', 'Mystics':'Aretuza Adept',
}
aliases = {norm(k): norm(v) for k,v in aliases.items()}
substitutions = {norm(k): norm(v) for k,v in substitutions.items()}
def resolve(text):
    key = norm(text)
    if key in names: return names[key], 'exact'
    if key in aliases and aliases[key] in names: return names[aliases[key]], 'alias'
    if key in substitutions and substitutions[key] in names: return names[substitutions[key]], 'role-substitution'
    return None, 'unresolved'
def card(text):
    ident, _ = resolve(text)
    if ident is None: raise ValueError('Unknown AI table card: '+text)
    return ident

# family names describe actual Beta mechanisms, not the DIY numbers in the file.
configs = [
 ('spies',8),('drain',3),('swarm',4),('machines',6),('cursed',6),('reveal',7),
 ('weather',15),('consume',3),('ambush',11),('skip',0),('alchemy',7),('skip',0),
 ('moonlight',4),('veterans',12),('dwarves',9),('consume',3),('greatswords',14),
 ('machines',6),('queensguard',13),('temerians',17),('reveal',7),('soldiers',8),
 ('deathwish',3),('discard',13),('swap',10),('temerians',17),('tall',5),
 ('handbuff',10),('weather',15),('handbuff',10),('singleton',11),('temerians',17),
 ('skip',0),('dwarves',9),('tall',3),('armor',6),('soldiers',8),('ng-handbuff',7),
 ('greatswords',14),('handbuff',10),('spells',10),('skip',0),('skip',0),('skip',0),
 ('axemen',14),('dryads',11),
]
families = {name:i+1 for i,name in enumerate(dict.fromkeys(name for name,_ in configs if name!='skip'))}
path = ROOT/'data/beta924/duel/presets.json'
document = read(path)
base = [p for p in document['presets'] if not p.get('aiRulesProfile')]
assert len(base)==53, 'Original starter/NPC identities must remain stable'
base_by_id = {p['id']:p for p in base}
raw = (ROOT/'deck_rules.txt').read_bytes()
blocks = re.split(r'(?m)^\s*Архетип:\s*',raw.decode('utf-8-sig'))[1:]
assert len(blocks)==len(configs)
profiles=[]
for number,(block,(family,base_id)) in enumerate(zip(blocks,configs),1):
    lines=block.splitlines(); title=lines[0].strip()
    leader_text=next(x.split(':',1)[1].strip() for x in lines if x.strip().startswith('Лидер:'))
    primary=re.split(r'\s*\(',leader_text)[0].strip()
    leader,status=resolve(primary)
    profile=dict(id=number,title=title,requestedLeader=leader_text,sourceText=block.strip(),family=family,notes=[],changes=[])
    if family=='skip' or leader is None or not full[leader]['leader']:
        profile.update(active=False,reason='Primary leader is absent from strict Beta 0.9.24')
        profiles.append(profile); continue
    faction=full[leader]['faction']; roster=[]
    start=next(j+1 for j,x in enumerate(lines) if 'Состав колоды' in x)
    stop=next((j for j in range(start,len(lines)) if re.match(r'\s*(Основной план|Муллиган)\b',lines[j])),len(lines))
    for line in lines[start:stop]:
        text=line.strip()
        if not text: continue
        count=1
        match=re.search(r'\s+x(\d+)\s*$',text,re.I)
        if match: count=int(match[1]);text=text[:match.start()]
        # English lists prefix card power, not copies. Frost has explicit Russian copy counts.
        text=re.sub(r'^\d+\s+','',text)
        ident,how=resolve(text)
        change=dict(requested=line.strip(),resolvedId=ident,method=how)
        if ident is None or full[ident]['faction'] not in (1,faction) or full[ident]['leader']:
            change['rejectedResolvedId']=ident;change['resolvedId']=None
            change['method']='fill-from-archetype';profile['changes'].append(change);continue
        if how!='exact':change['resolvedName']=english[ident];profile['changes'].append(change)
        roster.extend([ident]*min(count,3))
    if number in (6,7):
        roster=list(base_by_id[base_id]['templateIds'])
        profile['notes'].append('Use validated Beta base list: requested roster has foreign-faction cards or DIY-only frost mechanics.')
    if family=='alchemy':
        # This source accidentally repeats Reveal's list; the prose explicitly describes witcher/alchemy chains.
        roster=[card(n) for n in ['Viper Witcher']]*3+[card(n) for n in ['Vicovaro Novice']]*3+[
            card(n) for n in ['Ointment','Swallow',"Alzur's Thunder"] for _ in range(3)]+[
            card(n) for n in ['Vesemir: Mentor','Triss: Telekinesis',"Yennefer: Enchantress",'Royal Decree','Cantarella','Assire var Anahid','Peter Saar Gwynleve',"Alzur's Double-Cross",'Mandrake','The Last Wish']]
        profile['notes'].append('Alchemy prose takes precedence over copied Reveal roster; Alzur Thunder is control, not an alchemy card.')
    target=40 if number==32 else 25
    singleton=family=='singleton'; selected=[]; counts=Counter(); tiers=Counter()
    def add(ident):
        c=full[ident];tier=c['tier']
        if c['faction'] not in (1,faction) or c['leader'] or len(selected)>=target: return False
        if counts[ident]>=(1 if singleton or tier!=2 else 3): return False
        if tier in (4,8) and tiers[tier]>=(6 if tier==4 else 4): return False
        selected.append(ident);counts[ident]+=1;tiers[tier]+=1;return True
    # Preserve requested rarity slots; never silently treat a power prefix as six copies.
    for ident in sorted(roster,key=lambda i: -full[i]['tier']):
        if not add(ident): profile['changes'].append(dict(requested=english[ident],resolvedId=ident,method='excluded-copy-tier-or-deck-limit'))
    pool=list(base_by_id[base_id]['templateIds'])
    # Fill incomplete textual lists using the existing archetype, then same-faction bronze units.
    pool += [i for i,c in full.items() if c['faction']==faction and c['tier']==2 and c['typeMask']==4]
    for ident in pool:
        if len(selected)>=target:break
        if add(ident):profile['changes'].append(dict(requested='Unfilled roster slot',resolvedId=ident,resolvedName=english[ident],method='archetype-fill'))
    if len(selected)<target:
        for ident,c in full.items():
            if len(selected)>=target:break
            if c['faction']==1 and c['tier']==2 and c['typeMask']==4 and add(ident):
                profile['changes'].append(dict(requested='Unfilled singleton slot',resolvedId=ident,resolvedName=english[ident],method='archetype-fill'))
    assert len(selected)==target
    preset_id=len(base)+1
    base.append(dict(id=preset_id,key=f'ai-rules-{number}',title='ИИ · '+title,
        description='Адаптация пользовательского deck_rules к строгой Beta 0.9.24. '+family,
        faction=faction,leader=leader,templateIds=selected,aiRulesProfile=number))
    profile.update(active=True,leader=leader,faction=faction,familyId=families[family],presetId=preset_id,templateIds=selected)
    profiles.append(profile)

# Author-approved replacements take precedence over the adapted DIY rosters.
# Copy from the canonical preset, never from hidden player zones during a match.
overrides = read('data/beta924/ai/deck_overrides.json')
assert overrides['schema'] == 1
for override in overrides['profiles']:
    profile = next(p for p in profiles if p['id'] == override['profileId'])
    assert profile['active']
    source = base_by_id[override['copyPresetId']]
    preset = next(p for p in base if p['id'] == profile['presetId'])
    assert source['faction'] == profile['faction'], 'Deck override must retain its faction'
    preset['leader'] = profile['leader'] = source['leader']
    preset['templateIds'] = list(source['templateIds'])
    profile['templateIds'] = list(source['templateIds'])
    profile['changes'] = [dict(requested=profile['title'], resolvedName=source['title'], method='author-approved-preset-copy', sourcePresetId=source['id'])]
    profile['notes'] = [override['reason']]
    profile['rosterOverride'] = override

# The reviewed proposal supersedes the original DIY adaptation and old roster
# overrides. Original presets 1..53 and established AI identities 54..93 stay put.
research = read('data/beta924/ai/researched115.json')
assert research['schema'] == 1 and len(research['profiles']) == 46
assert research['sourceSha256'] == hashlib.sha256((ROOT/research['source']).read_bytes()).hexdigest(), 'Re-import the edited proposal explicitly before building'
beta_titles = {
    10: 'Аретуза: магический контроль Фольтеста',
    12: 'Солдаты Эмгыра',
    33: 'Бран: раны и мечники',
    42: 'Солдаты и рыцари Фольтеста',
    43: 'Харальд: дождь и топорники',
    44: 'Фольтест: усиление колоды',
}
for proposed in research['profiles']:
    profile = next(p for p in profiles if p['id'] == proposed['id'])
    family = proposed['family'] or profile['family']
    display_title = beta_titles.get(profile['id'], proposed['title'])
    assert family in families, family
    selected = list(proposed['templateIds'])
    leader = proposed['leader']; faction = proposed['faction']
    counts = Counter(selected); tiers = Counter(full[i]['tier'] for i in selected)
    assert len(selected) == (40 if profile['id'] == 32 else 25)
    assert full[leader]['leader'] and full[leader]['faction'] == faction
    assert tiers[8] <= 4 and tiers[4] <= 6
    assert all(not full[i]['leader'] and full[i]['faction'] in (1,faction) and n <= (3 if full[i]['tier']==2 else 1) for i,n in counts.items())
    if family == 'singleton': assert len(counts) == len(selected)
    preset = next((p for p in base if p['id'] == proposed['presetId']), None)
    if preset is None:
        preset = dict(id=proposed['presetId'], key=f'ai-rules-{profile["id"]}', aiRulesProfile=profile['id'])
        base.append(preset)
    assert preset['aiRulesProfile'] == profile['id']
    preset.update(title='ИИ · '+display_title, description='Исследованный состав Beta 0.9.24; '+family,
                  faction=faction,leader=leader,templateIds=selected)
    profile.pop('reason',None);profile.pop('rosterOverride',None)
    profile.update(active=True,title=display_title,family=family,familyId=families[family],
                   leader=leader,faction=faction,presetId=preset['id'],templateIds=selected,
                   passPolicy=proposed['passPolicy'],strategy=proposed['strategy'],
                   notes=['Approved researched Beta proposal; exact roster, no automatic fillers.'],
                   changes=[dict(requested=proposed['title'],resolvedName='Точный состав из исследованного документа',method='author-researched-roster',sourceSection=proposed['sourceSection'])])
base.sort(key=lambda p:p['id'])
assert [p['id'] for p in base] == list(range(1,100))

# Explicit legal combo dependencies shared by all decks, including named NPC variants.
combo_names = [
 ('Impera Enforcers',['Ambassador','Emissary','Joachim de Wett','Assassin'],3),
 ('Mangonel',['Alchemist','Vattier de Rideaux','Nilfgaardian Knight'],3),
 ('Standard Bearer',['Slave Infantry','Recruit','Alba Armored Cavalry'],3),
 ('Alba Armored Cavalry',['Slave Infantry','Recruit','Emissary'],2),
 ('Siege Support',['Ballista','Reinforced Ballista','Battering Ram','Siege Tower','Trebuchet'],2),
 ('Ballista',['Siege Master'],3),('Reinforced Ballista',['Siege Master'],3),('Battering Ram',['Siege Master'],3),
 ('Cursed Knight',['Damned Sorceress'],3),('Kaedweni Revenant',['Tormented Mage','Bloody Flail'],2),
 ('Vrihedd Dragoon',['Elven Swordmaster','Vrihedd Neophyte'],3),
 ('Hawker Smuggler',['Dol Blathanna Archer','Half-Elf Hunter'],2),
 ('Farseer',['Hawker Support','Hawker Healer','Vrihedd Neophyte'],2),
 ('Dol Blathanna Sentry',['Elven Mercenary','Reconnaissance','Swallow',"Alzur's Thunder"],2),
 ('Yarpen Zigrin',['Dwarven Agitator','Mahakam Volunteers','Dwarven Mercenary'],2),
 ('Tuirseach Veteran',['Tuirseach Hunter','Tuirseach Bearmaster','Tuirseach Skirmisher'],3),
 ('An Craite Greatsword',['Dimun Light Longship'],3),('Tuirseach Axeman',['Dimun Warship','An Craite Whaler','Birna Bran'],3),
 ('An Craite Longship',['Drummond Warmonger','Ermion','Svanrige Tuirseach'],3),
 ('Nekker',['Forktail','Vran Warrior','Kayran'],3),('Arachas Behemoth',['Forktail','Vran Warrior','Kayran'],3),
 ('Celaeno Harpy',['Vran Warrior','Forktail','Cyclops'],3),
 ("D'ao",['Griffin','Cyclops'],3),('Rotfiend',['Griffin','Cyclops'],2),
 ('Wild Hunt Drakkar',['Wild Hunt Hound','Wild Hunt Rider','Wild Hunt Warrior','Wild Hunt Navigator'],2),
]
combos=[dict(setup=card(setup),payoff=card(payoff),weight=weight) for setup,payoffs,weight in combo_names for payoff in payoffs]
engines={card(n):w for n,w in [
 ('Impera Enforcers',2),('Mangonel',2),('Standard Bearer',2),('Alba Armored Cavalry',1),
 ('Siege Support',2),('Redanian Knight-Elect',2),('Reinforced Trebuchet',1),('Vrihedd Dragoon',1),
 ('Hawker Smuggler',1),('Farseer',2),('Yarpen Zigrin',1),('An Craite Greatsword',2),
 ('Dimun Light Longship',2),('An Craite Longship',2),('Tuirseach Axeman',2),('Savage Bear',1),
 ('Derran',1),('Nekker',1),('Arachas Behemoth',2),('Vran Warrior',2),('Wild Hunt Drakkar',1),
 ('Imlerith: Sabbath',4),('Ancient Foglet',1),('Reaver Hunter',2)]}
finishers=[card(n) for n in ['Geralt: Igni','Scorch','Schirrú','Sigismund Dijkstra','Mourntart','Old Speartip','Saesenthessis','Coral','Regis: Higher Vampire','Cerys an Craite']]
resurrectors=[card(n) for n in ['Priestess of Freya','Sigrdrifa','Restore','Dimun Corsair','Vicovaro Medic','Ointment','Paulie Dahlberg','Éibhear Hattori']]
document['presets']=base
path.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dest=ROOT/'data/beta924/ai';dest.mkdir(exist_ok=True)
report=dict(stage=115,source=research['source'],sourceSha256=research['sourceSha256'],families=families,
    profiles=profiles,combos=combos,engineWeights=engines,finishers=finishers,resurrectors=resurrectors,
    limitation='Exact researched Beta rosters. Strategy text is retained alongside executable conditional rules; historical DIY abilities are not introduced.')
(dest/'rules.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['// Generated from researched115.json by tools/build_ai_rules.py. No player private zones.',
    'struct SBetaGwentAICombo { var setup, payoff, weight : int; }',
    'function BetaGwentAICombos(out pairs : array<SBetaGwentAICombo>) {', '    var p : SBetaGwentAICombo; pairs.Clear();']
for p in combos: lines.append(f'    p.setup={p["setup"]};p.payoff={p["payoff"]};p.weight={p["weight"]};pairs.PushBack(p);')
lines+=['}']
def table(name,entries,result='int',default='0'):
    lines.extend([f'function {name}(id : int) : {result} {{','    switch(id) {'])
    lines.extend(f'    case {i}: return {value};' for i,value in entries)
    lines.extend([f'    default: return {default};','    }','}'])
table('BetaGwentAIEngine',engines.items())
table('BetaGwentAIFinisher',[(i,'true') for i in finishers],'bool','false')
table('BetaGwentAIResurrector',[(i,'true') for i in resurrectors],'bool','false')
active=[p for p in profiles if p['active']]
table('BetaGwentAIProfileFamily',[(p['id'],p['familyId']) for p in active])
table('BetaGwentAIPresetProfile',[(p['presetId'],p['id']) for p in active])
table('BetaGwentAIProfileLeader',[(p['id'],p['leader']) for p in active])
table('BetaGwentAIProfileLongRound',[(p['id'],'true') for p in active if p['passPolicy']=='L'],'bool','false')
lines+=['function BetaGwentAIProfileTitle(id : int) : string {','    switch(id) {']
lines += [f'    case {p["id"]}: return {json.dumps(p["title"],ensure_ascii=False)};' for p in active]
lines += ['    default: return "Общая стратегия";','    }','}']
lines+=['function BetaGwentAIProfileIds(out ids : array<int>) {','    ids.Clear();']+[f'    ids.PushBack({p["id"]});' for p in active]+['}']
# Scoring a known AI's own deck against requested profiles never inspects the user's deck.
lines+=['function BetaGwentAIProfileDeck(id : int, out ids : array<int>) : bool {','    switch(id) {']
lines += [f'    case {p["id"]}: return BetaGwentDuelPresetDeck({p["presetId"]},ids);' for p in active]
lines += ['    default: ids.Clear();return false;','    }','}']
lines+=['function BetaGwentAIRandomPreset() : int {', '    return BetaGwentAIChooseOrdinaryPreset();', '}']
(ROOT/'BetaGwent/development/scripts/game/betagwent/duelAICatalog.ws').write_text('\n'.join(bounded_helpers(lines))+'\n',encoding='utf-8-sig')
md=['# Адаптация deck_rules: этап88','',f'Источник: SHA-256 `{report["sourceSha256"]}`.',
    '',f'Активны {len(active)} из {len(profiles)} профилей. Шесть отсутствующих лидеров заменены согласованными Beta-адаптациями.',
    'Способности замен сохраняются из Beta0.9.24; замена роли не переносит способность DIY.',
    'Пресеты1–53, стартовые колоды и квестовые награды сохранены.', '',
    '| № | Архетип | Пресет | Изменения состава |','|---|---|---|---|']
for p in profiles:md.append(f'| {p["id"]} | {p["title"]} | {p.get("presetId","пропущен")} | {len(p["changes"])} |')
for p in active:
    md+=['',f'## {p["id"]}. {p["title"]}','']+p['notes']
    for x in p['changes']:md.append('- '+x['requested']+' → '+x.get('resolvedName',english.get(x.get('resolvedId'),'дополнение базовым архетипом'))+' ('+x['method']+').')
(ROOT/'docs/ai_rules88_adaptation.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(f'Imported46 profiles, active{len(active)}, presets{len(base)}, combos{len(combos)}. Source retained in data/beta924/ai/rules.json.')

from build_ai_tuning95 import main as build_tuning
build_tuning()

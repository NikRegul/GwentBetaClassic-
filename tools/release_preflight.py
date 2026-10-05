"""Audit the REDkit build inputs without publishing or touching the installed game.

Creates a content-hashed manifest, not an installable mod. Licensed Wwise project,
original game files and audio extraction are excluded from the input set.
"""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import json
import sqlite3
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'GwentB/myproject1'
WORK=PROJECT/'workspace'
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stage',type=int,choices=[86,87,88],default=88)
args=parser.parse_args()

def read(path):return json.loads((ROOT/path).read_text('utf-8'))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

presets=read('data/beta924/duel/presets.json')['presets']
starters=[p for p in presets if p.get('starter')]
assert len(starters)==5 and len({p['faction'] for p in starters})==5
catalog=read('data/beta924/normalized/catalog.json')
cards={t['templateId']:t for t in catalog['templates']}
starter_document=read('data/beta924/design/starter_decks.json')
expected={p['id']:p for p in starter_document['decks']}
for p in starters:
    source=expected[p['id']]
    assert p['leader']==source['leader'] and p['faction']==source['faction']
    assert Counter(p['templateIds'])==Counter({c['templateId']:c['copies'] for c in source['cards']})
    assert sum(cards[c]['fields']['Tier']==8 for c in p['templateIds'])==4
    assert sum(cards[c]['fields']['Tier']==4 for c in p['templateIds'])==6
rewards=read('data/beta924/design/npc_rewards.json')['assignments']
assert len({r['deckName'] for r in rewards})==len(rewards)
assert len({r['goldTemplateId'] for r in rewards})==len(rewards)
assert all(cards[r['goldTemplateId']]['fields']['Tier']==8 for r in rewards)
by_preset={p['id']:p for p in presets}
assert len(rewards)==33 and len(presets)==(93 if args.stage>=88 else 53)
assert len({r['preset'] for r in rewards})==len(rewards)
assert len({tuple(sorted(by_preset[r['preset']]['templateIds'])) for r in rewards})==len(rewards)
for p in presets:
    counts=Counter(p['templateIds'])
    assert 25<=len(p['templateIds'])<=40
    assert all(cards[c]['fields']['FactionId'] in (1,p['faction']) for c in counts)
    assert all(n <= (3 if cards[c]['fields']['Tier']==2 else 1) for c,n in counts.items())
    assert sum(n for c,n in counts.items() if cards[c]['fields']['Tier']==8)<=4
    assert sum(n for c,n in counts.items() if cards[c]['fields']['Tier']==4)<=6
for r in rewards:assert r['goldTemplateId'] in by_preset[r['preset']]['templateIds']
tournament=read('docs/evidence/native-tournament83.json')
assert digest(Path(tournament['source']))==tournament['sha256']
assert {g['deck'] for g in tournament['minigames']}=={'NMLTournament2','NilfTournament2','SkelTournament2','ScoiaTournament2'}
assert all(g['forcedFaction']=='GwintFaction_Skellige' for g in tournament['minigames'])
assert {g['deck'] for g in tournament['minigames']} <= {r['deckName'] for r in rewards}
full=read('data/beta924/planning/full_catalog.json')
assert len(full['cards'])==479 and sum(c['leader'] for c in full['cards'])==21
generated=(WORK/'scripts/game/betagwent/duelCatalog.ws').read_text(encoding='utf-8-sig')
total=re.search(r'function BetaGwentCollectionTotal\(faction : int\) : int.*?\n}',generated,re.S)
assert total and re.search(r'case 0:\s*return 479;',total.group())
shop=read('data/beta924/design/shop_cards.json')
assert all(cards[r['templateId']]['fields']['Tier'] in (2,4) for r in shop['mappings'])
assert all(digest(Path(path))==sha for path,sha in shop['nativeSourcesUnchanged'].items())
definitions=ET.parse(WORK/'gameplay/items/betagwent_shop.xml')
names={e.get('name') for e in definitions.iter('item')}
assert next(e for e in definitions.iter('item') if e.get('name')=='betagwent_keg').get('stackable')=='999'
assert names=={r['betaItem'] for r in shop['mappings']}|{'betagwent_keg'}
for folder in ('items','items_plus'):
    tree=ET.parse(WORK/f'gameplay/{folder}/def_loot_shops.xml')
    merchant=next(e for e in tree.iter('loot') if e.get('name')=='_store__Barons_Quartermaster')
    kegs=[e for e in merchant.iter('loot_entry') if e.get('name')=='betagwent_keg']
    assert len(kegs)==1 and kegs[0].get('quantity_min')=='50' and kegs[0].get('quantity_max')=='50'
database=PROJECT/'LocalEditorStringDataBaseW3_UTF8_mod.db'
with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    for item in definitions.iter('item'):
        for field in ('localisation_key_name','localisation_key_description'):
            rows=db.execute('SELECT STRINGS.LANG FROM STRING_INFO JOIN STRINGS USING(STRING_ID) WHERE STRING_KEY=?',(item.get(field),)).fetchall()
            assert {r[0] for r in rows}=={2,9}
prepared=read('docs/evidence/board-native-preparation.json')
assert prepared['compile']['exitCode']==0 and not prepared['compile']['timedOut']
for source in prepared['activeSources']:assert digest(Path(source['path']))==source['sha256']
assert len(prepared['activeSources'])==(60 if args.stage>=88 else 58)
bridges={}
for entry,filename in [('BetaGwentBoard','board-bridge-bytecode.json'),('DeckBuilder','board-bridge-bytecode-DeckBuilder.json'),('GwintGame','board-bridge-bytecode-GwintGame.json')]:
    path=ROOT/'docs/evidence'/filename
    evidence=json.loads(path.read_text('utf8'));assert evidence['passed'];bridges[entry]=len(evidence['bindings'])
    assert bridges[entry]==44
    assert digest(Path(evidence['swf']))==evidence['sha256']
audio=read('docs/evidence/audio-import79.json')
bank=read('docs/evidence/audio-bank-build79.json')
assert digest(Path(bank['target']))==bank['sha256']
assert bank['installed'] and bank['exitCode']==0 and bank['embeddedMedia']==audio['mediaCount']>200 and audio['fullImport']
project=read('GwentB/myproject1/myproject1.w3edit')
paths=list((WORK/'scripts/game/betagwent').glob('*.ws'))
for folder in ('betagwent','gameplay','soundbanks'):
    paths.extend(p for p in (WORK/folder).rglob('*') if p.is_file() and p.suffix.lower() in {'.xml','.menu','.guiconfig','.redswf','.bnk','.csv'})
paths.extend([PROJECT/'myproject1.w3edit',database])
files=[dict(path=p.relative_to(PROJECT).as_posix(),bytes=p.stat().st_size,sha256=digest(p)) for p in sorted(set(paths))]
gates=[
    'Combined NPC/shop/quest/localization/round/save runtime acceptance remains pending.',
    'Accept one-of-each Beta Collect All Cards/Almanac, native reward tags and tournament admission in game.',
    'Accept four assigned Blood and Wine requests and review DLC inclusion; project currently excludes ep1/bob.',
    'Set release metadata, cook/publish in REDkit, export localization, then check the package in ordinary TW3.',
    'New Game Plus and existing saves need compatibility acceptance.'
]
gates.insert(0,'Accept expanded1418-media bank, animations/impact timing, empty opposing row frost with Caranthir on controller, I original descriptions and draft rename/save. Also accept outstanding controller/editor/keg stage85 scenarios. Individual AI archetypes follow test release.')
report=dict(stage=86,status='REDkit input preparation; not an installable game release',starterRevision=starter_document['revision'],starterDecks=len(starters),inventoryKegs=True,kegPriceCrowns=150,kegStock=50,controllerSupport=True,controllerRuntimeVerified=False,fullAudioRequiredForTestRelease=True,presets=len(presets),questAssignments=len(rewards),collectibles=479,leaders=21,collectionCompletion='one copy of every collectible and leader',toussaintRequests=4,shopMappings=len(shop['mappings']),localizationKeys=shop['localizationCount'],compiledSources=len(prepared['activeSources']),bridgeBindings=bridges,installedMedia=bank['embeddedMedia'],preparedFullMedia=audio['mediaCount'],runtimeVerified=False,readyForGameInstall=False,projectMetadata=project,releaseGates=gates,files=files,totalBytes=sum(f['bytes'] for f in files))
report['stage']=args.stage
if args.stage==87:report['releaseGates'].insert(0,'Stage87 controller action modes, LB/RB rows, L3 board inspection, editor trigger shortcuts and pane switching require runtime acceptance. Russian first alpha; English UI/audio follows the test release.')
if args.stage==88:
    report['releaseGates']=[g.replace('Individual AI archetypes follow test release.','Archetype battle acceptance remains pending.') for g in report['releaseGates']]
    report['releaseGates'].insert(0,'Stage88: forty adapted deck_rules profiles, combo ordering and actual Impera boost need native battle acceptance. Sixty sources compiled; user language translation remains deferred.')
out=ROOT/f'BetaGwent/build/release{args.stage}/input-manifest.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
(ROOT/f'docs/evidence/stage{args.stage}-release-preflight.json').write_text(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(manifest=str(out),files=len(files),totalBytes=report['totalBytes'],starters=5,questAssignments=len(rewards),shopMappings=len(shop['mappings']),installedMedia=bank['embeddedMedia'],preparedMedia=audio['mediaCount'],readyForGameInstall=False),ensure_ascii=False))

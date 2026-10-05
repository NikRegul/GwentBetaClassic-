"""Full read-only collection catalogue, independent of implemented/owned cards."""
from pathlib import Path
import json,hashlib,re,argparse
from ws_codegen import localized_plain_text
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--language',choices=['ru','en'],default='ru')
parser.add_argument('--output-dir',type=Path)
args=parser.parse_args()
UI_OUT=args.output_dir or ROOT/'BetaGwent/ui/src'
UI_OUT.mkdir(parents=True,exist_ok=True)
LOCALE='en_us' if args.language=='en' else 'ru_ru'
raw=(ROOT/'data/beta924/normalized/catalog.json').read_bytes()
digest=hashlib.sha256(raw).hexdigest()
if digest!='022539802636cb45e92123a630c3788a0674c39b538fa1f69a64761a6b3ddbd3':raise RuntimeError('Canonical source changed')
source=json.loads(raw)
done={c['templateId'] for c in json.loads((ROOT/'data/beta924/duel/slice.json').read_text(encoding='utf-8'))['cards']}
artpath=ROOT/'docs/evidence/card-art-build.json'
arts={c['templateId'] for c in json.loads(artpath.read_text(encoding='utf-8'))['cards']} if artpath.exists() else set()
def category_text(t):
    names=[]
    for word_index, word in enumerate(t['categoryWords']):
        mask=int(word['decimal'])
        for bit in range(64):
            if mask & (1 << bit):
                name=source['localization'][LOCALE].get('card_category_'+str(word_index*64+bit))
                if name:names.append(name)
    return ' · '.join(names)

tags={t['templateId']:category_text(t) for t in source['templates']}
# Keep categories available for internal units and ability choices too.
tag_lines=['package {','    public class BetaGwentCardTags {','        private static var values:Object;',
    '        public static function text(id:int):String {',
    '            if(!values){ values={};']
tag_items=[(ident,title) for ident,title in tags.items() if title]
for i in range(0,len(tag_items),60):tag_lines.append('                page'+str(i//60)+'();')
tag_lines+=['            }','            return values[id]||"";','        }']
for i in range(0,len(tag_items),60):
    tag_lines+=['        private static function page'+str(i//60)+'():void {']
    tag_lines+=[f'            values[{ident}]={json.dumps(title,ensure_ascii=False)};' for ident,title in tag_items[i:i+60]]
    tag_lines+=['        }']
tag_lines+=['    }','}']
(UI_OUT/'BetaGwentCardTags.as').write_text('\n'.join(tag_lines)+'\n',encoding='utf8')
presets=json.loads((ROOT/'data/beta924/duel/presets.json').read_text(encoding='utf8'))['presets']
starters={ident for p in presets if p.get('starter') for ident in p['templateIds']+[p['leader']]}
quest_records=json.loads((ROOT/'data/beta924/design/npc_rewards.json').read_text(encoding='utf8'))['assignments']
quest_sources={r['goldTemplateId']:r['character'] for r in quest_records}
def acquisition(ident,tier):
    if ident in quest_sources:return ('Победить: '+quest_sources[ident]+'. Также может выпасть из бочки у торговца в крепости Барона.',quest_sources[ident])
    if tier in (2,4):return ('Бочка у торговца в крепости Барона; случайная награда за первые четыре победы над обычным игроком/торговцем (по одной карте). Некоторые карты также продаются торговцами.','Бочка / случайный торговец')
    return ('Бочка у торговца в крепости Барона.','Бочка')
records=[]
def original_description(ident):
    values={}
    for g in source['abilities']:
        if g['type']!='CardAbility' or g['templateId']!=ident:continue
        for group in g['sourceTree']['children']:
            if group['tag'] not in ('TemporaryVariables','PersistentVariables'):continue
            for v in group['children']:
                a=v['attributes']
                if a.get('Type')=='IntVar':values[a['Name']]=a['V']
                elif a.get('Type')=='CardDefVar':
                    templates=[x['attributes']['TemplateId'] for x in v['children'] if 'TemplateId' in x['attributes']]
                    if templates:values[a['Name']]=source['localization'][LOCALE].get(templates[0]+'_name',templates[0])
    value=source['localization'][LOCALE].get(str(ident)+'_tooltip','')
    for key,replacement in values.items():value=value.replace('{'+key+'}',str(replacement))
    return localized_plain_text(value)

# Original rule text also exists for spawned units and ability choices.
keyword_defs={}
for key,value in source['localization'][LOCALE].items():
    if not key.startswith('keyword_'):continue
    plain=localized_plain_text(value)
    label=plain.split(':',1)[0]
    if ':' in plain:keyword_defs.setdefault(label,plain)
texts=[]
for t in source['templates']:
    ident=t['templateId'];description=original_description(ident)
    glossary=[definition for label,definition in keyword_defs.items()
              if re.search(r'(?<!\w)'+re.escape(label)+r'(?!\w)',description,re.I)]
    texts.append(dict(templateId=ident,description=description,
        flavor=localized_plain_text(source['localization'][LOCALE].get(str(ident)+'_fluff','')),
        glossary='\n\n'.join(glossary),power=t['fields']['Power'],typeMask=t['fields']['Type']))
lines=['package {','    public class BetaGwentCardText {','        private static var values:Object;',
       '        public static function find(id:int):Object {','            if(!values){ values={};']
for i in range(0,len(texts),25):lines.append(f'                page{i//25}();')
lines+=['            }','            return values[id];','        }']
for i in range(0,len(texts),25):
    lines.append(f'        private static function page{i//25}():void {{')
    for item in texts[i:i+25]:lines.append('            values['+str(item['templateId'])+']='+json.dumps(item,ensure_ascii=False,separators=(',',':'))+';')
    lines.append('        }')
lines+=['    }','}']
(UI_OUT/'BetaGwentCardText.as').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for t in source['templates']:
    f=t['fields']; ident=t['templateId']
    if t['attributes']['Availability']!='1' or f['Kind']!=1 or f['Tier'] not in (1,2,4,8):continue
    description=original_description(ident)
    how,short=acquisition(ident,f['Tier'])
    if ident in starters:how="Стартовый набор. "+how;short="Стартовый набор"
    records.append(dict(templateId=ident,title=source['localization'][LOCALE].get(str(ident)+'_name',str(ident)),
        description=description,tags=tags[ident],power=f['Power'],tier=f['Tier'],typeMask=f['Type'],faction=f['FactionId'],
        leader=f['Tier']==1,spy=f['Type']==4 and int(t['placement'].get('OpponentSide',0))!=0 and int(t['placement'].get('PlayerSide',0))==0,implemented=ident in done,hasArt=ident in arts,
        acquisition=how,acquisitionShort=short,acquisitionAssigned=True,owned=None,ownershipTracked=True))
records.sort(key=lambda c:(c['faction'],-c['tier'],c['title']))
document=dict(catalogSha256=digest,cards=records,count=len(records),
    policy='Every original Availability1/Kind1/Tier1,2,4,8/candidate, including Doomed; not filtered by owned status or implemented effects. Save-backed runtime ownership supplied over the bridge. Sources are assigned; NPC/shop/keg integration awaits runtime acceptance. DEV practice access is separate from ownership.')
target=UI_OUT/'full_catalog.json' if args.output_dir else ROOT/'data/beta924/planning/full_catalog.json';target.write_text(json.dumps(document,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Small initializers avoid a single giant AVM2 initializer and WScript lookup table.
lines=['package {','    public class BetaGwentFullCatalog {','        private static var cache:Array;', '        private static var byId:Object={};',
    '        public static function all():Array {','            if(cache)return cache;','            cache=[];']
chunks=[records[i:i+25] for i in range(0,len(records),25)]
for i in range(len(chunks)):lines.append(f'            cache=cache.concat(page{i}());')
lines+=['            for each(var card:Object in cache)byId[card.templateId]=card;', '            return cache;', '        }', '        public static function find(id:int):Object { all(); return byId[id]; }']
for i,chunk in enumerate(chunks):
    lines.append(f'        private static function page{i}():Array {{ return [')
    lines.append(',\n'.join('            '+json.dumps(c,ensure_ascii=False,separators=(',',':')) for c in chunk))
    lines.append('        ]; }')
lines+=['    }','}']
(UI_OUT/'BetaGwentFullCatalog.as').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Full catalogue:',len(records),'candidates; acquisition assigned; runtime acceptance pending.')

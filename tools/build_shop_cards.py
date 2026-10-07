"""Map stock shop inventory to Beta items; preserve native source files."""
from pathlib import Path
import json,re,sqlite3,hashlib,xml.etree.ElementTree as ET
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[1]
SDK=Path('D:/GOG Galaxy/Games/The Witcher 3 REDkit/r4data')
WORK=ROOT/'GwentB/myproject1/workspace'
c=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text(encoding='utf8'))
ts={t['templateId']:t for t in c['templates']};loc=c['localization']['ru_ru']
eligible=[t for t in ts.values() if t['attributes']['Availability']=='1' and t['fields']['Kind']==1 and t['fields']['Tier'] in (2,4)]
def norm(x):return re.sub('[^a-z0-9]','',x.lower())
aliases={'clear_sky':113303,'rain':113312,'fog':113305,'frost':113302,'horn':113207,'scorch':113309,'dummy':113201,
 'mushroom':113320,'skellige_storm':113203,'nekker':132305,'ekkima':132313,'fogling':132301,'arachas':132304,
 'crone_whispess':132206,'crone_weavess':132208,'crone_brewess':132207,'celaeno_harpy':132217,
 'earth_elemental':132213,'ice_giant':132212,'toad':132216,'black_archer':162312,'archer_support':162310,
 'impera_brigade':162307,'nausicaa':162309,'combat_engineer':162315,'young_emissary':162314,
 'blue_stripes':122311,'crinfrid':122306,'catapult':122315,'siege_tower':122304,'havekar_support':142312,
 'havekar_nurse':142301,'dol_infantry':142304,'dol_dwarf':142305,'dol_archer':142310,'vrihedd_cadet':142309,
 'elf_skirmisher':142316,'vrihedd_brigade':142302,'mahakam':142306,'vesemir':112203,'olgierd':112207,
 'cow':112209,'roach':112210,'clan_an_craite_warrior':152311,'clan_tordarroch_armorsmith':152302,
 'clan_heymaey_skald':152313,'clan_brokvar_archer':152304,'clan_drummond_shieldmaiden':152307,
 'clan_dimun_pirate':152303,'light_drakkar':152309,'war_drakkar':200105,'berserker':152306,'young_berserker':152306,
 'draig':152205,'holger_blackhand':152207,'donar_an_hindar':152204,'udalryk':152214,'blueboy_lugos':152203,
 'svanrige':152213,'mrmirror_foglet':132302,'plague_maiden':132202,'gargoyle':132213,'fire_elemental':132210}
native_cards=list(ET.parse(SDK/'gameplay/items/def_gwint_cards_final.xml').iter('card'))
factions={'F_NEUTRAL':1,'F_NORTHERN':8,'F_NILFGAARD':4,'F_SCOIATAEL':16,'F_MONSTERS':2,'F_SKELLIGE':32}
stock=list(ET.parse(SDK/'gameplay/items/def_item_gwint.xml').iter('item'))
records=[];items=ET.Element('redxml');defs=ET.SubElement(items,'definitions');itemroot=ET.SubElement(defs,'items')
strings=[]
for old in stock:
 name=old.get('name');stem=re.sub(r'\d+$','',name.removeprefix('gwint_card_'))
 native=next((x for x in native_cards if x.get('title')==old.get('localisation_key_name')),None)
 faction=factions.get(native.get('faction_index') if native is not None else '',1)
 if stem.startswith('emhyr'):faction=4
 elif stem.startswith('foltest'):faction=8
 elif stem.startswith('francesca'):faction=16
 elif stem.startswith('eredin'):faction=2
 elif stem.startswith('king_bran'):faction=32
 if stem in aliases:ident=aliases[stem];reason='explicit equivalent'
 else:
  matches=sorted(eligible,key=lambda t:SequenceMatcher(None,norm(stem),norm(t['attributes']['DebugName'])).ratio(),reverse=True)
  score=SequenceMatcher(None,norm(stem),norm(matches[0]['attributes']['DebugName'])).ratio()
  if score>=.76:ident=matches[0]['templateId'];reason='name equivalent'
  else:
   power=int(native.get('power','6')) if native is not None else 6
   choices=[t for t in eligible if t['fields']['FactionId']==faction and t['fields']['Type']==4]
   target=min(choices,key=lambda t:(abs(t['fields']['Power']-power),t['fields']['Tier']!=4,t['templateId']))
   ident=target['templateId'];reason='comparable unit of original faction; original hero/leader not sold as Beta gold'
 assert ident in ts and ts[ident]['fields']['Tier'] in (2,4)
 new='betagwent_shop_'+name.removeprefix('gwint_card_')
 title=loc[str(ident)+'_name'];key='bg_shop_'+name.removeprefix('gwint_card_')
 item=ET.SubElement(itemroot,'item',name=new,hold_slot='',equip_slot='',template='',stackable='20',ability_slots='0',category='misc',price=old.get('price','20'),icon_path=old.get('icon_path','icons/inventory/gwint/ico_gwent_weather_neutral.png'),localisation_key_name=key,localisation_key_description=key+'_desc')
 ET.SubElement(item,'tags').text='BetaGwentCard,EncumbranceOff,Lootable'
 strings += [(key,title),(key+'_desc','Карта Beta Gwent 0.9.24: '+title+'. Покупка пополняет коллекцию. Лимит: '+('3 копии.' if ts[ident]['fields']['Tier']==2 else '1 копия.'))]
 records.append(dict(legacyItem=name,betaItem=new,templateId=ident,title=title,reason=reason,price=int(old.get('price','20'))))
item=ET.SubElement(itemroot,'item',name='betagwent_keg',hold_slot='',equip_slot='',template='',stackable='999',ability_slots='0',category='misc',price='150',icon_path='icons/inventory/gwint/ico_gwent_weather_neutral.png',localisation_key_name='bg_keg_name',localisation_key_description='bg_keg_desc')
ET.SubElement(item,'tags').text='BetaGwentKeg,EncumbranceOff,Lootable'
strings += [('bg_keg_name','Бочка карт Beta Gwent'),('bg_keg_desc','150 крон. До четырёх недостающих бронзовых карт и выбор одной из трёх редких: серебро, золото или лидер. Если бронза исчерпана, выдаётся только редкий выбор за ту же цену. Можно купить несколько бочек сразу. В инвентаре выберите «Использовать», чтобы открыть одну. Редкий выбор сохраняется до подтверждения.')]
out=WORK/'gameplay/items/betagwent_shop.xml';out.parent.mkdir(parents=True,exist_ok=True);ET.indent(items);ET.ElementTree(items).write(out,encoding='utf8',xml_declaration=True)
source_hashes={}
for folder in ['items','items_plus']:
 original=SDK/('gameplay/'+folder+'/def_loot_shops.xml');raw=original.read_bytes();source_hashes[str(original)]=hashlib.sha256(raw).hexdigest()
 text=raw.decode('utf-8-sig');match=re.search(r'<loot name="_store__Barons_Quartermaster"[^>]*>',text)
 assert match
 text=text[:match.end()]+'\n        <loot_entry name="betagwent_keg" player_level_min="0" player_level_max="0" quantity_min="50" quantity_max="50" chance="-1" />'+text[match.end():]
 target=WORK/('gameplay/'+folder+'/def_loot_shops.xml');target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.read_bytes()!=raw and b'betagwent_keg' not in target.read_bytes():raise RuntimeError('Unexpected existing shop overlay')
 target.write_text(text,encoding='utf-8-sig')
# A transactional editor DB update; keep a snapshot and preserve all other rows.
database=ROOT/'GwentB/myproject1/LocalEditorStringDataBaseW3_UTF8_mod.db'
conn=sqlite3.connect(database);backup=ROOT/'BetaGwent/build/progression82/localization-before.db';backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():
 snapshot=sqlite3.connect(backup);conn.backup(snapshot);snapshot.close()
with conn:
 for key,text in strings:
  existing=conn.execute('SELECT STRING_ID FROM STRING_INFO WHERE STRING_KEY=?',(key,)).fetchone()
  if existing:ident=existing[0]
  else:
   ident=max(10000000,conn.execute('SELECT COALESCE(MAX(STRING_ID),0)+1 FROM STRING_INFO').fetchone()[0])
   conn.execute('INSERT INTO STRING_INFO(STRING_ID,RESOURCE,PROPERTY_NAME,STRING_KEY)VALUES(?,?,?,?)',(ident,'gameplay/items/betagwent_shop.xml','name' if not key.endswith('_desc') else 'description',key))
  for lang in [2,9]:
   conn.execute('DELETE FROM STRINGS WHERE STRING_ID=? AND LANG=?',(ident,lang))
   version=conn.execute('SELECT COALESCE(MAX(VERSION),0)+1 FROM STRINGS WHERE STRING_ID=?',(ident,)).fetchone()[0]
   conn.execute('INSERT INTO STRINGS(STRING_ID,LANG,VERSION,TEXT)VALUES(?,?,?,?)',(ident,lang,version,text))
conn.close()
lines=['// Generated shop conversion; original item definitions are not changed.']
for function,field in [('BetaGwentLegacyShopCard','legacyItem'),('BetaGwentShopCard','betaItem')]:
 groups=[records[i:i+40] for i in range(0,len(records),40)]
 lines += [f'function {function}(item : name) : int','{','    var id : int;']
 for i in range(len(groups)):lines += [f'    id={function}Part{i}(item);if(id!=0)return id;']
 lines += ['    return 0;','}']
 for i,group in enumerate(groups):
  lines += [f'function {function}Part{i}(item : name) : int','{','    switch(item) {']
  lines += [f"    case '{r[field]}': return {r['templateId']};" for r in group]+['    default: return 0;','    }','}']
groups=[records[i:i+40] for i in range(0,len(records),40)]
lines += ['function BetaGwentModernShopItem(item : name) : name','{','    var result : name;']
for i in range(len(groups)):lines += [f"    result=BetaGwentModernShopItemPart{i}(item);if(result!='')return result;"]
lines += ["    return '';",'}']
for i,group in enumerate(groups):
 lines += [f'function BetaGwentModernShopItemPart{i}(item : name) : name','{','    switch(item) {']
 lines += [f"    case '{r['legacyItem']}': return '{r['betaItem']}';" for r in group]+["    default: return '';",'    }','}']
(ROOT/'BetaGwent/development/scripts/game/betagwent/shopCatalog.ws').write_text('\n'.join(lines)+'\n',encoding='utf8')
report=dict(stage=83,mappings=records,nativeSourcesUnchanged=source_hashes,localizationCount=len(strings),merchant='Baron quartermaster, via original loot definition; existing inventories need restock',runtimeVerified=False)
(ROOT/'data/beta924/design/shop_cards.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(str(len(records))+' shop item mappings; '+str(len(strings))+' localization keys; Baron keg overlay ready.')

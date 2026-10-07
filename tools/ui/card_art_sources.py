"""Existing DIY art bindings only. Exact names resolve renumbered illustrations."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'LegacyGwent-diy(1)/LegacyGwent-diy/src/Cynthia.Card.Unity/src/Cynthia.Unity.Card/Assets/Addressables/Cards'
ALIASES={113401:'11330300',200307:'20005300',200158:'13110300',132310:'13231010',
    200008:'11332100',200023:'6010200',200519:'20044800',201657:'20153400',201744:'11340400',
    200530:'20023200',201643:'20151100',201645:'20143900',133301:'20154200',201656:'20150200',201704:'11340200',
    201562:'20022300',201563:'20022300',201702:'20159800',201703:'20159800',
    201709:'20163200',201710:'20163200',201768:'20163200',201711:'20163300',201712:'20163300',201746:'20006700',201747:'20006700'}
ALIASES.update({201666:'20022200',201667:'20022200',201719:'20162100',201720:'20162100',201721:'20169700',201722:'20169700'})
ALIASES.update({201694:'20160300',201695:'20160300',201713:'20154000',201714:'20154000',201672:'20153700',201673:'20153700'})
ALIASES.update({201715:'20161500',201716:'20161500'})
ALIASES.update({152318:'15231810',201627:'20027500'})
ALIASES.update({201717: '20010200', 201718: '20010200', 200175: '13221500', 200176: '13221500', 201770: '13221500', 201668: '20006200', 201669: '20006200', 201670: '20006200', 201671: '20006200'})
catalog=json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text(encoding='utf-8'))
mapping=(ROOT/'LegacyGwent-diy(1)/LegacyGwent-diy/src/Cynthia.Card/src/Cynthia.Card.Common/GwentGame/GwentMap.cs').read_text(encoding='utf-8-sig')
def normalize(value):return re.sub('[^a-z0-9]','',value.lower())
names={}
for ident,name,art in re.findall(r'CardId\s*=\s*"([^"]+)",\s*//([^\n]+)(?:(?!CardId\s*=).)*?CardArtsId\s*=\s*"([^"]+)"',mapping,re.S):
    names.setdefault(normalize(name),set()).add(art)
def resolve(template):
    if template in ALIASES:
        path=SOURCE/(ALIASES[template]+'.png')
        if path.exists():return path,'explicit_original_illustration_binding'
    path=SOURCE/(str(template)+'00.png')
    if path.exists():return path,'matching_original_template_id'
    english=catalog['localization'].get('en_us',{}).get(str(template)+'_name','')
    found=names.get(normalize(english),set()) if english else set()
    if len(found)==1:
        path=SOURCE/(next(iter(found))+'.png')
        if path.exists():return path,'exact_english_name_in_DIY_GwentMap'
    return None,'no_verified_art_binding'

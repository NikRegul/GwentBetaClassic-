"""Extract original data for the direct JS -> WS port. No native host/runtime."""
import hashlib,json,pathlib,xml.etree.ElementTree as E,zipfile

root=pathlib.Path(__file__).resolve().parents[3]
out=pathlib.Path(__file__).resolve().parent/'data'
out.mkdir(exist_ok=True)
archive=root/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'
with zipfile.ZipFile(archive) as z:
    raw_templates=z.read('Templates.xml');raw_profiles=z.read('Personalities.xml')
    templates=E.fromstring(raw_templates);profiles=E.fromstring(raw_profiles)

def scalar(text):
    if text is None:return ''
    if text in ('True','False'):return text=='True'
    try:return int(text)
    except ValueError:pass
    try:return float(text)
    except ValueError:return text

def bits(element):
    if element is None:return []
    return [i*64+b for i,v in enumerate(element) for b in range(64) if int(v.get('V','0'))&(1<<b)]

def tag_entry(x):
    try:tag_id=int(x.get('TagName'))
    except (ValueError,TypeError):return None # Original HasValidTag rejects non-numeric names.
    if tag_id==1:return None
    try:weight=float(x.text or 0)
    except ValueError:weight=0
    return {'id':tag_id,'weight':weight,'usage':usage.get(x.get('UsageType'),0),
            'rounds':rounds.get(x.get('ValidRounds'),7)}

def settings(x):
    node=x.find('Settings')
    return [] if node is None else [{'type':v.get('Type'),'value':scalar(v.text)} for v in node]

card_data={}
for t in templates:
    if t.get('Type')!='CardTemplate':continue
    def val(k,default=0):return scalar(t.findtext(k,str(default)))
    tid=int(t.get('Id'))
    placement=t.find('Placement')
    card_data[str(tid)]={'id':tid,'name':t.get('DebugName'),'type':val('Type'),'tier':val('Tier'),
        'power':val('Power'),'armor':val('Armor'),'tokens':val('Tokens'),'initialTimer':val('InitialTimer',-1),
        'linkedTemplateId':val('LinkedTemplateId'),'semanticTags':bits(t.find('SemanticTags')),
        'categories':bits(t.find('Categories')),'placement':{'player':int(placement.get('PlayerSide','0')) if placement is not None else 0,
        'opponent':int(placement.get('OpponentSide','0')) if placement is not None else 0}}

rounds={'None':0,'One':1,'Two':2,'Three':4,'NotOne':6,'NotTwo':5,'NotThree':3,'All':7}
usage={'BattleAndMulligan':0,'MulliganOnly':1,'BattleOnly':2}
profile_data={}
for p in profiles:
    entry={'name':p.get('Name'),'parent':p.get('ParentName'),'values':{},'inherited':{},'semanticTags':[],
           'associations':{},'sourceXml':E.tostring(p,encoding='unicode')}
    for field in p:
        if field.tag=='InheritedAttribs':entry['inherited']={x.tag:scalar(x.text) for x in field}
        elif field.tag=='SemanticTags':
            entry['semanticTags']=[v for x in field if (v:=tag_entry(x)) is not None]
        elif field.tag.endswith('Associations'):
            entry['associations'][field.tag]=[{'attributes':x.attrib,'settings':settings(x)} for x in field]
        elif len(field)==0:entry['values'][field.tag]=scalar(field.text)
    profile_data[entry['name']]=entry

for name,data in [('templates',card_data),('personalities',profile_data)]:
    (out/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
manifest={'schema':1,'purpose':'Direct JavaScript AI port for later WitcherScript implementation',
    'source':str(archive.relative_to(root)),'sourceXmlSha256':{
        'Templates.xml':hashlib.sha256(raw_templates).hexdigest(),'Personalities.xml':hashlib.sha256(raw_profiles).hexdigest()},
    'templates':len(card_data),'profiles':len(profile_data),'runtimeDependencies':['JavaScript'],
    'basePath':{k:profile_data['Base']['values'][k] for k in [
        'TreeSearchType','EvaluatorType','MulliganPickerType','CardPickerType','DepthOfChecking','MaxTimeAllowed']},
    'fullAiPortComplete':False}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False))

from pathlib import Path
import json,xml.etree.ElementTree as ET,sys
ROOT=Path('D:/w3mod');BASE=ROOT/'BetaGwent/build/universal081';sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import sound_index
checks=0;events=None
for key,version in [('audio-nextgen',150),('audio-classic',88)]:
 xml=BASE/key/('stream-bank.xml' if version==150 else 'legacy-bank.xml');root=ET.parse(xml).getroot()
 assert not root.findall('.//error') and not root.findall('.//skip');assert root.get('version')==str(version);checks+=2
 nodes=list(root.find('./object[@name="HircChunk"]/list'));mapping={int(n.find('field[@name="ulID"]').get('value')):n for n in nodes};assert len(mapping)==len(nodes);checks+=1
 ids={i for i,n in mapping.items() if n.get('name')=='CAkEvent'}
 if events is None:events=ids
 else:assert events==ids;checks+=1
 _,cache=sound_index(BASE/key/'soundspc.cache')
 for i,node in mapping.items():
  for field in node.iter('field'):
   name=field.get('name');value=field.get('value')
   if name in ('ulActionID','idExt','DirectParentID','ulChildID') and value and value!='0':assert int(value) in mapping;checks+=1
   if name=='sourceID':assert value+'.wem' in cache;checks+=1
   if name=='StreamType':assert int(value)==(2 if version==150 else 1);checks+=1
 merge=json.loads((BASE/'audio-merged/merge.json').read_text())
 for voice in merge['voices']:assert set(voice['events']).issubset(ids);checks+=1
report=dict(checks=checks,events=len(events),voices=5,media=merge['mediaCount'],eventAndMediaReferencesVerified=True,nativePlaybackVerified=False)
(BASE/'audio-reference-verification.json').write_text(json.dumps(report,indent=2));Path(__file__).with_name('universal_event_ids.json').write_text(json.dumps(sorted(events)))
print(report)

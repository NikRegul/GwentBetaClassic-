"""Bind original elemental sound events without adding native script files."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
def main():
 inventory=json.loads((ROOT/'docs/evidence/card-vfx163.json').read_text('utf8'))
 sounds={x['object']:f"bg79_fx_{x['eventId']}" for x in json.loads((ROOT/'docs/evidence/beta-audio86-vfx-map.json').read_text())}
 groups={};proof=[]
 for card in inventory['cards']:
  seen=set()
  for e in card['effects']:
   if e['node']!='ChangePowerNode' or not e.get('elementName'):continue
   op=e['fields'].get('Operation');method=e['fields'].get('AttackMethod',0)
   if op not in (0,1) or op in seen:continue
   seen.add(op);attack=e.get('attack') or {};impact=e.get('impact') or {}
   for launch in (False,True):
    if launch and method!=1:continue
    prefab=attack.get('prefab') if launch else impact.get('prefab') if method==1 else attack.get('prefab') or impact.get('prefab')
    event=sounds.get(prefab)
    if not event:continue
    groups.setdefault((launch,op,event),[]).append(card['templateId']);proof.append(dict(templateId=card['templateId'],operation=op,launch=launch,prefab=prefab,event=event))
 lines=['// BEGIN GENERATED ELEMENT AUDIO 164','function BetaGwentAudioElement164(templateId : int, kind : int, launch : bool) : string','{','    var hurting : bool;','    if(kind!=20 && kind!=21 && kind!=22 && kind!=23)return "";','    hurting=kind==20 || kind==22;']
 for launch in (False,True):
  for op in (0,1):
   lines+=['    if(launch=='+str(launch).lower()+' && hurting=='+str(op==1).lower()+'){','        switch(templateId){']
   for (l,o,event),ids in groups.items():
    if (l,o)!=(launch,op):continue
    lines+=['        '+' '.join('case '+str(id)+':' for id in ids)+' return "'+event+'";']
   lines+=['        }','    }']
 lines+=['    return "";','}','// END GENERATED ELEMENT AUDIO 164','']
 target=ROOT/'BetaGwent/development/scripts/game/betagwent/duelAudio.ws';s=target.read_text('utf-8-sig');begin='// BEGIN GENERATED ELEMENT AUDIO 164';end='// END GENERATED ELEMENT AUDIO 164'
 if begin in s:
  a=s.index(begin);b=s.index(end,a)+len(end);s=s[:a]+s[b:].lstrip('\n')
 s='\n'.join(lines)+s
 target.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
 (ROOT/'docs/evidence/element-audio164.json').write_text(json.dumps(dict(bindings=proof,allEventsPreexisting=True),indent=2)+'\n','utf8')
 print('Original elemental sound bindings:',len(proof))
if __name__=='__main__':main()

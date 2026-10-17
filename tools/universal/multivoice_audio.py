"""Merge frozen Wwise 150 voice banks without changing encoded media."""
from pathlib import Path
import argparse,hashlib,json,re,struct,subprocess,sys,xml.etree.ElementTree as ET
ROOT=Path('D:/w3mod')
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import sha,sound_index,require
from build_audio import chunks,chunk,field
VOICES=('ru','en','de','it','pt-br')
def fnv(s):
 v=2166136261
 for b in s.lower().encode('utf8'):v=((v*16777619)^b)&0xffffffff
 return v
def main():
 p=argparse.ArgumentParser();p.add_argument('--stage',type=int,default=202);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 out=a.out.resolve();require(out.is_relative_to(ROOT/'BetaGwent/build'),'Output outside build');out.mkdir(parents=True,exist_ok=True)
 event_names={}
 for f in (ROOT/'BetaGwent/development/scripts/game/betagwent').glob('*.ws'):
  for n in re.findall(r'bg79_[A-Za-z0-9_]+',f.read_text('utf-8-sig')):event_names[fnv(n)]=n
 for f in (ROOT/'BetaGwent/audio').glob('wwise*/Events/*.wwu'):
  for e in ET.parse(f).iter('Event'):
   n=e.get('Name');event_names[fnv(n)]=n
 records=[];media={};media_by_hash={};ids_used=set();inputs={};catalogs={};reports=[];header=None
 for lang in VOICES:
  source=ROOT/f'BetaGwent/build/release{a.stage}/{lang}/package/Mods/modBetaGwent0924/content/soundspc.cache'
  manifest=json.loads((source.parents[3]/'manifest.json').read_text('utf-8-sig'))
  expected=next(x for x in manifest['files'] if x['path'].endswith('/soundspc.cache'))['sha256'];require(sha(source)==expected,'Frozen audio changed')
  _,index=sound_index(source);require(len(index)==1,'Expected one bank')
  off,size=next(iter(index.values()))
  with source.open('rb') as f:f.seek(off);data=f.read(size)
  bank=out/(lang+'.bnk');bank.write_bytes(data);inputs[lang]=hashlib.sha256(data).hexdigest()
  xml=out/(lang+'.xml')
  if not xml.exists():subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/vendor/audio/wwiser.pyz'),'-d','xml','-dn',str(xml.with_suffix('')),str(bank)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
  tree=ET.parse(xml).getroot();require(not tree.findall('.//error') and not tree.findall('.//skip'),'Bank parsing failed')
  parts=dict(chunks(data));require(struct.unpack_from('<I',parts[b'BKHD'])[0]==150,'Unexpected source bank version')
  if header is None:header=parts[b'BKHD']
  require(parts[b'BKHD'][:12]==header[:12],'Voice bank version/ID/language differ')
  source_media={m:parts[b'DATA'][o:o+s] for m,o,s in struct.iter_unpack('<III',parts[b'DIDX'])};mid_map={}
  for mid,raw in source_media.items():
   digest=hashlib.sha256(raw).hexdigest()
   if digest not in media_by_hash:
    new=fnv('bg_multi_media_'+digest);require(new not in media,'Media ID collision');media_by_hash[digest]=new;media[new]=raw
   mid_map[mid]=media_by_hash[digest]
  nodes=list(tree.find('./object[@name="HircChunk"]/list'));mapping={}
  for node in nodes:
   old=int(field(node,'ulID'))
   if node.get('name')=='CAkEvent':
    require(old in event_names,'Missing event name '+str(old));name=event_names[old]
    new=old if lang=='ru' else fnv(name+'_'+lang.replace('-','_'))
   else:new=old if lang=='ru' else fnv('bg_multi_'+lang+'_'+str(old))
   require(new not in ids_used,'Object ID collision');ids_used.add(new);mapping[old]=new
  events=[]
  for node in nodes:
   start=int(node.find('field[@name="eHircType"]').get('offset'));length=int(field(node,'dwSectionSize'))+5
   raw=bytearray(data[start:start+length]);require(len(raw)==length,'HIRC range')
   for f in node.iter('field'):
    if f.get('type') not in ('sid','tid') or f.get('offset') is None:continue
    value=int(f.get('value'));name=f.get('name');new=None
    if name=='sourceID':new=mid_map[value]
    elif value in mapping:new=mapping[value]
    if new is not None:
     offset=int(f.get('offset'))-start;require(0<=offset<=len(raw)-4,'ID field extent');require(struct.unpack_from('<I',raw,offset)[0]==value,'ID field mismatch');struct.pack_into('<I',raw,offset,new)
   records.append(bytes(raw))
   if node.get('name')=='CAkEvent':events.append(mapping[int(field(node,'ulID'))])
  catalog=ROOT/f'BetaGwent/build/stage{a.stage}/{lang}/sources/scripts/game/betagwent/duelAudioCatalog.ws'
  require(catalog.exists(),'Frozen voice catalog missing');catalogs[lang]=str(catalog)
  reports.append(dict(language=lang,events=events,sourceObjects=len(nodes),media=len(source_media)))
  print('Merged',lang,len(nodes),'objects',flush=True)
 didx=bytearray();payload=bytearray()
 for mid,raw in sorted(media.items()):
  payload+=bytes((-len(payload))%16);didx+=struct.pack('<III',mid,len(payload),len(raw));payload+=raw
 result=chunk(b'BKHD',header)+chunk(b'DIDX',didx)+chunk(b'DATA',payload)+chunk(b'HIRC',struct.pack('<I',len(records))+b''.join(records))
 dest=out/'BetaGwent79.bnk';dest.write_bytes(result)
 report=dict(stage=a.stage,bank=str(dest),sha256=sha(dest),bytes=len(result),sourceBanks=inputs,catalogs=catalogs,voices=reports,mediaCount=len(media),objects=len(records),encodedMediaPreserved=True,nativePlaybackVerified=False)
 (out/'merge.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print('Universal bank MiB',len(result)/1024**2,flush=True)
if __name__=='__main__':main()

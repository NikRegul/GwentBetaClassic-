"""Read-only CR2W quest topology audit for the local Toussaint tournament.

Only bounded name/export/property tables and known pointer/scalar shapes are
read. Unknown properties remain raw; no native resources are written.
"""
from pathlib import Path
import hashlib,json,struct
ROOT=Path(__file__).resolve().parents[2]
PATH=Path('D:/GOG Galaxy/Games/The Witcher 3 REDkit/r4data/dlc/bob/data/quests/minor_quests/quest_files/cg700_card_game.w2phase')
b=PATH.read_bytes();assert b[:4]==b'CR2W' and struct.unpack_from('<I',b,4)[0]==163
tables=[struct.unpack_from('<III',b,40+i*12) for i in range(10)]
o,s,_=tables[0];strings=b[o:o+s];assert len(strings)==s
o,c,_=tables[1];names=[]
for i in range(c):
    q=struct.unpack_from('<I',b,o+i*8)[0];names.append(strings[q:strings.index(0,q)].decode('utf8'))
o,c,_=tables[4];exports=[struct.unpack_from('<HHIIIII',b,o+i*24) for i in range(c)]
cache={}
def props(ident):
    if ident in cache:return cache[ident]
    assert 1<=ident<=len(exports)
    ci,flags,parent,size,pos,template,crc=exports[ident-1]
    d=b[pos:pos+size];assert len(d)==size and d[:1]==b'\0'
    off=1;out={}
    while off+8<=len(d) and d[off:off+2]!=b'\0\0':
        ni,ty,length=struct.unpack_from('<HHI',d,off);end=off+4+length
        assert length>=4 and end<=len(d) and ni<len(names) and ty<len(names)
        out[names[ni]]=(names[ty],d[off+8:end]);off=end
    assert d[off:off+2]==b'\0\0'
    cache[ident]=out;return out
def ptr(prop):
    kind,data=prop;assert kind.startswith('ptr:') and len(data)==4
    return struct.unpack('<I',data)[0]
def handles(prop):
    kind,data=prop;assert kind.startswith('array:2,0,ptr:')
    count=struct.unpack_from('<I',data)[0];assert len(data)==4+4*count
    return list(struct.unpack_from('<'+'I'*count,data,4))
def text(prop):
    kind,data=prop
    if kind=='CName':assert len(data)==2;return names[struct.unpack('<H',data)[0]]
    if kind=='String' and data:
        # Single-byte length prefix, ASCII payload only in this audit.
        if data[0]&0x80 and not data[0]&0x40 and len(data)==1+(data[0]&0x3f):return data[1:].decode('ascii')
    return None
def upstream(node):
    result=[]
    for socket in handles(props(node).get('sockets',('array:2,0,ptr:CGraphSocket',b'\0'*4))):
        fields=props(socket)
        # An omitted direction is the default input. Explicit output sockets
        # are excluded; do not cross arbitrary downstream/failure paths.
        if 'direction' in fields:continue
        for connection in handles(fields.get('connections',('array:2,0,ptr:CGraphConnection',b'\0'*4))):
            pair=props(connection);a=ptr(pair['source']);z=ptr(pair['destination'])
            other=z if a==socket else a;result.append(ptr(props(other)['block']))
    return result
records=[]
for i,e in enumerate(exports,1):
    if names[e[0]]!='CGwintMinigame':continue
    fields=props(i);deck=text(fields['deckName']);queue=[(e[2],0)];visited=set();previous=[]
    while queue:
        node,depth=queue.pop(0)
        if node in visited or depth>10:continue
        visited.add(node);fields2=props(node)
        labels={k:text(v) for k,v in fields2.items() if v[0] in ('CName','String')}
        labels={k:v for k,v in labels.items() if v is not None}
        previous.append(dict(export=node,type=names[exports[node-1][0]],depth=depth,labels=labels))
        queue += [(other,depth+1) for other in upstream(node)]
    faction_kind,faction_data=fields['forceFaction'];assert faction_kind=='eGwintFaction' and len(faction_data)==2
    records.append(dict(deck=deck,export=i,forcedFaction=names[struct.unpack('<H',faction_data)[0]],upstream=previous))
report=dict(source=str(PATH),sha256=hashlib.sha256(b).hexdigest(),version=163,minigames=records,sourceModified=False,note='Known quest graph pointer topology only; no broad native deserialization claim.')
out=ROOT/'docs/evidence/native-tournament83.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
for r in records:print(r['deck'],[(n['type'],n['labels']) for n in r['upstream'][:14]])

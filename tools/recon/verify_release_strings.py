"""Check native cooked localization counts, IDs and key tables against its DB.

This checks layout and identity, not translation quality or language crypto.
The RTSW header/table layout is checked directly against native Wcc output.
"""
from pathlib import Path
import hashlib,json,sqlite3,struct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/release87'
database=BASE/'project/BetaGwent0924/LocalEditorStringDataBaseW3_UTF8_mod.db'
with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
    source_ids={r[0] for r in db.execute('SELECT STRING_ID FROM STRING_INFO')}
    assert len(source_ids)==396
result={}
for language in ['ru','en']:
    path=BASE/'package/Mods/modBetaGwent0924/content'/(language+'.w3strings')
    raw=path.read_bytes();assert raw[:4]==b'RTSW'
    offset=10
    def vlq():
        global offset
        value=raw[offset];offset+=1;number=value&63;shift=6
        while value&64:
            value=raw[offset];offset+=1
            number|=(value&127)<<shift;shift+=7
        return number
    count=vlq();assert count==len(source_ids)
    entries=[struct.unpack_from('<III',raw,offset+i*12) for i in range(count)]
    offset+=12*count
    encoded_ids={r[0] for r in entries};assert len(encoded_ids)==count
    candidates={v^min(source_ids) for v in encoded_ids}
    assert any({v^key for v in encoded_ids}==source_ids for key in candidates)
    keys=vlq();assert keys==count
    key_entries=[struct.unpack_from('<II',raw,offset+i*8) for i in range(keys)]
    assert len({r[0] for r in key_entries})==keys
    assert {r[1] for r in key_entries}==encoded_ids
    assert all(r[2]>0 for r in entries)
    result[language]=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
        version=struct.unpack_from('<I',raw,4)[0],strings=count,keyEntries=keys,
        encodedIdLayoutMatchesSource=True,keyTableCoversAllIds=True,nonemptyLengths=True)
report=dict(stage=87,languages=result,englishIsRussianFallback=True,runtimeVerified=False)
(ROOT/'docs/evidence/stage87-cooked-strings.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))

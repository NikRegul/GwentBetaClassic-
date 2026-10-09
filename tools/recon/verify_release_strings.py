"""Check native cooked localization counts, IDs and key tables against its DB.

This checks layout and identity, not translation quality or language crypto.
The RTSW header/table layout is checked directly against native Wcc output.
"""
from pathlib import Path
import argparse,hashlib,json,sqlite3,struct

ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--base',type=Path,default=ROOT/'BetaGwent/build/release87')
p.add_argument('--stage',type=int,default=87)
p.add_argument('--package-language',choices=['ru','en'])
a=p.parse_args();BASE=a.base.resolve()
database=BASE/'project/BetaGwent0924/LocalEditorStringDataBaseW3_UTF8_mod.db'
with sqlite3.connect(database.as_uri()+'?mode=ro',uri=True) as db:
    source_ids={r[0] for r in db.execute('SELECT STRING_ID FROM STRING_INFO')}
    assert source_ids
result={}
content=BASE/'package/Mods/modBetaGwent0924/content'
languages=sorted(path.stem for path in content.glob('*.w3strings'))
assert 'ru' in languages and 'en' in languages
for language in languages:
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
report=dict(stage=a.stage,languages=result,packageLanguage=a.package_language,runtimeVerified=False,
            note='Native ID/table layout verified; does not verify translation quality or decode language crypto.')
suffix='-'+a.package_language if a.package_language else ''
(ROOT/f'docs/evidence/stage{a.stage}-cooked-strings{suffix}.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))

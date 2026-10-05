"""Print bounded JSON chunks to the connected GitHub publisher; no credentials."""
from pathlib import Path
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--prepare',action='store_true');p.add_argument('--batch',type=int);p.add_argument('--part',type=int);a=p.parse_args()
base=ROOT/'BetaGwent/build/public-source89';out=base/'upload';out.mkdir(exist_ok=True)
if a.prepare:
    manifest=json.loads((base/'manifest.json').read_text('utf8'));batch=[];size=0;batches=[]
    def save():
        text=json.dumps(batch,ensure_ascii=True);index=len(batches)
        chunks=[text[i:i+48000] for i in range(0,len(text),48000)]
        for i,chunk in enumerate(chunks):(out/f'{index}-{i}.txt').write_text(chunk,'ascii')
        batches.append(dict(index=index,parts=len(chunks),files=len(batch)))
    for f in manifest['files']:
        entry=dict(path=f['path'],mode='100644',type='blob',content=(base/'GwentBetaClassic'/f['path']).read_text('utf-8-sig'))
        n=len(json.dumps(entry,ensure_ascii=True))
        if size+n>650000 and batch:save();batch=[];size=0
        batch.append(entry);size+=n
    if batch:save()
    (out/'batches.json').write_text(json.dumps(batches),'ascii');print(json.dumps(batches))
else:print((out/f'{a.batch}-{a.part}.txt').read_text('ascii'),end='')

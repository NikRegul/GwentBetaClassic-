"""Split the accepted embedded Classic bank by language without re-encoding media."""
from pathlib import Path
import argparse,hashlib,json,struct,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import INPUTS
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import write_sound_cache,sha
from build_audio import chunks,chunk,object_record
SOURCE=INPUTS/'authoring/classic081-geometry-effects-fix14/audio/banks/betagwent79.bnk'
MERGED=INPUTS/'authoring/universal081/audio-merged'

def fnv(s):
    v=2166136261
    for x in s.lower().encode():v=((v*16777619)^x)&0xffffffff
    return v

def records(bank):
    h=dict(chunks(bank))[b'HIRC'];count=struct.unpack_from('<I',h)[0];pos=4;result={}
    for _ in range(count):
        kind,size=struct.unpack_from('<BI',h,pos);pos+=5;body=h[pos:pos+size];pos+=size
        ident=struct.unpack_from('<I',body)[0];assert ident not in result
        result[ident]=(kind,body)
    assert pos==len(h)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to((ROOT/'BetaGwent/build').resolve()) and not out.exists()
    out.mkdir();(out/'banks').mkdir()
    accepted=json.loads((SOURCE.parents[1]/'audio.json').read_text('utf8'));assert sha(SOURCE)==accepted['bankSha256']
    original=SOURCE.read_bytes();parts=dict(chunks(original));all_records=records(original)
    media={mid:parts[b'DATA'][offset:offset+size] for mid,offset,size in struct.iter_unpack('<III',parts[b'DIDX'])}
    merger=json.loads((MERGED/'merge.json').read_text('utf8'));groups={}
    for voice in merger['voices']:
        lang=voice['language'];source=MERGED/(lang+'.bnk');assert sha(source)==merger['sourceBanks'][lang]
        groups[lang]=set(voice['events'])|{i if lang=='ru' else fnv('bg_multi_'+lang+'_'+str(i)) for i,(k,b) in records(source.read_bytes()).items() if k!=4}
        assert groups[lang]<=all_records.keys()
    assert set.union(*groups.values())==set(all_records)
    reports=[]
    for lang,ids in groups.items():
        # Generic UI/effect events are Russian (unsuffixed) in the universal scripts.
        # Keep that complete graph alongside the selected language's graph.
        ids=ids|groups['ru'];name='betagwent091_'+lang.replace('-','_')+'.bnk';bankid=fnv(name[:-4])
        used={struct.unpack_from('<I',body,12)[0] for i,(kind,body) in all_records.items() if i in ids and kind==2}
        data=bytearray();didx=bytearray();offsets={}
        for mid in sorted(used):
            payload=media[mid];data+=bytes((-len(data))%16);offsets[mid]=(len(data),len(payload));data+=payload
            didx+=struct.pack('<III',mid,*offsets[mid])
        output=[]
        for ident,(kind,raw) in all_records.items():
            if ident not in ids:continue
            body=bytearray(raw)
            if kind==2:
                assert struct.unpack_from('<I',body,8)[0]==0
                mid=struct.unpack_from('<I',body,12)[0];struct.pack_into('<3I',body,16,bankid,*offsets[mid])
                assert body[:16]==raw[:16] and body[28:]==raw[28:]
            elif kind==3:
                action,target=struct.unpack_from('<HI',body,4);assert target in ids
                if action==0x0403:struct.pack_into('<I',body,14,bankid)
                else:assert action==0x0103
            elif kind==4:
                count=struct.unpack_from('<I',body,4)[0]
                assert len(body)==8+4*count and all(x[0] in ids for x in struct.iter_unpack('<I',body[8:]))
            output.append(object_record(kind,body))
        header=bytearray(parts[b'BKHD'][:20]);struct.pack_into('<I',header,4,bankid)
        header+=bytes((-(8+len(header)+8+len(didx)+8))%16)
        bank=chunk(b'BKHD',header)+chunk(b'DIDX',didx)+chunk(b'DATA',data)+chunk(b'HIRC',struct.pack('<I',len(output))+b''.join(output))
        assert len(bank)<130*1024**2
        dest=out/'banks'/name;dest.write_bytes(bank);checked=dict(chunks(bank))
        for mid,(offset,size) in offsets.items():assert checked[b'DATA'][offset:offset+size]==media[mid]
        assert set(records(bank))==ids
        reports.append(dict(language=lang,name=name,bankId=bankid,bytes=len(bank),sha256=sha(dest),objects=len(output),media=len(used)))
        print(lang,round(len(bank)/1024**2,3),'MiB',flush=True)
    cache=write_sound_cache(out/'banks',out/'soundspc.cache')
    (out/'manifest.json').write_text(json.dumps(dict(sourceSha256=sha(SOURCE),banks=reports,cache=cache,encodedMediaPreserved=True,nativePlaybackVerified=False),indent=2),'utf8')

if __name__=='__main__':main()

"""Stage 096: add the imported Beta UI sound events to the shipped audio caches.

Rebuilding the 0.8.1 universal audio chain is not needed: the 0.9.0 caches are
patched incrementally. Next-Gen (5.0+): the merged Wwise 150 bank of the 0.9.0
5.0+ archive gains the stage-096 events, actions and sounds (streamed: wem files
in the cache) and the updated bg79_sfx actor-mixer. Classic (1.32): the RU
project bank is converted to Wwise 88 by tools/classic132/build_audio.py
(needs WwiseConsole) and the same closure is appended to every language bank of
build-inputs/classic-audio. Media bytes, IDs and every existing object are kept.
Outputs: BetaGwent/build-inputs/nextgen-audio096/soundspc.cache and
BetaGwent/build-inputs/classic-audio096/. Run on Windows:
    python -X utf8 tools/features096/patch_audio096.py            (both)
    python -X utf8 tools/features096/patch_audio096.py --nextgen-only
"""
from pathlib import Path
import argparse,hashlib,json,shutil,struct,subprocess,sys,zipfile
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'));sys.path.insert(0,str(ROOT/'tools'))
from formats import sound_index,write_sound_cache,fnv64,sha,require
from build_inputs import INPUTS
NEW_BANK=ROOT/'BetaGwent/audio/wwise/GeneratedSoundBanks/Windows/BetaGwent79.bnk'
BASE_ZIP=INPUTS/'package-baseline/GwentBetaClassic-0.9.0-5.0+-AllLanguages.zip'
NG_ENTRY='Mods/modBetaGwent0924/content/soundspc.cache'
CLASSIC_IN=INPUTS/'classic-audio';CLASSIC_OUT=INPUTS/'classic-audio096';NG_OUT=INPUTS/'nextgen-audio096'
WORK=ROOT/'BetaGwent/build/audio096-patch'
SOURCE_REPORT=ROOT/'docs/evidence/stage096-ui-audio.json'
MIXER=10544868  # bg79_sfx
def fnv(s):
    v=2166136261
    for b in s.lower().encode():v=((v*16777619)^b)&0xffffffff
    return v
def chunks(raw):
    pos=0;out=[]
    while pos<len(raw):
        tag,sz=struct.unpack_from('<4sI',raw,pos);out.append((tag,raw[pos+8:pos+8+sz]));pos+=8+sz
    return out
def chunk(tag,data):return tag+struct.pack('<I',len(data))+data
def records(h):
    n=struct.unpack_from('<I',h)[0];p=4;out=[]
    for _ in range(n):
        k,sz=struct.unpack_from('<BI',h,p);body=h[p+5:p+5+sz];out.append((struct.unpack_from('<I',body)[0],k,body));p+=5+sz
    require(p==len(h),'HIRC extent');return out
def hirc(rows):return struct.pack('<I',len(rows))+b''.join(struct.pack('<BI',k,len(b))+b for _,k,b in rows)
# Wwise loads HIRC in order and an event resolves its actions while loading:
# an event placed before its action makes the WHOLE bank fail to load (all Beta
# sounds silent, script falls back to TW3 GUI). Generated banks always list
# sounds, then actions, then events, so appended objects keep that order.
WWISE_RANK={2:0,3:1,4:2}
def wwise_order(extra):return sorted(extra,key=lambda r:WWISE_RANK.get(r[1],-1))
def require_load_order(rows,v88=False):
    kinds={i:k for i,k,_ in rows};seen=set()
    for i,k,b in rows:
        if k==4:
            if v88:count=struct.unpack_from('<I',b,4)[0];acts=[struct.unpack_from('<I',b,8+4*j)[0] for j in range(count)]
            else:count=b[4];acts=[struct.unpack_from('<I',b,5+4*j)[0] for j in range(count)]
            require(all(a in seen for a in acts if a in kinds),'event before its action: %d'%i)
        elif k==3:
            target=struct.unpack_from('<I',b,6)[0]
            require(kinds.get(target)!=2 or target in seen,'action before its sound: %d'%i)
        seen.add(i)
def event_names():
    report=json.loads(SOURCE_REPORT.read_text('utf8'))
    names=['bg79_fx_'+i for i in report['rendered']]
    if '2977021572' in report['rendered']:names.append('bg79_fx_2977021572_stop')
    return names
def closure(rec,names,v88=False):
    """Events -> actions -> targets (sounds). Returns ordered IDs."""
    ids=[]
    for n in names:
        e=fnv(n);require(e in rec and rec[e][0]==4,'event missing in bank: '+n);ids.append(e)
        body=rec[e][1]
        # Wwise 150 events: u8 count + ids; Wwise 88: u32 count + ids.
        if v88:count=struct.unpack_from('<I',body,4)[0];acts=[struct.unpack_from('<I',body,8+4*i)[0] for i in range(count)]
        else:count=body[4];acts=[struct.unpack_from('<I',body,5+4*i)[0] for i in range(count)]
        for a in acts:
            require(rec[a][0]==3,'action');ids.append(a);t=struct.unpack_from('<I',rec[a][1],6)[0];require(t in rec,'action target')
            if rec[t][0]==2:ids.append(t)
    return list(dict.fromkeys(ids))
def mixer_children(body):
    for n in range(1,4000):
        off=len(body)-4*n-4
        if off<0:break
        if struct.unpack_from('<I',body,off)[0]==n:return off,[x[0] for x in struct.iter_unpack('<I',body[off+4:])]
    raise ValueError('actor-mixer children not found')
def merge_mixer(old,new):
    oo,oc=mixer_children(old);no,nc=mixer_children(new)
    require(old[:oo]==new[:no],'bg79_sfx properties differ between banks');require(set(oc)<=set(nc),'bg79_sfx lost children')
    return new
def union_mixer(old,new):
    """Keep the shipped mixer properties; add the children the new bank has."""
    oo,oc=mixer_children(old);no,nc=mixer_children(new);kids=oc+[x for x in nc if x not in oc]
    return old[:oo]+struct.pack('<I',len(kids))+b''.join(struct.pack('<I',x) for x in kids)
def nextgen(names):
    raw_zip=zipfile.ZipFile(BASE_ZIP).read(NG_ENTRY);WORK.mkdir(parents=True,exist_ok=True)
    cache=WORK/'base-nextgen.cache';cache.write_bytes(raw_zip);version,index=sound_index(cache);require(version==2,'Next-Gen cache v2')
    files={}
    with cache.open('rb') as f:
        for name,(off,size) in index.items():f.seek(off);files[name]=f.read(size)
    base=dict(chunks(files['betagwent79.bnk']));new=dict(chunks(NEW_BANK.read_bytes()))
    require(base[b'BKHD'][:8]==new[b'BKHD'][:8],'bank version/id')
    brows=records(base[b'HIRC']);bset={i for i,_,_ in brows};nrec={i:(k,b) for i,k,b in records(new[b'HIRC'])}
    didx={m:(o,s) for m,o,s in struct.iter_unpack('<III',new[b'DIDX'])}
    add=[i for i in closure(nrec,names) if i not in bset];added_media=[]
    rows=[(i,k,(merge_mixer(b,nrec[i][1]) if i==MIXER else b)) for i,k,b in brows]
    extra=[]
    for i in add:
        k,b=nrec[i];b=bytearray(b)
        if k==2:
            require(b[8]==0,'expected embedded source in the project bank');mid=struct.unpack_from('<I',b,9)[0];o,s=didx[mid]
            name=str(mid)+'.wem';files[name]=new[b'DATA'][o:o+s];added_media.append(name)
            b[8]=2;struct.pack_into('<I',b,13,0)  # streamed from the cache, as build_caches.py
        extra.append((i,k,bytes(b)))
    rows+=wwise_order(extra);require_load_order(rows)
    files['betagwent79.bnk']=chunk(b'BKHD',base[b'BKHD'])+chunk(b'HIRC',hirc(rows))
    out=NG_OUT;out.mkdir(parents=True,exist_ok=True);target=out/'soundspc.cache'
    order=sorted(n for n in files if n.endswith('.bnk'))+sorted(n for n in files if n.endswith('.wem'))
    names_blob=bytearray();table=bytearray();cursor=64
    for n in order:table+=struct.pack('<QQQ',len(names_blob),cursor,len(files[n]));names_blob+=n.encode()+b'\0';cursor+=len(files[n])
    header=bytearray(raw_zip[:64]);struct.pack_into('<QQQI',header,16,cursor+len(names_blob),len(order),cursor,len(names_blob))
    struct.pack_into('<QQ',header,48,(max(len(files[n]) for n in order)+4095)&~4095,fnv64(names_blob+table))
    with target.open('wb') as f:
        f.write(header)
        for n in order:f.write(files[n])
        f.write(names_blob);f.write(table)
    v,check=sound_index(target);require(v==2 and len(check)==len(order),'written cache index')
    with target.open('rb') as f:
        for n in order:o,s=check[n];f.seek(o);require(f.read(s)==files[n],'cached payload '+n)
    rep=dict(baseSha256=hashlib.sha256(raw_zip).hexdigest(),sha256=sha(target),files=len(order),addedObjects=len(add),addedMedia=len(added_media),events=len(names))
    (out/'manifest.json').write_text(json.dumps(rep,indent=2)+'\n','utf8');return rep
def classic(names,console):
    conv=WORK/'classic-convert';xml=WORK/'ru-bank'
    if not (WORK/'ru-bank.xml').exists():
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/vendor/audio/wwiser.pyz'),'-d','xml','-dn',str(xml),str(NEW_BANK)],check=True)
    converted=conv/'BetaGwent79.bnk'
    if not converted.exists():
        cmd=[sys.executable,'-X','utf8',str(ROOT/'tools/classic132/build_audio.py'),'--bank',str(NEW_BANK),'--xml',str(WORK/'ru-bank.xml'),'--out',str(conv)]
        if console:cmd+=['--console',str(console)]
        subprocess.run(cmd,check=True)
    c=dict(chunks(converted.read_bytes()));crec={i:(k,b) for i,k,b in records(c[b'HIRC'])}
    # build_audio.py keeps the *source* Opus media in conv/wem (decoder input) and
    # writes the Wwise Vorbis it encoded for Wwise 88 to conv/banks/Windows. 1.32
    # cannot decode Opus (0x3041): taking conv/wem left every new sound silent.
    def cmedia(mid):
        raw=(conv/'banks/Windows'/(str(mid)+'.wem')).read_bytes();p=raw.find(b'fmt ')
        require(p>0 and struct.unpack_from('<IH',raw,p+4)==(66,0xffff),'Classic media must be Wwise Vorbis: %d'%mid)
        return raw
    want=closure(crec,names,True)
    manifest=json.loads((CLASSIC_IN/'manifest.json').read_text('utf8'))
    if CLASSIC_OUT.exists():shutil.rmtree(CLASSIC_OUT)
    (CLASSIC_OUT/'banks').mkdir(parents=True);reports=[]
    for entry in manifest['banks']:
        src=CLASSIC_IN/'banks'/entry['name'];raw=src.read_bytes();require(sha(src)==entry['sha256'],'classic bank changed: '+entry['name'])
        parts=dict(chunks(raw));bankid=struct.unpack_from('<I',parts[b'BKHD'],4)[0]
        rows=records(parts[b'HIRC']);have={i for i,_,_ in rows}
        data=bytearray(parts[b'DATA']);didx=bytearray(parts[b'DIDX']);known={m for m,_,_ in struct.iter_unpack('<III',bytes(didx))}
        rows=[(i,k,(union_mixer(b,crec[i][1]) if i==MIXER and i in crec else b)) for i,k,b in rows]
        extra=[]
        for i in [x for x in want if x not in have]:
            k,b=crec[i];b=bytearray(b)
            if k==2:
                # streamed [id][plugin][type=1][mid][fileId=mid][tail] -> embedded [id][plugin][type=0][mid][bank][offset][size][tail]
                require(struct.unpack_from('<I',b,8)[0]==1,'expected streamed Wwise 88 source');mid=struct.unpack_from('<I',b,12)[0]
                if mid not in known:
                    payload=cmedia(mid);data+=bytes((-len(data))%16);off=len(data);data+=payload;didx+=struct.pack('<III',mid,off,len(payload));known.add(mid)
                o,s=[(o,s) for m,o,s in struct.iter_unpack('<III',bytes(didx)) if m==mid][0]
                b=bytearray(bytes(b[:8])+struct.pack('<5I',0,mid,bankid,o,s)+bytes(b[20:]))
            elif k==3:
                action=struct.unpack_from('<H',b,4)[0]
                if action==0x0403:struct.pack_into('<I',b,14,bankid)
            extra.append((i,k,bytes(b)))
        # Wwise 88 (1.32): a parent links its children while it loads, so the new
        # sounds must precede bg79_sfx exactly as in generated banks; Wwise 2019
        # (Next-Gen) tolerates either order, but 1.32 reports nativeLoaded=false.
        extra=wwise_order(extra);sounds=[r for r in extra if r[1]==2];at=[i for i,_,_ in rows].index(MIXER)
        rows=rows[:at]+sounds+rows[at:]+[r for r in extra if r[1]!=2];require_load_order(rows,True)
        pos={i:n for n,(i,_,_) in enumerate(rows)};_,kids=mixer_children(rows[pos[MIXER]][2])
        require(all(pos[c]<pos[MIXER] for c in kids if c in pos),'bg79_sfx child after its parent')
        # Wwise looks media up by binary search: DIDX must stay sorted by media id
        # (appending new media at the end broke every lookup past the insertion point).
        didx=b''.join(struct.pack('<III',*m) for m in sorted(struct.iter_unpack('<III',bytes(didx))))
        require(len({m for m,_,_ in struct.iter_unpack('<III',didx)})==len(didx)//12,'duplicate media id')
        header=bytearray(parts[b'BKHD']);bank=chunk(b'BKHD',header)+chunk(b'DIDX',bytes(didx))+chunk(b'DATA',bytes(data))+chunk(b'HIRC',hirc(rows))
        for m,mo,ms in struct.iter_unpack('<III',bytes(didx)):
            p=data.find(b'fmt ',mo,mo+64);require(p>0 and struct.unpack_from('<H',data,p+8)[0]==0xffff,'non-Vorbis media in classic bank: %d'%m)
        require(len(bank)<130*1024**2,'bank size')
        dest=CLASSIC_OUT/'banks'/entry['name'];dest.write_bytes(bank)
        reports.append(dict(entry,bytes=len(bank),sha256=sha(dest),objects=len(rows)))
    cache=write_sound_cache(CLASSIC_OUT/'banks',CLASSIC_OUT/'soundspc.cache')
    out=dict(manifest,banks=reports,cache=cache,stage096=dict(events=len(names),objects=len(want),sourceManifestSha256=sha(CLASSIC_IN/'manifest.json')))
    (CLASSIC_OUT/'manifest.json').write_text(json.dumps(out,indent=2),'utf8');return out['stage096']
def main():
    global WORK,CLASSIC_OUT,NG_OUT,SOURCE_REPORT
    a=argparse.ArgumentParser();a.add_argument('--nextgen-only',action='store_true');a.add_argument('--console',type=Path)
    a.add_argument('--work',type=Path);a.add_argument('--classic-out',type=Path);a.add_argument('--nextgen-out',type=Path);a.add_argument('--source-report',type=Path);a.add_argument('--report',type=Path);args=a.parse_args()
    if args.work:WORK=args.work.resolve()
    if args.classic_out:CLASSIC_OUT=args.classic_out.resolve()
    if args.nextgen_out:NG_OUT=args.nextgen_out.resolve()
    if args.source_report:SOURCE_REPORT=args.source_report.resolve()
    names=event_names();report=dict(nextgen=nextgen(names))
    if not args.nextgen_only:report['classic']=classic(names,args.console)
    (args.report or ROOT/'docs/evidence/stage096-audio-caches.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))
if __name__=='__main__':main()

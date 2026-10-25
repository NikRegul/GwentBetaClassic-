"""Prepare separate Next-Gen/Classic music caches; do not overwrite any voice cache."""
from pathlib import Path
import argparse, copy, json, struct, sys, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from build_audio import chunks, chunk, object_record, field, node_params
from formats import sha, fnv64, sound_index, write_sound_cache

def main():
    p=argparse.ArgumentParser();p.add_argument('--music',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists();out.mkdir(parents=True)
    music=a.music.resolve();report=json.loads((music/'music.json').read_text('utf8'));source=Path(report['bank']);assert sha(source)==report['bankSha256']
    parts=dict(chunks(source.read_bytes()));bankid=struct.unpack_from('<I',parts[b'BKHD'],4)[0]
    tree=ET.parse(str(source)+'.xml');items=tree.getroot().find('./object[@name="HircChunk"]/list');assert len(items)==5
    sound=next(n for n in items if n.get('name')=='CAkSound');assert int(field(sound,'OverrideBusId'))==3991942870
    props=sound.find('.//object[@name="NodeInitialParams"]')
    loop=next(n for n in props.findall('./object/list/object') if '[Loop]' in n.find('field[@name="pID"]').get('valuefmt',''))
    assert int(field(loop,'pValue'))==0,'Infinite native loop must survive export'
    media={mid:parts[b'DATA'][offset:offset+size] for mid,offset,size in struct.iter_unpack('<III',parts[b'DIDX'])};assert len(media)==1
    mid,payload=next(iter(media.items()));legacy=bytearray(payload);pos=12;patched=False
    while pos<len(legacy):
        tag,size=struct.unpack_from('<4sI',legacy,pos);start=pos+8
        if tag==b'fmt ':
            assert size==66 and struct.unpack_from('<H',legacy,start)[0]==0xffff
            config=struct.unpack_from('<I',legacy,start+20)[0];channels=struct.unpack_from('<H',legacy,start+2)[0]
            assert config&255==channels and (config>>8)&15==1
            struct.pack_into('<I',legacy,start+20,config>>12);patched=True
        end=start+size;pos=end+(size&1 if end<len(legacy) else 0)
    assert patched and pos==len(legacy)
    records=[]
    for node in items:
        name=node.get('name');ident=int(field(node,'ulID'));body=struct.pack('<I',ident)
        if name=='CAkSound':
            simplified=copy.deepcopy(node)
            for parent in simplified.iter():
                for prop in list(parent):
                    if prop.tag=='object' and prop.find('field[@name="pID"]') is not None:parent.remove(prop)
            params,_=node_params(simplified);assert params[12]==0
            # AkPropID_088 Loop=7, value 0 means infinite. Other parameters stay exact.
            params=params[:12]+b'\1\7'+struct.pack('<i',0)+params[13:]
            body+=struct.pack('<6I',0x40001,0,mid,bankid,0,len(legacy))+b'\0'+params;kind=2
        elif name in ('CAkActionPlay','CAkActionStop'):
            action=int(field(node,'ulActionType'));assert action in (0x0403,0x0103)
            body+=struct.pack('<HI',action,int(field(node,'idExt')))+b'\0\0\0\4'+struct.pack('<I',bankid if action==0x0403 else 0);kind=3
        elif name=='CAkEvent':
            actions=[int(x.get('value')) for x in node.findall('.//field[@name="ulActionID"]')]
            body+=struct.pack('<I',len(actions))+b''.join(struct.pack('<I',x) for x in actions);kind=4
        else:raise ValueError(name)
        records.append(object_record(kind,body))
    didx=struct.pack('<III',mid,0,len(legacy));header=struct.pack('<5I',88,bankid,0,0,39)
    header+=bytes((-(8+len(header)+8+len(didx)+8))%16)
    classic=chunk(b'BKHD',header)+chunk(b'DIDX',didx)+chunk(b'DATA',legacy)+chunk(b'HIRC',struct.pack('<I',len(records))+b''.join(records))
    results={}
    for platform,bank in [('nextgen',source.read_bytes()),('classic',classic)]:
        folder=out/platform/'banks';folder.mkdir(parents=True);target=folder/'betagwentmenu.bnk';target.write_bytes(bank)
        cache=out/platform/'Mods/modBetaGwentMenuMusic/content/soundspc.cache';cache.parent.mkdir(parents=True)
        if platform=='classic':write_sound_cache(folder,cache)
        else:
            names=b'betagwentmenu.bnk\0';cursor=64+len(bank);table=struct.pack('<QQQ',0,64,len(bank))
            header=struct.pack('<4sIIIQQQIIQQ',b'CS3W',2,0,0,cursor+len(names),1,cursor,len(names),0,(len(bank)+4095)&~4095,fnv64(names+table))
            assert len(header)==64;cache.write_bytes(header+bank+names+table)
        version,index=sound_index(cache);assert set(index)=={'betagwentmenu.bnk'}
        offset,length=index['betagwentmenu.bnk'];assert cache.read_bytes()[offset:offset+length]==bank
        results[platform]=dict(cache=str(cache),cacheSha256=sha(cache),bank=str(target),bankSha256=sha(target),bankVersion=150 if platform=='nextgen' else 88,cacheVersion=version)
    (out/'manifest.json').write_text(json.dumps(dict(source=report,platforms=results,noInitBank=True,separateFromVoices=True,nativePlaybackVerified=False),indent=2),'utf8')
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()

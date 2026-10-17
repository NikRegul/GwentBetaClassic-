"""Rebuild a pinned voice event bank for Classic's Wwise 88 format.

Frozen Opus media is decoded to PCM16, then encoded as Wwise Vorbis (quality 6).
Sample count, sample rate and channels are verified. Sound/event IDs,
parent groups, volume and stop targets are retained. No Init bank is produced.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import wave
import shutil
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
DECODER=ROOT/'tools/vendor/audio/vgmstream-r2117/vgmstream-cli.exe'


def chunks(raw):
    pos=0
    while pos<len(raw):
        tag,size=struct.unpack_from('<4sI',raw,pos);pos+=8
        yield tag,raw[pos:pos+size];pos+=size
    assert pos==len(raw)


def chunk(tag,data):return tag+struct.pack('<I',len(data))+data
def object_record(kind,data):return struct.pack('<BI',kind,len(data))+data
def field(node,name,default=None):
    f=node.find('.//field[@name="'+name+'"]')
    return f.get('value') if f is not None else default


def node_params(node):
    parent=int(field(node,'DirectParentID','0'));bus=int(field(node,'OverrideBusId','0'))
    props=node.find('.//object[@name="NodeInitialParams"]')
    values=[]
    if props is not None:
        for prop in props.findall('./object/list/object'):
            ident=prop.find('field[@name="pID"]');value=prop.find('field[@name="pValue"]')
            if ident is not None and value is not None:
                if '[Volume]' not in ident.get('valuefmt',''):
                    raise ValueError('Unmapped source property: '+str(ident.attrib))
                values.append(float(value.get('value')))
    if len(values)>1:raise ValueError('Multiple volume properties')
    params=(b'\0\0'+struct.pack('<II',bus,parent)+b'\0\0'+
            (b'\1\0'+struct.pack('<f',values[0]) if values else b'\0')+b'\0'+
            b'\1\1\0\0'+b'\0'*4+struct.pack('<BBBH8B',1,0,0,0,*([0]*8))+
            struct.pack('<IH',0,0))
    return params,parent



def encode_vorbis(out,wavs,converted,metrics,console,quality):
    project=out/'encoder-project'
    template=ROOT/'BetaGwent/audio/wwise'
    if not project.exists():
        project.mkdir()
        for path in template.rglob('*'):
            if path.suffix.lower() in ('.wwu','.wproj'):
                dest=project/path.relative_to(template);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,dest)
    conversion=project/'Conversion Settings/Default Work Unit.wwu'
    tree=ET.parse(conversion);plugin=tree.find('.//ConversionPlugin')
    plugin.set('PluginName','Vorbis');plugin.set('PluginID','4')
    old=plugin.find('PropertyList')
    if old is not None:plugin.remove(old)
    props=ET.SubElement(plugin,'PropertyList');ET.SubElement(props,'Property',Name='QualityFactor',Type='Real32',Value=str(quality))
    tree.write(conversion,encoding='utf8',xml_declaration=True)
    sources=ET.Element('ExternalSourcesList',SchemaVersion='1',Root=str(wavs))
    for mid in converted:ET.SubElement(sources,'Source',Path=str(mid)+'.wav',Conversion='W3 sfx conversion settings',Destination=str(mid)+'.wem')
    xml=out/'sources.wsources';ET.ElementTree(sources).write(xml,encoding='utf8',xml_declaration=True)
    command=[str(console),'convert-external-source',str(project/'BetaGwent79.wproj'),'--platform','Windows','--source-file',str(xml),'--output',str(out/'encoded'),'--no-wwise-dat']
    print('Encoding',len(converted),'media as Vorbis quality',quality,flush=True)
    with (out/'encoder.log').open('wb') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:raise RuntimeError((out/'encoder.log').read_text('utf8',errors='replace')[-6000:])
    output={}
    for mid in converted:
        path=out/'encoded/Windows'/(str(mid)+'.wem');raw=bytearray(path.read_bytes());pos=12;found=False
        while pos<len(raw):
            tag,size=struct.unpack_from('<4sI',raw,pos);start=pos+8
            if tag==b'fmt ':
                assert size==66 and struct.unpack_from('<H',raw,start)[0]==0xffff
                channels,rate=struct.unpack_from('<HI',raw,start+2)
                assert channels==metrics[str(mid)]['channels'] and rate==metrics[str(mid)]['sampleRate']
                assert struct.unpack_from('<I',raw,start+24)[0]==metrics[str(mid)]['frames']
                # Old Wwise expects a speaker mask here, not the later packed AkChannelConfig.
                config=struct.unpack_from('<I',raw,start+20)[0]
                assert config&255==channels and (config>>8)&15==1
                struct.pack_into('<I',raw,start+20,config>>12);found=True
            end=start+size;assert end<=len(raw)
            pos=end+(size&1 if end<len(raw) else 0)
        assert found and pos==len(raw)
        output[mid]=bytes(raw)
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bank',type=Path,required=True)
    p.add_argument('--xml',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--codec',choices=('vorbis','pcm'),default='vorbis')
    p.add_argument('--quality',type=int,choices=range(1,11),default=6)
    p.add_argument('--console',type=Path,default=Path('C:/Audiokinetic/Wwise_2023.1.19.8928/images/Authoring/x64/Release/bin/WwiseConsole.exe'))
    a=p.parse_args();out=a.out.resolve()
    if not out.is_relative_to((ROOT/'BetaGwent/build').resolve()):p.error('Output outside build')
    out.mkdir(parents=True,exist_ok=True);wem=out/'wem';wav=out/'wav';wem.mkdir(exist_ok=True);wav.mkdir(exist_ok=True)
    source=a.bank.read_bytes();parts=dict(chunks(source));bank_id=struct.unpack_from('<I',parts[b'BKHD'],4)[0]
    fingerprint=dict(bankSha256=hashlib.sha256(source).hexdigest(),decoderSha256=hashlib.sha256(DECODER.read_bytes()).hexdigest(),xmlSha256=hashlib.sha256(a.xml.read_bytes()).hexdigest())
    fingerprint.update(codec=a.codec,quality=a.quality,encoderSha256=hashlib.sha256(a.console.read_bytes()).hexdigest() if a.codec=='vorbis' else None)
    cache=out/'inputs.json'
    if cache.exists() and json.loads(cache.read_text('utf8'))!=fingerprint:raise ValueError('Audio inputs changed; use a fresh output directory')
    cache.write_text(json.dumps(fingerprint,indent=2)+'\n','utf8')
    media={mid:parts[b'DATA'][off:off+size] for mid,off,size in struct.iter_unpack('<III',parts[b'DIDX'])}
    def decode(item):
        mid,data=item;src=wem/(str(mid)+'.wem');dst=wav/(str(mid)+'.wav')
        if not src.exists():src.write_bytes(data)
        if not dst.exists():
            result=subprocess.run([str(DECODER),'-i','-o',str(dst),str(src)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=60)
            if result.returncode:raise RuntimeError(result.stderr.decode('utf8',errors='replace'))
        with wave.open(str(dst),'rb') as audio:
            assert audio.getsampwidth()==2 and audio.getnframes()>0
            channels,rate,frames=audio.getnchannels(),audio.getframerate(),audio.getnframes()
            pcm=audio.readframes(frames) if a.codec=='pcm' else b''
        # A standard PCM WAVE is the native Wwise PCM codec's media payload.
        fmt=struct.pack('<HHIIHH',1,channels,rate,rate*channels*2,channels*2,16)
        payload=b'WAVE'+chunk(b'fmt ',fmt)+chunk(b'data',pcm)
        return mid,b'RIFF'+struct.pack('<I',len(payload))+payload,dict(frames=frames,sampleRate=rate,channels=channels)
    converted={};metrics={}
    with ThreadPoolExecutor(max_workers=6) as pool:
        for i,(mid,data,info) in enumerate(pool.map(decode,media.items()),1):
            converted[mid]=data;metrics[str(mid)]=info
            if i%200==0:print(f'Decoded {i}/{len(media)} voice media',flush=True)
    if a.codec=='vorbis':converted=encode_vorbis(out,wav,converted,metrics,a.console,a.quality)
    didx=bytearray();data=bytearray();offsets={}
    bankdir=out/'banks/Windows';bankdir.mkdir(parents=True,exist_ok=True)
    for mid,payload in converted.items():
        (bankdir/(str(mid)+'.wem')).write_bytes(payload)
    # Include padding in BKHD so DATA starts at the standard 16-byte boundary.
    header=struct.pack('<5I',88,bank_id,0,0,39)+b'\0'*8
    padding=(-(8+len(header)+8+len(didx)+8))%16;header+=b'\0'*padding
    data_start=8+len(header)+8+len(didx)+8
    root=ET.parse(a.xml).getroot();items=root.find('./object[@name="HircChunk"]/list')
    allowed={'CAkSound','CAkActorMixer','CAkActionPlay','CAkActionStop','CAkEvent'}
    if {node.get('name') for node in items}-allowed:raise ValueError('Unsupported source hierarchy objects')
    records=[];ids=set();event_ids=set()
    for node in items:
        name=node.get('name');ident=int(field(node,'ulID'));ids.add(ident)
        body=struct.pack('<I',ident)
        if name=='CAkSound':
            mid=int(field(node,'sourceID'));assert mid in converted
            params,parent=node_params(node)
            # Wwise <=88 uses source type 1 for external streaming; the cache
            # resolves numeric .wem IDs. The small bank never loads all PCM.
            body+=struct.pack('<4I',0x00040001 if a.codec=='vorbis' else 0x00010001,1,mid,mid)+b'\0'+params
            kind=2
        elif name=='CAkActorMixer':
            params,parent=node_params(node)
            children=[int(f.get('value')) for f in node.findall('.//object[@name="Children"]/field[@name="ulChildID"]')]
            body+=params+struct.pack('<I',len(children))+b''.join(struct.pack('<I',x) for x in children);kind=7
        elif name.startswith('CAkAction'):
            target=int(field(node,'idExt'));action=int(field(node,'ulActionType'));assert action in (0x0403,0x0103)
            body+=struct.pack('<HI',action,target)+b'\0\0\0\4'
            if name=='CAkActionPlay':body+=struct.pack('<I',bank_id)
            else:body+=struct.pack('<I',0)
            kind=3
        else:
            actions=[int(x.get('value')) for x in node.findall('.//field[@name="ulActionID"]')]
            body+=struct.pack('<I',len(actions))+b''.join(struct.pack('<I',x) for x in actions);kind=4;event_ids.add(ident)
        records.append(object_record(kind,body))
    assert len(ids)==len(records)
    result=chunk(b'BKHD',header)+chunk(b'HIRC',struct.pack('<I',len(records))+b''.join(records))
    bank=out/'BetaGwent79.bnk';bank.write_bytes(result);(bankdir/bank.name).write_bytes(result)
    listing='Streamed Audio\tID\tName\tAudio source file\t\tWwise Object Path\tNotes\tData Size\n'
    listing+=''.join(f'\t{mid}\t{mid}\t{bankdir / (str(mid)+".wem")}\t\t\\BetaGwent79\\{mid}\t\t{len(payload)}\n' for mid,payload in converted.items())
    (bankdir/'BetaGwent79.txt').write_text(listing,'utf8')
    report=dict(sourceBankSha256=hashlib.sha256(source).hexdigest(),bankVersion=88,bankId=bank_id,
                bytes=len(result),sha256=hashlib.sha256(result).hexdigest(),mediaCount=len(media),
                eventCount=len(event_ids),eventIds=sorted(event_ids),sourceMedia=metrics,
                pcm16=a.codec=='pcm',audioCodec=a.codec,vorbisQuality=a.quality if a.codec=='vorbis' else None,streamedMedia=True,streamedBytes=sum(map(len,converted.values())),noInitBank=True,nativePlaybackVerified=False)
    (out/'audio.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({k:report[k] for k in ['bankVersion','bytes','mediaCount','eventCount']},indent=2),flush=True)


if __name__=='__main__':main()

"""Retain Classic Vorbis payloads but use the stock embedded-bank source route."""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import sound_index,write_sound_cache,sha
from build_audio import chunks,chunk,object_record

BUILD=ROOT/'BetaGwent/build/classic081-geometry-effects-fix14'
SOURCE=ROOT/'BetaGwent/build/universal081/audio-classic/soundspc.cache'


def main():
    out=BUILD/'audio';assert not out.exists(),'Fresh audio output required'
    out.mkdir();banks=out/'banks';banks.mkdir()
    _,index=sound_index(SOURCE)
    with SOURCE.open('rb') as f:
        off,size=index['betagwent79.bnk'];f.seek(off);parts=dict(chunks(f.read(size)))
        bankid=struct.unpack_from('<I',parts[b'BKHD'],4)[0]
        hirc=parts[b'HIRC'];count=struct.unpack_from('<I',hirc)[0];pos=4
        records=[];didx=bytearray();data=bytearray();media={};changed=0
        for _ in range(count):
            kind,size=struct.unpack_from('<BI',hirc,pos);pos+=5;body=hirc[pos:pos+size];pos+=size
            if kind==2:
                plugin,stream,mid,fileid=struct.unpack_from('<4I',body,4)
                assert stream==1 and mid==fileid and plugin==0x40001
                if mid not in media:
                    mo,ms=index[str(mid)+'.wem'];f.seek(mo);payload=f.read(ms);assert len(payload)==ms
                    data+=b'\0'*((-len(data))%16);offset=len(data);data+=payload
                    didx+=struct.pack('<III',mid,offset,ms);media[mid]=(offset,ms,hashlib.sha256(payload).hexdigest())
                offset,ms,_=media[mid]
                # Wwise 88 stock gui.bnk: embedded sources include the bank ID,
                # DATA-relative offset and size. The remaining parameters stay exact.
                body=body[:8]+struct.pack('<5I',0,mid,bankid,offset,ms)+body[20:]
                changed+=1
            records.append(object_record(kind,body))
        assert pos==len(hirc) and changed>0 and len(media)==len(index)-1
    header=parts[b'BKHD'][:20]
    header+=b'\0'*((-(8+len(header)+8+len(didx)+8))%16)
    bank=chunk(b'BKHD',header)+chunk(b'DIDX',didx)+chunk(b'DATA',data)+chunk(b'HIRC',struct.pack('<I',count)+b''.join(records))
    target=banks/'betagwent79.bnk';target.write_bytes(bank)
    checked=dict(chunks(bank));assert checked[b'DIDX']==didx and checked[b'DATA']==data
    for mid,(offset,size,digest) in media.items():assert hashlib.sha256(checked[b'DATA'][offset:offset+size]).hexdigest()==digest
    cache=out/'soundspc.cache';cacheReport=write_sound_cache(banks,cache)
    report=dict(sourceSha256=sha(SOURCE),bankSha256=sha(target),bankBytes=len(bank),bankVersion=88,
        sourcesChanged=changed,mediaCount=len(media),mediaBytesUnchanged=True,hierarchyAndEventIdsUnchanged=True,
        embeddedMedia=True,streamedMedia=False,codec='vorbis',nativePlaybackVerified=False,cache=cacheReport)
    (out/'audio.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report,indent=2))


if __name__=='__main__':main()

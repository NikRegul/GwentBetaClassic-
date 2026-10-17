from pathlib import Path
import hashlib,json,struct,sys,xml.etree.ElementTree as ET
ROOT=Path('D:/w3mod');BASE=ROOT/'BetaGwent/build/universal081'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import write_sound_cache,sound_index,fnv64,sha,require
from build_audio import chunks,chunk
def main():
 raw=(BASE/'audio-merged/BetaGwent79.bnk').read_bytes();parts=dict(chunks(raw));pos=0
 while raw[pos:pos+4]!=b'HIRC':pos+=8+struct.unpack_from('<I',raw,pos+4)[0]
 payload_start=pos+8;hirc=bytearray(parts[b'HIRC']);tree=ET.parse(BASE/'audio-merged/merged.xml')
 count=0
 for node in tree.findall('.//object[@name="CAkSound"]'):
  f=node.find('.//field[@name="StreamType"]');off=int(f.get('offset'))-payload_start;require(hirc[off]==0,'Expected embedded source');hirc[off]=2
  f=node.find('.//field[@name="uInMemoryMediaSize"]');struct.pack_into('<I',hirc,int(f.get('offset'))-payload_start,0);count+=1
 bankdir=BASE/'audio-nextgen/banks/Windows';bankdir.mkdir(parents=True,exist_ok=True)
 (bankdir/'BetaGwent79.bnk').write_bytes(chunk(b'BKHD',parts[b'BKHD'])+chunk(b'HIRC',hirc))
 for mid,off,size in struct.iter_unpack('<III',parts[b'DIDX']):(bankdir/(str(mid)+'.wem')).write_bytes(parts[b'DATA'][off:off+size])
 files=sorted(bankdir.glob('*.bnk'))+sorted(bankdir.glob('*.wem'));names=bytearray();table=bytearray();cursor=64
 for path in files:
  table+=struct.pack('<QQQ',len(names),cursor,path.stat().st_size);names+=path.name.lower().encode()+b'\0';cursor+=path.stat().st_size
 source=ROOT/'BetaGwent/build/release202/ru/package/Mods/modBetaGwent0924/content/soundspc.cache'
 header=bytearray(source.read_bytes()[:64]);struct.pack_into('<QQQI',header,16,cursor+len(names),len(files),cursor,len(names))
 struct.pack_into('<QQ',header,48,(max(p.stat().st_size for p in files)+4095)&~4095,fnv64(names+table))
 cache=BASE/'audio-nextgen/soundspc.cache'
 with cache.open('wb') as f:
  f.write(header)
  for p in files:
   with p.open('rb') as src:
    import shutil;shutil.copyfileobj(src,f)
  f.write(names);f.write(table)
 version,index=sound_index(cache);require(version==2 and len(index)==len(files),'Next-Gen cache index')
 with cache.open('rb') as f:
  for path in files:
   off,size=index[path.name.lower()];f.seek(off);require(hashlib.sha256(f.read(size)).hexdigest()==sha(path),'Next-Gen cache payload mismatch')
 classic=BASE/'audio-classic/soundspc.cache';report=write_sound_cache(BASE/'audio-classic/banks/Windows',classic)
 report.update(bytes=classic.stat().st_size,audioCodec='vorbis');(BASE/'audio-classic/sound-cache.json').write_text(json.dumps(report,indent=2))
 report=dict(nextgenBytes=cache.stat().st_size,classicBytes=classic.stat().st_size,streamedSounds=count,media=len(files)-1,nativePlaybackVerified=False)
 (BASE/'audio-caches.json').write_text(json.dumps(report,indent=2));print(report)
if __name__=='__main__':main()

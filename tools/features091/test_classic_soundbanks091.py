"""Regression: the Classic bundle must carry the 1.32 always-load bank list (Seven Cats hang)."""
import struct, sys, zipfile, zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import classic_soundbanks091 as c

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_ARCHIVES
BASE=BASE_ARCHIVES/'GwentBetaClassic-0.9.0-1.32-AllLanguages.zip'

def entry(raw):
    count=struct.unpack_from('<I',raw,16)[0]
    for pos in range(32,32+count,320):
        if raw[pos:pos+256].split(b'\0')[0]==c.ENTRY:
            size,_,offset=struct.unpack_from('<III',raw,pos+276);crc=struct.unpack_from('<I',raw,pos+312)[0]
            return raw[offset:offset+size],crc,pos
    raise AssertionError('missing entry')

def main():
    with zipfile.ZipFile(BASE) as z:raw=z.read('Mods/modBetaGwentClassic132/content/blob0.bundle')
    old,_,_=entry(raw);assert all(b in c.banks(old) for b in c.NEXTGEN_ONLY),'base archive should show the defect'
    fixed=c.fix_bundle(raw);new,crc,pos=entry(fixed)
    assert len(fixed)==len(raw) and zlib.crc32(new)==crc
    listed=c.banks(new);vanilla=c.banks(c.VANILLA.read_bytes())
    assert listed==vanilla and c.GWENT_BANK not in listed and not any(b in listed for b in c.NEXTGEN_ONLY)
    # Only the list payload and its CRC change.
    changed=[i for i,(a,b) in enumerate(zip(raw,fixed)) if a!=b]
    _,_,offset=struct.unpack_from('<III',raw,pos+276)
    assert all(offset<=i<offset+len(new) or pos+312<=i<pos+316 for i in changed)
    assert c.fix_bundle(fixed)==fixed
    print('PASS classic soundbank list: vanilla 1.32 (%d banks), betagwent79 on demand only, %d bytes changed'%(len(vanilla),len(changed)))

if __name__=='__main__':main()

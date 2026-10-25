"""Read real OpenType cmaps; check new UI strings against shipped font subsets."""
from pathlib import Path
import argparse,hashlib,json,struct
ROOT=Path(__file__).resolve().parents[2]

def points(path):
    raw=path.read_bytes();u16=lambda p:struct.unpack_from('>H',raw,p)[0];u32=lambda p:struct.unpack_from('>I',raw,p)[0]
    tables={raw[p:p+4]:u32(p+8) for p in range(12,12+16*u16(4),16)}
    base=tables[b'cmap'];result=set()
    for entry in range(base+4,base+4+8*u16(base+2),8):
        platform,encoding=struct.unpack_from('>HH',raw,entry)
        if platform!=0 and not(platform==3 and encoding in [1,10]):continue
        sub=base+u32(entry+4);kind=u16(sub)
        if kind==12:
            for p in range(sub+16,sub+16+12*u32(sub+12),12):
                start,end,glyph=struct.unpack_from('>III',raw,p)
                result.update(c for c in range(start,end+1) if glyph+c-start)
        elif kind==4:
            count=u16(sub+6)//2;ends=sub+14;starts=ends+count*2+2;deltas=starts+count*2;offsets=deltas+count*2
            for i in range(count):
                delta=u16(deltas+i*2);offset=u16(offsets+i*2)
                for c in range(u16(starts+i*2),min(65534,u16(ends+i*2))+1):
                    glyph=u16(offsets+i*2+offset+2*(c-u16(starts+i*2))) if offset else c
                    if glyph and ((glyph+delta)&65535):result.add(c)
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);a=p.parse_args()
    data=json.loads((ROOT/'data/beta924/design/release093_ui.json').read_text('utf8'));records=[]
    for i,code in enumerate(data['languages']):
        chars={ord(c) for row in [*data['text'].values(),*data['opponents'].values()] for c in row[i] if not c.isspace()}
        directory=ROOT/'BetaGwent/build-inputs/authoring/languages137/fonts/prepared'/code
        faces=json.loads((directory/'plan.json').read_text('utf8'))['faces']
        for role,face in faces.items():
            font=directory/face['file'];missing=chars-points(font)
            assert not missing,(code,role,''.join(map(chr,sorted(missing))))
            records.append(dict(language=code,face=role,font=font.name,sha256=hashlib.sha256(font.read_bytes()).hexdigest(),characters=len(chars),missing=0))
    report=dict(languages=13,complete=True,records=records,scope='Actual permanent shipped OpenType font subsets; new offer labels and opponent names only, not a native-game screenshot check.')
    a.out.write_text(json.dumps(report,indent=2)+'\n','utf8');print('PASS all13languages,',len(records),'real font faces')

if __name__=='__main__':main()

"""Read-only list of Beta Gwent fact names, including orphaned NPC reward keys.

SNFH/FZLC layout reference (independent implementation):
https://github.com/Atvaark/W3SavegameEditor/tree/master/W3SavegameEditor.Core/ChunkedLz4
Does not edit, repack or upload saves. No third-party dependencies.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct
LIMIT=256*1024*1024
def lz4(block,expected):
    if not 0<expected<=LIMIT:raise ValueError('Invalid decompressed size')
    out=bytearray();pos=0
    def length(base):
        nonlocal pos
        value=base
        if base==15:
            while True:
                if pos>=len(block):raise ValueError('Truncated LZ4 length')
                extra=block[pos];pos+=1;value+=extra
                if extra<255:break
        return value
    while pos<len(block):
        token=block[pos];pos+=1;n=length(token>>4)
        if pos+n>len(block) or len(out)+n>expected:raise ValueError('Invalid LZ4 literals')
        out.extend(block[pos:pos+n]);pos+=n
        if pos==len(block):break
        if pos+2>len(block):raise ValueError('Truncated LZ4 offset')
        distance=int.from_bytes(block[pos:pos+2],'little');pos+=2;n=length(token&15)+4
        if distance<=0 or distance>len(out) or len(out)+n>expected:raise ValueError('Invalid LZ4 match')
        for i in range(n):out.append(out[-distance])
    if len(out)!=expected:raise ValueError('Decompressed size differs from header')
    return bytes(out)
def unpack(data):
    if not data.startswith(b'SNFHFZLC'):raise ValueError('Only SNFH/FZLC PC saves are supported')
    if len(data)<16:raise ValueError('Truncated save header')
    count,header=struct.unpack_from('<II',data,8)
    if not 1<=count<=65536 or not 16+count*12<=header<=len(data):raise ValueError('Invalid chunk table')
    chunks=[struct.unpack_from('<III',data,16+i*12) for i in range(count)]
    if sum(n for _,n,_ in chunks)>LIMIT:raise ValueError('Save exceeds read-only scanner budget')
    result=bytearray();pos=header
    for compressed,size,end in chunks:
        if compressed==0 or pos+compressed>len(data) or end not in (0,pos+compressed):raise ValueError('Invalid chunk bounds')
        result.extend(lz4(data[pos:pos+compressed],size));pos+=compressed
    if pos!=len(data):raise ValueError('Unexpected trailing save data')
    return bytes(result)
def names(data):
    # Fact identifiers are ASCII strings in the decompressed save. Include both
    # serializations; never infer/remove native quest keys from nearby bytes.
    values=set()
    pattern=rb'(?<![A-Za-z0-9_])(?:bg_[A-Za-z0-9_\-]+|betagwent_[A-Za-z0-9_\-]+)(?![A-Za-z0-9_])'
    for blob in (data,data[::2] if data.count(b'\0')>len(data)//8 else b'',data[1::2] if data.count(b'\0')>len(data)//8 else b''):
        for item in re.findall(pattern,blob):
            if len(item)<=120:values.add(item.decode('ascii'))
    return sorted(values)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('save',type=Path);parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    source=args.save.resolve();output=args.out.resolve()
    if output==source or output.suffix.lower()=='.sav':parser.error('Output must be a new .txt file, never a save')
    raw=source.read_bytes();keys=names(unpack(raw))
    # Small batches work with the standalone mod's checked string-list command.
    commands=['bg_clean_keys('+json.dumps('|'.join(keys[i:i+12]))+')' for i in range(0,len(keys),12)]
    with output.open('x',encoding='utf8') as stream:stream.write('\n'.join(commands)+'\n')
    output.with_suffix(output.suffix+'.json').write_text(json.dumps(dict(saveSha256=hashlib.sha256(raw).hexdigest(),facts=keys,saveModified=False),indent=2),'utf8')
    print('Read-only scan:',len(keys),'Beta Gwent identifiers;',len(commands),'console batches ->',output)
if __name__=='__main__':main()

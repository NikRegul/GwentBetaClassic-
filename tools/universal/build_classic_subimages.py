"""Bind Classic UI classes to native GFx atlas rectangles without new pixels."""
import json
from pathlib import Path
import re
import struct
import zlib

import build_classic_bitmap_fix as base
from install_native_hd93 import symbols, tag
from update_board_resource import movie_parts
from formats import require

ROOT = base.ROOT
BUILD = ROOT / 'BetaGwent/build/classic081-subimages-fix12'
DEFINITION_TAGS = {2,6,7,10,11,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008}


def add_fragments(movie):
    entries = json.loads((BUILD/'subimages.json').read_text('utf8'))['entries']
    source = (BUILD/'ui/src/BetaGwentHDArt.as').read_text('utf-8-sig')
    pages = {int(page): Path(name).stem.encode('ascii')+b'_png' for name,page in
             re.findall(r'\[Embed\(source="([^"]+)"[^\]]*\)\] private static var Page(\d+):Class;',source)}
    # Optional pre-existing particle sheets use the same native rectangle path.
    # Older UI-only manifests have no atlas overrides and retain their IDs.
    pages.update({row['page']:row['atlas'].encode('ascii') for row in entries if row.get('atlas')})
    prefix,tags,tail = movie_parts(movie)
    bindings=symbols(tags)
    images={struct.unpack_from('<H',p)[0]:struct.unpack('<6H',p) for c,p,_ in tags if c==1008}
    page_images={}
    for page, stem in pages.items():
        ids=[ident for ident,name in bindings.items() if name.split(b'$')[0]==stem]
        require(len(ids)<=1,'Ambiguous atlas class')
        if ids:
            require(ids[0] in images,'Atlas class has no native image definition')
            page_images[page]=images[ids[0]]
    next_id=1+max(struct.unpack_from('<H',p)[0] for c,p,_ in tags if c in DEFINITION_TAGS)
    generated, rows, mapping = [], [], bytearray()
    for row in entries:
        if row['page'] not in page_images:continue
        _, image, bx,by,bw,bh=page_images[row['page']]
        require(bx==by==0,'Expected an unpacked original atlas')
        x,y,w,h=(row[k] for k in ('x','y','width','height'))
        require(0<=x<x+w<=bw and 0<=y<y+h<=bh,'Fragment leaves atlas')
        require(next_id<65536,'Native character ID overflow')
        payload=struct.pack('<6H',next_id,image,x,y,x+w,y+h)
        generated.append(tag(1008,payload))
        mapping+=struct.pack('<H',next_id)+row['className'].encode('ascii')+b'\0'
        rows.append(dict(row,characterId=next_id,imageId=image))
        next_id+=1
    require(rows,'Movie has no UI fragments')
    generated.append(tag(76,struct.pack('<H',len(rows))+mapping))
    inserted=False;body=bytearray(prefix)
    for code,payload,raw in tags:
        if code==82:
            require(not inserted,'Multiple ABC blocks')
            body+=b''.join(generated);inserted=True
        body+=raw
    require(inserted,'No ABC insertion point')
    require(movie[:3]==b'CFX','Expected compressed native GFx')
    result=movie[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    checked=movie_parts(result)[1];checked_symbols=symbols(checked)
    require(all(checked_symbols.get(ident)==name for ident,name in bindings.items()),'Original image/font bindings changed')
    require(next(p for c,p,_ in checked if c==82)==next(p for c,p,_ in tags if c==82),'Compiled bytecode changed')
    definitions={struct.unpack_from('<H',p)[0]:p for c,p,_ in checked if c==1008}
    for row in rows:
        require(checked_symbols[row['characterId']]==row['className'].encode('ascii'),'Lost fragment class')
        require(struct.unpack('<6H',definitions[row['characterId']])==(
            row['characterId'],row['imageId'],row['x'],row['y'],row['x']+row['width'],row['y']+row['height']),
            'Wrong native fragment bounds')
    root=bindings[0].decode('ascii')
    (BUILD/(root+'-subimages.json')).write_text(json.dumps(dict(root=root,entries=rows,originalBindingsPreserved=True,
        bitmapPixelsUnchanged=True,nativeRectanglesVerified=True),indent=2),'utf8')
    return result


def main():
    base.BUILD=BUILD
    base.SOURCE=ROOT/'BetaGwent/build/classic081-bitmap-fix11'
    base.VERSION='0.8.1-classic-native-subimages-fix12'
    base.ARCHIVE_NAME='GwentBetaClassic-0.8.1-1.32-fix12-SubimagesPatch.zip'
    base.edit_movie=add_fragments
    base.main()


if __name__=='__main__':main()

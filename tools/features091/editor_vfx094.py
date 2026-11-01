"""Bounded editor atlas extension and Classic native frame bindings.

All original texture blocks are copied verbatim. Only the exact reviewed
Elements atlas receives extra BC3 rows; no existing rectangles move.
"""
from pathlib import Path
import hashlib,json,struct,sys,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui'),str(ROOT/'tools/universal')]
from formats import Resource
from build_classic_bitmap_fix import native
from update_board_resource import movie_parts
from install_native_hd93 import symbols,tag

sha=lambda data:hashlib.sha256(data).hexdigest()
FOLDERS=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']

def write_as(ui,name,text):
    raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
    for folder in FOLDERS:(ui/folder/name).write_bytes(raw)

def prepare(ui,platform,base):
    import shutil
    from PIL import Image
    spec=ROOT/'data/beta924/design/editor_vfx094.json'
    if not spec.exists():return None
    data=json.loads(spec.read_text('utf8'));image=ROOT/'BetaGwent/ui/assets/elements164/Elements.png'
    assert sha(image.read_bytes())==data['extendedAtlasSha256']
    previous=base/'ui/assets/elements164/Elements.png'
    assert sha(previous.read_bytes())==data['baseAtlasSha256']
    before=Image.open(previous).convert('RGBA');after=Image.open(image).convert('RGBA')
    assert list(before.size)==data['baseSize'] and after.crop((0,0,*before.size)).tobytes()==before.tobytes()
    shutil.copy2(image,ui/'assets/elements164/Elements.png')
    target=ui/'assets/editor094';target.mkdir()
    source=ROOT/'BetaGwent/ui/assets/editor094/append-bc3.bin';assert sha(source.read_bytes())==data['appendedBlocksSha256']
    shutil.copy2(source,target/source.name)
    if platform=='classic':
        path=ui/'src/BetaGwentClassicEffects.as';text=path.read_text('utf-8-sig')
        marker='private static var classes:Object={'
        assert text.count(marker)==1
        entries=','.join('"editor:%d":BetaGwentEditorFxCell094_%d'%(i,i) for i in range(len(data['rects'])))+','
        write_as(ui,path.name,text.replace(marker,marker+entries))
        for i in range(len(data['rects'])):
            write_as(ui,'BetaGwentEditorFxCell094_%d.as'%i,
              'package { import mx.core.BitmapAsset; public class BetaGwentEditorFxCell094_%d extends BitmapAsset {public function BetaGwentEditorFxCell094_%d(){super();}}}'%(i,i))
        path=ui/'src/BetaGwentElementArt164.as';text=path.read_text('utf-8-sig')
        marker='public static function region(index:int,rect:Array,w:Number,h:Number):Sprite {'
        assert text.count(marker)==1
        addition='\n            var nativeCell:Sprite=BetaGwentClassicEffects.view("editor:"+index,w,h);\n            if(nativeCell){nativeCell.x=-w/2;nativeCell.y=-h/2;var centeredCell:Sprite=new Sprite();centeredCell.mouseEnabled=false;centeredCell.mouseChildren=false;centeredCell.addChild(nativeCell);return centeredCell;}'
        write_as(ui,path.name,text.replace(marker,marker+addition))
    (ui/'editor_vfx094.json').write_text(json.dumps(data,indent=2)+'\n','utf8')
    return dict(specSha256=sha(spec.read_bytes()),extendedAtlasSha256=data['extendedAtlasSha256'],
                appendedBlocksSha256=data['appendedBlocksSha256'],baseSize=data['baseSize'],size=data['size'],frames=len(data['rects']))

def extend_resource(raw,data,blocks,classic):
    assert sha(blocks)==data['appendedBlocksSha256']
    old=Resource(raw);pos,movie=native(old);prefix,tags,tail=movie_parts(movie);bindings=symbols(tags)
    candidates=[k for k,v in bindings.items() if v.split(b'$')[0]==b'Elements_png'];assert len(candidates)==1
    cid=candidates[0]
    ident,image,x,y,w,h=next(struct.unpack('<6H',d) for c,d,r in tags if c==1008 and struct.unpack_from('<H',d)[0]==cid)
    assert [w,h]==data['baseSize'] and x==y==0
    info=next(d for c,d,r in tags if c==1009 and struct.unpack_from('<H',d)[0]==image)
    off=11+info[10];linkage=info[off+1:];assert len(linkage)==info[off]
    found=[]
    for index,chunk in enumerate(old.chunks[1:],1):
        props,offset=old.properties(chunk)
        name=next(v[1:] for n,t,v in props if old.names[n]=='linkageName')
        if name==linkage:found.append((index,chunk,props,offset))
    assert len(found)==1
    index,chunk,props,offset=found[0];header=list(struct.unpack_from('<6I',chunk,offset))
    assert header==[0,1,w,h,w*4,w*h],header
    cooked=old.records[index][1]==8192;pixel_offset=offset+28 if cooked else offset+24
    if cooked:assert chunk[offset+24:offset+28]==struct.pack('<HH',16,0)
    else:assert chunk[-4:]==b'\0'*4
    old_pixels=chunk[pixel_offset:pixel_offset+w*h];assert len(old_pixels)==w*h
    nw,nh=data['size'];assert nw==w and len(blocks)==w*(nh-h)
    properties=bytearray(chunk[:offset]);cursor=1
    while properties[cursor:cursor+2]!=b'\0\0':
        n,t,size=struct.unpack_from('<HHI',properties,cursor)
        if old.names[n]=='height':assert struct.unpack_from('<I',properties,cursor+8)[0]==h;struct.pack_into('<I',properties,cursor+8,nh)
        cursor+=4+size
    header[3]=nh;header[5]=nw*nh
    extended=bytes(properties)+struct.pack('<6I',*header)+(struct.pack('<HH',16,0) if cooked else b'')+old_pixels+blocks+(b'' if cooked else b'\0'*4)
    new_chunks=old.chunks[:];new_chunks[index]=extended
    definitions={2,6,7,10,11,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008}
    next_id=1+max(struct.unpack_from('<H',d)[0] for c,d,r in tags if c in definitions)
    extras=[];mapping=bytearray()
    if classic:
        for i,(rx,ry,rw,rh) in enumerate(data['rects']):
            assert rx>=0 and ry>=h and rx+rw<=nw and ry+rh<=nh and next_id<65536
            extras.append(tag(1008,struct.pack('<6H',next_id,image,rx,ry,rx+rw,ry+rh)))
            mapping+=struct.pack('<H',next_id)+('BetaGwentEditorFxCell094_%d'%i).encode()+b'\0';next_id+=1
        extras.append(tag(76,struct.pack('<H',len(data['rects']))+mapping))
    body=bytearray(prefix)
    for code,payload,encoded in tags:
        if code==1009 and struct.unpack_from('<H',payload)[0]==image:
            value=bytearray(payload);struct.pack_into('<HH',value,6,nw,nh);encoded=tag(code,value)
        elif code==1008 and struct.unpack_from('<H',payload)[0]==cid:
            encoded=tag(code,struct.pack('<6H',cid,image,0,0,nw,nh))
        if code==82:body+=b''.join(extras)
        body+=encoded
    updated=movie[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    new_chunks[0]=old.chunks[0][:pos]+struct.pack('<I',len(updated))+updated+struct.pack('<I',0)
    result=old.replace_chunks(new_chunks);checked=Resource(result)
    assert checked.imports==old.imports and checked.records[index][0]==old.records[index][0]
    assert checked.chunks[index][pixel_offset:pixel_offset+w*h]==old_pixels
    assert all(checked.chunks[i]==old.chunks[i] for i in range(1,len(old.chunks)) if i!=index)
    after=symbols(movie_parts(native(checked)[1])[1]);assert all(after[k]==v for k,v in bindings.items())
    return result,dict(originalBlocksSha256=sha(old_pixels),originalBlockBytes=len(old_pixels),
                       appendedBytes=len(blocks),textureChunk=index,classicFrameBindings=len(data['rects']) if classic else 0,
                       originalOtherTexturesPreserved=True,existingNativeBindingsPreserved=True)

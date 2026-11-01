"""Beta picker artwork in unused page-18 cells; native DDS length never changes.

Original card/deck cells and every BC3 block outside the new rectangles survive
verbatim. Classic receives real DefineSubImage bindings, not atlas scrollRects.
"""
from pathlib import Path
import hashlib, io, json, re, struct, sys, zlib
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT/'tools/features091'), str(ROOT/'tools/ui')]
from editor_vfx094 import write_as
from build_classic_bitmap_fix import native
from formats import Resource
from update_board_resource import movie_parts
from install_native_hd93 import symbols, tag
sha = lambda b: hashlib.sha256(b).hexdigest()
SPEC = ROOT/'data/beta924/design/window_art098.json'
ASSET = ROOT/'BetaGwent/ui/assets/windows098'

def bleed_transparent_rgb099(image):
    """BC3 colour fitting ignores alpha. Extend visible RGB into low-alpha texels."""
    import numpy as np
    from PIL import Image
    data=np.array(image.convert('RGBA'));rgb=data[:,:,:3].astype('float32')
    known=data[:,:,3]>=max(1,float(data[:,:,3].max())*.75)
    if not known.any():return image
    for _ in range(image.width+image.height):
        if known.all():break
        sums=np.zeros_like(rgb);counts=np.zeros(known.shape,dtype='float32')
        for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:
            mask=np.roll(known,(dy,dx),(0,1));values=np.roll(rgb,(dy,dx),(0,1))
            if dy==1:mask[0,:]=False
            if dy==-1:mask[-1,:]=False
            if dx==1:mask[:,0]=False
            if dx==-1:mask[:,-1]=False
            sums+=values*mask[:,:,None];counts+=mask
        fill=(~known)&(counts>0);rgb[fill]=sums[fill]/counts[fill,None];known|=fill
    data[:,:,:3]=np.rint(rgb).astype('uint8');return Image.fromarray(data)

def prepare(ui, platform, base):
    import shutil
    data = json.loads(SPEC.read_text('utf8'))
    image = ROOT/'BetaGwent/ui/assets/battle104/deckscreens104.png'
    assert sha(image.read_bytes()) == data['atlasSha256']
    assert sha((base/'ui/assets/battle104/deckscreens104.png').read_bytes()) == data['baseAtlasSha256']
    shutil.copy2(image, ui/'assets/battle104/deckscreens104.png')
    dest = ui/'assets/windows098'; dest.mkdir(exist_ok=True)
    shutil.copy2(ASSET/'blocks.bin', dest/'blocks.bin')
    (ui/'window_art098.json').write_text(json.dumps(data, indent=2)+'\n', 'utf8')
    for i in range(len(data['nativeRects'])+len(data.get('paperRects',[]))):
        write_as(ui, 'BetaGwentWindowCell098_%d.as'%i,
            'package { import mx.core.BitmapAsset; public class BetaGwentWindowCell098_%d extends BitmapAsset { public function BetaGwentWindowCell098_%d(){super();}}}'%(i,i))

def patch_resource(raw, data, blocks, classic):
    assert sha(blocks) == data['blocksSha256']
    old = Resource(raw); pos, movie = native(old); prefix, tags, tail = movie_parts(movie); names = symbols(tags)
    cid, = [k for k,v in names.items() if v.split(b'$')[0] == b'deckscreens104_png']
    _, image, x, y, w, h = next(struct.unpack('<6H',d) for c,d,r in tags if c==1008 and struct.unpack_from('<H',d)[0]==cid)
    assert [x,y,w,h] == [0,0,*data['size']]
    info = next(d for c,d,r in tags if c==1009 and struct.unpack_from('<H',d)[0]==image)
    off = 11+info[10]; linkage = info[off+1:]
    found = []
    for i,chunk in enumerate(old.chunks[1:],1):
        props,offset = old.properties(chunk)
        if any(old.names[n]=='linkageName' and v[1:]==linkage for n,t,v in props): found.append((i,chunk,offset))
    (index,chunk,offset), = found
    cooked = old.records[index][1]==8192; pixel_offset = offset+(28 if cooked else 24)
    assert list(struct.unpack_from('<6I',chunk,offset)) == [0,1,w,h,w*4,w*h]
    before = chunk[pixel_offset:pixel_offset+w*h]; after = bytearray(before); touched = set(); cursor = 0
    for x,y,rw,rh in data['rects']:
        for row in range(rh//4):
            dest = (((y//4)+row)*(w//4)+x//4)*16; size = rw//4*16
            after[dest:dest+size] = blocks[cursor:cursor+size]; cursor += size
            touched.update(range(dest//16,(dest+size)//16))
    assert cursor == len(blocks) and len(before)==len(after)
    assert all(before[i:i+16]==after[i:i+16] for i in range(0,len(before),16) if i//16 not in touched)
    chunks = old.chunks[:]; chunks[index] = chunk[:pixel_offset]+bytes(after)+chunk[pixel_offset+w*h:]
    extras = []
    if data['nativeRects']:
        bindings_rects=[(image,r) for r in data['nativeRects']]
        if data.get('paperRects'):
            hud_cid, = [k for k,v in names.items() if v.split(b'$')[0]==b'hud126_png']
            hud_image = next(struct.unpack('<6H',d)[1] for c,d,r in tags if c==1008 and struct.unpack_from('<H',d)[0]==hud_cid)
            bindings_rects += [(hud_image,r) for r in data['paperRects']]
        definitions = {2,6,7,10,11,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008}
        ident = 1+max(struct.unpack_from('<H',d)[0] for c,d,r in tags if c in definitions)
        bindings = bytearray()
        for i,(atlas,(x,y,rw,rh)) in enumerate(bindings_rects):
            extras.append(tag(1008,struct.pack('<6H',ident,atlas,x,y,x+rw,y+rh)))
            bindings += struct.pack('<H',ident)+('BetaGwentWindowCell098_%d'%i).encode()+b'\0'; ident += 1
        extras.append(tag(76,struct.pack('<H',len(bindings_rects))+bindings))
    body = prefix+b''.join((b''.join(extras) if c==82 else b'')+r for c,d,r in tags)
    updated = movie[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    chunks[0] = old.chunks[0][:pos]+struct.pack('<I',len(updated))+updated+struct.pack('<I',0)
    result = old.replace_chunks(chunks)
    checked = Resource(result)
    assert all(checked.chunks[i]==old.chunks[i] for i in range(1,len(chunks)) if i!=index)
    return result, {'textureBytesAdded':0,'patchedUnusedBlocks':len(touched),'otherTexturesPreserved':True,'nativeBindings':len(bindings_rects)}

def generate():
    import numpy as np
    from PIL import Image
    sys.path.insert(0,str(ROOT/'tools/vendor/audio-python')); import UnityPy
    assert not SPEC.exists(), 'Already generated; keep reviewed assets immutable'
    ASSET.mkdir(parents=True,exist_ok=True)
    source = ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber'
    wanted = {'gamebackgrounds':['vs_ranked_play_season_left','vs_ranked_play_season_right'], 'banners':['Banner_Default'],
              'cardpicker':['paper_slot','default_icon_crown'], 'shared':['scrollbar_handle','divider_metal_vertical']}
    images = {}; provenance = {}
    for bundle,items in wanted.items():
        path = source/bundle
        for o in UnityPy.load(str(path)).objects:
            if o.type.name!='Sprite': continue
            d = o.read_typetree(); name = d['m_Name']
            if name in items:
                images[name] = o.read().image.convert('RGBA')
                provenance[name] = {'bundle':bundle,'bundleSha256':sha(path.read_bytes()),'spritePathId':o.path_id,'border':d['m_Border']}
    atlas_path = ROOT/'BetaGwent/ui/assets/battle104/deckscreens104.png'; base_raw = atlas_path.read_bytes()
    before = Image.open(io.BytesIO(base_raw)).convert('RGBA'); after = before.copy(); width,height = before.size
    hd = (ROOT/'BetaGwent/ui/src/BetaGwentHDArt.as').read_text('utf-8-sig')
    slots = json.loads(re.search(r'slots:Object=(.*);',hd)[1]); occupied = np.zeros((height,width),bool)
    for page,x,y,w,h in slots.values():
        if page==18: occupied[max(0,int(y)-4):min(height,int(y+h)+4),max(0,int(x)-4):min(width,int(x+w)+4)]=True
    rod = images['scrollbar_handle']
    cells = [('MAP_LEFT',images['vs_ranked_play_season_left'],176,160),('MAP_RIGHT',images['vs_ranked_play_season_right'],176,160),
             ('TITLE',images['Banner_Default'],320,44),('SLOT',images['paper_slot'],64,80),('CROWN',images['default_icon_crown'],48,48),
             ('ROD_TOP',rod.crop((0,0,44,115)),20,48),('ROD_MIDDLE',rod.crop((0,115,44,136)),20,12),('ROD_BOTTOM',rod.crop((0,136,44,245)),20,48),
             ('DIVIDER',images['divider_metal_vertical'],12,256)]
    rects = []; blocks = bytearray()
    for name,im,w,h in cells:
        found = None
        for y in range(4,height-h-3,4):
            for x in range(4,width-w-3,4):
                if not occupied[y-4:y+h+4,x-4:x+w+4].any(): found=(x,y);break
            if found: break
        assert found, name
        x,y = found; occupied[y-4:y+h+4,x-4:x+w+4]=True
        assert not np.array(before.crop((x,y,x+w,y+h)))[:,:,3].any(), name
        im = im.resize((w,h),Image.Resampling.LANCZOS)
        if name.startswith('MAP_'):
            a = np.array(im,dtype=np.float32);a[:,:,:3]*=[1,.5904761553,0];a[:,:,3]*=.3137255013
            im = Image.fromarray(np.rint(a).astype('uint8'))
        im=bleed_transparent_rgb099(im)
        after.paste(im,(x,y)); rects.append([x,y,w,h]); stream = io.BytesIO();im.save(stream,format='DDS',pixel_format='DXT5')
        raw = stream.getvalue();assert raw[84:88]==b'DXT5' and len(raw)==128+w*h;blocks+=raw[128:]
    for page,x,y,w,h in slots.values():
        if page==18:assert before.crop((x,y,x+w,y+h)).tobytes()==after.crop((x,y,x+w,y+h)).tobytes()
    after.save(atlas_path,optimize=True);(ASSET/'blocks.bin').write_bytes(blocks)
    # Exact native subimages of the existing wood sprite make thin frame bands safe
    # on both GFx versions; there is no added texture data for these nine cells.
    native_rects=rects+[[333+x,y,w,h] for y,h in [(0,16),(16,396),(412,16)] for x,w in [(0,16),(16,480),(496,16)]]
    paper_rects=[[0,1178,687,48],[0,1226,687,287],[0,1513,687,48]]
    data = {'schema':1,'baseAtlasSha256':sha(base_raw),'atlasSha256':sha(atlas_path.read_bytes()),'blocksSha256':sha(blocks),
            'nativeRects':native_rects,'paperRects':paper_rects,
            'size':[width,height],'rects':rects,'names':[c[0] for c in cells],'sources':provenance,'textureBytesAdded':0,'existingCellsPreserved':True}
    SPEC.write_text(json.dumps(data,indent=2)+'\n','utf8')
    text = '''package {
    import flash.display.Sprite;
    import flash.display.Bitmap;
    // Original Beta picker sprites; unused cells of the existing page-18 atlas.
    public class BetaGwentWindowArt098 {
        public static const %s;
        public static const WOOD_FIRST:int=9;
        public static const PAPER_FIRST:int=18;
        private static const RECTS:Array=%s;
        private static const TYPES:Array=[%s];
        public static function cell(id:int,w:Number,h:Number):Sprite {
            var r:Array=RECTS[id];if(!r)return null;
            var type:Class=TYPES[id];var bitmap:Bitmap=new type() as Bitmap;
            if(bitmap&&bitmap.width>0&&bitmap.height>0){
                var bound:Sprite=new Sprite();bound.mouseEnabled=false;bound.mouseChildren=false;
                bitmap.smoothing=true;bitmap.pixelSnapping="never";bitmap.scaleX=w/bitmap.width;bitmap.scaleY=h/bitmap.height;bound.addChild(bitmap);return bound;
            }
            if(id>=PAPER_FIRST)return BetaGwentHDArt.clip(BetaGwentHud104.PARCHMENT,w,h,r[0],r[1]-1178,r[2],r[3]);
            return BetaGwentHDArt.clip(BetaGwentDeckArt104.WOOD_LARGE,w,h,r[0]-333,r[1],r[2],r[3]);
        }
    }
}
''' % (','.join('%s:int=%d'%(c[0],i) for i,c in enumerate(cells)),json.dumps(native_rects+paper_rects,separators=(',',':')),','.join('BetaGwentWindowCell098_%d'%i for i in range(len(native_rects+paper_rects))))
    write_as(ROOT/'BetaGwent/ui','BetaGwentWindowArt098.as',text)
    for i in range(len(native_rects+paper_rects)):
        write_as(ROOT/'BetaGwent/ui','BetaGwentWindowCell098_%d.as'%i,
                 'package { import mx.core.BitmapAsset; public class BetaGwentWindowCell098_%d extends BitmapAsset { public function BetaGwentWindowCell098_%d(){super();}}}'%(i,i))
    print(json.dumps({'cells':len(rects),'textureBytesAdded':0,'patchBytes':len(blocks)}))

if __name__=='__main__': generate()

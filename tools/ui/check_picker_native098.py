"""Independently inspect delivered picker ABC, subimages and untouched DDS blocks."""
from pathlib import Path
import argparse, hashlib, io, json, struct, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/features091'),str(ROOT/'tools/ui'),str(ROOT/'tools/classic132'),str(ROOT/'tools/universal')]
from formats import Resource, bundle_entries
from build_classic_bitmap_fix import native
from update_board_resource import movie_parts
from install_native_hd93 import symbols
sha=lambda b:hashlib.sha256(b).hexdigest()

def texture(resource,tags,names,prefix):
    cid,=[k for k,v in names.items() if v.split(b'$')[0]==prefix]
    _,image,x,y,w,h=next(struct.unpack('<6H',d) for c,d,r in tags if c==1008 and struct.unpack_from('<H',d)[0]==cid)
    info=next(d for c,d,r in tags if c==1009 and struct.unpack_from('<H',d)[0]==image)
    pos=11+info[10];link=info[pos+1:]
    found=[]
    for i,chunk in enumerate(resource.chunks[1:],1):
        props,offset=resource.properties(chunk)
        if any(resource.names[n]=='linkageName' and v[1:]==link for n,t,v in props):
            start=offset+(28 if resource.records[i][1]==8192 else 24)
            found.append((image,i,w,h,chunk[start:start+w*h]))
    row,=found;return row

def check_bc3_colors099(pixels,width,data):
    # Decode the actual delivered BC3 blocks. PNG previews cannot detect the
    # transparent RGB colours leaking through the BC3 colour fit.
    import numpy as np
    from PIL import Image
    atlas=Image.open(ROOT/'BetaGwent/ui/assets/battle104/deckscreens104.png').convert('RGBA')
    expected=(ROOT/'BetaGwent/ui/assets/windows098/blocks.bin').read_bytes();cursor=0;proof=[]
    for name,(x,y,w,h) in zip(data['names'],data['rects']):
        blocks=b''.join(pixels[((y//4+r)*(width//4)+x//4)*16:((y//4+r)*(width//4)+(x+w)//4)*16] for r in range(h//4))
        assert blocks==expected[cursor:cursor+w*h],'Delivered picker BC3 differs: '+name
        cursor+=w*h
        stream=io.BytesIO();Image.new('RGBA',(w,h)).save(stream,format='DDS',pixel_format='DXT5')
        decoded=np.array(Image.open(io.BytesIO(stream.getvalue()[:128]+blocks)).convert('RGBA'),dtype=float)
        ref=np.array(atlas.crop((x,y,x+w,y+h)),dtype=float);alpha=ref[:,:,3]/255
        error=float((abs(decoded[:,:,:3]-ref[:,:,:3])*alpha[:,:,None]).sum()/max(1,alpha.sum())/3)
        # Crown was 8.63 before RGB bleed, now 2.41 on the native BC3 decoder.
        assert error<(4 if name=='CROWN' else 10),'Visible BC3 colour contamination: '+name
        proof.append(dict(name=name,alphaWeightedMeanRgbError=round(error,3)))
    assert cursor==len(expected)
    return proof

def main():
    p=argparse.ArgumentParser();p.add_argument('--ui',type=Path,required=True);p.add_argument('--patch',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    data=json.loads((ROOT/'data/beta924/design/window_art098.json').read_text('utf8'))
    patch=json.loads((a.patch/'manifest.json').read_text('utf8'));records=[]
    for platform,key in [('1.32','classic'),('5.0+','nextgen')]:
        source=json.loads((a.ui/key/'menus/menus.json').read_text('utf8'))['menus']
        originals={n.replace('\\','/'):r for n,r in bundle_entries(a.patch/key/'original.bundle')}
        for item in patch['platforms'][platform]['menus']:
            path=item['path'];raw=(a.patch/key/'resources'/path).read_bytes();r=Resource(raw)
            tags=movie_parts(native(r)[1])[1];names=symbols(tags)
            entry='BetaGwentKeg' if path.endswith(('panel_test.redswf','betagwent_kegop.redswf')) else 'DeckBuilder' if path.endswith(('deck_builder.redswf','betagwent_decks.redswf')) else 'GwintGame' if path.endswith(('gwint_game.redswf','betagwent_npc00.redswf')) else 'BetaGwentBoard'
            built=next(m for m in source if m['entry']==entry)
            compiled=Path(built['path']).with_suffix('.swf').read_bytes()
            abc=lambda t:next(d for c,d,rr in t if c==82)
            assert abc(tags)==abc(movie_parts(compiled)[1]),'Delivered bytecode differs: '+path
            assert len(raw)==item['bytes'] and len(raw)<(32 if key=='classic' else 65)*1024**2
            original=Resource(originals[path]);old_tags=movie_parts(native(original)[1])[1];old_names=symbols(old_tags)
            row={'platform':key,'entry':entry,'bytes':len(raw),'sha256':sha(raw),'abcMatchesCompiled':True}
            if entry!='BetaGwentKeg':
                image,index,w,h,pixels=texture(r,tags,names,b'deckscreens104_png')
                _,old_index,ow,oh,old_pixels=texture(original,old_tags,old_names,b'deckscreens104_png')
                assert (w,h)==(ow,oh)==tuple(data['size'])
                allowed=set()
                for x,y,rw,rh in data['rects']:
                    for by in range(y//4,(y+rh)//4):
                        allowed.update(range(by*(w//4)+x//4,by*(w//4)+(x+rw)//4))
                changed={i for i in range(len(pixels)//16) if pixels[i*16:i*16+16]!=old_pixels[i*16:i*16+16]}
                assert changed<=allowed,'Existing DDS cells changed: '+path
                subimages={struct.unpack_from('<H',d)[0]:struct.unpack('<6H',d) for c,d,rr in tags if c==1008}
                hud_image=texture(r,tags,names,b'hud126_png')[0]
                expected=[(image,rect) for rect in data['nativeRects']]+[(hud_image,rect) for rect in data['paperRects']]
                for i,(atlas,(x,y,rw,rh)) in enumerate(expected):
                    ident,=[k for k,v in names.items() if v==('BetaGwentWindowCell098_%d'%i).encode()]
                    assert subimages[ident]==(ident,atlas,x,y,x+rw,y+rh),'Wrong native picker UV: '+path
                assert len(pixels)==len(old_pixels)
                row.update(nativeSubimages=len(expected),ddsBytesAdded=0,changedBlocks=len(changed),allOldCellsPreserved=True)
                row['decodedBc3Colors099']=check_bc3_colors099(pixels,w,data)
            else:
                assert r.chunks[1:]==original.chunks[1:]
                row['kegTexturesPreserved']=True
            records.append(row)
    assert len(records)==8
    report={'complete':True,'menus':records,'allOldCellsPreserved':True,'newTextureBytes':0,'nativeGameTested':False}
    a.out.write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({'menus':8,'nativePickerBindings':sum(r.get('nativeSubimages',0) for r in records),'maximumBytes':max(r['bytes'] for r in records),'newTextureBytes':0}))
if __name__=='__main__':main()

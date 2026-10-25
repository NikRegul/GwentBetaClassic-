"""Replace only compiled UI code in final17 resources; preserve native art/layout."""
from pathlib import Path
import argparse, hashlib, json, shutil, struct, sys, zipfile, zlib

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from build_inputs import BASE_ARCHIVES, UI_BASELINE
sys.path[:0]=[str(ROOT/'tools/classic132'),str(ROOT/'tools/ui'),str(ROOT/'tools/universal'),str(ROOT/'tools/features082')]
from formats import Resource, bundle_entries
from build_classic_bitmap_fix import native
from update_board_resource import movie_parts
from install_native_hd93 import symbols, tag
from build_classic_streaming_fix import metadata as classic_metadata
import build_release
from classic_soundbanks091 import fix_bundle

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def movie_patch(old, template, compiled):
    prefix,tags,tail=movie_parts(old)
    old_symbols=symbols(movie_parts(template)[1]);new_tags=movie_parts(compiled)[1];new_symbols=symbols(new_tags)
    assert old_symbols.keys()==new_symbols.keys()
    assert all(old_symbols[k].split(b'$')[0]==new_symbols[k].split(b'$')[0] for k in old_symbols)
    aliases={old_symbols[k]:new_symbols[k] for k in old_symbols}
    shipping=symbols(tags)
    assert set(old_symbols.values())<=set(shipping.values()),'Shipping template differs'
    abc=next(raw for code,data,raw in new_tags if code==82)
    body=bytearray(prefix)
    for code,data,raw in tags:
        if code==82:raw=abc
        elif code==76:
            group=symbols([(code,data,raw)])
            raw=tag(76,struct.pack('<H',len(group))+b''.join(struct.pack('<H',k)+aliases.get(v,v)+b'\0' for k,v in group.items()))
        elif code==1009:
            size=data[10];name=data[11:11+size];name=aliases.get(name,name)
            raw=tag(code,data[:10]+bytes([len(name)])+name+data[11+size:])
        body+=raw
    result=old[:4]+struct.pack('<I',len(body)+8)+zlib.compress(body+tail,9)
    after=movie_parts(result)[1]
    assert [(c,d) for c,d,_ in tags if c not in (76,82,1009)]==[(c,d) for c,d,_ in after if c not in (76,82,1009)]
    assert symbols(after)=={k:aliases.get(v,v) for k,v in shipping.items()}
    assert next(raw for c,d,raw in after if c==82)==abc
    return result

def resource_patch(raw, old_template, new_swf):
    previous=Resource(raw);pos,movie=native(previous)
    template=native(Resource(old_template.read_bytes()))[1]
    updated=movie_patch(movie,template,new_swf.read_bytes())
    root=previous.chunks[0][:pos]+struct.pack('<I',len(updated))+updated+struct.pack('<I',0)
    result=previous.replace_chunks([root,*previous.chunks[1:]])
    checked=Resource(result)
    assert checked.chunks[1:]==previous.chunks[1:] and checked.imports==previous.imports
    return result

def repack(source, replacements, output):
    with source.open('rb') as f:
        header=bytearray(f.read(32));toc=f.read(struct.unpack_from('<I',header,16)[0])
    version=struct.unpack_from('<H',header,20)[0];width=320 if version==3 else 304
    rows={toc[i:i+256].split(b'\0')[0].decode('ascii').replace('\\','/'):bytearray(toc[i:i+width]) for i in range(0,len(toc),width)}
    files={};preserved={}
    for name,raw in bundle_entries(source):
        name=name.replace('\\','/');preserved[name]=hashlib.sha256(raw).hexdigest()
        if name in replacements:raw=replacements[name]
        dest=output.parent/'resources'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);files[name]=dest
    assert set(replacements)<=set(files)
    cursor=(32+len(toc)+4095)&~4095;table=bytearray();positions={}
    for name,row in rows.items():
        raw=files[name].read_bytes();size=len(raw);positions[name]=cursor
        if version==3:
            struct.pack_into('<III',row,276,size,size,cursor);struct.pack_into('<II',row,312,zlib.crc32(raw),0)
        else:struct.pack_into('<QIIII',row,272,cursor,size,size,zlib.crc32(raw),0)
        table+=row;cursor=(cursor+size+4095)&~4095
    total=max(positions[n]+p.stat().st_size for n,p in files.items());struct.pack_into('<I',header,8,total)
    with output.open('wb') as f:
        f.write(header);f.write(table)
        for name,p in files.items():
            f.write(bytes(positions[name]-f.tell()))
            with p.open('rb') as s:shutil.copyfileobj(s,f)
    assert {n.replace('\\','/'):hashlib.sha256(raw).hexdigest() for n,raw in bundle_entries(output)}=={n:sha(p) for n,p in files.items()}
    assert all(sha(p)==preserved[n] for n,p in files.items() if n not in replacements)
    return files,positions,len(table),len(files)-len(replacements)

def main():
    p=argparse.ArgumentParser();p.add_argument('--ui',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=True);assert not (out/'manifest.json').exists()
    base=BASE_ARCHIVES
    platforms={}
    for platform,key,mod in [('1.32','classic','modBetaGwentClassic132'),('5.0+','nextgen','modBetaGwent0924')]:
        folder=out/key;folder.mkdir(exist_ok=True)
        with zipfile.ZipFile(base/f'GwentBetaClassic-0.9.0-{platform}-AllLanguages.zip') as z:
            bundle=folder/'original.bundle';bundle.write_bytes(z.read(f'Mods/{mod}/content/blob0.bundle'))
            metadata=z.read(f'Mods/{mod}/content/metadata.store')
        original={n.replace('\\','/'):raw for n,raw in bundle_entries(bundle)}
        menus=json.loads((a.ui/key/'menus/menus.json').read_text('utf8'))['menus'];replacements={};reports=[]
        old_menus=json.loads((UI_BASELINE/key/'menus/menus.json').read_text('utf8'))['menus']
        paths={'BetaGwentBoard':'betagwent/betagwent_board.redswf','GwintGame':'gameplay/gui_new/swf/gwint/gwint_game.redswf' if key=='classic' else 'betagwent/betagwent_npc00.redswf','DeckBuilder':'gameplay/gui_new/swf/gwint/deck_builder.redswf' if key=='classic' else 'betagwent/betagwent_decks.redswf','BetaGwentKeg':'gameplay/gui_new/swf/test/panel_test.redswf' if key=='classic' else 'betagwent/betagwent_kegop.redswf'}
        for m in menus:
            entry=m['entry'];path=paths[entry];old=next(x for x in old_menus if x['entry']==entry)
            assert sha(Path(old['path']))==old['sha256']
            swf=Path(m['path']).with_suffix('.swf');assert sha(swf)==m['sourceSha256']
            raw=resource_patch(original[path],Path(old['path']),swf)
            assert len(raw)<(32 if key=='classic' else 65)*1024**2
            replacements[path]=raw;reports.append(dict(path=path,bytes=len(raw),nativeTextureChunksPreserved=True,imageDefinitionsPreserved=True))
        dest=folder/'blob0.bundle';files,positions,toc_size,preserved=repack(bundle,replacements,dest)
        if key=='classic':
            dest.write_bytes(fix_bundle(dest.read_bytes()));meta=classic_metadata(metadata,dest,{})
        else:
            build_release.redux=lambda:{}
            meta=build_release.nextgen_metadata(metadata,dest,positions,files,toc_size)
        (folder/'metadata.store').write_bytes(meta)
        records={f'Mods/{mod}/content/{n}':dict(path=str(folder/n),sha256=sha(folder/n)) for n in ['blob0.bundle','metadata.store']}
        platforms[platform]=dict(files=records,menus=reports,unchangedBundlePayloads=preserved)
        print('Verified UI patch',platform,flush=True)
    (out/'manifest.json').write_text(json.dumps(dict(version='0.9.1',platforms=platforms,gameplayVerified=False),indent=2),'utf8')

if __name__=='__main__':main()

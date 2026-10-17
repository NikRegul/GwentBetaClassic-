"""Build a Classic UI overlay from a pinned release, preserving its native art."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import zlib

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/ui'))
from update_board_resource import validate_resource, unpack_root, movie_parts, header_crc, validate_image_linkages
from install_native_hd93 import symbols

ENTRIES = {'BetaGwentBoard':'betagwent_board','GwintGame':'betagwent_npc00','DeckBuilder':'betagwent_decks','BetaGwentKeg':'betagwent_kegop'}
ROOTS = {'BetaGwentBoard':'BetaGwentBoard','GwintGame':'BetaGwentNpcMenu','DeckBuilder':'BetaGwentDeckMenu','BetaGwentKeg':'BetaGwentKegMenu'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, log, timeout=300):
    with log.open('wb') as output:
        result = subprocess.run(list(map(str, command)), cwd=ROOT, stdout=output, stderr=subprocess.STDOUT,
                                timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode:
        raise RuntimeError(log.read_text('utf8', errors='replace')[-6000:])


def replace_abc(resource_path, new_swf, output):
    resource, records = validate_resource(resource_path)
    validate_image_linkages(resource)
    metadata, gfx, authoring = unpack_root(resource)
    prefix, old_tags, tail = movie_parts(authoring)
    _, new_tags, _ = movie_parts(new_swf.read_bytes())
    old_symbols,new_symbols=symbols(old_tags),symbols(new_tags)
    if old_symbols.keys()!=new_symbols.keys() or any(old_symbols[k].split(b'$')[0]!=new_symbols[k].split(b'$')[0] for k in old_symbols):
        raise ValueError('Compiled image/class identities differ from frozen release: ' + str(resource_path))
    aliases={old_symbols[k]:new_symbols[k] for k in old_symbols}
    # Keep each SymbolClass tag after its corresponding character definitions.
    # Fonts and atlas bitmaps are in different groups. Moving bitmap bindings
    # before DefineSubImage makes native GFx construct empty Bitmap instances.
    if 0 not in new_symbols:raise ValueError('Compiled document class is missing')
    def tag(code,data):return struct.pack('<HI',(code<<6)|63,len(data))+data
    def replace_tag(code,data,raw):
        if code==82:return abc
        if code==76:
            original_group=symbols([(code,data,raw)])
            if not set(original_group)<=set(new_symbols):raise ValueError('Unknown symbol group')
            payload=struct.pack('<H',len(original_group))+b''.join(
                struct.pack('<H',ident)+new_symbols[ident]+b'\0' for ident in original_group)
            return tag(code,payload)
        if code==1009:
            size=data[10];name=data[11:11+size];new_name=aliases.get(name,name)
            return tag(code,data[:10]+bytes([len(new_name)])+new_name+data[11+size:])
        return raw
    abc = next(raw for code, data, raw in new_tags if code == 82)
    payload = next(data for code, data, raw in new_tags if code == 82)
    native_prefix, native_tags, native_tail = movie_parts(gfx)
    native_body = native_prefix + b''.join(replace_tag(code,data,raw) for code,data,raw in native_tags)
    native = gfx[:4] + struct.pack('<I', len(native_body)+8) + zlib.compress(native_body+native_tail, 9)
    # Authoring pixels/font tags are taken from the same frozen release too.
    source_body = prefix + b''.join(replace_tag(code,data,raw) for code,data,raw in old_tags)
    source = b'CWS' + authoring[3:4] + struct.pack('<I', len(source_body)+8) + zlib.compress(source_body+tail, 6)
    root = metadata + struct.pack('<I', len(native)) + native + struct.pack('<I', len(source)) + source
    table = resource.tables[4][0]
    result = bytearray(resource.data[:table]) + bytearray(len(records)*24)
    for i, (record, chunk) in enumerate(zip(records, [root]+[e['data'] for e in resource.exports[1:]])):
        row = list(record);row[3]=len(chunk);row[4]=len(result);row[6]=zlib.crc32(chunk)
        struct.pack_into('<HHIIIII', result, table+i*24, *row)
        result += chunk
    struct.pack_into('<II', result, 24, len(result), len(result))
    struct.pack_into('<III', result, 88, table, len(records), zlib.crc32(result[table:table+len(records)*24]))
    struct.pack_into('<I', result, 32, header_crc(result))
    output.write_bytes(result)
    checked, _ = validate_resource(output);validate_image_linkages(checked)
    _, checked_gfx, _ = unpack_root(checked)
    assert next(data for code, data, _ in movie_parts(checked_gfx)[1] if code == 82) == payload
    for movie in (checked_gfx,unpack_root(checked)[2]):
        tags=movie_parts(movie)[1]
        assert symbols(tags)==new_symbols, 'Lost document, image or font class binding'
        defined=set()
        binding_ids=[]
        definitions={2,6,7,10,11,20,21,22,32,33,34,35,36,37,39,46,48,60,75,83,84,87,90,91,1008}
        for code,data,raw in tags:
            if code in definitions:defined.add(struct.unpack_from('<H',data)[0])
            if code==76:
                group=symbols([(code,data,raw)])
                assert not (set(group)-defined-{0}), 'Symbol bound before its character definition'
                binding_ids.extend(group)
        assert len(binding_ids)==len(set(binding_ids))==len(new_symbols), 'Duplicate/missing symbol bindings'

    assert [e['data'] for e in checked.exports[1:]] == [e['data'] for e in resource.exports[1:]]
    return dict(path=str(output), sha256=sha(output), bytes=output.stat().st_size,
                originalTextureChunksPreserved=True, symbolIdsPreserved=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',type=int,required=True)
    parser.add_argument('--prepared',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--source-ui',type=Path,help='Pinned ui directory containing src and assets')
    args=parser.parse_args();out=args.out.resolve()
    if out.exists() and not args.resume or not out.is_relative_to((ROOT/'BetaGwent/build').resolve()):
        parser.error('Use a fresh build directory')
    frozen=json.loads((ROOT/f'docs/evidence/stage{args.stage}-completion.json').read_text('utf8'))
    candidates=[ROOT/f'BetaGwent/build/stage{args.stage}/common/ui/src',ROOT/'BetaGwent/ui/src',*sorted((ROOT/'tmp').glob('backup*/BetaGwent/ui/src'),reverse=True)]
    if args.source_ui:candidates=[args.source_ui/'src']
    inputs={}
    for name,digest in frozen['sources'].items():
        match=next((p/name for p in candidates if (p/name).is_file() and sha(p/name)==digest),None)
        if match is None:raise RuntimeError('Exact frozen UI source is unavailable: '+name)
        inputs[name]=match
    source=ROOT/'BetaGwent/ui/src' if not args.source_ui else args.source_ui/'src'
    ui=out/'ui'
    if not args.resume:
        shutil.copytree(source,ui/'src')
        for name,path in inputs.items():shutil.copy2(path,ui/'src'/name)
        shutil.copytree(args.source_ui/'assets' if args.source_ui else ROOT/'BetaGwent/ui/assets',ui/'assets')
    # Support classes (mx.core.BitmapAsset) are not stage sources; also repairs
    # a resumed copy made before they were pinned.
    support=source/'mx/core/BitmapAsset.as'
    if not support.is_file():raise RuntimeError('UI support class missing: '+str(support))
    if not (ui/'src/mx').exists():shutil.copytree(source/'mx',ui/'src/mx')
    if sha(ui/'src/mx/core/BitmapAsset.as')!=sha(support):raise RuntimeError('UI support class differs from pinned UI')
    board=ui/'src/BetaGwentBoard.as';raw=board.read_bytes()
    assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
    bridge=(ROOT/'tools/classic132/classic_text_bridge.as.inc').read_text('utf8')
    bridge='\n'.join(line for line in bridge.splitlines() if not line.startswith('//'))
    text=raw.decode('utf-8-sig')
    marker='        public function setControllerInput('
    assert text.count(marker)==1
    if 'public function openClassicTextInput(' not in text:
        text=text.replace(marker,bridge.replace('\n','\r\n')+'\r\n'+marker)
        board.write_bytes(b'\xef\xbb\xbf'+text.encode('utf8'))
    java=Path(r'C:\Program Files\Microsoft\jdk-11.0.12.7-hotspot\bin\java.exe')
    royale=ROOT/'tools/vendor/apache-royale-0.9.12/royale-asjs/lib'
    api=Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\r4data\gameplay\gui_new\actionscript')
    script=(args.prepared/'Mods/modBetaGwentClassic132/content/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf16')
    bindings=sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',script)))
    reports=[]
    for entry,stem in ENTRIES.items():
        print('Classic menu',entry,flush=True)
        if args.resume and (out/(stem+'.redswf')).exists():
            previous=json.loads((out/'menus.json').read_text('utf8'))
            assert previous['sourceStage']==args.stage and previous['frozenSources']==frozen['sources']
            item=next(x for x in previous['menus'] if x['entry']==entry)
            assert sha(Path(item['path']))==item['sha256']
            reports.append(item);continue
        variant=ui/('src-'+entry);shutil.copytree(ui/'src',variant,dirs_exist_ok=True)
        pages=set(range(0,9))|{11,14,15}|set(range(21,40)) if entry=='BetaGwentKeg' else set(range(0,21))
        art=variant/'BetaGwentHDArt.as';art_raw=art.read_bytes();art_text=art_raw.decode('utf-8-sig')
        for page in map(int,re.findall(r'private static var Page(\d+):Class;',art_text)):
            if page in pages:continue
            art_text,n=re.subn(r'[ \t]*\[Embed\([^\]]*\)\] private static var Page%d:Class;\r?\n'%page,'',art_text)
            assert n==1
            art_text=re.sub(r'(private static var types:Array=\[[^\]]*?)\bPage%d\b'%page,r'\1null',art_text)
        art.write_bytes((b'\xef\xbb\xbf' if art_raw.startswith(b'\xef\xbb\xbf') else b'')+art_text.encode('utf8'))
        swf=out/(stem+'.swf')
        if not (args.resume and swf.exists()):run([java,'-Xmx3g','-Duser.language=en','-Duser.country=US','-jar',royale/'mxmlc.jar',
             '-load-config='+str(ROOT/'BetaGwent/ui/board-config.xml'),'-output='+str(swf),
             '-source-path='+str(variant),'-source-path+='+str(api),'-includes+=scaleform.gfx.KeyboardEventEx',variant/(ROOTS[entry]+'.as')],out/(stem+'-compile.log'))
        if not (args.resume and (out/(stem+'-fonts.log')).exists()):run([sys.executable,ROOT/'tools/ui/build_beta_fonts104.py','inject',swf],out/(stem+'-fonts.log'))
        dump=out/(stem+'-abc.txt')
        run([java,'-jar',royale/'compiler-swfdump.jar','-abc',swf],dump,60)
        abc=dump.read_text('utf8',errors='replace')
        missing=[name for name in bindings if not re.search(r'public function '+re.escape(name)+r'\(',abc)]
        if missing:raise RuntimeError('Missing compiled bindings: '+repr(missing))
        menu=next(m for m in frozen['menus'] if m['entry']==entry and m['language']=='ru')
        old=Path(menu['resource']);assert sha(old)==menu['sha256']
        item=replace_abc(old,swf,out/(stem+'.redswf'))
        item.update(entry=entry,bindings=len(bindings),sourceSha256=sha(swf));reports.append(item)
    (out/'menus.json').write_text(json.dumps(dict(sourceStage=args.stage,sources={n:str(p) for n,p in inputs.items()},language='ru',menus=reports,
        frozenSources=frozen['sources'],scriptBindings=bindings,canonicalSourcesModified=False,classicTextBridge=True,uiCopies=5),indent=2)+'\n','utf8')
    print('Four Classic menus built with frozen art and 5 isolated UI copies.',flush=True)


if __name__=='__main__':main()

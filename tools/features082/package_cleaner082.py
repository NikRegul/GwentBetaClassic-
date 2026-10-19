"""Package the opt-in cleaner plus inert item definitions needed while loading."""
from pathlib import Path
import sys,json,hashlib,shutil,struct,zipfile,zlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];BUILD=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'BetaGwent/build/cleaner082';BASE=ROOT/'BetaGwent/build/release082-final'
sys.path[:0]=[str(ROOT/'tools/classic132')]
from formats import write_bundle,bundle_entries,fnv64,sha
from build_resources import vlq,read_vlq
def metadata(files,bundle,classic):
    strings=bytearray(b'\0')
    def add(s):pos=len(strings);strings.extend(s.encode('ascii')+b'\0');return pos
    file_rows=[bytes(32)];entries=[bytes(20 if classic else 24)];dirs=[bytes(8)];directory_ids={'':0};init=[];hashes=[]
    def directory(name):
        if name not in directory_ids:
            parent,_,leaf=name.rpartition('\\');pid=directory(parent);directory_ids[name]=len(dirs);dirs.append(struct.pack('<2I',add(leaf),pid))
        return directory_ids[name]
    raw=bundle.read_bytes();stride=320 if classic else 304;toc=raw[32:32+stride*len(files)];maximum=0
    for i in range(len(files)):
        row=toc[i*stride:(i+1)*stride];name=row[:256].split(b'\0')[0].decode('ascii');fid=i+1
        if classic:size,packed,offset=struct.unpack_from('<III',row,276)
        else:offset,size,packed=struct.unpack_from('<QII',row,272)
        assert size==packed==files[name.replace('\\','/')].stat().st_size;maximum=max(maximum,size)
        file_rows.append(struct.pack('<8I',add(name),0,size,size,fid,0,0,0));entries.append(struct.pack('<5I',fid,1,offset,size,0) if classic else struct.pack('<Q4I',offset,size,0,fid,1))
        parent,_,leaf=name.rpartition('\\');init.append(struct.pack('<3I',fid,directory(parent),add(leaf)));hashes.append(struct.pack('<Qq',fnv64(name.encode('ascii')),fid))
    start=32+len(toc);name_offset=add('blob0.bundle')
    bundle_row=struct.pack('<6I',name_offset,1,len(files),len(raw)-start,start,0) if classic else struct.pack('<Q4I',len(raw)-start,start,name_offset,1,len(files))
    arrays=[file_rows,entries,[bytes(24),bundle_row],[],dirs,init,sorted(hashes,key=lambda r:struct.unpack_from('<Q',r)[0])]
    result=b'\x03VTM'+struct.pack('<3I',6 if classic else 7,maximum,maximum)+vlq(len(strings))+strings
    return result+b''.join(vlq(len(rows))+b''.join(rows) for rows in arrays)
def assets(content,classic):
    moditems=set()
    for p in (BASE/'classic/resources').rglob('*.xml'):
        try:
            raw=p.read_bytes();root=ET.fromstring(raw.decode('utf16' if raw.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig'))
        except (ET.ParseError,UnicodeError,ValueError):continue
        moditems|={x.attrib['name'] for x in root.findall('./definitions/items/item') if x.attrib.get('name','').startswith('betagwent_')}
    assert 'betagwent_keg' in moditems
    resource=BUILD/('resources-classic' if classic else 'resources-nextgen');files={}
    for mode in ['items','items_plus']:
        root=ET.Element('redxml');items=ET.SubElement(ET.SubElement(root,'definitions'),'items')
        for name in sorted(moditems):
            item=ET.SubElement(items,'item',dict(name=name,hold_slot='',equip_slot='',template='',stackable='999',ability_slots='0',category='misc',price='0',icon_path='icons/inventory/gwint/ico_gwent_weather_neutral.png',localisation_key_name='gwint_name_dummy',localisation_key_description='gwint_desc_gwint_card'))
            ET.SubElement(item,'tags').text='NoShowInPlayersInventory,EncumbranceOff'
        for name,raw in [('betagwent_cleanup_items.xml',ET.tostring(root,encoding='utf8',xml_declaration=True)),('betagwent_redux_inventory.xml',(BASE/'redux/gameplay'/mode/'betagwent_redux_inventory.xml').read_bytes())]:
            p=resource/'gameplay'/mode/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw);files[p.relative_to(resource).as_posix()]=p
    content.mkdir(parents=True);bundle=content/'blob0.bundle'
    if classic:write_bundle(files,bundle)
    else:
        rows=bytearray();offset=(32+304*len(files)+4095)&~4095;positions={}
        for name,p in sorted(files.items()):
            row=bytearray(304);encoded=name.replace('/','\\').encode('ascii');row[:len(encoded)]=encoded
            struct.pack_into('<QIIII',row,272,offset,p.stat().st_size,p.stat().st_size,zlib.crc32(p.read_bytes()),0);positions[name]=offset;rows+=row;offset=(offset+p.stat().st_size+4095)&~4095
        header=bytearray((BASE/'nextgen/package/Mods/modBetaGwent0924/content/blob0.bundle').read_bytes()[:32]);struct.pack_into('<II',header,8,max(positions[n]+p.stat().st_size for n,p in files.items()),0);struct.pack_into('<I',header,16,len(rows))
        with bundle.open('wb') as stream:
            stream.write(header);stream.write(rows)
            for name,p in sorted(files.items()):stream.write(bytes(positions[name]-stream.tell()));stream.write(p.read_bytes())
    assert {n.replace('\\','/'):hashlib.sha256(raw).hexdigest() for n,raw in bundle_entries(bundle)}=={n:sha(p) for n,p in files.items()}
    (content/'metadata.store').write_bytes(metadata(files,bundle,classic))
    # XML-only package: sentinel, no external resources or dependency edges.
    (content/'dep.cache').write_bytes(b'SPED'+struct.pack('<I',2)+vlq(1)+bytes(16)+b''.join(vlq(1)+bytes(4) for _ in range(3)))
    return len(moditems)
def main():
    label='cleaner082-safe-native' if BUILD.name=='cleaner082-safe' else 'cleaner082-native-report'
    native=json.loads((ROOT/f'BetaGwent/build/universal081/classic-runtime/runs/{label}/result.json').read_text('utf8'));assert native['compilePassed'] and not native['errors']
    ng=json.loads((BUILD/'compile-nextgen/result.json').read_text('utf8'));assert ng['exitCode']==0 and ng['patchSourcesUnchangedDuringCompile']
    for classic in [True,False]:
        version='1.32' if classic else '5.0+';package=BUILD/('package-classic' if classic else 'package-nextgen');assert not package.exists()
        content=package/'Mods/modBetaGwentCleaner082/content';content.mkdir(parents=True)
        if classic:shutil.copytree(BUILD/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts',content/'scripts')
        else:shutil.copy2(BUILD/'compile-nextgen/compiled/blob.rsblob',content/'precompiled.rsblob')
        count=assets(package/'Mods/modBetaGwentCleanerItems082/content',classic)
        docs=package/'BetaGwentCleanerDocs';docs.mkdir()
        shutil.copy2(ROOT/'docs/releases/0.8.2_CLEANER_RU.md',docs/'README_RU.md');shutil.copy2(ROOT/'tools/features082/save_fact_index.py',docs/'save_fact_index.py')
        shutil.copy2(BUILD/'inventory.json',docs/'profile-fields.json');shutil.copy2(BUILD/'tests.json',docs/'tests.json')
        info=dict(version='0.8.2',platform=version,nativeCompilationPassed=True,gameplayVerified=False,automaticCleanup=False,retainedItemDefinitions=count,fullHistoricalSaveErasureVerified=False)
        for mod in ['modBetaGwentCleaner082','modBetaGwentCleanerItems082']:(package/'Mods'/mod/'info.json').write_text(json.dumps(info,indent=2),'utf8')
        records=[dict(path=p.relative_to(package).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(package.rglob('*')) if p.is_file()]
        (package/'manifest.json').write_text(json.dumps(dict(**info,files=records),indent=2),'utf8')
        revision='-r2' if BUILD.name=='cleaner082-safe' else ''
        dest=ROOT/f'BetaGwent/release/GwentBetaClassic-Cleaner-0.8.2{revision}-{version}.zip'
        with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in sorted(package.rglob('*')):
                if p.is_file():z.write(p,p.relative_to(package).as_posix())
        with zipfile.ZipFile(dest) as z:assert z.testzip() is None
        digest=sha(dest);dest.with_suffix('.zip.sha256').write_text(digest+'  '+dest.name+'\n','ascii');print(dest,dest.stat().st_size)
if __name__=='__main__':main()

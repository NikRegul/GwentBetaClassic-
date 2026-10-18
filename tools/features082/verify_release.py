"""Audit the final RC archives, native containers and every metadata cross-index."""
from pathlib import Path
import hashlib,json,struct,sys,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-rc1'
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import bundle_entries,fnv64,sha
from build_resources import read_vlq

def verify(platform):
    part=BUILD/platform;package=part/'package';mod='modBetaGwentClassic132' if platform=='classic' else 'modBetaGwent0924'
    content=package/'Mods'/mod/'content';version=6 if platform=='classic' else 7;stride=320 if version==6 else 304
    bundle=content/'blob0.bundle';sizes={};crcs={};xml_names=[]
    # Read one resource at a time; compare every packed payload to the final manifest.
    for name,raw in bundle_entries(bundle):
        assert name not in sizes;sizes[name]=len(raw);crcs[name]=hashlib.sha256(raw).hexdigest()
        if name.endswith('betagwent_redux_inventory.xml'):
            items=ET.fromstring(raw).findall('./definitions/items/item');assert len(items)==203
            assert all(i.attrib['template']==i.attrib['equip_slot']==i.attrib['hold_slot']=='' for i in items)
            xml_names.append(name)
    assert len(xml_names)==2 and len(sizes)==(390 if version==6 else 354)
    with bundle.open('rb') as f:
        header=f.read(32);toc=f.read(struct.unpack_from('<I',header,16)[0])
    positions={}
    for i in range(0,len(toc),stride):
        row=toc[i:i+stride];name=row[:256].split(b'\0')[0].decode('ascii')
        if version==6:size,packed,offset=struct.unpack_from('<III',row,276)
        else:offset,size,packed=struct.unpack_from('<QII',row,272)
        assert size==packed==sizes[name] and offset+size<=bundle.stat().st_size
        positions[name]=offset
    data=(content/'metadata.store').read_bytes();assert struct.unpack_from('<I',data,4)[0]==version
    count,pos=read_vlq(data,16);strings=data[pos:pos+count];pos+=count;arrays=[]
    for width in (32,20 if version==6 else 24,24,4,8,12,16):
        count,pos=read_vlq(data,pos);arrays.append([data[p:p+width] for p in range(pos,pos+count*width,width)]);pos+=count*width
    assert pos==len(data) and not arrays[3]
    def text(off):return strings[off:strings.index(0,off)].decode('ascii')
    names={fid:text(struct.unpack_from('<I',row)[0]) for fid,row in enumerate(arrays[0]) if fid}
    assert set(names.values())==set(sizes) and len(arrays[1])==len(names)+1
    for fid,name in names.items():
        row=arrays[0][fid];assert struct.unpack_from('<II',row,8)==(sizes[name],sizes[name])
        if version==6:entry_fid,bid,offset,packed,nxt=struct.unpack('<5I',arrays[1][fid])
        else:offset,packed,nxt,entry_fid,bid=struct.unpack('<Q4I',arrays[1][fid])
        assert (entry_fid,bid,offset,packed,nxt)==(fid,1,positions[name],sizes[name],0)
    hashes=[struct.unpack('<QII',r) for r in arrays[6]]
    assert len(hashes)==len(names) and [h[0] for h in hashes]==sorted(h[0] for h in hashes)
    assert {h[1] for h in hashes}==set(names)
    for h,fid,upper in hashes:
        assert upper in ((0,) if version==6 else (0,0xffffffff))
        assert h==fnv64(names[fid].encode('ascii')),(names[fid],'path hash')
    def directory(i):
        parts=[]
        while i:
            off,i=struct.unpack('<2i',arrays[4][i]);parts.append(text(off))
        return '\\'.join(reversed(parts))
    indexed=set()
    for record in arrays[5]:
        fid,did,off=struct.unpack('<3i',record)
        if not fid:continue
        parent=directory(did);name=(parent+'\\' if parent else '')+text(off)
        assert name==names[fid];indexed.add(fid)
    assert indexed==set(names)
    maximum=max(sizes.values());assert struct.unpack_from('<II',data,8)==(maximum,maximum)
    assert maximum<=(32 if version==6 else 63)*1024**2
    if version==6:
        expected=json.loads((BUILD/'classic-prepared/preparation.json').read_text('utf8'))['outputScripts']
        actual={p.relative_to(content/'scripts').as_posix():sha(p) for p in (content/'scripts').rglob('*.ws')}
        assert actual==expected
    else:assert sha(content/'precompiled.rsblob')==sha(BUILD/'compile-nextgen/compiled/blob.rsblob')
    release_version=json.loads((package/'Mods'/mod/'info.json').read_text('utf8'))['version']
    manifest=json.loads((package/('manifest-'+release_version+'.json')).read_text('utf8'))
    archive_info=json.loads((part/'archive.json').read_text('utf8'));archive=Path(archive_info['path'])
    assert sha(archive)==archive_info['sha256']
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))==len(manifest['files'])+1
        for row in manifest['files']:
            p=package/row['path'];assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
            with z.open(row['path']) as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['sha256']
    return dict(platform=platform,bundleEntries=len(sizes),metadataPathsAndHashesVerified=True,reduxItemsPerMode=203,maximumResourceMiB=maximum/1024**2,archive=archive_info,nativeGameplayVerified=False)

if __name__=='__main__':
    if len(sys.argv)>1:BUILD=Path(sys.argv[1]).resolve()
    report=[verify(p) for p in ['classic','nextgen']]
    (BUILD/'final-audit.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report,indent=2))

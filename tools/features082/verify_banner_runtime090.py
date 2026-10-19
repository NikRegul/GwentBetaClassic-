"""Verify runtime prerequisites omitted by the first banner release."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/ui'),str(ROOT/'tools/classic132')]
from update_board_resource import movie_parts
from install_native_hd93 import symbols
from formats import Resource,bundle_entries,fnv64
from dependencies import read_dependency_cache
FINAL=ROOT/'BetaGwent/build/release090-final5'
NATIVE=ROOT/'BetaGwent/build/banners090-sdk-fix4'
UI=ROOT/'BetaGwent/build/release090-banner-runtime2'
DEPOT='gameplay/gui_new/swf/betagwentbanners/'
checks=0
def check(ok,label):
    global checks
    assert ok,label
    checks+=1
def digest(data):return hashlib.sha256(data).hexdigest()
manifest=json.loads((NATIVE/'banners-report.json').read_text('utf8'))
expected={}
for key,row in manifest['banners'].items():
    filename=row['file'];check(filename==filename.lower(),'canonical lowercase path '+key)
    expected[DEPOT+filename]=row['classic']['sha256']
    for platform in ['classic','nextgen']:
        path=NATIVE/platform/'resources'/DEPOT/filename;r=Resource(path.read_bytes())
        chunk=r.chunks[0];_,pos=r.properties(chunk);size=struct.unpack_from('<I',chunk,pos)[0]
        gfx=chunk[pos+4:pos+4+size];_,tags,_=movie_parts(gfx);binding=symbols(tags)
        exporter=[p for c,p,raw in tags if c==1000]
        check(len(exporter)==1 and key.lower().encode() in exporter[0].lower() and b'betagwent-board' not in exporter[0],platform+' real SDK ExporterInfo '+key)
        check(not any(c==65 for c,p,raw in tags),platform+' SDK-stripped ScriptLimits '+key)
        info=[p for c,p,raw in tags if c==1009]
        check(len(info)==1 and info[0][10]>0,platform+' named external bitmap '+key)
        export=info[0][11:11+info[0][10]]
        subimages={struct.unpack_from('<H',p)[0]:struct.unpack('<6H',p) for c,p,raw in tags if c==1008}
        bound=[ident for ident,name in binding.items() if name==export]
        check(len(bound)==1 and bound[0] in subimages and subimages[bound[0]][1]==0,platform+' bitmap export matches a real SubImage class '+key)
        check(path.read_bytes()==(FINAL/'banners'/platform/DEPOT/filename).read_bytes(),platform+' staged page '+key)
for platform in ['classic','nextgen']:
    source=(UI/platform/'ui/src/BetaGwentBoard.as').read_text('utf-8-sig')
    loader=(UI/platform/'ui/src/BetaGwentBanners090.as').read_text('utf-8-sig')
    check('name.toLowerCase()' in loader,'runtime URL case '+platform)
    menus=json.loads((UI/platform/'menus/menus.json').read_text('utf8'))
    for row in menus['menus']:
        path=Path(row['path']);check(digest(path.read_bytes())==row['sha256'],'immutable menu '+platform+'/'+row['entry'])
        abc=path.with_name(path.stem+'-abc.txt').read_text('utf8')
        check('layoutBigPower090' in abc,'new power/layout method compiled '+platform+'/'+row['entry'])
content=FINAL/'package-candidate/classic/package/DLC/dlcBetaGwentClassic132Assets/content'
bundle=content/'bundles/blob0.bundle';deps=read_dependency_cache((content/'dep.cache').read_bytes());metadata=(content/'metadata.store').read_bytes()
found={name.replace('\\','/'):digest(raw) for name,raw in bundle_entries(bundle) if '/betagwentbanners/' in name.replace('\\','/')}
check(found==expected,'all 18 banner movies registered in actual Classic DLC bundle')
with bundle.open('rb') as stream:header=stream.read(32);toc=stream.read(struct.unpack_from('<I',header,16)[0])
for i in range(0,len(toc),320):
    row=toc[i:i+320];name=row[:256].split(b'\0')[0].decode('ascii').replace('\\','/')
    if name not in expected:continue
    guid=hashlib.md5(('betagwent090:'+name).encode('ascii')).digest()
    check(row[256:272]==guid and guid in deps['guids'],'DLC GUID and dependency '+name)
    check(name.replace('/','\\').encode()+b'\0' in metadata and struct.pack('<Q',fnv64(name.replace('/','\\').encode())) in metadata,'DLC lowercase path and native lookup hash '+name)
old=ROOT/'BetaGwent/build/release090-final4/package-candidate/classic/package/DLC/dlcBetaGwentClassic132Assets/content/bundles/blob0.bundle'
before={n:digest(b) for n,b in bundle_entries(old)}
after={n:digest(b) for n,b in bundle_entries(bundle) if '/betagwentbanners/' not in n.replace('\\','/')}
check(before==after,'all previously accepted DLC payloads retained byte-for-byte')
runtime=json.loads((UI/'banner-runtime-tests.json').read_text('utf8'));check(runtime['checks']==334,'actual AS async/fallback tests passed')
report=dict(checks=checks,classicDLCBannerCount=len(found),realSDKPages=36,acceptedDLCPayloadsUnchanged=len(before),asyncUIChecks=334,inGameVerified=False)
(FINAL/'banner-runtime-verification.json').write_text(json.dumps(report,indent=2),'utf8');print(json.dumps(report,indent=2))

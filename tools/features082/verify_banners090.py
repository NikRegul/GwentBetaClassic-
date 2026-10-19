"""Check banner pixels, cooked resources and both packaged bundle/depot indexes."""
from pathlib import Path
import hashlib, json, os, struct, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/classic132'))
from formats import Resource, bundle_entries
from dependencies import read_dependency_cache

BASE = ROOT/'BetaGwent/build'/os.environ.get('BG_FINAL','release090-final2')
INPUT = ROOT/'BetaGwent/build'/os.environ.get('BG_BANNER_INPUT','banners090-seamfix-input')
NATIVE = ROOT/'BetaGwent/build'/os.environ.get('BG_BANNERS','banners090-native')
DEPOT = 'gameplay/gui_new/swf/betagwentbanners/'
checks = 0


def check(value, reason):
    global checks
    assert value, reason
    checks += 1


meta = json.loads((INPUT/'banners.json').read_text('utf8'))
native_report = json.loads((NATIVE/'banners-report.json').read_text('utf8'))
check(len(meta['banners']) == 18, 'six groups times three tiers')
report = {}
for platform,mod in [('classic','modBetaGwentClassic132'),('nextgen','modBetaGwent0924')]:
    content = BASE/'package-candidate'/platform/'package/Mods'/mod/'content'
    expected = {}
    for key in meta['banners']:
        filename=native_report['banners'][key].get('file',key+'.redswf')
        path = NATIVE/platform/'resources'/DEPOT/filename
        data = path.read_bytes(); r = Resource(data)
        check(r.classes == ['CSwfResource','CSwfTexture'], key+' native root and inline texture')
        check(struct.unpack_from('<I',data,4)[0] == (163 if platform=='classic' else 164), key+' platform version')
        check(all(row[1] == (8192 if platform=='classic' else 0) for row in r.records), key+' cooked flags')
        props,pos = r.properties(r.chunks[1]); props={r.names[n]:(r.names[t],v) for n,t,v in props}
        check(r.names[struct.unpack('<H',props['compression'][1])[0]]=='TCM_DXTAlpha', key+' BC3 alpha')
        tail = r.chunks[1][pos:]
        pixels = tail[28:] if platform=='classic' else tail[24:-4]
        check(pixels == (INPUT/(key+'.dds')).read_bytes()[128:], key+' original encoded pixels preserved')
        check(len(data) < 0x2000000, key+' async resource limit')
        expected[DEPOT+filename] = hashlib.sha256(data).hexdigest()
    found = {n.replace('\\','/'):hashlib.sha256(raw).hexdigest()
             for n,raw in bundle_entries(content/'blob0.bundle',lambda n: '/betagwentbanners/' in n.replace('\\','/'))}
    check(found == expected, platform+' bundle contains exactly the 18 built pages')
    metadata = (content/'metadata.store').read_bytes()
    for name in expected:
        check(name.replace('/','\\').encode('ascii')+b'\0' in metadata, platform+' depot path in metadata')
    if platform=='classic':
        deps = read_dependency_cache((content/'dep.cache').read_bytes())
        with (content/'blob0.bundle').open('rb') as f:
            header=f.read(32); toc=f.read(struct.unpack_from('<I',header,16)[0])
        for i in range(0,len(toc),320):
            row=toc[i:i+320]; name=row[:256].split(b'\0')[0].decode('ascii').replace('\\','/')
            if name not in expected: continue
            guid=hashlib.md5(('betagwent090:'+name.lower()).encode('ascii')).digest()
            check(row[256:272] == guid and guid in deps['guids'], name+' stable GUID and dependency entry')
    build = json.loads((BASE/'package-candidate'/platform/'package/BetaGwentDocs/BuildInfo.json').read_text('utf8'))
    check(len(build['betaBanners'])==18, platform+' bundle build manifest')
    check(build['maximumResourceBytes'] < (32 if platform=='classic' else 65)*1048576, platform+' menu/resource budget')
    report[platform] = dict(banners=18,maximumResourceBytes=build['maximumResourceBytes'])
result = dict(candidate=str(BASE),checks=checks,platforms=report,inGameVerified=False)
(ROOT/'docs/evidence/banners090-resources.json').write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps(result,indent=2))

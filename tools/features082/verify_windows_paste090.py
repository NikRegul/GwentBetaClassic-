"""Verify the frozen UI, native bridge and both final Windows-paste archives."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[2]
FINAL=ROOT/'BetaGwent/build/release090-final4'
UI=ROOT/'BetaGwent/build/release090-windows-paste'
NATIVE=ROOT/'BetaGwent/build/clipboard090-r6b'
checks=0
def check(ok,label):
    global checks
    assert ok,label
    checks+=1
def sha(data):return hashlib.sha256(data).hexdigest()

native_test=json.loads((NATIVE/'native-tests.json').read_text('utf8'))
check(native_test['passed'] and native_test['checks']==341 and not native_test['userClipboardModified'],'native integration evidence')
ui_test=json.loads((UI/'windows-paste-tests.json').read_text('utf8'))
check(ui_test['checks']==80 and ui_test['windowsReadsPerPaste']==1,'production AS evidence')
import re
text=(UI/'nextgen/ui/src/BetaGwentExchangeText082.as').read_text('utf-8-sig')
values=json.loads(re.search(r'VALUES:Array=(\[.*?\]);',text,re.S)[1])
codes=['','ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw']
for language in range(1,14):
    folder='BetaGwent/build/release082-rc3/exchange-fonts' if language>=10 else 'BetaGwent/build/text138'
    font=(ROOT/folder/codes[language]/'BetaLocale137.as').read_text('utf-8-sig')
    chars=json.loads(re.search(r'public var characters:String=(".*?");',font,re.S)[1])
    check(set(values[language][11]+values[language][11].upper())<=set(chars),'all error glyphs in existing locale fonts '+codes[language])
reuse=json.loads((FINAL/'compile-reuse.json').read_text('utf8'))
check(reuse['gameplaySourcesIdentical'] and reuse['preparedManifestIdentical'],'gameplay compilation reuse validated')
archives={}
for platform,version,bins in [('classic','1.32',['x64']),('nextgen','5.0+',['x64','x64_dx12'])]:
    menus=json.loads((UI/platform/'menus/menus.json').read_text('utf8'))
    check(len(menus['menus'])==4,'four menus '+platform)
    for item in menus['menus']:
        path=Path(item['path'])
        check(sha(path.read_bytes())==item['sha256'],'compiled menu SHA '+item['entry'])
        abc=path.with_name(path.stem+'-abc.txt').read_text('utf8')
        check(all(x in abc for x in ['betagwent:windows-paste-v1','betagwent:windows-paste-begin-v1','betagwent:windows-paste-bit-v1']),'protocol in actual ABC '+platform+'/'+item['entry'])
    frozen=json.loads((UI/platform/'ui-inputs.json').read_text('utf8'))['sources']
    check(menus['frozenSources']==frozen,'menu sources frozen '+platform)
    check({p.name:sha(p.read_bytes()) for p in (UI/platform/'ui/src').glob('*.as')}==frozen,'input hashes unchanged '+platform)
    file=FINAL/f'package-candidate/archives-optional/GwentBetaClassic-0.9.0-{version}-AllLanguages.zip'
    with zipfile.ZipFile(file) as archive:
        manifest=json.loads(archive.read('manifest-0.9.0.json'))
        rows={row['path']:row for row in manifest['files']}
        info=json.loads(archive.read('BetaGwentDocs/BuildInfo.json'))
        check(info['nativeClipboard']['directions']==['game-to-windows','windows-to-game'],'both directions in package '+platform)
        check(info['nativeClipboard']['inGameVerified'] is False,'honest game verification state '+platform)
        for folder in bins:
            for name in ['dinput8.dll','GwentBetaClipboard.asi']:
                key='Optional-CopyButton/bin/'+folder+('/plugins/' if name.endswith('.asi') else '/')+name
                data=archive.read(key)
                check(sha(data)==sha((NATIVE/name).read_bytes())==rows[key]['sha256'],'updated native binary '+key)
                if name.endswith('.asi'):check(b'betagwent:windows-paste-v1\0' in data,'read capability marker '+folder)
        check('Ctrl+V' in archive.read('Optional-CopyButton/README_RU.txt').decode('utf-8-sig'),'bundled Windows paste instructions')
    data=file.read_bytes();digest=sha(data)
    check(file.with_suffix('.zip.sha256').read_text('ascii').split()[0]==digest,'archive checksum '+platform)
    archives[platform]=dict(path=str(file),bytes=len(data),sha256=digest)
report=dict(checks=checks,archives=archives,nativeChecks=341,uiChecks=80,regressionChecks=455,userClipboardModified=False,inGameVerified=False)
(FINAL/'windows-paste-verification.json').write_text(json.dumps(report,indent=2),'utf8')
print(json.dumps(report,indent=2))

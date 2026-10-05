"""Rebuild the same event IDs with English Beta recordings in an isolated project."""
from pathlib import Path
import json,shutil,subprocess,sys,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/recon'),str(ROOT/'tools/vendor/audio-python')]
from extract_beta_audio import decode,chunks,fnv
import UnityPy
src=ROOT/'BetaGwent/audio/wwise';dst=ROOT/'BetaGwent/audio/wwise-en89'
manifest=json.loads((ROOT/'docs/evidence/audio-import79.json').read_text('utf8'))
for p in src.rglob('*'):
    if not p.is_file() or any(part in ('.cache','GeneratedSoundBanks','Originals','.backup','Logs') for part in p.relative_to(src).parts):continue
    if p.suffix.lower() not in ('.wwu','.wproj','.wf','.prof'):continue
    target=dst/p.relative_to(src);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
bundle=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/audio/highend/vo/en-us'
voices={}
for obj in UnityPy.load(str(bundle)).objects:
    if obj.type.name=='TextAsset':
        a=obj.read();voices[a.m_Name]=a.m_Script.encode('utf8','surrogateescape')
missing=[]
for item in manifest['media']:
    out=dst/'Originals/SFX/BetaGwent79'/(item['key']+'.wav');out.parent.mkdir(parents=True,exist_ok=True)
    if item['role']=='voice':
        key=item['voiceKey']
        if key not in voices:missing.append(key);continue
        wem=ROOT/'BetaGwent/build/audio89-en/wem'/(key+'.wem');wem.parent.mkdir(parents=True,exist_ok=True);wem.write_bytes(voices[key])
        decode(wem,out)
    else:shutil.copyfile(src/'Originals/SFX/BetaGwent79'/out.name,out)
if missing:raise RuntimeError('English voice keys missing: '+str(len(missing)))
console=Path(json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0])
project=dst/'BetaGwent79.wproj'
result=subprocess.run([str(console),'generate-soundbank',str(project),'--platform','Windows','--bank','BetaGwent79','--abort-on-load-issues','--no-source-control','--skip-languages'],capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
log=ROOT/'BetaGwent/build/audio89-en/wwise.log';log.write_bytes(result.stdout+result.stderr)
bank=dst/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
if result.returncode or not bank.exists():raise RuntimeError('English Wwise build failed; inspect '+str(log))
parts=dict(chunks(bank.read_bytes()))
assert len(parts[b'DIDX'])//12==manifest['mediaCount']
import struct
assert struct.unpack_from('<II',parts[b'BKHD'])[1]==fnv('BetaGwent79')
report=dict(language='en',mediaCount=manifest['mediaCount'],originalEnglishBundleSha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bank=str(bank),bytes=bank.stat().st_size,sha256=hashlib.sha256(bank.read_bytes()).hexdigest(),englishVoicesVerified=True,licenseIncluded=False)
(ROOT/'docs/evidence/stage89-en-audio.json').write_text(json.dumps(report,indent=2),'utf8')
print(json.dumps(report))

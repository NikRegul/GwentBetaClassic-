"""Stage 109: add the shop troll's keg-opening lines (Gwent Beta 0.9.24) to both sound banks.

RU lines from AssetBundles/audio/highend/vo/shop/ru-ru, EN from .../shop/en-us (WEM -> WAV via
vgmstream). Adds Sounds under bg79_voice and Events bg79_vo_keg_<key> to the RU project
(BetaGwent/audio/wwise) and the EN project (BetaGwent/audio/wwise-en89), then regenerates both
BetaGwent79.bnk with the licensed WwiseConsole recorded in docs/evidence/audio-bank-build79.json.
Idempotent: previous keg entries are replaced. Run on Windows:  python -X utf8 tools/ui/add_keg_audio109.py
"""
from pathlib import Path
import json,re,shutil,subprocess,sys,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/recon'),str(ROOT/'tools/vendor/audio-python')]
from extract_beta_audio import decode
import UnityPy
SHOP=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/audio/highend/vo/shop'
NS=uuid.UUID('6b1f3c3e-2b6a-4f7e-9d43-109c0ffee109')
GUI=('GUI','{FD72CAE9-14F8-4BA2-A9F2-CF69D62BC9AB}','{A568D181-8F88-497D-B088-3998BC403D7B}')
CONV=('W3 sfx conversion settings','{CD5FEB1F-5340-419B-B846-9C660D7A1B24}','{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
# kind -> Beta keys (see duelAudioKeg.ws): 1 smash, 2 common, 3 rare, 4 epic, 5 legendary, 6 choice, 7 final, 8 before smash.
KEYS={1:['ShopTrollDialogues.%d'%i for i in (37,38,39,40,41)],2:['TrollShopDialoguesP3.%d'%i for i in (14,15,16)],
      3:['TrollShopDialoguesP3.4','TrollShopDialoguesP3.3'],4:['TrollShopDialoguesP3.5'],5:['TrollShopDialoguesP3.1'],
      6:['TrollShopDialoguesP3.17','TrollShopDialoguesP3.18'],7:['TrollShopDialoguesP3.40','TrollShopDialoguesP3.41','TrollShopDialoguesP3.30'],
      8:['ShopTrollDialogues.29','ShopTrollDialogues.30','ShopTrollDialogues.31']}
def gid(s):return '{'+str(uuid.uuid5(NS,s)).upper()+'}'
def wname(key):return 'vo_keg_'+re.sub(r'[^A-Za-z0-9]','_',key)
def ref(parent,name,target):
    rl=parent.find('ReferenceList')
    if rl is None:rl=ET.SubElement(parent,'ReferenceList')
    e=ET.SubElement(rl,'Reference',Name=name);ET.SubElement(e,'ObjectRef',Name=target[0],ID=target[1],WorkUnitID=target[2])
def write(path,root):ET.indent(root,space='\t');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def patch(project,lang):
    clips={o.read().m_Name:o.read().m_Script.encode('utf8','surrogateescape') for o in UnityPy.load(str(SHOP/lang)).objects if o.type.name=='TextAsset'}
    actor_path=project/'Actor-Mixer Hierarchy/BetaGwent79.wwu';event_path=project/'Events/BetaGwent79.wwu'
    actor=ET.parse(actor_path).getroot();events=ET.parse(event_path).getroot()
    mixer=next(m for m in actor.iter('ActorMixer') if m.get('Name')=='bg79_voice');children=mixer.find('ChildrenList')
    unit=actor.find('.//WorkUnit').get('ID')
    for s in list(children):
        if s.get('Name','').startswith('vo_keg_'):children.remove(s)
    echildren=events.find('.//WorkUnit/ChildrenList')
    for e in list(echildren):
        if e.get('Name','').startswith('bg79_vo_keg_'):echildren.remove(e)
    durations={}
    for key in sorted({k for v in KEYS.values() for k in v}):
        raw=clips['SAY.'+key];name=wname(key)
        wem=ROOT/'BetaGwent/build/audio109'/lang/(key+'.wem');wem.parent.mkdir(parents=True,exist_ok=True);wem.write_bytes(raw)
        info=decode(wem,ROOT/'BetaGwent/build/audio109'/lang/(name+'.wav'))
        target=project/'Originals/SFX/BetaGwent79'/(name+'.wav');target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/info['path'],target)
        durations[name]=info.get('durationMs',0)
        sid,src=gid(lang+'sound'+name),gid(lang+'source'+name)
        sound=ET.SubElement(children,'Sound',Name=name,ID=sid);ref(sound,'OutputBus',GUI);ref(sound,'Conversion',CONV)
        s=ET.SubElement(ET.SubElement(sound,'ChildrenList'),'AudioFileSource',Name=name,ID=src)
        ET.SubElement(s,'Language').text='SFX';ET.SubElement(s,'AudioFile').text='BetaGwent79\\'+name+'.wav'
        ET.SubElement(ET.SubElement(sound,'ActiveSourceList'),'ActiveSource',Name=name,ID=src,Platform='Linked')
        ev=ET.SubElement(echildren,'Event',Name='bg79_'+name,ID=gid(lang+'event'+name))
        act=ET.SubElement(ET.SubElement(ev,'ChildrenList'),'Action',Name='',ID=gid(lang+'action'+name));ref(act,'Target',(name,sid,unit))
    write(actor_path,actor);write(event_path,events);return durations
def generate(console,project):
    r=subprocess.run([str(console),'generate-soundbank',str(project/'BetaGwent79.wproj'),'--platform','Windows','--bank','BetaGwent79','--abort-on-load-issues','--no-source-control','--skip-languages'],
                     capture_output=True,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
    log=ROOT/'BetaGwent/build/audio109'/(project.name+'-wwise.log');log.parent.mkdir(parents=True,exist_ok=True);log.write_bytes(r.stdout+r.stderr)
    bank=project/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
    if r.returncode or not bank.exists():raise SystemExit('Wwise bank build failed; see '+str(log))
    return bank
def main():
    console=Path(json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0])
    if not console.exists():raise SystemExit('WwiseConsole not found: '+str(console))
    report={}
    for folder,lang in (('wwise','ru-ru'),('wwise-en89','en-us')):
        project=ROOT/'BetaGwent/audio'/folder;report[folder]=dict(durations=patch(project,lang))
        bank=generate(console,project);report[folder]['bank']=str(bank);report[folder]['bytes']=bank.stat().st_size
    (ROOT/'docs/evidence/stage109-keg-audio.json').write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report,indent=1)[:2000])
if __name__=='__main__':main()

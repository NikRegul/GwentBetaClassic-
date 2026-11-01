"""Stage 096: import the Beta UI sounds the 0.9.6 interface needs into every
BetaGwent79 Wwise project and rebuild the banks (run on Windows).

Events (Wwise IDs from the pinned client): the pass-hold coin
(CoinTurnIndicatorSoundHandler: StartPassing 2977021572, PassingConfirmed
3893297074 = play + stop StartPassing; ProgressParameter RTPC 952843278 has no
curve in the pinned banks, so the sound plays unmodulated), deck builder
(UIDBPanelSoundHandler, ToggleButtonSoundHandler, CardGridContainerSoundHandler,
InputFieldSoundHandler), card preview (UICardPreviewSoundHandler), popups,
history, outcome and button sounds from docs/evidence/beta-sound-events86.json.
Each becomes Sound fx_<id> + Event bg79_fx_<id>; bg79_fx_2977021572_stop stops
the hold sound. Idempotent. Usage: python -X utf8 tools/ui/add_beta_ui_audio096.py [--no-bank]
"""
from pathlib import Path
import argparse,json,re,shutil,struct,subprocess,sys,uuid,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'tools/recon'),str(ROOT/'tools/vendor/audio-python')]
from extract_beta_audio import decode
STREAM=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/Audio/GeneratedSoundBanks/Windows'
OUT=ROOT/'BetaGwent/build/audio096'
NS=uuid.UUID('0c0a1d96-0960-4b8e-9a3c-096000c0ffee')
GUI=('GUI','{FD72CAE9-14F8-4BA2-A9F2-CF69D62BC9AB}','{A568D181-8F88-497D-B088-3998BC403D7B}')
CONV=('W3 sfx conversion settings','{CD5FEB1F-5340-419B-B846-9C660D7A1B24}','{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
COMPONENTS={'UIDBPanelSoundHandler','CardGridContainerSoundHandler','ToggleButtonSoundHandler','UICardPreviewSoundHandler',
    'PopupPanelSoundHandler','InputFieldSoundHandler','HistoryWindowSoundHandler','TurnBannerSoundHandler',
    'UIOutcomeRootPanelSoundHandler','ButtonSoundHandler','UIOutcomeScoreSoundHandler','UIOutcomeRankSoundHandler','UIOutcomeRewardsSoundHandler','UIBattleChoicePanelSoundHandler'}
COIN={2977021572:'StartPassing',3893297074:'PassingConfirmed',3801975717:'OpponentShortCoinToss'}
PROJECTS=['wwise','wwise-en89','wwise-de137','wwise-it137','wwise-pt-br137']
def gid(s):return '{'+str(uuid.uuid5(NS,s)).upper()+'}'
def chunks(raw):
    pos=0
    while pos+8<=len(raw):
        tag,size=struct.unpack_from('<4sI',raw,pos);yield tag,raw[pos+8:pos+8+size];pos+=8+size
def package(path):
    """AKPK v1: banks and media (32-bit IDs), externals (64-bit IDs)."""
    raw=path.read_bytes();magic,hb,ver,ls,bs,ms,es=struct.unpack_from('<4s6I',raw,0);assert magic==b'AKPK' and ver==1
    def table(off,size,wide):
        out=[];n=struct.unpack_from('<I',raw,off)[0];p=off+4
        for _ in range(n):
            if wide:ident,block,length,start,lang=struct.unpack_from('<QIIII',raw,p);p+=24
            else:ident,block,length,start,lang=struct.unpack_from('<IIIII',raw,p);p+=20
            out.append((ident,raw[start*block:start*block+length]))
        return out
    base=28+ls;return raw,table(base,bs,False),table(base+bs,ms,False),table(base+bs+ms,es,True)
def stage():
    banks=OUT/'banks';wems=OUT/'wem';banks.mkdir(parents=True,exist_ok=True);wems.mkdir(parents=True,exist_ok=True)
    for name in ('Core','Default','Vfx','Cards'):
        raw,bk,media,ext=package(STREAM/(name+'.pck'))
        for ident,blob in bk:(banks/(name+'_'+str(ident)+'.bnk')).write_bytes(blob)
        for ident,blob in media+ext:(wems/(str(ident)+'.wem')).write_bytes(blob)
def events():
    refs=json.loads((ROOT/'docs/evidence/beta-sound-events86.json').read_text('utf8'))
    ids={}
    for e in refs['ui']:
        if e['component'] in COMPONENTS:ids.setdefault(int(e['eventId'])&0xffffffff,[]).append(e['component']+e['field'])
    for k,v in COIN.items():ids.setdefault(k,[]).append('CoinTurnIndicatorSoundHandler/'+v)
    return ids
def render(ids):
    txtp=OUT/'txtp';txtp.mkdir(exist_ok=True)
    args=[sys.executable,str(ROOT/'tools/vendor/audio/wwiser.pyz')]+[str(OUT/'banks'/(n+'_*.bnk')) for n in ('Core','Default','Vfx','Cards')]+['-d','none','-g','-gd','-go',str(txtp),'-gw',str(OUT/'wem'),'-gf']+[str(i) for i in ids]
    r=subprocess.run(args,capture_output=True,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW);(OUT/'wwiser.log').write_bytes(r.stdout+r.stderr)
    if r.returncode:raise SystemExit('wwiser failed; see '+str(OUT/'wwiser.log'))
    # wwiser expands the bank globs itself (1000+ Cards banks exceed the Windows command line).
    made={};gen=sorted(txtp.glob('*.txtp'))
    # wwiser's -gw also rewrites embedded-bank references into the wem folder;
    # point them back at the staged banks (as prepare_audio_import does).
    banks={b.name:b.as_posix() for b in (OUT/'banks').glob('*.bnk')}
    for t in gen:
        text=t.read_text('utf8',errors='replace')
        fixed=re.sub(r'[A-Za-z]:/[^\r\n#]+?/([^/\r\n]+\.bnk)',lambda m:banks.get(m[1],m[0]),text)
        if fixed!=text:t.write_text(fixed,encoding='utf8')
    for i in ids:
        hit=[p for p in gen if re.search(r'(?<!\d)'+str(i)+r'(?!\d)',p.read_text('utf8',errors='replace'))]
        if not hit:print('no playable rendering for',i);continue
        made[i]=decode(hit[0],OUT/'wav'/('fx_'+str(i)+'.wav'))
    return made
def ref(parent,name,target):
    rl=parent.find('ReferenceList')
    if rl is None:rl=ET.SubElement(parent,'ReferenceList')
    e=ET.SubElement(rl,'Reference',Name=name);ET.SubElement(e,'ObjectRef',Name=target[0],ID=target[1],WorkUnitID=target[2])
def patch(project,made):
    ap=project/'Actor-Mixer Hierarchy/BetaGwent79.wwu';ep=project/'Events/BetaGwent79.wwu'
    actor=ET.parse(ap).getroot();evs=ET.parse(ep).getroot();unit=actor.find('.//WorkUnit').get('ID')
    mixer=next(m for m in actor.iter('ActorMixer') if m.get('Name')=='bg79_sfx');children=mixer.find('ChildrenList')
    echildren=evs.find('.//WorkUnit/ChildrenList')
    have={s.get('Name'):s for s in children}
    added=[]
    for i,info in sorted(made.items()):
        name='fx_'+str(i);target=project/'Originals/SFX/BetaGwent79'/(name+'.wav');target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/info['path'],target)
        sound=have.get(name)
        if sound is None:
            sid,src=gid('sound'+name),gid('source'+name);sound=ET.SubElement(children,'Sound',Name=name,ID=sid);ref(sound,'OutputBus',GUI);ref(sound,'Conversion',CONV)
            s=ET.SubElement(ET.SubElement(sound,'ChildrenList'),'AudioFileSource',Name=name,ID=src)
            ET.SubElement(s,'Language').text='SFX';ET.SubElement(s,'AudioFile').text='BetaGwent79\\'+name+'.wav'
            ET.SubElement(ET.SubElement(sound,'ActiveSourceList'),'ActiveSource',Name=name,ID=src,Platform='Linked');added.append(name)
        target_ref=(name,sound.get('ID'),unit)
        for evname,stop in [('bg79_'+name,False)]+([('bg79_'+name+'_stop',True)] if i==2977021572 else []):
            for old in [e for e in echildren if e.get('Name')==evname]:echildren.remove(old)
            ev=ET.SubElement(echildren,'Event',Name=evname,ID=gid('event'+evname));acts=ET.SubElement(ev,'ChildrenList')
            act=ET.SubElement(acts,'Action',Name='',ID=gid('action'+evname))
            if stop:ET.SubElement(ET.SubElement(act,'PropertyList'),'Property',Name='ActionType',Type='int16',Value='2')
            ref(act,'Target',target_ref)
            if i==3893297074 and 2977021572 in made:  # PassingConfirmed also stops StartPassing
                hold=next(s for s in children if s.get('Name')=='fx_2977021572')
                st=ET.SubElement(acts,'Action',Name='',ID=gid('stopaction'+evname));ET.SubElement(ET.SubElement(st,'PropertyList'),'Property',Name='ActionType',Type='int16',Value='2')
                ref(st,'Target',('fx_2977021572',hold.get('ID'),unit))
    for root,path in ((actor,ap),(evs,ep)):ET.indent(root,space='\t');ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
    return added
def generate(console,project):
    r=subprocess.run([str(console),'generate-soundbank',str(project/'BetaGwent79.wproj'),'--platform','Windows','--bank','BetaGwent79','--abort-on-load-issues','--no-source-control','--skip-languages'],
                     capture_output=True,timeout=900,creationflags=subprocess.CREATE_NO_WINDOW)
    (OUT/(project.name+'-wwise.log')).write_bytes(r.stdout+r.stderr)
    bank=project/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
    if r.returncode or not bank.exists():raise SystemExit('Wwise bank build failed; see '+str(OUT/(project.name+'-wwise.log')))
    return bank
def main():
    global OUT
    a=argparse.ArgumentParser();a.add_argument('--no-bank',action='store_true');a.add_argument('--out',type=Path);a.add_argument('--report',type=Path);args=a.parse_args()
    if args.out:OUT=args.out.resolve()
    stage();ids=events();made=render(ids)
    report=dict(events={str(k):v for k,v in ids.items()},rendered={str(k):v for k,v in made.items()},projects={})
    console=Path(json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0])
    for folder in PROJECTS:
        project=ROOT/'BetaGwent/audio'/folder
        if not (project/'BetaGwent79.wproj').exists():continue
        entry=dict(added=patch(project,made))
        if not args.no_bank:bank=generate(console,project);entry.update(bank=str(bank),bytes=bank.stat().st_size)
        report['projects'][folder]=entry
    (args.report or ROOT/'docs/evidence/stage096-ui-audio.json').write_text(json.dumps(report,indent=1)+'\n','utf8')
    print(json.dumps({k:len(v) if isinstance(v,dict) else v for k,v in report.items()}))
if __name__=='__main__':main()

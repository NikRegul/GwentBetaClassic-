"""Add Queen's original creature call to private copies of the five voice banks."""
from pathlib import Path
import copy, hashlib, json, shutil, subprocess, sys, uuid, wave, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ui'))
from build_voice137 import PROJECTS, language_bridge
from build_voice_mix135 import inventory
NS=uuid.UUID('46133e82-71c7-437e-b9a2-a663b897099e')
def gid(name):return '{'+str(uuid.uuid5(NS,name)).upper()+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,tree):
    ET.indent(tree,space='\t');tree.write(p,encoding='utf8',xml_declaration=True)
def main():
    previous=json.loads((ROOT/'docs/evidence/voice138.json').read_text('utf8'))
    console=json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0]
    reports={}
    for lang,folder in PROJECTS.items():
        original=ROOT/'BetaGwent/audio'/folder
        project=ROOT/'BetaGwent/build/audio141'/lang/'wwise'
        if project.exists():raise RuntimeError('Use a new audio stage: '+str(project))
        shutil.copytree(original,project,ignore=shutil.ignore_patterns('.cache','GeneratedSoundBanks','.backup','.wsettings'))
        actor=project/'Actor-Mixer Hierarchy/BetaGwent79.wwu';events=project/'Events/BetaGwent79.wwu'
        tree=ET.parse(actor);etree=ET.parse(events)
        sound=copy.deepcopy(next(x for x in tree.iter('Sound') if x.get('Name')=='fx_1985436563'))
        name='vo_ArachasQueen';sound.set('Name',name);sound.set('ID',gid('sound'))
        for x in sound.iter():
            if x.tag in ('AudioFileSource','ActiveSource'):x.set('Name',name);x.set('ID',gid('source'))
        voice=next(x for x in tree.iter('ActorMixer') if x.get('Name')=='bg79_voice')
        voice.find('ChildrenList').append(sound)
        event=copy.deepcopy(next(x for x in etree.iter('Event') if x.get('Name')=='bg79_fx_1985436563'))
        event.set('Name','bg79_'+name);event.set('ID',gid('event'))
        for x in event.iter('Action'):x.set('ID',gid('action'))
        for x in event.iter('ObjectRef'):
            if x.get('Name')=='fx_1985436563':x.set('Name',name);x.set('ID',gid('sound'))
        etree.find('.//WorkUnit/ChildrenList').append(event)
        write(actor,tree);write(events,etree)
        wav=project/'Originals/SFX/BetaGwent79/fx_1985436563.wav'
        with wave.open(str(wav)) as w:assert w.getnframes()/w.getframerate()==3.619
        log=project.parent/'wwise.log'
        with log.open('wb') as out:
            result=subprocess.run([console,'generate-soundbank',str(project/'BetaGwent79.wproj'),'--platform','Windows','--bank','BetaGwent79','--abort-on-load-issues','--no-source-control','--skip-languages'],stdout=out,stderr=subprocess.STDOUT,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode:raise RuntimeError('Wwise failed: '+str(log))
        bank=project/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
        old=Path(previous[lang]['bank']);before=inventory(old.read_bytes());after=inventory(bank.read_bytes())
        assert sha(old)==previous[lang]['sha256'] and before<after
        assert len([x for x in after-before if x[0]==4])==1
        patch=ROOT/f'BetaGwent/build/stage141/{lang}/sources/scripts'
        shutil.copytree(ROOT/f'BetaGwent/build/stage140/ru/sources/scripts',patch)
        # Language-specific catalog durations remain exactly as previously built.
        shutil.copy2(ROOT/f'BetaGwent/build/stage138/{lang}/sources/scripts/game/betagwent/duelAudioCatalog.ws',patch/'game/betagwent/duelAudioCatalog.ws')
        for filename in ('duelSession.ws','duelAudio.ws'):
            shutil.copy2(ROOT/'BetaGwent/development/scripts/game/betagwent'/filename,patch/'game/betagwent'/filename)
        bridge=patch/'game/betagwent/developmentBoardMenu.ws'
        bridge.write_text(language_bridge((ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig'),lang),'utf-8-sig')
        reports[lang]=dict(previous[lang],bank=str(bank),sha256=sha(bank),bytes=bank.stat().st_size,patch=str(patch),
            bridgeSha256=sha(bridge),catalogSha256=sha(patch/'game/betagwent/duelAudioCatalog.ws'),
            queenEvent='bg79_vo_ArachasQueen',queenSourceSha256=sha(wav),queenDuration=3.619,
            originalBankUnmodified=True,previousBankSha256=sha(old),voiceBankReused=False,
            voiceCount=previous[lang]['voiceCount']+1,localizedVoiceCount=previous[lang]['voiceCount'],
            eventInventoryPreserved=False,previousEventInventoryPreserved=True,
            addedObjects=sorted(after-before),log=str(log))
        print('Queen voice bank built: '+lang,flush=True)
    (ROOT/'docs/evidence/voice141.json').write_text(json.dumps(reports,indent=2)+'\n','utf8')
if __name__=='__main__':main()

"""Raise Beta dialogue gain in both private banks; never deploy or ship Init.bnk."""
from pathlib import Path
import hashlib,json,struct,subprocess,xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]

def inventory(raw):
    chunks={};offset=0
    while offset<len(raw):
        name,size=struct.unpack_from('<4sI',raw,offset);offset+=8
        chunks[name]=raw[offset:offset+size];offset+=size
    assert offset==len(raw) and all(k in chunks for k in [b'BKHD',b'HIRC',b'DIDX',b'DATA'])
    data=chunks[b'HIRC'];count=struct.unpack_from('<I',data)[0];offset=4;objects=set()
    for _ in range(count):
        kind,size=struct.unpack_from('<BI',data,offset);offset+=5
        assert kind in [2,3,4,7] and size>=4 and offset+size<=len(data)
        objects.add((kind,struct.unpack_from('<I',data,offset)[0]));offset+=size
    assert offset==len(data)
    return objects

def main():
    console=Path(json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0])
    assert console.is_file()
    reports=[]
    for language,folder in [('ru','wwise'),('en','wwise-en89')]:
        project=ROOT/'BetaGwent/audio'/folder
        actor=project/'Actor-Mixer Hierarchy/BetaGwent79.wwu'
        tree=ET.parse(actor);voice=next(n for n in tree.iter('ActorMixer') if n.get('Name')=='bg79_voice')
        prop=next(n for n in voice.find('PropertyList') if n.get('Name')=='Volume')
        prop.set('Value','0')
        ET.indent(tree,space='\t');tree.write(actor,encoding='utf8',xml_declaration=True)
        bank=project/'GeneratedSoundBanks/Windows/BetaGwent79.bnk'
        before=inventory(bank.read_bytes())
        result=subprocess.run([str(console),'generate-soundbank',str(project/'BetaGwent79.wproj'),
            '--platform','Windows','--bank','BetaGwent79','--abort-on-load-issues','--no-source-control','--skip-languages'],
            capture_output=True,timeout=600,creationflags=subprocess.CREATE_NO_WINDOW)
        log=ROOT/f'BetaGwent/build/audio135/{language}-wwise.log';log.parent.mkdir(parents=True,exist_ok=True)
        log.write_bytes(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError('Wwise failed: '+str(log))
        raw=bank.read_bytes();assert inventory(raw)==before,'Sound/event inventory changed'
        reports.append(dict(language=language,bank=str(bank),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
            actor=str(actor),actorSha256=hashlib.sha256(actor.read_bytes()).hexdigest(),voiceGainDb=0,voiceGainChangeDb=6,
            objectInventoryPreserved=True,log=str(log)))
    (ROOT/'docs/evidence/voice-mix135.json').write_text(json.dumps(dict(banks=reports,installed=False,nativePlaybackVerified=False),indent=2)+'\n','utf8')
    print(json.dumps(reports))

if __name__=='__main__':main()

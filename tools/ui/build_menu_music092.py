"""Build an isolated editor music bank from Beta's mus_main_menu source, never Init.bnk.

The event identity is pinned by MainMenuMusicState::.ctor in Assembly-CSharp.dll:
mus_main_menu -> SetSwitch(4251174751,2005704188) -> source 559056504.
"""
from pathlib import Path
import argparse, hashlib, json, shutil, struct, subprocess, sys, uuid, wave
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/recon'))
from extract_beta_audio import chunks, decode, fnv
NS=uuid.UUID('272192a4-f522-44a7-9dd3-c97c0a09d17c')
def gid(s):return '{'+str(uuid.uuid5(NS,s)).upper()+'}'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,root):
    p.parent.mkdir(parents=True,exist_ok=True);ET.indent(root,space='\t');ET.ElementTree(root).write(p,encoding='utf8',xml_declaration=True)
def unit(section):
    root=ET.Element('WwiseDocument',Type='WorkUnit',ID=gid(section),SchemaVersion='119')
    u=ET.SubElement(ET.SubElement(root,section),'WorkUnit',Name='BetaGwentMenu',ID=gid(section),PersistMode='Standalone')
    return root,u,ET.SubElement(u,'ChildrenList')
def ref(p,name,target,ident,workunit):
    refs=p.find('ReferenceList')
    if refs is None:refs=ET.SubElement(p,'ReferenceList')
    ET.SubElement(ET.SubElement(refs,'Reference',Name=name),'ObjectRef',Name=target,ID=ident,WorkUnitID=workunit)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);a=parser.parse_args();out=a.out.resolve()
    assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists(),'Use a fresh build directory'
    out.mkdir(parents=True)
    package=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/Audio/GeneratedSoundBanks/Windows/Music.pck'
    assert sha(package)=='94544807e869a64e77d12c762e9eb9fca63a8f1c5e1fd588f9d54113515d7b51'
    raw=package.read_bytes();magic,h,v,ls,bs,ms,es=struct.unpack_from('<4s6I',raw);assert magic==b'AKPK' and v==1
    pos=28+ls+bs;count=struct.unpack_from('<I',raw,pos)[0];entries=[struct.unpack_from('<5I',raw,pos+4+i*20) for i in range(count)]
    ident,block,size,start,lang=next(x for x in entries if x[0]==559056504)
    wem=out/'559056504.wem';wem.write_bytes(raw[block*start:block*start+size]);assert wem.read_bytes().startswith(b'RIFF')
    wav=out/'main_menu_theme.wav';info=decode(wem,wav)
    # Separate private project: no original voice project or shipped bank is changed.
    project=out/'wwise';template=ROOT/'tools/ui/wwise-base'
    for p in template.rglob('*'):
        if p.is_file() and p.suffix in ('.wwu','.wproj'):
            dest=project/p.relative_to(template);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    # The accepted project's conversion definition and GUI bus closure are minimal.
    for rel in ['Conversion Settings/Default Work Unit.wwu','Master-Mixer Hierarchy/Default Work Unit.wwu','Audio Devices/Default Work Unit.wwu']:
        shutil.copy2(ROOT/'BetaGwent/audio/wwise'/rel,project/rel)
    mixer_path=project/'Master-Mixer Hierarchy/Default Work Unit.wwu';mixer=ET.parse(mixer_path).getroot()
    gui=next(x for x in mixer.iter('Bus') if x.get('Name')=='GUI')
    parent=next(x for x in mixer.iter() if gui in list(x))
    ET.SubElement(parent,'Bus',Name='Music',ID='{AC8DA8A9-B09E-4E08-BCEC-0FD3D36D101C}')
    write(mixer_path,mixer)
    # Vorbis is usable by both platform encoders. Music follows the native Music bus.
    conversion=project/'Conversion Settings/Default Work Unit.wwu';tree=ET.parse(conversion).getroot();plugin=tree.find('.//ConversionPlugin')
    plugin.set('PluginName','Vorbis');plugin.set('PluginID','4')
    old=plugin.find('PropertyList')
    if old is not None:plugin.remove(old)
    ET.SubElement(ET.SubElement(plugin,'PropertyList'),'Property',Name='QualityFactor',Type='Real32',Value='6');write(conversion,tree)
    actor,au,ac=unit('AudioObjects');sound=ET.SubElement(ac,'Sound',Name='bg_menu_theme',ID=gid('sound'))
    props=ET.SubElement(sound,'PropertyList')
    ET.SubElement(props,'Property',Name='IsLoopingEnabled',Type='bool',Value='True')
    ref(sound,'OutputBus','Music','{AC8DA8A9-B09E-4E08-BCEC-0FD3D36D101C}','{A568D181-8F88-497D-B088-3998BC403D7B}')
    ref(sound,'Conversion','W3 sfx conversion settings','{CD5FEB1F-5340-419B-B846-9C660D7A1B24}','{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
    source=ET.SubElement(ET.SubElement(sound,'ChildrenList'),'AudioFileSource',Name='main_menu_theme',ID=gid('source'))
    ET.SubElement(source,'Language').text='SFX';ET.SubElement(source,'AudioFile').text='BetaGwentMenu\\main_menu_theme.wav'
    ET.SubElement(ET.SubElement(sound,'ActiveSourceList'),'ActiveSource',Name='main_menu_theme',ID=gid('source'),Platform='Linked')
    target=project/'Originals/SFX/BetaGwentMenu/main_menu_theme.wav';target.parent.mkdir(parents=True);shutil.copy2(wav,target)
    write(project/'Actor-Mixer Hierarchy/BetaGwentMenu.wwu',actor)
    events,eu,ec=unit('Events')
    for name,stop in [('bg_menu_music_play',False),('bg_menu_music_stop',True)]:
        ev=ET.SubElement(ec,'Event',Name=name,ID=gid(name));action=ET.SubElement(ET.SubElement(ev,'ChildrenList'),'Action',Name='',ID=gid(name+'action'))
        if stop:ET.SubElement(ET.SubElement(action,'PropertyList'),'Property',Name='ActionType',Type='int16',Value='2')
        ref(action,'Target','bg_menu_theme',gid('sound'),au.get('ID'))
    write(project/'Events/BetaGwentMenu.wwu',events)
    banks,bu,bc=unit('SoundBanks');bank=ET.SubElement(bc,'SoundBank',Name='BetaGwentMenu',ID=gid('bank'));includes=ET.SubElement(bank,'ObjectInclusionList')
    for u,f in [(au,'6'),(eu,'3')]:ET.SubElement(includes,'ObjectRef',Name=u.get('Name'),ID=u.get('ID'),WorkUnitID=u.get('ID'),Origin='Manual',Filter=f)
    ET.SubElement(bank,'ObjectExclusionList');ET.SubElement(bank,'GameSyncExclusionList');write(project/'SoundBanks/BetaGwentMenu.wwu',banks)
    console=json.loads((ROOT/'docs/evidence/audio-bank-build79.json').read_text('utf8'))['command'][0]
    command=[console,'generate-soundbank',str(project/'Project.wproj'),'--platform','Windows','--bank','BetaGwentMenu','--abort-on-load-issues','--no-source-control','--skip-languages']
    with (out/'wwise.log').open('wb') as log:r=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    assert r.returncode==0,(out/'wwise.log').read_text('utf8',errors='replace')[-4000:]
    bnk=project/'GeneratedSoundBanks/Windows/BetaGwentMenu.bnk';parts=dict(chunks(bnk.read_bytes()))
    with (out/'bank-parse.log').open('wb') as log:
        parsed=subprocess.run([sys.executable,str(ROOT/'tools/vendor/audio/wwiser.pyz'),str(bnk),'-d','xml'],stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    assert parsed.returncode==0,'New bank could not be independently parsed'
    nodes=ET.parse(str(bnk)+'.xml').getroot()
    props=nodes.find('.//object[@name="CAkSound"]//object[@name="NodeInitialParams"]')
    loop=next(n for n in props.findall('./object/list/object') if '[Loop]' in n.find('field[@name="pID"]').get('valuefmt',''))
    assert loop.find('field[@name="pValue"]').get('value')=='0','Expected infinite native sound loop'
    report=dict(source=str(package),sourceSha256=sha(package),originalEvent='mus_main_menu',eventId=fnv('mus_main_menu'),switchGroup=4251174751,switchState=2005704188,mediaId=559056504,mediaSha256=sha(wem),pcm=info,
                bank=str(bnk),bankSha256=sha(bnk),bankVersion=struct.unpack_from('<I',parts[b'BKHD'])[0],events=['bg_menu_music_play','bg_menu_music_stop'],loop=True,bus='Music',nativePlaybackVerified=False,installed=False)
    (out/'music.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

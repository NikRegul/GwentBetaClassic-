"""Prepare a Beta soundbank in a private Wwise2023 project.

Does not run Wwise, publish, install an Init bank, or touch REDkit's project.
The bounded import remains available; --full requires the user's project license.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/recon'))
from extract_beta_audio import decode
OUT = ROOT / 'BetaGwent/build/audio79'
PROJECT = ROOT / 'BetaGwent/audio/wwise'
RED_AUDIO = Path(r'D:\GOG Galaxy\Games\The Witcher 3 REDkit\assets\w3_audio')
NAMESPACE = uuid.UUID('902345cd-619f-4523-a01c-b790ddf92b51')


def guid(name):
    return '{' + str(uuid.uuid5(NAMESPACE, name)).upper() + '}'


def xml_write(path, tree):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space='\t')
    ET.ElementTree(tree).write(path, encoding='utf-8', xml_declaration=True)


def windows_only(root):
    for parent in root.iter():
        for child in list(parent):
            if child.get('Platform') not in (None, 'Windows', 'Linked'):
                parent.remove(child)
    return root


def prepare_project():
    # A console-created 2023.1.19 skeleton avoids the REDkit project's custom
    # property defaults/plugins. Only the native GUI bus chain is required.
    base = ROOT / 'tools/ui/wwise-base'
    allowed = {f.relative_to(base) for f in base.rglob('*.wwu')}
    allowed |= {Path(folder) / 'BetaGwent79.wwu' for folder in
                ['Actor-Mixer Hierarchy', 'Events', 'SoundBanks']}
    for previous in PROJECT.rglob('*.wwu'):
        if previous.relative_to(PROJECT) not in allowed:
            previous.unlink()
    for f in base.rglob('*.wwu'):
        xml_write(PROJECT / f.relative_to(base), ET.parse(f).getroot())
    mixer_path = Path('Master-Mixer Hierarchy/Default Work Unit.wwu')
    mixer = ET.parse(RED_AUDIO / mixer_path).getroot()
    # Keep the existing bus GUIDs so the additional bank targets TW3's Init.
    master = mixer.find('./Busses/WorkUnit/ChildrenList/Bus')
    root_children = mixer.find('./Busses/WorkUnit/ChildrenList')
    for node in list(root_children):
        if node is not master: root_children.remove(node)
    immerse = next(b for b in master.find('ChildrenList') if b.get('Name') == 'Immerse')
    gui = next(b for b in immerse.find('ChildrenList') if b.get('Name') == 'GUI')
    master.find('ChildrenList').clear(); master.find('ChildrenList').append(immerse)
    immerse.find('ChildrenList').clear(); immerse.find('ChildrenList').append(gui)
    for bus in [master, immerse, gui]:
        for node in list(bus):
            if node.tag in ['ObjectLists', 'StateInfo', 'EffectList', 'AuxSendValues']:
                bus.remove(node)
    xml_write(PROJECT / mixer_path, windows_only(mixer))
    device_path = Path('Audio Devices/Default Work Unit.wwu')
    device = ET.parse(RED_AUDIO / device_path).getroot()
    for children in device.iter('ChildrenList'):
        for node in list(children):
            if node.get('Name') != 'System': children.remove(node)
    for node in device.iter('AudioDevice'):
        for child in list(node):
            if child.tag in ['ObjectLists', 'EffectList', 'StateInfo']:
                node.remove(child)
    xml_write(PROJECT / device_path, windows_only(device))
    conversion_path = Path('Conversion Settings/Default Work Unit.wwu')
    conversions = ET.parse(RED_AUDIO / conversion_path).getroot()
    children = conversions.find('./Conversions/WorkUnit/ChildrenList')
    for node in list(children):
        if node.get('Name') != 'W3 sfx conversion settings': children.remove(node)
    xml_write(PROJECT / conversion_path, windows_only(conversions))
    project = ET.parse(base / 'Project.wproj').getroot()
    existing=PROJECT / 'BetaGwent79.wproj'
    if existing.exists():
        prior=ET.parse(existing).getroot()
        # Preserve the user's project license. Never print/license-switch it.
        current=next((p for p in prior.iter('Property') if p.get('Name')=='LicenseKey'),None)
        for owner in project.iter():
            for prop in list(owner):
                if prop.tag=='Property' and prop.get('Name')=='LicenseKey' and current is not None:
                    owner.remove(prop);owner.append(copy.deepcopy(current))
    project.find('./ProjectInfo/Project').set('Name', 'BetaGwent79')
    project.find('./ProjectInfo/Project').set('ID', '{548A8C7F-A06F-4B97-B57D-3F54C03F089D}')
    default_conversion = project.find('./ProjectInfo/Project/DefaultConversion')
    default_conversion.set('Name', 'W3 sfx conversion settings')
    default_conversion.set('ID', '{CD5FEB1F-5340-419B-B846-9C660D7A1B24}')
    for prop in project.iter('Property'):
        if prop.get('Name') == 'SoundBankPaths':
            for value in prop.iter('Value'):
                value.text = 'GeneratedSoundBanks\\Windows\\'
    for obj in project.iter('ObjectRef'):
        if obj.get('Name') == 'Master Audio Bus':
            obj.set('ID', master.get('ID')); obj.set('WorkUnitID', mixer.find('./Busses/WorkUnit').get('ID'))
        if obj.get('Name') == 'Default Conversion Settings':
            obj.set('Name', 'W3 sfx conversion settings'); obj.set('ID', '{CD5FEB1F-5340-419B-B846-9C660D7A1B24}')
            obj.set('WorkUnitID', '{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
    xml_write(PROJECT / 'BetaGwent79.wproj', project)


def workunit(section, name):
    ident = guid(section + name)
    root = ET.Element('WwiseDocument', Type='WorkUnit', ID=ident, SchemaVersion='119')
    unit = ET.SubElement(ET.SubElement(root, section), 'WorkUnit', Name=name, ID=ident, PersistMode='Standalone')
    return root, unit, ET.SubElement(unit, 'ChildrenList')


def ref(parent, name, target_name, target_id, unit_id):
    ref_list = parent.find('ReferenceList')
    if ref_list is None:
        ref_list = ET.SubElement(parent, 'ReferenceList')
    entry = ET.SubElement(ref_list, 'Reference', Name=name)
    ET.SubElement(entry, 'ObjectRef', Name=target_name, ID=target_id, WorkUnitID=unit_id)


def script_lookup(name, result_type, values, empty):
    items = sorted(values.items()); groups = [items[i:i + 60] for i in range(0, len(items), 60)]
    lines = [f'function {name}(id : int) : {result_type}', '{']
    for i, group in enumerate(groups):
        lines.append(f'    if (id <= {group[-1][0]}) return {name}{i}(id);')
    lines += ['    return ' + empty + ';', '}']
    for i, group in enumerate(groups):
        lines += [f'function {name}{i}(id : int) : {result_type}', '{', '    switch (id)', '    {']
        lines += [f'        case {ident}: return {value};' for ident, value in group]
        lines += ['        default: break;', '    }', '    return ' + empty + ';', '}']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--full',action='store_true');args=parser.parse_args()
    extraction = json.loads((ROOT / 'docs/evidence/beta-audio-extract79.json').read_text('utf8'))
    if not extraction['decodedVoices']:
        raise RuntimeError('Decode Russian voices first')
    sliced = json.loads((ROOT / 'data/beta924/duel/slice.json').read_text('utf8'))
    playable = {c['templateId'] for c in sliced['cards']}
    priority = sorted(playable) if args.full else list(dict.fromkeys(sliced['leaderIds'] + [ident for p in sliced['presets'] for ident in p['templateIds']]))
    cards = {c['templateId']:c for c in extraction['cards']}
    voices = {v['key']:v for v in extraction['voices'] if v['role'] == 'cards'}
    media = {}; selected_voice = {}
    for ident in priority:
        card = cards.get(ident)
        if not card or not any(t['type'] in ('2', '3', '4') and t['vo'].lower() == 'true' for t in card['triggers']):
            continue
        candidates = [v for v in card['defaultVoices'] if v['key'] in voices]
        if not candidates:
            continue
        selected_voice[ident] = candidates[0]['key']
        for candidate in (candidates if args.full else candidates[:1]):
            key=candidate['key']
            media.setdefault('vo_' + key, dict(key='vo_' + key, role='voice', source=voices[key]['pcm'], voiceKey=key))
    selected_effect = {}
    for ident in priority:
        card = cards.get(ident)
        if not card:
            continue
        trigger = next((t for t in card['triggers'] if t['type'] == '3'), None)
        effect = next((e for e in card['effects'] if trigger and e['type'] == trigger['sfx']), None)
        if not effect:
            continue
        event_id = int(effect['event']) & 0xffffffff
        key = 'fx_' + str(event_id)
        if not args.full and key not in media and len(media) >= 200:
            continue
        media.setdefault(key, dict(key=key, role='sfx', originalEventId=event_id))
        selected_effect[ident] = key
    reveal_effect, transform_effect, voice_triggers = {}, {}, {}
    ui_bindings, cue_bindings, weather_bindings = {}, {}, {}
    def add_effect(event_id):
        key = 'fx_' + str(event_id & 0xffffffff)
        media.setdefault(key, dict(key=key, role='sfx', originalEventId=event_id & 0xffffffff))
        return key
    if args.full:
        refs = json.loads((ROOT / 'docs/evidence/beta-sound-events86.json').read_text('utf8'))
        for ident in priority:
            card = cards.get(ident)
            if not card: continue
            voice_triggers[ident] = sum(1 << int(t['type']) for t in card['triggers'] if t['vo'].lower() == 'true')
            for trigger_type, lookup in [('2', reveal_effect), ('4', transform_effect)]:
                trigger = next((t for t in card['triggers'] if t['type'] == trigger_type), None)
                effect = next((e for e in card['effects'] if trigger and e['type'] == trigger['sfx']), None)
                if effect: lookup[ident] = add_effect(int(effect['event']))
        def ui(component, field):
            return next(e['eventId'] for e in refs['ui'] if e['component'] == component and e['field'] == field)
        ui_bindings = {1:add_effect(ui('UIBattleChoicePanelSoundHandler','/GenericClick')),
                       2:add_effect(ui('UIBattleChoicePanelSoundHandler','/Show')),
                       3:add_effect(ui('UIBattleChoicePanelSoundHandler','/CardHovered')),
                       4:add_effect(ui('UIBattleChoicePanelSoundHandler','/GenericCancel')),
                       5:add_effect(ui('UIBattleChoicePanelSoundHandler','/CardReplaced'))}
        vfx = {e['object']:e['eventId'] for e in refs['vfx']}
        # All battle VFX are staged, including elemental variants for later polish.
        for entry in refs['vfx']:
            add_effect(entry['eventId'])
            if entry['hideEventId']: add_effect(entry['hideEventId'])
        cue_bindings = {3:add_effect(vfx['PowerDirectPhysical']), 5:add_effect(ui('GameIntroSoundHandler','/FadeOutSfx/Events/0')),
            6:add_effect(ui('MessageRendererSoundHandler','/LocalHalfCrown')), 7:add_effect(ui('GameIntroSoundHandler','/VsSfx/Events/0')),
            32:add_effect(vfx['CardTimerVFX']), 9:add_effect(vfx['LockToken']), 10:add_effect(vfx['NatureTransform']),
            11:add_effect(vfx['DestroyDestroyBlood']), 12:add_effect(vfx['BanishCardEffect']),
            14:add_effect(ui('UIBattleChoicePanelSoundHandler','/CardReplaced')), 15:add_effect(vfx['SpawnBlink']),
            16:add_effect(vfx['SpawnBlink']), 17:add_effect(ui('GameIntroSoundHandler','/FadeOutSfx/Events/0')),
            20:add_effect(vfx['PowerDirectPhysical']), 21:add_effect(vfx['PowerUp']),
            22:add_effect(vfx['ArmorDecrease']), 23:add_effect(vfx['ArmorIncrease']),
            24:add_effect(vfx['AmbushEffect']), 25:add_effect(vfx['NatureTransform']),
            26:add_effect(vfx['ResilienceToken']), 27:add_effect(vfx['ResetPhysicalBuff']),
            28:add_effect(vfx['GoldLanding']),
            29:add_effect(ui('MessageRendererSoundHandler','/OpponentHalfCrown')),
            30:add_effect(ui('MessageRendererSoundHandler','/LocalFullCrown')),
            31:add_effect(ui('MessageRendererSoundHandler','/OpponentFullCrown'))}
        weather_bindings = {0:add_effect(vfx['BoardEffect_ClearWeather']),1:add_effect(vfx['FrostTokenEffect']),
            2:add_effect(vfx['FogTokenEffect']),4:add_effect(vfx['RainTokenEffect']),
            16:add_effect(vfx['DroughtTokenEffect']),32:add_effect(vfx['RaghNarRoogTokenEffect']),
            64:add_effect(vfx['SkelligeStormTokenEffect']),128:add_effect(vfx['GoldenFrothTokenEffect']),
            256:add_effect(vfx['Moonlight']),512:add_effect(vfx['PitfallTrapTokenEffect']),
            1024:add_effect(vfx['RowEffect_DragonsDreamSmoke']),2048:add_effect(vfx['BloodMoon'])}
    effects = [m['originalEventId'] for m in media.values() if m['role'] == 'sfx']
    txtp_dir = OUT / 'txtp'
    if effects:
        extract_args = [sys.executable, str(ROOT / 'tools/vendor/audio/wwiser.pyz'),
                str(OUT / 'banks/Core/*.bnk'), str(OUT / 'banks/Default/*.bnk'), str(OUT / 'banks/Cards/*.bnk'), str(OUT / 'banks/Vfx/*.bnk'),
                '-d', 'none', '-g', '-gd', '-go', str(txtp_dir),
                '-gw', str(OUT / 'banks/Cards'), '-gf'] + [str(i) for i in effects]
        result = subprocess.run(extract_args, capture_output=True, timeout=120, creationflags=subprocess.CREATE_NO_WINDOW)
        (OUT / 'wwiser-generate.log').write_bytes(result.stdout + result.stderr)
        if result.returncode:
            raise RuntimeError('wwiser failed; inspect wwiser-generate.log')
        generated = sorted(txtp_dir.glob('*.txtp'))
        # wwiser's -gw override applies to embedded bank references too. Each
        # package has its own bank directory; point rendered playlists at the
        # actual pinned bank rather than assuming everything is in Cards.
        bank_paths = {p.name:p.as_posix() for p in (OUT / 'banks').rglob('*.bnk')}
        for playlist in generated:
            text = playlist.read_text('utf8')
            corrected = re.sub(r'[A-Za-z]:/[^\r\n#]+?/([^/\r\n]+\.bnk)',
                lambda m: bank_paths.get(m[1], m[0]), text)
            if corrected != text: playlist.write_text(corrected, encoding='utf8')
        for item in list(media.values()):
            if item['role'] != 'sfx':
                continue
            matches = [p for p in generated if re.search(r'(?<!\d)' + str(item['originalEventId']) + r'(?!\d)', p.read_text('utf8'))]
            if not matches:
                raise RuntimeError('No rendered event for ' + item['key'])
            item['txtp'] = str(matches[0].relative_to(ROOT))
            item['source'] = decode(matches[0], OUT / 'wav/sfx' / (item['key'] + '.wav'))
    # Clone only the small native dependency closure, never REDkit's whole project.
    PROJECT.mkdir(parents=True, exist_ok=True)
    prepare_project()
    actor_root, actor_unit, actor_children = workunit('AudioObjects', 'BetaGwent79')
    mixer_ids = {}
    for role in ['voice', 'sfx']:
        name = 'bg79_' + role
        mixer = ET.SubElement(actor_children, 'ActorMixer', Name=name, ID=guid(name))
        mixer_ids[role] = guid(name)
        prop_list = ET.SubElement(mixer, 'PropertyList')
        ET.SubElement(prop_list, 'Property', Name='Volume', Type='Real64', Value='-6' if role == 'voice' else '-9')
        ref(mixer, 'OutputBus', 'GUI', '{FD72CAE9-14F8-4BA2-A9F2-CF69D62BC9AB}', '{A568D181-8F88-497D-B088-3998BC403D7B}')
        ref(mixer, 'Conversion', 'W3 sfx conversion settings', '{CD5FEB1F-5340-419B-B846-9C660D7A1B24}', '{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
        children = ET.SubElement(mixer, 'ChildrenList')
        for item in media.values():
            if item['role'] != role:
                continue
            sound_id = guid('sound' + item['key']); source_id = guid('source' + item['key'])
            item['wwiseName'] = re.sub(r'[^A-Za-z0-9_]', '_', item['key'])
            sound = ET.SubElement(children, 'Sound', Name=item['wwiseName'], ID=sound_id)
            ref(sound, 'OutputBus', 'GUI', '{FD72CAE9-14F8-4BA2-A9F2-CF69D62BC9AB}', '{A568D181-8F88-497D-B088-3998BC403D7B}')
            ref(sound, 'Conversion', 'W3 sfx conversion settings', '{CD5FEB1F-5340-419B-B846-9C660D7A1B24}', '{EF9CA0AB-7C72-4A75-875D-4E59C5D1D875}')
            source = ET.SubElement(ET.SubElement(sound, 'ChildrenList'), 'AudioFileSource', Name=item['wwiseName'], ID=source_id)
            ET.SubElement(source, 'Language').text = 'SFX'
            ET.SubElement(source, 'AudioFile').text = 'BetaGwent79\\' + item['key'] + '.wav'
            ET.SubElement(ET.SubElement(sound, 'ActiveSourceList'), 'ActiveSource', Name=item['wwiseName'], ID=source_id, Platform='Linked')
            wav = PROJECT / 'Originals/SFX/BetaGwent79' / (item['key'] + '.wav')
            wav.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(ROOT / item['source']['path'], wav)
    xml_write(PROJECT / 'Actor-Mixer Hierarchy/BetaGwent79.wwu', actor_root)
    event_root, event_unit, event_children = workunit('Events', 'BetaGwent79')
    def event(name, target_name, target_id, stop=False):
        ev = ET.SubElement(event_children, 'Event', Name=name, ID=guid('event' + name))
        action = ET.SubElement(ET.SubElement(ev, 'ChildrenList'), 'Action', Name='', ID=guid('action' + name))
        if stop:
            ET.SubElement(ET.SubElement(action, 'PropertyList'), 'Property', Name='ActionType', Type='int16', Value='2')
        ref(action, 'Target', target_name, target_id, actor_unit.get('ID'))
    for item in media.values():
        item['event'] = 'bg79_' + item['wwiseName']; event(item['event'], item['wwiseName'], guid('sound' + item['key']))
    for role in ['voice', 'sfx']:
        event('bg79_stop_' + role, 'bg79_' + role, mixer_ids[role], True)
    xml_write(PROJECT / 'Events/BetaGwent79.wwu', event_root)
    bank_root, bank_unit, bank_children = workunit('SoundBanks', 'BetaGwent79')
    bank = ET.SubElement(bank_children, 'SoundBank', Name='BetaGwent79', ID=guid('bank'))
    inclusions = ET.SubElement(bank, 'ObjectInclusionList')
    for unit, filt in [(actor_unit, '6'), (event_unit, '3')]:
        ET.SubElement(inclusions, 'ObjectRef', Name=unit.get('Name'), ID=unit.get('ID'), WorkUnitID=unit.get('ID'), Origin='Manual', Filter=filt)
    ET.SubElement(bank, 'ObjectExclusionList'); ET.SubElement(bank, 'GameSyncExclusionList')
    xml_write(PROJECT / 'SoundBanks/BetaGwent79.wwu', bank_root)
    # Additional templates may explicitly share AudioId/default voice or effect.
    voice_lookup = {}; effect_lookup = {}; duration_lookup = {}
    for ident in playable:
        card = cards.get(ident)
        if not card:
            continue
        first = card['defaultVoices'][:1]
        if first and 'vo_' + first[0]['key'] in media and any(t['type'] in ('2','3','4') and t['vo'].lower() == 'true' for t in card['triggers']):
            item = media['vo_' + first[0]['key']]
            voice_lookup[ident] = json.dumps(item['event']); duration_lookup[ident] = f'{item["source"]["durationMs"] / 1000:.3f}f'
        trigger = next((t for t in card['triggers'] if t['type'] == '3'), None)
        effect = next((e for e in card['effects'] if trigger and e['type'] == trigger['sfx']), None)
        key = 'fx_' + str(int(effect['event']) & 0xffffffff) if effect else ''
        if key in media:
            effect_lookup[ident] = json.dumps(media[key]['event'])
    variants={}
    for ident in playable:
        card=cards.get(ident)
        if card and ident in voice_lookup:
            variants[ident]=[(media['vo_'+v['key']],int(v['likelihood'])) for v in card['defaultVoices'] if 'vo_'+v['key'] in media]
    def variant_function(name,typ,duration=False):
        groups=[list(sorted(variants.items()))[i:i+15] for i in range(0,len(variants),15)]
        out=[f'function {name}(id : int, roll : int) : {typ}','{']
        for i,group in enumerate(groups):out += [f'    if(id <= {group[-1][0]})return {name}Part{i}(id,roll);']
        out+=['    return '+('0.0f' if duration else '""')+';','}']
        for i,group in enumerate(groups):
            out += [f'function {name}Part{i}(id : int, roll : int) : {typ}','{','    switch(id)','    {']
            for ident,items in group:
                out += [f'    case {ident}:']
                total=sum(weight for _,weight in items); threshold=0
                for item,weight in items:
                    threshold+=weight
                    value=f'{item["source"]["durationMs"]/1000:.3f}f' if duration else json.dumps(item['event'])
                    out += [f'        if(roll%{total}<{threshold})return {value};']
                out+=['        break;']
            out+=['    default: break;','    }','    return '+('0.0f' if duration else '""')+';','}']
        return '\n'.join(out)
    # False until a successful Wwise build and explicit workspace installation.
    lines = ['// Generated from pinned CardAudio.xml. Source banks128 are not runtime banks.',
             'function BetaGwentAudioBankInstalled() : bool { return false; }',
             script_lookup('BetaGwentAudioVoice', 'string', voice_lookup, '""'),
             script_lookup('BetaGwentAudioVoiceDuration', 'float', duration_lookup, '0.0f'),
             script_lookup('BetaGwentAudioEffect', 'string', effect_lookup, '""'),
             variant_function('BetaGwentAudioVoiceVariant','string'),
             variant_function('BetaGwentAudioVoiceVariantDuration','float',True)]
    for name,lookup,typ,empty in [('BetaGwentAudioRevealEffect',reveal_effect,'string','""'),
            ('BetaGwentAudioTransformEffect',transform_effect,'string','""'),
            ('BetaGwentAudioVoiceTriggers',voice_triggers,'int','0'),
            ('BetaGwentAudioUi',ui_bindings,'string','""'),
            ('BetaGwentAudioCue',cue_bindings,'string','""'),
            ('BetaGwentAudioWeather',weather_bindings,'string','""')]:
        lines.append(script_lookup(name,typ,{k:(json.dumps(media[v]['event']) if typ=='string' else str(v)) for k,v in lookup.items()},empty) if lookup else f'function {name}(id : int) : {typ} {{ return {empty}; }}')
    script_path=ROOT/('BetaGwent/audio/generated/duelAudioCatalog-full.ws' if args.full else 'BetaGwent/development/scripts/game/betagwent/duelAudioCatalog.ws')
    script_path.parent.mkdir(parents=True,exist_ok=True)
    script_path.write_text('\n\n'.join(lines) + '\n', encoding='utf8')
    report = dict(stage=86 if args.full else 79, fullImport=args.full, voiceVariantBindings=sum(len(v) for v in variants.values()), project=str(PROJECT / 'BetaGwent79.wproj'), media=list(media.values()),
        mediaCount=len(media), voiceBindings=len(voice_lookup), effectBindings=len(effect_lookup),
        originalCardAudioSha256=extraction['cardAudioXmlSha256'], importedRussianVoicesAs='SFX (fixed Russian, GUI bus)',
        wwiseBuildVerified=False, bankInstalled=False, runtimeVerified=False,
        ambushBindings=len(reveal_effect),transformBindings=len(transform_effect),uiBindings=len(ui_bindings),cueBindings=len(cue_bindings),weatherBindings=len(weather_bindings),voiceSelection='Original likelihood weights; original trigger gating; presentation RNG only',
        limitation='Russian battle voices and all standard play effects; Beta UI/VFX cues. Premium-preview loops are not battle audio. Music and optional taunt/announcer cosmetics remain outside this bank.')
    (ROOT / 'docs/evidence/audio-import79.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(f'Prepared {len(media)} WAV files: {len(voice_lookup)} voice bindings, {len(effect_lookup)} Beta play effect bindings. Wwise compilation pending.')


if __name__ == '__main__':
    main()

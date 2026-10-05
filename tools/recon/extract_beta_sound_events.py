"""Read pinned Beta serialized sound references; do not modify Unity assets.

Stripped VisualEffectSoundHandler layout is checked against every bank hash and
the object extent. Card sound types are verified separately from managed IL:
Standard=1, Premium=2, Ambush=3. Premium previews are not battle effects.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
sys.path.insert(0, str(ROOT / 'tools/recon'))
import UnityPy
from extract_beta_audio import fnv

CLIENT = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data'
sources = {}
events = []
for relative in ['StreamingAssets/AssetBundles/gui/prefabs/game_base',
                 'StreamingAssets/AssetBundles/gui/prefabs/deckbuilder_base',
                 'StreamingAssets/AssetBundles/gui/prefabs/global_base']:
    source = CLIENT / relative
    sources[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
    for obj in UnityPy.load(str(source)).objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        tree = obj.read_typetree()
        component = obj.read().m_Script.read().m_ClassName
        if 'Sound' not in component:
            continue
        def walk(value, field):
            if isinstance(value, dict):
                if 'ID' in value and 'EnableActionOnEvent' in value and value['ID']:
                    events.append(dict(source=relative, component=component, field=field,
                                       eventId=value['ID'] & 0xffffffff))
                elif value.get('m_PathID'):
                    target = obj.assets_file.objects.get(value['m_PathID'])
                    if target and target.type.name == 'MonoBehaviour':
                        linked = target.read_typetree()
                        if 'Events' in linked:
                            walk(linked, field)
                for key, child in value.items():
                    walk(child, field + '/' + key)
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, field + '/' + str(index))
        walk(tree, '')

source = CLIENT / 'sharedassets8.assets'
sources[str(source)] = hashlib.sha256(source.read_bytes()).hexdigest()
vfx = []
for obj in UnityPy.load(str(source)).objects:
    if obj.type.name != 'MonoBehaviour':
        continue
    data = obj.read(check_read=False)
    component = data.m_Script.read().m_ClassName
    if component not in ('VisualEffectSoundHandler', 'CardTokenVisualEffectSoundHandler'):
        continue
    raw = obj.get_raw_data()
    # MonoBehaviour header + tracking bool/alignment, listener enum, container PPtr.
    pos = 32 + (len(data.m_Name.encode('utf8')) + 3) // 4 * 4 + 20
    bank_id = struct.unpack_from('<I', raw, pos)[0]
    pos += 4
    def string():
        global pos
        length = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
        value = raw[pos:pos + length].decode('utf8')
        pos += (length + 3) // 4 * 4
        return value
    bank_name, package = string(), string()
    event_id = struct.unpack_from('<I', raw, pos)[0]
    pos += 4
    hide_id = 0
    if component == 'CardTokenVisualEffectSoundHandler':
        hide_id = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
    assert pos == len(raw) and fnv(bank_name) == bank_id and package.lower() == 'vfx.pck'
    vfx.append(dict(object=data.m_GameObject.read().m_Name, eventId=event_id,
                    hideEventId=hide_id, bankName=bank_name, bankId=bank_id))
assert len(vfx) == 57
report = dict(stage=86, sourceHashes=sources, sourceUnchanged=all(
    hashlib.sha256(Path(p).read_bytes()).hexdigest() == sha for p, sha in sources.items()),
    ui=events, vfx=vfx, premiumPreviewImported=False)
(ROOT / 'docs/evidence/beta-sound-events86.json').write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(f'Mapped {len(events)} UI references and {len(vfx)} VFX references from original Beta.')

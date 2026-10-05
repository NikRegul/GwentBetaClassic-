"""Read-only extraction of Beta boards, weather and combat presentation.

Exports Unity configuration/curves and original textures for adaptation to GFx.
Does not claim that Unity particles or shaders run directly in The Witcher 3.
"""
from pathlib import Path
from collections import Counter
import argparse
import gzip
import hashlib
import json
import re
import sys
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
import UnityPy
CLIENT = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data'
OUTPUT = ROOT / 'BetaGwent/build/beta-presentation91'
PATTERN = re.compile(r'weather|frost|fog|rain|power|destroy|banish|consume|projectile|damage|hit|roweffect|spawn|resurrect|ambush', re.I)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(value):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', value)[:110]

def json_default(value):
    if isinstance(value, bytes):
        return {'binaryHex': value.hex()}
    raise TypeError(type(value).__name__)

def hierarchy(environment):
    names, transforms, by_go = {}, {}, {}
    for obj in environment.objects:
        if obj.type.name == 'GameObject':
            names[obj.path_id] = obj.read().m_Name
        elif obj.type.name in ('Transform', 'RectTransform'):
            data = obj.read()
            transforms[obj.path_id] = (data.m_GameObject.path_id, data.m_Father.path_id)
            by_go[data.m_GameObject.path_id] = obj.path_id
    def path(go):
        result, visited = [], set()
        transform = by_go.get(go)
        while transform in transforms and transform not in visited:
            visited.add(transform)
            go, transform = transforms[transform]
            result.append(names.get(go, str(go)))
        return '/'.join(reversed(result)) or names.get(go, str(go))
    return path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', action='store_true')
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources, objects, errors = {}, [], []
    for relative in ['sharedassets8.assets', 'StreamingAssets/AssetBundles/gui/prefabs/game_base']:
        source = CLIENT / relative
        sources[str(source)] = sha(source)
        environment = UnityPy.load(str(source))
        object_path = hierarchy(environment)
        selected = []
        for obj in environment.objects:
            if obj.type.name not in ('ParticleSystem', 'ParticleSystemRenderer', 'AnimationClip', 'MonoBehaviour'):
                continue
            data = obj.read(check_read=False)
            go = getattr(data, 'm_GameObject', None)
            path = object_path(go.path_id) if go else getattr(data, 'm_Name', '')
            component = ''
            if obj.type.name == 'MonoBehaviour':
                try:
                    component = data.m_Script.read().m_ClassName
                except Exception:
                    continue
                if not any(word in component for word in ('Animation', 'MovementParams', 'ProceduralAnimation', 'VisualEffect')):
                    continue
            if not PATTERN.search(path) and not any(word in component for word in ('MovementParams', 'ProceduralAnimation')):
                continue
            item = dict(source=relative, type=obj.type.name, pathId=obj.path_id, hierarchy=path, component=component)
            objects.append(item)
            selected.append(obj)
            if args.inventory:
                continue
            directory = OUTPUT / ('weather' if re.search(r'weather|frost|fog|rain', path, re.I) else 'combat')
            directory.mkdir(exist_ok=True)
            stem = safe(relative.split('/')[-1]) + '-' + str(obj.path_id) + '-' + safe(path.split('/')[-1] or component)
            raw_path = directory / (stem + '.bin')
            raw_path.write_bytes(obj.get_raw_data())
            item['raw'] = str(raw_path)
            item['rawSha256'] = sha(raw_path)
            try:
                tree = obj.read_typetree()
                config = directory / (stem + '.json.gz')
                payload = json.dumps(tree, ensure_ascii=False, default=json_default).encode('utf8')
                config.write_bytes(gzip.compress(payload, mtime=0))
                item['configuration'] = str(config)
            except Exception as error:
                item['configurationUnavailable'] = str(error)
        if not args.inventory:
            # Resolve texture dependencies from the selected renderers' material
            # bindings. They identify the actual weather/impact textures.
            texture_ids = set()
            material_ids = set()
            for obj in selected:
                if obj.type.name != 'ParticleSystemRenderer':
                    continue
                for pointer in obj.read().m_Materials:
                    if not pointer.path_id:
                        continue
                    try:
                        material_obj = pointer.deref()
                        material = material_obj.read()
                        material_ids.add(material_obj.path_id)
                        tree = material_obj.read_typetree()
                        mat_dir = OUTPUT / 'materials'
                        mat_dir.mkdir(exist_ok=True)
                        mat_path = mat_dir / (safe(relative.split('/')[-1]) + '-' + str(material_obj.path_id) + '.json')
                        mat_path.write_text(json.dumps(tree, default=json_default, indent=2), 'utf8')
                        for key, binding in material.m_SavedProperties.m_TexEnvs:
                            tex = binding.m_Texture
                            if tex.path_id:
                                texture_obj = tex.deref()
                                texture_ids.add((texture_obj.assets_file.name, texture_obj.path_id))
                    except Exception as error:
                        errors.append(dict(source=relative, renderer=obj.path_id, material=pointer.path_id, error=str(error)))
            for obj in environment.objects:
                if obj.type.name != 'Texture2D' or (obj.assets_file.name, obj.path_id) not in texture_ids:
                    continue
                data = obj.read()
                texture_dir = OUTPUT / 'textures'
                texture_dir.mkdir(exist_ok=True)
                dest = texture_dir / (safe(relative.split('/')[-1]) + '-' + str(obj.path_id) + '-' + safe(data.m_Name) + '.png')
                try:
                    data.image.save(dest)
                    objects.append(dict(source=relative, type='Texture2D', pathId=obj.path_id, name=data.m_Name,
                                        image=str(dest), size=[data.m_Width, data.m_Height], sha256=sha(dest)))
                except Exception as error:
                    errors.append(dict(source=relative, texture=obj.path_id, error=str(error)))
    boards, board_geometry = [], []
    if not args.inventory:
        bundles = CLIENT / 'StreamingAssets/AssetBundles/boards'
        for source in sorted(bundles.rglob('*')):
            if not source.is_file() or source.suffix == '.manifest' or source.name == 'manifest':
                continue
            sources[str(source)] = sha(source)
            for obj in UnityPy.load(str(source)).objects:
                directory = OUTPUT / 'boards' / source.relative_to(bundles).parent / source.name
                directory.mkdir(parents=True, exist_ok=True)
                data = obj.read()
                if obj.type.name == 'Mesh':
                    dest = directory / (str(obj.path_id) + '-' + safe(data.m_Name) + '.obj')
                    dest.write_text(data.export(), 'utf8')
                    board_geometry.append(dict(bundle=str(source.relative_to(bundles)), type='Mesh', name=data.m_Name,
                                               pathId=obj.path_id, file=str(dest), sha256=sha(dest)))
                elif obj.type.name in ('Material', 'Transform', 'GameObject', 'MeshRenderer', 'MeshFilter'):
                    dest = directory / (str(obj.path_id) + '-' + obj.type.name + '.json')
                    dest.write_text(json.dumps(obj.read_typetree(), default=json_default, indent=2), 'utf8')
                    board_geometry.append(dict(bundle=str(source.relative_to(bundles)), type=obj.type.name,
                                               pathId=obj.path_id, file=str(dest), sha256=sha(dest)))
                if obj.type.name != 'Texture2D':
                    continue
                dest = directory / (str(obj.path_id) + '-' + safe(data.m_Name) + '.png')
                try:
                    data.image.save(dest)
                    boards.append(dict(bundle=str(source.relative_to(bundles)), name=data.m_Name, pathId=obj.path_id,
                                       image=str(dest), size=[data.m_Width, data.m_Height], sha256=sha(dest)))
                except Exception as error:
                    errors.append(dict(source=str(source), texture=obj.path_id, error=str(error)))
        sheet = Image.new('RGB', (1200, ((len(boards)+4)//5)*190), '#222932')
        draw = ImageDraw.Draw(sheet)
        for i, board in enumerate(boards):
            im = Image.open(board['image']).convert('RGBA');im.thumbnail((224, 144))
            x, y = (i % 5) * 240, (i // 5) * 190
            sheet.paste(im, (x+8, y+4), im)
            draw.text((x+8, y+150), board['name'][:30], fill='white')
            draw.text((x+8, y+166), board['bundle'], fill='white')
        sheet.save(OUTPUT / 'boards-contact.png')
    assert all(sha(Path(path)) == value for path, value in sources.items()), 'Source changed'
    report = dict(stage=91, sourceHashes=sources, sourceUnchanged=True, objects=objects, boards=boards, boardGeometry=board_geometry,
                  errors=errors, inventoryOnly=args.inventory, nativeRuntimeVerified=False)
    report_path = OUTPUT / ('inventory.json' if args.inventory else 'manifest.json')
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
    print(json.dumps(dict(objects=dict(Counter(item['type'] for item in objects)), boards=len(boards),
                         boardMeshes=sum(item['type']=='Mesh' for item in board_geometry),
                         errors=len(errors), report=str(report_path)), ensure_ascii=False))
    if args.inventory:
        for item in objects:
            if item['type'] == 'ParticleSystem':
                print(item['source'], item['pathId'], item['hierarchy'])

if __name__ == '__main__':
    main()

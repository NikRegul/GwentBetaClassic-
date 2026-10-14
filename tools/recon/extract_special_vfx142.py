"""Inventory every collectible beta special and export its original VFX sources.

Unity MonoBehaviour type trees omit custom fields here. Decode the two nested
Lists from the schema in Assembly-CSharp.dll, check byte consumption, and keep
raw components as well as available particle/material/texture configuration.
"""
from pathlib import Path
import gzip
import hashlib
import json
import math
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
import UnityPy

OUT = ROOT / 'BetaGwent/build/special-vfx142'
SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
ELEMENTS = {1:'Physical',16:'Fire',32:'Ice',64:'Lightning',128:'Earth',256:'Air',
            512:'LightMagic',1024:'DarkMagic',2048:'Nature',4096:'Water',8192:'Poison',16384:'Blood',32768:'Bubbles'}

def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', 'utf8')

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = sha(SOURCE)
    env = UnityPy.load(str(SOURCE))
    objects = {o.path_id:o for o in env.objects if o.assets_file.name == SOURCE.name}
    scripts, names, gos, parents, transforms = {}, {}, {}, {}, {}
    for oid, o in objects.items():
        if o.type.name == 'GameObject': names[oid] = o.read().m_Name
        if o.type.name in ('Transform','RectTransform'):
            d = o.read(); transforms[oid] = d.m_GameObject.path_id
            parents[oid] = d.m_Father.path_id
        if o.type.name == 'MonoBehaviour':
            d = o.read(check_read=False)
            try: scripts[oid] = d.m_Script.read().m_ClassName
            except Exception: continue
            gos[oid] = d.m_GameObject.path_id
    def binding(oid):
        return dict(pathId=oid, prefab=names.get(gos.get(oid), ''), component=scripts.get(oid,'')) if oid else None
    registry = {}
    suffix_sizes = {'CardPowerAttackVFXHandlerData':24, 'CardMovementVFXHandlerData':None,
                    'LocationTokenVFXHandlerData':None}
    for oid, cls in scripts.items():
        if not (cls.endswith('VFXHandlerData') and cls not in ('CardSpawnVFXHandlerData','CardTokenVFXHandlerData')) and cls != 'AttackApplyMethodData': continue
        raw = objects[oid].get_raw_data()
        offset = (32 + struct.unpack_from('<i',raw,28)[0]+3)//4*4
        def integer():
            nonlocal offset
            value = struct.unpack_from('<i',raw,offset)[0];offset += 4
            return value
        def count():
            value = integer(); assert 0 <= value <= 1024, (cls,offset,value)
            return value
        def pointer():
            nonlocal offset
            file_id, path_id = struct.unpack_from('<iq',raw,offset);offset += 12
            assert file_id == 0 and (path_id == 0 or path_id in objects)
            return path_id
        rows = []
        for method in range(count()):
            effects = [pointer() for _ in range(count())]
            overrides = {}
            for element in range(count()):
                for _ in range(count()):
                    effect = pointer(); template = integer()
                    overrides.setdefault(str(element), {})[str(template)] = binding(effect)
            if any(effects) or overrides:
                rows.append(dict(method=method, effects={str(i):binding(p) for i,p in enumerate(effects) if p}, overrides=overrides))
        expected = suffix_sizes.get(cls, 0)
        if expected is not None: assert len(raw)-offset == expected, (cls,len(raw)-offset)
        registry[cls] = dict(pathId=oid, rows=rows, decodedBytes=offset, trailingBytes=len(raw)-offset)
        if cls=='LocationTokenVFXHandlerData':
            token_effects=[pointer() for _ in range(count())]
            assert offset==len(raw)
            registry[cls]['tokenEffects']={str(1<<index):binding(p) for index,p in enumerate(token_effects) if p}
    catalog = json.loads((ROOT/'data/beta924/normalized/catalog.json').read_text('utf8'))
    specials = [t for t in catalog['templates'] if t['fields']['Type']==2 and t['attributes'].get('Availability')=='1']
    abilities = {a['templateId']:a for a in catalog['abilities'] if 'templateId' in a}
    def resolve(cls, method, element, template):
        row = next((r for r in registry.get(cls,{}).get('rows',[]) if r['method']==method), None)
        if not row or element <= 0: return None
        index = str(int(math.log2(element)))
        return row['overrides'].get(index,{}).get(str(template)) or row['effects'].get(index)
    cards = []
    for t in specials:
        tid = t['templateId']; effects = []
        for node in abilities.get(tid,{}).get('nodes',[]):
            fields = {c['tag']:c['attributes'].get('V') for c in node['sourceTree']['children']}
            visual = {k:int(v) for k,v in fields.items() if k in ('ElementType','AttackMethod','RemovalType','MovementType','Operation','LocationToken','Tokens','SpawnType') and v is not None}
            if not visual: continue
            element = visual.get('ElementType',1); method = visual.get('AttackMethod',0)
            attack = resolve('AttackApplyMethodData',method,element,tid)
            impact = resolve('CardPowerAttackVFXHandlerData',0,element,tid) if node['type']=='ChangePowerNode' else None
            row_effect=registry.get('LocationTokenVFXHandlerData',{}).get('tokenEffects',{}).get(str(visual.get('Tokens',visual.get('LocationToken',0)))) if node['type']=='ChangeLocationTokensNode' else None
            effects.append(dict(nodeId=node['nodeId'], node=node['type'], fields=visual,
                                elementName=ELEMENTS.get(element), attack=attack, impact=impact,rowEffect=row_effect))
        cards.append(dict(templateId=tid, name=t['attributes']['DebugName'],
                          title=catalog['localization']['ru_ru'].get(str(tid)+'_name'), effects=effects,
                          status='graph-and-registry' if any(e['attack'] or e['impact'] for e in effects) else 'graph-or-token-runtime'))
    # Export all nonempty registry prefabs, their descendants, and renderer dependencies.
    roots = {gos[b['pathId']] for table in registry.values() for row in table['rows']
             for b in list(row['effects'].values())+[v for per in row['overrides'].values() for v in per.values()] if b}
    # Include persistent row tokens, spawn/ambush effects and fallback prefabs,
    # which live outside the generic attack table.
    roots.update(go for oid,go in gos.items() if go and 'VisualEffect' in scripts[oid])
    go_transform = {go:tr for tr,go in transforms.items()}
    def under(go):
        tr = go_transform.get(go); visited = set()
        while tr and tr not in visited:
            if transforms.get(tr) in roots: return True
            visited.add(tr); tr = parents.get(tr)
        return go in roots
    selected = set()
    for oid,o in objects.items():
        if o.type.name not in ('GameObject','Transform','ParticleSystem','ParticleSystemRenderer','MonoBehaviour','Animator','MeshRenderer','MeshFilter','TrailRenderer','LineRenderer'): continue
        d = o.read(check_read=False); go = oid if o.type.name=='GameObject' else getattr(getattr(d,'m_GameObject',None),'path_id',0)
        if under(go): selected.add(oid)
    selected.update(table['pathId'] for table in registry.values())
    selected.update(oid for oid,cls in scripts.items() if cls=='BezierProjectileSettings')
    def refs(tree):
        if isinstance(tree,dict):
            if tree.get('m_FileID')==0 and tree.get('m_PathID') in objects: yield tree['m_PathID']
            for value in tree.values(): yield from refs(value)
        elif isinstance(tree,list):
            for value in tree: yield from refs(value)
    queue = list(selected)
    for oid in queue:
        o = objects[oid]
        try: tree = o.read_typetree(check_read=False)
        except Exception: continue
        for dep in refs(tree):
            if dep not in selected and objects[dep].type.name in ('Material','Texture2D','Shader','Mesh','AnimatorController','AnimationClip'):
                selected.add(dep);queue.append(dep)
    exported = []
    for oid in sorted(selected):
        o = objects[oid]; stem = f'{oid}-{scripts.get(oid,o.type.name)}'
        raw = OUT/'objects'/f'{stem}.bin';raw.parent.mkdir(exist_ok=True);raw.write_bytes(o.get_raw_data())
        item = dict(pathId=oid,type=o.type.name,component=scripts.get(oid),raw=str(raw.relative_to(ROOT)),sha256=sha(raw))
        try:
            tree = o.read_typetree() # Strict: never claim a truncated custom type tree is complete.
            config = raw.with_suffix('.json.gz');config.write_bytes(gzip.compress(json.dumps(tree,default=lambda x:{'binaryHex':x.hex()} if isinstance(x,bytes) else str(x)).encode(),mtime=0))
            item['configuration'] = str(config.relative_to(ROOT))
        except Exception as error: item['configurationUnavailable'] = str(error)
        if o.type.name=='Texture2D':
            d=o.read();dest=OUT/'textures'/f'{oid}-{d.m_Name}.png';dest.parent.mkdir(exist_ok=True)
            try: d.image.save(dest);item['image']=str(dest.relative_to(ROOT));item['name']=d.m_Name
            except Exception as error: item['imageUnavailable']=str(error)
        exported.append(item)
    # Materials and textures commonly live in another sharedassets file. Follow
    # actual PPtrs, preserving file identity instead of treating path IDs globally.
    dependencies = {}
    for oid in sorted(selected):
        o = objects[oid]
        if o.type.name not in ('ParticleSystemRenderer','MeshRenderer','TrailRenderer','LineRenderer'): continue
        for pointer in o.read().m_Materials:
            if not pointer.path_id: continue
            material_obj = pointer.deref(); material = material_obj.read()
            dependencies[(material_obj.assets_file.name,material_obj.path_id)] = material_obj
            for _,value in material.m_SavedProperties.m_TexEnvs:
                if value.m_Texture.path_id:
                    tex = value.m_Texture.deref()
                    dependencies[(tex.assets_file.name,tex.path_id)] = tex
    for (file,oid),o in sorted(dependencies.items()):
        stem=f'{file}-{oid}-{o.type.name}'; dest=OUT/'dependencies'/f'{stem}.bin';dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(o.get_raw_data());item=dict(sourceAsset=file,pathId=oid,type=o.type.name,raw=str(dest.relative_to(ROOT)),sha256=sha(dest))
        try:
            tree=o.read_typetree();config=dest.with_suffix('.json.gz')
            config.write_bytes(gzip.compress(json.dumps(tree,default=str).encode(),mtime=0));item['configuration']=str(config.relative_to(ROOT))
        except Exception as error:item['configurationUnavailable']=str(error)
        if o.type.name=='Texture2D':
            d=o.read();image=OUT/'textures'/f'{file}-{oid}-{d.m_Name}.png';image.parent.mkdir(exist_ok=True)
            try:d.image.save(image);item.update(image=str(image.relative_to(ROOT)),name=d.m_Name,size=[d.m_Width,d.m_Height])
            except Exception as error:item['imageUnavailable']=str(error)
        exported.append(item)
    report = dict(stage=142, source=str(SOURCE.relative_to(ROOT)), sourceSha256=before,
                  schemaSource='Gwent_Data/Managed/Assembly-CSharp.dll: ACardAttackVFXHandlerData, CardElementVisualEffectsContainer, CardAttackVisualEffectOverride',
                  registry=registry, specials=cards, specialCount=len(cards), exported=exported,
                  prefabs=[dict(gameObject=go,name=names[go],components=[dict(pathId=oid,component=scripts[oid]) for oid,g in gos.items() if g==go]) for go in sorted(roots)],
                  sourceUnchanged=sha(SOURCE)==before, nativeGameTested=False)
    assert report['sourceUnchanged'] and len(cards)==85
    save(OUT/'manifest.json',report)
    save(ROOT/'docs/evidence/special-vfx142.json',{k:v for k,v in report.items() if k!='exported'})
    print(json.dumps(dict(specials=len(cards),registryTables=len(registry),exported=len(exported),textures=sum('image' in e for e in exported),crow=next(c for c in cards if c['templateId']==200224)),ensure_ascii=False))

if __name__=='__main__':main()

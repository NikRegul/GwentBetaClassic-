"""Pin complete original elemental prefab hierarchies for the 0.7 GFx port.

Keeps Unity particle curves, transforms, materials, meshes, trails and custom
component bytes. This is source extraction, not a claim that Unity shaders run
in Scaleform. Original files are never written.
"""
from pathlib import Path
import collections
import gzip
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from PIL import Image,ImageDraw

BASE=ROOT/'BetaGwent/build/element-vfx163'
SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
WANTED={
 'LightMagic':['PowerDirectLightMagic','PowerLightMagicProjectile','PowerRowLightMagic','PowerSideLightMagic','PowerBoardLightMagic','BoardEffect_ClearWeather'],
 'DarkMagic':['PowerDirectDarkMagic','PowerDarkMagicProjectile','PowerRowDarkMagic','PowerSideDarkMagic','PowerBoardDarkMagic'],
 'Physical':['PowerDirectPhysical','PowerPhysicalProjectile','PowerRowPhysical'],
 'Fire':['PowerDirectFire','PowerFireProjectile','PowerSideFire'],
 'Ice':['PowerRowIce','PowerSideIce','PowerBoardIce'],
 'Earth':['PowerDirectEarth'], 'Air':['PowerRowAir','AirTokenAttack'],
 'Presentation':['CardLandingEffect','GoldLanding','CardFrostLandingEffect','CardRainLandingEffect','CardMistLandingEffect','SpawnBlink','AmbushEffect','NatureTransform','PromoteSimpleVFX','DemoteParticleSimpleVFX'],
 # Inventory the approved lightning for compatibility, without changing it.
 'Lightning':['PowerDirectLightning','PowerLightningProjectile'],
}


def sha(path):
 with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def identity(obj):return (obj.assets_file.name,obj.path_id)


def save_tree(obj):
 asset,pid=identity(obj);stem=f'{asset}-{pid}-{obj.type.name}'
 raw=BASE/'objects'/(stem+'.bin');raw.parent.mkdir(parents=True,exist_ok=True)
 raw.write_bytes(obj.get_raw_data())
 record=dict(asset=asset,pathId=pid,type=obj.type.name,raw=raw.relative_to(ROOT).as_posix(),sha256=sha(raw))
 try:
  tree=obj.read_typetree()
  target=raw.with_suffix('.json.gz')
  target.write_bytes(gzip.compress(json.dumps(tree,default=lambda x:dict(binaryHex=x.hex()) if isinstance(x,bytes) else str(x)).encode(),mtime=0))
  record.update(configuration=target.relative_to(ROOT).as_posix(),configurationSha256=sha(target))
 except Exception as error:record['configurationUnavailable']=str(error)
 return record


def main():
 before=sha(SOURCE);env=UnityPy.load(str(SOURCE));objects={o.path_id:o for o in env.objects}
 names={oid:o.read().m_Name for oid,o in objects.items() if o.type.name=='GameObject'}
 by_name=collections.defaultdict(list)
 for oid,name in names.items():by_name[name].append(oid)
 transforms={};by_go={}
 for oid,o in objects.items():
  if o.type.name=='Transform':
   d=o.read();transforms[oid]=d;by_go[d.m_GameObject.path_id]=oid
 roots={name:by_name[name][0] for group in WANTED.values() for name in group}
 assert all(len(by_name[name])==1 for name in roots),'Ambiguous original prefab name'
 card=json.loads((ROOT/'docs/evidence/card-vfx163.json').read_text('utf8'))
 # Include real per-template overrides. They remain distinct from the default
 # family even when the generic registry points to the same element.
 for name in card['prefabs']:
  if 'Power' in name and name in by_name and len(by_name[name])==1:roots[name]=by_name[name][0]
 records={};textures={};materials={}
 def store(obj):
  key=identity(obj)
  if key not in records:records[key]=save_tree(obj)
  return records[key]
 def material(pointer):
  obj=pointer.deref();key=identity(obj)
  if key in materials:return materials[key]
  data=obj.read();record=store(obj);shader=data.m_Shader.read()
  entries=[]
  for prop,slot in data.m_SavedProperties.m_TexEnvs:
   if not slot.m_Texture.path_id:continue
   tex=slot.m_Texture.deref();tkey=identity(tex)
   if tkey not in textures:
    td=tex.read();tr=store(tex);target=BASE/'textures'/f'{tkey[0]}-{tkey[1]}.png';target.parent.mkdir(exist_ok=True)
    td.image.save(target)
    tr.update(name=td.m_Name,size=[td.m_Width,td.m_Height],image=target.relative_to(ROOT).as_posix(),imageSha256=sha(target))
    textures[tkey]=tr
   entries.append(dict(property=prop,textureAsset=tkey[0],texturePathId=tkey[1],
                       scale=[slot.m_Scale.x,slot.m_Scale.y],offset=[slot.m_Offset.x,slot.m_Offset.y]))
  # Unity 2017's compiled shader stores its name in m_ParsedForm; m_Name
  # is empty. Preserve the real blend model for the GFx material conversion.
  shader_name=shader.m_Name or data.m_Shader.deref().read_typetree().get('m_ParsedForm',{}).get('m_Name','')
  record.update(name=data.m_Name,shader=shader_name,textures=entries)
  materials[key]=record
  return record
 prefabs=[]
 for name,rid in sorted(roots.items()):
  queue=[by_go[rid]];go_ids=[]
  for transform_id in queue:
   transform=transforms[transform_id];go_ids.append(transform.m_GameObject.path_id)
   queue.extend(child.path_id for child in transform.m_Children)
  components=[];particle_count=0;other_renderers=[]
  for go_id in go_ids:
   go=objects[go_id].read();store(objects[go_id])
   for component in go.m_Component:
    pointer=component.component if hasattr(component,'component') else component[1]
    obj=pointer.deref();r=store(obj);r=dict(r,gameObject=go_id,gameObjectName=names[go_id])
    if obj.type.name=='MonoBehaviour':
     mono=obj.read(check_read=False);r['component']=mono.m_Script.read().m_ClassName
    if obj.type.name=='ParticleSystem':particle_count+=1
    if obj.type.name.endswith('Renderer'):
     renderer=obj.read();r['materials']=[identity(p.deref()) for p in renderer.m_Materials if p.path_id]
     for p in renderer.m_Materials:
      if p.path_id:material(p)
     if obj.type.name!='ParticleSystemRenderer':other_renderers.append(dict(pathId=obj.path_id,type=obj.type.name,gameObjectName=names[go_id]))
    if obj.type.name=='MeshFilter':
     mesh=obj.read().m_Mesh
     if mesh.path_id:store(mesh.deref())
    components.append(r)
  prefabs.append(dict(name=name,gameObject=rid,element=next((element for element,names_ in WANTED.items() if name in names_),None),
                      particleSystems=particle_count,otherRenderers=other_renderers,components=components))
 assert sha(SOURCE)==before,'Original client changed'
 result=dict(stage=163,source=SOURCE.relative_to(ROOT).as_posix(),sourceSha256=before,
             requestedGenericPrefabs=sum(len(v) for v in WANTED.values()),prefabs=prefabs,
             materials=list(materials.values()),textures=list(textures.values()),objects=list(records.values()),
             sourceUnchanged=True,lightningRenderingUnmodified=True,uniquePrefabRenderingComplete=False)
 BASE.mkdir(parents=True,exist_ok=True)
 (BASE/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
 evidence={k:v for k,v in result.items() if k not in ('objects','materials','textures','prefabs')}
 evidence.update(manifest=(BASE/'manifest.json').relative_to(ROOT).as_posix(),manifestSha256=sha(BASE/'manifest.json'),
                 prefabs=[{k:p[k] for k in ('name','gameObject','element','particleSystems','otherRenderers')} for p in prefabs],
                 materialCount=len(materials),textureCount=len(textures))
 (ROOT/'docs/evidence/element-vfx163.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf8')
 # Contact sheet of source materials only; label it explicitly so it is never
 # mistaken for a preview of the still-to-be-ported animated effect.
 entries=list(textures.values());cols=8;cell=128;row=158
 sheet=Image.new('RGB',(cols*cell,44+((len(entries)+cols-1)//cols)*row),'#202b36');draw=ImageDraw.Draw(sheet)
 draw.text((12,12),'BETA SOURCE TEXTURES / NOT AN ANIMATION PREVIEW',fill='white')
 for i,t in enumerate(entries):
  im=Image.open(ROOT/t['image']).convert('RGBA');im.thumbnail((116,116))
  x=(i%cols)*cell+(cell-im.width)//2;y=44+(i//cols)*row
  sheet.paste(im,(x,y),im);draw.text(((i%cols)*cell+4,y+118),t['name'][:18],fill='#f0d8a0')
 sheet.save(BASE/'source-textures.png')
 print(json.dumps(dict(prefabs=len(prefabs),particles=sum(p['particleSystems'] for p in prefabs),
                       materials=len(materials),textures=len(textures),sourceUnchanged=True,
                       uniquePrefabRenderingComplete=False)))


if __name__=='__main__':main()

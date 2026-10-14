"""Read source materials and hierarchy for the 0.7.3 presentation work."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
BASE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data'
WANTED=['CardLandingEffect','GoldLanding','CardFrostLandingEffect','CardRainLandingEffect','CardMistLandingEffect','SpawnBlink','AmbushEffect','NatureTransform','PromoteSimpleVFX','DemoteParticleSimpleVFX','ResilienceToken','SpyingToken','RevealToken','CardTimerVFX','ArmorIncrease','ArmorDecrease']
def main():
 env=UnityPy.load(str(BASE/'sharedassets8.assets'),str(BASE/'resources.assets'))
 by_name={}
 for o in env.objects:
  if o.type.name=='GameObject':
   go=o.read()
   if go.m_Name in WANTED:by_name.setdefault(go.m_Name,[]).append(o)
 def shader(mat):
  try:
   s=mat.m_Shader.read();return s.m_ParsedForm.m_Name if hasattr(s,'m_ParsedForm') else s.m_Name
  except Exception:return None
 def walk(obj,path,nodes):
  go=obj.read();node={'path':path+'/'+go.m_Name,'id':obj.path_id,'components':[]};nodes.append(node)
  children=[]
  for c in go.m_Component:
   pp=c[1] if isinstance(c,tuple) else c.component
   o=pp.deref();item={'type':o.type.name,'id':o.path_id};node['components'].append(item)
   if o.type.name=='Transform':
    t=o.read();item['position']={k:getattr(t.m_LocalPosition,k) for k in ['x','y','z']};item['rotation']={k:getattr(t.m_LocalRotation,k) for k in ['x','y','z','w']};item['scale']={k:getattr(t.m_LocalScale,k) for k in ['x','y','z']}
    children=[ch.read().m_GameObject.deref() for ch in t.m_Children]
   elif o.type.name=='ParticleSystem':
    tree=o.read_typetree();item['duration']=tree.get('lengthInSec');item['data']=tree
   elif o.type.name in ['ParticleSystemRenderer','MeshRenderer','TrailRenderer','SpriteRenderer']:
    d=o.read();item['materials']=[]
    for m in d.m_Materials:
     if not m.path_id:continue
     mat=m.read();textures=[]
     for key,v in mat.m_SavedProperties.m_TexEnvs:
      try:textures.append({'property':key,'id':v.m_Texture.path_id,'name':v.m_Texture.read().m_Name})
      except Exception:pass
     item['materials'].append({'id':m.path_id,'name':mat.m_Name,'shader':shader(mat),'textures':textures})
   elif o.type.name=='MonoBehaviour':
    try:item['class']=o.read().m_Script.read().m_ClassName
    except Exception:pass
    item['rawHex']=o.get_raw_data().hex()
  for child in children:walk(child,node['path'],nodes)
 entries={}
 for name in WANTED:
  nodes=[]
  if by_name.get(name):walk(by_name[name][0],'',nodes)
  entries[name]={'found':bool(nodes),'nodes':nodes}
 report={'stage':178,'source':str(BASE/'sharedassets8.assets'),'sourceSha256':hashlib.sha256((BASE/'sharedassets8.assets').read_bytes()).hexdigest(),'prefabs':entries}
 output=ROOT/'docs/evidence/presentation-source178.json';output.write_text(json.dumps(report,indent=2,default=lambda v:list(v) if isinstance(v,bytes) else str(v))+'\n','utf8')
 for name,entry in entries.items():
  materials={(m['name'],m['shader']) for n in entry['nodes'] for c in n['components'] for m in c.get('materials',[])}
  print(name,'nodes',len(entry['nodes']),'particles',sum(c['type']=='ParticleSystem' for n in entry['nodes'] for c in n['components']),'materials',sorted(materials))
if __name__=='__main__':main()

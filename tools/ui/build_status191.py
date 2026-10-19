"""Bake beta status show/hide curves; reuse existing HUD textures in GFx."""
from pathlib import Path
import hashlib,json,math,sys,zlib
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from build_beta_motion100 import streamed,evaluate
from build_elements164 import write_as

NAMES=['ResilienceToken','SpyingToken','RevealToken']
PARTS={'ResilienceToken':{'bar':'Root/MeshElement','shield':'Root/MeshElement/MeshElementShield',
 'left':'Root/MeshElement/fittingL','right':'Root/MeshElement/fittingR'},
 'SpyingToken':{'eye':'Root/CardIcon','iris':'Root/CardIcon/Eye'},'RevealToken':{'icon':'Root/CardIcon'}}

def channels(clip,steps=60):
 curves=streamed(clip);data=clip['m_MuscleClip']['m_Clip']['data'];dense=data['m_DenseClip'];const=data['m_ConstantClip']['data']
 count=data['m_StreamedClip']['curveCount'];result={};offset=0
 for b in clip['m_ClipBindingConstant']['genericBindings']:
  size={1:3,2:4,3:3,4:3}.get(b['attribute'],1) if b['typeID']==4 else 1
  values=[]
  for axis in range(size):
   idx=offset+axis; samples=[]
   for step in range(steps+1):
    t=clip['m_MuscleClip']['m_StopTime']*step/steps
    if idx in curves:v=evaluate(curves[idx],t)
    elif idx<count+dense['m_CurveCount']:
     frame=min(dense['m_FrameCount']-1,max(0,round((t-dense['m_BeginTime'])*dense['m_SampleRate'])))
     v=dense['m_SampleArray'][frame*dense['m_CurveCount']+idx-count]
    else:v=const[idx-count-dense['m_CurveCount']]
    assert math.isfinite(v);samples.append(round(v,6))
   values.append(samples)
  result[(b['path'],b['typeID'],b['attribute'])]=values;offset+=size
 return result

def main():
 source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets';before=hashlib.sha256(source.read_bytes()).hexdigest()
 env=UnityPy.load(str(source));objs={o.path_id:o for o in env.objects};tables={};proof=[];emission={}
 armor_clip=next(o for o in objs.values() if o.type.name=='AnimationClip' and o.read().m_Name=='Armor_animationClip')
 armor=armor_clip.read_typetree();rates=channels(armor,222)
 def emission_paths(obj,path=''):
  go=obj.read();components=[(c[1] if isinstance(c,tuple) else c.component).deref() for c in go.m_Component]
  rate=rates.get((zlib.crc32(path.encode()),198,2883525743))
  for o in components:
   if o.type.name=='ParticleSystem' and rate:emission[str(o.path_id)]=dict(path=path,seconds=armor['m_MuscleClip']['m_StopTime'],rate=rate[0])
   if o.type.name=='Transform':
    for child in o.read().m_Children:
     ch=child.read().m_GameObject.deref();emission_paths(ch,(path+'/' if path else '')+ch.read().m_Name)
 for obj in objs.values():
  if obj.type.name=='GameObject' and obj.read().m_Name in ['ArmorIncrease','ArmorDecrease']:emission_paths(obj)
 for obj in objs.values():
  if obj.type.name!='GameObject' or obj.read().m_Name not in NAMES:continue
  name=obj.read().m_Name;anim=next((c[1] if isinstance(c,tuple) else c.component).read() for c in obj.read().m_Component if (c[1] if isinstance(c,tuple) else c.component).deref().type.name=='Animator')
  controller=anim.m_Controller.read_typetree();clips=[objs[p['m_OverrideClip']['m_PathID']] for p in controller['m_Clips']]
  parsed={}
  for o in clips:
   c=o.read_typetree();phase='show' if 'Show' in c['m_Name'] else 'hide' if 'Hide' in c['m_Name'] else 'idle'
   parsed[phase]=(c,channels(c));proof.append(dict(prefab=name,clip=c['m_Name'],pathId=o.path_id,sha256=hashlib.sha256(o.get_raw_data()).hexdigest(),durationMs=c['m_MuscleClip']['m_StopTime']*1000))
  for phase in ['show','hide']:
   clip,values=parsed[phase];end=parsed['show'][1];parts={}
   for key,path in PARTS[name].items():
    pid=zlib.crc32(path.encode());scale=values.get((pid,4,3));reference=end.get((pid,4,3));pos=values.get((pid,4,1));refpos=end.get((pid,4,1))
    # Material float bindings (customType 22) pack RGBA in the upper channel
    # bits: 1090582214/1359017670/1627453126/1895888582 for this source property.
    alpha=values.get((pid,23,1895888582));opacity=alpha[0] if alpha else [1]*61
    active=values.get((pid,1,zlib.crc32(b'm_IsActive')))
    if active:opacity=[a*b for a,b in zip(opacity,active[0])]
    if name=='ResilienceToken' and key!='bar':
     parent_active=values.get((zlib.crc32(b'Root/MeshElement'),1,zlib.crc32(b'm_IsActive')))
     if parent_active:opacity=[a*b for a,b in zip(opacity,parent_active[0])]
    # Unity meshes face the table in different local planes. The existing HUD
    # layout is retained; only normalized source scale/displacement is applied.
    axes=[0,2] if name=='ResilienceToken' else [0,1]
    s=[[round(v/max(.00001,reference[a][-1]),6) for v in scale[a]] if scale and reference else [1]*61 for a in axes]
    delta=[[round(v-refpos[a][-1],6) for v in pos[a]] if pos and refpos else [0]*61 for a in [0,1 if name=='ResilienceToken' else 2]]
    parts[key]=dict(sx=s[0],sy=s[1],dx=delta[0],dy=delta[1],alpha=opacity)
   tables[name+'_'+phase]=dict(ms=round(clip['m_MuscleClip']['m_StopTime']*1000,3),parts=parts)
 # GFx's AS3 optimizer is fragile with deeply nested literals. Build only the
 # requested clip, one channel at a time, rather than an 85-slot static stack.
 factories=[];cases=[]
 for index,(key,table) in enumerate(tables.items()):
  body=['var parts:Object={};']
  for part,channels_data in table['parts'].items():
   body.append('parts[%s]={};'%json.dumps(part))
   for channel,samples in channels_data.items():
    body.append('parts[%s][%s]=%s;'%(json.dumps(part),json.dumps(channel),json.dumps(samples,separators=(',',':'))))
  body.append('return {ms:%s,parts:parts};'%table['ms'])
  factories.append('private static function clip%d():Object {%s}'%(index,''.join(body)))
  cases.append('case %s: cache[key]=clip%d();break;'%(json.dumps(key),index))
 text='package { public class BetaGwentStatusData191 { private static var cache:Object={}; public static function clip(name:String,phase:String):Object {var key:String=name+"_"+phase;if(!cache[key]){switch(key){'+''.join(cases)+'}}return cache[key];} '+''.join(factories)+' } }'
 write_as('BetaGwentStatusData191.as',text)
 report=dict(stage=191,source=str(source.relative_to(ROOT)),sourceSha256=before,clips=proof,tables=tables,animatedEmission=emission,
  armorClip=dict(pathId=armor_clip.path_id,sha256=hashlib.sha256(armor_clip.get_raw_data()).hexdigest(),seconds=armor['m_MuscleClip']['m_StopTime']),
  texturesAdded=0,nativeGameTested=False,adaptation='Normalized original mesh curves on existing 2D HUD positions; 3D rotation and material dissolve are not emulated')
 assert hashlib.sha256(source.read_bytes()).hexdigest()==before
 (ROOT/'docs/evidence/status-source191.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(dict(clips=len(proof),tables=len(tables),texturesAdded=0)))

if __name__=='__main__':main()

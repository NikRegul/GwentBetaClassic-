"""Compile original Beta elemental particle recipes and compact quad atlases.

All timings, curves, colors, transforms, UV sheets and materials originate in
the pinned Unity extraction. Runtime projection/particle budgeting is the GFx
adaptation; no spell uses a recolored generic burst as its new renderer.
"""
from pathlib import Path
import gzip,hashlib,json,math,sys
from PIL import Image,ImageChops
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'vendor/audio-python'))
import UnityPy
from bake_element_mesh164 import bake

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'BetaGwent/ui/assets/elements164'
FAMILIES=['LightMagic','DarkMagic','Physical','Fire','Ice','Earth','Air','Presentation']
FOLDERS=['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']
SAMPLES=17
SOURCE_STEP_CURVES=False

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tree(c):return json.loads(gzip.decompress((ROOT/c['configuration']).read_bytes()))
def rnd(x):return round(float(x),5)
def vec(v):return [v.get(k,0) for k in ('x','y','z')]
def qrotate(q,v):
 x,y,z,w=q;vx,vy,vz=v;tx=2*(y*vz-z*vy);ty=2*(z*vx-x*vz);tz=2*(x*vy-y*vx)
 return [vx+w*tx+y*tz-z*ty,vy+w*ty+z*tx-x*tz,vz+w*tz+x*ty-y*tx]
def qmul(a,b):
 x,y,z,w=a;X,Y,Z,W=b
 return [w*X+x*W+y*Z-z*Y,w*Y-x*Z+y*W+z*X,w*Z+x*Y-y*X+z*W,w*W-x*X-y*Y-z*Z]
def hermite(keys,t):
 if not keys:return 1
 if t<=keys[0]['time']:return keys[0]['value']
 for a,b in zip(keys,keys[1:]):
  if t>b['time']:continue
  if SOURCE_STEP_CURVES and (not math.isfinite(a['outSlope']) or not math.isfinite(b['inSlope'])):return a['value'] if t<b['time'] else b['value']
  span=b['time']-a['time'];u=(t-a['time'])/span
  return (2*u**3-3*u*u+1)*a['value']+(u**3-2*u*u+u)*span*a['outSlope']+(-2*u**3+3*u*u)*b['value']+(u**3-u*u)*span*b['inSlope']
 return keys[-1]['value']
def value(c,t=.5,r=.5):
 mode=c.get('minMaxState',0);hi=c.get('scalar',0);lo=c.get('minScalar',hi)
 if mode==0:return hi
 if mode==3:return lo+(hi-lo)*r
 high=hermite(c.get('maxCurve',{}).get('m_Curve',[]),t)*hi
 low=hermite(c.get('minCurve',{}).get('m_Curve',[]),t)*lo if mode==2 else high
 return low+(high-low)*r
def curve(c,default=1):
 if c is None:return [default,default]
 if c['minMaxState']==0:return [rnd(c['scalar'])]*2
 if c['minMaxState']==3:return [rnd(c.get('minScalar',c['scalar'])),rnd(c['scalar'])]
 return [[rnd(value(c,i/(SAMPLES-1),r)) for i in range(SAMPLES)] for r in (0,1)]
def gradient(g):
 def one(d):
  colors=[[rnd(d.get('ctime'+str(i),0)/65535),*[rnd(d['key'+str(i)][k]) for k in ('r','g','b')]] for i in range(d.get('m_NumColorKeys',0))]
  alphas=[[rnd(d.get('atime'+str(i),0)/65535),rnd(d['key'+str(i)]['a'])] for i in range(d.get('m_NumAlphaKeys',0))]
  return dict(c=colors or [[0,1,1,1],[1,1,1,1]],a=alphas or [[0,1],[1,1]])
 mode=g.get('minMaxState',0)
 if mode in (0,2):
  def constant(c):return dict(c=[[0,c['r'],c['g'],c['b']],[1,c['r'],c['g'],c['b']]],a=[[0,c['a']],[1,c['a']]])
  return [constant(g['minColor'] if mode==2 else g['maxColor']),constant(g['maxColor'])]
 return [one(g['minGradient'] if mode==3 else g['maxGradient']),one(g['maxGradient'])]
def write_as(name,text):
 raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
 for folder in FOLDERS:
  target=ROOT/'BetaGwent/ui'/folder/name
  if target.parent.exists():target.write_bytes(raw)

def main():
 global SOURCE_STEP_CURVES
 source=ROOT/'BetaGwent/build/element-vfx163/manifest.json';m=json.loads(source.read_text('utf8'))
 assert sha(ROOT/m['source'])==m['sourceSha256']
 mats={(v['asset'],v['pathId']):v for v in m['materials']}
 textures={(v['asset'],v['pathId']):v for v in m['textures']}
 OUT.mkdir(parents=True,exist_ok=True)
 tiles=[{} for _ in FAMILIES];presets={};proof=[];unity=[None];unity_objects={}
 def source_mesh(renderer):
  if not unity[0]:
   unity[0]=UnityPy.load(str(ROOT/m['source']));unity_objects.update({o.path_id:o for o in unity[0].objects})
  d=unity_objects[renderer['pathId']].read()
  if renderer['type']=='MeshRenderer':
   go=d.m_GameObject.read()
   for component in go.m_Component:
    pointer=component[1] if isinstance(component,tuple) else component.component
    obj=pointer.deref()
    if obj.type.name=='MeshFilter':return obj.read().m_Mesh.read()
  elif getattr(d,'m_Mesh',None) and d.m_Mesh.path_id:return d.m_Mesh.read()
  return None
 def tile(material,family,cols,rows,renderer=None):
  main=next((t for t in material['textures'] if t['property']=='_MainTex'),None)
  if not main:return None
  mesh=source_mesh(renderer) if renderer else None
  key=(main['textureAsset'],main['texturePathId'],cols,rows,'Additive' in material['shader'],material['pathId'],mesh.m_Name if mesh else None)
  if key in tiles[family]:return tiles[family][key]['slot']
  src=textures[key[:2]];im=Image.open(ROOT/src['image']).convert('RGBA')
  if material['shader']=='VFX/Special/ClearWeather/LightShaft':
   # Unity's shader turns this noise into luminous shafts. Its raw RGB on an
   # opaque quad is black; transfer source luminance into alpha before baking.
   mask=im.convert('L');im=Image.new('RGBA',im.size,(255,255,255,0));im.putalpha(mask)
  if material['shader']=='VFX/Board/BoardGradient':
   # The original board texture is an intensity mask, not opaque artwork.
   mask=im.getchannel('R');gradient=next((t for t in material['textures'] if t['property']=='_GradientMask'),None)
   if gradient:
    g=Image.open(ROOT/textures[(gradient['textureAsset'],gradient['texturePathId'])]['image']).convert('L').resize(im.size)
    mask=ImageChops.multiply(mask,g)
   im.putalpha(mask)
  # Original additive shaders make black transparent. Unpremultiply RGB so
  # native NORMAL blending reproduces light without a rectangular black card.
  if key[4]:
   pixels=[]
   for r,g,b,a in im.getdata():
    peak=max(r,g,b);pixels.append((round(r*255/peak),round(g*255/peak),round(b*255/peak),round(a*peak/255)) if peak else (0,0,0,0))
   im.putdata(pixels)
  if mesh:im=bake(mesh,im,main)
  start=sum(t['slot'][4] for t in tiles[family].values());cell=64 if cols*rows>1 else 128
  frames=[]
  for i in range(cols*rows):
   x=i%cols;y=rows-1-i//cols
   frames.append(im.crop((round(x*im.width/cols),round(y*im.height/rows),round((x+1)*im.width/cols),round((y+1)*im.height/rows))).resize((cell,cell),Image.Resampling.LANCZOS))
  slot=[family,start,cell,cell,cols*rows]
  tiles[family][key]=dict(slot=slot,frames=frames,source=src['image'],sha256=src['imageSha256'],grid=[cols,rows],shader=material['shader'])
  return slot
 for prefab in m['prefabs']:
  family_name=prefab.get('element')
  if family_name not in FAMILIES:continue # Approved lightning and already ported overrides stay unchanged.
  family=FAMILIES.index(family_name);projectile='Projectile' in prefab['name']
  # Unity stores step tangents as infinity. Preserve already accepted elemental
  # recipes; evaluate these correctly for the newly ported presentation family.
  SOURCE_STEP_CURVES=family_name=='Presentation'
  components=prefab['components'];trans={c['pathId']:tree(c) for c in components if c['type']=='Transform'}
  by_go={c['gameObject']:c['pathId'] for c in components if c['type']=='Transform'}
  go_active={c['gameObject']:True for c in components}
  for c in m['objects']:
   if c['type']=='GameObject' and c['pathId'] in go_active:go_active[c['pathId']]=bool(tree(c).get('m_IsActive',True))
  world={}
  def transform(ident):
   if ident in world:return world[ident]
   t=trans[ident];p=vec(t['m_LocalPosition']);s=vec(t['m_LocalScale']);q=[t['m_LocalRotation'][k] for k in ('x','y','z','w')];active=go_active.get(t['m_GameObject']['m_PathID'],True)
   parent=t['m_Father']['m_PathID']
   if parent in trans:
    pp,ps,pq,pa=transform(parent);offset=qrotate(pq,[p[i]*ps[i] for i in range(3)]);p=[pp[i]+offset[i] for i in range(3)];s=[ps[i]*s[i] for i in range(3)];q=qmul(pq,q);active=active and pa
   elif not projectile:p=[0,0,0] # Runtime placement supplies the prefab origin.
   world[ident]=(p,s,q,active);return world[ident]
  renderers={c['gameObject']:c for c in components if c['type'].endswith('Renderer')}
  emitters=[];static=[];end=0
  for c in components:
   if c['type'] not in ('ParticleSystem','MeshRenderer','TrailRenderer'):continue
   position,scale,rotation,active=transform(by_go[c['gameObject']])
   if not active:continue
   renderer=renderers.get(c['gameObject']);data=tree(c)
   if not renderer or not renderer.get('materials'):continue
   material=mats[tuple(renderer['materials'][0])];rd=tree(renderer);md=tree(material)['m_SavedProperties'];colors=dict(md['m_Colors']);floats=dict(md['m_Floats']);tint=colors.get('_TintColor',dict(r=1,g=1,b=1,a=1))
   mult=2 if 'VFX/' in material['shader'] else 1
   rgb=[rnd(tint[k]*mult) for k in ('r','g','b')];alpha=rnd(tint['a']*floats.get('_AlphaMultiplier',1))
   if prefab['name']=='BoardEffect_ClearWeather' and c['type']=='MeshRenderer':
    rgb=[rnd(colors['_node_2964'][k]) for k in ('r','g','b')];alpha=.7
   if c['type']!='ParticleSystem':
    slot=tile(material,family,1,1,renderer if c['type']=='MeshRenderer' else None)
    if slot:
     width=28 if c['type']=='MeshRenderer' and projectile else 55 if projectile else 220
     height=14 if projectile else 30
     static.append(dict(tile=slot,p=[0,0,0] if prefab['name']=='BoardEffect_ClearWeather' else list(map(rnd,position)),size=[1000,480] if prefab['name']=='BoardEffect_ClearWeather' else [width,height],rgb=rgb,alpha=alpha,trail=c['type']=='TrailRenderer',name=c['gameObjectName']))
    continue
   ini=data['InitialModule'];em=data['EmissionModule'];shape=data['ShapeModule'];uv=data['UVModule']
   if not ini.get('enabled',True) or not em.get('enabled',False):continue
   # These two billboard emitters still reference the 6x6 hail sheet with UV
   # animation disabled. A GFx quad must sample one ice chip, not the whole grid.
   hail_sheet=family_name=='Ice' and c['gameObjectName'] in ('HailLeft','HailRight')
   cols,rows=(uv['tilesX'],uv['tilesY']) if uv.get('enabled') or hail_sheet else (1,1)
   slot=tile(material,family,cols,rows,renderer if rd.get('m_RenderMode')==4 else None)
   if not slot:continue
   delay=curve(data['startDelay'],0);duration=float(data['lengthInSec']);births=[];accumulator=0
   for burst in em['m_Bursts']:
    for cycle in range(max(1,int(burst['cycleCount']))):
     births.extend([float(burst['time'])+cycle*float(burst['repeatInterval'])]*min(512,round(value(burst['countCurve']))))
   dt=1/120
   for step in range(min(720,math.ceil(duration/dt))):
    t=step*dt;accumulator+=max(0,value(em['rateOverTime'],min(1,t/max(.001,duration))))*dt
    while accumulator>=1 and len(births)<512:births.append(t);accumulator-=1
   if not births:continue
   births.sort()
   if data.get('looping') and births[0]>.001:births.insert(0,0)
   color=gradient(ini['startColor']);over=gradient(data['ColorModule']['gradient']) if data['ColorModule']['enabled'] else None
   size=data['SizeModule'];velocity=data['VelocityModule'];force=data['ForceModule'];clamp=data['ClampVelocityModule'];spin=data['RotationModule']
   sh=dict(enabled=shape['enabled'],type=shape['type'],radius=shape['radius']['value'],angle=shape['angle'],scale=vec(shape['m_Scale']),position=vec(shape['m_Position']),random=shape.get('randomDirectionAmount',0))
   # Disabled Unity shape modules may contain a NaN cone angle; it is unused.
   if not sh['enabled'] and not math.isfinite(sh['angle']):sh['angle']=0
   size_scale=[1,1,1] if data.get('scalingMode')==2 else vec(trans[by_go[c['gameObject']]]['m_LocalScale']) if data.get('scalingMode')==1 else scale
   emitter=dict(id=c['pathId'],name=c['gameObjectName'],tile=slot,births=list(map(rnd,births)),delay=delay,duration=rnd(duration),loop=data['looping'],sizeScale=list(map(rnd,size_scale)),
     lifetime=curve(ini['startLifetime']),speed=curve(ini['startSpeed']),size=curve(ini['startSize']),sizeY=curve(ini['startSizeY']) if ini['size3D'] else None,
     rotation=curve(ini['startRotation']),color=color,over=over,sizeOver=curve(size['curve']) if size['enabled'] else [1,1],
     spin=curve(spin['curve']) if spin['enabled'] else [0,0],gravity=curve(ini['gravityModifier'],0),
     velocity=[curve(velocity[a],0) for a in ('x','y','z')] if velocity['enabled'] else None,
     force=[curve(force[a],0) for a in ('x','y','z')] if force['enabled'] else None,
     clamp=curve(clamp['magnitude']) if clamp['enabled'] else None,drag=curve(clamp.get('drag'),0) if clamp['enabled'] else [0,0],
     uv=curve(uv['frameOverTime']) if uv['enabled'] else [0,0],uvStart=curve(uv['startFrame'],0) if uv['enabled'] else [0,0],cycles=uv.get('cycles',1),
     sheetAnimation=bool(uv['enabled'] and uv['frameOverTime']['minMaxState'] in (1,2)),
     p=list(map(rnd,position)),q=list(map(rnd,rotation)),scale=list(map(rnd,scale)),shape=sh,
     rgb=rgb,alpha=alpha,alphaExponent=floats.get('_AlphaExponent',1),
     stretched=rd.get('m_RenderMode')==1,length=rnd(rd.get('m_LengthScale',1)),
     world=not bool(data.get('moveWithTransform',True)),maxParticles=ini['maxNumParticles'])
   emitters.append(emitter)
   end=max(end,max(births)+max(delay if isinstance(delay[0],(int,float)) else delay[1])+max(value(ini['startLifetime'],i/16,r) for i in range(17) for r in (0,1)))
   proof.append(dict(prefab=prefab['name'],particle=c['pathId'],material=material['pathId'],shader=material['shader'],rawSha256=c['sha256'],configurationSha256=c['configurationSha256']))
  emitters.sort(key=lambda e:e['p'][2],reverse=True)
  method=3 if prefab['name']=='BoardEffect_ClearWeather' else 1 if projectile else 4 if 'Board' in prefab['name'] else 3 if 'Side' in prefab['name'] else 2 if 'Row' in prefab['name'] else 0
  presets[prefab['name']]=dict(family=family,method=method,projectile=projectile,emitters=emitters,static=static,duration=rnd(min(2.4,max(.4,end))),
     extent=[1000,480] if prefab['name']=='BoardEffect_ClearWeather' else [220,32 if method==2 else 130 if method==3 else 280] if method>=2 else [22,32])
 # Pack variable cell sizes using a 1024px shelf per element. Every source
 # sheet retains all cells; half-texel inset in the quad renderer stops leaks.
 rects=[];assets=[]
 for family,entries in enumerate(tiles):
  x=y=shelf=0;positions=[]
  for entry in entries.values():
   for frame in entry['frames']:
    w,h=frame.size
    if x+w>1024:x=0;y+=shelf;shelf=0
    positions.append((frame,x,y));rects.append([family,x,y,w,h]);x+=w;shelf=max(shelf,h)
   # Replace the temporary per-family frame index with the global rectangle offset.
   entry['slot'][1]=len(rects)-len(entry['frames'])
  height=max(4,math.ceil((y+shelf)/4)*4);atlas=Image.new('RGBA',(1024,height))
  for frame,ax,ay in positions:atlas.paste(frame,(ax,ay))
  path=OUT/(FAMILIES[family]+'.png');atlas.save(path,optimize=True)
  assets.append(dict(element=FAMILIES[family],path=path.relative_to(ROOT).as_posix(),sha256=sha(path),size=list(atlas.size),ddsBytes=atlas.width*atlas.height))
 # Preserve seven logical family atlases, but embed one physical page. Keg
 # menus already use 31 textures, so seven new embeds would exceed the native
 # writer's existing 32-texture guard. Two 1024px columns need only 5.5 MiB.
 heights=[0,0];placements={}
 for family in sorted(range(len(assets)),key=lambda f:assets[f]['size'][1],reverse=True):
  column=min(range(2),key=lambda i:heights[i]);placements[family]=(column*1024,heights[column]);heights[column]+=assets[family]['size'][1]
 combined=Image.new('RGBA',(2048,max(heights)))
 for family,asset in enumerate(assets):combined.paste(Image.open(ROOT/asset['path']),placements[family])
 for rect in rects:
  ox,oy=placements[rect[0]];rect[0]=0;rect[1]+=ox;rect[2]+=oy
 page=OUT/'Elements.png';combined.save(page,optimize=True)
 embedded=[dict(path=page.relative_to(ROOT).as_posix(),sha256=sha(page),size=list(combined.size),ddsBytes=combined.width*combined.height)]
 # Slot arrays are shared references in recipes, so their rect offsets above
 # are now the actual atlas bindings used by both preview and AS.
 json_path=OUT/'recipes.json';json_path.write_text(json.dumps(dict(presets=presets,rects=rects),separators=(',',':'),allow_nan=False),'utf8')
 chunks=[];factories=[];factory_index=0;preset_index=0
 for family in range(len(FAMILIES)):
  entries=[]
  for name,p in presets.items():
   if p['family']!=family:continue
   emitter_calls=[]
   for emitter in p['emitters']:
    factories.append('        private static function emitter%d():Object { return %s; }'%(factory_index,json.dumps(emitter,separators=(',',':'))));emitter_calls.append('emitter%d()'%factory_index);factory_index+=1
   data={k:v for k,v in p.items() if k!='emitters'};data['emitters']='EMITTER_LIST'
   literal=json.dumps(data,separators=(',',':')).replace('"EMITTER_LIST"','['+','.join(emitter_calls)+']')
   factories.append('        private static function preset%d():Object { return %s; }'%(preset_index,literal))
   entries.append(json.dumps(name)+':preset%d()'%preset_index);preset_index+=1
  chunks.append('        private static function family%d():Object { return {%s}; }'%(family,','.join(entries)))
 data='''package {
    // GENERATED from original Unity particle/material/transform data.
    public class BetaGwentElementData164 {
        private static var groups:Array=[family0(),family1(),family2(),family3(),family4(),family5(),family6()];
        public static const RECTS:Array=RECTS;
        public static function preset(name:String):Object { for each(var group:Object in groups)if(group[name])return group[name];return null; }
        public static function names():Array { var list:Array=[];for each(var group:Object in groups)for(var name:String in group)list.push(name);return list; }
CHUNKS
    }
}
'''.replace('RECTS;',json.dumps(rects,separators=(',',':'))+';').replace('CHUNKS','\n'.join(chunks+factories)).replace('family5(),family6()]','family5(),family6(),family7()]')
 write_as('BetaGwentElementData164.as',data)
 additive={str(v['particle']):1 for v in proof if 'Additive' in v['shader']}
 blend='package { public class BetaGwentElementBlend173 { private static const ADDITIVE:Object='+json.dumps(additive,separators=(',',':'))+'; public static function additive(id:int):Boolean {return ADDITIVE.hasOwnProperty(String(id));} } }'
 write_as('BetaGwentElementBlend173.as',blend)

 report=dict(stage=164,sourceManifest=str(source.relative_to(ROOT)),sourceManifestSha256=sha(source),presets=list(presets),particles=len(proof),
             sourceParticles=proof,logicalAtlases=assets,atlases=embedded,inlineDDSBytes=sum(a['ddsBytes'] for a in embedded),recipeSha256=sha(json_path),nativeGameTested=False,
             adaptation='2D projection; finite deterministic particle budget; procedural Unity shader displacement is not executed')
 (ROOT/'docs/evidence/elements164.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(dict(presets=len(presets),emitters=len(proof),atlasMiB=report['inlineDDSBytes']/1048576,rects=len(rects))))

if __name__=='__main__':main()

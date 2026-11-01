"""Isolated Beta editor particle preview; no game or canonical UI changes."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, math, re, subprocess, sys
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from PIL import Image,ImageDraw,ImageChops,ImageFont
SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs/deckbuilder_base'
MODEL=ROOT/'BetaGwent/ui/src/BetaGwentElement164.as'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def model_js(circle=False,axis_sizes=False):
 source=MODEL.read_text('utf-8-sig');functions=[]
 for name in ['random','sample','pick','rotate','colorKey','gradientValue','plan','spawn','packet']:
  start=source.index('function '+name+'(');opening=source.index('{',start);end=opening+1;depth=1
  while depth:
   depth+=(source[end]=='{')-(source[end]=='}');end+=1
  text=source[start:end]
  text=re.sub(r':(?:String|Object|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))','',text).replace(':*','')
  text=re.sub(r'for each\((.*?) in (.*?)\)',r'for(\1 of Object.values(\2||{}))',text)
  text=re.sub(r'(\w+) is Number',r"(typeof \1==='number')",text);functions.append(text)
 result='const int=v=>v|0,uint=v=>v>>>0;\n'+'\n'.join(functions)
 if circle:
  old='if(sh.type==5||sh.type==15||sh.type==16)'
  assert result.count(old)==1
  result=result.replace(old,'if(sh.type==10){direction=[Math.cos(angle),Math.sin(angle),0];point=[direction[0]*radius,direction[1]*radius,0];}\n                else '+old)
 if axis_sizes:
  old='pick(e.sizeY,p.phase,r[3])*pick(e.sizeOver,t,r[4])*scale'
  assert result.count(old)==1
  result=result.replace(old,'pick(e.sizeY,p.phase,r[3])*pick(e.sizeOverY||e.sizeOver,t,r[4])*scale')
  old=':out.w;'
  assert result.count(old)==1
  result=result.replace(old,':e.sizeOverY?Math.max(.02,Math.abs(pick(e.size,p.phase,r[3])*pick(e.sizeOverY,t,r[4])*scale)):out.w;')
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path);p.add_argument('--include-circle',action='store_true')
 p.add_argument('--roots',nargs='+',default=['UIDBCardAdd','UIDBCardRemove'])
 p.add_argument('--no-render',action='store_true',help='Export source recipes and finite packet proof only; no card-sized preview for row/stat effects')
 p.add_argument('--axis-sizes',action='store_true',help='Offline adapter for separate X/Y size-over-lifetime; production battle code unchanged')
 a=p.parse_args()
 if set(a.roots)!=set(['UIDBCardAdd','UIDBCardRemove']) and not a.no_render:
  p.error('Row/stat prefabs require --no-render until their own projection and shader preview is implemented')
 out=(a.out or ROOT/'BetaGwent/build'/datetime.now().strftime('editor-vfx094-preview-%Y%m%d-%H%M%S')).resolve()
 if out.exists() or not out.is_relative_to((ROOT/'BetaGwent/build').resolve()):p.error('Use a fresh directory below BetaGwent/build')
 before=sha(SOURCE)
 spec=importlib.util.spec_from_file_location('recipe_helpers094',ROOT/'tools/ui/build_elements164.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.SOURCE_STEP_CURVES=True
 env=UnityPy.load(str(SOURCE));roots={o.read().m_Name:o for o in env.objects if o.type.name=='GameObject' and o.read().m_Name in a.roots}
 if set(roots)!=set(a.roots):raise ValueError('All requested editor source roots required')
 out.mkdir(parents=True);(out/'textures').mkdir();textures={};presets={};omitted=[];proof=[]
 for name,root in sorted(roots.items()):
  emitters=[];end=0;root_pose={}
  def walk(obj,pos,scale,rot,is_root=False,active=True):
   nonlocal end
   go=obj.read();cs=[(c[1] if isinstance(c,tuple) else c.component).deref() for c in go.m_Component];t=next(c.read() for c in cs if c.type.name in ['Transform','RectTransform'])
   lp=[getattr(t.m_LocalPosition,k) for k in 'xyz'];ls=[getattr(t.m_LocalScale,k) for k in 'xyz'];lq=[getattr(t.m_LocalRotation,k) for k in 'xyzw']
   if is_root:root_pose.update(position=lp,scale=ls,rotation=lq)
   offset=h.qrotate(rot,[x*y for x,y in zip(lp,scale)]);pos=[0,0,0] if is_root else [x+y for x,y in zip(pos,offset)];scale=[x*y for x,y in zip(scale,ls)];rot=h.qmul(rot,lq);active=active and bool(go.m_IsActive)
   renderer=next((c for c in cs if c.type.name=='ParticleSystemRenderer'),None)
   for c in cs:
    if c.type.name in ['MeshRenderer','Animator']:omitted.append(dict(prefab=name,node=go.m_Name,type=c.type.name,reason='Unity mesh/shader animation is not evaluated'))
    if c.type.name!='ParticleSystem':continue
    d=c.read_typetree();ini=d['InitialModule'];em=d['EmissionModule'];shape=d['ShapeModule'];uv=d['UVModule']
    if not active or not em['enabled'] or (shape['enabled'] and shape['type'] not in ([0,1,2,3,5,10,15,16] if a.include_circle else [0,1,2,3,5,15,16])):
     omitted.append(dict(prefab=name,node=go.m_Name,type='ParticleSystem',reason='Inactive or unsupported source shape '+str(shape['type'])));continue
    rd=renderer.read_typetree();mat=next(x for x in renderer.read().m_Materials if x.path_id).deref();md=mat.read();shader_tree=md.m_Shader.deref().read_typetree().get('m_ParsedForm',{});shader=shader_tree.get('m_Name','');blend=shader_tree['m_SubShaders'][0]['m_Passes'][0]['m_State']['rtBlend0'];factors={k:blend[k]['val'] for k in ['srcBlend','destBlend','blendOp']}
    if shader not in ['VFX/Common/AdditiveAlphaRGB','Particles/Additive','VFX/Common/AdditiveAlpha'] or rd['m_RenderMode'] not in [0,1] or factors['destBlend']!=1 or factors['srcBlend'] not in [1,5] or factors['blendOp']!=0:
     omitted.append(dict(prefab=name,node=go.m_Name,type='ParticleSystem',reason='Unsupported material/renderer '+shader));continue
    main=next(v for k,v in md.m_SavedProperties.m_TexEnvs if k=='_MainTex');tex=main.m_Texture.deref();key=str(tex.path_id)
    if key not in textures:
     dest=out/'textures'/(key+'.png');tex.read().image.save(dest);textures[key]=dict(path='textures/'+dest.name,sha256=sha(dest),rawSha256=hashlib.sha256(tex.get_raw_data()).hexdigest())
    seconds=float(d['lengthInSec']);births=[];acc=0
    for burst in em['m_Bursts']:
     for cycle in range(max(1,int(burst['cycleCount']))):births.extend([burst['time']+cycle*burst['repeatInterval']]*min(512,round(h.value(burst['countCurve']))))
    for step in range(min(1200,math.ceil(seconds*120))):
     acc+=max(0,h.value(em['rateOverTime'],step/120/max(.001,seconds)))/120
     while acc>=1 and len(births)<1024:births.append(step/120);acc-=1
    births.sort();colors=dict(md.m_SavedProperties.m_Colors);floats=dict(md.m_SavedProperties.m_Floats);tint=colors.get('_TintColor',dict(r=1,g=1,b=1,a=1));tint={k:(tint[k] if isinstance(tint,dict) else getattr(tint,k)) for k in 'rgba'};velocity=d['VelocityModule'];force=d['ForceModule'];clamp=d['ClampVelocityModule'];spin=d['RotationModule'];size=d['SizeModule']
    e=dict(id=str(c.path_id),name=go.m_Name,texture=textures[key]['path'],blend='add',tile=[0,0,1,1,uv['tilesX']*uv['tilesY'] if uv['enabled'] else 1],columns=uv['tilesX'] if uv['enabled'] else 1,rows=uv['tilesY'] if uv['enabled'] else 1,
     births=births,delay=h.curve(d['startDelay'],0),duration=seconds,sizeScale=[1,1,1] if d.get('scalingMode')==2 else ls if d.get('scalingMode')==1 else scale,
     lifetime=h.curve(ini['startLifetime']),speed=h.curve(ini['startSpeed']),size=h.curve(ini['startSize']),sizeY=h.curve(ini['startSizeY']) if ini['size3D'] else None,rotation=h.curve(ini['startRotation']),color=h.gradient(ini['startColor']),over=h.gradient(d['ColorModule']['gradient']) if d['ColorModule']['enabled'] else None,
     sizeOver=h.curve(size['curve']) if size['enabled'] else [1,1],spin=h.curve(spin['curve']) if spin['enabled'] else [0,0],gravity=h.curve(ini['gravityModifier'],0),velocity=[h.curve(velocity[k],0) for k in 'xyz'] if velocity['enabled'] else None,force=[h.curve(force[k],0) for k in 'xyz'] if force['enabled'] else None,clamp=h.curve(clamp['magnitude']) if clamp['enabled'] else None,drag=h.curve(clamp.get('drag'),0) if clamp['enabled'] else [0,0],
     uv=h.curve(uv['frameOverTime']) if uv['enabled'] else [0,0],uvStart=h.curve(uv['startFrame'],0) if uv['enabled'] else [0,0],cycles=uv.get('cycles',1),sheetAnimation=bool(uv['enabled'] and uv['frameOverTime']['minMaxState'] in [1,2]),p=pos,q=rot,scale=scale,
     shape=dict(enabled=shape['enabled'],type=shape['type'],radius=shape['radius']['value'],angle=shape['angle'] if shape['enabled'] else 0,scale=h.vec(shape['m_Scale']),position=h.vec(shape['m_Position']),random=shape.get('randomDirectionAmount',0)),rgb=[tint[k] for k in 'rgb'],alpha=tint['a']*floats.get('_AlphaMultiplier',1),stretched=rd['m_RenderMode']==1,length=rd.get('m_LengthScale',1),world=not d.get('moveWithTransform',True))
    if a.axis_sizes and size['enabled'] and size.get('separateAxes'):e['sizeOverY']=h.curve(size['y'])
    emitters.append(e);end=max(end,max(births,default=0)+max(h.value(ini['startLifetime'],i/16,r) for i in range(17) for r in [0,1])+max(h.value(d['startDelay'],0,r) for r in [0,1]));proof.append(dict(prefab=name,node=go.m_Name,particle=str(c.path_id),rawSha256=hashlib.sha256(c.get_raw_data()).hexdigest(),shader=shader,material=str(mat.path_id),blend='add',sourceBlend=factors,births=len(births)))
   for child in t.m_Children:walk(child.read().m_GameObject.deref(),pos,scale,rot,active=active)
  walk(root,[0,0,0],[1,1,1],[0,0,0,1],True)
  presets[name]=dict(family=8,method=0,projectile=False,extent=[22,32],emitters=emitters,static=[],duration=max(.04,end),sourceRootPose=root_pose)
 data=out/'recipes.json';data.write_text(json.dumps(dict(presets=presets,textures=textures),indent=2,allow_nan=False)+'\n','utf8');(out/'particle-model.js').write_text(model_js(a.include_circle,a.axis_sizes),'utf8')
 driver="""const fs=require('fs'),vm=require('vm'),[model,data,out]=process.argv.slice(1),c=vm.createContext({Math,Number,Object,Array});vm.runInContext(fs.readFileSync(model,'utf8'),c);const d=JSON.parse(fs.readFileSync(data,'utf8')),result={};let packets=0;for(const [name,p] of Object.entries(d.presets)){const a=c.plan(p,94,600),b=c.plan(p,94,600);if(JSON.stringify(a)!==JSON.stringify(b))throw Error('Non-determinism');result[name]=[];for(let i=0;i<48;i++){const t=i/47*p.duration;const frame={seconds:t,particles:[]};for(const part of a.particles){const pose=c.packet(part,t,{});if(pose.visible){for(const k of ['x','y','w','h','angle','r','g','b','a'])if(!Number.isFinite(pose[k]))throw Error('Nonfinite '+k);frame.particles.push({pose,texture:part.e.texture,columns:part.e.columns,rows:part.e.rows,blend:part.e.blend});packets++;}}result[name].push(frame)}}fs.writeFileSync(out,JSON.stringify(result));console.log(JSON.stringify({deterministic:true,finiteVisiblePackets:true,packets}));"""
 checked=json.loads(subprocess.run(['node','-e',driver,str(out/'particle-model.js'),str(data),str(out/'packets.json')],capture_output=True,text=True,check=True).stdout)
 frames=json.loads((out/'packets.json').read_text('utf8'))
 if not a.no_render:render_frames(out,frames)
 limitations=['Particle subset only; meshes, custom shader math and Unity Animator tracks omitted','Orthographic XY projection; source root translation removed, serialized root scale retained','Source tint and textures retained; Unity shader arithmetic, One/One alpha preprocessing and dynamic activation not reproduced','Unsupported circle shape type 10 omitted; source additive blend retained per whitelisted source material']
 if a.include_circle:limitations[-1]='Source circle shape 10 supported in the offline spawn adapter; production battle particle model unchanged'
 if a.axis_sizes:limitations.append('Offline separate-axis size curves retained; production battle model unchanged. Non-uniform transform scaling remains a separate projection limitation.')
 report=dict(complete=True,source=str(SOURCE.relative_to(ROOT)),sourceSha256=before,sourceUnchanged=sha(SOURCE)==before,model=str(MODEL.relative_to(ROOT)),modelSha256=sha(MODEL),particles=proof,omitted=omitted,limitations=limitations,verification=checked,nativeGameTested=False,canonicalUiChanged=False,rendered=not a.no_render,roots=a.roots)
 if not report['sourceUnchanged']:raise RuntimeError('Source changed')
 (out/'report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf8')
 if not a.no_render:write_html(out,frames,limitations,omitted)
 print(json.dumps(dict(output=str(out),**checked)))
def render_frames(out,frames):
 images={};W,H=520,360;font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14);sheet=Image.new('RGB',(W*4,H*2));(out/'frames').mkdir()
 for row,(name,timeline) in enumerate(frames.items()):
  for index,frame in enumerate(timeline):
   panel=Image.new('RGBA',(W,H),(28,37,42,255));draw=ImageDraw.Draw(panel);draw.rectangle((210,105,310,245),fill=(68,76,64),outline=(184,166,112));draw.text((12,12),name+' / %.2f s'%frame['seconds'],font=font,fill='white')
   for particle in frame['particles']:
    p=particle['pose'];path=particle['texture'];images.setdefault(path,Image.open(out/path).convert('RGBA'));image=images[path];cols,rows=particle['columns'],particle['rows'];col=p['frame']%cols;rr=rows-1-p['frame']//cols;image=image.crop((col*image.width//cols,rr*image.height//rows,(col+1)*image.width//cols,(rr+1)*image.height//rows))
    image=Image.merge('RGBA',[channel.point(lambda v,m=p[k]:v*m) for channel,k in zip(image.split(),['r','g','b','a'])]);w=max(1,min(2000,round(p['w']*2)));hh=max(1,min(2000,round(p['h']*2)));image=image.resize((w,hh),Image.Resampling.BILINEAR).rotate(-p['angle'],Image.Resampling.BICUBIC,expand=True);x=round(W/2+p['x']*2-image.width/2);y=round(H/2+p['y']*2-image.height/2)
    if particle['blend']=='add':
     light=Image.new('RGBA',(W,H));light.alpha_composite(image,(x,y));alpha=light.getchannel('A');rgb=Image.merge('RGB',[ImageChops.multiply(ch,alpha) for ch in light.convert('RGB').split()]);panel=ImageChops.add(panel.convert('RGB'),rgb).convert('RGBA')
    else:panel.alpha_composite(image,(x,y))
   panel.convert('RGB').save(out/'frames'/(name+'-%02d.png'%index))
   if index in [4,12,24,36]:sheet.paste(panel.convert('RGB'),([4,12,24,36].index(index)*W,row*H))
 sheet.save(out/'contact-sheet.png')
def write_html(out,frames,limitations,omitted):
 import html
 content='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Beta editor source particles</title><style>body{background:#172129;color:#e7ded0;font:16px system-ui;margin:30px auto;max-width:1100px}img{max-width:100%;border:1px solid #53636b}button,select,input{font:inherit;margin:10px;padding:8px}li{margin:8px}</style><h1>Editor VFX · source particle subset</h1><p>Research preview, not the complete effect or native Scaleform acceptance.</p><select id="name"></select><button id="play">Replay</button><label><input type="checkbox" id="loop" checked>Loop</label><img id="frame" width="1040"><input id="time" type="range" min="0" max="47" value="0"><ul>'''
 content+=''.join('<li>'+html.escape(s)+'</li>' for s in limitations)+'</ul><details><summary>Omitted source components</summary><pre>'+html.escape(json.dumps(omitted,ensure_ascii=False,indent=2))+'</pre></details><p><a href="report.json">Provenance and verification</a> · <a href="contact-sheet.png">Contact sheet</a></p><script>'
 content+='const frames='+json.dumps({k:len(v) for k,v in frames.items()})+''';const selector=document.getElementById('name'),image=document.getElementById('frame'),slider=document.getElementById('time');for(const n of Object.keys(frames)){const o=document.createElement('option');o.textContent=n;selector.append(o)}let index=0,playing=true;function draw(){image.src='frames/'+selector.value+'-'+String(index).padStart(2,'0')+'.png';slider.value=index}selector.onchange=()=>{index=0;draw()};document.getElementById('play').onclick=()=>{index=0;playing=true;draw()};slider.oninput=()=>{playing=false;index=Number(slider.value);draw()};setInterval(()=>{if(playing){draw();if(index<47)index++;else if(document.getElementById('loop').checked)index=0;else playing=false}},60);draw();</script></html>'''
 (out/'index.html').write_text(content,'utf8')
if __name__=='__main__':main()

"""Bake supported original editor meshes/particles, exact extracted pixel instructions.

Projection, 30 Hz sampling, finite source-particle model and mip-0 sampling are
the explicit GFx adaptation. Empty source meshes and unbound tracks stay omitted.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, subprocess, sys, zlib
import numpy as np
from PIL import Image,ImageDraw
from editor_shader094 import MaterialProgram
from preview_editor_vfx094 import model_js
from build_elements164 import qrotate
ROOT=Path(__file__).resolve().parents[2]
W,H,FPS=128,160,30
X,Y=np.meshgrid(-40+(np.arange(W)+.5)*80/W,50-(np.arange(H)+.5)*100/H)

def grid(texels):
    """Sampling grid over the unchanged 80x100 source extent (texels per Unity unit)."""
    global W,H,X,Y
    W,H=int(round(80*texels)),int(round(100*texels))
    X,Y=np.meshgrid(-40+(np.arange(W)+.5)*80/W,50-(np.arange(H)+.5)*100/H)

def transforms(nodes):
    result={}
    for n in nodes:
        p=np.array([n['position'][k] for k in 'xyz']);s=np.array([n['scale'][k] for k in 'xyz']);q=[n['rotation'][k] for k in 'xyzw']
        local=np.eye(4);local[:3,:3]=np.array([qrotate(q,[float(i==j) for i in range(3)]) for j in range(3)]).T@np.diag(s)
        local[:3,3]=p if n['path'] else 0
        parent=n['path'].rsplit('/',1)[0] if '/' in n['path'] else ''
        result[n['path']]=result[parent]@local if n['path'] else local
    return result

def raster_mesh(mesh,matrix,cull):
    vertices=np.array(mesh['vertices']);vertices=(np.c_[vertices,np.ones(len(vertices))]@matrix.T)[:,:3]
    uv=np.array(mesh['uv']);colors=np.array(mesh['colors'] or [[1,1,1,1]]*len(vertices))
    output=[];seen=np.zeros((H,W),bool)
    for group in mesh['triangles']:
        for ids in group:
            a,b,c=vertices[ids,:2];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-8 or cull==2 and den>0 or cull==1 and den<0:continue
            wa=((b[1]-c[1])*(X-c[0])+(c[0]-b[0])*(Y-c[1]))/den
            wb=((c[1]-a[1])*(X-c[0])+(a[0]-c[0])*(Y-c[1]))/den;wc=1-wa-wb
            inside=(wa>=-1e-6)&(wb>=-1e-6)&(wc>=-1e-6)&~seen;seen|=inside
            iy,ix=np.where(inside)
            if not len(ix):continue
            weights=np.stack([wa[inside],wb[inside],wc[inside]],axis=1)
            output.append((iy,ix,weights@uv[ids],weights@colors[ids]))
    return output

def overrides(material,tracks,time,seconds):
    props={**copy.deepcopy(material['floats']),**copy.deepcopy(material['colors'])}
    for tex in material['textures']:
        props[tex['property']+'_ST']=[tex['scale']['x'],tex['scale']['y'],tex['offset']['x'],tex['offset']['y']]
    for track in tracks:
        attribute=track['binding']['attribute'];names=[n for n in props if zlib.crc32(n.encode())&0xfffffff==attribute&0xfffffff]
        assert len(names)==1,('Unresolved animated material property',attribute,names)
        key=names[0];p=min(120,max(0,time/max(.0001,seconds)*120));i=min(119,int(p));f=p-i
        value=track['values'][0][i]*(1-f)+track['values'][0][i+1]*f;group=attribute>>28
        if group==8:props[key]=value
        else:
            channel=group-4 if group>=4 else group
            if isinstance(props[key],dict):props[key]['rgba'[channel]]=value
            else:props[key][channel]=value
    return props

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audit',type=Path,required=True);p.add_argument('--shaders',type=Path,required=True);p.add_argument('--particles',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--texels',type=float,default=1.6,help='texels per Unity unit; 1.6 is the first 128x160 prototype');a=p.parse_args()
    grid(a.texels);out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists();out.mkdir()
    audit=json.loads((a.audit/'audit.json').read_text('utf8'));particle=json.loads((a.particles/'recipes.json').read_text('utf8'))
    particle_proof=json.loads((a.particles/'report.json').read_text('utf8'))
    assert audit['sourceSha256']==particle_proof['sourceSha256']
    materials={k:MaterialProgram(a.audit,a.shaders,audit,k) for k in audit['materials']}
    mat_by_particle={row['particle']:row['material'] for row in particle_proof['particles']}
    for preset in particle['presets'].values():
        for emitter in preset['emitters']:emitter['rgb']=[1,1,1];emitter['alpha']=1
    (out/'recipes.json').write_text(json.dumps(particle),'utf8');(out/'model.js').write_text(model_js(True),'utf8')
    driver="""const fs=require('fs'),vm=require('vm'),[dir]=process.argv.slice(1),c=vm.createContext({Math,Number,Object,Array});vm.runInContext(fs.readFileSync(dir+'/model.js','utf8'),c);const data=JSON.parse(fs.readFileSync(dir+'/recipes.json','utf8')),out={};for(const [name,p] of Object.entries(data.presets)){const plan=c.plan(p,94,600);out[name]=[];for(let i=0;i<30;i++){const time=i/30,parts=[];for(const part of plan.particles){const pose=c.packet(part,time,{});if(pose.visible)parts.push({pose,id:part.e.id,columns:part.e.columns,rows:part.e.rows});}out[name].push(parts);}}fs.writeFileSync(dir+'/particles.json',JSON.stringify(out));"""
    subprocess.run(['node','-e',driver,str(out)],check=True)
    packets=json.loads((out/'particles.json').read_text('utf8'));metadata={};omitted=[];sheet=Image.new('RGB',(W*8,H*2),(25,34,38));thumb=(128,160)
    for row,(name,preset) in enumerate(audit['presets'].items()):
        folder=out/name;folder.mkdir();matrices=transforms(preset['nodes']);mesh_cache=[]
        clip=preset['clips'][0]
        lifetime=next(c['configuration']['m_Duration'] for c in preset['nodes'][0]['components'] if c.get('script')=='VFXPoolableComponent')
        assert lifetime==1.0
        for node in preset['nodes']:
            for component in node['components']:
                if component['type']!='MeshRenderer':continue
                if node.get('mesh') is None:
                    omitted.append(dict(prefab=name,path=node['path'],reason='Serialized MeshFilter has no mesh; source spawn only reparents/positions prefab'))
                    continue
                mid=component['materials'][0];program=materials[mid];sd=json.loads(__import__('gzip').decompress((a.shaders/program.material['shader']/'serialized.json.gz').read_bytes()))
                state=sd['m_ParsedForm']['m_SubShaders'][0]['m_Passes'][0]['m_State'];cull=state['culling']['val']
                raster=raster_mesh(audit['meshes'][node['mesh']],matrices[node['path']],cull)
                tracks=[t for t in clip['tracks'] if t['path']==node['path'] and t['binding']['typeID']==23]
                mesh_cache.append((program,raster,tracks))
        summaries=[]
        for index in range(FPS):
            time=index/FPS;add=np.zeros((H,W,3),np.float32);normal=np.zeros((H,W,4),np.float32)
            def blend(program,iy,ix,pixels):
                assert np.isfinite(pixels).all(),('Nonfinite source shader',program.shader['name'],time)
                factor=program.shader['blend'];src,dst=factor['srcBlend'],factor['destBlend']
                assert factor['blendOp']==0
                if dst==1:
                    assert src in [1,5];amount=1 if src==1 else np.clip(pixels[:,3:4],0,1)
                    add[iy,ix]+=np.maximum(0,pixels[:,:3])*amount
                else:
                    assert src==5 and dst==10
                    alpha=np.clip(pixels[:,3:4],0,1);old=normal[iy,ix]
                    normal[iy,ix,:3]=pixels[:,:3]*alpha+old[:,:3]*(1-alpha)
                    normal[iy,ix,3:4]=alpha+old[:,3:4]*(1-alpha)
            for program,raster,tracks in mesh_cache:
                props=overrides(program.material,tracks,time,clip['seconds'])
                for iy,ix,uv,color in raster:
                    inputs={'v1':np.c_[uv,np.zeros(len(uv)),np.ones(len(uv))], 'v2':color}
                    if program.shader['name']=='UI/UIGlow':inputs['v2']=np.c_[.5+X[iy,ix]*8/1920,.5-Y[iy,ix]*8/1080,np.zeros(len(uv)),np.ones(len(uv))]
                    blend(program,iy,ix,program.shade(inputs,time,props))
            for part in packets[name][index]:
                pose=part['pose'];r=pose['angle']*math.pi/180;dx=X-pose['x'];dy=Y+pose['y'];u=(np.cos(r)*dx-np.sin(r)*dy)/pose['w']+.5;v=(np.sin(r)*dx+np.cos(r)*dy)/pose['h']+.5
                inside=(u>=0)&(u<1)&(v>=0)&(v<1);iy,ix=np.where(inside)
                if not len(ix):continue
                frame=pose['frame'];uv=np.c_[(u[inside]+frame%part['columns'])/part['columns'],(v[inside]+frame//part['columns'])/part['rows'],np.zeros(len(ix)),np.ones(len(ix))]
                color=np.tile([pose[k] for k in ['r','g','b','a']],(len(ix),1));program=materials[mat_by_particle[part['id']]]
                inputs={'v1':color,'v2':uv} if program.shader['name']=='Particles/Additive' else {'v1':uv,'v2':color}
                blend(program,iy,ix,program.shade(inputs,time))
            alpha=normal[:,:,3:4];straight=np.divide(normal[:,:,:3],alpha,out=np.zeros_like(normal[:,:,:3]),where=alpha>0)
            image=Image.fromarray(np.round(np.clip(add,0,1)*255).astype(np.uint8),'RGB');image.save(folder/('add-%02d.png'%index))
            ordinary=Image.fromarray(np.round(np.clip(np.concatenate([straight,alpha],axis=2),0,1)*255).astype(np.uint8),'RGBA');ordinary.save(folder/('normal-%02d.png'%index))
            summaries.append(dict(index=index,seconds=time,addPixels=int(np.count_nonzero(np.max(np.array(image),axis=2))),normalPixels=int(np.count_nonzero(np.array(ordinary)[:,:,3]))))
            if index in [0,1,2,3,5,8,15,29]:
                bg=np.zeros((H,W,3),np.float32);bg[:]=[.10,.14,.15];card=(abs(X)<11)&(abs(Y)<16);bg[card]=[.25,.29,.25]
                bg=bg*(1-alpha)+normal[:,:,:3]+add;preview=Image.fromarray(np.round(np.clip(bg,0,1)*255).astype(np.uint8),'RGB')
                sheet.paste(preview,([0,1,2,3,5,8,15,29].index(index)*W,row*H))
        metadata[name]=dict(seconds=lifetime,clipSeconds=clip['seconds'],frames=summaries)
    sheet.resize((thumb[0]*16,thumb[1]*4)).save(out/'contact-sheet.png')
    report=dict(complete=True,sourceSha256=audit['sourceSha256'],fps=FPS,frameSize=[W,H],extent=[80,100],texelsPerUnit=a.texels,presets=metadata,omitted=omitted,
      materials=[p.shader['name'] for p in materials.values()],sourceShaderInstructionsEvaluated=True,nativeGameTested=False,
      limitations=['Orthographic XY projection, fixed 1920x1080 camera anchor; UI screen-space distortion is baked at that anchor',
                   'Existing finite AS particle model plus offline Circle shape 10, deterministic seed 94; no production battle effects changed',
                   'Float32 shader instructions with bilinear mip-0 samples; GPU derivatives, colour-space conversion and exact native visual parity not established',
                   'Mixed source blending retained as separate ordinary-alpha and additive layers; output quantized to 8-bit at 30 Hz'])
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(dict(output=str(out),frames=60,omitted=omitted)))

if __name__=='__main__':main()

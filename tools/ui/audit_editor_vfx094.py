"""Decode original editor mesh/material/animation sources into a fresh local audit."""
from pathlib import Path
import argparse, gzip, hashlib, json, math, sys, zlib
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from UnityPy.export.ShaderConverter import export_shader
from UnityPy.helpers.MeshHelper import MeshHandler
from build_status191 import channels

SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs/deckbuilder_base'
DEFAULTS=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/Resources/unity default resources'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rawsha=lambda o:hashlib.sha256(o.get_raw_data()).hexdigest()

def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--roots',nargs='+',default=['UIDBCardAdd','UIDBCardRemove']);a=p.parse_args()
    out=a.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
    before=sha(SOURCE);defaults_before=sha(DEFAULTS);env=UnityPy.load(str(SOURCE),str(DEFAULTS));out.mkdir();materials={};shaders={};textures={};meshes={};presets={}
    roots={o.read().m_Name:o for o in env.objects if o.type.name=='GameObject' and o.read().m_Name in a.roots}
    assert set(roots)==set(a.roots),'Missing requested prefab roots'
    def material(ref):
        obj=ref.deref();key=str(obj.path_id)
        if key in materials:return key
        tree=obj.read_typetree();shader=obj.read().m_Shader.deref();sid=str(shader.path_id)
        if sid not in shaders:
            st=shader.read_typetree();name=st['m_ParsedForm']['m_Name'];dest=out/'shaders'/(sid+'.shader');dest.parent.mkdir(exist_ok=True)
            dest.write_text(export_shader(shader.read()),'utf8')
            state=st['m_ParsedForm']['m_SubShaders'][0]['m_Passes'][0]['m_State']['rtBlend0']
            shaders[sid]=dict(name=name,rawSha256=rawsha(shader),exportSha256=sha(dest),platforms=st['platforms'],
                              blend={k:state[k]['val'] for k in ['srcBlend','destBlend','blendOp']},
                              properties=st['m_ParsedForm']['m_PropInfo'])
        props=tree['m_SavedProperties'];tex=[]
        for k,v in props['m_TexEnvs']:
            if not v['m_Texture']['m_PathID']:continue
            ptr=next(vv for kk,vv in obj.read().m_SavedProperties.m_TexEnvs if kk==k).m_Texture
            to=ptr.deref();tid=str(to.path_id)
            if tid not in textures:
                dest=out/'textures'/(tid+'.png');dest.parent.mkdir(exist_ok=True);image=to.read().image;image.save(dest)
                tt=to.read_typetree()
                textures[tid]=dict(name=to.read().m_Name,size=list(image.size),rawSha256=rawsha(to),pngSha256=sha(dest),
                                   settings=tt.get('m_TextureSettings'),colorSpace=tt.get('m_ColorSpace'))
            tex.append(dict(property=k,texture=tid,scale=v['m_Scale'],offset=v['m_Offset']))
        materials[key]=dict(name=tree['m_Name'],rawSha256=rawsha(obj),shader=sid,
                            floats=dict(props['m_Floats']),colors=dict(props['m_Colors']),textures=tex)
        return key
    for name,root in roots.items():
        nodes=[];clips=[]
        def walk(obj,path):
            go=obj.read();components=[(c[1] if isinstance(c,tuple) else c.component).deref() for c in go.m_Component]
            tr=next(c for c in components if c.type.name in ['Transform','RectTransform']);t=tr.read_typetree()
            node=dict(path=path,pathHash=zlib.crc32(path.encode()),name=go.m_Name,active=go.m_IsActive,
                      objectId=str(obj.path_id),position=t['m_LocalPosition'],scale=t['m_LocalScale'],rotation=t['m_LocalRotation'],components=[])
            for c in components:
                if c.type.name in ['MeshRenderer','ParticleSystemRenderer']:
                    d=c.read_typetree();node['components'].append(dict(type=c.type.name,id=str(c.path_id),
                      materials=[material(ref) for ref in c.read().m_Materials if ref.path_id],configuration=d))
                elif c.type.name=='MeshFilter':
                    if not c.read().m_Mesh.path_id:
                        node['mesh']=None
                        continue
                    mesh=c.read().m_Mesh.deref();mid=str(mesh.path_id)
                    if mid not in meshes:
                        h=MeshHandler(mesh.read());h.process()
                        meshes[mid]=dict(name=mesh.read().m_Name,rawSha256=rawsha(mesh),vertices=h.m_Vertices,uv=h.m_UV0,
                                         colors=h.m_Colors,triangles=h.get_triangles())
                    node['mesh']=mid
                elif c.type.name=='ParticleSystem':
                    d=c.read_typetree();file=out/'particles'/(str(c.path_id)+'.json.gz');file.parent.mkdir(exist_ok=True)
                    file.write_bytes(gzip.compress(json.dumps(d,allow_nan=True).encode()))
                    node['components'].append(dict(type=c.type.name,id=str(c.path_id),rawSha256=rawsha(c)))
                elif c.type.name=='Animator':
                    ctrl=c.read().m_Controller.deref();ct=ctrl.read_typetree();save(out/'controllers'/(str(ctrl.path_id)+'.json'),ct)
                    for clipref in ctrl.read().m_AnimationClips:
                        clip=clipref.deref();cd=clip.read_typetree();values=channels(cd,120);tracks=[]
                        for binding in cd['m_ClipBindingConstant']['genericBindings']:
                            key=(binding['path'],binding['typeID'],binding['attribute'])
                            tracks.append(dict(binding=binding,values=values[key]))
                        clips.append(dict(id=str(clip.path_id),name=cd['m_Name'],rawSha256=rawsha(clip),
                                          seconds=cd['m_MuscleClip']['m_StopTime'],tracks=tracks))
                        dest=out/'clips'/(str(clip.path_id)+'.json.gz');dest.parent.mkdir(exist_ok=True)
                        dest.write_bytes(gzip.compress(json.dumps(cd,allow_nan=True).encode()))
                elif c.type.name=='MonoBehaviour':
                    data=c.read_typetree()
                    node['components'].append(dict(type='MonoBehaviour',id=str(c.path_id),
                      script=c.read().m_Script.read().m_ClassName,configuration=data))
            nodes.append(node)
            for child in tr.read().m_Children:
                childgo=child.read().m_GameObject.deref();childname=childgo.read().m_Name
                walk(childgo,path+'/'+childname if path else childname)
        walk(root,'')
        paths={n['pathHash']:n for n in nodes}
        for clip in clips:
            for track in clip['tracks']:
                binding=track['binding']
                track['path']=paths[binding['path']]['path'] if binding['path'] in paths else None
                if track['path'] is None:
                    track['unboundReason']='No matching transform in this serialized prefab; do not invent a target'
                assert all(math.isfinite(v) for axis in track['values'] for v in axis)
        presets[name]=dict(rootId=str(root.path_id),nodes=nodes,clips=clips)
    assert sha(SOURCE)==before and sha(DEFAULTS)==defaults_before
    save(out/'audit.json',dict(source=str(SOURCE.relative_to(ROOT)),sourceSha256=before,sourceUnchanged=True,
                              presets=presets,materials=materials,shaders=shaders,textures=textures,meshes=meshes,
                              defaultResourcesSha256=defaults_before,
                              animationDecoder='Existing build_status191.channels: streamed/dense/constant',
                              nativeGameTested=False))
    print(json.dumps(dict(output=str(out),presets=len(presets),materials=len(materials),shaders=len(shaders),textures=len(textures))))

if __name__=='__main__':main()

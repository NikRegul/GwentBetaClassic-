"""Read the beta deck-stat widgets and their referenced validity effects.

No assets are installed or modified. This is an inventory, not a renderer.
"""
from pathlib import Path
import argparse,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
SOURCE=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs/deckbuilder_base'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    out=args.out.resolve();assert out.is_relative_to(ROOT/'BetaGwent/build') and not out.exists()
    before=sha(SOURCE);environment=UnityPy.load(str(SOURCE));widgets=[];effect_pools=[]
    def local(reader,ref):
        if not isinstance(ref,dict) or ref.get('m_FileID')!=0:return None
        return reader.assets_file.objects.get(ref.get('m_PathID'))
    def name(reader,ref):
        target=local(reader,ref)
        if target is None:return None
        data=target.read_typetree()
        return data.get('m_Name') or name(target,data.get('m_GameObject') or data.get('m_RootGameObject'))
    def hierarchy(obj,prefix=''):
        tree=obj.read_typetree();node=dict(name=tree['m_Name'],id=str(obj.path_id),active=tree.get('m_IsActive'),components=[],children=[])
        for entry in tree.get('m_Component',[]):
            ref=entry[1] if isinstance(entry,tuple) else entry.get('component',entry)
            component=local(obj,ref)
            if component is None:continue
            data=component.read_typetree();row=dict(type=component.type.name,id=str(component.path_id))
            if component.type.name in ['Transform','RectTransform']:
                row.update(position=data.get('m_LocalPosition'),scale=data.get('m_LocalScale'))
                for child in data.get('m_Children',[]):
                    transform=local(component,child)
                    if transform:
                        target=local(transform,transform.read_typetree().get('m_GameObject'))
                        if target:node['children'].append(hierarchy(target))
            elif component.type.name in ['ParticleSystemRenderer','MeshRenderer']:
                row['materials']=[dict(reference=r,name=name(component,r)) for r in data.get('m_Materials',[])]
            elif component.type.name=='MonoBehaviour':
                row['duration']=data.get('m_Duration')
            node['components'].append(row)
        return node
    for reader in environment.objects:
        if reader.type.name!='MonoBehaviour':continue
        tree=reader.read_typetree()
        if 'm_CounterVFXPool' in tree:
            pools={}
            for key in ['m_AddCardVFXPool','m_RemoveCardVFXPool','m_CounterVFXPool']:
                value=tree.get(key);target=local(reader,value)
                pools[key]=dict(reference=value,targetType=target.type.name if target else None,
                                target=target.read_typetree() if target else None)
                if target:pools[key]['prefabName']=name(target,pools[key]['target'].get('m_Prefab'))
            effect_pools.append(dict(id=str(reader.path_id),owner=name(reader,tree.get('m_GameObject')),pools=pools))
        if 'm_ValidDeckVFX' not in tree and 'm_BronzeLabel' not in tree:continue
        record=dict(id=str(reader.path_id),owner=name(reader,tree.get('m_GameObject')),
            validColor=tree.get('m_TextValidColor'),invalidColor=tree.get('m_TextInvalidColor'),
            hasCounters={k:k in tree for k in ['m_TotalLabel','m_BronzeLabel','m_SilverLabel','m_GoldLabel']},
            validVfxReference=tree.get('m_ValidDeckVFX'))
        target=local(reader,tree.get('m_ValidDeckVFX'))
        record['validVfx']=hierarchy(target) if target else None
        widgets.append(record)
    assert sha(SOURCE)==before
    report=dict(source=str(SOURCE),sourceSha256=before,widgets=widgets,effectPools=effect_pools,installed=False,rendered=False,nativeGameplayVerified=False)
    out.mkdir();(out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(widgets=len(widgets),colors=[w['invalidColor'] for w in widgets],effects=[w['validVfx']['name'] if w['validVfx'] else None for w in widgets],deckCardPoolOwners=len(effect_pools)),ensure_ascii=False))

if __name__=='__main__':main()

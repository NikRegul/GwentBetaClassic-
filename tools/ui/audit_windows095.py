"""Read-only provenance for the remaining Beta UI windows, images and animation bindings."""
from pathlib import Path
import argparse, hashlib, json, sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
GUI=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs'
CS=ROOT/'BetaGwent/build-inputs/reference/beta-original-csharp'
WANT={'UIBattleChoicePrefab','UIHistoryPrefab','UIOutcomeRootPrefab','UIPopupPanelPrefab','SettingsWindow'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def scan(path):
    env=UnityPy.load(str(path));objects={o.path_id:o for o in env.objects};cache={}
    def read(pid):
        if pid not in cache:
            try:cache[pid]=objects[pid].read_typetree()
            except Exception:cache[pid]={}
        return cache[pid]
    def ref(ptr):
        if not isinstance(ptr,dict):return ptr
        pid=ptr.get('m_PathID',0);fid=ptr.get('m_FileID',0)
        if not pid:return {'default':True}
        if fid or pid not in objects:return {'externalFile':fid,'pathId':pid}
        d=read(pid);return {'pathId':pid,'type':objects[pid].type.name,'name':d.get('m_Name'),
            **({'shader':ref(d.get('m_Shader'))} if 'm_Shader' in d else {})}
    gos={pid:read(pid) for pid,o in objects.items() if o.type.name=='GameObject'}
    transforms={pid:read(pid) for pid,o in objects.items() if o.type.name in ('RectTransform','Transform')}
    parents={}
    for t in transforms.values():
        parent=transforms.get(t.get('m_Father',{}).get('m_PathID',0),{})
        parents[t['m_GameObject']['m_PathID']]=parent.get('m_GameObject',{}).get('m_PathID',0)
    scripts={pid:read(pid).get('m_ClassName') for pid,o in objects.items() if o.type.name=='MonoScript'}
    roots={pid:d['m_Name'] for pid,d in gos.items() if d.get('m_Name') in WANT}
    report={}
    for root,name in roots.items():
        nodes=[]
        for pid,go in gos.items():
            cur=pid;seen=set()
            while cur and cur!=root and cur not in seen:seen.add(cur);cur=parents.get(cur,0)
            if cur!=root:continue
            comps=[]
            for item in go.get('m_Component',[]):
                ptr=item.get('component',item.get('second',{}));cid=ptr.get('m_PathID')
                if cid not in objects:continue
                obj=objects[cid];d=read(cid);typ=obj.type.name
                cls=scripts.get(d.get('m_Script',{}).get('m_PathID',0),'')
                if typ=='Animator':comps.append({'type':typ,'controller':ref(d.get('m_Controller'))})
                elif typ=='MonoBehaviour' and (cls in ('Image','RawImage','UIAnim_Position','UIAnim_CanvasGroup','AnimateSharedMaterial','UIAnim_ImageColor') or 'SoundHandler' in cls):
                    row={'class':cls}
                    for key in ['m_Material','m_Sprite','m_Texture']:
                        if key in d:row[key]=ref(d[key])
                    if 'm_Color' in d:row['color']=d['m_Color']
                    comps.append(row)
            if comps:nodes.append({'name':go.get('m_Name'),'components':comps})
        report[name]=nodes
    return {'bundle':str(path.relative_to(ROOT)),'sha256':sha(path),'windows':report,
        'materials':[{'name':read(pid).get('m_Name'),'shader':ref(read(pid).get('m_Shader'))} for pid,o in objects.items() if o.type.name=='Material'],
        'animationClips':[read(pid).get('m_Name') for pid,o in objects.items() if o.type.name=='AnimationClip']}
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    report={'bundles':[scan(GUI/n) for n in ['game_base','global_base']], 'classes':[]}
    names={'UIBattleChoicePanel','UIBattleChoicePanelSoundHandler','UIOutcomeRootPanel','UIOutcomeCarousel','UIOutcomeScores','OutcomeScoreRowContoller','UIOutcomeScoreSoundHandler','UIOutcomeRewardsSoundHandler','UIHistoryPanel','HistoryWindowSoundHandler','UIHistoryListView','HistoryPanelInputHandler','SettingsWindow','SettingsWindowVisualResourcesProvider','PopupPanel','PopupControl','PopupPanelSoundHandler'}
    for f in sorted(CS.rglob('*.cs')):
        if f.stem in names:report['classes'].append({'path':str(f.relative_to(ROOT)),'sha256':sha(f)})
    report['limitations']=['External material/controller references recorded without inventing shader/curve data.',
        'No particle effect or blend mode is replaced by this UI adaptation. Native Unity animation/particle parity remains a separate acceptance item.']
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n','utf8')
    print(json.dumps({'windows':[list(x['windows']) for x in report['bundles']],'classes':len(report['classes'])}))
if __name__=='__main__':main()

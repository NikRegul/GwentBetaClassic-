"""Bake Ragnarok's original meteor path and activation times for the GFx port."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
from build_status191 import channels
from build_elements164 import write_as

def main():
 source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
 env=UnityPy.load(str(source));clip=next(o for o in env.objects if o.type.name=='AnimationClip' and o.read().m_Name=='RagNarRoog_Metheor')
 tree=clip.read_typetree();values=channels(tree,120);seconds=tree['m_MuscleClip']['m_StopTime']
 pos=values[(1539825560,4,1)];active=values[(1993626846,1,2086281974)][0]
 impact=next(i for i,v in enumerate(active) if v>.5)/120*seconds*1000
 data=dict(ms=round(seconds*1000,3),impactMs=round(impact,3),y=pos[1],z=pos[2])
 # Channel arrays are separate statements to keep native optimizer stacks small.
 text='package {public class BetaGwentBattle080 {public static const MS:Number=%s;public static const IMPACT_MS:Number=%s;private static const Y:Array=%s;private static const Z:Array=%s;public static function y(p:Number):Number{return BetaGwentStatus191.sample(Y,p);}public static function z(p:Number):Number{return BetaGwentStatus191.sample(Z,p);}}}'%(data['ms'],data['impactMs'],json.dumps(data['y']),json.dumps(data['z']))
 write_as('BetaGwentBattle080.as',text)
 report=dict(source=str(source.relative_to(ROOT)),sourceSha256=hashlib.sha256(source.read_bytes()).hexdigest(),clipId=clip.path_id,clipSha256=hashlib.sha256(clip.get_raw_data()).hexdigest(),data=data,nativeGameTested=False)
 (ROOT/'docs/evidence/battle080.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps(dict(durationMs=data['ms'],impactMs=data['impactMs'])))
if __name__=='__main__':main()

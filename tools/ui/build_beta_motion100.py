"""Bake original Unity Hermite/streamed curves into small GFx lookup tables.
No new textures. Unity Z/rotation/shader channels are not claimed reproduced.
"""
from pathlib import Path
import gzip,hashlib,json,math,struct,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
def hermite(keys,t):
 if not keys:return t
 if t<=keys[0]['time']:return keys[0]['value']
 if t>=keys[-1]['time']:return keys[-1]['value']
 for a,b in zip(keys,keys[1:]):
  if a['time']<=t<=b['time']:
   dt=b['time']-a['time'];u=(t-a['time'])/dt
   return (2*u**3-3*u**2+1)*a['value']+(u**3-2*u**2+u)*a['outSlope']*dt+(-2*u**3+3*u**2)*b['value']+(u**3-u**2)*b['inSlope']*dt
 raise ValueError('No interval')
def streamed(clip):
 words=clip['m_MuscleClip']['m_Clip']['data']['m_StreamedClip']['data'];raw=struct.pack('<'+str(len(words))+'I',*words);p=0;curves={}
 while p<len(raw):
  t,n=struct.unpack_from('<fi',raw,p);p+=8
  if not 0<=n<=10000:raise ValueError('Invalid streamed clip')
  for _ in range(n):
   index,*co=struct.unpack_from('<iffff',raw,p);p+=20
   if math.isfinite(t) and t>=0:curves.setdefault(index,[]).append((t,co))
 if p!=len(raw):raise ValueError('Incomplete streamed clip')
 return curves
def evaluate(keys,t):
 a=keys[0]
 for key in keys:
  if key[0]<=t:a=key
  else:break
 dt=max(0,t-a[0]);v=a[1];return ((v[0]*dt+v[1])*dt+v[2])*dt+v[3]
def main():
 source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/prefabs/game_base';digest=hashlib.sha256(source.read_bytes()).hexdigest();e=UnityPy.load(str(source))
 preview=next(o for o in e.objects if o.path_id==1070957962630426735).read_typetree()
 motion=json.loads((ROOT/'docs/evidence/beta-motion100.json').read_text());records={r['id']:r for r in motion['records']};tables={};durations={};origins={}
 for name,key,duration in [('PREVIEW','EaseEnterAnim','EaseEnterAnimTime'),('PREVIEW_FULL','RightEnterAnim','RightEnterAnimTime')]:
  tables[name]=[hermite(preview[key]['m_Curve'],i/120) for i in range(121)];durations[name]=preview[duration]*1000;origins[name]={'asset':str(source),'object':1070957962630426735,'curve':key}
 step=records[3968]['parameters'];tables['LAND']=[hermite(step['TranslationX']['keys'],i/120) for i in range(121)];durations['LAND']=step['Time']*1000;origins['LAND']={'object':3968,'curve':'TranslationX','file':motion['source']}
 for name,file in [('POWER_UP','TotalPowerIncrease'),('POWER_DOWN','TotalPowerDecrease'),('POWER_UP_LARGE','TotalPowerIncreaseLarge'),('POWER_DOWN_LARGE','TotalPowerDecreaseLarge')]:
  p=next((ROOT/'BetaGwent/build/beta-presentation91/combat').glob('*-'+file+'.json.gz'));clip=json.loads(gzip.decompress(p.read_bytes()));curves=streamed(clip);duration=clip['m_MuscleClip']['m_StopTime']
  if len(clip['m_ClipBindingConstant']['genericBindings'])!=1 or clip['m_ClipBindingConstant']['genericBindings'][0]['attribute']!=3:raise ValueError('Expected original XYZ scale clip')
  tables[name]=[evaluate(curves[0],duration*i/120) for i in range(121)];durations[name]=duration*1000;origins[name]={'clip':file,'export':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'channel':'scale X/Y; Z omitted in GFx'}
 for name,values in tables.items():
  if not all(math.isfinite(v) for v in values):raise ValueError(name)
 lines=['package {','    // Generated from original Beta serialized curves; 2D adaptation.','    public class BetaGwentBetaMotion {']
 for name,values in tables.items():
  lines+=['        private static const '+name+':Array=['+','.join(format(v,'.7g') for v in values)+'];']
 lines+=['        public static function duration(name:String):Number {','            switch(name) {']
 lines+=['                case "'+name+'": return '+format(v,'.9g')+';' for name,v in durations.items()]
 lines+=['            } return 300;','        }','        public static function sample(name:String,progress:Number):Number {','            var values:Array; switch(name) {']
 lines+=['                case "'+name+'": values='+name+'; break;' for name in tables]
 lines+=['            } if(!values)return progress;','            var p:Number=Math.max(0,Math.min(1,progress))*120;','            var a:int=int(p); var b:int=Math.min(120,a+1);','            return values[a]+(values[b]-values[a])*(p-a);','        }','    }','}']
 (ROOT/'BetaGwent/ui/src/BetaGwentBetaMotion.as').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Source changed')
 report={'sourceSha256':digest,'sourceUnchanged':True,'curves':origins,'durationsMs':durations,'bounds':{k:[min(v),max(v)] for k,v in tables.items()},'texturesAdded':0,'nativeVisualParityVerified':False}
 (ROOT/'docs/evidence/beta-motion100-bake.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('Baked',len(tables),'original curves; no textures added')
if __name__=='__main__':main()

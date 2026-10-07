"""Read original Beta serialized movement assets without editing the client.
Explicit Unity 5 layouts are checked against complete object byte lengths.
"""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'tools/vendor/audio-python'))
import UnityPy
class Reader:
 def __init__(self,b):self.b=b;self.p=0
 def read(self,fmt):
  v=struct.unpack_from('<'+fmt,self.b,self.p);self.p+=struct.calcsize('<'+fmt);return v[0] if len(v)==1 else list(v)
 def align(self):self.p=(self.p+3)//4*4
 def ptr(self):return {'file':self.read('i'),'pathId':self.read('q')}
 def flag(self):v=self.read('B');self.align();return bool(v)
 def string(self):n=self.read('i');v=self.b[self.p:self.p+n].decode('utf-8');self.p+=n;self.align();return v
 def curve(self):
  n=self.read('i')
  if not 0<=n<=1000:raise ValueError('Invalid key count '+str(n))
  keys=[dict(zip(('time','value','inSlope','outSlope'),self.read('ffff'))) for _ in range(n)]
  return {'keys':keys,'preInfinity':self.read('i'),'postInfinity':self.read('i'),'rotationOrder':self.read('i')}
 def header(self):self.ptr();self.flag();self.ptr();return self.string()
def main():
 source=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets';digest=hashlib.sha256(source.read_bytes()).hexdigest();e=UnityPy.load(str(source));records=[]
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  data=o.read(check_read=False);name=data.m_Script.read().m_ClassName
  if name not in ('MovementSettings','MovementDefinition','VelocityMovementStep','TimeMovementStep'):continue
  r=Reader(o.get_raw_data());title=r.header();value={}
  if name=='MovementSettings':
   value['MouseDragDistanceFromBoard']=r.read('f')
   fields=('MulliganOutgoing','MulliganIncoming','InLocation','InHand','MouseDrag','TransactionCancel','TransactionCancelOnHand','HandToExecutionStack','ActiveToExecutionStack','EventToExecutionStack','DeckToGraveyard','DeckToHand','DeckToHandOpponent','HandDiscardToExecutionStack','ExecutionStackToGraveyard','ExecutionStackToActive','ExecutionStackToHand','ToPlayStack','GenericToPlayStack','HandDiscardToGraveyardFar','HandDiscardToGraveyardClose')
   value.update({n:r.ptr() for n in fields})
  elif name=='MovementDefinition':
   value={'Pause':r.read('i'),'PushToMovementQueue':r.flag()};value['Steps']=[r.ptr() for _ in range(r.read('i'))]
  else:
   value={'AnchorTo':r.read('i'),'OffsetType':r.read('i'),'ClearPause':r.read('i'),'TimeBeforePopping':r.read('f')}
   if name=='TimeMovementStep':
    value.update(Time=r.read('f'),HasTranslationPerAxis=r.flag())
    for n in ('TranslationX','TranslationY','TranslationZ'):value[n]=r.curve()
    value['HasRotation']=r.flag();value['MaxRotation']=r.read('fff');value['HasRotationPerAxis']=r.flag()
    for n in ('RotationX','RotationY','RotationZ'):value[n]=r.curve()
   else:
    value.update(MaxSpeed=r.read('f'),Acceleration=r.read('f'),SpeedPerAxis=r.flag())
    for n in ('SpeedXAxis','SpeedYAxis','SpeedZAxis'):value[n]=r.curve()
    value.update(MaxDistanceToAnchor=r.read('f'),RotationAcceleration=r.read('f'),RotationSpeedCurve=r.curve(),MaxRotation=r.read('fff'),RotationAtDistanceCurve=r.curve())
   value.update(HasAnimation=r.flag(),AnimationType=r.read('i'))
  if r.p!=len(r.b):raise ValueError(f'{name} {title}: consumed {r.p}/{len(r.b)}; unsupported layout')
  records.append({'id':o.path_id,'name':title,'class':name,'bytes':len(r.b),'parameters':value})
 if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Original source changed')
 out=ROOT/'docs/evidence/beta-motion100.json';out.write_text(json.dumps({'source':str(source),'sha256':digest,'sourceUnchanged':True,'records':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print('Extracted',len(records),'fully parsed movement objects:',out)
if __name__=='__main__':main()

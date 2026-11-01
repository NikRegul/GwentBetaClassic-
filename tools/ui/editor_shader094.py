"""Bounded float32 evaluator for the extracted editor pixel-shader instructions.

No generic substitute shader. Unknown instructions fail. Offline sampling uses
the source wrap setting and bilinear mip 0; GPU derivatives/colour-space pipeline
and the game's camera are separate visual-acceptance limitations.
"""
from pathlib import Path
import copy, gzip, json, re
import numpy as np
from PIL import Image

def arguments(text):
    return re.split(r',\s*(?![^()]*\))',text)

def sample(image,uv,wrap=0):
    h,w=image.shape[:2];x=uv[:,0]*w-.5;y=(1-uv[:,1])*h-.5
    x0=np.floor(x).astype(int);y0=np.floor(y).astype(int);fx=(x-x0)[:,None];fy=(y-y0)[:,None]
    def ix(v,n):return v%n if wrap==0 else np.clip(v,0,n-1)
    a=image[ix(y0,h),ix(x0,w)];b=image[ix(y0,h),ix(x0+1,w)]
    c=image[ix(y0+1,h),ix(x0,w)];d=image[ix(y0+1,h),ix(x0+1,w)]
    return ((a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy).astype(np.float32)

def execute(assembly,inputs,buffers,textures):
    count=len(next(iter(inputs.values())));regs={k:np.array(v,dtype=np.float32,copy=True) for k,v in inputs.items()}
    def value(token,integer=False):
        token=token.strip();negative=token.startswith('-');token=token[1:] if negative else token
        absolute=token.startswith('|');token=token.strip('|')
        if token.startswith('l('):
            literals=arguments(token[2:-1]);numbers=[]
            for t in literals:
                numbers.append(np.array([int(t,16)],dtype=np.uint32).view(np.float32)[0] if t.startswith('0x') else float(t))
            if len(numbers)==1:numbers*=4
            result=np.broadcast_to(np.array(numbers,dtype=np.float32),(count,4))
        else:
            match=re.fullmatch(r'(cb\d+\[\d+\]|[rvo]\d+)(?:\.([xyzw]+))?',token);assert match,token
            name,swizzle=match.groups()
            if name.startswith('cb'):
                cb,index=map(int,re.findall(r'\d+',name));base=np.broadcast_to(buffers[cb][index],(count,4))
            else:base=regs.setdefault(name,np.zeros((count,4),np.float32))
            swizzle=swizzle or 'xyzw';swizzle=(swizzle*4)[:4]
            result=base[:,['xyzw'.index(c) for c in swizzle]]
        if integer:
            result=np.ascontiguousarray(result).view(np.int32)
            if negative:result=-result
        else:
            if absolute:result=np.abs(result)
            if negative:result=-result
        return result
    for line in assembly.splitlines():
        line=line.strip()
        if not line or line.startswith('//') or line.startswith('dcl_') or line in ['ps_4_0','ret']:continue
        opcode,operand=line.split(' ',1);args=arguments(operand);dest=args[0];sat=opcode.endswith('_sat');opcode=opcode.removesuffix('_sat')
        match=re.fullmatch(r'([ro]\d+)(?:\.([xyzw]+))?',dest);assert match,dest
        name,mask=match.groups();mask=mask or 'xyzw'
        with np.errstate(divide='ignore',invalid='ignore',over='ignore'):
            if opcode=='sample':
                index=int(re.match(r't(\d+)',args[2]).group(1));image,wrap=textures[index];result=sample(image,value(args[1])[:,:2],wrap)
            elif opcode in ['and','iadd']:
                a,b=value(args[1],True),value(args[2],True)
                result=np.ascontiguousarray((a&b) if opcode=='and' else a+b).view(np.float32)
            elif opcode=='itof':result=value(args[1],True).astype(np.float32)
            else:
                a=value(args[1]);b=value(args[2]) if len(args)>2 else None;c=value(args[3]) if len(args)>3 else None
                if opcode=='mov':result=a
                elif opcode=='add':result=a+b
                elif opcode=='mul':result=a*b
                elif opcode=='mad':result=a*b+c
                elif opcode=='div':result=a/b
                elif opcode=='min':result=np.minimum(a,b)
                elif opcode=='max':result=np.maximum(a,b)
                elif opcode=='log':result=np.log2(a)
                elif opcode=='exp':result=np.exp2(a)
                elif opcode=='frc':result=a-np.floor(a)
                elif opcode=='dp3':result=np.repeat(np.sum(a[:,:3]*b[:,:3],axis=1)[:,None],4,axis=1)
                elif opcode in ['ge','lt']:
                    result=np.where(a>=b if opcode=='ge' else a<b,np.uint32(0xffffffff),np.uint32(0)).view(np.float32)
                else:raise ValueError('Unsupported source pixel instruction '+opcode)
            if sat:result=np.clip(result,0,1)
        target=regs.setdefault(name,np.zeros((count,4),np.float32));indices=['xyzw'.index(c) for c in mask]
        target[:,indices]=result[:,indices]
    assert 'o0' in regs
    return regs['o0']

class MaterialProgram:
    def __init__(self,audit_dir,shader_dir,audit,material_id):
        self.material=copy.deepcopy(audit['materials'][str(material_id)]);sid=self.material['shader']
        self.shader=audit['shaders'][sid]
        tree=json.loads(gzip.decompress((Path(shader_dir)/sid/'serialized.json.gz').read_bytes()))
        passed=tree['m_ParsedForm']['m_SubShaders'][0]['m_Passes'][0]
        self.names={index:name for name,index in passed['m_NameIndices']};self.params=passed['progFragment']['m_SubPrograms'][0]
        report=json.loads((Path(shader_dir)/'report.json').read_text('utf8'))
        program=next(p for p in report['shaders'][sid]['programs'] if p['index']==self.params['m_BlobIndex'])
        self.assembly=(Path(shader_dir)/sid/program['file']).read_text('utf8')
        tex={row['property']:row for row in self.material['textures']};self.textures={}
        for param in self.params['m_TextureParams']:
            name=self.names[param['m_NameIndex']];row=tex.get(name)
            if not row:raise ValueError('Unresolved source texture '+name)
            image=np.array(Image.open(Path(audit_dir)/'textures'/(row['texture']+'.png')).convert('RGBA'),np.float32)/255
            wrap=audit['textures'][row['texture']].get('settings',{}).get('m_WrapMode',0)
            self.textures[param['m_Index']]=(image,wrap)
    def shade(self,inputs,seconds,overrides=None):
        values={**self.material['floats'],**self.material['colors']}
        values['_Time']=[seconds/20,seconds,seconds*2,seconds*3]
        for row in self.material['textures']:
            values[row['property']+'_ST']=[row['scale']['x'],row['scale']['y'],row['offset']['x'],row['offset']['y']]
        values.update(overrides or {});buffers={}
        slots={v['m_NameIndex']:v['m_Index'] for v in self.params['m_ConstantBufferBindings']}
        for cb in self.params['m_ConstantBuffers']:
            data=np.zeros(max(1,(cb['m_Size']+15)//16)*4,np.float32)
            for param in cb['m_VectorParams']:
                name=self.names[param['m_NameIndex']]
                if name not in values:raise ValueError('Unresolved source uniform '+name)
                v=values[name]
                if isinstance(v,dict):v=[v[k] for k in 'rgba']
                elif isinstance(v,(int,float)):v=[v]
                index=param['m_Index']//4;data[index:index+param['m_Dim']]=v[:param['m_Dim']]
            buffers[slots[cb['m_NameIndex']]]=data.reshape(-1,4)
        return execute(self.assembly,inputs,buffers,self.textures)

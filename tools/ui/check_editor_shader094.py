"""Independent numeric checks for source-shader sampling, alpha and mixed blending."""
from pathlib import Path
import argparse,json
import numpy as np
from editor_shader094 import MaterialProgram,execute,sample

def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',type=Path,required=True);p.add_argument('--shaders',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    data=json.loads((a.audit/'audit.json').read_text('utf8'));checks=0
    def eq(actual,expected,name):
        nonlocal checks
        np.testing.assert_allclose(actual,expected,atol=2e-6,rtol=2e-6,err_msg=name);checks+=1
    tex=np.array([[[.2,.3,.5,.4]]],np.float32);uv=np.array([[.5,.5,0,1]],np.float32)
    vertex=np.array([[.7,.9,.5,.75]],np.float32);tint=np.array([.8,.6,.4,.5],np.float32)
    for mid in ['2421597316335589149','1430841163770799006']:
        program=MaterialProgram(a.audit,a.shaders,data,mid);program.textures={0:(tex,1)}
        actual=program.shade({'v1':uv,'v2':vertex},.1,{'_Brightness':3,'_AlphaPower':2,'_TintColor':tint.tolist()})[0]
        expected=tex[0,0,:3]*vertex[0,:3]*tint[:3]*3*(tex[0,0,3]*vertex[0,3]*tint[3])**2*tex[0,0,3]
        eq(actual[:3],expected,'One/One alpha-power mask and material brightness');eq(actual[3],1,'shader writes additive alpha one')
    program=MaterialProgram(a.audit,a.shaders,data,'8744766969455095725');program.textures={0:(tex,1)}
    actual=program.shade({'v1':uv,'v2':vertex},0,{'_TintColor':tint.tolist()})[0]
    eq(actual[:3],2*tex[0,0,:3]*tint[:3]*vertex[0,:3],'custom flash source two-times RGB')
    eq(actual[3],tex[0,0,3]*tint[3]*vertex[0,3],'custom flash source alpha retained')
    program=MaterialProgram(a.audit,a.shaders,data,'-999152266299583250');program.textures={0:(tex,1)}
    eq(program.shade({'v1':uv,'v2':vertex},0,{'_Brightness':2,'_TintColor':tint.tolist()})[0],
       np.r_[tex[0,0,:3]*vertex[0,:3]*tint[:3]*2,1],'ordinary source additive RGB')
    image=np.array([[[1,0,0,1],[0,1,0,1]]],np.float32)
    eq(sample(image,np.array([[1,.5]],np.float32),0)[0],[.5,.5,0,1],'repeat wraps both bilinear taps')
    eq(sample(image,np.array([[1,.5]],np.float32),1)[0],[0,1,0,1],'clamp does not wrap')
    asm='ps_4_0\nge r0.x, v1.x, v1.y\nand r0.x, r0.x, l(0x3f800000)\nmov o0.xyzw, r0.xxxx\nret'
    eq(execute(asm,{'v1':np.array([[1,0,0,0],[0,1,0,0]],np.float32)},{},{})[:,0],[1,0],'D3D bool bitmask and float bit reinterpretation')
    program=MaterialProgram(a.audit,a.shaders,data,'5438722605629055662')
    inputs={'v1':uv,'v2':np.array([[.5,.5,0,1]],np.float32)}
    x=program.shade(inputs,.1,{'_Alpha':.5,'_UIFade':0});y=program.shade(inputs,.1,{'_Alpha':.25,'_UIFade':0})
    eq(x[:,:3],y[:,:3],'ordinary alpha control does not change RGB');eq(x[:,3],2*y[:,3],'ordinary alpha control remains separate')
    eq(program.shade(inputs,.1,{'_UIFade':1})[:,3],[0],'source UI fade fully hides normal layer')
    try:execute('ps_4_0\nunknown o0.xyzw, v1.xyzw',{'v1':vertex},{},{})
    except ValueError:checks+=1
    else:raise AssertionError('Unknown source instructions must not be approximated silently')
    assert program.shader['blend']==dict(srcBlend=5,destBlend=10,blendOp=0);checks+=1
    result=dict(checks=checks,failures=[],sourcePixelInstructions=True,independentFormulaControls=True,nativeGpuParity=False)
    a.out.write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))

if __name__=='__main__':main()

"""Independent closed-form checks for the original ValidVFX material.

The One/One pixel shader multiplies texture alpha twice when AlphaPower=1;
the output alpha is 1, so no additional vertex/texture alpha is applied at blend.
"""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
from editor_shader094 import MaterialProgram
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--audit',type=Path,required=True)
 p.add_argument('--shaders',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 assert not a.out.exists()
 data=json.loads((a.audit/'audit.json').read_text('utf8'));program=MaterialProgram(a.audit,a.shaders,data,'3040660544023381124')
 assert program.material['floats']==dict(_AlphaPower=1.0,_Brightness=2.0)
 assert program.material['colors']['_TintColor']==dict(r=1.0,g=1.0,b=1.0,a=1.0)
 assert program.shader['blend']==dict(srcBlend=1.0,destBlend=1.0,blendOp=0.0)
 checks=0
 for texture_alpha in [0,.25,.5,1]:
  for vertex_alpha in [0,.2,.7,1]:
   tex=np.array([[[.2,.3,.5,texture_alpha]]],np.float32)
   vertex=np.array([[.7,.4,.9,vertex_alpha]],np.float32);program.textures={0:(tex,1)}
   actual=program.shade({'v1':np.array([[.5,.5,0,1]],np.float32),'v2':vertex},.1)[0]
   expected=np.r_[tex[0,0,:3]*vertex[0,:3]*2*texture_alpha**2*vertex_alpha,1]
   np.testing.assert_allclose(actual,expected,atol=2e-6,rtol=2e-6);assert np.isfinite(actual).all();checks+=1
 report=dict(complete=True,checks=checks,failures=[],sourceSha256=data['sourceSha256'],auditSha256=sha(a.audit/'audit.json'),
  shaderReportSha256=sha(a.shaders/'report.json'),formula='RGB=textureRGB*vertexRGB*2*textureAlpha^2*vertexAlpha; outputAlpha=1; One/One Add',
  nativeGameplayVerified=False,canonicalUiChanged=False)
 a.out.write_text(json.dumps(report,indent=2)+'\n','utf8');print(json.dumps(report))

if __name__=='__main__':main()

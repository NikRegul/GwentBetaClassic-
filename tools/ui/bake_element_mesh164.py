"""Project original particle meshes with their UVs and vertex colors to a quad."""
import numpy as np
from PIL import Image
from UnityPy.helpers.MeshHelper import MeshHandler

def bake(mesh,image,texenv,size=128):
 h=MeshHandler(mesh);h.process()
 vertices=np.array(h.m_Vertices);uv=np.array(h.m_UV0);colors=np.array(h.m_Colors or [[1,1,1,1]]*len(vertices))
 # Use the two principal mesh axes. Particle orientation is supplied at runtime.
 axes=sorted(range(3),key=lambda i:np.ptp(vertices[:,i]),reverse=True)[:2];axes.sort()
 xy=vertices[:,axes];lo=xy.min(axis=0);span=np.maximum(1e-6,xy.max(axis=0)-lo);xy=(xy-lo)/span*(size-1);xy[:,1]=size-1-xy[:,1]
 tex=np.array(image,dtype=float)/255;out=np.zeros((size,size,4));scale=np.array(texenv['scale']);offset=np.array(texenv['offset'])
 for group in h.get_triangles():
  for triangle in group:
   ids=list(triangle);a,b,c=xy[ids];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
   if abs(den)<1e-8:continue
   left,top=np.maximum(0,np.floor(np.min(xy[ids],axis=0))).astype(int);right,bottom=np.minimum(size-1,np.ceil(np.max(xy[ids],axis=0))).astype(int)
   yy,xx=np.mgrid[top:bottom+1,left:right+1];wa=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den;wb=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;wc=1-wa-wb
   weights=np.stack([wa,wb,wc],axis=-1);inside=np.min(weights,axis=-1)>=-1e-5
   coords=(weights@uv[ids])*scale+offset;coords%=1
   tx=np.minimum(tex.shape[1]-1,(coords[:,:,0]*tex.shape[1]).astype(int));ty=np.minimum(tex.shape[0]-1,((1-coords[:,:,1])*tex.shape[0]).astype(int))
   rgba=tex[ty,tx]*(weights@colors[ids]);target=out[top:bottom+1,left:right+1];target[inside]=rgba[inside]
 return Image.fromarray(np.clip(out*255,0,255).astype('uint8'),'RGBA')

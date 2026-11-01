"""Dump the level8 CoinRoot ParticleSystem modules used by BetaGwentPassCoin096 (UnityPy portable)."""
import UnityPy,os,json
D=os.environ['HOME']+'/mnt/w3mod/Gwent 0.9.24.3.432/Gwent_Data/'
env=UnityPy.load(D+'level8');objs={o.path_id:o for o in env.objects}
names={};tr={};comps={}
for o in env.objects:
    if o.type.name=='GameObject':d=o.read_typetree();names[o.path_id]=d['m_Name'];comps[o.path_id]=[c['component']['m_PathID'] for c in d['m_Component']]
for o in env.objects:
    if o.type.name in('Transform','RectTransform'):tr[o.path_id]=o.read_typetree()
def path(p):
    out=[]
    while p in tr:out.append(names[tr[p]['m_GameObject']['m_PathID']]);p=tr[p]['m_Father']['m_PathID']
    return '/'.join(reversed(out))
def mm(c):
    st=c.get('minMaxState');
    if st==0:return c['scalar']
    if st==3:return ['rand',c['minScalar'],c['scalar']]
    def cv(k):return [(round(x['time'],3),round(x['value'],3)) for x in c[k]['m_Curve']]
    return ['curve',st,c['scalar'],cv('maxCurve'),cv('minCurve') if st==2 else None]
def grad(g):
    def one(x):
        n=x['m_NumColorKeys'];na=x['m_NumAlphaKeys']
        cols=[(round(x['ctime%d'%i]/65535,3),[round(x['key%d'%i][k],3) for k in 'rgb']) for i in range(n)]
        als=[(round(x['atime%d'%i]/65535,3),round(x['key%d'%i]['a'],3)) for i in range(na)]
        return dict(c=cols,a=als)
    st=g['minMaxState']
    if st==0:return ['const',[round(g['maxColor'][k],3) for k in 'rgba']]
    if st==2:return ['randcol',[round(g['minColor'][k],3) for k in 'rgba'],[round(g['maxColor'][k],3) for k in 'rgba']]
    if st==1:return ['grad',one(g['maxGradient'])]
    return ['randgrad',one(g['minGradient']),one(g['maxGradient'])]
res={}
for p,d in tr.items():
    pth=path(p)
    if not pth.startswith('CoinRoot/'):continue
    g=d['m_GameObject']['m_PathID']
    for pid in comps[g]:
        o=objs[pid]
        if o.type.name!='ParticleSystem':continue
        s=o.read_typetree();I=s['InitialModule'];E=s['EmissionModule'];S=s['ShapeModule']
        e=dict(path=pth,looping=s['looping'],duration=s['lengthInSec'],sim=s.get('moveWithTransform'),prewarm=s.get('prewarm'),
          life=mm(I['startLifetime']),speed=mm(I['startSpeed']),size=mm(I['startSize']),rot=mm(I['startRotation']),color=grad(I['startColor']),
          max=I['maxNumParticles'],gravity=mm(I['gravityModifier']),rate=mm(E['rateOverTime']),bursts=[(b['time'],mm(b['countCurve']) if 'countCurve' in b else b.get('minCount')) for b in E.get('m_Bursts',[])],
          shape=dict(on=S['enabled'],type=S['type'],angle=S.get('angle'),radius=S['radius']['value'] if isinstance(S['radius'],dict) else S['radius'],arc=S.get('arc') if not isinstance(S.get('arc'),dict) else S['arc']['value'],thick=S.get('radiusThickness')))
        for mod in ['ColorModule','SizeModule','VelocityModule','RotationModule','UVModule','ForceModule','ClampVelocityModule','NoiseModule','TrailModule']:
            m=s.get(mod)
            if m and m.get('enabled'):
                if mod=='ColorModule':e['colorOver']=grad(m['gradient'])
                elif mod=='SizeModule':e['sizeOver']=mm(m['curve'])
                elif mod=='VelocityModule':e['vel']=[mm(m[k]) for k in 'xyz'];e['velSpace']=m.get('inWorldSpace')
                elif mod=='RotationModule':e['spin']=mm(m['curve'])
                elif mod=='UVModule':e['uv']=[m.get('tilesX'),m.get('tilesY'),mm(m['frameOverTime'])]
                elif mod=='ClampVelocityModule':e['clamp']=[mm(m['magnitude']),m.get('dampen')]
                else:e[mod]='on'
        res[pth]=e
        print(json.dumps(e)[:1200])
json.dump(res,open('coinps.json','w'),indent=1)

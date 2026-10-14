"""Extract the Gwent 0.9.24 banish effect (BanishCardEffect prefab) for the GFx board.

Sources (Gwent_Data/sharedassets8.assets):
  BanishCardEffect (GameObject 1150), CardBanishVisualEffect (MonoBehaviour 4266):
    m_BanishMaterial = Banish_Small_Material, m_DissolveProgress = linear 0..1,
    m_MaterialPropertiesToAnimate = [_DissolveProgress], m_DissolveAnimationTime = 1.2 s.
  Banish_Small_Material: _DissolveTex NoiseSoftEge, _DissolveRamp EpicHighlightGradient,
    _EmissionMulti 1.86.
  Particle systems: BackLines (BanishBack / BanishHit 2x2), EmissionElementMid and
    EmissionElementRim (BanishSparks / BanishSparks 1 3x3). The root ExplosionFragments
    system has zero emission and no bursts, so it never shows anything.
Outputs:
  BetaGwent/ui/assets/special144/banish_beta.png  (BanishHit 2x2 x 128 px, then BanishSparks 3x3 x 64 px)
  BANISH noise/ramp in BetaGwent/ui/src/BetaGwentDissolveData144.as
  docs/evidence/banish160.json
Requires UnityPy (development step, not part of the release build).
"""
from pathlib import Path
import json,re,struct,sys
ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
W,H=44,60
EMISSION=1.86
def main():
    import UnityPy
    from PIL import Image
    env=UnityPy.load(str(DATA));objs={o.path_id:o for o in env.objects}
    go=objs[1150].read();assert go.m_Name=='BanishCardEffect'
    raw=objs[4266].get_raw_data()
    material=struct.unpack_from('<iq',raw,44);assert material==(0,199),material
    keys=struct.unpack_from('<i8f',raw,56);assert keys[0]==2 and keys[1:]==(0,0,1,1,1,1,1,1),keys
    assert raw[112:129]==b'_DissolveProgress'
    seconds=struct.unpack_from('<f',raw,len(raw)-4)[0];assert abs(seconds-1.2)<1e-6,seconds
    mat=objs[199].read();assert mat.m_Name=='Banish_Small_Material'
    tex={k:v.m_Texture.m_PathID for k,v in mat.m_SavedProperties.m_TexEnvs}
    floats=dict(mat.m_SavedProperties.m_Floats)
    noise=objs[tex['_DissolveTex']].read();ramp=objs[tex['_DissolveRamp']].read()
    assert noise.m_Name=='NoiseSoftEge' and ramp.m_Name=='EpicHighlightGradient'
    grid=noise.image.convert('L').resize((W,H),Image.Resampling.BOX)
    values=[min(254,round(v*254/255)) for v in grid.getdata()]
    noise_hex=''.join('%02x'%v for v in values)
    strip=ramp.image.convert('RGB');row=strip.height//2
    # Six bands from the cut outward, sampled at band centres and lit by _EmissionMulti.
    ramp_colors=[]
    for k in range(6):
        r,g,b=strip.getpixel((min(strip.width-1,int((k+.5)/6*strip.width)),row))
        ramp_colors.append((min(255,round(r*floats['_EmissionMulti'])),min(255,round(g*floats['_EmissionMulti'])),min(255,round(b*floats['_EmissionMulti']))))
    # Atlas: BanishHit (2048, 2x2) and BanishSparks 1 (1024, 3x3), straight alpha.
    hit=objs[597].read();sparks=objs[771].read();assert hit.m_Name=='BanishHit' and sparks.m_Name=='BanishSparks 1'
    atlas=Image.new('RGBA',(256,448),(0,0,0,0))
    h=hit.image.convert('RGBA');cw=h.width/2
    for i in range(4):
        cell=h.resize((128,128),Image.Resampling.LANCZOS,box=((i%2)*cw,(i//2)*cw,(i%2+1)*cw,(i//2+1)*cw));atlas.paste(cell,((i%2)*128,(i//2)*128))
    s=sparks.image.convert('RGBA');cs=s.width/3
    for i in range(9):
        cell=s.resize((64,64),Image.Resampling.LANCZOS,box=((i%3)*cs,(i//3)*cs,(i%3+1)*cs,(i//3+1)*cs));atlas.paste(cell,((i%3)*64,256+(i//3)*64))
    target=ROOT/'BetaGwent/ui/assets/special144/banish_beta.png';atlas.save(target,optimize=True)
    # Dissolve data class: insert or replace the BANISH block.
    block=('        // BanishCardEffect: Banish_Small_Material _DissolveTex=NoiseSoftEge,\n'
           '        // _DissolveRamp=EpicHighlightGradient x _EmissionMulti %.2f; 1.2 s, linear.\n'
           '        public static const BANISH:String="%s";\n'
           '        public static const BANISH_RAMP:Array=[%s];\n'
           '        public static const BANISH_MS:int=%d;\n')%(floats['_EmissionMulti'],noise_hex,','.join('0x%02X%02X%02X'%c for c in ramp_colors),round(seconds*1000))
    for folder in ('src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder'):
        path=ROOT/'BetaGwent/ui'/folder/'BetaGwentDissolveData144.as'
        if not path.exists():continue
        text=path.read_text('utf-8-sig')
        text=re.sub(r'        // BanishCardEffect:.*?BANISH_MS:int=\d+;\n','',text,flags=re.S)
        anchor='        public static const POISON:String='
        at=text.index(anchor);end=text.index('\n',at)+1
        text=text[:end]+block+text[end:]
        path.write_text(text,'utf-8')
    evidence=dict(source=str(DATA.name),prefab='BanishCardEffect',material='Banish_Small_Material',dissolveSeconds=seconds,curve='linear 0..1',
        emissionMulti=floats['_EmissionMulti'],outline=[round(v,3) for v in (lambda c:(c.r,c.g,c.b))(dict(mat.m_SavedProperties.m_Colors)['_OutlineColor'])],
        ramp=['#%02X%02X%02X'%c for c in ramp_colors],noiseGrid=[W,H],
        particles=dict(
            backLines=dict(delay=.03,burst=8,life=[.18,.30],size=[18,36],sizeOverLife=[0,1],lengthScale=1.4,pivotY=.2,shape='cone r3.2 a90',spin=[-5.236,0],
                color='AlphaBlended 2*tint(0.006,0,0.176)*grey[0..0.26]',alphaKeys=[[0,0],[.071,1],[.635,1],[1,0]],sheet=[2,2]),
            mid=dict(delay=.18,offset=[.8,1.6],scale=[1.088,1.585],burst=11,rate=79,duration=.33,rateCurve=[[0,.336],[.23,1],[1,.007]],life=[.23,.5],speed=[27,75],
                clamp=[95,[1,.147],[.681,.106]],size=[4.5,9],sizeOverLife=[.875,.308],shape='cone r7.68 a41.24 random direction',
                color='AlphaBlended 2*tint(0.935,0.882,1)*start[(1,0.82,0.66)..white]',alphaKeys=[[0,0],[.071,1],[.782,1],[1,0]],sheet=[3,3]),
            rim=dict(delay=.23,burst=11,rate=70,duration=.33,life=[.23,.6],speed=[45,120],clamp=[150,[1,.117],[.769,.081]],size=[3.491,7.5],sizeOverLife=[.875,.308],
                shape='cone r6.295 a72.9',alphaKeys=[[0,0],[.071,1],[.782,1],[1,0]],sheet=[3,3]),
            fragments='ExplosionFragments: rate 0, no bursts (inactive)'),
        audio='vfx_custom_banish (3040005591) = BetaGwentAudioCue 12')
    (ROOT/'docs/evidence/banish160.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n','utf8')
    print('banish atlas',target.stat().st_size,'bytes; ramp',evidence['ramp'])
if __name__=='__main__':main()

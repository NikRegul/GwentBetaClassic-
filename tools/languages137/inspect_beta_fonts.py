"""Inventory of every TMP font asset in the Beta fonts bundle (read-only)."""
from pathlib import Path
import json, sys
ROOT = Path(__file__).resolve().parents[2]
try:
    import UnityPy
except ImportError:
    sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python')); import UnityPy
env = UnityPy.load(str(ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/fonts'))
tex, fonts = {}, {}
for o in env.objects:
    if o.type.name == 'Texture2D':
        t = o.read(); tex[t.m_Name] = [t.m_Width, t.m_Height, str(t.m_TextureFormat)]
    elif o.type.name == 'MonoBehaviour':
        try: d = o.read_typetree()
        except Exception: continue
        if 'm_glyphInfoList' in d:
            info = d['m_fontInfo']
            fb = [x for x in (d.get('fallbackFontAssets') or [])]
            fonts[d['m_Name']] = dict(info={k: info.get(k) for k in ('Name', 'PointSize', 'Padding', 'AtlasWidth', 'AtlasHeight', 'LineHeight', 'Ascender', 'Baseline', 'CapHeight')},
                                      glyphs=sorted(int(g['id']) for g in d['m_glyphInfoList']), fallbacks=len(fb))
out = {n: dict(f['info'], glyphCount=len(f['glyphs']), fallbacks=f['fallbacks'], texture=tex.get(n)) for n, f in fonts.items()}
OUT = ROOT / 'BetaGwent/build/languages137/fonts'; OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'beta-font-inventory.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', 'utf8')
(OUT / 'beta-font-glyphs.json').write_text(json.dumps({n: f['glyphs'] for n, f in fonts.items()}) + '\n', 'utf8')
for n, v in sorted(out.items()): print(n, v['glyphCount'], v['PointSize'], v['AtlasWidth'], v['AtlasHeight'], v['texture'], 'fb', v['fallbacks'])

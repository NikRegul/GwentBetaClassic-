"""Restore camera-facing Beta board surfaces and native hand/leader dividers.

Read-only Unity input. Existing board/HUD page dimensions and logical slots stay
unchanged. Mesh export mirrors X; the runtime performs the one final reflection.
"""
from pathlib import Path
import hashlib, json, re, sys
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
import UnityPy
from beta_board_sources import bake
from extract_beta_layout103 import scene, rect_at

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ui = ROOT / 'BetaGwent/ui'
    out = ROOT / 'BetaGwent/build/stage120/board-source'
    out.mkdir(parents=True, exist_ok=True)
    compact = Image.open(ui / 'assets/compact98/boards.png').convert('RGBA')
    hd = Image.open(ui / 'assets/hd94/boards.png').convert('RGBA')
    sizes = (compact.size, hd.size)
    records, originals = [], {}
    for index in range(1, 6):
        source = ROOT / f'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/boards/halfs/factions/{index}'
        originals[str(source)] = sha(source)
        env = UnityPy.load(str(source))
        objects = {o.path_id: o for o in env.objects}
        for side, name in [(1, 'board_bottom'), (2, 'board_top')]:
            go = next(o.path_id for o in env.objects if o.type.name == 'GameObject' and o.read().m_Name == name)
            filt = next(o.read() for o in env.objects if o.type.name == 'MeshFilter' and o.read().m_GameObject.path_id == go)
            renderer = next(o.read() for o in env.objects if o.type.name == 'MeshRenderer' and o.read().m_GameObject.path_id == go)
            mat = renderer.m_Materials[0].read()
            binding = next(v for k, v in mat.m_SavedProperties.m_TexEnvs if k == '_MainTex')
            mesh, tex = filt.m_Mesh.read(), binding.m_Texture.read()
            mesh_path, tex_path = out / (mesh.m_Name + '.obj'), out / (tex.m_Name + '.png')
            mesh_path.write_text(mesh.export(), 'utf8'); tex.image.save(tex_path)
            bounds = ([-124, -95, 0], [160, 3, 0]) if side == 1 else ([-124, -3, 0], [160, 95, 0])
            image = bake(mesh_path, tex_path, [binding.m_Scale.x, binding.m_Scale.y],
                         [binding.m_Offset.x, binding.m_Offset.y], size=(2048, 708), world_bounds=bounds, frontmost=True)
            faction = 1 << index
            image.save(ui / f'assets/hd94/board-{faction}-{side}.png')
            x, y = (side - 1) * 2048, (index - 1) * 708
            hd.paste(image, (x, y))
            compact.paste(image.resize((1536, 531), Image.Resampling.LANCZOS), ((side - 1) * 1536, (index - 1) * 531))
            records.append(dict(faction=faction, side=side, nearZ='minimum', mesh=mesh.m_Name, texture=tex.m_Name))
    hd.save(ui / 'assets/hd94/boards.png'); compact.save(ui / 'assets/compact98/boards.png')
    assert sizes == (compact.size, hd.size)
    # The unused portion of the resilience row holds both original dividers;
    # no additional page or GUI memory is needed.
    source = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/sharedassets8.assets'
    originals[str(source)] = sha(source)
    env = UnityPy.load(str(source)); objects = {o.path_id: o for o in env.objects}
    hud = Image.open(ui / 'assets/tokens111/hud111.png').convert('RGBA')
    code_path = ui / 'src/BetaGwentHDArt.as'; code = code_path.read_text('utf-8-sig')
    slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', code)[1])
    for i, pid in enumerate([1047, 1051]):
        ident, x, y, w, h = -1900 - i, 368 + i * 52, hud.height - 128, 44, 96
        for key, slot in slots.items():
            if slot[0] == 15 and key not in ['-1900', '-1901']:
                _, a, b, c, d = slot
                assert x+w <= a or a+c <= x or y+h <= b or b+d <= y, (ident, key)
        hud.paste(objects[pid].read().image.resize((w, h), Image.Resampling.LANCZOS), (x, y))
        slots[str(ident)] = [15, x, y, w, h]
    target = ui / 'assets/battle120'; target.mkdir(exist_ok=True); hud.save(target / 'hud120.png')
    code = re.sub(r'private static var slots:Object=\{.*?\};', 'private static var slots:Object='+json.dumps(slots,separators=(',',':'))+';', code)
    code = code.replace('tokens111/hud111.png', 'battle120/hud120.png')
    code_path.write_text(code, 'utf-8-sig')
    level = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/level8'; originals[str(level)] = sha(level)
    nodes = scene(level); dividers = []
    for name, n in nodes.items():
        if name.endswith('/LeftSeparator') or name.endswith('/RightSeparator'):
            x,y,z = n['world']; sx,sy,_ = n['scale']
            rect = rect_at(x,y,z,.87*abs(sx),1.93*abs(sy))
            dividers.append([-1900 if name.endswith('/LeftSeparator') else -1901, *rect])
    (ui / 'src/BetaGwentBoardDetails120.as').write_text('package {\n public class BetaGwentBoardDetails120 {\n  public static const DIVIDERS:Array='+json.dumps(dividers,separators=(',',':'))+';\n }\n}\n', 'utf8')
    report = dict(boards=records, dividers=dividers, dimensionsUnchanged=True,
                  runtimeMirrorRequired=True, originalsUnchanged=all(sha(Path(p))==v for p,v in originals.items()),
                  sourceHashes=originals, boardAtlasSha256=sha(ui/'assets/compact98/boards.png'),
                  hudAtlasSha256=sha(target/'hud120.png'), runtimeVerified=False)
    (ROOT / 'docs/evidence/board120.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print('Restored 10 camera-facing board halves and 6 native separators; atlas dimensions unchanged.')

if __name__ == '__main__': main()

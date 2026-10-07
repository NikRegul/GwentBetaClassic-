"""Project the original Gwent Beta 0.9.24 battle scene into the 1920x1080 board.

Sources (read-only): Gwent_Data/level8 (battle scene: camera, board anchors,
row/leader/hand/pile colliders, counters, ribbon, crowns, score, turn coin) and
the stage-91 ribbon OBJ exports. The original camera is perspective, FOV 60,
at (0,0,-185) looking +Z; Unity mesh/OBJ export negates X.

Output: BetaGwent/ui/src/BetaGwentBoardLayout.as (generated constants) and
docs/evidence/beta-layout103.json. Board art keeps the HD bake world bounds
(x -160..124, y -95..3 / -3..95) projected on the row plane (z=1.14).
"""
from pathlib import Path
import argparse, glob, hashlib, json, math, os, sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CAM_Z, FOV, W, H = -185.0, 60.0, 1920.0, 1080.0
T = math.tan(math.radians(FOV / 2))


def proj(x, y, z):
    d = z - CAM_Z
    return (W / 2 + x / (d * T * W / H) * W / 2, H / 2 - y / (d * T) * H / 2)


def rect_at(cx, cy, z, w, h):
    a, b = proj(cx - w / 2, cy + h / 2, z), proj(cx + w / 2, cy - h / 2, z)
    return [round(a[0], 1), round(a[1], 1), round(b[0] - a[0], 1), round(b[1] - a[1], 1)]


def center(world):
    p = proj(*world)
    return [round(p[0], 1), round(p[1], 1)]


def q2m(q):
    x, y, z, w = q['x'], q['y'], q['z'], q['w']
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def scene(level8):
    import UnityPy
    env = UnityPy.load(str(level8))
    objs = {o.path_id: o for o in env.objects}
    names, tr, colliders = {}, {}, {}
    for o in env.objects:
        if o.type.name == 'GameObject':
            names[o.path_id] = o.read_typetree()['m_Name']
    for o in env.objects:
        if o.type.name in ('Transform', 'RectTransform'):
            d = o.read_typetree()
            tr[o.path_id] = d
    by_go = {d['m_GameObject']['m_PathID']: p for p, d in tr.items()}
    for o in env.objects:
        if o.type.name == 'BoxCollider':
            d = o.read_typetree()
            colliders.setdefault(by_go[d['m_GameObject']['m_PathID']], []).append(
                (d['m_Center'], d['m_Size']))
    world = {}

    def wm(p):
        if p not in world:
            d = tr[p]
            m = np.eye(4)
            m[:3, :3] = q2m(d['m_LocalRotation']) * np.array([d['m_LocalScale'][k] for k in 'xyz'])
            m[:3, 3] = [d['m_LocalPosition'][k] for k in 'xyz']
            f = d['m_Father']['m_PathID']
            world[p] = wm(f) @ m if f in tr else m
        return world[p]

    def path(p):
        out = []
        while p in tr:
            out.append(names[tr[p]['m_GameObject']['m_PathID']])
            p = tr[p]['m_Father']['m_PathID']
        return '/'.join(reversed(out))
    nodes = {}
    for p in tr:
        m = wm(p)
        d = tr[p]
        nodes[path(p)] = dict(world=[float(v) for v in m[:3, 3]], scale=[float(m[i, i]) for i in range(3)],
                              size=[d['m_SizeDelta']['x'], d['m_SizeDelta']['y']] if 'm_SizeDelta' in d else None,
                              colliders=[([c['x'], c['y'], c['z']], [s['x'], s['y'], s['z']]) for c, s in colliders.get(p, [])])
    cam = nodes['Game Main Camera']['world']
    if [round(v, 3) for v in cam] != [0.0, 0.0, CAM_Z]:
        raise SystemExit('Unexpected original camera position: ' + str(cam))
    return nodes


def collider_rect(nodes, key):
    n = nodes[key]
    (c, s), = n['colliders']
    wx, wy, wz = n['world']
    return rect_at(wx + c[0], wy + c[1], wz + c[2], s[0], s[1])


def ui_rect(nodes, key, scale=1.0):
    n = nodes[key]
    return rect_at(n['world'][0], n['world'][1], n['world'][2], n['size'][0] * scale, n['size'][1] * scale)


def obj_rect(path):
    v = [list(map(float, l.split()[1:4])) for l in open(path) if l.startswith('v ')]
    p = [proj(-a, b, c) for a, b, c in v]
    xs, ys = [q[0] for q in p], [q[1] for q in p]
    return [round(min(xs), 1), round(min(ys), 1), round(max(xs) - min(xs), 1), round(max(ys) - min(ys), 1)]


def build(level8, boards):
    n = scene(level8)
    L = {}
    plane = 1.14
    L['boardHalf'] = {'1': [*map(lambda v: round(v, 1), proj(-160, 3, plane)), 0, 0],
                      '2': [*map(lambda v: round(v, 1), proj(-160, 95, plane)), 0, 0]}
    for side, (top, bottom) in (('1', (3, -95)), ('2', (95, -3))):
        a, b = proj(-160, top, plane), proj(124, bottom, plane)
        L['boardHalf'][side] = [round(a[0], 1), round(a[1], 1), round(b[0] - a[0], 1), round(b[1] - a[1], 1)]
    L['rows'] = {}
    for side, name in (('1', 'BotSide'), ('2', 'TopSide')):
        for zone, row in ((1, 'Melee'), (2, 'Ranged'), (4, 'Siege')):
            L['rows'][side + ':' + str(zone)] = collider_rect(n, f'Board/{name}/{row}')
    L['rowScore'], L['crownHalf'], L['score'], L['handCounter'], L['handCount'] = {}, {}, {}, {}, {}
    L['deck'], L['grave'], L['leader'], L['hand'], L['presentation'] = {}, {}, {}, {}, {}
    for side, name, ui in (('1', 'BotSide', 'UIBot'), ('2', 'TopSide', 'UITop')):
        for zone, row in ((1, 'Melee'), (2, 'Ranged'), (4, 'Siege')):
            L['rowScore'][side + ':' + str(zone)] = ui_rect(n, f'Board/{name}/{ui}/LocationScores/{row}Score')
        for half in (1, 2):
            L['crownHalf'][side + ':' + str(half)] = ui_rect(n, f'Board/{name}/{ui}/PlayerRibbon/CrownsView/CrownHalf{half}')
        L['score'][side] = ui_rect(n, f'Board/{name}/{ui}/PlayerRibbon/PlayerScore')
        L['handCounter'][side] = ui_rect(n, f'Board/{name}/{ui}/Counters/HandCounter/HandIcon')
        L['handCount'][side] = ui_rect(n, f'Board/{name}/{ui}/Counters/HandCounter/HandIcon/HandCount')
        L['deck'][side] = collider_rect(n, f'Board/{name}/Deck')
        L['grave'][side] = collider_rect(n, f'Board/{name}/Graveyard')
        L['leader'][side] = collider_rect(n, f'Board/{name}/Leader')
        L['hand'][side] = collider_rect(n, f'Board/{name}/Hand')
        pv = n[f'Board/{name}/PresentationView/CardView/Cube']
        L['presentation'][side] = rect_at(*pv['world'], pv['scale'][0], pv['scale'][1])
    coin = n['CoinRoot/Scaler/Scalar2/TurnCoin/CoinRoot/CoinMain/CoinWobble/CoinRoll/Rot/CoinTop/Coin']
    # CoinBase mesh radius 12.21 (sharedassets8 Mesh 809), rotated to face the camera.
    L['coin'] = rect_at(*coin['world'], 24.42, 24.42 * 131.3 / 135.8)
    pb = n['Board/UIOnBoard/TurnInfo/PassButton']
    L['passButton'] = rect_at(*pb['world'], pb['size'][0] * pb['scale'][0], pb['size'][1] * pb['scale'][1])
    L['ribbon'] = {}
    order = ['Mon', 'Nil', 'Nor', 'Sco', 'Ske']
    for index, short in enumerate(order):
        for side, suffix in (('1', 'Bottom'), ('2', 'Top')):
            path = glob.glob(str(Path(boards) / str(index + 1) / f'*BoardRibbon_{suffix}_{short}.obj'))[0]
            L['ribbon'][f'{index}:{side}'] = obj_rect(path)
    return L


def emit_as(L):
    def arr(v): return '[' + ','.join(str(x) for x in v) + ']'
    def obj(d): return '{' + ','.join(f'"{k}":{arr(v)}' for k, v in sorted(d.items())) + '}'
    lines = ['package {', '    // GENERATED by tools/ui/extract_beta_layout103.py from Gwent Beta 0.9.24 level8.',
             '    // Original perspective camera projected to 1920x1080. Values: [x, y, width, height].',
             '    public class BetaGwentBoardLayout {']
    for key in ('boardHalf', 'rows', 'rowScore', 'crownHalf', 'score', 'handCounter', 'handCount', 'deck', 'grave',
                'leader', 'hand', 'presentation', 'ribbon'):
        lines.append(f'        public static const {key.upper() if key in ("deck","hand","grave") else key}:Object={obj(L[key])};')
    lines.append(f'        public static const coin:Array={arr(L["coin"])};')
    lines.append(f'        public static const passButton:Array={arr(L["passButton"])};')
    lines.append('        public static function rect(table:Object,key:String):Array { return table[key] as Array; }')
    lines += ['    }', '}', '']
    return '\n'.join(lines).replace('public static const DECK', 'public static const deck').replace(
        'public static const HAND', 'public static const hand').replace('public static const GRAVE', 'public static const grave')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--level8', type=Path, default=ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/level8')
    ap.add_argument('--boards', type=Path, default=ROOT / 'BetaGwent/build/beta-presentation91/boards/halfs/factions')
    ap.add_argument('--out', type=Path, default=ROOT / 'BetaGwent/ui/src/BetaGwentBoardLayout.as')
    ap.add_argument('--evidence', type=Path, default=ROOT / 'docs/evidence/beta-layout103.json')
    a = ap.parse_args()
    vendor = ROOT / 'tools/vendor/audio-python'
    if vendor.exists() and os.name == 'nt':
        sys.path.insert(0, str(vendor))
    L = build(a.level8, a.boards)
    a.out.write_text(emit_as(L), 'utf8')
    digest = hashlib.sha256(a.level8.read_bytes()).hexdigest()
    a.evidence.write_text(json.dumps(dict(stage=103, camera=dict(position=[0, 0, CAM_Z], fov=FOV), screen=[W, H],
        source=dict(level8=str(a.level8), sha256=digest), layout=L, generated=str(a.out)), indent=1) + '\n', 'utf8')
    print('Wrote', a.out)

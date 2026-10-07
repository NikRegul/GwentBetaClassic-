"""Inventory the original Gwent Beta 0.9.24 GUI (read-only).

For each prefab bundle: full GameObject hierarchy with RectTransform anchors,
pivot, size, scale, active state, component classes (MonoScript names), Image
sprite names and default texts -> BetaGwent/build/beta-ui103/prefabs/<b>.json
and docs/beta-ui/<b>.tree.txt (readable). For each sprite atlas: sprite index
(name, rect, pivot, border/9-slice) and, with --sprites, PNG export to
BetaGwent/build/beta-ui103/sprites/<atlas>/<name>.png.

Linux shell: PYTHONPATH=tools/vendor/unitypy-portable. Windows: tools/vendor/audio-python.
"""
from pathlib import Path
import argparse, hashlib, json, os, re, sys

ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui'
PREFABS = ['game_base', 'deckbuilder_base', 'matchsetup', 'global_base', 'loading_base']
ATLASES = ['uber/panels', 'uber/shared', 'uber/deckbuilder', 'uber/cardmanagement', 'uber/borders', 'uber/banners',
           'uber/factionpreview', 'uber/combatloadingscreen', 'uber/bgsetupsingleplayer', 'uber/cardslotleaders',
           'uber/cardslotneu', 'uber/cardslotmon', 'uber/cardslotnil', 'uber/cardslotnor', 'uber/cardslotsco', 'uber/cardslotske',
           # stage 104: battle screen, intro, mulligan, deck picker
           'uber/avatars', 'uber/board', 'uber/buttons', 'uber/gamepanels', 'uber/yourturnpanel', 'uber/sidepreview',
           'uber/cardpicker', 'uber/endgamescreen', 'uber/inputbutton_pc', 'uber/inputbutton_xbox', 'uber/dialogs',
           'uber/popups', 'uber/menu', 'uber/deckpicker', 'uber/matchsetup', 'uber/woodenbackground', 'uber/turnhistory',
           'uber/cardrendering', 'uber/generalgradients', 'uber/characters', 'uber/factionbgspreview', 'uber/masks',
           'uber/factioniconsmedium', 'uber/factioniconssmall', 'uber/filterbuttons', 'uber/collection', 'uber/cardnotification',
           'uber/taunts', 'uber/gamebackgrounds', 'uber/loadingscreenbackgrounds', 'uber/socialfeatures', 'uber/history']


def r2(v):
    return None if v is None else [round(v[k], 2) for k in ('x', 'y')]


def prefab(path):
    import UnityPy
    env = UnityPy.load(str(path))
    objs = {o.path_id: o for o in env.objects}
    cache = {}

    def td(pid):
        if pid not in cache:
            try:
                cache[pid] = objs[pid].read_typetree()
            except Exception as exc:
                cache[pid] = {'_error': str(exc)}
        return cache[pid]
    scripts = {o.path_id: td(o.path_id).get('m_ClassName') for o in env.objects if o.type.name == 'MonoScript'}
    sprites = {o.path_id: td(o.path_id).get('m_Name') for o in env.objects if o.type.name == 'Sprite'}
    nodes, transforms = {}, {}
    for o in env.objects:
        if o.type.name != 'GameObject':
            continue
        d = td(o.path_id)
        node = dict(name=d.get('m_Name'), active=bool(d.get('m_IsActive')), components=[])
        for c in d.get('m_Component', []):
            ptr = c.get('component', c.get('second'))
            pid, fid = ptr['m_PathID'], ptr['m_FileID']
            if fid != 0 or pid not in objs:
                node['components'].append({'type': 'external'}); continue
            kind = objs[pid].type.name
            entry = {'type': kind}
            if kind in ('RectTransform', 'Transform'):
                t = td(pid); transforms[pid] = (o.path_id, t)
                node['transform'] = pid
                entry.update(position=[round(t['m_LocalPosition'][k], 2) for k in 'xyz'],
                             scale=[round(t['m_LocalScale'][k], 3) for k in 'xyz'],
                             rotation=[round(t['m_LocalRotation'][k], 4) for k in 'xyzw'])
                if kind == 'RectTransform':
                    entry.update(anchorMin=r2(t['m_AnchorMin']), anchorMax=r2(t['m_AnchorMax']), anchoredPosition=r2(t['m_AnchoredPosition']),
                                 sizeDelta=r2(t['m_SizeDelta']), pivot=r2(t['m_Pivot']))
            elif kind == 'MonoBehaviour':
                m = td(pid)
                entry['class'] = scripts.get(m.get('m_Script', {}).get('m_PathID'), '?')
                entry['enabled'] = bool(m.get('m_Enabled', 1))
                sp = m.get('m_Sprite')
                if isinstance(sp, dict) and sp.get('m_PathID'):
                    entry['sprite'] = sprites.get(sp['m_PathID'], str(sp['m_PathID']))
                    entry['imageType'] = m.get('m_Type'); entry['color'] = m.get('m_Color')
                if isinstance(m.get('m_text'), str): entry['text'] = m['m_text'][:200]
                if isinstance(m.get('m_Text'), str): entry['text'] = m['m_Text'][:200]
                for key in ('m_fontSize', 'm_FontData'):
                    if key in m and isinstance(m[key], (int, float)): entry['fontSize'] = m[key]
                if 'm_ReferenceResolution' in m: entry['referenceResolution'] = r2(m['m_ReferenceResolution'])
            node['components'].append(entry)
        nodes[o.path_id] = node
    children = {}
    roots = []
    for gid, node in nodes.items():
        pid = node.get('transform')
        if pid is None:
            continue
        father = transforms[pid][1]['m_Father']['m_PathID']
        if father in transforms:
            children.setdefault(transforms[father][0], []).append((transforms[pid][1], gid))
        else:
            roots.append(gid)
    # Keep the serialized child order (sibling order defines draw order in uGUI).
    order = {}
    for pid, (gid, t) in transforms.items():
        order[gid] = [transforms[c['m_PathID']][0] for c in t['m_Children'] if c['m_PathID'] in transforms]

    def build(gid):
        n = dict(nodes[gid]); n.pop('transform', None)
        n['children'] = [build(c) for c in order.get(gid, [])]
        return n
    return [build(r) for r in sorted(roots, key=lambda g: nodes[g]['name'] or '')]


def tree_text(roots):
    out = []

    def walk(n, depth):
        rt = next((c for c in n['components'] if c['type'] in ('RectTransform', 'Transform')), {})
        parts = []
        if 'anchoredPosition' in rt:
            parts.append(f"ap={rt['anchoredPosition']} size={rt['sizeDelta']} amin={rt['anchorMin']} amax={rt['anchorMax']} pivot={rt['pivot']}")
        if rt.get('scale') and rt['scale'] != [1, 1, 1]: parts.append(f"scale={rt['scale']}")
        for c in n['components']:
            if c['type'] == 'MonoBehaviour' and c.get('class') not in (None, '?'):
                s = c['class']
                if 'sprite' in c: s += f"[{c['sprite']}]"
                if c.get('text'): s += '"' + c['text'].replace('\n', ' ')[:40] + '"'
                parts.append(s)
        out.append('  ' * depth + (n['name'] or '?') + ('' if n['active'] else ' (off)') + ' ' + ' '.join(parts))
        for ch in n['children']:
            walk(ch, depth + 1)
    for r in roots:
        walk(r, 0)
    return '\n'.join(out) + '\n'


def atlas(path, export_dir=None):
    import UnityPy
    env = UnityPy.load(str(path))
    index = []
    for o in env.objects:
        if o.type.name != 'Sprite':
            continue
        d = o.read_typetree()
        rec = dict(name=d['m_Name'], rect=[round(d['m_Rect'][k], 1) for k in ('x', 'y', 'width', 'height')],
                   pivot=r2(d.get('m_Pivot')), border=[round(d['m_Border'][k], 1) for k in ('x', 'y', 'z', 'w')] if 'm_Border' in d else None,
                   pixelsToUnits=d.get('m_PixelsToUnits'), pathId=o.path_id)
        if export_dir:
            try:
                image = o.read().image
                safe = re.sub(r'[^0-9A-Za-z_.\-]+', '_', d['m_Name'])
                target = export_dir / (safe + '.png'); image.save(target); rec['png'] = target.name
            except Exception as exc:
                rec['exportError'] = str(exc)[:200]
        index.append(rec)
    return sorted(index, key=lambda r: r['name'])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--gui', type=Path, default=GUI)
    ap.add_argument('--out', type=Path, default=ROOT / 'BetaGwent/build/beta-ui103')
    ap.add_argument('--docs', type=Path, default=ROOT / 'docs/beta-ui')
    ap.add_argument('--sprites', action='store_true')
    ap.add_argument('--only', nargs='*')
    a = ap.parse_args()
    if os.name == 'nt':
        sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
    (a.out / 'prefabs').mkdir(parents=True, exist_ok=True); a.docs.mkdir(parents=True, exist_ok=True)
    manifest = dict(stage=103, prefabs={}, atlases={})
    for name in PREFABS:
        if a.only and name not in a.only: continue
        src = a.gui / 'prefabs' / name
        roots = prefab(src)
        (a.out / 'prefabs' / (name + '.json')).write_text(json.dumps(roots, ensure_ascii=False) + '\n', 'utf8')
        (a.docs / (name + '.tree.txt')).write_text(tree_text(roots), 'utf8')
        count = sum(1 for _ in re.finditer('"name"', json.dumps(roots)))
        manifest['prefabs'][name] = dict(source=str(src), sha256=hashlib.sha256(src.read_bytes()).hexdigest(), roots=[r['name'] for r in roots], objects=count)
        print('prefab', name, len(roots), 'roots', count, 'objects', flush=True)
    for name in ATLASES:
        if a.only and name not in a.only: continue
        src = a.gui / 'spriteatlases' / name
        target = a.out / 'sprites' / name.replace('/', '_') if a.sprites else None
        if target: target.mkdir(parents=True, exist_ok=True)
        index = atlas(src, target)
        (a.out / ('atlas_' + name.replace('/', '_') + '.json')).write_text(json.dumps(index, ensure_ascii=False, indent=0) + '\n', 'utf8')
        manifest['atlases'][name] = dict(source=str(src), sha256=hashlib.sha256(src.read_bytes()).hexdigest(), sprites=len(index),
                                         exported=sum(1 for r in index if 'png' in r), errors=sum(1 for r in index if 'exportError' in r))
        print('atlas', name, len(index), 'sprites', flush=True)
    evidence = ROOT / 'docs/evidence/beta-ui103.json'
    if evidence.exists():
        previous = json.loads(evidence.read_text('utf8'))
        for key in ('prefabs', 'atlases'):
            previous.get(key, {}).update(manifest[key]); manifest[key] = previous.get(key, manifest[key])
    evidence.write_text(json.dumps(manifest, indent=1) + '\n', 'utf8')


if __name__ == '__main__':
    main()

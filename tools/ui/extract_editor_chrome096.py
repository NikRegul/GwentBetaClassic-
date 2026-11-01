"""Export the Beta 0.9.24 deck-builder chrome sprites used by stage 096.

Read-only on the Beta install. Writes BetaGwent/ui/assets/editor096/<name>.png
plus sources.json (atlas, sprite name, rect, sha256 of the bundle).
Linux shell: PYTHONPATH=tools/vendor/unitypy-portable. Windows: tools/vendor/audio-python.
"""
from pathlib import Path
import hashlib, json, os, sys
ROOT = Path(__file__).resolve().parents[2]
GUI = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/AssetBundles/gui/spriteatlases/uber'
WANT = {
    'deckbuilder': ['db_filter_reset', 'db_filter_new_all', 'db_filter_new_new', 'db_filter_sort_asc', 'db_filter_sort_desc',
                    'db_filter_owned_all_icon', 'db_filter_owned_owned', 'db_filter_owned_unowned', 'db_filter_faction_all_icon'],
    'panels': ['symbol_scraps', 'symbol_barrels'],
    'buttons': ['btn_square_idle', 'btn_square_toggle_frame', 'btn_square_hovered'],
    'shared': ['textsearch_icon'],
}


def main():
    if os.name == 'nt': sys.path.insert(0, str(ROOT / 'tools/vendor/audio-python'))
    import UnityPy
    out = ROOT / 'BetaGwent/ui/assets/editor096'; out.mkdir(parents=True, exist_ok=True)
    index = out / 'sources.json'
    sources = json.loads(index.read_text('utf8')) if index.exists() else {}
    only = sys.argv[1:] or list(WANT)  # one atlas per call keeps each run short
    for atlas, names in WANT.items():
        if atlas not in only: continue
        bundle = GUI / atlas
        env = UnityPy.load(str(bundle))
        for o in env.objects:
            if o.type.name != 'Sprite': continue
            d = o.read_typetree()
            if d['m_Name'] not in names: continue
            target = out / (d['m_Name'] + '.png'); o.read().image.save(target)
            sources[d['m_Name']] = dict(atlas='uber/' + atlas, rect=[round(d['m_Rect'][k], 1) for k in ('x', 'y', 'width', 'height')],
                                        bundleSha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
                                        pngSha256=hashlib.sha256(target.read_bytes()).hexdigest())
        missing = set(names) - set(sources)
        assert not missing, (atlas, missing)
    index.write_text(json.dumps(sources, indent=1, sort_keys=True) + '\n', 'utf8')
    print(len(sources), 'sprites ->', out)


if __name__ == '__main__': main()

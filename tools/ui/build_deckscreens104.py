"""Pack Gwent Beta 0.9.24 deck-screen sprites (match setup, deck picker, deck builder).

Page 17: every card slot strip (gui/spriteatlases/uber/cardslot*: <ArtId*10>_slot,
512x64 -> 224x28; leaders 512x128 -> 320x80), bound to template ids through
Templates ArtId. Page 18: UIMatchSetupPrefab / DeckPickerPrefab / UIDBPrefab chrome.
Generates BetaGwentDeckArt104.as (templateId -> slot id table + chrome ids).
"""
from pathlib import Path
import glob, hashlib, json, os, re, sys
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_hud104 import Packer, sprite, fit, nine, ROOT, SPR

FACTIONS = ['mon', 'nil', 'nor', 'sco', 'ske']


def main():
    dry = '--dry' in sys.argv
    srcdir = Path(sys.argv[sys.argv.index('--src') + 1]) if '--src' in sys.argv else ROOT / 'BetaGwent/ui/src'
    catalog = json.loads((ROOT / 'data/beta924/normalized/catalog.json').read_text('utf8'))
    by_art = {}
    for t in catalog['templates']:
        a = t['art'].get('ArtId')
        if a and a != '0': by_art.setdefault(str(int(a) * 10), []).append(int(t['attributes']['Id']))
    p17 = Packer(2048, 2048); table = {}
    leaders = sorted(glob.glob(str(SPR / 'uber_cardslotleaders' / '*_slot.png')))
    slots = sorted(p for p in glob.glob(str(SPR / 'uber_cardslot*' / '*_slot.png')) if 'leaders' not in p)
    ident = -3000
    for path in leaders + slots:
        name = os.path.basename(path)[:-9]
        if name not in by_art: continue
        leader = 'leaders' in path
        im = Image.open(path).convert('RGBA')
        p17.add(ident, fit(im, 288, 72) if leader else fit(im, 192, 24), os.path.relpath(path, SPR))
        for tid in by_art[name]: table[tid] = ident
        ident -= 1
    # Opaque full-screen backgrounds share the opaque (DXT1) slot page.
    p17.x = 0; p17.y += p17.row + 2; p17.row = 0
    p17.add(-3700, fit(sprite('bgsetupsingleplayer', 'BGSetupPractice').convert('RGB').convert('RGBA'), 960, 540), 'bgsetupsingleplayer/BGSetupPractice')
    p17.add(-3701, fit(sprite('deckbuilder', 'db_background').convert('RGB').convert('RGBA'), 960, 540), 'deckbuilder/db_background')
    for v in p17.slots.values(): v[0] = 17
    p18 = Packer(1024, 2048)
    chrome = [
        (-3702, 'matchsetup', 'ms_banner', (470, 114)),
        (-3703, 'matchsetup', 'ms_button_BG', (415, 151)),
        (-3704, 'matchsetup', 'ms_button_nornal', (256, 60)),
        (-3705, 'matchsetup', 'ms_button_rollover', (256, 60)),
        (-3706, 'matchsetup', 'ms_deck_name_bg', (358, 61)),
        (-3707, 'matchsetup', 'ms_heraldic_corners', (144, 176)),
        (-3709, 'deckpicker', 'dp_slot_gold', (341, 42)),
        (-3710, 'deckpicker', 'dp_slot_silver', (341, 42)),
        (-3711, 'deckpicker', 'dp_slot_bronze', (341, 42)),
        (-3712, 'deckpicker', 'dp_slot_copies_bg', (40, 40)),
        (-3713, 'deckpicker', 'dp_slot_diamond_bg', (64, 64)),
        (-3714, 'deckpicker', 'dp_icon_crown', (32, 32)),
        (-3715, 'deckpicker', 'dp_icon_valid', (48, 64)),
        (-3716, 'deckpicker', 'dp_icon_invalid', (48, 64)),
        (-3717, 'deckpicker', 'dp_icon_newdeck', (38, 38)),
        (-3718, 'deckpicker', 'dp_newdeck_bg', (333, 62)),
        (-3719, 'deckpicker', 'dp_stats_gold_bg', (54, 64)),
        (-3720, 'deckpicker', 'dp_stats_silver_bg', (54, 64)),
        (-3721, 'deckpicker', 'dp_stats_bronze_bg', (54, 64)),
        (-3722, 'deckpicker', 'dp_slot_gradient_bg', (320, 4)),
        (-3723, 'deckpicker', 'dp_icon_special_gold', (32, 32)),
        (-3724, 'deckpicker', 'dp_icon_special_silver', (32, 32)),
        (-3725, 'deckpicker', 'dp_icon_special_bronze', (32, 32)),
        (-3726, 'deckpicker', 'dp_top_bar_gradient', (512, 60)),
        (-3727, 'deckpicker', 'dp_bottom_bar_gradient', (512, 60)),
        (-3728, 'deckbuilder', 'db_card_copies_bg', (64, 64)),
        (-3730, 'shared', 'woodpanel_large_bg', (512, 428)),
        (-3731, 'shared', 'textsearch_idle', (64, 64)),
    ]
    for i, f in enumerate(FACTIONS):
        chrome += [(-3740 - i, 'deckpicker', 'dp_ornament_%s_bg' % f, (92, 90)), (-3745 - i, 'deckpicker', 'dp_stats_%s_bg' % f, (393, 120))]
    for i, f in enumerate(['mon', 'nil', 'nor', 'sco', 'ske', 'neu']):
        chrome += [(-3750 - i, 'filterbuttons', 'db_filter_faction_%s_icon' % f, (50, 50))]
    chrome += [(-3756, 'filterbuttons', 'db_filter_tier_bronze', (48, 48)), (-3757, 'filterbuttons', 'db_filter_tier_silver', (48, 48)),
               (-3758, 'filterbuttons', 'db_filter_tier_gold', (48, 48)), (-3759, 'deckbuilder', 'db_filter_tier_all', (48, 48)),
               (-3760, 'buttons', 'btn_filter_idle', (66, 56)), (-3761, 'buttons', 'btn_filter_toggle_frame', (66, 56))]
    frame = sprite('matchsetup', 'ms_large_image_frame')
    p18.add(-3708, fit(frame, 331, 238), 'matchsetup/ms_large_image_frame (drawn 9-sliced)')
    chrome.sort(key=lambda c: -c[3][1])
    for ident, atlas, name, size in chrome:
        try: im = sprite(atlas, name)
        except FileNotFoundError: print('missing', atlas, name); continue
        p18.add(ident, fit(im, *size), atlas + '/' + name)
    for v in p18.slots.values(): v[0] = 18
    if dry:
        print('dry run: page 17', len(p17.records), 'h', p17.y + p17.row, '; page 18', len(p18.records), 'h', p18.y + p18.row); return
    out17 = ROOT / 'BetaGwent/ui/assets/battle104/cardslots104.png'; p17.used().convert('RGB').save(out17)
    out18 = ROOT / 'BetaGwent/ui/assets/battle104/deckscreens104.png'; p18.used().save(out18)
    src = srcdir / 'BetaGwentHDArt.as'; raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw; text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text)
    binding = {k: v for k, v in json.loads(m[1]).items() if v[0] not in (17, 18)}
    binding.update(p17.slots); binding.update(p18.slots)
    text = text[:m.start(1)] + json.dumps(binding, separators=(',', ':')) + text[m.end(1):]
    for n, f in ((17, 'cardslots104.png'), (18, 'deckscreens104.png')):
        if 'private static var Page%d:Class' % n not in text:
            text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle104/%s",compression="true",quality="100")] private static var Page%d:Class;\n private static var types:Array=' % (f, n))
            text = text.replace('Page%d];' % (n - 1), 'Page%d,Page%d];' % (n - 1, n))
    if 'Page17,Page18' not in text: raise SystemExit('BetaGwentHDArt.as layout changed')
    src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + (text.replace('\n', '\r\n') if crlf else text).encode('utf8'))
    pairs = ','.join('%d:%d' % (k, v) for k, v in sorted(table.items()))
    (srcdir / 'BetaGwentDeckArt104.as').write_text('''package {
    // GENERATED by tools/ui/build_deckscreens104.py: Beta deck-screen sprites (pages 17-18).
    public class BetaGwentDeckArt104 {
        private static const SLOTS:Object={%s};
        public static function slot(templateId:int):int{return SLOTS[templateId]!=null?int(SLOTS[templateId]):0;}
        public static const BG_SETUP:int=-3700,BG_BUILDER:int=-3701,MS_BANNER:int=-3702,MS_BUTTON_BG:int=-3703,MS_BUTTON:int=-3704,
            MS_BUTTON_HOVER:int=-3705,MS_NAME_BG:int=-3706,MS_CORNERS:int=-3707,MS_FRAME:int=-3708,
            DP_GOLD:int=-3709,DP_SILVER:int=-3710,DP_BRONZE:int=-3711,DP_COPIES:int=-3712,DP_DIAMOND:int=-3713,DP_CROWN:int=-3714,
            DP_VALID:int=-3715,DP_INVALID:int=-3716,DP_NEWDECK_ICON:int=-3717,DP_NEWDECK:int=-3718,DP_STAT_GOLD:int=-3719,
            DP_STAT_SILVER:int=-3720,DP_STAT_BRONZE:int=-3721,DP_GRADIENT:int=-3722,DP_SPECIAL_GOLD:int=-3723,DP_SPECIAL_SILVER:int=-3724,
            DP_SPECIAL_BRONZE:int=-3725,DP_TOP_SHADE:int=-3726,DP_BOTTOM_SHADE:int=-3727,DB_COPIES:int=-3728,PAPER:int=-3729,WOOD_LARGE:int=-3730,
            SEARCH:int=-3731,TIER_BRONZE:int=-3756,TIER_SILVER:int=-3757,TIER_GOLD:int=-3758,TIER_ALL:int=-3759,FILTER_BTN:int=-3760,FILTER_ON:int=-3761;
        public static function ornament(faction:int):int{return -3740-Math.max(0,Math.min(4,faction));}
        public static function stats(faction:int):int{return -3745-Math.max(0,Math.min(4,faction));}
        public static function factionFilter(faction:int):int{return -3750-Math.max(0,Math.min(5,faction));}
    }
}
''' % pairs, 'utf8')
    (ROOT / 'docs/evidence/beta-deckscreens104.json').write_text(json.dumps(dict(stage=104, pages={'17': str(out17), '18': str(out18)},
        sha256={'17': hashlib.sha256(out17.read_bytes()).hexdigest(), '18': hashlib.sha256(out18.read_bytes()).hexdigest()},
        slotTemplates=len(table), sprites=p17.records + p18.records), indent=1) + '\n', 'utf8')
    print('page 17:', len(p17.records), 'slots /', len(table), 'templates; page 18:', len(p18.records), 'chrome; heights', p17.y + p17.row, p18.y + p18.row)


if __name__ == '__main__':
    main()

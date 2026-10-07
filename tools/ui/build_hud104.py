"""Pack the original Gwent Beta 0.9.24 battle HUD sprites into art page 15.

Sources (read-only): sprites exported by tools/recon/extract_beta_ui103.py --sprites
into BetaGwent/build/beta-ui103/sprites/<atlas>/<name>.png (uber quality atlases of
gui/spriteatlases) plus Neutral_SmallCardMesh_CardBack from sharedassets8.assets
(cached in BetaGwent/build/stage104/cardback650.png).
Writes BetaGwent/ui/assets/battle104/hud104.png, registers ids -1700..-1899 on page 15
in BetaGwentHDArt.as and generates BetaGwentHud104.as (id tables for the board).
"""
from pathlib import Path
import hashlib, json, re
from PIL import Image, ImageFilter, ImageOps
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / 'BetaGwent/build/beta-ui103/sprites'
FACTIONS = ['MON', 'NIL', 'NOR', 'SCO', 'SKE', 'NEU']          # editorFactionIndex order 0..5
LEADER_AVATAR = {131101: 'avatar-eredin', 200055: 'avatar-FTUX-unseen_elder', 200158: 'avatar-dagon', 200159: 'avatar-bran',
                 200160: 'avatar-FTUX-crach', 200161: 'avatar-FTUX-harald', 200162: 'avatar-FTUX-emhyr', 200163: 'avatar-NIL',
                 200164: 'avatar-FTUX-calveit', 200165: 'avatar-francesca', 200166: 'avatar-FTUX-eithne', 200167: 'avatar-brouver_hoog',
                 200168: 'avatar-foltest', 200169: 'avatar-FTUX-radovid', 200170: 'avatar-FTUX-henselt', 201580: 'avatar-NIL',
                 201587: 'avatar-MON', 201589: 'avatar-SCO', 201595: 'avatar-NOR', 201597: 'avatar-SKE', 201743: 'avatar-MON'}
FACTION_AVATAR = ['avatar-MON', 'avatar-NIL', 'avatar-NOR', 'avatar-SCO', 'avatar-SKE', 'avatar-default']
TITLE_BG = dict(MON='side_preview_title_bg_MON', NIL='side_preview_title_bg_NIL', NOR='side_preview_title_bg_NR',
                SCO='side_preview_title_bg_SCO', SKE='side_preview_title_bg_SKE', NEU='side_preview_title_bg_NEU')
INFO_BG = dict(MON='side_preview_info_bg_MON', NIL='side_preview_info_title_bg_NIL_GENERAL', NOR='side_preview_info_bg_NR',
               SCO='side_preview_info_bg_SCO', SKE='side_preview_info_bg_SKE', NEU='side_preview_info_bg_NEU')
LINE = dict(MON='metal_title_line_MON_SKE', SKE='metal_title_line_MON_SKE', NOR='metal_title_line_NOR_NIL_SCO',
            NIL='metal_title_line_NOR_NIL_SCO', SCO='metal_title_line_NOR_NIL_SCO', NEU='general_metal_title_line')
# Default card-back tints (no faction card-back bundle ships with the offline beta client).
BACK_TINT = dict(MON=(122, 36, 30), NIL=(34, 34, 36), NOR=(28, 86, 118), SCO=(52, 86, 38), SKE=(70, 50, 96), NEU=None)
INPUTS = ['keycode_LC', 'keycode_RC', 'input_xbox_v2_A', 'input_xbox_v2_B', 'input_xbox_v2_X', 'input_xbox_v2_Y',
          'input_xbox_v2_LBumper', 'input_xbox_v2_RBumper', 'input_xbox_v2_LTrigger', 'input_xbox_v2_RTrigger',
          'input_xbox_v2_Back', 'input_xbox_v2_Start', 'input_xbox_v2_RStick']


def sprite(atlas, name):
    return Image.open(SPR / ('uber_' + atlas) / (name + '.png')).convert('RGBA')


def fit(im, w, h):
    return im.resize((w, h), Image.Resampling.LANCZOS)


def nine(im, border, w, h):
    """Unity 9-slice (border = left, bottom, right, top in source px) at scale s."""
    l, b, r, t = [int(v) for v in border]
    W, H = im.size; out = Image.new('RGBA', (w, h))
    s = min(1.0, h / H * 1.0)
    L, R, T, B = [max(1, round(v * s)) for v in (l, r, t, b)]
    xs = [(0, l, 0, L), (l, W - r, L, w - R), (W - r, W, w - R, w)]
    ys = [(0, t, 0, T), (t, H - b, T, h - B), (H - b, H, h - B, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(im.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.Resampling.LANCZOS), (dx0, dy0))
    return out


def clean_back(base):
    """Neutral back face with the whole interior replaced by a plain stained field.

    Only the outer gold frame and the inner black rule of Neutral_SmallCardMesh_CardBack
    are kept; the interior is a seeded multi-scale noise field matched to the mean
    tone of the original parchment (no emblem, outline or band seams can remain).
    """
    a = np.asarray(base.convert('RGBA')).astype(np.float32)
    x0, x1, y0, y1 = 54, 366, 54, 462            # inside the inner black rule (512px texture)
    w, h = x1 - x0, y1 - y0
    rng = np.random.default_rng(924)
    field = np.zeros((h, w), np.float32)
    for cells, weight in ((4, .5), (9, .3), (22, .14), (60, .06)):
        small = rng.random((cells, max(2, int(cells * w / h)))).astype(np.float32)
        field += weight * np.asarray(Image.fromarray(small).resize((w, h), Image.Resampling.BICUBIC))
    field = (field - field.mean()) / (field.std() + 1e-6)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    vignette = 0.72 + 0.28 * np.clip(edge / 26.0, 0, 1)
    ref = np.concatenate([a[62:100, x0:x1, :3].reshape(-1, 3), a[418:452, x0:x1, :3].reshape(-1, 3)])
    mean = ref.mean(0)
    lum = (1 + 0.11 * field) * vignette
    out = a.copy(); out[y0:y1, x0:x1, :3] = np.clip(mean[None, None, :] * lum[:, :, None], 0, 255)
    return Image.fromarray(out.astype(np.uint8), 'RGBA').crop((28, 28, 392, 488))


def faction_back(base, emblem, tint):
    """Clean back body recoloured to the faction tint with a gold faction emblem."""
    out = clean_back(base)
    a = np.asarray(out).astype(np.float32); h, w = a.shape[:2]
    if tint:
        yy, xx = np.mgrid[0:h, 0:w]
        inner = ((xx > 22) & (xx < w - 22) & (yy > 22) & (yy < h - 22)).astype(np.float32)
        k = np.asarray(Image.fromarray((inner * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[:, :, None] / 255
        lum = a[:, :, :3].mean(2, keepdims=True) / 110.0
        col = np.clip(np.array(tint, np.float32)[None, None, :] * lum, 0, 255)
        a[:, :, :3] = a[:, :, :3] * (1 - k) + col * k
        out = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
    if emblem is not None:
        e = emblem.convert('RGBA'); g = np.asarray(e).astype(np.float32)
        l2 = g[:, :, :3].mean(2, keepdims=True) / 255
        gold = np.concatenate([np.clip((l2 ** .7) * np.array([[[330, 255, 140]]]) + 40, 0, 255), g[:, :, 3:]], 2)
        e = Image.fromarray(gold.astype(np.uint8), 'RGBA')
        size = int(w * .52); e = e.resize((size, int(size * e.height / e.width)), Image.Resampling.LANCZOS)
        shadow = Image.new('RGBA', e.size, (0, 0, 0, 0)); shadow.putalpha(e.getchannel('A').filter(ImageFilter.GaussianBlur(4)))
        out.alpha_composite(shadow, ((w - e.width) // 2 + 2, (h - e.height) // 2 + 3))
        out.alpha_composite(e, ((w - e.width) // 2, (h - e.height) // 2))
    return out


class Packer:
    def __init__(self, w, h):
        self.page = Image.new('RGBA', (w, h)); self.x = self.y = self.row = 0; self.w = w; self.slots = {}; self.records = []

    def add(self, ident, im, label):
        if self.x + im.width > self.w: self.x = 0; self.y += self.row + 2; self.row = 0
        if self.y + im.height > self.page.height: raise SystemExit('page 15 overflow at ' + label)
        self.page.alpha_composite(im, (self.x, self.y)); self.slots[str(ident)] = [15, self.x, self.y, im.width, im.height]
        self.records.append(dict(id=ident, source=label, size=list(im.size))); self.x += im.width + 2; self.row = max(self.row, im.height)

    def used(self):
        """Page cropped to the used height (multiple of 4: GFx DDS export pads to mult4)."""
        h = (self.y + self.row + 3) // 4 * 4
        return self.page.crop((0, 0, self.page.width, max(4, h)))


def main():
    p = Packer(1024, 2048)
    avatars = ['avatar-geralt'] + sorted(set(LEADER_AVATAR.values()) | set(FACTION_AVATAR))
    for i, name in enumerate(avatars): p.add(-1700 - i, fit(sprite('avatars', name), 88, 88), name)
    p.x = 0; p.y += p.row + 2; p.row = 0
    for i, f in enumerate(FACTIONS): p.add(-1740 - i, fit(sprite('sidepreview', TITLE_BG[f]), 282, 86), TITLE_BG[f])
    for i, f in enumerate(FACTIONS): p.add(-1750 - i, fit(sprite('sidepreview', INFO_BG[f]), 282, 86), INFO_BG[f])
    for i, f in enumerate(FACTIONS):
        atlas = 'panels' if LINE[f] == 'general_metal_title_line' and not (SPR / 'uber_sidepreview' / (LINE[f] + '.png')).exists() else 'sidepreview'
        p.add(-1760 - i, fit(sprite(atlas, LINE[f]), 332, 6), LINE[f])
    p.add(-1730, fit(sprite('yourturnpanel', 'your_turn_banner_bg'), 512, 125), 'your_turn_banner_bg')
    p.add(-1731, fit(sprite('yourturnpanel', 'your_turn_banner_left'), 161, 84), 'your_turn_banner_left')
    p.add(-1732, fit(sprite('yourturnpanel', 'your_turn_banner_right'), 161, 84), 'your_turn_banner_right')
    p.add(-1733, fit(sprite('yourturnpanel', 'board-status-bg-shadow'), 512, 38), 'board-status-bg-shadow')
    p.add(-1770, fit(sprite('popups', 'popup_bg_title'), 600, 56), 'popup_bg_title')
    p.add(-1734, fit(sprite('sidepreview', 'side_preview_gradient'), 4, 64), 'side_preview_gradient')
    btn = json.loads((ROOT / 'BetaGwent/build/beta-ui103/atlas_uber_buttons.json').read_text('utf8'))
    border = {s['name']: s['border'] for s in btn}
    icon = fit(sprite('socialfeatures', 'menu_icon'), 46, 42)
    for i, state in enumerate(('btn_wide_idle_300', 'btn_wide_hovered_300')):
        b = nine(sprite('buttons', state), border[state], 156, 108); b.alpha_composite(icon, ((156 - 46) // 2, (108 - 42) // 2))
        p.add(-1780 - i, b, state + ' + menu_icon (UIBattlePrefab OpenWindowButton)')
    for i, state in enumerate(('btn_wide_idle_300', 'btn_wide_hovered_300')):
        p.add(-1782 - i, nine(sprite('buttons', state), border[state], 408, 64), state)
    for i, name in enumerate(INPUTS):
        p.add(-1790 - i, fit(sprite('inputbutton_pc' if name.startswith('keycode') else 'inputbutton_xbox', name), 48, 48), name)
    p.add(-1810, fit(sprite('cardrendering', 'shield_icon'), 59, 64), 'shield_icon')
    p.add(-1811, fit(sprite('cardrendering', 'timer_icon'), 46, 64), 'timer_icon')
    for i, name in enumerate(('big_crown_empty', 'big_crown_left_half_blue', 'big_crown_right_half_blue', 'big_crown_left_half_red', 'big_crown_right_half_red')):
        p.add(-1815 - i, fit(sprite('panels', name), 112, 112), name)
    for i, name in enumerate(('placeholder_arrow',)):
        p.add(-1825 - i, fit(sprite('panels', name), 39, 59), name)
    base = Image.open(ROOT / 'BetaGwent/build/stage104/cardback650.png').convert('RGBA')
    emblems = [Image.open(ROOT / 'BetaGwent/build/beta-ui103/emblems' / (f + '.png')) if (ROOT / 'BetaGwent/build/beta-ui103/emblems' / (f + '.png')).exists() else None for f in FACTIONS]
    page12 = Image.open(ROOT / 'BetaGwent/ui/assets/battle101/battle_widgets101.png').convert('RGBA')
    hd = (ROOT / 'BetaGwent/ui/src/BetaGwentHDArt.as').read_text('utf-8-sig')
    slots = json.loads(re.search(r'private static var slots:Object=(\{.*?\});', hd)[1])
    for i, f in enumerate(FACTIONS):
        em = None
        if i < 5:
            s = slots[str(-1501 - i)]; em = page12.crop((s[1], s[2], s[1] + s[3], s[2] + s[4]))
        back = faction_back(base, em, BACK_TINT[f]) if BACK_TINT[f] else base.crop((28, 28, 392, 488))
        p.add(-1830 - i, fit(back, 128, 171), 'Neutral_SmallCardMesh_CardBack recoloured ' + f)
    # Mulligan (UIBattleChoicePrefab / CardPicker): parchment, wooden side panel, empty preview slot, chain.
    shared = {s['name']: s for s in json.loads((ROOT / 'BetaGwent/build/beta-ui103/atlas_uber_cardpicker.json').read_text('utf8'))}
    p.x = 0; p.y += p.row + 2; p.row = 0
    p.add(-1850, nine(sprite('cardpicker', 'paperBG_slice'), shared['paperBG_slice']['border'], 1373, 765).resize((687, 383), Image.Resampling.LANCZOS), 'paperBG_slice 9-slice 1373x765 (half res)')
    p.add(-1851, fit(sprite('shared', 'woodpanel_small_bg'), 203, 411), 'woodpanel_small_bg')
    p.add(-1852, fit(sprite('shared', 'side_preview_slot'), 190, 266), 'side_preview_slot')
    p.add(-1853, fit(sprite('banners', 'silver_chain'), 22, 117), 'silver_chain')
    p.add(-1854, nine(sprite('panels', '9slice-tiny'), [30, 31, 30, 30], 700, 260).resize((350, 130), Image.Resampling.LANCZOS), '9slice-tiny 700x260 (half res)')
    out = ROOT / 'BetaGwent/ui/assets/battle104/hud104.png'; p.used().save(out)
    # Page 16: match intro (UIGameIntroRootPrefab): faction silhouettes + VS.
    p16 = Packer(1400, 1004); p16.slots = {}
    for i, f in enumerate(('monster', 'nilf', 'north', 'scoia', 'skel')):
        left = sprite('factionbgspreview', 'vs_%s_left_preview' % f); right = sprite('factionbgspreview', 'vs_%s_right_preview' % f)
        p16.add(-1870 - i, fit(left, round(left.width * 300 / left.height), 300), 'vs_%s_left_preview' % f)
        p16.add(-1875 - i, fit(right, round(right.width * 300 / right.height), 300), 'vs_%s_right_preview' % f)
    p16.add(-1880, sprite('panels', 'vs_image'), 'vs_image')
    for k, v in p16.slots.items(): v[0] = 16
    out16 = ROOT / 'BetaGwent/ui/assets/battle104/intro104.png'; p16.used().save(out16)
    p.slots.update(p16.slots); p.records += p16.records
    # Register page 15.
    src = ROOT / 'BetaGwent/ui/src/BetaGwentHDArt.as'; raw = src.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw; text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    m = re.search(r'private static var slots:Object=(\{.*?\});', text)
    binding = {k: v for k, v in json.loads(m[1]).items() if v[0] not in (15, 16)}; binding.update(p.slots)
    text = text[:m.start(1)] + json.dumps(binding, separators=(',', ':')) + text[m.end(1):]
    if 'private static var Page15:Class' not in text:
        text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle104/hud104.png",compression="true",quality="100")] private static var Page15:Class;\n private static var types:Array=')
        text = text.replace('Page13,Page14];', 'Page13,Page14,Page15];')
    if 'private static var Page16:Class' not in text:
        text = text.replace(' private static var types:Array=', ' [Embed(source="../assets/battle104/intro104.png",compression="true",quality="100")] private static var Page16:Class;\n private static var types:Array=')
        text = text.replace('Page14,Page15];', 'Page14,Page15,Page16];')
    if 'Page15,Page16' not in text: raise SystemExit('BetaGwentHDArt.as layout changed')
    src.write_bytes((b'\xef\xbb\xbf' if bom else b'') + (text.replace('\n', '\r\n') if crlf else text).encode('utf8'))
    leaders = ','.join('%d:%d' % (k, -1700 - avatars.index(v)) for k, v in sorted(LEADER_AVATAR.items()))
    factions = ','.join(str(-1700 - avatars.index(v)) for v in FACTION_AVATAR)
    (ROOT / 'BetaGwent/ui/src/BetaGwentHud104.as').write_text('''package {
    // GENERATED by tools/ui/build_hud104.py: original Gwent Beta HUD sprite ids (art page 15).
    public class BetaGwentHud104 {
        public static const PLAYER_AVATAR:int=-1700;
        private static const LEADER_AVATARS:Object={%s};
        private static const FACTION_AVATARS:Array=[%s];
        public static function avatar(leader:int,faction:int):int{return LEADER_AVATARS[leader]!=null?int(LEADER_AVATARS[leader]):int(FACTION_AVATARS[Math.max(0,Math.min(5,faction))]);}
        public static function titleBg(faction:int):int{return -1740-Math.max(0,Math.min(5,faction));}
        public static function infoBg(faction:int):int{return -1750-Math.max(0,Math.min(5,faction));}
        public static function titleLine(faction:int):int{return -1760-Math.max(0,Math.min(5,faction));}
        public static function cardBack(faction:int):int{return -1830-Math.max(0,Math.min(5,faction));}
        public static const TURN_BG:int=-1730,TURN_LEFT:int=-1731,TURN_RIGHT:int=-1732,STATUS_SHADOW:int=-1733,GRADIENT:int=-1734;
        public static const POPUP_TITLE:int=-1770,MENU_IDLE:int=-1780,MENU_HOVER:int=-1781,WIDE_IDLE:int=-1782,WIDE_HOVER:int=-1783;
        public static const KEY_LC:int=-1790,KEY_RC:int=-1791,PAD_A:int=-1792,PAD_B:int=-1793,PAD_X:int=-1794,PAD_Y:int=-1795,
            PAD_LB:int=-1796,PAD_RB:int=-1797,PAD_LT:int=-1798,PAD_RT:int=-1799,PAD_BACK:int=-1800,PAD_START:int=-1801,PAD_RS:int=-1802;
        public static const SHIELD:int=-1810,TIMER:int=-1811,CROWN_EMPTY:int=-1815,CROWN_LEFT_BLUE:int=-1816,CROWN_RIGHT_BLUE:int=-1817,
            CROWN_LEFT_RED:int=-1818,CROWN_RIGHT_RED:int=-1819,ROW_ARROW:int=-1825;
        public static function introLeft(faction:int):int{return -1870-Math.max(0,Math.min(4,faction));}
        public static function introRight(faction:int):int{return -1875-Math.max(0,Math.min(4,faction));}
        public static const VS:int=-1880;
        public static const PARCHMENT:int=-1850,WOOD_PANEL:int=-1851,PREVIEW_SLOT:int=-1852,CHAIN:int=-1853,POPUP:int=-1854;
    }
}
''' % (leaders, factions), 'utf8')
    (ROOT / 'docs/evidence/beta-hud104.json').write_text(json.dumps(dict(stage=104, page=15, atlas=str(out), size=list(Image.open(out).size),
        sha256=hashlib.sha256(out.read_bytes()).hexdigest(), sprites=p.records), indent=1) + '\n', 'utf8')
    print('page 15:', len(p.records), 'sprites, used height', p.y + p.row)


if __name__ == '__main__':
    main()

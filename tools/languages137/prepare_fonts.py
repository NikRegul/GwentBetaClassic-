"""Per-locale font files for the card texts of 13 languages (read-only for the live mod).

Writes BetaGwent/build/languages137/fonts/prepared/<locale>/ : subset font files that contain
exactly the needed code points (fonts/needed-codepoints.json), a preview PNG and plan.json.
Choice per locale follows the original Beta 0.9.24 font for that language:
  Latin/Cyrillic: HalisGR (titles) + PF Din Text Cond Pro (body), original TTFs;
  ru_ru: Beta HalisGR has no Cyrillic in the TTF, titles use PF Din Bold (as the mod today);
  jp_jp: Beta Mgen+ (built on Source Han Sans) -> Noto Sans CJK JP (same glyph design);
  kr_kr: Beta Iropke Batang (serif) -> Noto Serif CJK KR;
  zh_cn: Beta FZ Lanting Hei (commercial) -> Noto Sans CJK SC;
  zh_tw: Beta Noto Sans CJK TC -> the same font.
"""
from pathlib import Path
import json
from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'BetaGwent/build/languages137'
SRC = L / 'fonts/sources'
B, N = SRC / 'beta-ttf', SRC / 'noto-cjk'
LATIN = dict(title=B / 'HalisGR-Bold.ttf', titleMedium=B / 'HalisGR-Medium.ttf', body=B / 'PFDinTextCondPro-Regular.ttf', bodyBold=B / 'PFDinTextCondPro-Bold.ttf', bodyMedium=B / 'PFDinTextCondPro-Medium.ttf')
PLAN = {l: LATIN for l in ('en_us', 'de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'es_mx', 'pt_br')}
PLAN['ru_ru'] = dict(title=B / 'PFDinTextCondPro-Bold.ttf', body=B / 'PFDinTextCondPro-Regular.ttf', bodyBold=B / 'PFDinTextCondPro-Bold.ttf', bodyMedium=B / 'PFDinTextCondPro-Medium.ttf')
PLAN['jp_jp'] = dict(title=N / 'NotoSansJP-Bold.otf', body=N / 'NotoSansJP-Medium.otf')
PLAN['kr_kr'] = dict(title=N / 'NotoSerifKR-Bold.otf', body=N / 'NotoSerifKR-Medium.otf')
PLAN['zh_cn'] = dict(title=N / 'NotoSansSC-Bold.otf', body=N / 'NotoSansSC-Medium.otf')
PLAN['zh_tw'] = dict(title=N / 'NotoSansTC-Bold.otf', body=N / 'NotoSansTC-Medium.otf')
BETA_ORIGINAL = dict(jp_jp='Mgenplus Medium/Light + Logotype (titles)', kr_kr='Iropke Batang + Hmfmold (titles)', zh_cn='FZ Lanting Hei Demibold/Extralight', zh_tw='Noto Sans CJK TC Medium/DemiLight')
needed = json.loads((L / 'fonts/needed-codepoints.json').read_text('utf8'))
SAMPLES = ['112101', '200166', '122101', '201599']
summary = {}
for locale, faces in PLAN.items():
    out = L / 'fonts/prepared' / locale; out.mkdir(parents=True, exist_ok=True)
    cps = set(needed[locale]) | {32, 160}
    files = {}
    for role, src in faces.items():
        font = TTFont(src); cmap = font.getBestCmap()
        have = cps & set(cmap); missing = sorted(cps - set(cmap))
        opts = subset.Options(); opts.layout_features = ['kern', 'liga', 'calt', 'locl', 'palt', 'vert']; opts.name_IDs = ['*']; opts.notdef_outline = True
        opts.drop_tables += ['DSIG']
        sub = subset.Subsetter(opts); sub.populate(unicodes=sorted(have)); sub.subset(font)
        target = out / (src.stem + '.subset' + src.suffix); font.save(target)
        files[role] = dict(source=str(src.relative_to(ROOT)), file=target.name, glyphs=len(have), bytes=target.stat().st_size,
                           missing=''.join(chr(c) for c in missing))
    cards = json.loads((L / 'text' / locale / 'cards.json').read_text('utf8'))
    img = Image.new('RGB', (1100, 900), (24, 20, 16)); d = ImageDraw.Draw(img); y = 16
    for ident in SAMPLES:
        c = cards[ident]
        d.text((20, y), c['name'], font=ImageFont.truetype(str(faces['title']), 34), fill=(232, 200, 120)); y += 46
        body = ImageFont.truetype(str(faces['body']), 24); line = ''
        desc = c['description'].replace('\n', ' ')
        words = list(desc) if locale in ('jp_jp', 'zh_cn', 'zh_tw') else desc.split(' ')
        sep = '' if locale in ('jp_jp', 'zh_cn', 'zh_tw') else ' '
        for w in words:
            trial = (line + sep + w) if line else w
            if d.textlength(trial, font=body) > 1050: d.text((20, y), line, font=body, fill=(235, 230, 220)); y += 32; line = w
            else: line = trial
        d.text((20, y), line, font=body, fill=(235, 230, 220)); y += 32
        d.text((20, y), c['tags'], font=ImageFont.truetype(str(faces['body']), 20), fill=(160, 150, 130)); y += 44
    img.save(out / 'preview.png')
    plan = dict(locale=locale, faces=files, betaOriginal=BETA_ORIGINAL.get(locale, 'same family as the Beta'), license='OFL 1.1 (Noto CJK)' if locale in BETA_ORIGINAL else 'original Beta fonts (as embedded by the mod today)')
    (out / 'plan.json').write_text(json.dumps(plan, ensure_ascii=False, indent=1) + '\n', 'utf8')
    summary[locale] = {r: (f['glyphs'], round(f['bytes'] / 1024), f['missing']) for r, f in files.items()}
(L / 'fonts/prepared/summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1) + '\n', 'utf8')
for k, v in summary.items(): print(k, v)

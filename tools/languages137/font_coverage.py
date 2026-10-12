"""Font coverage for the 13 text languages (read-only; writes languages137/fonts).

Needed characters per locale = every character of the card texts (names, rules, flavor,
categories, keywords) + the locale's full alphabet (for the mod UI translation that does
not exist yet) + ASCII digits/punctuation. Candidates: the fonts the mod embeds today
(Beta TMP atlases, traced), the original Beta TTFs found in LegacyGwent, the Beta CJK TMP
atlases, and Noto Sans/Serif CJK (OFL) downloaded from notofonts/noto-cjk.
"""
from pathlib import Path
import json, string
from fontTools.ttLib import TTFont
ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'BetaGwent/build/languages137'
SRC = L / 'fonts/sources'
ALPHA = {
 'ru_ru': 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя«»—–…№',
 'en_us': '’‘“”—–…', 'de_de': 'ÄÖÜäöüß„“‚‘—–…', 'fr_fr': 'ÀÂÆÇÉÈÊËÎÏÔŒÙÛÜŸàâæçéèêëîïôœùûüÿ«»’—–…',
 'it_it': 'ÀÈÉÌÍÒÓÙÚàèéìíòóùú’«»—–…', 'pl_pl': 'ĄĆĘŁŃÓŚŹŻąćęłńóśźż„”’—–…',
 'es_es': 'ÁÉÍÑÓÚÜáéíñóúü¡¿«»’—–…', 'es_mx': 'ÁÉÍÑÓÚÜáéíñóúü¡¿«»’—–…', 'pt_br': 'ÁÂÃÀÇÉÊÍÓÔÕÚÜáâãàçéêíóôõúü“”’—–…',
 'jp_jp': '', 'kr_kr': '', 'zh_cn': '', 'zh_tw': ''}
BASE = string.ascii_letters + string.digits + string.punctuation
fonts104 = json.loads((ROOT / 'BetaGwent/ui/build/beta-fonts104.json').read_text('utf8'))
beta_atlas = json.loads((L / 'fonts/beta-font-glyphs.json').read_text('utf8'))
cands = {}
for name in ('HalisGRMedium', 'HalisGRBold', 'PFDinTextCondPro'):
    cands['mod-today:' + name] = set(map(int, fonts104[name]['glyphs']))
for name, glyphs in beta_atlas.items():
    if name not in ('GwentNumbers',): cands['beta-atlas:' + name] = set(glyphs)
for f in sorted((SRC / 'beta-ttf').glob('*.ttf')) + sorted((SRC / 'noto-cjk').glob('*.otf')):
    cands['file:' + f.name] = set(TTFont(f, lazy=True).getBestCmap())
needed = {}
report = dict(stage=137, method=__doc__.strip(), candidates={k: len(v) for k, v in cands.items()}, locales={})
for locale in ALPHA:
    text = (L / 'text' / locale / 'charset.txt').read_text('utf8').strip()
    kw = json.loads((L / 'text' / locale / 'keywords.json').read_text('utf8'))
    chars = set(text) | set(BASE) | set(ALPHA[locale]) | {c for d in kw.values() for v in d.values() for c in v}
    uifile = L / 'ui' / (locale + '.json')
    if uifile.is_file():  # translated mod UI (stage 137) joins the card texts
        chars |= {c for v in json.loads(uifile.read_text('utf8')).values() for c in v}
    chars = {ord(c) for c in chars if not c.isspace()}
    needed[locale] = chars
    res = {}
    for k, v in cands.items():
        miss = sorted(chars - v)
        res[k] = dict(missing=len(miss), sample=''.join(map(chr, miss[:40])))
    report['locales'][locale] = dict(needed=len(chars), coverage=res)
(L / 'fonts/coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', 'utf8')
(L / 'fonts/needed-codepoints.json').write_text(json.dumps({k: sorted(v) for k, v in needed.items()}) + '\n', 'utf8')
for locale, r in report['locales'].items():
    best = sorted(r['coverage'].items(), key=lambda kv: kv[1]['missing'])[:4]
    print(locale, r['needed'], ' | '.join(f"{k.split(':')[1]}={v['missing']}" + (f"[{v['sample'][:12]}]" if v['missing'] else '') for k, v in best))
    for k in ('mod-today:PFDinTextCondPro', 'file:PFDinTextCondPro-Regular.ttf', 'file:HalisGR-Medium.ttf'):
        v = r['coverage'][k]; print('   ', k, v['missing'], v['sample'][:30])

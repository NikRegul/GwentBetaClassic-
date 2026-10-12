"""Split the live RU->EN dictionary (tools/localization89.strings) into
  * card-derived strings: translated automatically from the original Beta CSVs;
  * mod UI strings: to be translated, written to languages137/ui/source.json with
    per-locale hints (official Beta names of cards / keywords / factions found in the string).
"""
from pathlib import Path
import json, re, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from localization89 import strings
from ws_codegen import localized_plain_text
L = ROOT / 'BetaGwent/build/languages137'
LOCALES = ['de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'es_mx', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn', 'zh_tw']
lookup = strings()
import zipfile, csv, io
z = zipfile.ZipFile(ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions')
tables = {}
for loc in ['ru_ru'] + LOCALES:
    rows = csv.DictReader(io.StringIO(z.read(f'Localization/{loc}.csv').decode('utf-8-sig'), newline=''), delimiter=';')
    tables[loc] = {r['Key']: r.get(loc, '') or '' for r in rows if r.get('Key')}
cards = {loc: json.loads((L / 'text' / loc / 'cards.json').read_text('utf8')) for loc in ['ru_ru'] + LOCALES}
# RU string -> per-locale translation, from (a) raw CSV values and their plain text, (b) built card fields.
auto = {}
def add(ru, per):
    if not ru: return
    slot = auto.setdefault(ru, {})
    for loc, v in per.items():
        if v: slot.setdefault(loc, set()).add(v)
for key, ru in tables['ru_ru'].items():
    add(ru, {loc: tables[loc].get(key, '') for loc in LOCALES})
    add(localized_plain_text(ru), {loc: localized_plain_text(tables[loc].get(key, '')) for loc in LOCALES})
for ident, c in cards['ru_ru'].items():
    for f in ('name', 'description', 'flavor', 'tags', 'glossary'):
        add(c[f], {loc: cards[loc][ident][f] for loc in LOCALES})
card_part, ui = {}, []
ambiguous = {}
for ru, en in lookup.items():
    if ru in auto:
        per = {}
        for loc in LOCALES:
            vals = auto[ru].get(loc, set())
            if len(vals) == 1: per[loc] = next(iter(vals))
            elif vals: per[loc] = sorted(vals)[0]; ambiguous.setdefault(ru, {})[loc] = sorted(vals)
        card_part[ru] = per
    else: ui.append(ru)
# Hints: official names inside UI strings.
names = {}
for ident, c in cards['ru_ru'].items():
    if len(c['name']) >= 3: names[c['name']] = ident
kw = {}
for loc in ['ru_ru'] + LOCALES:
    k = json.loads((L / 'text' / loc / 'keywords.json').read_text('utf8'))['keywords']
    for key, v in k.items(): kw.setdefault(key, {})[loc] = re.split(r'[:：]', v, 1)[0].strip()
name_re = re.compile('|'.join(re.escape(n) for n in sorted(names, key=len, reverse=True)))
source = []
for i, ru in enumerate(ui):
    hints = {}
    for m in set(name_re.findall(ru)):
        ident = names[m]; hints[m] = {loc: cards[loc][ident]['name'] for loc in LOCALES}
    for key, per in kw.items():
        r = per.get('ru_ru')
        if r and len(r) >= 4 and re.search(r'(?<!\w)' + re.escape(r[:max(4, len(r) - 2)]), ru, re.I): hints.setdefault(r, {loc: per.get(loc, '') for loc in LOCALES})
    source.append(dict(id=i, ru=ru, en=lookup[ru], hints=hints))
out = L / 'ui'; out.mkdir(parents=True, exist_ok=True)
(out / 'source.json').write_text(json.dumps(source, ensure_ascii=False, indent=1) + '\n', 'utf8')
(out / 'card-derived.json').write_text(json.dumps(card_part, ensure_ascii=False, indent=1) + '\n', 'utf8')
(out / 'card-derived-ambiguous.json').write_text(json.dumps(ambiguous, ensure_ascii=False, indent=1) + '\n', 'utf8')
missing_auto = {loc: sum(1 for v in card_part.values() if loc not in v) for loc in LOCALES}
print(json.dumps(dict(total=len(lookup), cardDerived=len(card_part), ui=len(ui), withHints=sum(1 for s in source if s['hints']), ambiguous=len(ambiguous), cardMissingPerLocale=missing_auto)))

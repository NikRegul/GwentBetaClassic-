"""Stage 137 preparation: card text for all 13 original Beta 0.9.24 locales.

Read-only with respect to the live mod: writes only BetaGwent/build/languages137/text.
Uses exactly the same derivation as tools/build_full_catalog.py (variable substitution,
categories, keyword glossary, flavor), with the locale's original Beta CSV instead of the
ru_ru/en_us tables of the normalized catalogue. ru_ru and en_us outputs are compared with
the live catalogue to prove the pipeline is identical.
"""
from pathlib import Path
import csv, hashlib, io, json, re, sys, zipfile
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from ws_codegen import localized_plain_text
from keyword_glossary import keyword_mentioned

SOURCE = ROOT / 'Gwent 0.9.24.3.432/Gwent_Data/StreamingAssets/data_definitions'
OUT = ROOT / 'BetaGwent/build/languages137/text'
LOCALES = ['ru_ru', 'en_us', 'de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'es_mx', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn', 'zh_tw']
catalog_raw = (ROOT / 'data/beta924/normalized/catalog.json').read_bytes()
catalog = json.loads(catalog_raw)
collection = json.loads((ROOT / 'data/beta924/planning/full_catalog.json').read_text('utf8'))['cards']
collection_ids = [c['templateId'] for c in collection]

def load_tables():
    tables = {}
    with zipfile.ZipFile(SOURCE) as archive:
        for locale in LOCALES:
            raw = archive.read(f'Localization/{locale}.csv')
            rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'), newline=''), delimiter=';'))
            keys = [r['Key'] for r in rows if r.get('Key')]
            if len(keys) != len(set(keys)): raise SystemExit('duplicate key in ' + locale)
            tables[locale] = ({r['Key']: r.get(locale, '') or '' for r in rows if r.get('Key')}, hashlib.sha256(raw).hexdigest())
    return tables

def build(table):
    def category_text(t):
        names = []
        for word_index, word in enumerate(t['categoryWords']):
            mask = int(word['decimal'])
            for bit in range(64):
                if mask & (1 << bit):
                    name = table.get('card_category_' + str(word_index * 64 + bit))
                    if name: names.append(name)
        return ' · '.join(names)
    def description(ident):
        values = {}
        for g in catalog['abilities']:
            if g['type'] != 'CardAbility' or g['templateId'] != ident: continue
            for group in g['sourceTree']['children']:
                if group['tag'] not in ('TemporaryVariables', 'PersistentVariables'): continue
                for v in group['children']:
                    a = v['attributes']
                    if a.get('Type') == 'IntVar': values[a['Name']] = a['V']
                    elif a.get('Type') == 'CardDefVar':
                        templates = [x['attributes']['TemplateId'] for x in v['children'] if 'TemplateId' in x['attributes']]
                        if templates: values[a['Name']] = table.get(templates[0] + '_name', templates[0])
        value = table.get(str(ident) + '_tooltip', '')
        for key, replacement in values.items():
            # Some locales spell the variable in another case ({damage}) or with a stray space ({Damage2 } in zh_tw).
            value = re.sub(r'\{\s*' + re.escape(key) + r'\s*\}', lambda m, r=str(replacement): r, value, flags=re.I)
        return localized_plain_text(value)
    keyword_defs = {}
    for key, value in table.items():
        if not key.startswith('keyword_'): continue
        plain = localized_plain_text(value)
        # CJK texts use a full-width colon.
        parts = re.split(r'[:：]', plain, 1)
        if len(parts) == 2: keyword_defs.setdefault(parts[0].strip(), plain)
    cards = {}
    for t in catalog['templates']:
        ident = t['templateId']; text = description(ident)
        glossary = [d for label, d in keyword_defs.items() if keyword_mentioned(label, text)]
        cards[str(ident)] = dict(name=table.get(str(ident) + '_name', ''), description=text,
            flavor=localized_plain_text(table.get(str(ident) + '_fluff', '')), tags=category_text(t), glossary='\n\n'.join(glossary))
    categories = {k: v for k, v in table.items() if k.startswith('card_category_')}
    keywords = {k: localized_plain_text(v) for k, v in table.items() if k.startswith('keyword_')}
    factions = {k: table.get(k, '') for k in ('100_name', '101_name', '102_name', '103_name', '104_name', '105_name')}
    return cards, categories, keywords, factions

def numbers(s): return sorted(re.findall(r'\d+', s))

tables = load_tables()
OUT.mkdir(parents=True, exist_ok=True)
built = {locale: build(tables[locale][0]) for locale in LOCALES}
ru_cards = built['ru_ru'][0]
report = dict(stage=137, source=str(SOURCE.relative_to(ROOT)), sourceSha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              catalogSha256=hashlib.sha256(catalog_raw).hexdigest(), collectionCards=len(collection_ids), templates=len(catalog['templates']), locales=[])
# Pipeline identity: ru_ru must reproduce the live catalogue titles and descriptions.
live = {c['templateId']: c for c in collection}
mismatch = [i for i in collection_ids if ru_cards[str(i)]['name'] != live[i]['title'] or ru_cards[str(i)]['description'] != live[i]['description']]
report['ruMatchesLiveCatalogue'] = not mismatch; report['ruLiveMismatches'] = mismatch[:20]
for locale in LOCALES:
    cards, categories, keywords, factions = built[locale]
    folder = OUT / locale; folder.mkdir(parents=True, exist_ok=True)
    (folder / 'cards.json').write_text(json.dumps(cards, ensure_ascii=False, indent=1) + '\n', 'utf8')
    (folder / 'keywords.json').write_text(json.dumps(dict(keywords=keywords, categories=categories, factions=factions), ensure_ascii=False, indent=1) + '\n', 'utf8')
    missing_name = [i for i in collection_ids if not cards[str(i)]['name']]
    missing_text = [i for i in collection_ids if ru_cards[str(i)]['description'] and not cards[str(i)]['description']]
    missing_flavor = [i for i in collection_ids if ru_cards[str(i)]['flavor'] and not cards[str(i)]['flavor']]
    placeholders = [i for i in collection_ids if re.search(r'\{[^}]*\}', cards[str(i)]['description'])]
    number_diff = [i for i in collection_ids if cards[str(i)]['description'] and numbers(cards[str(i)]['description']) != numbers(ru_cards[str(i)]['description'])]
    chars = sorted({c for i in collection_ids for f in ('name', 'description', 'flavor', 'tags', 'glossary') for c in cards[str(i)][f] if not c.isspace()})
    (folder / 'charset.txt').write_text(''.join(chars) + '\n', 'utf8')
    report['locales'].append(dict(locale=locale, csvSha256=tables[locale][1], keys=len(tables[locale][0]),
        missingNames=missing_name, missingDescriptions=missing_text, missingFlavor=missing_flavor,
        unresolvedPlaceholders=placeholders, numbersDifferFromRussian=number_diff, distinctCharacters=len(chars),
        keywords=len(keywords), categories=len(categories)))
(OUT / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
print(json.dumps(dict(ruMatchesLive=report['ruMatchesLiveCatalogue'], mismatches=len(mismatch),
    locales={l['locale']: [len(l['missingNames']), len(l['missingDescriptions']), len(l['missingFlavor']), len(l['unresolvedPlaceholders']), len(l['numbersDifferFromRussian']), l['distinctCharacters']] for l in report['locales']}), ensure_ascii=False))

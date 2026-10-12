"""Assemble the mod UI dictionaries (RU source -> 11 locales) from:
card-derived strings (original Beta CSVs), keyword glossaries, templated strings,
hand-translated batches (ui/tr/b*.json), 'ИИ · <deck>' composition.
es_mx is derived from es_es; zh_tw from zh_cn via OpenCC s2twp; official Beta names
are then substituted for both. Writes languages137/ui/<locale>.json and ui/report.json."""
from pathlib import Path
import json, re, glob, sys
from opencc import OpenCC
ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'BetaGwent/build/languages137'
U = L / 'ui'
BASE = ['de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn']
ALL = ['de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'es_mx', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn', 'zh_tw']
src = json.loads((U / 'source.json').read_text('utf8'))
byid = {s['id']: s for s in src}
card = json.loads((U / 'card-derived.json').read_text('utf8'))
parts = [json.loads((U / 'tr/glossary.json').read_text('utf8')), json.loads((U / 'tr/templated.json').read_text('utf8'))]
for f in sorted(glob.glob(str(U / 'tr/b*.json'))): parts.append(json.loads(Path(f).read_text('utf8')))
ui = {l: {} for l in ALL}
for part in parts:
    for i, per in part.items():
        ru = byid[int(i)]['ru']
        for l, v in per.items():
            if l in ui: ui[l][ru] = v
# Corrections after review of official Beta keyword names (Resilient).
FIX = {439: dict(fr_fr='Tenace : reste sur le plateau à la manche suivante.', it_it='Resistenza: resta in campo nel round successivo.',
                 pl_pl='Wytrzymałość: zostanie na polu w następnej rundzie.', es_es='Resistente: permanece en el tablero en la siguiente ronda.',
                 kr_kr='잔류: 다음 라운드에도 필드에 남습니다.', zh_cn='坚韧：会在下一小局留在战场上。')}
for i, per in FIX.items():
    ru = byid[i]['ru']; lead = re.match(r'^\s*', ru).group(); trail = re.search(r'\s*$', ru).group()
    for l, v in per.items(): ui[l][ru] = lead + v + trail
EXTRA = {  # deck names used only inside 'ИИ · ...'
 'Алхимия': dict(de_de='Alchemie', fr_fr='Alchimie', it_it='Alchimia', pl_pl='Alchemia', es_es='Alquimia', pt_br='Alquimia', jp_jp='錬金術', kr_kr='연금술', zh_cn='炼金'),
 'Невольничья пехота': dict(de_de='Sklaveninfanterie', fr_fr='Infanterie d\'esclaves', it_it='Fanteria di schiavi', pl_pl='Niewolnicza piechota', es_es='Infantería esclava', pt_br='Infantaria escrava', jp_jp='奴隷歩兵', kr_kr='노예 보병', zh_cn='奴隶步兵'),
}
AI = dict(de_de='KI · ', fr_fr='IA · ', it_it='IA · ', pl_pl='SI · ', es_es='IA · ', pt_br='IA · ', jp_jp='AI · ', kr_kr='AI · ', zh_cn='AI · ')
unresolved = []
for s in src:
    ru = s['ru']
    if not ru.strip() or ru in ui['de_de'] or ru in card: continue
    m = re.fullmatch(r'ИИ · (.+)', ru)
    if m:
        rest = m.group(1)
        for l in BASE:
            v = ui[l].get(rest) or card.get(rest, {}).get(l) or EXTRA.get(rest, {}).get(l)
            if v: ui[l][ru] = AI[l] + v
        if all(ru in ui[l] for l in BASE): continue
    unresolved.append(s['id'])
# Card-derived strings straight from the original Beta localisation (all 11 locales).
# Keyword glossaries missing for a locale (its card text names other keywords) are
# composed from the official keyword definitions, part by part.
kwall = {l: json.loads((L / 'text' / l / 'keywords.json').read_text('utf8'))['keywords'] for l in ['ru_ru'] + ALL}
rudefs = {v: k for k, v in kwall['ru_ru'].items()}
for ru, per in card.items():
    for l in ALL:
        if per.get(l): ui[l].setdefault(ru, per[l])
        elif all(p in rudefs for p in ru.split('\n\n')):
            ui[l].setdefault(ru, '\n\n'.join(kwall[l][rudefs[p]] for p in ru.split('\n\n')))
cards = {l: json.loads((L / 'text' / l / 'cards.json').read_text('utf8')) for l in ['es_es', 'es_mx', 'zh_cn', 'zh_tw']}
kws = {l: json.loads((L / 'text' / l / 'keywords.json').read_text('utf8')) for l in ['es_es', 'es_mx', 'zh_cn', 'zh_tw']}
def name_pairs(a, b, conv=lambda x: x, keywords=True):
    pairs = {}
    for i in cards[a]:
        x, y = conv(cards[a][i]['name']), cards[b][i]['name']
        if x and y and x != y and len(x) >= 2: pairs[x] = y
    for grp in (('keywords', 'categories') if keywords else ()):
        for k, v in kws[a][grp].items():
            w = kws[b][grp].get(k)
            if not w: continue
            x = conv(re.split(r'[:：]', v, 1)[0].strip()); y = re.split(r'[:：]', w, 1)[0].strip()
            if x and y and x != y and len(x) >= 2: pairs[x] = y
    return dict(sorted(pairs.items(), key=lambda kv: -len(kv[0])))
def apply(text, pairs, words=False):
    if not pairs: return text
    body = '|'.join(re.escape(k) for k in pairs)
    rx = re.compile(r'(?<!\w)(?:' + body + r')(?!\w)' if words else body)
    return rx.sub(lambda m: pairs[m.group()], text)
# es_mx: Latin American wording + official es_mx names.
MX = [(r'\bPulsa\b', 'Presiona'), (r'\bpulsa\b', 'presiona'), (r'\bmando\b', 'control'), (r'\bratón\b', 'mouse'), (r'\bMayús\b', 'Shift'),
      (r'\bCoste\b', 'Costo'), (r'\bcoste\b', 'costo'), (r'\bOmitir\b', 'Saltar'), (r'\bomitir\b', 'saltar'), (r'\bHas ganado\b', 'Ganaste'), (r'\bha pasado\b', 'pasó'), (r'\bHa ganado\b', 'Ganó')]
# Card names only: keyword labels are verb forms and would break inflected nouns.
mx_pairs = {k: v for k, v in name_pairs('es_es', 'es_mx', keywords=False).items() if len(k) >= 4}
cc = OpenCC('s2twp'); tw_pairs = name_pairs('zh_cn', 'zh_tw', conv=cc.convert)
# Runtime fragments glued in code (audit 137): language button and gamepad row slot.
ADDED = {
 'Текст: ': dict(de_de='Text: ', fr_fr='Texte : ', it_it='Testo: ', pl_pl='Tekst: ', es_es='Texto: ', pt_br='Texto: ', jp_jp='テキスト：', kr_kr='텍스트: ', zh_cn='文本：'),
 ' · место ': dict(de_de=' · Platz ', fr_fr=' · position ', it_it=' · posizione ', pl_pl=' · miejsce ', es_es=' · posición ', pt_br=' · posição ', jp_jp=' · 位置 ', kr_kr=' · 위치 ', zh_cn=' · 位置 '),
}
for ru, per in ADDED.items():
    for l in BASE: ui[l][ru] = per[l]
for ru, v in list(ui['es_es'].items()):
    if ru in card: continue
    t = apply(v, mx_pairs, words=True)
    for a, b in MX: t = re.sub(a, b, t)
    ui['es_mx'][ru] = t
for ru, v in list(ui['zh_cn'].items()):
    if ru in card: continue
    ui['zh_tw'][ru] = apply(cc.convert(v), tw_pairs).replace('“', '「').replace('”', '」').replace('‘', '『').replace('’', '』').replace('呐', '吶')
# Checks.
problems = {l: [] for l in ALL}
for s in src:
    ru = s['ru']
    if not ru.strip(): continue
    for l in ALL:
        v = ui[l].get(ru)
        if v is None: problems[l].append((s['id'], 'missing')); continue
        if ru in card: continue
        if ru.count('\n') != v.count('\n'): problems[l].append((s['id'], 'newlines'))
        for tag in ('<b>', '</b>', '<br>'):
            if ru.count(tag) != v.count(tag): problems[l].append((s['id'], 'tag ' + tag))
        if re.match(r'^\s*', ru).group() != re.match(r'^\s*', v).group() or re.search(r'\s*$', ru).group() != re.search(r'\s*$', v).group():
            problems[l].append((s['id'], 'edge whitespace'))
        if re.search(r'[А-Яа-яЁё]', v) and not re.search(r'[йцукенгшщзхъфывапролджэячсмитьбюё]{20}', v): problems[l].append((s['id'], 'cyrillic left'))
for ru in card:
    for l in ALL:
        if ru not in ui[l]: problems[l].append(('card', ru[:40], 'missing'))
for l in ALL:
    (U / f'{l}.json').write_text(json.dumps(ui[l], ensure_ascii=False, indent=1) + '\n', 'utf8')
report = dict(stage=137, sourceStrings=sum(1 for s in src if s['ru'].strip()) + len(card), uiStrings=sum(1 for s in src if s['ru'].strip()),
              cardDerived=len(card), unresolved=unresolved,
              locales={l: dict(entries=len(ui[l]), problems=problems[l][:50], problemCount=len(problems[l])) for l in ALL},
              origin={'card-derived': 'original Beta 0.9.24 localisation', 'ui': 'translated by Claude from RU+EN, needs native review',
                      'es_mx': 'derived from es_es + official es_mx names', 'zh_tw': 'OpenCC s2twp from zh_cn + official zh_tw names'})
(U / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=1) + '\n', 'utf8')
print(json.dumps(dict(unresolved=len(unresolved), ids=unresolved[:20], counts={l: (len(ui[l]), len(problems[l])) for l in ALL}), ensure_ascii=False))

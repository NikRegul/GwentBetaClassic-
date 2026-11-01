# -*- coding: utf-8 -*-
import os, re, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from texts094 import T, NAMES
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC = os.path.join(ROOT, 'docs/releases/0.9.3/nexus')
OUT = os.path.join(ROOT, 'release/0.9.4/nexus-final')
os.makedirs(OUT, exist_ok=True)
H = '[size=4][color=#e0b354][b]{}[/b][/color][/size]'
def rd(p): return open(p, encoding='utf-8-sig').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(s)
def balanced(t):
    bad = []
    for tag in ['spoiler','b','size','color','center','list','code','url']:
        if len(re.findall(r'\[' + tag + r'[\]=]', t)) != t.count('[/' + tag + ']'): bad.append(tag)
    return bad
combined = rd(os.path.join(SRC, 'NEXUS_DESCRIPTION_0.9.3.bbcode.txt'))
report = {}
for lang, (title, paras) in T.items():
    old = rd(os.path.join(SRC, lang, 'description.bbcode.txt'))
    body = old.strip()
    assert combined.count(body) == 1, lang
    L = body.split('\n')
    i = next(k for k, l in enumerate(L) if '[b]0.9.3 — ' in l)
    j = next(k for k in range(i + 1, len(L)) if L[k].startswith('[size=4]'))
    for k in range(len(L)):
        if not (i <= k < j): L[k] = L[k].replace('0.9.3', '0.9.4')
    sec = [H.format('0.9.4 — ' + title), '']
    for p in paras: sec += [p, '']
    L = L[:i] + sec + L[i:]
    new = '\n'.join(L)
    combined = combined.replace(body, new)
    wr(os.path.join(OUT, 'per-language', lang, 'description.bbcode.txt'), new + '\n')
    report[lang] = {'left093': new.count('0.9.3'), 'bad': balanced(new)}
head_old = 'Gwent Beta 0.9.24 · 0.9.3[/size]'
assert combined.count(head_old) == 1
combined = combined.replace(head_old, 'Gwent Beta 0.9.24 · 0.9.4[/size]')
wr(os.path.join(OUT, 'NEXUS_DESCRIPTION_0.9.4.bbcode.txt'), combined)
def post(lang):
    title, paras = T[lang]
    t = title[0].upper() + title[1:]
    return '[size=5][b]Gwent Beta Classic 0.9.4[/b][/size]\n\n[b]' + t + '[/b]\n\n' + '\n\n'.join(paras) + '\n\nClassic 1.32 · Next-Gen 5.0+ · Steam Deck'
enru = post('en') + '\n\n[line]\n\n' + post('ru') + '\n'
wr(os.path.join(OUT, 'NEXUS_POST_0.9.4_EN_RU.bbcode.txt'), enru)
allp = '\n\n[line]\n\n'.join('[b]' + NAMES[l] + '[/b]\n\n' + post(l) for l in T) + '\n'
wr(os.path.join(OUT, 'NEXUS_POST_0.9.4_ALL_LANGUAGES.bbcode.txt'), allp)
for l in T: wr(os.path.join(OUT, 'per-language', l, 'post.bbcode.txt'), post(l) + '\n')
print(json.dumps(report, ensure_ascii=False))
print('combined', len(combined), 'bad', balanced(combined), '0.9.3 left', combined.count('0.9.3'), '0.9.4', combined.count('0.9.4'))
print('post EN/RU chars', len(enru), 'bad', balanced(enru), '| all-lang post chars', len(allp))

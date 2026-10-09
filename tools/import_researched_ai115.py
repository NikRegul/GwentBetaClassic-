"""Strict, reproducible import of the author's researched Beta deck proposal.

Names must resolve exactly after punctuation/accent normalization. No role fillers,
silent truncation, or imaginary leaders. Existing preset identities stay stable.
"""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'deck_rules_researched_114.md'
DEST = ROOT / 'data/beta924/ai/researched115.json'

def normalize(text):
    text = text.lower().replace('ё', 'е')
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    return re.sub(r'[^a-zа-я0-9]', '', text)

def main():
    raw = SOURCE.read_bytes()
    source = raw.decode('utf-8-sig')
    canonical = json.loads((ROOT / 'data/beta924/normalized/catalog.json').read_text(encoding='utf-8-sig'))
    cards = {c['templateId']: c for c in json.loads((ROOT / 'data/beta924/planning/full_catalog.json').read_text(encoding='utf-8-sig'))['cards']}
    names = {}
    for ident in cards:
        for lang in ('ru_ru', 'en_us'):
            key = normalize(canonical['localization'][lang][str(ident) + '_name'])
            names.setdefault(key, set()).add(ident)
    existing = json.loads((ROOT / 'data/beta924/ai/rules.json').read_text(encoding='utf-8-sig'))['profiles']
    identities = {p['id']: p['presetId'] for p in existing if p['active']}
    # Six approved adaptations are appended; never shift 54..93.
    identities.update({10: 94, 12: 95, 33: 96, 42: 97, 43: 98, 44: 99})
    adaptations = {10: 'machines', 12: 'soldiers', 33: 'greatswords', 42: 'temerians', 43: 'axemen', 44: 'temerians'}
    profiles = []
    errors = []
    sections = re.split(r'(?m)^## (\d{2})\. (.+)\r?\n', source)
    for number, title, body in zip(sections[1::3], sections[2::3], sections[3::3]):
        ident = int(number)
        if ident > 46:
            continue
        body = re.split(r'(?m)^## ', body, maxsplit=1)[0]
        roster_body = body.split('### Предложенный полный состав Beta', 1)[-1].split('### Правки состава', 1)[0]
        leader_match = re.search(r'Лидер: \*\*(.+?)\*\* \(ID (\d+)\)', roster_body)
        if not leader_match:
            errors.append(f'{ident}: missing leader'); continue
        leader = int(leader_match[2]); faction = cards[leader]['faction']
        if not cards[leader]['leader']:
            errors.append(f'{ident}: {leader} is not a leader')
        roster = []
        entries = []
        for count, name in re.findall(r'(?m)^- (\d+) × (.+?)\r?$', roster_body):
            candidates = names.get(normalize(name), set())
            if len(candidates) != 1:
                errors.append(f'{ident}: ambiguous/unknown {name}: {sorted(candidates)}'); continue
            card = next(iter(candidates)); count = int(count)
            roster.extend([card] * count)
            entries.append(dict(templateId=card, copies=count, name=name))
        counts = Counter(roster); tiers = Counter(cards[c]['tier'] for c in roster)
        expected = 40 if ident == 32 else 25
        if len(roster) != expected:
            errors.append(f'{ident}: {len(roster)} cards, expected {expected}')
        for card, count in counts.items():
            c = cards[card]
            if c['leader'] or c['faction'] not in (1, faction) or count > (3 if c['tier'] == 2 else 1):
                errors.append(f'{ident}: illegal card/copies {card} x{count}')
        if tiers[8] > 4 or tiers[4] > 6 or (ident == 31 and max(counts.values(), default=0) > 1):
            errors.append(f'{ident}: rarity/singleton limit')
        strategy_body = body.split('### Твои правки и стратегия — заполнено', 1)[-1]
        fields = re.split(r'\*\*(.+?):\*\*\s*', strategy_body)
        strategy = {key.strip(): value.strip().strip('-').strip() for key, value in zip(fields[1::2], fields[2::2])}
        pass_text = next((value for key, value in strategy.items() if key.startswith('Пас и догон')), '')
        policy = 'L' if re.search(r'Политика L\b', pass_text) else 'T'
        profiles.append(dict(id=ident, title=title.strip(), presetId=identities[ident], leader=leader,
                             faction=faction, templateIds=roster, roster=entries,
                             family=adaptations.get(ident), passPolicy=policy, strategy=strategy,
                             sourceSection=f'{number}. {title}'))
    if len(profiles) != 46:
        errors.append(f'Expected 46 profiles, got {len(profiles)}')
    if errors:
        raise ValueError('\n'.join(errors))
    result = dict(schema=1, stage=115, source=SOURCE.name, sourceSha256=hashlib.sha256(raw).hexdigest(),
                  policies=source.split('## Политики паса:', 1)[1].split('## Составы', 1)[0].strip(), profiles=profiles)
    DEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Imported {len(profiles)} researched profiles; all rosters legal; stable preset IDs 54..99.')

if __name__ == '__main__':
    main()

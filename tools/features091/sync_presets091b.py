"""Guarded sync of reviewed AI preset rosters (0.9.1b) into generated runtime files.

Source of truth: data/beta924/ai/deck_patch128.json -> tools/build_ai_rules.py ->
data/beta924/duel/presets.json. This script copies only the listed preset rosters
into duelCatalog.ws (card list + header counts) and slice.json. Card definitions
are never touched.

Usage: python -X utf8 tools/features091/sync_presets091b.py 56 58
"""
from collections import Counter
from pathlib import Path
import hashlib, json, re, sys
ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / 'BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'


def read(p):
    return json.loads((ROOT / p).read_text('utf-8-sig'))


def write(p, data, crlf):
    text = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if crlf:
        text = text.replace('\n', '\r\n')
    (ROOT / p).write_bytes(text.encode('utf8'))


def main(ids):
    presets = {p['id']: p for p in read('data/beta924/duel/presets.json')['presets']}
    full = {c['templateId']: c for c in read('data/beta924/planning/full_catalog.json')['cards']}
    raw = CATALOG.read_bytes()
    crlf = b'\r\n' in raw[:4000]
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    slice_raw = (ROOT / 'data/beta924/duel/slice.json').read_bytes()
    data = json.loads(slice_raw.decode('utf-8-sig'))
    report = []
    for ident in ids:
        preset = presets[ident]
        cards = preset['templateIds']
        assert len(cards) == 25
        units = sum(1 for i in cards if full[i]['typeMask'] == 4)
        tiers = Counter(full[i]['tier'] for i in cards)
        pattern = r'(function BetaGwentDuelPresetCards%d\(out ids : array<int>\)\n\{\n)((?:    ids\.PushBack\(\d+\);\n)+)(\})' % ident
        match = re.search(pattern, text)
        assert match, ident
        old = [int(i) for i in re.findall(r'PushBack\((\d+)\)', match.group(2))]
        body = ''.join('    ids.PushBack(%d);\n' % i for i in cards)
        text = text[:match.start(2)] + body + text[match.end(2):]
        header = re.compile(r'(    case %d:\n        value\.id = %d; value\.leaderTemplateId = )(\d+)(;\n.*?\n        value\.unitCount = )(\d+)(; value\.specialCount = )(\d+)(;\n        value\.goldCount = )(\d+)(; value\.silverCount = )(\d+)(;)' % (ident, ident), re.S)
        h = header.search(text)
        assert h, ident
        text = (text[:h.start()] + h.group(1) + str(preset['leader']) + h.group(3) + str(units) + h.group(5) + str(25 - units)
                + h.group(7) + str(tiers[8]) + h.group(9) + str(tiers[4]) + h.group(11) + text[h.end():])
        target = next(p for p in data['presets'] if p['id'] == ident)
        target.update(templateIds=list(cards), leader=preset['leader'], unitCount=units, specialCount=25 - units,
                      goldCount=tiers[8], silverCount=tiers[4], cards=[dict(templateId=i, copies=n) for i, n in Counter(cards).items()])
        report.append(dict(preset=ident, oldCards=old, newCards=cards, units=units))
    out = text.replace('\n', '\r\n') if crlf else text
    CATALOG.write_bytes(b'\xef\xbb\xbf' + out.encode('utf8'))
    data['presetsSourceSha256'] = hashlib.sha256((ROOT / 'data/beta924/duel/presets.json').read_bytes()).hexdigest()
    write('data/beta924/duel/slice.json', data, b'\r\n' in slice_raw[:4000])
    print(json.dumps(report, ensure_ascii=False))


if __name__ == '__main__':
    main([int(a) for a in sys.argv[1:]])

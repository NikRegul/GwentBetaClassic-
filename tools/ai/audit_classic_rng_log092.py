"""Preserve and inspect a retail log; no game files or processes are changed."""
from pathlib import Path
import collections, hashlib, json, re, shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'BetaGwent/drafts/day-iteration-20261023/classic132-rng-regression'
OUT.mkdir(parents=True, exist_ok=True)
source = Path.home()/'Documents/The Witcher 3/scriptslog.txt'
raw = source.read_bytes()
digest = hashlib.sha256(raw).hexdigest()
copy = OUT/('scriptslog-'+digest[:12]+'.txt')
if not copy.exists():
    copy.write_bytes(raw)
games = []
for ordinal, block in enumerate(raw.decode('utf-8', errors='replace').split('DUEL_STARTED schema=')[1:], 1):
    start = block.splitlines()[0]
    fields = dict(re.findall(r'(\w+)=([^\s]+)', start))
    records = []
    first = block.split('AI_POSITION schema=1 decision=1 ', 1)
    if len(first) > 1:
        position = first[1].split('AI_REASON schema=1 decision=1 event=PLAN')[0]
        for line in position.splitlines():
            if 'AI_POSITION_CARDS decision=1 ' not in line:
                continue
            records.extend([int(x) for x in item.split(':')]
                           for item in line.split()
                           if re.fullmatch(r'-?\d+(?::-?\d+){12}', item))
    # Instance IDs were allocated in shuffled-deck order, before drawing/mulligan.
    own = sorted((x for x in records if x[2] == 1 and x[4] in (8, 16)), key=lambda x: x[0])
    outcomes = [x for x in block.splitlines() if any(t in x for t in
                ('DUEL_ROUND', 'DUEL_MATCH', 'DUEL_FINISH', 'DUEL_FATAL'))]
    views = [dict(re.findall(r'(\w+)=([^\s]+)', x)) for x in block.splitlines() if 'BOARD_VIEW revision=' in x]
    last_view = views[-1] if views else None
    games.append({'ordinal': ordinal, 'start': fields,
                  'initialOwnTemplateOrder': [x[1] for x in own],
                  'observedOwnHandAfterMulligan': [x[1] for x in sorted(own, key=lambda x:x[5]) if x[4] == 8],
                  'outcomeLines': outcomes, 'lastBoardView': last_view,
                  'winnerMask': int(last_view['flags']) // 16 if last_view else 0,
                  'maximumLoggedDraws': max([int(x) for x in re.findall(r'\bdraws=(\d+)', block)] or [0])})
groups = {}
for game in games:
    if len(game['initialOwnTemplateOrder']) != 25:
        continue
    key = game['start']['ownPreset']
    groups.setdefault(key, []).append(game)
report = {'schema': 1, 'capturedAtUtc': datetime.now(timezone.utc).isoformat(),
          'source': str(source), 'sourceMtimeUtc': datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
          'sha256': digest, 'preservedCopy': str(copy.relative_to(ROOT)), 'games': games,
          'groups': {k: {'games': len(v), 'distinctSeeds': len({x['start']['seed'] for x in v}),
                        'distinctInitialOwnOrders': len({tuple(x['initialOwnTemplateOrder']) for x in v})}
                     for k, v in groups.items()},
          'starterCounts': dict(collections.Counter(x['start']['starter'] for x in games)),
          'completedGames': sum(x['winnerMask'] != 0 for x in games),
          'humanWins': sum(x['winnerMask'] == 1 for x in games),
          'aiWins': sum(x['winnerMask'] == 2 for x in games),
          'humanTwoRoundWins': sum(x['winnerMask'] == 1 and x['lastBoardView']['round'] == '2' for x in games),
          'interpretation': 'Different logged seeds produce identical allocated own-deck template order. '
                            'Hand changes after different human mulligans are not fresh shuffle variation. '
                            'The log proves repetition, not the arithmetic cause or universal AI weakness.'}
(OUT/'log-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:report[k] for k in ('sha256','groups','starterCounts')}, ensure_ascii=False))

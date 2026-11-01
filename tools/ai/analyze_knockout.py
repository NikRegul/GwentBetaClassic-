"""Audit a completed frozen Classic/Hard knockout; select development replays."""
import argparse
import collections
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    source, output = args.source.resolve(), args.output.resolve()
    if output.exists():
        raise ValueError('Use a fresh analysis folder')
    plan, report = read(source/'plan.json'), read(source/'report.json')
    digest = sha(source/'plan.json')
    assert report['complete'] and report['errors'] == 0 and report['planSha256'] == digest
    assert sha(source/'entrants.json') == plan['rosterSha256']
    assert sha(source/'profile-mapping.json') == plan['mappingSha256']
    assert sha(Path(plan['current'])/'manifest.json') == plan['commonManifestSha256']
    for name, expected in plan['codeFiles'].items():
        assert sha(source/'frozen'/name) == expected, name
    entrants = {e['key']: e for e in read(source/'entrants.json')}
    series = [read(p) for p in sorted((source/'series').glob('*.json'))]
    assert len(series) == report['series'] == plan['series']
    stats, losses, seen = {}, [], set()
    cross = {group: dict(points=0, games=0) for group in ('hard', 'classic')}
    beta_errors, forced_searches, finish_reasons = [], 0, collections.Counter()
    for match in series:
        assert match['planSha256'] == digest
        assert len(match['games']) % 2 == 0
        assert plan['format']['basePairs']*2 <= len(match['games']) <= (plan['format']['basePairs']+plan['format']['maxExtraPairs'])*2
        points = 0
        for index, item in enumerate(match['games']):
            game_id = item['id']
            assert game_id not in seen
            seen.add(game_id)
            path = source/'games'/(game_id+'.json')
            assert sha(path) == item['sha256'], game_id
            game = read(path)
            assert game['id'] == game_id and game['series'] == match['id']
            assert game['status'] == 'complete' and game['winner'] in (1, 2, 3)
            assert game['planSha256'] == digest and game['commonFingerprint'] == plan['commonFingerprint']
            assert game['pair'] == index//2 and game['mirror'] == index % 2
            a, b = (match['right'], match['left']) if index % 2 else (match['left'], match['right'])
            assert (game['left'], game['right']) == (a, b)
            points += .5 if game['winner'] == 3 else int(game['winner'] == (2 if index % 2 else 1))
            forced_searches += game['betaForcedSearches']
            beta_errors.extend(dict(game=game_id, error=e) for e in game['betaPlaymakerErrors'])
            finish_reasons.update(t['finishReason'] for t in game['trace'] if t['policy'] == 'beta')
            for side, key, enemy_key in ((1, a, b), (2, b, a)):
                entrant, enemy = entrants[key], entrants[enemy_key]
                score = .5 if game['winner'] == 3 else int(game['winner'] == side)
                row = stats.setdefault(key, dict(key=key, title=entrant['title'], faction=entrant['faction'], group=entrant['group'], games=0, points=0, losses=0, swept=0))
                row['games'] += 1
                row['points'] += score
                lost = game['winner'] not in (3, side)
                swept = lost and game['crowns'][side-1] == 0
                row['losses'] += lost
                row['swept'] += swept
                if entrant['group'] != enemy['group']:
                    cross[entrant['group']]['games'] += 1
                    cross[entrant['group']]['points'] += score
                if lost:
                    losses.append(dict(game=game_id, side=side, key=key, enemy=enemy_key, group=entrant['group'], enemyGroup=enemy['group'], faction=entrant['faction'], title=entrant['title'], seed=game['seed'], crowns=game['crowns'], turns=len(game['trace']), swept=swept))
        assert points == match['leftPoints'] and len(match['games'])-points == match['rightPoints']
        if points != len(match['games'])/2:
            assert match['resolution'] == 'game-points'
            assert match['winner'] == (match['left'] if points > len(match['games'])/2 else match['right'])
        else:
            assert match['resolution'] == 'seeded-draw'
            coin = hashlib.sha256((str(plan['masterSeed'])+':tie:'+match['id']).encode()).digest()[0] & 1
            assert match['winner'] == (match['left'] if coin else match['right'])
    assert len(seen) == report['games'] == len(list((source/'games').glob('*.json')))
    assert cross == report['crossPolicy']
    assert not list((source/'errors').glob('*.json'))
    selected, classic = [], []
    for group, destination in (('hard', selected), ('classic', classic)):
        for faction in (2, 4, 8, 16, 32):
            eligible = [r for r in losses if r['group'] == group and r['enemyGroup'] == group and r['faction'] == faction]
            unique = set()
            for row in sorted(eligible, key=lambda r: (not r['swept'], r['turns'], r['game'])):
                if row['key'] in unique:
                    continue
                destination.append(row)
                unique.add(row['key'])
                if len(unique) == 2:
                    break
    decks = sorted((dict(row, pointRate=row['points']/row['games']) for row in stats.values()), key=lambda r: (r['group'], r['pointRate'], r['key']))
    result = dict(schema=1, kind='development-evidence-not-strength-trial', source=str(source), snapshot=plan['current'], planSha256=digest, reportSha256=sha(source/'report.json'), completedBrackets=report['grids'], completedSeries=len(series), games=len(seen), crossPolicy=cross, betaPlaymakerErrors=beta_errors, betaForcedSearches=forced_searches, betaFinishReasons=finish_reasons, decks=decks, selected=selected, selectedClassic=classic, limits=report['limits'])
    output.mkdir(parents=True)
    (output/'sessions-analysis.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps(dict(games=len(seen), series=len(series), audited=True, crossPolicy=cross, betaPlaymakerErrors=len(beta_errors), betaForcedSearches=forced_searches, selectedHard=len(selected), selectedClassic=len(classic), lowestHard=[r for r in decks if r['group']=='hard'][:5]), ensure_ascii=False))


if __name__ == '__main__':
    main()

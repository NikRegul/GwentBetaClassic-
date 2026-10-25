"""Verify the frozen four-group league and report paired/deck uncertainty."""
import argparse
import hashlib
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values, rng, repetitions=4000):
    # Resample whole mirror pairs, never the two seats independently. Enclose
    # this with a Wilson interval using the number of pairs as effective n,
    # so six identical observed pair results cannot imply zero uncertainty.
    n=len(values)
    if not n:
        return [0.,1.]
    mean=sum(values)/n
    draws=sorted(sum(rng.choice(values) for _ in values)/n for _ in range(repetitions))
    z=1.959963984540054;den=1+z*z/n
    centre=(mean+z*z/(2*n))/den
    margin=z*math.sqrt(mean*(1-mean)/n+z*z/(4*n*n))/den
    return [max(0.,min(draws[int(.025*repetitions)],centre-margin)),
            min(1.,max(draws[min(repetitions-1,int(.975*repetitions))],centre+margin))]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('--audit-only',action='store_true')
    args=parser.parse_args();out=args.directory.resolve()
    plan=json.loads((out/'plan.json').read_text('utf8'));digest=sha(out/'plan.json')
    assert plan['kind']=='paired-four-group-tournament' and plan['ratingPermitted']
    for name,value in plan['codeFiles'].items():
        assert sha(out/'frozen'/name)==value, name
    assert sha(Path(plan['config']['current'])/'manifest.json')==plan['commonManifestSha256']
    assert sha(Path(plan['config']['policy091'])/'comparison.json')==plan['policyProofSha256']
    assert sha(Path(plan['config']['originalRosters']))==plan['originalRostersSha256']
    schedule=plan['schedule'];by_id={r['id']:r for r in schedule}
    assert len(schedule)==1104 and len(by_id)==len(schedule)
    pairs=defaultdict(list);groups=defaultdict(set);grids=Counter();records={}
    for entry in schedule:
        assert entry['left']!=entry['right']
        for key in ('left','right'):
            group=entry[key].split(':',1)[0];groups[group].add(entry[key])
        pairs[(entry['grid'],entry['pair'])].append(entry)
        grids[entry['grid']]+=1
    assert {g:len(v) for g,v in groups.items()}=={'091':46,'092':46,'beta092':46,'betaOriginal':45}
    assert grids=={0:552,1:552}
    for key,pair in pairs.items():
        assert len(pair)==2,key
        a,b=pair;assert a['left']==b['right'] and a['right']==b['left'] and a['seed']==b['seed'],key
    expected={i+'.json' for i in by_id}
    saved={p.name for p in (out/'games').glob('*.json')};assert saved<=expected
    prefix=True
    for entry in schedule:
        file=out/'games'/(entry['id']+'.json')
        if not file.exists():prefix=False;continue
        assert prefix,'Saved results must be a consecutive prefix'
        result=json.loads(file.read_text('utf8'))
        for key in ('id','left','right','seed'):assert result[key]==entry[key],(entry['id'],key)
        assert result['planSha256']==digest and result['status']=='complete',entry['id']
        assert result['winner'] in (1,2,3) and len(result['finalStateSha256'])==64
        records[entry['id']]=result
    audit=dict(planSha256=digest,plannedGames=len(schedule),completedGames=len(records),
               groups={g:len(v) for g,v in groups.items()},grids=dict(grids),mirroredPairs=len(pairs),
               complete=len(records)==len(schedule),inputsUnchanged=True)
    if args.audit_only:
        print(json.dumps(audit));return
    assert audit['complete'],'Wait for every planned game; do not rate a prefix'
    progress=json.loads((out/'progress.json').read_text('utf8'))
    assert progress['status']=='complete' and progress['technicalErrors']==0 and progress['completed']==len(schedule)
    stats={d:dict(key=d,group=g,games=0,wins=0,losses=0,draws=0,pairs=[])
           for g,keys in groups.items() for d in keys}
    group_pairs=defaultdict(list);matchups=defaultdict(list);exposures=Counter();peak=0;forced=0
    for entries in pairs.values():
        a,b=entries;decks=[a['left'],a['right']];scores={d:[] for d in decks}
        for entry in entries:
            result=records[entry['id']];peak=max(peak,result['betaPeakCallbackMs']);forced+=result['betaForcedSearches']
            for side,key in enumerate((entry['left'],entry['right']),1):
                score=.5 if result['winner']==3 else float(result['winner']==side)
                stat=stats[key];stat['games']+=1
                stat['draws' if score==.5 else 'wins' if score==1 else 'losses']+=1
                scores[key].append(score);exposures[key]+=1
        for key,values in scores.items():
            score=sum(values)/2;stats[key]['pairs'].append(score)
            group=key.split(':',1)[0];other=next(d.split(':',1)[0] for d in decks if d!=key)
            group_pairs[group].append(score);matchups[(group,other)].append(score)
    rng=random.Random(924040923)
    deck_rows=[]
    for key in sorted(stats):
        stat=stats[key];values=stat.pop('pairs')
        stat.update(scoreRate=(stat['wins']+.5*stat['draws'])/stat['games'],mirrorPairs=len(values),interval95Approx=interval(values,rng))
        deck_rows.append(stat)
    deck_rows.sort(key=lambda r:(-r['scoreRate'],r['key']))
    group_rows=[]
    for group,values in sorted(group_pairs.items()):
        rows=[r for r in deck_rows if r['group']==group]
        group_rows.append(dict(group=group,games=sum(r['games'] for r in rows),mirrorPairs=len(values),
                               scoreRate=sum(values)/len(values),deckWeightedScoreRate=sum(r['scoreRate'] for r in rows)/len(rows),
                               interval95Approx=interval(values,rng)))
    group_rows.sort(key=lambda r:-r['deckWeightedScoreRate'])
    comparison=[dict(group=a,opponent=b,mirrorPairs=len(v),scoreRate=sum(v)/len(v),interval95Approx=interval(v,rng)) for (a,b),v in sorted(matchups.items())]
    report=dict(**audit,informationAsymmetry='Beta sees full hands/decks;091/092 retain their own original information limits. These scores compare complete configured agents, not equal-information algorithms.',
                betaProfileScope='Only the five original faction Practice profiles were tested (DepthOfChecking1/MaxTimeAllowed3), not all229 profiles. Strongest original Beta profile has not been established.',
                format='Paired league, two rotated grids; no knockout bracket.45 original assets vs46 other decks: one extra exposure per grid is reported explicitly.',
                uncertainty='Approximate95% envelope: bootstrap whole mirror pairs plus Wilson effective pair count. Opponent mixes are fixed and small per deck; intervals do not prove generalization to human decks. Group exposure-weighted and equal-deck means are separate.',
                groupsRanking=group_rows,matchups=comparison,decksRanking=deck_rows,deckExposures=dict(sorted(exposures.items())),
                betaPeakCallbackMs=peak,betaForcedSearches=forced,nativeSteamDeckAcceptance=False)
    destination=out/'analysis';destination.mkdir(exist_ok=True)
    (destination/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    def percent(v):return f'{v*100:.1f}%'
    def limits(v):return '–'.join(percent(x) for x in v)
    lines=['# Сравнение четырёх групп — две фиксированные сетки','',
           f'Проверены все {len(records)} партий, {len(pairs)} зеркальных пар. Ошибок нет; исходники и план не изменены.','',
           'Бета видит скрытые руки и колоды. У 0.9.1/0.9.2 сохранены исходные ограничения информации. Это сравнение настроенных соперников с указанной асимметрией.','',
           'Группа беты использует только пять исходных фракционных Practice-профилей (depth1/time3). Остальные профили не сравнивались; сильнейший исходный профиль беты не установлен. Результат нельзя распространять на все229 профилей.','',
           '| Группа | Партий | Очки | Среднее по колодам | Приблизительный интервал95% |',
           '|---|---:|---:|---:|---:|']
    lines += [f"| {r['group']} | {r['games']} | {percent(r['scoreRate'])} | {percent(r['deckWeightedScoreRate'])} | {limits(r['interval95Approx'])} |" for r in group_rows]
    lines += ['', 'Интервалы учитывают зеркальные пары целиком. Для защиты от ложной уверенности при одинаковых исходах они расширены оценкой Wilson с числом пар как эффективным объёмом. Это приближение для данной сетки, а не доказательство силы против любых колод человека.','',
              'Формат — парная лига, а не выбывание. В группе подлинных колод 45 участников против46 в остальных: повторное участие одной колоды в каждой сетке показано в JSON; среднее по колодам дано отдельно.','',
              '| Колода | Партий | Побед/ничьих/поражений | Очки | Интервал95% |','|---|---:|---:|---:|---:|']
    lines += [f"| {r['key']} | {r['games']} | {r['wins']}/{r['draws']}/{r['losses']} | {percent(r['scoreRate'])} | {limits(r['interval95Approx'])} |" for r in deck_rows]
    lines += ['',f'Максимум одного callback поиска беты: {peak}мс на этом компьютере; это не нативная проверка SteamDeck. Принудительных остановок по исходному лимиту времени: {forced}.']
    (destination/'REPORT_RU.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(complete=True,groupsRanking=group_rows,report=str(destination/'REPORT_RU.md')),ensure_ascii=False))


if __name__=='__main__':main()

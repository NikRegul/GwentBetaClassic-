"""Validate complete knockout graphs and rank decks by balanced mean placement."""
from pathlib import Path
import csv,datetime,hashlib,html,json,math,statistics,sys

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf8'))
def main():
    out=Path(sys.argv[1]).resolve();config=read(out/'config.json');progress=read(out/'progress.json');identity=read(out/'identity.json')
    assert progress['complete'] and progress['errors']==0
    assert identity['configSha256']==sha(out/'config.json') and identity['scheduleSha256']==sha(out/'schedule.json')
    assert config['metadataSha256']==sha(out/'deck-metadata.json')
    for n,h in identity['tools'].items():assert sha(out/'runner'/n)==h
    manifest=read(Path(config['snapshot'])/'manifest.json');assert manifest['fingerprint']==identity['fingerprint']
    for n,h in manifest['snapshotFiles'].items():assert sha(Path(config['snapshot'])/n)==h
    meta=read(out/'deck-metadata.json');pool=[d['presetId'] for d in meta['decks']];size=len(pool)
    assert size in (46,92) and len(set(pool))==size and meta['fingerprint']==manifest['fingerprint']
    if config.get('versioned'):
        original=read(Path(config['originalSnapshot'])/'manifest.json')
        assert original['fingerprint']==config['originalFingerprint']==meta['originalFingerprint']
        for n,h in original['snapshotFiles'].items():assert sha(Path(config['originalSnapshot'])/n)==h
        for n,h in config['oldPolicyFiles'].items():assert sha(Path(config['oldPolicy'])/n)==h
        assert set(pool)==set(manifest['presets'])|{d+100 for d in original['presets']} and size==92
        assert all(d['version']==('0.9.1' if d['presetId']>=100 else '0.9.2') for d in meta['decks'])
    else:assert set(pool)==set(manifest['presets']) and size==46
    plan=read(out/'schedule.json');nodes={n['id']:n for n in plan['nodes']};done={};game_times=[];games=[]
    for line in (out/'series.jsonl').read_text('utf8').splitlines():
        r=json.loads(line);assert r['id'] in nodes and r['id'] not in done;n=nodes[r['id']]
        def resolve(ref):return ref.get('deck') if 'deck' in ref else done[ref['winner']]['winnerDeck']
        a,b=resolve(n['a']),resolve(n['b']);assert a==r['a'] and b==r['b'] and a!=b
        assert r['bracket']==n['bracket'] and r['stage']==n['stage'] and 4<=len(r['games'])<=len(n['seeds'])*2 and len(r['games'])%2==0
        points=0
        for i,g in enumerate(r['games']):
            reverse=i%2==1;assert not g.get('error') and g['winner'] in (1,2,3)
            assert (g['left'],g['right'],g['seed'])==((b,a,n['seeds'][i//2]) if reverse else (a,b,n['seeds'][i//2]))
            points+=.5 if g['winner']==3 else int((g['left'] if g['winner']==1 else g['right'])==a)
            if i%2==1 and i>=3 and i<len(r['games'])-1:assert points==(i+1)/2,'Continued decided series'
            game_times.append(g['milliseconds']/1000);games.append(g)
        tied=points==len(r['games'])/2
        assert not tied or len(r['games'])==len(n['seeds'])*2
        winner=(b if n['lot'] else a) if tied else (a if points>len(r['games'])/2 else b)
        assert r['pointsA']==points and r['lotUsed']==tied and r['winnerDeck']==winner and r['loserDeck']==(b if winner==a else a)
        done[r['id']]=r
    assert len(done)==len(nodes)==progress['completedSeries'] and len(games)==progress['completedGames']
    times=sorted(game_times)
    speed=dict(games=len(games),seconds=progress['totalSeconds'],gamesPerSecond=len(games)/progress['totalSeconds'],meanGameSeconds=statistics.mean(times),p95GameSeconds=times[min(len(times)-1,math.ceil(len(times)*.95)-1)],maximumGameSeconds=max(times),workers=config['workers'])
    if config['benchmark']:
        assert len(done)==size
        (out/'benchmark.json').write_text(json.dumps(dict(identity=identity,speed=speed,complete=True),indent=2)+'\n','utf8');print(json.dumps(speed));return
    assert len(plan['brackets'])==config['cycles']*23 and len(done)==len(plan['brackets'])*(size-1)
    stats={d:dict(presetId=d,title=next(x['title'] for x in meta['decks'] if x['presetId']==d),placements=[],byes=0,titles=0,finals=0,seriesWins=0,seriesLosses=0,lotWins=0,lotLosses=0,wins=0,losses=0,draws=0,opponents=set()) for d in pool}
    main_size=32 if size==46 else 64
    places={0:(main_size+1+size)/2};stage=1;width=main_size
    while width>1:places[stage]=(width/2+1+width)/2;stage+=1;width//=2
    for d in meta['decks']:stats[d['presetId']].update(version=d.get('version'),basePreset=d.get('basePreset',d['presetId']))
    bracket_rows=[]
    for bracket in plan['brackets']:
        records=[r for r in done.values() if r['bracket']==bracket['id']];assert len(records)==size-1
        losers=[r['loserDeck'] for r in records];final=done[bracket['final']];winner=final['winnerDeck']
        assert len(set(losers))==size-1 and set(losers+[winner])==set(pool)
        for d in bracket['byes']:stats[d]['byes']+=1
        for r in records:
            stats[r['loserDeck']]['placements'].append(places[r['stage']])
        stats[winner]['placements'].append(1);stats[winner]['titles']+=1
        stats[winner]['finals']+=1;stats[final['loserDeck']]['finals']+=1
        bracket_rows.append(dict(bracket=bracket['id'],winner=winner,runnerUp=final['loserDeck'],finalByLot=final['lotUsed']))
    for r in done.values():
        stats[r['winnerDeck']]['seriesWins']+=1;stats[r['loserDeck']]['seriesLosses']+=1
        stats[r['a']]['opponents'].add(r['b']);stats[r['b']]['opponents'].add(r['a'])
        if r['lotUsed']:stats[r['winnerDeck']]['lotWins']+=1;stats[r['loserDeck']]['lotLosses']+=1
        for g in r['games']:
            for seat,d in [(1,g['left']),(2,g['right'])]:stats[d]['draws' if g['winner']==3 else 'wins' if g['winner']==seat else 'losses']+=1
    ranking=[]
    for d in pool:
        s=stats[d];assert len(s['placements'])==len(plan['brackets']) and s['byes']==config['cycles']*9
        mean=statistics.mean(s['placements']);se=statistics.stdev(s['placements'])/math.sqrt(len(s['placements']))
        s.update(meanPlacement=mean,approximate95=[max(1,mean-1.96*se),min(size,mean+1.96*se)],opponents=len(s['opponents']))
        ranking.append(s)
    ranking.sort(key=lambda s:(s['meanPlacement'],-s['titles'],-s['finals'],s['presetId']))
    finished=datetime.datetime.fromisoformat(progress.get('finishedAt') or progress['updatedAt']);deadline=datetime.datetime.fromisoformat(config['deadline'])
    report=dict(identity=identity,complete=True,strength=4,brackets=len(plan['brackets']),series=len(done),games=len(games),errors=0,seriesByLot=sum(r['lotUsed'] for r in done.values()),speed=speed,bracketResults=bracket_rows,ranking=ranking,deadline=config['deadline'],finishedAt=finished.isoformat(),finishedBeforeDeadline=finished<=deadline,reportGeneratedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),nativeGameTested=False)
    if config.get('versioned'):
        differences=[]
        for i in range(len(plan['brackets'])):
            old=statistics.mean(s['placements'][i] for s in ranking if s['version']=='0.9.1')
            new=statistics.mean(s['placements'][i] for s in ranking if s['version']=='0.9.2')
            differences.append(old-new)
        mean=statistics.mean(differences);se=statistics.stdev(differences)/math.sqrt(len(differences));ci=[mean-2.576*se,mean+2.576*se]
        cross=[g for g in games if stats[g['left']]['version']!=stats[g['right']]['version']]
        mixed=[r for r in done.values() if stats[r['a']]['version']!=stats[r['b']]['version']]
        report['versionComparison']=dict(scope='combined policy and historical roster; common current card mechanics',original='0.9.1',candidate='0.9.2-final16:00',decksPerVersion=46,pairedBrackets=len(differences),meanPlacementImprovement=mean,approximate99=ci,confirmedBetter=ci[0]>0,
            newHeadToHeadWins=sum(g['winner']!=3 and stats[g['left'] if g['winner']==1 else g['right']]['version']=='0.9.2' for g in cross),
            oldHeadToHeadWins=sum(g['winner']!=3 and stats[g['left'] if g['winner']==1 else g['right']]['version']=='0.9.1' for g in cross),headToHeadDraws=sum(g['winner']==3 for g in cross),headToHeadSeries=len(mixed),headToHeadSeriesByLot=sum(r['lotUsed'] for r in mixed),
            newSeriesWins=sum(stats[r['winnerDeck']]['version']=='0.9.2' for r in mixed),oldSeriesWins=sum(stats[r['winnerDeck']]['version']=='0.9.1' for r in mixed),
            versions={v:dict(titles=sum(s['titles'] for s in ranking if s['version']==v),finals=sum(s['finals'] for s in ranking if s['version']==v),meanPlacement=statistics.mean(s['meanPlacement'] for s in ranking if s['version']==v)) for v in ('0.9.1','0.9.2')})
    (out/'ratings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    lines=['# Рейтинг колод: повторные сетки на выбывание','',f"Высокая сложность; {len(pool)} колод, {len(plan['brackets'])} сеток, {len(done)} серий, {len(games)} партий. Ошибок нет.",'',
           'Каждая серия: минимум четыре партии на двух разных раздачах с обеими сторонами; при равенстве добавляются зеркальные пары до заранее установленного предела. Только оставшаяся ничья разрешается заранее выбранным нейтральным жребием; он не считается победой в сыгранной партии.',
           f"Серий, решённых последним жребием: {report['seriesByLot']}. У каждой колоды одинаково пропусков первого круга: {config['cycles']*9}.",'',
           'Основной порядок — среднее место по всем сеткам (меньше лучше). Проигравшие в одном круге делят диапазон мест; показан его центр. Интервалы средних мест приблизительные, по разбросу результатов между сетками; близкие результаты не доказывают различие силы. Процент побед в сыгранных партиях здесь описательный: соперники зависят от продвижения в сетке. Это рейтинг автопилотов в данном формате, а не обещание победы над человеком.','',
           '| № | Колода | Среднее место | Примерный 95% интервал | Титулы | Финалы | Серии В–П | Партии В–П–Н | Соперников |','|---:|---|---:|---|---:|---:|---|---|---:|']
    for i,s in enumerate(ranking,1):
        ci=s['approximate95'];lines.append(f"| {i} | {s['title'].replace('|','/')} | {s['meanPlacement']:.2f} | {ci[0]:.2f}–{ci[1]:.2f} | {s['titles']} | {s['finals']} | {s['seriesWins']}–{s['seriesLosses']} | {s['wins']}–{s['losses']}–{s['draws']} | {s['opponents']} |")
    if config.get('versioned'):
        v=report['versionComparison'];ci=v['approximate99'];lines[4:4]=[
            'Сравниваются ИСХОДНАЯ 0.9.1 и итоговая 0.9.2 после дневных улучшений. У каждой версии собственные составы колод, лидер, веса и политика решений; правила карт общие — текущая исправленная боевая механика. Результат относится к совокупности ИИ и колод, отдельно эффект алгоритма он не выделяет.','',
            f"Встречи разных версий: 0.9.2 выиграла {v['newHeadToHeadWins']} партий, 0.9.1 — {v['oldHeadToHeadWins']}, ничьих {v['headToHeadDraws']}. Серии: {v['newSeriesWins']}–{v['oldSeriesWins']}, из них {v['headToHeadSeriesByLot']} решены последним жребием.",
            f"Улучшение среднего места новой версии: {v['meanPlacementImprovement']:.2f} (положительное лучше); приблизительный 99% интервал по независимым сеткам {ci[0]:.2f}…{ci[1]:.2f}. Критерий преимущества выполнен: {v['confirmedBetter']}. Очные проценты описательные: дальнейшие соперники зависят от продвижения по сетке.",'']
    text='\n'.join(lines)+'\n';(out/'RATING_RU.md').write_text(text,'utf8')
    with (out/'ratings.csv').open('w',newline='',encoding='utf-8-sig') as f:
        cols=['presetId','version','basePreset','title','meanPlacement','titles','finals','seriesWins','seriesLosses','wins','losses','draws','byes','opponents'];w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(ranking)
    trs=''.join('<tr>'+''.join('<td>'+html.escape(str(v))+'</td>' for v in [i,s['title'],f"{s['meanPlacement']:.2f}",s['titles'],s['finals'],f"{s['wins']} / {s['losses']} / {s['draws']}"])+'</tr>' for i,s in enumerate(ranking,1))
    (out/'RATING.html').write_text('<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Рейтинг колод</title><style>body{font:16px system-ui;margin:2em;max-width:1200px;background:#15191d;color:#eee}table{border-collapse:collapse;width:100%}td,th{padding:.65em;border-bottom:1px solid #53606c;text-align:left}input{font:inherit;padding:.6em}tr:nth-child(even){background:#20282e}</style><h1>Рейтинг колод</h1><p>'+html.escape(lines[2])+'</p><p>Среднее место по сеткам; одинаковое число пропусков первого круга. Подробный протокол и неопределённость — в RATING_RU.md.</p><input placeholder="Найти колоду" oninput="for(const r of document.querySelectorAll(\'tbody tr\'))r.hidden=!r.textContent.toLowerCase().includes(this.value.toLowerCase())"><table><thead><tr><th>№</th><th>Колода</th><th>Среднее место</th><th>Титулы</th><th>Финалы</th><th>Партии В / П / Н</th></tr></thead><tbody>'+trs+'</tbody></table></html>','utf8')
    print(json.dumps(dict(complete=True,decks=size,brackets=report['brackets'],games=report['games'],top=[s['presetId'] for s in ranking[:5]])))

if __name__=='__main__':main()

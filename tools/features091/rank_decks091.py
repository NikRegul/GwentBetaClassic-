"""Describe deck results using only balanced maximum-vs-maximum games."""
from pathlib import Path
from collections import defaultdict
import argparse, json, math
ROOT=Path(__file__).resolve().parents[2]

def rank(experiment,partial=False):
    shards=sorted(experiment.glob('versions-??/report.json'));rows={};groups=defaultdict(list)
    titles={p['presetId']:p['title'] for p in json.loads((experiment/'versions-00/profiles.json').read_text('utf8'))['profiles']}
    games=0
    for p in shards:
        r=json.loads(p.read_text('utf8'));assert not r['errors']
        if not partial:assert r['complete']
        for g in r['games']:
            games+=1
            for seat,deck,enemy in [(1,g['left'],g['right']),(2,g['right'],g['left'])]:
                row=rows.setdefault(deck,dict(preset=deck,title=titles[deck],wins=0,losses=0,draws=0,opponents=set(),policies={'candidate':[0,0],'baseline':[0,0]}))
                score=.5 if g['winner']==3 else float(g['winner']==seat)
                row['draws' if score==.5 else 'wins' if score==1 else 'losses']+=1;row['opponents'].add(enemy)
                policy='candidate' if seat==g['newSeat']+1 else 'baseline'
                row['policies'][policy][0]+=score;row['policies'][policy][1]+=1
                groups[deck,p.parent.name,g['block']].append(score)
    for deck,row in rows.items():
        blocks=[sum(values)/4 for key,values in groups.items() if key[0]==deck and len(values)==4]
        n=len(blocks);mean=sum(blocks)/n if n else .5
        se=math.sqrt(sum((x-mean)**2 for x in blocks)/(n-1)/n) if n>1 else .5
        row.update(games=row['wins']+row['losses']+row['draws'],scoreRate=(row['wins']+.5*row['draws'])/(row['wins']+row['losses']+row['draws']),
                   completeBlocks=n,opponents=sorted(row['opponents']),lower99=max(0,mean-2.576*se),upper99=min(1,mean+2.576*se))
        row['category']='strong-in-sample' if row['scoreRate']>=.65 and row['lower99']>.5 else 'weak-in-sample' if row['scoreRate']<=.35 and row['upper99']<.5 else 'middle-or-matchup-dependent'
    if not partial:
        shards_expected=json.loads((experiment/'identity.json').read_text('utf8'))['shards']
        assert len(shards)==shards_expected and games==184*shards_expected
        assert len(rows)==46 and all(r['games']==8*shards_expected and r['completeBlocks']==2*shards_expected for r in rows.values())
    return dict(complete=not partial,totalGames=games,experiment='maximum versus previous maximum, both policy assignments',
                fingerprint=json.loads((experiment/'identity.json').read_text('utf8'))['candidate'],
                limitation='Simulation of frozen pre-Bran-fix rosters. Not a human tier list; intervals are approximate per-deck block intervals, not simultaneous confidence for all 46 decks.',
                decks=sorted(rows.values(),key=lambda r:-r['scoreRate']))

def main():
    p=argparse.ArgumentParser();p.add_argument('--experiment',type=Path,default=ROOT/'BetaGwent/build/ai091/final18');p.add_argument('--partial',action='store_true');p.add_argument('--output',type=Path);p.add_argument('--markdown',type=Path);a=p.parse_args()
    report=rank(a.experiment.resolve(),a.partial)
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    if a.markdown:
        assert report['complete'],'Do not publish a partial ranking as final'
        lines=['# Результаты колод под управлением ИИ — 0.9.1','',
            'Это рейтинг результата управления колодой ИИ, а не силы колоды в руках человека. Пользователь успешно играет Накерами, Роем и Проклятием Адды; их низкие показатели требуют проверки стратегии ИИ, а не автоматического ослабления/замены состава.',
            '',f"Всего {report['totalGames']} партий максимума против прежнего максимума; каждая колода играла 144 партии против 36 разных соперников, по 72 партии каждой версией ИИ. Лёгкая сложность в этот рейтинг не включена. Начальные раздачи и назначения политик парные. Снимок: `{report['fingerprint']}`.",
            '', 'Относится к составам до исправления Брана. Трисс в пресете 96 позже заменена Морским Вепрем; прежний процент не является измерением исправленного состава.',
            '', 'Интервалы — приближённые 99% по 36 группам связанных партий для каждой колоды. Это не одновременная гарантия ранжирования всех 46 колод. В каждом конкретном противостоянии только одна seed-раздача; все возможные матчапы и человеческие линии не покрыты.',
            '', '| Место | Колода | Победы:поражения:ничьи | Доля очков | 99% интервал | Новый / прежний ИИ |', '|---:|---|---:|---:|---:|---:|']
        for i,r in enumerate(report['decks'],1):
            rates=[100*r['policies'][p][0]/r['policies'][p][1] for p in ['candidate','baseline']]
            lines.append(f"| {i} | {r['title']} | {r['wins']}:{r['losses']}:{r['draws']} | {100*r['scoreRate']:.1f}% | {100*r['lower99']:.1f}–{100*r['upper99']:.1f}% | {rates[0]:.1f}% / {rates[1]:.1f}% |")
        lines+=['','Нельзя автоматически заключать, что низкая строка означает слабый архетип. Проверять нужно отдельно: законность и совместимость состава, правильность реализации карт, выбор муллигана, подготовку комбинации, распределение ресурсов по раундам и качество паса.',
                '', 'Для трёх колод с подтверждённой пользователем человеческой силой подготовлен [разбор текущих стратегий](AI_THREE_DECK_STRATEGIES_091_RU.md). Их составы сохранены до обсуждения человеческих линий.']
        a.markdown.write_text('\n'.join(lines)+'\n',encoding='utf8')
    print(json.dumps(dict(complete=report['complete'],games=report['totalGames'],top=report['decks'][:7],bottom=report['decks'][-7:]),ensure_ascii=False,indent=2))
if __name__=='__main__':main()

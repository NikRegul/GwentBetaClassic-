"""Validate complete balanced tournaments and publish deck/matchup rankings.

Deal blocks (two mirrored games) are the sampling units. Hoeffding bounds
handle their dependence without pretending every mirrored game is independent.
"""
import argparse, csv, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
LEVELS={2:'Лёгкая',3:'Обычная',4:'Высокая'}
FACTIONS={2:'Чудовища',4:'Нильфгаард',8:'Королевства Севера',16:'Скоя’таэли',32:'Скеллиге'}

def interval(mean,n):
    radius=math.sqrt(math.log(40)/(2*n))
    return [max(0,mean-radius),min(1,mean+radius)]

def stats(values):
    games=[g for value in values for g in value]
    w=games.count(1);d=games.count(.5);l=games.count(0);n=len(games)
    mean=(w+d/2)/n
    return dict(games=n,blocks=len(values),wins=w,losses=l,draws=d,winRate=w/n,score=mean,ci95=interval(mean,len(values)))

def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();root=a.directory.resolve()
    progress=json.loads((root/'progress.json').read_text('utf8'))
    assert progress['complete'] and progress['errors']==0,'Only a complete error-free tournament can be ranked'
    config=json.loads((root/'config.json').read_text('utf8'))
    records=[json.loads(x) for x in (root/'blocks.jsonl').read_text('utf8').splitlines() if x]
    tasks=json.loads((root/'schedule.json').read_text('utf8'))
    assert len(records)==len(tasks) and len({x['id'] for x in records})==len(tasks)
    schedule={x['id']:x for x in tasks}
    manifest=json.loads((Path(config['snapshot'])/'manifest.json').read_text('utf8'));pool=manifest['presets']
    metadata_path=root/'deck-metadata.json'
    if metadata_path.exists():
        frozen_metadata=json.loads(metadata_path.read_text('utf8'));assert frozen_metadata['fingerprint']==manifest['fingerprint']
        profiles=frozen_metadata['decks']
    else:
        assert manifest['fingerprint']=='contract-only','Real ratings require names and rosters from the frozen rules'
        profiles=json.loads((ROOT/'data/beta924/ai/rules.json').read_text('utf8'))['profiles']
    names={x['presetId']:x['title'] for x in profiles}
    metadata={x['presetId']:x for x in profiles}
    results={s:{'decks':{d:[] for d in pool},'pairs':{},'seats':{1:[],2:[]}} for s in map(int,config['blocksByStrength'])}
    for r in records:
        assert all(r[k]==v for k,v in schedule[r['id']].items())
        s=r['strength'];out=results[s];key=(r['a'],r['b']);assert len(r['games'])==2
        samples={r['a']:[],r['b']:[]}
        for reverse,g in zip([False,True],r['games']):
            assert g['reverse']==reverse and not g.get('error') and g['winner'] in (1,2,3) and g['seed']==r['seed']
            assert [g['left'],g['right']]==([r['b'],r['a']] if reverse else [r['a'],r['b']])
            for seat,d in [(1,g['left']),(2,g['right'])]:samples[d].append(.5 if g['winner']==3 else int(g['winner']==seat))
            out['seats'][1].append(.5 if g['winner']==3 else int(g['winner']==1))
            out['seats'][2].append(.5 if g['winner']==3 else int(g['winner']==2))
        for d in samples:out['decks'][d].append(samples[d])
        out['pairs'].setdefault(key,[]).append(samples[r['a']])
    rating={};rows=[];pair_rows=[]
    for strength,out in results.items():
        count=config['blocksByStrength'][str(strength)]
        assert len(out['pairs'])==1035 and all(len(v)==count for v in out['pairs'].values())
        decks={d:{'id':d,'title':names[d],'faction':FACTIONS[metadata[d]['faction']],'leader':metadata[d]['requestedLeader'],**stats(out['decks'][d]),'matchups':[],'versusFactions':{}} for d in pool}
        assert all(d['games']==90*count for d in decks.values())
        for (a,b),values in out['pairs'].items():
            for d,enemy,seq in [(a,b,values),(b,a,[[1-x for x in v] for v in values])]:
                rec={'opponent':enemy,'title':names[enemy],**stats(seq)}
                decks[d]['matchups'].append(rec)
                decks[d]['versusFactions'].setdefault(metadata[enemy]['faction'],[]).extend(seq)
                pair_rows.append({'difficulty':LEVELS[strength],'deck':d,'title':names[d],'opponent':enemy,'opponentTitle':names[enemy],**{k:v for k,v in rec.items() if k not in ('opponent','title','ci95')},'ci95Low':rec['ci95'][0],'ci95High':rec['ci95'][1]})
        ordered=sorted(decks.values(),key=lambda d:(-d['score'],-d['winRate'],d['id']))
        for rank,d in enumerate(ordered,1):
            d['versusFactions']=[{'faction':FACTIONS[faction],**stats(values)} for faction,values in d['versusFactions'].items()]
            d['versusFactions'].sort(key=lambda x:-x['score'])
            d['rank']=rank;d['matchups'].sort(key=lambda m:(-m['score'],m['opponent']))
            d['best']=d['matchups'][:3];d['worst']=list(reversed(d['matchups'][-3:]))
            rows.append({'difficulty':LEVELS[strength],**{k:v for k,v in d.items() if k not in ('matchups','best','worst','ci95','versusFactions')},'ci95Low':d['ci95'][0],'ci95High':d['ci95'][1]})
        rating[strength]={'title':LEVELS[strength],'decks':ordered,'games':sum(d['games'] for d in ordered)//2,'gamesPerPair':count*2,'seedBlocksPerPair':count,'leftScore':sum(out['seats'][1])/len(out['seats'][1])}
    report={'identity':progress['identity'],'metadataSha256':hashlib.sha256(metadata_path.read_bytes()).hexdigest() if metadata_path.exists() else None,'reportToolSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'complete':True,'games':progress['completedGames'],'errors':0,'confidence':'Individual 95% Hoeffding bounds; independent mirrored deal blocks, not individual games; not simultaneous across selected matchups','rankBy':'wins + half draws against equal frequency of all other 45 decks','humanStrengthMeasured':False,'nativeGameplayVerified':False,'levels':rating}
    (root/'ratings.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    for name,values in [('rankings.csv',rows),('matchups.csv',pair_rows)]:
        with (root/name).open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fieldnames=list(values[0]));w.writeheader();w.writerows(values)
    pct=lambda x:f'{100*x:.1f}%'
    parts=['# Рейтинг 46 колод и матчапов\n',f"Завершено **{report['games']:,} партий**, ошибок нет. Все 1035 пар на каждом уровне, одинаковая частота соперников и обе стороны. Код ИИ: `{manifest['fingerprint']}`.\n",
    'Это рейтинг колод под управлением проверяемого ИИ. Он не измеряет их потолок под управлением человека и не доказывает рост силы ИИ против игрока.\n',
    'Места отсортированы по доле очков: победа = 1, ничья = 0,5. Процент побед приведён отдельно. 95% интервалы рассчитаны по независимым парам раздач с переменой сторон; две партии одной пары не считаются независимыми. Использована консервативная граница Хёффдинга. Случайность уменьшается размером выборки, но не исчезает.\n',
    'Лучшие и худшие соперники — наблюдаемые результаты. Интервалы относятся к отдельным оценкам; выбор крайних результатов среди 45 соперников увеличивает риск случайного лидерства. Пересечение интервала с 50% не подтверждает преимущество. Близкие места в общем рейтинге также не следует считать доказанно различными.\n']
    for strength in [4,3,2]:
        if strength not in rating:continue
        level=rating[strength]
        parts += [f"## {level['title']} сложность\n",f"{level['games']:,} партий; {level['gamesPerPair']} на каждую пару ({level['seedBlocksPerPair']} независимых раздач × 2 стороны). Очки левой стороны: {pct(level['leftScore'])}.\n",
        '| Место | Колода | Партий | Побед | Ничьих | Очки | 95% интервал очков | Хорошие матчапы, очки | Плохие матчапы, очки |',
        '|---:|---|---:|---:|---:|---:|---|---|---|']
        for d in level['decks']:
            def matchlist(key):return '; '.join(f"{m['title']} {pct(m['score'])}" for m in d[key])
            parts.append(f"| {d['rank']} | {d['title']} [#{d['id']}] | {d['games']} | {pct(d['winRate'])} | {d['draws']} | {pct(d['score'])} | {pct(d['ci95'][0])}–{pct(d['ci95'][1])} | {matchlist('best')} | {matchlist('worst')} |")
        parts.append('')
        matrix={d['id']:{m['opponent']:m['score'] for m in d['matchups']} for d in level['decks']}
        with (root/f'matrix-strength{strength}.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.writer(f);w.writerow(['Колода / соперник']+[f"{names[d]} [#{d}]" for d in pool])
            for d in pool:w.writerow([f'{names[d]} [#{d}]']+['' if d==e else matrix[d][e] for e in pool])
    (root/'RATING_RU.md').write_text('\n'.join(parts)+'\n','utf8')
    # Standalone searchable report. Full data is embedded; no network is used.
    payload=json.dumps(report,ensure_ascii=False).replace('<','\\u003c')
    page='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Рейтинг колод Gwent</title>
<style>body{font:16px system-ui;background:#111820;color:#e4eaf0;margin:30px}h1{font-size:27px}select,input{font:inherit;padding:8px;background:#202c38;color:inherit;border:1px solid #647384;margin-right:12px}table{border-collapse:collapse;width:100%;margin-top:22px}th,td{padding:10px;text-align:left;border-bottom:1px solid #354350}th{position:sticky;top:0;background:#17232e}tr:hover{background:#203142}.muted{color:#acbbc8;max-width:1100px}button{font:inherit;background:none;border:0;color:#8bc9ff;cursor:pointer;text-align:left}#detail{padding:20px;background:#192735;margin-top:24px}small{color:#acbbc8}</style>
<h1>46 колод: рейтинг и матчапы</h1><p class="muted">99 360 партий. Колоды играют под управлением ИИ. Места определены по очкам (победа + половина ничьих). Интервалы консервативные, по независимым раздачам с переменой сторон. Близкие места и отдельные матчапы могут различаться случайно.</p>
<select id="level"><option value="4">Высокая</option><option value="3">Обычная</option><option value="2">Лёгкая</option></select><input id="search" placeholder="Найти колоду"><span id="count"></span>
<table><thead><tr><th>Место</th><th>Колода</th><th>Партий</th><th>Победы</th><th>Очки</th><th>95% интервал очков</th><th>Лучший соперник</th><th>Худший соперник</th></tr></thead><tbody id="body"></tbody></table><section id="detail" hidden></section>
<script>const data=PAYLOAD;const $=id=>document.getElementById(id),pct=x=>(100*x).toFixed(1)+'%',esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function render(){const l=data.levels[$('level').value],q=$('search').value.toLowerCase();$('count').textContent=l.games.toLocaleString('ru')+' партий, '+l.gamesPerPair+' на матчап';$('detail').hidden=true;$('body').innerHTML=l.decks.filter(d=>d.title.toLowerCase().includes(q)).map(d=>`<tr><td>${d.rank}</td><td><button data-id="${d.id}">${esc(d.title)}</button><br><small>${esc(d.faction)} · #${d.id}</small></td><td>${d.games}</td><td>${pct(d.winRate)}</td><td>${pct(d.score)}</td><td>${d.ci95.map(pct).join(' – ')}</td><td>${esc(d.best[0].title)} ${pct(d.best[0].score)}</td><td>${esc(d.worst[0].title)} ${pct(d.worst[0].score)}</td></tr>`).join('');}
$('level').onchange=render;$('search').oninput=render;$('body').onclick=e=>{const b=e.target.closest('button');if(!b)return;const d=data.levels[$('level').value].decks.find(d=>d.id===+b.dataset.id);$('detail').hidden=false;$('detail').innerHTML='<h2>'+esc(d.title)+': все соперники</h2><p>'+esc(d.faction)+' · '+esc(d.leader)+'</p><h3>Против фракций</h3><table><tr><th>Фракция</th><th>Партий</th><th>Очки</th><th>95% интервал</th></tr>'+d.versusFactions.map(m=>`<tr><td>${esc(m.faction)}</td><td>${m.games}</td><td>${pct(m.score)}</td><td>${m.ci95.map(pct).join(' – ')}</td></tr>`).join('')+'</table><h3>Против отдельных колод</h3><p class="muted">Наблюдаемые результаты. Интервалы отдельные, без поправки на выбор лучших из 45 соперников.</p><table><tr><th>Соперник</th><th>Партий</th><th>Победы</th><th>Очки</th><th>95% интервал</th></tr>'+d.matchups.map(m=>`<tr><td>${esc(m.title)}</td><td>${m.games}</td><td>${pct(m.winRate)}</td><td>${pct(m.score)}</td><td>${m.ci95.map(pct).join(' – ')}</td></tr>`).join('')+'</table>';$('detail').scrollIntoView({behavior:'smooth'});};render();</script></html>'''
    (root/'RATING.html').write_text(page.replace('PAYLOAD',payload).replace('99 360 партий',f"{report['games']:,} партий".replace(',',' ')),'utf8')
    print(json.dumps({'complete':True,'games':report['games'],'rows':len(rows),'matchups':len(pair_rows),'report':str(root/'RATING_RU.md')},ensure_ascii=False))

if __name__=='__main__':main()

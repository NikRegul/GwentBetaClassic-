"""Review exact legal original Beta lists against the current46, before import."""
from pathlib import Path
from collections import Counter
import json

ROOT=Path(__file__).resolve().parents[2]
DRAFT=ROOT/'BetaGwent/drafts/day-iteration-20261023'

def main():
    beta=json.loads((DRAFT/'direct-beta-js-rosters-audit-01.json').read_text('utf8'))
    ours=json.loads((DRAFT/'beta-original-js/final092-rosters.json').read_text('utf8'))['decks']
    result=[]
    for d in beta['eligible']:
        matches=[];a=Counter(d['templateIds'])
        for other in ours:
            b=Counter(other['templateIds']);shared=sum((a&b).values());overlap=shared/min(len(d['templateIds']),len(other['templateIds']))
            same_leader=d['leader']==other['leader']
            if overlap>=.8 or (same_leader and overlap>=.65):
                matches.append(dict(preset=other['presetId'],title=other['title'],shared=shared,betaCards=len(d['templateIds']),ourCards=len(other['templateIds']),overlap=round(overlap,3),sameLeader=same_leader,exact=a==b and same_leader,
                                    betaOnly=list((a-b).elements()),ourOnly=list((b-a).elements())))
        matches.sort(key=lambda m:(m['exact'],m['overlap'],m['sameLeader']),reverse=True)
        duplicate_beta=[o['asset'] for o in beta['eligible'] if o['asset']!=d['asset'] and o['leader']==d['leader'] and Counter(o['templateIds'])==a]
        result.append(dict(**d,similarToCurrent=matches,exactBetaDuplicates=duplicate_beta,activation='awaiting-user-decision' if matches or duplicate_beta else 'distinct-approved-by-request'))
    report=dict(schema=1,scope='Exact original legal lists; similarity is a review flag, never an automatic card replacement',constructionInvalidExcluded=beta['excludedDecks'],sourceLegal=len(result),
                criterion='overlap>=80% of smaller deck, or same leader and overlap>=65%; multiplicities counted',
                distinct=sum(r['activation']=='distinct-approved-by-request' for r in result),review=sum(r['activation']=='awaiting-user-decision' for r in result),decks=result)
    out=DRAFT/'beta-deck-import-review.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    rows=['# Подлинные колоды беты: обзор перед добавлением','',f"Допущено по составу: {len(result)} из73; исключено: {beta['excludedDecks']}. Разрешение ИИ видеть руку — отдельная настройка.",'',f"Отличающиеся: {report['distinct']}; требуют решения о похожести/дубликатах: {report['review']}.",'','Имена ниже — исходные имена файлов/asset, составы не изменены. Сходство учитывает число копий.','', '| Имя беты | Ближайшая наша колода | Общих карт | Лидер совпадает | Решение |','|---|---|---|---|---|']
    for d in result:
        m=d['similarToCurrent'][0] if d['similarToCurrent'] else None
        target=f"{m['preset']}: {m['title']}" if m else ('Дубликат Beta: '+', '.join(d['exactBetaDuplicates']) if d['exactBetaDuplicates'] else '—')
        overlap=f"{m['shared']}/{m['betaCards']} и {m['shared']}/{m['ourCards']}" if m else '—'
        rows.append(f"| {d['asset']} | {target} | {overlap} | {'да' if m and m['sameLeader'] else '—'} | {'на рассмотрение' if d['activation']=='awaiting-user-decision' else 'отличается'} |")
    (DRAFT/'BETA_DECK_IMPORT_REVIEW_RU.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='decks'},ensure_ascii=False))

if __name__=='__main__':main()

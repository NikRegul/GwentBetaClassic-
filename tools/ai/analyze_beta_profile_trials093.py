"""Audit immutable profile trials and summarize screening without shipping a winner."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,math

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def audit(out):
    plan=json.loads((out/'plan.json').read_text('utf8'));digest=sha(out/'plan.json')
    for n,h in plan['codeFiles'].items():assert sha(out/'frozen'/n)==h,n
    assert sha(Path(plan['current'])/'manifest.json')==plan['commonManifestSha256']
    expected={j['id'] for j in plan['schedule']};assert len(expected)==len(plan['schedule'])
    assert {p.stem for p in (out/'games').glob('*.json')}<=expected
    records=[];gap=False
    for job in plan['schedule']:
        p=out/'games'/(job['id']+'.json')
        if not p.exists():gap=True;continue
        assert not gap,'Results must form a prefix';r=json.loads(p.read_text('utf8'))
        assert r['planSha256']==digest and r['status']=='complete'
        for key in ('id','seed'):assert r[key]==job[key]
        assert r['left']==job['left']['key'] and r['right']==job['right']['key']
        assert r['winner'] in (1,2,3);records.append((job,r))
    return plan,records,dict(planSha256=digest,completed=len(records),planned=len(expected),complete=len(records)==len(expected),inputsUnchanged=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--audit-only',action='store_true');a=p.parse_args()
    plan,records,proof=audit(a.out)
    if a.audit_only:print(json.dumps(proof));return
    assert proof['complete'],'Wait for the complete fixed screen'
    progress=json.loads((a.out/'progress.json').read_text('utf8'));assert progress['status']=='complete' and progress['errors']==0
    stats=defaultdict(list)
    for job,r in records:
        score=.5 if r['winner']==3 else float(r['winner']==job['mirror']+1)
        stats[(job['deck'],job['candidate'])].append(score)
    rows=[]
    for (deck,name),scores in stats.items():
        n=len(scores);mean=sum(scores)/n;z=1.96;den=1+z*z/n;centre=(mean+z*z/(2*n))/den;margin=z*math.sqrt(mean*(1-mean)/n+z*z/(4*n*n))/den
        rows.append(dict(deck=deck,profile=name,games=n,scoreRate=mean,interval95Descriptive=[max(0,centre-margin),min(1,centre+margin)]))
    finalists=[]
    for d in plan['decks']:
        candidates=[r for r in rows if r['deck']==d['key']]
        source_direct={c['profile'] for c in d['candidates'] if c['direct']}
        candidates.sort(key=lambda r:(-r['scoreRate'],r['profile'] not in source_direct,r['profile']))
        if candidates and candidates[0]['scoreRate']>=.5:finalists.append(dict(deck=d['key'],profile=candidates[0]['profile'],screenScore=candidates[0]['scoreRate'],direct=candidates[0]['profile'] in source_direct))
    result=dict(**proof,validated=False,scope='Completed screening only. Small self-deck sample; a distinct varied-opponent holdout is required before shipping assignments.',rows=rows,finalists=finalists)
    dest=a.out/'analysis';dest.mkdir(exist_ok=True);(dest/'screen.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(**proof,finalists=len(finalists),validated=False)))

if __name__=='__main__':main()

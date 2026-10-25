"""Freeze a separate varied-opponent holdout after both screening plans finish."""
from pathlib import Path
import argparse,hashlib,json,shutil
from analyze_beta_profile_trials093 import audit

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('screen',type=Path);p.add_argument('gaps',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    assert not a.out.exists(),'Fresh confirmation directory required'
    sources=[];units={};finalists={};proofs=[]
    for out in [a.screen,a.gaps]:
        plan,records,proof=audit(out);assert proof['complete'],'Both fixed screening plans must finish'
        progress=json.loads((out/'progress.json').read_text('utf8'));assert progress['status']=='complete' and progress['errors']==0
        report=json.loads((out/'analysis/screen.json').read_text('utf8'));assert report['complete'] and not report['validated']
        sources.append(plan);proofs.append(dict(path=str(out.resolve()),planSha256=proof['planSha256'],analysisSha256=sha(out/'analysis/screen.json')))
        units.update({d['key']:d for d in plan['decks']})
        for f in report['finalists']:finalists[f['deck']]=f
    assert sources[0]['commonManifestSha256']==sources[1]['commonManifestSha256']
    # Research-pool decks from the same immutable catalogue; each appears in
    # exactly one composition unit, potentially through a quest NPC alias.
    pool=[]
    for d in units.values():
        ids=[b['presetId'] for b in d['aliases'] if 54<=b['presetId']<=99]
        if ids:pool.append(dict(d,presetId=ids[0],basePreset=ids[0]))
    assert len(pool)==46
    pool.sort(key=lambda d:d['presetId']);schedule=[];confirmations=[]
    for key,f in sorted(finalists.items()):
        d=units[key];same=[o for o in pool if o['faction']==d['faction'] and o['key']!=key]
        different=[o for o in pool if o['faction']!=d['faction']]
        opponents=[same[d['presetId']%len(same)],different[(d['presetId']*7)%len(different)]]
        confirmations.append(dict(deck=key,profile=f['profile'],baseline=d['baseline'],direct=f['direct'],opponents=[o['presetId'] for o in opponents]))
        for oi,o in enumerate(opponents):
            for block in range(2):
                for mirror in range(2):
                    for variant in ['candidate','baseline']:
                        profile=f['profile'] if variant=='candidate' else d['baseline']
                        agent=dict(d,key=key+':'+profile,policy='beta',profile=profile)
                        opponent=dict(o,key='hard:'+str(o['presetId']),policy='092')
                        left,right=(agent,opponent) if not mirror else (opponent,agent)
                        schedule.append(dict(id=f'{key}-o{oi}-b{block}-m{mirror}-{variant}',deck=key,candidate=f['profile'],baseline=d['baseline'],variant=variant,opponent=o['presetId'],block=block,mirror=mirror,seed=924120001+d['presetId']*101+oi*10007+block*100003,left=left,right=right))
    a.out.mkdir(parents=True);(a.out/'games').mkdir();files={}
    paths=list((ROOT/'tools/ai/beta_js092').rglob('*'))+[ROOT/'tools/ai'/n for n in ['comparison_bridge119.js','versioned_match092.js','variant_decks092.js','run_beta_profile_trials093.cjs']]
    for src in paths:
        if not src.is_file():continue
        rel=src.relative_to(ROOT);dest=a.out/'frozen'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest);files[rel.as_posix()]=sha(dest)
    plan=dict(schema=1,kind='beta-profile-varied-opponent-confirmation',ratingPermitted=False,current=sources[0]['current'],commonFingerprint=sources[0]['commonFingerprint'],commonManifestSha256=sources[0]['commonManifestSha256'],screeningProofs=proofs,codeFiles=files,units=list(units.values()),bindings=sources[0]['bindings'],confirmations=confirmations,schedule=schedule,
              selectionRule='Keep incumbent unless candidate scores higher on the paired holdout; ties may retain an explicitly authored source binding. Report broad uncertainty and do not claim a globally strongest profile.',stopOnError=True)
    (a.out/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(out=str(a.out),decks=len(confirmations),games=len(schedule),planSha256=sha(a.out/'plan.json'))))

if __name__=='__main__':main()

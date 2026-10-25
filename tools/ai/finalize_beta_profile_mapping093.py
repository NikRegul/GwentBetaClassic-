"""Select stable per-preset profiles only after the complete varied holdout."""
from pathlib import Path
from collections import defaultdict
import argparse,hashlib,json,math
from analyze_beta_profile_trials093 import audit

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('confirmation',type=Path);p.add_argument('equivalence',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    assert not a.out.exists(),'Never replace an accepted mapping'
    plan,records,proof=audit(a.confirmation);assert proof['complete']
    progress=json.loads((a.confirmation/'progress.json').read_text('utf8'));assert progress['status']=='complete' and progress['errors']==0
    assert plan['kind']=='beta-profile-varied-opponent-confirmation'
    for src in plan['screeningProofs']:
        root=Path(src['path']);assert sha(root/'plan.json')==src['planSha256'];assert sha(root/'analysis/screen.json')==src['analysisSha256']
    eq=json.loads(a.equivalence.read_text('utf8'));signatures=eq['signatures']
    assert eq['sourceProfilesSha256']==plan['codeFiles']['tools/ai/beta_js092/data/personalities.json']
    scores=defaultdict(lambda:defaultdict(dict))
    for job,r in records:
        agent_side=job['mirror']+1;score=.5 if r['winner']==3 else float(r['winner']==agent_side)
        scores[job['deck']][job['variant']][(job['opponent'],job['block'],job['mirror'])]=score
    selected={};assessment=[]
    for conf in plan['confirmations']:
        key=conf['deck'];s=scores[key];assert set(s['candidate'])==set(s['baseline']) and len(s['candidate'])==8
        candidate=sum(s['candidate'].values())/8;baseline=sum(s['baseline'].values())/8
        blocks=defaultdict(list)
        for (opponent,seed,mirror),value in s['candidate'].items():blocks[(opponent,seed)].append(value-s['baseline'][(opponent,seed,mirror)])
        delta=[sum(v)/len(v) for v in blocks.values()];assert len(delta)==4
        keep=candidate>baseline or conf['direct'] and candidate==baseline
        selected[key]=conf['profile'] if keep else conf['baseline']
        assessment.append(dict(**conf,candidateScore=candidate,baselineScore=baseline,meanPairedDelta=sum(delta)/len(delta),mirrorPairDeltas=delta,selected=selected[key],games=16,
                               evidence='Small fixed holdout; point estimate and individual pair deltas are descriptive, not proof of a globally strongest profile.'))
    assignments=[]
    for d in plan['units']:
        chosen=selected.get(d['key'],d['baseline']);reason='varied-holdout' if d['key'] in selected else 'no-screened-candidate-improved'
        if chosen==d['baseline']:
            equivalent=[name for name in d['direct'] if signatures.get(name)==signatures.get(chosen)]
            if equivalent:chosen=sorted(equivalent)[0];reason='authored-source-binding-exact-behaviour-equivalence'
        for alias in d['aliases']:assignments.append(dict(presetId=alias['presetId'],title=alias['title'],profile=chosen,composition=d['key'],reason=reason,sourceDeclaredProfiles=alias['directSerializedProfiles']))
    assignments.sort(key=lambda r:r['presetId']);assert [r['presetId'] for r in assignments]==list(range(21,130))
    execution=None
    execution_file=a.confirmation/'parallel-execution.json'
    if execution_file.exists():
        execution=json.loads(execution_file.read_text('utf8'))
        assert execution['planSha256']==proof['planSha256'] and execution['frozenInputsVerified']
        preflight=a.confirmation/('parallel-preflight-workers'+str(execution['workers'])+'-balanced.json')
        check=json.loads(preflight.read_text('utf8'))
        assert check['passed'] and check['workers']==execution['workers'] and check['planSha256']==proof['planSha256']
        execution=dict(**execution,preflightSha256=sha(preflight),note='Only orchestration parallelized after user authorization; immutable schedule/AI/settings kept. Timed search uses original wall-clock limit. Preflight exact parity is a finite sample.')
    report=dict(schema=1,validated=True,scope='Completed source-profile screening and varied-opponent holdout; explicit finite sample, no globally strongest-profile claim.',commonFingerprint=plan['commonFingerprint'],confirmation=dict(**proof,out=str(a.confirmation.resolve())),execution=execution,equivalenceSha256=sha(a.equivalence),assignments=assignments,assessment=assessment,
                pendingShippingChecks=['Named WS data/handler parity','Complete WS matches with selected profiles','Both native compilers and final archive checks'],installed=False)
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(out=str(a.out),presets=len(assignments),profiles=len({r['profile'] for r in assignments}),validated=True)))

if __name__=='__main__':main()

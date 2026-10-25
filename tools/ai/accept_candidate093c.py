"""Export a small auditable acceptance proof only after the fixed holdout passes."""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, math, subprocess
from comparison_inputs import validate_snapshot
from snapshot import inputs, fingerprint
from audit_policy093c import audit

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('holdout',type=Path);p.add_argument('output',type=Path);a=p.parse_args()
    candidate=a.candidate.resolve();holdout=a.holdout.resolve();destination=a.output.resolve();assert not destination.exists()
    manifest=validate_snapshot(candidate/'rules');summary=json.loads((holdout/'summary.json').read_text('utf8'));plan=json.loads((holdout/'plan.json').read_text('utf8'))
    assert manifest['fingerprint']==fingerprint(inputs())==summary['candidateFingerprint']==plan['candidateFingerprint']
    assert summary['complete'] and summary['acceptancePassed'] and summary['errors']==0
    assert plan['kind']=='holdout' and plan['plannedGames']==summary['completedGames']==3680 and plan['cycles']==10 and len(plan['pool'])==92
    assert summary['lower99']>.5 and summary['clusterLower99']>.5 and summary['compositionClusters']==92
    assert sha(holdout/'plan.json')==summary['planSha256']
    aa_path=ROOT/'BetaGwent/build/ai093c-aa-control-20261025-01/summary.json'
    aa=json.loads(aa_path.read_text('utf8'));assert aa['complete'] and aa['passed'] and aa['candidateFingerprint']==manifest['fingerprint']
    assert aa['games']==368 and aa['blocks']==92 and aa['scoreRate']==.5 and aa['errors']==0 and aa['everyMirroredPolicySwapCancels']
    for n,h in plan['tools'].items():assert sha(ROOT/'tools/ai'/n)==h,'Comparison tool changed '+n
    regressions=json.loads((candidate/'regressions/summary.json').read_text('utf8'));assert len(regressions)==85 and all(r['exitCode']==0 for r in regressions)
    targeted={}
    for name in ['check_reply_pass094','check_exhausted_frontier094','check_draw_frontier094','check_chase_budget093a','check_lock_resilience093b','check_plans093c','check_four_card093c']:
        record=json.loads((candidate/'regressions'/(name+'.json')).read_text('utf8'));assert not record['failures'] and record['fingerprint']==manifest['fingerprint'];targeted[name]=record['checks']
    assert sum(targeted.values())==7508
    baseline=json.loads((candidate/'baseline-policy/comparison.json').read_text('utf8'));assert baseline['sharedBattleMechanics']
    old_manifest=validate_snapshot(Path(baseline['oldSnapshot']));assert old_manifest['fingerprint']=='d9c95ce98f644dc07eed05b16258a6dc5ff1f5488c0c5920497cdb17f23c1c1e'
    source_audit=audit(candidate/'rules',Path(baseline['oldSnapshot']))
    witness_path=candidate/'real-position-witness.json'
    assert not witness_path.exists(),'Preserve an existing witness export'
    witness_tool=ROOT/'tools/ai/check_witness093c.cjs'
    witness_fixture=ROOT/'tools/ai/fixtures/four-card-tutor093c.json.gz'
    subprocess.run(['node',str(witness_tool),str(candidate/'rules'),baseline['oldSnapshot'],str(witness_path)],cwd=ROOT,check=True)
    witness=json.loads(witness_path.read_text('utf8'))
    assert witness['candidateFingerprint']==manifest['fingerprint'] and witness['baselineFingerprint']==old_manifest['fingerprint']
    shard_audit={};totals=collections.Counter();blocks_all=[];clusters=collections.defaultdict(list)
    for directory in sorted(holdout.glob('part-*')):
        report=json.loads((directory/'report.json').read_text('utf8'));assert report['complete'] and report['errors']==0
        for n,h in report['inputs'].items():assert sha(directory/n)==h,'Frozen shard changed '+n
        assert len(report['games'])==report['completedGames']==report['plannedGames']
        groups=collections.defaultdict(list);counts=collections.Counter()
        for game in report['games']:
            assert not game.get('error') and game['winner'] in (1,2,3)
            result='draws' if game['winner']==3 else 'wins' if game['winner']==game['newSeat']+1 else 'losses'
            counts[result]+=1;groups[game['block']].append(game)
        assert all(counts[key]==report[key] for key in ('wins','losses','draws'))
        totals.update(counts)
        for block,games in groups.items():
            assert len(games)==4 and len({g['id'] for g in games})==4
            value=sum(.5 if g['winner']==3 else int(g['winner']==g['newSeat']+1) for g in games)/4
            blocks_all.append(value)
            anchor=plan['pool'][report['blockStart']+block%report['blockCount']]
            clusters[anchor].append(value)
        shard_audit[directory.name]=dict(reportSha256=sha(directory/'report.json'),games=report['completedGames'],wins=report['wins'],losses=report['losses'],draws=report['draws'])
    assert len(shard_audit)==plan['workers']==4 and sum(totals.values())==3680
    assert all(totals[k]==summary[k] for k in ('wins','losses','draws'))
    assert len(blocks_all)==920 and len(clusters)==92 and all(len(v)==10 for v in clusters.values())
    def interval(values):
        n=len(values);mean=sum(values)/n
        se=math.sqrt(sum((v-mean)**2 for v in values)/(n-1)/n)
        return max(0,mean-2.576*se),min(1,mean+2.576*se)
    low,high=interval(blocks_all);cluster_low,cluster_high=interval([sum(v)/len(v) for v in clusters.values()])
    for key,value in [('lower99',low),('upper99',high),('clusterLower99',cluster_low),('clusterUpper99',cluster_high),('scoreRate',(totals['wins']+.5*totals['draws'])/3680)]:
        assert math.isclose(summary[key],value,abs_tol=1e-12),'Raw game recount disagrees: '+key
    proof=dict(schema=1,version='0.9.3c',accepted=True,acceptedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
               candidateFingerprint=manifest['fingerprint'],baselineVersion='0.9.3b',baselineSnapshot=baseline['oldSnapshot'],baselineFingerprint=old_manifest['fingerprint'],
               sharedBattleMechanics=True,hiddenInformationAccessUnchanged=True,regressionGroups=85,targetedChecks=targeted,negativeControl=dict(path=str(aa_path),sha256=sha(aa_path),result=aa),
               holdout=dict(path=str(holdout),planSha256=sha(holdout/'plan.json'),summarySha256=sha(holdout/'summary.json'),
                            games=3680,poolSize=92,seed=plan['seed'],cycles=10,wins=summary['wins'],losses=summary['losses'],draws=summary['draws'],
                            scoreRate=summary['scoreRate'],lower99=summary['lower99'],upper99=summary['upper99'],clusterLower99=summary['clusterLower99'],clusterUpper99=summary['clusterUpper99'],errors=0,shards=shard_audit),
               sourceFiles=manifest['files'],policySourceAudit=source_audit,
               qualitativeWitness=dict(result=witness,reportSha256=sha(witness_path),toolSha256=sha(witness_tool),fixtureSha256=sha(witness_fixture)),
               limits='Finite paired stand comparison against0.9.3b on92 compositions. No claim of globally strongest AI or retail gameplay acceptance.',
               nativeGameplayVerified=False,installed=False,published=False)
    destination.parent.mkdir(parents=True,exist_ok=True);destination.write_text(json.dumps(proof,indent=2)+'\n','utf8');print(json.dumps(proof['holdout']))


if __name__=='__main__':main()

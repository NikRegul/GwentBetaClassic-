"""A/A control: identical policies must cancel in every four-game block."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools/ai'))
from comparison_inputs import validate_snapshot


def main():
    p=argparse.ArgumentParser();p.add_argument('candidate',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
    candidate=a.candidate.resolve();out=a.out.resolve();assert not out.exists() and out.is_relative_to(ROOT/'BetaGwent/build')
    m=validate_snapshot(candidate);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    roster=ROOT/'BetaGwent/build/classic093-knockout-20261024-01/entrants.json';entrants=[e for e in json.loads(roster.read_text('utf8')) if e['group']=='hard'];pool=sorted(e['presetId'] for e in entrants);assert len(set(pool))==92
    out.mkdir();plan=dict(kind='identical-policy-negative-control',candidateFingerprint=m['fingerprint'],seed=2026102544,pool=pool,workers=4,games=368,
                         runnerSha256=sha(ROOT/'tools/ai/compare_all093c.js'),rosterSha256=sha(roster))
    (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n','utf8');jobs=[]
    for i in range(4):
        folder=out/f'part-{i:02}';folder.mkdir()
        for side in ['candidate','baseline']:shutil.copytree(candidate,folder/side)
        proof=dict(schema=1,baselineRules=sha(folder/'baseline/rules.js'),sameDeckCatalogue=sha(candidate/'sources/BetaGwent/development/scripts/game/betagwent/duelCatalog.ws'),sharedBattleMechanics=True,sessionPolicyMethods=[],identicalPolicyControl=True)
        (folder/'baseline/comparison.json').write_text(json.dumps(proof,indent=2),'utf8')
        for name in ['compare_all093c.js','comparison_bridge119.js','replay119.js']:shutil.copy2(ROOT/'tools/ai'/name,folder/name)
        config=dict(pool=pool,cycles=1,seed=plan['seed'],candidateLabel='identical policy A',baselineLabel='identical policy B',randomMatchups=True,
                    candidateStrength=4,baselineStrength=4,blockStart=i*23,blockCount=23,maximumKnowsStartingList=True,traceEvery=4,fastHost=True,simDamp=40)
        (folder/'run.json').write_text(json.dumps(config,indent=2),'utf8');(folder/'profiles.json').write_text(json.dumps(dict(profiles=entrants)),'utf8')
        jobs.append(dict(folder=folder))
    for job in jobs:
        job['log']=(job['folder']/'worker.log').open('w',encoding='utf8');job['process']=subprocess.Popen(['node',str(job['folder']/'compare_all093c.js'),str(job['folder'])],cwd=ROOT,stdout=job['log'],stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    while any(job['process'].poll() is None for job in jobs):time.sleep(5)
    games=blocks=0;records=[]
    for job in jobs:
        job['log'].close();assert job['process'].returncode==0;report=json.loads((job['folder']/'report.json').read_text('utf8'));assert report['complete'] and report['errors']==0 and report['scoreRate']==.5
        assert report['candidateRules']==report['baselineRules']
        for n,h in report['inputs'].items():assert sha(job['folder']/n)==h
        by_block={}
        for g in report['games']:by_block.setdefault(g['block'],[]).append(g)
        for group in by_block.values():
            assert len(group)==4 and group[0]['winner']==group[2]['winner'] and group[1]['winner']==group[3]['winner']
            assert sum(.5 if g['winner']==3 else int(g['winner']==g['newSeat']+1) for g in group)==2
        games+=len(report['games']);blocks+=len(by_block);records.append(dict(part=job['folder'].name,reportSha256=sha(job['folder']/'report.json')))
    assert games==368 and blocks==92;assert sha(ROOT/'tools/ai/compare_all093c.js')==plan['runnerSha256']
    result=dict(complete=True,passed=True,kind=plan['kind'],checkedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidateFingerprint=m['fingerprint'],games=games,blocks=blocks,scoreRate=.5,errors=0,everyMirroredPolicySwapCancels=True,planSha256=sha(out/'plan.json'),records=records)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n','utf8');print(json.dumps(result))


if __name__=='__main__':main()

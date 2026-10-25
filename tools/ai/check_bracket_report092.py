"""Contract tests with synthetic results, never presented as played matches."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,tempfile

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False),'utf8')
def main():
    checks=0;versioned='--versioned' in sys.argv;size=92 if versioned else 46
    temporary_root=ROOT/'BetaGwent/build/bracket-contract092';temporary_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='contract-',dir=temporary_root) as folder:
        assert Path(folder).resolve().is_relative_to(temporary_root.resolve())
        out=Path(folder);runner=out/'runner';runner.mkdir();snapshot=out/'snapshot';snapshot.mkdir()
        for n in ['bracket_schedule092.js','bracket_tournament092.js','variant_decks092.js','report_bracket092.py']:shutil.copy2(ROOT/'tools/ai'/n,runner/n)
        js=r'''
const fs=require('fs'),path=require('path'),s=require(process.argv[1]),out=process.argv[2];
const size=Number(process.argv[3]),base=Array.from({length:46},(_,i)=>54+i),pool=size===92?[...base,...base.map(i=>i+100)]:base,plan=s.plan(pool,1,923101600),done=new Map(),records=[];
for(const n of plan.nodes){const task=s.available(n,done),winnerDeck=Math.min(task.a,task.b);
 const games=Array.from({length:4},(_,i)=>({left:i%2?task.b:task.a,right:i%2?task.a:task.b,seed:task.seeds[i>>1],winner:winnerDeck===(i%2?task.b:task.a)?1:2,milliseconds:1}));
 const r={id:n.id,bracket:n.bracket,stage:n.stage,a:task.a,b:task.b,games,pointsA:s.points(games,task.a),winnerDeck,loserDeck:Math.max(task.a,task.b),lotUsed:false};s.validate(task,r);done.set(n.id,r);records.push(r);}
fs.writeFileSync(path.join(out,'schedule.json'),JSON.stringify(plan));fs.writeFileSync(path.join(out,'series.jsonl'),records.map(r=>JSON.stringify(r)).join('\n')+'\n');
'''
        subprocess.run(['node','-e',js,str(runner/'bracket_schedule092.js'),str(out),str(size)],check=True,capture_output=True)
        write(snapshot/'manifest.json',dict(fingerprint='contract-only',snapshotFiles={},presets=list(range(54,100))))
        pool=list(range(54,100))+(list(range(154,200)) if versioned else [])
        write(out/'deck-metadata.json',dict(fingerprint='contract-only',originalFingerprint='contract-only',decks=[dict(presetId=i,basePreset=i-100 if i>=100 else i,version='0.9.1' if i>=100 else '0.9.2',title=f'Test {i}') for i in pool]))
        config=dict(snapshot=str(snapshot),strength=4,cycles=1,workers=2,benchmark=False,deadline='2026-10-23T20:00:00+03:00',metadataSha256=sha(out/'deck-metadata.json'))
        if versioned:config.update(versioned=True,originalSnapshot=str(snapshot),originalFingerprint='contract-only',oldPolicy=str(snapshot),oldPolicyFiles={})
        write(out/'config.json',config)
        write(out/'progress.json',dict(complete=True,errors=0,completedSeries=23*(size-1),completedGames=23*(size-1)*4,totalSeconds=100,updatedAt='2026-10-23T16:00:00Z',finishedAt='2026-10-23T15:59:59Z'))
        identity=dict(fingerprint='contract-only',configSha256=sha(out/'config.json'),scheduleSha256=sha(out/'schedule.json'),tools={n:sha(runner/n) for n in ['bracket_tournament092.js','bracket_schedule092.js','variant_decks092.js']})
        write(out/'identity.json',identity)
        command=[sys.executable,'-X','utf8',str(runner/'report_bracket092.py'),str(out)]
        subprocess.run(command,check=True,capture_output=True)
        r=json.loads((out/'ratings.json').read_text('utf8'));assert r['complete'] and len(r['ranking'])==size and r['games']==23*(size-1)*4 and r['series']==23*(size-1);checks+=1
        assert r['ranking'][0]['presetId']==54 and r['ranking'][0]['titles']==23 and r['seriesByLot']==0;checks+=1
        assert all(s['byes']==9 and len(s['placements'])==23 for s in r['ranking']);checks+=1
        assert abs(sum(s['meanPlacement'] for s in r['ranking'])-size*(size+1)/2)<1e-8;checks+=1
        if versioned:
            v=r['versionComparison'];assert v['decksPerVersion']==46 and v['newHeadToHeadWins']>0 and v['oldHeadToHeadWins']==0 and v['confirmedBetter'];checks+=1
        assert r['finishedBeforeDeadline'];checks+=1
        original=(out/'series.jsonl').read_text('utf8');rows=[json.loads(line) for line in original.splitlines()]
        rows[0]['winnerDeck']=rows[0]['loserDeck'];(out/'series.jsonl').write_text('\n'.join(json.dumps(x) for x in rows)+'\n','utf8')
        assert subprocess.run(command,capture_output=True).returncode!=0;checks+=1
        (out/'series.jsonl').write_text(original,'utf8')
        plan=json.loads((out/'schedule.json').read_text('utf8'));saved=(out/'schedule.json').read_bytes();plan['brackets'][0]['byes'][0]=plan['brackets'][0]['byes'][1];write(out/'schedule.json',plan)
        identity['scheduleSha256']=sha(out/'schedule.json');write(out/'identity.json',identity)
        assert subprocess.run(command,capture_output=True).returncode!=0;checks+=1
        (out/'schedule.json').write_bytes(saved);identity['scheduleSha256']=sha(out/'schedule.json');write(out/'identity.json',identity)
        (out/'series.jsonl').write_text(original[:-5],'utf8');assert subprocess.run(command,capture_output=True).returncode!=0;checks+=1
    print(json.dumps(dict(checks=checks,syntheticContractOnly=True,completeRanking=True,rejectsWrongWinners=True,rejectsUnbalancedByes=True,rejectsTruncatedRecords=True)))

if __name__=='__main__':main()

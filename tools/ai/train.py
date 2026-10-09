"""Legacy C# self-play tuning of the actual WS battle AI, on all 46 decks.
For researched stage115 policies use Train-AI-JS.ps1, the verified training host.
"""
from pathlib import Path
import argparse, copy, hashlib, json, math, random, subprocess, sys, time
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/ai-selfplay'
DEV=ROOT/'BetaGwent/development/scripts/game/betagwent'
OPTIONS=16
def write(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(path)
def neutral(pool):return {'Name':'baseline','Shared':[0]*OPTIONS,'Decks':{str(p):[0]*OPTIONS for p in pool}}
def pool_ids():
 rules=json.loads((ROOT/'data/beta924/ai/rules.json').read_text(encoding='utf-8-sig'))
 presets=json.loads((ROOT/'data/beta924/duel/presets.json').read_text(encoding='utf-8-sig'))['presets']
 # Canonical mapping, not a separate training-only deck list.
 import re
 raw=(DEV/'duelAICatalog.ws').read_text(encoding='utf-8-sig')
 body=raw[raw.index('function BetaGwentAIPresetProfile'):];body=body[:body.index('\n}')]
 mapping={int(a):int(b) for a,b in re.findall(r'case\s+(\d+)\s*:\s*return\s+(\d+)\s*;',body)}
 active={p['id'] for p in rules['profiles'] if p['active']}
 ids=sorted(p for p,profile in mapping.items() if profile in active)
 if len(ids)!=46 or len(active)!=46:raise ValueError('Pool must contain every one of the 46 active profiles')
 indexed={p['id']:p for p in presets}
 if any(p not in indexed for p in ids):raise ValueError('Missing canonical deck')
 return ids
def schedule(pool,seed,cycles=1):
 rng=random.Random(seed);pairs=[]
 for cycle in range(cycles):
  offset=1+(seed+cycle)%(len(pool)-1)
  for i,p in enumerate(pool):
   q=pool[(i+offset)%len(pool)];deal=rng.randrange(1,2147483647)
   pairs.extend([[p,q,deal,0],[q,p,deal,1]])
 return pairs
def batch(left,right,matches,directory,label):
 path=directory/(label+'.batch.json');write(path,{'Left':left,'Right':right,'Matches':matches})
 result=directory/(label+'.jsonl')
 # Stream to disk: a crash leaves the finished games and their replay seeds.
 with result.open('w',encoding='utf-8') as out:
  process=subprocess.run(['dotnet',str(BUILD/'bin/Debug/net7.0/selfplay.dll'),str(path)],stdout=out,stderr=subprocess.PIPE,text=True,encoding='utf-8',timeout=max(120,len(matches)*8))
 if process.returncode:raise RuntimeError(process.stderr)
 rows=[json.loads(s) for s in result.read_text(encoding='utf-8').splitlines()]
 if len(rows)!=len(matches):raise RuntimeError('Incomplete match batch')
 return rows
def score(r):
 if r['Error']:return None
 if r['Winner']==3:return .5
 return float(r['Winner']==r['CandidateSeat'])
def stats(rows):
 good=[score(r) for r in rows if not r['Error']]
 return {'matches':len(rows),'completed':len(good),'errors':len(rows)-len(good),'winScore':sum(good)/len(good) if good else 0,'decisions':sum(r['Decisions'] for r in rows)}
def comparison(candidate,control):
 if any(r['Error'] for r in candidate+control):return {'eligible':False,'delta':0,'improved':0,'worsened':0}
 deltas=[score(a)-score(b) for a,b in zip(candidate,control)]
 improved=sum(d>0 for d in deltas);worse=sum(d<0 for d in deltas);n=improved+worse
 lower=0
 if n:
  z=1.96;p=improved/n;lower=(p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
 delta=sum(deltas)/len(deltas)
 return {'eligible':delta>=.025 and improved>worse,'delta':delta,'improved':improved,'worsened':worse,'wilsonLowerChangedGames':lower,'strongEvidence':n>=20 and lower>.5}
def mutate(policy,rng,generation,pool):
 p=copy.deepcopy(policy);p['Name']='candidate-'+str(generation)
 # Small bounded edits keep the current archetype rules as the starting policy.
 focus=pool[generation%len(pool)]
 # Alternate global and archetype tuning. A local mutation affects only two
 # games in the 40-deck sweep, so supplement it with paired focal matchups.
 for _ in range(4):
  row=p['Shared'] if generation%2==0 else p['Decks'][str(focus)]
  index=rng.randrange(OPTIONS);row[index]=max(-8,min(8,row[index]+rng.choice([-2,-1,1,2])))
 return p

def focal_schedule(pool,focus,seed,cycles):
 rng=random.Random(seed);opponents=rng.sample([p for p in pool if p!=focus],8);pairs=[]
 for _ in range(cycles):
  for q in opponents:
   deal=rng.randrange(1,2147483647)
   pairs.extend([[focus,q,deal,0],[q,focus,deal,1]])
 return pairs
def export(policy,directory,fingerprint,report):
 text=(DEV/'duelAITraining.ws').read_text(encoding='utf-8-sig').split('// EXPORT_WEIGHTS_BEGIN')[0]
 lines=['// EXPORT_WEIGHTS_BEGIN: learned constants; rules hash '+fingerprint,
 '// '+policy['Name']+'; offline self-play; native acceptance pending.',
 'function BetaGwentAITrainingWeight(preset : int, index : int) : int {']
 shared=[max(-8,min(8,w)) for w in policy['Shared']]
 overrides=[]
 for preset,row in policy['Decks'].items():
  effective=[max(-8,min(8,a+b)) for a,b in zip(policy['Shared'],row)]
  if effective==shared:continue
  overrides+=['    case '+preset+':']
  if any(effective):
   overrides+=['        switch(index) {']
   overrides+=['        case '+str(i)+': return '+str(w)+';' for i,w in enumerate(effective) if w]
   overrides+=['        }']
  overrides+=['        return 0;']
 if overrides:lines+=['    switch(preset) {']+overrides+['    }']
 if any(shared):
  lines+=['    switch(index) {']
  lines+=['    case '+str(i)+': return '+str(w)+';' for i,w in enumerate(shared) if w]
  lines+=['    }']
 lines+=['    return 0;','}']
 path=directory/'export/duelAITraining.ws';path.parent.mkdir(exist_ok=True)
 path.write_text(text+'\n'.join(lines)+'\n',encoding='utf-8-sig')
 write(directory/'export/report.json',report)

def export_state(state,directory):
 report={'rulesHash':state['rulesHash'],'pool':state['pool'],'generation':state['generation'],'promotions':state['promotions'],'hasLearnedPolicy':bool(state['promotions']),'nativeParityVerified':False,'method':'bounded evolutionary self-play ranking; pass safety and actual tempo unchanged'}
 export(state['champion'],directory,state['rulesHash'],report)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--generations',type=int,default=100);ap.add_argument('--seed',type=int,default=924)
 ap.add_argument('--cycles',type=int,default=1);ap.add_argument('--output',type=Path,default=ROOT/'BetaGwent/training/default');ap.add_argument('--resume',action='store_true');ap.add_argument('--smoke',action='store_true');ap.add_argument('--skip-build',action='store_true')
 args=ap.parse_args()
 if args.generations<0 or args.cycles<1:ap.error('generations>=0, cycles>=1 required')
 directory=args.output.resolve();directory.mkdir(parents=True,exist_ok=True);pool=pool_ids()
 if not args.skip_build:subprocess.run([sys.executable,str(ROOT/'tools/ai/build_simulator.py')],check=True)
 hashes=json.loads((BUILD/'sources.json').read_text(encoding='utf-8'))
 for relative,digest in hashes.items():
  actual=hashlib.sha256((ROOT/relative).read_text(encoding='utf-8-sig').encode('utf-8')).hexdigest()
  if actual!=digest:raise ValueError('Headless build is stale: '+relative+'; rerun without --skip-build')
 # Learned constants may change; shared feature code must remain identical.
 feature=(DEV/'duelAITraining.ws').read_text(encoding='utf-8-sig').split('// EXPORT_WEIGHTS_BEGIN')[0]
 hashes[str((DEV/'duelAITraining.ws').relative_to(ROOT))]=hashlib.sha256(feature.encode()).hexdigest()
 for p in ('data/beta924/ai/rules.json','data/beta924/duel/presets.json','tools/ai/build_simulator.py','tools/ai/train.py'):
  hashes[p]=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
 for p in sorted((ROOT/'tools/ai/host').glob('*.cs')):hashes[str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
 fingerprint=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest();write(directory/'source-manifest.json',hashes)
 baseline=neutral(pool);checkpoint=directory/'checkpoint.json'
 if checkpoint.exists() and not args.resume:raise ValueError('Output already has a checkpoint. Use --resume or a new output folder.')
 if args.resume:
  state=json.loads(checkpoint.read_text(encoding='utf-8'))
  if state['rulesHash']!=fingerprint:raise ValueError('Rules changed: start a new training run; do not mix incompatible checkpoints')
  if state['seed']!=args.seed or state['cycles']!=args.cycles:raise ValueError('Resume with the original seed and cycles')
 else:state={'rulesHash':fingerprint,'seed':args.seed,'cycles':args.cycles,'generation':0,'champion':baseline,'league':[baseline],'promotions':[],'pool':pool}
 write(checkpoint,state)
 if args.smoke:
  rows=batch(baseline,baseline,schedule(pool,args.seed,args.cycles),directory,'smoke')
  report={'pool':pool,'rulesHash':fingerprint,'summary':stats(rows),'nativeParityVerified':False};write(directory/'smoke-report.json',report);print(json.dumps(report['summary']))
  return 1 if report['summary']['errors'] else 0
 end=state['generation']+args.generations
 for gen in range(state['generation'],end):
  if (directory/'STOP').exists():print('STOP found; checkpoint retained.');break
  rng=random.Random(args.seed+gen*7919);candidate=mutate(state['champion'],rng,gen,pool);league=state['league'][gen%len(state['league'])]
  pairs=schedule(pool,args.seed+gen*41,args.cycles);label='g'+str(gen).zfill(5);focus=pool[gen%len(pool)]
  sweep_count=len(pairs)
  if gen%2:pairs+=focal_schedule(pool,focus,args.seed+gen*71,args.cycles)
  print(label+': self play, all '+str(len(pool))+' decks, '+str(len(pairs))+' games per policy',flush=True)
  cand=batch(candidate,league,pairs,directory,label+'-candidate');control=batch(state['champion'],league,pairs,directory,label+'-control');fit=comparison(cand,control)
  sweep=comparison(cand[:sweep_count],control[:sweep_count]);focus_fit=comparison(cand[sweep_count:],control[sweep_count:]) if gen%2 else None
  if focus_fit:fit['eligible']=focus_fit['eligible'] and sweep['delta']>=0 and stats(cand)['errors']==0 and stats(control)['errors']==0
  record={'generation':gen,'training':fit,'allDecks':sweep,'focus':focus if gen%2 else None,'focalTraining':focus_fit,'candidate':stats(cand),'accepted':False}
  if fit['eligible']:
   heldout=schedule(pool,100000000+args.seed+gen*43,args.cycles*2)
   heldout_count=len(heldout)
   if gen%2:heldout+=focal_schedule(pool,focus,200000000+args.seed+gen*89,args.cycles*4)
   val=batch(candidate,baseline,heldout,directory,label+'-validation');old=batch(state['champion'],baseline,heldout,directory,label+'-validation-control');gate=comparison(val,old)
   if gen%2:
    gate['focal']=comparison(val[heldout_count:],old[heldout_count:]);gate['sweep']=comparison(val[:heldout_count],old[:heldout_count])
    gate['eligible']=gate['focal']['eligible'] and gate['sweep']['delta']>=0 and stats(val)['errors']==0 and stats(old)['errors']==0
   record['validation']=gate;record['validationSummary']=stats(val)
   if gate['eligible']:
    state['champion']=candidate;state['league']=(state['league']+[candidate])[-8:];state['promotions'].append(record);record['accepted']=True
    write(directory/('champion-'+str(gen)+'.json'),candidate)
  state['generation']=gen+1;write(directory/(label+'-summary.json'),record);write(checkpoint,state)
  export_state(state,directory)
  print('accepted='+str(record['accepted'])+' delta='+str(round(fit['delta'],4))+' errors='+str(record['candidate']['errors']),flush=True)
 # Export the last admitted champion, never the last rejected candidate.
 export_state(state,directory);print('Export: '+str(directory/'export/duelAITraining.ws'),flush=True)
 return 0
if __name__=='__main__':sys.exit(main())

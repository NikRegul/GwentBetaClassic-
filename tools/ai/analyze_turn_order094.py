"""Count match wins by the actual first decision in authenticated finished series.

This is a descriptive tournament snapshot, not a causal estimate or a rerun.
Draws and technical errors are separate; unfinished series are excluded.
"""
from pathlib import Path
import argparse,collections,datetime,hashlib,json
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args()
 root=a.source.resolve();out=a.out.resolve();assert not out.exists(),'Use a fresh analysis directory'
 plan=read(root/'plan.json');digest=sha(root/'plan.json');progress=(root/'progress.json').read_bytes()
 assert json.loads(progress)['planSha256']==digest
 for file,expected in plan['codeFiles'].items():assert sha(root/'frozen'/file)==expected,file
 assert sha(root/'entrants.json')==plan['rosterSha256']
 entrants={e['key']:e for e in read(root/'entrants.json')}
 files=sorted((root/'series').glob('*.json'));seen=set();inventory={};groups={};starter_seats=collections.Counter();starting_policies=collections.Counter();same_deck={}
 def add(store,key,result):
  row=store.setdefault(key,dict(games=0,firstWins=0,secondWins=0,draws=0))
  row['games']+=1;row[['firstWins','secondWins','draws'][result]]+=1
 for file in files:
  series=read(file);assert series['planSha256']==digest and series['kind']=='series' and series['id']==file.stem
  assert len(series['games'])%2==0
  inventory[file.relative_to(root).as_posix()]=sha(file)
  for index,item in enumerate(series['games']):
   ident=item['id'];assert ident not in seen;seen.add(ident)
   path=root/'games'/(ident+'.json');assert sha(path)==item['sha256'];inventory[path.relative_to(root).as_posix()]=item['sha256']
   game=read(path);assert game['status']=='complete' and game['winner'] in [1,2,3]
   assert game['id']==ident and game['series']==series['id'] and game['planSha256']==digest
   assert game['pair']==index//2 and game['mirror']==index%2
   left,right=(series['right'],series['left']) if index%2 else (series['left'],series['right'])
   assert game['left']==left and game['right']==right
   # Seat numbers and mirror flags do not establish who actually started.
   # The authoritative runner appends a trace entry for each live turn after
   # mulligan. Legal opening decks have playable cards, so its first entry is
   # the first round's first live decision (card/leader/pass).
   assert game['trace'] and game['trace'][0]['round']==1
   first=game['trace'][0]['side'];assert first in [1,2]
   starter_seats[first]+=1;keys=[left,right];starter=entrants[keys[first-1]];second=entrants[keys[2-first]]
   starting_policies[starter['group']]+=1
   result=2 if game['winner']==3 else 0 if game['winner']==first else 1
   add(groups,'all',result)
   label='/'.join(sorted([starter['group'],second['group']]))
   add(groups,label,result);add(groups,'first='+starter['group']+';second='+second['group'],result)
   if starter['basePreset']==second['basePreset']:add(same_deck,label,result)
 for store in [groups,same_deck]:
  for row in store.values():
   n=row['games'];decisive=row['firstWins']+row['secondWins']
   row.update(firstWinPercent=100*row['firstWins']/n,secondWinPercent=100*row['secondWins']/n,
    drawPercent=100*row['draws']/n,firstPointsPercent=100*(row['firstWins']+.5*row['draws'])/n,
    firstWinPercentAmongDecisive=100*row['firstWins']/decisive if decisive else None)
 errors=sorted((root/'errors').glob('*.json'));assert len(seen)==groups['all']['games']
 out.mkdir();(out/'progress-at-sample.json').write_bytes(progress)
 (out/'source-files.json').write_text(json.dumps(inventory,indent=2)+'\n','utf8')
 result=dict(complete=True,kind='descriptive-turn-order-snapshot',sampledAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
  source=str(root),planSha256=digest,series=len(files),games=len(seen),technicalErrorFiles=len(errors),
  excludedUnfinishedSeries=True,starterDefinition='Side of first live trace decision in round 1, after mulligan; not seat/mirror number',
  starterSeats=dict(starter_seats),startingPolicies=dict(starting_policies),groups=groups,sameDeckGroups=same_deck,
  tournamentComplete=json.loads(progress)['status']=='complete',notCausalEstimate=True,
  informationAsymmetry='Hard uses restricted hidden information; Classic has broader access')
 (out/'analysis.json').write_text(json.dumps(result,indent=2)+'\n','utf8')
 print(json.dumps({k:result[k] for k in ['sampledAt','series','games','technicalErrorFiles','starterSeats','startingPolicies','groups','sameDeckGroups']}))

if __name__=='__main__':main()

"""Audit an immutable snapshot of completed series in an unfinished tournament.

Writes a new development-analysis folder, never a synthetic completion report.
"""
from pathlib import Path
import argparse,collections,datetime,hashlib,json,shutil
read=lambda p:json.loads(p.read_text('utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def seed_for(plan,g):
    n=(plan['masterSeed']+(((g['grid']*8+g['round'])*128+g['slot'])*8+g['pair']))&0xffffffff
    n=((n^(n>>16))*0x7feb352d)&0xffffffff
    n=((n^(n>>15))*0x846ca68b)&0xffffffff
    return (n^(n>>16))&0xffffffff

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('out',type=Path)
    parser.add_argument('--grid',type=int,help='Audit one completed or partial grid without marking the whole tournament complete');args=parser.parse_args()
    source=args.source.resolve();out=args.out.resolve();assert not out.exists(),'Use a fresh analysis folder'
    plan=read(source/'plan.json');digest=sha(source/'plan.json');inventory={}
    if args.grid is not None:assert 0<=args.grid<plan['grids']
    series_files=sorted((source/'series').glob('*.json'))
    if args.grid is not None:series_files=[p for p in series_files if p.name.startswith('g%02d-'%args.grid)]
    progress_raw=(source/'progress.json').read_bytes();progress=json.loads(progress_raw)
    assert progress['planSha256']==digest
    for name,expected in plan['codeFiles'].items():assert sha(source/'frozen'/name)==expected,name
    assert sha(source/'entrants.json')==plan['rosterSha256'] and sha(source/'profile-mapping.json')==plan['mappingSha256']
    assert sha(Path(plan['current'])/'manifest.json')==plan['commonManifestSha256']
    if plan.get('diagnosticsProofSha256'):assert sha(source/'diagnostics-proof.json')==plan['diagnosticsProofSha256']
    entrants={e['key']:e for e in read(source/'entrants.json')}
    seen=set();stats={};losses=[];maker_errors=[];forced=0;capture_errors=[];finish_reasons=collections.Counter()
    cross={g:dict(points=0,games=0) for g in ['hard','classic']};champions=[]
    for file in series_files:
        match=read(file);inventory[file.relative_to(source).as_posix()]=sha(file)
        assert match['planSha256']==digest and match['kind']=='series'
        assert match['id']==file.stem
        if args.grid is not None:assert match['grid']==args.grid
        if match['round']==7 and match['slot']==0:champions.append(dict(grid=match['grid'],key=match['winner'],title=entrants[match['winner']]['title'],group=entrants[match['winner']]['group'],resolution=match['resolution']))
        assert len(match['games'])%2==0 and plan['format']['basePairs']*2<=len(match['games'])<=2*(plan['format']['basePairs']+plan['format']['maxExtraPairs'])
        points=0
        for index,item in enumerate(match['games']):
            ident=item['id'];assert ident not in seen;seen.add(ident)
            path=source/'games'/(ident+'.json');assert sha(path)==item['sha256'];inventory[path.relative_to(source).as_posix()]=item['sha256']
            game=read(path)
            assert game['status']=='complete' and game['winner'] in [1,2,3]
            assert game['id']==ident and game['series']==match['id'] and game['planSha256']==digest
            assert game['commonFingerprint']==plan['commonFingerprint'] and game['seed']==seed_for(plan,game)
            assert game['pair']==index//2 and game['mirror']==index%2
            a,b=(match['right'],match['left']) if index%2 else (match['left'],match['right'])
            assert (game['left'],game['right'])==(a,b)
            points+=.5 if game['winner']==3 else int(game['winner']==(2 if index%2 else 1))
            forced+=game['betaForcedSearches'];maker_errors.extend(dict(game=ident,error=e) for e in game['betaPlaymakerErrors'])
            beta_trace=[t for t in game['trace'] if t['policy']=='beta'];finish_reasons.update(t['finishReason'] for t in beta_trace)
            if 'betaDecisionDiagnostics' in game:
                diagnostics=game['betaDecisionDiagnostics'];capture_errors.extend(dict(game=ident,diagnostic=d) for d in diagnostics if d.get('diagnosticError'))
                if not any(d.get('diagnosticError') for d in diagnostics):
                    assert len(diagnostics)==len(beta_trace)
                    assert sum(d['searchCallbacks'] for d in diagnostics)==game['betaSearchCallbacks']
                    assert sum(d['forceAtCallback'] is not None for d in diagnostics)==game['betaForcedSearches']
                    assert [d['playmakerError'] for d in diagnostics if d['playmakerError']]==game['betaPlaymakerErrors']
            for side,key,enemy_key in [(1,a,b),(2,b,a)]:
                entrant=entrants[key];enemy=entrants[enemy_key];score=.5 if game['winner']==3 else int(game['winner']==side)
                row=stats.setdefault(key,dict(key=key,title=entrant['title'],group=entrant['group'],faction=entrant['faction'],games=0,points=0))
                row['games']+=1;row['points']+=score
                if entrant['group']!=enemy['group']:cross[entrant['group']]['points']+=score;cross[entrant['group']]['games']+=1
                if game['winner'] not in [side,3]:losses.append(dict(game=ident,side=side,key=key,enemy=enemy_key,group=entrant['group'],enemyGroup=enemy['group'],faction=entrant['faction'],title=entrant['title'],seed=game['seed'],crowns=game['crowns'],turns=len(game['trace']),swept=game['crowns'][side-1]==0))
        assert points==match['leftPoints'] and len(match['games'])-points==match['rightPoints']
        if points==len(match['games'])/2:
            coin=hashlib.sha256((str(plan['masterSeed'])+':tie:'+match['id']).encode()).digest()[0]&1
            assert match['resolution']=='seeded-draw' and match['winner']==(match['left'] if coin else match['right'])
        else:assert match['resolution']=='game-points' and match['winner']==(match['left'] if points>len(match['games'])/2 else match['right'])
    selected={}
    for group in ['hard','classic']:
        chosen=[]
        for faction in [2,4,8,16,32]:
            keys=set()
            for row in sorted((r for r in losses if r['group']==group and r['enemyGroup']==group and r['faction']==faction),key=lambda r:(not r['swept'],r['turns'],r['game'])):
                if row['key'] in keys:continue
                chosen.append(row);keys.add(row['key'])
                if len(keys)==2:break
        selected[group]=chosen
    for name,expected in inventory.items():assert sha(source/name)==expected,'Completed result changed '+name
    final=read(source/'report.json') if (source/'report.json').exists() else None
    result=dict(schema=1,kind='development-prefix-not-strength-trial',analysisComplete=True,tournamentComplete=bool(final and final['complete']),
        gridFilter=args.grid,selectedGridComplete=args.grid is not None and len(series_files)==len(entrants)-1 and len(champions)==1,gridChampions=champions,
        sampledAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),source=str(source),snapshot=plan['current'],planSha256=digest,
        completedSeriesAnalyzed=len(series_files),gamesAnalyzed=len(seen),sourceProgressAtSample=progress,plannedSeries=plan['series'],
        betaPlaymakerErrors=maker_errors,betaForcedSearches=forced,betaFinishReasons=dict(finish_reasons),diagnosticCaptureErrors=capture_errors,
        crossPolicy=cross,decks=list(stats.values()),selected=selected,technicalErrorFiles=[p.name for p in sorted((source/'errors').glob('*.json'))],
        limits='Completed series snapshot only. Active series are excluded. Losses and material differences are review priorities, not automatic bugs. Knockout results are bracket-dependent; Classic has broader hidden-information access than Hard. Not a strength comparison.')
    out.mkdir(parents=True);(out/'progress-at-sample.json').write_bytes(progress_raw);shutil.copy2(__file__,out/'analyzer.py')
    (out/'source-files.json').write_text(json.dumps(inventory,indent=2)+'\n','utf8')
    (out/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    print(json.dumps(dict(series=len(series_files),games=len(seen),playmakerErrors=len(maker_errors),forcedSearches=forced,diagnosticCaptureErrors=len(capture_errors),selected={k:len(v) for k,v in selected.items()},tournamentComplete=result['tournamentComplete'])))

if __name__=='__main__':main()

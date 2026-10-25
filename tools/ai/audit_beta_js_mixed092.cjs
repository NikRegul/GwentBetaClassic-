/* Technical integration, not a strength experiment. Beta sees hidden data;
 * current 0.9.2 keeps its existing visibility restrictions. One rules engine. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime}=require('./beta_js092/session.cjs');
const {personality}=require('./beta_js092/profiles.cjs');
const {BetaTurnController}=require('./beta_js092/controller.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);if(fs.existsSync(out))throw Error('Fresh output required');
const config=JSON.parse(fs.readFileSync(path.resolve(process.argv[4]),'utf8'));
const decks=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
if(config.originalRosterAudit)decks.push(...JSON.parse(fs.readFileSync(path.resolve(config.originalRosterAudit),'utf8')).eligible);
const report={schema:1,config,ratingPermitted:false,nativeProcessesAllowed:false,
 informationAsymmetry:'Beta reads full hands/decks. Current 0.9.2 retains its own information limits. Outcomes are not equal-information algorithm evidence.',
 moduleSha256:Object.fromEntries(fs.readdirSync(path.join(__dirname,'beta_js092')).filter(n=>n.endsWith('.cjs')).map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'beta_js092',n))).digest('hex')])),records:[]};
for(const [left,right,seed]of config.schedule){
 const runtime=createRuntime(rules,seed),g=runtime.newSession(),a=decks.find(d=>d.presetId===left),b=decks.find(d=>d.presetId===right),betaSeat=config.betaSeat||1,p=personality(config.profileByFaction[(betaSeat===1?a:b).faction]);
 const record={left,right,seed,betaSeat,betaProfile:p.name,sourceDepth:p.DepthOfChecking,fingerprint:runtime.fingerprint,trace:[],betaCallbacks:0,currentTurns:0,selectorCalls:0};
 let permitLiveInternal=false;const prototype=g.constructor.prototype;
 for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex']){
  const original=prototype[name];prototype[name]=function(...args){
   if(this.externalPolicyMask===3||(this===g&&!permitLiveInternal))throw Error('Current-policy selector reached Beta-owned action: '+name);
   record.selectorCalls++;return original.apply(this,args);
  };
 }
 g.externalPolicyMask=betaSeat;g.aiSimDamp=40;const started=Date.now();
 try{
  permitLiveInternal=true;if(!g.InitializeWithDecks(a.templateIds,b.templateIds,a.leader,b.leader,left,right))throw Error('Mixed initialization rejected');permitLiveInternal=false;g.recordVisuals=false;
  let decisions=0;
  while(!g.Snapshot().matchWinnerMask){
   if(++decisions>300||Date.now()-started>180000)throw Error('Technical mixed-game limit');
   if(g.IsFatal())throw Error(g.GetMessage());
   if(g.mulligan){
    const owner=g.RequestDecisionSide();
    if(owner===betaSeat)stepMulligan(g,p);
    else{
     permitLiveInternal=true;const swap=owner===1;if(swap)runtime.swap(g);
     g.AiMulligan(g.mulliganBudget);if(swap)runtime.swap(g);g.RefreshMulligan();
     const ok=g.FinishMulligan(g.requestId);permitLiveInternal=false;if(!ok)throw Error('Current-policy mulligan rejected');
    }
    continue;
   }
   if(g.waiting){permitLiveInternal=true;const ok=g.BeginNextRound();permitLiveInternal=false;if(!ok)throw Error('Round rejected');continue;}
   if(g.IsPending())throw Error('Unowned live pending request '+g.GetMessage());
   const before=g.Snapshot(),side=before.currentPlayerId;
   if(side===betaSeat){
    const c=new BetaTurnController(runtime,p,{now:()=>Date.now()});c.start(g);let steps=0;
    while(!c.finished){if(c.step().mutations>1)throw Error('Beta cooperative budget exceeded');if(++steps>100000)throw Error('Technical Beta callback limit');}
    record.betaCallbacks+=steps;record.trace.push({side,template:c.chosen.decision?g.FindCard(c.chosen.decision.cardId).TemplateId():0,round:before.roundNumber,
     finishReason:c.search.finishReason,playmakerError:c.playmakerError,score:[g.Score(1),g.Score(2)]});
   }else{
    permitLiveInternal=true;const swap=side===1;if(swap)runtime.swap(g);const ok=g.OpponentStep();if(swap)runtime.swap(g);permitLiveInternal=false;if(!ok)throw Error('Current-policy turn rejected: '+g.GetMessage());
    record.currentTurns++;record.trace.push({side,round:before.roundNumber,score:[g.Score(1),g.Score(2)]});
   }
  }
  record.status='technical-game-complete';record.winner=g.Snapshot().matchWinnerMask;record.crowns=[g.Snapshot().playerOne.crowns,g.Snapshot().playerTwo.crowns];
 }catch(e){record.status='technical-incomplete';record.error=String(e.stack);}
 record.ms=Date.now()-started;report.records.push(record);fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...record,trace:undefined}));
}
report.complete=true;report.completedGames=report.records.filter(r=>r.status==='technical-game-complete').length;report.incompleteGames=report.records.length-report.completedGames;
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({completed:report.completedGames,incomplete:report.incompleteGames}));

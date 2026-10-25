/* Bounded end-to-end technical smoke of the selected source Base profile.
 * Both policies are the partial direct port. No formal strength results. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,basePersonality}=require('./beta_js092/session.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaAlphaBetaSearch}=require('./beta_js092/search.cjs'),{BetaMiniMaxEvaluator}=require('./beta_js092/core.cjs');
const {BetaPlayMaker}=require('./beta_js092/playmaker.cjs'),{BetaActionReplay}=require('./beta_js092/replay.cjs');
const {personality}=require('./beta_js092/profiles.cjs');
const {BetaTurnController}=require('./beta_js092/controller.cjs');
const rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);if(fs.existsSync(out))throw Error('Use a fresh audit output');
const decks=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
const config=process.argv[4]?JSON.parse(fs.readFileSync(path.resolve(process.argv[4]),'utf8')):null;
if(config?.originalRosterAudit)decks.push(...JSON.parse(fs.readFileSync(path.resolve(config.originalRosterAudit),'utf8')).eligible);
const schedule=config?.schedule||[[55,55,924020801],[56,57,924020802],[91,55,924020803]];
const report={schema:1,scope:'End-to-end technical smoke, source Base depth1 on both seats, real final rosters, source mulligans/search/PlayMaker/stored live decisions. Partial port; not high-difficulty mixed-policy comparison.',
 schedule,maxTurns:200,maxCallbacksPerSearch:config?.controller?100000:4000,maxWallMsPerGame:config?.controller?180000:30000,ratingPermitted:false,nativeProcessesAllowed:false,records:[]};
report.controller=!!config?.controller;
report.moduleSha256=Object.fromEntries(fs.readdirSync(path.join(__dirname,'beta_js092')).filter(n=>n.endsWith('.cjs')).map(n=>[n,crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'beta_js092',n))).digest('hex')]));
report.config=config;
for(const [left,right,seed]of schedule){
 const runtime=createRuntime(rules,seed),prototype=runtime.newSession().constructor.prototype;
 for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])prototype[name]=()=>{throw Error('P19 selector forbidden: '+name);};
 const g=runtime.newSession();g.externalPolicyMask=3;const a=decks.find(d=>d.presetId===left),b=decks.find(d=>d.presetId===right);
 const profiles=[null,...[a,b].map(d=>config?.profileByFaction?personality(config.profileByFaction[d.faction]):basePersonality())];
 const record={left,right,seed,profiles:profiles.slice(1).map(p=>p.name),fingerprint:runtime.fingerprint,turns:0,searchCallbacks:0,liveCallbacks:0,mulliganCallbacks:0,trace:[]},started=Date.now();
 try{
  if(!g.InitializeWithDecks(a.templateIds,b.templateIds,a.leader,b.leader,left,right))throw Error('Initialize failed');g.recordVisuals=false;
  while(g.Snapshot().matchWinnerMask===0){
   if(Date.now()-started>report.maxWallMsPerGame)throw Error('Technical game wall limit');
   if(g.IsFatal())throw Error(g.GetMessage());
   if(g.mulligan){stepMulligan(g,profiles[g.RequestDecisionSide()]);record.mulliganCallbacks++;continue;}
   if(g.waiting){if(!g.BeginNextRound())throw Error('Round transition rejected');continue;}
   if(g.IsPending())throw Error('Live action left unowned pending request');
   if(++record.turns>report.maxTurns)throw Error('Technical turn limit');
   const p=profiles[g.Snapshot().currentPlayerId];if(p.TreeSearchType!=='AlphaBeta'||p.EvaluatorType!=='MiniMax'||p.CardPickerType!=='BestCardForPersonality')throw Error('Source profile policy path not ported: '+p.name);
   if(config?.controller){
    const side=g.Snapshot().currentPlayerId,controller=new BetaTurnController(runtime,p,{now:()=>Date.now()});controller.start(g);
    let callbacks=0;while(!controller.finished){const r=controller.step();if(r.mutations>1)throw Error('Controller action budget violated');if(++callbacks>report.maxCallbacksPerSearch)throw Error('Technical controller callback limit');}
    record.searchCallbacks+=controller.searchCallbacks;record.liveCallbacks+=controller.replay.callbacks;
    const chosen=controller.chosen,template=chosen.decision?g.FindCard(chosen.decision.cardId).TemplateId():0;
    record.trace.push({side,template,round:g.Snapshot().roundNumber,strategy:controller.strategy.strategy,playmakerError:controller.playmakerError,
     finishReason:controller.search.finishReason,forceRequested:controller.forceRequested,completedDepth:controller.search.completedDepth,
     hints:chosen.choiceRecords.map(r=>[r.source,r.kind,r.hint]),score:[g.Score(1),g.Score(2)]});
    continue;
   }
   const choices=new BetaChoiceHandlers(runtime,p),tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g),e=new BetaMiniMaxEvaluator(p);
   const side=g.Snapshot().currentPlayerId,search=new BetaAlphaBetaSearch({tryPlayAction:n=>tree.tryPlayAction(n),score:n=>e.evaluate(n),finished:n=>n.terminal});
   search.start(root,p,side);let callbacks=0;
   while(!search.finished){const before=tree.mutations,r=search.step(1,32);if(tree.mutations-before>1||r.actionAttempts>1)throw Error('Search action budget violated');if(++callbacks>report.maxCallbacksPerSearch)throw Error('Technical search callback limit');}
   record.searchCallbacks+=callbacks;const strategic=new BetaPlayMaker().apply(root,p),chosen=root.children[0];if(!chosen)throw Error('Source search has no chosen action');
   const template=chosen.decision?g.FindCard(chosen.decision.cardId).TemplateId():0;
   const replay=new BetaActionReplay(runtime,p,g,chosen);while(!replay.finished){if(replay.step().mutations!==1)throw Error('Live action budget violated');record.liveCallbacks++;if(replay.callbacks>100)throw Error('Live continuation limit');}
   record.trace.push({side,template,round:g.Snapshot().roundNumber,strategy:strategic.strategy,hints:chosen.choiceRecords.map(r=>[r.source,r.kind,r.hint]),score:[g.Score(1),g.Score(2)]});
  }
  record.status='technical-game-complete';record.winner=g.Snapshot().matchWinnerMask;record.crowns=[g.Snapshot().playerOne.crowns,g.Snapshot().playerTwo.crowns];
 }catch(e){record.status='technical-incomplete';record.error=String(e.message);record.stack=String(e.stack).split('\n').slice(1,5);}
 record.ms=Date.now()-started;report.records.push(record);fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({...record,trace:undefined}));
}
report.complete=true;report.completedGames=report.records.filter(r=>r.status==='technical-game-complete').length;report.incompleteGames=report.records.length-report.completedGames;
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({completedGames:report.completedGames,incompleteGames:report.incompleteGames,ratingPermitted:false}));

/* Technical coverage audit, NOT a tournament or strength comparison.
 * Incomplete/unsupported positions are retained as diagnostics, never losses. */
'use strict';
const fs=require('fs'),path=require('path');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,basePersonality}=require('./beta_js092/session.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaAlphaBetaSearch}=require('./beta_js092/search.cjs'),{BetaMiniMaxEvaluator}=require('./beta_js092/core.cjs');
const {BetaPlayMaker}=require('./beta_js092/playmaker.cjs');
const rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);if(fs.existsSync(out))throw Error('Preserve prior audit; choose a fresh output');
const p=basePersonality(),runtime=createRuntime(rules,924020501);
const decks=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
const prototype=runtime.newSession().constructor.prototype;
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])prototype[name]=()=>{throw Error('P19 selector forbidden: '+name);};
const report={schema:1,scope:'Technical Base-profile depth1 opening search plus original PlayMaker after real source mulligans on all46 rosters; incomplete request integration, not a strength comparison.',
 fingerprint:runtime.fingerprint,seed:924020501,rosters:decks.length,maxCallbacksPerOpening:2000,maxWallMsPerOpening:5000,
 ratingPermitted:false,nativeProcessesAllowed:false,records:[]};
for(const d of decks){
 const started=Date.now(),record={preset:d.presetId};let tree=null,search=null;
 try{
  const g=runtime.newSession();g.externalPolicyMask=3;
  if(!g.InitializeWithDecks(d.templateIds,d.templateIds,d.leader,d.leader,d.presetId,d.presetId))throw Error('Initialize rejected');
  let mulliganSteps=0;while(g.mulligan){stepMulligan(g,p);if(++mulliganSteps>8)throw Error('Mulligan stalled');}
  const side=g.Snapshot().currentPlayerId,choices=new BetaChoiceHandlers(runtime,p);tree=new BetaGameTree(runtime,p,choices.hooks());
  const root=tree.root(g),e=new BetaMiniMaxEvaluator(p);
  search=new BetaAlphaBetaSearch({tryPlayAction:n=>tree.tryPlayAction(n),score:n=>e.evaluate(n),finished:n=>n.terminal});
  search.start(root,p,side);let callbacks=0;
  while(!search.finished){
   const before=tree.mutations,r=search.step(1,32);if(tree.mutations-before>1||r.actionAttempts>1)throw Error('Cooperative action budget violated');
   if(++callbacks>report.maxCallbacksPerOpening||Date.now()-started>report.maxWallMsPerOpening)throw Error('Technical opening audit limit reached');
  }
  const bestBefore=root.children[0]?.id,playmaker=new BetaPlayMaker().apply(root,p);
  Object.assign(record,{status:'depth1-complete',side,mulliganSteps,callbacks,rootChildren:root.children.length,nodes:search.explored,playmaker,bestBefore,bestAfter:root.children[0]?.id});
 }catch(e){Object.assign(record,{status:'technical-incomplete',error:String(e.message),stack:String(e.stack).split('\n').slice(1,4)});}
 record.mutations=tree?.mutations||0;record.nodes=search?.explored||0;record.ms=Date.now()-started;
 report.records.push(record);fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(record));
}
report.complete=true;report.completedOpenings=report.records.filter(r=>r.status==='depth1-complete').length;
report.incompleteOpenings=report.rosters-report.completedOpenings;fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({completedOpenings:report.completedOpenings,incompleteOpenings:report.incompleteOpenings,ratingPermitted:false}));

/* Four entrant groups, one current set of battle mechanics. Historical0.9.1
 * runs its verified original policy graft; only one live JS state advances.
 * This module does not choose an experiment schedule or award error losses. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {createRuntime}=require('./session.cjs'),{personality}=require('./profiles.cjs');
const {BetaTurnController}=require('./controller.cjs'),{stepMulligan}=require('./mulligan.cjs');
const practice={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
function entrants({current,original091,originalRosters}){
 const extract=require('../versioned_match092.js').extract;
 const result=[];
 for(const [group,snapshot]of [['091',original091],['092',current],['beta092',current]])
  for(const d of extract(snapshot))result.push({...d,key:group+':'+d.presetId,group,policy:group.startsWith('beta')?'beta':group,profile:practice[d.faction]});
 const audited=JSON.parse(fs.readFileSync(originalRosters,'utf8'));
 for(const d of audited.eligible)result.push({...d,key:'betaOriginal:'+d.asset,basePreset:d.presetId,group:'betaOriginal',policy:'beta'});
 return result;
}
function playMatch(config,left,right,seed){
 const runtime=createRuntime(config.current,seed),legacy=[left,right].some(d=>d.policy==='091')?createRuntime(config.current,seed,config.policy091):null;
 let g=runtime.newSession(),activeRuntime=runtime,activePolicy='idle';const seats=[null,left,right];
 const betaMask=(left.policy==='beta'?1:0)|(right.policy==='beta'?2:0),start=Date.now();
 const record={left:left.key,right:right.key,seed,commonFingerprint:runtime.fingerprint,oldPolicy:legacy?.policyIdentity||null,
  dispatches:{'091':0,'092':0,beta:0},betaSearchCallbacks:0,betaForcedSearches:0,betaPeakCallbackMs:0,betaPlaymakerErrors:[],trace:[]};
 for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex']){
  const prototype=g.constructor.prototype,original=prototype[name];prototype[name]=function(...args){
   if(activePolicy==='beta'||(this.externalPolicyMask===3&&!activePolicy.startsWith('mulligan:')))throw Error('Current-policy selector reached Beta state: '+name);
   return original.apply(this,args);
  };
 }
 const targetRuntime=policy=>policy==='091'?legacy:runtime;
 function transfer(target){if(activeRuntime!==target){g=target.deserialize(activeRuntime.serialize(g));activeRuntime=target;}}
 function withInternal(side,policy,callback){
  const target=targetRuntime(policy);transfer(target);if(side===1)target.swap(g);
  record.dispatches[policy]++;const result=callback(g);
  if(side===1)target.swap(g);transfer(runtime);return result;
 }
 try{
  g.externalPolicyMask=3;
  if(!g.InitializeWithDecks(left.templateIds,right.templateIds,left.leader,right.leader,left.basePreset??left.presetId,right.basePreset??right.presetId))throw Error('Initialization rejected');
  g.recordVisuals=false;g.aiSimDamp=40;
  for(const d of [left,right]){const valid=runtime.validateDeck(d.templateIds,d.faction,d.leader);if(!valid.valid)throw Error('Entrant is illegal under common rules '+d.key+': '+valid.message);}
  for(let decisions=0;!g.Snapshot().matchWinnerMask;decisions++){
   if(decisions>=500||Date.now()-start>240000)throw Error('Technical match limit');
   if(g.IsFatal())throw Error(g.GetMessage());
   if(g.mulligan){
    const side=g.RequestDecisionSide(),entrant=seats[side];g.externalPolicyMask=3;
    if(entrant.policy==='beta'){activePolicy='beta';record.dispatches.beta++;stepMulligan(g,personality(entrant.profile));}
    else{
     activePolicy='mulligan:'+entrant.policy;
     withInternal(side,entrant.policy,game=>game.AiMulligan(game.mulliganBudget));
     g.RefreshMulligan();if(!g.FinishMulligan(g.requestId))throw Error('Historical/current mulligan rejected');
    }
    continue;
   }
   if(g.waiting){g.externalPolicyMask=3;if(!g.BeginNextRound())throw Error('Round transition rejected');continue;}
   if(g.IsPending())throw Error('Unowned pending request: '+g.GetMessage());
   g.externalPolicyMask=betaMask;const side=g.Snapshot().currentPlayerId,entrant=seats[side],round=g.Snapshot().roundNumber;
   if(entrant.policy==='beta'){
    activePolicy='beta';
    record.dispatches.beta++;const p=personality(entrant.profile),controller=new BetaTurnController(runtime,p,{now:()=>Date.now()});controller.start(g);
    let callbacks=0;while(!controller.finished){const before=Date.now(),r=controller.step();record.betaPeakCallbackMs=Math.max(record.betaPeakCallbackMs,Date.now()-before);if(r.mutations>1)throw Error('Beta action budget violated');if(++callbacks>100000)throw Error('Technical Beta callback limit');}
    record.betaSearchCallbacks+=controller.searchCallbacks;if(controller.forceRequested)record.betaForcedSearches++;
    if(controller.playmakerError)record.betaPlaymakerErrors.push(controller.playmakerError);
    record.trace.push({side,round,policy:'beta',profile:p.name,template:controller.chosen.decision?g.FindCard(controller.chosen.decision.cardId).TemplateId():0,
     finishReason:controller.search.finishReason,completedDepth:controller.search.completedDepth,score:[g.Score(1),g.Score(2)]});
   }else{
    activePolicy=entrant.policy;
    if(!withInternal(side,entrant.policy,game=>game.OpponentStep()))throw Error('Policy turn rejected '+g.GetMessage());
    record.trace.push({side,round,policy:entrant.policy,score:[g.Score(1),g.Score(2)]});
   }
  }
  record.status='complete';record.winner=g.Snapshot().matchWinnerMask;record.crowns=[g.Snapshot().playerOne.crowns,g.Snapshot().playerTwo.crowns];
  record.finalStateSha256=crypto.createHash('sha256').update(JSON.stringify(runtime.serialize(g))).digest('hex');
 }catch(e){record.status='technical-error';record.error=String(e.stack);}
 record.ms=Date.now()-start;return record;
}
module.exports={entrants,playMatch};

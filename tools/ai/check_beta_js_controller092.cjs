'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,basePersonality,stateFromSession}=require('./beta_js092/session.cjs');
const {BetaTurnController}=require('./beta_js092/controller.cjs');
const {BetaActionReplay}=require('./beta_js092/replay.cjs');
const {stepMulligan}=require('./beta_js092/mulligan.cjs');
const {Status}=require('./beta_js092/search.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924022001),p=basePersonality();let checks=0;
function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','AiAdjacencyIndex'])runtime.newSession().constructor.prototype[name]=()=>{throw Error('P19 selector forbidden: '+name);};
const live=runtime.newSession();live.externalPolicyMask=3;assert(live.InitializeWithPresets(55,55));while(live.mulligan)stepMulligan(live,p);live.recordVisuals=false;
const original=stateFromSession(live);
for(const force of [false,true]){
 const game=runtime.cloneSession(live);let time=0;const c=new BetaTurnController(runtime,p,{now:()=>time});c.start(game);
 eq(c.forceAfterMs,(p.MaxTimeAllowed+1)*1000,'source AIPlayer delay plus module force-fetch1s');
 let steps=0,mutations=0;
 while(!c.finished){
  if(force&&c.search.explored>0)time=c.forceAfterMs;
  const r=c.step();eq(r.mutations<=1,true,'one mutation per controller step');mutations+=r.mutations;assert(++steps<20000);
 }
 eq(c.forceRequested,force,'forced stop only at supplied deadline');
 eq(c.chosen.status,Status.OK,'source StripNodes excludes uninitialised/error nodes');
 eq(c.scoredNodes.every(n=>n.status===Status.OK&&n.state),true,'only completed legal nodes may be picked');
 eq(c.replay.callbacks>0,true,'completed stored live replay');
 eq(stateFromSession(live),original,'search and live replay isolate original fixture');
 const independent=runtime.cloneSession(live),replay=new BetaActionReplay(runtime,p,independent,c.chosen);while(!replay.finished)replay.step();
 eq(stateFromSession(game),stateFromSession(independent),'same stored decision independently replays');
 eq(c.step(),{finished:true,mutations:0},'finished controller has no further action');
 if(force)eq(c.search.finishReason,'stopped','source force-fetch requests stop');
}
const report={checks,fingerprint:runtime.fingerprint,nativeProcessesAllowed:false,currentPolicySelectorsAllowed:false,scope:'Normal and forced source deadline, source status filtering, one action per callback, stored replay and original state isolation',ratingPermitted:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-controller-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

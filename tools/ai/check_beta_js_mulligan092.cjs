'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');
for(const n of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[n]=()=>{throw Error('Native process forbidden');};
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const {stepMulligan,chooseMulligan}=require('./beta_js092/mulligan.cjs');
const rules=path.resolve(process.argv[2]),runtime=createRuntime(rules,924020201),p=basePersonality();
const decks=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
let checks=0;const decisions=[];
function check(v,label){assert(v,label);checks++;}
for(const d of decks){
 const g=runtime.newSession();g.externalPolicyMask=3;
 g.AiMulligan=()=>{throw Error('Current mulligan forbidden');};
 g.AiCardKeepValue=()=>{throw Error('Current keep-value forbidden');};
 g.AiMulliganCandidate=()=>{throw Error('Current candidate forbidden');};
 check(g.InitializeWithDecks(d.templateIds,d.templateIds,d.leader,d.leader,d.presetId,d.presetId),'initialize real roster');
 for(const round of [1,2]){
  const seen=new Set();let steps=0;
  while(g.mulligan){
   const side=g.RequestDecisionSide();seen.add(side);
   const before=stateFromSession(g).cards.filter(c=>c.side===side&&c.zone===8&&c.playable);
   const expected=chooseMulligan(before,p),record=[];
   const selected=stepMulligan(g,p,record);
   check(selected.cardId===(expected?expected.id:0),'source picker owns actual exchange');
   check(record.length===1&&record[0]===selected,'one recorded decision per step');
   check(g.CountLocation(side,8)===before.length,'exchange preserves actual hand size');
   decisions.push({preset:d.presetId,round,...selected});
   check(++steps<=8,'bounded initial/later hooks');
  }
  check(seen.size===2,'both seats use source picker');
  if(round===1){check(g.Pass(g.Snapshot().currentPlayerId),'first pass');check(g.Pass(g.Snapshot().currentPlayerId),'second pass');check(g.BeginNextRound(),'later round opens mulligans');}
 }
}
const report={checks,rosters:decks.length,initialAndLaterSeatRequests:decks.length*4,decisions:decisions.length,
 fingerprint:runtime.fingerprint,currentPolicyMulliganCalls:0,maxGameMutationsPerStep:1,
 scope:'Source mulligan picker connected to actual shared-engine initial/later requests for both seats. Pass-only round transitions, not strength games.',
 fullAiPortComplete:false,fullMatchReady:false};
const out=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-mulligan-proof.json');
fs.writeFileSync(out,JSON.stringify({...report,records:decisions},null,2)+'\n');console.log(JSON.stringify(report));

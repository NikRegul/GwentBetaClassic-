'use strict';
// Technical action coverage. A successful play alone is NOT proof of every card formula.
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),rules=path.resolve(process.argv[2]),out=path.resolve(process.argv[3]);
if(fs.existsSync(out))throw Error('Fresh report required');
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
for(const [n,h] of Object.entries(manifest.snapshotFiles))if(crypto.createHash('sha256').update(fs.readFileSync(path.join(rules,n))).digest('hex')!==h)throw Error('Frozen input changed: '+n);
const templates=require('./beta_js092/data/templates.json');
const catalogPath=Object.keys(manifest.snapshotFiles).find(n=>n.endsWith('/duelCatalog.ws'));
if(!catalogPath)throw Error('Frozen catalog source required');
const catalog=fs.readFileSync(path.join(rules,catalogPath),'utf8');
const boardPath=Object.keys(manifest.snapshotFiles).find(n=>n.endsWith('/developmentBoardMenu.ws'));
const board=fs.readFileSync(path.join(rules,boardPath),'utf8');
const closing=board.slice(board.indexOf('event OnClosingMenu()'));
// Execute the shipped result-dispatch branch, with game APIs mocked. No quest
// completion or retail save/close behavior is claimed by this focused check.
const resultBranch=closing.slice(closing.indexOf('if(npcMatch){'),closing.indexOf('manager.gameRequested'))+'}';
const knownIds=[...new Set([...Object.keys(templates).map(Number),...Array.from(catalog.matchAll(/\bcase\s+(\d+)\s*:/g),m=>Number(m[1]))])].filter(n=>n>=100000).sort((a,b)=>a-b);
const ctx=vm.createContext({console:{log(){}},ids:knownIds,limit:Number(process.argv[4]||0),onlyLeaders:process.argv.includes('--leaders')});
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
vm.runInContext(source+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;
let random=198001;Host.random=()=>{random^=random<<13;random^=random>>>17;random^=random<<5;return (random>>>0)/4294967296;};
const cards=ids.map(id=>BetaGwentDuelDefinition(id)).filter(d=>d.header.templateId>0&&[2,4].includes(d.header.typeMask));
const records=[],failures=[];let assertions=0;
function check(v,n){assertions++;if(!v)throw Error(n);}
function add(g,t,zone,index,side){const key={v:0};check(g.registry.Allocate(key),'allocate');const c=new CBetaGwentDuelCard();c.Setup(g,key.v,t,side,zone,index);g.registry.Put(key.v,c);g.live.push(c);return c;}
function blank(side,kind,id){
 const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(54,54),'initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.pendingIds=[];
 g.waiting=false;g.recordVisuals=false;g.externalPolicyMask=3;g.weatherProfile=false;
 g.match.currentPlayerId=side;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=2;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=0;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 const support=[112405,132213,152310,122315,142315,162303,200040,112101,152214].filter(t=>BetaGwentDuelDefinition(t).header.typeMask===4);
 for(const s of [1,2]){
  if(kind!=='empty-board')for(let i=0;i<support.length;i++){const c=add(g,support[i],[1,2,4][i%3],Math.floor(i/3),s);if(i===0)c.power.SetCurrentPair(3,0);}
  if(kind!=='last-card')for(let i=0;i<4;i++)add(g,support[i%support.length],8,i,s);
  if(kind!=='empty-deck'&&kind!=='last-card')for(let i=0;i<12;i++)add(g,i===0?id:support[i%support.length],16,i,s);
  for(let i=0;i<support.length;i++)add(g,support[i],32,i,s);
 }
 return g;
}
function resolve(g){let steps=0;
 while(g.IsPending()){
  check(++steps<300,'pending request bound');let applied=false;
  if(g.mulligan){check(g.FinishMulligan(g.requestId),'finish nested mulligan');continue;}
  if(g.pendingLeader||g.pendingRally||g.pendingRow){
   for(const side of [1,2])for(const row of [1,2,4])if(!applied&&g.CanSelectRow(g.requestId,side,row))applied=g.SelectRow(g.requestId,side,row);
  }else if(g.pendingChoice){for(const id of [...g.pendingIds])if(!applied)applied=g.SelectTemplateChoice(g.requestId,id);}
  else {for(const id of [...g.pendingIds])if(!applied)applied=g.SelectTarget(g.requestId,id);}
  if(!applied)applied=g.FinishTarget(g.requestId);
  check(applied,'legal request can complete: '+g.GetMessage());check(!g.IsFatal(),'request not fatal: '+g.GetMessage());
 }
 g.FlushEffects();g.FlushDeaths();check(!g.IsFatal(),'flush not fatal: '+g.GetMessage());check(!g.IsPending(),'no stranded request');return steps;
}
globalThis.cardMatrixStep=function(d,side,kind){const record={id:d.header.templateId,title:d.title,type:d.header.typeMask,side,kind,collectible:BetaGwentDuelCollectible(d.header.templateId)};
 try{
  random=(198001+d.header.templateId*31+side)>>>0;const g=blank(side,kind,d.header.templateId),isLeader=BetaGwentDuelIsLeader(d.header.templateId);
  if(isLeader)record.execution='leader-ability';
  const mode=d.header.templateId===113401||d.header.templateId===113402;
  const c=add(g,mode?113303:d.header.templateId,isLeader?64:8,isLeader?0:g.CountLocation(side,8),side);
  if(isLeader){if(side===1)g.leaderTemplateOne=d.header.templateId;else g.leaderTemplateTwo=d.header.templateId;}
  const accepted=isLeader?g.UseLeader(side):g.Play(side,c.cardState.instanceId,1);
  if(d.header.templateId===113201&&kind==='empty-board'){
   check(!accepted&&!g.IsFatal()&&c.Snapshot().locationMask===8,'Decoy without a legal unit is safely rejected');record.expectedRejection=true;record.ok=true;records.push(record);return record;
  }
  check(accepted,'card accepted: '+g.GetMessage());
  if(mode){check(g.IsFirstLightChoice()&&g.SelectFirstLight(g.requestId,d.header.templateId),'execute real First Light mode');record.execution='first-light-choice';}
  record.requests=resolve(g);record.finalZone=c.Snapshot().locationMask;
  check(new Set(g.live.map(c=>c.cardState.instanceId)).size===g.live.length,'unique registry identities');
  for(const x of g.live){const s=x.Snapshot();check(Number.isFinite(s.power.currentPower)&&Number.isFinite(s.power.armor),'finite powers');}
  record.ok=true;
 }catch(e){record.ok=false;record.error=e.message;failures.push(record);}
 records.push(record);return record;
};
globalThis.matrixDefinitions=onlyLeaders?cards.filter(d=>BetaGwentDuelIsLeader(d.header.templateId)):limit?cards.slice(0,limit):cards;
globalThis.matrixRareCases=function(){const rare=[];
 for(const crowns of [[0,0],[1,1],[0,1],[1,0]])for(const score of [0,4]){
  const g=blank(1,'last-card',112101);g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));
  g.match.roundNumber=crowns[0]+crowns[1]===0?1:2;
  g.match.playerOne.crowns=crowns[0];g.match.playerTwo.crowns=crowns[1];
  if(score)for(const side of [1,2])add(g,112101,1,0,side).power.SetCurrentPair(score,0);
  check(g.Score(1)===score&&g.Score(2)===score,'tie fixture score');
  check(g.Pass(1)&&g.Pass(2),'two legal passes end tied round');
  let s=g.Snapshot();check(s.playerOne.crowns===crowns[0]+1&&s.playerTwo.crowns===crowns[1]+1,'tie awards both crowns');
  const winner=(crowns[0]===1?1:0)|(crowns[1]===1?2:0);check(s.matchWinnerMask===winner,'tie result follows previous crowns');
  check(!g.Pass(1)&&!g.Pass(2),'closed round cannot award crowns twice');
  if(!winner){check(g.BeginNextRound(),'tied round continues');while(g.mulligan)check(g.FinishMulligan(g.requestId),'empty-deck next-round mulligan completes');check(!g.IsFatal(),'empty-deck next round is safe');}
  else check(!g.BeginNextRound(),'finished match cannot reopen');
  rare.push({kind:'tie-and-double-pass',crowns,score,winner,ok:true});
 }
 return rare;
};
globalThis.matrixReport=()=>({complete:true,cards:cards.length,testedCards:matrixDefinitions.length,assertions,records,failures,nativeGameplayExecuted:false,scope:'Each accepted engine action in fixtures; semantic ability expectations remain in targeted regressions'});
`,ctx,{filename:'card-matrix198.bundle.js',timeout:120000});
const definitions=ctx.matrixDefinitions,scenes=['populated','empty-deck','empty-board','last-card'];
let n=0;
for(const d of definitions){for(const side of [1,2])for(const scene of scenes)ctx.cardMatrixStep(d,side,scene);if(++n%25===0){const report=ctx.matrixReport();fs.writeFileSync(out,JSON.stringify({...report,complete:false,platform:manifest.platform||'common',fingerprint:manifest.fingerprint},null,2));console.log(JSON.stringify({cards:n,total:definitions.length,failures:report.failures.length}));}}
const rareCases=ctx.matrixRareCases();
for(const npcMatch of [false,true])for(const selectingDecks of [false,true])for(const winner of [0,1,2,3]){
 const states=[],state=vm.createContext({npcMatch,selectingDecks,result:{matchWinnerMask:0},manager:null,
  AwardMatchReward(){},theGame:{GetGwintManager:()=>({})},session:{Snapshot:()=>({matchWinnerMask:winner})},
  thePlayer:{SetGwintMinigameState:v=>states.push(v)},EMS_End_PlayerWon:1,EMS_End_PlayerLost:2,EMS_End_PlayerForfeited:4});
 vm.runInContext(resultBranch,state);
 // Classic's native enum lacks PlayerForfeited; its compatibility adapter
 // deliberately maps an unfinished duel to PlayerLost.
 const forfeited=manifest.platform==='classic'?2:6;
 const expected=!npcMatch?[]:[!selectingDecks&&winner===1?1:!selectingDecks&&winner!==0?2:forfeited];
 if(JSON.stringify(states)!==JSON.stringify(expected))throw Error('Actual NPC close result dispatch differs: '+JSON.stringify({npcMatch,selectingDecks,winner,states,expected,resultBranch}));
 rareCases.push({kind:'npc-close-result',npcMatch,selectingDecks,winner,state:states,ok:true});
}
const report={...ctx.matrixReport(),rareCases,actualNativeResultDispatch:true,platform:manifest.platform||'common',fingerprint:manifest.fingerprint,checkerSha256:crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex')};fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({complete:true,cards:report.testedCards,cases:report.records.length,failures:report.failures.length,nativeGameplayExecuted:false}));
if(report.failures.length)process.exitCode=1;

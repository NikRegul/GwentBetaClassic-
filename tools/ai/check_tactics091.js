// Behaviour of the real production decision path, including counterexamples.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const ctx=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const cases=[];
function blank(profile=54,round=1,enemyHand=4){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 // Synthetic mid-match positions have no declared original list. Exercise
 // the public fallback (also used after switching from medium to high).
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();
 g.match.roundNumber=round;g.match.playerOne.crowns=0;g.match.playerTwo.crowns=round===2?1:0;
 g.archetypeAI.profile=BetaGwentAIPresetProfile(profile);g.archetypeAI.family=BetaGwentAIProfileFamily(g.archetypeAI.profile);
 g.aiSimDamp=40;for(let i=0;i<enemyHand;i++)add(g,112101,8,i,1);return g;
}
function act(g){
 const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'production decision completes');
 cases.push({plan:g.archetypeAI.roundPlan,logs:logs.filter(s=>/event=(SELECT|PLAN|PASS)/.test(s))});
 return logs;
}
function ready(g){g.match.currentPlayerId=2;g.match.turnActive=true;g.match.playerTwo.hasPassed=false;g.ClearAiPreparation();}
function combo(g){return [132305,201781,113309,112102,112101,132201].map(id=>add(g,id,8));}
// 1/3: a concrete cheap engine is played while valuable threats stay in hand.
for(const enemyAnswers of ['costly','ignored','cheap-catch','deciding']){
 const g=blank(),cards=combo(g);act(g);
 check(g.archetypeAI.roundPlan===3,'intention is established before observing the answer');
 check(cards.find(c=>c.TemplateId()===132201).Snapshot().locationMask!==8,'secondary engine is really deployed');
 check(cards.find(c=>c.TemplateId()===201781).Snapshot().locationMask===8,'key threat is retained');
 // Opponent's public response is constructed explicitly; no hidden identity
 // is passed to the decision code. The subsequent choice uses the real state.
 if(enemyAnswers!=='ignored'){
  add(g,122102,1,0,1,3);
  if(enemyAnswers==='cheap-catch')add(g,112101,1,1,1,10);
  else for(let i=0;i<4;i++)add(g,112101,1<<i%3,i+1,1,12+i);
 }
 if(enemyAnswers==='deciding'){g.match.playerOne.crowns=1;g.match.roundNumber=2;}
 ready(g);act(g);
 if(enemyAnswers==='costly')check(g.match.playerTwo.hasPassed,'expensive public answer ends optional pressure');
 if(enemyAnswers==='ignored')check(!g.match.playerTwo.hasPassed,'ignored bait does not cause an automatic concession');
 if(enemyAnswers==='cheap-catch')check(!g.match.playerTwo.hasPassed,'cheap useful catch overrides the prior plan');
 if(enemyAnswers==='deciding')check(!g.match.playerTwo.hasPassed,'survival overrides a previous bait plan');
}
// 3: a real enemy removal/lock is spent on the secondary threat; the AI can
// then deploy its key threat. The response is a legal human target selection.
for(const response of [113301,122211]){
 const g=blank(),cards=combo(g);act(g);
 const bait=cards.find(c=>c.TemplateId()===132201),key=cards.find(c=>c.TemplateId()===201781);
 const reply=add(g,response,8,4,1);
 check(g.Play(1,reply.Snapshot().instanceId,1),'opponent plays a real control response '+response);
 check(g.SelectTarget(g.requestId,bait.Snapshot().instanceId),'opponent targets the actual bait '+response);
 check(response===113301?bait.Snapshot().locationMask===32:(bait.Snapshot().tokenMask&4)!==0,'control actually removes or locks the bait '+response);
 act(g);
 if(response===122211)check(key.Snapshot().locationMask!==8,'key threat follows the spent lock and has a real duel target');
 else check(key.Snapshot().locationMask===8,'spent removal does not justify a duel engine without an enemy target');
}
// 2: the decision is tested at the real dry-pass gate, not a helper formula.
for(const profile of [54,68]){
 const g=blank(profile,2);
 if(profile===68){add(g,132201,8,0);add(g,132305,8,1);}
 for(let i=profile===68?2:0;i<6;i++)add(g,112101,8,i,2,10);act(g);
 if(profile===54)check(!g.match.playerTwo.hasPassed&&g.archetypeAI.roundPlan===2,'short-round hand pressures a publicly plausible combo');
 else check(g.match.playerTwo.hasPassed&&g.archetypeAI.roundPlan===1,'remaining engine package preserves a long final');
}
{
 const g=blank(54,2);for(let i=0;i<3;i++)add(g,112101,8,i,2,10);act(g);
 check(g.match.playerTwo.hasPassed,'pressure does not consume the last three cards on an empty board');
}
// 4: select control through OpponentStep, with active/locked threat variants.
for(const locked of [false,true]){
 const g=blank(54,3);g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 const engine=add(g,201624,1,0,1),body=add(g,112101,1,1,1,9);body.power.basePower=9;
 if(locked)engine.AddTokens(4);
 const removal=add(g,113301,8);for(let i=0;i<3;i++)add(g,112101,8,i+1,2,1);act(g);
 check(removal.Snapshot().locationMask===32,'real removal is played');
 if(!locked)check(engine.Snapshot().locationMask===32&&body.Snapshot().power.currentPower===9,'active growing threat is removed before the larger body');
 else check(body.Snapshot().locationMask===32,'locked threat loses its future-value priority');
}
// 5: sacrifice fodder with a concrete Deathwish, preserving the live engine.
{
 const g=blank(61,3);g.match.playerOne.crowns=g.match.playerTwo.crowns=1;
 const egg=add(g,132310,1,0),engine=add(g,132201,1,1),consumer=add(g,201701,8);
 act(g);check(engine.Snapshot().locationMask!==32,'consume keeps the live engine');
 check(egg.Snapshot().locationMask===32,'consume triggers the real fodder Deathwish');
}
// 6: a large public lead only taxes multiple replies if a one-card reset
// cannot erase it. An unknown list remains cautious; an announced list with
// no removal permits the pass. R3 is required regardless of that envelope.
for(const round of [1,3])for(const removal of ['absent','possible','unknown']){
 const g=blank(54,round);g.match.playerOne.crowns=round===3?1:0;g.match.playerTwo.crowns=round===3?1:0;
 if(removal!=='unknown')g.aiStartingDeckOne=[112101,112101,112101,removal==='possible'?113309:112101];
 add(g,112101,1,0,2,65);add(g,112101,1,0,1,10);
 for(let i=0;i<4;i++)add(g,112101,8,i,2,8);act(g);
 check(g.match.playerTwo.hasPassed===(round===1&&removal==='absent'),'optional pass respects a possible one-card reset and known starting list');
}
// 7: preserve Scorch with last say; use it when the enemy has already passed.
for(const passed of [false,true]){
 const g=blank(54,3,1);g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=passed;
 const revealed=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);revealed.AddTokens(64);revealed.power.SetCurrentPair(30,0);
 add(g,112101,1,0,2,6);add(g,112101,1,0,1,16);const scorch=add(g,113309,8),body=add(g,112101,8,1,2,passed?5:12);act(g);
 if(!passed){
  check(body.Snapshot().locationMask!==8,'useful body preserves the last control reply');check(scorch.Snapshot().locationMask===8,'scarce removal remains available');
  check(g.Play(1,revealed.Snapshot().instanceId,1),'opponent really plays the publicly revealed finisher');
  act(g);check(scorch.Snapshot().locationMask===32,'saved control is actually used on the last reply');
  check(g.Score(2)>g.Score(1),'waiting for the finisher wins the final score');
 }
 else check(scorch.Snapshot().locationMask===32,'last control is used for the sufficient catch after enemy pass');
}
// 8: scarce-resource catch-up and match survival, across all strengths.
for(const strength of [2,3,4]){
 Host.strength=strength;const g=blank(54,1,1);g.match.playerOne.hasPassed=true;
 add(g,112101,1,0,1,6);const cheap=add(g,112405,8,0,2,7),gold=add(g,112102,8);
 act(g);check(cheap.Snapshot().locationMask!==8&&gold.Snapshot().locationMask===8,'minimum sufficient card wins after pass at strength '+strength);
}
globalThis.result={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{filename:'tactics091.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.result,null,2)+'\n');

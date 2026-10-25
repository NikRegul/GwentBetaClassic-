// 0.9.2 playtest log (21 Oct 2026, preset 84): the AI boosted the opponent's Cantarella
// (a spy on our side) three times by 7, then Menno Coehoorn destroyed it: 34 points lost,
// the deciding round was lost 43:47. Boosts must avoid units the opponent can still erase.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const CANTARELLA=162210,MENNO=162102,PETER=162204,GUARD=142317,cases=[];
function side(c){return c.Snapshot().positionPlayerId;}function loc(c){return c.Snapshot().locationMask;}
function position(strength,enemyList){
 Host.strength=strength;const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=84;
 g.archetypeAI.Initialize(g,[],84,200167);
 g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 enemyList.forEach(t=>g.aiStartingDeckOne.PushBack(t));
 // The opponent's Cantarella spies for us: owner 1, on our melee row, spy token.
 const spy=add(g,CANTARELLA,1,0,2);spy.cardState.ownerId=1;spy.AddTokens(128);
 const own=add(g,112101,2,0,2,8);
 const guard=add(g,GUARD,8,0);add(g,112101,8,1,2,3);
 for(let i=0;i<4;i++)add(g,112101,8,i,1,5);
 add(g,112101,1,0,1,25);
 return {g,spy,own,guard};
}
function decide(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'AI turn completes '+label);
 cases.push({label,targets:logs.filter(s=>s.includes('TARGET_SELECT')).join(' | ').slice(0,200)});}
for(const strength of [2,3,4]){
 const {g,spy,own}=position(strength,[MENNO,PETER,112101]),before=spy.Snapshot().power.currentPower;
 check(spy.Snapshot().tokenMask&128,'fixture spy carries the spy token');
 check(g.TargetValue(spy.Snapshot(),2,2,7)<g.TargetValue(own.Snapshot(),2,2,7),'boosting a spy that Menno can destroy is worth less '+strength);
 decide(g,'menno '+strength);
 check(spy.Snapshot().power.currentPower===before,'the spy is not boosted '+strength);
 check(own.Snapshot().power.currentPower>8,'the boost goes to a safe own unit '+strength);
}
// Accumulated boosts are exposed to resets: spread instead of stacking one unit.
{
 const {g,own}=position(4,[PETER,112101]);
 const stacked=add(g,112101,2,1,2,20);// base 1 power, +19 boosted already
 check(g.TargetValue(stacked.Snapshot(),2,2,7)<g.TargetValue(own.Snapshot(),2,2,7),'a heavily boosted unit is a worse target while a reset is possible');
}
// The opponent's known list holds neither Menno nor a reset: no penalty, the old values stand.
{
 const {g,spy,own}=position(4,[112101,112101]);
 for(const c of g.live)if(side(c)===1&&loc(c)===16)c.Move(1,512,0);
 g.match.playerOne.hasPassed=false;
 check(g.TargetValue(spy.Snapshot(),2,2,7)===7&&g.TargetValue(own.Snapshot(),2,2,7)===7,'no known answer: full boost value');
}
// Below maximum difficulty the list is unknown, so Menno stays possible.
{
 const {g,spy}=position(2,[]);
 check(g.TargetValue(spy.Snapshot(),2,2,7)<7,'unknown list keeps the spy risk at lower difficulty');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'boost-exposure092.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases},null,1));

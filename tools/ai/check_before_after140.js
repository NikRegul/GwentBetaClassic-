'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
function run(dir){const c=vm.createContext({console:{log(){}}});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(dir+'/'+n,'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
 function clear(g){g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).forEach(c=>c.Move(2,512,0));}
 const results={};
 {
 const g=fixture();clear(g);g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 add(g,112101,1,0,1,5);const spy=add(g,162212,1,0,1,8);spy.Move(2,1,0);spy.AddTokens(128);const body=add(g,112101,8,0,2,16);
 g.OpponentStep();results.falseCiri={played:body.Snapshot().locationMask!==8,winner:g.Snapshot().matchWinnerMask};
 }
 {
 const g=fixture();clear(g);g.match.roundNumber=2;g.match.playerOne.crowns=1;g.leaderTemplateTwo=200166;
 add(g,112101,1,0,1,20);add(g,112101,1,0,2,15);add(g,142203,8);const leader=add(g,200166,64);
 g.OpponentStep();results.eithne={played:leader.Snapshot().locationMask!==64,passed:g.match.playerTwo.hasPassed};
 }
 {
 const g=fixture();clear(g);const medic=add(g,152310,8);add(g,152213,8);add(g,152307,8);g.archetypeAI.Refresh();
 results.medic={swapPriority:g.archetypeAI.Mulligan(medic),keepBonus:g.archetypeAI.MulliganKeepBonus(medic)};
 }
 {
 const g=fixture();clear(g);g.live.filter(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8).forEach(c=>c.Move(1,512,0));
 g.match.roundNumber=2;g.match.playerOne.crowns=1;for(let i=0;i<2;i++)add(g,112101,8,i,1);
 add(g,112101,2,0,1,59);const miruna=add(g,132108,1,0,1,4);miruna.ChangeTimer(1,2);
 add(g,112101,2,0,2,73);const victim=add(g,162210,1,0,1,25);victim.Move(2,1,0);victim.AddTokens(128);
 const first=add(g,201610,8),second=add(g,201610,8);add(g,201619,8);
 g.OpponentStep();results.miruna={passed:g.match.playerTwo.hasPassed,played:[first,second].some(c=>(c.Snapshot().locationMask&7)!==0)};
 }
 globalThis.results=results;
 `,c,{timeout:120000});return JSON.parse(JSON.stringify(c.results));}
const baseline=run('BetaGwent/build/audit140/baseline'),candidate=run('BetaGwent/build/audit140/candidate-v3');
assert(!baseline.falseCiri.played&&baseline.falseCiri.winner===1&&candidate.falseCiri.played);
assert(baseline.eithne.passed&&!baseline.eithne.played&&candidate.eithne.played&&!candidate.eithne.passed);
assert(baseline.medic.swapPriority===16&&candidate.medic.swapPriority===0);
assert(baseline.miruna.passed&&!baseline.miruna.played&&!candidate.miruna.passed&&candidate.miruna.played);
const report={stage:140,baseline,candidate,syntheticFixtures:true,actualWitcherScript:true,nativeGameTested:false};
fs.writeFileSync('BetaGwent/build/audit140/before-after.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

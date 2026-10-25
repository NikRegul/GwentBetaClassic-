'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peak=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...a){calls++;return play.apply(this,a);};
const cases=[];
for(const strength of [2,3,4]){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiSimDamp=70;g.match.roundNumber=1;g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();
 add(g,112405,1,0,2,6);add(g,112405,1,0,1,10);
 const cards=[112405,132201,113301,113209,201701].map((t,i)=>add(g,t,8,i,2));
 add(g,112405,16,0,2,8);add(g,112405,16,1,2,7);for(let i=0;i<5;i++)add(g,112405,8,i,1,6);
 const before=JSON.stringify({m:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount()});let ticks=0;
 while(true){calls=0;const ready=g.AiPreparationStep();peak=Math.max(peak,calls);check(calls<=1,'one actual simulated play per slow-device callback');
  check(JSON.stringify({m:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:g.random.DrawCount()})===before,'preparation preserves actual cards and RNG');
  if(ready)break;if(++ticks>650)throw Error('search floor stalls');}
 const exact=cards.filter(c=>g.aiPreparedIds.includes(c.Snapshot().instanceId)),roles=[...new Set(exact.map(c=>g.AiSearchRole(c.Definition())))];
 check(exact.length===(strength===4?5:3),'additional high-level candidate coverage only applies on high difficulty');
 check(g.aiPreparedUpliftIds.length===(strength===4?3:2),'bounded continuation budget respects the difficulty');
 if(strength===4)check(cards.every(c=>roles.includes(g.AiSearchRole(c.Definition()))),'every available strategic role receives an actual trial');
 cases.push({strength,exact:exact.length,roles,continuations:g.aiPreparedUpliftIds.length,ticks});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;
globalThis.report={checks,cases,peakSearchPlays:peak,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));

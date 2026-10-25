// Two public face-down cards: ordered timer worlds and finite copy counts.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');const {context:ctx,manifest}=load(path.resolve(process.argv[2]));ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],cases=[];check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function options(list,actual=142210,damp=0,strength=4){
 Host.strength=strength;Host.matchStrength=[strength,strength];const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.aiSimDamp=damp;g.aiStartingDeckOne=list.slice();
 const hidden=[add(g,actual,1,0,1),add(g,actual,2,0,1)];
 const cards=[],templates=[],timers=[],weights=[];const n=g.AiAmbushHypotheses({v:cards},{v:templates},{v:timers},{v:weights});
 return {g,hidden,cards,templates,timers,weights,n};
}
for(const template of [142210,142307]){
 const h=options([template,template]);check(h.n===4,'two timed copies have four ordered worlds: '+template);
 const worlds=[];for(let k=0;k<h.n;k++)worlds.push(h.timers.slice(k*2,k*2+2).join(','));
 check(new Set(worlds).size===4&&['1,1','1,2','2,1','2,2'].every(s=>worlds.includes(s)),'both timer orders and both equal timers represented');
 check(h.weights.every(w=>w===2),'same-template probability uses remaining copies without replacement');
 check(h.cards.length===2&&h.templates.length===8,'flattened world shape');
 cases.push({template,worlds,weights:h.weights});
}
{
 const h=options([142208,142208,142204]);const pairs=[];
 for(let k=0;k<h.n;k++)pairs.push(h.templates.slice(k*2,k*2+2).join(','));
 check(h.n===3&&new Set(pairs).size===3,'three legal ordered untimed worlds');
 check(['142208,142208','142208,142204','142204,142208'].every(s=>pairs.includes(s)),'both asymmetric trap placements retained');
 check(h.weights.every(w=>w===8),'2x1 same-kind multiplicity equals 2x1 cross-kind multiplicity');
}
{
 const h=options([142208,142204]);check(h.n===2,'one copy each supports two ordered placements');
 check(h.templates[0]!==h.templates[1]&&h.templates[2]!==h.templates[3],'one public copy cannot fill two hidden slots');
 check(options([142210]).n===0,'insufficient copies keeps conservative exit');
}
for(const [damp,strength,cap] of [[0,4,4],[50,4,1],[69,4,1],[70,4,0],[0,3,2],[0,2,0]]){
 const h=options([142208,142208,142204,142210,142307,201779],142210,damp,strength);
 check(h.n<=cap&&(cap===0?h.n===0:h.n>0),'existing budget cap '+damp+'/'+strength);
}
{
 const a=options([142210,142210],142210),b=options([142210,142210],142307);
 check(JSON.stringify([a.templates,a.timers,a.weights])===JSON.stringify([b.templates,b.timers,b.weights]),'real hidden identities do not influence pair worlds');
 const original=a.hidden.map(c=>JSON.stringify(c.Snapshot()));
 for(let k=0;k<a.n;k++){
  const clone=a.g.AiSimClone();clone.AiApplyAmbushHypothesis(a.cards,a.templates,a.timers,k*2);
  for(let j=0;j<2;j++)check(clone.FindCard(a.cards[j]).Snapshot().timerValue===a.timers[k*2+j],'each timer world reaches the real cloned card');
 }
 check(a.hidden.every((c,i)=>JSON.stringify(c.Snapshot())===original[i]),'world construction preserves real hidden cards');
}
globalThis.report={checks,failures,cases,scope:'Public pair enumeration/copy probabilities; no strength claim',nativeGameplayVerified:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
if(report.failures.length)process.exitCode=1;

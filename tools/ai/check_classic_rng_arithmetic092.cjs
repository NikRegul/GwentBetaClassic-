'use strict';
// Diagnose arithmetic models against the preserved retail shuffle, no runtime launch.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const dir=path.join(root,'BetaGwent/drafts/day-iteration-20261023/classic132-rng-regression');
const audit=JSON.parse(fs.readFileSync(path.join(dir,'log-audit.json'),'utf8'));
const rules=path.join(root,'BetaGwent/build/release092-swarm-fix2-20261023/rules');
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const rosters=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
function mulFloat32(a,b){const n=Math.fround(Math.fround(a)*Math.fround(b));return n>=2147483648||n< -2147483648?-2147483648:n|0;}
function mulDouble(a,b){const n=a*b;return n>=2147483648||n< -2147483648?-2147483648:n|0;}
const models={wrap:Math.imul,float32:mulFloat32,doubleOverflow:mulDouble,
 seedAssignFloat32:(a,b)=>b===69069?mulFloat32(a,b):Math.imul(a,b),
 seedAssignDoubleOverflow:(a,b)=>b===69069?mulDouble(a,b):Math.imul(a,b),
 seedAssignSaturate:(a,b)=>b===69069?Math.max(-2147483648,Math.min(2147483647,a*b))|0:Math.imul(a,b),
 seedAssignZero:(a,b)=>b===69069?0:Math.imul(a,b),
 onlyTemperFloat32:(a,b)=>b!==69069?mulFloat32(a,b):Math.imul(a,b),
 saturate:(a,b)=>Math.max(-2147483648,Math.min(2147483647,a*b))|0};
const report=[];
for(const [name,multiply] of Object.entries(models)){
 for(const compoundFloat of [false,true]){
 const start=source.indexOf('class CBetaGwentRandomGenerator '),end=source.indexOf('\nclass ',start+10);
 let altered=source.slice(0,start)+source.slice(start,end).replaceAll('Math.imul(','multiply(')+source.slice(end);
 if(compoundFloat)altered=altered.replace('this.cursor+=1;','this.cursor=Math.fround(this.cursor+1)|0;');
 const shuffle=new Function('multiply','seed','ids',altered+String.raw`
  const r=new CBetaGwentRandomGenerator();r.Initialize(seed);const box={v:ids.slice()};r.Shuffle(box);return box.v;
 `).bind(null,multiply);
 const cases=[];
 for(const game of audit.games){
  const d=rosters.find(x=>x.presetId===Number(game.start.ownPreset));
  // User preset16 is a custom deck, not part of the46 generated rosters.
  if(!d)continue;
  const actual=shuffle(Number(game.start.seed),d.templateIds);
  cases.push({ordinal:game.ordinal,seed:Number(game.start.seed),matches:JSON.stringify(actual)===JSON.stringify(game.initialOwnTemplateOrder),actual});
 }
 report.push({model:name+(compoundFloat?'-floatCursor':''),matched:cases.filter(x=>x.matches).length,total:cases.length,cases});
 }
}
fs.writeFileSync(path.join(dir,'arithmetic-models.json'),JSON.stringify({schema:1,diagnosticOnly:true,
 note:'Matching a model is evidence for investigation, not direct execution proof of native arithmetic.',models:report},null,2)+'\n');
console.log(JSON.stringify(report.map(({model,matched,total})=>({model,matched,total}))));

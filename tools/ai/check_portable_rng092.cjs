'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..'),out=path.join(root,'BetaGwent/drafts/day-iteration-20261023/classic132-rng-regression');
// Reject every overflowing multiplication in the candidate's translated code.
let checkedMultiplies=0;
function boundedMultiply(a,b){const product=BigInt(a)*BigInt(b);assert(product>=-2147483648n&&product<=2147483647n,'Candidate depended on overflow');checkedMultiplies++;return Number(product);}
const source=fs.readFileSync(path.join(out,'portable-rng.js'),'utf8').replaceAll('Math.imul(','boundedMultiply(');
const exportsBox={exports:{}};new Function('module','boundedMultiply',source)(exportsBox,boundedMultiply);
const {CBetaGwentRandomGenerator:R,BetaGwentRngShiftLeft:left,BetaGwentRngSeedMultiply:mul,Host}=exportsBox.exports;
let checks=0;const eq=(a,b)=>{assert.deepEqual(a,b);checks++;};
const values=[0,1,-1,2147483647,-2147483648,1073741824,-1073741824,65535,65536,69069];
let independent=923102401;
for(let i=0;i<10000;i++){independent=(Math.imul(independent,1664525)+1013904223)|0;values.push(independent);}
for(const n of values){eq(mul(n),Number(BigInt.asIntN(32,BigInt(n)*69069n)));for(const bits of [0,1,7,15,30,31])eq(left(n,bits),Number(BigInt.asIntN(32,BigInt(n)<<BigInt(bits))));}
const fixtures=JSON.parse(fs.readFileSync(path.join(root,'docs/evidence/beta-rng-fixtures.json'),'utf8'));
for(const v of fixtures.vectors){const r=new R();r.Initialize(v.seed);eq(v.values.map(()=>r.NextBits()>>>0),v.values);}
const oldDir=path.join(root,'BetaGwent/build/release092-swarm-fix2-20261023/rules');
const original=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(oldDir,n),'utf8')).join('\n');
const old=new Function(original+';return CBetaGwentRandomGenerator;')();
const audit=JSON.parse(fs.readFileSync(path.join(out,'log-audit.json'),'utf8'));
const seeds=[...new Set([...fixtures.vectors.map(v=>v.seed),...audit.games.map(g=>Number(g.start.seed))])];
for(const seed of seeds){
 const r=new R(),reference=new old();r.Initialize(seed);reference.Initialize(seed);
 for(let i=0;i<1300;i++){reference.cursor|=0;eq(r.NextBits(),reference.NextBits());}
 eq(r.DrawCount(),1300);eq(r.words,reference.words);
}
const hands=[];
for(const game of audit.games){const r=new R();r.Initialize(Number(game.start.seed));const ids={v:Array.from({length:25},(_,i)=>i)};r.Shuffle(ids);hands.push(ids.v);}
eq(new Set(hands.map(x=>x.join(','))).size,12);
const repeat=new R(),same=new R();repeat.Initialize(923102401);same.Initialize(923102401);
const hand1={v:Array.from({length:25},(_,i)=>i)},hand2={v:hand1.v.slice()};repeat.Shuffle(hand1);same.Shuffle(hand2);eq(hand1.v,hand2.v);
// Model a bad platform contract. Only the self-test is injected; actual fallback
// generation, reinitialization and draws execute the translated production code.
class BadPlatform extends R {NextBits(){if(!this.implementationChecked)return 0;return super.NextBits();}}
let engineCalls=0,engineState=923102401;
Host.random=()=>{engineCalls++;engineState=(Math.imul(engineState,1664525)+1013904223)>>>0;return engineState/4294967296;};
const bad=new BadPlatform();bad.Initialize(123456789);eq(bad.UsesEngineTape(),true);eq(engineCalls,1024);eq(bad.DrawCount(),0);
const saved=JSON.stringify(bad),firstTape=Array.from({length:1100},()=>bad.NextBits());
eq(firstTape.slice(0,76),firstTape.slice(1024));eq(engineCalls,1024);
bad.Initialize(123456789);eq(Array.from({length:1100},()=>bad.NextBits()),firstTape);eq(engineCalls,1024);
const copied=new R();Object.assign(copied,JSON.parse(saved));eq(Array.from({length:1100},()=>copied.NextBits()),firstTape);eq(engineCalls,1024);
const fallbackOrders=[];
for(let i=0;i<12;i++){const b=new BadPlatform();b.Initialize(123456789);const ids={v:Array.from({length:25},(_,i)=>i)};b.Shuffle(ids);fallbackOrders.push(ids.v.join(','));}
eq(new Set(fallbackOrders).size,12);eq(engineCalls,13*1024);
const report={schema:1,checks,checkedMultiplies,originalFixtures:fixtures.vectors.length,seeds:seeds.length,
 drawsPerSeed:1300,retailSeedShuffles:12,distinctRetialSeedShuffles:new Set(hands.map(x=>x.join(','))).size,
 fallbackContractChecks:11,fallbackTapeLength:1024,fallbackCycleExplicit:true,
 nativeGameplayVerified:false,scope:'Overflow-independent arithmetic preserves original vectors in JS. Bad contract selects captured engine tape, with independent copied/reseeded draws and no new engine calls. Actual Classic verification remains; no installation.'};
fs.writeFileSync(path.join(out,'portable-rng-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

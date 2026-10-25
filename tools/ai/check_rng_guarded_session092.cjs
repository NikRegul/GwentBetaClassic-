'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');
const rules=path.resolve(process.argv[2]||path.join(root,'BetaGwent/build/release092-rng-guarded-20261024/rules'));
const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const run=new Function('broken',code+String.raw`
 let engineState=923102409,engineCalls=0;
 Host.matchStrength=[4,4];Host.strength=4;Host.seatIndex=1;
 Host.random=()=>{engineCalls++;engineState=(Math.imul(engineState,1664525)+1013904223)>>>0;return engineState/4294967296;};
 if(broken){const original=CBetaGwentRandomGenerator.prototype.SeedWords;
 CBetaGwentRandomGenerator.prototype.SeedWords=function(seed){original.call(this,seed);this.words.fill(0);};}
 const games=[];for(let i=0;i<12;i++){
  const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(91,56))throw Error('Initialization rejected');
  games.push(g);
 }
 const g=games[0],cloner=new CBetaGwentCloner(),copy=cloner.CloneSession(g,900000001);
 const pick=r=>({words:r.words.slice(),draws:r.draws,cursor:r.cursor,remaining:r.remaining,
  initialSeed:r.initialSeed,reseedValue:r.reseedValue,engineTapeMode:r.engineTapeMode,
  implementationChecked:r.implementationChecked,engineTape:r.engineTape.slice(),engineTapeCursor:r.engineTapeCursor});
 const before=pick(g.random),cloneBefore=pick(copy.random),callsBefore=engineCalls;
 const draws=Array.from({length:80},()=>copy.random.NextBits());
 const originalAfter=pick(g.random);
 copy.random.Initialize(923102410);const reinitialized=Array.from({length:80},()=>copy.random.NextBits());
 const independentTape=g.random.engineTape!==copy.random.engineTape;
 const orders=games.map(x=>x.live.filter(c=>c.Snapshot().ownerId===1&&c.Snapshot().locationMask!==64).map(c=>c.TemplateId()).join(','));
 const matches=[];
 for(const [left,right,seed]of [[91,56,923102421],[56,91,923102422]]){
  const result=__play(left,right,seed,4,4,200);matches.push(result);
 }
 return {broken,engineCallsBeforeMatches:callsBefore,engineCallsAfterCloneWork:engineCalls,
  originalBefore:before,originalAfter,cloneBefore,independentTape,distinctOrders:new Set(orders).size,
  usesTape:games.map(x=>x.random.UsesEngineTape()),draws,reinitialized,matches};
`);
const reports=[];
for(const broken of [false,true]){
 const r=run(broken);
 assert.deepEqual(r.originalBefore,r.cloneBefore);assert.deepEqual(r.originalBefore,r.originalAfter);
 assert(r.independentTape);assert.equal(r.distinctOrders,12);assert(r.usesTape.every(x=>x===broken));
 assert.equal(r.engineCallsBeforeMatches,broken?12*1025:12);
 // __play installs its own deterministic host RNG. The counter is intentionally
 // detached for matches; clone work before that must consume no engine calls.
 assert.equal(r.engineCallsBeforeMatches,r.engineCallsAfterCloneWork);
 for(const game of r.matches){assert(!game.error,JSON.stringify(game));assert([1,2,3].includes(game.winner));}
 reports.push({brokenContractInjected:broken,distinctOrders:r.distinctOrders,
  engineCallsForTwelveStarts:r.engineCallsBeforeMatches,cloneSourceUnchanged:true,cloneEngineCalls:0,
  copiedTapeIndependent:true,matches:r.matches});
}
const report={schema:1,scope:'Actual translated full sessions, production CloneSession and full existing-policy games; not a Beta AI comparison or native gameplay check.',
 fingerprint:JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8')).fingerprint,nativeGameplayVerified:false,cases:reports};
fs.writeFileSync(path.join(root,'BetaGwent/drafts/day-iteration-20261023/classic132-rng-regression/guarded-session-proof.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));

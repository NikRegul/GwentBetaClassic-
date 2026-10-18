'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve('BetaGwent/build/release082-rc1/rules-tests'),context=vm.createContext({console});
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const side of [1,2])for(const doomed of [false,true]){
 const g=fixture(side),c=add(g,132314,1,0,side,1);g.recordVisuals=true;g.visualFrames=[];
 if(doomed)c.AddTokens(512);
 g.QueuePower(c,-10,false);g.FlushEffects();g.FlushDeaths();
 const expected=doomed?512:32;check(c.Snapshot().locationMask===expected,'real death destination '+side+'/'+doomed);
 const f=g.visualFrames.filter(f=>f.kind===3).at(-1);check(!!f,'death is presented');
 const i=f.destinationIds.indexOf(c.Snapshot().instanceId);
 check(i>=0&&f.destinationZones[i]===expected&&f.destinationSides[i]===side,'snapshot preserves actual public destination');
 const cloner=new CBetaGwentCloner(),copy=new CBetaGwentDuelVisualFrame();cloner.flipSeats=true;cloner.CopyDuelVisualFrame(f,copy);
 check(copy.destinationSides[i]===3-side&&copy.destinationIds[i]===f.destinationIds[i]&&copy.destinationZones[i]===expected,'seat reversal preserves identity and destination');
 const enemyHand=g.live.find(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);
 check(!f.destinationIds.includes(enemyHand.Snapshot().instanceId),'destination metadata excludes hidden hand');
}
for(const side of [1,2])for(const doomed of [false,true]){
 const g=fixture(side),special=add(g,113101,256,0,side);g.recordVisuals=true;g.visualFrames=[];g.playStack=[special];
 if(doomed)special.AddTokens(512);
 g.CompletePlay(special);
 check(!g.IsFatal()&&special.Snapshot().locationMask===(doomed?512:32),'resolved special follows real rules');
 const frames=g.visualFrames.filter(f=>f.kind===19);check(frames.length===(doomed?0:1),'one discard cue only for retained special');
 if(!doomed){const f=frames[0];check(f.targetId===special.Snapshot().instanceId&&f.targetTemplateId===113101&&f.targetSide===side&&f.targetZone===32,'resolved special carries exact identity and side');}
}
globalThis.report={checks,actualWitcherScript:true,nativeGameplayVerified:false};
`,context,{timeout:120000});
fs.writeFileSync(path.join(snapshot,'discard-rules.json'),JSON.stringify(context.report,null,2));console.log(JSON.stringify(context.report));

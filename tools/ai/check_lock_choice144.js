// 0.6.8: lock-toggle abilities (Radovid V, Ciaran) are valued by the lock change, not by raw power.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture.replace("console.log('PASS',n);","")+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const enemies of [0,1,2]){
 const g=fixture();clearHand(g,2);clearHand(g,1);add(g,112101,8,0,1);
 const es=[];for(let i=0;i<enemies;i++)es.push(add(g,112101,1,i,1,6));
 const squire=add(g,123301,1,0,2);const plain=add(g,112101,1,1,2,4);add(g,200169,64,0,2);
 check(g.UseLeader(2),'Radovid used');let n=0;while(g.IsPending()&&n++<6)__pending(g);
 check((squire.Snapshot().tokenMask&4)===0,'Radovid never locks our own Redanian Squire engine ('+enemies+' enemies)');
 if(enemies===2)check(es.every(e=>(e.Snapshot().tokenMask&4)!==0),'both enemy units locked and damaged');
}
globalThis.report={checks};
`,context,{timeout:120000});
console.log('PASS: '+context.report.checks+' lock-choice checks');

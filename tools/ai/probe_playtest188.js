'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path');
const snapshot=path.resolve(process.argv[2]);
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInNewContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const g=fixture();g.aiSimDamp=0;
g.live.filter(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8).forEach(c=>c.Move(2,512,0));
g.match.playerOne.hasPassed=true;
[6,10,4,11,3].forEach((p,i)=>add(g,132314,1,i,1,p));
add(g,132314,1,0,2,5);add(g,132314,2,0,2,5);
[132313,132220,200067,132409,132303,200112,200112].forEach((t,i)=>add(g,t,8,i,2));
add(g,201587,64,0,2);
const actions=g.live.filter(c=>c.cardState.positionPlayerId===2&&[8,64].includes(c.cardState.locationMask)).map(c=>({id:c.cardState.locationMask===64?-1:c.cardState.instanceId,cards:c.cardState.locationMask===64?0:1,reserve:0,gain:g.AiExactTempo(c)}));
console.log('actions',actions,'plan',g.AiChaseActual(actions,25));
const first=g.AiSimClone();first.AiSimPlay(actions[1].id);
console.log('first',first.Score(2),first.Score(1),first.aiChaseSpent);
for(const a of actions){const h=first.AiSimClone();const r=h.AiSimPlay(a.id<0?h.Leader(2).Snapshot().instanceId:a.id);console.log('follow',a.id,r,h.Score(2),h.Score(1),h.aiChaseSpent);}
Host.log=s=>{if(/CHASE|event=SELECT|event=PASS/.test(s))console.log(s);};g.OpponentStep();
console.log('after',g.Score(2),g.Score(1),g.aiChaseSpent,g.match.Snapshot());g.OpponentStep();
`,{console},{timeout:120000});

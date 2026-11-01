'use strict';
const fs=require('fs'),assert=require('node:assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs'),obs=require('./retail_position094.cjs');
const rt=createRuntime(process.argv[2]),g=rt.newSession();assert(g.InitializeWithPresets(54,54));
const spy=g.live.find(c=>c.Snapshot().ownerId===1),id=spy.Snapshot().instanceId;
spy.Move(2,1,0);const logs=[];rt.host.log=s=>logs.push(s);g.AiLogPosition();rt.host.log=null;
let checks=0;function ok(value){assert(value);checks++;}
const fields=s=>Object.fromEntries([...s.matchAll(/(\w+)=([^\s]+)/g)].map(m=>[m[1],m[2]]));
const header=fields(logs.find(s=>s.startsWith('AI_POSITION ')));
ok(obs.compareHeader(g,header).length===0);
ok(obs.compareHeader(g,{...header,current:3-g.Snapshot().currentPlayerId}).some(e=>e.key==='current'));
ok(obs.compareHeader(g,{...header,passed:'1,1'}).some(e=>e.key==='passed'));
const tuples=logs.filter(s=>s.startsWith('AI_POSITION_CARDS ')).flatMap(s=>s.split(/\s+/).filter(t=>/^-?\d+(?::-?\d+){12}$/.test(t)).map(t=>t.split(':').map(Number)));
ok(tuples.length===g.live.length);
for(const tuple of tuples)ok(obs.compareCard(g,tuple).length===0);
const tuple=tuples.find(t=>t[0]===id);ok(tuple[2]===2&&tuple[3]===1);
const swapped=tuple.slice();[swapped[2],swapped[3]]=[swapped[3],swapped[2]];
ok(obs.compareCard(g,swapped).length===1);
for(const column of [4,5,6,7,8,9,10,11,12]){const bad=tuple.slice();bad[column]++;ok(obs.compareCard(g,bad).length===1);}
ok(obs.compareCard(g,[999999,...tuple.slice(1)]).length===1);
const shell=rt.newSession();assert(shell.InitializeWithPresets(54,54));shell.mulligan=false;shell.pendingCard=null;shell.pendingLeader=null;
shell.match.currentPlayerId=1;shell.match.turnActive=true;shell.match.roundActive=true;
const expected={...obs.header(shell),current:2,passed:'1,0'};
ok(obs.recoverShellPass(shell,expected)===null); // A real hand/leader still exists.
for(const c of shell.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,64].includes(s.locationMask))c.Move(1,512,0);}
const emptyExpected={...obs.header(shell),current:2,passed:'1,0'};
ok(obs.recoverShellPass(shell,{...emptyExpected,passed:'0,0'})===null);
ok(obs.recoverShellPass(shell,{...emptyExpected,current:1})===null);
ok(obs.recoverShellPass(shell,emptyExpected)?.side===1);
ok(shell.Snapshot().playerOne.hasPassed&&shell.Snapshot().currentPlayerId===2);
ok(obs.compareHeader(shell,emptyExpected).length===0);
const report={checks,failures:[],actualWitcherScriptLogger:true,spy:{id,side:2,owner:1},nativeTuples:tuples};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({checks,failures:[]}));

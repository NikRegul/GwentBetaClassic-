// Reported 25.10.2026: AI Kayran consumed a 7-power Vran Warrior instead of the
// player's Miruna, two turns before her charm of the AI's 11-power unit.
// Consume targets must count the enemy engine/charm they remove, as damage kills do.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;
function check(v,n){if(!v)throw Error(n);checks++;console.log('PASS',n);}
function add(g,t,zone,index=0,side=2,power){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);if(power!==undefined)c.power.SetCurrentPair(power,0);
 g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(56,56))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=2;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<6;i++){add(g,112101,8,i,1);add(g,112101,8,i);}return g;}
for(const [label,victimPower] of [['strong victim',11],['medium victim',8]]){
 const g=fixture();
 const miruna=add(g,132108,1,0,1);miruna.cardState.timerValue=2;
 const warrior=add(g,132308,2,0,1,7);
 add(g,112101,1,0,2,victimPower);
 const kayran=add(g,132107,8,6,2);
 check(g.Play(2,kayran.cardState.instanceId,2),'AI plays Kayran: '+label);
 for(let k=0;k<8&&g.IsPending();k++)check(__pending(g),'AI resolves request: '+label);
 g.FlushEffects();g.FlushDeaths();
 check((miruna.Snapshot().locationMask&7)===0,'Kayran consumes Miruna before her charm: '+label);
 check((warrior.Snapshot().locationMask&7)!==0,'Vran Warrior stays: '+label);
 check(!g.IsFatal()&&!g.IsPending(),'turn completes: '+label);
}
// Without a pending charm (timer spent / nothing to charm) the bigger body is still preferred.
{
 const g=fixture();
 const miruna=add(g,132108,1,0,1);miruna.cardState.timerValue=0;
 const warrior=add(g,132308,2,0,1,7);
 const kayran=add(g,132107,8,6,2);
 check(g.Play(2,kayran.cardState.instanceId,2),'AI plays Kayran without charm threat');
 for(let k=0;k<8&&g.IsPending();k++)check(__pending(g),'AI resolves request without threat');
 g.FlushEffects();g.FlushDeaths();
 check((warrior.Snapshot().locationMask&7)===0&&(miruna.Snapshot().locationMask&7)!==0,'without a threat the 7-power warrior is consumed');
}
globalThis.kayranReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'kayran197.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.kayranReport,null,2)+'\n');

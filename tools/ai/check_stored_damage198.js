// Lugos uses the BASE power of the discarded card, not his printed damage.
// The fresh 00:51 log contains his two-stage request. Exercise the adjacent
// regenerating-target failure found while auditing Cyclops' shared scorer.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const rules=path.resolve(process.argv[2]),negative=process.argv.includes('--negative-control');
const context=vm.createContext({console,negative});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;const records=[];
function check(v,n){checks++;if(!v)throw Error(n);}
function add(g,t,zone,index,side,power){const id={v:0};check(g.registry.Allocate(id),'allocate');const c=new CBetaGwentDuelCard();c.Setup(g,id.v,t,side,zone,index);if(power!==undefined)c.power.SetCurrentPair(power,0);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(lethal,alone){const g=new CBetaGwentDuelSession();check(g.InitializeWithPresets(50,50),'initialize');g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=2;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<4;i++)add(g,112101,8,i,1);for(let i=0;i<3;i++)add(g,112101,8,i,2);
 const sw=add(g,200040,1,0,1);sw.power.basePower=14;sw.power.SetCurrentPair(lethal?8:14,0);sw.cardState.timerValue=2;
 const weak=alone?null:add(g,152213,2,0,1,4);add(g,152311,16,0,2);const source=add(g,152106,8,3,2);
 check(g.Play(2,source.cardState.instanceId,2),'Lugos played');for(let i=0;i<8&&g.IsPending();i++)check(__pending(g),'Lugos request resolves');g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),'Lugos completes');
 return {sw:sw.Snapshot(),weak:weak?.Snapshot(),damage:source.monsterStored};}
let r=fixture(false,false);records.push(r);
if(negative){check(r.sw.power.currentPower===5&&(r.weak.locationMask&7)!==0,'old Lugos wastes nine damage on a regenerating swordsman');}
else{
 check(r.sw.power.currentPower===14,'Lugos preserves untouched regenerating swordsman');check((r.weak.locationMask&7)===0,'Lugos kills the vulnerable unit');
 r=fixture(true,false);records.push(r);check((r.sw.locationMask&7)===0,'Lugos still finishes a lethal swordsman');
 r=fixture(false,true);records.push(r);check(r.sw.power.currentPower===5,'Lugos still attacks the only legal target');
}
globalThis.storedDamageReport={checks,records,negativeControl:negative,actualWitcherScript:true,nativeGameplayVerified:false};
`,context,{filename:'stored-damage198.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.storedDamageReport,null,2)+'\n');
console.log(JSON.stringify(context.storedDamageReport));

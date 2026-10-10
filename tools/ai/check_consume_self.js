// Execute the real translated WitcherScript, including target requests and passive queues.
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
function fixture(side=2){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,54))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=side;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<4;i++){add(g,112101,8,i,1);add(g,112101,8,i);}return g;}
function alive(c){return (c.Snapshot().locationMask&7)!==0&&!c.Snapshot().isWaitingToDie;}
// Alone: no self target, no phantom power and no pending choice left behind.
for(const side of [1,2])for(const template of [201701,201606]){
 const g=fixture(side),c=add(g,template,8,4,side),power=c.Snapshot().power.currentPower;
 check(g.Play(side,c.cardState.instanceId,1),'play consumer '+template+'/'+side);
 check(alive(c)&&c.Snapshot().power.currentPower===power,'alone consumer survives unchanged '+template+'/'+side);
 check(!g.IsFatal()&&!g.IsPending(),'empty consume pool completes '+template+'/'+side);
}
// A second copy is legal: exclude identity, never the template.
for(const side of [1,2]){
 const g=fixture(side),victim=add(g,201701,1,0,side),c=add(g,201701,8,4,side);
 check(g.Play(side,c.cardState.instanceId,1),'play beside another Barbegazi '+side);
 if(side===1){
  check(g.pendingIds.includes(victim.cardState.instanceId)&&!g.pendingIds.includes(c.cardState.instanceId),'player target list excludes self');
  check(!g.SelectTarget(g.requestId,c.cardState.instanceId),'player cannot submit self');
  check(g.SelectTarget(g.requestId,victim.cardState.instanceId),'player can consume another copy');
 }
 check(alive(c)&&c.Snapshot().power.currentPower===12,'same-template meal grants correct power '+side);
 check(victim.Snapshot().locationMask===32&&!g.IsFatal()&&!g.IsPending(),'meal dies and turn completes '+side);
}
// A multi-target consumer must stop after exhausting other units, rather than eat itself.
{
 const g=fixture(),victim=add(g,112101,1,0,2,3),c=add(g,201606,8,4),power=c.Snapshot().power.currentPower;
 check(g.Play(2,c.cardState.instanceId,1),'play multi-target consumer');
 check(alive(c)&&c.Snapshot().power.currentPower===power+3,'only real meal contributes power');
 check(victim.Snapshot().locationMask===32&&!g.IsFatal()&&!g.IsPending(),'second empty choice ends safely');
}
// Reject illegal direct calls and bypass attempts at the authoritative action queue.
{
 const g=fixture(),c=add(g,201701,1),power=c.Snapshot().power.currentPower;
 check(g.QueueConsume(c,c)===false,'shared queue rejects self');
 for(const operation of [4,5]){
  const action=new CBetaGwentDuelEffectAction();action.runtime=g.effects;action.attacker=c;action.target=c;action.operation=operation;action.allowedLocations=7;
  check(!action.IsValid(),'execution rejects self for operation '+operation);
 }
 check(g.effects.Enqueue(c,4,0,false,c),'enqueue bypass attempt for managed validation');
 g.FlushEffects();g.FlushDeaths();
 check(alive(c)&&c.Snapshot().power.currentPower===power&&!g.IsFatal(),'bypassed self-consume is skipped without killing');
}
// Graveyard consumption still banishes its meal, without applying a second deathwish.
{
 const g=fixture(),c=add(g,201701,1),victim=add(g,112101,32,0,2,3);
 check(g.QueueConsume(c,victim),'legal graveyard meal accepted');g.FlushEffects();g.FlushDeaths();
 check(alive(c)&&victim.Snapshot().locationMask===512&&!g.IsFatal(),'legal graveyard consumption survives guard');
}
globalThis.consumeReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'consume-self.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.consumeReport,null,2)+'\n');

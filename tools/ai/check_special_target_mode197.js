// Manticore Venom, Elven Saber (and Venom played by Last Wish) share
// specialMode 16 with Caranthir, but they are ordinary target specials.
// They must not open Caranthir's row-move request, and their target is required.
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
function fixture(side){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,54))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=side;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<4;i++){add(g,112101,8,i,1);add(g,112101,8,i);}return g;}
for(const template of [113306,201643]){
 const g=fixture(1),victim=add(g,112101,2,0,2,20),ally=add(g,112101,1,0,1,8),card=add(g,template,8,4,1);
 check(g.Play(1,card.cardState.instanceId,1)&&g.IsPending(),'player special opens target request '+template);
 check(!g.IsCaranthirMoveRequest()&&!g.PlacementCard(),'no Caranthir row-move mode or placement card '+template);
 check(g.GetRequestSnapshot().limits.minimum===1,'target is required '+template);
 check(!g.FinishTarget(g.requestId)||g.IsPending(),'cannot skip the required target '+template);
 const before=victim.Snapshot().power.currentPower;
 check(g.SelectTarget(g.requestId,victim.cardState.instanceId)&&!g.IsPending()&&!g.IsFatal(),'target accepted '+template);
 g.FlushEffects();g.FlushDeaths();
 const after=victim.Snapshot();check(after.power.currentPower<before||(after.locationMask&7)===0,'target damaged '+template);
 check(ally.Snapshot().power.currentPower===8,'ally untouched '+template);
}
{
 const g=fixture(1);add(g,112101,1,0,2,10);const car=add(g,132104,8,4,1);
 check(g.Play(1,car.cardState.instanceId,2)&&g.IsPending(),'Caranthir still requests a target');
 check(g.IsCaranthirMoveRequest(),'Caranthir keeps its row-move mode');
}
globalThis.specialTargetReport={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'special-target197.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.specialTargetReport,null,2)+'\n');

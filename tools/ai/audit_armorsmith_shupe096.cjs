'use strict';
// Armorsmith (152317): up to MaxTargets=2 allies; each ChangeArmor(+Armor=3) and
// ChangePower(Restore, 500) = full heal to base+permanent, boosts untouched.
// Shupe: Knight (201737) branch 201740: RequestCardTargets -> ResetCards(Power).
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
let checks=0;const failures=[],notes=[];function check(v,n){checks++;if(!v)failures.push(n);}
function add(g,t,zone,index=0,side=2){const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();
 c.Setup(g,id.v,t,side,zone,index);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(side){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(50,50))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;
 g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;g.match.currentPlayerId=side;g.externalPolicyMask=3;
 g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<3;i++){add(g,112101,8,i,1);add(g,112101,8,i,2);}return g;}
function unit(g,side,row,index,current){const c=add(g,112405,row,index,side);c.ChangeBasePower(12-c.Snapshot().power.basePower,true);c.power.SetCurrentPair(current,0);return c;}
for(const side of [1,2]){
 const g=fixture(side),a=unit(g,side,1,0,9),b=unit(g,side,1,1,15),smith=add(g,152317,8,4,side);
 if(!g.Play(side,smith.Snapshot().instanceId,2))throw Error('play armorsmith');
 check(g.SelectTarget(g.requestId,a.Snapshot().instanceId),'first target '+side);
 if(g.IsPending())check(g.SelectTarget(g.requestId,b.Snapshot().instanceId),'second target '+side);
 if(g.IsPending())g.FinishTarget(g.requestId);
 g.FlushEffects();g.FlushDeaths();const sa=a.Snapshot(),sb=b.Snapshot();
 check(sa.power.currentPower===12&&sa.power.armor===3,'wounded ally: full heal + 3 armor '+side+' actual '+sa.power.currentPower+'/'+sa.power.armor);
 check(sb.power.currentPower===15&&sb.power.armor===3,'boosted ally: power kept + 3 armor '+side+' actual '+sb.power.currentPower+'/'+sb.power.armor);
 check(!g.IsFatal()&&!g.IsPending(),'armorsmith resolves '+side);
}
for(const side of [1,2]){
 let offered=false;
 for(const r of [.05,.2,.37,.55,.71,.9]){
  Host.random=()=>r;const g=fixture(side),t=unit(g,BetaGwentOpponentId(side),1,0,15),shupe=add(g,201737,8,4,side);
  if(!g.Play(side,shupe.Snapshot().instanceId,1))throw Error('play shupe');
  if(!g.pendingIds.includes(201740))continue;offered=true;
  check(g.SelectTemplateChoice(g.requestId,201740),'knight branch selected '+side);
  if(g.pendingIds.includes(t.Snapshot().instanceId))check(g.SelectTarget(g.requestId,t.Snapshot().instanceId),'reset target '+side);
  g.FlushEffects();g.FlushDeaths();
  check(t.Snapshot().power.currentPower===12,'Shupe knight branch: Reset(Power) on the target '+side+' actual '+t.Snapshot().power.currentPower);
  check(!g.IsFatal(),'shupe resolves '+side);break;
 }
 if(!offered)notes.push('branch 201740 not offered for side '+side+' with the sampled RNG');
}
globalThis.result={checks,failures,notes,actualWitcherScript:true,nativeGameplayVerified:false};
`,context,{timeout:150000});
const r=context.result;if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(r,null,2)+'\n');console.log(JSON.stringify(r));if(r.failures.length)process.exitCode=1;

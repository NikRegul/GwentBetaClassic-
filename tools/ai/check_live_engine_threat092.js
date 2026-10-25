// Spend control on a working engine, not an exhausted once-only ability.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function blank(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;return g;}
{
 const g=blank(),spent=add(g,132201,2,0,1,15);spent.cardState.timerValue=0;
 const left=add(g,112405,1,0,1,5),squire=add(g,123301,1,1,1,8),right=add(g,112405,1,2,1,5);squire.power.SetCurrentPair(8,2);
 const shackles=add(g,113319,8,0,2);add(g,112405,8,1,2,6);add(g,112405,8,2,2,6);
 const reply=add(g,112405,8,0,1,6);add(g,112405,8,1,1,6);g.archetypeAI.Refresh();
 const before=left.Snapshot().power.currentPower+right.Snapshot().power.currentPower;
 check(g.Play(2,shackles.Snapshot().instanceId,1)&&!g.IsPending()&&!g.IsFatal(),'actual Shackles resolves automatic target');
 console.log('CONTROL_TARGET',JSON.stringify({spentLocked:Boolean(spent.Snapshot().tokenMask&4),activeLocked:Boolean(squire.Snapshot().tokenMask&4)}));
 check((squire.Snapshot().tokenMask&4)!==0&&(spent.Snapshot().tokenMask&4)===0,'actual control disables working Squire rather than spent Behemoth');
 check(g.Play(1,reply.Snapshot().instanceId,4),'actual enemy play advances its end-turn engine');
 check(left.Snapshot().power.currentPower+right.Snapshot().power.currentPower===before,'real subsequent end-turn loses both adjacent boosts');
}
for(const id of [132201,201624]){
 const g=blank(),c=add(g,id,2,0,1);for(let i=0;i<3;i++){add(g,112405,8,i,1,6);add(g,112405,8,i,2,6);}
 c.cardState.timerValue=0;g.archetypeAI.Refresh();check(g.AiEngineValue(c.Snapshot(),2)===0,'no phantom future after exhausted charges '+id);
 c.cardState.timerValue=1;check(g.AiEngineValue(c.Snapshot(),2)>0,'charged instance retains future threat '+id);
}
{
 const g=blank(),ship=add(g,152309,2,0,1,6);const reply=add(g,112405,8,0,1,6);
 add(g,112405,8,0,2,6);add(g,112405,8,1,2,6);add(g,112405,8,1,1,6);g.archetypeAI.Refresh();
 check(g.AiEngineValue(ship.Snapshot(),2)===0,'isolated Dimun has no current engine payoff');
 g.match.currentPlayerId=1;check(g.Play(1,reply.Snapshot().instanceId,4),'actual enemy turn resolves without a right neighbour');
 check(ship.Snapshot().power.currentPower===6,'real isolated ship does not strengthen itself');
 add(g,112405,2,1,1,6);check(g.AiEngineValue(ship.Snapshot(),2)>0,'adding a real right neighbour reactivates threat');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));

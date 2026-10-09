// Targeted rule/placement regressions, run against a frozen source snapshot.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const context=vm.createContext({console});
const code=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
vm.runInContext(code+`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
function fixture(){
 const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,88))throw Error('fixture initialization');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=2;
 g.match.playerOne.hasPassed=true;g.match.playerOne.crowns=1;g.match.playerTwo.hasPassed=false;
 g.recordVisuals=false;return g;
}
{
 const g=fixture();const hidden=add(g,122106,1,8,0,40);g.aiSimulating=true;hidden.HideUnknownFromAi();
 check(hidden.Snapshot().power.currentPower===6&&hidden.TemplateId()===112101,'hidden opposing hand uses anonymous power and identity');
}
function add(g,template,side,zone,index,power){
 const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();c.Setup(g,id.v,template,side,zone,index);
 if(power!==undefined){c.cardState.power.currentPower=power;c.power.currentPower=power;}
 g.registry.Put(id.v,c);g.live.push(c);return c;
}
function check(value,message){if(!value)throw Error(message);console.log('PASS',message);}
{
 const g=fixture();add(g,123301,2,2,0);add(g,122104,2,2,1);
 // An arbitrary plain unit, a spy tutor, Shani and Reaver Scout all use the
 // same insertion algorithm; these IDs are fixtures, not special-case policy.
 for(const template of [112101,122106,122307]){
  const d=BetaGwentDuelDefinition(template),r={v:0},i={v:0};
  check(g.AiSupportSlot(2,d,r,i)&&r.v===2&&i.v===0,'support slot '+template+' next to armoured knight');
 }
}
{
 const g=fixture();g.match.playerOne.hasPassed=false;g.match.playerOne.crowns=0;g.match.roundNumber=1;
 add(g,112101,1,1,0,20);add(g,112101,2,4,0,1);const medic=add(g,162304,2,8,0);
 const acted=g.OpponentStep();
 if(!g.match.playerTwo.hasPassed)console.log('medic fixture diagnostics',acted,g.GetMessage(),g.match.Snapshot(),medic.cardState);
 check(acted&&g.match.playerTwo.hasPassed&&medic.cardState.locationMask===8,'preserve last medic when optional round cannot be caught');
}
{
 const g=fixture();g.weather.hazards[4]=1;const d=BetaGwentDuelDefinition(201600);
 check(g.BestCardRow(2,d)!==2,'plain created unit avoids frost');
}
{
 const g=fixture();const vran=add(g,132308,2,1,0);add(g,132305,2,2,0);
 const anchor=g.BestVranAnchor(2);check(anchor!==vran.cardState.instanceId,'Vran preserves another Vran');
}
{
 const g=fixture();add(g,112101,1,1,0,7);add(g,112101,2,4,0,1);const leader=add(g,200162,2,64,0);
 const actions=[Object.assign(new SBetaGwentAIChaseAction(),{id:-1,gain:7,cards:1,reserve:0})];
 const plan=g.AiChaseActual(actions,7);check(plan.reachable&&plan.firstId===-1,'winning leader is a reachable chase');
}
`,context,{filename:'scenarios111.bundle.js',timeout:120000});

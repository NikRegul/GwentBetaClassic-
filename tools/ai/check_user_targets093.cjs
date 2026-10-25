'use strict';
const fs=require('fs'),path=require('path');
const {createRuntime}=require('./beta_js092/session.cjs');
const {rebuild,fixtureRoot}=require('./reconstruct_user_positions093.cjs');
const runtime=createRuntime(path.resolve(process.argv[2])),records=[],failures=[];let checks=0;
function check(ok,message){checks++;if(!ok){failures.push(message);throw Error(message);}}
const load=name=>JSON.parse(fs.readFileSync(path.join(fixtureRoot,name+'.json'),'utf8'));
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 runtime.host.strength=strength;runtime.host.matchStrength=[strength,strength];
 const p=load('cantarella-ambassador');p.damp=damp;const g=rebuild(runtime,p);
 check(g.Play(2,23,1)&&!g.IsFatal()&&!g.IsPending(),'real Ambassador choice completes');
 check(g.FindCard(16).Snapshot().power.currentPower===11,'Ambassador preserves vulnerable Cantarella at '+strength+'/'+damp);
 check(g.Score(2)===64,'all twelve immediate boost points still reach our board');
 check(g.Play(1,20,2),'the logged Menno reply is legal');
 if(g.IsPending())check(g.SelectTarget(g.requestId,16),'Menno may destroy the same logged spy');
 check(g.FindCard(16).Snapshot().locationMask===32,'authoritative Menno ability destroys the spy');
 check(g.Score(2)>=53,'the twelve extra points survive the actual Menno reply');
 records.push({kind:'logged-ambassador',strength,damp,afterMenno:g.Score(2)});
}
runtime.host.strength=4;runtime.host.matchStrength=[4,4];
for(const damp of [0,40,70]){
 const p=load('greatsword-damage');p.damp=damp;const g=rebuild(runtime,p),before=g.FindCard(5).Snapshot().power.currentPower;
 check(g.Play(2,35,1)&&!g.IsFatal()&&!g.IsPending(),'logged damage choice resolves');
 check(g.FindCard(5).Snapshot().power.currentPower===before,'damage goes to another useful target, not the regenerating sword');
 records.push({kind:'logged-damage',damp,swordPower:g.FindCard(5).Snapshot().power.currentPower});
}
// A due heal is already executed by an exact target simulation. Its future-only
// correction must not subtract the same restoration for a second time.
{
 const g=rebuild(runtime,load('greatsword-damage')),sword=g.FindCard(5),source=g.FindCard(35);
 sword.cardState.timerValue=1;const t=sword.Snapshot();
 check(g.AiRegenerationLoss(t,2,7)===7,'seven damage to an already wounded due sword will be restored');
 check(g.AiChoiceFutureValue(source,sword)===0,'exact next-turn restoration is not debited twice');
 check(g.AiDamageChoice(t,2,7)<g.AiDamageChoice(t,2,7,true),'heuristic damage values future restoration');
 const before=sword.Snapshot().power.currentPower;g.MonsterPower(source,sword,-7);g.FlushDeaths();g.BeforeTurnWithEvents(1);g.FlushDeaths();
 check(sword.Snapshot().power.currentPower>before,'real next-turn reaction heals and strengthens after nonlethal damage');
}
{
 const g=rebuild(runtime,load('greatsword-damage')),sword=g.FindCard(5);
 let t=sword.Snapshot();check(g.AiRegenerationLoss(t,2,t.power.currentPower)===0,'lethal damage prevents regeneration');
 sword.AddTokens(4);t=sword.Snapshot();check(g.AiRegenerationLoss(t,2,7)===0,'lock suppresses future restoration');
 sword.cardState.tokenMask&=~4;sword.power.currentArmor=10;t=sword.Snapshot();check(g.AiRegenerationLoss(t,2,7)===0,'armour-only damage does not enable a heal');
 sword.power.currentArmor=0;sword.power.currentPower=sword.power.basePower+10;t=sword.Snapshot();
 check(g.AiRegenerationLoss(t,2,7)===0,'removing only boosts is lasting useful damage');
 g.match.playerOne.hasPassed=true;sword.power.currentPower=11;t=sword.Snapshot();check(g.AiRegenerationLoss(t,2,7)===0,'passed opponent cannot take another restoration turn');
}
// The public list and public spent cards determine counters. Private identities
// cannot alter which ally receives the Ambassador boost.
{
 const selected=[];
 for(const changed of [false,true]){
  const g=rebuild(runtime,load('cantarella-ambassador'));
  if(changed)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&[8,16].includes(s.locationMask)&&(s.tokenMask&64)===0)c.cardState.runtimeTemplate.templateId=112405;}
  const logs=[];runtime.host.log=s=>logs.push(s);g.Play(2,23,1);runtime.host.log=null;
  selected.push(logs.find(s=>s.includes('event=TARGET_SELECT source=162315')));
 }
 check(selected[0]===selected[1],'boost targeting ignores hidden opposing hand/deck identities');
 const g=rebuild(runtime,load('cantarella-ambassador'));g.match.playerOne.hasPassed=true;
 check(g.AiBoostExposure(g.FindCard(16).Snapshot(),2,12)===0,'spy boost is fully usable after the opponent passed');
}
const report={fingerprint:runtime.fingerprint,checks,failures,records,actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

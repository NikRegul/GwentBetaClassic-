// Weather choices execute the release WitcherScript, including created cards.
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
function fixture(){const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,54))throw Error('initialize');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 for(let i=0;i<4;i++){add(g,112101,8,i,1);add(g,112101,8,i);}return g;}
function weatherBoard(g){for(const row of [1,2,4]){add(g,112101,row,0,2,5);g.weather.ApplyHazard(2,row,1);}}
function deckCount(g,template){return g.live.filter(c=>c.TemplateId()===template&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===16).length;}
for(const profile of [false,true]){
 const g=fixture();weatherBoard(g);g.weatherProfile=profile;
 const d=BetaGwentDuelDefinition(122207),clear=BetaGwentDuelViewDefinition(113401);
 check(g.AiCreatedOptionValue(clear,2,false)>g.AiCreatedOptionValue(clear,2,true),'clear future value separated from current points '+profile);
 check(g.AiManagedDeployValue(d,2,false)>g.AiManagedDeployValue(d,2,true),'Dethmold values prevented weather damage '+profile);
 const c=add(g,122207,8,4);g.AiSimPlay(c.cardState.instanceId);
 check([1,2,4].every(r=>g.WeatherToken(2,r)===0),'Dethmold actually creates Clear Skies for all three rows '+profile);
 check(!g.IsFatal() && !g.pendingCard,'created weather answer completes the turn '+profile);
}
{
 const g=fixture();weatherBoard(g);g.match.playerOne.hasPassed=true;
 const clear=BetaGwentDuelViewDefinition(113401);
 check(g.AiClearWeatherTicks(2)===0,'no future weather points after opposing pass');
 check(g.AiCreatedOptionValue(clear,2,false)===g.AiCreatedOptionValue(clear,2,true),'passed opponent gets only actual damaged-unit boost');
 const c=add(g,113303,8,4),before=g.Score(2);g.AiSimPlay(c.cardState.instanceId);
 check(g.Score(2)-before===6,'First Light catch-up is the real six-point boost');
}
{
 const g=fixture();g.weather.ApplyHazard(2,1,1);g.weather.ApplyHazard(2,2,128);
 check(g.weather.ClearValue(2,2,false)===0,'empty weather rows have no invented rescue points');
 add(g,112101,2,0,2,20);check(g.weather.ClearValue(2,2,false)===0,'friendly boon is not removed or valued as damage');
 const c=add(g,113401,8,4);g.AiSimPlay(c.cardState.instanceId);
 check(g.WeatherToken(2,2)===128,'Clear Skies retains boons');
}
{
 const g=fixture();const c=add(g,112101,1,0,2,20);c.power.AddArmor(99);g.weather.ApplyHazard(2,1,1);
 check(g.weather.ClearValue(2,0,false)===0,'armour absorbing the forecast prevents false rescue points');
 c.power.SetCurrentPair(20,0);c.AddTokens(8);
 check(g.weather.ClearValue(2,0,false)===0,'hidden ambush is not a forecast weather target');
}
{
 const g=fixture();weatherBoard(g);const clear=add(g,113401,16),tutor=add(g,200166,8,4);
 check(g.AiAbilityChoiceValue(tutor,clear,2)>0,'pile choice values a weather-clearing action');
}
for(const template of [122214,132307,162309,200147,142302])for(const row of [1,2,4]){
 const g=fixture();add(g,112101,row,0,2,5);g.weather.ApplyHazard(2,row,1);
 const c=add(g,template,8,4),d=c.Definition();
 check(g.AiClearsOwnRow(d),'own-row cleaner is recognized '+template);
 check(g.BestCardRow(2,d)===row,'cleaner chooses occupied weather row '+template+'/'+row);
 check(g.AiPlacementAnchor(d)===0,'archetype anchor cannot override cleansing '+template+'/'+row);
 g.AiSimPlay(c.cardState.instanceId);
 check(g.WeatherToken(2,row)===0,'real deployment clears the selected row '+template+'/'+row);
 check(!g.IsFatal(),'cleansing deployment resolves '+template+'/'+row);
}

for(const locked of [false,true]){
 const g=fixture(),behemoth=add(g,132201,2,0),fodder=add(g,112101,2,1),vran=add(g,132308,8,4);
 behemoth.cardState.timerValue=3;if(locked)behemoth.AddTokens(4);
 check(g.AiConsumeSpawnValue(2,0)===(locked?0:3),'consume counts only unlocked charged Behemoths '+locked);
 if(!locked){
  check(g.BestVranAnchor(2)===fodder.cardState.instanceId,'ordinary fodder is a useful consume with Behemoth');
  const before=g.live.filter(c=>c.TemplateId()===200174&&(c.Snapshot().locationMask&7)!==0).length;
  g.AiSimPlay(vran.cardState.instanceId);
  check(fodder.Snapshot().locationMask===32,'Vran actually consumes the selected right-hand neighbour');
  check(behemoth.Snapshot().locationMask===2 && behemoth.Snapshot().timerValue===2,'Behemoth preserved and charge used');
  check(g.live.filter(c=>c.TemplateId()===200174&&(c.Snapshot().locationMask&7)!==0).length===before+1,'real consume creates one young Arachas');
  check(!g.IsFatal()&&!g.pendingCard,'consume and spawn complete without blocked turn');
 }
}
{
 const g=fixture(),first=add(g,132308,2,0),behemoth=add(g,132201,2,1),fodder=add(g,112101,2,2),second=add(g,132308,8,4);
 behemoth.cardState.timerValue=2;
 check(g.BestVranAnchor(2)===fodder.cardState.instanceId,'second Vran preserves both consume engines and Behemoth');
 g.AiSimPlay(second.cardState.instanceId);
 check(first.Snapshot().locationMask===2 && behemoth.Snapshot().locationMask===2,'engines survive insertion in the middle');
 check(second.Snapshot().locationIndex===2,'second Vran inserted before its food instead of empty row');
}
for(const enemyPresent of [false,true]){
 const g=fixture(),ally=add(g,112101,2,0,2,20),enemy=enemyPresent?add(g,112101,1,0,1,20):null,viper=add(g,200124,8,4);
 g.nilfInitialTwo=[200022,200022,200022];
 // Choose a real alchemy template from the catalog rather than prescribing its category.
 const alchemy=[113303,113302,113301,200022,200023,200026,200030,200052,200079].find(t=>BetaGwentNorthernCategory(t,11));
 check(!!alchemy,'fixture contains a real alchemy card');g.nilfInitialTwo=[alchemy,alchemy,alchemy];
 check(g.NilfAlchemy(2)===3,'Viper uses the starting deck alchemy count');
 if(!enemyPresent)check(g.AiManagedDeployValue(viper.Definition(),2,true)<0,'Viper forecast includes unavoidable friendly damage');
 g.AiSimPlay(viper.cardState.instanceId);
 check(!g.IsFatal()&&!g.pendingCard,'Viper resolves with '+(enemyPresent?'enemy':'only friendly')+' targets');
 if(enemyPresent){check(enemy.Snapshot().power.currentPower===17,'Viper prefers enemy damage when available');check(ally.Snapshot().power.currentPower===20,'friendly unit left intact when enemy is better');}
 else check(ally.Snapshot().power.currentPower<20 || viper.Snapshot().power.currentPower<viper.Definition().header.power,'empty enemy field still takes a mandatory legal damage target');
}

{
 const g=fixture();g.match.roundNumber=2;
 g.live.filter(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8).forEach(c=>c.Move(1,512,0));
 add(g,112101,2,0,2,20);add(g,112101,1,0,1,5);
 const held=add(g,112101,8,4),hand=g.CountLocation(2,8);
 check(!g.LeaderAvailable(1),'exhausted-opponent fixture has no unused leader');
 check(g.AiWinsByPassingExhaustedOpponent(),'public round effects prove pass wins second round');
 check(g.OpponentStep(),'AI takes an exhausted-opponent action');
 check(g.CountLocation(2,8)===hand && held.Snapshot().locationMask===8,'AI passes without spending a card in the already-won round');
 check(g.match.playerTwo.hasPassed,'exhausted-opponent pass is applied');
}
for(const profile of [false,true]){
 const g=fixture();g.weatherProfile=profile;
 const seed=add(g,132305,2,0,2,3),vran=add(g,132308,1,0,2,18),warrior=add(g,132211,8,4);
 check(g.AiDeckCopyChoiceValue(seed,2)>g.AiDeckCopyChoiceValue(vran,2),'deathwish copy setup outranks a buffed Vran '+profile);
 g.AiSimPlay(warrior.cardState.instanceId);
 check(deckCount(g,132305)===2,'Warrior actually adds two Nekkers rather than Vran or itself '+profile);
 check(deckCount(g,132308)===0 && deckCount(g,132211)===0,'wrong deck copies are absent '+profile);
 check(!g.IsFatal()&&!g.pendingCard,'Warrior completes its copy choice '+profile);
 const row=seed.Snapshot().locationMask,index=seed.Snapshot().locationIndex;
 g.QueueConsume(vran,seed);g.FlushEffects();g.FlushDeaths();
 check(deckCount(g,132305)===1,'first consumed Nekker pulls one added copy '+profile);
 let replacement=g.live.find(c=>c.TemplateId()===132305&&c.Snapshot().locationMask===row);
 check(!!replacement&&replacement.Snapshot().locationIndex===index,'deathwish summons into the vacated row and slot '+profile);
 g.QueueConsume(vran,replacement);g.FlushEffects();g.FlushDeaths();
 check(deckCount(g,132305)===0,'second deathwish pulls the remaining added copy '+profile);
 check(g.live.some(c=>c.TemplateId()===132305&&c.Snapshot().locationMask===row),'second added copy really reaches the board '+profile);
 check(!g.IsFatal(),'two added copies resolve without a blocked graph '+profile);
}
globalThis.weatherReport={stage:121,checks,actualWitcherScript:true};
`,context,{filename:'scenarios121.bundle.js',timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.weatherReport,null,2)+'\n');

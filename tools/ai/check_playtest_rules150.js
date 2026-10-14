'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
// Chosen deploy pools exclude the acting instance, including same-template copies.
for(const template of [142317,200299,112214,152304,152203,152317,200147]){
 const g=fixture(1),other=add(g,template,1,0,1),source=add(g,template,8,4,1);
 check(g.Play(1,source.cardState.instanceId,1),'deploy '+template);
 check(!g.pendingIds.includes(source.cardState.instanceId),'no self target '+template);
 check(g.pendingIds.includes(other.cardState.instanceId),'another copy remains legal '+template);
 check(!g.SelectTarget(g.requestId,source.cardState.instanceId),'reject forged self selection '+template);
}
// Lock exposes an ambush, then Morvudd halves it. Its reveal ability is not run.
for(const template of [142204,142208,201779]){
 const g=fixture(1),trap=add(g,template,1,0,2),morvudd=add(g,132205,8,4,1);
 const initial=trap.Snapshot().power.currentPower;
 morvudd.power.SetCurrentPair(12,0);
 check(g.Play(1,morvudd.cardState.instanceId,1),'play Morvudd against '+template);
 const before=morvudd.Snapshot().power.currentPower;
 if(alive(morvudd)&&g.IsPending()){
  check(g.pendingIds.includes(trap.cardState.instanceId),'concealed ambush can be locked '+template);
  check(g.SelectTarget(g.requestId,trap.cardState.instanceId),'lock chosen ambush '+template);
  check((trap.Snapshot().tokenMask&12)===4,'face up and locked '+template);
  check(trap.Snapshot().power.currentPower===Math.floor(initial/2),'Morvudd halves revealed target '+template);
  check(morvudd.Snapshot().power.currentPower===before,'no reveal attack during lock '+template);
 }
 if(template===142208)check(before===5,'Morenn attacks before the deploy choice');
 check(!g.IsFatal(),'ambush resolves safely '+template);
}
// Destroy retains normal death rules but emits no damage-to-zero presentation.
for(const template of [113309,112102,112107,113308]){
 const g=fixture(),victim=add(g,112101,1,0,1,12),source=add(g,template,1,0,2);
 g.recordVisuals=true;g.visualFrames=[];g.SetVisualSource(source.cardState.instanceId,template,2,1);
 g.QueueDestroy(victim);g.FlushDeaths();
 check(!alive(victim),'destroy kills '+template);
 check(!g.visualFrames.some(f=>f.kind===2&&f.targetId===victim.cardState.instanceId),'no damage frame for destroy '+template);
 check(g.visualFrames.some(f=>f.kind===3&&f.templateId===template),'death preserves cause '+template);
}
// Every graveyard victim survives native recording as an individual consume event.
{
 const g=fixture(),source=add(g,132202,8,4);for(let i=0;i<8;i++)add(g,142317,32,i,2);
 g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(2,source.cardState.instanceId,1),'Mourntart plays');
 const meals=g.visualFrames.filter(f=>f.kind===11);
 if(meals.length!==8)console.log('MEALS',meals.length,JSON.stringify(g.visualFrames.map(f=>[f.kind,f.sourceId,f.templateId,f.targetId,f.attackCount])));
 check(meals.length===8,'all eight consume identities reach the UI');
 check(new Set(meals.map(f=>f.targetId)).size===8,'consume victims are distinct');
 check(meals.every(f=>f.templateId===132202),'consume source remains Mourntart');
 check(meals.every(f=>f.targetZone===32&&f.targetPower>0),'consume visuals preserve the original pile and portrait power');
}
// Lock-toggle retains unrelated tokens on an ordinary unit.
{
 const g=fixture(),c=add(g,142317,1);c.AddTokens(129);c.ToggleLock();
 check((c.Snapshot().tokenMask&133)===133,'lock does not clear Resilience or Spying');
 c.ToggleLock();check((c.Snapshot().tokenMask&133)===129,'unlock restores only the lock bit');
}
// Crow's damage and death frames carry the actual spell identity for delayed deaths.
{
 const g=fixture(1),spell=add(g,200224,8,4,1);
 for(const row of [1,2,4])add(g,142317,row,0,2,1);
 g.recordVisuals=true;g.visualFrames=[];check(g.Play(1,spell.cardState.instanceId,1),'Crow plays');
 if(g.IsPending())check(g.SelectTarget(g.requestId,g.pendingIds[0]),'Crow chooses target');
 const damage=g.visualFrames.filter(f=>f.kind===2&&f.templateId===200224),deaths=g.visualFrames.filter(f=>f.kind===3&&f.templateId===200224);
 check(damage.length>0&&deaths.length>0,'lethal Crow events retain the spell cause');
}
// Woodland's Fog follows occupied enemy rows for both ordinary and weather decks.
for(const profile of [false,true])for(const row of [2,4]){
 const g=fixture();g.weatherProfile=profile;add(g,112101,row,0,1,12);
 check(g.BestCardRow(2,BetaGwentDuelDefinition(132103))===row,'Woodland chooses occupied Fog row '+row+'/'+profile);
}
// Exact live-log case: 22-power Vran, 20 enemy points, final useless Decoy.
for(const passed of [false,true]){
 const g=fixture();g.live.filter(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8).forEach(c=>c.Move(2,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=passed;
 const vran=add(g,132308,1,0,2,22),enemy=add(g,142317,2,0,1,20),decoy=add(g,113201,8,0,2);
 check(g.AiUselessDecoy(decoy),'Decoy rejects the only negative-value target '+passed);
 check(g.OpponentStep(),'AI completes the turn '+passed);
 check(g.match.playerTwo.hasPassed,'AI passes instead of wasting Decoy '+passed);
 check(decoy.Snapshot().locationMask===8&&vran.Snapshot().power.currentPower===22,'Decoy and boosted Vran are preserved '+passed);
}
{
 const g=fixture(),vran=add(g,132308,1,0,2,6),decoy=add(g,113201,8,4,2);
 check(!g.AiUselessDecoy(decoy),'profitable Decoy remains available');
 check(g.Play(2,decoy.cardState.instanceId,1),'profitable Decoy plays normally');
 check(vran.Snapshot().power.currentPower===9,'positive Decoy replays and boosts its target');
}
// Decoy cannot be spent without a legal target or finish an active target request empty.
for(const side of [1,2]){
 const g=fixture(side),decoy=add(g,113201,8,4,side);
 check(!g.HasRequiredPlayTarget(decoy),'empty Decoy has no legal play '+side);
 check(!g.Play(side,decoy.cardState.instanceId,1),'authority rejects empty Decoy '+side);
 check(decoy.Snapshot().locationMask===8&&!g.match.playerOne.hasMadeInitialMoveForCurrentTurn&&!g.match.playerTwo.hasMadeInitialMoveForCurrentTurn,'rejected Decoy consumes no card or turn '+side);
}
{
 const g=fixture(1),target=add(g,142317,1,0,1),decoy=add(g,113201,8,4,1);
 check(g.Play(1,decoy.cardState.instanceId,1),'Decoy opens a real target request');
 check(g.GetRequestSnapshot().limits.minimum===1,'Decoy target is mandatory');
 check(!g.FinishTarget(g.requestId),'cannot finish Decoy without a target');
 check(g.SelectTarget(g.requestId,target.cardState.instanceId),'mandatory Decoy can resolve on a legal target');
}
// Geralt: Professional uses faction, never category, and has both graph branches.
for(const spec of [{id:132314,power:30,armor:10,kill:true},{id:142317,power:7,armor:0,kill:false},{id:142317,power:7,armor:5,kill:false}]){
 const g=fixture(1),target=add(g,spec.id,2,0,2,spec.power),geralt=add(g,201772,8,4,1);
 target.power.SetCurrentPair(spec.power,spec.armor);g.recordVisuals=true;g.visualFrames=[];
 check(g.Play(1,geralt.cardState.instanceId,1),'Professional plays '+spec.id+'/'+spec.armor);
 check(g.SelectTarget(g.requestId,target.cardState.instanceId),'Professional accepts enemy target '+spec.id+'/'+spec.armor);
 if(spec.kill){
  check(!alive(target),'Professional destroys Monster regardless of strength and armour');
  check(!g.visualFrames.some(f=>f.kind===2&&f.targetId===target.cardState.instanceId),'Monster destruction has no preliminary damage');
 }else{
  check(alive(target)&&target.Snapshot().power.currentPower===spec.power-Math.max(0,4-spec.armor),'non-Monster takes exactly four damage through armour');
  check(target.Snapshot().power.armor===Math.max(0,spec.armor-4),'Professional uses armour normally on non-Monster');
 }
 check(!g.IsFatal()&&!g.IsPending(),'Professional finishes normally');
}
{
 const g=fixture(1),target=add(g,132314,2,0,2),creator=add(g,200058,8,4,1);
 check(g.Play(1,creator.cardState.instanceId,1),'Triss creates a card');
 g.monsters.neutral.Select(creator,201772);
 check(!!g.pendingRally&&g.pendingRally.TemplateId()===201772,'created Professional awaits placement');
 g.PlaceRally(1,1,-3);
 check(g.SelectTarget(g.requestId,target.cardState.instanceId),'created Professional targets Drowner');
 check(!alive(target)&&!g.IsFatal()&&!g.IsPending(),'created Professional destroys Drowner and returns to its creator');
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{timeout:120000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log('PASS: '+context.report.checks+' playtest checks');

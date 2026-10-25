// Mixed board/revealed-hand abilities need their own effect value, not tutor card value.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const dir=path.resolve(process.argv[2]),ctx=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
for(const strength of [2,3,4]){
 Host.strength=strength;
 {
  const g=fixture(),source=add(g,162209,1,0,2),armored=add(g,112101,1,0,1,50),engine=add(g,162308,2,0,1,7);
  armored.power.SetArmor(9);const gift=add(g,162210,8,4,1);gift.cardState.tokenMask|=64;gift.cardState.timerValue=0;
  check(g.AiAbilityChoiceValue(source,engine,2)>g.AiAbilityChoiceValue(source,armored,2),'Serrit prefers a killed engine to damage absorbed by armour '+strength);
  check(g.AiAbilityChoiceValue(source,gift,2)<0,'Serrit does not weaken the points an enemy spy would give us');
  g.playStack.PushBack(source);check(g.match.ClaimInitialMove(2)===0,'actual Serrit ability has a live action');
  g.MonsterRequest(source,[armored.cardState.instanceId,engine.cardState.instanceId,gift.cardState.instanceId],2,1,1);
  check(engine.Snapshot().locationMask===32&&armored.Snapshot().power.armor===9,'actual Serrit removes the engine');
  check(!g.IsFatal()&&!g.IsPending(),'Serrit request completes');
 }
 {
  const g=fixture(),source=add(g,162309,1,0,2),own=add(g,112101,2,0,2,5),gift=add(g,162210,8,4,2);gift.cardState.tokenMask|=64;gift.cardState.timerValue=0;
  check(g.AiAbilityChoiceValue(source,own,2)>g.AiAbilityChoiceValue(source,gift,2),'Vrihedd Brigade boosts an ally instead of a held spy '+strength);
  g.playStack.PushBack(source);check(g.match.ClaimInitialMove(2)===0,'actual Brigade ability has a live action');
  g.MonsterRequest(source,[gift.cardState.instanceId,own.cardState.instanceId],2,1,1);
  check(own.Snapshot().power.currentPower===8&&gift.Snapshot().power.currentPower===13,'actual Brigade gives three points to the safe ally');
  check(!g.IsFatal()&&!g.IsPending(),'Brigade request completes');
 }
 {
  const g=fixture(),source=add(g,162209,1,0,2),held=add(g,112101,8,4,1,20);held.cardState.tokenMask|=64;
  check(g.AiAbilityChoiceValue(source,held,2)>0,'Serrit can weaken a strong revealed ordinary unit');
  g.match.playerOne.hasPassed=true;
  check(g.AiAbilityChoiceValue(source,held,2)===0,'passed enemy hand has no current-round damage value');
 }
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{filename:'mixed-zone-choices.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2)+'\n');

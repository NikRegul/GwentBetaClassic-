'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
// Coral must compare the direction of the swing and preserve friendly engines.
{
 const g=fixture(),own=add(g,200040,1,0,2,15),enemy=add(g,122314,1,0,1,8),coral=add(g,152107,8,4);
 check(g.AiAbilityChoiceValue(coral,enemy,0)>g.AiAbilityChoiceValue(coral,own,0),'Coral values enemy transformation above own swordsman');
 check(g.Play(2,coral.cardState.instanceId,2),'Coral plays');
 check(enemy.TemplateId()===200307&&own.TemplateId()===200040,'Coral actually transforms enemy and preserves swordsman');
}
// Django should enable the next swordsman cycle, rather than hurt himself.
{
 const g=fixture(),sword=add(g,200040,1,0),filler=add(g,112101,1,1,2,8),django=add(g,152203,8,4);
 sword.ChangeTimer(1,2);
 check(g.AiAbilityChoiceValue(django,sword,0)>g.AiAbilityChoiceValue(django,django,0),'Django prefers newly enabling timer-one swordsman');
 check(g.Play(2,django.cardState.instanceId,1),'Django plays with real target simulation');
 check(sword.Snapshot().power.currentPower===sword.Snapshot().power.basePower-1,'Django actually damages timer-one swordsman');
 sword.power.SetCurrentPair(sword.Snapshot().power.basePower-1,0);
 check(g.AiFriendlyDamageSetup(sword.Snapshot(),2,1)===0,'already damaged swordsman does not promise a second cycle');
 sword.cardState.tokenMask|=4;
 check(g.AiFriendlyDamageSetup(sword.Snapshot(),2,1)===0,'locked swordsman has no setup value');
}
// A right-consuming Vran starts before both eggs, not between them.
{
 const g=fixture(),first=add(g,132316,1,0),second=add(g,132316,1,1);
 check(g.BestVranAnchor(2)===first.cardState.instanceId,'Vran starts a chain before two eggs');
}
// Put hostile spies into damaging contact weather, including both arrivals for Pugach.
for(const profile of [false,true]){
 const g=fixture();g.weatherProfile=profile;add(g,112101,1,0,1,8);g.weather.ApplyHazard(1,2,2048);g.FlushEffects();
 const d=BetaGwentDuelDefinition(132204);
 check(g.BestCardRow(2,d)===2,'spy prefers Blood Moon row profile='+profile);
}
// Periodic weather is not immediate contact damage; boons must not look harmful.
{
 const g=fixture(),d=BetaGwentDuelDefinition(132204);g.weather.ApplyHazard(1,2,256);g.FlushEffects();
 check(g.BestCardRow(2,d)!==2,'spy does not mistake Full Moon boon for damaging contact weather');
}
// Enemy-wide random specials advertise an enemy cast area, not an own row.
{
 const g=fixture(1),d=BetaGwentDuelDefinition(200009);
 check(g.DirectSpecialKind(d)===3&&d.targetSide===2,'Shrike casts on enemy half');
 for(let row=1;row<=4;row*=2)add(g,112101,row,0,2,10);
 const c=add(g,200009,8,4,1);
 check(g.Play(1,c.cardState.instanceId,1),'Shrike resolves from a cast area');
 check([1,2,4].every(row=>g.live.some(c=>c.cardState.positionPlayerId===2&&c.Snapshot().locationMask===row&&c.Snapshot().power.currentPower<10)),'Shrike still damages enemies across all rows');
}
// A 13-point spy with a weak draw must not throw away a late lead.
{
 const g=fixture();g.live.filter(c=>c.Snapshot().locationMask===8&&c.cardState.positionPlayerId===2).forEach(c=>c.Move(2,512,0));
 add(g,112101,1,0,2,10);add(g,112101,1,0,1,8);
 const spy=add(g,162210,8,0);add(g,112101,16,0,2,3);add(g,112101,16,1,2,3);
 g.Leader(2)?.Move(2,512,0);
 check(g.AiSpyUnrecoverable(spy),'late spy with weak follow-up cannot throw away the lead');
}
// All 46 reviewed rosters remain legal; Natalis now has two tactics.
{
 const g=fixture(),ointment=add(g,201619,16,0),wish=add(g,113102,8,4),unit=add(g,122314,16,1);
 check(g.AiCreatedOptionValue(ointment.Definition(),2)===0,'empty Ointment has zero ability value');
 check(g.AiAbilityChoiceValue(add(g,122403,1,0),ointment,2)===0,'alchemy tutor does not invent Ointment targets');
 add(g,122314,32,0,2,6);
 check(g.AiCreatedOptionValue(ointment.Definition(),2)===0,'Ointment rejects grave targets over five power');
 check(g.Play(2,wish.cardState.instanceId,1),'Last Wish resolves its real candidate selection');
 check(unit.Snapshot().locationMask!==16&&ointment.Snapshot().locationMask===16,'Last Wish chooses useful unit instead of empty Ointment');
}
{
 const g=fixture();for(let i=0;i<5;i++)add(g,132201,1,i,2,10);
 g.weather.ApplyHazard(2,1,64);g.FlushEffects();
 const moon=BetaGwentDuelModeDefinition(BetaGwentDuelDefinition(200067),201746);
 check(moon.specialToken===256,'Full Moon option fixture');
 check(g.weather.ReplacementValue(2,2,1,256)>0,'Full Moon values preventing future storm damage');
 check(g.specials.RowValue(moon,2,2,1)>g.specials.RowValue(moon,2,2,2),'Full Moon prefers replacing own storm to an empty row');
 check(g.weather.ReplacementValue(2,1,1,256)===0,'no invented replacement value on a clear enemy row');
}
{
 const ids={v:[]};BetaGwentAIOrdinaryPresets(ids);
 check(ids.v.length===46&&new Set(ids.v).size===46,'all 46 distinct archetypes remain active');
 const deck={v:[]};BetaGwentDuelPresetDeck(58,deck);
 check(deck.v.length===25&&deck.v.includes(123201)&&deck.v.includes(200019),'Cursed Adda contains Reinforcements and Marching Orders in 25 cards');
}
// Returning the same instance to the deck must not silently heal its strength.
for(const mode of ['shuffle','bottom','exchange']){
 const g=fixture(),c=add(g,152209,8,4),draw=add(g,112101,16,0);
 c.ChangeBasePower(-2,true);c.ChangePower(-4,true);const before=c.Snapshot().power;
 if(mode==='shuffle')g.NorthMoveInactive(c,2,16,true);
 if(mode==='bottom')g.NilfBottom(c);
 if(mode==='exchange')g.NorthExchange(c,draw);
 check(c.Snapshot().locationMask===16&&c.Snapshot().power.currentPower===before.currentPower&&c.Snapshot().power.basePower===before.basePower,'deck '+mode+' preserves weakened instance');
 g.NilfTake(c,2);
 check(c.Snapshot().locationMask===8&&c.Snapshot().power.currentPower===before.currentPower,'drawing preserves weakened strength after '+mode);
}
// Morkvarg revives before weakening; the final one-strength death banishes him.
{
 const g=fixture(),c=add(g,152209,1,0);
 for(const expected of [4,2,1]){
  c.Kill();g.FlushDeaths();
  check(alive(c)&&c.Snapshot().power.currentPower===expected&&c.Snapshot().power.basePower===expected,'Morkvarg revives with '+expected+' strength');
 }
 c.Kill();g.FlushDeaths();
 check(c.Snapshot().locationMask===512&&!c.Snapshot().isWaitingToDie&&!g.IsFatal(),'Morkvarg disappears at zero instead of remaining on board');
}
{
 const g=fixture(),c=add(g,152209,8,4,2,1);
 g.NilfDiscard(c);g.FlushDeaths();
 check(alive(c)&&c.Snapshot().power.currentPower===4,'damaged discarded Morkvarg revives with positive weakened strength');
}
{
 const g=fixture(),c=add(g,152209,32,0);c.ChangeBasePower(-9,true);
 g.NorthResurrect(c,0,1,-3,false);
 check(c.Snapshot().locationMask===512,'generic resurrection excludes exhausted zero-base units');
}
{
 const g=fixture(),c=add(g,152209,32,0);
 for(const row of [1,2,4])for(let i=0;i<9;i++)add(g,112101,row,i);
 g.monsters.skellige.ReviveMorkvarg(c,0,-3);
 check(c.Snapshot().locationMask===32&&c.Snapshot().power.basePower===9,'full board does not weaken an unsuccessful Morkvarg resurrection');
}
{
 const g=fixture(),c=add(g,152209,1,0);c.AddLock();c.Kill();g.FlushDeaths();
 check(c.Snapshot().locationMask===32&&(c.Snapshot().tokenMask&4)!==0,'locked Morkvarg remains locked in grave without resurrection');
}
globalThis.report={stage:123,checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'scenarios123.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');

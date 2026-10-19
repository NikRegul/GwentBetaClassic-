// Real translated WitcherScript: target threat, optional-round pass and nested specials.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function clearHand(g,side){g.live.filter(c=>c.cardState.positionPlayerId===side&&c.cardState.locationMask===8).forEach(c=>c.Move(side,512,0));}
function targets(timer=2){
 const g=fixture(),vran=add(g,132305,1,0,1,27),miruna=add(g,132108,2,0,1,4);
 miruna.cardState.timerValue=timer;
 const victim=add(g,142205,2,0,2,10),sword=add(g,200535,8,4,2,9);
 return {g,vran,miruna,victim,sword};
}
{
 const {g,vran,miruna,sword}=targets(),before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
 check(g.AiAbilityDamage(sword,vran)===9,'master swordsman uses current power as damage');
 check(g.AiEngineValue(miruna.Snapshot(),2)===20,'Miruna forecasts the two-sided ten-power charm');
 check(g.AiAbilityChoiceValue(sword,miruna,0)>g.AiAbilityChoiceValue(sword,vran,0),'preventing charm beats nine damage to a surviving Vran');
 check(g.AiChoiceFutureValue(sword,miruna)===20,'exact choice retains the delayed charm correction');
 check(JSON.stringify(g.live.map(c=>c.Snapshot()))===before&&g.random.DrawCount()===draws,'forecast changes neither live cards nor live RNG');
 check(g.Play(2,sword.cardState.instanceId,4),'swordsman actually plays');
 check(!alive(miruna)&&vran.Snapshot().power.currentPower===27,'real target selection kills Miruna and preserves Vran power');
 check(!g.IsFatal()&&!g.IsPending(),'swordsman has no unfinished request');
}
{
 const {g,miruna,sword}=targets(1);
 check(g.AiChoiceFutureValue(sword,miruna)===0,'one-tick charm already resolved by exact play is not double-counted');
 check(g.Play(2,sword.cardState.instanceId,4)&&!alive(miruna),'imminent Miruna also receives the actual strike');
}
{
 const {g,miruna,victim}=targets();
 miruna.AddTokens(4);check(g.AiEngineValue(miruna.Snapshot(),2)===0,'locked Miruna has no charm threat');
 miruna.ToggleLock();miruna.cardState.timerValue=0;check(g.AiEngineValue(miruna.Snapshot(),2)===0,'expired Miruna has no repeated payoff');
 miruna.cardState.timerValue=4;check(g.AiEngineValue(miruna.Snapshot(),2)===0,'timer outside public horizon has no payoff');
 miruna.cardState.timerValue=2;victim.Move(2,4,0);check(g.AiEngineValue(miruna.Snapshot(),2)===0,'only the opposing row supplies a charm victim');
 victim.Move(2,2,0);victim.AddTokens(8);check(g.AiEngineValue(miruna.Snapshot(),2)===0,'hidden ambush is excluded as in the real charm query');
 victim.cardState.tokenMask&=~8;g.match.playerOne.hasPassed=true;check(g.AiEngineValue(miruna.Snapshot(),2)===0,'passed Miruna owner cannot start another turn');
 g.match.playerOne.hasPassed=false;
 for(let i=1;i<9;i++)add(g,142317,2,i,1,1);
 check(g.AiEngineValue(miruna.Snapshot(),2)===0,'full destination row has no charm capacity');
}
function optionalPosition(mandatory=false){
 const g=fixture();clearHand(g,2);
 add(g,112101,4,0,2,67);add(g,142317,2,0,2,13);
 add(g,112101,1,0,1,38);const miruna=add(g,132108,2,0,1,4);miruna.cardState.timerValue=1;
 const aglais=add(g,142106,8,0,2,14);add(g,113309,8,1,2);add(g,142203,8,2,2);
 add(g,112101,8,4,1);g.match.playerOne.crowns=mandatory?1:0;
 return {g,aglais};
}
{
 const {g,aglais}=optionalPosition(),logs=[];Host.log=s=>logs.push(s);
 check(!g.AiAglaisHasTarget(2),'Aglais sees an empty enemy special grave');
 check(g.AiTimingReserve(aglais,14)>=16,'empty Aglais ability is reserved for later rounds');
 check(g.AiExactTempo(aglais)===-12,'fourteen-power Aglais minus imminent thirteen-power charm is minus twelve');
 check(g.OpponentStep(),'optional-round decision resolves');Host.log=null;
 check(g.match.playerTwo.hasPassed&&aglais.Snapshot().locationMask===8,'passing with a remaining lead preserves empty Aglais');
 check(logs.some(s=>s.includes('reason=no_positive_play_pass_keeps_lead')),'log identifies the resource-preserving pass');
 check(!g.IsFatal()&&!g.IsPending(),'optional pass resolves safely');
}
{
 const {g,aglais}=optionalPosition(true);
 check(g.OpponentStep()&&!g.match.playerTwo.hasPassed,'mandatory round is not conceded by optional-round policy');
 check(aglais.Snapshot().locationMask!==8,'mandatory round can still use an empty Aglais body');
}
{
 // Isolate the empty ability/body decision from optional-round hand economy.
 // A fixture with ten opposing cards would now correctly decline a -3+ chase.
 const g=fixture();clearHand(g,2);clearHand(g,1);g.match.playerOne.hasPassed=true;
 add(g,112101,1,0,1,6);const aglais=add(g,142106,8,0,2,8);
 check(g.OpponentStep()&&alive(aglais),'Aglais body remains a legal winning catch after a pass');
}
{
 const g=fixture(),special=add(g,113309,32,0,1);
 check(g.AiAglaisHasTarget(2),'bronze or silver enemy special is a legal Aglais target');
 special.AddTokens(512);check(!g.AiAglaisHasTarget(2),'doomed special cannot be replayed');
 special.cardState.tokenMask&=~512;special.cardState.runtimeTierMask=8;check(!g.AiAglaisHasTarget(2),'gold special is excluded');
 special.cardState.runtimeTierMask=4;special.Move(2,32,0);check(!g.AiAglaisHasTarget(2),'own grave is excluded');
}
{
 const g=fixture(),first=add(g,142317,1,0,2,11),second=add(g,142317,2,0,2,11);
 add(g,112101,1,0,1,10);const scorch=add(g,113309,16,0,2),poet=add(g,201776,16,1,2);
 check(g.AiCreatedOptionValue(scorch.Definition(),2)===-22,'created Scorch counts both friendly eleven-power deaths with negative sign');
 check(g.AiPileCandidateValue(scorch,2,false,0)===-22,'pile Scorch has the same signed real value');
 check(g.AiPileCandidateValue(poet,2,false,0)>-22,'Dandelion Poet beats friendly-only Scorch');
 const wish=add(g,113102,8,4,2);
 check(g.Play(2,wish.cardState.instanceId,4),'Last Wish actually plays its nested choice');
 check(alive(first)&&alive(second)&&alive(poet),'Last Wish picks Dandelion, preserving both friendly strongest units');
 check(scorch.Snapshot().locationMask===8&&!g.IsFatal()&&!g.IsPending(),'Dandelion draws harmful Scorch but plays a safe hand card');
}
{
 const g=fixture();clearHand(g,2);add(g,142317,1,0,2,11);add(g,142317,2,0,2,11);add(g,112101,1,0,1,10);
 add(g,113309,16,0,2);const wish=add(g,113102,8,0,2),safe=add(g,142317,8,1,2,6);
 check(g.AiExactTempo(wish)<0,'parent simulation sees harmful forced Scorch');
 check(g.OpponentStep()&&wish.Snapshot().locationMask===8&&alive(safe),'AI chooses a safe hand card over tutor with only harmful Scorch');
}
for(const [own,enemy,expected] of [[11,12,12],[12,11,-12],[11,11,0]]){
 const g=fixture();add(g,142317,1,0,2,own);add(g,142317,1,0,1,enemy);
 const d=BetaGwentDuelDefinition(113309);
 check(g.specials.DefinitionValue(d,2)===expected,'Scorch enemy/friendly/tied maximum '+own+'/'+enemy);
}
globalThis.report={checks,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'miruna-aglais-scorch180.bundle.js',timeout:180000});
console.log(JSON.stringify(context.report));
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');

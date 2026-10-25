// Regressions from player feedback: board targeting, optional conceal, Reveal and round economy.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
context.manifestText=fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function empty(side=2){const g=fixture(side);g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();return g;}
function hand(g,side,n,power=10){for(let i=0;i<n;i++)add(g,112101,8,i,side,power);}
const decisions=[];
for(const side of [1,2]){
 const g=empty(side),enemy=3-side,legal=add(g,112101,1,0,enemy,15),panther=add(g,200139,8,0,side);
 for(let i=0;i<4;i++)add(g,112101,2,i,enemy,15);
 check(g.Play(side,panther.Snapshot().instanceId,4),'Panther plays '+side);
 if(side===1){const req=g.GetRequestSnapshot();check(req.kind===2,'Panther requests board targets');
  check(g.pendingIds.length===1&&g.pendingIds[0]===legal.Snapshot().instanceId,'Panther excludes full rows');
  check(!g.FinishTarget(g.requestId),'Panther target remains mandatory');
  check(g.SelectTarget(g.requestId,legal.Snapshot().instanceId),'Panther selects board unit');}
 check(legal.Snapshot().power.currentPower===8&&!g.IsPending()&&!g.IsFatal(),'Panther deals seven and completes '+side);
}
for(const count of [1,2,3,4,5]){
 const g=empty(1),targets=[];for(let i=0;i<count;i++)targets.push(add(g,112101,1,i,2,15));
 const panther=add(g,200139,8,0,1);check(g.Play(1,panther.Snapshot().instanceId,2),'Panther boundary deploy '+count);
 check(!!g.IsPending()===(count<4),'Panther requires strictly fewer than four units '+count);
 if(count<4){check(g.pendingIds.length===count,'Panther includes all legal row units '+count);g.SelectTarget(g.requestId,targets[0].Snapshot().instanceId);}
 check(!g.IsPending()&&!g.IsFatal(),'Panther boundary resolves '+count);
}
for(const count of [0,1,2]){
 const g=empty(1),ally=add(g,112101,8,0,1,5),enemy=add(g,112101,8,0,2,5),henry=add(g,200227,8,1,1);
 ally.SetRevealed(true);enemy.SetRevealed(true);
 check(g.Play(1,henry.Snapshot().instanceId,1),'Henry plays '+count);
 let req=g.GetRequestSnapshot();check(req.limits.minimum===0&&req.limits.maximum===2,'Henry offers zero to all units');
 if(count>=1){check(g.SelectTarget(g.requestId,ally.Snapshot().instanceId),'Henry conceals ally');
  req=g.GetRequestSnapshot();check(req.selectedCount===1&&req.limits.minimum===0&&req.limits.maximum===2,'Henry keeps stable optional count');}
 if(count===2)check(g.SelectTarget(g.requestId,enemy.Snapshot().instanceId),'Henry conceals enemy');
 else check(g.FinishTarget(g.requestId),'Henry finishes early '+count);
 check(!g.IsPending()&&!g.IsFatal(),'Henry completes '+count);
 check(ally.Snapshot().power.currentPower===(count?7:5),'Henry ally boost '+count);
 check(enemy.Snapshot().power.currentPower===(count===2?3:5),'Henry enemy damage '+count);
 check(((ally.Snapshot().tokenMask&64)!==0)===(count===0),'Henry preserves unchosen ally '+count);
 check(((enemy.Snapshot().tokenMask&64)!==0)===(count!==2),'Henry preserves unchosen enemy '+count);
}
for(const owner of [1,2])for(const targetSide of [1,2])for(const active of [1,2]){
 const g=empty(active),machine=add(g,162317,1,0,owner),victim=add(g,112101,1,0,3-owner,30),card=add(g,112101,8,0,targetSide);
 g.NilfReveal(card,true);g.FlushEffects();g.FlushDeaths();
 const expected=active===owner?28:30;
 check(victim.Snapshot().power.currentPower===expected,'Mangonel uses active owner, either hand '+owner+'/'+targetSide+'/'+active);
 g.NilfReveal(card,true);g.NilfReveal(card,false);g.FlushEffects();g.FlushDeaths();
 check(victim.Snapshot().power.currentPower===expected,'no duplicate or conceal shot '+owner+'/'+targetSide+'/'+active);
}
for(const targetSide of [1,2]){
 const g=empty(1),victim=add(g,112101,1,0,2,30),machine=add(g,162317,1,0,1),card=add(g,112101,8,0,targetSide),alchemist=add(g,162316,8,1,1);
 check(g.Play(1,alchemist.Snapshot().instanceId,2),'Alchemist actual deploy '+targetSide);
 check(g.SelectTarget(g.requestId,card.Snapshot().instanceId),'Alchemist reveals selected hand '+targetSide);
 check(victim.Snapshot().power.currentPower===28,'actual Reveal triggers Mangonel '+targetSide);
}
for(const template of [142204,142208,142306])for(const power of [1,40]){
 const g=empty(),ambush=add(g,template,1,2,1,power);ambush.AddTokens(8);
 for(const i of [0,1,3,4])add(g,112101,1,i,1,2);
 add(g,112101,1,0,2,9);hand(g,2,4,20);hand(g,1,4);
 const rng=g.random.DrawCount();check(g.AiPublicAmbushPassRisk()===14,'public ambush risk ignores hidden template/power '+template+'/'+power);
 check(g.AiPublicPassLead()===-13,'visible lead is unsafe under ambush '+template+'/'+power);
 check(g.random.DrawCount()===rng,'pass forecast preserves live RNG');
 ambush.AddTokens(4);check(g.AiPublicAmbushPassRisk()===0,'locked ambush cannot trigger');
}
{
 const g=empty(),ambush=add(g,142204,1,2,1,6);ambush.AddTokens(8);
 for(const i of [0,1,3,4])add(g,112101,1,i,1,2);
 add(g,112101,1,0,2,9);hand(g,2,4,20);hand(g,1,4);g.match.playerOne.hasPassed=true;
 const predicted=g.AiPublicPassLead();check(predicted===-13,'Toruviel exact risk fixture');
 const clone=g.AiSimClone();check(clone!==null,'clone exists');
 check(g.OpponentStep()&&!g.match.playerTwo.hasPassed,'AI catches up instead of passing under Toruviel');
 check(!g.IsFatal()&&!g.IsPending(),'Toruviel decision completes');
}
for(const enemyHand of [6,7])for(const ownHand of [2,5]){
 const g=empty();add(g,112101,1,0,2,10);add(g,112101,2,0,2,17);add(g,112101,4,0,2,23);add(g,112101,1,0,1,10);hand(g,2,ownHand);hand(g,1,enemyHand);
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'large-lead decision completes');Host.log=null;
 if(!g.match.playerTwo.hasPassed)console.log(logs.filter(s=>/event=(BEGIN|PLAN|SELECT|PASS)|researched_economy|leaderBurst/.test(s)).join('\n'));
 check(g.match.playerTwo.hasPassed,'40 points ahead passes with card deficit '+ownHand+'/'+enemyHand);
 check(g.CountLocation(2,8)===ownHand,'large-lead pass saves remaining hand');
 decisions.push({ownHand,enemyHand,lead:40,logs:logs.filter(s=>/event=(SELECT|PASS)/.test(s))});
}
for(const preset of JSON.parse(manifestText).presets){
 const g=empty();g.archetypeAI.Initialize(g,[],preset,BetaGwentDuelPreset(preset).leaderTemplateId);
 add(g,112101,1,0,2,10);add(g,112101,2,0,2,17);add(g,112101,4,0,2,23);add(g,112101,1,0,1,10);
 hand(g,2,5);hand(g,1,6);
 check(g.OpponentStep()&&g.match.playerTwo.hasPassed&&!g.IsFatal(),'every archetype saves its hand at a safe 40-point lead '+preset);
}
check(BetaGwentAIRoundDecision(1,0,0,10,5,6,10,25,false)===0,'small lead still needs tempo');
check(BetaGwentAIRoundDecision(2,0,1,40,5,6,10,25,false)===0,'must-win round keeps playing');
check(BetaGwentAIRoundDecision(1,0,0,40,5,6,10,50,false)===0,'large public answer envelope prevents premature pass');
check(BetaGwentAIEarlyPass(55,25,0,5,6,0),'multi-reply tax can recover red-coin deficit');
globalThis.report={checks,decisions,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'feedback092.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,actualWitcherScript:true,nativeGameTested:false}));

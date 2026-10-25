// User log 23 Oct 20:20-20:24: Olgierd misses Vran, all Nekkers remain in R2
// hand, and a draw-spy opening is immediately conceded after the opponent passes.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),observe=process.argv.includes('--observe');
const ctx=vm.createContext({console,observe,tunes:JSON.parse(fs.readFileSync(path.join(snapshot,'tunes.json'),'utf8'))});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
Host.tunes=[tunes,tunes];const failures=[],cases=[];
function expect(value,label){checks++;if(!value)failures.push(label);console.log(value?'PASS':'FAIL',label);}
function blank(preset=56,round=1){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne=[];g.aiStartingDeckTwo=[];g.presetTwo=preset;
 g.archetypeAI.Initialize(g,[],preset,BetaGwentDuelPreset(preset).leaderTemplateId);
 g.match.roundNumber=round;g.match.playerOne.crowns=round===2?1:0;g.match.playerTwo.crowns=0;
 return g;
}
function act(g,label,staged=false){const logs=[];Host.log=s=>logs.push(s);try{
 let ok=g.OpponentStep(),ticks=0;
 while(staged&&!ok&&!g.AiPreparationIsReady()){
  while(!g.AiPreparationStep())if(++ticks>500)throw Error('staged gift chase stalled');
  ok=g.OpponentStep();
 }
 expect(ok&&!g.IsFatal()&&!g.IsPending(),label+' completes');
 }finally{Host.log=null;}
 cases.push({label,select:logs.filter(s=>/event=(SELECT|PASS|CHASE)/.test(s)),consume:logs.filter(s=>s.includes('DUEL_VRAN_CONSUME'))});return logs;}
// A currently active Vran has ordinary food to its right. Olgierd must be fed
// before that food: his end-turn return preserves the body and yields +5.
for(const damp of [40,65]){
 const g=blank();g.aiSimDamp=damp;
 add(g,132201,1,0,2);const vran=add(g,132308,1,1,2);vran.cardState.timerValue=1;
 add(g,200174,1,2,2);add(g,200174,1,3,2);add(g,201776,4,0,2);
 const olg=add(g,112207,8,0,2);add(g,132305,16,0,2);
 for(let i=0;i<4;i++)add(g,112405,8,i,1);add(g,112405,1,0,1,30);
 const logs=act(g,'Olgierd feed/'+damp);
 // Vran ticks on the next own turn start, after the opponent's real action.
 // Olgierd's return then resolves at that own turn's end.
 const enemy=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);
 Host.log=s=>logs.push(s);try{
  expect(g.Play(1,enemy.Snapshot().instanceId,2),'opponent turn advances Vran timer/'+damp);
  expect(g.Pass(2),'own turn end resolves Olgierd return/'+damp);
 }finally{Host.log=null;}
 expect(logs.some(s=>s.includes('DUEL_VRAN_CONSUME')&&s.includes('target='+olg.cardState.instanceId)),'Vran actually consumes Olgierd/'+damp);
 expect((olg.Snapshot().locationMask&7)!==0,'Olgierd returns after the meal/'+damp);
 expect(vran.Snapshot().power.currentPower>=11,'Vran receives Olgierd five points/'+damp);
}
// A spent/locked Vran must not force a feeding placement.
{
 const g=blank(),vran=add(g,132308,4,0,2),olg=add(g,112207,8,0,2);
 vran.AddLock();add(g,200174,1,0,2);
 expect(g.AiAdjacencyIndex(olg,4)===-3,'locked Vran does not request a meal slot');
}
// A Nekker with a grown deck copy is worth more than replacing its meal with
// Olgierd. Feeding an active Vran must not break that winning deathwish chain.
{
 const g=blank(56,2),vran=add(g,132308,1,0,2),nekker=add(g,132305,1,1,2,5),olg=add(g,112207,8,0,2);
 vran.cardState.timerValue=1;add(g,132305,16,0,2,18);add(g,132305,16,1,2,18);
 for(let i=0;i<4;i++)add(g,112405,8,i,1);
 expect(g.AiAdjacencyIndex(olg,1)!==1,'Olgierd does not displace a stronger Nekker chain');
}
// At R2 the enemy owns a crown: three growing Nekkers in hand leave no chain
// target in deck. One remaining mulligan should restore a deck copy.
{
 const g=blank(56,2),nekkers=[];
 for(let i=0;i<3;i++)nekkers.push(add(g,132305,8,i,2,11));
 add(g,132308,8,3,2);add(g,132308,8,4,2);add(g,200539,8,5,2);add(g,132202,8,6,2);
 add(g,132304,16,0,2);add(g,132201,16,1,2);add(g,132201,16,2,2);
 g.AiMulligan(1);
 expect(nekkers.filter(c=>c.Snapshot().locationMask===16).length===1,'R2 mulligan restores one Nekker to deck');
 expect(nekkers.filter(c=>c.Snapshot().locationMask===8).length===2,'R2 keeps two grown Nekkers in hand');
}
// Last seed is kept; the ordinary first mulligan still removes a drone.
for(const template of [132305,132304]){
 const g=blank(),card=add(g,template,8,0,2);add(g,132308,8,1,2);add(g,112207,8,2,2);
 add(g,132201,16,0,2);add(g,132201,16,1,2);if(template===132304)add(g,132304,16,2,2);
 g.AiMulligan(1);
 expect(card.Snapshot().locationMask===(template===132305?8:16),'mulligan '+(template===132305?'keeps last Nekker':'removes initial drone'));
}
// Already spent spies do not justify a special two-action chase commitment.
for(const ownSpy of [false,true])for(const damp of [40,65]){
 const g=blank(77);g.aiSimDamp=damp;g.match.playerOne.hasPassed=true;
 const gift=add(g,ownSpy?122203:112405,1,0,1,13);
 if(ownSpy){gift.cardState.ownerId=2;gift.cardState.tokenMask|=128;gift.cardState.timerValue=0;}
 for(let i=0;i<10;i++)add(g,112405,8,i,1);
 for(let i=0;i<10;i++)add(g,112405,8,i,2,7);
 g.aiRoundHandOne=10;g.aiRoundHandTwo=10;
 act(g,'opening gift chase/'+ownSpy+'/'+damp);
 expect(g.match.playerTwo.hasPassed,'ordinary resource budget still applies after the spy/'+ownSpy+'/'+damp);
}
// Before playing a spy, simulate a real enemy pass and at most one own action.
// Body-only fixtures distinguish one-card recovery from leader+card or two cards.
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let plays=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(id){plays++;return play.call(this,id);};
function spyPosition(power,round=1,lead=0){
 const g=blank(77,round),spy=add(g,122203,8,0,2);
 for(let i=0;i<9;i++)add(g,112405,8,i+1,2,power);
 for(let i=0;i<5;i++)add(g,112405,16,i,2,power);
 for(let i=0;i<10;i++)add(g,112405,8,i,1);
 if(lead)add(g,112405,1,0,2,lead);
 return {g,spy};
}
function visible(g){return JSON.stringify({match:g.match.Snapshot(),cards:g.live.map(c=>c.Snapshot()),draws:g.random.DrawCount()});}
for(const power of [7,14])for(const damp of [40,65]){
 const {g,spy}=spyPosition(power);g.aiSimDamp=damp;
 const before=visible(g),job=new CBetaGwentAISpy188();job.Initialize(g,spy.cardState.instanceId);
 let ticks=0,peak=0,done=false;
 while(!done){plays=0;done=job.Step();peak=Math.max(peak,plays);if(++ticks>250)throw Error('spy guard stalled');}
 expect(job.unsafe===(power===7),'pre-play spy guard distinguishes one-card recovery/'+power+'/'+damp);
 expect(peak<=1,'spy forecast performs at most one simulated play per callback/'+power+'/'+damp);
 expect(visible(g)===before,'spy forecast preserves live board and RNG/'+power+'/'+damp);
 if(power===7){
  const logs=act(g,'unsafe spy opening/'+damp);
  expect(spy.Snapshot().locationMask===8,'AI keeps unsafe spy in hand/'+damp);
  expect(logs.some(s=>s.includes('reason=draw_spy_cannot_recover_after_pass')),'AI explains rejected pass-vulnerable spy/'+damp);
 }
}
// A secure existing lead and a mandatory second round retain their own logic.
for(const [round,lead] of [[1,20],[2,0]]){
 const {g,spy}=spyPosition(7,round,lead),job=new CBetaGwentAISpy188();job.Initialize(g,spy.cardState.instanceId);
 let ticks=0;while(!job.Step())if(++ticks>250)throw Error('spy guard counterexample stalled');
 expect(!job.unsafe,'spy guard preserves safe lead or mandatory-round option/'+round+'/'+lead);
}
// Cooperative preparation must use the same guard, without spending live RNG.
{
 const a=spyPosition(7),b=spyPosition(7);a.g.aiSimDamp=65;b.g.aiSimDamp=65;
 const before=visible(b.g);let ticks=0,peak=0,done=false;
 while(!done){plays=0;done=b.g.AiPreparationStep();peak=Math.max(peak,plays);if(++ticks>500)throw Error('staged spy forecast stalled');}
 expect(peak<=1,'cooperative preparation keeps one-play callback limit');
 expect(visible(b.g)===before,'cooperative spy preparation preserves live board and RNG');
 act(a.g,'sync spy opening');act(b.g,'staged spy opening',true);
 expect(visible(a.g)===visible(b.g),'cooperative and synchronous pre-play spy choices agree');
}
globalThis.report={checks,failures,cases,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{filename:'swarm-playtest092.bundle.js',timeout:180000});
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(ctx.report,null,2)+'\n');
if(ctx.report.failures.length&&!observe)throw Error(ctx.report.failures.join('; '));
console.log(JSON.stringify({checks:ctx.report.checks,failures:ctx.report.failures}));

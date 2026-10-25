// Production decisions: response tax, R1 investment, and R2 plans from the actual hand.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),out=process.argv[3],observe=process.argv.includes('--observe');
const context=vm.createContext({console,observe});
context.manifestText=fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0]
 .replace("if(!v)throw Error(n);checks++;console.log('PASS',n);","if(!v){failures.push(n);if(!observe)throw Error(n);}checks++;console.log(v?'PASS':'FAIL',n);");
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;const failures=[];'+fixture+String.raw`
const cases=[];
function blank(preset=54,round=1){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.match.roundNumber=round;
 g.match.playerOne.crowns=0;g.match.playerTwo.crowns=round===2?1:0;g.aiSimDamp=40;
 g.archetypeAI.Initialize(g,[],preset,BetaGwentDuelPreset(preset).leaderTemplateId);return g;}
function body(g,id,zone,index,side,power){const c=add(g,id,zone,index,side);c.power.ResetTemplatePower(power,0);return c;}
function hand(g,side,n,power=8){const r=[];for(let i=0;i<n;i++)r.push(body(g,112405,8,i,side,power));return r;}
function act(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'complete decision '+label);cases.push({label,logs:logs.filter(s=>/event=(OPTION|PLAN|ROUND_BUDGET|PRESSURE_VALUE|SELECT|PASS)/.test(s))});}
// Both cards force the same extra public reply; Geralt's overkill costs a gold.
for(const deciding of [false,true]){
 const g=blank();if(deciding){g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;}
 for(const [row,power] of [[1,8],[2,12],[4,14]])add(g,112405,row,0,2,power);
 add(g,112405,1,0,1,10);hand(g,1,6);
 const cheap=body(g,112405,8,0,2,9),gold=body(g,112103,8,1,2,20);hand(g,2,4,3);
 act(g,'equal-reply-tax/'+deciding);
 check(!g.match.playerTwo.hasPassed,'small lead is still contested');
 if(!deciding)check(cheap.Snapshot().locationMask!==8&&gold.Snapshot().locationMask===8,'cheap threshold crossing preserves gold for the final');
 else check(gold.Snapshot().locationMask!==8,'deciding round retains full immediate tempo');
}
// Taking a 14-point deficit with these bodies consumes two cards, leaving -2.
for(const balance of [0,2])for(const mustWin of [false,true]){
 const g=blank();if(mustWin){g.match.roundNumber=2;g.match.playerOne.crowns=1;}
 add(g,112405,1,0,1,20);add(g,112405,1,0,2,6);hand(g,1,5);const cards=hand(g,2,5+balance,8);
 act(g,'two-card-commitment/'+balance+'/'+mustWin);
 const pass=balance===0&&!mustWin;
 check(g.match.playerTwo.hasPassed===pass,'optional expensive chase respects hand balance and survival');
 if(pass)check(cards.every(c=>c.Snapshot().locationMask===8),'concession saves the whole remaining hand');
}
// A strong single-card catch is still played, including a leader-free plain hand.
{
 const g=blank();add(g,112405,1,0,1,20);add(g,112405,1,0,2,6);hand(g,1,5);const winner=body(g,112405,8,0,2,16);hand(g,2,4,8);
 act(g,'one-card-catch');check(!g.match.playerTwo.hasPassed&&winner.Snapshot().locationMask!==8,'one-card catch overrides resource preservation');
}
// Real spy play: removal comes from the known list, including creators.
for(const vulnerable of [false,true])for(const removal of [0,113309,142108,112102]){
 const g=blank();g.match.currentPlayerId=1;g.aiStartingDeckOne.PushBack(112405);if(removal)g.aiStartingDeckOne.PushBack(removal);
 if(vulnerable){add(g,112405,1,0,2,30);add(g,112405,2,0,1,14);}
 else{for(const [row,power] of [[1,8],[2,12],[4,14]])add(g,112405,row,0,2,power);add(g,112405,2,0,1,14);}
 hand(g,2,5);hand(g,1,5);
 const spy=add(g,162210,8,5,1);add(g,112405,16,0,1);add(g,112405,16,1,1);
 check(g.Play(1,spy.Snapshot().instanceId,4),'human actually plays a draw spy');
 check(g.IsPending()&&g.pendingIds.length===2,'draw spy offers its real two-card choice');
 check(g.SelectTarget(g.requestId,g.pendingIds[0]),'human finishes the spy draw');
 check(g.match.currentPlayerId===2&&g.CountLocation(1,8)===6,'spy turn preserves the public red-coin card deficit');
 const remaining=g.CountLocation(2,8);act(g,'human-draw-spy/'+vulnerable+'/'+removal);
 if(vulnerable&&removal)check(!g.match.playerTwo.hasPassed,'possible Scorch, Schirru or Igni protects the vulnerable lead');
 else check(g.match.playerTwo.hasPassed&&g.CountLocation(2,8)===remaining,'spy lead permits pass when safe or Scorch absent from the known list');
}
// Private hand/deck movements never change the known unseen pool.
if(typeof CBetaGwentDuelSession.prototype.AiEnemyMayHold==='function'){
 const g=blank();hand(g,1,4);g.aiStartingDeckOne.PushBack(112405);
 check(!g.AiEnemyMayHold(113309),'Scorch absent from starting list is excluded');
 g.aiStartingDeckOne.PushBack(113309);check(g.AiEnemyMayHold(113309),'unseen starting Scorch remains possible');
 const scorch=add(g,113309,16,0,1);check(g.AiEnemyMayHold(113309),'actual hidden deck location is not consulted');
 scorch.Move(1,8,4);check(g.AiEnemyMayHold(113309),'actual hidden hand location is not consulted');
 scorch.Move(1,32,0);check(!g.AiEnemyMayHold(113309),'publicly spent only copy is excluded');
 g.aiStartingDeckOne.PushBack(113309);check(g.AiEnemyMayHold(113309),'one of two starting copies remains possible');
 g.aiStartingDeckOne.Clear();g.aiStartingDeckOne.PushBack(142108);
 check(!g.AiEnemyMayHold(113309)&&g.AiEnemyMayHold(142108),'Schirru remains an independent route to Scorch');
 const made=add(g,113309,8,4,1);made.createdCopy=true;made.AddTokens(64);
 check(g.AiEnemyMayHold(113309),'public generated Scorch in hand is respected');
}
for(const preset of [54,68])for(const engines of [false,true]){
 const g=blank(preset,2);hand(g,1,4);
 if(engines){add(g,132201,8,0);add(g,132305,8,1);hand(g,2,4,10);}else hand(g,2,6,10);
 act(g,'final-hand/'+preset+'/'+engines);
 check(g.match.playerTwo.hasPassed===engines,'actual engine package preserves long final; bodies can pressure '+preset+'/'+engines);
 check(g.archetypeAI.roundPlan===(engines?1:2),'plan follows the remaining hand '+preset+'/'+engines);
}
// Losing the cheap bodies during pressure must allow the plan to be reconsidered.
{
 const g=blank(54,2);hand(g,1,4);hand(g,2,6,10);g.archetypeAI.Refresh();
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);g.archetypeAI.PlanTurn(model);
 check(g.archetypeAI.roundPlan===2,'independent hand starts a pressure plan');
 g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8).slice(0,3).forEach(c=>c.Move(2,512,0));
 add(g,132201,8,0);add(g,132305,8,1);g.archetypeAI.Refresh();g.archetypeAI.PlanTurn(model);
 check(g.archetypeAI.roundPlan===1,'engine-heavy remaining hand cancels an earlier pressure plan');
}
if(typeof BetaGwentAIReplyCards==='function'){
 check(BetaGwentAIReplyCards(25,25,0)===2,'strict lead requires a second reply at equality');
 check(BetaGwentAIReplyCards(24,25,0)===1,'one point below the boundary still takes one reply');
 check(BetaGwentAIReplyCards(25,25,20)===1,'available leader can replace hand tempo');
 check(BetaGwentAIPressureDiscount(24,20,30,0)>BetaGwentAIPressureDiscount(24,9,30,0),'overkill within the same reply bracket is discounted');
 check(!BetaGwentAIInvestmentPass(3,1,1,-20,5,5,true,3,10,10),'no concession in a deciding round');
 check(!BetaGwentAIInvestmentPass(1,0,0,-20,5,5,true,3,10,24),'valuable engine continuation vetoes estimated concession');
}
// The next-round plan must depend on our hand, not the archetype label.
if(typeof CBetaGwentArchetypeAI.prototype.FinalNeedsLongRound==='function'){
 for(const preset of JSON.parse(manifestText).presets)for(const engines of [false,true]){
  const g=blank(preset,2);hand(g,1,4);
  if(engines){add(g,132201,8,0);add(g,132305,8,1);hand(g,2,4,10);}else hand(g,2,6,10);
  g.archetypeAI.Refresh();const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);g.archetypeAI.PlanTurn(model);
  check(g.archetypeAI.FinalNeedsLongRound()===engines,'hand-based final length across archetypes '+preset+'/'+engines);
  check(g.archetypeAI.roundPlan===(engines?1:2),'hand-based pressure plan across archetypes '+preset+'/'+engines);
 }
}
globalThis.report={checks,failures,cases,actualWitcherScript:true,nativeGameTested:false,observedBaseline:observe};
`,context,{filename:'round-economy093.bundle.js',timeout:180000});
if(out)fs.writeFileSync(out,JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,failures:context.report.failures.length}));
if(context.report.failures.length)process.exitCode=1;

// 0.9.2 class-level AI rules (22 Oct 2026): one pass guard for every pass reason, deck/grave
// plays keep archetype gains, own pending timers count against a pass, Scorch exposure of
// boosts, and conceding a hopeless first round that would burn held finishers.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const cases=[];function side(c){return c.Snapshot().positionPlayerId;}function loc(c){return c.Snapshot().locationMask;}
function position(strength,preset,leader,round,enemyCrowns,ownCrowns,enemyList){
 Host.strength=strength;const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=preset;g.archetypeAI.Initialize(g,[],preset,leader);
 g.match.roundNumber=round;g.match.playerOne.crowns=enemyCrowns;g.match.playerTwo.crowns=ownCrowns;
 const l=g.Leader(2);if(l)l.Move(2,512,0);(enemyList||[]).forEach(t=>g.aiStartingDeckOne.PushBack(t));g.archetypeAI.Refresh();return g;}
// 1) The pass guard replaces any conceding pass by a legal play.
for(const strength of [2,4]){
 const g=position(strength,56,201743,3,1,1);add(g,112101,1,0,1,20);add(g,112101,1,0,2,10);const card=add(g,112101,8,0,2,3);
 for(let i=0;i<3;i++)add(g,112101,8,i,1,4);
 check(g.AiPassConcedesMatch(),'behind in the deciding round: a pass concedes '+strength);
 check(g.AiExplainedPass('test')&&!g.match.playerTwo.hasPassed&&(loc(card)&7)!==0,'any pass reason is replaced by the legal play '+strength);
}
{
 const g=position(4,56,201743,3,1,1);add(g,112101,1,0,1,10);add(g,112101,1,0,2,20);add(g,112101,8,0,2,3);add(g,112101,8,0,1,4);
 check(!g.AiPassConcedesMatch()&&g.AiExplainedPass('test')&&g.match.playerTwo.hasPassed,'ahead: a pass is still allowed');
}
{
 const g=position(4,56,201743,1,0,0);add(g,112101,1,0,1,20);add(g,112101,8,0,2,3);add(g,112101,8,0,1,4);
 check(!g.AiPassConcedesMatch()&&g.AiExplainedPass('test')&&g.match.playerTwo.hasPassed,'an optional round may still be conceded');
}
{
 const g=position(4,56,201743,2,1,0);add(g,112101,1,0,1,10);add(g,112101,1,0,2,10);add(g,112101,8,0,1,4);
 check(g.AiPassConcedesMatch(),'a tie without our crown also concedes after the opponent took round one');
}
// The guard never forces an illegal play: a lone Decoy without a target still passes
// (arena 22 Oct: Slave Infantry vs 90, the forced Decoy was rejected and stalled the match).
for(const strength of [2,4]){
 const g=position(strength,87,200164,2,1,0);g.match.playerOne.hasPassed=true;
 add(g,142305,1,0,1,9);const decoy=add(g,113201,8,0,2);
 check(g.AiPassConcedesMatch(),'decoy case: the pass concedes '+strength);
 const ok=g.OpponentStep();
 check(ok&&!g.IsFatal()&&!g.IsPending()&&g.match.playerTwo.hasPassed&&loc(decoy)===8,'no legal play: the AI passes instead of stalling '+strength);
}
// 2) A resurrector pulled from the deck keeps its grave payoff, as when played from hand.
{
 const g=position(4,93,200166,1,0,0),eyvar=add(g,200520,16,0,2);const d=eyvar.Definition();
 const before=g.AiPileCandidateValue(eyvar,2,false,0);add(g,142316,32,0,2,3);g.archetypeAI.Refresh();
 const gain=g.archetypeAI.PileGain(d,false),after=g.AiPileCandidateValue(eyvar,2,false,0);
 check(gain>0&&after-before>=gain,'deck play of Eyvar counts his resurrection target ('+before+'->'+after+', gain '+gain+')');
}
// 3) Own pending timers count against a pass only when that pass ends the round
// (the opponent has passed). While the opponent still plays, our timers keep firing.
{
 const g=position(4,56,201743,2,0,0),vran=add(g,132308,1,0,2,6);vran.cardState.timerValue=1;
 check(g.AiOwnTimerGain(1)===0,'opponent still playing: our timers keep working after a pass');
 g.match.playerOne.hasPassed=true;
 check(g.AiOwnTimerGain(1)>0,'opponent passed: our pass ends the round and forfeits a one-tick timer');
 vran.cardState.timerValue=3;check(g.AiOwnTimerGain(1)===0,'a timer beyond the reachable turn starts is not counted');
 check(g.AiOwnTimerGain(3)>0,'more hand cards reach more turn starts');
}
// The engine fact behind the rule: after our pass our Vran still consumes on the opponent's turn.
{
 const g=fixture(),vran=add(g,132308,1,0,2,6);add(g,142305,1,1,2,3);vran.cardState.timerValue=1;
 g.match.currentPlayerId=2;check(g.Pass(2),'AI passes');
 const e=g.live.find(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8);g.match.currentPlayerId=1;
 check(g.Play(1,e.cardState.instanceId,2)&&vran.Snapshot().power.currentPower>6,'our timer fires during the opponent turn after our pass');
}
// 4) Scorch exposure: do not create the board's strongest non-gold unit while Scorch is possible.
{
 const g=position(4,84,200167,2,0,0,[113309,112101]);add(g,112101,1,0,1,12);
 const tall=add(g,142305,1,1,2,10),small=add(g,142305,2,0,2,2);add(g,112101,8,0,1,3);
 check(g.TargetValue(tall.Snapshot(),2,2,7)<g.TargetValue(small.Snapshot(),2,2,7),'boosting into the strongest unit is worse while Scorch is possible');
 const h=position(4,84,200167,2,0,0,[112101,112101]);add(h,112101,1,0,1,12);const t2=add(h,142305,1,1,2,10);add(h,112101,8,0,1,3);
 check(h.TargetValue(t2.Snapshot(),2,2,7)===7,'no Scorch in the known list: full value');
 // Scorch burns gold too: a gold unit pushed to the top is just as exposed.
 const k=position(4,84,200167,2,0,0,[113309,112101]);add(k,142305,1,0,1,12);
 const gold=add(k,112101,1,1,2,10),low=add(k,142305,2,0,2,2);add(k,112101,8,0,1,3);
 check(k.TargetValue(gold.Snapshot(),2,2,7)<k.TargetValue(low.Snapshot(),2,2,7),'a gold unit made the strongest is exposed to Scorch as well');
 // A face-down ambush is not a Scorch target, so it does not raise the bar.
 const am=add(k,142307,1,2,1,30);am.AddTokens(8);
 check(k.TargetValue(gold.Snapshot(),2,2,7)<k.TargetValue(low.Snapshot(),2,2,7),'a hidden ambush does not shield the strongest unit');
}
// 5) A hopeless first round does not burn held finishers.
for(const strength of [2,3,4]){
 const g=position(strength,56,201743,1,0,0);add(g,112101,1,0,1,40);add(g,112101,1,0,2,10);
 // The whole hand could catch up (Mourntart eats eight grave units, two 11-power Sappers),
 // but no single play retakes the lead: keep the finisher and the card count.
 const hand=[add(g,132202,8,0,2),add(g,142307,8,1,2),add(g,142307,8,2,2)];
 for(let i=0;i<3;i++)add(g,112101,8,i,1,6);for(let i=0;i<8;i++)add(g,132304,32,i,2,1);g.archetypeAI.Refresh();
 const logs=[];Host.log=s=>logs.push(s);g.OpponentStep();Host.log=null;
 cases.push({label:'concede '+strength,selected:(logs.find(s=>s.includes('event=PASS'))||logs.find(s=>s.includes('event=SELECT'))||'').slice(0,140)});
 check(g.match.playerTwo.hasPassed&&hand.every(c=>loc(c)===8),'hopeless round one is conceded with the finisher kept '+strength);
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'ai-classes092.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases},null,1));

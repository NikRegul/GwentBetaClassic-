// 0.9.1b playtest logs (20 Oct 2026):
// 1) round 3, 12:20, last card Pugach: AI passed (every_play_loses_points) and conceded the match;
// 2) Nekkers & Consume: Forktail ate both Nekkers before Nekker Warrior seeded deck copies;
// 3) round-2 mulligan returned the held finisher Mourntart to the deck;
// 4) Double Cross was rejected although it pulls Pugach under a pending Miruna;
// 5) an empty Slyzard (no bronze grave unit with a deck copy) was dumped in a lost first round.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const PUGACH=132204,MOURNTART=132202,NEKKER=132305,WARRIOR=132211,FORKTAIL=201606,VRAN=132308,cases=[];
function side(c){return c.Snapshot().positionPlayerId;}function loc(c){return c.Snapshot().locationMask;}
function position(strength,preset,leaderId,round,enemyCrowns,ownCrowns){
 Host.strength=strength;const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=preset;
 g.archetypeAI.Initialize(g,[],preset,leaderId);
 g.match.roundNumber=round;g.match.playerOne.crowns=enemyCrowns;g.match.playerTwo.crowns=ownCrowns;
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 return g;
}
function decide(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'AI turn completes '+label);
 const r={label,selected:logs.find(s=>s.includes('event=SELECT'))||logs.find(s=>s.includes('event=PASS'))||'',keep:logs.filter(s=>s.includes('DUEL_AI_KEEP')).join(' ')};
 cases.push(r);return r;}
// 1) Decisive round, behind, the last card loses points now but keeps the match alive.
function lastSpy(strength,round,enemyCrowns,ownCrowns,ownPower){
 const g=position(strength,56,201743,round,enemyCrowns,ownCrowns);
 add(g,NEKKER,1,0,2,ownPower);add(g,142106,2,0,1,20);add(g,201704,8,0,1);
 const pugach=add(g,PUGACH,8,0);
 const mourntart=add(g,MOURNTART,16,0);add(g,132304,16,1);add(g,200539,16,2);
 for(let i=0;i<9;i++)add(g,i%2?132308:132305,32,i,2,1);
 return {g,pugach,mourntart};
}
for(const strength of [2,3,4])for(const [round,enemyCrowns,ownCrowns] of [[3,1,1],[2,1,0]]){
 const label='concede '+strength+'/r'+round,{g,pugach}=lastSpy(strength,round,enemyCrowns,ownCrowns,12);
 const r=decide(g,label);
 check(!g.match.playerTwo.hasPassed,'AI does not pass away the match '+label);
 check(side(pugach)===1&&(loc(pugach)&7)!==0,'last card Pugach is played '+label);
}
// Ahead in the decisive round the old rule still saves points: no forced harmful play.
{
 const {g,pugach}=lastSpy(4,3,1,1,30),r=decide(g,'ahead decisive');
 check(loc(pugach)===8,'ahead in the decisive round, Pugach is kept '+r.selected.slice(0,60));
}
// 2) Nekker Warrior seeds deck copies before an own consumer eats the board Nekker.
function nekkers(strength,round,hand){
 const g=position(strength,67,201743,round,0,0);
 const nekker=add(g,NEKKER,1,0,2,1);add(g,142308,1,0,1,10);
 const deck=[add(g,NEKKER,16,0,2,4),add(g,NEKKER,16,1,2,4)];add(g,132304,16,2);add(g,200539,16,3);
 const cards={};hand.forEach((t,i)=>cards[t]=add(g,t,8,i));
 for(let i=0;i<8;i++)add(g,112101,8,i,1,5);
 g.archetypeAI.Refresh();
 return {g,nekker,deck,cards};
}
for(const strength of [2,3,4]){
 const label='seed '+strength,{g,cards}=nekkers(strength,1,[FORKTAIL,WARRIOR,VRAN,201776,113209,200221]);
 const before=g.live.filter(c=>side(c)===2&&loc(c)===16&&c.TemplateId()===NEKKER).length;
 decide(g,label);
 check(loc(cards[FORKTAIL])===8&&loc(cards[VRAN])===8,'own consumers wait for Nekker Warrior '+label);
 check((loc(cards[WARRIOR])&7)!==0,'Nekker Warrior is played first '+label);
 const after=g.live.filter(c=>side(c)===2&&loc(c)===16&&c.TemplateId()===NEKKER).length;
 check(after===before+2,'Nekker Warrior copies the Nekker into the deck '+label+' ('+before+'->'+after+')');
}
// Without Nekker Warrior in hand consumers are not delayed by this rule.
{
 const {g}=nekkers(4,1,[FORKTAIL,201776]);const d=BetaGwentDuelDefinition(FORKTAIL);
 const {g:h}=nekkers(4,1,[FORKTAIL,WARRIOR,201776]);
 check(g.archetypeAI.Priority(d)-h.archetypeAI.Priority(d)===8,'the consumer delay applies only while Nekker Warrior can seed');
}
// 3) Between rounds the held finisher stays in hand; the mulligan swaps something else.
for(const strength of [3,4]){
 const g=position(strength,56,201743,2,1,0);
 const hand=[NEKKER,132108,NEKKER,MOURNTART,VRAN,133302].map((t,i)=>add(g,t,8,i));
 [122107,132107,132201,132201,200091,113209,132304].forEach((t,i)=>add(g,t,16,i));
 for(let i=0;i<10;i++)add(g,132305,32,i,2,1);
 g.AiMulligan(1);
 check(loc(hand[3])===8,'mulligan keeps Mourntart in hand '+strength);
 check(!g.IsFatal(),'mulligan completes '+strength);
}
// 4) Double Cross pulls Pugach from the deck under our pending Miruna and the charm returns him.
for(const strength of [2,4])for(const timer of [1,2])for(const stregobor of [false,true]){
 const label='cross '+strength+'/t'+timer+'/stregobor='+stregobor;let g=position(strength,56,201743,2,1,0);
 const miruna=add(g,132108,2,0,2);miruna.cardState.timerValue=timer;
 add(g,NEKKER,1,0,2,6);add(g,113209,1,0,1,10);
 const cross=add(g,113209,8,0);add(g,NEKKER,8,1);
 const alternative=stregobor?add(g,200091,8,2):add(g,112405,8,2,2,3);
 let pugach=add(g,PUGACH,16,0);add(g,132304,16,1);add(g,132304,16,2);
 for(let i=0;i<4;i++)add(g,112101,8,i,1,6);
 const direct=g.AiSimClone();decide(g,label);
 if(loc(cross)!==32){
  check(stregobor&&(loc(alternative)&7)!==0&&loc(pugach)===8&&pugach.Snapshot().power.currentPower===1,'alternative must really draw a one-power Pugach '+label);
  direct.archetypeAI.Refresh();
  check(direct.AiSimPlay(cross.Snapshot().instanceId)!==-2147483647,'direct tutor combo still resolves '+label);
  g=direct;pugach=g.FindCard(pugach.Snapshot().instanceId);
 }
 check(side(pugach)===1&&loc(pugach)===2,'Double Cross plays Pugach opposite Miruna '+label);
 for(let k=0;k<timer;k++){g.match.currentPlayerId=1;const o=g.live.find(c=>side(c)===1&&loc(c)===8);check(g.Play(1,o.cardState.instanceId,4),'opponent replies '+label);
  if(k<timer-1){g.match.currentPlayerId=2;decide(g,label+' wait');}}
 check(side(pugach)===2&&loc(pugach)===2,'the charm returns the pulled Pugach '+label);
}
// 5) A lost optional round with only held cards and a targetless Slyzard: pass, keep the hand.
// A live Miruna is deliberately absent: her real eighty-point charm in this board
// is a profitable continuation, covered independently in check_pending_charm092.
function slyzard(strength,graveCopy){
 const g=position(strength,56,201743,1,0,0);
 add(g,112101,1,0,2,40);add(g,112101,2,0,2,30);add(g,112101,1,0,1,40);add(g,112101,2,0,1,32);
 add(g,132201,32,0,2);add(g,122107,32,1,2);if(graveCopy)add(g,132304,32,2,2);
 const hand=[NEKKER,200539,200539,113209].map((t,i)=>add(g,t,8,i));
 add(g,PUGACH,16,0);add(g,132107,16,1);add(g,122107,16,2);if(graveCopy)add(g,132304,16,3);
 for(let i=0;i<4;i++)add(g,112101,8,i,1,6);
 g.archetypeAI.Refresh();return {g,hand};
}
for(const strength of [2,3,4]){
 const {g,hand}=slyzard(strength,false),d=BetaGwentDuelDefinition(200539);
 check(!g.archetypeAI.SlyzardHasTarget(d),'Slyzard sees no bronze grave unit with a deck copy '+strength);
 decide(g,'slyzard '+strength);
 check(hand.every(c=>loc(c)===8),'no empty Slyzard or held card is dumped '+strength);
 check(g.match.playerTwo.hasPassed,'the lost optional round is conceded with the full hand '+strength);
}
{
 const {g}=slyzard(4,true),d=BetaGwentDuelDefinition(200539);
 check(g.archetypeAI.SlyzardHasTarget(d),'a bronze grave unit with a deck copy is a real Slyzard target');
 const {g:h}=slyzard(4,false);
 check(g.archetypeAI.Priority(d)-h.archetypeAI.Priority(d)===12,'only a targetless Slyzard is penalised');
}
// Pugach goes under a waiting Miruna only when he, not her current target, is the one charmed.
for(const [target,expected] of [[3,true],[16,false]]){
 const g=position(4,56,201743,2,1,0),miruna=add(g,132108,2,0,2);miruna.cardState.timerValue=2;
 add(g,112101,2,0,1,target);add(g,NEKKER,1,0,2,6);
 const pugach=add(g,PUGACH,8,0);add(g,NEKKER,8,1);add(g,200091,8,2);
 // A weak deck keeps the spy draw from deciding: only the charm matters here.
 for(let i=0;i<5;i++)add(g,112101,16,i,2,1);for(let i=0;i<4;i++)add(g,112101,8,i,1,6);
 g.archetypeAI.Refresh();const pd=BetaGwentDuelDefinition(PUGACH),ret=g.archetypeAI.MirunaSpyReturn(pd);
 check((ret>0)===expected,'Miruna return for Pugach against a '+target+'-power target '+ret);
 cases.push({label:'priority '+target,selected:'priority='+g.archetypeAI.Priority(pd)+' return='+ret,keep:''});
 if(!expected)check(g.archetypeAI.Priority(pd)<=0,'no Miruna ordering bonus when a stronger target will be charmed');
 decide(g,'target '+target);
 check((side(pugach)===1&&loc(pugach)===2)===expected,'Pugach under Miruna against a '+target+'-power target: '+expected);
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'playtest091b.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases.map(c=>c.label+': '+c.selected.replace(/AI_REASON schema=1 /,'').slice(0,120)+(c.keep?' | '+c.keep.slice(0,90):''))},null,1));

// Reported round-3 Miruna opening: no charm target, then Dandelion over a held Pugach.
// Miruna opens on an empty board only as the Miruna -> Pugach combo.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const MIRUNA=132108,PUGACH=132204,POET=201776,NEKKER=132305,DROWNER=132308,cases=[];
// Swarm profile (preset 56), decisive third round, empty board, AI to move.
function position(strength){
 Host.strength=strength;const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=56;
 g.archetypeAI.Initialize(g,[],56,201743);
 g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 for(let i=0;i<4;i++)add(g,132304,16,i);
 for(let i=0;i<7;i++)add(g,112101,8,i,1,6+i);
 return g;
}
function loc(c){return c.Snapshot().locationMask;}
function side(c){return c.Snapshot().positionPlayerId;}
function decide(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'AI turn completes '+label);
 cases.push({label,selected:logs.find(s=>s.includes('event=SELECT'))||logs.find(s=>s.includes('event=PASS'))||''});}
function opponentPlays(g,power,row){g.match.currentPlayerId=1;
 const c=g.live.find(x=>side(x)===1&&loc(x)===8&&x.Snapshot().power.currentPower===power);
 check(g.Play(1,c.cardState.instanceId,row),'opponent plays '+power+' into row '+row);g.match.currentPlayerId=2;return c;}
// Without Pugach there is nothing to charm yet: hold Miruna until a target appears.
for(const strength of [2,4])for(const [extra,targetRow] of [[[],1],[[NEKKER],2],[[NEKKER,DROWNER],4]]){
 const label=strength+'/'+extra.length+'/'+targetRow,g=position(strength);
 const miruna=add(g,MIRUNA,8,0);add(g,POET,8,1);add(g,132201,8,2);extra.forEach((t,i)=>add(g,t,8,3+i));
 decide(g,'open '+label);
 check(loc(miruna)===8,'Miruna is not opened against an empty board '+label);
 opponentPlays(g,10,targetRow);
 check(g.AiBestMirunaRow(2,miruna.Definition())===targetRow,'row choice follows the only charm target '+label);
 decide(g,'answer '+label);
 if(extra.length<2)check(loc(miruna)===targetRow,'Miruna is placed opposite the charm target '+label);
 else check(loc(miruna)===targetRow||loc(miruna)===8,'Miruna is never placed away from the charm target '+label);
}
// With Pugach in hand the empty-board opening is the deck combo: Miruna now, Pugach next turn.
// An empty deck keeps Dandelion from drawing a stronger opener, so the combo itself is measured.
function combo(g,label,miruna,pugach,poet){
 const row=loc(miruna);
 check((row&7)!==0&&side(miruna)===2&&loc(pugach)===8&&loc(poet)===8,'Miruna opens the combo alone '+label);
 opponentPlays(g,10,row===1?2:1);
 decide(g,'combo prepare '+label);
 check(side(pugach)===1&&loc(pugach)===row,'Pugach is sent opposite Miruna (directly or through Dandelion) '+label);
 opponentPlays(g,6,4);
 check(side(pugach)===2&&loc(pugach)===row,'the charm returns Pugach to the AI '+label);
}
for(const strength of [2,4])for(const extra of [[NEKKER],[NEKKER,DROWNER]]){
 const label=strength+'/'+extra.length,g=position(strength);
 g.live.filter(c=>side(c)===2&&loc(c)===16).forEach(c=>c.Move(2,512,0));
 g.live.filter(c=>side(c)===1&&loc(c)===8&&c.Snapshot().power.currentPower>10).forEach(c=>c.Move(1,512,0));
 const miruna=add(g,MIRUNA,8,0),pugach=add(g,PUGACH,8,1),poet=add(g,POET,8,2);extra.forEach((t,i)=>add(g,t,8,3+i));
 decide(g,'combo open '+label);combo(g,label,miruna,pugach,poet);
}
// With a full deck the strong AI may open with Dandelion instead; once Miruna lands
// against an empty row, Pugach (not a held Dandelion or other card) must follow.
for(const strength of [2,4]){
 const label='deck '+strength,g=position(strength);
 const miruna=add(g,MIRUNA,8,0),pugach=add(g,PUGACH,8,1),poet=add(g,POET,8,2);
 decide(g,'deck open '+label);
 check(loc(pugach)===8,'Pugach is never spent before Miruna '+label);
 if(loc(miruna)!==8){
  const row=loc(miruna);opponentPlays(g,10,row===1?2:1);decide(g,'deck prepare '+label);
  check(side(pugach)===1&&loc(pugach)===row,'opened Miruna is followed by Pugach '+label);
 }
}
// Miruna already waits opposite an empty row: Pugach is the prepared target, not Dandelion.
for(const strength of [2,4])for(const timer of [2,1]){
 const label=strength+'/t'+timer,g=position(strength),miruna=add(g,MIRUNA,1,0,2);miruna.cardState.timerValue=timer;
 const pugach=add(g,PUGACH,8,0),poet=add(g,POET,8,1);add(g,NEKKER,8,2);add(g,112101,2,0,1,7);
 decide(g,'prepare '+label);
 check(side(pugach)===1&&loc(pugach)===1,'Pugach is sent into the row opposite Miruna '+label);
 check(loc(poet)===8,'Dandelion is held while Pugach prepares the charm '+label);
 opponentPlays(g,6,4);
 if(timer===1)check(side(pugach)===2&&loc(pugach)===1,'the charm returns Pugach to the AI '+label);
 else check(miruna.Snapshot().timerValue===1&&side(pugach)===1,'charm still pending after one tick '+label);
}
// Row capacity: Miruna and the charmed unit need two free slots in her row.
{
 const g=position(4),miruna=add(g,MIRUNA,8,0);for(let i=0;i<8;i++)add(g,NEKKER,1,i,2,1);
 add(g,112101,1,0,1,12);add(g,112101,2,0,1,7);
 check(g.AiBestMirunaRow(2,miruna.Definition())===2,'full own melee skips the stronger melee target');
 check(g.AiMirunaTargetPower(2,1)===12&&g.AiMirunaTargetPower(2,2)===7&&g.AiMirunaTargetPower(2,4)===0,'target power reads only public opposing units');
}
// The no-target penalty is a cost, never a prohibition: a last card is still played.
{
 const g=position(4);g.live.filter(c=>side(c)===2&&loc(c)===16).forEach(c=>c.Move(2,512,0));
 const miruna=add(g,MIRUNA,8,0);add(g,112101,1,0,1,3);
 decide(g,'last card');
 check(loc(miruna)!==8&&!g.match.playerTwo.hasPassed,'lone Miruna is still played in the decisive round');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'miruna-timing091.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases.map(c=>c.label+': '+c.selected.replace(/AI_REASON schema=1 /,'').slice(0,140))},null,1));

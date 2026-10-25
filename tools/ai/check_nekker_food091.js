// Reported round-2 must-win position (log decision 16): Vran-warrior ate a 3-power
// Young Glaveeye instead of a board Nekker whose deathwish summons a 12-power deck copy.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const VRAN=132308,NEKKER=132305,YOUNG=200174,SLIME=200539,cases=[];
function side(c){return c.Snapshot().positionPlayerId;}function loc(c){return c.Snapshot().locationMask;}
// decisive: enemy holds a crown in round 2; otherwise an open first round.
function position(strength,decisive,deckCopies=2){
 Host.strength=strength;const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=56;
 g.archetypeAI.Initialize(g,[],56,201743);
 g.match.roundNumber=decisive?2:1;g.match.playerOne.crowns=decisive?1:0;g.match.playerTwo.crowns=0;
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 // Board: melee 6/7/7 then the Nekker last; ranged 4 then a Young Glaveeye chain.
 add(g,112101,1,0,2,6);add(g,112101,1,1,2,7);add(g,112101,1,2,2,7);
 const nekker=add(g,NEKKER,1,3,2,5);
 add(g,112101,2,0,2,4);const young=add(g,YOUNG,2,1,2,3);add(g,YOUNG,2,2,2,3);
 const copies=[];for(let i=0;i<deckCopies;i++)copies.push(add(g,NEKKER,16,i,2,12));
 add(g,132304,16,deckCopies);
 const vran=add(g,VRAN,8,0),slime=add(g,SLIME,8,1);
 add(g,112101,1,0,1,30);add(g,112101,2,0,1,22);add(g,112101,4,0,1,20);add(g,112101,8,0,1,8);
 g.archetypeAI.Refresh();
 return {g,nekker,young,copies,vran,slime};
}
function decide(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'AI turn completes '+label);
 cases.push({label,selected:logs.find(s=>s.includes('event=SELECT'))||'',consume:logs.filter(s=>s.includes('DUEL_VRAN_CONSUME')).join(' ')});}
for(const strength of [2,3,4]){
 const label='decisive '+strength,{g,nekker,young,copies,vran}=position(strength,true),before=g.Score(2);
 check(g.archetypeAI.FoodPenalty(nekker.Snapshot())===0,'no Nekker food penalty in a deciding round with a deck copy '+label);
 check(g.BestVranAnchor(2)===nekker.cardState.instanceId,'Vran anchors on the board Nekker '+label);
 decide(g,label);
 check((loc(vran)&7)!==0,'Vran is played '+label);
 check(loc(vran)===1&&loc(nekker)!==1,'Vran eats the Nekker to its right '+label);
 check(copies.some(c=>loc(c)===1),'Nekker deathwish summons its deck copy into melee '+label);
 check(loc(young)===2,'Young Glaveeye is kept '+label);
 check(g.Score(2)-before>=15,'the Nekker line gains at least fifteen points '+label+' ('+(g.Score(2)-before)+')');
}
// Early rounds keep the author line: Nekkers are finishers and are not eaten.
for(const strength of [2,4]){
 const {g,nekker}=position(strength,false);
 check(g.archetypeAI.FoodPenalty(nekker.Snapshot())===10,'open round keeps the Nekker food penalty '+strength);
 check(g.BestVranAnchor(2)!==nekker.cardState.instanceId,'open round does not anchor Vran on the Nekker '+strength);
}
// Without a deck copy the Nekker summons nothing: the penalty stays.
{
 const {g,nekker}=position(4,true,0);
 check(g.archetypeAI.FoodPenalty(nekker.Snapshot())===10,'no deck copy keeps the Nekker food penalty');
}
// Hand and deck Nekkers are not food at all; the exemption is board-only.
{
 const {g,copies}=position(4,true);
 check(g.archetypeAI.FoodPenalty(copies[0].Snapshot())===10,'deck Nekker is not exempted');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'nekker-food091.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases.map(c=>c.label+': '+c.selected.replace(/AI_REASON schema=1 /,'').slice(0,110)+' | '+c.consume)},null,1));

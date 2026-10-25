// 0.9.1c playtest log (20 Oct 2026): round 3, 13:18, the opponent's hand is empty, Miruna waits
// with one tick and the AI holds only Double Cross (pulls Pugach). The AI rejected Double Cross
// and passed: Miruna's return was zeroed whenever the opponent had no cards or had passed.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const PUGACH=132204,MIRUNA=132108,CROSS=113209,cases=[];
function side(c){return c.Snapshot().positionPlayerId;}function loc(c){return c.Snapshot().locationMask;}
function position(strength,timer,enemyPassed,extraHand){
 Host.strength=strength;const g=fixture();
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=56;
 g.archetypeAI.Initialize(g,[],56,201743);
 g.match.roundNumber=3;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=enemyPassed;
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 add(g,133302,1,0,2,9);const miruna=add(g,MIRUNA,2,0,2);miruna.cardState.timerValue=timer;
 add(g,112101,1,0,1,18);
 const cross=add(g,CROSS,8,0);const extra=extraHand?add(g,112101,8,1,2,2):null;
 const pugach=add(g,PUGACH,16,0);add(g,112101,16,1,2,1);add(g,112101,16,2,2,1);
 g.archetypeAI.Refresh();return {g,miruna,cross,pugach,extra};
}
function decide(g,label){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'AI turn completes '+label);
 const r=logs.find(s=>s.includes('event=SELECT'))||logs.find(s=>s.includes('event=PASS'))||'';cases.push({label,selected:r});return r;}
for(const strength of [2,3,4])for(const enemyPassed of [false,true]){
 const label=strength+(enemyPassed?'/passed':'/empty'),{g,cross,pugach,miruna}=position(strength,1,enemyPassed,false);
 check(g.archetypeAI.MirunaSpyReturn(BetaGwentDuelDefinition(PUGACH))>0,'Miruna return counts with an empty or passed enemy hand '+label);
 decide(g,label);
 check(!g.match.playerTwo.hasPassed&&loc(cross)===32,'Double Cross is played instead of a conceding pass '+label);
 check(side(pugach)===1&&loc(pugach)===2,'Pugach lands opposite Miruna '+label);
 if(!enemyPassed){g.match.currentPlayerId=1;check(g.Pass(1),'the empty-handed opponent passes '+label);}
 // Our next turn start fires the charm (Pugach may first pull a stronger enemy unit into the row).
 check(miruna.Snapshot().timerValue===0,'Miruna resolved at our turn start '+label);
 check(g.live.filter(c=>side(c)===2&&(loc(c)&2)!==0&&c!==miruna).length>0,'a unit opposite Miruna was charmed to our side '+label);
 check(g.Score(2)>g.Score(1),'the AI is now ahead '+label+' '+g.Score(2)+':'+g.Score(1));
}
// Timer 2 with no second card: the charm cannot fire in time, so no return is counted,
// but the last card is still played because the pass would concede the match.
{
 const {g,cross}=position(4,2,false,false);
 check(g.archetypeAI.MirunaSpyReturn(BetaGwentDuelDefinition(PUGACH))===0,'two ticks with one card left: no return');
 decide(g,'timer2');
 check(loc(cross)===32,'the last card is still played in a conceding position');
}
// Timer 2 with one more card in hand: two turn starts are reachable, the return counts.
{
 const {g}=position(4,2,false,true);
 check(g.archetypeAI.MirunaSpyReturn(BetaGwentDuelDefinition(PUGACH))>0,'two ticks with two cards: return counts');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'playtest091c.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases.map(c=>c.label+': '+c.selected.replace(/AI_REASON schema=1 /,'').slice(0,120))},null,1));

// Public pass outcomes, deciding-round resources, and concrete discard setups.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const decisions=[];
function clear(g,side=2){g.live.filter(c=>c.Snapshot().positionPlayerId===side&&c.Snapshot().locationMask===8).forEach(c=>c.Move(side,512,0));}
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 Host.strength=strength;
 const g=fixture();clear(g);g.aiSimDamp=damp;g.match.roundNumber=3;
 g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.match.playerOne.hasPassed=true;
 add(g,112101,1,0,1,5);const ciri=add(g,162212,1,0,1,8);ciri.Move(2,1,0);ciri.AddTokens(128);
 const body=add(g,112101,8,0,2,16),before=g.random.DrawCount();
 check(g.Score(2)>g.Score(1),'misleading current lead');
 const passing=g.AiSimClone();passing.Pass(2);
 check(passing.Snapshot().matchWinnerMask===1,'passing really loses the match');
 const lead=g.AiPublicPassLead();check(lead===-13,'projected public pass includes relocation');
 check(ciri.Snapshot().positionPlayerId===2&&g.random.DrawCount()===before&&!g.match.playerTwo.hasPassed,'public projection leaves live match and RNG unchanged');
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'chase completes');Host.log=null;
 check(body.Snapshot().locationMask!==8&&!g.IsFatal()&&!g.IsPending(),'play the sufficient answer rather than concede');
 g.match.currentPlayerId=2;g.match.turnActive=true;check(g.Pass(2),'finish after answer');
 check(g.Snapshot().matchWinnerMask===2,'answer wins after the actual pass reaction');
 decisions.push({case:'false-ciri-pass',strength,damp,logs:logs.filter(s=>/event=(CHASE|SELECT|PASS)/.test(s))});
}
// The live report had Yaevinn and an unused Eithne. This synthetic board tests
// that resource horizon, rather than claiming to reconstruct its missing board.
for(const round of [2,3])for(const strength of [2,3,4]){
 Host.strength=strength;const g=fixture();clear(g);g.match.roundNumber=round;g.match.playerOne.crowns=1;
 add(g,112101,1,0,1,20);add(g,112101,1,0,2,15);
 const spy=add(g,142203,8),leader=add(g,200166,64),logs=[];g.leaderTemplateTwo=200166;Host.log=s=>logs.push(s);
 check(g.OpponentStep(),'deciding-round action completes');Host.log=null;
 check(leader.Snapshot().locationMask!==64&&!g.match.playerTwo.hasPassed,'use positive leader before giving up');
 check(spy.Snapshot().locationMask===8&&!g.IsFatal()&&!g.IsPending(),'negative spy does not displace useful leader');
 decisions.push({case:'eithne-before-pass',round,strength,logs:logs.filter(s=>/event=(LEADER_OPTION|SELECT|PASS)/.test(s))});
}
Host.strength=4;
// A public Miruna steals the same 25-point unit after a play OR a pass.
// The play's negative absolute tempo still improves on the resolved pass.
for(const strength of [2,3,4])for(const damp of [0,40,70]){
 Host.strength=strength;const g=fixture();clear(g);clear(g,1);g.aiSimDamp=damp;g.match.roundNumber=2;g.match.playerOne.crowns=1;
 for(let i=0;i<2;i++)add(g,112101,8,i,1);
 add(g,112101,2,0,1,59);const miruna=add(g,132108,1,0,1,4);miruna.ChangeTimer(1,2);
 add(g,112101,2,0,2,73);const victim=add(g,162210,1,0,1,25);victim.Move(2,1,0);victim.AddTokens(128);
 const first=add(g,201610,8),second=add(g,201610,8),ointment=add(g,201619,8);
 const draws=g.random.DrawCount(),baselineLead=g.Score(2)-g.Score(1),passLead=g.AiPublicPassLead(true),exact=g.AiExactTempo(first);
 check(baselineLead===35&&passLead===-15,'public timer overturns the apparent 98:63 lead');
 check(exact<0&&exact>passLead-baselineLead,'playing infantry loses fewer points than passing');
 check(victim.Snapshot().positionPlayerId===2&&miruna.Snapshot().timerValue===1&&g.random.DrawCount()===draws,'timer projections do not mutate live ownership, timers or RNG');
 const logs=[];Host.log=s=>logs.push(s);check(g.OpponentStep(),'Miruna decision completes');Host.log=null;
 check(!g.match.playerTwo.hasPassed&&[first,second].some(c=>(c.Snapshot().locationMask&7)!==0),'continue the deciding round despite negative absolute tempo');
 check(ointment.Snapshot().locationMask===8&&!g.IsFatal()&&!g.IsPending(),'empty resurrection is not mistaken for a useful alternative');
 decisions.push({case:'miruna-unavoidable-turn-loss',strength,damp,baselineLead,passLead,exact,logs:logs.filter(s=>/event=(SELECT|PASS)/.test(s))});
}
Host.strength=4;
for(const crowns of [0,1])for(const round of [1,2,3]){
 const g=fixture();g.match.roundNumber=round;g.match.playerOne.crowns=crowns;const gold=add(g,112101,8);
 check((g.AiReserveCost(gold.Definition())===0)===(round===3||crowns===1),'rare-card reserve follows match survival');
 const baron=add(g,122101,8,0,2,15);
 if(round===3||crowns===1)check(g.AiGrowthReserve(baron)===0,'no reserve for a future round that may never happen');
}
for(const mode of ['birna','bran','none','no-target','returner','duplicate']){
 const g=fixture();clear(g);const medic=add(g,152310,8);let target;
 if(mode==='birna'||mode==='duplicate'||mode==='no-target'||mode==='returner')add(g,152213,8);
 if(mode==='bran'){add(g,200159,64);g.leaderTemplateTwo=200159;target=add(g,152307,16);}
 if(mode==='birna'||mode==='duplicate')target=add(g,152307,8);
 if(mode==='no-target')add(g,113301,8);
 if(mode==='returner')add(g,152209,8);
 if(mode==='duplicate')add(g,152310,8);
 g.archetypeAI.Refresh();const priority=g.archetypeAI.Mulligan(medic);
 check((priority<16)===(mode==='birna'||mode==='bran'),'opening medic is kept only with a concrete eligible discard '+mode);
 decisions.push({case:'medic-discard-setup',mode,priority,keep:g.archetypeAI.MulliganKeepBonus(medic)});
}
{
 const g=fixture();clear(g);const medic=add(g,152310,8),birna=add(g,152213,8),queen=add(g,152307,8);
 for(let i=0;i<5;i++)add(g,152303,16,i);
 check(g.OpponentStep()&&(birna.Snapshot().locationMask&7)!==0,'play discard setup before the empty-grave medic');
 check(queen.Snapshot().locationMask===32&&medic.Snapshot().locationMask===8,'discard an eligible soldier while preserving resurrection');
 for(let i=0;i<2&&medic.Snapshot().locationMask===8;i++){g.match.currentPlayerId=2;g.match.turnActive=true;check(g.OpponentStep(),'combo follow-up completes');}
 check((medic.Snapshot().locationMask&7)!==0&&(queen.Snapshot().locationMask&7)!==0,'actual AI follows discard with resurrection');
 check(!g.IsFatal()&&!g.IsPending(),'combo leaves no unresolved request');
}
// Locking the public spy suppresses its pass reaction; score-only path remains exact.
{
 const g=fixture();const ciri=add(g,162212,1,0,1,8);ciri.Move(2,1,0);ciri.AddTokens(128|4);
 check(g.AiPublicPassLead()===g.Score(2)-g.Score(1),'locked False Ciri has no pass relocation');
}
globalThis.report={stage:140,checks,decisions,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'strategy140.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify(context.report));

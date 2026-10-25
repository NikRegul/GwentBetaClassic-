// Reproduce the reported 61/round-2 dry pass through the production decision path.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const cases=[];
function position(strength,damp,round=2){
 Host.strength=strength;const g=fixture();g.aiSimDamp=damp;
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();g.presetTwo=61;
 g.archetypeAI.Initialize(g,[],61,201743);
 g.match.roundNumber=round;g.match.playerOne.crowns=1;g.match.playerTwo.crowns=round===3?1:0;
 g.match.playerOne.hasPassed=true;const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 return g;
}
function decide(g){const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'actual chase completes');
 const selected=logs.find(s=>s.includes('event=SELECT')&&s.includes('action=card'))||'';
 cases.push({strength:Host.strength,damp:g.aiSimDamp,round:g.match.roundNumber,selected,logs:logs.filter(s=>/event=(OPTION|CHASE|SELECT|PASS)/.test(s))});
}
for(const strength of [2,3,4])for(const damp of [0,40,70,100]){
 const g=position(strength,damp),hand=[132217,200539,132211,200019,200539,200221,201776,132211].map((t,i)=>add(g,t,8,i));
 const brew=hand[5],graves=[];for(let i=0;i<5;i++)graves.push(add(g,132305,32,i));
 add(g,132305,16);add(g,200539,16,1);
 const seed=g.random.DrawCount();decide(g);
 if(!globalThis.observeOnly){
  check(brew.Snapshot().locationMask===8,'Brewess survives the empty second round '+strength+'/'+damp);
  check(graves.every(c=>c.Snapshot().locationMask===32),'Nekker resurrection pool survives '+strength+'/'+damp);
  check(g.Score(2)>0&&!g.match.playerTwo.hasPassed,'cheap card actually wins the dry-pass round '+strength+'/'+damp);
  check(hand.some((c,i)=>i!==5&&(c.Snapshot().locationMask&7)!==0),'ordinary alternative is really played '+strength+'/'+damp);
 }
 check(g.random.DrawCount()===seed,'search does not consume the live RNG');
}
// A low-tempo Nekker must not summon the remaining chain merely to take one point.
for(const strength of [2,4]){
 const g=position(strength,40),nekker=add(g,132305,8),ordinary=add(g,112101,8,1,2,8);
 add(g,132305,16);add(g,132305,32);
 decide(g);
 if(!globalThis.observeOnly)check(nekker.Snapshot().locationMask===8&&(ordinary.Snapshot().locationMask&7)!==0,'save Nekker when a normal body wins '+strength);
}
// Preservation is a cost, never a prohibition: play Brewess when she is the only winning answer.
for(const round of [2,3]){
 const g=position(4,40,round),brew=add(g,200221,8);add(g,132305,32);add(g,132305,32,1);
 add(g,112101,1,0,1,5);add(g,112101,8,1,2,1);decide(g);
 if(!globalThis.observeOnly)check((brew.Snapshot().locationMask&7)!==0&&g.Score(2)>g.Score(1),'Brewess wins when her ability is necessary '+round);
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,Object.assign(context,{observeOnly:process.argv.includes('--observe')}),{filename:'brewess091.bundle.js',timeout:180000});
if(process.argv[3]&&process.argv[3]!=='--observe')fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases.map(c=>({strength:c.strength,damp:c.damp,round:c.round,selected:c.selected}))},null,2));

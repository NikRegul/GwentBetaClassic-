// Dryads rebuilt around Ciri: Nova (preset 93, 22 Oct 2026): exactly two copies of every bronze,
// so Nova enters with 22 base power. The AI keeps her for the deciding round.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const NOVA=201626,cases=[];
function loc(c){return c.Snapshot().locationMask;}
// The real preset: bronze copies are counted from the frozen starting list.
{
 const ref={v:[]};BetaGwentDuelPresetDeck(93,ref);const list=Array.from(ref.v);
 const counts={};for(const t of list){const d=BetaGwentDuelDefinition(t);if(d.header.tierMask===2)counts[t]=(counts[t]||0)+1;}
 check(list.length===26,'Dryads: 26 cards');
 check(Object.values(counts).every(n=>n===2)&&Object.keys(counts).length===8,'eight bronze pairs, no single or third copy');
 check(list.filter(t=>BetaGwentDuelDefinition(t).header.tierMask===8).length===4&&list.filter(t=>BetaGwentDuelDefinition(t).header.tierMask===4).length===6,'four gold and six silver');
 check(list.includes(NOVA),'Ciri: Nova is in the deck');
}
function match(strength,round){
 Host.strength=strength;const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,93))throw Error('initialize');
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=round;
 g.match.playerOne.crowns=round===3?1:0;g.match.playerTwo.crowns=round===3?1:0;g.match.playerOne.hasPassed=false;g.match.playerTwo.hasPassed=false;
 const nova=g.live.find(c=>c.TemplateId()===NOVA&&c.Snapshot().positionPlayerId===2);
 if(loc(nova)!==8){const h=g.live.find(c=>c.Snapshot().positionPlayerId===2&&loc(c)===8&&c.TemplateId()!==NOVA);const hi=h.Snapshot().locationIndex;h.Move(2,16,0);nova.Move(2,8,hi);}
 const leader=g.Leader(2);if(leader)leader.Move(2,512,0);
 return {g,nova};
}
for(const strength of [2,4]){
 const {g,nova}=match(strength,3);
 check(g.Play(2,nova.cardState.instanceId,1),'Nova can be played '+strength);
 check(nova.Snapshot().power.currentPower===22,'Nova enters with 22 power from the real starting list '+strength+' ('+nova.Snapshot().power.currentPower+')');
 check(!g.IsFatal()&&!g.IsPending(),'Nova resolves '+strength);
}
for(const strength of [2,3,4]){
 const {g,nova}=match(strength,1);g.archetypeAI.Refresh();
 check(g.archetypeAI.Reserve(nova.Definition())>=12,'Nova is reserved before the deciding round '+strength);
 const logs=[];Host.log=s=>logs.push(s);g.OpponentStep();Host.log=null;
 cases.push({label:'round1 '+strength,selected:(logs.find(s=>s.includes('event=SELECT'))||logs.find(s=>s.includes('event=PASS'))||'').slice(0,140)});
 check(loc(nova)===8,'Nova is not spent in round one '+strength);
}
{
 const {g,nova}=match(4,3);g.archetypeAI.Refresh();
 check(g.archetypeAI.Reserve(nova.Definition())===0,'no reserve in the deciding round');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'ciri-nova092.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
console.log(JSON.stringify({checks:context.report.checks,cases:context.report.cases},null,1));

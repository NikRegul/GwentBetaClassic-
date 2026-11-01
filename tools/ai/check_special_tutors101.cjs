'use strict';
// Actual WS rules. Logged positions are partial public reconstructions, not
// historical-runtime replays; synthetic controls specify their own full state.
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
context.observe=process.argv.includes('--observe');
context.positions=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/special-tutors101.json'),'utf8'));
const setup=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+setup+String.raw`
const failures=[],cases=[];
if(observe&&!CBetaGwentDuelSession.prototype.AiSpecialTutorMulliganPriority)
 CBetaGwentDuelSession.prototype.AiSpecialTutorMulliganPriority=function(){return 0;};
check=function(v,n){checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
function blank(round=3,preset=93){
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.presetOne=g.presetTwo=preset;g.leaderTemplateOne=g.leaderTemplateTwo=200166;
 g.archetypeAI.Initialize(g,[],preset,200166);g.aiSimDamp=40;
 g.match.roundNumber=round;g.match.playerOne.crowns=g.match.playerTwo.crowns=round===3?1:0;
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();return g;
}
function prepare(g){let ticks=0;while(!g.AiPreparationStep())if(++ticks>12000)throw Error('stalled');}
function act(g,staged){if(staged)prepare(g);const logs=[];Host.log=s=>logs.push(s);
 try{let ok=false;for(let i=0;i<4&&!ok;i++){ok=g.OpponentStep();if(!ok)prepare(g);}check(ok&&!g.IsFatal()&&!g.IsPending(),'decision resolves');}
 finally{Host.log=null;}return logs;
}
for(const preset of [74,81,93]){
 const g=blank(3,preset),ith=add(g,142107,8,0),bolt=add(g,113301,8,1),swallow=add(g,113310,8,2);
 add(g,112405,16,0);g.archetypeAI.Refresh();
 check(g.AiTutorTargetCount(ith)===0,'Ithlinne has no legal deck target, preset '+preset);
 const before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
 check(g.AiSpecialTutorMulliganPriority(bolt)>g.AiTutorMulliganPriority(ith),'return fuel before replacing empty tutor '+preset);
 check(g.AiSpecialTutorMulliganPriority(swallow)===0,'alchemy cannot fuel Ithlinne '+preset);
 check(before===JSON.stringify(g.live.map(c=>c.Snapshot()))&&draws===g.random.DrawCount(),'mulligan estimate is read only '+preset);
 g.AiMulligan(1);
 check(bolt.Snapshot().locationMask===16&&ith.Snapshot().locationMask===8&&swallow.Snapshot().locationMask===8,'one swap restores Ithlinne instead of dumping her '+preset);
 check(g.AiTutorTargetCount(ith)===1,'returned spell is a legal target '+preset);
 const enemy=add(g,112405,1,0,1,30);
 check(g.Play(2,ith.cardState.instanceId,1)&&!g.IsPending()&&!g.IsFatal(),'Ithlinne actually plays returned spell twice '+preset);
 check(enemy.Snapshot().power.currentPower===12&&g.Score(2)===2,'two real nine-point hits and two-point body '+preset);
}
{
 const g=blank(),merc=add(g,142308,8,0),swallow=add(g,113310,8,1);add(g,112405,16,0);
 check(g.AiSpecialTutorMulliganPriority(swallow)>30,'Mercenary can receive alchemy');g.AiMulligan(1);
 check(swallow.Snapshot().locationMask===16&&merc.Snapshot().locationMask===8,'Mercenary gets a deck target');
 check(g.Play(2,merc.cardState.instanceId,1)&&g.Score(2)===11&&!g.IsPending(),'Mercenary actually plays returned Swallow on itself');
}
{
 const priorities=[];
 for(const hidden of [112405,113301]){
  const g=blank();add(g,142107,8,0);const spell=add(g,113301,8,1);add(g,112405,16,0);
  add(g,hidden,8,0,1);add(g,hidden,16,0,1);g.archetypeAI.Refresh();
  priorities.push(g.AiSpecialTutorMulliganPriority(spell));
 }
 check(priorities[0]===priorities[1]&&priorities[0]>30,'own tutor pool ignores opposing hidden hand and deck');
}
{
 const g=blank(),ith=add(g,142107,8,0),merc=add(g,142308,8,1),spell=add(g,113301,16,0),swallow=add(g,113310,8,2);
 check(g.AiSpecialTutorMulliganPriority(swallow)>30,'two consumers need two distinct deck targets');
 swallow.Move(2,16,1);const spare=add(g,113301,8,3);
 check(g.AiSpecialTutorMulliganPriority(spare)===0,'sufficient pool does not force return of every special');
 spell.Move(2,32,0);
 check(g.AiSpecialTutorMulliganPriority(spare)>30,'alchemy pool cannot replace Ithlinne spell pool');
 const silver=add(g,113301,8,4);silver.cardState.runtimeTierMask=4;
 check(g.AiSpecialTutorMulliganPriority(silver)===0,'runtime silver is not a bronze tutor target');
}
for(const staged of [false,true])for(const damp of [0,40,70]){
 const g=blank(),swallow=add(g,113310,8,0),enemy=add(g,112405,1,0,1,22);add(g,112405,8,0,1);
 g.aiSimDamp=damp;const logs=act(g,staged);cases.push({kind:'unbacked',staged,damp,logs});
 check(swallow.Snapshot().locationMask===8&&enemy.Snapshot().power.currentPower===22&&g.match.playerTwo.hasPassed,'mandatory round does not force an unbacked enemy boost '+staged+'/'+damp);
}
// Independent positive control: without the gift Scorch kills only the 18.
// Boosting the opposing 8 to 18 makes Scorch remove both, gaining eight more.
{
 const g=blank(),small=add(g,112405,1,0,1,8),enemy=add(g,112405,1,1,1,18),swallow=add(g,113310,8,0),scorch=add(g,113309,8,1);
 add(g,112405,8,0,1);g.archetypeAI.Refresh();
 const logs=act(g,false);cases.push({kind:'scorch-setup',logs});
 check(swallow.Snapshot().locationMask!==8&&!g.match.playerTwo.hasPassed,'profitable enemy boost remains playable');
 check(g.Pass(1)&&g.OpponentStep(),'Scorch continuation resolves after opposing pass');
 check(!alive(small)&&!alive(enemy)&&scorch.Snapshot().locationMask!==8,'setup actually removes both opposing units');
}
for(const p of positions.positions)for(const staged of [false,true]){
 const g=blank(),map=new Map();g.aiSimDamp=40;
 for(const c of p.cards){
  if(c.zone===512)continue;
  const card=add(g,c.template,c.zone,c.index,c.side,c.power);map.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.tokenMask=c.tokens;card.cardState.timerValue=c.timer;
  card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);
 }
 g.aiStartingDeckOne.Clear();for(const t of p.known)g.aiStartingDeckOne.PushBack(t);g.archetypeAI.Refresh();
 const enemy=map.get(1),old=enemy.Snapshot().power.currentPower,swallow=map.get(44);
 const logs=act(g,staged);cases.push({kind:'public-log-reconstruction',decision:p.decision,staged,logs:logs.filter(s=>/event=(SELECT|PASS|REJECT|OPTION)/.test(s))});
 check(enemy.Snapshot().power.currentPower<=old,'reported position does not gift ten points '+p.decision+'/'+staged);
 check(swallow.Snapshot().locationMask===8,'reported Swallow remains available for our unit '+p.decision+'/'+staged);
}
globalThis.report={checks,failures,cases,actualWitcherScript:true,historicalRuntimeVerified:false,nativeGameTested:false};
`,context,{filename:'special-tutors101.bundle.js',timeout:240000});
if(process.argv[3]&&!process.argv[3].startsWith('--'))fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');
if(context.report.failures.length&&!context.observe)process.exitCode=1;
console.log(JSON.stringify({checks:context.report.checks,failures:context.report.failures}));

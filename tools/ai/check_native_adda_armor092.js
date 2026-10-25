// Rebuilt public position from the native Adda/Armor match; omitted state is not a full native replay.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const P=JSON.parse(require('zlib').gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/adda-armor-final092.json.gz'))));
context.P=P;
context.P8=JSON.parse(require('zlib').gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/adda-armor-late-pass092.json.gz'))));
context.P1=JSON.parse(require('zlib').gunzipSync(fs.readFileSync(path.join(__dirname,'fixtures/adda-armor-opening092.json.gz'))));
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
function rebuild(P){const strength=Number(P.head.strength);Host.strength=strength;Host.matchStrength=[strength,strength];
const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(Number(P.head.presetOne),Number(P.head.presetTwo)))throw Error('initialize');
g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
const leaders=[g.Leader(1),g.Leader(2)];
for(const c of g.live.slice())if(c!==leaders[0]&&c!==leaders[1])c.Move(c.Snapshot().positionPlayerId,512,0);
for(let i=0;i<2;i++)if(leaders[i]&&!P.leaders[i])leaders[i].Move(i+1,512,0);
const leaderTemplates=new Set(leaders.filter(Boolean).map(c=>c.TemplateId()));
for(const c of P.cards){
 if(c.zone===512||leaderTemplates.has(c.template)&&c.zone!==1&&c.zone!==2&&c.zone!==4)continue;
 const card=add(g,c.template,c.zone,c.index,c.side,c.power);
 card.cardState.ownerId=c.owner;card.cardState.tokenMask=c.tokens;card.cardState.timerValue=c.timer;
 if(c.armor)card.power.SetCurrentPair(c.power,c.armor);
}
g.match.roundNumber=Number(P.head.round);g.match.playerOne.crowns=P.crowns[0];g.match.playerTwo.crowns=P.crowns[1];
g.match.playerOne.hasPassed=P.passed[0];g.match.playerTwo.hasPassed=P.passed[1];
g.match.currentPlayerId=2;g.match.roundActive=true;g.match.turnActive=true;
g.aiStartingDeckOne.Clear();for(const t of P.known)g.aiStartingDeckOne.PushBack(t);
if(P.weather.some(x=>x))throw Error('Unsupported weather in public log reconstruction');return g;}
// A global boost belongs before cards leave the hand/deck. Both normal and
// reduced preparation budgets must retain Foltest's future boost credit.
const openings=[];
for(const strength of [3,4])for(const damp of [40,70]){
 const payload=JSON.parse(JSON.stringify(P1));payload.head.strength=String(strength);
 const start=rebuild(payload);start.aiSimDamp=damp;
 const units=start.live.filter(c=>c.Snapshot().positionPlayerId===2&&[8,16].includes(c.Snapshot().locationMask)&&c.Definition().header.typeMask===4&&!BetaGwentDuelSpying(c.TemplateId()));
 const powers=units.map(c=>c.Snapshot().power.currentPower);
 check(start.OpponentStep()&&!start.IsFatal(),'opening decision resolves '+strength+'/'+damp);
 check(!start.LeaderAvailable(2)&&start.CountLocation(2,8)===10,'Foltest boosts before spending the opening hand '+strength+'/'+damp);
 check(units.every((c,i)=>c.Snapshot().power.currentPower===powers[i]+1),'every held/deck unit actually receives the early boost '+strength+'/'+damp);
 openings.push({strength,damp,leaderPlayed:true,boostedUnits:units.length});
}
// Test the other pilot too: all of Adda's original hand/deck cards are ours
// in this reconstruction. The enemy forecast uses Armor's starting list.
const addaPayload=JSON.parse(JSON.stringify(P1));
[addaPayload.head.presetOne,addaPayload.head.presetTwo]=[addaPayload.head.presetTwo,addaPayload.head.presetOne];
addaPayload.known=P1.cards.filter(c=>c.side===2&&[8,16].includes(c.zone)).map(c=>c.template);
addaPayload.cards.forEach(c=>{c.side=3-c.side;c.owner=3-c.owner;});
addaPayload.crowns.reverse();addaPayload.passed.reverse();addaPayload.leaders.reverse();
const addaOpenings=[];
for(const damp of [40,70]){
 const start=rebuild(addaPayload);start.aiSimDamp=damp;const selections=[];
 Host.log=s=>{if(s.includes('event=SELECT '))selections.push(s);};
 let ok;try{ok=start.OpponentStep();}finally{Host.log=null;}
 check(ok&&!start.IsFatal(),'Adda opening resolves '+damp);
 check(selections.some(s=>s.includes('template=201624 ')),'Adda sets up Revenant before the compound tutor '+damp);
 addaOpenings.push({damp,selection:selections[0]});
}
function addaOrder(order){
 const g=rebuild(addaPayload).AiSimClone();
 for(const template of order){
  if(g.Snapshot().currentPlayerId===1)check(g.AiSimSkipTurn(),'advance a non-intervening opposing turn');
  g.archetypeAI.Refresh();
  const c=g.live.find(c=>c.TemplateId()===template&&c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);
  check(Boolean(c)&&g.AiSimPlay(c.Snapshot().instanceId)!==-2147483647,'resolve actual Adda combo card '+template);
 }
 return g.Score(2);
}
const comboEarly=addaOrder([201624,122103,201628]),comboLate=addaOrder([122103,201624,201628]);
check(comboEarly===comboLate+8,'same three cards generate eight more actual points when Revenant precedes Natalis');
const g=rebuild(P);
g.aiSimDamp=70;const original=g.AiSimClone();const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
check(ok&&!g.IsFatal(),'rebuilt decision completes');
const line=logs.find(s=>/event=(SELECT|PASS) /.test(s))||'';
const kind=line.includes('event=PASS')?'pass':(line.includes('action=leader')?'leader':'card');
const tm=/template=(\d+)/.exec(line),template=kind==='card'&&tm?Number(tm[1]):0;
console.log('LOGGED:',P.logged.text);console.log('NOW:   ',line.replace('AI_REASON schema=1 ','').slice(0,240));
const same=kind===P.logged.kind&&template===P.logged.template;
check(logs.filter(s=>s.includes('event=SHORT_LINE')).length===3,'all three openings retain whole-line counterplay at damp70');
// Independent three-action oracle: execute our opening, the public Seltkirk
// hypothesis, then every remaining own follow-up through the actual rules.
// This does not read the reply tree's estimates or the hidden hand identities.
const alternatives=[];
for(const first of original.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8)){
 const root=original.AiSimClone();root.AiSpyForecastDeck(0);
 if(root.AiSimPlay(first.Snapshot().instanceId)===-2147483647)continue;
 const enemy=root.AiReverseClone(),slot=enemy.live.find(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8);
 check(Boolean(slot),'public reply has a hand slot');slot.Move(2,512,0);
 const reply=add(enemy,201618,8,0,2);
 check(enemy.AiSimPlay(reply.Snapshot().instanceId)!==-2147483647,'public duel response resolves');
 const own=enemy.AiReverseClone();let best=-Infinity;
 for(const follow of own.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8)){
  const h=own.AiSimClone();if(h.AiSimPlay(follow.Snapshot().instanceId)!==-2147483647)best=Math.max(best,h.Score(2)-h.Score(1));
 }
 alternatives.push({first:first.TemplateId(),bestLeadAfterReplyAndFollow:best});
}
const selected=alternatives.find(a=>a.first===template),old=alternatives.find(a=>a.first===201618);
console.log('RESOLVED_LINES',JSON.stringify(alternatives));
check(selected&&selected.bestLeadAfterReplyAndFollow===Math.max(...alternatives.map(a=>a.bestLeadAfterReplyAndFollow)),'whole-line choice agrees with independent actual three-action oracle');
const late=rebuild(P8);late.aiSimDamp=70;
check(late.Score(2)===79&&late.Score(1)===58&&late.CountLocation(2,8)===3&&late.CountLocation(1,8)===4,'late first-round native score and hand sizes reconstructed');
check(late.LeaderAvailable(2)&&!late.LeaderAvailable(1),'only our once-per-match leader remains');
check(late.OpponentStep()&&!late.IsFatal(),'late first-round decision completes');
check(!late.Snapshot().playerTwo.hasPassed,'an unused leader alone does not authorize a first-round pass');
globalThis.report={checks,openings,addaOpenings,addaNonInterveningCombo:{early:comboEarly,late:comboLate},logged:P.logged,now:{kind,template,line},alternatives,latePass:{ownHand:late.CountLocation(2,8),leaderPreserved:Boolean(late.LeaderAvailable(2))},rebuiltPublicPosition:true,actualWitcherScript:true,nativeGameTested:false};
`,context,{filename:'native-adda-armor092.bundle.js',timeout:180000});
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(context.report,null,2)+'\n');

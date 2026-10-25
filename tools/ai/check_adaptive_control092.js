// Candidate-specific public controls use the same bounded number of actual plays.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
function position(){const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=70;
 g.aiStartingDeckOne=[113301,113301,113301,113309];
 add(g,112405,1,0,2,5);add(g,112405,1,0,1,4);
 const strong=add(g,112405,8,0,2,20),weak=add(g,112405,8,1,2,3);
 add(g,112405,8,0,1,8);add(g,112405,8,1,1,8);g.archetypeAI.Refresh();return {g,strong,weak};}
function state(g){return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.Snapshot(),rng:g.random.DrawCount(),request:g.requestId});}
const cases=[];
for(const mutate of [false,true]){
 const {g,strong,weak}=position();
 if(mutate)for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId!==1||s.locationMask!==8)continue;
  c.definition=BetaGwentDuelDefinition(113309);c.cardState.runtimeTemplate=c.definition.header;c.power.SetCurrentPair(55,9);c.cardState.timerValue=7;}
 const before=state(g),model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);
 check(model.templates.length===1&&model.templates[0]===113301,'one frequency-only control slot starts with common Alzur damage');
 const root=g.AiSimClone();check(root.AiSimPlay(strong.Snapshot().instanceId)!==-2147483647,'exposed twenty-point body actually resolves');
 const reply=model.Apply(root);
 check(model.templates.length===1&&model.templates[0]===113309,'same slot considers rare Scorch against the exposed maximum');
 check(model.evaluated===1&&reply&&reply.FindCard(strong.Snapshot().instanceId).Snapshot().locationMask===32,'exactly one actual modeled reply destroys the exposed unit');
 check(state(g)===before,'public adaptation preserves real cards, turn, request and RNG');
 const other=g.AiSimClone();check(other.AiSimPlay(weak.Snapshot().instanceId)!==-2147483647,'small body actually resolves');
 model.BeginApply(other);
 cases.push({mutate,largeReply:113309,smallReply:model.templates[0]});
}
check(JSON.stringify(cases[0].largeReply)===JSON.stringify(cases[1].largeReply)&&cases[0].smallReply===cases[1].smallReply,'hidden hand templates/powers/timers do not change selection');
{
 const {g,strong}=position();g.live.filter(c=>c.Snapshot().positionPlayerId===1&&c.Snapshot().locationMask===8).forEach(c=>c.AddTokens(64));
 const model=new CBetaGwentPublicResponseAI();model.Initialize(g,1);const original=Array.from(model.templates);
 const root=g.AiSimClone();root.AiSimPlay(strong.Snapshot().instanceId);model.BeginApply(root);
 check(JSON.stringify(model.templates)===JSON.stringify(original),'fully revealed hand retains its actual bounded replies');
}
globalThis.report={checks,cases,actualWitcherScript:true,nativeGameTested:false};
`,ctx,{timeout:180000});
const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));

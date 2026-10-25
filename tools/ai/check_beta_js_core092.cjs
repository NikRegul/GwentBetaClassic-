/* Direct JavaScript port checks. Native process launch is explicitly forbidden.
 * Formula expectations are independent arithmetic/branch cases from source;
 * all real final0.9.2 rosters are also read through the shared JS rule engine. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const cp=require('node:child_process');
for(const name of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[name]=()=>{throw Error('Native process forbidden in direct JS port test');};
const {BetaMiniMaxEvaluator,BetaSemanticMulliganPicker,chooseLowestPowerMulligan,chooseBestCardForPersonality,quality,validRound}=require('./beta_js092/core.cjs');
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const p=basePersonality(),mulligan=new BetaSemanticMulliganPicker();let checks=0;
function equal(a,b){assert.deepEqual(a,b);checks++;}
function near(a,b){assert(Math.abs(a-b)<0.00002,`${a} != ${b}`);checks++;}
function card(id,side=1,power=10,tier=2){return {id,templateId:id,side,zone:8,index:0,playable:true,templateTier:tier,runtimeTier:tier,
 type:4,printedPower:power,power,tokens:0,linkedTemplateId:0,semanticTags:[],categories:[]};}
function state(cards=[]){return {cards,currentPlayerId:1,startingPlayerId:1,roundIndex:0,roundId:1,winnerMask:0,
 players:[{score:0},{score:0}],rounds:[],rows:[1,2].flatMap(side=>[1,2,4].map(row=>({side,row,token:0})))};}
function node(s,decision=null,parentState=s){return {state:s,parentState,executingPlayerId:1,decision,locationChoices:[],handlerScore:0};}
const zero={...p,semanticTags:[]};
for(const k of Object.keys(zero))if(k.endsWith('Preference'))zero[k]=0;
const e=new BetaMiniMaxEvaluator(zero);
equal(quality([card(1,1,4,2),card(2,1,5,4),card(3,1,6,8),card(4,1,7,1)]),{bronze:1,silver:1,gold:1,leader:1,carryover:0,count:4});
const unplayable=card(5);unplayable.playable=false;equal(quality([unplayable]).count,0);
near(e.evaluate(node(state([card(1,1,10,8),card(2,2,10,2)]))),62.5);
near(e.evaluate(node(state([card(1,1,10,8),card(2,2,10,8)]))),50);
const leader=card(7,1,5,1);leader.zone=64;
near(e.evaluate(node(state([leader,card(8,2,5,1)]))),50); // Leader zone64 is included.
const pool=card(10,1,5,1);pool.zone=128;
near(e.evaluate(node(state([leader,pool,card(8,2,5,1)]))),50); // SpawningPool128 is excluded.
near(e.evaluate(node(state())),0);
for(const [winner,expected]of [[1,100],[2,0]]){const s=state();s.winnerMask=winner;near(e.evaluate(node(s)),expected);}
const draw=state();draw.winnerMask=3;near(e.evaluate(node(draw)),0); // Draw uses formula, not a forced terminal50.
const res=card(1,1,7);res.zone=1;res.tokens=1;
let s=state([res]);s.players[0].score=7;
equal(e.details(node(s)).ownValue,14);
s.roundIndex=1;s.roundId=2;s.rounds=[{winnerMask:2}];equal(e.details(node(s)).ownValue,21);
s.roundIndex=2;s.roundId=3;s.rounds=[{winnerMask:2},{winnerMask:1}];equal(e.details(node(s)).carryMultiplier,0);
const history=state();history.roundIndex=1;history.roundId=2;history.rounds=[{winnerMask:3}];history.players[0].score=10;
near(e.evaluate(node(history)),100); // Literal original All(0x303) vs ordinary draw(3).
history.rounds[0].winnerMask=0x303;near(e.evaluate(node(history)),100*40/70);
const tempo=state([card(1),card(2,2)]);tempo.currentPlayerId=2;
near(e.evaluate(node(tempo)),100*14/18); // Original first-player compensation +5/-5.
const played=card(9);played.zone=1;played.semanticTags=[8,9];
const semanticState=state([played]);semanticState.players=[{score:10},{score:10}];
const semanticProfile={...zero,SemanticEvaluatorScoringWeight:1,semanticTags:[
 {id:8,weight:100,usage:2,rounds:7},{id:9,weight:-100,usage:2,rounds:7}]};
const se=new BetaMiniMaxEvaluator(semanticProfile),sn=node(semanticState,{cardId:9,side:1,row:1});
near(se.evaluate(sn),75);equal(se.details(sn).semantic,100);
semanticProfile.semanticTags[0].usage=1;equal(se.details(sn).semantic,-100);
equal(validRound({rounds:1},0),true);equal(validRound({rounds:1},1),false);
equal(validRound({rounds:6},2),true);equal(validRound({rounds:0},0),false);
const weatherCard=card(10);weatherCard.zone=32;weatherCard.type=2;weatherCard.categories=[52];
const ws=state([weatherCard]);ws.rows[0].token=1;
const weatherEval=new BetaMiniMaxEvaluator({...zero,WeatherCardPreference:4,PlayWeatherOntoWeatherPreference:-20,PlayWeatherOntoSameWeatherPreference:-30});
const wn=node(ws,{cardId:10,side:1,row:32});wn.locationChoices=[[{side:1,row:1}]];
equal(weatherEval.genericPreference(wn,weatherCard),-16); // Original never selects same-weather branch.
const stackingState=state([played,card(11),card(12),card(13)]);
stackingState.cards[1].zone=1;stackingState.cards[2].zone=1;stackingState.cards[3].zone=2;
const stackEval=new BetaMiniMaxEvaluator({...zero,RowStackingPreference:-3});
equal(stackEval.rowStacking(node(stackingState,{cardId:9,side:1,row:1}),played),-3);
equal(stackEval.rowStacking(node(stackingState,{cardId:9,side:1,row:2}),played),-1);
const hazardProfile={...zero,PlayingIntoBoonsPreference:2,PlayingIntoHazardsPreference:-1.5},he=new BetaMiniMaxEvaluator(hazardProfile);
stackingState.rows[0].token=1;equal(he.rowEffect(node(stackingState,{cardId:9,side:1,row:1})),-1.5);
stackingState.rows[3].token=1;equal(he.rowEffect(node(stackingState,{cardId:9,side:2,row:1})),1.5);
stackingState.rows[0].token=256;equal(he.rowEffect(node(stackingState,{cardId:9,side:1,row:1})),2);
// Source mulligan: tags, duplicate penalties, linked cards and exact thresholds.
const a=card(1,1,6),b=card(2,1,5);equal(mulligan.choose([a,b],zero).id,2);equal(mulligan.choose([a],zero),null);
a.semanticTags=[2];equal(mulligan.score(a,zero,[a]),-44);
a.semanticTags=[4];equal(mulligan.score(a,zero,[a]),56);
a.semanticTags=[3];b.templateId=a.templateId;equal(mulligan.score(a,zero,[a,b]),-45);
a.semanticTags=[5];equal(mulligan.score(a,zero,[a,b]),57);
a.semanticTags=[19];a.linkedTemplateId=7;b.linkedTemplateId=7;equal(mulligan.score(a,zero,[a,b]),61);
a.semanticTags=[20];equal(mulligan.score(a,zero,[a,b]),-45);
a.semanticTags=[8];equal(mulligan.score(a,{...zero,semanticTags:[{id:8,weight:-10,usage:1,rounds:0}]},[a]),-4);
equal(mulligan.score(a,{...zero,semanticTags:[{id:8,weight:-10,usage:2,rounds:7}]},[a]),6);
equal(mulligan.choose([],p),null);
const low=card(4,1,1);low.printedPower=6;const printed=card(5,1,2);printed.printedPower=4;
equal(chooseLowestPowerMulligan([low,printed]),null); // Lowest current power is tested, no second candidate.
low.printedPower=4;equal(chooseLowestPowerMulligan([low,printed]).id,4);
equal(chooseBestCardForPersonality([{id:1,revisedScore:10},{id:2,revisedScore:12}]).id,2);
equal(chooseBestCardForPersonality([]),null);
const before=JSON.stringify(sn);se.evaluate(sn);se.evaluate(sn);equal(JSON.stringify(sn),before);
const runtime=createRuntime(),rosters=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../../data/beta924/ai/validation093/final092-rosters.json'),'utf8')).decks;
const realCases=[];
for(const d of rosters){
 const g=runtime.newSession();assert(g.InitializeWithDecks(d.templateIds,d.templateIds,d.leader,d.leader,d.presetId,d.presetId));
 const rngBefore=JSON.stringify(g.random),position=stateFromSession(g),positionBefore=JSON.stringify(position);
 for(const side of [1,2]){
  const evaluation=new BetaMiniMaxEvaluator(p).evaluate({...node(position),executingPlayerId:side});assert(Number.isFinite(evaluation));
  const hand=position.cards.filter(c=>c.side===side&&c.zone===8&&c.playable),choice=mulligan.choose(hand,p);
  assert(choice===null||hand.includes(choice));realCases.push({preset:d.presetId,side,evaluation,mulligan:choice?.id||0});checks+=2;
 }
 equal(JSON.stringify(position),positionBefore);equal(JSON.stringify(g.random),rngBefore);
}
const files=['beta_js092/core.cjs','beta_js092/session.cjs','beta_js092/data/templates.json','beta_js092/data/personalities.json'];
const hashes=Object.fromEntries(files.map(f=>[f,crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,f))).digest('hex')]));
const report={schema:1,complete:true,checks,realInitialPositions:realCases.length,realCases,hashes,fingerprint:runtime.fingerprint,
 nativeProcessesAllowed:false,componentsOnly:true,fullAiPortComplete:false,fullMatchReady:false,notStrengthResult:true,
 limitations:['End-to-end Beta policy is not complete; separate action/mulligan reports cover the new opt-in shared-engine hooks.','This historical P19 component test still uses current side2 mulligan; these are only component evaluations of those positions.','Best-card ties use input order; original List.Sort gives no stable tie guarantee.']};
const out=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-core-proof.json');
fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({...report,realCases:undefined,hashes:undefined}));

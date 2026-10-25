'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {BetaPlayMaker}=require('./beta_js092/playmaker.cjs');
const {BetaSearchNode,Status}=require('./beta_js092/search.cjs');
const {personality}=require('./beta_js092/profiles.cjs');
const templates=require('./beta_js092/data/templates.json');
const stage=path.resolve(process.argv[2]);
const rules=path.resolve(process.argv[3]);
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n')+'\n'+fs.readFileSync(path.join(stage,'ws-stage.js'),'utf8');
const ws=new Function(source+`return {node:()=>{let n=new CBetaOriginalNode();n.Initialize();return n;},maker:()=>new CBetaOriginalPlayMaker(),
 profile:f=>{let p=new CBetaOriginalPersonality();if(!p.Initialize(f))throw Error('faction');return p;}};`)();
let checks=0;const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
const names={2:'p_Monster_Practice',4:'p_Nilfgaard_Practice',8:'p_NorthernRealms_Practice',16:"p_Scoia'tael_Practice",32:'p_Skellige_Practice'};
for(const [faction,name]of Object.entries(names))for(const round of ['Round1','Round2WonFirstRound','Round2LostFirstRound','Round2DrewFirstRound','Round3'])
 for(const passStatus of ['OpponentStillPlaying','OpponentPassed','OpponentWillAutoPass'])for(const scoreStatus of ['Ahead','Behind','Drawing'])
 for(const turn of [1,2,3,7,8])for(const carryStatus of ['Ahead','Behind','Drawing'])for(const cardStatus of ['Ahead','Behind','Drawing']){
  const values={round,passStatus,scoreStatus,turn,carryStatus,carryDiff:carryStatus==='Ahead'?10:carryStatus==='Behind'?-3:0,cardStatus,hand:3};
  const a=Object.assign(new BetaPlayMaker(),values,{p:personality(name)}),b=Object.assign(ws.maker(),values,{p:ws.profile(Number(faction))});
  eq(b.Strategy(),a.strategy(),'Source strategy '+JSON.stringify(values));
  for(const winning of [false,true])eq(b.Threshold(winning),a.threshold(winning),'Source threshold');
 }
const lowTemplate=Object.values(templates).find(t=>t.semanticTags.includes(6)).id;
const regular=Object.values(templates).find(t=>t.type===4&&!t.semanticTags.includes(6)).id;
function game(state){return {
 match:{roundNumber:state.roundId,roundTurnIndex:state.roundTurnIndex,playerOne:{hasPassed:state.passed[0]},playerTwo:{hasPassed:state.passed[1]},results:state.rounds.map(r=>({roundNumber:r.roundNumber||state.roundId-1,winnerMask:r.winnerMask,scoreOne:r.playerScores[0],scoreTwo:r.playerScores[1]}))},
 Score:side=>state.players[side-1].score,
 live:state.cards.map(c=>({Snapshot:()=>({positionPlayerId:c.side,locationMask:c.zone,canBePlayed:c.playable,tokenMask:c.tokens,power:{currentPower:c.power}})})),
 FindCard:id=>{const c=state.cards.find(c=>c.id===id);return c?{TemplateId:()=>c.templateId}:null;}};}
function fixture(side){
 const state={roundId:1,roundIndex:0,roundTurnIndex:1,currentRoundWinner:0,passed:[false,false],rounds:[],players:[{score:0},{score:0}],cards:[]};state.players[side-1].score=5;
 for(const actor of [1,2])for(let i=0;i<3;i++)state.cards.push({id:actor*100+i,templateId:i===2?lowTemplate:regular,side:actor,zone:8,playable:true,power:5,tokens:0,semanticTags:i===2?[6]:[]});
 const root=new BetaSearchNode(1,0);root.state=state;root.executingPlayerId=side;root.status=Status.OK;
 root.children=[[null,20,5],[side*100,10,7],[side*100+1,8,17],[side*100+2,7,6]].map(([card,score,diff],i)=>{
  const n=new BetaSearchNode(i+2,1,root);n.status=Status.OK;n.executingPlayerId=side;n.decision=card===null?null:{cardId:card};
  n.state=JSON.parse(JSON.stringify(state));n.state.players[side-1].score=diff;n.revisedScore=score;return n;});
 function convert(n,parent){const typed=ws.node();typed.id=n.id;typed.parentNode=parent;typed.status=n.status;typed.executingPlayerId=n.executingPlayerId;
  typed.hasState=true;typed.game=game(n.state);typed.cardId=n.decision?.cardId||0;typed.revised=n.revisedScore;typed.children=n.children.map(c=>convert(c,typed));return typed;}
 return {root,typed:convert(root,null)};
}
const strategies=['Default','Pass','PlayBestCard','PlayStrongestCard','PlayLowTempoCardIfAbleOtherwisePlayBest','PlayLowTempoCardIfAbleOtherwisePlayStrongest','PlayLowTempoCardIfAbleOtherwisePass','PassIfStillWinningOtherwisePlayBestCard','PassIfStillWinningOrDrawingOtherwisePlayBestCard','PassIfStillWinningOtherwisePlayStrongestCard','PassIfStillWinningOrDrawingOtherwisePlayStrongestCard','PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest','PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayBest','PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest','PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePlayStrongest','PassIfStillWinningOtherwisePlayLowTempoCardIfAbleOtherwisePass','PassIfStillWinningOrDrawingOtherwisePlayLowTempoCardIfAbleOtherwisePass','DontPassUnlessAllPlayActionsAreDetrimental','PassIfOpponentCantCatchUpIn1Card','PlayIfAbleToGetWithinThresholdOrOvertakeInOneCard','PlayIfAbleToOvertakeInOneCard'];
for(const side of [1,2])for(const [faction,name]of Object.entries(names))for(const strategy of strategies){
 const {root,typed}=fixture(side),a=new BetaPlayMaker(),b=ws.maker();a.determine(root,personality(name));b.Determine(typed,ws.profile(Number(faction)));
 for(const key of ['round','scoreStatus','carryStatus','cardStatus','passStatus','turn','hand','diff','carryDiff'])eq(b[key],a[key],'Read actual source context '+key);
 a.implement(strategy);b.Implement(strategy);eq(b.failed,false,'No unsupported source strategy');
 const scores=n=>n.children.map(c=>[c.id,c.revisedScore]).sort((x,y)=>x[0]-y[0]);
 eq(typed.children.map(c=>[c.id,c.RevisedScore()]).sort((x,y)=>x[0]-y[0]),scores(root),'Same revised-only correction '+strategy);
 eq(typed.children.map(c=>c.id),root.children.map(c=>c.id),'Same stable order '+strategy);
}
// Unfinished nodes must stop source PlayMaker, not read a partial battle state.
const {root,typed}=fixture(1),a=new BetaPlayMaker(),b=ws.maker();a.determine(root,personality(names[2]));b.Determine(typed,ws.profile(2));
root.children[1].state=null;typed.children[1].hasState=false;let threw=false;try{a.implement('DontPassUnlessAllPlayActionsAreDetrimental');}catch{threw=true;}
b.Implement('DontPassUnlessAllPlayActionsAreDetrimental');eq(b.failed,threw,'Original caught-exception boundary');
const report={checks,profiles:5,strategyFamilies:21,mirroredSeats:true,nativeCompiled:false,scope:'Typed WS strategy table and revised-only corrections vs direct original JS; no live WS match yet'};
fs.writeFileSync(path.join(stage,'playmaker-parity.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

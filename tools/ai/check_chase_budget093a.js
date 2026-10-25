// Replacing a zero-card leader chase must not bypass the hand-card budget.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));ctx.observe=process.argv.includes('--observe');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
const failures=[],cases=[];check=(v,n)=>{checks++;if(!v){failures.push(n);if(!observe)throw Error(n);}};
const scenarios=[
 {name:'card-deficit',own:3,enemy:5,spent:0,round:1,ownCrowns:0,enemyCrowns:0,expect:'leader'},
 {name:'cumulative-spend',own:4,enemy:2,spent:2,round:1,ownCrowns:0,enemyCrowns:0,expect:'leader'},
 {name:'cheap-first',own:6,enemy:5,spent:0,round:1,ownCrowns:0,enemyCrowns:0,expect:'card'},
 {name:'second-affordable',own:6,enemy:3,spent:1,round:1,ownCrowns:0,enemyCrowns:0,expect:'card'},
 {name:'keep-final-hand',own:3,enemy:2,spent:1,round:1,ownCrowns:0,enemyCrowns:0,expect:'leader'},
 {name:'round-two-preserve',own:3,enemy:5,spent:0,round:2,ownCrowns:1,enemyCrowns:0,expect:'leader'},
 {name:'must-survive',own:3,enemy:5,spent:0,round:2,ownCrowns:0,enemyCrowns:1,expect:'card'},
 {name:'deciding-round',own:3,enemy:5,spent:0,round:3,ownCrowns:1,enemyCrowns:1,expect:'leader'},
 {name:'no-leader',own:3,enemy:5,spent:0,round:1,ownCrowns:0,enemyCrowns:0,expect:'pass'}
];
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),rng:[g.random.InitialSeed(),g.random.DrawCount()],request:g.requestId});}
const play=CBetaGwentDuelSession.prototype.AiSimPlay;let calls=0,peakPlays=0;
CBetaGwentDuelSession.prototype.AiSimPlay=function(...args){calls++;return play.apply(this,args);};
for(const scenario of scenarios)for(const strength of [2,3,4])for(const staged of [false,true]){
 Host.strength=strength;Host.matchStrength=[strength,strength];
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=scenario.round;g.match.playerOne.crowns=scenario.enemyCrowns;g.match.playerTwo.crowns=scenario.ownCrowns;
 g.match.playerOne.hasPassed=true;g.aiSimDamp=40;g.aiChaseRound=scenario.round;g.aiChaseSpent=scenario.spent;g.aiChaseInitialHand=scenario.own+scenario.spent;
 add(g,112405,1,0,1,6);add(g,112405,1,0,2,4);
 for(let i=0;i<scenario.enemy;i++)add(g,112405,8,i,1,8);
 const hand=[];for(let i=0;i<scenario.own;i++)hand.push(add(g,112405,8,i,2,8));
 let leader=null;if(scenario.expect!=='pass'){leader=add(g,200168,64,0,2);g.leaderTemplateTwo=200168;}
 const before=state(g);
 if(staged){let ticks=0;while(true){calls=0;const ready=g.AiPreparationStep();peakPlays=Math.max(peakPlays,calls);
   check(calls<=1,'chase preparation keeps one simulated play per callback');check(state(g)===before,'chase preparation preserves live cards, match and RNG');
   if(ready)break;if(++ticks>650)throw Error('chase preparation stalled');}}
 const logs=[];Host.log=s=>logs.push(s);let ok;
 try{ok=g.OpponentStep();let attempts=0;while(!ok&&g.aiPreparationStage>0&&!g.aiPreparationReady){
   if(++attempts>3)throw Error('chase commit stalled');let ticks=0;while(!g.AiPreparationStep())if(++ticks>650)throw Error('late chase preparation stalled');ok=g.OpponentStep();}
 }finally{Host.log=null;}
 check(ok&&!g.IsFatal()&&!g.IsPending(),'real chase completes: '+scenario.name);
 const actual=g.match.playerTwo.hasPassed?'pass':leader&&leader.Snapshot().locationMask!==64?'leader':'card';
 check(actual===scenario.expect,'executed action respects the actual hand-card budget: '+scenario.name);
 check(g.CountLocation(2,8)===scenario.own-(actual==='card'?1:0),'reported plan and actual hand consumption agree: '+scenario.name);
 if(scenario.expect==='leader')check(hand.every(c=>c.Snapshot().locationMask===8),'forbidden replacement preserves every hand card');
 if(actual!=='pass'){check(g.Score(2)>g.Score(1),'chosen action really overtakes the passed opponent');
  check(g.Pass(2)&&g.Snapshot().playerTwo.crowns>scenario.ownCrowns,'direct native pass confirms the round win');}
 cases.push({scenario:scenario.name,strength,staged,actual,expected:scenario.expect,hand:g.CountLocation(2,8),selected:logs.filter(s=>/event=(SELECT|CHASE_RESOURCE|PASS)/.test(s))});
}
CBetaGwentDuelSession.prototype.AiSimPlay=play;
globalThis.result={checks,failures,cases,peakPlays,actualWitcherScript:true,nativeGameplayVerified:false};
`,ctx,{timeout:120000});
const report={fingerprint:manifest.fingerprint,...ctx.result};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(report.failures.length)process.exitCode=1;

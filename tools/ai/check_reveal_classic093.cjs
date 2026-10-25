// Full original Beta search and replay, never the ordinary Hard target picker.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs'),{personality}=require('./beta_js092/profiles.cjs');
const {BetaTurnController}=require('./beta_js092/controller.cjs');
const runtime=createRuntime(path.resolve(process.argv[2])),records=[];let checks=0;
const check=(v,n)=>{checks++;assert(v,n);};
function add(g,id,zone,index,side){const r={v:0};g.registry.Allocate(r);const c=runtime.newCard();c.Setup(g,r.v,id,side,zone,index);g.registry.Put(r.v,c);g.live.push(c);return c;}
const proto=runtime.newSession().constructor.prototype;
for(const n of ['AiMulligan','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','AiAbilityChoiceValue','AiAdjacencyIndex'])
 proto[n]=()=>{throw Error('Ordinary selector forbidden: '+n);};
for(const profile of ['p_Nilfgaard_Practice','ch_fac_skellige_1'])for(const synergy of [false,true]){
 const g=runtime.newSession();g.externalPolicyMask=3;check(g.InitializeWithPresets(72,72),'real reveal deck setup');
 for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.pendingCard=g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 const m=g.match;m.roundNumber=3;m.currentPlayerId=2;m.roundActive=m.turnActive=true;
 m.playerOne.crowns=m.playerTwo.crowns=1;m.playerOne.hasPassed=m.playerTwo.hasPassed=false;
 m.results.push({roundNumber:1,winnerMask:0x101,scoreOne:20,scoreTwo:10},{roundNumber:2,winnerMask:0x202,scoreOne:10,scoreTwo:20});
 const source=add(g,162316,8,0,2),enemy=[add(g,112405,8,0,1),add(g,113310,8,1,1)];
 const golems=[add(g,132407,16,0,2),add(g,132407,16,1,2)];
 add(g,112405,1,0,1);add(g,112405,2,0,1);
 const own=synergy?add(g,162301,8,1,2):null;
 const p=personality(profile),controller=new BetaTurnController(runtime,p,{now:()=>0});controller.start(g);
 let steps=0;while(!controller.finished){controller.step();check(++steps<20000,'bounded cooperative search/replay');}
 check(!g.IsFatal()&&!g.IsPending(),'full original turn completed');
 const shown=enemy.filter(c=>(c.Snapshot().tokenMask&64)!==0).length;
 const deployed=golems.filter(c=>(c.Snapshot().locationMask&7)!==0).length;
 check(shown===deployed,'each enemy reveal deploys a distinct available golem');
 if(!synergy){check(shown===2,'original full search reveals both enemy cards with no own reveal synergy');check(deployed===2,'both golems enter after original live replay');}
 else check(shown>0||own.Snapshot().locationMask!==8,'own reveal choices must realize a legal body synergy');
 records.push({profile,synergy,steps,enemyCardsRevealed:shown,golemsDeployed:deployed,chosen:controller.chosen.decision,ownRevealed:own?Boolean(own.Snapshot().tokenMask&64):false});
}
const report={checks,records,fingerprint:runtime.fingerprint,originalSourceHandlers:true,ordinaryPolicySelectorsAllowed:false,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

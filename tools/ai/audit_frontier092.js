// Independent exhaustive continuation of small fully visible native-rule finals.
// The oracle calls Play/Pass, never AiSimPlay, a heuristic, or the reply-tree job.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const {context:ctx,manifest}=load(path.resolve(process.argv[2]));
ctx.regression=process.argv.includes('--regression');
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
vm.runInContext('Host.strength=4;'+fixture+String.raw`
let nodes=0;
function children(g){
 const actions=[{id:0,row:0}],out=[];
 for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===2&&s.locationMask===8&&s.canBePlayed)
  for(const row of [1,2,4])actions.push({id:s.instanceId,row});}
 for(const action of actions){const h=g.AiSimClone();
  const ok=action.id?h.Play(2,action.id,action.row):h.Pass(2);
  if(ok&&!h.IsFatal()&&!h.IsPending())out.push({action,h});
 }
 return out;
}
function solve(g,depth=0){
 nodes++;if(depth>7)throw Error('oracle did not terminate');
 const m=g.Snapshot();if(m.matchWinnerMask)return m.matchWinnerMask===2?1:m.matchWinnerMask===1?-1:0;
 if(m.currentPlayerId===1)return -solve(g.AiReverseClone(),depth);
 const choices=children(g);if(!choices.length)throw Error('no legal native action');
 let best=-2;for(const {h} of choices)best=Math.max(best,solve(h,depth+1));return best;
}
const cases=[];
for(const pending of [false,true])for(const enemyCard of [112405,113301,113309])for(const ourOther of [112405,113301,113309])for(const board of [[12,14],[20,18],[8,21],[26,30]]){
 if(regression&&(pending||enemyCard!==113309||ourOther!==113301||![12,8].includes(board[0])))continue;
 const g=fixture();g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.match.roundNumber=3;g.match.playerOne.crowns=g.match.playerTwo.crowns=1;g.aiSimDamp=40;
 g.aiStartingDeckOne.Clear();g.aiStartingDeckTwo.Clear();
 add(g,112405,2,0,2,board[0]);add(g,112405,2,0,1,board[1]);
 if(pending){const active=add(g,132108,2,1,2);active.cardState.timerValue=1;}
 const mira=add(g,pending?112405:132108,8,0,2,pending?7:undefined),other=add(g,ourOther,8,1,2,ourOther===112405?9:undefined);
 const enemy=add(g,enemyCard,8,0,1,enemyCard===112405?7:undefined);
 for(const c of [mira,other,enemy])c.AddTokens(64);
 const root=g.AiSimClone(),choices=children(root);
 const results=choices.map(x=>({...x.action,value:solve(x.h)})),best=Math.max(...results.map(x=>x.value));
 const logs=[];Host.log=s=>logs.push(s);let ok;try{ok=g.OpponentStep();}finally{Host.log=null;}
 if(!ok||g.IsFatal()||g.IsPending())throw Error('policy failed');
 let chosen={id:0,row:0};
 for(const c of [mira,other]){const s=c.Snapshot();if(s.locationMask!==8)chosen={id:s.instanceId,row:s.locationMask};}
 // A terminal can move played cards to the grave; use the logged selected id.
 const line=logs.find(s=>s.includes('event=SELECT '));
 if(line){const id=Number(/card=(\d+)/.exec(line)[1]);chosen.id=id;
  if(![1,2,4].includes(chosen.row))chosen.row=results.find(x=>x.id===id)?.row||0;}
 const value=results.find(x=>x.id===chosen.id&&x.row===chosen.row)?.value;
 if(value===undefined)throw Error('selected action absent from oracle '+JSON.stringify({chosen,results,line}));
 cases.push({pending,enemyCard,ourOther,board,best,selectedValue:value,chosen,optimal:value===best,selection:line||logs.find(s=>s.includes('event=PASS ')),results});
}
if(regression){check(cases.length===2,'both independently solved regression finals executed');check(cases.every(c=>c.best===1&&c.optimal),'each selected action preserves the available native-rule win');}
globalThis.report={cases,nodes,checks,optimal:cases.filter(c=>c.optimal).length,total:cases.length,actualNativeRuleContinuation:true,fullNativeGameTested:false};
`,ctx,{timeout:240000});
const report={fingerprint:manifest.fingerprint,...ctx.report};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));
console.log(JSON.stringify({fingerprint:manifest.fingerprint,optimal:report.optimal,total:report.total,nodes:report.nodes,failures:report.cases.filter(c=>!c.optimal)}));

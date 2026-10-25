// Replay recorded retail actions, never substitute a new policy for historical decisions.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const [snapshot,input,output]=process.argv.slice(2);if(!output)throw Error('snapshot log output-directory');
fs.mkdirSync(output,{recursive:true});
const ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
vm.runInContext(String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.tunes=[{},{}];
function retailStart(f){Host.random=()=> (Number(f.seed)+0.1)/2147483647;__simDepthHost=0;
 active=new CBetaGwentDuelSession();if(!active.InitializeWithPresets(Number(f.ownPreset),Number(f.enemyPreset),Number(f.ownLeader),Number(f.enemyLeader)))throw Error('initialization');active.recordVisuals=false;
 if(active.live.Size()!==Number(f.cards)||active.roundStarter!==Number(f.starter))throw Error('Initial native deal is not reproduced: card count/starter differ. Do not treat this as a historical state.');}
function retailAction(f){const n=k=>Number(f[k]);
 switch(f.action){
 case 'play':return active.Play(1,n('card'),n('row'));
 case 'play_before':return active.PlayBefore(1,n('card'),n('row'));
 case 'play_target':return active.PlayOnTarget(1,n('card'),n('row'));
 case 'pending_place_before':return active.SelectPlacementBefore(n('card'),n('row'));
 case 'ability_row':return active.SelectRow(n('card'),Math.floor(n('row')/8),n('row')%8);
 case 'leader':return active.UseLeader(1);
 case 'pass':return active.Pass(1);
 case 'nextRound':return active.BeginNextRound();
 default:throw Error('unknown action '+f.action);
 }}
function retailSelect(f,finish){if(!active.IsPending())return false;
 const id=Number(f.id),item=Number(f.item);
 if(active.IsMulligan())return finish?active.FinishMulligan(id):active.SelectMulligan(id,item);
 if(active.IsTemplateChoice()&&!finish)return active.SelectTemplateChoice(id,item);
 return finish?active.FinishTarget(id):active.SelectTarget(id,item);}
function retailAIPlay(f,id){return active.PlayAtIndex(2,Number(id),Number(f.row),Number(f.index));}
function retailView(){const m=active.Snapshot();return {round:m.roundNumber,ownScore:active.Score(2),enemyScore:active.Score(1),ownHand:active.CountLocation(2,8),enemyHand:active.CountLocation(1,8),draws:active.random.DrawCount(),fatal:active.IsFatal(),message:active.GetMessage()};}
`,ctx);
const lines=fs.readFileSync(input,'utf8').split(/\r?\n/),games=[];let game=null,selected=null;
for(let i=0;i<lines.length;i++){
 const text=lines[i].split('[BetaGwent] ')[1];if(!text)continue;
 const fields=Object.fromEntries([...text.matchAll(/(\w+)=([^\s]+)/g)].map(m=>[m[1],m[2]]));ctx.f=fields;
 if(text.startsWith('DUEL_STARTED ')){
  game={number:games.length+1,start:fields,actions:[],verifiedDecisions:[],errors:[]};games.push(game);selected=null;
  try{vm.runInContext('retailStart(f)',ctx);}catch(e){game.errors.push({line:i+1,error:String(e)});}continue;
 }
 if(!game||game.errors.length)continue;
 try{
  if(text.startsWith('BOARD_INTENT ')){
   const ok=vm.runInContext('retailAction(f)',ctx);game.actions.push({line:i+1,...fields,accepted:ok});
  }else if(text.startsWith('UI_REQUEST_SELECT ')||text.startsWith('UI_REQUEST_FINISH ')){
   ctx.finish=text.startsWith('UI_REQUEST_FINISH ');vm.runInContext('retailSelect(f,finish)',ctx);
  }else if(text.startsWith('AI_REASON ')&&fields.event==='BEGIN'){
   const view=vm.runInContext('retailView()',ctx);const mismatch=Object.keys(view).filter(k=>fields[k]!==undefined&&Number(fields[k])!==view[k]);
   if(mismatch.length)throw Error('state mismatch '+JSON.stringify({expected:fields,actual:view,mismatch}));
   const state=ctx.bridge.dump(),file=`match-${game.number}-decision-${fields.decision}.json.gz`;
   fs.writeFileSync(path.join(output,file),zlib.gzipSync(JSON.stringify({line:i+1,begin:fields,state})));
   game.verifiedDecisions.push({line:i+1,...fields,file});
  }else if(text.startsWith('AI_REASON ')&&fields.event==='SELECT'){
   if(fields.action==='leader')vm.runInContext('active.UseLeader(2)',ctx);else selected=Number(fields.card);
  }else if(text.startsWith('AI_REASON ')&&fields.event==='PASS'){
   if(!vm.runInContext('active.Pass(2)',ctx))throw Error('recorded AI pass rejected');
  }else if(text.startsWith('DUEL_PLAY ')&&fields.player==='2'){
   if(!selected)throw Error('missing AI selection');ctx.selected=selected;
   if(!vm.runInContext('retailAIPlay(f,selected)',ctx))throw Error('recorded AI play rejected');selected=null;
  }
  if(vm.runInContext('active.IsFatal()',ctx))throw Error(vm.runInContext('active.GetMessage()',ctx));
 }catch(e){game.errors.push({line:i+1,text,error:String(e.stack||e)});}
}
fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({snapshot,input,games},null,2));
console.log(JSON.stringify(games.map(g=>({number:g.number,verifiedDecisions:g.verifiedDecisions.length,firstError:g.errors[0]})),null,2));

// Replay recorded retail actions, never substitute a new policy for historical decisions.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const observables=require('./retail_position094.cjs');
const [snapshot,input,output]=process.argv.slice(2);if(!output)throw Error('snapshot log output-directory');
if(fs.existsSync(output))throw Error('Use a fresh replay output directory');
const recoverShell=process.argv.includes('--replay-auto-pass'),customDeckFromLog=process.argv.includes('--custom-deck-from-log'),crypto=require('crypto');
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
for(const [name,hash]of Object.entries(manifest.snapshotFiles))if(digest(path.join(snapshot,name))!==hash)throw Error('Frozen input changed '+name);
fs.mkdirSync(output,{recursive:true});
const ctx=vm.createContext({console,observables});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(snapshot,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),ctx);
vm.runInContext(String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.seatIndex=1;Host.tunes=[{},{}];
function retailStart(f){Host.random=()=> (Number(f.seed)+0.1)/2147483647;__simDepthHost=0;
 active=new CBetaGwentDuelSession();let initialized;
 if(f.customCards){
  const own=[],enemy={v:[]};for(const id of f.customCards)own.push(id);
  if(!BetaGwentDuelPresetDeck(Number(f.enemyPreset),enemy))throw Error('opponent preset');
  initialized=active.InitializeWithDecks(own,enemy.v,Number(f.ownLeader),Number(f.enemyLeader),Number(f.ownPreset),Number(f.enemyPreset));
 }else initialized=active.InitializeWithPresets(Number(f.ownPreset),Number(f.enemyPreset),Number(f.ownLeader),Number(f.enemyLeader));
 if(!initialized)throw Error('initialization');active.recordVisuals=false;
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
  game={number:games.length+1,start:fields,actions:[],counterMatches:[],verifiedDecisions:[],inferredShellTransitions:[],errors:[]};games.push(game);selected=null;
  try{
   if(customDeckFromLog&&Number(fields.ownPreset)>=1001){
    const following=lines.slice(i+1),nextGame=following.findIndex(s=>s.includes('[BetaGwent] DUEL_STARTED '));
    const position=following.slice(0,nextGame<0?following.length:nextGame).find(s=>/AI_POSITION schema=1 decision=1 /.test(s));
    const known=position&&/\bknown=([\d,]+)(?:\s|$)/.exec(position);
    if(!known)throw Error('Custom deck requires the first logged starting composition; never guess missing cards');
    fields.customCards=known[1].split(',').map(Number);
    if(fields.customCards.length<25||fields.customCards.length>40||fields.customCards.some(n=>!Number.isSafeInteger(n)||n<=0))throw Error('Malformed custom starting composition');
    game.customDeckSource='AI_POSITION decision=1 known; order and every observable must still match';
   }
   vm.runInContext('retailStart(f)',ctx);
  }catch(e){game.errors.push({line:i+1,error:String(e)});}continue;
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
   game.counterMatches.push({line:i+1,...fields});
   game.pendingPosition={line:i+1,begin:fields,state,file,headerChecked:false,seen:[]};
  }else if(text.startsWith('AI_POSITION ')){
   if(recoverShell){const transition=vm.runInContext('observables.recoverShellPass(active,f)',ctx);if(transition){
    game.inferredShellTransitions.push({line:i+1,...transition});
    if(game.pendingPosition)game.pendingPosition.state=ctx.bridge.dump();
   }}
   const mismatch=vm.runInContext('observables.compareHeader(active,f)',ctx);
   if(mismatch.length)throw Error('logged position header mismatch '+JSON.stringify(mismatch));
   if(!game.pendingPosition)throw Error('Position without decision');
   game.pendingPosition.headerChecked=true;game.pendingPosition.cardCount=Number(fields.cardCount);
  }else if(text.startsWith('AI_POSITION_CARDS ')){
   const pending=game.pendingPosition;if(!pending?.headerChecked)throw Error('Cards without checked position header');
   for(const token of text.split(/\s+/)){
    if(!/^-?\d+(?::-?\d+){12}$/.test(token))continue;
    const tuple=token.split(':').map(Number);ctx.loggedTuple=tuple;
    const mismatch=vm.runInContext('observables.compareCard(active,loggedTuple)',ctx);
    if(mismatch.length)throw Error('logged card mismatch '+JSON.stringify(mismatch));
    if(pending.seen.includes(tuple[0]))throw Error('Duplicate logged card');pending.seen.push(tuple[0]);
   }
   if(pending.seen.length===pending.cardCount){
    fs.writeFileSync(path.join(output,pending.file),zlib.gzipSync(JSON.stringify({line:pending.line,begin:pending.begin,state:pending.state,loggedObservablesVerified:true,inferredShellTransitions:[...game.inferredShellTransitions],historicalRuntimeVerified:false})));
    game.verifiedDecisions.push({line:pending.line,...pending.begin,file:pending.file,loggedObservablesVerified:true});
    game.pendingPosition=null;
   }
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
const complete=games.length>0&&games.every(g=>!g.errors.length&&g.verifiedDecisions.length===g.counterMatches.length);
fs.writeFileSync(path.join(output,'report.json'),JSON.stringify({schema:2,complete,snapshot,input,games,recoverShell,customDeckFromLog,inputSha256:digest(input),manifestSha256:digest(path.join(snapshot,'manifest.json')),checkerSha256:digest(__filename),observableCheckerSha256:digest(require.resolve('./retail_position094.cjs')),historicalRuntimeVerified:false,scope:'Counters and complete logged position observables are checked separately. Any automatic shell transition is explicitly labelled as inferred. Unlogged queues, private AI cache state, host timing and executable identity are not verified.'},null,2));
console.log(JSON.stringify(games.map(g=>({number:g.number,verifiedDecisions:g.verifiedDecisions.length,firstError:g.errors[0]})),null,2));
if(!complete)process.exitCode=1;

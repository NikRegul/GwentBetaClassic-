'use strict';
// Cancellation expectations come from the original request/ability/stack classes.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt),snap=c=>c.Snapshot(),id=c=>snap(c).instanceId;
let checks=0;const failures=[],cases=[];function check(ok,n){checks++;if(!ok)failures.push(n);}
function state(g){return JSON.stringify({match:g.Snapshot(),cards:g.live.map(c=>c.Snapshot()),hazards:g.weather.hazards});}
function flush(g){g.events.Flush();g.FlushEffects();g.FlushDeaths();}
function queen(side){const g=fixture(side);g.mulliganReactions=true;
 const targets=[0,1,2].map(i=>id(add(g,132209,side,1,i,5+i)));
 const q=id(add(g,201743,side,64,0,7));g[side===1?'leaderTemplateOne':'leaderTemplateTwo']=201743;
 return {g,q,targets};}
for(const side of [1,2]){
 const {g,q}=queen(side),before=state(g),draws=g.random.DrawCount();
 check(g.UseLeader(side)&&g.SelectRow(g.requestId,side,2),'Queen placement '+side);
 check(g.CanCancelTargetRequest098(),'Queen before first consume cancellable '+side);
 const request=g.requestId;
 check(!g.CancelTargetRequest098(request+1,side)&&!g.CancelTargetRequest098(request,3-side),'wrong request/seat rejected '+side);
 check(g.CancelTargetRequest098(request,side),'Queen cancel accepted '+side);
 check(state(g)===before,'Queen restores cards, power, armor, hand order, weather and turn '+side);
 check(g.FindCard(q).Snapshot().locationMask===64&&g.CanAct(side)&&!g.IsPending(),'leader available again '+side);
 check(!g.CancelTargetRequest098(request,side)&&!g.SelectTarget(request,q),'duplicate cancel and stale choice rejected '+side);
 check(g.random.DrawCount()===draws,'cancel without randomness consumes no RNG '+side);
 check(g.FindCard(q).game===g&&g.weather.game===g&&g.monsters.game===g,'restored graph points to live session '+side);
 // Repeated checkpoints must not reuse an old clone epoch or mutate a saved graph.
 for(let n=0;n<3;n++){
  check(g.UseLeader(side)&&g.SelectRow(g.requestId,side,1)&&g.CancelTargetRequest098(g.requestId,side),'repeat Queen cancel '+side+'/'+n);
  check(state(g)===before,'repeat leaves exact gameplay state '+side+'/'+n);
 }
 check(g.UseLeader(side)&&g.SelectRow(g.requestId,side,2),'Queen can be played after cancellation '+side);
 const target=g.pendingIds[0],old=snap(g.FindCard(target)).power.currentPower;
 check(g.SelectTarget(g.requestId,target),'first consume accepted '+side);
 check(!g.CanCancelTargetRequest098()&&!g.CancelTargetRequest098(g.requestId,side),'first applied consume closes cancellation '+side);
 check(snap(g.FindCard(q)).power.currentPower===7+old,'first consume remains applied '+side);
 cases.push({side,card:201743,mode:'cancel, repeat, commit first consume'});
}
// No global RNG rewind: original ExecutionStack.Rollback never restores RandomGenerator.
{
 const {g}=queen(1);g.UseLeader(1);g.SelectRow(g.requestId,1,2);g.random.NextBounded(97);
 const stream=g.random,draws=stream.DrawCount(),oracle=rt.cloneSession(g).random.NextBounded(97);
 check(g.CancelTargetRequest098(g.requestId,1),'cancel after pure random calculation');
 check(g.random===stream&&g.random.DrawCount()===draws&&g.random.NextBounded(97)===oracle,'original RNG stream and next value retained');
}
// Ordinary directed damage, boost and weather; both seats use the same rule API.
for(const side of [1,2])for(const tid of [162102,162315,113301]){
 const g=fixture(side);g.mulliganReactions=true;add(g,132209,side,1,0,15);add(g,132209,3-side,2,0,20);
 const source=id(add(g,tid,side,8,2)),before=state(g);
 check(g.Play(side,source,1),'directed play accepted '+side+'/'+tid);
 check(g.IsPending()&&g.CanCancelTargetRequest098(),'directed request can cancel '+side+'/'+tid);
 check(g.CancelTargetRequest098(g.requestId,side),'directed cancellation '+side+'/'+tid);
 check(state(g)===before&&g.CanAct(side),'directed cancellation restores full gameplay '+side+'/'+tid);
 cases.push({side,card:tid,mode:'cancel directed play'});
}
// RequestCardChoicesAction.InitCommon hard-codes CanCancel=false (tutors/creation).
for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;add(g,132403,side,16,0);add(g,132209,side,16,1);
 const source=id(add(g,162314,side,8,0));g.Play(side,source,1);
 check(g.IsPending()&&!g.CanCancelTargetRequest098()&&!g.CancelTargetRequest098(g.requestId,side),'Emissary choice cannot cancel '+side);
}
// Nested units return to placement, never to the hand or to choosing another tutor result.
{
 const g=fixture(1);g.mulliganReactions=true;add(g,132209,1,1,0,15);add(g,132209,2,1,0,20);
 const child=id(add(g,162308,1,16,0)),parent=id(add(g,162314,1,8,0));g.Play(1,parent,1);
 check(g.IsPending()&&g.SelectTarget(g.requestId,child),'Emissary child selected');
 if(g.pendingRally)g.SelectRow(g.requestId,1,2);flush(g);
 check(g.IsPending()&&g.CanCancelTargetRequest098()&&g.CancelTargetRequest098(g.requestId,1),'nested unit target cancellation accepted');
 check(g.pendingRally&&id(g.pendingRally)===child&&g.playStack.length===1&&id(g.playStack[0])===parent&&!g.CanAct(1),'same child awaits placement and parent stays committed');
 check(g.SelectRow(g.requestId,1,1)&&g.CanCancelTargetRequest098(),'nested child may be placed again');
 check(g.SelectTarget(g.requestId,g.pendingIds[0])&&!g.CanCancelTargetRequest098(),'nested child damage commits normally');
}
const base=path.resolve(__dirname,'../../BetaGwent/build-inputs/reference/beta-original-csharp');
const names=['GwentGameplay/RequestCardTargetsAction.cs','GwentGameplay/RequestLocationTargetsAction.cs','GwentGameplay/RequestCardChoicesAction.cs',
 'GwentGameplay/ARequestTargetsNode.cs','GwentGameplay/ARequestTargetsAction.cs','GwentGameplay/AbilityInstance.cs','GwentGameplay/PlayedAbilityInstance.cs',
 'GwentGameplay/ExecutionStack.cs','GwentGameplay/RequestPlayCardAction.cs','GwentGameplay/BoardManager.cs','GwentVisuals/SelectTargetsHandlerComponent.cs'];
const sourceEvidence=names.map(n=>({file:n,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(base,n))).digest('hex')}));
const report={checks,failures,cases,sourceEvidence,fingerprint:rt.fingerprint,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[3]){if(fs.existsSync(process.argv[3]))throw Error('fresh report required');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({checks,failures,cases:cases.length}));if(failures.length)process.exitCode=1;

'use strict';
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt),id=c=>c.Snapshot().instanceId;
let checks=0;const failures=[];const check=(v,n)=>{checks++;if(!v)failures.push(n);};
for(const side of [1,2])for(const onBoard of [false,true]){
 const g=fixture(side);g.mulliganReactions=true;g.recordVisuals=true;
 const target=id(add(g,132209,3-side,1,0,20)),roach=id(add(g,112210,side,onBoard?2:16,0,4)),source=id(add(g,132102,side,8,0,9));
 const before=JSON.stringify(g.live.map(c=>c.Snapshot())),draws=g.random.DrawCount();
 check(g.Play(side,source,1),'Imlerith starts '+side+'/'+onBoard);
 check(g.deferredPlay099&&g.TentativeSource099()===source&&g.CanCancelTargetRequest098(),'target request stays tentative '+side+'/'+onBoard);
 check(g.FindCard(roach).Snapshot().locationMask===(onBoard?2:16),'Roach unchanged before target '+side+'/'+onBoard);
 check(g.VisualSnapshot()[side===1?'scoreOne':'scoreTwo']===(onBoard?4:0),'tentative body absent from displayed score '+side+'/'+onBoard);
 check(g.random.DrawCount()===draws&&!g.visualFrames.some(f=>f.kind===1),'no confirmed play/voice/history/RNG before target '+side+'/'+onBoard);
 check(g.CancelTargetRequest098(g.requestId,side)&&JSON.stringify(g.live.map(c=>c.Snapshot()))===before,'cancel restores only tentative placement '+side+'/'+onBoard);
 check(g.Play(side,source,1)&&g.SelectTarget(g.requestId,target),'replay and select target '+side+'/'+onBoard);
 check(!g.fatal&&!g.IsPending()&&!g.deferredPlay099,'confirmation resolves normally '+side+'/'+onBoard);
 check((g.FindCard(roach).Snapshot().locationMask&7)!==0&&g.FindCard(target).Snapshot().power.currentPower===16,'Roach then directed hit after commitment '+side+'/'+onBoard);
 check(g.visualFrames.filter(f=>f.kind===1&&f.sourceId===source).length===1,'one confirmed history/play event '+side+'/'+onBoard);
}
for(const side of [1,2]){
 const g=fixture(side);g.mulliganReactions=true;const child=id(add(g,162308,side,16,0));add(g,132209,3-side,1,0,20);
 const source=id(add(g,162314,side,8,0));check(g.Play(side,source,1),'Emissary start '+side);
 check(g.GetRequestSnapshot().limits.minimum===1&&!g.FinishTarget(g.requestId),'Emissary cannot finish empty with a legal offer '+side);
 check(g.SelectTarget(g.requestId,child)&&g.pendingRally&&id(g.pendingRally)===child,'Emissary plays selected offer '+side);
 check(!g.deferredPlay099,'PlayCards commits parent before child placement '+side);
}
// Separate armor-depletion flag survives merged attack frames, including a hit that also loses strength.
{
 const g=fixture(1);g.recordVisuals=true;const a=add(g,132209,2,1,0,20,3),b=add(g,132209,2,1,1,20,2);
 g.MonsterPower(a,a,-1);g.FlushEffects();check(!g.visualFrames.some(f=>f.armorBroken099),'partial armour hit does not break');
 g.MonsterPower(a,a,-5);g.FlushEffects();check(g.visualFrames.some(f=>f.armorBroken099),'armour and strength hit retains armor-break signal');
 g.MonsterPower(a,b,-3);g.FlushEffects();check(g.visualFrames.some(f=>f.armorBroken099),'subsequent attack does not erase depletion signal');
}
const report={checks,failures,fingerprint:rt.fingerprint,actualWitcherScript:true,nativeGameTested:false,
 scope:'Pending-target commit boundary, logged Imlerith/Roach shape, mandatory Emissary and armor-impact metadata.'};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

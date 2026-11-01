'use strict';
// Explicit numbers/filter constants below come from the 25 source graphs,
// recorded before reading these handlers, not from runtime definitions.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const sourceEvidence=require('./source_power096.cjs');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[];const snap=c=>c.Snapshot(),id=c=>snap(c).instanceId,check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
function flush(g){g.FlushEffects();g.FlushDeaths();}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,19573+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function begin(g,tid,side){g.mulliganReactions=true;const source=add(g,tid,side,8,40);check(g.Play(side,id(source),2),'real deploy');return source;}
function choose(g,c){check(g.IsPending()&&g.pendingIds.includes(id(c)),'exact target offered');if(!g.IsPending())return false;check(g.SelectTarget(g.requestId,id(c)),'selection accepted');flush(g);return true;}
const singles=[
 [112106,0,'damage',5],[112214,0,'weaken',4],[113301,0,'damage',9],[113306,0,'damage',13],[113310,0,'boost',10],[113313,1,'multiply',150],
 [142317,1,'boost',7],[162313,1,'boost',5],[162315,1,'boost',12],[200299,1,'boost',6],[200540,2,'damage',4]
];
for(const [tid,filter,op,amount]of singles)for(const side of [1,2])for(const targetSide of [side,3-side])for(const armor of [0,3,20])run(tid,side,`${targetSide}/${armor}`,g=>{
 const target=add(g,132209,targetSide,1,0,30,armor),spare=add(g,132209,3-targetSide,4,0,30,armor),hidden=add(g,142307,targetSide,1,1,20),immune=add(g,132209,targetSide,1,2,20,0,256),grave=add(g,132209,targetSide,32,0,20);target.ChangeBasePower(12-snap(target).power.basePower,true);target.power.SetPermanentPowerAndArmor(3,armor);target.power.SetCurrentPair(30,armor);const before=snap(target),source=begin(g,tid,side);
 const eligible=filter===0||filter===1&&targetSide===side||filter===2&&targetSide!==side;check(g.pendingIds.includes(id(target))===eligible,'graph side filter');check(!g.pendingIds.includes(id(hidden))&&!g.pendingIds.includes(id(immune))&&!g.pendingIds.includes(id(grave)),'Ignore264 and Active filter');check(!g.pendingIds.includes(id(source)),'executing instance excluded');check(g.GetRequestSnapshot().limits.minimum===1,'exact single target required');
 if(!eligible){check(JSON.stringify(snap(target).power)===JSON.stringify(before.power),'excluded target unchanged');return;}check(!g.FinishTarget(g.requestId),'mandatory target cannot be skipped');choose(g,target);const s=snap(target),wanted=op==='damage'?30-Math.max(0,amount-armor):op==='boost'?30+amount:op==='multiply'?45:26;
 check(s.power.currentPower===wanted,'source formula on current power',{actual:s.power.currentPower,wanted});check(s.power.basePower===(op==='weaken'?8:12),'base versus current target');check(s.power.permanentPower===3,'permanent retained');check(s.power.armor===(op==='damage'?Math.max(0,armor-amount):armor),'armor used only by current damage');check(s.tokenMask===before.tokenMask,'power action retains tokens');check(s.positionPlayerId===before.positionPlayerId&&s.locationMask===before.locationMask,'power does not move surviving instance');check(g.random.DrawCount()===0,'no RNG');check(!g.IsPending(),'complete');
});
for(const side of [1,2])for(const base of [1,3,4,8])run(112214,side,'weaken clamp'+base,g=>{
 const target=add(g,132209,3-side,1,0,20,9);target.ChangeBasePower(base-snap(target).power.basePower,true);target.power.SetPermanentPowerAndArmor(-base,9);target.power.SetCurrentPair(20,9);begin(g,112214,side);choose(g,target);const s=snap(target);check(s.power.basePower===Math.max(0,base-4),'base clamped0');check(s.power.permanentPower===-Math.max(0,base-4),'negative permanent clamped to negative new base');check(s.power.currentPower===16&&s.power.armor===9,'current offset uses requested-4 delta, armor ignored');
});
// Medic collects both distinct targets first. Original ARequestTargetsAction
// clamps two to one when only a single other unit is available.
for(const side of [1,2])for(const count of [1,2])run(142301,side,'targets'+count,g=>{
 const targets=Array.from({length:count},(_,i)=>add(g,132209,side,1,i,20,4)),enemy=add(g,132209,3-side,4,0,20),source=begin(g,142301,side);check(!g.pendingIds.includes(id(source))&&!g.pendingIds.includes(id(enemy)),'own other targets only');choose(g,targets[0]);if(count===2){check(snap(targets[0]).power.currentPower===20,'first pick waits until second selected');check(!g.pendingIds.includes(id(targets[0])),'same instance cannot be repeated');choose(g,targets[1]);}check(targets.every(c=>snap(c).power.currentPower===23&&snap(c).power.armor===4),'all chosen units gain3 retaining armor');check(!g.IsPending(),'complete');
});
for(const side of [1,2])for(const mode of ['repeat','kill-first','friendly'])run(142310,side,mode,g=>{
 const target=add(g,132209,mode==='friendly'?side:3-side,1,0,mode==='kill-first'?3:30),other=add(g,132209,3-side,4,0,30);begin(g,142310,side);choose(g,target);check(g.IsPending(),'second request');
 if(mode==='kill-first'){check(!g.pendingIds.includes(id(target)),'dead first target not in refreshed second pool');choose(g,other);check(snap(other).power.currentPower===29,'second1damage');}
 else{check(snap(target).power.currentPower===27,'first3damage applied before second request');check(g.pendingIds.includes(id(target)),'same surviving instance may be selected again');choose(g,target);check(snap(target).power.currentPower===26,'total3+1damage on repeated instance');}check(g.random.DrawCount()===0,'no RNG');
});
for(const side of [1,2])for(const mode of ['decline','normal','revealed'])run(142312,side,mode,g=>{
 const target=add(g,132209,side,8,0,20,4,mode==='revealed'?64:0),enemy=add(g,132209,3-side,8,0,20),spell=add(g,113205,side,8,1),leader=add(g,200163,side,64,0),before=snap(target);begin(g,142312,side);check(g.pendingIds.includes(id(target))&&!g.pendingIds.includes(id(enemy))&&!g.pendingIds.includes(id(spell))&&!g.pendingIds.includes(id(leader)),'own Unit hand pool');
 if(mode==='decline'){check(g.FinishTarget(g.requestId),'CardChoice0 may decline');flush(g);check(JSON.stringify(snap(target))===JSON.stringify(before),'declined has no effect');}else{choose(g,target);check(snap(target).power.currentPower===23&&snap(target).power.basePower===before.power.basePower&&snap(target).power.armor===4,'hand current boost3');check(snap(target).locationMask===8&&snap(target).locationIndex===0&&snap(target).tokenMask===before.tokenMask,'no movement/reveal/reset');}check(g.random.DrawCount()===0,'no RNG');
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceEvidence,scope:'14 cards: explicit current/base formulas, filters, mandatory target/optional hand choice, changed power and armor, multiple-target collection, repeated-hit refresh. All other branches remain open.',semanticCoverageComplete:false};if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh output');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,14),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;

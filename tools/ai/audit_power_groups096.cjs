'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const sourceEvidence=require('./source_power096.cjs');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2])),{fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[];const snap=c=>c.Snapshot(),id=c=>snap(c).instanceId,check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
function flush(g){g.FlushEffects();g.FlushDeaths();}
function run(tid,side,mode,body){label=tid+'/'+side+'/'+mode;const g=fixture(side,85317+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id:tid,side,mode});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function begin(g,tid,side){g.mulliganReactions=true;const source=add(g,tid,side,8,40,10);check(g.Play(side,id(source),2),'real play');flush(g);return source;}
function choose(g,c){check(g.IsPending()&&g.pendingIds.includes(id(c)),'pivot offered');if(!g.IsPending())return;check(g.SelectTarget(g.requestId,id(c)),'pivot selected');flush(g);}
for(const tid of [112401,112402,113204])for(const side of [1,2])for(const armor of [0,1,4])run(tid,side,'both sides armor'+armor,g=>{
 const all=[];for(const seat of [side,3-side])for(const row of [1,2,4])for(const mode of ['plain','gold','immune','hidden']){const c=add(g,mode==='gold'?112101:mode==='hidden'?142307:132209,seat,row,all.filter(x=>snap(x).positionPlayerId===seat&&snap(x).locationMask===row).length,20,armor,mode==='immune'?256:0);all.push(c);}
 const source=begin(g,tid,side);if(tid!==113204)check(snap(source).power.currentPower===10,'owner excluded');for(const c of all){const s=snap(c),affected=(s.tokenMask&8)===0&&(tid!==113204||s.positionPlayerId!==side),delta=!affected?0:tid===112401?2:-Math.max(0,(tid===112402?2:1)-armor);check(s.power.currentPower===20+delta,'captured all-tier row formula '+id(c));check(s.power.armor===(affected&&tid!==112401?Math.max(0,armor-(tid===112402?2:1)):armor),'armor semantics '+id(c));}check(g.random.DrawCount()===0,'no RNG');
});
for(const tid of [112403,112404])for(const side of [1,2])for(const row of [1,2,4])run(tid,side,'four neighbours row'+row,g=>{
 g.mulliganReactions=true;const units=Array.from({length:8},(_,i)=>add(g,i===5?142307:132209,side,row,i,20,1,i===2?256:0)),other=add(g,132209,side,row===1?4:1,0,20),source=add(g,tid,side,8,0,10);check(g.PlayBefore(side,id(source),id(units[4])),'real insertion at index4');flush(g);check(snap(source).locationIndex===4&&snap(source).power.currentPower===10,'owner position and no self effect');for(const c of units){const s=snap(c),hit=[2,3,5,6].includes(s.locationIndex)&&(s.tokenMask&8)===0,delta=hit?(tid===112403?2:-1):0;check(s.power.currentPower===20+delta,'four shape neighbours index'+s.locationIndex);check(s.power.armor===(hit&&tid===112404?0:1),'armored neighbour delta');}check(snap(other).power.currentPower===20,'other row unchanged');
});
for(const side of [1,2])for(const targetSide of [side,3-side])for(const row of [1,2,4])run(113202,side,'half/'+targetSide+'/'+row,g=>{
 const bronze=add(g,132403,targetSide,row,0,23,7),silver=add(g,132209,targetSide,row,1,9,4),gold=add(g,112101,targetSide,row,2,23,7),immune=add(g,132403,targetSide,row,3,23,7,256),hidden=add(g,142307,targetSide,row,4,23,7),other=add(g,132403,targetSide,row===1?4:1,0,23,7);begin(g,113202,side);check(g.SelectRow(g.requestId,targetSide,row),'either-side exact row accepted');flush(g);for(const [c,want]of [[bronze,11],[silver,4],[gold,23],[immune,11],[hidden,23],[other,23]]){check(snap(c).power.currentPower===want,'50% floor/current-tier filter');check(snap(c).power.armor===(c===silver?4:7),'halving ignores and retains armor');}check(g.random.DrawCount()===0,'no RNG');
});
for(const tid of [113207,113311])for(const side of [1,2])for(const targetSide of [side,3-side])run(tid,side,'shape/'+targetSide,g=>{
 const units=Array.from({length:9},(_,i)=>add(g,i===5?142307:132209,targetSide,1,i,20,1,i===3?256:0)),other=add(g,132209,targetSide,4,0,20),pivot=units[4],radius=tid===113207?2:1,states=[];const orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...args)=>{if(args[4]===2)states.push(units.filter(c=>Math.abs(snap(c).locationIndex-4)<=radius&&(snap(c).tokenMask&8)===0).map(c=>snap(c).power.currentPower));return orig(...args);};begin(g,tid,side);choose(g,pivot);
 for(const c of units){const s=snap(c),hit=Math.abs(s.locationIndex-4)<=radius&&(s.tokenMask&8)===0;check(s.power.currentPower===(hit?23:20),'secondary shape: hidden excluded, immune allowed index'+s.locationIndex);check(s.power.armor===(hit&&tid===113311?3:1),'secondary shape armor index'+s.locationIndex);}
 if(tid===113311)check(states.length>0&&states.every(s=>s.every(v=>v===23)),'all boosts precede first armor action');check(snap(other).power.currentPower===20,'other row unaffected');check(g.random.DrawCount()===0,'no RNG');
});
// A spell pushed into play by its own unit keeps that unit inside the shape: the source
// GetCardsInShape filters Ambush only, never the execution stack. Keira must be able to
// boost herself with her own Thunder, also when she is the only body in the row.
for(const side of [1,2])for(const seats of [4,0])run(122108,side,'creator in shape seats'+seats,g=>{
 g.mulliganReactions=true;
 const neighbours=Array.from({length:seats},(_,i)=>add(g,132209,side,1,i,20,1));const keira=add(g,122108,side,8,40,7);
 check(g.Play(side,id(keira),1),'Keira plays onto the shaped row');flush(g);
 check(g.pendingChoice&&g.pendingIds.includes(113311),'Thunder is one of the three options');
 check(g.SelectTemplateChoice(g.requestId,113311),'Thunder selected from the choice list');flush(g);
 check(g.pendingIds.includes(id(keira)),'the executing parent is offered as a pivot');choose(g,keira);
 const pivot=snap(keira);check(!!(pivot.locationMask&7),'Keira remains on the row');
 for(const c of neighbours){const s=snap(c),hit=Math.abs(s.locationIndex-pivot.locationIndex)<=1;
  check(s.power.currentPower===(hit?23:20)&&s.power.armor===(hit?3:1),'neighbour window index'+s.locationIndex);}
 check(snap(keira).power.currentPower===10&&snap(keira).power.armor===2,'the creating unit is boosted by the spell it created');
 check(g.random.DrawCount()===0,'no RNG in the shape resolution');
});
for(const side of [1,2])for(const count of [0,1,4,6])run(122202,side,'shuffle'+count,g=>{
 const order=count===6?[5,1,4,0,3,2]:Array.from({length:count},(_,i)=>i),targets=order.map(i=>add(g,132209,side,1,i,20,2,i===1?256:0)),hidden=add(g,142307,side,4,0,20),enemy=add(g,132209,3-side,1,0,20),draws=[];const orig=g.random.NextBounded.bind(g.random);g.random.NextBounded=n=>{const v=orig(n);draws.push({n,v});return v;};const source=begin(g,122202,side),physical=[...targets].sort((a,b)=>snap(a).locationIndex-snap(b).locationIndex),expected=[...physical];
 check(draws.length===Math.max(0,count-1),'N-1 shuffle RNG, excludes executing owner',{draws,count});let correct=draws.length===Math.max(0,count-1);for(let n=count-1,k=0;n>0;n--,k++){if(draws[k]?.n!==n+1){correct=false;break;}const j=draws[k].v;[expected[n],expected[j]]=[expected[j],expected[n]];}check(correct,'source Fisher-Yates bounds');if(correct){const chosen=expected.slice(0,5);for(const c of targets)check(snap(c).power.currentPower===(chosen.includes(c)?23:20),'physical candidate order determines exact selected set');}
 check(snap(source).power.currentPower===10,'Priscilla excluded from captured list');check(snap(hidden).power.currentPower===20&&snap(enemy).power.currentPower===20,'hidden/other-side excluded');check(targets.every(c=>snap(c).power.armor===2),'boost retains armor');
});
for(const side of [1,2])run(122312,side,'Soldiers mask67108864',g=>{
 const soldier=add(g,122310,side,1,0,20,3),immune=add(g,122310,side,2,0,20,3,256),gold=add(g,122310,side,4,0,20,3),notSoldier=add(g,132209,side,2,1,20,3),enemy=add(g,122310,3-side,1,0,20,3),hand=add(g,122310,side,8,0,20,3);gold.cardState.runtimeTierMask=8;const source=begin(g,122312,side);for(const c of [soldier,immune,gold])check(snap(c).power.currentPower===21,'own visible Soldier1boost all tiers/immune');for(const c of [notSoldier,enemy,hand])check(snap(c).power.currentPower===20,'non-Soldier/other-side/inactive excluded');check(snap(source).power.currentPower===10,'executing owner excluded');
});
for(const side of [1,2])run(142201,side,'Dwarf all active/hand/deck',g=>{
 const records=[];for(const seat of [side,3-side])for(const zone of [1,2,4,8,16,32]){const c=add(g,142317,seat,zone,0,20,7,zone===2?256:0);c.ChangeBasePower(14-snap(c).power.basePower,true);c.power.SetPermanentPowerAndArmor(-2,7);c.power.SetCurrentPair(20,7);records.push({c,before:snap(c),hit:seat===side&&zone!==32});}const other=add(g,132209,side,1,1,20,7),source=begin(g,142201,side);
 for(const {c,before,hit}of records){const s=snap(c);check(s.power.basePower===before.power.basePower+(hit?1:0),'Dwarf base strengthen correct side/zone');check(s.power.currentPower===before.power.currentPower+(hit?1:0),'current offset preserved');check(s.power.permanentPower===-2&&s.power.armor===7,'permanent and armor retained');check(s.locationMask===before.locationMask&&s.positionPlayerId===before.positionPlayerId,'no movement');}check(snap(other).power.currentPower===20&&snap(source).power.currentPower===10,'non-Dwarf/executing owner excluded');
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceEvidence,scope:'11 cards: fixed numeric/group/shape/category/RNG branches; all external reaction orders and full native behavior remain open.',semanticCoverageComplete:false};if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh output');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,15),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;

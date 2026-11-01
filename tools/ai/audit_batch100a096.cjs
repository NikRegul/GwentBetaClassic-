'use strict';
const {rt,add,snap,id,check,flush,run,begin,choose,trace,finish}=require('./fixture_batch100096.cjs')(process.argv[2]);
for(const tid of [113308,113309])for(const side of [1,2])run(tid,side,'all extremes/ties',g=>{
 const a=add(g,132209,side,1,0,tid===113308?3:20,9),b=add(g,132209,3-side,2,0,tid===113308?3:20,4,256),other=add(g,132209,side,4,0,10),hidden=add(g,142307,3-side,4,0,tid===113308?1:30);begin(g,tid,side);
 check([a,b].every(c=>snap(c).locationMask===32),'ALL equal CURRENT extremes destroyed regardless armor/NotTargetable');check(snap(other).locationMask===4&&snap(hidden).locationMask===4,'nonextreme/hidden untouched');check(!g.IsPending()&&g.random.DrawCount()===0,'automatic/no RNG');
});
for(const [tid,token,own,all]of [[113312,4,false,false],[200018,16,false,true],[201749,128,true,false],[113101,32,false,true],[113203,64,false,false],[113302,1,false,false],[113305,2,false,false],[152105,64,false,false],[200228,512,false,false],[201637,1024,false,false]])for(const side of [1,2])run(tid,side,'row deploy only',g=>{
 const seat=own?side:3-side,targets=[1,2,4].map(row=>add(g,132209,seat,row,0,30,4));for(const row of [1,2,4])g.weather.ApplyHazard(seat,row,256);flush(g);const source=begin(g,tid,side);
 if(!all){check(g.IsPending()&&g.pendingRow,'required row request');check(g.SelectRow(g.requestId,seat,2),'correct-side row accepted');flush(g);}else check(!g.IsPending(),'all enemy rows automatic');
 for(const row of [1,2,4])check(g.weather.Token(seat,row)===(all||row===2?token:256),'row token replaced exactly');
 check(targets.every(c=>snap(c).power.currentPower===30),'deploy graph has no immediate damage/boost');check(g.random.DrawCount()===0,'deploy no RNG');check(snap(source).power.armor===0,'unused tooltip armor not granted');
});
for(const tid of [122214,132307])for(const side of [1,2])for(const token of [1,128,256,4096])run(tid,side,'clear-mask/'+token,g=>{
 g.weather.hazards[(side-1)*3+1]=token;g.weather.hazards[(side-1)*3]=2;const source=begin(g,tid,side);check(g.weather.Token(side,2)===(token&~3711),'REMOVE3711 preserves boons/FireSP');check(g.weather.Token(side,1)===2,'other row untouched');check(!g.IsPending()&&snap(source).power.armor===0,'no request/armor grant');
});
for(const side of [1,2])for(const fromSide of [1,2])run(152210,side,'other Hand to enemy Active/'+fromSide,g=>{
 const owner=add(g,152210,side,1,0,30),target=add(g,132209,fromSide,8,0,30,0);const old=snap(target);target.Move(3-side,2,0);g.MonsterMoved(old,false,2);flush(g);check(snap(target).power.currentPower===29,'other Hand arrival enemy active gets CURRENT damage1');check(snap(owner).power.currentPower===30,'owner unchanged');
});
for(const side of [1,2])run(200236,side,'nonboosted bronze/silver',g=>{
 const healthy=add(g,132209,3-side,1,0,rt.definition(132209).header.power,8),boosted=add(g,132209,3-side,2,0,30),gold=add(g,112101,3-side,4,0,1);begin(g,200236,side);check(g.pendingIds.includes(id(healthy))&&!g.pendingIds.includes(id(boosted))&&!g.pendingIds.includes(id(gold)),'exact unboosted tier filter');choose(g,healthy);check(snap(healthy).locationMask===32,'destroy bypasses armor');
});
for(const side of [1,2])run(200532,side,'own current row',g=>{g.weather.ApplyHazard(side,2,1);flush(g);begin(g,200532,side);check(g.weather.Token(side,2)===128&&!g.IsPending(),'own-row Froth without request');});
for(const side of [1,2])run(201573,side,'deathwish BASE3',g=>{
 const source=add(g,201573,side,1,0,10),target=add(g,132209,side,2,0,30,4,256),before=snap(target),rng=trace(g);g.QueueDestroy(source);flush(g);check(snap(target).power.basePower===before.power.basePower+3&&snap(target).power.currentPower===33,'BASE strengthen3 preserves offset');check(snap(target).power.armor===4,'armor retained');check(rng.length===1&&rng[0].n===1,'singleton RNG consumed');
});
for(const side of [1,2])for(const fogSide of [1,2])run(132302,side,'any-side fog/'+fogSide,g=>{const source=add(g,132302,side,1,0,30);g.weather.ApplyHazard(fogSide,4,2);flush(g);g.events.AfterTurn(side);flush(g);check(snap(source).power.currentPower===31,'owner AfterTurn sees fog ANY active row');});
for(const side of [1,2])run(201777,side,'destroy hidden including NotTargetable',g=>{const hidden=add(g,142307,3-side,1,0,30,4,256),visible=add(g,132209,3-side,2,0,30);begin(g,201777,side);check(g.pendingIds.includes(id(hidden))&&!g.pendingIds.includes(id(visible)),'only raw Ambush despite NotTargetable');choose(g,hidden);check(snap(hidden).locationMask===32,'hidden destroyed');});
finish(process.argv[3],'100a:20 independent source cards, deploy/primary passive branches; row ticks and complete branch coverage deferred.');

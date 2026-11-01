'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
// 200038 Archespore: owner BeforeTurn -> MoveCards self to GetRandomLastAvailablePosition(own, Active minus current) -> random enemy (Ignore8) 1 dmg; Killed -> random enemy 4 dmg.
if(want(200038))for(const side of [1,2])for(const full1 of [false,true])run(200038,side,'archespore turn/'+(full1?'melee full':'open'),g=>{
 const a=add(g,200038,side,2,0,7);if(full1)for(let i=0;i<9;i++)add(g,132403,side,1,i,30);const e1=add(g,132209,3-side,1,0,20,0),e2=add(g,132209,3-side,4,0,20,0),h=add(g,142307,3-side,2,0,20,0,8);
 const rng=trace(g);g.BeforeTurnWithEvents(side);flush(g);const rows=full1?[4]:[1,4],d0=rng[0];
 check(!!d0&&d0.n===rows.length&&snap(a).locationMask===rows[d0.v],'self moved to a random OTHER non-full own row',{loc:snap(a).locationMask,rng});
 const d1=rng[1],en=[e1,e2];check(!!d1&&d1.n===2&&snap(en[d1.v]).power.currentPower===19&&snap(en[1-d1.v]).power.currentPower===20&&snap(h).power.currentPower===20,'random visible enemy (Ignore Ambush) takes 1',{rng});
});
if(want(200038))for(const side of [1,2])run(200038,side,'archespore deathwish',g=>{
 const a=add(g,200038,side,2,0,3);const e1=add(g,132209,3-side,1,0,20),e2=add(g,132209,3-side,2,0,20);const rng=trace(g);g.QueueDestroy(a);flush(g);const d=rng.find(r=>r.n===2);
 check(!!d&&snap([e1,e2][d.v]).power.currentPower===16,'Killed: random enemy 4 damage',{rng});
});
// 162212 False Ciri on side P (position): BeforeTurn(P)+Disloyal -> +1; AfterPassed(P)+Disloyal -> move to opponent same location/index; Killed -> random lowest-level unit of P in its From row destroyed.
if(want(162212))for(const P of [1,2])for(const dis of [true,false])run(162212,P,'false ciri turn/'+dis,g=>{
 const c=add(g,162212,P,2,0,8,0,dis?128:0);g.BeforeTurnWithEvents(P);flush(g);check(snap(c).power.currentPower===(dis?9:8),'Disloyal-only BeforeTurn boost1');
});
if(want(162212))for(const P of [1,2])run(162212,P,'false ciri pass',g=>{
 add(g,132403,3-P,2,0,30);add(g,132403,3-P,2,1,30);add(g,132403,P,2,0,30);const c=add(g,162212,P,2,1,8,0,128);g.match.currentPlayerId=P;check(g.Pass(P),'owner passes');flush(g);const s=snap(c);
 check(s.positionPlayerId===3-P&&s.locationMask===2,'moved to opponent same location (Beta keeps the index; mod appends: open, not changed)',{s:[s.positionPlayerId,s.locationMask,s.locationIndex]});
});
if(want(162212))for(const P of [1,2])run(162212,P,'false ciri deathwish',g=>{
 const lo1=add(g,132403,P,2,0,2),lo2=add(g,132403,P,2,1,2),hi=add(g,132209,P,2,2,9),other=add(g,132403,P,4,0,1),c=add(g,162212,P,2,3,1,0,128);const rng=trace(g);g.QueueDestroy(c);flush(g);const d=rng.find(r=>r.n===2);
 check(!!d&&[32,512].includes(snap([lo1,lo2][d.v]).locationMask)&&snap([lo1,lo2][1-d.v]).locationMask===2&&snap(hi).locationMask===2&&snap(other).locationMask===4,'random lowest in its former row destroyed',{rng});
});
// 132108 Miruna: Played timer=2; owner BeforeTurn decrements; at 0 TimerTriggered steals a random highest enemy unit in her location id to her own row end.
if(want(132108))for(const side of [1,2])run(132108,side,'miruna timer',g=>{
 const hi1=add(g,132209,3-side,2,0,15),hi2=add(g,132209,3-side,2,1,15),lo=add(g,132403,3-side,2,2,3),far=add(g,132209,3-side,1,0,30);const m=begin(g,132108,side);
 check(snap(m).timerValue===2,'Played sets timer 2');g.BeforeTurnWithEvents(side);flush(g);check(snap(m).timerValue===1&&[hi1,hi2].every(c=>snap(c).positionPlayerId===3-side),'first BeforeTurn: timer1 only');
 const rng=trace(g);g.BeforeTurnWithEvents(side);flush(g);const d=rng.find(r=>r.n===2),st=d?[hi1,hi2][d.v]:null;
 check(!!st&&snap(st).positionPlayerId===side&&snap(st).locationMask===2&&snap(far).positionPlayerId===3-side&&snap(lo).positionPlayerId===3-side,'at 0: random highest enemy unit of her row id moved to her side/row',{rng,loc:st&&snap(st).positionPlayerId});
});

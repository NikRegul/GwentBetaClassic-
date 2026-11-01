'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
// 153201 Restore: own-grave Skellige Bronze/Silver Unit|UnitEvent Min1 -> own hand index0, Set BASE 8, Doomed512, category; then choose exactly 1 hand card (tiers14) and play it.
if(want(153201))for(const side of [1,2])run(153201,side,'restore',g=>{
 const sk=add(g,152305,side,32,0),sk2=add(g,152307,side,32,1),nr=add(g,132403,side,32,2),enemy=add(g,152305,3-side,32,0),h=add(g,132209,side,8,0);
 const owner=begin(g,153201,side);check(g.IsPending()&&JSON.stringify(g.pendingIds)===JSON.stringify([sk,sk2].map(id)),'own graveyard Skellige faction only, in order',{mod:g.pendingIds});
 check(g.GetRequestSnapshot().limits.minimum===1,'first choice Min1');check(g.SelectTarget(g.requestId,id(sk2)),'pick');flush(g);
 let s=snap(sk2);check(s.locationMask===8&&s.power.basePower===8&&(s.tokenMask&512)!==0,'in hand, BASE set to 8, Doomed',{s:[s.locationMask,s.tokenMask],p:s.power});
 check(g.IsPending()&&g.pendingIds.includes(id(sk2))&&g.pendingIds.includes(id(h))&&g.GetRequestSnapshot().limits.minimum===1,'second choice: any own hand card incl. the returned one, mandatory',{mod:g.pendingIds});
 check(g.SelectTarget(g.requestId,id(sk2)),'play returned');flush(g);place(g);s=snap(sk2);check((s.locationMask&7)!==0&&s.power.basePower===8,'returned card played with BASE 8',{s:s.locationMask,p:s.power});
});
// 142105 Zoltan: up to 3 targets (Min=Max=min(3,n)) in rows other than his own, both sides, Ignore 264; allies -> his row end + strengthen 2; enemies -> opposite row same location + 2 damage.
if(want(142105))for(const side of [1,2])run(142105,side,'zoltan',g=>{
 const al=add(g,132209,side,1,0,10),en=add(g,132209,3-side,4,0,10,1),same0=add(g,132403,side,2,0,30),hid=add(g,142307,3-side,1,0,30,0,8),en2=add(g,132403,3-side,2,0,30);
 const owner=begin(g,142105,side);check(g.IsPending()&&same(g.pendingIds,[al,en].map(id)),'targets: other rows of both sides, not hidden/NT, not his row',{mod:g.pendingIds});
 check(g.SelectTarget(g.requestId,id(al)),'ally');flush(g);check(g.IsPending(),'Min=Max=2 when 2 valid (ARequestTargetsAction)');check(g.SelectTarget(g.requestId,id(en)),'enemy');flush(g);
 const a=snap(al),e=snap(en);check(a.positionPlayerId===side&&a.locationMask===2&&a.power.basePower===15&&a.power.currentPower===12,'ally moved to his row, strengthened 2',{a:[a.locationMask],p:a.power});
 check(e.positionPlayerId===3-side&&e.locationMask===2&&e.power.currentPower===9&&e.power.armor===0,'enemy moved to opposite row, 2 damage armor first',{e:[e.locationMask],p:e.power});
});

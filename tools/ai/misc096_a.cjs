'use strict';
const {rt,add,snap,id,check,flush,run,begin,trace,fresh,ids,place,same,want}=globalThis.__misc;
// 152204 Donar: any-side unit target (Ignore NotTargetable256 only) -> Toggle Lock4; then 0..1 enemy-grave Bronze unit -> OWN graveyard.
if(want(152204))for(const side of [1,2])for(const skip of [false,true])run(152204,side,'lock+steal/'+(skip?'skip':'take'),g=>{
 const a=add(g,132403,3-side,1,0,30),hid=add(g,142307,3-side,2,0,30,0,8),nt=add(g,132403,3-side,4,0,30,0,256),own=add(g,132209,side,1,0,30),locked=add(g,132310,side,4,0,30,0,4);
 const gr=[132403,132310,132209].map((t,i)=>add(g,t,3-side,32,i));const owner=begin(g,152204,side);
 check(g.IsPending()&&same(g.pendingIds,[a,hid,own,locked].map(id)),'target set: both sides, NotTargetable excluded, ambush/locked included',{mod:g.pendingIds});
 check(g.SelectTarget(g.requestId,id(locked)),'target');flush(g);check((snap(locked).tokenMask&4)===0,'Toggle removes existing Lock');
 check(g.IsPending()&&JSON.stringify(g.pendingIds)===JSON.stringify([gr[0],gr[1]].map(id)),'second choice: enemy graveyard Bronze units in order',{mod:g.pendingIds});
 check(g.GetRequestSnapshot().limits.minimum===0,'steal choice Min0');
 if(skip){check(g.FinishTarget(g.requestId),'skip');flush(g);check(gr.every(c=>snap(c).positionPlayerId===3-side&&snap(c).locationMask===32),'nothing moved');return;}
 check(g.SelectTarget(g.requestId,id(gr[1])),'pick');flush(g);const s=snap(gr[1]);check(s.positionPlayerId===side&&s.locationMask===32,'moved to OWN graveyard (MakeCardPosition owner,32)',{s:[s.positionPlayerId,s.locationMask]});
});
// 201753 Peasant militia: own row target -> 3x201677 at row end.
if(want(201753))for(const side of [1,2])for(const r of [1,4])run(201753,side,'militia/'+r,g=>{
 add(g,132403,side,r,0,30);for(let i=0;i<6;i++)add(g,132403,side,r===4?4:2,i+1,30);const pre=ids(g),owner=begin(g,201753,side);
 check(g.IsPending()&&[1,2,4].every(x=>g.CanSelectRow(g.requestId,side,x))&&![1,2,4].some(x=>g.CanSelectRow(g.requestId,3-side,x)),'own rows only (ValidPlayers owner, Active)');
 check(g.SelectRow(g.requestId,side,r),'row');flush(g);const n=fresh(g,pre).filter(s=>s.runtimeTemplate.templateId===201677);
 const cap=r===4?9-7:9-1;check(n.length===Math.min(3,cap)&&n.every(s=>s.positionPlayerId===side&&s.locationMask===r),'3 peasants (capacity) appended',{n:n.length,cap});
});
// 200021 Roar: own unit target mandatory -> destroy -> spawn+play Bear 152406; no target -> nothing.
if(want(200021))for(const side of [1,2])for(const empty of [false,true])run(200021,side,'roar/'+(empty?'none':'one'),g=>{
 const u=empty?null:add(g,132209,side,2,0,30,5);add(g,132403,3-side,2,0,30);const pre=ids(g),owner=begin(g,200021,side);
 if(empty){flush(g);check(!g.IsPending()&&fresh(g,pre).filter(s=>s.instanceId!==id(owner)).length===0,'no own unit: no spawn');return;}
 check(g.IsPending()&&same(g.pendingIds,[id(u)]),'own units only');check(g.SelectTarget(g.requestId,id(u)),'pick');flush(g);
 check(snap(u).locationMask===32,'destroyed despite armor');check(g.IsPending()&&!!g.pendingRally,'bear placement');place(g);
 const n=fresh(g,pre).filter(s=>s.instanceId!==id(owner));check(n.length===1&&n[0].runtimeTemplate.templateId===152406&&(n[0].locationMask&7)&&n[0].positionPlayerId===side,'bear spawned and played own side',{n:n.map(s=>[s.runtimeTemplate.templateId,s.locationMask])});
});
// 122102 Roche: Played damage 7 to an enemy unit (Ignore 264).
if(want(122102))for(const side of [1,2])run(122102,side,'damage7',g=>{
 const a=add(g,132209,3-side,1,0,10,3),b=add(g,132403,3-side,2,0,30,0,8),c=add(g,132403,side,1,0,30);begin(g,122102,side);
 check(g.IsPending()&&same(g.pendingIds,[id(a)]),'enemy visible units only');g.SelectTarget(g.requestId,id(a));flush(g);const s=snap(a);check(s.power.currentPower===6&&s.power.armor===0,'7 damage armor first',{p:s.power});
});
// 201635 Glorious hunt: own score >= enemy -> spawn+play 113306; smaller -> spawn+play 132209.
if(want(201635))for(const side of [1,2])for(const [mine,theirs] of [[10,5],[5,5],[3,9]])run(201635,side,'hunt/'+mine+'-'+theirs,g=>{
 add(g,132403,side,1,0,mine);add(g,132403,3-side,1,0,theirs);const pre=ids(g),owner=begin(g,201635,side);place(g);
 let k=0;while(g.IsPending()&&k++<5){if(g.pendingIds.length){g.SelectTarget(g.requestId,g.pendingIds[0]);}else if(!g.FinishTarget(g.requestId))break;flush(g);place(g);}
 const n=fresh(g,pre),wantT=mine>=theirs?113306:132209;check(n.some(s=>s.runtimeTemplate.templateId===wantT)&&!n.some(s=>s.runtimeTemplate.templateId===(wantT===113306?132209:113306)),'branch by PlayerGetScore A(own) vs B(enemy): Bigger/Equal->113306, Smaller->132209',{n:n.map(s=>s.runtimeTemplate.templateId)});
});

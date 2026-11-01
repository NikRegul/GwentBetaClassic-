'use strict';
// Independent contracts derived from graph connections and statically read C#.
// No Beta C# host; only the production WS -> JS engine is executed.
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {graph}=require('./source_graph095.cjs');
const h=graph(200300,190),o=graph(122213,266),s=graph(142212,1444);
o.variable('Boost',1);s.variable('Boost',1);s.variable('RealBoost',0);
h.node(173,'BranchNode');h.node(165,'IsLocationFull');h.edge(8,'FlowOut',173,'FlowIn');h.edge(165,'DV',173,'Condition');h.edge(173,'FlowOutFalse',39,'FlowIn');
h.node(23,'LocationIdNegateNode');h.value(23,'LocationMask',7);h.edge(14,'DV',23,'DS');h.edge(23,'DV',28,'LocationId');h.value(28,'Ignore',264);
h.edge(39,'SelectedTargets',50,'Cards');h.edge(50,'FlowOut',84,'FlowIn');h.value(140,'Tokens',8);h.value(140,'Negate','True');h.edge(140,'Out',121,'e0');h.edge(121,'FilteredCards',91,'DS');h.edge(91,'DV',100,'Power');h.edge(39,'SelectedTargets',100,'Targets');h.value(100,'Operation',1);h.value(100,'IgnoreArmor','False');
o.value(12,'LocationMask',7);o.edge(16,'DV',12,'DS');o.edge(12,'DV',136,'Location');o.edge(136,'Out',142,'List');o.edge(80,'FlowOut',195,'FlowIn');o.edge(120,'Out',122,'LocationId');o.value(205,'Tokens',8);o.value(205,'Negate','True');o.value(210,'Negate','True');o.edge(214,'DV',210,'CardId');o.edge(9,'Out',236,'PlayerIdFilter');
s.value(1438,'Tokens',8);s.value(1438,'Negate','True');s.edge(1438,'Out',665,'e0');s.edge(1113,'FlowFor',1429,'FlowIn');s.edge(1316,'Out',1429,'List');s.edge(1429,'FlowOutTrue',1322,'FlowIn');s.edge(1351,'FlowOut',1391,'FlowIn');s.edge(1113,'FlowOut',1367,'FlowIn');
const {createRuntime}=require('./beta_js092/session.cjs'),rt=createRuntime(path.resolve(process.argv[2]));
let checks=0;const failures=[],cases=[];
const check=(v,label)=>{checks++;if(!v)failures.push(label);};
function add(g,id,side,zone,index,hidden=false){const ref={v:0};assert(g.registry.Allocate(ref));const c=rt.newCard();c.Setup(g,ref.v,id,side,zone,index);g.registry.Put(ref.v,c);g.live.push(c);if(hidden)c.AddTokens(8);return c;}
function fixture(side,seed=83291){const g=rt.newSession();assert(g.InitializeWithPresets(54,54));for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
 g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;g.weatherProfile=false;g.externalPolicyMask=3;
 g.match.currentPlayerId=side;g.match.roundActive=g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;g.random.Initialize(seed);return g;}
function fill(g,side,row,n,hidden=0){return Array.from({length:n},(_,i)=>add(g,132403,side,row,i,i<hidden));}
function finish(g,label){g.FlushEffects();g.FlushDeaths();check(!g.IsFatal()&&!g.IsPending(),label+' resolves');}
// Harpoon: full destination suppresses the entire request; same-row enemies
// never enter its pool. Count AFTER movement, excluding Ambush only (not 256).
for(const side of [1,2])for(const row of [1,2,4])for(const mode of ['normal','hidden','full','armor']){
 const g=fixture(side),enemy=3-side,other=[1,2,4].find(r=>r!==row),n=mode==='full'?9:3;
 const dest=fill(g,enemy,row,n,mode==='hidden'?2:0);dest[dest.length-1].AddTokens(256);
 const same=dest[0],target=add(g,132403,enemy,other,0);target.power.SetCurrentPair(30,mode==='armor'?3:0);
 const hiddenTarget=add(g,132403,enemy,other,1,true),immuneTarget=add(g,132403,enemy,other,2);immuneTarget.AddTokens(256);
 const card=add(g,200300,side,8,0);check(g.Play(side,card.Snapshot().instanceId,row),'harpoon play '+side+'/'+row+'/'+mode);
 const pool=[...g.pendingIds];
 if(mode==='full'){check(!g.IsPending(),'full destination: no target request '+side+'/'+row);if(g.IsPending())g.SelectTarget(g.requestId,target.Snapshot().instanceId);check(target.Snapshot().power.currentPower===30,'full destination: no damage');}
 else {
  check(pool.includes(target.Snapshot().instanceId),'other-row visible target available');
  check(!pool.includes(same.Snapshot().instanceId),'same-row target excluded '+side+'/'+row+'/'+mode);
  check(!pool.includes(hiddenTarget.Snapshot().instanceId)&&!pool.includes(immuneTarget.Snapshot().instanceId),'ambush and not-targetable excluded');
  check(g.SelectTarget(g.requestId,target.Snapshot().instanceId),'choose target');finish(g,'harpoon');
  const damage=n+1-(mode==='hidden'?2:0),armor=mode==='armor'?3:0,t=target.Snapshot();
  check(t.positionPlayerId===enemy&&t.locationMask===row&&t.locationIndex===n,'moves to opponent matching row, appended');
  check(t.power.currentPower===30-Math.max(0,damage-armor)&&t.power.armor===Math.max(0,armor-damage),'visible destination count / armor '+side+'/'+row+'/'+mode+' got '+JSON.stringify(t.power));
 }
 cases.push({card:200300,side,row,mode,pool,actual:target.Snapshot()});
}
// Odrin: current side's BEFORE turn, another available row, then current row
// boost excluding its INSTANCE and Ambush. Full alternatives leave it in place.
for(const side of [1,2])for(const row of [1,2,4])for(const mode of ['jump','blocked','locked','other-turn']){
 const g=fixture(side),other=[1,2,4].filter(r=>r!==row),odrin=add(g,122213,side,row,0);
 const near=add(g,132403,side,row,1),nearHidden=add(g,132403,side,row,2,true);
 for(const r of other)fill(g,side,r,mode==='blocked'?9:(r===other[0]?9:2));
 const all=g.live.filter(c=>(c.Snapshot().locationMask&7)!==0),before=new Map(all.map(c=>[c.Snapshot().instanceId,c.Snapshot()]));
 if(mode==='locked')odrin.AddTokens(4);const draws=g.random.DrawCount();g.BeforeTurnWithEvents(mode==='other-turn'?3-side:side);finish(g,'Odrin');
 const active=!['locked','other-turn'].includes(mode),expected=active&&mode!=='blocked'?other[1]:row,t=odrin.Snapshot();
 check(t.locationMask===expected&&t.positionPlayerId===side,'Odrin destination '+side+'/'+row+'/'+mode);
 check(g.random.DrawCount()-draws===(active&&mode!=='blocked'?1:0),'Odrin singleton/no available RNG '+mode);
 for(const c of all){const old=before.get(c.Snapshot().instanceId),boost=active&&c!==odrin&&old.locationMask===expected&&(old.tokenMask&8)===0?1:0;check(c.Snapshot().power.currentPower===old.power.currentPower+boost,'Odrin boost only final visible neighbours '+side+'/'+row+'/'+mode);}
 check(nearHidden.Snapshot().locationMask===row,'Odrin hidden neighbour stays');
 if(active&&mode!=='blocked')check(t.locationIndex===2,'Odrin append');cases.push({card:122213,side,row,mode,actual:t});
}
// Sheldon: source list excludes face-down cards; per-card available-row check
// prevents overfilling. Count successful move branches, then boost self once.
for(const side of [1,2])for(const row of [1,2,4])for(const capacity of [0,1,3,18]){
 const g=fixture(side),other=[1,2,4].filter(r=>r!==row),friends=fill(g,side,row,3),hidden=add(g,132403,side,row,3,true);
 fill(g,side,other[0],9-Math.min(capacity,9));fill(g,side,other[1],9-Math.max(0,capacity-9));
 const card=add(g,142212,side,8,0),power=card.Snapshot().power.currentPower,draws=g.random.DrawCount();check(g.Play(side,card.Snapshot().instanceId,row),'Sheldon play');finish(g,'Sheldon');
 const moved=friends.filter(c=>c.Snapshot().locationMask!==row).length,expected=Math.min(3,capacity);
 check(moved===expected&&hidden.Snapshot().locationMask===row,'Sheldon moves only available visible neighbours');
 check(card.Snapshot().power.currentPower===power+expected,'Sheldon actual moved count boost');check(g.random.DrawCount()-draws===expected,'Sheldon one row draw per moved neighbour');
 check([row,...other].every(r=>g.CountLocation(side,r)<=9),'Sheldon capacity');cases.push({card:142212,side,row,capacity,moved});
}
const shared=['MoveCardsNode','GetAvailableLocationsNode','BoardManager','GetLocationCards','FilterCardTokensNode','AListGetRandomElementNode'];
const report={checks,failures,cases,fingerprint:rt.fingerprint,sourceEvidence:[h.evidence([...shared,'IsLocationFull','CardListLengthNode','ChangePowerNode']),o.evidence([...shared,'BeforeTurnTrigger','GetOwnerLocationNode','FilterCardIdNode']),s.evidence([...shared,'LocationListBranchNode','CardListForeachNode'])],actualWitcherScript:true,scope:'Placement/relocation, capacity, visible row counts, armor and owner/lock guards; exact Beta RNG sequence and arbitrary external trigger ordering remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'Fresh report required');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}
console.log(JSON.stringify({checks,failures,cases:cases.length,fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;

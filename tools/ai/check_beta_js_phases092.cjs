/* Explicit source graph phases, both seats. Mode overrides are fixture-only
 * original TemplateId handlers; no generated fixture outcome rates strength. */
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,basePersonality,stateFromSession,templates}=require('./beta_js092/session.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaHandler}=require('./beta_js092/handlers.cjs'),{BetaActionReplay}=require('./beta_js092/replay.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924023001),p=basePersonality();let checks=0,nodes=0;
function eq(a,b,l){assert.deepEqual(a,b,l);checks++;}
function add(g,t,z,i,side){const id={v:0};g.registry.Allocate(id);const c=runtime.newCard();c.Setup(g,id.v,t,side,z,i);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(side){
 const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));
 g.mulligan=false;g.waiting=false;g.pendingCard=null;g.pendingLeader=null;g.match.currentPlayerId=side;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=1;g.recordVisuals=false;
 for(const player of [g.match.playerOne,g.match.playerTwo]){player.hasPassed=false;player.hasMadeInitialMoveForCurrentTurn=false;}
 for(const seat of [1,2])for(const zone of [2,8,16,32])for(let i=0;i<4;i++)add(g,112405,zone,i,seat);
 for(const seat of [1,2]){add(g,131101,1,0,seat);add(g,112101,1,1,seat);add(g,132306,1,2,seat);add(g,152406,4,0,seat);add(g,112202,4,1,seat);add(g,142202,4,2,seat);add(g,152406,32,5,seat);}
 // Required subtype targets for Bone Talisman and original create/tutor pools.
 add(g,132301,32,4,side);add(g,113301,16,4,side);add(g,113303,16,5,side);add(g,133301,16,6,side);return g;
}
for(const name of ['AiMulligan','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','AiAbilityChoiceValue','AiCreatedOptionValue','AiAdjacencyIndex'])runtime.newSession().constructor.prototype[name]=()=>{throw Error('P19 selector forbidden '+name);};
const cases=[
 [152204,0,[32,53]],[200020,0,[1,31]],[163201,0,[55,56]],[201611,0,[55,56]],
 [201603,201694,[26,33]],[201603,201695,[26,24]],
 [201662,201713,[26,34]],[201662,201714,[26,33]],
 [201648,201711,[26,33]],[201648,201712,[26,32]],
 [201598,201702,[26,22]],[201598,201703,[26,36]],
 [201697,201721,[26,27]],[201697,201722,[26,33]],
 [201621,201719,[26,27]],[201621,201720,[26,1]],
 [201653,201672,[26,27]],[201653,201673,[26,35]],
 [201731,201734,[27,28]],[201731,201732,[27,23]],
 [201737,201740,[27,38]],[201737,201741,[27,1]],
 [132215,200176,[26,1]],
];
const categories=fixture(1).monsters.north;
for(const t of Object.values(templates))eq(categories.BlackBloodCategory(t.id),t.categories.includes(16)||t.categories.includes(40),'Black Blood exact original category mask '+t.id);
for(const side of [1,2])for(const [template,mode,expected]of cases){
 const g=fixture(side),source=add(g,template,8,5,side),choices=new BetaChoiceHandlers(runtime,p),original=choices.handler.bind(choices);
 if([201725,201731,201737].includes(template)){
  let found=false;for(let seed=1;seed<=30;seed++){
   g.random.Initialize(924023000+seed);const probe=runtime.cloneSession(g),pool=Array.from({length:5},(_,i)=>template+1+i);probe.ShuffleIds({v:pool});
   if(pool.slice(0,3).includes(mode)){found=true;break;}
  }
  assert(found,'fixture seed offers desired source random-three mode');
 }
 choices.handler=(type,t,hint,exact)=>t===template&&mode&&type==='CardChoicesAssociations'&&hint===expected[0]?new BetaHandler('TemplateId',{TemplateId:mode}):original(type,t,hint,exact);
 const tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g),n=root.children.find(n=>n.decision?.cardId===source.Snapshot().instanceId);assert(n,'fixture has legal source');
 let callbacks=0;while(true){const before=tree.mutations,result=tree.tryPlayAction(n);eq(tree.mutations-before<=1,true,'phase cooperative mutation bound');if(result!==null)break;assert(++callbacks<90,'phase continuation bound');}
 nodes++;const records=n.choiceRecords.filter(r=>r.source===template);
 eq(records.map(r=>r.hint),expected,'literal source hint sequence '+[template,mode,side]);
 const live=runtime.cloneSession(g),replay=new BetaActionReplay(runtime,p,live,n);while(!replay.finished)replay.step();eq(stateFromSession(live),stateFromSession(n.game),'phase stored replay '+template);
}
const report={checks,nodes,fingerprint:runtime.fingerprint,nativeProcessesAllowed:false,currentPolicySelectorsAllowed:false,modeOverrides:'Explicit original TemplateId fixture handler only',ratingPermitted:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-phases-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

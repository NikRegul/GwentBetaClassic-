'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const cp=require('node:child_process');for(const k of ['spawn','spawnSync','exec','execSync','execFile','execFileSync','fork'])cp[k]=()=>{throw Error('Native process forbidden');};
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs');
const {BetaGameTree}=require('./beta_js092/actions.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const {BetaHandler}=require('./beta_js092/handlers.cjs');
const {BetaActionReplay}=require('./beta_js092/replay.cjs');
const runtime=createRuntime(path.resolve(process.argv[2]),924020601),p=basePersonality();let checks=0,nodes=0;
function eq(a,b,label){assert.deepEqual(a,b,label);checks++;}
function add(g,t,z,i,side){const id={v:0};g.registry.Allocate(id);const c=runtime.newCard();c.Setup(g,id.v,t,side,z,i);g.registry.Put(id.v,c);g.live.push(c);return c;}
function fixture(side){
 const g=runtime.newSession();g.externalPolicyMask=3;assert(g.InitializeWithPresets(54,54));
 g.live.forEach(c=>c.Move(c.Snapshot().positionPlayerId,512,0));g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.recordVisuals=false;
 g.match.currentPlayerId=side;g.match.roundActive=true;g.match.turnActive=true;g.match.roundNumber=1;
 for(const player of [g.match.playerOne,g.match.playerTwo]){player.hasPassed=false;player.hasMadeInitialMoveForCurrentTurn=false;}
 for(let i=0;i<4;i++){add(g,112405,8,i,side);add(g,112405,8,i,3-side);add(g,112405,16,i,side);add(g,112405,16,i,3-side);}return g;
}
const prototype=runtime.newSession().constructor.prototype;
for(const name of ['AiMulligan','AiMulliganCandidate','AiCardKeepValue','BestTarget','BestCardRow','BestOwnRow','BestNestedRow','BestModeChoice','ChooseDagonWeather','ChooseFirstLight','BestWeatherRow','BestEnemyRow','AiPileCandidateValue','AiAbilityChoiceValue','AiCreatedOptionValue','BestVranAnchor','AiAdjacencyIndex'])prototype[name]=()=>{throw Error('P19 selector forbidden: '+name);};
function prepare(g,c){const choices=new BetaChoiceHandlers(runtime,p),tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g);return {choices,tree,root,node:root.children.find(n=>n.decision?.cardId===c.Snapshot().instanceId)};}
function complete(tree,n){let callbacks=0;while(true){const before=tree.mutations,r=tree.tryPlayAction(n);eq(tree.mutations-before<=1,true,'one mutation per callback');if(r!==null)break;assert(++callbacks<60);}nodes++;}
// Each possible source Random count is fixed for coverage only. Ranking and
// request semantics still use the original handler; every chosen set is stored
// once, then replayed with the policy RNG disabled.
for(const side of [1,2])for(const count of [0,1,2,3]){
 const g=fixture(side),leader=add(g,200159,64,0,side),before=stateFromSession(g),draws=g.random.DrawCount(),b=prepare(g,leader);
 const original=b.choices.handler.bind(b.choices);
 b.choices.handler=(type,t,hint,exact)=>t===200159&&type==='CardChoicesAssociations'?new BetaHandler('Random'):original(type,t,hint,exact);
 b.choices.next=(min,max)=>min===0&&max===4?count:min;
 complete(b.tree,b.node);
 eq(b.node.choiceRecords.length,1,'Bran records one whole source decision');
 const record=b.node.choiceRecords[0];eq(record.chosen.length,count,'original random cardinality');
 eq(new Set(record.chosen.map(c=>c.id)).size,count,'no duplicate selections');
 for(const c of record.chosen){const s=b.node.game.FindCard(c.id).Snapshot();eq(s.locationMask,32,'chosen card discarded');eq(s.power.basePower,c.basePower+1,'discarded card strengthened');}
 const replay=b.tree.child(b.root,{...b.node.decision});replay.choiceRecords=b.node.choiceRecords.map(r=>({...r,chosen:r.chosen.map(c=>({...c}))}));
 b.choices.next=()=>{throw Error('Stored decision must not draw again');};complete(b.tree,replay);
 eq(stateFromSession(replay.game),stateFromSession(b.node.game),'complete replay has identical state');
 const live=runtime.cloneSession(g),action=new BetaActionReplay(runtime,p,live,b.node);
 while(!action.finished)eq(action.step().mutations,1,'live whole-set replay yields each action');
 eq(stateFromSession(live),stateFromSession(b.node.game),'live whole-set action matches simulated branch');
 eq(g.random.DrawCount(),draws,'live RNG unchanged');eq(stateFromSession(g),before,'source unchanged');
}
// A simulated pass may initialize the NEXT round and forecast own mulligans.
// Live replay must stop before that boundary; the two live controllers then
// perform their real mulligans. Sibling simulation must use its saved prefix.
for(const side of [1,2]){
 const g=fixture(side);add(g,112405,1,0,side);g.match[side===1?'playerTwo':'playerOne'].hasPassed=true;
 const choices=new BetaChoiceHandlers(runtime,p),tree=new BetaGameTree(runtime,p,choices.hooks()),root=tree.root(g),n=root.children.find(n=>n.decision===null);
 complete(tree,n);eq(n.game.Snapshot().roundNumber,2,'search resolves speculative round2');eq(n.mulliganChoices.length>0,true,'own simulated mulligans recorded');
 const bad={...p,MulliganPickerType:'MustNeverRecomputeStoredChoice'},saved=new BetaChoiceHandlers(runtime,bad),again=new BetaGameTree(runtime,bad,saved.hooks()),root2=again.root(g),n2=root2.children.find(n=>n.decision===null);
 n2.mulliganChoices=n.mulliganChoices.map(x=>({...x}));complete(again,n2);
 eq(n2.mulliganChoices,n.mulliganChoices,'stored mulligan prefix not appended again');eq(stateFromSession(n2.game),stateFromSession(n.game),'stored own simulated mulligan exactly replayed');
 const live=runtime.cloneSession(g),action=new BetaActionReplay(runtime,p,live,n);while(!action.finished)action.step();
 eq(live.waiting,true,'live action stops at round boundary');eq(live.mulligan,false,'live replay does not forecast either live mulligan');eq(live.Snapshot().roundNumber,1,'next live round belongs to coordinator');
}
for(const side of [1,2])for(const template of [200048,200165]){
 const g=fixture(side),source=add(g,template,template===200165?64:8,5,side),b=prepare(g,source);
 // Ban Ard's second pool is bronze special cards.
 add(g,113301,16,5,side);
 // Always choose the first legal card, using the source Power handler, to
 // exercise both concrete exchange stages instead of Random's optional zero.
 const original=b.choices.handler.bind(b.choices);
 b.choices.handler=(type,t,hint,exact)=>t===template&&type==='CardChoicesAssociations'?new BetaHandler('Power'):original(type,t,hint,exact);
 complete(b.tree,b.node);eq(b.node.choiceRecords.map(r=>r.hint),[49,45],'hand/deck source AIHints');
 const [hand,deck]=b.node.choiceRecords.map(r=>r.chosen[0]);
 eq(b.node.game.FindCard(hand.id).Snapshot().locationMask,16,'hand card enters deck');eq(b.node.game.FindCard(deck.id).Snapshot().locationMask,8,'deck card enters hand');
}
for(const side of [1,2])for(const [template,modes]of [[201615,[201715,201716]],[200102,[201717,201718]]])for(const mode of modes){
 const g=fixture(side);add(g,113301,16,5,side);add(g,112207,16,6,side);const source=add(g,template,8,5,side),b=prepare(g,source);
 const original=b.choices.handler.bind(b.choices);
 b.choices.handler=(type,t,hint,exact)=>t===template&&hint===26?new BetaHandler('TemplateId',{TemplateId:mode}):original(type,t,hint,exact);
 complete(b.tree,b.node);eq(b.node.choiceRecords[0].hint,26,'initial source mode hint');eq(b.node.choiceRecords[0].chosen[0].templateId,mode,'fixture covers specified mode');
 const second=b.node.choiceRecords[1];assert(second,'Second phase absent: '+[side,template,mode]);eq(second.hint,mode===201716||mode===201718?27:template===201615?1:24,'source second-stage hint');
}
// Original Bianca and Saskia choose their initial optional set once. Saskia
// then chooses the whole required replacement set, with no optional finish.
for(const side of [1,2])for(const template of [122204,200209])for(const count of [0,1,2]){
 const g=fixture(side),source=add(g,template,8,5,side),b=prepare(g,source),original=b.choices.handler.bind(b.choices);
 b.choices.handler=(type,t,hint,exact)=>t===template&&type==='CardChoicesAssociations'?new BetaHandler('Random'):original(type,t,hint,exact);
 b.choices.next=(min,max)=>min===0&&max===3?count:min;
 complete(b.tree,b.node);
 eq(b.node.choiceRecords[0].chosen.length,count,'optional original whole swap set');
 if(template===200209&&count){eq(b.node.choiceRecords.length,2,'Saskia initial and replacement sets');eq(b.node.choiceRecords[1].chosen.length,count,'all committed replacements chosen once');}
 const live=runtime.cloneSession(g),replay=new BetaActionReplay(runtime,p,live,b.node);while(!replay.finished)replay.step();
 eq(stateFromSession(live),stateFromSession(b.node.game),'whole swap stored replay');
}
for(const side of [1,2])for(const room of [1,2,3]){
 const g=fixture(side);for(let i=0;i<9-room;i++)add(g,112405,1,i,3-side);for(let i=0;i<3;i++)add(g,112405,2,i,3-side);
 const source=add(g,200218,8,5,side),b=prepare(g,source),original=b.choices.handler.bind(b.choices);
 b.node=b.root.children.find(n=>n.decision?.cardId===source.Snapshot().instanceId&&n.decision.row===1);assert(b.node,'Jotunn row1 fixture');
 b.choices.handler=(type,t,hint,exact)=>t===200218&&type==='CardTargetsAssociations'?new BetaHandler('Power'):original(type,t,hint,exact);
 complete(b.tree,b.node);eq(b.node.choiceRecords.length,1,'one whole source Jotunn set');eq(b.node.choiceRecords[0].chosen.length,room,'common capacity caps source request before selection');
 eq(b.node.game.CountLocation(3-side,1),9,'exactly fills available row capacity');
 const live=runtime.cloneSession(g),replay=new BetaActionReplay(runtime,p,live,b.node);while(!replay.finished)replay.step();eq(stateFromSession(live),stateFromSession(b.node.game),'Jotunn capacity replay');
}
const report={checks,nodes,fingerprint:runtime.fingerprint,nativeProcessLaunch:false,currentPolicySelectorsAllowed:false,
 scope:'Both seats: Bran whole 0..3 source decisions drained cooperatively and replayed without RNG; hand/deck exchange hints; both mode branches of Isengrim/Hym. Fixture branch overrides are explicit original handlers, not strength evidence.',fullMatchReady:false};
fs.writeFileSync(path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/direct-beta-js-stages-proof.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

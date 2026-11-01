'use strict';
// Independent expectations were recorded before implementation review in the
// 2026-10-29 block. C# is read only; all scenarios execute translated common WS.
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const sourcePath=path.join(root,'data/beta924/design/rules_audit096_token_sources.json');
const review=JSON.parse(fs.readFileSync(sourcePath,'utf8'));
for(const r of review.records)for(const c of r.classes)assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root,c.file))).digest('hex'),c.sha256,'source changed '+c.file);
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
let checks=0,label='';const failures=[],cases=[];
const check=(v,s,detail)=>{checks++;if(!v)failures.push({case:label,assertion:s,...(detail?{detail}:{})});};
const snap=c=>c.Snapshot(),cid=c=>snap(c).instanceId;
function flush(g){g.FlushEffects();g.FlushDeaths();}
function begin(g,id,side,row=2){g.mulliganReactions=true;const c=add(g,id,side,8,20);check(g.Play(side,cid(c),row),'actual play accepted');flush(g);return c;}
function choose(g,c){const id=typeof c==='number'?c:cid(c);check(g.IsPending(),'choice exists');if(!g.IsPending())return false;check(g.pendingIds.includes(id),'selected instance in pool');const ok=g.SelectTarget(g.requestId,id);check(ok,'selection accepted');flush(g);return ok;}
function finish(g){check(g.IsPending(),'request available for finishing');const ok=g.FinishTarget(g.requestId);check(ok,'optional choice can be declined');flush(g);return ok;}
function run(id,side,mode,body){label=id+'/'+side+'/'+mode;const g=fixture(side,82431+side);try{body(g);check(!g.IsFatal(),'no fatal');cases.push({id,side,mode,draws:g.random.DrawCount()});}catch(e){failures.push({case:label,fixtureError:e.stack});}}
function setPool(g,expected,note){const actual=[...g.pendingIds].sort((a,b)=>a-b),want=expected.map(cid).sort((a,b)=>a-b);check(JSON.stringify(actual)===JSON.stringify(want),note,{actual,want});}
// The five single-target toggle graphs share Lock4 but retain distinct powers.
for(const id of [113319,132205,122211])for(const side of [1,2])for(const targetSide of [side,3-side])for(const locked of [false,true])for(const hidden of [false,true])run(id,side,`${targetSide}/${locked}/${hidden}`,g=>{
 const target=add(g,132209,targetSide,2,0,23,3);target.ChangeBasePower(4,true);target.power.SetPermanentPowerAndArmor(2,3);target.power.SetCurrentPair(23,3);target.cardState.tokenMask=(locked?4:0)|1|128|(hidden?8:0)|16;
 const excluded=add(g,132209,targetSide,1,0,20,0,256),before=snap(target);begin(g,id,side);check(!g.pendingIds.includes(cid(excluded)),'NotTargetable excluded');check(g.pendingIds.includes(cid(target)),'Ambush target allowed by Ignore256');choose(g,target);
 const s=snap(target),wantTokens=locked?(before.tokenMask&~4):((before.tokenMask|4)&~137);
 check(s.tokenMask===wantTokens,'ToggleLock strips three tokens only on adding lock',{actual:s.tokenMask,wantTokens});
 const damage=targetSide===side?0:id===113319?4:0;const want=id===132205&&targetSide!==side?11:id===122211?before.power.basePower+before.power.permanentPower:23-Math.max(0,damage-3);
 check(s.power.currentPower===want,'independent follow-up formula',{actual:s.power.currentPower,want});check(s.power.armor===(id===113319&&targetSide!==side?0:3),'armor semantics');check(!g.IsPending(),'completed');
});
for(const side of [1,2])for(const initial of [0,1,4,5])run(113307,side,'resilience'+initial,g=>{
 const target=add(g,132209,3-side,2,0,15,2,initial);begin(g,113307,side);choose(g,target);check(snap(target).tokenMask===(initial^1),'Resilience toggles while Lock retained');check(snap(target).power.currentPower===15&&snap(target).power.armor===2,'power and armor unchanged');
});
// Egan collects both targets before a single ChangeTokens action. No effect on
// the first selected instance may leak while the second choice is pending.
for(const side of [1,2])run(162208,side,'batch toggle',g=>{
 const a=add(g,132209,side,1,0,20,2,137),b=add(g,132209,3-side,4,0,20,2,4);const source=begin(g,162208,side);check(!g.pendingIds.includes(cid(source)),'owner in execution stack excluded');choose(g,a);check(snap(a).tokenMask===137,'first pick is not locked before choice complete');check(g.IsPending(),'second target required');choose(g,b);check(snap(a).tokenMask===4&&snap(b).tokenMask===0,'both locks commit');check(!g.IsPending(),'done');
});
for(const side of [1,2])run(200169,side,'batch toggle then damage',g=>{
 const a=add(g,132209,3-side,1,0,20,1,137),b=add(g,132209,side,4,0,20,2,4);const observations=[];const orig=g.NilfPowerChanged.bind(g);g.NilfPowerChanged=(...args)=>{if(args[4]===1)observations.push([snap(a).tokenMask,snap(b).tokenMask]);return orig(...args);};
 const source=begin(g,200169,side);check(!g.pendingIds.includes(cid(source)),'owner in execution stack excluded');choose(g,a);check(snap(a).tokenMask===137&&snap(a).power.currentPower===20,'first pick unchanged while selecting second');choose(g,b);check(snap(a).tokenMask===4&&snap(b).tokenMask===0,'two toggles applied');check(snap(a).power.currentPower===17&&snap(b).power.currentPower===20,'enemy4damage only, armor applied');check(observations.every(x=>x[0]===4&&x[1]===0),'all toggles before any damage');
});
for(const side of [1,2])for(const token of [0,128])run(200118,side,'spying'+token,g=>{
 const target=add(g,132209,3-side,2,0,20,2,token);begin(g,200118,side);choose(g,target);check(snap(target).tokenMask===(token^128),'Spying toggle');check(snap(target).positionPlayerId===3-side&&snap(target).locationMask===2,'token does not relocate');
});
// Letho's source performs Destroy, rather than damage or drain actions.
for(const side of [1,2])run(162101,side,'sum lock destroy',g=>{
 const a=add(g,132209,3-side,2,0,21,6,137),b=add(g,132209,3-side,2,1,13,3,1);let damaged=0;const orig=g.MonsterDamaged.bind(g);g.MonsterDamaged=(...args)=>{if(args[1]===a||args[1]===b)damaged++;return orig(...args);};
 const source=begin(g,162101,side);const before=snap(source).power.currentPower;choose(g,a);check(snap(a).power.currentPower===21&&snap(a).tokenMask===137,'first choice unchanged');choose(g,b);check(snap(a).locationMask===32&&snap(b).locationMask===32,'both destroyed to grave');check(snap(source).power.currentPower===before+34,'captured current sum34');check(damaged===0,'Destroy emits no damage reactions',{damaged});check((snap(a).tokenMask&4)!==0&&(snap(b).tokenMask&4)!==0,'victims locked before destruction');
});
// True card choices retain min0. These use a captured set and commit together.
for(const id of [162103,162316,200163,201616])for(const side of [1,2])for(const mode of ['none','one','two'])run(id,side,mode,g=>{
 const reveal=id!==201616,token=reveal?0:64;
 const own=[add(g,132209,side,8,0,10,0,token),add(g,113205,side,8,1,0,0,token)],enemy=[add(g,132209,3-side,8,0,10,0,token),add(g,113205,3-side,8,1,0,0,token),add(g,112101,3-side,8,2,10,0,token),add(g,132209,3-side,8,3,10,0,token)];
 const other=add(g,132209,side,8,2,10,0,reveal?64:0);const expected=id===162103?own:[...own,...enemy];begin(g,id,side);setPool(g,expected,'hand candidate pool matches graph');if(mode==='none')check(g.FinishTarget(g.requestId),'optional finish accepted');
 // A successful probe ends the request; other modes select without probing.
 if(mode==='none'){flush(g);check([...own,...enemy].every(c=>((snap(c).tokenMask&64)!==0)===!reveal),'zero picks do not change any card');return;}
 choose(g,own[0]);if(mode==='one'){check(((snap(own[0]).tokenMask&64)!==0)===!reveal,'first pick waits for finish');finish(g);}else{check(((snap(own[0]).tokenMask&64)!==0)===!reveal,'first pick waits for second');choose(g,own[1]);if(id===200163&&g.IsPending())finish(g);}
 check(((snap(own[0]).tokenMask&64)!==0)===reveal,'first selected committed');check(((snap(own[1]).tokenMask&64)!==0)===(mode==='two'?reveal:!reveal),'only chosen second committed');check(((snap(other).tokenMask&64)!==0)===reveal,'wrong-state card remains unchanged');
 if(id===162103){const n=mode==='two'?2:1;check(enemy.filter(c=>(snap(c).tokenMask&64)!==0).length===n,'Vattier reveals same count on enemy');check(g.random.DrawCount()===n,'one RNG per enemy reveal, no whole-pool shuffle',{actual:g.random.DrawCount(),n});}
 check(!g.IsPending(),'complete after requested number or explicit finish');
});
// Separate optional probes above must never cancel a scenario under test.
// (The boolean expression deliberately calls FinishTarget only in none mode.)
for(const side of [1,2])run(200031,side,'exclude revealed',g=>{
 const unrevealed=add(g,132209,side,8,0,20),revealed=add(g,132209,side,8,1,20,0,64),enemy=add(g,132209,3-side,2,0,50,2);unrevealed.ChangeBasePower(3,true);const base=snap(unrevealed).power.basePower;begin(g,200031,side);setPool(g,[unrevealed],'Leo excludes already revealed own hand');choose(g,unrevealed);check((snap(unrevealed).tokenMask&64)!==0,'reveal before damage request');choose(g,enemy);check(snap(enemy).power.currentPower===50-Math.max(0,base-2),'damage uses changed base power');
});
for(const side of [1,2])for(const mode of ['bronze','silver','gold','empty'])run(162318,side,mode,g=>{
 const cards=[];if(mode==='bronze')cards.push(add(g,132403,side,8,0));if(['bronze','silver'].includes(mode))cards.push(add(g,132205,side,8,1));if(mode!=='empty')cards.push(add(g,112101,side,8,2));const pre=add(g,132209,side,8,3,10,0,64);const source=begin(g,162318,side);check(cards.length===0||((snap(cards[0]).tokenMask&64)!==0&&cards.slice(1).every(c=>(snap(c).tokenMask&64)===0)),'lowest tier eligible revealed');check(g.random.DrawCount()===(cards.length?1:0),'random even singleton, none if empty');check(snap(source).power.armor===rt.definition(162318).header.armor,'unused Armor variable creates no armor');
});
for(const side of [1,2])for(const tie of [false,true])run(162203,side,'Cynthia tie'+tie,g=>{
 const a=add(g,132209,3-side,8,0,16),b=add(g,132209,3-side,8,1,tie?16:10),spell=add(g,113205,3-side,8,2,100),revealed=add(g,132209,3-side,8,3,30,0,64);const draws=[];const orig=g.RandomIndex.bind(g);g.RandomIndex=n=>{const v=orig(n);draws.push({n,v});return v;};const source=begin(g,162203,side),base=rt.definition(162203).header.power;const chosen=tie?[b,a][draws[0]?.v]:a;
 check((snap(chosen).tokenMask&64)!==0,'HighestLevel uses reversed stable physical-hand tie order');check(snap(source).power.currentPower===base+16,'boost highest current16');check((snap(spell).tokenMask&64)===0,'special excluded regardless power100');check(draws.length===1&&draws[0].n===(tie?2:1),'single highest candidate RNG');
});
for(const tid of [162208,162316])for(const side of [1,2])run(tid,side,'mid-choice clone',g=>{
 const zone=tid===162208?1:8,a=add(g,132209,side,zone,0,20),b=add(g,132209,3-side,zone,0,20),source=begin(g,tid,side);choose(g,a);const before=JSON.stringify([snap(a),snap(b)]),clone=rt.cloneSession(g);check(clone.pendingIds.includes(cid(b)),'cloned second request retains exact instance');choose(clone,clone.FindCard(cid(b)));const ca=clone.FindCard(cid(a)),cb=clone.FindCard(cid(b));check(tid===162208?((snap(ca).tokenMask&4)!==0&&(snap(cb).tokenMask&4)!==0):((snap(ca).tokenMask&64)!==0&&(snap(cb).tokenMask&64)!==0),'cloned captured first and second choices commit');check(JSON.stringify([snap(a),snap(b)])===before&&g.IsPending(),'real state remains pending and unchanged');choose(g,b);check(!g.IsPending(),'real state independently completes');
});
// A revealed unit in the opponent's hand is reachable only through the candidate
// list: the flash view draws the enemy hand as backs along the top edge, so the
// on-board arrow cannot click them even when the card is face-up.
for(const side of [1,2])for(const id of [162206,162209])for(const mode of ['revealed','unrevealed'])run(id,side,mode+' hand target request',g=>{
 const board=add(g,132209,3-side,2,0,20,2),hand=mode==='revealed'?add(g,132305,3-side,8,0,10,0,64):add(g,132305,3-side,8,0,10),deckCopy=add(g,132305,3-side,16,1);begin(g,id,side);
 setPool(g,mode==='revealed'?[board,hand]:[board],'unrevealed enemy hand stays out of the pool');
 const kind=g.GetRequestSnapshot().kind;check((kind===1)===(mode==='revealed'),'pool with a revealed enemy-hand unit stays in the candidate list',{kind,mode});check((g.IsPileChoice()===true)===(mode==='revealed'),'the candidate list is not downgraded to the arrow mode',{pile:g.IsPileChoice(),mode});
 if(mode==='unrevealed'){check(!g.SelectTarget(g.requestId,cid(hand)),'unrevealed hand unit rejected');choose(g,board);check(!g.IsPending(),'board-only pool completes');return;}
 choose(g,hand);check(!g.IsPending(),'revealed hand unit is selectable');
 check(id===162206?(snap(hand).locationMask===8&&snap(hand).power.currentPower===10&&snap(board).locationMask===2&&snap(board).power.currentPower===20&&snap(deckCopy).locationMask===32):(snap(hand).locationMask===8&&snap(hand).power.currentPower===1&&snap(board).power.currentPower===20&&snap(deckCopy).locationMask===16),'the hand target resolves alone',{id,handZone:snap(hand).locationMask,handPower:snap(hand).power.currentPower,deck:snap(deckCopy).locationMask});
});
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,sourceReview:sourcePath,scope:'Source-driven targeted deploy/choice/token branches. Full card semantics and arbitrary external interactions remain open.',semanticCoverageComplete:false};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]),'fresh report required');fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,cases:cases.length,failures:failures.length,firstFailures:failures.slice(0,14),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;

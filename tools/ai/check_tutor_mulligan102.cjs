'use strict';
// Mulligan returns a hand card that a held deck tutor can play while that
// tutor's own deck pool is short (two per held tutor). Log 01.11.2026, seed
// 616139146: two Tormented Mages (201628) and two Alzur's Thunders in hand,
// two spells/items left in the deck, no mulligan. Eligibility is decided by the
// live rules on a search clone. Usage: node check_tutor_mulligan102.cjs <rules-dir> [report.json]
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const positions=require('./fixtures/tutor_mulligan102.json').positions;
let checks=0;const failures=[],cases=[];
function check(ok,n){checks++;if(!ok)failures.push(n);}
function hand(g){return g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===2&&s.locationMask===8);}
function mulligan(g,budget){const logs=[];rt.host.log=s=>logs.push(s);try{g.AiMulligan(budget);}finally{rt.host.log=null;}
 return logs.filter(s=>/MULLIGAN_TUTOR_TARGET|DUEL_AI_MULLIGAN/.test(s));}
function returned(logs,card){return logs.some(s=>s.startsWith('DUEL_AI_MULLIGAN outgoing='+card.Snapshot().instanceId+' '));}
// 1. Logged round-two start (decision 6 holds the unchanged post-mulligan hand).
{
 const p=positions.find(p=>p.name==='mages-round2');
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=+p.begin.round;const byId=new Map();
 for(const c of p.cards){if(c.zone===512)continue;const card=add(g,c.template,c.side,c.zone,c.index,c.power,c.armor,c.tokens);byId.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.canBePlayed=!!c.playable;card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);}
 g.archetypeAI.Initialize(g,[],+p.position.presetTwo,+p.start.enemyLeader);
 const logs=mulligan(g,1);cases.push({name:p.name,logs});
 check(returned(logs,byId.get(32))||returned(logs,byId.get(49)),'logged round two returns one Thunder for the two mages');
}
// 2. Synthetic pairs: tutor + its target in hand, a short pool in the deck.
function board(tutor,target,deckTargets,filler=112405){
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=1;
 const t=add(g,tutor,2,8),x=add(g,target,2,8);for(let i=0;i<6;i++)add(g,filler,2,8);
 for(const d of deckTargets)add(g,d,2,16);for(let i=0;i<8;i++)add(g,filler,2,16);
 add(g,112405,1,8);add(g,112405,1,16);g.archetypeAI.Initialize(g,[],54,0);return {g,t,x};}
const pairs=[[201628,113301,'Tormented Mage, Thunder'],[200033,113302,'Arethusa Adept, Biting Frost'],[142207,142305,'Barclay, dwarf'],
 [142102,142208,'Isengrim (gold), silver ambush'],[200154,122102,'Royal Decree, gold unit'],[131102,142207,"Ge'els, silver unit"],[132402,113302,'Wild Hunt Hound, Biting Frost'],[142107,113301,'Ithlinne, spell']];
for(const [tutor,target,name] of pairs){
 const {g,x,t}=board(tutor,target,[]);const draws=g.random.DrawCount(),before=JSON.stringify(g.live.map(c=>c.Snapshot()));
 const ta={v:[]},tb={v:[]},tv={v:[]};const pr=g.AiTutorReturnMulliganPriority102(x,g.live.filter(c=>c.Snapshot().positionPlayerId===2&&c.Snapshot().locationMask===8),ta,tb,tv);
 check(g.random.DrawCount()===draws&&JSON.stringify(g.live.map(c=>c.Snapshot()))===before,'estimate preserves cards and RNG: '+name);
 check(pr>0,'target is flagged: '+name);
 const logs=mulligan(g,1);cases.push({name,logs});check(returned(logs,x)||tutor===142107,'target is returned: '+name);
 check(t.Snapshot().locationMask===8,'tutor stays in hand: '+name);
}
// 3. Negatives.
{const {g,x}=board(201628,113301,[113310,113310,113301,113301]);const logs=mulligan(g,1);
 check(!logs.some(s=>s.includes('MULLIGAN_TUTOR_TARGET')),'enough spells in the deck: no tutor return');}
{const {g,x}=board(112405,113301,[]);const logs=mulligan(g,1);
 check(!logs.some(s=>s.includes('MULLIGAN_TUTOR_TARGET')),'no tutor in hand: no tutor return');}
{const {g,x}=board(142207,113301,[]);const logs=mulligan(g,1);
 check(!logs.some(s=>s.includes('MULLIGAN_TUTOR_TARGET template=113301')),'Barclay does not take a spell');}
{const {g,x}=board(201628,201628,[]);const logs=mulligan(g,1);
 check(!logs.some(s=>s.includes('MULLIGAN_TUTOR_TARGET')),'a mage is not a target of another mage');}
const report={checks,failures,cases,fingerprint:rt.fingerprint,actualWitcherScript:true,historicalRuntimeVerified:false,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;

// Real WS->JS engine: every captioned choice uses the UI mode its caption assumes,
// and the chosen / remaining cards really go where the caption says.
'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {createRuntime}=require('./beta_js092/session.cjs');const rt=createRuntime(path.resolve(process.argv[2]));let checks=0;
const check=(v,n)=>{checks++;assert(v,n);};
const HAND=8,DECK=16,GRAVE=32;
function add(g,id,side,zone,index){const r={v:0};g.registry.Allocate(r);const c=rt.newCard();c.Setup(g,r.v,id,side,zone,index);g.registry.Put(r.v,c);g.live.push(c);return c;}
function session(id,keep){
 const g=rt.newSession();g.InitializeWithPresets(72,72);
 for(const side of [1,2]){let n=0;for(const c of g.live){const s=c.Snapshot();if(s.positionPlayerId===side&&s.locationMask===DECK&&n<6){c.Move(side,GRAVE,n);n++;}}}
 g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;
 g.match.currentPlayerId=1;g.match.roundActive=g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;
 const src=add(g,id,1,HAND,9);check(g.Play(1,src.Snapshot().instanceId,1),id+' plays');check(g.IsPending(),id+' asks the human');return g;}
const where=(g,id)=>{for(const c of g.live){const s=c.Snapshot();if(s.instanceId===id)return s;}return null;};
const count=(g,side,zone)=>g.live.filter(c=>{const s=c.Snapshot();return s.positionPlayerId===side&&s.locationMask===zone;}).length;
function mode(g){const opts=g.pendingIds.map(x=>where(g,x));const rs=g.GetRequestSnapshot();
 return {pile:g.IsPileChoice()&&rs.kind===1,hand:rs.kind===2&&!g.IsPileChoice()&&opts.length>0&&opts.every(s=>s.positionPlayerId===1&&s.locationMask===HAND),opts};}
const records=[];
const CASES=[
 [152214,'pile',2,(g,pick,rest)=>{check(where(g,pick).locationMask===HAND,'Udalryk: chosen card drawn');check(rest.every(id=>where(g,id).locationMask===GRAVE),'Udalryk: the other is discarded to the graveyard');}],
 [122203,'pile',2,(g,pick,rest)=>{check(where(g,pick).locationMask===HAND,'Thaler: chosen card drawn');check(rest.every(id=>where(g,id).locationMask===DECK),'Thaler: the other stays in the deck');}],
 [142203,'pile',2,(g,pick,rest)=>{check(where(g,pick).locationMask===HAND,'Yaevinn: chosen card drawn');check(rest.every(id=>where(g,id).locationMask===DECK),'Yaevinn: the other stays in the deck');}],
 [131102,'pile',2,(g,pick,rest)=>{const deck=g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===1&&s.locationMask===DECK);const top=Math.min(...deck.map(s=>s.locationIndex));
   check(rest.every(id=>where(g,id).locationMask===DECK&&where(g,id).locationIndex===top),"Ge'els: the other goes to the top of the deck");check(where(g,pick).locationMask!==DECK,"Ge'els: chosen card leaves the deck to be played");
   const hand=count(g,1,HAND);g.Draw(1,1);check(rest.every(id=>where(g,id).locationMask===HAND)&&count(g,1,HAND)===hand+1,"Ge'els: the next draw is the card left on top");}],
 [200071,'hand',2,(g,pick,rest)=>{check(where(g,pick).positionPlayerId===1&&where(g,pick).locationMask===HAND,'Shilard: chosen card kept');check(rest.every(id=>where(g,id).positionPlayerId===2&&where(g,id).locationMask===HAND),'Shilard: the other goes to the opponent hand');}],
 ...[112211,152103,152213].map(id=>[id,'hand',0,(g,pick)=>check(where(g,pick).locationMask===GRAVE,id+': chosen hand card discarded to the graveyard')]),
 ...[112212,122204,142303,201638].map(id=>[id,'hand',0,(g,pick,rest,before)=>{check(where(g,pick).locationMask===DECK,id+': chosen card returns to the deck');check(count(g,1,HAND)===before,id+': a replacement card arrives');}]),
 ...[200209,200165,200048].map(id=>[id,'hand',0,null]),
 [132216,'hand',0,(g,pick)=>check(![HAND,DECK,GRAVE].includes(where(g,pick).locationMask),'Toad Prince: consumed unit leaves the hand')],
 ...[152106,200036,200159].map(id=>[id,'pile',0,(g,pick)=>check(where(g,pick).locationMask===GRAVE,id+': chosen deck card discarded to the graveyard')]),
 [112208,'hand',0,(g,pick,rest,before,opp)=>{check(where(g,pick).locationMask===HAND,'Operator: the unit stays in hand');check(count(g,2,HAND)===opp+1,'Operator: the opponent receives a copy');}],
];
for(const [id,expected,size,verify] of CASES){
 const g=session(id);const m=mode(g);
 check(expected==='pile'?m.pile&&!m.hand:m.hand&&!m.pile,id+' uses the '+expected+' UI mode its caption assumes');
 if(size)check(g.pendingIds.length===size,id+' offers '+size+' cards');
 const pick=g.pendingIds[0],rest=g.pendingIds.slice(1),before=count(g,1,HAND)-(expected==='hand'?0:0),opp=count(g,2,HAND);
 check(g.SelectTarget(g.requestId,pick),id+' accepts an offered card');
 if(g.IsPending()&&g.GetRequestSnapshot().limits.maximum>1&&g.FinishTarget)g.FinishTarget(g.requestId);
 for(let n=0;g.IsPending()&&n<8;n++){if(g.pendingIds.length)g.SelectTarget(g.requestId,g.pendingIds[0]);else if(!g.SelectRow(g.requestId,1,1))g.SelectRow(g.requestId,2,1);}
 check(!g.IsPending(),id+' finishes after the remaining steps');
 if(verify)verify(g,pick,rest,before,opp);
 check(!g.IsFatal(),id+' resolves without a fatal state');
 records.push({templateId:id,mode:expected,offered:size||m.opts.length});
}
const report={checks,records,fingerprint:rt.fingerprint,actualWitcherScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

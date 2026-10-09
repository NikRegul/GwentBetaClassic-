// Experimental response search against frozen WS rules. Not exported into 0.3.2.
// Run: node tools/ai/public_responses112.js <snapshot> <report.json>
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]);
const output=path.resolve(process.argv[3]||'BetaGwent/training/public-response112.json');
const context=vm.createContext({console});
const host=['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n');
const experiment=String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[{},{}];Host.seatIndex=1;Host.random=()=>.37;
function add(g,template,side,zone,index,power) {
 const id={v:0};g.registry.Allocate(id);const c=new CBetaGwentDuelCard();c.Setup(g,id.v,template,side,zone,index);
 if(power!==undefined){c.cardState.power.currentPower=power;c.power.currentPower=power;}
 g.registry.Put(id.v,c);g.live.push(c);return c;
}
function publicView(g) {
 const seen=new Map();
 for(const c of g.live) {
  const s=c.Snapshot();
  if(s.ownerPlayerId!==1 || !(s.locationMask&39) || (s.tokenMask&8)!==0)continue;
  const id=s.runtimeTemplate.templateId;seen.set(id,(seen.get(id)||0)+1);
 }
 // This reads a publicly displayed leader, never presetOne or hidden templates.
 return {faction:BetaGwentDuelDefinition(g.leaderTemplateOne).header.factionMask,
         hand:g.CountLocation(1,8),passed:g.match.playerOne.hasPassed,seen};
}
function belief(view) {
 const profiles={v:[]};BetaGwentAIProfileIds(profiles);const mass=new Map();let eligible=0;
 for(const profile of profiles.v) {
  const leader=BetaGwentAIProfileLeader(profile);
  if(BetaGwentDuelDefinition(leader).header.factionMask!==view.faction)continue;
  eligible++;const cards={v:[]};BetaGwentAIProfileDeck(profile,cards);
  const copies=new Map();for(const id of cards.v)copies.set(id,(copies.get(id)||0)+1);
  for(const [id,count] of copies) {
   const left=Math.max(0,count-(view.seen.get(id)||0));
   if(left)mass.set(id,(mass.get(id)||0)+left);
  }
 }
 // Keep frequently represented cards and a small set of potential control
 // replies. Their model weight remains their frequency, not an oracle score.
 const all=Array.from(mass,([id,weight])=>({id,weight})).sort((a,b)=>b.weight-a.weight||a.id-b.id);
 const control=all.filter(c=>[1,6,13,17,25,27].includes(BetaGwentDuelDefinition(c.id).effect));
 const selected=[];
 for(const c of [...control.slice(0,3),...all])if(!selected.some(x=>x.id===c.id)&&selected.length<8)selected.push(c);
 return {profiles:profiles.v.length,eligible,poolSize:all.length,candidates:selected};
}
function applyPlausibleReply(root,template) {
 const h=root.AiSimClone();if(!h)return null;
 // Erase exact archetype knowledge before turning the modeled foe into side 2.
 h.presetOne=0;h.nilfInitialOne.Clear();
 __swap(h);
 const placeholder=h.live.find(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8);
 if(!placeholder)return null;
 placeholder.Move(2,512,0); // Substitute one anonymous card; keep the hand count.
 const c=add(h,template,2,8,0);const gain=h.AiSimPlay(c.cardState.instanceId);
 if(gain===-2147483647||h.IsFatal()||h.IsPending())return null;
 __swap(h);return {game:h,gain};
}
function bestNext(g,limit=4) {
 if(g.match.currentPlayerId!==2||!g.match.turnActive)return null;
 const cards=g.live.filter(c=>c.cardState.positionPlayerId===2&&c.cardState.locationMask===8&&c.cardState.canBePlayed);
 let best=null;
 for(const c of cards.slice(0,limit)) {
  const h=g.AiSimClone();if(!h)continue;
  const gain=h.AiSimPlay(c.cardState.instanceId);
  if(gain!==-2147483647&&(best===null||gain>best))best=gain;
 }
 return best;
}
function evaluate(g,cardId) {
 const view=publicView(g),model=belief(view),root=g.AiSimClone();
 if(!root)return null;
 const first=root.AiSimPlay(cardId);if(first===-2147483647)return null;
 const rows=[];
 if(!view.passed&&view.hand>0&&root.match.currentPlayerId===1)for(const c of model.candidates) {
  const response=applyPlausibleReply(root,c.id);if(!response)continue;
  rows.push({template:c.id,title:BetaGwentDuelDefinition(c.id).title,weight:c.weight,
             replyGain:response.gain,ourContinuation:bestNext(response.game)});
 }
 const weight=rows.reduce((n,c)=>n+c.weight,0);
 // A weighted diagnostic, not a calibrated probability that a card is held.
 const expectedReply=weight?rows.reduce((n,c)=>n+c.replyGain*c.weight,0)/weight:0;
 return {card:cardId,template:g.FindCard(cardId).TemplateId(),firstGain:first,
         profiles:model.profiles,eligibleProfiles:model.eligible,poolSize:model.poolSize,
         candidates:model.candidates,replies:rows,expectedReplyGain:expectedReply,
         worstReplyGain:rows.length?Math.max(...rows.map(c=>c.replyGain)):0,
         modeledNet:first-expectedReply,rejectedReplies:model.candidates.length-rows.length};
}
function fixture() {
 const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,88))throw Error('fixture');
 g.live.forEach(c=>c.Move(c.cardState.positionPlayerId,512,0));
 g.mulligan=false;g.pendingCard=null;g.pendingLeader=null;g.waiting=false;g.weatherProfile=false;
 g.match.currentPlayerId=2;g.match.turnActive=true;g.match.roundActive=true;g.match.roundNumber=1;
 g.match.playerOne.hasPassed=false;g.match.playerOne.crowns=0;g.match.playerTwo.hasPassed=false;g.recordVisuals=false;
 add(g,123301,2,2,0);add(g,112101,2,2,1);add(g,122104,1,1,0);
 add(g,122104,2,32,0);
 for(let i=0;i<3;i++)add(g,112101,1,8,i);
 return g;
}
const g=fixture();const ids=[123301,112101,122106].map(id=>add(g,id,2,8,0).cardState.instanceId);
const model=belief(publicView(g));if(model.profiles!==46)throw Error('all 46 archetypes must be represented');
function gameplayState(g) { return JSON.stringify({cards:g.live.map(c=>c.Snapshot()),match:g.match.Snapshot(),
 seed:g.random.InitialSeed(),draws:g.random.DrawCount(),request:g.requestId,waiting:g.waiting}); }
const before=gameplayState(g);
const results=ids.map(id=>evaluate(g,id));
if(gameplayState(g)!==before)throw Error('diagnostic changed cards, match, random state or active request');
// Change true hidden identities, powers and the exact preset. The public model
// and answer branches must remain identical, not merely hide their log labels.
const hidden=g.live.filter(c=>c.cardState.positionPlayerId===1&&c.cardState.locationMask===8);
for(const c of hidden){c.definition=BetaGwentDuelDefinition(122106);c.cardState.runtimeTemplate=c.definition.header;
 c.cardState.power.currentPower=40;c.power.currentPower=40;}
g.presetOne=90;
const changed=ids.map(id=>evaluate(g,id));
if(JSON.stringify(changed)!==JSON.stringify(results))throw Error('hidden information affected the response search');
g.match.playerOne.hasPassed=true;
if(evaluate(g,ids[0]).replies.length!==0)throw Error('response model must not invent a move after pass');
globalThis.result={experimental:true,nativeIntegration:false,trainingImportAllowed:false,
 poolProfiles:40,privacyInvariantVerified:true,actualGameUnchanged:true,passedOpponentHasNoReply:true,
 results,limitations:['Frequency weights are not calibrated hand probabilities.',
 'Only eight modeled hand responses and four continuations are evaluated.',
 'Unavailable chains are reported and excluded, which can bias the result.',
 'Known opponent leader responses and observed-archetype posteriors remain to be added.']};
`;
vm.runInContext(host+'\n'+experiment,context,{filename:'public-response112.bundle.js',timeout:180000});
fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify(context.result,null,2));
console.log('Experimental response report:',output);
console.log('40 archetypes; privacy invariant; unchanged actual state; pass check verified.');
for(const r of context.result.results)console.log(r&&{template:r.template,first:r.firstGain,replies:r.replies.length,net:r.modeledNet});

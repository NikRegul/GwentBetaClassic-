'use strict';
// Review list for a real game log: every logged AI unit-target choice is
// replayed from its decision-start position (partial log snapshot, no hidden
// cards), the logged card is forced, and each first pick is tried on a clone
// (later picks finished by the AI). Choices worse than the best by >= gap are
// listed for review; this is NOT proof of a bug (positions are partial).
// Usage: node flag_ai_log102.cjs <rules-dir> <decisions.json from audit_ai_log198.py> [out.json] [gap=2]
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const D=JSON.parse(fs.readFileSync(process.argv[3],'utf8'));const minGap=+(process.argv[5]||2);
const lead=g=>g.Score(2)-g.Score(1);
function prepare(g){let t=0;while(!g.AiPreparationStep())if(++t>12000)throw Error('stalled');}
function finish(k){for(let i=0;i<8&&k.IsPending();i++){prepare(k);k.OpponentStep();}k.FlushDeaths();}
function rebuild(game,dec){
 const g=fixture(2),byId=new Map();g.externalPolicyMask=0;g.aiSimDamp=70;const p=dec.position,b=dec.begin;
 g.presetOne=+p.presetOne;g.presetTwo=+p.presetTwo;g.leaderTemplateOne=+game.start.ownLeader;g.leaderTemplateTwo=+game.start.enemyLeader;
 const m=g.match;m.roundNumber=+b.round;m.playerOne.crowns=+b.enemyCrowns;m.playerTwo.crowns=+b.ownCrowns;m.playerOne.hasPassed=b.enemyPassed==='true';
 for(const c of dec.cards){if(c.zone===512)continue;const card=add(g,c.template,c.side,c.zone,c.index,c.power,c.armor,c.tokens);byId.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.timerValue=c.timer;card.cardState.canBePlayed=!!c.playable;card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);}
 g.archetypeAI.Initialize(g,[],g.presetTwo,g.leaderTemplateTwo);
 g.aiStartingDeckOne.Clear();for(const t of (p.known||'').split(',').filter(Boolean))g.aiStartingDeckOne.PushBack(+t);
 g.aiRoundHandTwo=g.CountLocation(2,8);g.aiRoundHandOne=g.CountLocation(1,8);return {g,byId};}
const flags=[],skipped=[];let examined=0;
for(const game of D.games)for(const dec of game.decisions){
 if(!dec.position||dec.cards.length!==+dec.position.cardCount)continue;
 const sel=dec.events.find(e=>e.event==='SELECT'&&e.action==='card');if(!sel)continue;
 const first=dec.events.find(e=>e.event==='TARGET_SELECT'&&e.kind==='0'&&e.source===String(dec.cards.find(c=>c.id===+sel.card)?.template));
 if(!first)continue;
 const rowEv=dec.events.find(e=>e.event==='ROW'&&e.card===sel.card&&e.selected==='true');
 examined++;const where={game:game.index,decision:dec.begin.decision,line:+first.line,card:+sel.card,template:+sel.template,loggedTarget:+first.target};
 try{
  const {g,byId}=rebuild(game,dec);const l0=lead(g);let h=null;
  const cardId=byId.get(+sel.card).Snapshot().instanceId,loggedId=byId.has(+first.target)?byId.get(+first.target).Snapshot().instanceId:-1;
  const logOf=new Map([...byId].map(([k,c])=>[c.Snapshot().instanceId,k]));
  for(const row of rowEv?[+rowEv.row]:[1,2,4]){const k=rt.cloneSession(g);k.externalPolicyMask=3;if(k.Play(2,cardId,row)){h=k;break;}}
  if(!h||!h.pendingIds.includes(loggedId)){skipped.push({...where,reason:h?'logged_target_not_offered':'replay_play_failed'});continue;}
  const all=[];
  for(const t of [...h.pendingIds]){const k=rt.cloneSession(h);k.externalPolicyMask=0;k.aiSimulating=true;if(!k.SelectTarget(k.requestId,t))continue;finish(k);if(k.IsFatal())continue;
   const c=h.FindCard(t).Snapshot();all.push({target:logOf.get(t)??t,side:c.positionPlayerId,template:c.runtimeTemplate.templateId,power:c.power.currentPower,lead:lead(k)-l0});}
  const logged=all.find(a=>a.target===+first.target),best=all.reduce((a,b)=>b.lead>a.lead?b:a,all[0]);
  if(logged&&best&&best.lead-logged.lead>=minGap){

   // Full current-rules move from the decision start (the AI may now pick another card).
   let now=null;try{const k=rt.cloneSession(g);k.externalPolicyMask=0;prepare(k);let ok=false;for(let i=0;i<4&&!ok;i++){ok=k.OpponentStep();if(!ok)prepare(k);}finish(k);now=lead(k)-l0;}catch(e){}
   flags.push({...where,kind:'target_choice_below_best',gap:best.lead-logged.lead,logged,best,currentRulesLead:now,fixedByCurrentRules:now!==null&&best.lead-now<minGap});}
 }catch(e){skipped.push({...where,reason:'error '+String(e.message).slice(0,80)});}
}
const report={examined,flags,skipped,minGap,scope:'Review list from partial logged positions; not a bug verdict.'};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({examined,flags:flags.map(f=>[f.game,f.decision,f.template,f.logged.template+'@'+f.logged.side,'best',f.best.template+'@'+f.best.side,'gap',f.gap,'now',f.currentRulesLead,'fixed',f.fixedByCurrentRules]),skipped:skipped.length}));

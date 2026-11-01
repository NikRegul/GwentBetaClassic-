'use strict';
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const positions=require('./fixtures/feedback101.json').positions;
function rebuild(p){
 const g=fixture(2),byId=new Map();g.externalPolicyMask=0;g.aiSimDamp=70;
 g.presetOne=+p.position.presetOne;g.presetTwo=+p.position.presetTwo;
 g.leaderTemplateOne=+p.start.ownLeader;g.leaderTemplateTwo=+p.start.enemyLeader;
 const m=g.match;m.roundNumber=+p.begin.round;m.playerOne.crowns=+p.begin.enemyCrowns;m.playerTwo.crowns=+p.begin.ownCrowns;m.playerOne.hasPassed=p.begin.enemyPassed==='true';
 for(const c of p.cards){if(c.zone===512)continue;
  const card=add(g,c.template,c.side,c.zone,c.index,c.power,c.armor,c.tokens);byId.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.timerValue=c.timer;card.cardState.canBePlayed=!!c.playable;
  card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);
 }
 g.archetypeAI.Initialize(g,[],g.presetTwo,g.leaderTemplateTwo);
 g.aiStartingDeckOne.Clear();for(const t of (p.position.known||'').split(',').filter(Boolean))g.aiStartingDeckOne.PushBack(+t);
 g.aiRoundHandTwo=g.CountLocation(2,8);g.aiRoundHandOne=g.CountLocation(1,8);return {g,byId};
}
if(require.main===module)for(const p of positions){
 const {g,byId}=rebuild(p),logs=[];rt.host.log=s=>logs.push(s);
 if(p.name==='scorch'){
  const h=rt.cloneSession(g);h.aiSimulating=true;console.log('pass-before',g.Score(2),g.Score(1),g.AiPublicPassLead(true));
  for(let i=0;i<3&&!h.Snapshot().matchWinnerMask;i++){const side=h.Snapshot().currentPlayerId;console.log('pass',side,h.Pass(side),h.Score(2),h.Score(1),h.Snapshot().matchWinnerMask);}
 }
 g.OpponentStep();rt.host.log=null;
 console.log(p.name,p.begin.decision,logs.filter(s=>/event=(SELECT|PASS|LEADER_OPTION|TARGET_FINISH)/.test(s)));
}
module.exports={rt,rebuild,positions};

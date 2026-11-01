'use strict';
// Halving answers (Morvudd) are kept while a bigger target the opponent may
// still hold is public (starting list minus seen copies), not when the opponent
// passed, has no cards, or nothing bigger can follow. Hard never reads the real
// hidden hand. Usage: node check_answer_reserve102.cjs <rules-dir> [report.json]
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const p=require('./fixtures/answer102.json').positions[0];
let checks=0;const failures=[],cases=[];function check(ok,n){checks++;if(!ok)failures.push(n);}
function prepare(g){let t=0;while(!g.AiPreparationStep())if(++t>12000)throw Error('stalled');}
function act(g){const logs=[];rt.host.log=s=>logs.push(s);try{prepare(g);let ok=false;for(let i=0;i<4&&!ok;i++){ok=g.OpponentStep();if(!ok)prepare(g);}}finally{rt.host.log=null;}
 return logs.filter(s=>/ANSWER_RESERVE|event=SELECT|DUEL_PLAY player=2/.test(s));}
function rebuild(hideTibor){const g=fixture(2),byId=new Map();g.externalPolicyMask=0;g.aiSimDamp=70;const P=p.position,b=p.begin;
 g.presetOne=+P.presetOne;g.presetTwo=+P.presetTwo;g.leaderTemplateOne=+p.start.ownLeader;g.leaderTemplateTwo=+p.start.enemyLeader;
 g.match.roundNumber=+b.round;g.match.playerOne.crowns=+b.enemyCrowns;g.match.playerTwo.crowns=+b.ownCrowns;
 for(const c of p.cards){if(c.zone===512)continue;const card=add(g,c.template,c.side,c.zone,c.index,c.power,c.armor,c.tokens);byId.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.timerValue=c.timer;card.cardState.canBePlayed=!!c.playable;card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);}
 g.archetypeAI.Initialize(g,[],g.presetTwo,g.leaderTemplateTwo);g.aiStartingDeckOne.Clear();
 for(const t of (P.known||'').split(',').filter(Boolean))if(!(hideTibor&&+t===162107))g.aiStartingDeckOne.PushBack(+t);
 g.aiRoundHandTwo=g.CountLocation(2,8);g.aiRoundHandOne=g.CountLocation(1,8);return {g,byId};}
const morvudd=43;
{const {g,byId}=rebuild(false);const draws=g.random.DrawCount();const logs=act(g);cases.push({name:'logged',logs});
 check(logs.some(s=>s.includes('ANSWER_RESERVE')&&s.includes('template=132205')),'logged: Morvudd reserve is explained');
 check(byId.get(morvudd).Snapshot().locationMask===8,'logged: Morvudd is kept while Tibor may follow');}
// Hidden identities must not matter: replace the opponent's real hand.
{const a=rebuild(false),b=rebuild(false);for(const c of b.g.live){const s=c.Snapshot();if(s.positionPlayerId===1&&s.locationMask===8)c.cardState.runtimeTemplate.templateId=112405;}
 const la=act(a.g).filter(s=>/SELECT|ANSWER/.test(s)),lb=act(b.g).filter(s=>/SELECT|ANSWER/.test(s));
 check(JSON.stringify(la)===JSON.stringify(lb),'reserve ignores the real hidden enemy hand');}
// No bigger public target: no reserve.
{const {g}=rebuild(true);const logs=act(g);cases.push({name:'no Tibor in list',logs});check(!logs.some(s=>s.includes('ANSWER_RESERVE')),'no bigger public target: no reserve');}
// Opponent passed: answer now.
{const {g}=rebuild(false);g.match.playerOne.hasPassed=true;const logs=act(g);check(!logs.some(s=>s.includes('ANSWER_RESERVE')),'passed opponent: no reserve');}
// Morvudd is the last card: play it.
{const {g,byId}=rebuild(false);for(const [id,c] of byId){const s=c.Snapshot();if(s.positionPlayerId===2&&s.locationMask===8&&id!==morvudd)c.Move(2,512,0);}
 const logs=act(g);check(!logs.some(s=>s.includes('ANSWER_RESERVE')),'last card: no reserve');}
const report={checks,failures,cases,fingerprint:rt.fingerprint,actualWitcherScript:true,historicalRuntimeVerified:false,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;

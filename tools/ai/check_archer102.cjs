'use strict';
// Tuirseach Archer (152315) and the Raging Berserker/Bear (152301/152405).
// Log 01.11.2026, decision 17: 16 targets, no exact simulation (more than 14),
// the static score was the target's power regardless of side, so the archer hit
// the AI's own 12-power bear. Usage: node check_archer102.cjs <rules-dir> [report.json]
const fs=require('fs'),path=require('path');
const rt=require('./beta_js092/session.cjs').createRuntime(path.resolve(process.argv[2]));
const {fixture,add}=require('./audit_fixture095.cjs')(rt);
const positions=require('./fixtures/archer102.json').positions;
let checks=0;const failures=[],cases=[];
function check(ok,n){checks++;if(!ok)failures.push(n);}
function prepare(g){let t=0;while(!g.AiPreparationStep())if(++t>12000)throw Error('stalled');}
function act(g){const logs=[];rt.host.log=s=>logs.push(s);
 try{prepare(g);let ok=false;for(let i=0;i<4&&!ok;i++){ok=g.OpponentStep();if(!ok)prepare(g);}check(ok&&!g.IsFatal()&&!g.IsPending(),'action resolves');}
 finally{rt.host.log=null;}return logs.filter(s=>/event=(SELECT|TARGET_SELECT)|DUEL_TRANSFORM|DUEL_PLAY /.test(s));}
function rebuild(p){
 const g=fixture(2),byId=new Map();g.externalPolicyMask=0;g.aiSimDamp=70;
 g.presetOne=+p.position.presetOne;g.presetTwo=+p.position.presetTwo;
 g.leaderTemplateOne=+p.start.ownLeader;g.leaderTemplateTwo=+p.start.enemyLeader;
 const m=g.match;m.roundNumber=+p.begin.round;m.playerOne.crowns=+p.begin.enemyCrowns;m.playerTwo.crowns=+p.begin.ownCrowns;m.playerOne.hasPassed=p.begin.enemyPassed==='true';
 for(const c of p.cards){if(c.zone===512)continue;
  const card=add(g,c.template,c.side,c.zone,c.index,c.power,c.armor,c.tokens);byId.set(c.id,card);
  card.cardState.ownerId=c.owner;card.cardState.timerValue=c.timer;card.cardState.canBePlayed=!!c.playable;
  card.power.ResetTemplatePower(c.base,c.armor);card.power.SetCurrentPair(c.power,c.armor);}
 g.archetypeAI.Initialize(g,[],g.presetTwo,g.leaderTemplateTwo);
 g.aiStartingDeckOne.Clear();for(const t of (p.position.known||'').split(',').filter(Boolean))g.aiStartingDeckOne.PushBack(+t);
 g.aiRoundHandTwo=g.CountLocation(2,8);g.aiRoundHandOne=g.CountLocation(1,8);return {g,byId};}
function ownField(g){return g.live.map(c=>c.Snapshot()).filter(s=>s.positionPlayerId===2&&(s.locationMask&7)!==0);}
// 1. The logged position: the archer is the last card, the enemy has passed.
{
 const p=positions.find(p=>p.name==='archer-d17'),{g,byId}=rebuild(p);
 const bear=byId.get(50),before=new Map(ownField(g).map(s=>[s.instanceId,s.power.currentPower]));
 const logs=act(g);cases.push({name:p.name,logs});
 check(logs.some(s=>s.includes('DUEL_PLAY player=2 template=152315')),'logged archer is played');
 check(bear.Snapshot().power.currentPower===12,'logged own bear is not hit');
 check(ownField(g).every(s=>!before.has(s.instanceId)||s.power.currentPower>=before.get(s.instanceId)),'no own unit loses power');
}
// 2. Synthetic static path (more than 14 targets) and exact path (at most 14).
function board(many,own,ownPower,enemyBerserker){
 const g=fixture(2);g.externalPolicyMask=0;g.match.roundNumber=2;
 const key=add(g,own,2,2,0,ownPower);const enemy=[];
 const fillers=many?7:3,enemies=many?8:4;
 for(let i=0;i<fillers;i++)add(g,112405,2,[1,4][i%2],Math.floor(i/2),3);
 for(let i=0;i<enemies;i++)enemy.push(add(g,i===0&&enemyBerserker?152301:112405,1,[1,2,4][i%3],Math.floor(i/3),i===0&&enemyBerserker?8:5));
 add(g,152315,2,8);add(g,112405,1,8);add(g,112405,1,8);return {g,key,enemy};}
for(const many of [true,false]){
 {const {g,key}=board(many,152405,12);const logs=act(g);cases.push({name:'bear many='+many,logs});
  check(key.Snapshot().power.currentPower===12,'own bear is not hit, many='+many);}
 {const {g,key}=board(many,152301,8);const logs=act(g);cases.push({name:'berserker many='+many,logs});
  const s=key.Snapshot();check(s.runtimeTemplate.templateId===152405&&s.power.currentPower===12,'own berserker is hit and becomes a bear, many='+many);}
 {const {g,enemy}=board(many,112405,3,true);const logs=act(g);cases.push({name:'enemy berserker many='+many,logs});
  check(enemy[0].Snapshot().runtimeTemplate.templateId===152301,'enemy berserker is not turned into a bear, many='+many);}
}
const report={checks,failures,cases,fingerprint:rt.fingerprint,actualWitcherScript:true,historicalRuntimeVerified:false,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;

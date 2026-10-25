/* Transport fixture only: frozen P16 policy on original native states containing
 * exclusively ability-free Geralt units and disabled leaders. Never used as a
 * roster adapter or a strength comparison. Any broader state is rejected. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..');
const rules=path.join(root,'BetaGwent/build/release092-beta-final-20261023/rules');
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
const hash=f=>crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex');
for(const [file,sha]of Object.entries(manifest.snapshotFiles))if(hash(path.join(rules,file))!==sha)throw Error('Frozen control changed');
const source=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const decide=new Function('native','memory','tunes','seed',source+String.raw`
Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[tunes,tunes];Host.seatIndex=1;
let random=seed>>>0||1;Host.random=()=>{random^=random<<13;random>>>=0;random^=random>>>17;random>>>=0;random^=random<<5;random>>>=0;return random/4294967296;};
const request=native.requests[0],actor=request?.player;
if(native.kind!=='original-authoritative-state-not-policy-observation'||native.state!==32||native.winner!==0||
 ![1,2].includes(actor)||request?.kind!=='RequestPlayCardAction'||request.details.forcedCard!==0||
 native.players.some(p=>p.hasMadeInitialMove)||native.cards.some(c=>c.inExecutionStack||c.beingPlayed||c.waitingToDie))
 throw Error('Body transport fixture requires normal decision boundary');
if(native.cards.some(c=>c.position.zone===64?c.playable:c.template!==112103||c.tokens!==0||c.timer!==-1||c.power!==15||c.basePower!==15||c.permanentPower!==0||c.armor!==0))
 throw Error('Body transport fixture rejects abilities, active leaders or modified units');
const flip=n=>n===actor?2:n===3-actor?1:n;
const g=new CBetaGwentDuelSession();if(!g.InitializeWithPresets(54,54))throw Error('Framework initialization failed');
g.live=[];g.registry=new CBetaGwentDuelRegistry();g.registry.Initialize();
while(g.registry.nextId<=Math.max(...native.cards.map(c=>c.id))){const id={v:0};if(!g.registry.Allocate(id))throw Error('Allocate');}
for(const c of native.cards){
 if(![1,2,4,8,16,32,64,512].includes(c.position.zone))throw Error('Unknown zone');
 const card=new CBetaGwentDuelCard();card.Setup(g,c.id,c.template,flip(c.position.side),c.position.zone,c.position.index);
 const s=card.cardState;s.canBePlayed=c.playable;s.runtimeTierMask=c.tier;s.tokenMask=c.tokens;s.timerValue=c.timer;
 s.power.basePower=c.basePower;s.power.permanentPower=c.permanentPower;s.power.currentPower=c.power;s.power.armor=c.armor;
 card.power.initialized=false;card.power.InitFromFields(s.power);g.registry.Put(c.id,card);g.live.push(card);
}
g.mulligan=false;g.waiting=false;g.pendingCard=null;g.pendingLeader=null;g.pendingRally=null;g.recordVisuals=false;
g.presetOne=0;g.presetTwo=0;g.leaderTemplateOne=native.cards.find(c=>c.position.zone===64&&flip(c.position.side)===1).template;
g.leaderTemplateTwo=native.cards.find(c=>c.position.zone===64&&flip(c.position.side)===2).template;
g.aiStartingDeckOne=Array(25).fill(112103);g.aiStartingDeckTwo=Array(25).fill(112103);
g.nilfInitialOne=Array(25).fill(112103);g.nilfInitialTwo=Array(25).fill(112103);
g.nilfSpellOne=0;g.nilfSpellTwo=0;g.nilfLastMovedUnit=0;
g.weatherAI.Initialize(g);g.weatherProfile=false;g.archetypeAI.Initialize(g,g.nilfInitialTwo,0,g.leaderTemplateTwo);
g.match.roundNumber=native.round;g.match.startingPlayerId=flip(native.starting);g.match.currentPlayerId=2;
g.match.turnSequence=native.rounds.reduce((n,r)=>n+r.turn,0);g.match.roundActive=true;g.match.turnActive=true;g.match.results=[];
for(const p of native.players){const dest=flip(p.id)===1?g.match.playerOne:g.match.playerTwo;
 dest.crowns=p.crowns;dest.hasPassed=p.passed;dest.hasMadeInitialMoveForCurrentTurn=p.hasMadeInitialMove;
 if(g.Score(flip(p.id))!==p.score)throw Error('Body fixture score import mismatch');}
for(const r of native.rounds.filter(r=>r.finished)){
 const x=new SBetaGwentRoundResult();x.roundNumber=r.id;x.startingPlayerId=flip(r.starting);
 x.scoreOne=r.scores[3-actor-1];x.scoreTwo=r.scores[actor-1];
 x.winnerMask=actor===2?r.winner:((r.winner&1)<<1)|((r.winner&2)>>1);
 x.crownDeltaOne=(x.winnerMask&1)?1:0;x.crownDeltaTwo=(x.winnerMask&2)?1:0;g.match.results.push(x);
}
g.aiRoundHandOne=native.roundHands[3-actor-1];g.aiRoundHandTwo=native.roundHands[actor-1];g.aiSimDamp=40;g.ClearAiPreparation();
const keys=['aiChaseRound','aiChaseInitialHand','aiChaseSpent','aiObservedRound','aiObservedEnemyScore','aiPublicTempo'];
for(const k of keys)if(memory[k]!==undefined)g[k]=memory[k];
for(const k of ['planRound','roundPlan','planEnemyInvestment','planOwnInvestment'])if(memory.archetype?.[k]!==undefined)g.archetypeAI[k]=memory.archetype[k];
let action=null;const logs=[];Host.log=line=>logs.push(line);
function capture(a){if(action)throw Error('Multiple actions');action=a;return true;}
g.Play=(s,card,row)=>capture({kind:'play',card,row});
g.PlayBefore=()=>{throw Error('Unexpected adjacency in ability-free fixture');};
g.UseLeader=()=>{throw Error('Disabled leader used in body fixture');};
g.Pass=s=>capture({kind:'pass'});
if(!g.OpponentStep()||!action||g.IsFatal())throw Error('Frozen policy failed in body fixture');
const nextMemory={archetype:{}};for(const k of keys)nextMemory[k]=g[k];
for(const k of ['planRound','roundPlan','planEnemyInvestment','planOwnInvestment'])nextMemory.archetype[k]=g.archetypeAI[k];
if(action.kind==='play'){
 const move=request.details.moves.find(m=>m.card===action.card&&m.position.side===actor&&m.position.zone===action.row);
 if(!move)throw Error('Frozen policy proposed illegal native move');action={kind:'play',...move};
}else if(!request.details.canPass)throw Error('Frozen policy proposed illegal pass');
return {action,memory:nextMemory,logs};
`);
const tunes=JSON.parse(fs.readFileSync(path.join(rules,'tunes.json'),'utf8'));
module.exports={fingerprint:manifest.fingerprint,chooseBody:(native,memory={},seed=923058401)=>decide(native,memory,tunes,seed)};

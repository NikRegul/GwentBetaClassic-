/* Shared JS/WS battle session access for the direct JS AI port. This loads the
 * existing stand's rules once; it never starts or synchronizes another engine. */
'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const templates=require('./data/templates.json'),profiles=require('./data/personalities.json');
const {personality}=require('./profiles.cjs');
const root=path.resolve(__dirname,'../../..');
function basePersonality(){return personality('Base');}
function createRuntime(rules=path.join(root,'BetaGwent/build/release092-swarm-fix2-20261023/rules'),seed=923071001,policyGraft=null){
 const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
 for(const [file,sha]of Object.entries(manifest.snapshotFiles)){
  const digest=crypto.createHash('sha256').update(fs.readFileSync(path.join(rules,file))).digest('hex');
  if(digest!==sha)throw Error('Frozen shared rules changed: '+file);
 }
 let policyRules=path.join(rules,'rules.js'),policyIdentity=null;
 if(policyGraft){
  const proof=JSON.parse(fs.readFileSync(path.join(policyGraft,'comparison.json'),'utf8'));
  if(path.resolve(proof.candidate)!==path.resolve(rules)||!proof.original091||!proof.sharedBattleMechanics)throw Error('Historical policy graft is not for these common rules');
  policyRules=path.join(policyGraft,'rules.js');
  const digest=crypto.createHash('sha256').update(fs.readFileSync(policyRules)).digest('hex');
  if(digest!==proof.baselineRules)throw Error('Historical policy graft changed');
  policyIdentity={version:'0.9.1',rulesSha256:digest,originalSnapshot:proof.oldSnapshot};
 }
 const source=[fs.readFileSync(path.join(rules,'runtime.js'),'utf8'),fs.readFileSync(policyRules,'utf8'),fs.readFileSync(path.join(rules,'harness.js'),'utf8')].join('\n');
 const tunes=JSON.parse(fs.readFileSync(path.join(policyGraft||rules,'tunes.json'),'utf8'));
 // This codec transfers a single JS battle state between historical policy
 // contexts built with identical common mechanics. It never runs C# or keeps
 // a second independently advancing game. Clone caches are disposable.
 const codec=require('../comparison_bridge119.js').split('let active=null')[0].replace(/\brandomState\b/g,'rngState');
 const make=new Function('tunes','seed',source+String.raw`
 Host.strength=4;Host.matchStrength=[4,4];Host.tunes=[tunes,tunes];Host.seatIndex=1;
 let rngState=seed>>>0||1;
 Host.random=()=>{rngState^=rngState<<13;rngState>>>=0;rngState^=rngState>>>17;rngState>>>=0;rngState^=rngState<<5;rngState>>>=0;return rngState/4294967296;};
 // Production cloner stamps live on source objects. Allocate across ALL Beta
 // searches in this runtime, never restart a per-tree stamp counter and reuse
 // another tree's cached state. Negative range is separate from current AI.
 let betaCloneStamp=-2000000000;
 `+codec+String.raw`
 return {externalPolicyHooks:typeof CBetaGwentDuelSession.prototype.IsExternalPolicy==='function',
  newSession:()=>new CBetaGwentDuelSession(),newCard:()=>new CBetaGwentDuelCard(),newCloner:()=>new CBetaGwentCloner(),definition:id=>BetaGwentDuelDefinition(id),
  validateDeck:(cards,faction,leader)=>BetaGwentValidateDeck(cards,faction,leader),swap:__swap,isReversed:__reversed,
  serialize:g=>pack(g,true),deserialize:data=>unpack(data),
  cloneSession:g=>new CBetaGwentCloner().CloneSession(g,++betaCloneStamp),host:Host};
 `);
 return {...make(tunes,seed),fingerprint:manifest.fingerprint,policyIdentity};
}
function stateFromSession(game){
 const m=game.Snapshot(),cards=[],rows=[];
 for(let i=0;i<game.live.length;i++){
  const c=game.live[i],s=c.Snapshot(),t=templates[String(c.TemplateId())];
  if(!t)throw Error('Original template metadata missing: '+c.TemplateId());
  cards.push({id:s.instanceId,templateId:t.id,side:s.positionPlayerId,zone:s.locationMask,index:s.locationIndex,
   playable:s.canBePlayed,templateTier:s.runtimeTemplate.tierMask,runtimeTier:s.runtimeTierMask,type:s.runtimeTemplate.typeMask,
   printedPower:s.runtimeTemplate.power,power:s.power.currentPower,basePower:s.power.basePower,tokens:s.tokenMask,linkedTemplateId:t.linkedTemplateId,
   placement:t.placement,inExecution:s.isInExecutionStack||game.playStack.includes(c),visibleToBoth:(s.tokenMask&8)===0,
   semanticTags:t.semanticTags,categories:t.categories});
 }
 // Board-manager ordering is preserved when selecting stable ties in hand.
 cards.sort((a,b)=>a.side-b.side||a.zone-b.zone||a.index-b.index||a.id-b.id);
 for(let side=1;side<=2;side++)for(let row=1;row<=4;row*=2)rows.push({side,row,token:game.WeatherToken(side,row)});
 return {currentPlayerId:m.currentPlayerId,startingPlayerId:m.startingPlayerId,roundIndex:m.roundNumber-1,
  roundTurnIndex:game.match.roundTurnIndex,currentRoundWinner:game.match.results.find(r=>r.roundNumber===m.roundNumber)?.winnerMask||0,
  roundId:m.roundNumber,winnerMask:m.matchWinnerMask,players:[{score:game.Score(1)},{score:game.Score(2)}],
  passed:[m.playerOne.hasPassed,m.playerTwo.hasPassed],
  cards,rows,rounds:game.match.results.map(r=>({winnerMask:r.winnerMask,playerScores:[r.scoreOne,r.scoreTwo]}))};
}
module.exports={createRuntime,stateFromSession,basePersonality,templates};

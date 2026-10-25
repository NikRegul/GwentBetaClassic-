'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {technicalAction}=require('./check_native_choice_adapter092.cjs');
const {inspectNativeModel,fingerprint}=require('./native_session_import092.cjs');
const draft=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const {reports}=require('./native_bridge_paths092.cjs');
const rosters=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8'));
async function run(name){
  const deck=rosters.decks.find(d=>d.asset===name);assert(deck);
  const config={mode:'external',deck:{faction:deck.faction,leader:deck.leader.templateId,cards:deck.cards}};
  const client=new OriginalBetaClient();let s;
  const result={deck:name,imported:0,cardsCompared:0,randomWordsCompared:0,rounds:[],hazardStates:0,rejected:{},errors:0};
  try{
    s=await client.request('init',{seed:923058101,first:1,players:[config,config]});
    for(let steps=0;steps<350&&s.winner===0;steps++){
      const req=s.requests[0];assert(req);
      if(req.kind==='RequestPlayCardAction'&&req.details.forcedCard===0&&
         !s.cards.some(c=>c.inExecutionStack||c.beingPlayed||c.waitingToDie)){
        for(const actor of [1,2]){
          const before=JSON.stringify(s),memory={aiPublicTempo:19,aiEnemyRowPlays:[2,3,4],archetype:{planRound:2,roundPlan:1,planEnemyInvestment:7,planOwnInvestment:8}};
          let model;
          try{model=inspectNativeModel(s,[config,config],{actor,memory});}
          catch(e){
            if(!/Unmapped persistent ability state|Unmapped location token/.test(e.message))throw e;
            result.rejected[e.message]=(result.rejected[e.message]||0)+1;continue;
          }
          assert.equal(JSON.stringify(s),before,'Model import changed authoritative snapshot');
          assert.equal(model.fullMatchReady,false,'Partial model must not claim full adapter');
          assert.equal(model.round,s.round);assert.equal(model.current,s.current);
          assert.deepEqual(model.crowns,actor===2?s.players.map(p=>p.crowns):s.players.map(p=>p.crowns).reverse());
          assert.deepEqual(model.roundHands,actor===2?s.roundHands:s.roundHands.slice().reverse());
          assert.equal(model.cards.length,s.cards.length);
          for(const card of model.cards){
            const original=s.cards.find(c=>c.id===card.id);assert(original);
            assert.deepEqual(card,{id:original.id,template:original.template,side:original.position.side,
              zone:original.position.zone,index:original.position.index,tier:original.tier,tokens:original.tokens,timer:original.timer,
              playable:original.playable,basePower:original.basePower,power:original.power,permanentPower:original.permanentPower,armor:original.armor,
              inExecutionStack:original.inExecutionStack,waitingToDie:original.waitingToDie});
          }
          const {encoding,...random}=s.random;assert.deepEqual(model.random,random,'RNG checkpoint changed during import');
          const hazards=[];
          for(const side of actor===2?[1,2]:[2,1])for(const zone of [1,2,4])hazards.push(s.locations.find(l=>l.side===side&&l.zone===zone).tokens);
          assert.deepEqual(model.hazards,hazards);assert.deepEqual(model.memory.aiEnemyRowPlays,memory.aiEnemyRowPlays);
          assert.equal(model.memory.aiPublicTempo,19);assert.deepEqual(model.memory.archetype,memory.archetype);
          const finished=s.rounds.filter(r=>r.finished);assert.equal(model.results.length,finished.length);
          for(let i=0;i<finished.length;i++){
            const expected=finished[i],actual=model.results[i];
            assert.equal(actual.roundNumber,expected.id);
            assert.equal(actual.startingPlayerId,actor===2?expected.starting:3-expected.starting);
            assert.equal(actual.scoreOne,expected.scores[2-actor]);assert.equal(actual.scoreTwo,expected.scores[actor-1]);
            assert.equal(actual.winnerMask,actor===2?expected.winner:((expected.winner&1)<<1)|((expected.winner&2)>>1));
          }
          result.imported++;result.cardsCompared+=model.cards.length;result.randomWordsCompared+=model.random.words.length;
          if(hazards.some(Boolean))result.hazardStates++;
          if(!result.rounds.includes(s.round))result.rounds.push(s.round);
        }
      }
      s=await client.request('action',{sequence:s.sequence,request:req.id,...technicalAction(s)});
      assert.equal(s.loggerErrors,0);
    }
    assert.notEqual(s.winner,0);assert(result.imported>0);console.log(JSON.stringify(result));return result;
  }catch(e){fs.writeFileSync(path.join(reports,'native-session-import-failure.json'),JSON.stringify({deck:name,error:e.stack,state:s},null,2)+'\n');throw e;}
  finally{await client.close();}
}
(async()=>{
  const results=[];
  for(const name of ['d_Skellige_Practice_Easy','d_Nilfgaard_Practice','d_NorthernRealms_Practice',"d_Scoia'tael_Practice_Easy"])
    results.push(await run(name));
  const report={schema:1,complete:true,fingerprint,fullMatchReady:false,
    scope:'Partial shared WS model import: exact cards/ordering/location tokens/RNG/round history and supplied policy-memory roundtrip. Both actor orientations on ordinary states of four complete native technical-driver games. Unknown persistent state rejected; policy memory reconstruction/history/ability counters still incomplete. No policy strength result.',results};
  fs.writeFileSync(path.join(reports,'native-session-import-smoke.json'),JSON.stringify(report,null,2)+'\n');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});

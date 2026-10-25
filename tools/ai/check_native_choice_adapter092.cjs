/* Actual native games up to a paused request, then frozen WS nested choices.
 * Legal-action driver supplies earlier moves only. This is NOT selfplay/rating. */
'use strict';
const assert=require('assert/strict'),fs=require('fs'),path=require('path');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {chooseNativeChoice,fingerprint}=require('./native_choice_adapter092.cjs');
const draft=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js');
const {reports}=require('./native_bridge_paths092.cjs');
const rosters=JSON.parse(fs.readFileSync(path.join(draft,'original-rosters.json'),'utf8'));
function technicalAction(s){
  const r=s.requests[0],d=r.details;
  switch(r.kind){
    case 'RequestMulliganAction':return {kind:'mulligan-finish'};
    case 'RequestPlayCardAction':{
      const cards=new Map(s.cards.map(c=>[c.id,c]));
      const moves=d.moves.slice().sort((a,b)=>(cards.get(b.card)?.power||0)-(cards.get(a.card)?.power||0));
      if(!moves.length){assert(d.canPass);return {kind:'pass'};}return {kind:'play',...moves[0]};
    }
    case 'RequestCardTargetsAction':return {kind:'targets',cards:d.valid.slice(0,d.max)};
    case 'RequestCardChoicesAction':return {kind:'choices',cards:d.choices.slice(0,d.max).map(c=>c.id)};
    case 'RequestLocationTargetsAction':return {kind:'locations',locations:d.valid.slice(0,d.max)};
    default:throw Error('Unhandled driver request '+r.kind);
  }
}
async function check(template,deckName,first){
  const roster=rosters.decks.find(d=>d.asset===deckName);assert(roster);
  const config={mode:'external',deck:{faction:roster.faction,leader:roster.leader.templateId,cards:roster.cards}};
  const client=new OriginalBetaClient();let s;
  try{
    s=await client.request('init',{seed:923058101,first,players:[config,config]});
    for(let step=0;step<250&&s.winner===0;step++){
      const req=s.requests[0],source=s.cards.find(c=>c.id===req.details.requester);
      if(source?.template===template&&req.kind!=='RequestPlayCardAction'){
        const before=JSON.stringify(s),started=performance.now();
        const proposed=chooseNativeChoice(s,[config,config]);
        assert.equal(JSON.stringify(s),before,'Policy import changed native source snapshot');
        const second=chooseNativeChoice(s,[config,config]);
        assert.deepEqual(second.action,proposed.action,'Same frozen seed produced different action');
        let guards=0;
        for(const mutate of [
          x=>{x.requests[0].ability.currentNode=-1;},
          x=>{x.cards[0].persistent=[{name:'unmapped',storedValue:1}];},
          x=>{x.locations[0].tokens=64;},
          x=>{x.requests[0].ability.temporary.push({dynamicGetter:true,sourceVariable:null});},
          x=>{x.random.encoding='unmapped';}
        ]){
          const bad=JSON.parse(before);mutate(bad);assert.throws(()=>chooseNativeChoice(bad,[config,config]));guards++;
        }
        const after=await client.request('action',{sequence:s.sequence,request:req.id,...proposed.action});
        assert.equal(after.sequence,s.sequence+1);assert.equal(after.loggerErrors,0);
        assert.deepEqual(await client.request('snapshot'),after,'Post-choice snapshot has side effects');
        const projection=proposed.choiceProjection?.map(p=>{
          const actual=after.cards.find(c=>c.id===p.id);assert(actual);
          return {expected:p,after:{id:actual.id,template:actual.template,side:actual.position.side,
            zone:actual.position.zone,power:actual.power,armor:actual.armor}};
        });
        for(const p of projection)assert.deepEqual(p.after,p.expected,'Native resolved choice differs from frozen WS local projection');
        // Discard has no end-turn damage in these original fixtures. Require the
        // actual selected instance identities, not just matching templates.
        if(template===152103)for(const p of projection)assert.equal(p.after.zone,32,'Selected discard did not enter native graveyard');
        const result={source:template,graph:req.ability.graph,deck:deckName,first,actor:req.player,sequence:s.sequence,
          action:proposed.action,originalInstances:proposed.originalInstanceChoices,scoreConvention:proposed.scoreConvention,
          rejectedUnmappedStates:guards,cardsImported:proposed.cardsImported,randomCheckpoint:proposed.randomCheckpoint,projection,
          milliseconds:performance.now()-started,errors:after.loggerErrors};
        console.log(JSON.stringify(result));return result;
      }
      s=await client.request('action',{sequence:s.sequence,request:req.id,...technicalAction(s)});
    }
    throw Error('Requested original graph not encountered: '+template);
  }catch(e){fs.writeFileSync(path.join(reports,'native-choice-adapter-failure.json'),JSON.stringify({template,first,error:String(e),state:s},null,2)+'\n');throw e;}
  finally{await client.close();}
}
if(require.main===module)(async()=>{
  const results=[];
  for(const [template,deck]of [[152103,'d_Skellige_Practice_Easy'],[152315,'d_Skellige_Practice_Easy'],[112102,'d_Nilfgaard_Practice']])
    for(const first of [1,2])results.push(await check(template,deck,first));
  const report={schema:1,complete:true,fingerprint,
    scope:'Three explicitly mapped native deploy graphs, actual frozen WS nested handlers and native legal-action validation. Earlier moves are technical driver. NOT a full real-roster mixed game or strength result.',
    results};
  fs.writeFileSync(path.join(reports,'native-choice-adapter-smoke.json'),JSON.stringify(report,null,2)+'\n');
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
module.exports={technicalAction};

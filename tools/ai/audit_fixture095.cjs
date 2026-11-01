'use strict';
const assert=require('assert/strict');
module.exports=function(rt){
 function add(g,id,side,zone,index=0,power,armor=0,tokens=0){assert.equal(rt.definition(id).header.templateId,id,'fixture requires a supported template '+id);const ref={v:0};assert(g.registry.Allocate(ref));const c=rt.newCard();c.Setup(g,ref.v,id,side,zone,index);g.registry.Put(ref.v,c);g.live.push(c);if(power!==undefined)c.power.SetCurrentPair(power,armor);if(tokens)c.AddTokens(tokens);return c;}
 function fixture(side,seed=83291){const g=rt.newSession();assert(g.InitializeWithPresets(54,54));for(const c of g.live)c.Move(c.Snapshot().positionPlayerId,512,0);
  g.mulligan=false;g.waiting=false;g.pendingCard=g.pendingLeader=null;g.recordVisuals=false;g.weatherProfile=false;g.externalPolicyMask=3;g.match.currentPlayerId=side;g.match.roundActive=g.match.turnActive=true;g.match.roundNumber=1;g.match.playerOne.hasPassed=g.match.playerTwo.hasPassed=false;g.random.Initialize(seed);return g;}
 function fill(g,side,row,n){return Array.from({length:n},(_,i)=>add(g,132403,side,row,i));}
 return {add,fixture,fill};
};

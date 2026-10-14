'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const snapshot=path.resolve(process.argv[2]),context=vm.createContext({console});
const fixture=fs.readFileSync('tools/ai/check_consume_self.js','utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const board=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const at=board.indexOf('function '+name+'('),start=board.indexOf('{',at);let end=start+1,depth=1;
 assert(at>=0,name);for(;depth;end++){if(board[end]==='{')depth++;if(board[end]==='}')depth--;}
 return board.slice(at,end).replace(/:(String|Object|void|int|uint|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))');
}
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n')+'\nHost.strength=4;'+fixture+String.raw`
const g=fixture(1),source=add(g,132202,8,4,1);
const nekkers=[add(g,132305,1,0,1),add(g,132305,8,5,1),add(g,132305,16,0,1)];
globalThis.initialNekkers=nekkers.map(c=>c.Snapshot().power.currentPower);
for(let i=0;i<10;i++)add(g,[132201,132308,132304,200091,112207,162210,162211][i%7],32,i,1);
g.recordVisuals=true;g.visualFrames=[];
const before=g.VisualSnapshot();check(g.Play(1,source.cardState.instanceId,4),'real Mourntart plays');
function cardView(v){const s=v.card;return {id:s.instanceId,templateId:s.runtimeTemplate.templateId,power:s.power.currentPower,armor:s.power.armor,
 tokens:s.tokenMask,zone:s.locationMask,side:s.positionPlayerId};}
globalThis.cards=before.cards.map(cardView);
globalThis.frames=g.visualFrames.map((f,i)=>({revision:i,cards:f.cards.map(cardView),scores:[f.scoreOne,f.scoreTwo],cue:{kind:f.kind,source:f.sourceId,target:f.targetId,
 templateId:f.templateId,audioKind:f.audioKind,targetView:{zone:f.targetZone,side:f.targetSide,templateId:f.targetTemplateId,power:f.targetPower}}}));
globalThis.finalNekkers=nekkers.map(c=>c.Snapshot().power.currentPower);
globalThis.int=v=>v|0;
`+extract('collapseMourntart'),context,{timeout:120000});
const collapsed=context.collapseMourntart(context.frames),swallows=collapsed.filter(f=>f.cue.kind===11);
assert.equal(swallows.length,1,'one swallow across actual board, hand and deck Nekker reactions');
assert.equal(swallows[0].cue.massTargets.length,10,'all ten graveyard victims');
assert(context.finalNekkers.every((p,i)=>p===context.initialNekkers[i]+10),'each Nekker gains all ten triggers');
const boosts=collapsed.filter(f=>f.cue.massConsumeBoost);
assert.equal(boosts.length,1,'one final boost frame after swallowing');
assert(collapsed.indexOf(boosts[0])>collapsed.indexOf(swallows[0]),'boost follows swallow');
assert(boosts[0].cue.hitTargets.includes(context.frames[0].cue.source),'consumer receives its final boost');
assert(swallows[0].cards.find(c=>c.id===boosts[0].cue.source).power===4,'consumer power waits for swallowing');
assert(boosts[0].cards.find(c=>c.id===boosts[0].cue.source).power===14,'final consumer power appears once');
assert.equal(swallows[0].historyFrames.length,context.frames.length-1,'all original operations remain in history after deploy');
console.log('PASS actual WitcherScript to ActionScript: ten meals, board/hand/deck Nekkers, one swallow then one boost');

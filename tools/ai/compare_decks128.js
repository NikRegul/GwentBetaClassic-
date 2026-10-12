// Same AI, old versus revised roster, paired seeds and both seats. No mod build.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),output=path.resolve(process.argv[3]);
const ids=(process.argv[4]||'94,74,85,87,89,69,97,99,83').split(',').map(Number);
const games=Number(process.argv[5]||40);
const alternatives=process.argv[6]?JSON.parse(fs.readFileSync(process.argv[6],'utf8')):{};
if(games<2||games%2)throw Error('Use an even game count for balanced seats');
const patch=JSON.parse(fs.readFileSync('data/beta924/ai/deck_patch128.json','utf8'));
const metadata=JSON.parse(fs.readFileSync('data/beta924/duel/presets.json','utf8')).presets;
const manifest=JSON.parse(fs.readFileSync(path.join(snapshot,'manifest.json'),'utf8'));
const signature=JSON.stringify({fingerprint:manifest.fingerprint,patch,games,alternatives});
let report={schema:1,signature,gamesPerDeck:games,mode:'same AI, old roster vs new roster; equal seeds, mirrored seats',simulationDamp:40,strength:4,nativeGameTested:false,decks:{}};
if(fs.existsSync(output)){
 report=JSON.parse(fs.readFileSync(output,'utf8'));
 if(report.signature!==signature)throw Error('Inputs changed; choose a new output report');
}
for(const id of ids){
 const change=patch.decks.find(p=>p.presetId===id);if(!change)throw Error('No roster revision '+id);
 const meta=metadata.find(p=>p.id===id),ctx=vm.createContext({console});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n'),ctx);
 ctx.originalId=id;ctx.virtualId=1000+id;ctx.oldCards=change.expectedTemplateIds;
 const snapshotCards=JSON.parse(vm.runInContext('(()=>{const ids={v:[]};if(!BetaGwentDuelPresetDeck(originalId,ids))throw Error("Missing frozen deck");return JSON.stringify(ids.v);})()',ctx));
 ctx.newCards=alternatives[id]||snapshotCards;
 vm.runInContext(`
 const originalDeck=BetaGwentDuelPresetDeck,originalPreset=BetaGwentDuelPreset,originalProfile=BetaGwentAIPresetProfile,originalWeight=BetaGwentAITrainingWeight;
 BetaGwentDuelPresetDeck=function(id,ids){if(id===virtualId||id===originalId&&newCards){ids.v=Array.from(id===virtualId?oldCards:newCards);return true;}return originalDeck(id,ids);};
 BetaGwentDuelPreset=function(id){const p=originalPreset(id===virtualId?originalId:id);if(id===virtualId)p.id=virtualId;return p;};
 BetaGwentAIPresetProfile=function(id){return originalProfile(id===virtualId?originalId:id);};
 BetaGwentAITrainingWeight=function(id,index){return originalWeight(id===virtualId?originalId:id,index);};
 Host.simDamp=40;
 `,ctx);
 const entry=report.decks[id]||(report.decks[id]={title:meta.title,oldCards:change.expectedTemplateIds,newCards:ctx.newCards,games:[]});
 for(let n=entry.games.length;n<games;n++){
  const seed=128000+Math.floor(n/2),newOnLeft=n%2===0;
  ctx.gameArgs=[newOnLeft?id:1000+id,newOnLeft?1000+id:id,seed,4,4,120];
  const start=Date.now();let result;
  try{result=vm.runInContext('__harness.play(...gameArgs)',ctx,{timeout:120000});}
  catch(e){throw Error('Game '+id+'/'+n+' failed: '+e);}
  entry.games.push({...result,newOnLeft,elapsedMs:Date.now()-start});
  entry.newWins=entry.games.filter(g=>g.winner===(g.newOnLeft?1:2)).length;
  entry.oldWins=entry.games.filter(g=>g.winner===(g.newOnLeft?2:1)).length;
  entry.draws=entry.games.filter(g=>g.winner===3).length;
  entry.errors=entry.games.filter(g=>g.winner===0).length;
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  if(result.error)throw Error('Engine failure retained in report: '+result.error);
  console.log(id,entry.games.length+'/'+games,'new/old/tie',entry.newWins,entry.oldWins,entry.draws,'ms',Date.now()-start);
 }
}

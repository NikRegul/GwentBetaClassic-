// End-to-end smoke games for the four new leader decks; not a strength estimate.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const snapshot=path.resolve(process.argv[2]),ctx=vm.createContext({console});
vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(snapshot,f),'utf8')).join('\n'),ctx);
vm.runInContext('Host.simDamp=40;',ctx);
const results=[],output=process.argv[3]||'docs/evidence/variety128.json';
for(const id of [60,76,77,95])for(const mirror of [false,true]){
 const args=mirror?[54,id,128046,4,4,120]:[id,54,128046,4,4,120];
 ctx.args=args;
 const game=vm.runInContext('__harness.play(...args)',ctx,{timeout:120000});
 results.push(game);fs.writeFileSync(output,JSON.stringify({smokeOnly:true,nativeGameTested:false,results},null,2)+'\n');
 if(game.error)throw Error(game.error);
 console.log('PASS new leader full game',id,mirror,game.steps);
}

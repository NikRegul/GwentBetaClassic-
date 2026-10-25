'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),copies=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'];
const files=copies.map(c=>fs.readFileSync(path.join(root,'BetaGwent/ui',c,'BetaGwentBoard.as'))),raw=files[0],source=raw.toString('utf8');let checks=0;
const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
for(const file of files){eq(file.equals(raw),true,'Five identical copies');eq(file.subarray(0,3).toString('hex'),'efbbbf','UTF8 BOM');eq(file.toString('utf8').replace(/\r\n/g,'').includes('\n'),false,'CRLF');}
function extract(name){const at=source.indexOf('function '+name+'(');assert(at>=0);const open=source.indexOf('{',at);let depth=1,end=open+1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:\s*(Boolean|String|void|int|Array|Number|Object)\b/g,'');}
const calls=[],ctx=vm.createContext({round:0,flags:0,selectingDecks:true,editingDeck:false,browsingCatalog:false,kegOpen:false,effectGallery:false,
 difficultyIndex:3,controllerMenuOpen:false,soundEnabled:true,voiceEnabled:true,animationTempo:1,reducedMotion:false,aiPauseIndex:1,
 BetaGwentTextLanguage:{language:1,protect(){}},send:(name,args)=>calls.push({name,args}),render(){},closeControllerMenu(){},openControllerMenu(){},int:Math.trunc});
for(const f of ['originalDifficultyInMatch','unfairDifficultyText','difficultyName','cycleDifficulty','setAudioStatus'])vm.runInContext(extract(f),ctx);
const chosen=[];for(let i=0;i<4;i++){ctx.cycleDifficulty();chosen.push(ctx.difficultyIndex);}eq(chosen,[4,1,2,3],'Fourth option before match');
ctx.setAudioStatus(true,true,10,false,1,4);eq(ctx.difficultyName(),'Классическая','Saved fourth difficulty reflected');
eq(ctx.unfairDifficultyText(true).includes('руку и колоду'),true,'Information advantage explained');
for(let language=1;language<=13;language++){ctx.BetaGwentTextLanguage.language=language;assert(ctx.unfairDifficultyText(false).length>0&&ctx.unfairDifficultyText(true).length>0);checks++;}
ctx.BetaGwentTextLanguage.language=1;ctx.selectingDecks=false;ctx.round=1;ctx.flags=0;
const count=calls.length;ctx.cycleDifficulty();eq(ctx.difficultyIndex,4,'Unfair fixed during match');eq(calls.length,count,'No mid-search policy event');
ctx.difficultyIndex=3;const existing=[];for(let i=0;i<3;i++){ctx.cycleDifficulty();existing.push(ctx.difficultyIndex);}eq(existing,[1,2,3],'Existing live difficulty cycle preserved');
ctx.flags=16;ctx.difficultyIndex=3;ctx.cycleDifficulty();eq(ctx.difficultyIndex,4,'Fourth option after match');
eq(calls.at(-1).args[5],4,'Correct native difficulty argument');
const report={checks,fiveIdenticalBomCrlfCopies:true,languages:13,scope:'Actual AS settings methods, saved fourth option, unchanged existing cycle, safe match boundary and information tooltip; native menu packaging still required'};
fs.writeFileSync(path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-ws-port/ui-contract.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

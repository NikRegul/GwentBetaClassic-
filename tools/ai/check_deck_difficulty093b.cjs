// Actual header/render prefixes: detect the panel occlusion missed by the old
// button-existence test. Native AS compilation and menu verification follow.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
const root=path.resolve(__dirname,'../..'),observe=process.argv.includes('--observe');
const outputs=process.argv.slice(2).filter(a=>a!=='--observe'),out=outputs[0]?path.resolve(outputs[0]):null;
let checks=0;const failures=[],cases=[];
function check(v,label){checks++;if(!v){failures.push(label);if(!observe)throw Error(label);}}
function extract(source,name){const at=source.indexOf('function '+name+'(');if(at<0)throw Error('Missing '+name);
 const open=source.indexOf('{',at);let end=open+1,depth=1;for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:\s*(?:Boolean|String|void|int|Array|Number|Object|Function|Sprite)\b/g,'');}
const copies=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'];
const canonical=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentBoard.as'));
for(const folder of copies){const raw=fs.readFileSync(path.join(root,'BetaGwent/ui',folder,'BetaGwentBoard.as'));
 check(raw.equals(canonical),'identical board copy '+folder);check(raw.subarray(0,3).toString('hex')==='efbbbf','BOM '+folder);
 check(!raw.toString('utf8').replace(/\r\n/g,'').includes('\n'),'CRLF '+folder);}
for(const [platform,file] of [['nextgen','BetaGwent/ui/src/BetaGwentBoard.as'],['classic','tools/features091/BetaGwentBoard_classic093.as']]){
 const source=fs.readFileSync(path.join(root,file),'utf8'),buttons=[],panels=[];
 let changes=0;
 const ctx=vm.createContext({selectingDecks:true,editingDeck:false,ready:true,pickerSide:0,entryMode:0,npcDisplayName:'NPC',ownPreset:54,
  BetaGwentTextLanguage:{language:1},BetaGwentReleaseText093:{opponent:name=>name},
  content:{},editorState:{faction:2},viewed:{leaderId:200168},
  textChoiceLabel:()=> 'Текст: Авто · Русский',voiceChoiceLabel:()=> 'Озвучка: Авто · Русский',difficultyName:()=> 'Классическая',
  cycleTextLanguage(){},cycleVoiceLanguage(){},cycleDifficulty:()=>changes++,
  editorSmallButton:(parent,title,x,y,w,h,enabled,callback)=>buttons.push({title,x,y,w,h,enabled,callback}),
  languageButton:(title,x,y,w,callback)=>buttons.push({title,x,y,w,h:30,enabled:true,callback}),
  paintArt:(parent,id,w,h,x=0,y=0)=>{if(id==='panel')panels.push({x,y,w,h});},wideArt(){},betaNine(){},betaLabel:()=>({}),
  deckOption:()=>({leaderId:200168}),cardFaction:()=>2,editorFactionIndex:()=>0,
  BetaGwentHud104:{CHAIN:1,WOOD_PANEL:'panel'},BetaGwentDeckArt104:{BG_SETUP:1,BG_BUILDER:2,stats:()=>3},BetaGwentFonts:{TITLE:1}});
 vm.runInContext(extract(source,'betaPlaque'),ctx);
 vm.runInContext(extract(source,'opponentName'),ctx);
 for(const [name,marker] of [['drawBetaDeckList','var golds'],['drawBetaDeckPicker','var savedCount'],['drawBetaMatchSetup','// centre:'],['drawBetaDeckEditor','var bronzes']]){
  const fn=extract(source,name),cut=fn.indexOf(marker);if(cut<0)throw Error('Missing render boundary '+name);
  vm.runInContext(fn.slice(0,cut)+'}',ctx);
 }
 for(const mode of ['practice','decks','npc','picker','editor']){
  buttons.length=panels.length=0;ctx.selectingDecks=mode!=='editor';ctx.editingDeck=mode==='editor';ctx.pickerSide=mode==='picker'?1:0;
  ctx.entryMode=mode==='decks'?1:mode==='npc'?2:0;
  if(mode==='editor')ctx.drawBetaDeckEditor();else ctx.drawBetaMatchSetup();
  const difficulty=buttons.find(b=>b.callback===ctx.cycleDifficulty);
  check(Boolean(difficulty),platform+'/'+mode+': difficulty exists in deck header');
  if(difficulty){
   check(difficulty.enabled,platform+'/'+mode+': ready button enabled');
   const overlaps=panels.some(p=>difficulty.x<p.x+p.w&&difficulty.x+difficulty.w>p.x&&difficulty.y<p.y+p.h&&difficulty.y+difficulty.h>p.y);
   check(!overlaps,platform+'/'+mode+': later deck panel cannot cover difficulty');
   check(difficulty.y+difficulty.h<=129,platform+'/'+mode+': all button pixels stay in header');
   difficulty.callback();
  }
  for(let i=0;i<buttons.length;i++)for(let j=i+1;j<buttons.length;j++){
   const a=buttons[i],b=buttons[j];check(!(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+b.h&&a.y+a.h>b.y),platform+'/'+mode+': header controls do not overlap');}
  cases.push({platform,mode,buttons:buttons.map(({callback,...b})=>b),panels:panels.slice()});
 }
 check(changes===5,platform+': every deck-context button invokes the saved difficulty action');
 ctx.selectingDecks=ctx.editingDeck=false;buttons.length=0;ctx.betaPlaque('Коллекция');
 check(buttons.length===2,platform+': unrelated collection header preserved');
}
const report={checks,failures,cases,nativeMenuTested:false,actualAsRenderPrefixes:true};
if(out)fs.writeFileSync(out,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures,cases:cases.length}));if(failures.length)process.exitCode=1;

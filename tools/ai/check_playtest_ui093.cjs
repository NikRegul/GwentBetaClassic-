'use strict';
// Execute actual AS methods across card selection, row focus and native submit.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const source=fs.readFileSync(path.resolve(__dirname,'../../BetaGwent/ui/src/BetaGwentBoard.as'),'utf8');
let checks=0;const eq=(a,b,n)=>{assert.deepEqual(a,b,n);checks++;};
function extract(name){const at=source.indexOf('function '+name+'(');assert(at>=0,name);const open=source.indexOf('{',at);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:\s*(?:Boolean|String|void|int|Array|Number|Object|Function|Sprite)\b/g,'')
 .replace(/for each\(var (\w+) in (\w+)\)/g,'for(const $1 of $2)');}
const focus=[],submitted=[],buttons=[];
const c=vm.createContext({selected:0,revision:17,keyboardFocusId:0,focusedRow:0,controllerInspectBoard:false,
 ready:true,playing:false,detailOpen:false,pileOpen:false,effectGallery:false,editingDeck:false,selectingDecks:false,
 current:1,flags:0,requestId:0,requestKind:0,rowRequest:false,requestPlayer:1,rowMode:0,
 cards:[{id:71,side:1,zone:8,canPlay:true}],playRules:{71:{kind:2,side:2,rowMask:3}},cardDetails:{71:{typeMask:2}},
 controller:{focusTag:tag=>focus.push(tag),focusKey:key=>focus.push(key)},int:Math.trunc,
 render(){},canPlaceSelected:()=>false,canPlacePending:()=>false,canPlaceBefore:()=>false,canDirectTarget:()=>false,
 openCardDetail(){throw Error('Unexpected inspection');},submitBoard:(name,args)=>submitted.push({name,args}),
 placementSide:()=>1,isCaranthirChoice:()=>false,content:{},voiceChoiceLabel:()=> 'Озвучка: RU',textChoiceLabel:()=> 'Текст: RU',
 difficultyName:()=> 'Классическая',cycleTextLanguage(){},cycleVoiceLanguage(){},cycleDifficulty(){},
 editorSmallButton:(parent,title,x,y,w,h,enabled,callback)=>buttons.push({title,x,y,w,h,enabled,callback}),
 paintArt(){},betaNine(){},betaLabel:()=>({}),BetaGwentHud104:{CHAIN:1},BetaGwentFonts:{TITLE:1}});
for(const name of ['canAct','controllerRowSelection','controllerQuickSpecial','controllerCardAction','canPlayRow','canSelectRow','rowEnabled','halfCastSide','chooseRow','controllerRowAction','betaPlaque'])vm.runInContext(extract(name),c);
c.controllerCardAction(71);eq(c.selected,71,'White Frost selected from hand');eq(focus.at(-1),'row','Controller moves directly to rows');
eq(c.controllerRowSelection(),true,'Direct row spell has row context');
for(const [side,row,valid] of [[2,1,true],[2,2,true],[2,4,false],[1,1,false]]){
 eq(c.rowEnabled(side,row),valid,'Only legal adjacent-pair anchors '+side+'/'+row);
 const count=submitted.length;c.controllerRowAction(side,row)();eq(submitted.length,count+(valid?1:0),'Confirm only legal row');
 if(valid){eq(submitted.at(-1).name,'OnBetaGwentBoardPlayRowTarget','Direct row bridge');eq(Array.from(submitted.at(-1).args),[17,71,2,row],'Selected legal row submitted');}
}
c.rowRequest=true;c.requestId=12;c.requestKind=2;c.rowMode=10;c.controllerRowAction(2,2)();
eq(submitted.at(-1).name,'OnBetaGwentDuelRowTarget','Nested row request retains original bridge');
c.rowRequest=false;c.requestId=0;c.selected=0;eq(Boolean(c.controllerRowSelection()),false,'Normal turn remains hand context');
c.playRules[71]={kind:1,side:2};c.selected=71;eq(Boolean(c.controllerRowSelection()),false,'Unit target remains card context');
c.selectingDecks=true;c.betaPlaque('Бой');eq(buttons.length,3,'Language, voice and difficulty before battle');
eq(buttons[2].title,'Сложность ИИ: Классическая','Chosen difficulty visible');eq(buttons[2].callback,c.cycleDifficulty,'Same saved setting callback');
eq(buttons[2].x,buttons[1].x,'Difficulty next to language controls');assert(buttons[2].y>=buttons[1].y+buttons[1].h&&buttons[2].y+buttons[2].h<=129);checks++;
c.selectingDecks=false;c.editingDeck=true;buttons.length=0;c.betaPlaque('Редактор');eq(buttons.length,3,'Difficulty is also available in the deck editor');
eq(buttons[2].callback,c.cycleDifficulty,'Editor uses the same saved difficulty');
c.editingDeck=false;buttons.length=0;c.betaPlaque('Коллекция');eq(buttons.length,2,'Unrelated collection header preserved');
assert(source.includes('controllerRowSelection()?"rows":'));assert(source.includes('!playing&&controllerRowSelection()&&!detailOpen&&!pileOpen?"row":""'));checks+=2;
console.log(JSON.stringify({checks,whiteFrostDirectFocus:true,prebattleDifficulty:true,nativeMenuTested:false}));

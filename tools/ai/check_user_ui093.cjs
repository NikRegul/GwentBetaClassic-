// Execute the shipped AS offer/name methods on both platform sources.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');let checks=0;const records=[];
const check=(v,n)=>{checks++;assert(v,n);};
function extract(source,name){const at=source.indexOf('function '+name+'(');assert(at>=0,name);const open=source.indexOf('{',at);let depth=1,end=open+1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end).replace(/:\s*(?:Boolean|String|void|int|Array|Number|Object|Function|Sprite)\b/g,'')
 .replace(/for each\(var (\w+) in ([\w.]+)\)/g,'for(const $1 of $2)');}
const labels=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentReleaseText093.as'),'utf8');
const model=JSON.parse(fs.readFileSync(path.join(root,'data/beta924/design/release093_ui.json'),'utf8'));
const actual={};for(const key of ['TEXT','NAMES','ALIASES'])actual[key]=JSON.parse(labels.match(new RegExp('private static const '+key+':Object=(.+);'))[1]);
check(JSON.stringify(actual.TEXT)===JSON.stringify(model.text)&&JSON.stringify(actual.NAMES)===JSON.stringify(model.opponents)&&JSON.stringify(actual.ALIASES)===JSON.stringify(model.aliases),'compiled source tables equal reviewed language data');
const lctx=vm.createContext({...actual,BetaGwentTextLanguage:{translate:v=>v}});
for(const name of ['label','opponent'])vm.runInContext(extract(labels,name),lctx);
for(const lang of Array.from({length:13},(_,i)=>i+1)){
 for(const key of Object.keys(model.text))check(lctx.label(key,lang)===model.text[key][lang-1],'explicit choice text '+lang+'/'+key);
 for(const [name,values] of Object.entries(model.opponents))for(const value of values)
  check(lctx.opponent(value,lang)===values[lang-1],'NPC localized from any source language: '+name+'/'+lang);
 check(lctx.opponent('ch_fac_northern_4',lang)===model.opponents['Соперник'][lang-1],'internal profile hidden');
 check(lctx.opponent('p_Nilfgaard_Practice',lang)===model.opponents['Соперник'][lang-1],'internal Practice hidden');
 check(lctx.opponent('A custom NPC',lang)==='A custom NPC','unknown NPC identity preserved');
}
for(const file of ['BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as']){
 const source=fs.readFileSync(path.join(root,file),'utf8'),buttons=[],headings=[],tiles=[],sent=[];
 function Sprite(){this.graphics={clear(){},beginFill(){},drawRect(){},endFill(){}};this.addChild=()=>{};}
 const ctx=vm.createContext({requestId:101,requestKind:2,requestPlayer:1,rowRequest:false,requestSourceTemplate:162210,
 requestCards:[{id:21,revealed:true,templateId:112405,title:'First'},{id:22,revealed:true,templateId:113310,title:'Second'}],
 cards:[{id:21,zone:8,side:1,power:8},{id:22,zone:8,side:1,power:0},{id:23,zone:8,side:1,power:10}],
 pileChoice:false,rowMode:0,templateChoice:false,handPowerChoice:false,graveyardChoice:false,requestMessage:'',requestMax:1,requestCount:0,requestFinish:false,
 mulliganConfirm:false,detailOpen:false,playing:false,mulliganHidden:false,abilityHidden:false,ready:true,skin:3,mulliganPickedId:0,keyboardFocusId:0,
 BetaGwentReleaseText093:lctx,BetaGwentTextLanguage:{language:2},Sprite,WIDE_PAD:100,content:new Sprite(),choiceLayer:new Sprite(),
 BetaGwentCardText:{find:()=>({power:8})},cardDetails:{},BetaGwentFonts:{BODY:1},
 canPlacePending:()=>false,render(){},readableText:v=>v,abilityOverviewLayout:n=>({cols:n,w:200,h:300,captionH:20,stepY:320}),
 stripHeading:(parent,heading,hint)=>headings.push({heading,hint}),compactOverviewCard:(parent,c)=>{tiles.push(c);return new Sprite();},
 attachMulliganReading(){},attachRequestCard:(tile,id)=>sent.push(id),showMulliganCard(){},enemyAmbush:()=>false,
 editorBetaButton:(parent,title,x,y,w,h,enabled,callback)=>buttons.push({title,callback}),betaLabel:()=>({}),
 isOptionalMultiChoice:()=>false,Math,int:Math.trunc});
 for(const name of ['isCardOffer','isChoiceTable','isMulliganHand','choiceTableHidden','toggleChoiceTable','cardOfferLabel','choiceCaptionKey','sourceAbilityText','choiceHeading','choiceHint','drawBetaAbilityChoices'])vm.runInContext(extract(source,name),ctx);
 check(ctx.isCardOffer()&&!ctx.isMulliganHand(),'Cantarella offer is not mulligan');
 ctx.drawBetaAbilityChoices();check(headings[0].heading==='Keep one card','specific keep choice heading');
 check(headings[0].hint.includes('bottom of your deck'),'return destination explained');
 check(sent.join(',')==='21,22','only two offered instance IDs rendered, no arbitrary hand card');
 ctx.toggleChoiceTable();check(ctx.abilityHidden&&ctx.choiceTableHidden(),'table inspection hides offer');
 ctx.toggleChoiceTable();check(!ctx.abilityHidden,'offer can be reopened');
 ctx.cards[1].zone=1;check(!ctx.isCardOffer(),'mixed hand/board targets stay on board');ctx.cards[1].zone=8;
 ctx.requestSourceTemplate=162316;ctx.requestCards=[{id:90,revealed:false,templateId:0,title:'Back'}];
 tiles.length=sent.length=0;ctx.drawBetaAbilityChoices();check(ctx.isCardOffer(),'hidden enemy reveal candidates need no live secret card');
 check(tiles[0].hidden&&tiles[0].templateId===0&&tiles[0].power===0,'enemy hand remains hidden in modal');
 check(sent[0]===90,'hidden legal instance ID still selectable');
 ctx.requestKind=1;ctx.requestCards=[];check(ctx.isMulliganHand()&&ctx.isChoiceTable(),'ordinary mulligan retained');
 check(!source.includes('npcDeckLabel'),'all opponent labels use identity');
 check(source.includes('side==2?opponentName()')&&source.includes('side==1?"Ведьмак":opponentName()'),'battle HUD and intro use same NPC name');
 check(!source.includes('pickerSide==1?"ВАША КОЛОДА"'),'misplaced picker title removed');
 check(source.includes('deckListTop178=picked&&factionLeaders.length>1?428:378'),'unused leader controls gap collapses');
 check(source.includes('908-deckListTop178')&&source.includes('y:deckListTop178+y'),'scroll height and controller coordinates follow collapsed list');
 check(source.includes('if(!playing&&isChoiceTable()) drawChoices();')&&source.includes('isChoiceTable()?"choice"'),'render and controller both enter offer mode');
 records.push({file,offeredIds:sent.slice(),hiddenCardsProtected:true});
}
const report={checks,records,languages:13,nativeGameplayVerified:false,scope:'Actual AS methods; native compilation/menu packaging and retail input acceptance remain separate'};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

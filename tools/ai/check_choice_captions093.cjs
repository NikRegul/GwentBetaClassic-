// Execute the shipped AS choice-caption methods on both platform boards in all 13 languages.
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
const TEXT=JSON.parse(labels.match(/private static const TEXT:Object=(.+);/)[1]);
check(JSON.stringify(TEXT)===JSON.stringify(model.text),'compiled caption table equals reviewed language data');
const lctx=vm.createContext({TEXT});vm.runInContext(extract(labels,'label'),lctx);
// [template, mode, heading key, hint key]
const CASES=[[152214,'pile','drawOne','drawDiscardHint'],[122203,'pile','drawOne','drawReturnHint'],[142203,'pile','drawOne','drawReturnHint'],
 [131102,'play','playOne','playTopHint'],[200071,'hand','keep','keepGiveHint'],[162210,'hand','keep','keepHint'],
 ...[112211,152103,152213].map(t=>[t,'hand','discardHand','discardHandHint']),
 ...[112212,122204,142303,201638,200209,200165,200048].map(t=>[t,'hand','swapHand','swapHandHint']),
 [132216,'hand','consumeHand','consumeHandHint'],...[152106,200036,200159].map(t=>[t,'pile','discardDeck','discardDeckHint']),
 [112208,'hand','offer','copyBothHint']];
for(const [,,h,n] of CASES){check(TEXT[h]&&TEXT[n],'caption keys exist '+h+'/'+n);
 for(let l=0;l<13;l++)check(TEXT[h][l].length>0&&TEXT[n][l].length>0&&TEXT[h][l]!==TEXT[n][l],'non-empty distinct caption '+h+'/'+n+'/'+l);}
check(TEXT.drawDiscardHint[0].includes('сброс')&&TEXT.drawDiscardHint[1].includes('graveyard'),'Udalryk caption names the graveyard');
const ABILITY={122201:'Усильте 3 отряда в вашей колоде на 2 ед.',142312:'Усильте отряд в вашей руке на 3 ед.'};
for(const file of ['BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as']){
 const source=fs.readFileSync(path.join(root,file),'utf8');const headings=[];
 function Sprite(){this.graphics={clear(){},beginFill(){},drawRect(){},endFill(){}};this.addChild=()=>{};}
 const ctx=vm.createContext({requestId:101,requestKind:2,requestPlayer:1,rowRequest:false,requestSourceTemplate:0,requestCards:[],cards:[],
  pileChoice:false,rowMode:0,templateChoice:false,handPowerChoice:false,graveyardChoice:false,requestMessage:'Выберите карту',requestMax:1,requestCount:0,requestFinish:false,
  mulliganConfirm:false,detailOpen:false,playing:false,mulliganHidden:false,abilityHidden:false,ready:true,skin:3,mulliganPickedId:0,keyboardFocusId:0,
  BetaGwentReleaseText093:lctx,BetaGwentTextLanguage:{language:1},Sprite,WIDE_PAD:100,content:new Sprite(),choiceLayer:new Sprite(),
  BetaGwentCardText:{find:id=>({power:8,description:ABILITY[id]||''})},cardDetails:{},BetaGwentFonts:{BODY:1},
  canPlacePending:()=>false,render(){},readableText:v=>v==null?'':String(v),abilityOverviewLayout:n=>({cols:n,w:200,h:300,captionH:20,stepY:320}),
  stripHeading:(parent,heading,hint)=>headings.push({heading,hint}),compactOverviewCard:()=>new Sprite(),
  attachMulliganReading(){},attachRequestCard(){},showMulliganCard(){},enemyAmbush:()=>false,editorBetaButton(){},betaLabel:()=>({}),
  isOptionalMultiChoice:()=>false,Math,int:Math.trunc});
 for(const name of ['isCardOffer','isChoiceTable','isMulliganHand','choiceTableHidden','toggleChoiceTable','cardOfferLabel','choiceCaptionKey','sourceAbilityText','choiceHeading','choiceHint','drawBetaAbilityChoices'])vm.runInContext(extract(source,name),ctx);
 function setMode(template,mode){ctx.requestSourceTemplate=template;
  ctx.requestCards=[{id:21,revealed:true,templateId:112405,title:'A'},{id:22,revealed:true,templateId:113310,title:'B'}];
  if(mode==='hand'){ctx.requestKind=2;ctx.pileChoice=false;ctx.rowMode=0;ctx.cards=[{id:21,zone:8,side:1},{id:22,zone:8,side:1}];}
  else{ctx.requestKind=1;ctx.pileChoice=true;ctx.rowMode=mode==='play'?12:14;ctx.cards=[];}}
 const draw=()=>{headings.length=0;ctx.drawBetaAbilityChoices();return headings[0];};
 for(let lang=1;lang<=13;lang++){ctx.BetaGwentTextLanguage.language=lang;
  for(const [t,mode,h,n] of CASES){setMode(t,mode);const shown=draw();
   check(shown&&shown.heading===TEXT[h][lang-1],'Beta modal heading '+t+'/'+lang);
   check(shown.hint.startsWith(TEXT[n][lang-1]),'Beta modal outcome hint '+t+'/'+lang);
   check(ctx.choiceHeading('x')===(mode==='hand'?'x':TEXT[h][lang-1])||mode==='hand','classic modal heading '+t+'/'+lang);
   if(mode!=='hand')check(ctx.choiceHint('x')===TEXT[n][lang-1],'classic modal hint '+t+'/'+lang);
   else check(ctx.cardOfferLabel(false)===TEXT[h][lang-1]&&ctx.cardOfferLabel(true)===TEXT[n][lang-1],'offer browser caption '+t+'/'+lang);}
 }
 ctx.BetaGwentTextLanguage.language=1;
 setMode(152214,'hand');check(ctx.choiceCaptionKey(true)==='','Udalryk caption is never shown for a different request shape');
 setMode(200071,'pile');check(ctx.choiceCaptionKey(true)==='','Shilard caption only for its hand offer');
 setMode(122201,'pile');check(draw().hint.startsWith(ABILITY[122201]),'uncaptioned deck choice shows the card ability');
 setMode(142312,'hand');check(draw().hint.startsWith(ABILITY[142312]),'uncaptioned hand offer shows the card ability');
 setMode(201776,'play');check(ctx.choiceHint('fallback')==='fallback','play choice without caption keeps its play explanation');
 setMode(162316,'hand');check(ctx.cardOfferLabel(false)===TEXT.reveal[0],'reveal heading kept');
 ctx.requestPlayer=2;setMode(152214,'pile');check(ctx.choiceCaptionKey(false)==='','opponent decisions get no player caption');ctx.requestPlayer=1;
 check(source.includes('if(pileChoice&&!isCardOffer()){heading=choiceHeading(heading);hint=choiceHint(hint);}'),'Beta skin uses captions');
 check(source.includes('text(modal,isCardOffer()?cardOfferLabel():pileChoice?choiceHeading(')&&source.includes('text(modal,isCardOffer()?cardOfferLabel(true):pileChoice?choiceHint('),'classic skin uses captions');
 records.push({file,cases:CASES.length,languages:13});
}
const report={checks,records,captioned:CASES.map(c=>c[0]),nativeGameplayVerified:false,scope:'Actual AS methods of both boards; native menu packaging separate'};
if(process.argv[2])fs.writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report).slice(0,300));

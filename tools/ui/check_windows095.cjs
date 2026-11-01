'use strict';
// Execute production AS bodies against protocol, navigation and layout scenarios.
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const file=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
let checks=0;const failures=[];function check(v,n){checks++;if(!v)failures.push(n);}
const controls=[],sent=[],sounds=[];
c.controller.registerControl=(sprite,title,action,card,detail,tag)=>controls.push({sprite,title,action,card,tag});
c.controller.getFocus=()=>null;c.controller.focusTag=()=>{};
Object.assign(c,{ready:true,playing:false,skin:3,pileOpen:false,detailOpen:false,selectingDecks:false,editingDeck:false,browsingCatalog:false,kegOpen:false,
 requestId:7,requestKind:1,requestPlayer:1,requestFinish:true,requestCount:0,requestMax:3,revision:9,serverRevision:9,
 requestCards:[],cards:[],cardDetails:{},mulliganSlots:[],mulliganHidden:false,abilityHidden:false,mulliganPickedId:0,keyboardFocusId:0,
 mulliganPreview:null,mulliganPreviewKey:'',mulliganConfirm:false,choicePage:0,choiceSoundKey095:'',
 isMulliganHand:()=>c.mulligan,isChoiceTable:()=>true,isCardOffer:()=>false,templateChoice:false,pileChoice:true,handPowerChoice:false,rowMode:14,
 requestMessage:'',choiceHeading:s=>s,choiceHint:s=>s,isOptionalMultiChoice:()=>false,
 animations:[],reducedMotion:true,leaderIds:[131101,200055],leaderNames:['Игрок','Соперник'],flags:16,crowns:[2,0],
 outcomeRounds095:[],outcomePage095:0,outcomeSeen095:'',outcomeRewardSeen095:'',rewardCard096:null,
 clearPlacementGhost(){},clearDrag(){},findRequestCard:id=>c.requestCards.find(x=>x.id===id),
 send:(name,args)=>sent.push({name,args}),uiSound:k=>sounds.push(k),
 drawBetaSidePreview(card,detail,parent){parent.addChild(new c.Sprite());c.mulliganReading=new c.TextField();},
 render(){},closeNameInput(){},closePileView(){},closeCardDetail(){},cardOfferLabel:()=>'',enemyAmbush:()=>false,
 betaVisual:()=>new c.Sprite(),paintCardBack(){},paintChoiceArt(){},toggleChoiceTable(){},requestMulliganFinish(){},finishMulligan(){},
 betaRoundCrownId:()=>-1523,drawRewardPanel096:()=>{},historyEventPage:0,
 // 0.9.7 Beta chrome helpers and controller glyphs on buttons.
 padSwaps096:[],padIcon096:()=>36,padGlyph096:n=>n,pileScroll097:0,outcomeProgress097:null,outcomeSlide097:0,
});
// The beta grid geometry is read from the checked source itself, so the scenario
// cannot drift away from the production constants.
const asGeometry=prefix=>{const out={};for(const m of source.matchAll(new RegExp('\\b'+prefix+'\\w*:(?:Number|int)=(-?[\\d.]+)','g')))out[m[0].split(':')[0]]=+m[1];return out;};
const geometry097=asGeometry('CHOICE_');
Object.assign(c,geometry097,{choiceScroll097:0,choiceScrollRequest:0,choiceGrid097:null,choiceFocused097:-1});
check(Object.keys(geometry097).length>=13,'beta choice geometry is readable from the source');
const names=['pickerArt098','pickerSurface098','pickerShades098','cancelPickerDrag098','betaPickerScroll098','scrollPile098','selectPicker098','movePicker098','betaPlankChrome097','betaWideButtonIn097','emptyChoiceSlot097','outcomeSections097','outcomeTab097','drawOutcomeProgress097','outcomeBar097','betaFrame','betaWindow','pileCardInspect','battleChoiceChrome095','popupWindow095','choiceWheel095','choiceVisibility095','choiceTableHidden','overviewLayout','abilityOverviewLayout','compactOverviewCard',
 'mulliganCardsInPlace','showMulliganCard','drawBetaMulligan','drawBetaAbilityChoices','attachMulliganReading','attachRequestCard','requestAction','sendRequest',
 'betaChoiceGrid097','keepChoiceRow097','scrollChoice097','mulliganWheel097','betaChoiceScroll097','betaChoiceRod097',
 'noteOutcomeRound095','selectOutcomePage095','drawBetaOutcome095','closeOutcome095','drawBetaConfirm','drawBetaPile095','showPileCard','stepPileCard',
 'submitDeckExchange','exchangeCraft','setDeckExchange','confirmBoardClose095'];
vm.runInContext(names.map(n=>H.extract(n,source)).join('\n'),c);
const reset=()=>{controls.length=0;c.content=new c.Sprite();c.choiceLayer=new c.Sprite();};
const fixture=(id,revealed=true)=>({id,templateId:revealed?132402:0,title:revealed?'Карта '+id:'Рубашка',revealed,power:5,side:1,zone:8,typeMask:4});
c.mulligan=true;c.requestCards=Array.from({length:10},(_,i)=>fixture(i+1));c.cards=c.requestCards;
reset();c.drawBetaMulligan();
check(controls.filter(x=>x.tag==='target').length===10,'all ten initial hand choices remain actionable');
const before=Array.from(c.mulliganSlots);c.requestCards.splice(3,1,fixture(77));
const after=Array.from(c.mulliganCardsInPlace()).map(x=>x.id);
check(after[3]===77&&after.every((id,i)=>i===3||id===before[i]),'replacement retains all neighbouring slots');
let selected=c.requestAction('OnBetaGwentRequestSelect',77);sent.length=0;c.ready=true;selected();selected();
check(sent.length===1&&sent[0].args.join()==='9,7,1,1,77','one authoritative request with complete captured context');
check(!sounds.includes(23),'mulligan waits for its existing authoritative replacement sound instead of doubling it');
for(const field of ['revision','requestId','requestPlayer','requestKind']){c.ready=true;selected=c.requestAction('OnBetaGwentRequestSelect',77);const old=c[field];c[field]++;selected();check(sent.length===1,'stale '+field+' cannot submit');c[field]=old;}
// Beta keeps one cell size and five columns: a third row scrolls under the parchment and
// shows the metal rod, instead of widening the cards to squeeze every row inside the frame.
const freshMulligan=count=>{const offer=Array.from({length:count},(_,i)=>fixture(i+1));
 c.mulligan=true;c.requestKind=1;c.requestMax=3;c.requestFinish=true;c.requestCards=offer;c.cards=offer;
 c.mulliganSlots=[];c.mulliganPickedId=0;c.keyboardFocusId=0;c.choiceFocused097=-1;c.choiceScroll097=0;c.choiceScrollRequest=0;};
for(const count of [10,11,12,13,17,29,30]){
 freshMulligan(count);reset();c.drawBetaMulligan();
 const grid=c.choiceGrid097,rows=Math.max(2,Math.ceil(count/c.CHOICE_COLS097)),gapY=grid.stepY-grid.h,blockH=rows*grid.h+(rows-1)*gapY;
 const cells=controls.filter(x=>x.tag==='target');
 check(grid.cols===c.CHOICE_COLS097&&grid.rows===rows,'fixed five columns for '+count);
 check(grid.left===c.CHOICE_GRID_X097-c.CHOICE_AREA_X097&&grid.stepX===c.CHOICE_STEP_X097&&grid.stepY===c.CHOICE_STEP_Y097&&grid.padTop>=c.CHOICE_TOP097,'the block keeps the beta anchor and pitch: '+count);
 check(grid.maxScroll===Math.max(0,grid.padTop*2+blockH-c.CHOICE_AREA_H097),'scroll range follows the rows for '+count);
 check((grid.maxScroll>0)===(rows>2),'the bar appears exactly when a third row does not fit: '+count);
 check(cells.length===count,'every offered card is actionable at rest: '+count);
 check(cells.every((x,i)=>Math.abs(x.sprite.x-(grid.left+(i%grid.cols)*grid.stepX))<0.01),'cards keep the five anchored lanes for '+count);
 check(cells.every(x=>x.sprite.x>=grid.left&&x.sprite.x+grid.w<=grid.left+(grid.cols-1)*grid.stepX+grid.w&&x.sprite.y>=grid.padTop&&x.sprite.y+grid.h<=grid.padTop+blockH),'cells stay inside the anchored five-column block: '+count);
 const gridSprite=c.choiceLayer.children.flatMap(s=>s.children).find(s=>s.x===c.CHOICE_AREA_X097&&s.y===c.CHOICE_AREA_Y097&&!s.art);
 check(!!gridSprite,'the cell block is anchored to the parchment opening: '+count);
 // The beta keeps the free lanes of the last row as engraved crown plates. They share the
 // anchored lanes with the cards, so a plate can never sit on top of a dealt card.
 const plates=(gridSprite||{children:[]}).children.filter(s=>s.children.some(c=>c.art&&c.art.id===-3730&&c.art.sub[2]===64&&c.art.sub[3]===80));
 check(plates.length===(grid.cols-count%grid.cols)%grid.cols,'the last row keeps the beta crown plates: '+count);
 check(plates.every(p=>Math.floor((p.y-grid.padTop)/grid.stepY)===rows-1),'crown plates stay in the last row: '+count);
 check(plates.every(p=>{const lane=Math.round((p.x-grid.left)/grid.stepX);return Math.abs(p.x-(grid.left+lane*grid.stepX))<0.01&&lane>=count-(rows-1)*grid.cols&&lane<grid.cols;}),'crown plates fill only the free lanes: '+count);
 check(!plates.some(p=>cells.some(t=>p.x<t.sprite.x+grid.w-1&&p.x+grid.w>t.sprite.x+1&&p.y<t.sprite.y+grid.h-1&&p.y+grid.h>t.sprite.y+1)),'no crown plate overlaps a card: '+count);
 if(grid.maxScroll>0){
  check(!!grid.rod&&!!grid.rod.parent&&grid.thumbH>0&&grid.travel>0,'the rod is drawn in its groove: '+count);
  check(Math.abs(grid.rod.y)<0.01,'the rod starts at the top of its travel: '+count);
  check(c.CHOICE_BAR_X097-14>=c.CHOICE_AREA_X097+grid.left+(grid.cols-1)*grid.stepX+grid.w&&c.CHOICE_BAR_X097+14<=c.CHOICE_AREA_X097+c.CHOICE_AREA_W097,'the groove sits between the cells and the frame: '+count);
  check(!!gridSprite.scrollRect&&gridSprite.scrollRect.x===0&&gridSprite.scrollRect.width===c.CHOICE_AREA_W097&&gridSprite.scrollRect.height===c.CHOICE_AREA_H097,'the scroll window is the parchment opening itself: '+count);
  check(Math.abs(c.CHOICE_AREA_Y097+c.CHOICE_AREA_H097-938.4)<.01,'the window ends on the parchment edge instead of inside the field: '+count);
  const ids=[];
  for(let offset=0;offset<=grid.maxScroll;offset+=Math.round(c.CHOICE_AREA_H097*.6)){
   c.choiceScroll097=offset;reset();c.drawBetaMulligan();ids.push(...controls.filter(x=>x.tag==='target').map(x=>x.card.id));}
  c.choiceScroll097=grid.maxScroll;reset();c.drawBetaMulligan();
  const full=c.choiceGrid097;ids.push(...controls.filter(x=>x.tag==='target').map(x=>x.card.id));
  check(Math.abs(full.rod.y-full.travel)<0.01,'the rod reaches the end of the groove at full scroll: '+count);
  check(new Set(ids).size===count,'every card is reachable by scrolling: '+count);
  // At the end of the travel the row gap after the last row rests on the frame edge, so the
  // bottom row shows whole rather than being sliced mid-card.
  check(Math.abs(full.padTop*2+blockH-(full.maxScroll+c.CHOICE_AREA_H097))<0.01,'the travel ends with the last row whole: '+count);
 }
}
freshMulligan(10);reset();c.drawBetaMulligan();
check(c.choiceGrid097.maxScroll===0,'the accepted ten-card offer still needs no bar');
const g2=c.choiceGrid097,levels=[...new Set(controls.filter(x=>x.tag==='target').map(x=>x.sprite.y))];
check(levels.length===2&&levels[0]===g2.padTop&&levels[1]===g2.padTop+g2.stepY,'ten cards keep the anchored two-row block');
check(Math.abs(c.CHOICE_AREA_Y097+levels[0]-301.4)<=1&&Math.abs(c.CHOICE_AREA_Y097+levels[1]+g2.h-795.4)<=1,'the two-row block spans the beta lanes y 236..722');
freshMulligan(13);reset();c.drawBetaMulligan();
check(c.choiceGrid097.maxScroll>0,'thirteen cards need scrolling');
c.scrollChoice097(9e5);check(c.choiceScroll097===c.choiceGrid097.maxScroll,'the scroll setter clamps to the content end');
c.scrollChoice097(-5);check(c.choiceScroll097===0,'and clamps to the top');
c.mulliganWheel097({delta:-3,stopPropagation(){}});check(c.choiceScroll097>0,'mouse wheel moves the beta grid');
c.keyboardFocusId=12;c.choiceFocused097=-1;c.choiceScroll097=0;reset();c.drawBetaMulligan();
check(c.choiceScroll097>0,'keyboard focus on the last row drags the window down');
for(let redraw=0;redraw<3;redraw++){c.choiceScroll097=0;reset();c.drawBetaMulligan();}
check(c.choiceScroll097===0,'a manual wheel position survives the following redraws');
c.ready=true;c.mulligan=false;c.requestMax=1;c.requestFinish=false;
for(const count of [0,1,8,18,30,31,77,129]){
 c.requestCards=Array.from({length:count},(_,i)=>fixture(i+1,i!==0));c.cards=[];
 const ids=[];
 for(let page=0;page<1;page++){
  reset();c.choicePage=page;c.drawBetaAbilityChoices();
  const targets=controls.filter(x=>x.tag==='target');ids.push(...targets.map(x=>x.card.id));
  check(!controls.some(x=>/Без выбора|Завершить выбор|Продолжить/.test(x.title)),'mandatory selection has no skip '+count+'/'+page);
  check(targets.every(x=>x.sprite.x>=0&&x.sprite.y>=0),'all choice targets in grid '+count+'/'+page);
  check(targets.every(x=>{const card=H.dump(x.sprite).find(o=>o.art&&o.art.id===132402);return !card||card.art.h>=100;}),'readable cards in large choice '+count+'/'+page);
  if(page===0&&count)check(targets[0].card.hidden&&targets[0].card.templateId===0,'concealed offer stays concealed '+count);
 }
 check(ids.length===count&&new Set(ids).size===count,'each option reachable exactly once '+count);
}
c.requestCards=[];c.requestFinish=true;c.choicePage=0;reset();c.drawBetaAbilityChoices();
check(controls.some(x=>x.title==='Продолжить'),'empty optional request can continue');
// Visibility sounds follow transitions, not redraws.
sounds.length=0;c.choiceSoundKey095='';c.abilityHidden=false;c.choiceVisibility095();c.choiceVisibility095();c.abilityHidden=true;c.choiceVisibility095();
check(sounds.join()==='20,21','choice sounds once on showing/hiding');
// Snapshot evidence: duplicate replay replaces the same round; unplayed rounds are absent.
c.noteOutcomeRound095({cue:{kind:17}});
check(c.rewardCard096===null&&c.outcomePage095===0,'new match clears the previous reward and carousel page');
c.noteOutcomeRound095({cue:{kind:6},round:1,scores:[84,13]});c.noteOutcomeRound095({cue:{kind:6},round:1,scores:[84,13]});
c.noteOutcomeRound095({cue:{kind:6},round:2,scores:[0,0]});
check(c.outcomeRounds095.length===2&&c.outcomeRounds095[1].scores.join()==='0,0','rounds deduplicate and zero-zero is a completed draw');
reset();sounds.length=0;c.ready=true;c.drawBetaOutcome095();c.drawBetaOutcome095();
check(sounds.filter(x=>x===18).length===1,'outcome redraw does not repeat the score cue');
check(H.dump(c.content).some(x=>x.text==='—'),'unplayed third round shows empty marker');
c.rewardCard096={templateId:132402,gained:50,total:150};c.selectOutcomePage095(1);check(c.outcomePage095===1,'reward carousel reachable');c.selectOutcomePage095(-1);check(c.outcomePage095===0,'scores reachable again');
c.outcomePage095=1;c.drawBetaOutcome095();c.drawBetaOutcome095();
check(sounds.filter(x=>x===19).length===1&&sounds.filter(x=>x===24).length===1,'reward announcement and card/currency appearance each play once');
sent.length=0;c.ready=true;c.closeOutcome095();c.closeOutcome095();check(sent.length===1,'repeated result close dispatches once');
// Confirmation callbacks remain single-use and revision-bound for both devices.
let yes=0,no=0;reset();c.drawBetaConfirm('ЗАГОЛОВОК','длинный текст '.repeat(60),()=>yes++,()=>no++);const accept=c.confirmYes;accept();accept();check(yes===1,'confirmation accept dispatched once');
reset();c.drawBetaConfirm('ЗАГОЛОВОК','текст',()=>yes++,()=>no++);const stale=c.confirmYes;c.revision++;stale();check(yes===1,'stale confirmation cannot dispatch');
reset();c.drawBetaConfirm('ЗАГОЛОВОК','текст',()=>yes++,()=>no++);c.confirmNo095();c.confirmYes();check(no===1&&yes===1,'cancel consumes confirmation');
for(const field of ['requestId','requestPlayer','requestKind']){reset();c.drawBetaConfirm('ЗАГОЛОВОК','текст',()=>yes++,()=>no++);const stale=c.confirmYes,old=c[field];c[field]++;stale();check(yes===1,'same-revision stale modal '+field+' cannot dispatch');c[field]=old;}
// The hand-offer protocol uses kind=2, but must retain a readable side preview.
c.requestKind=2;c.mulligan=false;c.mulliganPreview=new c.Sprite();c.mulliganPreviewKey='';c.showMulliganCard(fixture(99),{});
check(c.mulliganPreview.numChildren>0,'hand-only kind-2 offer has a side preview');c.requestKind=1;
// Public piles: every card reachable, including page boundaries; no rule-engine calls.
c.pileOpen=true;c.pileView={revision:10,count:46,side:1,zone:16,cards:Array.from({length:46},(_,i)=>({...fixture(i+1),description:'Описание'}))};
const pileIds=[];
// 0.9.7: one scrolling grid sharing the card picker's five anchored lanes and the same
// parchment scroll window; every card is reachable by scrolling.
for(let step=0;step<12;step++){reset();c.pileLayer=new c.Sprite();c.pilePicked=null;c.pileScroll097=step*c.CHOICE_STEP_Y097;c.drawBetaPile095();pileIds.push(...controls.filter(x=>x.tag==='card').map(x=>x.card.id));}
check(new Set(pileIds).size===46,'every pile card is reachable by scrolling');
reset();c.pileLayer=new c.Sprite();c.pilePicked=null;c.pileScroll097=0;c.drawBetaPile095();
const pileGrid=c.pileLayer.children.flatMap(s=>s.children).find(s=>s.x===c.CHOICE_AREA_X097&&s.y===c.CHOICE_AREA_Y097&&!s.art);
check(!!pileGrid&&!!pileGrid.scrollRect&&pileGrid.scrollRect.height===c.CHOICE_AREA_H097,'the pile window is the parchment opening too');
check(controls.filter(x=>x.tag==='card').every(x=>Math.abs((x.sprite.x-(c.CHOICE_GRID_X097-c.CHOICE_AREA_X097))%c.CHOICE_STEP_X097)<0.01&&Math.abs((x.sprite.y-c.CHOICE_TOP097)%c.CHOICE_STEP_Y097)<0.01&&x.sprite.x>=c.CHOICE_GRID_X097-c.CHOICE_AREA_X097&&x.sprite.y>=c.CHOICE_TOP097),'pile cards share the card picker lanes');
// pileCardInspect includes the existing complete-card action; bind it separately.
check(!H.extract('drawBetaPile095',source).includes('send('),'pile browser has no native mutation path');
// Rebuilding the virtual keyboard must preserve the live input/counter and popup chrome.
Object.assign(c,{nameKeyboard095:null,nameRussian:true,nameUpper:false,textPurpose:0,textLimit:48,nameLetter:()=>()=>{},editName(){},submitNameInput(){}});
vm.runInContext(H.extract('drawNameKeyboard',source).replace('Sprite(nameLayer.getChildAt(1))','nameLayer.getChildAt(1)'),c);
c.nameLayer=new c.Sprite();c.nameLayer.addChild(new c.Sprite());const box=c.popupWindow095(c.nameLayer,460,180,1000,720,'НАЗВАНИЕ КОЛОДЫ');
c.nameField=new c.TextField();c.nameCounter=new c.TextField();box.addChild(c.nameField);box.addChild(c.nameCounter);const fixed=box.numChildren;
c.drawNameKeyboard();c.drawNameKeyboard();
check(box.children.includes(c.nameField)&&box.children.includes(c.nameCounter),'language/case switches retain text input and counter');
check(box.numChildren===fixed+1,'keyboard rebuild replaces only its own container');
// Run the real keyboard filter and paging route, including PageUp/PageDown.
let keyCode=H.extract('onKey',source).replace(/keyboardStage.focus is TextField/g,'(keyboardStage.focus && keyboardStage.focus.isText)').replace(/TextField\(keyboardStage.focus\)/g,'keyboardStage.focus');
vm.runInContext(H.extract('controllerPage',source)+'\n'+keyCode,c);
Object.assign(c,{effectGallery:false,introStart:0,controllerMenuOpen:false,nameOpen:false,detailOpen:false,pileOpen:false,mulliganConfirm:false,
 editorDragId178:0,createDeckOpen178:false,kegOpen:false,keyboardStage:{focus:null},canInspectPile:()=>false,heldKey:0,lastKeyTime:0,dragId:0,
 flags:0,playing:false,editorExitPrompt:false,tutorialPage:-1,choicePage:0,requestCards:Array.from({length:77},(_,i)=>fixture(i+1))});
const key=k=>{c.heldKey=0;c.onKey({keyCode:k,preventDefault(){},stopImmediatePropagation(){}});};
c.abilityHidden=false;c.mulliganHidden=false;c.choiceGrid097=c.betaChoiceGrid097(77);c.choiceScroll097=0;key(34);check(c.choiceScroll097>0,'keyboard PageDown scrolls long choice list');key(33);check(c.choiceScroll097===0,'keyboard PageUp returns');
c.flags=16;c.ready=true;sent.length=0;key(27);check(sent.length===1&&sent[0].name==='OnBetaGwentBoardClose','Escape closes the result without opening battle settings');
// Import confirmation waits for the authoritative result, and ignores stale callbacks.
Object.assign(c,{ready:true,nameOpen:true,nameRevision:c.revision,exchangeImport:true,exchangePending095:false,exchangeMissing:[],textPurpose:3,
 nameField:new c.TextField(),exchangeMessage:new c.TextField(),exchangeQuotedCode:'BG1:example',exchangeCurrent:()=>true,traceImport090(){}});
sent.length=0;c.submitDeckExchange();c.submitDeckExchange();check(sent.length===1&&c.exchangePending095,'repeated deck import dispatches once while pending');
c.setDeckExchange(c.revision-1,'','error',false);check(c.exchangePending095,'stale import reply cannot unlock pending action');
c.setDeckExchange(c.revision,'','error',false);check(!c.exchangePending095,'matching import reply permits retry');
let craft=c.exchangeCraft(132402);c.revision++;craft();check(sent.length===1,'old craft callback cannot use the next revision');c.nameRevision=c.revision;
craft=c.exchangeCraft(132402);craft();craft();check(sent.length===2,'missing-card craft dispatches once while pending');
c.boardClosePending095=false;sent.length=0;c.confirmBoardClose095();c.confirmBoardClose095();check(sent.length===1,'surrender confirmation dispatches once');
const raw=fs.readFileSync(file);check(raw.subarray(0,3).equals(Buffer.from([239,187,191]))&&!raw.toString().replace(/\r\n/g,'').includes('\n'),'Board BOM and CRLF preserved');
// Independent measurements from img/мулиган бета*.png (2560x1440 -> stage x.75).
const measured=c.betaChoiceGrid097(12);
check(Math.abs(c.CHOICE_GRID_X097-184.5)<1&&Math.abs(c.CHOICE_AREA_Y097+measured.padTop-237.4)<1,'first cell matches the Beta screenshot');
check(measured.w===180&&measured.h===219&&measured.stepX===234&&measured.stepY===275,'card size and pitch match the screenshot');
check(Math.abs(c.CHOICE_AREA_Y097+measured.padTop+2*measured.stepY-measured.maxScroll-640.4)<1,'bottom scroll puts the third row at the Beta screenshot position');
for(const count of [1,3,5,7,12,31,77]){
 const grid=c.betaChoiceGrid097(count);
 check(grid.rows===Math.max(2,Math.ceil(count/5)),'Beta fills at least two rows: '+count);
 const root=new c.Sprite(),surface=c.pickerSurface098(root,grid,grid.maxScroll);
 const paper=surface.children.slice(0,3);check(surface.scrollRect.y===grid.maxScroll&&paper[0].y===0&&paper[1].y<paper[0].art.h&&paper[2].y<paper[1].y+paper[1].art.h&&Math.abs(paper[2].y+paper[2].art.h-grid.contentH)<.01,'paper shares the card scroll offset with covered bitmap seams: '+count);
 check(surface.children.filter(x=>x.art&&x.art.id===-3730).length===2,'both original drawings travel with the parchment: '+count);
}
// Pointer dragging must work after stage scaling and must release every stage listener.
const proto=c.Sprite.prototype,oldAdd=proto.addEventListener,oldRemove=proto.removeEventListener;
proto.addEventListener=function(name,fn){this.events??={};(this.events[name]??=[]).push(fn);};
proto.removeEventListener=function(name,fn){if(this.events?.[name])this.events[name]=this.events[name].filter(x=>x!==fn);};
const host=new c.Sprite();c.stage=host;c.Event.DEACTIVATE='deactivate';
Object.assign(c,{playing:false,pileOpen:false,mulligan:true,abilityHidden:false,mulliganHidden:false,requestId:7,pickerDragCancel098:null});
let offsets=[];const root=new c.Sprite();c.betaPickerScroll098(root,measured,0,v=>offsets.push(v));
const bar=root.children[0],hit=bar.children[0];bar.localToGlobal=p=>({x:p.x*.75,y:100+p.y*.75});
const pointer=y=>({stageX:0,stageY:100+y*.75,stopImmediatePropagation(){}});
hit.events.d[0](pointer(measured.thumbH/2));
check(offsets.at(-1)===0,'grabbing the rod does not jump');
host.events[c.MouseEvent.MOUSE_MOVE][0](pointer(c.CHOICE_BAR_H097));
check(offsets.at(-1)===measured.maxScroll,'drag reaches bottom under .75 stage scaling');
host.events[c.MouseEvent.MOUSE_UP][0]({});
check(Object.values(host.events).every(a=>!a.length),'mouse-up releases all stage drag listeners');
hit.events.d[0](pointer(c.CHOICE_BAR_H097));host.events.deactivate[0]({});
check(Object.values(host.events).every(a=>!a.length),'deactivation releases all stage drag listeners');
hit.events.d[0](pointer(0));c.cancelPickerDrag098();
check(Object.values(host.events).every(a=>!a.length),'closing a picker cancels its active drag');
hit.events.d[0](pointer(0));c.requestId++;host.events[c.MouseEvent.MOUSE_MOVE][0](pointer(50));
check(Object.values(host.events).every(a=>!a.length),'a replaced authoritative request cancels the old drag');
proto.addEventListener=oldAdd;proto.removeEventListener=oldRemove;
// Selection beyond the viewport must first reveal the row, for both navigation devices.
c.pileOpen=true;c.pileView={revision:10,side:1,zone:32,cards:Array.from({length:46},(_,i)=>fixture(i+1))};c.pileLayer=new c.Sprite();c.pilePicked=null;
c.drawPileView=()=>c.drawBetaPile095();
for(const index of [0,14,45,20,0]){
 c.selectPicker098(index);const grid=c.betaChoiceGrid097(46),top=grid.padTop+Math.floor(index/5)*grid.stepY;
 check(c.pilePicked===c.pileView.cards[index]&&top>=c.pileScroll097&&top+grid.h<=c.pileScroll097+c.CHOICE_AREA_H097,'pile focus reveals the whole card: '+index);
}
c.pileOpen=false;c.requestCards=Array.from({length:77},(_,i)=>fixture(i+1));c.cards=[];c.mulligan=false;c.requestFinish=false;c.choiceScrollRequest=0;c.choiceFocused097=-1;
reset();c.drawBetaAbilityChoices();c.selectPicker098(76);check(c.keyboardFocusId===77&&c.choiceScroll097>0,'long ability choice uses the same focus scroll');
reset();c.drawBetaAbilityChoices();check(c.choiceScroll097>0,'redrawing a long choice retains its scroll');
freshMulligan(7);c.mulliganHidden=true;reset();c.drawBetaMulligan();
check(controls.some(n=>n.title==='Показать карты'&&n.sprite.x===1004&&n.sprite.y===1000),'hidden mulligan retains the Beta show button position');
check(controls.some(n=>n.title==='Закончить обмен'&&n.sprite.x===678),'hidden mulligan still offers finish');c.mulliganHidden=false;
c.pileOpen=true;c.pilePicked=fixture(1);c.detailOpen=false;c.nameOpen=false;c.controllerMenuOpen=false;c.mulliganConfirm=false;c.flags=0;let opened=null;c.openCardDetail=card=>{opened=card;};key(13);
check(opened===c.pilePicked,'Enter inspects the selected pile card');c.pileOpen=false;
proto.addEventListener=function(name,fn){this.events??={};(this.events[name]??=[]).push(fn);};
vm.runInContext(['drawBetaSidePreview','scheduleSideKeywords102','clearSideKeywords102'].map(n=>H.extract(n,source)).join('\n'),c);
Object.assign(c,{sideKeywordParent102:null,sideKeywordAnchor102:null,sideKeywordPane102:null,sideKeywordCard102:0});
Object.assign(c,{pileOpen:true,animations:[],reducedMotion:true,editingDeck:false,selectingDecks:false,browsingCatalog:false});
c.drawBetaSidePreview(fixture(1),{description:'Длинное описание'},new c.Sprite());
const description=c.pileDetail;description.maxScrollV=100;description.scrollV=10;
check(description.events.w.length===1,'pile description registers one wheel handler');
description.events.w[0]({delta:2,stopPropagation(){}});
check(description.scrollV===8,'one wheel event scrolls the description once');
proto.addEventListener=oldAdd;
const controllerSource=fs.readFileSync(process.env.ROOT+'/BetaGwent/ui/src/BetaGwentController.as','utf8'),moves=[];
c.getFocus=()=>({card:{pickerIndex098:12}});c.candidates=()=>[];c.invoke=(name,node)=>moves.push({name,node});
vm.runInContext(H.extract('navigate',controllerSource)+'\n'+H.extract('focusPicker',controllerSource),c);
for(const mode of ['choice','pile']){c.state=()=>({mode});c.movementAt=-1000;c.navigate(40);check(moves.at(-1).name==='pickerMove'&&moves.at(-1).node.index===12&&moves.at(-1).node.direction===40,'D-pad delegates hidden-row navigation in '+mode);}
let selectedNode=null;const wanted={scope:'choice',card:{pickerIndex098:14}};
c.candidates=()=>[{scope:'pile',card:{pickerIndex098:14}},wanted];c.state=()=>({mode:'choice'});c.select=node=>{selectedNode=node;};c.focusPicker(14);
check(selectedNode===wanted,'controller restores the revealed card in the current picker scope');
const localePath=path.join(path.dirname(file),'BetaGwentUiText096.as');
const locale=fs.readFileSync(fs.existsSync(localePath)?localePath:process.env.ROOT+'/BetaGwent/ui/src/BetaGwentUiText096.as','utf8');
const maps=JSON.parse(locale.match(/BY:Array=(.*);/)[1]);
for(let lang=0;lang<12;lang++)for(const key of ['Бронзовая','Серебряная','Золотая','Итоги партии','Награды'])check(!!maps[lang][key]&&maps[lang][key]!==key,'accepted/new translation retained '+lang+'/'+key);
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(raw).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

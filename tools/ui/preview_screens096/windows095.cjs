'use strict';
// Layout preview from production AS. Does not claim Scaleform raster/animation parity.
const fs=require('fs'),vm=require('vm'),path=require('path');
process.env.ROOT=path.resolve(__dirname,'../../..');
const output=process.argv[2];process.argv=process.argv.slice(0,2);require('../check_windows095.cjs');
const H=require('./harness.cjs'),c=H.ctx,src=fs.readFileSync(process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as','utf8');
const scenes={};
Object.assign(c,{ready:true,playing:false,revision:30,serverRevision:30,skin:3,requestId:7,requestKind:1,requestPlayer:1,
 requestFinish:true,requestCount:1,requestMax:3,choicePage:0,mulliganHidden:false,abilityHidden:false,mulliganConfirm:false,editingDeck:false,selectingDecks:false,browsingCatalog:false,
 pileOpen:false,detailOpen:false,controllerMenuOpen:false,nameOpen:false,animations:[],reducedMotion:true,mulliganSlots:[],mulliganPickedId:0,keyboardFocusId:0,
 templateDetails:{},cardDetails:{},leaderNames:['ЭРЕДИН','ЭМГЫР ВАР ЭМРЕЙС'],crowns:[2,1],flags:16,rewardMessage:'Награда за победу',
 sideFaction:()=>1,ambushReading:()=>'',closeControllerMenu(){},clearDetailKeywords096(){},setChildIndex(){},numChildren:20,detailBack:[],historyReturnPage:-1,historyReturnEntry:-1,
 detailNavCard:null,historyEntryIndex:-1,historyEventPage:0,historyPage:0,scores:[84,13],tutorialPage:-1,
});
const names=['drawBetaSidePreview','drawRewardPanel096','historyLine','historyCardButton','historyEntryAction','openHistory','openHistoryEntry',
 'menuItem','menuTabAction','controllerMenuAction','openControllerMenu','openDeckExchange','redrawExchange'];
vm.runInContext(names.map(n=>H.extract(n,src)).join('\n'),c);
const fixture=H.all.filter(x=>x.typeMask===4&&x.templateId>0).slice(0,10).map((x,i)=>({...x,id:i+1,side:1,zone:8,revealed:true,tokens:0,timer:-1}));
c.cards=fixture;c.requestCards=fixture;c.cardDetails=Object.fromEntries(fixture.map(x=>[x.id,{description:x.description,typeMask:4}]));
function fresh(){c.content=new c.Sprite();c.choiceLayer=new c.Sprite();c.detailLayer=new c.Sprite();}
fresh();c.mulligan=true;c.drawBetaMulligan();scenes['choice-mulligan']=H.dump(c.content);
for(const count of [7,12,31]){
 const many=Array.from({length:count},(_,i)=>({...fixture[i%fixture.length],id:i+1}));
 c.cards=many;c.requestCards=many;c.mulliganSlots=[];c.keyboardFocusId=0;c.mulliganPickedId=0;c.choiceScrollRequest=0;c.choiceFocused097=-1;
 fresh();c.choiceScroll097=0;c.drawBetaMulligan();scenes['mulligan-'+count+'-top']=H.dump(c.content);
 if(c.choiceGrid097.maxScroll){fresh();c.choiceScroll097=c.choiceGrid097.maxScroll;c.drawBetaMulligan();scenes['mulligan-'+count+'-bottom']=H.dump(c.content);}
 if(count===12){fresh();c.mulliganPickedId=6;c.drawBetaMulligan();scenes['mulligan-12-inspect']=H.dump(c.content);c.mulliganPickedId=0;}
}
c.cards=fixture;c.requestCards=fixture;
fresh();c.mulligan=false;c.templateChoice=false;c.pileChoice=true;c.rowMode=14;c.drawBetaAbilityChoices();scenes['choice-ability']=H.dump(c.content);
fresh();c.requestId=0;c.outcomePage095=0;c.outcomeRounds095=[{round:1,scores:[84,13]},{round:2,scores:[12,41]},{round:3,scores:[55,38]}];c.rewardCard096={templateId:fixture[0].templateId,gained:50,total:150};c.drawBetaOutcome095();scenes['outcome-scores']=H.dump(c.content);
fresh();c.outcomePage095=1;c.drawBetaOutcome095();scenes['outcome-rewards']=H.dump(c.content);
fresh();c.actionHistory=fixture.slice(0,5).map((x,i)=>({title:x.title,kind:1,start:[12,13],end:[20+i,13],actor:x,events:[{target:fixture[(i+1)%10],title:'Усиление'}]}));c.openHistory();scenes['history']=H.dump(c.detailLayer);
fresh();c.pileLayer=new c.Sprite();c.pileOpen=true;c.pileView={revision:30,count:fixture.length,side:1,zone:32,cards:fixture};c.pilePage=0;c.pilePicked=null;c.drawBetaPile095();scenes['pile']=H.dump(c.pileLayer);
fresh();c.drawBetaConfirm('ОБМЕН КАРТ','Закончить обмен? Можно заменить ещё 2.',()=>{},()=>{});scenes['confirmation']=H.dump(c.choiceLayer);
fresh();Object.assign(c,{detailOpen:false,pileOpen:false,nameOpen:false,kegOpen:false,browsingCatalog:false,editingDeck:false,selectingDecks:false,
 controllerMenuOpen:false,controllerMenuLayer:new c.Sprite(),controllerMenuTab:0,controllerMenuFocus:'',leaderOne:true,entryMode:0,
 canAct:()=>true,canInspectPile:()=>true,skipReplay(){}});c.controller.menuControl=()=>{};
c.openControllerMenu();scenes['battle-menu']=H.dump(c.controllerMenuLayer);
Object.assign(c,{controllerMenuOpen:false,nameOpen:false,nameLayer:new c.Sprite(),editingDeck:true,ready:true,
 keyboardStage:{focus:null},copyExchange(){},pasteExchange(){},checkDeckExchange(){},clipboardText:()=>'',exchangeCurrent:()=>false,exchangeCode:()=>'',scraps:500});
c.openDeckExchange(false);scenes['deck-export']=H.dump(c.nameLayer);
c.nameOpen=false;c.nameLayer=new c.Sprite();c.openDeckExchange(true);scenes['deck-import']=H.dump(c.nameLayer);
fs.writeFileSync(output,JSON.stringify(scenes));console.log('Recorded '+Object.keys(scenes).length+' production layouts');

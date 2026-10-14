'use strict';
// Execute the shipped AS and native event bodies, including stale-input and receipt paths.
const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const asPath='BetaGwent/ui/src/BetaGwentBoard.as',wsPath='BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws';
const as=fs.readFileSync(asPath,'utf8'),ws=fs.readFileSync(wsPath,'utf8');
function extract(source,name,native=false){
 const a=source.indexOf((native?'event ':'function ')+name+'(');assert(a>=0,name);const b=source.indexOf('{',a);let i=b+1,d=1;
 while(d){if(source[i]==='{')d++;if(source[i]==='}')d--;i++;}
 let text;
 // Explicit type stripping also handles AS for-in declarations and custom native structs.
 text=source.slice(a,i).replace(/^event /,'function ').replace(/:\s*(?:array<[^>]+>|String|Function|Object|void|int|uint|bool|Boolean|Number|Array|Sprite|TextField|SBetaGwentClearedDeck|W3PlayerWitcher|string)(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2))')
  .replace(/\(W3PlayerWitcher\)thePlayer/g,'thePlayer')
  .replace(/var snapshot\s*;/g,'var snapshot={};');
 return text;
}
let checks=0;const check=(v,label)=>{assert(v,label);checks++;};
const c=vm.createContext({Math,String,Number,Object,Array,int:n=>n|0});
vm.runInContext(`var editingDeck=true,ready=true,revision=10,editorState={slot:1,faction:2,leader:11,total:3},editorName='Test',editorBaseline=null;
var editorNewOnly=false,editorScroll178=0,deckScroll178=0,editorFeedbackOrigin178=null;function editorFeedbackPoint178(){return {x:0,y:0};}
var editorPosition=0,editorStrength=0,editorSearch='x',editorTier=8,editorType=4,editorOwnedOnly=true,editorFactionOnly=true,editorPage=4;
var editorCards=[],editorById={},editorUndo=[],editorPending=null,editorUndoPending=false,editorFlight=null;
var BetaGwentUi138={filters:{}},definitions={},BetaGwentFullCatalog={find(id){return definitions[id];}},events=[],renders=0;
function render(){renders++;}function send(name,args){events.push([name,args]);}function closeControllerMenu(){controllerMenuOpen=false;editorExitPrompt=false;}
var controllerMenuOpen=false,editorExitPrompt=false,editorExitNextKeg=false,controllerMenuLayer={},WIDE_PAD=0,buttons=[];
function panel(){}function betaFrame(){return {};}function text(){return {};}function editorSmallButton(parent,title,x,y,w,h,enabled,action){buttons.push({title,action});}
var controller={focusTag(tag){this.focused=tag;}};
`+['editorSignature','requestEditorExit','leaveEditor','editorExtraFilter','editorPositionMatches','sortEditorCards','sortEditorCollection','rememberEditorFilters','restoreEditorFilters','editorCounts','settleEditorUndo','undoEditorChange','editorAction'].map(n=>extract(as,n)).join('\n'),c);
const card=(id,power=5,tier=2)=>({templateId:id,copies:1,power,tier,typeMask:4,title:'same',canAdd:true});
c.editorCards=[card(1),card(2)];c.definitions={1:{placementMask:1},2:{placementMask:7},3:{placementMask:2},4:{placementMask:4}};
c.editorBaseline=c.editorSignature();c.requestEditorExit();check(c.events.at(-1)[0]==='OnBetaGwentDeckEditorLeave'&&c.events.at(-1)[1][1]===false,'unchanged draft exits without a prompt');
c.ready=true;c.events=[];c.editorCards.reverse();check(c.editorSignature()===c.editorBaseline,'composition comparison ignores array order');
c.editorName='Renamed';c.requestEditorExit(true);check(c.editorExitPrompt&&c.events.length===0&&c.buttons.length===3,'rename prompts before exiting or opening kegs');
c.buttons[2].action();check(!c.controllerMenuOpen&&c.events.length===0&&c.editingDeck,'cancel keeps draft and sends no mutation');
c.buttons=[];c.requestEditorExit(true);c.buttons[0].action();check(c.events.at(-1)[1].join('|')==='10|true|Renamed|true','save forwards edited name and keg transition');
c.ready=true;c.editorName='Test';c.editorState.leader=12;check(c.editorSignature()!==c.editorBaseline,'leader changes are dirty');c.editorState.leader=11;
c.editorState.faction=4;check(c.editorSignature()!==c.editorBaseline,'faction changes are dirty');c.editorState.faction=2;
c.editorCards[0].copies=2;check(c.editorSignature()!==c.editorBaseline,'copy changes are dirty');c.editorCards[0].copies=1;
for(let pos=1;pos<=4;pos++){c.editorPosition=pos;for(let id=1;id<=4;id++)check(c.editorPositionMatches(card(id))===(id===[0,1,3,4,2][pos]),'source placement mask '+pos+'/'+id);}
c.editorPosition=5;check(c.editorPositionMatches({typeMask:2})&&!c.editorPositionMatches(card(2)),'event filter is exclusive of units');
c.editorStrength=1;check(c.sortEditorCollection(card(1,3,8),card(2,10,2))<0,'weak-first power precedes rarity');
c.editorStrength=2;check(c.sortEditorCollection(card(1,3,8),card(2,10,2))>0,'strong-first power precedes rarity');
check(c.sortEditorCollection(card(1),card(2))<0,'ties have deterministic template ordering');
c.rememberEditorFilters();c.editorPosition=0;c.editorStrength=0;c.restoreEditorFilters(2);check(c.editorPosition===5&&c.editorStrength===2,'per-faction filter memory includes new fields');
c.editorExtraFilter(0)();check(c.editorPage===0&&c.editorPosition===0&&c.editorStrength===0&&!c.editorOwnedOnly&&!c.editorFactionOnly&&c.editorSearch===''&&c.editorTier===0&&c.editorType===0,'reset restores every collection filter');
c.editorCards=[card(1),card(2)];c.editorById={1:c.editorCards[0],2:c.editorCards[1]};c.editorUndo=[];c.ready=true;
c.editorAction('OnBetaGwentDeckEditorClear')();c.editorCards.forEach(x=>x.copies=0);c.settleEditorUndo();
check(c.editorUndo.length===1&&c.editorUndo[0].bulk&&c.editorUndo[0].before[1]===1,'clear creates one reversible bulk entry');
c.ready=true;c.undoEditorChange();check(c.events.at(-1)[0]==='OnBetaGwentDeckEditorRestore','undo uses a single native restore');c.editorCards.forEach(x=>x.copies=1);c.settleEditorUndo();check(c.editorUndo.length===0,'restore acknowledgement consumes the undo entry');
c.ready=true;c.editorAction('OnBetaGwentDeckEditorChange',1,1)();c.editorCards[0].copies=2;c.settleEditorUndo();check(c.editorUndo.length===1&&!c.editorUndo[0].bulk,'ordinary per-card undo remains compatible');
// Actual native event bodies; engine arrays have value semantics and bounded snapshots.
class WArray extends Array {Size(){return this.length;}Clear(){this.length=0;}PushBack(v){this.push(v?.cards?{...v,cards:WArray.from(v.cards)}:v);}Erase(i){this.splice(i,1);}}
const n=vm.createContext({WArray,LogChannel(){},FlashArgInt:v=>v,FlashArgBool:v=>v});
vm.runInContext(`var configured=true,revision=20,deckDraft={cards:new WArray(1,2,2),faction:2},deckClearHistory=new WArray(),published=0;
function PublishDeckEditor(){revision++;published++;}var selectingDecks=false,saveOkay=false,openCalls=0;
function OnBetaGwentDeckEditorSave(value,title){if(!saveOkay){PublishDeckEditor();return false;}deckDraft=null;revision++;return true;}
function OnBetaGwentDeckEditorCancel(){deckDraft=null;revision++;return true;}function OnBetaGwentKegOpen(){openCalls++;}
var kegOnly=true,kegCanOpenNext=false,grants=0,backups=0,acks=[],collection=0,pending=true;
var thePlayer={BetaGwentKegPending(){return pending;},BetaGwentChooseKeg(id){if(!pending||id!==99)return false;pending=false;grants++;return true;},BetaGwentBackupProfile(){backups++;},BetaGwentEnsureCollection(){}};
var finishKegChoice={InvokeSelfTwoArgs(rev,success){acks.push([rev,success]);}};function PublishCollection(){collection++;}function Publish(){}
`+['OnBetaGwentDeckEditorClear','OnBetaGwentDeckEditorRestore','OnBetaGwentDeckEditorLeave','OnBetaGwentKegChoose'].map(nm=>extract(ws,nm,true)).join('\n'),n);
check(!n.OnBetaGwentDeckEditorClear(19)&&n.deckDraft.cards.length===3,'stale clear is rejected');
check(n.OnBetaGwentDeckEditorClear(20)&&n.deckDraft.cards.length===0&&n.deckClearHistory.length===1,'native clear records snapshot');
check(!n.OnBetaGwentDeckEditorRestore(20),'stale restore is rejected');
check(n.OnBetaGwentDeckEditorRestore(21)&&n.deckDraft.cards.join(',')==='1,2,2'&&n.deckClearHistory.length===0,'native restore preserves duplicate copies');
check(!n.OnBetaGwentDeckEditorRestore(22),'repeated restore rejected');
check(!n.OnBetaGwentDeckEditorLeave(22,true,'invalid',true)&&n.deckDraft&&n.openCalls===0,'failed save keeps draft and does not open a keg');
check(n.OnBetaGwentDeckEditorLeave(23,false,'ignored',true)&&!n.deckDraft&&n.openCalls===1,'discard transitions only after abandoning draft');
n.revision=30;check(!n.OnBetaGwentKegChoose(29,99)&&n.grants===0&&n.openCalls===1,'stale choice cannot grant or open another keg');
check(!n.OnBetaGwentKegChoose(30,1)&&n.acks.at(-1)[1]===false&&n.grants===0,'invalid choice returns to selection without auto-opening');
check(n.OnBetaGwentKegChoose(30,99)&&n.grants===1&&n.backups===1&&n.revision===31&&n.acks.at(-1).join(',')==='31,true'&&n.kegCanOpenNext,'grant and backup precede successful receipt');
check(!n.OnBetaGwentKegChoose(30,99)&&n.grants===1,'duplicate old choice cannot grant twice');
check(!n.OnBetaGwentKegChoose(31,99)&&n.grants===1&&n.openCalls===1,'duplicate current choice cannot consume a keg');
// UI next/finish commands never grant, and block repeats until native acknowledgement.
vm.runInContext(`var serverRevision=40,kegOpen=true,kegCommitted=false,kegPicked=0,kegOffers=[{templateId:99}],pendingKeg=true,kegPhase=2,unopenedKegs=2;
function kegClose(){kegOpen=false;}`+['finishKegChoice','commitKegChoice','nextKeg','kegFinish'].map(nm=>extract(as,nm)).join('\n'),c);
c.ready=true;c.revision=40;c.events=[];c.commitKegChoice();c.commitKegChoice();check(c.events.length===1&&!c.ready,'confirm sends one choice until ack');
c.finishKegChoice(39,true);check(!c.ready&&!c.kegCommitted,'stale receipt cannot unlock next');
c.finishKegChoice(41,true);check(c.ready&&c.kegCommitted&&!c.pendingKeg&&c.kegPhase===3,'summary waits for committed native receipt');
c.nextKeg();c.nextKeg();check(c.events.length===2&&c.events[1][0]==='OnBetaGwentKegOpen'&&c.events[1][1][0]===41,'next opens once with current receipt revision');
c.ready=true;c.unopenedKegs=0;c.nextKeg();check(c.events.length===2,'no next action without unopened kegs');c.kegFinish();check(!c.kegOpen,'done closes a committed result without replaying the grant');
const canonical=JSON.parse(fs.readFileSync('data/beta924/normalized/catalog.json','utf8'));
const catalog=JSON.parse(fs.readFileSync('data/beta924/planning/full_catalog.json','utf8')).cards;
for(const row of catalog){const source=canonical.templates.find(t=>t.templateId===row.templateId);check(row.placementMask===((+source.placement.PlayerSide|+source.placement.OpponentSide)&7),'real source placement '+row.templateId);}
for(const dir of ['src','src-BetaGwentBoard','src-GwintGame','src-BetaGwentKeg','src-DeckBuilder']){const raw=fs.readFileSync('BetaGwent/ui/'+dir+'/BetaGwentBoard.as');check(raw.equals(fs.readFileSync(asPath))&&raw.subarray(0,3).toString('hex')==='efbbbf'&&!/(?<!\r)\n/.test(raw.toString()),'mirrored AS BOM/CRLF '+dir);}
const report={stage:168,checks,actualActionScript:true,actualNativeEvents:true,nativeGameTested:false,sources:Object.fromEntries([asPath,wsPath].map(p=>[p,crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')]))};
fs.writeFileSync('docs/evidence/editor168.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

// Execute production AS dispatch/creation and native events against immutable-deck expectations.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto'),assert=require('node:assert/strict');
const boardPath=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as';
const nativePath=process.argv[3]||'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws';
const board=fs.readFileSync(boardPath,'utf8'),nativeRaw=fs.readFileSync(nativePath);
const native=nativeRaw.toString(nativeRaw[0]===255&&nativeRaw[1]===254?'utf16le':'utf8');
function extract(source,name,event=false){
 const start=source.indexOf((event?'event ':'function ')+name+'(');assert(start>=0,name);
 const open=source.indexOf('{',start);let end=open+1,depth=1;
 while(depth){depth+=(source[end]==='{')-(source[end]==='}');end++;}
 return source.slice(start,end).replace(/^event /,'function ').replace(/\bout\s+(?=\w+\s*:)/g,'')
 .replace(/:\s*(?:array<[^>]+>|String|string|Function|Object|void|int|uint|bool|Boolean|Number|Array|Sprite|Point|Rectangle|TextField|Event|MouseEvent|SBetaGwentDuelDefinition|SBetaGwentDeckExchange|W3PlayerWitcher)(?=\s*(?:[,)=;{]|in\b))/g,'')
 .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))').replace(/\(W3PlayerWitcher\)thePlayer/g,'thePlayer');
}
let checks=0;const failures=[];function check(ok,label){checks++;if(!ok)failures.push(label);}
class WArray extends Array{Size(){return this.length;}Erase(i){this.splice(i,1);}Clear(){this.length=0;}}
function state(slot=1){return {slot,faction:2,leader:11,cards:WArray.of(101,101,102),title:'Имя',limitedCollection:true};}
function nativeContext(draft=state()){
 const c=vm.createContext({LogChannel(){},configured:true,selectingDecks:true,revision:9,deckDraft:draft,
  deckClearHistory:WArray.of({cards:[101]}),libraryOnly:true,npcMatch:false,forcedBetaFaction:0,editorPublishedFaction:2,
  replies:[],published:0,collectionChecks:0,allocations:0,
  BetaGwentDuelIsLeader:id=>[11,12,21].includes(id),
  BetaGwentDuelDefinition:id=>({header:{factionMask:[21,201].includes(id)?4:id===102?1:2}}),
  BetaGwentParseDeckExchange:()=>({valid:true,leader:11,faction:2,cards:[101],message:''}),
 });
 c.thePlayer={BetaGwentOwned:()=>1,BetaGwentEnsureCollection(){c.collectionChecks++;return true;}};
 c.deckLibrary={Edit(){c.allocations++;return state(3);}};
 c.PublishDeckEditor=()=>{c.published++;c.revision++;};c.PublishDeckSelection=()=>{c.published++;};
 c.PublishDeckExchange=(code,message,accepted)=>c.replies.push({code,message,accepted});
 vm.runInContext(extract(native,'OnBetaGwentDeckEditorLeader',true)+'\n'+extract(native,'OnBetaGwentDeckCreate',true)+'\n'+extract(native,'ExchangeParse'),c);
 return c;
}
// Existing user and starter decks must retain leader, faction, duplicate cards and undo history.
for(const slot of [1,9])for(const leader of [11,12,21,999]){
 const c=nativeContext(state(slot)),before=JSON.stringify([c.deckDraft,c.deckClearHistory]);
 check(c.OnBetaGwentDeckEditorLeader(9,leader)===false,'native refuses leader edit '+slot+'/'+leader);
 check(JSON.stringify([c.deckDraft,c.deckClearHistory])===before,'native preserves complete draft/history '+slot+'/'+leader);
}
for(const invalid of ['stale','unconfigured','no-draft']){
 const c=nativeContext();if(invalid==='unconfigured')c.configured=false;if(invalid==='no-draft')c.deckDraft=null;
 const before=JSON.stringify([c.deckDraft,c.deckClearHistory]);
 check(c.OnBetaGwentDeckEditorLeader(invalid==='stale'?8:9,21)===false,'invalid request rejected '+invalid);
 check(c.published===0&&JSON.stringify([c.deckDraft,c.deckClearHistory])===before,'invalid request has no effects '+invalid);
}
// Importing a composition may not silently change an existing deck's identity.
for(const [leader,faction,allowed]of [[11,2,true],[12,2,false],[21,4,false],[11,4,false]]){
 const c=nativeContext(),before=JSON.stringify(c.deckDraft);
 c.BetaGwentParseDeckExchange=()=>({valid:true,leader,faction,cards:[101],message:''});
 check(c.ExchangeParse(9,'BG1',{})===allowed,'existing import identity '+leader+'/'+faction);
 check(JSON.stringify(c.deckDraft)===before,'import validation does not mutate draft '+leader+'/'+faction);
 if(!allowed)check(c.collectionChecks===0&&c.replies.length===1&&!c.replies[0].accepted,'incompatible import refused before collection work '+leader+'/'+faction);
}
for(const leader of [11,12,21]){
 const c=nativeContext(null);c.BetaGwentParseDeckExchange=()=>({valid:true,leader,faction:leader===21?4:2,cards:[101]});
 check(c.ExchangeParse(9,'BG1',{})===true,'new import still chooses leader '+leader);
 check(c.deckDraft===null&&c.allocations===0,'import check allocates no slot '+leader);
 check(c.OnBetaGwentDeckCreate(9,leader)===true,'native creates with selected leader '+leader);
 check(c.deckDraft.leader===leader&&c.deckDraft.faction===(leader===21?4:2),'created identity matches choice '+leader);
 check(c.OnBetaGwentDeckCreate(c.revision,11)===false&&c.allocations===1,'cannot recreate open draft '+leader);
}
// Retained/forged AS closures must be harmless, without disabling the editor or discarding undo.
const a=vm.createContext({int:v=>v|0,ready:true,editingDeck:true,revision:7,editorState:state(),editorUndo:[{id:101}],editorPending:null,
 editorUndoPending:false,sent:[],rememberEditorFilters(){},editorCounts:()=>({101:2}),editorFeedbackPoint178:()=>({x:1,y:1}),
 editorFeedbackOrigin178:null,render(){}});
a.send=(event,args)=>a.sent.push([event,args]);
vm.runInContext(extract(board,'editorAction'),a);
for(const leader of [11,12,21]){
 const before=JSON.stringify([a.editorState,a.editorUndo,a.editorPending]);a.editorAction('OnBetaGwentDeckEditorLeader',leader)();
 check(a.sent.length===0&&a.ready,'AS sends no leader request '+leader);
 check(JSON.stringify([a.editorState,a.editorUndo,a.editorPending])===before,'AS keeps draft and history '+leader);
 a.ready=true;
}
// Creation remains a separate choice before the first native allocation.
Object.assign(a,{createDeckOpen178:true,selectingDecks:true,createFaction178:2,createLeader178:11,entryMode:1,
 ownedCopies:{11:1,12:1,21:1},editorFactionAvailable:f=>f===2,cardFaction:id=>id===21?4:2});
vm.runInContext(['createLeaderAction178','confirmDeckCreator178'].map(name=>extract(board,name)).join('\n'),a);
a.createLeaderAction178(12)();check(a.createLeader178===12,'creator permits another owned leader');
a.createLeaderAction178(21)();check(a.createLeader178===12,'creator rejects another faction');
a.sent=[];a.confirmDeckCreator178();a.confirmDeckCreator178();
check(a.sent.length===1&&a.sent[0][0]==='OnBetaGwentDeckCreate'&&a.sent[0][1][1]===12,'creator submits chosen leader once');
for(const name of ['drawBetaDeckEditor','drawDeckEditor']){
 const fn=extract(board,name);
 check(!fn.includes('OnBetaGwentDeckEditorLeader')&&!fn.includes('createLeaderAction178'),'no leader or faction mutation controls '+name);
 check(fn.includes('leaderOption(editorState.leader)')&&fn.includes('attachInspect('),'saved leader remains inspectable '+name);
}
const digest=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report={checks,failures,boardSha256:digest(boardPath),nativeSha256:digest(nativePath),actualProductionBodies:true,nativeGameplayTested:false};
if(process.argv[4])fs.writeFileSync(process.argv[4],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

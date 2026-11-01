// Run real editor AS callbacks: filtered result position and receipt lifetime.
'use strict';
const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict'),crypto=require('crypto');
const file=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
function extract(name){const start=source.indexOf('function '+name+'(');assert(start>=0,name);const open=source.indexOf('{',start);let end=open+1,depth=1;
 while(depth){depth+=(source[end]==='{')-(source[end]==='}');end++;}
 return source.slice(start,end).replace(/:\s*(?:Object|String|Function|void|int|uint|Number|Boolean|Array|Sprite|TextField)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');}
let checks=0;const failures=[];
function check(ok,name){checks++;if(!ok)failures.push(name);}
function context(){const c=vm.createContext({Math,Array,Object,String,Boolean,int:v=>v|0,
 ready:true,editingDeck:true,revision:17,serverRevision:17,renders:0,editorPage:4,editorScroll178:960,
 catalogPage:3,catalogScroll178:720,editorTier:0,editorType:0,editorFactionOnly:false,editorOwnedOnly:false,
 editorPosition:0,editorStrength:0,editorNewOnly:false,editorSearch:'',catalogSearch:'',searchDeadline:99,
 nameOpen:true,nameRevision:17,textPurpose:1,pendingTextAt:0,nameField:{text:'  Search  '},
 editorState:{slot:2,faction:4},editorCards:[{templateId:42,copies:1}],editorById:{},
 editorPending:null,editorUndo:[],editorUndoPending:false,editorBaseline:'old',editorName:'Deck',
 editorFlight:{id:42,amount:1,origin:{x:400,y:400}},editorFeedbackOrigin178:{x:400,y:400},
 BetaGwentTextLanguage:{protect(){}},
 render(){c.renders++;},closeNameInput(){c.nameOpen=false;},send(){},editName(){},
 rememberEditorFilters(){},restoreEditorFilters(){},clearDrag(){}});
 vm.runInContext(['editorOwnedToggle','editorFilterAction','editorExtraFilter','submitNameInput','beginDeckEditor'].map(extract).join('\n'),c);return c;}
function filterState(c){return JSON.stringify([c.editorTier,c.editorType,c.editorFactionOnly,c.editorOwnedOnly,c.editorPosition,c.editorStrength,c.editorNewOnly,c.editorSearch,c.editorPage,c.editorScroll178,c.renders]);}
for(const kind of ['tier','owned','position','strength','new','reset']){
 const c=context();const callback=kind==='tier'?c.editorFilterAction(8,4,true):kind==='owned'?c.editorOwnedToggle():c.editorExtraFilter(kind==='position'?1:kind==='strength'?2:kind==='new'?3:0);
 callback();check(c.editorPage===0&&c.editorScroll178===0,'changed '+kind+' filter starts at first result');check(c.renders===1,'changed '+kind+' filter renders once');
 if(kind==='tier')check(c.editorTier===8&&c.editorType===4&&c.editorFactionOnly,'requested tier/type/faction applied');
 if(kind==='owned')check(c.editorOwnedOnly,'ownership filter toggled');
 if(kind==='new')check(c.editorNewOnly,'new cards filter toggled');
 for(const guard of ['pending','left-editor','new-revision']){
  const c=context();const callback=kind==='tier'?c.editorFilterAction(8,4,true):kind==='owned'?c.editorOwnedToggle():c.editorExtraFilter(kind==='position'?1:kind==='strength'?2:kind==='new'?3:0);
  if(guard==='pending')c.ready=false;if(guard==='left-editor')c.editingDeck=false;if(guard==='new-revision')c.revision++;
  const before=filterState(c);callback();check(filterState(c)===before,kind+' ignores '+guard+' callback');
 }
}
for(const purpose of [1,2]){const c=context();c.textPurpose=purpose;c.submitNameInput();
 check((purpose===1?c.editorSearch:c.catalogSearch)==='Search','submitted search trims input');
 check((purpose===1?c.editorPage:c.catalogPage)===0&&(purpose===1?c.editorScroll178:c.catalogScroll178)===0,'submitted search resets visible results');
 check(c.renders===1,'submitted search renders once');
}
{const c=context();c.nameRevision=16;const before=filterState(c);c.submitNameInput();check(filterState(c)===before,'stale submitted search leaves filters unchanged');}
for(const [slot,faction]of [[2,4],[3,4],[2,8]]){const c=context();c.beginDeckEditor(18,slot,faction,200164,'Deck',25,4,6,true);
 check(c.editorFlight===null,'new authoritative snapshot clears old flight '+slot+'/'+faction);
 check(c.editorFeedbackOrigin178===null,'new snapshot clears stale pointer origin '+slot+'/'+faction);
}
{const c=context(),flight=c.editorFlight,origin=c.editorFeedbackOrigin178;c.beginDeckEditor(16,3,8,200164,'Old',25,4,6,true);
 check(c.editorFlight===flight&&c.editorFeedbackOrigin178===origin,'stale snapshot cannot consume current feedback');}
{const c=context();c.editorPending={id:42,origin:{x:99,y:77}};const pending=c.editorPending;c.beginDeckEditor(18,2,4,200164,'Deck',26,4,6,true);
 check(c.editorPending===pending&&c.editorPending.origin.x===99,'same-editor acknowledgement retains pending confirmed origin');}
const report={checks,failures,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

'use strict';
// Exercise the real acknowledgement/undo/drawing path before adding editor VFX.
// Host drawing objects are shims; no assertion claims native GFx acceptance.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..');
const source=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentBoard.as'),'utf8');
function extract(name){
 const at=source.indexOf('function '+name+'(');assert(at>=0,name);
 const open=source.indexOf('{',at);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(at,end)
  .replace(/:\s*(?:Object|String|Function|void|int|Number|Boolean|Array|Sprite|TextField|BetaGwentEditorValid095|BetaGwentEditorFx094)\b(?=\s*(?:[,)=;{]|in\b))/g,'')
  .replace(/for each\((.*?) in (.*?)\)/g,'for($1 of Object.values($2||{}))');
}
let checks=0;
function eq(actual,expected,label){assert.deepEqual(actual,expected,label);checks++;}
function Sprite(){this.children=[];this.addChild=child=>{this.children.push(child);return child;};}
const c=vm.createContext({Math,Array,Object,String,Boolean,Sprite,int:v=>Number(v)|0,skin:3,BETA_CARD_ASPECT:17.64/21.46,EDITOR_FLIGHT_MS:320,
 BetaGwentEditorFxData094:{MS:1000},BetaGwentEditorFx094:function(){this.available=true;},
 BetaGwentEditorValidData095:{MS:300},BetaGwentEditorValid095:function(){this.available=true;},BetaGwentUi138:{flashes:true},
 editorPending:null,editorState:{slot:2,faction:4},editorUndo:[],editorUndoPending:false,
 editorFlight:null,editorFeedbackOrigin178:null,editorCards:[],editorById:{},shelves178:{},shelfCards178:{},
 ready:true,editingDeck:true,revision:17,reducedMotion:false,editorName:'Example',deckListTop178:428,
 content:new Sprite(),animations:[],events:[],drawn:[],
 send(name,args){c.events.push({name,args:Array.from(args)});},rememberEditorFilters(){},
 editorSummary:()=>'',editorBetaButton(){},playDeckSlotFx096(){},uiSound(){},paintArt(tile,id,w,h){c.drawn.push({id,w,h});}
});
vm.runInContext(['editorCounts','editorFeedbackPoint178','editorCollectionCard094','editorFxPlan094','editorAction','settleEditorUndo','undoEditorChange','drawEditorFeedback'].map(extract).join('\n'),c);
const plain=v=>JSON.parse(JSON.stringify(v));
function counts(a,b=0){c.editorCards=[{templateId:42,copies:a,canAdd:a<3},{templateId:43,copies:b,canAdd:b<3}];c.editorById=Object.fromEntries(c.editorCards.map(x=>[x.templateId,x]));}
function reset(){
 Object.assign(c,{editorPending:null,editorState:{slot:2,faction:4},editorUndo:[],editorUndoPending:false,
  editorFlight:null,editorFeedbackOrigin178:null,ready:true,editingDeck:true,revision:17,reducedMotion:false,
  content:new Sprite(),animations:[],events:[],drawn:[],shelves178:{},shelfCards178:{}});counts(1);
}
function request(amount){c.editorAction('OnBetaGwentDeckEditorChange',42,amount)();}
function confirm(a,b=0){counts(a,b);c.settleEditorUndo();c.ready=true;}
for(const amount of [1,-1]){
 reset();c.editorFeedbackOrigin178={x:735,y:510};request(amount);
 eq(c.ready,false,'request waits for authoritative state');
 eq(c.editorFlight,null,'request itself produces no success animation');
 eq(c.events[0].args,[17,42,amount],'original revision and signed change sent');
 eq(plain(c.editorPending.origin),{x:735,y:510},'actual pointer origin retained');
 confirm(1+amount);
 eq(c.editorUndo.length,1,'only confirmed change enters undo history');
 eq(plain(c.editorFlight),{id:42,amount,origin:{x:735,y:510},valid095:false},'confirmed signed feedback');
 c.drawEditorFeedback();
 eq(c.drawn.length,1,'one confirmed card is drawn');
 eq(c.animations.length,1,'one flight is enqueued');
 eq(c.animations[0].toX,amount>0?182:922,'addition/removal uses corresponding pane destination');
 eq(c.animations[0].fromX,697,'flight starts at saved pointer');
 eq(c.editorFlight,null,'feedback consumed');
 c.drawEditorFeedback();c.settleEditorUndo();
 eq(c.animations.length,1,'redraw and duplicate completion do not replay confirmation');
}
for(const scenario of ['reject','other-card','wrong-delta','slot','faction']){
 reset();request(1);
 if(scenario==='reject')counts(1);
 if(scenario==='other-card')counts(2,1);
 if(scenario==='wrong-delta')counts(3);
 if(scenario==='slot'){counts(2);c.editorState.slot=3;}
 if(scenario==='faction'){counts(2);c.editorState.faction=8;}
 c.settleEditorUndo();c.drawEditorFeedback();
 eq(c.editorFlight,null,scenario+' has no success feedback');
 eq(c.animations.length,0,scenario+' has no flight');
 eq(c.editorUndo.length,0,scenario+' cannot enter undo history');
 eq(c.editorPending,null,scenario+' consumes pending request');
}
for(const property of ['revision','ready','editingDeck']){
 reset();const action=c.editorAction('OnBetaGwentDeckEditorChange',42,1);
 if(property==='revision')c.revision=18;else c[property]=false;
 action();eq(c.events.length,0,property+' guard sends no request');
 eq(c.editorPending,null,property+' guard creates no confirmation');
}
reset();request(1);confirm(2);c.drawEditorFeedback();c.animations=[];c.undoEditorChange();
eq(c.events.at(-1).args,[17,42,-1],'undo requests actual inverse change');
eq(c.editorFlight,null,'undo request waits for confirmation');
confirm(1);eq(c.editorUndo.length,0,'confirmed undo pops history');
eq(c.editorFlight.amount,-1,'confirmed undo uses removal feedback');
c.drawEditorFeedback();eq(c.animations.length,1,'confirmed undo has exactly one flight');
reset();request(1);confirm(2);c.drawEditorFeedback();c.animations=[];c.undoEditorChange();confirm(2);
eq(c.editorUndo.length,0,'rejected inverse invalidates history');
eq(c.editorFlight,null,'rejected undo has no success feedback');
for(const reduced of [true,false]){
 reset();c.reducedMotion=reduced;request(1);confirm(2);c.drawEditorFeedback();
 eq(c.animations.length,reduced?0:1,'reducedMotion controls confirmed feedback');
 eq(c.editorUndo.length,1,'accessibility setting does not alter successful edit');
 eq(c.editorFlight,null,'suppressed feedback is consumed, not deferred');
}
for(const event of ['OnBetaGwentDeckEditorClear','OnBetaGwentDeckEditorRestore']){
 reset();if(event.endsWith('Restore'))c.editorUndo=[{before:{42:2,43:0}}];
 c.editorAction(event)();confirm(event.endsWith('Restore')?2:0);c.drawEditorFeedback();
 eq(c.animations.length,0,'bulk operation does not impersonate a single-card effect');
 eq(c.editorPending,null,'bulk acknowledgement consumed');
}
reset();c.shelves178.deck={columns:1,rowHeight:40,offset:80,height:200};c.shelfCards178.deck=[0,1,42,3].map(templateId=>({templateId}));
eq(plain(c.editorFeedbackPoint178(42,'deck')),{x:220,y:448},'visible deck row respects independent scrolling');
eq(plain(c.editorFeedbackPoint178(0,'deck')),{x:220,y:660},'offscreen deck row uses pane fallback');
c.shelves178.collection={columns:6,rowHeight:186,offset:186,height:622};c.shelfCards178.collection=Array.from({length:12},(_,templateId)=>({templateId}));
// 0.9.6: the real Beta tile centre (480+18+col*156+64, face 128 x 156).
eq(plain(c.editorFeedbackPoint178(7,'collection')),{x:718,y:382},'visible collection row respects grid and scrolling');
eq(plain(c.editorFeedbackPoint178(1,'collection')),{x:960,y:620},'offscreen collection uses pane fallback');
const canonical=fs.readFileSync(path.join(root,'BetaGwent/ui/src/BetaGwentBoard.as'));
for(const folder of ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']){
 const raw=fs.readFileSync(path.join(root,'BetaGwent/ui',folder,'BetaGwentBoard.as'));
 eq(raw.equals(canonical),true,'canonical mirrors match '+folder);
}
eq(canonical.subarray(0,3).toString('hex'),'efbbbf','Board BOM preserved');
eq(/(?<!\r)\n/.test(canonical.toString()),false,'Board CRLF preserved');
// Beta AUIDeckStatsWidget: only ADD reaching exactly 25, after acknowledgement.
for(const scenario of ['add25','add24','add26','remove25','rejected','sameRevision','otherSlot','otherLeader','reduced','flashesOff','duplicate']){
 reset();c.BetaGwentUi138.flashes=true;c.editorState.leader=12;
 const amount=scenario==='remove25'?-1:1;
 const total=scenario==='add24'?23:scenario==='add26'?25:scenario==='remove25'?26:24;
 counts(1,total-1);request(amount);
 eq(c.animations.length,0,'no speculative flash '+scenario);
 if(scenario!=='sameRevision')c.revision++;
 if(scenario==='otherSlot')c.editorState.slot++;
 if(scenario==='otherLeader')c.editorState.leader++;
 if(scenario==='reduced')c.reducedMotion=true;
 if(scenario==='flashesOff')c.BetaGwentUi138.flashes=false;
 confirm(scenario==='rejected'?1:1+amount,total-1);c.drawEditorFeedback();
 const flashes=c.animations.filter(x=>x.editorValid095);
 eq(flashes.length,['add25','duplicate'].includes(scenario)?1:0,'exact source trigger '+scenario);
 if(flashes.length){eq(flashes[0].duration,300,'source lifetime');eq([flashes[0].toX,flashes[0].toY],[232,214],'stats widget origin');}
 if(scenario==='duplicate'){c.settleEditorUndo();c.drawEditorFeedback();eq(c.animations.filter(x=>x.editorValid095).length,1,'duplicate acknowledgement does not replay flash');}
}
console.log(JSON.stringify({checks,actualActionScript:true,confirmationBoundary:true,nativeGameTested:false}));

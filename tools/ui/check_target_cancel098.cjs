'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),crypto=require('crypto');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const file=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
vm.runInContext(['setRequestCancel098','cancelPlayHistory098','canCancelTargetRequest098','onStageClick','onStageMouseDown','isInspectMouse','controllerCommand','onKey'].map(n=>H.extract(n,source).replace(/:\s*KeyboardEvent\b/g,'').replace(/\bis TextField\b/g,'instanceof TextField')).join('\n'),c);
let checks=0;const failures=[],sent=[];const check=(v,n)=>{checks++;if(!v)failures.push(n);};let inspections=0,closed=0,cleared=0;
Object.assign(c,{RIGHT_CLICK_EVENT:'rightClick',replayMouse:()=>false,sendRequest:n=>sent.push(n),clearDrag:()=>cleared++,
 closeCardDetail:()=>closed++,openCardDetail:()=>inspections++,clearPlacementGhost(){},render(){},canFinishRequest:()=>false,
 isChoiceTable:()=>false,isMulliganHand:()=>false,controller:{active:false,getFocus:()=>null},inspection:null});
function reset(){sent.length=0;inspections=closed=cleared=0;Object.assign(c,{rightMouseAt:-1000,ready:true,playing:false,detailOpen:false,pileOpen:false,
 controllerMenuOpen:false,nameOpen:false,mulliganConfirm:false,requestId:5,requestPlayer:1,requestCancel098:true,
 hoveredCard:null,hoveredDetail:null,leaderRow:false,selected:0,suppressClickUntil:0,introStart:0,editorDragId178:0,
 effectGallery:false,browsingCatalog:false,kegOpen:false,createDeckOpen178:false,editingDeck:false,selectingDecks:false,
 tutorialPage:-1,entryMode:0,dragId:0,skin:3,flags:0,editorExitPrompt:false,heldKey:0,lastKeyTime:0});}
const event=(type,buttonIdx)=>({type,buttonIdx,keyCode:27,preventDefault(){},stopImmediatePropagation(){}});
for(const [type,button]of [['rightClick',undefined],['c',1],['rightMouseDown',undefined]]){
 reset();if(type==='rightMouseDown')c.onStageMouseDown(event(type,button));else c.onStageClick(event(type,button));
 check(sent.length===1&&sent[0]==='OnBetaGwentRequestAbort','RMB cancels on native event '+type);
 check(inspections===0,'RMB does not open card while cancelling '+type);
 c.onStageClick(event('rightClick'));check(sent.length===1,'paired native right-click is debounced '+type);
}
reset();c.hoveredCard={id:10};c.onStageClick(event('c',1));check(sent[0]==='OnBetaGwentRequestAbort'&&inspections===0,'targeting RMB takes priority over card inspection, like Beta');
for(const blocked of ['playing','detailOpen','pileOpen','controllerMenuOpen','nameOpen','mulliganConfirm']){
 reset();c[blocked]=true;check(!c.canCancelTargetRequest098(),'overlay/replay blocks cancel '+blocked);
}
for(const field of ['ready','requestCancel098']){reset();c[field]=false;c.onStageClick(event('rightClick'));check(!sent.length,'no unauthorised cancel '+field);}
reset();c.requestPlayer=2;check(!c.canCancelTargetRequest098(),'opponent request cannot cancel');
reset();c.requestId=0;check(!c.canCancelTargetRequest098(),'no current request cannot cancel');
reset();c.controllerCommand('back');check(sent[0]==='OnBetaGwentRequestAbort','controller back cancels authoritative target request');
reset();c.onKey(event('key'));check(sent[0]==='OnBetaGwentRequestAbort','Escape cancels authoritative target request');
reset();c.requestCancel098=false;c.hoveredCard={id:10};c.onStageClick(event('rightClick'));check(inspections===1&&!sent.length,'ordinary RMB inspection retained');
reset();c.detailOpen=true;c.onStageClick(event('rightClick'));check(closed===1&&!sent.length,'RMB closes detail before underlying targeting');
c.incoming={revision:12};c.setRequestCancel098(11,true);check(!c.incoming.requestCancel098,'stale capability update rejected');
c.setRequestCancel098(12,true);check(c.incoming.requestCancel098===true,'current capability accepted');
c.setRequestCancel098(12,false);check(c.incoming.requestCancel098===false,'capability revoked after commit');
c.actionHistory=[{kind:1,actor:{id:12},start:[3,4]},{kind:1,actor:{id:11},start:[1,2]}];c.cancelPlayHistory098(12);
check(c.actionHistory.length===1&&c.actionHistory[0].actor.id===11&&c.historyScores[0]===3,'authoritative cancellation removes tentative history and preserves parent');
c.cancelPlayHistory098(12);check(c.actionHistory.length===1,'duplicate history cancellation cannot remove an older unrelated play');
c.actionHistory=[{kind:2,actor:{id:99}},{kind:1,actor:{id:22},start:[8,9]},{kind:1,actor:{id:11}}];c.cancelPlayHistory098(22);
check(c.actionHistory.length===1&&c.actionHistory[0].actor.id===11&&c.historyScores[1]===9,'tentative play and its early reactions disappear together');
const report={checks,failures,sourceSha256:crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

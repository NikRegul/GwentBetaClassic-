'use strict';
// Execute shipped AS aiming: choices in hand/piles have no board target arrow.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const root=path.resolve(__dirname,'../..');let checks=0;
for(const file of ['BetaGwent/ui/src/BetaGwentBoard.as','tools/features091/BetaGwentBoard_classic093.as']){
 const source=fs.readFileSync(path.join(root,file),'utf8'),at=source.indexOf('function updateAimPreview('),open=source.indexOf('{',at);let end=open+1,depth=1;
 for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 const method=source.slice(at,end).replace(/:\s*(?:Boolean|String|void|uint|int|Array|Number|Object)\b/g,'');
 const arrows=[],clears=[];
 const c=vm.createContext({hoveredCard:null,controller:{active:false},detailOpen:false,pileOpen:false,playing:false,editingDeck:false,selectingDecks:false,browsingCatalog:false,
  requestId:12,requestKind:2,requestPlayer:1,requestSourceId:9,requestSourceTemplate:152213,rowRequest:false,selected:0,revision:4,aimKey:'old-arrow',int:Math.trunc,
  aimLayer:{graphics:{clear:()=>clears.push(true)}},canDirectTarget:()=>false,canPlacePending:()=>false,findRequestCard:()=>({id:1}),
  aimSourcePose091:()=>({x:800,y:100,width:80,height:120}),drawCueArrow:(...args)=>arrows.push(args),displayedCards:{}});
 vm.runInContext(method,c);
 const run=(zone,player,template,controller=false,direct=false)=>{
  c.requestSourceTemplate=template;c.requestPlayer=player;c.requestId=direct?0:12;c.canDirectTarget=()=>direct;
  const card={id:1,zone};c.hoveredCard=controller?null:card;c.controller={active:controller,getFocus:()=>({card})};c.displayedCards={1:{...card,x:100,y:800,width:80,height:120}};
  c.aimKey='old-arrow';arrows.length=0;const before=clears.length;c.updateAimPreview();assert.equal(clears.length,before+1,'Stale arrow cleared');checks++;
  return arrows.length;
 };
 for(const controller of [false,true])for(const template of [152213,152103,112211,162210]){
  for(const zone of [8,16,32,64])for(const player of [1,2]){assert.equal(run(zone,player,template,controller),0,'Hand/pile offer has no arrow');checks++;}
  for(const zone of [1,2,4]){assert.equal(run(zone,2,template,controller),0,'Opponent request never aims from human cursor');checks++;assert.equal(run(zone,1,template,controller),1,'Human board target retains arrow');checks++;}
 }
 for(const zone of [1,2,4]){assert.equal(run(zone,1,113301,false,true),1,'Direct board targeting retained');checks++;}
 for(const zone of [8,16,32]){assert.equal(run(zone,1,113301,false,true),0,'Off-board direct choice has no arrow');checks++;}
}
const copies=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg'].map(p=>fs.readFileSync(path.join(root,'BetaGwent/ui',p,'BetaGwentBoard.as')));
assert(copies.every(b=>b.equals(copies[0])&&b.subarray(0,3).equals(Buffer.from([239,187,191]))&&!b.toString().replaceAll('\r\n','').includes('\n')));checks++;
console.log(JSON.stringify({checks,actualActionScript:true,svanrigeHandArrow:false,boardTargetArrow:true,nativeGameplayVerified:false}));

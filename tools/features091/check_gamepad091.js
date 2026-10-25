'use strict';
// Reuse the established actual-AS navigation harness, adding release regressions.
const fs=require('fs'),path=require('path'),vm=require('vm');
const root=path.resolve(__dirname,'../..');let total=0;
for(const platform of ['classic','nextgen']){
 const dir=path.resolve(process.argv[2]||'BetaGwent/build-inputs/ui',platform,'ui/src');
 let harness=fs.readFileSync(path.join(root,'tools/ui/check_controller126.js'),'utf8');
 for(const name of ['BetaGwentController.as','BetaGwentBoard.as'])
  harness=harness.replaceAll("'BetaGwent/ui/src/"+name+"'",JSON.stringify(path.join(dir,name)));
 const tests=`
const leftPile=node('leftPile',0,750,'control');leftPile.pile=true;
const rightPile=node('rightPile',1700,750,'control');rightPile.pile=true;
const middleHand=node('middleHand',800,950,'hand'),endHand=node('endHand',1100,950,'hand');
setup([leftPile,middleHand,endHand,rightPile],middleHand,'battle');
check(move(39)===endHand,'right visits the next hand card before a pile');
check(move(39)===rightPile,'right edge of hand reaches right pile');
setup([leftPile,middleHand,endHand,rightPile],middleHand,'battle');
check(move(37)===leftPile,'left edge of hand reaches left pile');
const boardUnit=node('boardUnit',800,400,'card',1,2);
setup([leftPile,boardUnit,rightPile],boardUnit,'inspect');
check(move(39)===rightPile,'board row edge reaches right pile');
setup([leftPile,boardUnit,rightPile],boardUnit,'target');boardUnit.tag='target';
check(move(39)===boardUnit,'target selection never jumps to a pile');
boardUnit.tag='card';
function callbackAfter(marker,event=''){
 let a=board.indexOf(marker);check(a>=0,'hover marker exists');
 if(event)a=board.indexOf(event,a);
 const b=board.indexOf('function(e:MouseEvent):void{',a),open=board.indexOf('{',b);
 let d=1,i=open+1;for(;d;i++){if(board[i]==='{')d++;if(board[i]==='}')d--;}
 return board.slice(open+1,i-1).replace(/:(?:String|Object|void|int|uint|Number|Array|Boolean|Sprite|Event|TextField|MouseEvent|Function|Rectangle)\\b(?=\\s*(?:[,)=;{]|in\\b))/g,'');
}
const handBlock=board.indexOf('var enabled:Boolean=canInspectPile()');
check(handBlock>=0&&board.includes('controller.markPile(pile)'),'pile controls marked for navigation');
const h=vm.createContext({controller:{active:true},dragging:false,detailOpen:false,glow:{},
 uiTween(){},setHandHover(){throw Error('idle cursor reset hand focus');},
 c:{side:1,zone:8},showPileCard(){h.pileReads++;},showMulliganCard(){h.mulliganReads++;},pileReads:0,mulliganReads:0});
const bind=board.indexOf('// With a gamepad the idle cursor');
check(bind>=0,'hand hover guard exists');
// Execute actual event bodies. Controller-active paths must return before mutating preview state.
const over=callbackAfter('private function attachInspect','p.addEventListener(MouseEvent.ROLL_OVER');
const out=callbackAfter('private function attachInspect','p.addEventListener(MouseEvent.ROLL_OUT');
vm.runInContext('(function(){'+over+'})();',h);
vm.runInContext('(function(){'+out+'})();',h);
check(h.hoveredCard===undefined,'idle mouse cannot replace controller preview');
const pile=callbackAfter('private function pileCardInspect');
const mulligan=callbackAfter('private function attachMulliganReading');
h.detail={};vm.runInContext('(function(){'+pile+'})();(function(){'+mulligan+'})();',h);
check(h.pileReads===0&&h.mulliganReads===0,'idle mouse cannot replace pile/mulligan preview');
h.controller.active=false;vm.runInContext('(function(){'+pile+'})();(function(){'+mulligan+'})();',h);
check(h.pileReads===1&&h.mulliganReads===1,'mouse previews still work when controller is inactive');
`;
 harness=harness.slice(0,harness.indexOf('const report='))+tests+'\nchecks;';
 const ctx=vm.createContext({require,console,process,vm});
 const checks=vm.runInContext(harness,ctx);total+=checks;
 console.log(platform,checks,'actual-AS controller/hover checks passed');
}
fs.writeFileSync(process.argv[3]||path.resolve(process.argv[2]||'BetaGwent/build-inputs/ui','gamepad-tests.json'),JSON.stringify({checks:total,actualActionScript:true,nativeControllerTested:false},null,2));

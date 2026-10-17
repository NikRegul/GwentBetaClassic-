// Execute the actual startup methods with a simulated native bridge.
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const path='D:/w3mod/BetaGwent/build/classic081-boot-fix4/ui/src/BetaGwentBoard.as';
const source=fs.readFileSync(path,'utf8');
function method(name){
 let p=source.indexOf('function '+name+'('),begin=source.indexOf('{',p),end=begin+1,depth=1;
 assert(p>=0,name);while(depth){if(source[end]==='{')depth++;if(source[end]==='}')depth--;end++;}
 return source.slice(p,end).replace(/:(?:String|Array|void|Event|Error|int|Boolean)\b/g,'').replace(/var (\w+):(?:String|Array|int|Boolean)/g,'var $1');
}
let checks=0;
function check(value,label){assert(value,label);checks++;}
function fixture(fail=false,delay=false){
 const c=vm.createContext({startupAttached:false,startupError:'',connected:false,stage:{},keyboardStage:null,
  events:[],sequence:[],_NATIVE_callGameEvent:null,current:0,playing:false,soundEnabled:true,voiceEnabled:true,
  registrationName:()=> 'DeckBuilder',addEventListener:()=>{},removeEventListener:()=>{},bridgeClock:()=>0,
  Event:{ENTER_FRAME:'frame',ADDED_TO_STAGE:'added',DEACTIVATE:'deactivate'},
  MouseEvent:{MOUSE_MOVE:'move',MOUSE_UP:'up',CLICK:'click',MOUSE_DOWN:'down'},KeyboardEvent:{KEY_DOWN:'kd',KEY_UP:'ku'},RIGHT_CLICK_EVENT:'right',
  onAdded:null,waitForBridge:null,onKey:()=>{},onKeyUp:()=>{},onDragMove:()=>{},onReplayMouseUp:()=>{},onDragEnd:()=>{},onReplayDeactivate:()=>{},onStageClick:()=>{},onStageMouseDown:()=>{},
  controller:{bind(){c.sequence.push('bind');if(fail)throw Error('simulated input error');}},
  changeSkin:()=>c.sequence.push('skin'),render:()=>c.sequence.push('render'),trace:()=>{},
 });
 c.stage.addEventListener=()=>{};
 c.native=function(event,args){check(this._NATIVE_callGameEvent===c.native,'native receiver owns the callback');c.events.push([event,args]);};
 c.ExternalInterface={available:false,call(name,menu,root){c.sequence.push('register');check(name==='registerMenu'&&menu==='DeckBuilder','Classic registration parameters');if(!delay)root._NATIVE_callGameEvent=c.native;}};
 vm.runInContext(['onAdded','waitForBridge','send'].map(method).join('\n'),c);
 return c;
}
let c=fixture();c.onAdded(null);
check(c.sequence.join(',')==='register,bind,skin,render','register before input and artwork');
c.onAdded(null);check(c.sequence.filter(x=>x==='register').length===1,'stage reentry does not register twice');
c.waitForBridge(null);c.waitForBridge(null);
check(c.events.map(e=>e[0]).join(',')==='OnBetaGwentControllerTrace,OnConfigUI,OnBetaGwentAudioSettings','one handshake with trace and settings');
c=fixture(true);c.onAdded(null);c.waitForBridge(null);
check(c.events.at(-1)[0]==='OnBetaGwentBoardClose','startup failure closes the paused menu');
check(!c.events.some(e=>e[0]==='OnConfigUI'),'failed startup does not configure the game');
check(c.events[0][1][3].includes('simulated input error'),'startup failure is passed to the real WS log event');
c=fixture(false,true);c.onAdded(null);c.waitForBridge(null);check(c.events.length===0,'wait for delayed native injection');
c._NATIVE_callGameEvent=c.native;c.waitForBridge(null);check(c.connected,'delayed native injection completes handshake');
console.log(JSON.stringify({checks,actualActionScriptStartupMethods:true,nativeGameplayVerified:false}));

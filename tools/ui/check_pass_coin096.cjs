'use strict';
// 0.9.6 Beta pass-hold coin: source curves (CoinVisualsControl in level8) and wiring.
const fs=require('fs'),vm=require('vm'),path=require('path');
const ui=process.argv[2]||'BetaGwent/ui/src';
const fx=fs.readFileSync(path.join(ui,'BetaGwentPassCoin096.as'),'utf8'),board=fs.readFileSync(path.join(ui,'BetaGwentBoard.as'),'utf8'),pad=fs.readFileSync(path.join(ui,'BetaGwentController.as'),'utf8');
let checks=0;const failures=[];const check=(ok,label)=>{checks++;if(!ok)failures.push(label);};
const constant=n=>JSON.parse(fx.match(new RegExp('const '+n+':Array=([^;]+);'))[1]);
const start=fx.indexOf('public static function curve(');let end=fx.indexOf('{',start)+1,d=1;while(d){d+=(fx[end]==='{')-(fx[end]==='}');end++;}
const c=vm.createContext({Math});vm.runInContext(fx.slice(start,end).replace('public static function','function').replace(/:\s*(Array|Number|int)(?=\s*[,)=;{])/g,''),c);
const FILL=constant('FILL'),SHAKE=constant('SHAKE'),near=(a,b,e=1e-3)=>Math.abs(a-b)<e;
check(near(c.curve(FILL,0),0)&&near(c.curve(FILL,.65),1)&&near(c.curve(FILL,1),1,1e-5),'fill reaches 1 at 65% of the hold and stays');
check(near(c.curve(FILL,.325),.5,.01),'fill is linear before 65% (slopes 1/0.65)');
check(c.curve(SHAKE,.6)<.01&&c.curve(SHAKE,.8)>.95&&c.curve(SHAKE,.99)<.6,'shake starts after 61.5%, peaks, settles at the end');
check(/355\*fill/.test(fx)&&/HEAD_R:Number=55/.test(fx),'effect root turns 355 x fill on the 55 px source circle');
check(/hold>=0\.97&&!endPlayed/.test(fx),'EndGlow once at 97%');
check(/acc\.mist\+=dt\*50/.test(fx)&&/acc\.sparks\+=dt\*100/.test(fx)&&/acc\.flare\+=dt\*8/.test(fx),'source emission rates');
check(board.includes('updatePassCoin096(now);')&&board.includes('passCoinSprite096=coin;')&&board.includes('controller.passHoldProgress()'),'mouse, P and pad Y drive the same coin effect');
check(!/passRing\.graphics\.lineStyle\(6,0xEAD7A0/.test(board),'old drawn ring removed');
check(/public function passHoldProgress\(\):Number/.test(pad),'controller exposes the Y hold');
check(board.includes('if(hold>=.1&&passSound096==0){passSound096=1;')&&board.includes('[passLastHold096>=.97?2:0]'),'StartPassing above 10 %, PassingConfirmed at the end, stop on early release');
const wsPath=[path.join(ui,'../../development/scripts/game/betagwent/duelAudio.ws'),'BetaGwent/development/scripts/game/betagwent/duelAudio.ws'].find(f=>fs.existsSync(f));const ws=fs.readFileSync(wsPath,'utf8');
check(ws.includes('"bg79_fx_2977021572"')&&ws.includes('"bg79_fx_3893297074"')&&ws.includes('"bg79_fx_2977021572_stop"'),'WS posts the Beta coin events');
const report={checks,failures,actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

'use strict';
const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const root=path.resolve(__dirname,'../..'),build=path.resolve(root,process.argv[2]||'BetaGwent/build/release082-rc3');let checks=0;
function fn(s,name){const a=s.indexOf('function '+name+'('),b=s.indexOf('{',a);assert(a>=0,name);let n=1,i=b+1;for(;n;i++){if(s[i]==='{')n++;if(s[i]==='}')n--;}
 return s.slice(a,i).replace(/:(?:DisplayObject|String|Function|Object|Rectangle|void|int|Number|Array|Boolean|Event)\b(?=\s*(?:[,)=;{]|in\b))/g,'').replace(/for each\((.*?) in (.*?)\)/g,'for($1 of $2)');}
function rect(x,y,w,h){return {x,y,width:w,height:h,clone(){return rect(x,y,w,h);}};}
function host(source){const c=vm.createContext({Math,Number,owner:{},now:1000,int:v=>v|0,movementAt:-1000,navigationColumn:NaN,editorReturnKey:'',dirty:false,currentMode:'editor',saved:{},focus:null,lastRect:null,lastKey:'',events:[],nodes:[],shelves:{},autoPicked:false,
 getTimer(){return c.now;},state(){return {mode:'editor',preferred:'card',shelves:c.shelves,accept:true};},candidates(){return c.nodes;},invoke(name,node){c.events.push({name,node});},trace(){}});
 vm.runInContext(['getFocus','select','navigationLane','gridWrap','editorFooter','navigate','activate'].map(n=>fn(source,n)).join('\n'),c);return c;}
for(const platform of ['nextgen','classic']){
 const source=fs.readFileSync(path.join(build,platform,'ui/src/BetaGwentController.as'),'utf8');
 for(const pane of ['deck','collection']){
  const c=host(source),x=pane==='deck'?80:500,columns=pane==='deck'?1:5;
  c.shelves[pane]={columns,count:150,rowHeight:200,height:440,offset:0};
  const a={key:'a',tag:'card',rect:rect(x,320,150,180),card:{shelfPane:pane,shelfIndex:0}},b={key:'b',tag:'card',rect:rect(x,520,150,180),card:{shelfPane:pane,shelfIndex:columns}};
  let saves=0;const save={key:'save',tag:'control',rect:rect(474,1002,240,48),action(){saves++;}},cancel={key:'cancel',tag:'control',rect:rect(1418,1002,240,48),action(){}};
  c.nodes=[a,b,save,cancel];c.focus=a;c.navigate(40);assert(c.focus===b);checks++;
  c.now+=100;c.navigate(40);assert(c.focus===save&&!c.events.some(e=>e.name==='shelfSelect'));checks++;
  c.activate();assert(saves===1);checks++;
  c.now+=100;c.navigate(38);assert(c.focus===b);checks++;
  c.focus=b;c.shelves[pane].count=columns+1;c.now+=100;c.navigate(40);assert(c.focus===save);checks++;
  // Other editor actions remain reachable horizontally from Save.
  c.now+=100;c.navigate(39);assert(c.focus===cancel);checks++;
 }
 const c=host(source);const save={key:'save',tag:'control',rect:rect(474,1002,240,48),action(){}};c.nodes=[save];c.focus=save;c.navigate(38);assert(c.focus===save);checks++;
}
const report={checks,actualActionScript:true,visibleEdgeReachesSave:true,confirmSaves:true,nativeGamepadVerified:false};fs.writeFileSync(path.join(build,'editor-navigation-tests.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));

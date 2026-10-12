// Exercise the real finish eligibility and event callback used by mouse, F and pad.
'use strict';
const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync('BetaGwent/ui/src/BetaGwentBoard.as','utf8');
function extract(name){
 const start=source.indexOf('function '+name+'('),open=source.indexOf('{',start);let depth=1,end=open+1;
 if(start<0)throw Error(name);for(;depth;end++){if(source[end]==='{')depth++;if(source[end]==='}')depth--;}
 return source.slice(start,end).replace(/:(String|Function|Object|void|int|Number|Array|Boolean)\b(?=\s*(?:[,)=;{]|in\b))/g,'');
}
const c=vm.createContext({});
vm.runInContext(`var pileOpen=false,detailOpen=false,ready=true,playing=false,requestId=12,revision=9,requestPlayer=1,requestKind=1,requestFinish=true,rowRequest=false,leaderRow=false,rowMode=14,requestMax=2,mulligan=false;
var sent=[];function isMulliganHand(){return mulligan;}function send(n,args){sent.push({name:n,args:args});}
`+extract('canFinishRequest')+'\n'+extract('isOptionalMultiChoice')+'\n'+extract('sendRequest')+'\n'+extract('requestAction'),c);
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
check(c.canFinishRequest()&&c.isOptionalMultiChoice(),'zero choices allow finish');
const old=c.requestAction('OnBetaGwentRequestFinish');old();check(c.sent.length===1&&c.sent[0].args[1]===12&&!c.ready,'finish action sends current request and waits');
c.requestId=13;c.ready=true;old();check(c.sent.length===1,'stale finish callback cannot finish new request');
check(c.canFinishRequest()&&c.isOptionalMultiChoice(),'updated partial request remains finishable');
c.requestFinish=false;check(!c.canFinishRequest()&&!c.isOptionalMultiChoice(),'mandatory follow-up has no finish');
c.requestFinish=true;c.ready=false;check(!c.canFinishRequest(),'busy input cannot finish');
c.ready=true;c.playing=true;check(!c.canFinishRequest(),'replay cannot finish');
c.playing=false;c.pileOpen=true;check(!c.canFinishRequest(),'open pile takes focus');
c.pileOpen=false;c.mulligan=true;check(!c.isOptionalMultiChoice(),'mulligan retains its own finish caption');
for(const name of ['drawBetaActions','drawBetaAbilityChoices','drawChoices']){
 const body=extract(name);check(body.includes('isOptionalMultiChoice()')&&body.includes('Завершить выбор'),name+' uses consistent finish caption');
}
const english=JSON.parse(fs.readFileSync('data/beta924/design/english89.json','utf8'));
check(english['Завершить выбор']==='Finish selection','English finish caption exists');
const report={checks,actualActionScript:true,nativeMouseAndControllerTested:false};
fs.writeFileSync('docs/evidence/optional-ui124.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));

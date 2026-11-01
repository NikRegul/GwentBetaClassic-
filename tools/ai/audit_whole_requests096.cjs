'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {createRuntime,stateFromSession,basePersonality}=require('./beta_js092/session.cjs'),{BetaChoiceHandlers}=require('./beta_js092/choices.cjs');
const rules=path.resolve(process.argv[2]),rt=createRuntime(rules),{fixture,add}=require('./audit_fixture095.cjs')(rt);
const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const typed=new Function(code+'\nreturn {choices:()=>new CBetaOriginalChoiceHandlers(),node:()=>new CBetaOriginalNode(),record:()=>new CBetaOriginalChoiceRecord()};')();
let checks=0;const failures=[],cases=[],check=(v,s)=>{checks++;if(!v)failures.push(s);};
for(const tid of [162208,200169])for(const side of [1,2])for(const count of [1,2,4]){
 const label=tid+'/'+side+'/'+count,g=fixture(side,49001+side);g.mulliganReactions=true;for(let i=0;i<count;i++)add(g,132209,i%2?3-side:side,1,i,20,3);
 const source=add(g,tid,side,8,0);check(g.Play(side,source.Snapshot().instanceId,2),label+' real play');g.FlushEffects();
 const h=new BetaChoiceHandlers(rt,basePersonality()),a={game:g,executingPlayerId:side,choiceRecords:[],choiceCursor:0,handlerScore:0},b=typed.node();b.game=rt.cloneSession(g);b.executingPlayerId=side;
 const t=typed.choices();
 try{
  const r=h.describe(a),s=t.Describe(b);check(!t.failed,label+' typed Describe supported');check(r.kind==='targets'&&s.kind==='targets',label+' source request-kind');
  check(r.min===Math.min(2,count)&&s.minimum===r.min&&s.maximum===r.max&&r.max===Math.min(2,count),label+' entire required source target set');
  const chosen=r.items.slice(0,r.max),record={source:tid,kind:'targets',hint:r.hint,chosen};a.choiceRecords=[record];
  const tr=typed.record();tr.source=tid;tr.kind='targets';tr.sourceHint=r.hint;tr.chosen=s.items.slice(0,r.max);b.choiceRecords=[tr];b.choiceCursor=0;
  const randomBefore=g.random.DrawCount();
  for(let n=0;n<chosen.length;n++){h.request(a);t.Request(b);check(!t.failed,label+' typed continuation '+n);check(JSON.stringify(stateFromSession(g))===JSON.stringify(stateFromSession(b.game)),label+' identical state after each stored choice '+n);}
  check(!g.IsPending()&&!b.game.IsPending(),label+' whole set completed');check(g.random.DrawCount()===randomBefore,label+' stored decisions consume no live RNG');cases.push({id:tid,side,count});
 }catch(e){failures.push({case:label,error:e.stack});}
}
const report={schema:1,fingerprint:rt.fingerprint,checks,failures,cases,scope:'Both seats and 1/2/4 candidates: common Egan/Radovid target set accepted by JS and translated WS, cooperative stored continuations identical. No strength claim.'};
if(process.argv[3]){assert(!fs.existsSync(process.argv[3]));fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');}console.log(JSON.stringify({checks,failures:failures.length,firstFailures:failures.slice(0,5),fingerprint:rt.fingerprint}));if(failures.length)process.exitCode=1;

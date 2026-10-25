'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js');
const [candidate,baseline,casesFile,output]=process.argv.slice(2).map(p=>path.resolve(p));
const cases=JSON.parse(fs.readFileSync(casesFile,'utf8')).publicModels;
const fixture=fs.readFileSync(path.join(__dirname,'check_consume_self.js'),'utf8').split('Host.strength=4;')[1].split('// Alone:')[0];
const functions=fs.readFileSync(path.join(__dirname,'check_planning097.js'),'utf8').split("vm.runInContext('Host.strength=4;'+fixture+String.raw` ".trim())[1].split('const play=')[0];
function evaluate(dir){const {context:c,manifest}=load(dir);c.cases=cases;
 vm.runInContext('Host.strength=4;'+fixture+functions,c);
 return {fingerprint:manifest.fingerprint,rows:vm.runInContext(`(()=>{
 const rows=[];for(const strength of [2,3,4]){Host.strength=strength;Host.matchStrength=[strength,strength];
 for(let i=0;i<cases.length;i++){const model=cases[i],{g,own}=fromModel(model),logs=[];Host.log=s=>logs.push(s);
  if(!g.OpponentStep()||g.IsFatal()||g.IsPending())throw Error('unresolved endgame decision');Host.log=null;
  const moved=own.find(id=>g.FindCard(id).Snapshot().locationMask!==8);
  const index=g.match.playerTwo.hasPassed?-1:own.indexOf(moved);
  if(!g.match.playerTwo.hasPassed&&index<0)throw Error('no first action');
  rows.push({strength,case:i,optimal:solve(model),choiceValue:moveValue(model,index),index,
   publicTree:logs.some(s=>s.includes('event=PUBLIC_ENDGAME_TREE')),selection:logs.find(s=>/event=(SELECT|PASS)\b/.test(s))});
 }}return rows;
 })()`,c,{timeout:240000})};}
const fresh=evaluate(candidate),old=evaluate(baseline),summary={};
for(const strength of [2,3,4]){const a=fresh.rows.filter(x=>x.strength===strength),b=old.rows.filter(x=>x.strength===strength);
 summary[strength]={positions:a.length,optimalBefore:b.filter(x=>x.choiceValue===x.optimal).length,optimalAfter:a.filter(x=>x.choiceValue===x.optimal).length,
  improved:a.filter((x,i)=>x.choiceValue>b[i].choiceValue).length,regressed:a.filter((x,i)=>x.choiceValue<b[i].choiceValue).length,
  correctedMissedWins:a.filter((x,i)=>x.optimal===1&&x.choiceValue===1&&b[i].choiceValue<1).map(x=>x.case)};}
const report={candidate:fresh.fingerprint,baseline:old.fingerprint,summary,details:fresh.rows.map((x,i)=>({...x,before:old.rows[i]})),
 limitation:'Authored public Scorch/plain-body positions used during development, not an independent match win-rate sample.'};
fs.writeFileSync(output,JSON.stringify(report,null,2));console.log(JSON.stringify(summary));

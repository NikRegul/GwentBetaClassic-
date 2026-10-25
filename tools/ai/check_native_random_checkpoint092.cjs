'use strict';
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const root=path.resolve(__dirname,'../..');
const rules=path.join(root,'BetaGwent/build/release092-beta-final-20261023/rules');
const manifest=JSON.parse(fs.readFileSync(path.join(rules,'manifest.json'),'utf8'));
for(const [name,sha]of Object.entries(manifest.snapshotFiles))assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(rules,name))).digest('hex'),sha);
const code=['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(rules,n),'utf8')).join('\n');
const replay=new Function('checkpoint',code+String.raw`
if(checkpoint.encoding!=='original-beta-scalar-cursor-v1'||checkpoint.words.length!==625)throw Error('Unsupported native checkpoint');
const r=new CBetaGwentRandomGenerator();
r.words=checkpoint.words.map(x=>x|0);r.cursor=checkpoint.cursor|0;r.remaining=checkpoint.remaining;
r.reseedValue=checkpoint.reseedValue|0;r.initialSeed=checkpoint.initialSeed|0;r.draws=checkpoint.draws|0;
return Array.from({length:32},()=>r.NextBits()>>>0);
`);
(async()=>{
  const client=new OriginalBetaClient();
  try{
    const original=await client.request('random-checkpoint-selftest');
    for(const c of original.cases)assert.deepEqual(replay(c.checkpoint),c.expected,'Native/WS checkpoint mismatch: '+c.seed+'/'+c.skip);
    const report={schema:1,complete:true,fingerprint:manifest.fingerprint,cases:original.cases.length,
      comparedValues:original.cases.reduce((n,c)=>n+c.expected.length,0),errors:0,
      scope:'Direct original internal RNG fields imported into unchanged frozen WS generator. Independent oracle, including twist boundary. No live game advanced.',
      seeds:[...new Set(original.cases.map(c=>c.seed))],positions:[...new Set(original.cases.map(c=>c.skip))]};
    fs.writeFileSync(path.join(root,'BetaGwent/drafts/day-iteration-20261023/beta-original-js/native-random-checkpoint-smoke.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report));
  }finally{await client.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});

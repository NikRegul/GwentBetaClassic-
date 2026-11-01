'use strict';
// Freeze graph hashes + hand-written independent expectations (written from graphs/C# before reading handlers).
const fs=require('fs'),crypto=require('crypto'),{catalog}=require('./source_graph095.cjs'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const [,,inFile,outFile,scope]=process.argv,exp=JSON.parse(fs.readFileSync(inFile,'utf8'));
const records=Object.entries(exp.cards).map(([id,text])=>({id:+id,graphs:catalog.abilities.filter(a=>a.templateId===+id&&a.nodes.length).map(a=>({nid:a.nid,sha256:sha(JSON.stringify(a.sourceTree))})),expected:text}));
const cs=(exp.csharp||[]).map(n=>{const f='BetaGwent/build-inputs/reference/beta-original-csharp/GwentGameplay/'+n+'.cs';return {n,sha256:fs.existsSync(f)?sha(fs.readFileSync(f)):null};});
fs.writeFileSync(outFile,JSON.stringify({schema:1,scope,independentExpectationsBeforeHandlers:true,allBranchesComplete:false,csharp:cs,records},null,1)+'\n');console.log(records.length);

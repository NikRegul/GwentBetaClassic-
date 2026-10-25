'use strict';
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {OriginalBetaClient}=require('./original_beta_client092.cjs');
const {inspectNativeModel}=require('./native_session_import092.cjs');
const {chooseOpening}=require('./native_opening_adapter092.cjs');
const draft=path.resolve(__dirname,'../../BetaGwent/drafts/day-iteration-20261023/beta-original-js');
(async()=>{
 const client=new OriginalBetaClient();let original;
 try{original=await client.request('logger-selftest');assert.equal(original.passed,true);
  assert.deepEqual(original,{passed:true,errors:4,handledFallbacks:1,fatalErrors:3,guards:4});
 }finally{await client.close();}
 const a=JSON.parse(fs.readFileSync(path.join(draft,'native-persistent-audit.json'),'utf8')).cases[0];
 const native=JSON.parse(JSON.stringify(a.state));native.loggerErrors=1;native.loggerHandledFallbacks=1;native.loggerFatalErrors=0;
 const configs=[a.config,a.config],before=JSON.stringify(native),model=inspectNativeModel(native,configs,{actor:1,memory:{}});
 assert.equal(JSON.stringify(native),before);assert.equal(model.cards.length,native.cards.length);let guards=4;
 for(const change of [x=>{x.loggerFatalErrors=1},x=>{x.loggerHandledFallbacks=0},x=>{x.loggerErrors=0},
  x=>{x.loggerHandledFallbacks=-1},x=>{x.loggerErrors=1.5}]){
  const bad=JSON.parse(before);change(bad);assert.throws(()=>inspectNativeModel(bad,configs,{actor:1,memory:{}}),/Invalid original authoritative model/);guards++;
 }
 const diagnostic=JSON.parse(before);diagnostic.diagnosticOnly=true;diagnostic.ratingPermitted=false;
 assert.throws(()=>inspectNativeModel(diagnostic,configs,{actor:1,memory:{}}),/Invalid original authoritative model/);guards++;
 assert.equal(inspectNativeModel(diagnostic,configs,{actor:1,memory:{},diagnosticAnalysis:true}).cards.length,native.cards.length);guards++;
 diagnostic.loggerErrors=2;diagnostic.loggerDiagnosticReplayErrors=1;
 assert.throws(()=>inspectNativeModel(diagnostic,configs,{actor:1,memory:{}}),/Invalid original authoritative model/);guards++;
 assert.equal(inspectNativeModel(diagnostic,configs,{actor:1,memory:{},diagnosticAnalysis:true}).cards.length,native.cards.length);guards++;
 diagnostic.ratingPermitted=true;
 assert.throws(()=>inspectNativeModel(diagnostic,configs,{actor:1,memory:{},diagnosticAnalysis:true}),/Invalid original authoritative model/);guards++;
 diagnostic.ratingPermitted=false;diagnostic.diagnosticOnly=false;
 assert.throws(()=>inspectNativeModel(diagnostic,configs,{actor:1,memory:{},diagnosticAnalysis:true}),/Invalid original authoritative model/);guards++;
 assert.throws(()=>chooseOpening({...native,diagnosticOnly:true},configs),/Diagnostic native state/);guards++;
 assert.throws(()=>chooseOpening({...native,loggerDiagnosticReplayErrors:1},configs),/Diagnostic native state/);guards++;
 const report={schema:1,complete:true,originalClassifier:original,guards,
  totalDiagnosticsPreserved:true,unknownErrorsStillFatal:true,notStrengthResult:true};
 fs.writeFileSync(path.join(draft,'native-logger-classification-smoke.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
})().catch(e=>{console.error(e.stack);process.exitCode=1;});

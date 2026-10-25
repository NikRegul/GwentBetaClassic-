// Longer cooperative thinking is allowed only when measured individual calls stay short.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
const {load}=require('./diagnose_strategy096.js'),{context:ctx,manifest}=load(path.resolve(process.argv[2]));
vm.runInContext(String.raw`
let checks=0;function check(v,n){if(!v)throw Error(n);checks++;}
function feedback(strength,total,peak,stage=0){Host.strength=strength;Host.matchStrength=[strength,strength];const g=new CBetaGwentDuelSession();g.aiSimDamp=40;g.aiPreparationStage=stage;g.aiPreparationReady=false;g.AiPerfFeedback(total,peak);return g.aiSimDamp;}
check(feedback(4,5000,10)===40,'high keeps deeper search when total thought is long but every measured call is short');
check(feedback(4,5000,60)===65,'a heavy individual call still reduces search');
check(feedback(4,500,60)===65,'short total does not hide a heavy individual call');
check(feedback(4,9000,10)===65,'very long total still has a finite recovery budget');
check(feedback(4,5000,30)===65,'slower individual calls retain the conservative total limit');
check(feedback(4,5000,0)===65,'missing per-call measurement retains the conservative limit');
check(feedback(3,5000,10)===65,'lower difficulty budget unchanged');
check(feedback(4,500,5)===30,'fast calls still recover the search budget');
check(feedback(4,5000,60,1)===40,'active preparation ignores feedback until its current plan is complete');
globalThis.report={checks,actualWitcherScript:true,nativeFrameTimesMeasured:false};
`,ctx,{timeout:30000});const report={fingerprint:manifest.fingerprint,...ctx.report};if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2));console.log(JSON.stringify(report));

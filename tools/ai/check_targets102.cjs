'use strict';
// Target choices with more than 14 candidates: the 14 best by static score are
// simulated (two-hit Dol Blathanna Archer saves the 1 for an own Berserker), and
// resets (Cockatrice, Witch Hunter) score the change back to base power.
// Each AI choice must equal the best first pick found by brute force on clones.
// Usage: node check_targets102.cjs <rules-dir> [report.json]
const fs=require('fs'),path=require('path'),cp=require('child_process'),os=require('os');
const rules=path.resolve(process.argv[2]);let checks=0;const failures=[],cases=[];
const tmp=path.join(os.tmpdir(),'targets102-'+process.pid+'.jsonl');
const run=(ids,variants)=>{cp.execFileSync('node',[path.join(__dirname,'audit_static_targets102.cjs'),rules,tmp,'0','100',ids.join(',')],{env:{...process.env,VARIANTS:variants}});};
try{fs.unlinkSync(tmp);}catch(e){}
run([200233,200132],'plain,boosted');run([142310,152315],'plain,berserker,armour');
for(const r of fs.readFileSync(tmp,'utf8').trim().split('\n').map(JSON.parse)){
 cases.push(r);checks++;
 if(!('gap' in r)||r.gap>0)failures.push(r.id+' '+r.variant+' gap='+r.gap+(r.skip?' skip='+r.skip:'')+(r.err?' err='+r.err:''));
}
try{fs.unlinkSync(tmp);}catch(e){}
const report={checks,failures,cases,actualWitcherScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures}));if(failures.length)process.exitCode=1;

// Reconstruct one decision from an immutable paired match, checking every view.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib');
const [file,reason,output]=process.argv.slice(2);
if(!output)throw Error('Usage: node inspect_strategy092.js MATCH.json.gz PASS_REASON OUTPUT.json');
const saved=JSON.parse(zlib.gunzipSync(fs.readFileSync(file)));
const root=path.dirname(path.dirname(path.resolve(file))),proof=JSON.parse(fs.readFileSync(path.join(root,'report.json'),'utf8'));
function host(dir){const context=vm.createContext({console});
 vm.runInContext(['runtime.js','rules.js','harness.js'].map(n=>fs.readFileSync(path.join(dir,n),'utf8')).join('\n')+'\n'+require('./comparison_bridge119.js'),context);
 const bridge=context.bridge;bridge.setTunes(JSON.parse(fs.readFileSync(path.join(dir,'tunes.json'),'utf8')));bridge.setStrength(4);return bridge;}
const fresh=host(proof.candidate),old=host(proof.baseline),record=saved.record;
const target=saved.decisions.find(d=>d.version==='candidate'&&saved.logs.slice(d.logStart,d.logEnd).some(l=>l.text.includes('event=PASS reason='+reason+' ')));
if(!target)throw Error('Requested decision absent');
let h=fresh;h.load(saved.initial);if(record.mirror)h.mirror();
const first=record.newSeat===1?fresh:old;if(first!==h){first.load(h.dump());h=first;}h.initialMulligan();
for(let step=0;step<=target.step;step++){
 let view=h.view();if(!view.mulligan&&!view.pending&&!view.waiting&&view.current===1){h.swap();view=h.view();}
 const chooser=view.mulligan?1-view.actor:view.actor,next=chooser===record.newSeat?fresh:old;
 if(next!==h){next.load(h.dump());h=next;}
 if(JSON.stringify(h.view())!==JSON.stringify(saved.decisions[step].before))throw Error('Replay diverged before step '+step);
 if(step===target.step){fs.writeFileSync(output,JSON.stringify({schema:1,source:path.resolve(file),reason,step,record,before:h.view(),state:h.dump()},null,2));break;}
 h.step();
}
console.log(JSON.stringify({output,step:target.step,reason,exactReplay:true}));

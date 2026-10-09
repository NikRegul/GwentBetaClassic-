// Re-run a saved comparison match with its frozen decision policies and raw deal.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),zlib=require('zlib'),crypto=require('crypto');
const input=path.resolve(process.argv[2]||'');
if(!fs.existsSync(input))throw Error('Usage: node tools/ai/replay119.js <matches/game-N.json.gz>');
const replay=JSON.parse(zlib.gunzipSync(fs.readFileSync(input))),report=JSON.parse(fs.readFileSync(path.join(path.dirname(path.dirname(input)),'report.json'),'utf8'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
function host(folder,hash){if(sha(path.join(folder,'rules.js'))!==hash)throw Error('Frozen rules changed: '+folder);
 const context=vm.createContext({console});vm.runInContext(['runtime.js','rules.js','harness.js'].map(f=>fs.readFileSync(path.join(folder,f),'utf8')).join('\n')+'\n'+require('./comparison_bridge119'),context);
 context.bridge.setTunes(JSON.parse(fs.readFileSync(path.join(folder,'tunes.json'),'utf8')));return context.bridge;}
const fresh=host(report.candidate,report.candidateRules),old=host(report.baseline,report.baselineRules),record=replay.record;
const log=[];fresh.setLog(s=>log.push({version:'candidate',text:s}));old.setLog(s=>log.push({version:'baseline',text:s}));
let h=fresh,result=null,steps=0;h.load(replay.initial);if(record.mirror)h.mirror();
const first=record.newSeat===1?fresh:old;if(first!==h){first.load(h.dump());h=first;}
try{h.initialMulligan();for(;steps<500;steps++){
 let s=h.view();if(s.fatal)throw Error(s.message);
 if(s.winner){let winner=s.winner;if(s.reversed)winner=((winner&1)<<1)|((winner&2)>>1);result={winner,steps};break;}
 if(!s.mulligan&&!s.pending&&!s.waiting&&s.current===1){h.swap();s=h.view();}
 const chooser=s.mulligan?1-s.actor:s.actor,target=chooser===record.newSeat?fresh:old;
 if(target!==h){target.load(h.dump());h=target;}h.step();
 }if(!result)throw Error('decision limit');
}catch(e){result={winner:0,steps,error:String(e.stack||e)};}
const identical=result.winner===record.winner&&result.steps===record.steps&&Boolean(result.error)===Boolean(record.error)&&JSON.stringify(log)===JSON.stringify(replay.logs);
console.log(JSON.stringify({match:record.id,identical,result,logRecords:log.length},null,2));
if(!identical)process.exitCode=1;

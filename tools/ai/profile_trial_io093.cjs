'use strict';
const fs=require('node:fs');
const pause=new Int32Array(new SharedArrayBuffer(4));
// Windows readers/virus scanners can briefly deny replacing a JSON status file.
// Retry only sharing/permission failures, with a bounded two-second wait.
function renameWithRetry(from,to,rename=fs.renameSync,sleep=ms=>Atomics.wait(pause,0,0,ms)){
 for(let attempt=0;;attempt++){
  try{rename(from,to);return attempt;}
  catch(e){if(!['EPERM','EACCES','EBUSY'].includes(e.code)||attempt>=100)throw e;sleep(20);}
 }
}
module.exports={renameWithRetry};

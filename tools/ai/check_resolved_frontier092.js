'use strict';
const cp=require('child_process'),path=require('path');
const result=cp.spawnSync(process.execPath,[path.join(__dirname,'audit_frontier092.js'),...process.argv.slice(2),'--regression'],{stdio:'inherit'});
if(result.error)throw result.error;
process.exit(result.status??1);

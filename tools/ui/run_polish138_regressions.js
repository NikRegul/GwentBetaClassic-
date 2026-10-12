// Run existing UI regressions against the isolated draft. Only source paths are redirected;
// fixtures, assertions and production methods run unchanged.
'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm'),cp=require('child_process');
const root=path.resolve(__dirname,'../..'),draft=path.join(root,'BetaGwent/drafts/ui-polish138');
if(process.env.BG_UI138_FIXTURE==='1'){
 const read=fs.readFileSync;
 fs.readFileSync=function(file,...args){
  if(typeof file==='string'&&process.env.BG_UI138_LIVE!=='1'){
   const absolute=path.resolve(file),prefix=path.join(root,'BetaGwent/ui/src')+path.sep;
   if(absolute.startsWith(prefix))file=path.join(draft,'src',absolute.slice(prefix.length));
  }
  return read.call(fs,file,...args);
 };
}else{
 const suites=['check_controller123.js','check_catalog123.js','check_optional124.js',
  'check_halfcast126.js','check_controller126.js','check_timing126.js',
  'check_card_presentation126.js','check_followups127.js','check_presentation133.js',
  'check_ux135.js','check_release137.js','check_leader_release137.js','check_fixes061.js'];
 const results=[];let failed=false;
 for(const suite of suites){
  const result=cp.spawnSync(process.execPath,['-r',__filename,path.join(__dirname,suite),...(suite==='check_fixes061.js'?['--source-only','--stage138']:[])],
   {cwd:root,env:{...process.env,BG_UI138_FIXTURE:'1'},encoding:'utf8',maxBuffer:1<<24});
  results.push({suite,exitCode:result.status,output:result.stdout.trim().split('\n').at(-1),errors:result.stderr.trim()});
  if(result.status!==0){failed=true;console.error(suite+'\n'+result.stdout+'\n'+result.stderr);}
  else console.log(suite+': passed');
 }
 fs.mkdirSync(path.join(draft,'evidence'),{recursive:true});
 fs.writeFileSync(path.join(draft,'evidence/regressions.json'),JSON.stringify(results,null,2)+'\n');
 process.exitCode=failed?1:0;
}

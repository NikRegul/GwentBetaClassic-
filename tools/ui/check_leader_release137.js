// Reproduce the native crash contract: imported CSwfTexture cannot be disposed
// through AS BitmapData. Execute the actual page release method with a sentinel.
'use strict';
const fs=require('fs'),vm=require('vm'),crypto=require('crypto');
const path='tools/ui/leaders060/BetaLeaderMovie137.as';
const source=fs.readFileSync(path,'utf8');
const release=source.match(/public function release\(\):void\s*\{([^}]*)\}/);
if(!release)throw Error('Page release method missing');
let disposed=0,cleared=0;
const ctx=vm.createContext({pixels:{dispose(){disposed++;throw Error('Native DICommand_Dispose access violation');}},previous:7,graphics:{clear(){cleared++;}}});
vm.runInContext('function release(){'+release[1]+'}',ctx);
ctx.release();ctx.release();
if(disposed!==0||cleared!==2||ctx.pixels!==null||ctx.previous!==-1)throw Error('Engine-owned atlas must only drop references, idempotently');
// A released page must not attempt to draw from the dropped atlas.
if(!source.includes('if(!pixels)return;'))throw Error('Render after release must be inert');
const report={stage:137,passed:true,checks:3,nativeGameTested:false,
 nativeCrashOperation:'Scaleform::Render::DICommand_Dispose',
 sources:{[path]:crypto.createHash('sha256').update(source).digest('hex'),
 'tools/ui/check_leader_release137.js':crypto.createHash('sha256').update(fs.readFileSync(__filename)).digest('hex')}};
fs.writeFileSync('docs/evidence/leader-release137.json',JSON.stringify(report,null,2)+'\n');
console.log('PASS: engine-owned atlas release never calls BitmapData.dispose');

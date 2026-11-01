'use strict';
const fs=require('fs'),path=require('path'),vm=require('vm');
process.env.ROOT=path.resolve(__dirname,'../..');
const H=require('./preview_screens096/harness.cjs'),c=H.ctx;
const file=process.argv[2]||process.env.ROOT+'/BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
let checks=0;const failures=[];function check(v,n){checks++;if(!v)failures.push(n);}
const target={id:44,zone:1,side:2,index:0,power:7,tokens:0};
Object.assign(c,{ready:true,playing:false,detailOpen:false,pileOpen:false,editingDeck:false,selectingDecks:false,browsingCatalog:false,kegOpen:false,controllerMenuOpen:false,
 hoveredCard:target,legal:false,requestId:0,requestKind:2,rowRequest:false,requestCount:0,requestMax:3,requestMin:1,requestSourceTemplate:0,selected:0,
 cards:[target],cardDetails:{44:{tier:2}},templateRules:{},playRules:{},revision:1,placementPreview:null,actionPreviewKey:'',mouseX:-100,mouseY:-100,
 actionPreviewLayer:new c.Sprite(),displayedCards:{44:{x:400,y:200,width:80,height:110}},
 canDirectTarget:()=>c.legal,canPlacePending:()=>false,canPlaceSelected:()=>false,halfCastSide:()=>0,findRequestCard:()=>c.legal?target:null,
 rowGeometry:()=>({x:400,y:200,w:400,h:100}),rowEnabled:()=>false});
c.controller.active=false;c.BetaGwentUi138.helpLabels=true;c.BetaGwentUi138.chains=true;
vm.runInContext(['previewOutline','updateActionPreview','drawCueArrow'].map(n=>H.extract(n,source)).join('\n'),c);
let textDraws=0;c.text=()=>{textDraws++;throw Error('obsolete battle text rendered');};
for(const requestId of [0,42])for(const legal of [false,true]){
 c.requestId=requestId;c.legal=legal;c.revision++;c.updateActionPreview();
 check(textDraws===0,'no service prose with saved help enabled '+requestId+'/'+legal);
 check(c.actionPreviewLayer.graphics.ops.some(o=>o[0]==='rect')===legal,'legal target outline retained '+requestId+'/'+legal);
}
for(const [ax,ay,bx,by]of [[0,0,400,200],[400,800,600,100],[500,100,100,500]]){
 const arrow=new c.Sprite();c.drawCueArrow(arrow,ax,ay,80,110,bx,by,80,110,0x48BFFF);
 const ops=arrow.graphics.ops,end=ops.findIndex(o=>o[0]==='end');
 check(ops.some(o=>o[0]==='fill')&&ops.filter(o=>o[0]==='lineto').length>=6,'filled aiming arrow retained');
 check(end>=0&&!ops.slice(end+1).some(o=>o[0]==='move'||o[0]==='lineto'),'no debug centre stroke after arrow fill');
}
check(!H.extract('attachInspect',source).includes('battleDisabledReason'),'focus labels no longer append service reasons');
check(!H.extract('render',source).includes('requestInstruction()'),'render has no legacy request instruction overlay');
check(!H.extract('drawChainCue',source).includes('betaLabel'),'chain cue has no custom text strip');
check(!H.extract('drawVisualCue',source).includes('BetaGwentUi138.helpLabels'),'saved help flag cannot restore actor/fizzle prose');
check(!H.extract('openControllerMenu',source).includes('id:"help"')&&!H.extract('openControllerMenu',source).includes('id:"chains"'),'obsolete text switches removed');
const report={checks,failures,sourceSha256:require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),actualActionScript:true,nativeGameTested:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));if(failures.length)process.exitCode=1;

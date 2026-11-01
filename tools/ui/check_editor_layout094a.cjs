'use strict';
// Fit the card body to the native slot's INNER opening. Banners retain their
// original proportions and are checked against the surrounding wooden panel.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
const file=process.argv[2]||'BetaGwent/ui/src/BetaGwentBoard.as',source=fs.readFileSync(file,'utf8');
function extract(name){const at=source.indexOf('function '+name+'(');assert(at>=0,name);const a=source.indexOf('{',at);let b=a+1,d=1;
 while(d){d+=(source[b]==='{')-(source[b]==='}');b++;}
 return source.slice(at,b).replace(/:\s*(?:String|Number|Boolean|Array|int|void)\b/g,'');}
const banners=fs.readFileSync('BetaGwent/ui/src/BetaGwentBanners090.as','utf8');
const native=JSON.parse(banners.match(/DATA:Object=(.*);/)[1]);
const model=JSON.parse(fs.readFileSync('data/beta924/design/release093_ui.json','utf8'));
let checks=0;const failures=[],art=[],labels=[];
function check(ok,label){checks++;if(!ok)failures.push(label);}
const ctx=vm.createContext({Math,String,BETA_CARD_ASPECT:17.64/21.46,BETA_LARGE_CARD_ASPECT:15.85574533/22.7377556,
 content:{},BetaGwentDeckArt104:{stats:()=>-3749,DP_STAT_GOLD:1,DP_STAT_SILVER:2,DP_STAT_BRONZE:3},BetaGwentFonts:{BODY:0},
 paintArt:(p,id,w,h,x,y)=>art.push({id,x,y,w,h}),betaSlotLabel:(p,text,x,y,w,h)=>labels.push({text,x,y,w,h}),
 betaLabel:(p,text,x,y,w)=>labels.push({text,x,y,w}),
 BetaGwentTextLanguage:{language:1},BetaGwentReleaseText093:{opponent:(s,l)=>s||model.opponents['Соперник'][l-1]},
 opponentName:()=>ctx.name,name:''});
vm.runInContext(['betaSidePreviewPlacement','betaStatsWidget','npcMatchHint'].map(extract).join('\n'),ctx);
const large=Array.from(ctx.betaSidePreviewPlacement(true)),small=Array.from(ctx.betaSidePreviewPlacement(false));
for(const [name,b]of Object.entries(native)){
 const [x,y,w,h]=large;
 const bounds=[x+Math.min(0,b[0])*w-8,y+Math.min(0,b[1])*h-8,x+Math.max(1,b[0]+b[2])*w+8,y+Math.max(1,b[1]+b[3])*h+8];
 check(bounds[0]>=1485&&bounds[1]>=137&&bounds[2]<=1874&&bounds[3]<=979,'full native banner + glow inside wooden panel: '+name);
}
const opening=[1545+18*285/190,177+22*398/266,156*285/190,224*398/266];
check(large[2]>=230&&large[3]>=330,'card body fills the frame; fitting banner bounds must not shrink it again');
check(large[0]>=opening[0]-1e-6&&large[1]>=opening[1]-1e-6&&large[0]+large[2]<=opening[0]+opening[2]+1e-6&&large[1]+large[3]<=opening[1]+opening[3]+1e-6,'card body entirely inside the native inner opening');
check(Math.abs(large[0]+large[2]/2-opening[0]-opening[2]/2)<1e-6&&Math.abs(large[1]+large[3]/2-opening[1]-opening[3]/2)<1e-6,'card body centred in actual frame');
check(Math.abs(large[2]/large[3]-15.85574533/22.7377556)<1e-6,'native card aspect preserved');
check(small[0]===1477+(405-312)/2&&small[1]+small[3]===572&&small[2]===312,'battle preview placement retained');
check(source.includes('fromX:cardX+(big?0:24)')&&source.includes('card.x=cardX+(big?0:24)'),'deck preview stays in recess during fade-in');
ctx.betaStatsWidget(4,4,6,15,25,160);
check(art[0].x===52&&art[0].x+art[0].w===412,'stats texture inset 6px from both deck-row edges');
check(labels[3].x===52&&labels[3].w===360,'total centred in the same inset');
check(art[0].y===160&&art[0].y+art[0].h<=266&&source.includes('bronzes,total,160);')&&source.includes('bronzes,editorState.total,160);'),'stats below the wooden top border, above the next row, on both screens');
check(art.slice(1).every((a,i)=>a.x===labels[i].x&&a.y===labels[i].y&&a.w===labels[i].w&&a.h===labels[i].h),'counter text and textures use identical rectangles');
check(Math.abs((art[1].x+art[3].x+art[3].w)/2-232)<1e-6,'tier group centred over the deck rows');
for(let language=1;language<=13;language++){
 ctx.BetaGwentTextLanguage.language=language;ctx.name=model.opponents['Соперник'][language-1];
 check(ctx.npcMatchHint()==='Выход из боя считается поражением.','generic NPC is not repeated: '+language);
 ctx.name='Zoltan';check(ctx.npcMatchHint()==='Соперник: Zoltan · выход из боя считается поражением','actual NPC name remains visible: '+language);
}
const report={checks,failures,source:path.resolve(file),largePreview:large,battlePreview:small,statsArt:art,statsLabels:labels,
 nativeBannerExtentsVerified:Object.keys(native).length,actualActionScript:true,nativeGameplayVerified:false};
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({checks,failures,largePreview:large}));if(failures.length)process.exitCode=1;

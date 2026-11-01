'use strict';
const H=require('./harness.cjs');const {ctx,all}=H;const fs=require('fs');
const leaders=all.filter(c=>c.leader&&c.faction==16);const L=leaders[0];
function base(){Object.assign(ctx,{skin:3,ready:true,entryMode:1,scraps:1240,unopenedKegs:3,pendingKeg:false,reducedMotion:false,playing:false,editingDeck:false,browsingCatalog:false,selectingDecks:false,
 detailOpen:false,pileOpen:false,nameOpen:false,controllerMenuOpen:false,kegOpen:false,revision:5,serverRevision:5,collectionNew:{},ownedCopies:{},leaderIds:[L.templateId,0],animations:[],shelves178:{},shelfCards178:{},
 editorTier:0,editorType:0,editorFactionOnly:false,editorOwnedOnly:false,editorNeutralOnly:false,editorUnownedOnly:false,editorSearch:'',editorPosition:0,editorStrength:0,editorNewOnly:false,editorScroll178:0,deckScroll178:0,
 editorPage:0,editorCraft:null,editorPreviewId:0,editorUndo:[],catalogTier:0,catalogFaction:0,catalogType:0,catalogStatus:0,catalogPosition178:0,catalogSort:0,catalogSearch:'',catalogNewOnly:false,catalogScroll178:0,catalogPage:0,
 searchDeadline:0,inspection:null,catalogAbility:null,mulliganReading:null,pileDetail:null,editorBaseline:'x',deckListScroll:0,pickerSide:0,tutorialSeen:true,tutorialOffered:true,mulliganConfirm:false,deleteDeckId:0,connected:true,
 leaderPreview:null,battlePreviewKey:'',difficultyIndex:3});
 ctx.content=new ctx.Sprite();ctx.content.isRoot=true;}
const pool=all.filter(c=>!c.leader&&(c.faction==16||c.faction==1)&&!c.token&&c.collectible!==false);
function editorCards(){let golds=0,silvers=0,n=0;return pool.slice(0,80).map((c,i)=>{const e={templateId:c.templateId,title:c.title,description:c.description,power:c.power,tier:c.tier,typeMask:c.typeMask,faction:c.faction,copies:0,canAdd:true,timer:-1,tokens:0};
 if(n<25&&((c.tier==8&&golds<4)||(c.tier==4&&silvers<6)||(c.tier==2&&i%3==0))){e.copies=c.tier==2?(i%2?2:1):1;n+=e.copies;if(c.tier==8)golds++;if(c.tier==4)silvers++;}
 return e;});}
function own(cards){for(const c of all)ctx.ownedCopies[c.templateId]=c.templateId%3==0?0:(c.tier==2?3:1);}
const scenes={};
// deck editor
base();own();let cards=editorCards();let tot=cards.reduce((a,c)=>a+c.copies,0);
Object.assign(ctx,{editingDeck:true,editorCards:cards,editorById:Object.fromEntries(cards.map(c=>[c.templateId,c])),editorName:"Spella'tael",
 editorState:{slot:1001,faction:16,leader:L.templateId,total:tot,golds:cards.filter(c=>c.copies&&c.tier==8).length,silvers:cards.filter(c=>c.copies&&c.tier==4).length,valid:tot>=25,status:''},
 leaderOptions:[{id:L.templateId,title:L.title,description:L.description,power:L.power}]});
const preview=cards.find(c=>c.tier==8);ctx.editorPreviewId=preview.templateId;
ctx.drawBetaDeckEditor();ctx.drawDeckExchangeButtons();scenes.editor=H.dump(ctx.content);
// collection
base();own();Object.assign(ctx,{browsingCatalog:true,catalogPicked:all.find(c=>c.faction==16&&c.tier==8&&!c.leader),leaderOptions:[]});
ctx.drawBetaCatalog();scenes.catalog=H.dump(ctx.content);
// deck selection
base();own();const deckCards=editorCards().filter(c=>c.copies);
Object.assign(ctx,{selectingDecks:true,deckOptions:[{id:1001,title:"Spella'tael",leader:L.title,leaderId:L.templateId,cards:deckCards,description:''},{id:16,title:'Скоя’таэли',leader:L.title,leaderId:L.templateId,cards:deckCards,description:''}],
 ownPreset:1001,enemyPreset:16,chosenLeaders:[L.templateId,L.templateId],leaderOptions:[{id:L.templateId,title:L.title,description:L.description,power:L.power}],battlePreview:null});
ctx.drawBetaMatchSetup();scenes.selection=H.dump(ctx.content);
fs.writeFileSync(process.argv[2],JSON.stringify(scenes));console.log(Object.fromEntries(Object.entries(scenes).map(([k,v])=>[k,v.length])));

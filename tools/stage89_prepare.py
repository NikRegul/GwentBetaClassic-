"""Apply stage89 modal isolation and backward-compatible four-win rewards."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as'
s=p.read_text('utf-8-sig')
s=s.replace('private var choicePage:int=0;', 'private var choicePage:int=0;\n        private var choiceLayer:Sprite=new Sprite();')
s=s.replace('root:nameOpen?nameLayer:detailOpen?detailLayer:controllerMenuOpen?controllerMenuLayer:pileOpen?pileLayer:content,','root:nameOpen?nameLayer:detailOpen?detailLayer:controllerMenuOpen?controllerMenuLayer:pileOpen?pileLayer:base=="choice"?choiceLayer:content,')
s=s.replace('layers:[{root:nameLayer,mode:"name"}', 'layers:[{root:choiceLayer,mode:"choice"},{root:nameLayer,mode:"name"}')
s=s.replace('while(content.numChildren) content.removeChildAt(0);', 'while(choiceLayer.numChildren)choiceLayer.removeChildAt(0);\n            while(content.numChildren) content.removeChildAt(0);')
s=s.replace('private function button(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function):TextField', 'private function button(title:String,x:Number,y:Number,w:Number,enabled:Boolean,callback:Function,parent:Sprite=null):TextField')
s=s.replace('var p:Sprite=panel(content,x,y,w,48,enabled?0x273B43:0x222426);', 'var p:Sprite=panel(parent||content,x,y,w,48,enabled?0x273B43:0x222426);')
s=s.replace('{ return requestId>0?canSelectRow(side,zone):canPlayRow(side,zone); }', '{ return requestId>0&&requestKind==1?false:requestId>0?canSelectRow(side,zone):canPlayRow(side,zone); }')
s=s.replace('var modal:Sprite=panel(content,450,215,1000,600,0x10191F,.98);', 'content.addChild(choiceLayer);\n            // Opaque hit surface stops clicks reaching the board behind choices.\n            choiceLayer.graphics.clear();choiceLayer.graphics.beginFill(0,0.30);choiceLayer.graphics.drawRect(0,0,1920,1080);choiceLayer.graphics.endFill();\n            var modal:Sprite=panel(choiceLayer,450,215,1000,600,0x10191F,.98);')
start=s.index('        private function drawChoices():void')
end=s.index('        private function drawBacks():void',start)
chunk=s[start:end]
chunk=chunk.replace('requestAction("OnBetaGwentRequestFinish"));','requestAction("OnBetaGwentRequestFinish"),choiceLayer);')
chunk=chunk.replace('function():void{choicePage--;render();});','function():void{choicePage--;render();},choiceLayer);')
chunk=chunk.replace('function():void{choicePage++;render();});','function():void{choicePage++;render();},choiceLayer);')
s=s[:start]+chunk+s[end:]
p.write_text(s,'utf-8')
p=ROOT/'BetaGwent/development/scripts/game/betagwent/collectionProfile.ws'
s=p.read_text('utf-8-sig').replace('var i,id,gold : int;', 'var i,id,gold,rewarded : int;')
s=s.replace('if(betaGwentRewardedNpcs.Contains(npcId)) return "Награда за первую победу над этим игроком уже получена.";', '// Each saved occurrence is one rewarded win. Old saves contain one occurrence.\n    for(i=0;i<betaGwentRewardedNpcs.Size();i+=1)if(betaGwentRewardedNpcs[i]==npcId)rewarded+=1;\n    if(rewarded>=4)return "Все четыре награды этого игрока уже получены.";')
s=s.replace('if(pool.Size()==0){betaGwentRewardedNpcs.PushBack(npcId);return "Все бронзовые и серебряные карты уже собраны.";}', 'if(pool.Size()==0)return "Все бронзовые и серебряные карты уже собраны.";')
s=s.replace('" copies="+BetaGwentOwned(id));', '" copies="+BetaGwentOwned(id)+" rewardedWins="+(rewarded+1));')
s=s.replace('return "Новая карта: "+d.title+" ("+BetaGwentOwned(id)+"/"+BetaGwentCollectionCap(id)+")";', 'return "Новая карта: "+d.title+" ("+BetaGwentOwned(id)+"/"+BetaGwentCollectionCap(id)+") · Награда "+(rewarded+1)+"/4";')
p.write_text(s,'utf-8-sig')
for dest in ('BetaGwent/build/board-patch/game/betagwent','GwentB/myproject1/workspace/scripts/game/betagwent'):
    target=ROOT/dest/p.name;target.write_bytes(p.read_bytes())
p=ROOT/'tools/build_full_catalog.py'
s=p.read_text('utf-8').replace('за первую победу над обычным игроком/торговцем','за первые четыре победы над обычным игроком/торговцем (по одной карте)')
p.write_text(s,'utf-8')
print('Stage89 modal and four-win policy prepared.')

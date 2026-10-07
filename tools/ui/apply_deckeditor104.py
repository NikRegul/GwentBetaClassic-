"""Stage 104: Gwent Beta deck builder (UIDBPrefab) for skin 3.

DeckPicker/DeckCards on the left (stats widget, name, leader, slot rows), Collection
(woodpanel_large_bg, filter bar, 5x2 card grid) in the centre, SidePreview on the right.
Usage: apply_deckeditor104.py [BetaGwentBoard.as]  (requires apply_matchsetup104 first)
"""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[2]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
MARK = '// stage104-deckeditor'
METHODS = r'''
        // stage104-deckeditor: UIDBPrefab (deck builder) in the original arrangement.
        private function betaStatsWidget(fi:int,golds:int,silvers:int,bronzes:int,total:int,y:Number):void
        {
            paintArt(content,BetaGwentDeckArt104.stats(Math.min(4,fi)),371,108,52,y);
            var counters:Array=[[BetaGwentDeckArt104.DP_STAT_GOLD,golds+"/4",0xF6D36B],[BetaGwentDeckArt104.DP_STAT_SILVER,silvers+"/6",0xE6E6E6],[BetaGwentDeckArt104.DP_STAT_BRONZE,String(bronzes),0xE0B07A]];
            for(var k:int=0;k<3;k++){
                paintArt(content,counters[k][0],46,54,152+k*62,y+8);
                betaLabel(content,counters[k][1],148+k*62,y+20,54,18,counters[k][2],BetaGwentFonts.BODY,false,"center");
            }
            betaLabel(content,"КАРТЫ: "+total,52,y+72,371,18,total>=25?0xF2EEE4:0xF0B060,BetaGwentFonts.BODY,false,"center",1);
        }
        private function drawBetaDeckEditor():void
        {
            paintArt(content,BetaGwentDeckArt104.BG_BUILDER,1920,1080,0,0);
            betaPlaque("Редактор колоды");
            var fi:int=editorFactionIndex(editorState.faction);
            // left: DeckPicker / DeckCards
            paintArt(content,BetaGwentHud104.WOOD_PANEL,426,858,21,129);
            var bronzes:int=0;var selectedCards:Array=[];
            for each(var c:Object in editorCards)if(c.copies>0){selectedCards.push(c);if(c.tier==2)bronzes+=c.copies;}
            selectedCards.sort(sortEditorCards);
            betaStatsWidget(fi,editorState.golds,editorState.silvers,bronzes,editorState.total,146);
            var nameRow:Sprite=new Sprite();nameRow.x=46;nameRow.y=262;content.addChild(nameRow);
            paintArt(nameRow,BetaGwentDeckArt104.DP_NEWDECK,372,44,0,0);
            betaLabel(nameRow,String(editorName||"Новая колода").toUpperCase(),16,10,300,17,0xF2EEE4,BetaGwentFonts.TITLE,true,null,1.5);
            betaLabel(nameRow,"✎",336,8,26,18,0xCFC8BA,BetaGwentFonts.BODY);
            attachEditorClick(nameRow,openNameInput);
            var picked:Object=leaderOption(editorState.leader);var factionLeaders:Array=leadersForFaction(editorState.faction);var leaderIndex:int=0;
            for(var li:int=0;li<factionLeaders.length;li++)if(factionLeaders[li].id==editorState.leader)leaderIndex=li;
            if(picked){
                var leaderCard:Object={templateId:picked.id,title:picked.title,description:picked.description,power:picked.power,tier:1,typeMask:4,faction:editorState.faction,copies:1,tokens:0,timer:-1,side:1};
                var lrow:Sprite=deckSlotRow(content,leaderCard,46,312,372,60,true);
                attachInspect(lrow,leaderCard,{description:picked.description},372,60);
                if(factionLeaders.length>1){
                    var previous:Object=factionLeaders[(leaderIndex+factionLeaders.length-1)%factionLeaders.length];
                    var next:Object=factionLeaders[(leaderIndex+1)%factionLeaders.length];
                    betaWideButton("‹",46,374,60,ready,editorAction("OnBetaGwentDeckEditorLeader",previous.id));
                    betaWideButton("›",358,374,60,ready,editorAction("OnBetaGwentDeckEditorLeader",next.id));
                    betaLabel(content,"Сменить лидера",110,384,244,15,0xCFC8BA,BetaGwentFonts.BODY,false,"center");
                }
            }
            var perPage:int=13;var pages:int=Math.max(1,Math.ceil(selectedCards.length/perPage));editorListPage=Math.max(0,Math.min(editorListPage,pages-1));
            var list:Sprite=new Sprite();content.addChild(list);
            list.graphics.beginFill(0,0);list.graphics.drawRect(46,428,372,perPage*40);list.graphics.endFill();
            for(var i:int=editorListPage*perPage;i<Math.min(selectedCards.length,(editorListPage+1)*perPage);i++){
                c=selectedCards[i];c.side=1;
                var row:Sprite=deckSlotRow(list,c,46,428+(i-editorListPage*perPage)*40,372,38);
                attachInspect(row,c,{description:c.description},372,38);
                if(ready)attachEditorClick(row,editorAction("OnBetaGwentDeckEditorChange",c.templateId,-1));
            }
            if(!selectedCards.length)betaLabel(content,"Нажмите на карту в коллекции,\nчтобы добавить её в колоду.",52,470,360,18,0xCFC8BA,BetaGwentFonts.BODY,false,"center").height=60;
            list.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();editorListPage=Math.max(0,editorListPage+(e.delta<0?1:-1));render();});
            if(pages>1){
                betaWideButton("‹",46,950,60,ready&&editorListPage>0,function():void{editorListPage--;render();});
                betaLabel(content,(editorListPage+1)+" / "+pages,110,958,244,16,0xCFC8BA,BetaGwentFonts.BODY,false,"center");
                betaWideButton("›",358,950,60,ready&&editorListPage+1<pages,function():void{editorListPage++;render();});
            }
            // centre: Collection with the filter bar
            paintArt(content,BetaGwentDeckArt104.WOOD_LARGE,1026,858,447,129);
            var tiers:Array=[0,2,4,8];var tierIcons:Array=[BetaGwentDeckArt104.TIER_ALL,BetaGwentDeckArt104.TIER_BRONZE,BetaGwentDeckArt104.TIER_SILVER,BetaGwentDeckArt104.TIER_GOLD];
            for(var ti:int=0;ti<4;ti++)betaFilterButton(tierIcons[ti],482+ti*72,156,editorTier==tiers[ti],editorFilterAction(tiers[ti],editorType,editorFactionOnly));
            var factions:Array=[2,8,4,16,32];
            for(var f:int=0;f<factions.length;f++){
                var fIndex:int=editorFactionIndex(factions[f]);
                betaFilterButton(BetaGwentDeckArt104.factionFilter(fIndex),1040+f*72,156,editorState.faction==factions[f],
                    editorFactionAvailable(factions[f])?editorAction("OnBetaGwentDeckEditorLeader",editorFactionLeader(factions[f])):null);
            }
            betaWideButton("Все",482,226,110,ready,editorFilterAction(editorTier,0,editorFactionOnly));
            betaWideButton("Отряды",600,226,140,ready,editorFilterAction(editorTier,4,editorFactionOnly));
            betaWideButton("Особые",748,226,140,ready,editorFilterAction(editorTier,2,editorFactionOnly));
            betaWideButton(editorFactionOnly?"Без нейтральных":"С нейтральными",896,226,236,ready,editorFilterAction(editorTier,editorType,!editorFactionOnly));
            var searchInput:TextField=editorInput(editorSearch,1146,224,300,64);
            searchInput.addEventListener(Event.CHANGE,function(e:Event):void{editorSearch=searchInput.text;editorPage=0;searchDeadline=getTimer()+160;});
            content.graphics.lineStyle(2,0x6A5A44,.8);content.graphics.moveTo(474,286);content.graphics.lineTo(1446,286);content.graphics.lineStyle();
            editorCollection=new Sprite();editorCollection.x=0;editorCollection.y=0;content.addChild(editorCollection);
            editorCollection.addEventListener(MouseEvent.MOUSE_WHEEL,function(e:MouseEvent):void{e.stopPropagation();if(!ready)return;editorPage=Math.max(0,editorPage+(e.delta<0?1:-1));redrawEditorCollection();});
            redrawEditorCollection();
            // right: SidePreview
            paintArt(content,BetaGwentHud104.WOOD_PANEL,426,858,1473,129);
            paintArt(content,BetaGwentHud104.PREVIEW_SLOT,285,398,1545,177);
            editorPreview=new Sprite();editorPreview.mouseEnabled=false;editorPreview.mouseChildren=false;content.addChild(editorPreview);
            var preview:Object=editorById[editorPreviewId];if(!preview&&picked)preview={templateId:picked.id,title:picked.title,description:picked.description,power:picked.power,tier:1,typeMask:4,faction:editorState.faction,copies:1};
            if(!preview&&editorCards.length)preview=editorCards[0];
            editorPreviewId=0;showEditorCard(preview);
            // bottom
            if(editorState.status)betaLabel(content,editorState.status,474,948,972,17,editorState.valid?0xA6D6AF:0xF0C080,BetaGwentFonts.BODY,false,"center");
            betaWideButton("Сохранить",560,1002,260,ready&&editorState.valid,editorAction("OnBetaGwentDeckEditorSave"));
            betaWideButton("Очистить",840,1002,240,ready&&editorState.total>0,editorAction("OnBetaGwentDeckEditorClear"));
            betaWideButton("Отмена",1100,1002,240,ready,editorAction("OnBetaGwentDeckEditorCancel"));
        }
        private function betaFilterButton(icon:int,x:Number,y:Number,on:Boolean,callback:Function):void
        {
            var b:Sprite=new Sprite();b.x=x;b.y=y;content.addChild(b);
            paintArt(b,BetaGwentDeckArt104.FILTER_BTN,66,56,0,0);paintArt(b,icon,40,40,13,8);
            if(on)paintArt(b,BetaGwentDeckArt104.FILTER_ON,66,56,0,0);
            b.alpha=callback!=null?1:.4;
            if(callback!=null&&ready){
                b.buttonMode=true;b.mouseChildren=false;
                b.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();uiSound();callback();});
                controller.registerControl(b,"",callback,null,null,"control",null,new Rectangle(0,0,66,56));
            }
        }
        private function redrawBetaCollection():void
        {
            while(editorCollection.numChildren)editorCollection.removeChildAt(0);
            var filtered:Array=[];var query:String=editorSearch.toLowerCase();
            for each(var c:Object in editorCards){
                if(editorTier!=0&&editorTier!=c.tier)continue;
                if(editorType!=0&&editorType!=c.typeMask)continue;
                if(editorFactionOnly&&c.faction==1)continue;
                if(query.length>0&&(c.title+" "+c.description+" "+BetaGwentCardTags.text(c.templateId)).toLowerCase().indexOf(query)<0)continue;
                filtered.push(c);
            }
            var perPage:int=10;var pages:int=Math.max(1,Math.ceil(filtered.length/perPage));editorPage=Math.max(0,Math.min(editorPage,pages-1));
            var cw:Number=164,ch:Number=Math.round(164/BETA_CARD_ASPECT);
            for(var i:int=editorPage*perPage;i<Math.min(filtered.length,(editorPage+1)*perPage);i++){
                c=filtered[i];var n:int=i-editorPage*perPage;c.side=1;
                var tile:Sprite=new Sprite();tile.x=500+(n%5)*186;tile.y=306+int(n/5)*318;editorCollection.addChild(tile);
                tile.graphics.beginFill(0,.45);tile.graphics.drawRect(4,6,cw,ch);tile.graphics.endFill();
                paintBetaFace(tile,c.templateId,cw,ch,1);
                if(c.typeMask==4)betaPowerField(tile,String(c.power),cw,ch,0xFFFFFF);
                var cap:int=entryMode==0?(c.tier==2?3:1):int(ownedCopies[c.templateId]);
                if(c.copies>0){
                    paintArt(tile,BetaGwentDeckArt104.DB_COPIES,44,44,cw-48,4);
                    betaLabel(tile,"x"+c.copies,cw-48,14,44,17,0xF2EEE4,BetaGwentFonts.BODY,false,"center");
                }
                tile.alpha=c.canAdd||c.copies>0?1:.5;
                var shelf:TextField=betaLabel(tile,c.copies+" / "+cap,0,ch+6,cw,16,c.canAdd?0xF2EEE4:0xA49A88,BetaGwentFonts.BODY,false,"center");
                attachInspect(tile,c,{description:c.description},cw,ch);
                if(c.canAdd&&ready)attachEditorClick(tile,editorAction("OnBetaGwentDeckEditorChange",c.templateId,1));
            }
            if(filtered.length==0)betaLabel(editorCollection,"Нет карт, подходящих под фильтры.",474,560,972,22,0xF2EEE4,BetaGwentFonts.BODY,false,"center");
            var prev:Function=function():void{editorPage--;redrawEditorCollection();};
            var next:Function=function():void{editorPage++;redrawEditorCollection();};
            var start:int=content.numChildren;
            betaWideButton("‹",474,930,70,ready&&editorPage>0,prev);
            betaWideButton("›",1376,930,70,ready&&editorPage+1<pages,next);
            while(content.numChildren>start)editorCollection.addChild(content.getChildAt(start));
            betaLabel(editorCollection,"Коллекция: "+filtered.length+" · "+(editorPage+1)+" / "+pages,560,938,800,17,0xE8DCC4,BetaGwentFonts.BODY,false,"center");
        }
'''

def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
    if MARK in t: raise SystemExit('already applied')
    if '// stage104-matchsetup' not in t: raise SystemExit('apply_matchsetup104 first')
    def rep(a, b):
        nonlocal t
        if t.count(a) != 1: raise SystemExit('anchor %d: %r' % (t.count(a), a[:90]))
        t = t.replace(a, b)
    rep('        private function drawDeckEditor():void\n        {\n',
        METHODS.lstrip('\n').replace('        // stage104-deckeditor: UI', '        ' + MARK + '\n        // UI') +
        '        private function drawDeckEditor():void\n        {\n            if(skin==3){drawBetaDeckEditor();return;}\n')
    rep('            if(!editorCollection)return;\n            while(editorCollection.numChildren)editorCollection.removeChildAt(0);\n',
        '            if(!editorCollection)return;\n            if(skin==3){while(previewLayer.numChildren)previewLayer.removeChildAt(0);redrawBetaCollection();return;}\n            while(editorCollection.numChildren)editorCollection.removeChildAt(0);\n')
    rep('            editorPreviewId=c.templateId;\n            while(editorPreview.numChildren)editorPreview.removeChildAt(0);\n',
        '            editorPreviewId=c.templateId;\n            while(editorPreview.numChildren)editorPreview.removeChildAt(0);\n'
        '            if(skin==3){battlePreview=editorPreview;battlePreviewKey="";var view:Object={templateId:c.templateId,title:c.title,power:c.power,side:1,zone:64,tokens:0,description:c.description,timer:null};drawBetaSidePreview(view,{description:c.description});return;}\n')
    if crlf: t = t.replace('\n', '\r\n')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))
    print('deck editor applied to', SRC)

if __name__ == '__main__':
    main()

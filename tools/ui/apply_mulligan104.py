"""Stage 104: Gwent Beta mulligan (UIBattleChoicePrefab / CardPicker) for skin 3."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'BetaGwent/ui/src/BetaGwentBoard.as'
MARK = '// stage104-mulligan'
METHODS = r'''
        // stage104-mulligan: parchment 5x2, wooden preview panel, plaque, ЗАКОНЧИТЬ ОБМЕН / СКРЫТЬ КАРТЫ.
        private var mulliganHidden:Boolean=false;
        private var mulliganConfirm:Boolean=false;
        private function finishMulligan():void
        {
            mulliganConfirm=false;mulliganHidden=false;
            var finish:Function=requestAction("OnBetaGwentRequestFinish");finish();
        }
        private function drawBetaMulligan():void
        {
            content.addChild(choiceLayer);
            choiceLayer.graphics.clear();
            var remaining:int=Math.max(0,requestMax-requestCount);
            var plaque:Sprite=new Sprite();plaque.mouseEnabled=false;plaque.mouseChildren=false;if(!mulliganHidden)choiceLayer.addChild(plaque);
            paintArt(plaque,BetaGwentHud104.CHAIN,14,60,650,-6);paintArt(plaque,BetaGwentHud104.CHAIN,14,60,1256,-6);
            betaNine(plaque,-1400,690,74,615,38);
            betaLabel(plaque,"ВЫБЕРИТЕ КАРТУ, КОТОРУЮ ХОТИТЕ ОБМЕНЯТЬ. ["+requestCount+" ИЗ "+requestMax+"]",615,62,690,19,0xF2EEE4,BetaGwentFonts.BODY,false,"center",1);
            if(mulliganHidden){
                betaWideButton("Показать карты",75,858,255,true,function():void{mulliganHidden=false;render();});
                choiceLayer.addChild(content.getChildAt(content.numChildren-1));
                return;
            }
            choiceLayer.graphics.beginFill(0,.45);choiceLayer.graphics.drawRect(0,0,1920,1080);choiceLayer.graphics.endFill();
            choiceLayer.graphics.beginFill(0x0D0F10,.97);choiceLayer.graphics.drawRect(30,135,1432,825);choiceLayer.graphics.endFill();
            choiceLayer.graphics.lineStyle(3,0x4A4D4F,1);choiceLayer.graphics.drawRect(30,135,1432,825);
            choiceLayer.graphics.lineStyle(1,0x7C7F80,.8);choiceLayer.graphics.drawRect(40,145,1412,805);
            paintArt(choiceLayer,BetaGwentHud104.PARCHMENT,1373,765,52,165);
            paintArt(choiceLayer,BetaGwentHud104.WOOD_PANEL,405,822,1477,138);
            paintArt(choiceLayer,BetaGwentHud104.PREVIEW_SLOT,285,398,1545,177);
            var perPage:int=10;var pages:int=Math.max(1,Math.ceil(requestCards.length/perPage));
            choicePage=Math.min(choicePage,pages-1);
            var first:int=choicePage*perPage;var shown:int=Math.min(perPage,requestCards.length-first);
            var cw:Number=177,ch:Number=Math.round(177/BETA_CARD_ASPECT);
            for(var i:int=first;i<first+shown;i++){
                var c:Object=requestCards[i];var slot:int=i-first;
                var inRow:int=Math.min(5,shown-(slot<5?0:5));
                var x:Number=738-(inRow*234-57)/2+(slot%5)*234,y:Number=slot<5?300:578;
                var p:Sprite=new Sprite();p.x=x;p.y=y;choiceLayer.addChild(p);
                p.graphics.beginFill(0x000000,.35);p.graphics.drawRect(4,6,cw,ch);p.graphics.endFill();
                var handCard:Object=null;for each(var hc:Object in cards)if(hc.id==c.id){handCard=hc;break;}
                if(c.revealed){
                    paintBetaFace(p,c.templateId,cw,ch,1);
                    if(handCard&&handCard.power>0)betaPowerField(p,String(handCard.power),cw,ch,powerColor(handCard));
                    var view:Object=handCard||c;if(!view.side)view.side=1;
                    attachInspect(p,view,cardDetails[c.id],cw,ch);
                }else paintCardBack(p,cw,ch,1);
                if(c.selected||keyboardFocusId==c.id)p.filters=[new GlowFilter(0x34C6FF,1,22,22,3,2)];
                attachRequestCard(p,c.id);
            }
            if(pages>1){
                betaWideButton("‹",60,880,70,ready&&choicePage>0,function():void{choicePage--;render();});
                betaWideButton("›",1360,880,70,ready&&choicePage+1<pages,function():void{choicePage++;render();});
            }
            var buttons:int=content.numChildren;
            betaWideButton("Закончить обмен",682,1002,278,ready&&requestFinish,function():void{
                if(remaining>0){mulliganConfirm=true;render();}else finishMulligan();});
            betaWideButton("Скрыть карты",1005,1002,238,true,function():void{mulliganHidden=true;render();});
            while(content.numChildren>buttons)choiceLayer.addChild(content.getChildAt(buttons));
            if(battlePreview)choiceLayer.addChild(battlePreview);
            if(mulliganConfirm)drawBetaConfirm("ОБМЕН КАРТ","Закончить обмен? Можно заменить ещё "+remaining+".",finishMulligan,function():void{mulliganConfirm=false;render();});
        }
        private function drawBetaConfirm(title:String,body:String,yes:Function,no:Function):void
        {
            var layer:Sprite=new Sprite();choiceLayer.addChild(layer);
            layer.graphics.beginFill(0,.6);layer.graphics.drawRect(0,0,1920,1080);layer.graphics.endFill();
            layer.addEventListener(MouseEvent.CLICK,function(e:MouseEvent):void{e.stopPropagation();});
            paintArt(layer,BetaGwentHud104.POPUP,700,260,610,410);
            var bar:Sprite=new Sprite();layer.addChild(bar);paintArt(bar,BetaGwentHud104.POPUP_TITLE,660,52,630,428);
            betaLabel(layer,title,610,436,700,26,0xEDE9E2,BetaGwentFonts.TITLE,true,"center",6);
            var text1:TextField=text(layer,body,650,502,620,20,0xE8E4DA);text1.height=60;betaFace(BetaGwentFonts.BODY,text1,20,0xE8E4DA,false,"center");
            var start:int=content.numChildren;
            betaWideButton("Да",700,580,240,true,yes);betaWideButton("Нет",980,580,240,true,no);
            while(content.numChildren>start)layer.addChild(content.getChildAt(start));
        }
'''

def main():
    raw = SRC.read_bytes(); bom = raw.startswith(b'\xef\xbb\xbf'); t = raw.decode('utf-8-sig'); crlf = '\r\n' in t; t = t.replace('\r\n', '\n')
    if MARK in t: raise SystemExit('already applied')
    def rep(a, b):
        nonlocal t
        if t.count(a) != 1: raise SystemExit('anchor %d: %r' % (t.count(a), a[:90]))
        t = t.replace(a, b)
    rep('        private function drawChoices():void\n        {\n',
        METHODS.lstrip('\n') + '        private function drawChoices():void\n        {\n            if(skin==3&&requestKind==1&&!pileChoice&&!templateChoice&&!handPowerChoice&&!graveyardChoice){drawBetaMulligan();return;}\n')
    rep('            if(!playing&&requestId>0){\n                betaNine(content,-1400,976,43,430,158);',
        '            if(!playing&&requestId>0&&!(skin==3&&requestKind==1)){\n                betaNine(content,-1400,976,43,430,158);')
    t = t.replace('        // stage104-mulligan: parchment', '        ' + MARK + '\n        // stage104-mulligan: parchment', 1)
    if crlf: t = t.replace('\n', '\r\n')
    SRC.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))
    print('mulligan applied')

if __name__ == '__main__':
    main()

"""Apply reviewed RC3 UI changes to the isolated sources; preserve BOM/CRLF."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];BUILD=ROOT/'BetaGwent/build/release082-rc3'
def read(p):return p.read_text('utf-8-sig').replace('\r\n','\n')
def write(p,s):p.write_bytes(b'\xef\xbb\xbf'+s.replace('\r\n','\n').replace('\n','\r\n').encode('utf8'))
def rep(s,a,b):
    assert s.count(a)==1,a[:160];return s.replace(a,b)
def method(s,name):
    a=s.index('        private function '+name+'(');b=s.index('{',a);i=b+1;depth=1
    while depth:
        if s[i]=='{':depth+=1
        if s[i]=='}':depth-=1
        i+=1
    return s[a:i]
def board(s):
    old=method(s,'drawDeckExchangeButtons')
    new='''        private function drawDeckExchangeButtons():void
        {
            if(skin==3){
                betaWideButton("Импорт колоды",editingDeck?946:966,1002,220,ready,function():void{openDeckExchange(true);});
                if(editingDeck)betaWideButton("Экспорт колоды",1182,1002,220,ready,function():void{openDeckExchange(false);});
                return;
            }
            editorSmallButton(content,"Импорт колоды",1448,78,198,42,ready,function():void{openDeckExchange(true);});
            if(editingDeck)editorSmallButton(content,"Экспорт колоды",1658,78,210,42,ready,function():void{openDeckExchange(false);});
        }'''
    s=rep(s,old,new)
    for a,b in [('"Сохранить",560,1002,260','"Сохранить",474,1002,240'),('"Очистить",840,1002,240','"Очистить",730,1002,200'),('"Отмена",1100,1002,240','"Отмена",1418,1002,240'),
                ('"Заменить колоду",560,1002,300','"Заменить колоду",474,1002,240'),('"Редактировать",880,1002,260','"Редактировать",730,1002,220'),('"Все карты",1160,1002,200','"Все карты",1202,1002,180'),('"Выход",1380,1002,200','"Выход",1398,1002,180'),('"Бочки · "+unopenedKegs,1600,1002,260','"Бочки · "+unopenedKegs,1594,1002,240')]:
        s=rep(s,a,b)
    a='if(summary)betaLabel(content,summary,474,940,972,16,0xE8D3A6,BetaGwentFonts.BODY,false,"center").height=22;'
    s=rep(s,a,'if(summary){var status:TextField=text(content,summary,498,900,920,18,0xE8D3A6);status.multiline=true;status.wordWrap=true;status.height=44;betaFace(BetaGwentFonts.BODY,status,18,0xE8D3A6,false,"center");}')
    s=rep(s,'"Отменить карту",1488,918,388,48','"Отменить карту",1513,918,346,48')
    s=rep(s,'filtered.length,5,240,960,636,editorScroll178','filtered.length,5,240,960,574,editorScroll178')
    s=rep(s,'"collection",1448,306,636','"collection",1448,306,574')
    s=rep(s,'482,962,960,24,17','498,950,920,26,17')
    # Frame ornaments have a real inner border; keep labels/buttons inside it.
    s=rep(s,'var x:Number=56+column*580,y:Number=206+row*78;','var x:Number=64+column*578,y:Number=224+row*82;')
    old=method(s,'openControllerMenu');new=old.replace('"МЕНЮ БОЯ",56,28,1148,30','"МЕНЮ БОЯ",64,52,1132,30').replace('56+i*290,88,272,54','64+i*286,120,272,54').replace('56,310,1148,23','64,344,1132,22').replace('56,730,1148,19','64,692,1132,19').replace('56,804,1148,48','64,776,1132,48');s=rep(s,old,new)
    old=method(s,'requestBoardClose');new=old.replace('500,330,920,390','500,305,920,430').replace('34,30,850,32','64,52,792,30').replace('34,100,850,24','64,120,792,23').replace('.height=110','.height=110').replace('34,270,410,58','64,304,384,58').replace('476,270,410,58','472,304,384,58');s=rep(s,old,new)
    old=method(s,'requestEditorExit');new=old.replace('420,330,1080,390','420,305,1080,430').replace('34,30,1012,30','64,52,952,30').replace('34,104,1012,23','64,120,952,23').replace('34,270,318,58','64,304,304,58').replace('380,270,318,58','388,304,304,58').replace('726,270,318,58','712,304,304,58');s=rep(s,old,new)
    # The exchange status must participate in localization; the BG1 code stays opaque.
    s=rep(s,'BetaGwentTextLanguage.forget(exchangeMessage);exchangeMessage.height=360;','exchangeMessage.height=300;')
    old=method(s,'openDeckExchange');new=old.replace('32,26,1056,30','48,48,1024,30').replace('32,94,1056,23','48,116,1024,23').replace('32,220,1056,22','48,252,1024,22').replace('988,584,42,36','964,568,44,40').replace('1046,584,42,36','1028,568,44,40').replace('32,642,210,48','48,642,184,48').replace('254,642,240,48','248,642,224,48').replace('506,642,322,48','488,642,320,48').replace('32,642,280,48','48,642,280,48').replace('840,642,248,48','824,642,248,48');s=rep(s,old,new)
    # Translated status is assigned from its source each time (no double translation).
    import re
    s=re.sub(r'exchangeMessage\.text=("[^"\n]*");',r'BetaGwentTextLanguage.assign(exchangeMessage,\1);',s)
    s=rep(s,'exchangeMessage.text=message;exchangeMessage.scrollV=1;','BetaGwentTextLanguage.assign(exchangeMessage,message);exchangeMessage.scrollV=1;')
    return s
def controller(s):
    marker='        private function navigate(dir:int):void'
    helper='''        private function editorFooter(options:Array,current:Object):Object
        {
            var best:Object=null,distance:Number=Number.MAX_VALUE;
            var x:Number=current.rect.x+current.rect.width/2;
            for each(var node:Object in options)if(node.tag=="control"&&node.rect.y>=984){
                var d:Number=Math.abs(node.rect.x+node.rect.width/2-x);
                if(d<distance){distance=d;best=node;}
            }
            return best;
        }
'''
    s=rep(s,marker,helper+marker)
    old='if(row<shelf.offset||row+shelf.rowHeight>shelf.offset+shelf.height){invoke("shelfSelect",{pane:n.card.shelfPane,index:target});dirty=true;return;}'
    new='''if(row<shelf.offset||row+shelf.rowHeight>shelf.offset+shelf.height){
                            // The visible viewport is a navigation region. LB/RB and the right stick scroll it.
                            if(mode=="editor"&&dir==40){var footer:Object=editorFooter(allOptions,n);if(footer){select(footer);invoke("tickSound");return;}}
                            invoke("shelfSelect",{pane:n.card.shelfPane,index:target});dirty=true;return;
                        }'''
    return rep(s,old,new)
def main():
    for platform in ['nextgen','classic']:
        ui=BUILD/platform/'ui/src'
        write(ui/'BetaGwentBoard.as',board(read(ui/'BetaGwentBoard.as')))
        write(ui/'BetaGwentController.as',controller(read(ui/'BetaGwentController.as')))
    print('Patched editor navigation, layout and localized status assignments')
if __name__=='__main__':main()

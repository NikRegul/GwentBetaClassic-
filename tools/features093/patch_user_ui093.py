"""One-time reviewed edits over the pre-user-fixes board sources (fails if rerun)."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
for p in [ROOT/'BetaGwent/ui/src/BetaGwentBoard.as',ROOT/'tools/features091/BetaGwentBoard_classic093.as']:
    s=p.read_text('utf-8-sig')
    def change(a,b,count=1):
        global s
        assert s.count(a)==count,(p,a[:80],s.count(a));s=s.replace(a,b)
    change('private var npcDeckLabel:String="";','private function opponentName():String\n        {return BetaGwentReleaseText093.opponent(npcDisplayName,BetaGwentTextLanguage.language);}')
    change('npcDeckLabel=String(lines.length>1?lines[1]:lines[0]);','')
    s=s.replace('npcDeckLabel&&npcDeckLabel.length?npcDeckLabel:"Бой"','opponentName()').replace('+npcDeckLabel','+opponentName()').replace('?npcDeckLabel:', '?opponentName():').replace(':npcDeckLabel,',':opponentName(),').replace('+npcDisplayName+', '+opponentName()+')
    assert 'npcDeckLabel' not in s
    change('betaLabel(content,pickerSide==1?"ВАША КОЛОДА":"КОЛОДА СОПЕРНИКА",52,150,371,20,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",3);','if(pickerSide==2)betaLabel(content,"КОЛОДА СОПЕРНИКА",52,150,371,20,0xF2EEE4,BetaGwentFonts.TITLE,true,"center",3);')
    change('var y:Number=190;','var y:Number=pickerSide==1?150:190;')
    change('private var deckList178:Sprite;','private var deckList178:Sprite;\n        private var deckListTop178:Number=428;')
    change('new BetaGwentVirtualShelf178(list.length,1,40,372,480,deckScroll178)','new BetaGwentVirtualShelf178(list.length,1,40,372,908-deckListTop178,deckScroll178)')
    change('"deck",i,46,428,372,480','"deck",i,46,deckListTop178,372,908-deckListTop178')
    change('shelfBar178(deckList178,"deck",376,0,480);','shelfBar178(deckList178,"deck",376,0,908-deckListTop178);')
    change('{x:220,y:428+y}', '{x:220,y:deckListTop178+y}')
    change('deckList178=new Sprite();deckList178.x=46;deckList178.y=428;', 'deckListTop178=picked&&factionLeaders.length>1?428:378;\n            deckList178=new Sprite();deckList178.x=46;deckList178.y=deckListTop178;')
    change('        private function isMulliganHand():Boolean','''        // Hand-only legal requests use the full offer browser; board targets stay on the board.
        private function isCardOffer():Boolean
        {
            if(requestId<=0||requestKind!=2||requestPlayer!=1||rowRequest||canPlacePending()||requestCards.length==0)return false;
            for each(var option:Object in requestCards){
                var found:Boolean=false;
                for each(var live:Object in cards)if(live.id==option.id){if(live.zone!=8)return false;found=true;break;}
                if(!found)return false;
            }
            return true;
        }
        private function isChoiceTable():Boolean
        {return requestId>0&&(requestKind==1||isCardOffer());}
        private function cardOfferLabel(hint:Boolean=false):String
        {
            var key:String=requestSourceTemplate==162210?(hint?"keepHint":"keep"):
                requestSourceTemplate==162316||requestSourceTemplate==200163?(hint?"revealHint":"reveal"):(hint?"offerHint":"offer");
            return BetaGwentReleaseText093.label(key,BetaGwentTextLanguage.language);
        }
        private function isMulliganHand():Boolean''')
    for a,b in [
        ('requestId>0&&requestKind==1?"choice"','isChoiceTable()?"choice"'),
        ('requestId>0&&requestKind==1&&choiceTableHidden()','isChoiceTable()&&choiceTableHidden()'),
        ('if(requestId>0&&requestKind==1){if(skin==3)','if(isChoiceTable()){if(skin==3)'),
        ('requestKind==1&&skin==3&&node&&node.card','isChoiceTable()&&skin==3&&node&&node.card'),
        ('requestId>0&&requestKind==1&&!detailOpen','isChoiceTable()&&!detailOpen'),
        ('if(requestKind==1&&skin==3&&node.card)','if(isChoiceTable()&&skin==3&&node.card)'),
        ('else if(requestKind==1&&skin==3){var choiceFocus','else if(isChoiceTable()&&skin==3){var choiceFocus'),
        ('if(requestKind==1)choicePage=','if(isChoiceTable())choicePage='),
        ('if(!playing&&requestId>0 && requestKind==1) drawChoices();','if(!playing&&isChoiceTable()) drawChoices();'),
        ('!(skin==3&&requestKind==1)','!(skin==3&&isChoiceTable())'),
        ('requestKind==1&&skin==3||dragging','isChoiceTable()&&skin==3||dragging'),
        ('if(requestId==0||requestKind!=1||mulliganConfirm','if(!isChoiceTable()||mulliganConfirm'),
        ('if(skin==3&&requestKind==1){if(isMulliganHand())','if(skin==3&&isChoiceTable()){if(isMulliganHand())')]:
        assert a in s,(p,a);s=s.replace(a,b)
    change('var heading:String=templateChoice?', 'var heading:String=isCardOffer()?cardOfferLabel():templateChoice?')
    change('var hint:String=readableText(requestMessage);','var hint:String=isCardOffer()?cardOfferLabel(true):readableText(requestMessage);')
    change('            var heading:String=isCardOffer()', '            choiceLayer.graphics.beginFill(0,.72);choiceLayer.graphics.drawRect(-WIDE_PAD,0,1920+2*WIDE_PAD,1080);choiceLayer.graphics.endFill();\n            var heading:String=isCardOffer()')
    a='text(modal,templateChoice?(rowMode==13?'
    assert s.count(a)==3
    s=s.replace(a,'text(modal,isCardOffer()?cardOfferLabel():templateChoice?(rowMode==13?',1)
    s=s.replace(a,'text(modal,isCardOffer()?cardOfferLabel(true):templateChoice?(rowMode==13?')
    raw=b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8');p.write_bytes(raw)
    if p==ROOT/'BetaGwent/ui/src/BetaGwentBoard.as':
        for folder in COPIES[1:]:(ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as').write_bytes(raw)
print('Updated both platform board sources, five identical BOM/CRLF canonical copies.')

"""Reviewed one-time edit: explicit outcome captions for card choices (fails if rerun).

Udalryk, Thaler, Yaevinn, Ge'els, Shilard, hand discard/swap/consume and deck discard
say where the chosen and the remaining cards go. Other ability pile/offer choices show
the source card's own ability text instead of a generic line. Display only.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']
OLD_LABEL='''        private function cardOfferLabel(hint:Boolean=false):String
        {
            var key:String=requestSourceTemplate==162210?(hint?"keepHint":"keep"):
                requestSourceTemplate==162316||requestSourceTemplate==200163?(hint?"revealHint":"reveal"):(hint?"offerHint":"offer");
            return BetaGwentReleaseText093.label(key,BetaGwentTextLanguage.language);
        }
'''
NEW_LABEL='''        private function cardOfferLabel(hint:Boolean=false):String
        {
            var key:String=choiceCaptionKey(hint);
            if(!key)key=requestSourceTemplate==162316||requestSourceTemplate==200163?(hint?"revealHint":"reveal"):(hint?"offerHint":"offer");
            if(key=="offerHint"){var ability:String=sourceAbilityText();if(ability)return ability;}
            return BetaGwentReleaseText093.label(key,BetaGwentTextLanguage.language);
        }
        // Explicit outcome captions: where the chosen card and the remaining cards go.
        private function choiceCaptionKey(hint:Boolean):String
        {
            if(requestId<=0||requestPlayer!=1)return "";
            var hand:Boolean=isCardOffer();var pile:Boolean=pileChoice&&!hand;var base:String="";var note:String="";
            switch(requestSourceTemplate){
                case 162210:if(hand){base="keep";note="keepHint";}break;
                case 200071:if(hand){base="keep";note="keepGiveHint";}break;
                case 152214:if(pile){base="drawOne";note="drawDiscardHint";}break;
                case 122203:case 142203:if(pile){base="drawOne";note="drawReturnHint";}break;
                case 131102:if(pile){base="playOne";note="playTopHint";}break;
                case 112211:case 152103:case 152213:if(hand){base="discardHand";note="discardHandHint";}break;
                case 112212:case 122204:case 142303:case 201638:case 200209:case 200165:case 200048:if(hand){base="swapHand";note="swapHandHint";}break;
                case 132216:if(hand){base="consumeHand";note="consumeHandHint";}break;
                case 152106:case 200036:case 200159:if(pile){base="discardDeck";note="discardDeckHint";}break;
                case 112208:if(hand){base="offer";note="copyBothHint";}break;
            }
            return hint?note:base;
        }
        private function sourceAbilityText():String
        {
            var original:Object=requestSourceTemplate>0?BetaGwentCardText.find(requestSourceTemplate):null;
            var value:String=original&&original.description?readableText(String(original.description)):"";
            return value.split("\\n").join(" ");
        }
        private function choiceHeading(fallback:String):String
        {
            var key:String=choiceCaptionKey(false);
            return key?BetaGwentReleaseText093.label(key,BetaGwentTextLanguage.language):fallback;
        }
        private function choiceHint(fallback:String):String
        {
            var key:String=choiceCaptionKey(true);
            if(key)return BetaGwentReleaseText093.label(key,BetaGwentTextLanguage.language);
            if(pileChoice&&rowMode==14){var ability:String=sourceAbilityText();if(ability)return ability;}
            return fallback;
        }
'''
EDITS=[
 (OLD_LABEL,NEW_LABEL),
 ('            hint+=" · Осталось выбрать: "',
  '            if(pileChoice&&!isCardOffer()){heading=choiceHeading(heading);hint=choiceHint(hint);}\n            hint+=" · Осталось выбрать: "'),
 ('text(modal,isCardOffer()?cardOfferLabel():templateChoice?',
  'text(modal,isCardOffer()?cardOfferLabel():pileChoice?choiceHeading(rowMode==14?"Выберите карту для способности":"Выберите карту для розыгрыша"):templateChoice?'),
 ('text(modal,isCardOffer()?cardOfferLabel(true):templateChoice?(rowMode==13?"Наведите',
  'text(modal,isCardOffer()?cardOfferLabel(true):pileChoice?choiceHint(rowMode==14?requestMessage:"Выбранная карта будет разыграна из колоды или сброса. Для отряда затем выберите место в ряду."):templateChoice?(rowMode==13?"Наведите'),
]
def main():
    for p in [ROOT/'BetaGwent/ui/src/BetaGwentBoard.as',ROOT/'tools/features091/BetaGwentBoard_classic093.as']:
        raw=p.read_bytes();assert raw.startswith(b'\xef\xbb\xbf') and b'\r\n' in raw,p
        s=raw[3:].decode('utf8').replace('\r\n','\n')
        assert 'choiceCaptionKey' not in s,'already patched: '+str(p)
        for a,b in EDITS:
            assert s.count(a)==1,(p,a[:70],s.count(a));s=s.replace(a,b)
        out=b'\xef\xbb\xbf'+s.replace('\n','\r\n').encode('utf8');p.write_bytes(out)
        if p.name=='BetaGwentBoard.as':
            for folder in COPIES[1:]:(ROOT/'BetaGwent/ui'/folder/'BetaGwentBoard.as').write_bytes(out)
    print('Choice captions added to both platform boards; five identical BOM/CRLF canonical copies.')
if __name__=='__main__':main()

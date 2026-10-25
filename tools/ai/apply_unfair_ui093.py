"""Add the explicit fourth difficulty; preserve all five BOM/CRLF UI copies."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']


def main():
    paths=[ROOT/'BetaGwent/ui'/copy/'BetaGwentBoard.as' for copy in COPIES]
    assert len({p.read_bytes() for p in paths})==1
    text=paths[0].read_text('utf-8-sig')
    if 'private function unfairDifficultyText(' in text:
        from apply_playtest_ui093 import main as finish
        finish();return
    old='{id:"difficulty",title:"Сложность ИИ: "+difficultyName(),enabled:true,action:cycleDifficulty},'
    new='{id:"difficulty",title:"Сложность ИИ: "+difficultyName(),enabled:!(originalDifficultyInMatch()&&difficultyIndex==4),action:cycleDifficulty,reason:unfairDifficultyText(true)},'
    assert text.count(old)==1;text=text.replace(old,new)
    assert text.count('if(difficulty>=1&&difficulty<=3)')==1
    text=text.replace('if(difficulty>=1&&difficulty<=3)','if(difficulty>=1&&difficulty<=4)')
    old='private function difficultyName():String{return difficultyIndex==1?"лёгкая":difficultyIndex==2?"средняя":"высокая";}'
    new='private function difficultyName():String{return difficultyIndex==1?"лёгкая":difficultyIndex==2?"средняя":difficultyIndex==4?unfairDifficultyText(false):"высокая";}'
    assert text.count(old)==1;text=text.replace(old,new)
    assert text.count('difficultyIndex=difficultyIndex%3+1;')==1
    text=text.replace('difficultyIndex=difficultyIndex%3+1;',
      'if(originalDifficultyInMatch()){if(difficultyIndex==4)return;difficultyIndex=difficultyIndex%3+1;}else difficultyIndex=difficultyIndex%4+1;')
    names=['','Нечестный','Unfair','Unfair','Déloyal','Sleale','Nieuczciwy','Desleal','Desleal','Injusto','不公平','불공정','不公平','不公平']
    hints=['',
      'В режиме «Нечестный» ИИ видит вашу руку и колоду. Выбор режима — до начала партии.',
      'In Unfair mode, the AI sees your hand and deck. Select it before starting a match.',
      'Im Modus Unfair sieht die KI deine Hand und dein Deck. Vor Partiebeginn auswählen.',
      'En mode Déloyal, l’IA voit votre main et votre deck. À choisir avant la partie.',
      'In modalità Sleale, l’IA vede la tua mano e il tuo mazzo. Scegli prima della partita.',
      'W trybie Nieuczciwy SI widzi twoją rękę i talię. Wybierz go przed rozpoczęciem partii.',
      'En modo Desleal, la IA ve tu mano y tu mazo. Elígelo antes de empezar la partida.',
      'En modo Desleal, la IA ve tu mano y tu mazo. Elígelo antes de empezar la partida.',
      'No modo Injusto, a IA vê sua mão e seu baralho. Escolha antes de começar a partida.',
      '不公平モードでは、AIはあなたの手札とデッキを見ることができます。対戦開始前に選択してください。',
      '불공정 모드에서는 AI가 내 손패와 덱을 볼 수 있습니다. 대전 시작 전에 선택하세요.',
      '在不公平模式下，AI可以看到你的手牌和牌组。请在对局开始前选择。',
      '在不公平模式下，AI可以看到你的手牌和牌組。請在對局開始前選擇。']
    helper='''        private function originalDifficultyInMatch():Boolean
        {return round>0&&(flags>>4)==0&&!selectingDecks&&!editingDeck&&!browsingCatalog&&!kegOpen&&!effectGallery;}
        private function unfairDifficultyText(details:Boolean):String
        {
            var labels:Array=LABELS;
            var hints:Array=HINTS;
            var language:int=BetaGwentTextLanguage.language;if(language<1||language>13)language=1;
            var result:String=String(details?hints[language]:labels[language]);BetaGwentTextLanguage.protect(result);return result;
        }
'''.replace('LABELS',json.dumps(names,ensure_ascii=False)).replace('HINTS',json.dumps(hints,ensure_ascii=False))
    marker='        private function cycleDifficulty():void'
    assert text.count(marker)==1;text=text.replace(marker,helper+marker)
    text=text.replace('// Opponent difficulty: 1 easy, 2 normal, 3 hard (saved with the Witcher save).',
                      '// Opponent difficulty: 1 easy, 2 normal, 3 hard, 4 original Beta with hidden information.')
    raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
    for p in paths:p.write_bytes(raw)
    assert b'\n' not in raw.replace(b'\r\n',b'')
    print('Fourth difficulty and information tooltip:13 languages; five identical BOM/CRLF copies.')
    from apply_playtest_ui093 import main as finish
    finish()


if __name__=='__main__':main()

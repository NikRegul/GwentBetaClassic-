"""Apply the requested Classic label, pre-battle setting and direct row focus."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
COPIES=['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']

def main():
    paths=[ROOT/'BetaGwent/ui'/c/'BetaGwentBoard.as' for c in COPIES]
    assert len({p.read_bytes() for p in paths})==1
    text=paths[0].read_text('utf-8-sig')
    old=['','Нечестный','Unfair','Unfair','Déloyal','Sleale','Nieuczciwy','Desleal','Desleal','Injusto','不公平','불공정','不公平','不公平']
    names=['','Классическая','Classic','Klassisch','Classique','Classica','Klasyczny','Clásica','Clásica','Clássica','クラシック','클래식','经典','經典']
    before=json.dumps(old,ensure_ascii=False);after=json.dumps(names,ensure_ascii=False)
    if before in text:
        text=text.replace(before,after)
        for a,b in zip(old[1:],names[1:]):text=text.replace(a,b)
    hints=['','На классической сложности ИИ беты видит вашу руку и колоду. Выберите сложность до начала партии.',
           'On Classic difficulty, the Beta AI sees your hand and deck. Select difficulty before starting a match.',
           'Auf klassischer Schwierigkeit sieht die Beta-KI deine Hand und dein Deck. Vor Partiebeginn auswählen.',
           'En difficulté classique, l’IA bêta voit votre main et votre deck. À choisir avant la partie.',
           'A difficoltà classica, la IA beta vede la tua mano e il tuo mazzo. Scegli prima della partita.',
           'Na klasycznym poziomie SI bety widzi twoją rękę i talię. Wybierz przed rozpoczęciem partii.',
           'En dificultad clásica, la IA beta ve tu mano y tu mazo. Elígela antes de empezar la partida.',
           'En dificultad clásica, la IA beta ve tu mano y tu mazo. Elígela antes de empezar la partida.',
           'Na dificuldade clássica, a IA beta vê sua mão e seu baralho. Escolha antes de começar a partida.',
           'クラシック難易度では、ベータ版AIはあなたの手札とデッキを見ることができます。対戦開始前に選択してください。',
           '클래식 난이도에서는 베타 AI가 내 손패와 덱을 볼 수 있습니다. 대전 시작 전에 선택하세요.',
           '经典难度的测试版AI可以看到你的手牌和牌组。请在对局开始前选择难度。',
           '經典難度的測試版AI可以看到你的手牌和牌組。請在對局開始前選擇難度。']
    text=re.sub(r'var hints:Array=\[[^\n]*\];','var hints:Array='+json.dumps(hints,ensure_ascii=False)+';',text)
    if 'private function controllerRowSelection()' not in text:
        marker='        private function controllerContext():Object'
        helper='''        private function controllerRowSelection():Boolean
        {var rule:Object=playRules[selected];return rowRequest||canAct()&&selected>0&&rule&&int(rule.kind)==2;}
'''
        assert text.count(marker)==1;text=text.replace(marker,helper+marker)
        text=text.replace('rowRequest?"rows":','controllerRowSelection()?"rows":')
        text=text.replace('else controller.focusTag(canPlaceSelected()?"position":"target");','else controller.focusTag(canPlaceSelected()?"position":controllerRowSelection()?"row":"target");')
        text=text.replace('if(rowRequest||isCaranthirChoice()){controller.focusTag("row",direction);return;}',
                          'if(controllerRowSelection()||isCaranthirChoice()){controller.focusTag("row",direction);return;}')
        text=text.replace('!playing&&rowRequest&&requestId>0&&!detailOpen&&!pileOpen?"row":""',
                          '!playing&&controllerRowSelection()&&!detailOpen&&!pileOpen?"row":""')
    if 'difficultyName(),56,132,364,36' not in text:
        marker='            editorSmallButton(content,voiceChoiceLabel(),56,78,364,42,true,cycleVoiceLanguage);'
        assert text.count(marker)==1
        text=text.replace(marker,marker+'\n            if(selectingDecks)editorSmallButton(content,"Сложность ИИ: "+difficultyName(),56,132,364,36,ready,cycleDifficulty);')
    raw=b'\xef\xbb\xbf'+text.replace('\r\n','\n').replace('\n','\r\n').encode('utf8')
    for p in paths:p.write_bytes(raw)
    print('Classic label13 languages; pre-battle difficulty beside language; direct row focus; five BOM/CRLF sources.')

if __name__=='__main__':main()

"""Generate display-only choice text and NPC name aliases from permanent inputs."""
from pathlib import Path
import json,sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from localization89 import strings
CODES=['ru_ru','en_us','de_de','fr_fr','it_it','pl_pl','es_es','es_mx','pt_br','jp_jp','kr_kr','zh_cn','zh_tw']
TEXT={
 'offer':['Выберите карту','Choose a card','Wählt eine Karte','Choisissez une carte','Scegli una carta','Wybierz kartę','Elige una carta','Elige una carta','Escolha uma carta','カードを選択','카드 선택','选择一张牌','選擇一張牌'],
 'keep':['Оставьте одну карту','Keep one card','Behaltet eine Karte','Gardez une carte','Tieni una carta','Zatrzymaj jedną kartę','Quédate con una carta','Quédate con una carta','Fique com uma carta','残すカードを1枚選択','남길 카드 1장 선택','保留一张牌','保留一張牌'],
 'keepHint':['Выбранная карта останется в руке. Другая вернётся вниз колоды.','The selected card stays in your hand. The other returns to the bottom of your deck.','Die gewählte Karte bleibt auf der Hand. Die andere kommt unter euer Deck.','La carte choisie reste dans votre main. L’autre retourne au-dessous de votre jeu.','La carta scelta resta in mano. L’altra torna in fondo al mazzo.','Wybrana karta zostaje w ręce. Druga wraca na spód talii.','La carta elegida se queda en tu mano. La otra vuelve al fondo del mazo.','La carta elegida se queda en tu mano. La otra vuelve al fondo del mazo.','A carta escolhida fica na sua mão. A outra volta para o fundo do baralho.','選んだカードを手札に残し、もう1枚をデッキの一番下に戻します。','선택한 카드는 손에 남고, 다른 카드는 덱 맨 아래로 돌아갑니다.','选中的牌留在手中，另一张放回牌库底部。','選中的牌留在手中，另一張放回牌庫底部。'],
 'reveal':['Выберите карту для вскрытия','Choose a card to reveal','Wählt eine Karte zum Aufdecken','Choisissez une carte à révéler','Scegli una carta da rivelare','Wybierz kartę do ujawnienia','Elige una carta para revelar','Elige una carta para revelar','Escolha uma carta para revelar','公開するカードを選択','공개할 카드 선택','选择要揭示的牌','選擇要揭示的牌'],
 'revealHint':['Выберите карту. Скрытые карты соперника показаны рубашкой.','Choose a card. Hidden opposing cards are shown face down.','Wählt eine Karte. Verdeckte gegnerische Karten bleiben verdeckt.','Choisissez une carte. Les cartes cachées adverses sont face cachée.','Scegli una carta. Le carte avversarie nascoste restano coperte.','Wybierz kartę. Ukryte karty przeciwnika są zakryte.','Elige una carta. Las cartas ocultas del rival se muestran boca abajo.','Elige una carta. Las cartas ocultas del rival se muestran boca abajo.','Escolha uma carta. Cartas ocultas do oponente aparecem viradas para baixo.','カードを選択。相手の非公開カードは裏向きで表示されます。','카드를 선택하세요. 상대의 숨겨진 카드는 뒷면으로 표시됩니다.','选择一张牌。对手的隐藏牌以牌背显示。','選擇一張牌。對手的隱藏牌以牌背顯示。'],
 'offerHint':['Выберите одну из предложенных карт.','Choose one of the offered cards.','Wählt eine der angebotenen Karten.','Choisissez l’une des cartes proposées.','Scegli una delle carte proposte.','Wybierz jedną z proponowanych kart.','Elige una de las cartas ofrecidas.','Elige una de las cartas ofrecidas.','Escolha uma das cartas oferecidas.','提示されたカードから1枚を選択してください。','제시된 카드 중 1장을 선택하세요.','从提供的牌中选择一张。','從提供的牌中選擇一張。'],
 'drawOne':['Возьмите одну карту', 'Draw one card', 'Zieht eine Karte', 'Piochez une carte', 'Pesca una carta', 'Dobierz jedną kartę', 'Saca una carta', 'Roba una carta', 'Compre uma carta', '引くカードを1枚選択', '뽑을 카드 1장 선택', '抽取 1 张牌', '抽取 1 張卡牌'],
 'drawDiscardHint':['Выбранная карта уйдёт в руку, вторая — в сброс.', 'The selected card goes to your hand. The other goes to your graveyard.', 'Die gewählte Karte kommt auf eure Hand, die andere auf den Friedhof.', 'La carte choisie va dans votre main, l’autre au cimetière.', 'La carta scelta va in mano, l’altra nel cimitero.', 'Wybrana karta trafi do ręki, a druga na cmentarz.', 'La carta elegida va a tu mano y la otra, al cementerio.', 'La carta elegida va a tu mano y la otra, al cementerio.', 'A carta escolhida vai para a sua mão e a outra, para o cemitério.', '選んだカードは手札に加わり、もう1枚は墓場に送られます。', '선택한 카드는 손으로 가고, 나머지는 묘지로 갑니다.', '选中的牌加入手牌，另一张进入墓场。', '選中的卡牌加入手牌，另一張進入墓場。'],
 'drawReturnHint':['Выбранная карта уйдёт в руку, вторая останется в колоде.', 'The selected card goes to your hand. The other stays in your deck.', 'Die gewählte Karte kommt auf eure Hand, die andere bleibt in eurem Deck.', 'La carte choisie va dans votre main, l’autre reste dans votre jeu.', 'La carta scelta va in mano, l’altra resta nel mazzo.', 'Wybrana karta trafi do ręki, a druga zostanie w talii.', 'La carta elegida va a tu mano y la otra se queda en tu baraja.', 'La carta elegida va a tu mano y la otra se queda en tu mazo.', 'A carta escolhida vai para a sua mão e a outra fica no baralho.', '選んだカードは手札に加わり、もう1枚はデッキに残ります。', '선택한 카드는 손으로 가고, 나머지는 덱에 남습니다.', '选中的牌加入手牌，另一张留在牌组中。', '選中的卡牌加入手牌，另一張留在牌組中。'],
 'playOne':['Разыграйте одну карту', 'Play one card', 'Spielt eine Karte aus', 'Jouez une carte', 'Gioca una carta', 'Zagraj jedną kartę', 'Juega una carta', 'Juega una carta', 'Jogue uma carta', 'プレイするカードを1枚選択', '사용할 카드 1장 선택', '打出 1 张牌', '打出 1 張卡牌'],
 'playTopHint':['Выбранная карта будет разыграна, вторая ляжет на верх колоды.', 'The selected card is played. The other goes to the top of your deck.', 'Die gewählte Karte wird ausgespielt, die andere kommt oben auf euer Deck.', 'La carte choisie est jouée, l’autre est placée au-dessus de votre jeu.', 'La carta scelta viene giocata, l’altra va in cima al mazzo.', 'Wybrana karta zostanie zagrana, a druga trafi na wierzch talii.', 'La carta elegida se juega y la otra va a la parte superior de tu baraja.', 'La carta elegida se juega y la otra va a la parte superior de tu mazo.', 'A carta escolhida é jogada e a outra vai para o topo do baralho.', '選んだカードをプレイし、もう1枚はデッキの一番上に置かれます。', '선택한 카드를 사용하고, 나머지는 덱 맨 위로 갑니다.', '打出选中的牌，另一张放到牌组顶部。', '打出選中的卡牌，另一張放到牌組頂部。'],
 'keepGiveHint':['Выбранная карта останется у вас, вторая уйдёт в руку соперника.', 'You keep the selected card. The other goes to your opponent’s hand.', 'Ihr behaltet die gewählte Karte, die andere geht auf die Hand des Gegners.', 'Vous gardez la carte choisie, l’autre va dans la main de votre adversaire.', 'Tieni la carta scelta, l’altra va nella mano dell’avversario.', 'Zatrzymujesz wybraną kartę, a druga trafi do ręki przeciwnika.', 'Te quedas con la carta elegida y la otra va a la mano de tu rival.', 'Te quedas con la carta elegida y la otra va a la mano de tu rival.', 'Você fica com a carta escolhida e a outra vai para a mão do oponente.', '選んだカードを残し、もう1枚は対戦相手の手札に渡ります。', '선택한 카드는 갖고, 나머지는 상대의 손으로 갑니다.', '保留选中的牌，另一张交给对手。', '保留選中的卡牌，另一張交給對手。'],
 'discardHand':['Сбросьте карту из руки', 'Discard a card from your hand', 'Verwerft eine Karte von der Hand', 'Défaussez une carte de votre main', 'Scarta una carta dalla mano', 'Odrzuć kartę z ręki', 'Descarta una carta de tu mano', 'Descarta una carta de tu mano', 'Descarte uma carta da mão', '手札から破棄するカードを選択', '손에서 버릴 카드 선택', '从手牌中丢弃 1 张牌', '從手牌中丟棄 1 張卡牌'],
 'discardHandHint':['Выбранная карта уйдёт из руки в сброс.', 'The selected card goes from your hand to your graveyard.', 'Die gewählte Karte kommt von der Hand auf den Friedhof.', 'La carte choisie passe de votre main au cimetière.', 'La carta scelta passa dalla mano al cimitero.', 'Wybrana karta trafi z ręki na cmentarz.', 'La carta elegida pasa de tu mano al cementerio.', 'La carta elegida pasa de tu mano al cementerio.', 'A carta escolhida sai da sua mão e vai para o cemitério.', '選んだカードは手札から墓場に送られます。', '선택한 카드는 손에서 묘지로 갑니다.', '选中的牌将从手牌进入墓场。', '選中的卡牌將從手牌進入墓場。'],
 'swapHand':['Выберите карту для замены', 'Choose a card to swap', 'Wählt eine Karte zum Tauschen', 'Choisissez une carte à échanger', 'Scegli una carta da sostituire', 'Wybierz kartę do wymiany', 'Elige una carta para intercambiar', 'Elige una carta para intercambiar', 'Escolha uma carta para trocar', '交換するカードを選択', '교체할 카드 선택', '选择要交换的牌', '選擇要替換的卡牌'],
 'swapHandHint':['Выбранная карта вернётся в колоду, взамен вы получите другую.', 'The selected card returns to your deck and you get another card instead.', 'Die gewählte Karte kommt zurück ins Deck, dafür erhaltet ihr eine andere.', 'La carte choisie retourne dans votre jeu et vous en obtenez une autre.', 'La carta scelta torna nel mazzo e ne ricevi un’altra al suo posto.', 'Wybrana karta wróci do talii, a w zamian otrzymasz inną.', 'La carta elegida vuelve a tu baraja y recibes otra a cambio.', 'La carta elegida vuelve a tu mazo y recibes otra a cambio.', 'A carta escolhida volta para o baralho e você recebe outra no lugar.', '選んだカードはデッキに戻り、代わりに別のカードを得ます。', '선택한 카드는 덱으로 돌아가고, 대신 다른 카드를 받습니다.', '选中的牌返回牌组，你将获得另一张牌。', '選中的卡牌返回牌組，你將獲得另一張卡牌。'],
 'consumeHand':['Поглотите отряд из руки', 'Consume a unit from your hand', 'Verzehrt eine Einheit von der Hand', 'Dévorez une unité de votre main', 'Consuma un’unità dalla mano', 'Pochłoń jednostkę z ręki', 'Consume una unidad de tu mano', 'Consume una unidad de tu mano', 'Consuma uma unidade da mão', '手札から捕食するユニットを選択', '손에서 섭취할 유닛 선택', '吞噬 1 张手牌中的单位牌', '吞噬我方手牌中 1 張單位牌'],
 'consumeHandHint':['Выбранный отряд исчезнет из руки, а эта карта усилится на его силу.', 'The selected unit leaves your hand, and this card is boosted by its power.', 'Die gewählte Einheit verschwindet von der Hand, diese Karte wird um ihre Stärke verbessert.', 'L’unité choisie quitte votre main et la présente unité est améliorée de sa force.', 'L’unità scelta lascia la mano e questa carta si potenzia della sua forza.', 'Wybrana jednostka zniknie z ręki, a ta karta zostanie wzmocniona o jej siłę.', 'La unidad elegida sale de tu mano y esta carta se potencia con su poder.', 'La unidad elegida sale de tu mano y esta carta se potencia con su poder.', 'A unidade escolhida sai da sua mão e esta carta é reforçada pelo poder dela.', '選んだユニットは手札から消え、このカードはその戦力値分のブーストを得ます。', '선택한 유닛은 손에서 사라지고, 이 카드는 그 전력만큼 증폭됩니다.', '选中的单位牌将从手牌中消失，此牌获得等同于其战力的增益。', '選中的單位牌將從手牌中消失，此牌以其戰力值提升自身戰力。'],
 'discardDeck':['Сбросьте карту из колоды', 'Discard a card from your deck', 'Verwerft eine Karte aus eurem Deck', 'Défaussez une carte de votre jeu', 'Scarta una carta dal mazzo', 'Odrzuć kartę z talii', 'Descarta una carta de tu baraja', 'Descarta una carta de tu mazo', 'Descarte uma carta do baralho', 'デッキから破棄するカードを選択', '덱에서 버릴 카드 선택', '从牌组丢弃 1 张牌', '從牌組丟棄 1 張卡牌'],
 'discardDeckHint':['Выбранная карта уйдёт из колоды в сброс.', 'The selected card goes from your deck to your graveyard.', 'Die gewählte Karte kommt aus dem Deck auf den Friedhof.', 'La carte choisie passe de votre jeu au cimetière.', 'La carta scelta passa dal mazzo al cimitero.', 'Wybrana karta trafi z talii na cmentarz.', 'La carta elegida pasa de tu baraja al cementerio.', 'La carta elegida pasa de tu mazo al cementerio.', 'A carta escolhida sai do baralho e vai para o cemitério.', '選んだカードはデッキから墓場に送られます。', '선택한 카드는 덱에서 묘지로 갑니다.', '选中的牌将从牌组进入墓场。', '選中的卡牌將從牌組進入墓場。'],
 'copyBothHint':['Базовую копию выбранного отряда получат оба игрока. Сам отряд останется в руке.', 'Both players get a default copy of the selected unit. The unit itself stays in your hand.', 'Beide Spieler erhalten eine Standardkopie der gewählten Einheit. Die Einheit selbst bleibt auf eurer Hand.', 'Les deux joueurs reçoivent une copie par défaut de l’unité choisie. L’unité elle-même reste dans votre main.', 'Entrambi i giocatori ricevono una copia originale dell’unità scelta. L’unità resta nella tua mano.', 'Obaj gracze otrzymają standardowy egzemplarz wybranej jednostki. Sama jednostka zostaje w ręce.', 'Ambos jugadores reciben una copia por defecto de la unidad elegida. La unidad se queda en tu mano.', 'Ambos jugadores reciben una copia predeterminada de la unidad elegida. La unidad se queda en tu mano.', 'Os dois jogadores recebem uma cópia padrão da unidade escolhida. A unidade continua na sua mão.', '両プレイヤーが選んだユニットの同名カードを1枚ずつ得ます。ユニット自体は手札に残ります。', '두 플레이어 모두 선택한 유닛의 기본 복사본을 받습니다. 유닛 자체는 손에 남습니다.', '双方各获得 1 张选中单位的原始同名牌，该单位仍留在手牌中。', '雙方各獲得 1 張選中單位牌的預設同名牌，該單位牌仍留在手牌中。']}
ROLES={
 'Купец':['Купец','Merchant','Kaufmann','Marchand','Mercante','Kupiec','Mercader','Mercader','Mercador','商人','상인','商人','商人'],
 'Торговец':['Торговец','Trader','Händler','Commerçant','Commerciante','Handlarz','Comerciante','Comerciante','Comerciante','交易商','무역상','行商','行商'],
 'Корчмарь':['Корчмарь','Innkeeper','Wirt','Aubergiste','Locandiere','Karczmarz','Posadero','Posadero','Estalajadeiro','宿屋の主人','여관 주인','旅店老板','旅店老闆'],
 'Кузнец':['Кузнец','Blacksmith','Schmied','Forgeron','Fabbro','Kowal','Herrero','Herrero','Ferreiro','鍛冶職人','대장장이','铁匠','鐵匠'],
 'Бронник':['Бронник','Armorer','Rüstungsschmied','Armurier','Armaiolo','Płatnerz','Armero','Armero','Armeiro','鎧職人','갑옷 장인','铸甲匠','鑄甲匠'],
 'Травник':['Травник','Herbalist','Kräuterkundler','Herboriste','Erborista','Zielarz','Herbolario','Herbolario','Herbalista','薬草医','약초사','草药医生','草藥醫生']}

def main():
    tables={'ru_ru':{},'en_us':strings()}
    for code in CODES[2:]:tables[code]=json.loads((ROOT/f'BetaGwent/build-inputs/authoring/languages137/ui/{code}.json').read_text('utf8'))
    mapping=json.loads((ROOT/'data/beta924/design/beta_ai_profiles093.json').read_text('utf8'))
    keys=[x['title'] for x in mapping['assignments'][:33]]+['Соперник','Купец','Торговец','Корчмарь','Кузнец','Бронник','Травник']
    names={};aliases={}
    for key in keys:
        row=ROLES.get(key) or [key]+[tables[code].get(key,key) for code in CODES[1:]]
        # Unknown proper names remain intact, never replaced with a profile/deck.
        names[key]=row
        for value in row:aliases[value.lower()]=key
    for key,variants in {
        'Золтан Хивай':['Золтан','Zoltan'],
        'Сигизмунд Дийкстра':['Дийкстра','Dijkstra'],
        'Кровавый Барон':['Барон','Baron'],
        'Ольгерд фон Эверек':['Ольгерд','Olgierd'],
        'Крах ан Крайт':['Крах','Crach'],
        'Лугос Безумный':['Лугос','Lugos'],
    }.items():
        assert key in names
        for value in variants:aliases[value.lower()]=key
    for key,row in TEXT.items():assert len(row)==13 and all(row)
    data=dict(languages=CODES,text=TEXT,opponents=names,aliases=aliases)
    target=ROOT/'data/beta924/design/release093_ui.json';target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
    literal=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
    source='''package {
    // Generated by tools/features093/generate_user_ui093.py. Display only.
    public class BetaGwentReleaseText093 {
        private static const TEXT:Object=TEXT_DATA;
        private static const NAMES:Object=NAME_DATA;
        private static const ALIASES:Object=ALIAS_DATA;
        public static function label(key:String,language:int):String {
            var row:Array=TEXT[key];return row?String(row[Math.max(0,Math.min(12,language-1))]):key;
        }
        public static function opponent(value:String,language:int):String {
            value=value?value.replace(/^\\s+|\\s+$/g,""):"";
            if(!value||/^(ch_fac_|p_.*(?:Practice|Challenge)|(?:AI|ИИ)\\s*[·:]|gwint_|nilfgaard_|northern_|skellige_|monsters_|scoiatael_)/i.test(value))value="Соперник";
            var key:String=ALIASES[value.toLowerCase()];
            if(key&&NAMES[key])return String(NAMES[key][Math.max(0,Math.min(12,language-1))]);
            return BetaGwentTextLanguage.translate(value,language);
        }
    }
}
'''.replace('TEXT_DATA',literal(TEXT)).replace('NAME_DATA',literal(names)).replace('ALIAS_DATA',literal(aliases))
    raw=b'\xef\xbb\xbf'+source.replace('\n','\r\n').encode('utf8')
    for folder in ['src','src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:(ROOT/'BetaGwent/ui'/folder/'BetaGwentReleaseText093.as').write_bytes(raw)
    print('Generated 13 languages,',len(names),'opponent names,',len(aliases),'cross-language aliases.')

if __name__=='__main__':main()

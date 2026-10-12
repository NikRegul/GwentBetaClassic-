"""Templated UI strings: card acquisition texts (NPC name inside) and AI deck descriptions."""
from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[2]
L = ROOT / 'BetaGwent/build/languages137'
LANGS = ['de_de', 'fr_fr', 'it_it', 'pl_pl', 'es_es', 'pt_br', 'jp_jp', 'kr_kr', 'zh_cn']
T = {
 'de_de': ('Diese Karte erhältst du von: {N} (Siegesbelohnung). Sie kann auch aus einem Fass kommen oder mit Fetzen hergestellt werden.', 'Startset. ', 'Startset. Besiege: {N}. Auch aus einem Fass beim Händler in der Festung des Barons erhältlich.', 'Benutzerregeln (deck_rules), angepasst an die strikte Beta 0.9.24. {T}', 'Recherchiertes Deck der Beta 0.9.24; {T}'),
 'fr_fr': ("Cette carte peut être obtenue auprès de : {N} (récompense de victoire). Elle peut aussi sortir d'un tonneau ou être fabriquée avec des fragments.", 'Kit de départ. ', "Kit de départ. Vaincre : {N}. Peut aussi sortir d'un tonneau chez le marchand de la forteresse du Baron.", 'Règles du joueur (deck_rules) adaptées à la Bêta 0.9.24 stricte. {T}', 'Deck étudié de la Bêta 0.9.24 ; {T}'),
 'it_it': ('Questa carta si ottiene da: {N} (premio per la vittoria). Può anche uscire da un barile o essere creata con i frammenti.', 'Set iniziale. ', 'Set iniziale. Sconfiggi: {N}. Può uscire anche da un barile del mercante nella fortezza del Barone.', 'Regole del giocatore (deck_rules) adattate alla Beta 0.9.24 rigorosa. {T}', 'Mazzo studiato della Beta 0.9.24; {T}'),
 'pl_pl': ('Kartę można zdobyć od: {N} (nagroda za zwycięstwo). Może też wypaść z beczki lub zostać stworzona za skrawki.', 'Zestaw startowy. ', 'Zestaw startowy. Pokonaj: {N}. Może też wypaść z beczki u kupca w twierdzy Barona.', 'Zasady gracza (deck_rules) dostosowane do ścisłej Bety 0.9.24. {T}', 'Zbadana talia z Bety 0.9.24; {T}'),
 'es_es': ('Esta carta se obtiene de: {N} (recompensa por victoria). También puede salir de un barril o fabricarse con fragmentos.', 'Conjunto inicial. ', 'Conjunto inicial. Derrota a: {N}. También puede salir de un barril del mercader de la fortaleza del Barón.', 'Reglas del jugador (deck_rules) adaptadas a la Beta 0.9.24 estricta. {T}', 'Mazo investigado de la Beta 0.9.24; {T}'),
 'pt_br': ('Esta carta pode ser obtida de: {N} (recompensa por vitória). Também pode sair de um barril ou ser criada com fragmentos.', 'Conjunto inicial. ', 'Conjunto inicial. Derrote: {N}. Também pode sair de um barril do mercador da fortaleza do Barão.', 'Regras do jogador (deck_rules) adaptadas à Beta 0.9.24 estrita. {T}', 'Baralho pesquisado da Beta 0.9.24; {T}'),
 'jp_jp': ('入手先：{N}（勝利報酬）。樽から出ることもあり、スクラップで作成することもできます。', 'スターターセット。', 'スターターセット。勝利対象：{N}。男爵の砦の商人の樽から出ることもあります。', 'プレイヤーの deck_rules を厳密なベータ 0.9.24 に合わせたもの。{T}', 'ベータ 0.9.24 の調査済みデッキ；{T}'),
 'kr_kr': ('획득처: {N} (승리 보상). 통에서 나오거나 조각으로 제작할 수도 있습니다.', '시작 세트. ', '시작 세트. 승리 대상: {N}. 남작의 요새 상인의 통에서도 나올 수 있습니다.', '플레이어의 deck_rules를 엄격한 베타 0.9.24에 맞춘 구성. {T}', '베타 0.9.24 조사 덱; {T}'),
 'zh_cn': ('获取途径：{N}（胜利奖励）。也可能从桶中开出，或用碎片制作。', '初始卡组。', '初始卡组。击败：{N}。也可能从男爵要塞商人处的桶中开出。', '按严格的 Beta 0.9.24 改编的玩家 deck_rules。{T}', 'Beta 0.9.24 研究卡组；{T}'),
}
T8 = dict(de_de='Besiege: {N}. Auch aus einem Fass erhältlich oder mit Fetzen herstellbar.', fr_fr="Vaincre : {N}. Peut aussi sortir d'un tonneau ou être fabriquée avec des fragments.", it_it='Sconfiggi: {N}. Può anche uscire da un barile o essere creata con i frammenti.', pl_pl='Pokonaj: {N}. Może też wypaść z beczki lub zostać stworzona za skrawki.', es_es='Derrota a: {N}. También puede salir de un barril o fabricarse con fragmentos.', pt_br='Derrote: {N}. Também pode sair de um barril ou ser criada com fragmentos.', jp_jp='勝利対象：{N}。樽から出ることもあり、スクラップで作成することもできます。', kr_kr='승리 대상: {N}. 통에서 나오거나 조각으로 제작할 수도 있습니다.', zh_cn='击败：{N}。也可能从桶中开出，或用碎片制作。')
T9 = dict(de_de='Diese Karte erhältst du von:{S}\n{N}', fr_fr='Cette carte peut être obtenue auprès de :{S}\n{N}', it_it='Questa carta si ottiene da:{S}\n{N}', pl_pl='Kartę można zdobyć od:{S}\n{N}', es_es='Esta carta se obtiene de:{S}\n{N}', pt_br='Esta carta pode ser obtida de:{S}\n{N}', jp_jp='入手先：{S}\n{N}', kr_kr='획득처:{S}\n{N}', zh_cn='获取途径：{S}\n{N}')
AI = dict(de_de='KI · ', fr_fr='IA · ', it_it='IA · ', pl_pl='SI · ', es_es='IA · ', pt_br='IA · ', jp_jp='AI · ', kr_kr='AI · ', zh_cn='AI · ')
NAMES = {  # RU -> de, fr, it, pl, es, pt, jp, kr, zh
 'Бернард Тулле': ['Bernard Tulle'] * 6 + ['バーナード・タル', '버나드 툴레', '伯纳德·图勒'],
 'Борец за права животных': ['Tierschützer', 'Défenseur des droits des animaux', 'Animalista', 'Obrońca praw zwierząt', 'Activista por los derechos de los animales', 'Ativista dos direitos dos animais', '動物愛護活動家', '동물 권리 운동가', '动物权益活动家'],
 'Вернон Роше': ['Vernon Roche'] * 6 + ['ヴァーノン・ロッシュ', '버넌 로슈', '弗农·罗契'],
 'Вимме Вивальди': ['Vimme Vivaldi'] * 6 + ['ヴィム・ヴィヴァルディ', '빔메 비발디', '维米·维瓦尔第'],
 'Второй соперник турнира в Туссенте': ['Zweiter Gegner im Turnier von Toussaint', 'Deuxième adversaire du tournoi de Toussaint', 'Secondo avversario del torneo di Toussaint', 'Drugi przeciwnik w turnieju w Toussaint', 'Segundo rival del torneo de Toussaint', 'Segundo oponente do torneio de Toussaint', 'トゥサンの大会の2人目の対戦相手', '투생 토너먼트의 두 번째 상대', '陶森特比武大会的第二位对手'],
 'Главарь пуристов после турнира в Туссенте': ['Anführer der Puristen nach dem Turnier von Toussaint', 'Chef des puristes après le tournoi de Toussaint', 'Capo dei puristi dopo il torneo di Toussaint', 'Przywódca purystów po turnieju w Toussaint', 'Líder de los puristas tras el torneo de Toussaint', 'Líder dos puristas após o torneio de Toussaint', 'トゥサンの大会後の純血派のリーダー', '투생 토너먼트 이후 순혈파 우두머리', '陶森特比武大会后的纯血派首领'],
 'Граф Тибальт': ['Graf Tybalt', 'Comte Tybalt', 'Conte Tybalt', 'Hrabia Tybalt', 'Conde Tybalt', 'Conde Tybalt', 'ティバルト伯爵', '티발트 백작', '提伯特伯爵'],
 'Гремист': ['Gremist'] * 6 + ['グレミスト', '그레미스트', '格雷米斯特'],
 'Золтан Хивай': ['Zoltan Chivay'] * 6 + ['ゾルタン・シヴェイ', '졸탄 치베이', '卓尔坦·齐瓦'],
 'Корчмарь на распутье': ['Wirt an der Wegkreuzung', 'Aubergiste du carrefour', 'Locandiere al crocevia', 'Karczmarz na rozstajach', 'Posadero del cruce', 'Taberneiro da encruzilhada', '十字路の宿屋の主人', '갈림길 여관 주인', '十字路口的旅店老板'],
 'Крах ан Крайт': ['Crach an Craite'] * 6 + ['クラフ・アン・クライト', '크라흐 안 크라이트', '克拉茨·安·克莱特'],
 'Кровавый Барон': ['Blutiger Baron', 'Baron Sanglant', 'Barone Sanguinario', 'Krwawy Baron', 'Barón Sanguinario', 'Barão Sangrento', '血まみれ男爵', '피의 남작', '血腥男爵'],
 'Ламберт': ['Lambert'] * 6 + ['ランバート', '램버트', '兰伯特'],
 'Лодочник из Рудника': ['Bootsbauer aus Oreton', "Charpentier naval d'Oreton", 'Costruttore di barche di Oreton', 'Szkutnik z Oreton', 'Carpintero de ribera de Oreton', 'Construtor de barcos de Oreton', 'オレトンの船大工', '오레톤의 배 목수', '奥雷顿的造船匠'],
 'Лугос Безумный': ['Lugos der Verrückte', 'Lugos le Fou', 'Lugos il Pazzo', 'Szalony Lugos', 'Lugos el Loco', 'Lugos, o Louco', '狂人ルゴス', '미치광이 루고스', '疯子卢戈斯'],
 'Маркиза Серенити': ['Marquise Serenity', 'Marquise Serenity', 'Marchesa Serenity', 'Markiza Serenity', 'Marquesa Serenity', 'Marquesa Serenity', 'セレニティ侯爵夫人', '세레니티 후작 부인', '赛琳妮蒂侯爵夫人'],
 'Мышовур': ['Mäusesack', 'Ermion', 'Ermion', 'Myszowór', 'Ermion', 'Ermion', 'エルミオン', '에르미온', '艾尔米恩'],
 'Низушки на свадьбе': ['Halblinge auf der Hochzeit', 'Halfelins au mariage', 'Halfling al matrimonio', 'Niziołki na weselu', 'Medianos en la boda', 'Halflings no casamento', '結婚式のハーフリング', '결혼식의 하플링', '婚礼上的半身人'],
 'Оливер': ['Oliver'] * 6 + ['オリバー', '올리버', '奥利佛'],
 'Ольгерд фон Эверек': ['Olgierd von Everec'] * 6 + ['オルギエルド・フォン・エヴェレック', '올기에르드 폰 에베렉', '欧吉尔德·伊佛瑞克'],
 'Первый соперник турнира в Туссенте': ['Erster Gegner im Turnier von Toussaint', 'Premier adversaire du tournoi de Toussaint', 'Primo avversario del torneo di Toussaint', 'Pierwszy przeciwnik w turnieju w Toussaint', 'Primer rival del torneo de Toussaint', 'Primeiro oponente do torneio de Toussaint', 'トゥサンの大会の1人目の対戦相手', '투생 토너먼트의 첫 번째 상대', '陶森特比武大会的第一位对手'],
 'Саша': ['Sasha', 'Sasha', 'Sasha', 'Sasza', 'Sasha', 'Sasha', 'サーシャ', '사샤', '莎夏'],
 'Сигизмунд Дийкстра': ['Sigismund Dijkstra'] * 6 + ['シギスモンド・ディクストラ', '지기스문트 디익스트라', '西吉斯蒙德·迪杰斯特拉'],
 'Старый мудрец': ['Alter Weiser', 'Vieux sage', 'Vecchio saggio', 'Stary mędrzec', 'Viejo sabio', 'Velho sábio', '老賢者', '늙은 현자', '老贤者'],
 'Степан': ['Stjepan'] * 6 + ['ステパン', '스테판', '斯杰潘'],
 'Сьюста': ['Sjusta'] * 6 + ['シュスタ', '슈스타', '斯尤斯塔'],
 'Талер': ['Thaler', 'Thaler', 'Thaler', 'Talar', 'Thaler', 'Thaler', 'ターラー', '탈러', '塔勒'],
 'Торговец бродячего цирка': ['Händler des Wanderzirkus', 'Marchand du cirque itinérant', 'Mercante del circo itinerante', 'Kupiec wędrownego cyrku', 'Mercader del circo ambulante', 'Mercador do circo itinerante', '旅回りのサーカスの商人', '떠돌이 서커스 상인', '巡回马戏团商人'],
 'Торговец скоя’таэлей': ["Scoia'tael-Händler", "Marchand scoia'tael", "Mercante Scoia'tael", "Kupiec Scoia'tael", "Mercader scoia'tael", "Mercador scoia'tael", 'スコイア＝テルの商人', '스코이아텔 상인', '松鼠党商人'],
 'Финалист турнира в Туссенте': ['Finalist des Turniers von Toussaint', 'Finaliste du tournoi de Toussaint', 'Finalista del torneo di Toussaint', 'Finalista turnieju w Toussaint', 'Finalista del torneo de Toussaint', 'Finalista do torneio de Toussaint', 'トゥサンの大会の決勝進出者', '투생 토너먼트 결승 진출자', '陶森特比武大会决赛选手'],
 'Финнеас': ['Finneas'] * 6 + ['フィニアス', '피니어스', '菲尼亚斯'],
 'Хадко': ['Haddy', 'Haddy', 'Haddy', 'Hadko', 'Haddy', 'Haddy', 'ハディ', '해디', '哈迪'],
 'Шани': ['Shani'] * 6 + ['シャニ', '샤니', '夏妮'],
}
src = json.loads((L / 'ui/source.json').read_text('utf8'))
cards = {l: json.loads((L / 'text' / l / 'cards.json').read_text('utf8')) for l in ['ru_ru'] + LANGS}
card_by_name = {c['name']: i for i, c in cards['ru_ru'].items()}
def name(ru, li):
    if ru in card_by_name: return cards[LANGS[li]][card_by_name[ru]]['name']
    return NAMES[ru][li]
out = {}
for s in src:
    ru = s['ru']; res = None
    m1 = re.fullmatch(r'(Стартовый набор\. )?Карта может быть получена от: (.+) \(награда за победу\)\. Также может выпасть из бочки или быть создана за осколки\.', ru)
    m3 = re.fullmatch(r'Стартовый набор\. Победить: (.+)\. Также может выпасть из бочки у торговца в крепости Барона\.', ru)
    m4 = re.fullmatch(r'Адаптация пользовательского deck_rules к строгой Beta 0\.9\.24\. (\S+)', ru)
    m5 = re.fullmatch(r'Исследованный состав Beta 0\.9\.24; (\S+)', ru)
    m6 = re.fullmatch(r'Победить: (.+)\. Также может выпасть из бочки у торговца в крепости Барона\.', ru)
    m8 = re.fullmatch(r'(Стартовый набор\. )?Победить: (.+)\. Также может выпасть из бочки или быть создана за осколки\.', ru)
    m9 = re.fullmatch(r'Карта может быть получена от:( ?)\n(.+)', ru)
    m7 = re.fullmatch(r'ИИ · ([\x20-\x7e]+)', ru)
    if m1: res = {l: (T[l][1] if m1.group(1) else '') + T[l][0].replace('{N}', name(m1.group(2), i)) for i, l in enumerate(LANGS)}
    elif m3: res = {l: T[l][2].replace('{N}', name(m3.group(1), i)) for i, l in enumerate(LANGS)}
    elif m4: res = {l: T[l][3].replace('{T}', m4.group(1)) for l in LANGS}
    elif m5: res = {l: T[l][4].replace('{T}', m5.group(1)) for l in LANGS}
    elif m6: res = {l: T[l][2].replace('{N}', name(m6.group(1), i)).replace(T[l][1], '', 1) for i, l in enumerate(LANGS)}
    elif m8: res = {l: (T[l][1] if m8.group(1) else '') + T8[l].replace('{N}', name(m8.group(2), i)) for i, l in enumerate(LANGS)}
    elif m9: res = {l: T9[l].replace('{S}', m9.group(1)).replace('{N}', name(m9.group(2), i)) for i, l in enumerate(LANGS)}
    elif m7: res = {l: AI[l] + m7.group(1) for l in LANGS}
    if res: out[str(s['id'])] = res
(L / 'ui/tr/templated.json').write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', 'utf8')
print(len(out))

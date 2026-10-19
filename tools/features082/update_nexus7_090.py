"""0.9.0 build 7: add the new card view, banners, paste, tutorial and card fixes to Nexus texts.

Edits (backups in tmp/backup-texts090-build7): <lang>/manual.md "New in 0.9.0" for all 13
languages, en/ru post (md + bbcode, single and combined files), en/ru changelog (md + bbcode).
Then run tools/features082/refresh_showcase090.py to rebuild the description.
"""
from pathlib import Path
import shutil
ROOT = Path(__file__).resolve().parents[2]
N = ROOT / 'docs/releases/0.9.0/nexus'
BACKUP = ROOT / 'tmp/backup-texts090-build7'

NEW = {
 'en': ["Full card view in the Beta style: a large card with the original Beta 0.9.24 faction banner (factions, neutral cards and leaders), base power, readable flavour text, highlighted keywords and ←/→ browsing.",
        "Paste a deck code from the Windows clipboard on the Import screen (Paste button or Ctrl+V; requires Optional-CopyButton).",
        "Tutorial expanded to 10 pages: mulligan and draws, rows and neighbours, card statuses.",
        "Card fixes matching Beta: Myrgtabrakke deals 2 damage three times, Harald the Cripple's ability hits ten times."],
 'ru': ["Полный просмотр карты в стиле беты: большая карта с оригинальным знаменем фракции из Beta 0.9.24 (фракции, нейтральные карты и лидеры), базовая сила, читаемая цитата, подсветка ключевых слов и листание ←/→.",
        "Вставка кода колоды из буфера Windows на экране импорта (кнопка «Вставить» или Ctrl+V; нужна папка Optional-CopyButton).",
        "Обучение расширено до 10 страниц: муллиган и добор, ряды и соседи, статусы карт.",
        "Исправлены карты по данным беты: Миргтабракке наносит 2 ед. урона три раза, способность Харальда Хромого бьёт десять раз."],
 'de': ["Vollständige Kartenansicht im Beta-Stil: große Karte mit dem originalen Fraktionsbanner aus Beta 0.9.24 (Fraktionen, neutrale Karten und Anführer), Grundstärke, lesbarer Zitattext, hervorgehobene Schlüsselwörter und Blättern mit ←/→.",
        "Deckcode aus der Windows-Zwischenablage im Import einfügen (Schaltfläche „Einfügen“ oder Strg+V; erfordert Optional-CopyButton).",
        "Tutorial auf 10 Seiten erweitert: Mulligan und Nachziehen, Reihen und Nachbarn, Kartenstatus.",
        "Kartenkorrekturen wie in der Beta: Myrgtabrakke verursacht dreimal 2 Schaden, die Fähigkeit von Harald dem Krüppel trifft zehnmal."],
 'fr': ["Vue complète des cartes façon bêta : grande carte avec la bannière de faction originale de la bêta 0.9.24 (factions, cartes neutres et chefs), puissance de base, citation lisible, mots-clés mis en évidence et navigation ←/→.",
        "Collez un code de deck depuis le presse-papiers Windows dans l'écran d'import (bouton Coller ou Ctrl+V ; nécessite Optional-CopyButton).",
        "Tutoriel étendu à 10 pages : mulligan et pioche, rangées et voisins, états des cartes.",
        "Cartes corrigées comme dans la bêta : Myrgtabrakke inflige 2 dégâts trois fois, la capacité de Harald l'Estropié frappe dix fois."],
 'it': ["Vista completa della carta in stile beta: carta grande con lo stendardo di fazione originale della beta 0.9.24 (fazioni, carte neutrali e comandanti), forza base, citazione leggibile, parole chiave evidenziate e scorrimento ←/→.",
        "Incolla un codice mazzo dagli appunti di Windows nella schermata di importazione (pulsante Incolla o Ctrl+V; richiede Optional-CopyButton).",
        "Tutorial ampliato a 10 pagine: mulligan e pescate, file e vicini, stati delle carte.",
        "Carte corrette come nella beta: Myrgtabrakke infligge 2 danni tre volte, l'abilità di Harald lo Storpio colpisce dieci volte."],
 'pl': ["Pełny podgląd karty w stylu bety: duża karta z oryginalnym sztandarem frakcji z bety 0.9.24 (frakcje, karty neutralne i dowódcy), siła bazowa, czytelny cytat, wyróżnione słowa kluczowe i przewijanie ←/→.",
        "Wklejanie kodu talii ze schowka Windows na ekranie importu (przycisk Wklej lub Ctrl+V; wymaga Optional-CopyButton).",
        "Samouczek rozszerzony do 10 stron: mulligan i dobieranie, rzędy i sąsiedzi, statusy kart.",
        "Poprawione karty zgodnie z betą: Myrgtabrakke zadaje 2 obrażenia trzy razy, zdolność Haralda Kaleki trafia dziesięć razy."],
 'es': ["Vista completa de la carta al estilo de la beta: carta grande con el estandarte de facción original de la beta 0.9.24 (facciones, cartas neutrales y líderes), poder base, cita legible, palabras clave resaltadas y navegación con ←/→.",
        "Pega un código de mazo desde el portapapeles de Windows en la pantalla de importación (botón Pegar o Ctrl+V; requiere Optional-CopyButton).",
        "Tutorial ampliado a 10 páginas: mulligan y robo, filas y vecinos, estados de las cartas.",
        "Cartas corregidas como en la beta: Myrgtabrakke inflige 2 de daño tres veces y la habilidad de Harald el Lisiado golpea diez veces."],
 'pt-br': ["Visualização completa da carta no estilo da beta: carta grande com o estandarte de facção original da beta 0.9.24 (facções, cartas neutras e líderes), poder base, citação legível, palavras-chave destacadas e navegação com ←/→.",
        "Cole um código de baralho da área de transferência do Windows na tela de importação (botão Colar ou Ctrl+V; requer Optional-CopyButton).",
        "Tutorial ampliado para 10 páginas: mulligan e compra, fileiras e vizinhos, status das cartas.",
        "Cartas corrigidas como na beta: Myrgtabrakke causa 2 de dano três vezes e a habilidade de Harald, o Aleijado, atinge dez vezes."],
 'ja': ["ベータ風のカード詳細表示：ベータ0.9.24のオリジナル勢力バナー（各勢力、中立カード、リーダー）付きの大きなカード、基本戦力、読みやすいフレーバーテキスト、キーワード強調、←/→での切り替え。",
        "インポート画面でWindowsのクリップボードからデッキコードを貼り付け（貼り付けボタンまたはCtrl+V。Optional-CopyButtonが必要）。",
        "チュートリアルを10ページに拡張：マリガンとドロー、列と隣接、カードの状態。",
        "ベータに合わせたカード修正：Myrgtabrakkeは2ダメージを3回、Harald the Crippleのアビリティは10回当たります。"],
 'ko': ["베타 스타일의 카드 전체 보기: 베타 0.9.24의 원본 진영 깃발(각 진영, 중립 카드, 지도자)이 달린 큰 카드, 기본 전투력, 읽기 쉬운 인용문, 키워드 강조, ←/→ 넘기기.",
        "가져오기 화면에서 Windows 클립보드의 덱 코드를 붙여넣기(붙여넣기 버튼 또는 Ctrl+V, Optional-CopyButton 필요).",
        "튜토리얼이 10페이지로 확장: 멀리건과 드로우, 열과 인접 카드, 카드 상태.",
        "베타와 같도록 카드 수정: Myrgtabrakke는 피해 2를 세 번, Harald the Cripple의 능력은 열 번 적중합니다."],
 'zh-cn': ["测试版风格的完整卡牌视图：带有测试版0.9.24原版阵营旗帜（各阵营、中立卡牌和领袖）的大卡、基础战力、易读的引言、关键词高亮以及←/→翻页。",
        "在导入界面从Windows剪贴板粘贴卡组代码（粘贴按钮或Ctrl+V；需要Optional-CopyButton）。",
        "教程扩展为10页：调度与抽牌、排与相邻、卡牌状态。",
        "按测试版修正卡牌：Myrgtabrakke造成三次2点伤害，Harald the Cripple的能力命中十次。"],
 'zh-tw': ["測試版風格的完整卡牌檢視：帶有測試版0.9.24原版陣營旗幟（各陣營、中立卡牌和領袖）的大卡、基礎戰力、易讀的引言、關鍵字醒目提示以及←/→翻頁。",
        "在匯入畫面從Windows剪貼簿貼上牌組代碼（貼上按鈕或Ctrl+V；需要Optional-CopyButton）。",
        "教學擴充為10頁：調度與抽牌、排與相鄰、卡牌狀態。",
        "依測試版修正卡牌：Myrgtabrakke造成三次2點傷害，Harald the Cripple的能力命中十次。"],
}
NEW['es-mx'] = NEW['es']

POST = {
 'en': ('Installing after Redux', [
   ('Card view and tutorial', "The full card view now follows Beta: a large card with the original Beta 0.9.24 faction banner, base power in white, readable flavour text and highlighted keywords. Deck screens use the same banner. The tutorial has 10 pages, including mulligan and draws, rows and neighbours, and card statuses. A deck code can also be pasted from the Windows clipboard (Paste or Ctrl+V; requires Optional-CopyButton)."),
   ('Card fixes', "Myrgtabrakke now deals 2 damage three times and Harald the Cripple's ability hits ten times, matching the Beta 0.9.24 card data.")]),
 'ru': ('Установка после Redux', [
   ('Просмотр карт и обучение', "Полный просмотр карты теперь как в бете: большая карта с оригинальным знаменем фракции из Beta 0.9.24, базовая сила белым, читаемая цитата и подсветка ключевых слов. Экраны колод используют то же знамя. В обучении 10 страниц, включая муллиган и добор, ряды и соседей, статусы карт. Код колоды можно вставить из буфера Windows («Вставить» или Ctrl+V; нужна папка Optional-CopyButton)."),
   ('Исправления карт', "Миргтабракке теперь наносит 2 ед. урона три раза, а способность Харальда Хромого бьёт десять раз — как в данных карт Beta 0.9.24.")]),
}

CHANGELOG = {
 'en': ('Card inspection now follows Beta', [
   "Card inspection uses the original Beta 0.9.24 faction banners on the large card (factions, neutral cards and leaders), shows the base power in white and a readable flavour line. Deck screens show the same banner.",
   "Tutorial expanded to 10 pages (mulligan and draws, rows and neighbours, card statuses) with more space around the content.",
   "Fixed stray lines from the screen corner when previewing area targets; doomed units no longer show a cross badge.",
   "Myrgtabrakke deals 2 damage three times and Harald the Cripple's ability hits ten times, as in the Beta 0.9.24 card data."]),
 'ru': ('Просмотр карты сделан как в бете', [
   "В просмотре карты большая карта со знаменем фракции из Beta 0.9.24 (фракции, нейтральные карты и лидеры), базовая сила белым и читаемая цитата. Экраны колод показывают то же знамя.",
   "Обучение расширено до 10 страниц (муллиган и добор, ряды и соседи, статусы карт), содержимое отодвинуто от рамки.",
   "Исправлены лишние линии из угла экрана при предпросмотре целей по области; у обречённых отрядов убран крестик.",
   "Миргтабракке наносит 2 ед. урона три раза, способность Харальда Хромого бьёт десять раз — как в данных карт Beta 0.9.24."]),
}


def backup(p):
    t = BACKUP / p.relative_to(N)
    if not t.exists():
        t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, t)


def edit(p, fn):
    backup(p); s = p.read_text('utf8'); new = fn(s)
    assert new != s, p
    p.write_text(new, 'utf8')


def manual(lang):
    def fn(s):
        assert NEW[lang][0] not in s
        lines = s.split('\n'); start = next(i for i, l in enumerate(lines) if l.startswith('## ') and '0.9.0' in l)
        end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith('## '))
        last = max(i for i in range(start, end) if lines[i].startswith('- '))
        return '\n'.join(lines[:last + 1] + ['- ' + b for b in NEW[lang]] + lines[last + 1:])
    edit(N / lang / 'manual.md', fn)


def post_files(lang):
    anchor, sections = POST[lang]
    md = ''.join('**%s**\n%s\n\n' % (t, b) for t, b in sections)
    bb = ''.join('[b]%s[/b]\n%s\n\n' % (t, b) for t, b in sections)
    for p, text, a in [(N / lang / 'post.md', md, '**%s**' % anchor), (N / lang / 'post.bbcode.txt', bb, '[b]%s[/b]' % anchor),
                       (N / 'POST_0.9.0_EN_RU.md', md, '**%s**' % anchor), (N / 'NEXUS_POST_0.9.0_EN_RU.bbcode.txt', bb, '[b]%s[/b]' % anchor)]:
        def fn(s, text=text, a=a):
            assert s.count(a) == 1 and sections[0][1] not in s, (p, a)
            return s.replace(a, text + a)
        edit(p, fn)


def changelog(lang):
    anchor, lines = CHANGELOG[lang]
    def md(s):
        i = s.index(anchor); end = s.index('\n', i)
        return s[:end] + ''.join('\n- ' + l for l in lines) + s[end:]
    edit(N / lang / 'changelog.md', md)
    p = N / lang / 'changelog.bbcode.txt'
    if p.exists() and anchor in p.read_text('utf8'):
        def bb(s):
            i = s.index(anchor); end = s.index('\n', i)
            return s[:end] + ''.join('\n[*]' + l for l in lines) + s[end:]
        edit(p, bb)


def main():
    for lang in NEW: manual(lang)
    for lang in POST: post_files(lang)
    for lang in CHANGELOG: changelog(lang)
    print('Nexus texts updated; now run refresh_showcase090.py')


if __name__ == '__main__':
    main()

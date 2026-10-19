"""0.9.0 texts: Steam Deck works (checked by the author).

* 13 manual.md: one paragraph at the end of the "Important" section (shown in
  the visible part of the Nexus description in every language).
* en/ru posts (md, bbcode, combined): sentence after the platform paragraph.
* refresh_showcase090.py header line: Classic 1.32 / Next-Gen 5.0+ / Steam Deck.
Backups: tmp/backup-texts090-deck. Run refresh_showcase090.py afterwards.
"""
from pathlib import Path
import re, shutil

ROOT = Path(__file__).resolve().parents[2]
NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
BACKUP = ROOT / 'tmp/backup-texts090-deck'
DECK = {
    'en': '**Steam Deck:** the mod works on Steam Deck (tested by the author).',
    'ru': '**Steam Deck:** мод работает на Steam Deck (проверено автором).',
    'de': '**Steam Deck:** Die Mod läuft auf dem Steam Deck (vom Autor getestet).',
    'fr': '**Steam Deck :** le mod fonctionne sur Steam Deck (testé par l’auteur).',
    'it': '**Steam Deck:** la mod funziona su Steam Deck (testata dall’autore).',
    'pl': '**Steam Deck:** mod działa na Steam Decku (sprawdzone przez autora).',
    'es': '**Steam Deck:** el mod funciona en Steam Deck (probado por el autor).',
    'es-mx': '**Steam Deck:** el mod funciona en Steam Deck (probado por el autor).',
    'pt-br': '**Steam Deck:** o mod funciona no Steam Deck (testado pelo autor).',
    'ja': '**Steam Deck：** このModはSteam Deckでも動作します（作者が確認済み）。',
    'ko': '**Steam Deck:** 이 모드는 Steam Deck에서도 작동합니다(제작자 확인).',
    'zh-cn': '**Steam Deck：** 本模组可在 Steam Deck 上运行（作者已验证）。',
    'zh-tw': '**Steam Deck：** 本模組可在 Steam Deck 上執行（作者已驗證）。',
}
POST = {'en': ('Choose one archive for your game version.', 'Works on Steam Deck as well (tested by the author).'),
        'ru': ('Выбирайте один архив под свою версию игры.', 'Мод работает и на Steam Deck (проверено автором).')}


def load(p):
    raw = p.read_bytes(); t = raw.decode('utf-8-sig')
    return t.replace('\r\n', '\n'), raw.startswith(b'\xef\xbb\xbf'), b'\r\n' in raw


def store(p, t, bom, crlf):
    target = BACKUP / p.relative_to(ROOT)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
    if crlf: t = t.replace('\n', '\r\n')
    p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))


def manuals():
    for lang, line in DECK.items():
        p = NEXUS / lang / 'manual.md'; t, bom, crlf = load(p)
        assert 'Steam Deck' not in t, lang
        heads = [m.start() for m in re.finditer(r'(?m)^## ', t)]
        end = heads[1]  # "Important" is the first section
        t = t[:end].rstrip('\n') + '\n\n' + line + '\n\n' + t[end:]
        store(p, t, bom, crlf); print('manual', lang)


def posts():
    files = [NEXUS / 'en/post.md', NEXUS / 'en/post.bbcode.txt', NEXUS / 'ru/post.md', NEXUS / 'ru/post.bbcode.txt',
             NEXUS / 'POST_0.9.0_EN_RU.md', NEXUS / 'NEXUS_POST_0.9.0_EN_RU.bbcode.txt']
    for p in files:
        t, bom, crlf = load(p); assert 'Steam Deck' not in t, p
        lines = t.split('\n'); n = 0
        for i, x in enumerate(lines):
            for anchor, sentence in POST.values():
                if x.startswith(anchor):
                    lines[i] = x.rstrip() + ' ' + sentence; n += 1
        assert n == (2 if 'EN_RU' in p.name else 1), (p, n)
        store(p, '\n'.join(lines), bom, crlf); print('post', p.relative_to(NEXUS), n)


def header():
    p = ROOT / 'tools/features082/refresh_showcase090.py'; t, bom, crlf = load(p)
    old = '[b]Classic 1.32  /  Next-Gen 5.0+[/b]'; assert t.count(old) == 1
    store(p, t.replace(old, '[b]Classic 1.32  /  Next-Gen 5.0+  /  Steam Deck[/b]'), bom, crlf); print('header')


if __name__ == '__main__':
    manuals(); posts(); header()

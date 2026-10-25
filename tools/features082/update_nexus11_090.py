"""0.9.0 texts for build 11: cautious wording about profile backup recovery.

* 13 manual.md: one bullet at the end of "New in 0.9.0".
* en/ru changelog.md: one bullet in "Saves and compatibility"; changelog.bbcode.txt regenerated.
Backups: tmp/backup-texts090-build11. Run refresh_showcase090.py afterwards.
"""
from pathlib import Path
import re, shutil, sys
sys.path.insert(0, str(Path(__file__).parent))
from update_nexus9_090 import to_bbcode

ROOT = Path(__file__).resolve().parents[2]
NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
BACKUP = ROOT / 'tmp/backup-texts090-build11'
LINE = {'en': 'Improved backup handling for the collection and decks. This may help with some cases of lost progress; recovery depends '
       'on the data available in the backup.',
 'ru': 'Улучшена работа резервных копий коллекции и колод. Это может помочь в некоторых случаях сброса прогресса; восстановление '
       'зависит от данных, сохранившихся в резервной копии.',
 'de': 'Die Verarbeitung von Sicherungen der Sammlung und Decks wurde verbessert. Dies kann in manchen Fällen von '
       'Fortschrittsverlust helfen; die Wiederherstellung hängt von den verfügbaren Sicherungsdaten ab.',
 'fr': 'Amélioration de la gestion des sauvegardes de la collection et des decks. Cela peut aider dans certains cas de perte de '
       'progression ; la restauration dépend des données disponibles dans la copie de sauvegarde.',
 'it': 'Migliorata la gestione dei backup della collezione e dei mazzi. Questo può aiutare in alcuni casi di perdita dei '
       'progressi; il ripristino dipende dai dati disponibili nel backup.',
 'pl': 'Ulepszono obsługę kopii zapasowych kolekcji i talii. Może to pomóc w niektórych przypadkach utraty postępów; '
       'przywrócenie zależy od danych dostępnych w kopii zapasowej.',
 'es': 'Mejorada la gestión de las copias de seguridad de la colección y los mazos. Esto puede ayudar en algunos casos de '
       'pérdida de progreso; la recuperación depende de los datos disponibles en la copia de seguridad.',
 'es-mx': 'Se mejoró la gestión de las copias de seguridad de la colección y los mazos. Esto puede ayudar en algunos casos de '
          'pérdida de progreso; la recuperación depende de los datos disponibles en la copia de seguridad.',
 'pt-br': 'Melhorado o gerenciamento dos backups da coleção e dos baralhos. Isso pode ajudar em alguns casos de perda de '
          'progresso; a recuperação depende dos dados disponíveis no backup.',
 'ja': 'コレクションとデッキのバックアップ処理を改善しました。進行状況が失われた一部のケースで役立つ可能性がありますが、復元できる内容はバックアップに残っているデータによって異なります。',
 'ko': '컬렉션과 덱의 백업 처리를 개선했습니다. 일부 진행 상황 손실 문제에 도움이 될 수 있지만, 복원 가능한 내용은 백업에 남아 있는 데이터에 따라 달라집니다.',
 'zh-cn': '改进了收藏和卡组的备份处理。这可能有助于解决部分进度丢失问题；能否恢复以及可恢复的内容取决于备份中保留的数据。',
 'zh-tw': '改善了收藏與牌組的備份處理。這可能有助於解決部分進度遺失問題；能否恢復及可恢復的內容取決於備份中保留的資料。'}
SAVES = {'en': '## Saves and compatibility', 'ru': '## Сохранения и совместимость'}


def load(p):
    raw = p.read_bytes()
    return raw.decode('utf-8-sig').replace('\r\n', '\n'), raw.startswith(b'\xef\xbb\xbf'), b'\r\n' in raw


def store(p, t, bom, crlf):
    target = BACKUP / p.relative_to(ROOT)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)
    if crlf: t = t.replace('\n', '\r\n')
    p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + t.encode('utf8'))


def insert_after_list(t, start, line):
    """Insert '- line' after the last bullet of the list that follows heading index `start`."""
    lines = t.split('\n'); i = start + 1
    while i < len(lines) and not lines[i].startswith('- '): i += 1
    while i < len(lines) and lines[i].startswith('- '): i += 1
    lines.insert(i, '- ' + line)
    return '\n'.join(lines)


def main():
    for lang, line in LINE.items():
        p = NEXUS / lang / 'manual.md'; t, bom, crlf = load(p)
        if line in t: print('manual', lang, 'already'); continue
        heads = [i for i, x in enumerate(t.split('\n')) if x.startswith('## ')]
        store(p, insert_after_list(t, heads[1], line), bom, crlf); print('manual', lang)
    for lang in ['en', 'ru']:
        p = NEXUS / lang / 'changelog.md'; t, bom, crlf = load(p)
        if LINE[lang] in t: print('changelog', lang, 'already'); continue
        idx = t.split('\n').index(SAVES[lang])
        t = insert_after_list(t, idx, LINE[lang]); store(p, t, bom, crlf)
        bb = NEXUS / lang / 'changelog.bbcode.txt'; b0, bbom, bcrlf = load(bb)
        store(bb, to_bbcode(t), bbom, bcrlf); print('changelog', lang)


if __name__ == '__main__':
    main()

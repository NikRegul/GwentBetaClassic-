"""0.9.0 release texts: Import/Export are hidden without Optional-CopyButton.

* 13 manual.md: the "-debugscripts + Copy-Deck-Code.cmd" fallback sentence is
  replaced by "without these files Import and Export are hidden".
* en/ru changelog.md: same in BG1, plus one Deck sharing bullet. The RU BG1
  section (damaged earlier: cut paragraph and stray bullets) is rewritten from EN.
* en/ru changelog.bbcode.txt regenerated from changelog.md.
* Posts (en/ru md + bbcode, combined EN/RU files): fallback sentence replaced.
* repack_optional090.py README text, refresh_showcase090.py token list.
Backups: tmp/backup-texts090-build9. Run refresh_showcase090.py afterwards.
"""
from pathlib import Path
import re, shutil

ROOT = Path(__file__).resolve().parents[2]
NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
TOOLS = ROOT / 'tools/features082'
BACKUP = ROOT / 'tmp/backup-texts090-build9'
LANGS = ['en', 'ru', 'de', 'fr', 'it', 'pl', 'es', 'es-mx', 'pt-br', 'ja', 'ko', 'zh-cn', 'zh-tw']
START = {'en': 'Without these files', 'ru': 'Без этих файлов', 'de': 'Fehlen die Dateien', 'fr': 'Sans ces fichiers',
         'it': 'Senza questi file', 'pl': 'Bez tych plików', 'es': 'Sin estos archivos', 'es-mx': 'Sin estos archivos',
         'pt-br': 'Sem esses arquivos', 'ja': 'ファイルがない場合は', 'ko': '파일이 없으면', 'zh-cn': '缺少这些文件时',
         'zh-tw': None}
NEW = {'en': 'Without these files the Import and Export buttons are hidden.',
       'ru': 'Без этих файлов кнопки импорта и экспорта скрыты.',
       'de': 'Ohne diese Dateien sind die Schaltflächen Import und Export ausgeblendet.',
       'fr': 'Sans ces fichiers, les boutons Importer et Exporter sont masqués.',
       'it': 'Senza questi file i pulsanti Importa ed Esporta sono nascosti.',
       'pl': 'Bez tych plików przyciski Import i Eksport są ukryte.',
       'es': 'Sin estos archivos, los botones Importar y Exportar se ocultan.',
       'es-mx': 'Sin estos archivos, los botones Importar y Exportar se ocultan.',
       'pt-br': 'Sem esses arquivos, os botões Importar e Exportar ficam ocultos.',
       'ja': 'これらのファイルがない場合、インポートとエクスポートのボタンは表示されません。',
       'ko': '파일이 없으면 가져오기와 내보내기 버튼이 표시되지 않습니다.',
       'zh-cn': '缺少这些文件时，导入和导出按钮会隐藏。',
       'zh-tw': '缺少這些檔案時，匯入和匯出按鈕會隱藏。'}
CJK = ('ja', 'zh-cn', 'zh-tw')


def backup(p):
    target = BACKUP / p.relative_to(ROOT)
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, target)


def read(p):
    return p.read_bytes().decode('utf-8-sig')


def save(p, s, original):
    backup(p)
    bom = p.read_bytes().startswith(b'\xef\xbb\xbf')
    crlf = '\r\n' in original
    s = s.replace('\r\n', '\n')
    if crlf: s = s.replace('\n', '\r\n')
    p.write_bytes((b'\xef\xbb\xbf' if bom else b'') + s.encode('utf8'))


def sentence_end(line, b):
    ends = [i for i in (line.find('。', b), line.find('. ', b), line.find('.', b)) if i >= 0]
    end = min(ends) + 1
    return end


def fallback(line, lang):
    """Replace the 'without files ... -debugscripts ... Copy-Deck-Code.cmd.' span."""
    k = line.index('-debugscripts')
    marker = START[lang]
    if marker is None:  # zh-tw: the clause before "備用方法"
        a = line.rfind('。', 0, line.rfind('。', 0, k)) + 1
    else:
        a = line.rfind(marker, 0, k)
        assert a >= 0, (lang, marker)
    b = line.index('Copy-Deck-Code.cmd', k) + len('Copy-Deck-Code.cmd')
    end = sentence_end(line, b)
    new = NEW[lang]
    if lang not in CJK and end < len(line) and line[end] != ' ': new += ' '
    return line[:a] + new + line[end:]


def fix_lines(s, lang, test=lambda line: 'Copy-Deck-Code.cmd' in line and '-debugscripts' in line):
    lines = s.split('\n'); n = 0
    for i, line in enumerate(lines):
        if test(line): lines[i] = fallback(line, lang); n += 1
    return '\n'.join(lines), n


def manuals():
    for lang in LANGS:
        p = NEXUS / lang / 'manual.md'; s0 = read(p)
        s, n = fix_lines(s0, lang)
        assert n >= 1 and 'Copy-Deck-Code' not in s, (lang, n)
        save(p, s, s0); print('manual', lang, n)


RU_BG1 = '''## BG1

Экспорт показывает код колоды BG1, не зависящий от языка. «Копировать» помещает его в буфер Windows. Чтобы вставить код в игру, скопируйте его целиком в Windows и откройте импорт: код читается при открытии, а «Вставить» или Ctrl+V читают его снова. Вставка проверяет код; импорт и сохранение остаются отдельными действиями. Неверный код или занятый буфер не меняют введённый текст.

Обеим кнопкам нужна необязательная папка Optional-CopyButton из архива: скопируйте её папку bin в каталог игры (dinput8.dll и plugins/GwentBetaClipboard.asi рядом с witcher3.exe). Замените старую GwentBetaClipboard.asi: прежние версии только копировали из игры. Сам мод работает и без неё. Если у другого мода уже есть свой dinput8.dll, оставьте его и загрузите GwentBetaClipboard.asi через его ASI-загрузчик. Без этих файлов кнопки импорта и экспорта скрыты. С ними код можно также ввести вручную.

Недостающие карты, включая лидера, показываются картами: создайте каждую отдельно или все сразу за общую стоимость в осколках. Импорт недоступен, пока чего-то не хватает. Импорт создаёт черновик: сохраните его кнопкой «Сохранить колоду». Импорт из списка колод использует свободный пользовательский слот и не перезаписывает занятые. В тренировке используется прежняя коллекция без ограничений.
'''
BULLET = {'en': ('- Added Windows → game paste:', '- Import and Export appear only when Optional-CopyButton is installed; without it both buttons are hidden.'),
          'ru': ('- Добавлено обратное направление Windows → игра:', '- Кнопки импорта и экспорта появляются только при установленной Optional-CopyButton; без неё обе скрыты.')}


def changelogs():
    for lang in ['en', 'ru']:
        p = NEXUS / lang / 'changelog.md'; s0 = read(p); s = s0.replace('\r\n', '\n')
        if lang == 'en':
            old = ('Without these files the buttons say so; as an export fallback, start the game with -debugscripts, '
                   'export again and run Copy-Deck-Code.cmd. Import codes can also be typed manually.')
            assert s.count(old) == 1
            s = s.replace(old, 'Without these files the Import and Export buttons are hidden. With them, codes can also be typed manually.')
        else:
            a = s.index('## BG1\n'); assert s.count('## BG1\n') == 1 and '\n## ' not in s[a + 1:]
            s = s[:a] + RU_BG1
        anchor, bullet = BULLET[lang]
        lines = s.split('\n'); i = next(i for i, x in enumerate(lines) if x.startswith(anchor))
        assert bullet not in s
        lines.insert(i + 1, bullet); s = '\n'.join(lines)
        assert 'Copy-Deck-Code' not in s
        save(p, s, s0); print('changelog', lang)
        bb = NEXUS / lang / 'changelog.bbcode.txt'; b0 = read(bb)
        save(bb, to_bbcode(s), b0); print('changelog bbcode', lang)


def inline(t):
    t = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', t)
    return re.sub(r'`([^`]+)`', r'[font=Courier New]\1[/font]', t)


def to_bbcode(md):
    out, in_list, in_code = [], False, False
    for line in md.split('\n'):
        if line.startswith('```'):
            if in_list: out.append('[/list]'); in_list = False
            out.append('[/code]' if in_code else '[code]'); in_code = not in_code; continue
        if in_code: out.append(line); continue
        if line.startswith('- '):
            if not in_list: out.append('[list]'); in_list = True
            out.append('[*]' + inline(line[2:])); continue
        if in_list: out.append('[/list]'); in_list = False
        if line.startswith('# '): out.append('[size=5][color=#e0b354][b]' + line[2:] + '[/b][/color][/size]')
        elif line.startswith('## '): out.append('[size=4][color=#e0b354][b]' + line[3:] + '[/b][/color][/size]')
        else: out.append(inline(line))
    if in_list: out.append('[/list]')
    assert not in_code
    s = '\n'.join(out)
    for tag in ['list', 'code', 'b', 'size', 'color']:
        assert s.count('[' + tag) == s.count('[/' + tag + ']'), tag
    return s


POST = {'en': ('Fallback without these files: launch with -debugscripts, export again and run Copy-Deck-Code.cmd.',
               'Without these files the Import and Export buttons are hidden.'),
        'ru': ('Запасной путь без этих файлов: запуск с -debugscripts, повторный экспорт и Copy-Deck-Code.cmd.',
               'Без этих файлов кнопки импорта и экспорта скрыты.')}


def posts():
    files = [NEXUS / 'en/post.md', NEXUS / 'en/post.bbcode.txt', NEXUS / 'ru/post.md', NEXUS / 'ru/post.bbcode.txt',
             NEXUS / 'POST_0.9.0_EN_RU.md', NEXUS / 'NEXUS_POST_0.9.0_EN_RU.bbcode.txt']
    for p in files:
        s0 = read(p); s = s0
        for lang, (old, new) in POST.items():
            if old in s: s = s.replace(old, new)
        assert 'Copy-Deck-Code' not in s, p
        save(p, s, s0); print('post', p.name)


def tools():
    p = TOOLS / 'repack_optional090.py'; s0 = read(p); s = s0
    for old, new in [('Without it: launch with -debugscripts, export, run Copy-Deck-Code.cmd.', 'Without it the Import and Export buttons are hidden.'),
                     ('Без неё: запуск с -debugscripts, экспорт, затем Copy-Deck-Code.cmd.', 'Без неё кнопки импорта и экспорта скрыты.')]:
        assert s.count(old) == 1, old; s = s.replace(old, new)
    save(p, s, s0); print('repack text')
    p = TOOLS / 'refresh_showcase090.py'; s0 = read(p)
    old = "'bg_clean_keys', 'Copy-Deck-Code.cmd', "; assert s0.count(old) == 1
    save(p, s0.replace(old, "'bg_clean_keys', "), s0); print('showcase tokens')


if __name__ == '__main__':
    manuals(); changelogs(); posts(); tools()
    print('Done. Backups:', BACKUP)

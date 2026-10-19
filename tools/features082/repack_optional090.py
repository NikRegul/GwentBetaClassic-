"""Move the native copy files of the final 0.9.0 archives into Optional-CopyButton.

Reads release090-final/package-candidate/archives, writes archives-optional
(same names, new folder; the originals stay). bin/... -> Optional-CopyButton/bin/...,
adds a short README there, refreshes the bundled docs from docs/releases and the
in-archive manifest. Scripts, menus and DLC entries are copied byte for byte.
"""
from pathlib import Path
import os
import hashlib, json, zipfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final') / 'package-candidate/archives'
OUT = next(SRC.parent / ('archives-optional' + ('' if n < 2 else f'-{n}')) for n in range(1, 100)
           if not (SRC.parent / ('archives-optional' + ('' if n < 2 else f'-{n}'))).exists())
OPT = 'Optional-CopyButton/'
DOCS = {
    'BetaGwentDocs/README_EN.md': 'docs/releases/0.9.0/nexus/en/description.md',
    'BetaGwentDocs/README_RU.md': 'docs/releases/0.9.0/nexus/ru/description.md',
    'BetaGwentDocs/CHANGELOG_EN.md': 'docs/releases/0.9.0/nexus/en/changelog.md',
    'BetaGwentDocs/CHANGELOG_RU.md': 'docs/releases/0.9.0/nexus/ru/changelog.md',
    'BetaGwentDocs/CLEANUP_EN.md': 'docs/releases/0.9.0_CLEANUP_EN.md',
    'BetaGwentDocs/CLEANUP_RU.md': 'docs/releases/0.9.0_CLEANUP_RU.md',
}
README = {
'README_EN.txt': '''Optional: Copy and Paste for deck codes (Windows clipboard)

The mod works without this folder. Native Windows Copy and Paste need it.
Copy a complete BG1 code in Windows, open Import, then use Paste or Ctrl+V.
Import also reads the code when opened. Paste checks the code; Import and Save
remain separate actions. Update an older GwentBetaClipboard.asi to this version.
Install: copy the bin folder from here into the game directory, so that
dinput8.dll and plugins\\GwentBetaClipboard.asi are next to witcher3.exe
(1.32: bin\\x64; Next-Gen: bin\\x64_dx12 and, if present, bin\\x64).
If another mod already has a dinput8.dll there, do not overwrite it: put only
plugins\\GwentBetaClipboard.asi and let that mod's ASI loader load it.
It only copies or reads valid BG1 deck codes; it changes no saves or game files.
Remove: delete these two files.
Without it the Import and Export buttons are hidden.
''',
'README_RU.txt': '''Необязательно: «Копировать» и «Вставить» для кодов колод (буфер Windows)

Мод работает и без этой папки. Она нужна для копирования и вставки через Windows.
Скопируйте полный код BG1 в Windows, откройте импорт и нажмите «Вставить» или Ctrl+V.
При открытии импорта код тоже читается. Вставка проверяет код; импорт и сохранение
выполняются отдельно. Старую GwentBetaClipboard.asi замените этой версией.
Установка: скопируйте отсюда папку bin в каталог игры, чтобы dinput8.dll и
plugins\\GwentBetaClipboard.asi оказались рядом с witcher3.exe
(1.32: bin\\x64; Next-Gen: bin\\x64_dx12 и, если есть, bin\\x64).
Если там уже есть dinput8.dll другого мода, не заменяйте его: положите только
plugins\\GwentBetaClipboard.asi, его загрузит ASI-загрузчик того мода.
Копирует или читает только правильные коды BG1; сейвы и файлы игры не меняет.
Удаление: удалите эти два файла.
Без неё кнопки импорта и экспорта скрыты.
''',
}


def main():
    OUT.mkdir(exist_ok=False)
    for src in sorted(SRC.glob('GwentBetaClassic-0.9.0-*-AllLanguages.zip')):
        dst = OUT / src.name
        files = []
        with zipfile.ZipFile(src) as zin, zipfile.ZipFile(dst, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
            names = zin.namelist()
            assert any(n.startswith('bin/') for n in names), src.name
            for n in names:
                if n.startswith('manifest-'):
                    continue
                if n in DOCS:
                    data = (ROOT / DOCS[n]).read_bytes(); target = n
                elif n == 'BetaGwentDocs/BuildInfo.json':
                    info = json.loads(zin.read(n)); info['nativeClipboard']['optionalFolder'] = OPT.rstrip('/')
                    data = json.dumps(info, indent=2).encode('utf8'); target = n
                else:
                    data = zin.read(n); target = OPT + n if n.startswith('bin/') else n
                zout.writestr(zin.getinfo(n).__class__(target, zin.getinfo(n).date_time), data, zipfile.ZIP_DEFLATED, 6)
                files.append(dict(path=target, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
            for name, text in README.items():
                data = text.replace('\n', '\r\n').encode('utf-8-sig')
                zout.writestr(OPT + name, data, zipfile.ZIP_DEFLATED, 6)
                files.append(dict(path=OPT + name, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
            platform = '1.32' if '-1.32-' in src.name else '5.0+'
            manifest = dict(version='0.9.0', platform=platform, files=sorted(files, key=lambda f: f['path']),
                            nativeGameplayVerified=False, optionalCopyButton=OPT.rstrip('/'))
            zout.writestr('manifest-0.9.0.json', json.dumps(manifest, indent=2), zipfile.ZIP_DEFLATED, 6)
        with zipfile.ZipFile(dst) as z:
            assert z.testzip() is None
            assert not any(n.startswith('bin/') for n in z.namelist())
        digest = hashlib.sha256(dst.read_bytes()).hexdigest()
        dst.with_suffix('.zip.sha256').write_text(digest + '  ' + dst.name + '\n', 'ascii')
        print(json.dumps(dict(archive=str(dst), bytes=dst.stat().st_size, sha256=digest)), flush=True)


if __name__ == '__main__':
    main()

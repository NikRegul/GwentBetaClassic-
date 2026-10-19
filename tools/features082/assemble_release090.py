"""Collect the 0.9.0 release into one folder: two archives, Nexus texts, banner.

Source archives: BetaGwent/build/<BG_FINAL>/package-candidate/archives-optional.
Output: BetaGwent/release/GwentBetaClassic-0.9.0 (must not exist yet).
Nothing is uploaded; the folder is only a hand-off for publishing on Nexus.
"""
from pathlib import Path
import hashlib, json, os, shutil, zipfile

ROOT = Path(__file__).resolve().parents[2]
FINAL = ROOT / 'BetaGwent/build' / os.environ.get('BG_FINAL', 'release090-final9')
ARCHIVES = FINAL / 'package-candidate/archives-optional'
NEXUS = ROOT / 'docs/releases/0.9.0/nexus'
OUT = ROOT / 'BetaGwent/release/GwentBetaClassic-0.9.0'
R7 = hashlib.sha256((ROOT / 'BetaGwent/build/clipboard090-r7/GwentBetaClipboard.asi').read_bytes()).hexdigest()
ZIPS = ['GwentBetaClassic-0.9.0-1.32-AllLanguages.zip', 'GwentBetaClassic-0.9.0-5.0+-AllLanguages.zip']
TEXTS = {
    'NEXUS_DESCRIPTION_0.9.0.bbcode.txt': 'nexus/NEXUS_DESCRIPTION_0.9.0.bbcode.txt',
    'NEXUS_POST_0.9.0_EN_RU.bbcode.txt': 'nexus/NEXUS_POST_0.9.0_EN_RU.bbcode.txt',
    'DESCRIPTION_0.9.0.md': 'nexus/DESCRIPTION_0.9.0.md',
    'POST_0.9.0_EN_RU.md': 'nexus/POST_0.9.0_EN_RU.md',
    'preview.html': 'nexus/preview.html',
    'assets/GwentBetaClassic-header.jpg': 'nexus/GwentBetaClassic-header.jpg',
    'en/changelog.md': 'nexus/CHANGELOG_0.9.0_EN.md',
    'en/changelog.bbcode.txt': 'nexus/CHANGELOG_0.9.0_EN.bbcode.txt',
    'ru/changelog.md': 'nexus/CHANGELOG_0.9.0_RU.md',
    'ru/changelog.bbcode.txt': 'nexus/CHANGELOG_0.9.0_RU.bbcode.txt',
}
README = '''# Gwent Beta Classic 0.9.0 — релиз

Папка собрана скриптом tools/features082/assemble_release090.py из {final}.
Ничего не опубликовано.

## Файлы на Nexus (раздел Files, Main files)

1. `{z132}` — версия для игры 1.32 (Classic). Категория: Main.
   Имя на Nexus: «Gwent Beta Classic 0.9.0 — 1.32 (all languages)».
2. `{zng}` — версия для Next-Gen (5.0+). Категория: Main.
   Имя на Nexus: «Gwent Beta Classic 0.9.0 — Next-Gen 5.0+ (all languages)».

Версия файла: 0.9.0. Старые файлы 0.8.x перенести в Old versions.
SHA-256 указаны в `.sha256` рядом с архивами и в release.json.

## Тексты (папка nexus)

- `NEXUS_DESCRIPTION_0.9.0.bbcode.txt` — описание мода целиком. В редакторе Nexus
  включить режим исходного BBCode и вставить файл полностью.
- `GwentBetaClassic-header.jpg` (1800×600) — баннер над описанием / в Images.
- `NEXUS_POST_0.9.0_EN_RU.bbcode.txt` — пост о выходе 0.9.0 (Posts / Articles), EN, затем RU.
- `CHANGELOG_0.9.0_EN.*` / `CHANGELOG_0.9.0_RU.*` — список изменений; на вкладку
  Logs вставлять английский .md построчно (каждый пункт — отдельная строка).
- `.md` и `preview.html` — те же тексты для чтения и предпросмотра.

## Перед публикацией

- Установить оба архива начисто и проверить запуск, матч, импорт/экспорт колоды.
- Optional-CopyButton в архивах содержит мост буфера обмена r7 (быстрый импорт).
'''


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert not OUT.exists(), 'Release folder already exists: move it to tmp first'
    files = {}
    for name in ZIPS:
        z = ARCHIVES / name; s = ARCHIVES / (name + '.sha256')
        assert z.is_file() and s.is_file(), z
        digest = sha(z)
        assert s.read_text('utf8').split()[0].lower() == digest, 'sha256 mismatch ' + name
        with zipfile.ZipFile(z) as f:
            asi = [n for n in f.namelist() if n.endswith('GwentBetaClipboard.asi')]
            assert asi and all(hashlib.sha256(f.read(n)).hexdigest() == R7 for n in asi), 'bridge r7 not in ' + name
        files[name] = (z, s)
    for src in TEXTS:
        assert (NEXUS / src).is_file(), NEXUS / src
    (OUT / 'nexus').mkdir(parents=True)
    release = dict(version='0.9.0', source=FINAL.name, archives={}, texts={})
    for name, (z, s) in files.items():
        shutil.copy2(z, OUT / name); shutil.copy2(s, OUT / s.name)
        release['archives'][name] = dict(sha256=sha(OUT / name), bytes=(OUT / name).stat().st_size)
    for src, dst in TEXTS.items():
        shutil.copy2(NEXUS / src, OUT / dst)
        release['texts'][dst] = sha(OUT / dst)
    (OUT / 'release.json').write_text(json.dumps(release, indent=2, ensure_ascii=False), 'utf8')
    (OUT / 'README_RU.md').write_text(README.format(final=FINAL.name, z132=ZIPS[0], zng=ZIPS[1]), 'utf8')
    print('Release folder:', OUT)
    for name, info in release['archives'].items():
        print(' ', name, info['bytes'] // (1024 * 1024), 'MB', info['sha256'][:16])


if __name__ == '__main__':
    main()

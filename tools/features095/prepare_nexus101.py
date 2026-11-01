"""Prepare reviewable Nexus BBCode and source hashes; never publish or alter ZIPs."""
from pathlib import Path
import argparse, hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/features094'))
from collect_release094a import bbcode
from ui_release095 import NOTES
from notes095_public import ORDER
from nexus_posts095 import write_posts
from nexus_description095 import write_description, FILENAME


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked(text):
    stack = []
    for token in re.finditer(r'\[(/?)(b|size|list)(?:=[^\]]+)?\]', text):
        close, tag = token.groups()
        if close:
            assert stack and stack.pop() == tag, 'Unbalanced BBCode: ' + tag
        else:
            stack.append(tag)
    assert not stack
    assert '\ufffd' not in text
    return text.rstrip() + '\n'


def prepare(source, target):
    source, target = source.resolve(), target.resolve()
    assert source.is_relative_to(ROOT) and target.is_relative_to(ROOT)
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for language in ORDER:
        for kind in ['DESCRIPTION', 'POST', 'CHANGELOG']:
            original = source / f'0.9.5_{kind}_{language}.md'
            name = original.stem + '.bbcode.txt'
            output = target / name
            text = checked(bbcode(original.read_text('utf8')))
            output.write_text(text, 'utf8')
            records.append(dict(language=language, kind=kind, file=name,
                                source=original.name, sourceSha256=sha(original), sha256=sha(output)))
    posts = write_posts(source, target, bbcode)
    description = write_description(source, target, bbcode)
    report = dict(version='0.9.5', languages=len(ORDER), documents=len(records),
                  changesFrom='0.9.4', multipartPosts=posts, records=records, published=False,
                  archivesModified=False, combinedDescription=description)
    (target / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    (target / 'README_RU.md').write_text(
        '# Тексты Nexus для обновления 0.9.5\n\n'
        f'Полное описание главной: `{FILENAME}`. Английский открыт сверху, остальные 12 языков — в отдельных раскрывающихся блоках. Полные отдельные версии — `description-languages`; проверка — `description-manifest.json`.\n\n'
        'Короткий пост EN/RU: `NEXUS_POST_0.9.5_EN_RU.bbcode.txt`. Только крупные изменения после 0.9.4.\n\n'
        'Подробный changelog сохраняет все исправления. Описание, короткое сообщение и changelog подготовлены на 13 языках; исходные Markdown находятся рядом в пакете релиза.\n\n'
        'Копируйте текст в редактор BBCode. Ничего не опубликовано. Проверенные хеши источников и файлов — `manifest.json`.\n', 'utf8')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=NOTES)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = prepare(args.source, args.out or args.source / 'BBCode')
    print(json.dumps({k: v for k, v in report.items() if k != 'records'}, ensure_ascii=False))


if __name__ == '__main__':
    main()

"""Split complete, parallel EN/RU publication copy without dropping paragraphs."""
from pathlib import Path
import hashlib, json, re


def crlf_length(text):
    return len(text.replace('\r\n', '\n').replace('\n', '\r\n'))


def balanced(text):
    stack = []
    for token in re.finditer(r'\[(/?)(b|size|list)(?:=[^\]]+)?\]', text):
        close, tag = token.groups()
        if close:
            assert stack and stack.pop() == tag, 'Unbalanced BBCode: ' + tag
        else:
            stack.append(tag)
    assert not stack


def write_posts(source, target, converter):
    source, target = Path(source), Path(target)
    sources = {lang: source / f'0.9.5_POST_{lang}.md' for lang in ['EN', 'RU']}
    paragraphs = {lang: [p.strip() for p in f.read_text('utf8').split('\n\n') if p.strip()]
                  for lang, f in sources.items()}
    assert len(paragraphs['EN']) == len(paragraphs['RU']), 'Translations must preserve every paragraph'
    # Paragraph kinds must align before pairing; this catches a missing item.
    kind = lambda p: 'heading' if p.startswith('#') else 'item' if p.startswith('- ') else 'text'
    assert [kind(p) for p in paragraphs['EN']] == [kind(p) for p in paragraphs['RU']]
    atoms = {lang: [converter(p).strip() for p in ps] for lang, ps in paragraphs.items()}

    def render(indices, part, total):
        en = '\n\n'.join(atoms['EN'][i] for i in indices)
        ru = '\n\n'.join(atoms['RU'][i] for i in indices)
        return (f'[size=5][b]Gwent Beta Classic 0.9.4 → 0.9.5 — {part}/{total}[/b][/size]\n\n'
                f'[b]English[/b]\n\n{en}\n\n[line]\n\n[b]Русский[/b]\n\n{ru}\n')

    groups, current = [], []
    for index in range(len(atoms['EN'])):
        candidate = current + [index]
        if crlf_length(render(candidate, 99, 99)) > 5000:
            assert current, 'One parallel paragraph exceeds the Nexus post limit'
            groups.append(current)
            current = [index]
            assert crlf_length(render(current, 99, 99)) <= 5000
        else:
            current = candidate
    if current:
        groups.append(current)
    assert [i for group in groups for i in group] == list(range(len(atoms['EN'])))
    target.mkdir(parents=True, exist_ok=True)
    records = []
    for number, indices in enumerate(groups, 1):
        text = render(indices, number, len(groups))
        balanced(text)
        count = crlf_length(text)
        assert count <= 5000
        filename = f'NEXUS_POST_0.9.5_EN_RU_PART_{number:02d}_OF_{len(groups):02d}.bbcode.txt'
        file = target / filename
        file.write_text(text, 'utf8')
        records.append(dict(part=number, file=filename, charactersWithCrLf=count,
                            paragraphIndices=indices, sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
    combined = converter(sources['EN'].read_text('utf8')) + '\n\n[line]\n\n' + converter(sources['RU'].read_text('utf8')) + '\n'
    balanced(combined)
    full = target / 'NEXUS_POST_0.9.5_EN_RU_FULL_REFERENCE.bbcode.txt'
    full.write_text(combined, 'utf8')
    # Keep the established link current; it is a full reference, not one post.
    direct = target / 'NEXUS_POST_0.9.5_EN_RU.bbcode.txt'
    direct.write_text(combined, 'utf8')
    single = crlf_length(combined) <= 5000
    if single:
        records = [dict(part=1, file=direct.name, charactersWithCrLf=crlf_length(combined),
                        paragraphIndices=list(range(len(atoms['EN']))),
                        sha256=hashlib.sha256(direct.read_bytes()).hexdigest())]
    expected_parts = {r['file'] for r in records}
    for stale in target.glob('NEXUS_POST_0.9.5_EN_RU_PART_*_OF_*.bbcode.txt'):
        if stale.name not in expected_parts:
            assert not stale.is_symlink() and stale.resolve().parent == target.resolve()
            stale.unlink()
    report = dict(version='0.9.5', changesFrom='0.9.4', complete=True, perPostLimit=5000,
                  singlePost=single, scope='Public overview; detailed cumulative changelog is separate',
                  languages=['EN', 'RU'], paragraphsPerLanguage=len(atoms['EN']),
                  allParagraphsIncludedExactlyOnce=True, parts=records,
                  fullReference=dict(file=full.name, charactersWithCrLf=crlf_length(combined),
                                     sha256=hashlib.sha256(full.read_bytes()).hexdigest()),
                  sources={lang: dict(file=p.name, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                           for lang, p in sources.items()}, published=False)
    (target / 'nexus-posts-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    rows = ['# Сообщение об обновлении 0.9.4 → 0.9.5 для Nexus', '',
            ('Один короткий пост EN/RU. Только крупные изменения; весь текст вместе с BBCode и CRLF укладывается в 5000 символов.' if single else 'Публикуйте части по порядку. Каждая содержит EN и RU и укладывается в 5000 символов вместе с BBCode и CRLF.'), '',
            '| Часть | Файл | Символов |', '|---|---|---:|']
    rows += [f"| {r['part']}/{len(records)} | [{r['file']}]({r['file']}) | {r['charactersWithCrLf']} |" for r in records]
    rows += ['', 'Подробный список изменений после 0.9.4: `0.9.5_CHANGELOG_EN.md` и `0.9.5_CHANGELOG_RU.md` в пакете релиза.', '',
             'Мелкие исправления сохранены в changelog. Публичный пост содержит краткое описание крупных изменений.',
             'Все абзацы обоих исходников включены ровно один раз; разметка и SHA проверены. Ничего не опубликовано.', '']
    (target / 'NEXUS_MESSAGES_README_RU.md').write_text('\n'.join(rows), 'utf8')
    return report

"""Full Nexus showcase: visible English, twelve independent language spoilers."""
from pathlib import Path
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'docs/releases/0.9.3/nexus'
SAVES = ROOT / 'docs/releases/0.9.4-public-20261026'
FILENAME = 'NEXUS_DESCRIPTION_0.9.5_ALL_LANGUAGES.bbcode.txt'
LANGUAGES = [
    ('EN', 'English'), ('RU', 'Русский'), ('DE', 'Deutsch'),
    ('FR', 'Français'), ('IT', 'Italiano'), ('PL', 'Polski'),
    ('ES', 'Español'), ('ES_MX', 'Español (Latinoamérica)'),
    ('PT_BR', 'Português (Brasil)'), ('JA', '日本語'), ('KO', '한국어'),
    ('ZH_CN', '简体中文'), ('ZH_TW', '繁體中文'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(text):
    stack = []
    for token in re.finditer(r'\[(/?)(b|i|u|size|color|center|list|code|url|spoiler)(?:=[^\]]+)?\]', text):
        close, tag = token.groups()
        if close:
            assert stack and stack.pop() == tag, ('Invalid BBCode hierarchy', tag)
        else:
            stack.append(tag)
    assert not stack, stack
    assert '\ufffd' not in text


def write_description(source, target, converter):
    target.mkdir(parents=True, exist_ok=True)
    per_language = target / 'description-languages'
    per_language.mkdir(exist_ok=True)
    parts, records = [], []
    for index, (code, label) in enumerate(LANGUAGES):
        original = BASE / code.lower().replace('_', '-') / 'description.bbcode.txt'
        body = original.read_text('utf-8-sig').strip()
        # Keep the full reviewed showcase, installation, cleanup, support and
        # credits. Remove its internal folds so one click opens a whole language.
        body = body.replace('[spoiler]', '').replace('[/spoiler]', '')
        first_section = body.index('[size=4]')
        intro = body[:first_section].replace('0.9.3', '0.9.5')
        history_and_features = body[first_section:]
        post = source / f'0.9.5_POST_{code}.md'
        latest = converter(post.read_text('utf8')).strip()
        # Retain the profile/migration information introduced in 0.9.4, without
        # its superseded short introduction or duplicate feature summary.
        saves = SAVES / f'0.9.4_DESCRIPTION_{code}.md'
        sections = re.split(r'(?m)(?=^## )', saves.read_text('utf8'))
        assert len(sections) >= 3 and '0.9.4' in sections[1].splitlines()[0]
        migration = converter(sections[1]).strip()
        rendered = intro.rstrip() + '\n\n' + latest + '\n\n' + migration + '\n\n' + history_and_features
        rendered = re.sub(r'\n{4,}', '\n\n\n', rendered).strip() + '\n'
        validate(rendered)
        assert '[spoiler]' not in rendered
        output = per_language / f'0.9.5_DESCRIPTION_{code}.bbcode.txt'
        output.write_text(rendered, 'utf8')
        records.append(dict(language=code, name=label, file=str(output.relative_to(target)),
                            sha256=sha(output), showcaseSource=str(original.relative_to(ROOT)),
                            showcaseSha256=sha(original), updateSource=str(post.relative_to(ROOT)),
                            updateSha256=sha(post), profileSource=str(saves.relative_to(ROOT)),
                            profileSha256=sha(saves)))
        if index == 0:
            parts.append(rendered.rstrip())
            parts.append('[size=4][b]Translations · Переводы[/b][/size]')
        else:
            parts.append(f'[size=4][b]{label}[/b][/size]\n[spoiler]\n{rendered.rstrip()}\n[/spoiler]')
    combined = '\n\n'.join(parts) + '\n'
    validate(combined)
    assert combined.count('[spoiler]') == combined.count('[/spoiler]') == 12
    english = (per_language / '0.9.5_DESCRIPTION_EN.bbcode.txt').read_text('utf8').strip()
    assert combined.startswith(english) and combined.index('[spoiler]') > len(english)
    for record in records:
        assert combined.count((target / record['file']).read_text('utf8').strip()) == 1
    output = target / FILENAME
    output.write_text(combined, 'utf8')
    report = dict(version='0.9.5', complete=True, file=FILENAME, sha256=sha(output),
                  languages=13, firstVisibleLanguage='EN', collapsedLanguages=12,
                  nestedSpoilers=False, balancedBbcode=True,
                  charactersWithCrLf=len(combined.replace('\n', '\r\n')),
                  content='Full showcase, current overview, profile migration, installation, compatibility, cleanup, support and credits',
                  published=False, records=records,
                  formattingReference='https://forums.nexusmods.com/topic/13458901-guidance-to-update-your-bbcode-december-2023/')
    (target / 'description-manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', 'utf8')
    return report

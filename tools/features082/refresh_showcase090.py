"""Build the 13-language Nexus showcase and an offline visual proof.

manual.md preserves the complete pre-showcase publication text. Edit player
instructions there; edit the introduction in nexus090_showcase.json, then rerun.
No game files, release archives, changelogs or publication endpoints are changed.
"""
from pathlib import Path
import base64
import hashlib
import html
import importlib.util
import json
import re
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/releases/0.9.0/nexus'
DATA = ROOT / 'data/beta924/design/nexus090_showcase.json'
ORDER = ['en', 'ru', 'de', 'fr', 'it', 'pl', 'es', 'es-mx', 'pt-br', 'ja', 'ko', 'zh-cn', 'zh-tw']
NAMES = dict(zip(ORDER, ['English', 'Русский', 'Deutsch', 'Français', 'Italiano', 'Polski', 'Español', 'Español (Latinoamérica)', 'Português (Brasil)', '日本語', '한국어', '简体中文', '繁體中文']))
HTML_LANG = {'es-mx': 'es-MX', 'pt-br': 'pt-BR', 'zh-cn': 'zh-Hans', 'zh-tw': 'zh-Hant'}
spec = importlib.util.spec_from_file_location('nexus_bbcode', ROOT / 'tools/universal/prepare_nexus081.py')
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + '\n', encoding='utf8')


def inline(value):
    value = html.escape(value)
    value = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', value)
    value = re.sub(r'`([^`]+)`', r'<code>\1</code>', value)
    return re.sub(r'\[([^\]]+)\]\((https://[^)]+)\)', r'<a href="\2">\1</a>', value)


def markdown_html(value):
    """Small renderer for the existing publication dialect; escape raw HTML."""
    out = []
    paragraph = []
    listing = None
    code = None

    def flush():
        if paragraph:
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()

    def close_list():
        nonlocal listing
        if listing:
            out.append('</' + listing + '>')
            listing = None

    for line in value.splitlines():
        if line.startswith('```'):
            flush()
            close_list()
            if code is not None:
                out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
                code = None
            else:
                code = []
            continue
        if code is not None:
            code.append(line)
            continue
        if not line.strip():
            flush()
            close_list()
            continue
        heading = re.match(r'^(#{1,3}) (.*)', line)
        item = re.match(r'^(?:- |(\d+)\. )(.*)', line)
        if heading:
            flush()
            close_list()
            level = min(4, len(heading[1]) + 1)
            out.append(f'<h{level}>' + inline(heading[2]) + f'</h{level}>')
        elif item:
            flush()
            kind = 'ol' if item[1] else 'ul'
            if listing != kind:
                close_list()
                listing = kind
                out.append('<ol start="' + item[1] + '">' if kind == 'ol' else '<ul>')
            out.append('<li>' + inline(item[2]) + '</li>')
        else:
            close_list()
            paragraph.append(line.removeprefix('> '))
    flush()
    close_list()
    assert code is None
    return '\n'.join(out)


def validate_bbcode(value):
    stack = []
    for match in re.finditer(r'\[(/?)([a-z]+)(?:=[^\]]+)?\]', value):
        closing, tag = match.groups()
        if tag == 'line':
            continue
        if closing:
            assert stack and stack.pop() == tag, match[0]
        else:
            stack.append(tag)
    assert not stack, stack
    assert '**' not in value and '\ufffd' not in value


CSS = '''
:root{color-scheme:dark;--paper:#eee9dc;--muted:#b8bfb5;--gold:#e0b354;--line:#a687453d;--panel:#17221f}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:95px}body{margin:0;color:var(--paper);background:radial-gradient(ellipse at 12% 18%,#23423555,transparent 45%),#0b1311;font:17px/1.8 "Segoe UI",Arial,sans-serif}button,select,a{touch-action:manipulation}a{color:var(--gold);text-underline-offset:4px}a:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--gold);outline-offset:5px}header{position:sticky;top:0;z-index:10;background:#0b1311f5;border-bottom:1px solid var(--line);backdrop-filter:blur(16px)}.nav{max-width:1160px;margin:auto;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:14px 28px}.brand{font:600 15px Georgia,serif;letter-spacing:3px}.nav label{font-size:12px;color:var(--muted)}select{margin-left:10px;max-width:210px;background:#17221f;color:var(--paper);border:1px solid #78663d;border-radius:3px;padding:9px 12px;font:inherit;font-size:14px}main{max-width:1160px;margin:auto;padding:0 28px 70px}.hero{text-align:center;padding-bottom:20px}.banner{display:block;width:100%;height:auto;margin:0 auto 26px;border-bottom:1px solid var(--line)}.eyebrow{font-size:11px;letter-spacing:2.4px;color:var(--gold);margin:22px 0}h1,h2,h3,h4{font-family:Georgia,"Times New Roman",serif;font-weight:400;line-height:1.2;text-wrap:balance}h1{font-size:clamp(36px,5.3vw,66px);max-width:900px;margin:16px auto 26px}h2{font-size:clamp(30px,3.4vw,43px);margin:0 0 32px}h3{font-size:25px;margin:0 0 15px}h4{font-size:21px;color:var(--gold)}p{margin:0 0 18px}.lead{font-size:20px;max-width:810px;margin:0 auto 22px;color:#dadfd5}.moment{font:italic 20px/1.7 Georgia,serif;color:var(--muted);max-width:750px;margin:0 auto 25px}.stats{display:grid;grid-template-columns:repeat(4,1fr);border-block:1px solid var(--line);margin:45px 0 24px}.stat{padding:22px 14px;font-size:14px;line-height:1.5;display:flex;align-items:center;justify-content:center;min-height:100px}.stat+.stat{border-left:1px solid var(--line)}.stat b{display:block;font:37px/1.2 Georgia,serif;color:var(--gold);margin-bottom:6px}.section{padding:50px 0;border-bottom:1px solid var(--line)}.features{display:grid;grid-template-columns:1fr 1fr;gap:38px 58px}.feature{position:relative;padding-top:26px}.feature:before{content:attr(data-index);color:var(--gold);font-size:11px;letter-spacing:3px;display:block;margin-bottom:12px}.feature p,.faction p{color:var(--muted)}.factions{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.faction{padding:24px 18px 14px;background:linear-gradient(160deg,var(--tint),transparent 85%),var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent)}.faction:nth-child(1){--accent:#cf6657;--tint:#693c3330}.faction:nth-child(2){--accent:#cca544;--tint:#695a2630}.faction:nth-child(3){--accent:#6f9fc1;--tint:#27475e30}.faction:nth-child(4){--accent:#84ab70;--tint:#385c2d30}.faction:nth-child(5){--accent:#ad8dc3;--tint:#51386830}.faction h3{font-size:21px;color:var(--paper);overflow-wrap:anywhere}.faction p{font-size:14px;line-height:1.75}.cta{border:1px solid #b08e48;margin:56px 0 12px;padding:40px;text-align:center;background:radial-gradient(ellipse at top,#b08e4815,transparent 75%),#17221f}.cta h2{margin-bottom:20px}.cta p{max-width:760px;margin:0 auto 24px}.button{display:inline-block;padding:11px 24px;background:var(--gold);border:1px solid var(--gold);color:#142018;font-weight:600;text-decoration:none;font-size:14px;line-height:1.5}.button:hover{background:#f1ca78}.guide{max-width:890px;margin:auto}.guide h3{font-size:28px;margin-top:34px}.guide p,.guide li{color:#c4cdc3}.guide ul,.guide ol{padding-left:24px}.guide li{padding:5px 0}details{margin:14px 0;border:1px solid var(--line);background:#17221f66}summary{cursor:pointer;padding:19px 23px;color:var(--gold);font-size:15px;line-height:1.6}details[open]>summary{border-bottom:1px solid var(--line)}.detail-body{padding:7px 24px 24px}.detail-body h3{font-size:26px}.detail-body p,.detail-body li{font-size:15px}pre{padding:18px;background:#08100e;overflow:auto;border-left:2px solid var(--gold);line-height:1.6;font-size:13px;white-space:pre-wrap;overflow-wrap:anywhere}code{font-size:.9em}footer{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;padding-top:25px;color:var(--muted);font-size:12px;letter-spacing:.6px}[hidden]{display:none!important}@media(max-width:850px){.factions{grid-template-columns:repeat(2,1fr)}.faction:last-child{grid-column:1/-1}.features{gap:28px}.nav{padding-inline:20px}.brand{letter-spacing:1px;font-size:13px}}@media(max-width:560px){body{font-size:16px}main{padding-inline:18px}.nav{gap:8px;padding:11px 18px}.brand{max-width:120px;line-height:1.5}.nav label{font-size:0}select{font-size:13px;margin:0;max-width:175px}.banner{margin-bottom:22px}.eyebrow{font-size:9px;letter-spacing:1px}.lead{font-size:18px}.moment{font-size:18px}.stats{grid-template-columns:1fr 1fr;margin-top:30px}.stat{padding:17px 8px;min-height:100px;font-size:12px}.stat:nth-child(3){border-left:0;border-top:1px solid var(--line)}.stat:nth-child(4){border-top:1px solid var(--line)}.stat b{font-size:31px}.section{padding:35px 0}.features,.factions{grid-template-columns:1fr}.faction:last-child{grid-column:auto}.faction{padding:20px}.faction h3{font-size:23px}.faction p{font-size:15px}.cta{padding:27px 18px;margin-top:35px}.detail-body{padding-inline:16px}summary{padding:16px}.guide h3{font-size:25px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{header{position:static}.banner{max-height:190px;object-fit:contain}body{background:white;color:#111}.section,.cta,details{break-inside:avoid}.lead,.moment,.feature p,.faction p,.guide p,.guide li{color:#333}}
'''


def main():
    data = json.loads(DATA.read_text('utf8'))
    assert set(data) == set(ORDER)
    banner_source = ROOT / 'BetaGwent/release/nexus/GwentBetaClassic-header-v2.jpg'
    assert banner_source.exists(), 'Run python tools/build_nexus_header95.py first.'
    assets = OUT / 'assets'
    assets.mkdir(exist_ok=True)
    shutil.copyfile(banner_source, assets / 'GwentBetaClassic-header.jpg')
    image_uri = 'data:image/jpeg;base64,' + base64.b64encode(banner_source.read_bytes()).decode('ascii')
    bodies, rendered, previews = {}, {}, {}
    manuals = {}
    for lang in ORDER:
        folder = OUT / lang
        manual = folder / 'manual.md'
        if not manual.exists():
            # Keep all previously reviewed operational instructions verbatim.
            shutil.copyfile(folder / 'description.md', manual)
        source = manual.read_text('utf-8-sig')
        sections = re.split(r'(?m)^## ', source)
        assert len(sections) == 18, (lang, len(sections))
        sections = ['## ' + part.strip() + '\n' for part in sections[1:]]
        manuals[lang] = hashlib.sha256(manual.read_bytes()).hexdigest()
        d = data[lang]
        assert len(d['features']) == 4 and len(d['factions']) == 5 and len(d['stats']) == 4
        showcase = '# Gwent Beta Classic\n\n> ' + d['tagline'] + '\n\n## ' + d['headline'] + '\n\n' + d['intro'] + '\n\n' + d['moment'] + '\n\n'
        showcase += '\n'.join('- **' + s + '**' for s in d['stats']) + '\n\n## ' + d['whyTitle'] + '\n\n'
        showcase += '\n\n'.join('### ' + title + '\n\n' + body for title, body in d['features'])
        showcase += '\n\n## ' + d['factionsTitle'] + '\n\n'
        showcase += '\n\n'.join('### ' + title + '\n\n' + body for title, body in d['factions'])
        showcase += '\n\n## ' + d['ctaTitle'] + '\n\n' + d['cta'] + '\n\n'
        essentials = '## ' + d['guideTitle'] + '\n\n' + '\n\n'.join(sections[i] for i in [7, 10, 0, 8])
        # The old general overview is replaced by the new introduction; all
        # other sections are carried across in full, including safety wording.
        groups = [(d['detailsTitle'], [4, 1, 2, 5, 6]), (d['compatTitle'], [9, 11, 12, 13]), (d['supportTitle'], [14, 15, 16])]
        details_md = ''
        details_bb = ''
        details_html = ''
        for label, indices in groups:
            text = '\n\n'.join(sections[i] for i in indices)
            details_md += '\n\n<details>\n<summary>' + label + '</summary>\n\n' + text + '\n\n</details>'
            details_bb += '\n\n[color=#e0b354][b]' + label + '[/b][/color]\n[spoiler]\n' + bb.bbcode(text) + '[/spoiler]\n'
            details_html += '<details><summary>' + html.escape(label) + '</summary><div class="detail-body">' + markdown_html(text) + '</div></details>'
        bodies[lang] = showcase + essentials + details_md + '\n'
        # Typography has a distinct hero, compact numeric ribbon and gold
        # section headings while staying within the existing BBCode dialect.
        hero_bb = '[center][size=6][color=#e0b354][b]' + d['headline'] + '[/b][/color][/size]\n\n'
        hero_bb += '[size=2]' + d['tagline'] + '[/size]\n\n' + '  ·  '.join('[b]' + s + '[/b]' for s in d['stats']) + '[/center]\n\n'
        middle = showcase.split('## ' + d['headline'] + '\n\n', 1)[1]
        # The numeric ribbon already includes these four bullets.
        middle = middle.replace('\n'.join('- **' + s + '**' for s in d['stats']) + '\n\n', '', 1)
        rendered[lang] = hero_bb + bb.bbcode(middle + essentials) + details_bb
        validate_bbcode(rendered[lang])
        write(folder / 'description.md', bodies[lang])
        write(folder / 'description.bbcode.txt', rendered[lang])
        stats = ''.join('<div class="stat"><div>' + re.sub(r'^(\d+)', r'<b>\1</b>', html.escape(s)) + '</div></div>' for s in d['stats'])
        features = ''.join('<article class="feature" data-index="0' + str(i + 1) + '"><h3>' + html.escape(title) + '</h3><p>' + inline(body) + '</p></article>' for i, (title, body) in enumerate(d['features']))
        factions = ''.join('<article class="faction"><h3>' + html.escape(title) + '</h3><p>' + inline(body) + '</p></article>' for title, body in d['factions'])
        previews[lang] = f'''<section class="hero"><img class="banner" src="{image_uri}" alt="Gwent Beta Classic — Geralt and Ciri"><p class="eyebrow">{html.escape(d['tagline'])}</p><h1>{html.escape(d['headline'])}</h1><p class="lead">{inline(d['intro'])}</p><p class="moment">{inline(d['moment'])}</p><div class="stats">{stats}</div></section>
<section class="section"><h2>{html.escape(d['whyTitle'])}</h2><div class="features">{features}</div></section>
<section class="section"><h2>{html.escape(d['factionsTitle'])}</h2><div class="factions">{factions}</div></section>
<section class="cta"><h2>{html.escape(d['ctaTitle'])}</h2><p>{inline(d['cta'])}</p><a class="button" href="#guide-{lang}">{html.escape(d['guideTitle'])} ↓</a></section>
<section class="section guide" id="guide-{lang}"><h2>{html.escape(d['guideTitle'])}</h2>{markdown_html(essentials.split('\n\n', 1)[1])}{details_html}</section>'''
        # Preserve every non-overview section, including the complete command
        # examples, clipboard limitations, language caveats and uninstall steps.
        for index, section in enumerate(sections):
            if index != 3:
                assert section.strip() in bodies[lang], (lang, index)
        for token in ['479', '21', '46', '13', 'BG1', 'Optional-CopyButton', 'bg_clean_confirm', 'DELETE_BETA_GWENT', 'bg_clean_keys', '1.32', '5.0+', '203', '197']:
            assert token in bodies[lang], (lang, token)
        assert '\ufffd' not in bodies[lang]
    intro = '[center][size=6][color=#e0b354][b]GWENT BETA CLASSIC[/b][/color][/size]\n[size=3]The Witcher 3 · Gwent Beta 0.9.24 · 0.9.0[/size]\n\n[b]Classic 1.32  /  Next-Gen 5.0+  /  Steam Deck[/b]\n\nEnglish ↓\nLanguage · Язык · Sprache · Langue · Lingua · Język · Idioma · 言語 · 언어 · 语言 · 語言\n[/center]\n'
    combined = intro
    for lang in ORDER[1:]:
        combined += '\n[b]' + NAMES[lang] + '[/b]\n[spoiler]\n' + rendered[lang] + '\n[/spoiler]\n'
    combined += '\n[line]\n[b]English[/b]\n\n' + rendered['en']
    validate_bbcode(combined)
    write(OUT / 'NEXUS_DESCRIPTION_0.9.0.bbcode.txt', combined)
    write(OUT / 'DESCRIPTION_0.9.0.md', '# Gwent Beta Classic 0.9.0\n\n' + '\n\n'.join('<details' + (' open' if lang == 'en' else '') + '><summary>' + NAMES[lang] + '</summary>\n\n' + bodies[lang] + '\n</details>' for lang in ORDER))
    options = ''.join('<option value="' + lang + '"' + (' selected' if lang == 'ru' else '') + '>' + NAMES[lang] + '</option>' for lang in ORDER)
    pages = ''.join('<article data-lang="' + lang + '" lang="' + HTML_LANG.get(lang, lang) + '"' + (' hidden' if lang != 'ru' else '') + '>' + previews[lang] + '</article>' for lang in ORDER)
    # Each image is embedded once; all language articles share the same source.
    image_attribute = 'src="' + image_uri + '"'
    pages = pages.replace(image_attribute, 'data-banner')
    script = '''const select=document.querySelector('select');const articles=[...document.querySelectorAll('[data-lang]')];const valid=new Set(articles.map(x=>x.dataset.lang));function choose(lang,remember=true){if(!valid.has(lang))lang='ru';for(const article of articles)article.hidden=article.dataset.lang!==lang;document.documentElement.lang=articles.find(x=>x.dataset.lang===lang).lang;document.title='Gwent Beta Classic — '+select.querySelector('[value="'+lang+'"]').textContent;select.value=lang;if(remember){history.replaceState(null,'','#'+lang);try{localStorage.setItem('gwent-showcase-language',lang)}catch{}}}document.querySelectorAll('[data-banner]').forEach(img=>img.src=BANNER);let initial=location.hash.slice(1);if(!valid.has(initial)){try{initial=localStorage.getItem('gwent-showcase-language')}catch{}}choose(valid.has(initial)?initial:'ru',false);select.addEventListener('change',()=>{choose(select.value);window.scrollTo({top:0,behavior:'instant'})});'''
    narrow_css = '.guide{overflow-wrap:anywhere}@media(max-width:560px){.brand{max-width:100px;font-size:11px}select{max-width:160px}.button{max-width:100%;overflow-wrap:anywhere}}'
    page = '<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gwent Beta Classic</title><style>' + CSS + narrow_css + '</style></head><body><header><div class="nav"><span class="brand">GWENT BETA CLASSIC</span><label>Language / Язык <select aria-label="Language / Язык">' + options + '</select></label></div></header><main>' + pages + '<footer><span>GWENT BETA CLASSIC · 0.9.0</span><a href="https://github.com/NikRegul/GwentBetaClassic-">GitHub ↗</a></footer></main><script>const BANNER=' + json.dumps(image_uri) + ';' + script + '</script></body></html>'
    write(OUT / 'preview.html', page)
    report = dict(version='0.9.0', descriptionLanguages=13, languageSpoilers=12, detailSpoilersPerLanguage=3, spoilers=combined.count('[spoiler]'), englishDefault=True, previewDefault='ru', bbcodeBalanced=True, preservedManualSectionsPerLanguage=16, manualSha256=manuals, postLanguages=['en', 'ru'], embeddedCleaner=True, published=False, bbcodeFiles=sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob('*.bbcode.txt')))
    for p in OUT.rglob('*.bbcode.txt'):
        validate_bbcode(p.read_text('utf8'))
    write(OUT / 'validation.json', json.dumps(report, ensure_ascii=False, indent=2))
    write(OUT / 'README_RU.md', '''# Описание Nexus 0.9.0 — новая подача на 13 языках

[Открыть визуальный предпросмотр](preview.html) — автономный HTML: русский при первом открытии, переключение всех 13 языков, адаптация к телефону, баннер внутри файла. Это макет оформления; внешний вид редактора Nexus может отличаться.

[NEXUS_DESCRIPTION_0.9.0.bbcode.txt](NEXUS_DESCRIPTION_0.9.0.bbcode.txt) — готовое описание целиком для режима исходного BBCode в Nexus. Английский открыт, 12 остальных языков раскрываются отдельно. На каждом языке есть атмосферное вступление, цифры, четыре причины попробовать, пять фракций, приглашение сыграть и установка. Технические разделы собраны в три раскрывающихся блока.

В папках языков: description.md — полная новая страница; description.bbcode.txt — готовый текст на одном языке; manual.md — сохранённые прежние инструкции, источник технических разделов. Сохранены все 16 разделов, кроме прежнего краткого «О моде», которое заменено новым вступлением. Посты и changelog не изменялись.

assets/GwentBetaClassic-header.jpg — баннер 1800×600 из оригинального логотипа и артов Геральта/Цири. Его можно загрузить в редактор Nexus и поставить над описанием. В BBCode нет вымышленных ссылок на ещё не загруженные картинки. Полный архив для передачи: BetaGwent/release/GwentBetaClassic-0.9.0-Nexus-Showcase-13-Languages.zip.

Новый авторский текст хранится в data/beta924/design/nexus090_showcase.json. Инструкции правятся в языковых manual.md. Повторная генерация из корня проекта:

```powershell
python tools/features082/refresh_showcase090.py
```

Используйте этот генератор для нового описания: прежний prepare_publication090.py восстанавливает старую структуру из исторических входов. Проверки структуры и сохранности инструкций выполняются при генерации; результаты — validation.json. Переводы новых рекламных текстов требуют обычной вычитки носителями, особенно терминов восточноазиатских локализаций.

Материалы подготовлены локально, публикация не выполнялась. Игровые файлы и архивы мода не менялись. Предпросмотр не является проверкой работоспособности мода в игре.
''')
    archive = ROOT / 'BetaGwent/release/GwentBetaClassic-0.9.0-Nexus-Showcase-13-Languages.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():
                z.write(p, 'Nexus-Showcase/' + p.relative_to(OUT).as_posix())
        z.write(DATA, 'Sources/nexus090_showcase.json')
        z.write(Path(__file__), 'Sources/refresh_showcase090.py')
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    print(json.dumps(dict(languages=13, manualSectionsPreserved=16, bbcodeBalanced=True, preview=str(OUT / 'preview.html'), archive=str(archive), archiveBytes=archive.stat().st_size), ensure_ascii=False))


if __name__ == '__main__':
    main()

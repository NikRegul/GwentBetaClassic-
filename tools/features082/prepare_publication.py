"""Build future 0.8.2 Nexus copy; never publish or alter game packages."""
from pathlib import Path
import importlib.util
import json
import re
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/releases/0.8.2/nexus'
DATA = ROOT / 'data/beta924/design/nexus082_updates.json'
ORDER = ['en', 'ru', 'de', 'fr', 'it', 'pl', 'es', 'es-mx', 'pt-br', 'ja', 'ko', 'zh-cn', 'zh-tw']
NAMES = dict(zip(ORDER, ['English', 'Русский', 'Deutsch', 'Français', 'Italiano', 'Polski', 'Español (España)', 'Español (Latinoamérica)', 'Português (Brasil)', '日本語', '한국어', '简体中文', '繁體中文']))
spec = importlib.util.spec_from_file_location('nexus081', ROOT / 'tools/universal/prepare_nexus081.py')
bb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bb)

EXAMPLES = """bg_help()
bg_status()
bg_find('Imlerith')
bg_card(132102,1)
bg_faction('monsters')
bg_leaders()
bg_allcards()
bg_kegs(10)
bg_scraps(1000)
bg_shopcheck()
bg_shoprefill(5)"""

CHANGELOG = {
'ru': '''# Gwent Beta Classic 0.8.2 — Список изменений

## Обмен колодами

- Импорт и экспорт через буфер обмена в формате BG1. Код не зависит от языка, сохраняет фракцию, лидера и состав, пригоден для обмена между игроками.
- Импорт доступен из списка колод и редактора; экспорт — в редакторе. При недоступном прямом доступе к буферу остаётся текстовое поле для Ctrl+C/Ctrl+V.
- Неверная строка не меняет колоды, коллекцию или баланс. Проверяются карты, фракция, лидер, размер и ограничения состава.
- Показ недостающих карт, включая лидера, количества копий и общей стоимости. Создание выполняется отдельным действием при достаточном балансе; незавершённый выбор оплаченной бочки блокирует создание.
- Импорт создаёт черновик. Сохранение выполняется обычной кнопкой; занятые пользовательские слоты автоматически не перезаписываются.

## Консоль

- Добавлены справка, состояние коллекции, поиск карт, выдача карт/лидеров/фракций, бочек и осколков, диагностика и пополнение бочек у корчмаря.
- Соблюдаются лимиты копий; неверные параметры и опасное переполнение счётчиков отвергаются. Выдача ресурсов закрыта во время меню и партии, команды магазина требуют открытого магазина.

## Интерфейс и контроллер

- Новые подписи и сообщения обмена переведены на все 13 языков; дополнены недостающие символы японских, корейских и китайских шрифтов.
- Импорт списка колод перенесён в нижнюю панель. Действия редактора выровнены; состояние колоды, счётчики и отмена редактирования получили отдельное место и отступы.
- Переработаны отступы меню матча, окон выхода и обмена, заголовка подтверждения и подсказок контроллера.
- Нажатие вниз с нижнего видимого ряда карточной полки переводит фокус к действиям, включая сохранение; вверх возвращает к картам. LB/RB и правый стик сохраняют прокрутку.
- Исправлено открытие импорта и экспорта непосредственно из редактора колоды.

## Визуальные эффекты и звук

- Погибшие карты, которые по правилам уходят в сброс, летят к фактическому сбросу своей стороны; особые карты — после разрешения эффекта. Сыгранные отряды остаются на поле согласно правилам. Эффекты изгнания, растворения и поглощения сохранены.
- Портреты лидеров после однократного входа VS продолжают обычную анимацию. Добавлена повторная загрузка страницы при временном сбое.
- Вход королевы главоглазов синхронизирован с фактическим запуском её озвучки с учётом стороны, очереди реплик, пропуска и выключенных голосов.
- В сборку Classic 1.32 включены принятые исправления постоянного мороза, видимости снарядов и попаданий.

## Сохранения и совместимость

- Встроены 203 отсутствующих определения старых предметов Redux для обычного прохождения и НГ+, без замены 197 штатных определений. Это защита загрузки старого инвентаря, а не восстановление уже потерянных данных или конвертация коллекции Redux.
- Сохранены все 13 языков текста, пять озвучек и независимый выбор текста и голосов. Для Classic 1.32 и Next-Gen 5.0+ используются отдельные пакеты.
''',
'en': '''# Gwent Beta Classic 0.8.2 — Changelog

## Deck sharing

- Clipboard import and export using BG1 codes. Codes are language-independent and contain the faction, leader and card list for sharing between players.
- Import from the deck list or editor; export from the editor. A text field supports Ctrl+C/Ctrl+V when direct clipboard access is unavailable.
- Invalid codes leave decks, collection and balance unchanged. Validation covers card IDs, faction, leader, deck size and composition limits.
- Missing cards, including the leader, are listed with copy counts and total scrap cost. Crafting is a separate action requiring enough scraps; an unfinished paid keg choice blocks crafting.
- Import creates a draft. Save it with the usual button; occupied custom slots are never overwritten automatically.

## Console

- Added help, collection status, card search, card/leader/faction grants, keg and scrap grants, and innkeeper keg stock diagnostics and refill.
- Normal copy limits are enforced; invalid parameters and counter overflow are rejected. Resource grants are blocked in menus and matches; shop commands require an open shop.

## Interface and controller

- New deck exchange labels and messages translated into all 13 text languages, with missing Japanese, Korean and Chinese font glyphs added.
- Deck-list Import moved into the bottom action bar. Editor actions are aligned; deck status, counters and Undo have dedicated space and padding.
- Updated spacing in match menus, exit and exchange dialogs, confirmation titles and controller hints.
- Down from the bottom visible shelf row moves focus to actions, including Save; Up returns to cards. LB/RB and the right stick still scroll.
- Fixed opening Import and Export directly from the deck editor.

## Visuals and audio

- Dead cards that go to the graveyard now fly toward their actual side's graveyard; special cards do the same after resolution. Played units remain on the board as required by the rules. Banish, dissolve and consume effects are preserved.
- Leader portraits continue their normal animation after the one-shot VS entrance. Temporary page-load failures can retry.
- Arachas Queen's entrance is synchronized with the actual start of her voice, including seat order, queued lines, skipping and disabled voices.
- Classic 1.32 includes the accepted fixes for persistent frost, visible projectiles and impacts.

## Saves and compatibility

- Integrated 203 missing legacy Redux item definitions for normal games and New Game+, preserving 197 native definitions. This protects loading old inventory; it neither recovers already lost data nor converts Redux collections.
- All 13 text languages, five voice languages and independent text/voice selection are retained. Classic 1.32 and Next-Gen 5.0+ use separate packages.
'''
}
POST = {
'ru': '''# Gwent Beta Classic 0.8.2

В 0.8.2 можно делиться колодами: экспорт скопирует BG1-код в буфер, а импорт соберёт по нему черновик. Если карт не хватает, мод покажет список и стоимость создания. Создание — отдельным действием, сохранение колоды — обычной кнопкой. Неверный код ничего не меняет.

Добавлены консольные команды для поиска карт, коллекции, бочек, осколков и запаса бочек у корчмаря. Начните с bg_help().

Поправлены отступы меню и низ редактора, переведены сообщения обмена на все 13 языков. С контроллера теперь можно перейти вниз с видимого ряда карт к сохранению и вернуться вверх. Погибшие карты и разрешённые особые карты летят в свой сброс; портреты лидеров продолжают двигаться после VS, а вход королевы главоглазов привязан к её озвучке.

Для Classic 1.32 включены исправления мороза и эффектов ударов. Встроены определения старых предметов Redux для перехода со старого сохранения. Они не возвращают уже потерянный инвентарь: используйте копию до его потери.

Выбирайте отдельный пакет для 1.32 или 5.0+. В каждом — все 13 языков текста и пять озвучек. Перед обновлением сохраните резервную копию сейвов и прежних папок мода; для Classic обновите также входящий в архив DLC.

Спасибо за сообщения об ошибках и предложения! Для отчёта укажите версию игры, язык текста/голосов, карты и шаги повторения; по возможности приложите скриншот или видео и сохранение перед проблемой.
''',
'en': '''# Gwent Beta Classic 0.8.2

Share your decks in 0.8.2: Export copies a BG1 code to the clipboard, and Import builds a draft from it. Missing cards are listed with their crafting cost. Crafting is a separate action, and the deck is saved with the usual button. Invalid codes change nothing.

New console commands cover card search, collections, kegs, scraps and innkeeper keg stock. Start with bg_help().

Menu spacing and the deck editor footer have been improved, and exchange messages are translated into all 13 text languages. Controllers can move down from the visible card row to Save and return with Up. Dead cards and resolved special cards fly to their graveyard; leader portraits keep moving after VS, and Arachas Queen's entrance follows her voice playback.

Classic 1.32 includes frost and attack effect fixes. Legacy Redux item definitions are integrated for loading an older save after switching mods. They do not restore inventory already lost: use a backup from before the loss.

Choose the separate package for 1.32 or 5.0+. Each contains all 13 text languages and five voice languages. Back up your saves and previous mod folders before updating; Classic also needs its included DLC folder updated.

Thanks for your bug reports and suggestions! Include the game version, text/voice languages, involved cards and reproduction steps; a screenshot or video and a save from before the problem are helpful.
'''
}

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + '\n', encoding='utf-8-sig')

def main():
    updates = json.loads(DATA.read_text('utf8'))
    assert set(updates) == set(ORDER)
    descriptions = []
    # The complete previous descriptions retain their translated features,
    # language lists, save backup advice, requirements, reporting and credits.
    adjacent = {'en': ('adjacent', 'separate'), 'ru': ('соседними', 'отдельными'),
                'de': ('nebeneinanderliegenden', 'separaten'), 'fr': ('adjacents', 'distincts')}
    for lang in ORDER:
        source = (ROOT / 'docs/releases/0.8.1/nexus' / lang / 'description.md').read_text('utf-8-sig')
        parts = re.split(r'(?m)^## ', source)
        assert len(parts) == 11, (lang, len(parts))
        d = updates[lang]
        preamble = re.sub(r'^> .*$', '> ' + d['status'], parts[0].replace('0.8.1', '0.8.2'), flags=re.M)
        important = parts[1].split('\n\n')
        assert len([p for p in important if p.strip()]) == 3
        parts[1] = important[0] + '\n\n' + important[1] + '\n\n' + d['translation'] + '\n\n'
        parts[4] = d['heading'] + '\n\n' + '\n'.join('- ' + c for c in d['changes']) + '\n\n'
        parts[4] += '## ' + d['exchangeHeading'] + '\n\n' + d['exchange'].replace('\\n', '\n') + '\n\n'
        parts[4] += '## ' + d['consoleHeading'] + '\n\n' + d['console'] + '\n\n```text\n' + EXAMPLES + '\n```\n\n'
        installation = parts[6]
        installation, count = re.subn(r'(?m)^3\. .*$', '3. ' + d['install'], installation)
        assert count == 1
        parts[6] = installation
        parts[8] = parts[8].split('\n', 1)[0] + '\n\n' + d['compat'] + '\n\n'
        body = preamble + ''.join('## ' + p for p in parts[1:])
        if lang in adjacent:
            body = body.replace(*adjacent[lang])
        assert '0.8.1' not in body and '\ufffd' not in body
        folder = OUT / lang
        write(folder / 'description.md', body)
        rendered = bb.bbcode(body)
        write(folder / 'description.txt', rendered)
        descriptions.append((lang, body, rendered))
        if lang in CHANGELOG:
            for kind, texts in [('changelog', CHANGELOG), ('post', POST)]:
                write(folder / (kind + '.md'), texts[lang])
                write(folder / (kind + '.txt'), bb.bbcode(texts[lang]))
                write(OUT / f'NEXUS_{kind.upper()}_0.8.2_{lang.upper()}.txt', bb.bbcode(texts[lang]))
    combined = '[center][size=6][b]Gwent Beta Classic 0.8.2[/b][/size]\nGwent Beta 0.9.24 inside The Witcher 3\nEnglish below; 12 translations in spoilers.[/center]\n\n' + descriptions[0][2]
    for lang, _, rendered in descriptions[1:]:
        combined += '\n[line]\n[b]' + NAMES[lang] + '[/b]\n[spoiler]\n' + rendered + '[/spoiler]\n'
    write(OUT / 'NEXUS_DESCRIPTION_0.8.2.txt', combined)
    write(OUT / 'DESCRIPTION_ALL_LANGUAGES.md', '\n\n---\n\n'.join(t[1] for t in descriptions))
    write(OUT / 'README_RU.md', '''# Тексты Nexus для будущего релиза 0.8.2

NEXUS_DESCRIPTION_0.8.2.txt — полное описание BBCode: English открыт, 12 переводов в spoilers. Можно вставить целиком в описание Nexus.

Языковые папки содержат полные description.md и description.txt для всех 13 языков мода. Markdown предназначен для редактирования, TXT — для вставки в режиме BBCode. DESCRIPTION_ALL_LANGUAGES.md объединяет описания.

Changelog и post подготовлены только на RU и EN: файлы NEXUS_CHANGELOG_0.8.2_RU/EN.txt и NEXUS_POST_0.8.2_RU/EN.txt; редактируемые версии находятся в ru и en.

Это тексты для будущей публикации версии 0.8.2, без RC и внутренних статусов. Ничего не опубликовано на Nexus; игровые ZIP и установленные файлы не изменены. В описании не заявлено, что все функции прошли игровую приёмку.

Источник общих разделов — полные переводы описания 0.8.1. Новые разделы хранятся в data/beta924/design/nexus082_updates.json. Повторная генерация: python tools/features082/prepare_publication.py. Сценарии регрессий находятся отдельно в docs/releases/0.8.2/regression.
''')
    allowed = re.compile(r'\[(/?)([a-z]+)(?:=[^\]]+)?\]')
    checked = []
    for path in sorted(OUT.rglob('*.txt')):
        text = path.read_text('utf-8-sig')
        stack = []
        for tag in allowed.finditer(text):
            close, name = tag.groups()
            if name == 'line':
                continue
            if close:
                assert stack and stack.pop() == name, (path, tag.group())
            else:
                stack.append(name)
        assert not stack, (path, stack)
        assert '\ufffd' not in text
        checked.append(str(path.relative_to(OUT)))
    assert len(list(OUT.glob('*/description.md'))) == 13
    assert len(list(OUT.glob('*/post.md'))) == len(list(OUT.glob('*/changelog.md'))) == 2
    report = dict(languages=ORDER, bbcodeFiles=len(checked), checked=checked, published=False,
                  sourceDataSha256=hashlib.sha256(DATA.read_bytes()).hexdigest())
    write(OUT / 'validation.json', json.dumps(report, ensure_ascii=False, indent=2))
    archive = ROOT / 'BetaGwent/release/GwentBetaClassic-0.8.2-Nexus-Texts.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():
                z.write(path, path.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
    print(json.dumps(dict(languages=13, changelogLanguages=2, postLanguages=2, bbcodeFiles=len(checked), archive=str(archive)), ensure_ascii=False))

if __name__ == '__main__':
    main()

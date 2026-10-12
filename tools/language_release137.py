"""Native inventory localization shared by all five voice packages."""
import json
import shutil
import sqlite3
import subprocess
import sys
import re

SHOP = {
 'en_us': 'Beta Gwent 0.9.24 card: {title}. Adds to your collection. Copy limit: {cap}.',
 'de_de': 'Beta Gwent 0.9.24-Karte: {title}. Fügt die Karte deiner Sammlung hinzu. Exemplarlimit: {cap}.',
 'fr_fr': 'Carte Beta Gwent 0.9.24 : {title}. Ajoute la carte à votre collection. Limite d’exemplaires : {cap}.',
 'it_it': 'Carta di Beta Gwent 0.9.24: {title}. Aggiunge la carta alla collezione. Limite di copie: {cap}.',
 'pl_pl': 'Karta Beta Gwent 0.9.24: {title}. Dodaje kartę do kolekcji. Limit kopii: {cap}.',
 'es_es': 'Carta de Beta Gwent 0.9.24: {title}. Añade la carta a tu colección. Límite de copias: {cap}.',
 'es_mx': 'Carta de Beta Gwent 0.9.24: {title}. Agrega la carta a tu colección. Límite de copias: {cap}.',
 'pt_br': 'Carta de Beta Gwent 0.9.24: {title}. Adiciona a carta à sua coleção. Limite de cópias: {cap}.',
 'jp_jp': 'Beta Gwent 0.9.24のカード：{title}。購入するとコレクションに追加されます。所持上限：{cap}枚。',
 'kr_kr': 'Beta Gwent 0.9.24 카드: {title}. 구매하면 컬렉션에 추가됩니다. 보유 한도: {cap}장.',
 'zh_cn': 'Beta Gwent 0.9.24 卡牌：{title}。购买后加入收藏。持有上限：{cap}张。',
 'zh_tw': 'Beta Gwent 0.9.24 卡牌：{title}。購買後加入收藏。持有上限：{cap}張。',
}

LOCALES = {'ru': 'ru_ru', 'en': 'en_us', 'de': 'de_de', 'it': 'it_it',
           'fr': 'fr_fr', 'pl': 'pl_pl', 'es': 'es_es', 'esmx': 'es_mx',
           'br': 'pt_br', 'jp': 'jp_jp', 'kr': 'kr_kr', 'cn': 'zh_cn', 'zh': 'zh_tw'}


def translate(raw, locale, lookup):
    if locale == 'ru_ru': return raw
    if raw in lookup: return lookup[raw]
    item = re.fullmatch(r'Карта Beta Gwent 0\.9\.24: (.+)\. Покупка пополняет коллекцию\. Лимит: (\d+) копи[яий]\. ', raw+' ')
    if item:
        title, cap = item.groups()
        if title not in lookup: raise RuntimeError('Missing native card title '+locale+': '+title)
        return SHOP[locale].format(title=lookup[title], cap=cap)
    raise RuntimeError('Missing native item translation '+locale+': '+raw)


def cook_strings(root, base, project, content, job, voice):
    from localization89 import strings
    english = strings()
    prepared = root/'BetaGwent/build/languages137/ui'
    dictionaries = {locale: json.loads((prepared/f'{locale}.json').read_text('utf8'))
                    for locale in LOCALES.values() if locale not in ('ru_ru', 'en_us')}
    dictionaries.update(ru_ru={}, en_us=english)
    # Keep the frozen project unchanged; Wcc reads this isolated string project.
    fallback = base/'string-fallback/BetaGwent0924'
    fallback.mkdir(parents=True, exist_ok=True)
    (fallback/'workspace').mkdir(exist_ok=True)
    for path in project.glob('*.w3edit'): shutil.copyfile(path, fallback/path.name)
    shutil.copyfile(project/'LocalEditorStringDataBaseW3_UTF8_mod.db', fallback/'LocalEditorStringDataBaseW3_UTF8_mod.db')
    with sqlite3.connect(fallback/'LocalEditorStringDataBaseW3_UTF8_mod.db') as db:
        db.execute("insert or ignore into LANGUAGES(ID,LANG,FALLBACK) values(18,'UA',2)")
        russian = db.execute('select STRING_ID,TEXT from STRINGS where LANG=9').fetchall()
        versions = dict(db.execute('select STRING_ID,max(VERSION) from STRINGS group by STRING_ID'))
        languages = db.execute("select ID,lower(LANG) from LANGUAGES where LANG!='DEBUG' order by ID").fetchall()
        assert len(russian) == 396
        for ident, code in languages:
            locale = LOCALES.get(code, 'en_us')
            lookup = dictionaries[locale]
            rows = []
            for string_id, raw in russian:
                translated = translate(raw, locale, lookup)
                versions[string_id] += 1
                rows.append((string_id, ident, versions[string_id], translated))
            db.execute('delete from STRINGS where LANG=?', (ident,))
            db.executemany('insert into STRINGS(STRING_ID,LANG,VERSION,TEXT) values(?,?,?,?)', rows)
    codes = ','.join(code for _, code in languages)
    job('strings-all', ['cookstrings', str(content)+'\\', str(root/'depot')+'\\',
                        'LATEST_STRINGS_WITH_INFO_NEW', '-languages='+codes, '-platforms=pc'],
        expect=[content/(code+'.w3strings') for _, code in languages], workspace=fallback)
    subprocess.run([sys.executable, str(root/'tools/recon/verify_release_strings.py'), '--base', str(base),
                    '--stage', '137', '--package-language', voice], check=True, cwd=root)

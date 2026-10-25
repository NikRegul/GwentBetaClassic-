"""Update the reviewed 13-language showcase without changing its visual design."""
from pathlib import Path
import hashlib, importlib.util, json, re, shutil, zipfile

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/releases/0.9.0/nexus'
OUT=ROOT/'docs/releases/0.9.2/nexus'
DATA=ROOT/'data/beta924/design/nexus092_updates.json'
spec=importlib.util.spec_from_file_location('showcase090',ROOT/'tools/features082/refresh_showcase090.py')
show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)

def sizes(text):
    # Decimal archive sizes; the original detailed installation text retains
    # the engine resource limit and unchanged DLC explanation.
    return re.sub(r'\b448\b','454',re.sub(r'\b623\b','947',text))

def main():
    updates=json.loads(DATA.read_text('utf8'));design=json.loads(show.DATA.read_text('utf8'))
    assert set(updates)==set(show.ORDER);OUT.mkdir(parents=True,exist_ok=True)
    shutil.copytree(BASE/'assets',OUT/'assets',dirs_exist_ok=True)
    page=(BASE/'preview.html').read_text('utf8');bodies={};rendered={}
    for lang in show.ORDER:
        u=updates[lang];assert set(u)=={'title','ai','knowledge','cards','music','install'}
        section='## '+u['title']+'\n\n'+'\n\n'.join(u[k] for k in ['ai','knowledge','cards','music','install'])+'\n\n'
        markdown=sizes((BASE/lang/'description.md').read_text('utf8')).replace('0.9.0','0.9.2',1)
        marker='## '+design[lang]['whyTitle'];assert markdown.count(marker)==1
        markdown=markdown.replace(marker,section+marker,1)
        bbcode=sizes((BASE/lang/'description.bbcode.txt').read_text('utf8')).replace('0.9.0','0.9.2',1)
        marker='[size=4][color=#e0b354][b]'+design[lang]['whyTitle'];assert bbcode.count(marker)==1
        bbcode=bbcode.replace(marker,show.bb.bbcode(section)+'\n'+marker,1)
        show.validate_bbcode(bbcode)
        folder=OUT/lang;show.write(folder/'description.md',markdown);show.write(folder/'description.bbcode.txt',bbcode)
        assert all(token in markdown for token in ['479','21','46','13','BG1','bg_clean_confirm','DELETE_BETA_GWENT','modBetaGwentMenuMusic'])
        assert markdown.count('<details>')==3 and '\ufffd' not in markdown
        bodies[lang]=markdown;rendered[lang]=bbcode
        # Keep the existing responsive hero, feature/faction cards and accordions.
        start=page.index('<article data-lang="'+lang+'"');end=page.find('<article data-lang="',start+1)
        if end<0:end=page.index('<footer>',start)
        article=sizes(page[start:end]).replace('0.9.0','0.9.2',1)
        split=article.index('</section>')+len('</section>')
        article=article[:split]+'<section class="section release-update">'+show.markdown_html(section)+'</section>'+article[split:]
        page=page[:start]+article+page[end:]
    page=page.replace('GWENT BETA CLASSIC · 0.9.0','GWENT BETA CLASSIC · 0.9.2')
    show.write(OUT/'preview.html',page)
    original=(BASE/'NEXUS_DESCRIPTION_0.9.0.bbcode.txt').read_text('utf8')
    intro=original[:original.index('[/center]')+len('[/center]')].replace('0.9.0','0.9.2')+'\n'
    combined=intro
    for lang in show.ORDER[1:]:combined+='\n[b]'+show.NAMES[lang]+'[/b]\n[spoiler]\n'+rendered[lang]+'\n[/spoiler]\n'
    combined+='\n[line]\n[b]English[/b]\n\n'+rendered['en'];show.validate_bbcode(combined)
    show.write(OUT/'NEXUS_DESCRIPTION_0.9.2.bbcode.txt',combined)
    all_md='# Gwent Beta Classic 0.9.2\n\n'+'\n\n'.join('<details'+(' open' if lang=='en' else '')+'><summary>'+show.NAMES[lang]+'</summary>\n\n'+bodies[lang]+'\n</details>' for lang in show.ORDER)
    show.write(OUT/'DESCRIPTION_0.9.2.md',all_md)
    show.write(ROOT/'docs/releases/0.9.2_DESCRIPTION_ALL_LANGUAGES.md',all_md)
    for lang in ['en','ru']:
        show.write(ROOT/f'docs/releases/0.9.2_DESCRIPTION_{lang.upper()}.md',bodies[lang])
        for kind in ['changelog','post']:
            text=(ROOT/f'docs/releases/0.9.2_{kind.upper()}_{lang.upper()}.md').read_text('utf8')
            show.write(OUT/lang/(kind+'.md'),text);bbcode=show.bb.bbcode(text);show.validate_bbcode(bbcode)
            show.write(OUT/lang/(kind+'.bbcode.txt'),bbcode)
    show.write(OUT/'README_RU.md','''# Материалы Nexus 0.9.2

[Предпросмотр](preview.html) сохраняет оформление красивой страницы 0.9.0: баннер, золотые заголовки, блоки возможностей и фракций, раскрывающиеся инструкции. Есть переключатель всех 13 языков и мобильная раскладка. HTML автономен, баннер встроен.

[Полное описание для Nexus](NEXUS_DESCRIPTION_0.9.2.bbcode.txt): готовый BBCode, английский раскрыт, остальные 12 языков — в отдельных блоках. Для каждого языка также есть description.md и description.bbcode.txt в его папке. Баннер для загрузки в Nexus находится в assets/GwentBetaClassic-header.jpg; вымышленных ссылок на изображение в BBCode нет.

Changelog и пост подготовлены на русском и английском в ru и en. Описание подготовлено на EN, RU, DE, FR, IT, PL, ES, ES-MX, PT-BR, JA, KO, ZH-CN и ZH-TW. Новые переводы желательно вычитать носителями языка.

Повторная генерация: python -X utf8 tools/features092/prepare_nexus092.py из корня проекта. Исходные переводы обновления: data/beta924/design/nexus092_updates.json. Локальные тексты подготовлены для публикации; публикация на Nexus не выполнялась.
''')
    report=dict(version='0.9.2',descriptionLanguages=show.ORDER,descriptionLanguageCount=13,bbcodeBalanced=True,
                originalDesignPreserved=True,published=False,previewDefault='ru',newTranslationNativeReview=False,
                files={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='validation.json'})
    show.write(OUT/'validation.json',json.dumps(report,ensure_ascii=False,indent=2))
    archive=ROOT/'BetaGwent/release/GwentBetaClassic-0.9.2-Nexus-Showcase-13-Languages.zip'
    archive.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(OUT.rglob('*')):
            if p.is_file():z.write(p,'Nexus-Showcase/'+p.relative_to(OUT).as_posix())
        z.write(DATA,'Sources/nexus092_updates.json');z.write(Path(__file__),'Sources/prepare_nexus092.py')
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print(json.dumps(dict(languages=13,bbcodeBalanced=True,preview=str(OUT/'preview.html'),archive=str(archive)),ensure_ascii=False))

if __name__=='__main__':main()

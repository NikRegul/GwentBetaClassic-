"""Restore the reviewed full showcase for0.9.3 and a <=5000-character EN/RU post.

Publication copy only: never rebuild, install or change the game archives.
"""
from pathlib import Path
import argparse, base64, copy, hashlib, html, importlib.util, json, re, shutil

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'docs/releases/0.9.0/nexus'
OUT=ROOT/'docs/releases/0.9.3/nexus'
spec=importlib.util.spec_from_file_location('full_showcase090',ROOT/'tools/features082/refresh_showcase090.py')
show=importlib.util.module_from_spec(spec);spec.loader.exec_module(show)
from notes093_public import COPY, HEADINGS, spaced

PATCH={
'ru': ['92 уникальных состава','четыре уровня сложности ИИ',
'За знакомым столом теперь ещё больше соперников:76 обычных составов и33 тематических варианта квестовых персонажей —92 уникальные колоды. Среди них30 подлинных колод беты с исходными названиями. Выбирай одну из четырёх сложностей и пробуй новые сочетания — с мышью и клавиатурой или контроллером.',
'Для ошибки ИИ укажите сложность, раунд, счёт, участвующие карты и ожидаемый ход. Для пропавшей колоды приложите сохранение до проблемы и опишите, когда она исчезла: после сохранения колоды, загрузки игры или обновления мода.'],
'en': ['92 unique compositions','four AI difficulty levels',
'There are more rivals at familiar tables:76 ordinary lineups and33 thematic quest-character presets —92 unique compositions. They include30 authentic beta decks with their original names. Choose one of four difficulties and try a new combination with mouse and keyboard or a controller.',
'For an AI issue, include difficulty, round, score, involved cards and the expected move. For a missing deck, attach a save from before the problem and say whether it disappeared after saving the deck, loading the game or updating the mod.'],
'de': ['92 einzigartige Zusammenstellungen','vier KI-Schwierigkeitsgrade',
'Mehr Gegner an vertrauten Tischen:76 normale Decklisten und33 thematische Questgegner-Vorgaben ergeben92 einzigartige Zusammenstellungen. Darunter sind30 originale Beta-Decks mit ihren ursprünglichen Namen. Wähle einen von vier Schwierigkeitsgraden und spiele mit Maus und Tastatur oder Controller.',
'Bei KI-Problemen bitte Schwierigkeit, Runde, Punktestand, Karten und erwarteten Zug nennen. Bei einem verschwundenen Deck einen Spielstand von davor beilegen und angeben, ob es nach dem Speichern des Decks, Laden des Spiels oder Mod-Update verschwand.'],
'fr': ['92 compositions uniques','quatre niveaux de difficulté de l’IA',
'Davantage de rivaux aux tables familières:76 compositions ordinaires et33 variantes thématiques de personnages de quête, soit92 compositions uniques. Elles comprennent30 jeux authentiques de la bêta avec leurs noms d’origine. Choisissez parmi quatre difficultés, à la souris et au clavier ou à la manette.',
'Pour un problème d’IA, précisez difficulté, manche, score, cartes et coup attendu. Pour un jeu de cartes disparu, joignez une sauvegarde antérieure et indiquez si cela a suivi l’enregistrement du jeu, le chargement de la partie ou une mise à jour du mod.'],
'it': ['92 composizioni uniche','quattro livelli di difficoltà dell’IA',
'Più rivali ai tavoli familiari:76 composizioni normali e33 varianti tematiche dei personaggi delle missioni,92 composizioni uniche. Comprendono30 mazzi autentici della beta con i nomi originali. Scegli fra quattro difficoltà e gioca con mouse e tastiera o controller.',
'Per problemi dell’IA indica difficoltà, round, punteggio, carte e mossa prevista. Per un mazzo scomparso allega un salvataggio precedente e specifica se è successo dopo aver salvato il mazzo, caricato la partita o aggiornato il mod.'],
'pl': ['92 unikalne składy','cztery poziomy trudności SI',
'Więcej rywali przy znajomych stołach:76 zwykłych składów i33 tematyczne warianty postaci z zadań, czyli92 unikalne składy. Wśród nich30 autentycznych talii bety z oryginalnymi nazwami. Wybierz jeden z czterech poziomów trudności i graj myszą i klawiaturą lub kontrolerem.',
'Przy problemie SI podaj trudność, rundę, wynik, karty i oczekiwany ruch. Jeśli zniknęła talia, dołącz wcześniejszy zapis i napisz, czy stało się to po zapisaniu talii, wczytaniu gry czy aktualizacji moda.'],
'es': ['92 composiciones únicas','cuatro niveles de dificultad de la IA',
'Más rivales en mesas conocidas:76 composiciones normales y33 variantes temáticas de personajes de misiones,92 composiciones únicas. Incluyen30 mazos auténticos de la beta con sus nombres originales. Elige entre cuatro dificultades y juega con ratón y teclado o mando.',
'Para errores de IA indica dificultad, ronda, marcador, cartas y jugada esperada. Si desaparece un mazo, adjunta una partida guardada anterior e indica si ocurrió tras guardar el mazo, cargar la partida o actualizar el mod.'],
'es-mx': ['92 composiciones únicas','cuatro niveles de dificultad de la IA',
'Más rivales en mesas conocidas:76 composiciones normales y33 variantes temáticas de personajes de misiones,92 composiciones únicas. Incluyen30 mazos auténticos de la beta con sus nombres originales. Elige entre cuatro dificultades y juega con ratón y teclado o control.',
'Para errores de IA indica dificultad, ronda, marcador, cartas y jugada esperada. Si desaparece un mazo, adjunta una partida guardada anterior e indica si ocurrió tras guardar el mazo, cargar la partida o actualizar el mod.'],
'pt-br': ['92 composições únicas','quatro níveis de dificuldade da IA',
'Mais rivais nas mesas conhecidas:76 composições comuns e33 variantes temáticas de personagens de missões,92 composições únicas. Incluem30 baralhos autênticos da beta com os nomes originais. Escolha entre quatro dificuldades e jogue com mouse e teclado ou controle.',
'Para erros de IA, informe dificuldade, rodada, placar, cartas e jogada esperada. Se um baralho sumir, anexe um salvamento anterior e diga se ocorreu após salvar o baralho, carregar o jogo ou atualizar o mod.'],
'ja': ['92種類の独自構成','4段階のAI難易度',
'おなじみの卓に、さらに多彩な対戦相手が登場。通常76構成とクエスト人物用33設定、重複を除くと92構成です。元の名前を保持したベータ版のデッキ30種も含まれます。4段階の難易度を選び、マウスとキーボード、またはコントローラーで新たな組み合わせを試しましょう。',
'AIの問題では難易度、ラウンド、得点、関係するカード、期待した行動をお知らせください。デッキ消失では発生前のセーブを添付し、デッキ保存、ゲームのロード、MOD更新のどの後に起きたか記載してください。'],
'ko': ['92개의 고유 구성','4단계 AI 난이도',
'익숙한 탁자에서 더 다양한 상대를 만나세요. 일반 구성76개와 퀘스트 인물용 설정33개, 중복을 제외하면92개 구성입니다. 원래 이름을 유지한 베타 원본 덱30개도 포함됩니다. 4단계 난이도 중 하나를 골라 마우스와 키보드 또는 컨트롤러로 새 조합을 시험해 보세요.',
'AI 문제는 난이도, 라운드, 점수, 관련 카드와 예상한 행동을 알려 주세요. 덱이 사라졌다면 이전 저장 파일을 첨부하고 덱 저장, 게임 불러오기, 모드 업데이트 중 어떤 작업 후 발생했는지 적어 주세요.'],
'zh-cn': ['92种独立牌组构成','4档AI难度',
'熟悉的牌桌迎来更多对手：76种常规构成和33套任务角色主题预设，去重后共92种构成。其中包含30套保留原名的公测原始牌组。选择4档难度之一，用键鼠或手柄尝试新的组合。',
'AI问题请说明难度、回合、分数、相关卡牌及预期行动。牌组消失时请附上出问题前的存档，并说明发生在保存牌组、读取游戏还是更新模组之后。'],
'zh-tw': ['92種獨立牌組構成','4種AI難度',
'熟悉的牌桌迎來更多對手：76種一般構成和33套任務角色主題預設，去重後共92種構成。其中包含30套保留原名的公測原始牌組。選擇4種難度之一，用鍵鼠或控制器嘗試新的組合。',
'AI問題請說明難度、回合、分數、相關卡牌及預期行動。牌組消失時請附上出問題前的存檔，並說明發生在儲存牌組、讀取遊戲還是更新模組之後。']}
BASIC_LABEL=dict(zip(show.ORDER,['Ordinary difficulty levels','Обычные уровни сложности','Normale Schwierigkeitsgrade','Difficultés ordinaires','Difficoltà ordinarie','Zwykłe poziomy trudności','Dificultades normales','Dificultades normales','Dificuldades comuns','通常の難易度','일반 난이도','常规难度','一般難度']))

def code(lang):return lang.upper().replace('-','_')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):show.write(p,s)
def prose(lang,s):
    s=spaced(s)
    if lang not in ['ja','ko','zh-cn','zh-tw']:
        s=re.sub(r'([,:;])(?=[A-Za-zА-Яа-яЁё0-9])',r'\1 ',s)
        s=re.sub(r'(?<=[A-Za-zА-Яа-яЁё])\.(?=\d)', '. ',s)
    return s
def sized(s):
    for old,new in [('623','947'),('448','454'),('105','106')]:s=re.sub(r'(?<!\d)'+old+r'(?!\d)',new,s)
    return s

def collect_publication(source,nexus):
    """Update external publication files; leave archives and their proofs intact."""
    report=json.loads((source/'validation.json').read_text('utf8'))
    assert report['languages']==13 and report['post']['charactersIncludingMarkupAndCrLf']<=5000
    for name,digest in report['files'].items():assert sha(source/name)==digest,name
    full=nexus/'full'
    if source.resolve()!=full.resolve():shutil.copytree(source,full,dirs_exist_ok=True)
    for name in ['NEXUS_DESCRIPTION_0.9.3.bbcode.txt','NEXUS_POST_0.9.3_EN_RU.bbcode.txt']:
        shutil.copy2(source/name,nexus/name)
    # The formerly linked combined file now points to the full reviewed style.
    shutil.copy2(source/'NEXUS_DESCRIPTION_0.9.3.bbcode.txt',nexus/'0.9.3_DESCRIPTION_ALL_LANGUAGES_NEXUS.txt')
    if (nexus/'BBCode').is_dir():shutil.copy2(source/'NEXUS_DESCRIPTION_0.9.3.bbcode.txt',nexus/'BBCode/0.9.3_DESCRIPTION_ALL_LANGUAGES_NEXUS.txt')
    rows=['# Nexus0.9.3 — материалы для публикации','','[Полное описание: все13языков](NEXUS_DESCRIPTION_0.9.3.bbcode.txt). Прежнее оформление и полные инструкции, включая сообщение об ошибках.','',f'[Общий пост EN/RU](NEXUS_POST_0.9.3_EN_RU.bbcode.txt): **{report["post"]["charactersIncludingMarkupAndCrLf"]} /5000символов** вместе с разметкой и CRLF.','', '[Визуальный предпросмотр](full/preview.html) · [Проверка](full/validation.json)','','| Язык | Полное описание |','|---|---|']
    rows += ['| '+show.NAMES[lang]+' | [BBCode](full/'+lang+'/description.bbcode.txt) · [Markdown](full/'+lang+'/description.md) |' for lang in show.ORDER]
    rows += ['','Пост ограничен5000символов суммарно для двух языков; полное описание — отдельный большой файл. Игровые архивы не пересобирались и не изменялись. Ничего не опубликовано.','']
    write(nexus/'README.md','\n'.join(rows));return report

def reference_check(path):
    if path is None:return None
    raw=path.read_text('utf-8-sig');labels={v:k for k,v in show.NAMES.items()}
    starts=[(m.start(),m.end(),labels[m[0]]) for m in re.finditer(r'^.*$',raw,re.M) if m[0] in labels]
    assert len(starts)==13,'Expected all thirteen supplied language sections'
    normalize=lambda s:re.sub(r'\s+',' ',s).strip()
    for i,(_,end,lang) in enumerate(starts):
        actual=raw[end:starts[i+1][0] if i+1<len(starts) else len(raw)]
        source=re.sub(r'\[[^\]]+\]','',(BASE/lang/'description.bbcode.txt').read_text('utf8'))
        assert normalize(actual)==normalize(source),'Supplied body differs from reviewed source: '+lang
    return dict(sha256=sha(path),languageBodiesMatched=13,match='All words/sections match after whitespace and BBCode removal')

def build(out,reference=None):
    out.mkdir(parents=True,exist_ok=True);proof=reference_check(reference)
    design=json.loads(show.DATA.read_text('utf8'));music=json.loads((ROOT/'data/beta924/design/nexus092_updates.json').read_text('utf8'))
    bodies={};rendered={};previews={};manual_proof=[]
    for lang in show.ORDER:
        d=copy.deepcopy(design[lang]);stat,difficulties,npc,bug=[prose(lang,s) for s in PATCH[lang]];c=code(lang)
        old_stat=d['stats'][2];d['stats'][2]=stat;d['tagline']=d['tagline'].replace('0.9.0','0.9.3');d['features'][3][1]=npc
        source=(BASE/lang/'manual.md').read_text('utf-8-sig');split=re.split(r'(?m)^## ',source);assert len(split)==18
        original=['## '+s.strip()+'\n' for s in split[1:]];sections=original.copy()
        # Preserve all sixteen operational sections. Only update documented
        # version/count/size claims and append current mode/bug-report guidance.
        sections=[sized(s) for s in sections]
        lines=sections[4].splitlines();matched=[i for i,s in enumerate(lines) if '46' in s];assert len(matched)==1,(lang,matched)
        lines[matched[0]]='- '+stat+' · '+difficulties;sections[4]='\n'.join(lines)+'\n'
        heading,body=sections[2].split('\n',1);sections[2]=heading+'\n\n'+prose(lang,COPY[c][2])+'\n\n### '+BASIC_LABEL[lang]+'\n\n'+body.lstrip()
        sections[13]=sections[13].replace('0.9.0','0.9.3')
        sections[15]+='\n'+bug+'\n'
        update='## 0.9.3 — '+prose(lang,HEADINGS[c][1])+'\n\n'+'\n\n'.join(prose(lang,s) for s in [COPY[c][2],npc,COPY[c][4],COPY[c][5],COPY[c][6],COPY[c][7],COPY[c][8],music[lang]['music'],music[lang]['install'].replace('0.9.2','0.9.3')])+'\n\n'
        showcase='# Gwent Beta Classic\n\n> '+d['tagline']+'\n\n## '+d['headline']+'\n\n'+d['intro']+'\n\n'+d['moment']+'\n\n'
        showcase+='\n'.join('- **'+s+'**' for s in d['stats'])+'\n\n'+update+'## '+d['whyTitle']+'\n\n'
        showcase+='\n\n'.join('### '+title+'\n\n'+body for title,body in d['features'])+'\n\n## '+d['factionsTitle']+'\n\n'
        showcase+='\n\n'.join('### '+title+'\n\n'+body for title,body in d['factions'])+'\n\n## '+d['ctaTitle']+'\n\n'+d['cta']+'\n\n'
        essentials='## '+d['guideTitle']+'\n\n'+'\n\n'.join(sections[i] for i in [7,10,0,8])
        details_md='';details_bb='';details_html=''
        for label,indices in [(d['detailsTitle'],[4,1,2,5,6]),(d['compatTitle'],[9,11,12,13]),(d['supportTitle'],[14,15,16])]:
            text='\n\n'.join(sections[i] for i in indices)
            details_md+='\n\n<details>\n<summary>'+label+'</summary>\n\n'+text+'\n\n</details>'
            details_bb+='\n\n[color=#e0b354][b]'+label+'[/b][/color]\n[spoiler]\n'+show.bb.bbcode(text)+'[/spoiler]\n'
            details_html+='<details><summary>'+html.escape(label)+'</summary><div class="detail-body">'+show.markdown_html(text)+'</div></details>'
        bodies[lang]=showcase+essentials+details_md+'\n'
        hero='[center][size=6][color=#e0b354][b]'+d['headline']+'[/b][/color][/size]\n\n[size=2]'+d['tagline']+'[/size]\n\n'+'  ·  '.join('[b]'+s+'[/b]' for s in d['stats'])+'[/center]\n\n'
        middle=showcase.split('## '+d['headline']+'\n\n',1)[1].replace('\n'.join('- **'+s+'**' for s in d['stats'])+'\n\n','',1)
        rendered[lang]=hero+show.bb.bbcode(middle+essentials)+details_bb;show.validate_bbcode(rendered[lang])
        for i,section in enumerate(sections):
            if i!=3:assert section.strip() in bodies[lang],(lang,i)
        assert bodies[lang].count('<details>')==3
        for token in ['479','21','92','13','BG1','Optional-CopyButton','bg_clean_confirm','DELETE_BETA_GWENT','-debugscripts','scriptslog.txt','CrashDumps','203','197']:assert token in bodies[lang],(lang,token)
        assert old_stat not in bodies[lang] and '\ufffd' not in bodies[lang]
        write(out/lang/'description.md',bodies[lang]);write(out/lang/'description.bbcode.txt',rendered[lang])
        # Rebuild the accepted layout from its source CSS, not a disposable HTML
        # cache. The same banner, hero, feature/faction cards and accordions stay.
        stats=''.join('<div class="stat"><div>'+re.sub(r'^(\d+)',r'<b>\1</b>',html.escape(s))+'</div></div>' for s in d['stats'])
        features=''.join('<article class="feature" data-index="0'+str(i+1)+'"><h3>'+html.escape(t)+'</h3><p>'+show.inline(b)+'</p></article>' for i,(t,b) in enumerate(d['features']))
        factions=''.join('<article class="faction"><h3>'+html.escape(t)+'</h3><p>'+show.inline(b)+'</p></article>' for t,b in d['factions'])
        previews[lang]='<section class="hero"><img class="banner" data-banner alt="Gwent Beta Classic — Geralt and Ciri"><p class="eyebrow">'+html.escape(d['tagline'])+'</p><h1>'+html.escape(d['headline'])+'</h1><p class="lead">'+show.inline(d['intro'])+'</p><p class="moment">'+show.inline(d['moment'])+'</p><div class="stats">'+stats+'</div></section>'
        previews[lang]+='<section class="section guide">'+show.markdown_html(update)+'</section><section class="section"><h2>'+html.escape(d['whyTitle'])+'</h2><div class="features">'+features+'</div></section><section class="section"><h2>'+html.escape(d['factionsTitle'])+'</h2><div class="factions">'+factions+'</div></section>'
        previews[lang]+='<section class="cta"><h2>'+html.escape(d['ctaTitle'])+'</h2><p>'+show.inline(d['cta'])+'</p><a class="button" href="#guide-'+lang+'">'+html.escape(d['guideTitle'])+' ↓</a></section><section class="section guide" id="guide-'+lang+'"><h2>'+html.escape(d['guideTitle'])+'</h2>'+show.markdown_html(essentials.split('\n\n',1)[1])+details_html+'</section>'
        manual_proof.append(dict(language=lang,sourceSha256=sha(BASE/lang/'manual.md'),preservedSections=16))
    intro=(BASE/'NEXUS_DESCRIPTION_0.9.0.bbcode.txt').read_text('utf8').split('[/center]',1)[0].replace('0.9.0','0.9.3')+'[/center]\n'
    combined=intro+''.join('\n[b]'+show.NAMES[lang]+'[/b]\n[spoiler]\n'+rendered[lang]+'\n[/spoiler]\n' for lang in show.ORDER[1:])+'\n[line]\n[b]English[/b]\n\n'+rendered['en']
    show.validate_bbcode(combined);assert combined.count('[spoiler]')==51
    write(out/'NEXUS_DESCRIPTION_0.9.3.bbcode.txt',combined)
    write(out/'DESCRIPTION_0.9.3.md','# Gwent Beta Classic0.9.3\n\n'+'\n\n'.join('<details'+(' open' if lang=='en' else '')+'><summary>'+show.NAMES[lang]+'</summary>\n\n'+bodies[lang]+'\n</details>' for lang in show.ORDER))
    options=''.join('<option value="'+lang+'"'+(' selected' if lang=='ru' else '')+'>'+show.NAMES[lang]+'</option>' for lang in show.ORDER)
    pages=''.join('<article data-lang="'+lang+'" lang="'+show.HTML_LANG.get(lang,lang)+'"'+(' hidden' if lang!='ru' else '')+'>'+previews[lang]+'</article>' for lang in show.ORDER)
    banner_path=BASE/'assets/GwentBetaClassic-header.jpg'
    banner='data:image/jpeg;base64,'+base64.b64encode(banner_path.read_bytes()).decode('ascii') if banner_path.is_file() else ''
    script='const BANNER='+json.dumps(banner)+''';document.querySelectorAll('[data-banner]').forEach(e=>{if(BANNER)e.src=BANNER;else e.remove();});const select=document.querySelector('select'),articles=[...document.querySelectorAll('[data-lang]')];function choose(code){if(!articles.some(e=>e.dataset.lang===code))code='ru';articles.forEach(e=>e.hidden=e.dataset.lang!==code);select.value=code;document.documentElement.lang=articles.find(e=>!e.hidden).lang;document.title='Gwent Beta Classic0.9.3 — '+select.selectedOptions[0].textContent;}choose(location.hash.slice(1));select.addEventListener('change',()=>{choose(select.value);history.replaceState(null,'','#'+select.value);window.scrollTo(0,0);});'''
    css=show.CSS+'.guide{overflow-wrap:anywhere}@media(max-width:560px){.brand{max-width:100px;font-size:11px}select{max-width:160px}.button{max-width:100%;overflow-wrap:anywhere}}'
    page='<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Gwent Beta Classic0.9.3</title><style>'+css+'</style></head><body><header><div class="nav"><span class="brand">GWENT BETA CLASSIC</span><label>Language / Язык <select aria-label="Language / Язык">'+options+'</select></label></div></header><main>'+pages+'<footer><span>GWENT BETA CLASSIC ·0.9.3</span><a href="https://github.com/NikRegul/GwentBetaClassic-">GitHub ↗</a></footer></main><script>'+script+'</script></body></html>'
    write(out/'preview.html',page)
    if (BASE/'assets').is_dir():shutil.copytree(BASE/'assets',out/'assets',dirs_exist_ok=True)
    return dict(version='0.9.3',languages=13,languageSpoilers=12,detailSpoilersPerLanguage=3,bbcodeBalanced=True,providedReference=proof,manualSections=manual_proof,originalDesignPreserved=True,originalBannerIncluded=bool(banner),published=False)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=OUT);p.add_argument('--reference',type=Path);p.add_argument('--collect-to',type=Path);a=p.parse_args()
    report=build(a.out,a.reference)
    from nexus_post093 import prepare_post
    report['post']=prepare_post(a.out)
    write(a.out/'README_RU.md','# Nexus0.9.3 — полное описание в прежнем оформлении\n\nОсновной файл: [NEXUS_DESCRIPTION_0.9.3.bbcode.txt](NEXUS_DESCRIPTION_0.9.3.bbcode.txt). Все13языков, полные инструкции, совместимость, удаление и сообщение об ошибках.\n\n[Предпросмотр](preview.html) сохраняет прежний баннер, оформление, переключатель языков и раскрывающиеся разделы. Вид на Nexus может отличаться.\n\n[Общий пост EN/RU](NEXUS_POST_0.9.3_EN_RU.bbcode.txt) — до5000символов суммарно с разметкой и переводами строк. Полное описание этим лимитом не ограничено.\n\nПубликация и пересборка игровых архивов не выполнялись.\n')
    report['files']={p.relative_to(a.out).as_posix():sha(p) for p in a.out.rglob('*') if p.is_file() and p.name!='validation.json'}
    write(a.out/'validation.json',json.dumps(report,ensure_ascii=False,indent=2))
    if a.collect_to:collect_publication(a.out,a.collect_to)
    print(json.dumps({k:v for k,v in report.items() if k not in ['files','manualSections']},ensure_ascii=False))

if __name__=='__main__':main()

from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
header='''## Текущий шаг —89: два языковых пакета и публичные исходники

Пользователь установил предыдущий мод и принял пробную партию. Исправлен
фокус окна выбора Лютика: отдельная область выбора, блокирование рядов
за окном, кнопки и карты внутри своей области. Обычные NPC выбирают из55
случайных составов при новой партии; квестовые33 назначения сохранены.
За первые четыре победы над каждым обычным NPC — по бронзе/серебру;
старые награды считаются одной, без сброса коллекции и смены saved schema.

Собраны полные GwentBetaClassic-0.2.0-RU.zip и EN.zip. Переведены собственные
строки интерфейса/WS/предметов; исходные EN имена, правила, теги и glossary
взяты из0.9.24. Банк каждого языка1418 медиа, EN длительности фраз пересчитаны.
RU Wcc89a и EN Wcc89enc успешны, оба содержат60 WS. Три меню/44 связи,
native cook/strings/audio/dependencies/pack/metadata, CRC и SHA256 ZIP проверены.
Установленная игра на F: —5.0.0.1044392; REDkit5.0.1044630.

Публичный проект: https://github.com/NikRegul/GwentBetaClassic-
Лицензия авторского кода —GPL-3.0-only. Оригинальные клиенты/depot/SDK,
нативные шаблоны, изображения, аудио и ключ Wwise в исходники не включаются.
Добавлены инструкции сборки и устройства ИИ на RU/EN, управление, описания
релиза и заполненные поля Nexus. Переносимый автоматический bootstrap пока
не сделан: текущие внешние входы и абсолютные пути перечислены в BUILD.

Короткая новая приёмка: выбор Лютика, четыре награды/отсутствие пятой,
EN текст/фразы, сохранение и полная перезагрузка. Старые suites не повторялись.
Дальше —поле и анимации максимально близко к Beta0.9.24; ИИ доводим
по конкретным отчётам пользователя. Расширенная совместимость/квесты и
экономия размера остаются в ROADMAP.

'''
p=ROOT/'docs/plan.md';s=p.read_text('utf8')
if '## Текущий шаг —89' not in s:
    start=s.index('## Текущий шаг');end=s.find('\n## ',start+4)
    if end<0:end=start
    s=s[:start]+header+'## Предыдущий этап88\n\n'+s[start:end]+s[end:]
else:s=s.replace('EN Wcc89enb','EN Wcc89enc')
p.write_text(s,'utf8')
p=ROOT/'docs/progress.md';s=p.read_text('utf8')
if '2026-10-05 —89:' not in s:s+='\n## 2026-10-05 —89: RU/EN и публичные исходники\n\n'+header.split('\n\n',1)[1]
else:s=s.replace('EN Wcc89enb','EN Wcc89enc')
p.write_text(s,'utf8')
report={}
for lang in ('ru','en'):
    d=json.loads((ROOT/f'docs/evidence/stage89-release-{lang}.json').read_text('utf8'))
    report[lang]={k:d[k] for k in ('archive','archiveBytes','archiveSha256','archiveVerified')}
    comp=ROOT/('BetaGwent/build/board-compile89a' if lang=='ru' else 'BetaGwent/build/board-compile89enc')
    c=json.loads((comp/'result.json').read_text('utf8'));log=(comp/'stdout.txt').read_text('utf8',errors='replace')
    assert c['exitCode']==0 and len(c['patchSourcesBefore'])==60 and '[Script]: Error [' not in log
    frozen=ROOT/f'BetaGwent/build/release89/{lang}/project/BetaGwent0924/workspace/scripts'
    for entry in c['patchSourcesBefore']:assert hashlib.sha256((frozen/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    report[lang]['frozenCompiledSourcesMatch']=True
(ROOT/'docs/evidence/stage89-completion.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
print(json.dumps(report))

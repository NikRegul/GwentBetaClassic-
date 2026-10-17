from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys,zipfile
ROOT=Path('D:/w3mod');BASE=ROOT/'BetaGwent/build/universal081';WORK=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/classic132'))
from dependencies import copy_dependency_cache
OUTPUT=Path('C:/Users/NikR/Documents/Codex/2026-10-15/new-chat/outputs');OUTPUT.mkdir(exist_ok=True)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def make(platform):
 key='classic' if platform=='1.32' else 'nextgen';package=BASE/('package-'+key);mod='modBetaGwentClassic132' if key=='classic' else 'modBetaGwent0924'
 if package.exists():raise RuntimeError('Package already exists; keep the snapshot immutable')
 content=package/'Mods'/mod/'content';content.mkdir(parents=True)
 baseline=ROOT/'BetaGwent/build/release202/ru/package';docs=package/'BetaGwentDocs';docs.mkdir()
 for p in baseline.iterdir():
  if p.is_file() and p.name!='manifest.json':shutil.copy2(p,docs/p.name)
 if key=='nextgen':
  original=baseline/'Mods/modBetaGwent0924/content'
  for p in original.iterdir():
   if p.is_file() and p.name not in ('blob0.bundle','metadata.store','soundspc.cache','precompiled.rsblob'):shutil.copy2(p,content/p.name)
  shutil.copy2(BASE/'nextgen-compile-v3/compiled/blob.rsblob',content/'precompiled.rsblob')
  compiled=json.loads((BASE/'nextgen-compile-v3/result.json').read_text());assert compiled['exitCode']==0 and compiled['patchSourcesUnchangedDuringCompile']
 else:
  shutil.copytree(BASE/'classic-prepared/Mods/modBetaGwentClassic132/content/scripts',content/'scripts')
  copy_dependency_cache(baseline/'Mods/modBetaGwent0924/content/dep.cache',content/'dep.cache')
  for p in (baseline/'Mods/modBetaGwent0924/content').glob('*.w3strings'):shutil.copy2(p,content/p.name)
  compiled=json.loads((BASE/'classic-runtime/runs/universal-v3/result.json').read_text());assert compiled['compilePassed'] and not compiled['errors']
 for name in ('blob0.bundle','metadata.store'):shutil.copy2(BASE/('resources-'+key)/name,content/name)
 shutil.copy2(BASE/('audio-classic' if key=='classic' else 'audio-nextgen')/'soundspc.cache',content/'soundspc.cache')
 source_manifest=json.loads((baseline/'manifest.json').read_text('utf-8-sig'))
 info=dict(name='Gwent Beta Classic',modName=mod,version='0.8.1-preview',gameVersion=platform,voiceLanguage='multi',voiceLanguages=['ru','en','de','it','pt-br'],textLanguages=source_manifest['textLanguages'])
 (content.parent/'info.json').write_text(json.dumps(info,indent=2),'utf8')
 readme='''# Gwent Beta Classic 0.8.1-preview — все языки

Пробная версия для PLATFORM. Пять озвучек установлены вместе, общие звуки не дублируются. В моде рядом расположены две кнопки: «Текст» и «Озвучка». Нажатия перебирают варианты; после последнего снова включается «Авто». Те же настройки доступны в меню контроллера. Выбор озвучки останавливает текущую реплику; следующая звучит на новом языке.

«Авто» получает текущие языки непосредственно через theGame.GetGameLanguageName. Текст и речь определяются независимо. Если речь игры не RU/EN/DE/IT/PT-BR, используется EN; кнопка показывает переход, например «PL → EN». Текст поддерживает 13 языков. Неподдерживаемый текст также получает EN.

Выбор хранится в фактах сохранения: bg_text_language и bg_voice_language, ноль означает «Авто». Старый ручной язык текста сохраняется. Установщик задаёт только начальные предпочтения; сохранённые настройки имеют приоритет. Для сохранения выбора нужно штатно сохранить игру. Сами файлы сохранений установщик не меняет.

Установщик проверяет формат ресурсов игры, сохраняет предыдущие папки мода и заменяет собственные файлы. Резервная копия находится в BetaGwentBackup внутри папки игры. Подробности — InstallReport.json. Оригинальные параметры Localization не меняются. Начальные параметры BetaGwentTextLanguage и BetaGwentVoiceLanguage хранятся в [Hidden]; установщик регистрирует их в штатном hidden.xml, предварительно сохраняя его резервную копию. Остальные переменные сохраняются. При ошибке установки восстанавливаются и старые папки мода, и конфигурация.

Скрипты обеих платформ и четыре меню прошли нативную компиляцию. 4972 файла Vorbis полностью декодированы для проверки. Classic: Wwise 88, Vorbis quality 6, исходная частота/каналы/число сэмплов сохранены; потоковые media. Next-Gen сохраняет исходные Opus media, тоже потоковые. Установка в реальную игру, игровое воспроизведение всех озвучек и проверка сохранения настроек остаются открытыми: это кандидат для игровой проверки.

Проверить после установки: открыть редактор; две кнопки языка; RU/EN/DE/IT/PT-BR по очереди (лидер, обычная карта, бочка); Auto и неподдерживаемую озвучку игры; сохранить/загрузить ручной выбор и Auto; обновить поверх предыдущей версии и загрузить старое сохранение; начать и завершить партию. Для 1.32 отдельно проверить раскрытие бочки, покупку у корчмаря и НГ+.
'''.replace('PLATFORM',platform)
 (docs/'README_PREVIEW_RU.md').write_text(readme,'utf8')
 native=dict(version='0.8.1-preview',sourceStage=202,gameVersion=platform,nativeCompilationPassed=True,nativeGameplayVerified=False,nativeAudioPlaybackVerified=False,voices=['ru','en','de','it','pt-br'],textLanguages=13,guiLimitMiB=63)
 (docs/'BuildInfo.json').write_text(json.dumps(native,indent=2),'utf8')
 files=[dict(Path=p.relative_to(package).as_posix(),Sha256=sha(p),Bytes=p.stat().st_size) for p in sorted(package.rglob('*')) if p.is_file()]
 manifest=dict(Version='0.8.1-preview',Platform=platform,ModFolder=mod,Files=files)
 archive=BASE/('payload-'+key+'.zip')
 with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  z.writestr('package.json',json.dumps(manifest,ensure_ascii=False))
  for p in files:z.write(package/p['Path'],'files/'+p['Path'])
 name='GwentBetaClassic-0.8.1-preview-'+('1.32' if key=='classic' else '5.0+')+'-AllLanguages-Setup.exe'
 destination=OUTPUT/name;stub=(WORK/'SetupStub.exe').read_bytes()
 with destination.open('xb') as f:
  f.write(stub)
  with archive.open('rb') as src:shutil.copyfileobj(src,f)
  f.write(b'BGSETUP1'+struct.pack('<QQ',len(stub),archive.stat().st_size))
 digest=sha(destination);destination.with_suffix('.exe.sha256').write_text(digest+'  '+name+'\n','ascii')
 report=dict(platform=platform,installer=str(destination),bytes=destination.stat().st_size,sha256=digest,installedBytes=sum(p['Bytes'] for p in files),files=len(files),voices=5,textLanguages=13,nativeGameplayVerified=False)
 print(json.dumps(report,ensure_ascii=False),flush=True);return report
if __name__=='__main__':
 reports=[make(p) for p in ['5.0+','1.32']]
 (BASE/'installers.json').write_text(json.dumps(reports,indent=2),'utf8')

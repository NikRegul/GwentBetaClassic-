"""Finalize the local HD preview, retaining the explicit runtime acceptance gate."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
 evidence=ROOT/'docs/evidence';report=json.loads((evidence/'stage93-completion.json').read_text('utf8'))
 hd=json.loads((evidence/'hd-art93.json').read_text('utf8'))
 assert len(report['menus'])==6 and hd['cards']==562 and len(hd['boards'])==10
 assert len(hd['pages'])==7 and hd['originalsUnchanged'] and not hd['paletteReduction']
 dds_sets=[]
 for item in report['menus']:
  assert sha(Path(item['resource']))==item['sha256']
  suffix='' if item['entry']=='BetaGwentBoard' else '-'+item['entry']
  native=json.loads((evidence/f"stage93-{item['language']}-board-resource-update{suffix}.json").read_text('utf8'))
  assert native['totalTextureChunks']==10 and native['exportedBindings']==20
  assert native['aliasTexturesDeduplicated']==10
  dds_sets.append({b['sha256'] for b in native['bindings']})
  if item['language']=='ru':assert sha(ROOT/'GwentB/myproject1/workspace/betagwent'/Path(item['resource']).name)==item['sha256']
 assert all(s==dds_sets[0] for s in dds_sets),'DDS pixels differ between native menus/languages'
 for name,digest in report['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest
 quality=[]
 dds_dir=ROOT/'BetaGwent/ui/build/native-atlas-DeckBuilder'
 for page in hd['pages']:
  source=Path(page['path']);assert sha(source)==page['sha256']
  exported=list(dds_dir.glob(source.stem+'_png$*.dds'));assert len(exported)==1
  a=np.array(Image.open(source).convert('RGBA'))[::4,::4]
  b=np.array(Image.open(exported[0]).convert('RGBA'))[::4,::4]
  assert a.shape==b.shape
  opaque=a[:,:,3]>245
  rgb=float(np.abs(a[opaque,:3].astype(np.int16)-b[opaque,:3].astype(np.int16)).mean())
  alpha=float(np.abs(a[:,:,3].astype(np.int16)-b[:,:,3].astype(np.int16)).mean())
  assert rgb<12 and alpha<5,'Source/DDS colour or alpha mismatch'
  quality.append(dict(source=str(source),dds=str(exported[0]),size=page['size'],opaqueRGBMeanAbsoluteError=rgb,alphaMeanAbsoluteError=alpha,samplingStride=4))
 for lang in ('ru','en'):
  release=json.loads((evidence/f'stage93-release-{lang}.json').read_text('utf8'))
  assert release['archiveVerified'] and sha(Path(release['archive']))==release['archiveSha256']
  for stage in (89,91,92):
   old=json.loads((evidence/f'stage{stage}-release-{lang}.json').read_text('utf8'))
   assert sha(Path(old['archive']))==old['archiveSha256']
  for job in ('cook','dependencies','pack','metadata'):
   result=json.loads((ROOT/f'BetaGwent/build/release93/{lang}/jobs/{job}/result.json').read_text('utf8'))
   assert result['exitCode']==0 and not result['timedOut']
 report.update(hdManifestSha256=sha(evidence/'hd-art93.json'),hdDDSQuality=quality,
               ddsPixelsIdenticalAcrossMenusAndLanguages=True,publishingPerformed=False,
               previewArchives={l:json.loads((evidence/f'stage93-release-{l}.json').read_text('utf8'))['archive'] for l in ('ru','en')},
               nativeRuntimeVerified=False)
 (evidence/'stage93-completion.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 header='''## Текущий шаг — 93: HD-оформление боя и редактора колоды

Публикация отложена по замечанию пользователя. Собраны локальные RU/EN
`0.2.1-preview.3`; GitHub/Nexus не обновлялись. В REDkit установлены RU-меню,
игра на F: автоматически не менялась. Релиз0.2.0 и preview.1/.2 сохранены.
[Изменения и одна общая проверка](PRESENTATION93_RU.md).
[Порядок сборки и устройство ресурсов](HD_PRESENTATION_PIPELINE93.md).

Десять половин досок2048×708 вместо512×180, общий мировой масштаб,
правильные пропорции и видимые орнаменты. Семь HD-страниц: карты256×360,
доски и оригинальные UI-элементы. Отдельный малый атлас только для частиц.
62 изображения интерфейса,690 HD-привязок с алиасами,562 иллюстрации.
20 native-привязок используют10 уникальных DDS, без дублирования страниц.

В бою: деревянные фракционные панели, центрирование отрядов, общая геометрия
вставки/прицела/контроллера, постоянная карта/описание справа. История,
настройки и дополнительные действия вынесены в «Меню партии». Редактор:
HD-фон, полки, кнопки/рамки, крупная карта256×360. Выбор колод, каталог,
замена карт, бочки и сбросы приведены к общему деревянному стилю.
Механики, сохранения, карты, звуки и ИИ не менялись на этом этапе.

Шесть меню/44 связи, ABC/CRC/ссылки DDS проверены; одинаковые пиксели между
языками и меню подтверждены. Native cook/dependencies/pack/metadata,
ZIP CRC/SHA и совпадение60 WS с компиляцией90 прошли. Проверка DDS
с исходными HD-страницами прошла. Игровая/визуальная приёмка ещё впереди.

Далее: одна общая проверка редактора и боя, затем уточнение размеров,
пиктограмм/цифр и переходов, полный перенос компоновки выбора колод/
каталога, света/теней/погоды. Unity-освещение, перспектива и премиум-анимации
ещё не перенесены. После визуальной приёмки — публикация; ИИ по плану90.

'''
 plan=ROOT/'docs/plan.md';text=plan.read_text('utf8')
 if '## Текущий шаг — 93:' not in text:
  index=text.index('## Текущий шаг');text=text[:index]+header+text[index:].replace('## Текущий шаг —','## Этап')
 plan.write_text(text,'utf8')
 progress=ROOT/'docs/progress.md';text=progress.read_text('utf8')
 if '2026-10-05 — 93:' not in text:text+='\n## 2026-10-05 — 93: HD-интерфейс\n\n'+header.split('\n\n',1)[1]
 progress.write_text(text,'utf8')
 for path,rel in [(ROOT/'BetaGwent/README.md','../docs/'),(ROOT/'docs/README.md',''),(ROOT/'BetaGwent/ui/README.md','../../docs/')]:
  text=path.read_text('utf8')
  if '**Текущий этап93:' in text:continue
  end=text.index('\n\n');text=text[end+2:]
  top=f'''> **Текущий этап93: HD-оформление боя и редактора колоды.**
> Доски2048×708, крупные карты256×360, оригинальные фон/полки/рамки/кнопки.
> Общий стиль выбора колод, каталога, замены карт, бочек и сбросов.
> Локальные RU/EN preview.3; публикация отложена до игровой приёмки.
> [Изменения]({rel}PRESENTATION93_RU.md) · [Сборка]({rel}HD_PRESENTATION_PIPELINE93.md) · [План]({rel}plan.md).
> Native/архивные проверки прошли; внешний вид и управление в игре ещё
> не подтверждены. Релиз0.2.0 и предыдущие preview сохранены.

'''
  path.write_text(top+text,'utf8')
 print('Stage93 local preview finalized. HD/menus/packages verified; no publication. Runtime acceptance pending.')
if __name__=='__main__':main()

"""Check the finished local 0.2.1 build, without claiming runtime acceptance."""
from pathlib import Path
import hashlib,json,re
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 evidence=ROOT/'docs/evidence';report=json.loads((evidence/'stage94-completion.json').read_text('utf8'))
 hd=json.loads((evidence/'hd-art94.json').read_text('utf8'))
 for name,digest in report['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,'AS source changed after native build: '+name
 assert len(report['menus'])==6 and hd['cards']==562 and len(hd['boards'])==10
 assert len(hd['pages'])==12 and hd['bindings']==739 and hd['originalsUnchanged']
 # Exporter scratch files are replaced by each movie build. Persist the
 # final movie's identical texture set by content hash for all six reports.
 textureCache=ROOT/'BetaGwent/build/stage94/texture-evidence';textureCache.mkdir(parents=True,exist_ok=True)
 for path in (ROOT/'BetaGwent/ui/build/native-atlas').glob('*.dds'):
  digest=sha(path);dest=textureCache/(digest+'.dds')
  if not dest.exists():dest.write_bytes(path.read_bytes())
  assert sha(dest)==digest
 def dds(binding):
  path=textureCache/(binding['sha256']+'.dds')
  assert path.exists() and sha(path)==binding['sha256'],'Missing exact exported DDS: '+binding['source']
  return path
 sets=[];metrics=[]
 for item in report['menus']:
  assert sha(Path(item['resource']))==item['sha256']
  suffix='' if item['entry']=='BetaGwentBoard' else '-'+item['entry']
  native=json.loads((evidence/f"stage94-{item['language']}-board-resource-update{suffix}.json").read_text('utf8'))
  assert native['totalTextureChunks']==15 and native['exportedBindings']==30
  assert native['nativeABCMatchesBuiltSWF'] and native['headerTableChunkChecksumsVerified']
  sets.append(sorted(set(b['sha256'] for b in native['bindings'])))
 assert all(s==sets[0] for s in sets),'Texture pixels differ between menus/languages'
 native=json.loads((evidence/'stage94-ru-board-resource-update.json').read_text('utf8'))
 for page in hd['pages']:
  original=Path(page['path']);assert sha(original)==page['sha256']
  candidates=[b for b in native['bindings'] if Path(b['source']).name.startswith(original.stem+'_png')]
  assert candidates,original
  with Image.open(original) as im:a=np.array(im.convert('RGBA'),dtype=np.int16)
  with Image.open(dds(candidates[0])) as im:b=np.array(im.convert('RGBA'),dtype=np.int16)
  assert a.shape==b.shape
  opaque=a[:,:,3]>240;rgb=float(np.abs(a[:,:,:3]-b[:,:,:3])[opaque].mean()) if opaque.any() else 0
  alpha=float(np.abs(a[:,:,3]-b[:,:,3]).mean())
  assert rgb<8 and alpha<1.5,(original,rgb,alpha)
  metrics.append(dict(page=original.name,dimensions=page['size'],opaqueRGBMAE=rgb,alphaMAE=alpha))
 # Verify the actual exported DDS frame centre, not just the raw PNG.
 slot=json.loads(re.search(r'"-101":(\[[^\]]+\])',(ROOT/'BetaGwent/ui/src/BetaGwentHDArt.as').read_text('utf8'))[1])
 page,x,y,w,h=slot;original=Path(hd['pages'][page]['path'])
 frameDDS=dds(next(b for b in native['bindings'] if Path(b['source']).name.startswith(original.stem+'_png')))
 with Image.open(frameDDS) as im:centreAlpha=im.convert('RGBA').getpixel((x+w//2,y+h//2))[3]
 assert centreAlpha<=8,'Native target frame covers the card centre'
 aglais=json.loads((evidence/'aglais94.json').read_text('utf8'))
 assert aglais['passed'] and aglais['cases']==10
 for path,digest in aglais['sources'].items():assert sha(Path(path))==digest
 policy=json.loads((evidence/'pass-policy85.json').read_text('utf8'))
 assert policy['passed'] and len(policy['cases'])==25
 assert sha(Path(policy['source']))==policy['sha256']
 archives=[]
 for language in ('ru','en'):
  release=json.loads((evidence/f'stage94-release-{language}.json').read_text('utf8'))
  assert release['archiveVerified'] and sha(Path(release['archive']))==release['archiveSha256']
  compile_dir=ROOT/f'BetaGwent/build/board-compile94{language}'
  compile=json.loads((compile_dir/'result.json').read_text('utf8'))
  assert compile['exitCode']==0 and not compile['timedOut'] and compile['patchSourcesUnchangedDuringCompile']
  assert len(compile['patchSourcesBefore'])==60
  assert 'Success! Patch scripts blob saved' in (compile_dir/'stdout.txt').read_text('utf8',errors='replace')
  assert '[Script]: Error [' not in (compile_dir/'stdout.txt').read_text('utf8',errors='replace')
  root=ROOT/f'BetaGwent/build/release94/{language}/project/BetaGwent0924/workspace/scripts'
  for source in compile['patchSourcesBefore']:assert sha(root/source['path'])==source['sha256']
  archives.append({key:release[key] for key in ('archive','archiveBytes','archiveSha256')})
  for stage in (89,91,92,93):
   old=json.loads((evidence/f'stage{stage}-release-{language}.json').read_text('utf8'))
   assert sha(Path(old['archive']))==old['archiveSha256']
 report.update(version='0.2.1',hdPixelMetrics=metrics,archives=archives,
               compiledScriptsPerLanguage=60,policyChecks=25,aglaisChecks=10,targetFrameCentreAlpha=centreAlpha,nativeRuntimeVerified=False,
               installedGameModified=False,nexusPublicationPerformed=False)
 (evidence/'stage94-completion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 plan=ROOT/'docs/plan.md';t=plan.read_text('utf8')
 note='''
Сборка 0.2.1 RU/EN завершена локально: новые60 WS на язык,6 меню,
12 HD-страниц /15 уникальных native-текстур,44 связи каждого меню,
25 проверок паса/дуэли,10 сценариев Аглайисы, прозрачность DDS-рамки,
native cook и CRC/SHA архивов прошли.
Оригинальные ZIP89/91/92/93 сохранены. Установленная игра не менялась;
публикация Nexus вручную после одной проверки новой версии.
[Изменения/проверка](PRESENTATION94_RU.md) · [Сборка](BUILD_POLISH94.md).
'''
 marker='## Текущий шаг — 94: исправления ИИ, звука, погоды и контроллера\n'
 if note not in t:t=t.replace(marker,marker+note)
 plan.write_text(t,'utf8')
 progress=ROOT/'docs/progress.md';t=progress.read_text('utf8')
 if '2026-10-05 — 94:' not in t:t+='\n## 2026-10-05 — 94: 0.2.1\n'+note
 progress.write_text(t,'utf8')
 print('Validated 0.2.1 RU/EN, HD pixels, six menus and fresh scripts. Runtime acceptance pending.')
if __name__=='__main__':main()

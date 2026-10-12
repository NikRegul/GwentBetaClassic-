"""Verify 0.5.3 native compilation, menu provenance and packaged release metadata."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,zipfile,re,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'ai'))
from snapshot import verify as verify_snapshot
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main(stage=133,version='0.5.3',report_name='validation133.json'):
 # Test evidence must correspond to the source bytes being released.
 policy=read(E/'policy133.json');presentation=read(E/'presentation133.json');audio=read(E/'intro-audio133.json')
 locals_check=read(E/'locals133.json')
 assert locals_check['checks']>=5 and locals_check['invalidNativeLocalsRejected']
 cook_check=read(E/'cook-completion133.json')
 assert cook_check['checks']>=10 and cook_check['actualRunnerFunctions']
 states={lang:read(ROOT/f'BetaGwent/build/stage{stage}/powershell/{lang}-compile.json') for lang in ['ru','en']}
 assert states['ru']['run']==states['en']['run'] and all(s['stage']==stage for s in states.values()),'mixed native build runs'
 frozen=ROOT/f"BetaGwent/build/stage{stage}/powershell/{states['ru']['run']}-ai/snapshot"
 assert verify_snapshot(frozen)['fingerprint']==policy['fingerprint'],'stale full regression inputs'
 assert policy['checks']>=108 and presentation['checks']>=24
 for evidence in [policy,audio]:
  for name,digest in evidence['sources'].items():assert sha(ROOT/name)==digest,('stale regression evidence',name)
 assert sha(ROOT/'BetaGwent/ui/src/BetaGwentBoard.as')==presentation['sourceSha256'],'stale presentation evidence'
 assert {r['language'] for r in audio['reports']}=={'ru','en'} and all(r['pairs']>=441 and r['leaders']==21 and r['exhaustiveLeaderVariantPairs'] for r in audio['reports'])
 hidden=read(E/'hidden-information133.json')
 assert hidden['checks']==46 and all(r['pass'] for r in hidden['results']) and hidden['fingerprint']==policy['fingerprint']
 menus=read(E/f'stage{stage}-completion.json');assert len(menus['menus'])==8
 for name,digest in menus['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,name
 for m in menus['menus']:
  assert sha(Path(m['resource']))==m['sha256']
  suffix='' if m['entry']=='BetaGwentBoard' else '-'+m['entry']
  r=read(E/f"stage{stage}-{m['language']}-board-resource-update{suffix}.json")
  assert r['nativeABCMatchesBuiltSWF'] and r['headerTableChunkChecksumsVerified']
  bridge=read(E/f"stage{stage}-{m['language']}-board-bridge-bytecode{suffix}.json")
  contract=(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')
  expected=sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',contract)))
  assert expected and bridge['passed'] and bridge['bindings']==expected
  assert m['bindings']==len(expected)
 packages=[]
 for lang in ['ru','en']:
  build=Path(read(ROOT/f'BetaGwent/build/stage{stage}/powershell/{lang}-compile.json')['compiled'])
  compiled=read(build/'result.json')
  assert compiled['exitCode']==0 and not compiled['timedOut'] and compiled['patchSourcesUnchangedDuringCompile']
  log=(build/'stdout.txt').read_text('utf8',errors='replace')
  assert 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
  project=ROOT/f'BetaGwent/build/release{stage}/{lang}/project/BetaGwent0924/workspace/scripts'
  for item in compiled['patchSourcesBefore']:assert sha(project/item['path'])==item['sha256'],item['path']
  r=read(E/f'stage{stage}-release-{lang}.json');archive=Path(r['archive'])
  assert r['version']==version and r['archiveVerified'] and sha(archive)==r['archiveSha256']
  with zipfile.ZipFile(archive) as z:
   info=json.loads(z.read('Mods/modBetaGwent0924/info.json'))
   assert info['version']==version and info['gameVersion']=='5.01'
   notes=z.read('CHANGELOG_'+lang.upper()+'.md').decode('utf8')
   assert notes.splitlines()==(ROOT/f'BetaGwent/release/publish-{version}/CHANGELOG_{lang.upper()}.md').read_text('utf8').splitlines()
  packed=read(ROOT/f'BetaGwent/build/release{stage}/{lang}/packed-resources-verified.json')
  assert packed['packedPayloadsVerified']
  assert not any('redux' in item['path'].lower() for item in packed['entries'])
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   manifest=json.loads(z.read('manifest.json'))
   names=[name for name in z.namelist() if not name.endswith('/')]
   assert len(names)==len(set(names)),'duplicate ZIP entries'
   assert manifest['version']==version and manifest['stage']==stage and manifest['language']==lang
   assert set(names)=={item['path'] for item in manifest['files']}|{'manifest.json'},'incomplete manifest'
   assert 'reduxCompatibility' not in manifest
   for item in manifest['files']:
    assert z.getinfo(item['path']).file_size==item['bytes'],item['path']
    assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'],item['path']
   assert not any('redux' in name.lower() for name in z.namelist())
  assert archive.with_suffix('.zip.sha256').read_text('ascii').split()[0]==sha(archive)
  packages.append(dict(language=lang,archive=str(archive),bytes=archive.stat().st_size,sha256=r['archiveSha256'],freshNativeSources=len(compiled['patchSourcesBefore'])))
 report=dict(version=version,menus=8,packages=packages,archiveCrcAndManifestVerifiedByPackaging=True,nativeGameTested=False,checks={n:read(E/(n+'.json')) for n in ['followups126','halfcast126','quest126','engines126','weather-visual126','controller126','timing126','card-presentation126','decisive127','ships127','concede127','tutor127','preventive127','clearrisk127','draug127','combo127','no-targets127','followups-ui127','deck-combos128','rosters128','release-build126','losing131','cavalry131','ciri131','policy133','presentation133','intro-audio133']})
 report.update(verifiedAtUtc=datetime.now(timezone.utc).isoformat(),nativeRun=states['ru']['run'],regressionFingerprint=policy['fingerprint'],fullRegressionInputsCurrent=True,locals133=locals_check,cookCompletion133=cook_check)
 (E/report_name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps(dict(version=report['version'],menus=8,packages=packages,nativeGameTested=False),ensure_ascii=False))
if __name__=='__main__':main()

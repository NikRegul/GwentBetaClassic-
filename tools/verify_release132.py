"""Verify 0.5.2 native compilation, menu provenance and packaged release metadata."""
from pathlib import Path
import hashlib,json,zipfile,re
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'docs/evidence'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def main():
 menus=read(E/'stage132-completion.json');assert len(menus['menus'])==8
 for name,digest in menus['sources'].items():assert sha(ROOT/'BetaGwent/ui/src'/name)==digest,name
 for m in menus['menus']:
  assert sha(Path(m['resource']))==m['sha256']
  suffix='' if m['entry']=='BetaGwentBoard' else '-'+m['entry']
  r=read(E/f"stage132-{m['language']}-board-resource-update{suffix}.json")
  assert r['nativeABCMatchesBuiltSWF'] and r['headerTableChunkChecksumsVerified']
  bridge=read(E/f"stage132-{m['language']}-board-bridge-bytecode{suffix}.json")
  contract=(ROOT/'BetaGwent/development/scripts/game/betagwent/developmentBoardMenu.ws').read_text('utf-8-sig')
  expected=sorted(set(re.findall(r'GetMemberFlashFunction\("([^"]+)"\)',contract)))
  assert expected and bridge['passed'] and bridge['bindings']==expected
  assert m['bindings']==len(expected)
 packages=[]
 for lang in ['ru','en']:
  build=Path(read(ROOT/f'BetaGwent/build/stage132/powershell/{lang}-compile.json')['compiled'])
  compiled=read(build/'result.json')
  assert compiled['exitCode']==0 and not compiled['timedOut'] and compiled['patchSourcesUnchangedDuringCompile']
  log=(build/'stdout.txt').read_text('utf8',errors='replace')
  assert 'Success! Patch scripts blob saved' in log and '[Script]: Error [' not in log
  project=ROOT/f'BetaGwent/build/release132/{lang}/project/BetaGwent0924/workspace/scripts'
  for item in compiled['patchSourcesBefore']:assert sha(project/item['path'])==item['sha256'],item['path']
  r=read(E/f'stage132-release-{lang}.json');archive=Path(r['archive'])
  assert r['version']=='0.5.2' and r['archiveVerified'] and sha(archive)==r['archiveSha256']
  with zipfile.ZipFile(archive) as z:
   info=json.loads(z.read('Mods/modBetaGwent0924/info.json'))
   assert info['version']=='0.5.2' and info['gameVersion']=='5.01'
   notes=z.read('CHANGELOG_'+lang.upper()+'.md').decode('utf8')
   assert notes.splitlines()==(ROOT/f'BetaGwent/release/publish-0.5.2/CHANGELOG_{lang.upper()}.md').read_text('utf8').splitlines()
  packed=read(ROOT/f'BetaGwent/build/release132/{lang}/packed-resources-verified.json')
  assert packed['packedPayloadsVerified']
  assert not any('redux' in item['path'].lower() for item in packed['entries'])
  with zipfile.ZipFile(archive) as z:
   assert z.testzip() is None
   manifest=json.loads(z.read('manifest.json'))
   assert 'reduxCompatibility' not in manifest
   for item in manifest['files']:
    assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256'],item['path']
   assert not any('redux' in name.lower() for name in z.namelist())
  assert archive.with_suffix('.zip.sha256').read_text('ascii').split()[0]==sha(archive)
  packages.append(dict(language=lang,archive=str(archive),bytes=archive.stat().st_size,sha256=r['archiveSha256'],freshNativeSources=len(compiled['patchSourcesBefore'])))
 report=dict(version='0.5.2',menus=8,packages=packages,archiveCrcAndManifestVerifiedByPackaging=True,nativeGameTested=False,checks={n:read(E/(n+'.json')) for n in ['followups126','halfcast126','quest126','engines126','weather-visual126','controller126','timing126','card-presentation126','decisive127','ships127','concede127','tutor127','preventive127','clearrisk127','draug127','combo127','no-targets127','followups-ui127','deck-combos128','rosters128','release-build126','losing131','cavalry131','ciri131']})
 (E/'validation132.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps(dict(version=report['version'],menus=8,packages=packages,nativeGameTested=False),ensure_ascii=False))
if __name__=='__main__':main()

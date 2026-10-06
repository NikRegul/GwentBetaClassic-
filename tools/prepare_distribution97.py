"""Prepare verified 0.2.4 files for Nexus/Steam; does not upload anything."""
from pathlib import Path
import argparse,hashlib,json,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'BetaGwent/release/publish-0.2.4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 global OUT
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--stage',type=int,default=97)
 parser.add_argument('--version',default='0.2.4')
 args=parser.parse_args();stage=args.stage;version=args.version
 assert version and all(c.isalnum() or c in '.-' for c in version)
 OUT=ROOT/f'BetaGwent/release/publish-{version}'
 OUT.mkdir(parents=True,exist_ok=True)
 for language in ('ru','en'):
  tag=language.upper();archive=ROOT/f'BetaGwent/release/GwentBetaClassic-{version}-{tag}.zip'
  base=ROOT/f'BetaGwent/build/release{stage}/{language}'
  record=json.loads((ROOT/f'docs/evidence/stage{stage}-release-{language}.json').read_text('utf8'))
  assert record['version']==version and record['archiveVerified']
  assert sha(archive)==record['archiveSha256']
  with zipfile.ZipFile(archive) as z:assert z.testzip() is None
  nexus=OUT/'Nexus';nexus.mkdir(exist_ok=True);shutil.copyfile(archive,nexus/archive.name)
  checksum=archive.with_suffix('.zip.sha256');shutil.copyfile(checksum,nexus/checksum.name)
  for stem in ('NEXUS_FIELDS','NEXUS_DESCRIPTION','README','CONTROLS','CHANGELOG'):
   shutil.copyfile(ROOT/f'BetaGwent/release/{stem}_{tag}.md',nexus/f'{stem}_{tag}.md')
  steam=OUT/'Steam'/tag
  shutil.copytree(base/'package/Mods/modBetaGwent0924',steam/'modBetaGwent0924',dirs_exist_ok=True)
  for p in (base/'package/Mods/modBetaGwent0924').rglob('*'):
   if p.is_file():assert sha(p)==sha(steam/'modBetaGwent0924'/p.relative_to(base/'package/Mods/modBetaGwent0924'))
  for name in ('LICENSE','ATTRIBUTIONS.md','SOURCE.txt',f'README_{tag}.md',f'CONTROLS_{tag}.md',f'CHANGELOG_{tag}.md'):
   shutil.copyfile(base/'package'/name,steam/'modBetaGwent0924'/name)
  for stem in ('STEAM_DESCRIPTION','CONTROLS','CHANGELOG'):
   shutil.copyfile(ROOT/f'BetaGwent/release/{stem}_{tag}.md',steam/f'{stem}_{tag}.md')
  (steam/'upload-metadata.json').write_text(json.dumps(dict(title='Gwent Beta Classic — '+tag,version=version,language=language,contentDirectory=str(steam/'modBetaGwent0924'),thumbnail=str(OUT/'header.jpg'),workshopId=None,uploaded=False,runtimeAcceptancePending=True),ensure_ascii=False,indent=2)+'\n','utf8')
 shutil.copyfile(ROOT/'BetaGwent/release/nexus/GwentBetaClassic-header-v2.jpg',OUT/'header.jpg')
 shutil.copyfile(ROOT/f'docs/PUBLISH{stage}_RU.md',OUT/'PUBLISH_RU.md')
 for lang in ('RU','EN'):shutil.copyfile(ROOT/f'docs/PRESENTATION{stage}_{lang}.md',OUT/f'CHECK_{lang}.md')
 records=[dict(path=p.relative_to(OUT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='manifest.json']
 (OUT/'manifest.json').write_text(json.dumps(dict(version=version,stage=stage,files=records,uploaded=False,runtimeVerified=False),indent=2)+'\n','utf8')
 print('Prepared Nexus ZIPs, Steam content folders, descriptions, controls, preview and checks:',OUT)
if __name__=='__main__':main()

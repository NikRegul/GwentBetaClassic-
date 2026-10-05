"""Stage audited source deltas for one 0.2.1 commit; no upload or ref update."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'BetaGwent/build/public-source89/GwentBetaClassic'
OUT=ROOT/'BetaGwent/build/public-source94/GwentBetaClassic'
EXCLUDE={'github_auth_probe89.py','stage89_prepare.py','prepare_github89.py','download_github_cli93.py','style_presentation93.py','prepare_polish94.py'}
def main():
 OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(OLD,OUT,dirs_exist_ok=True)
 paths=[]
 for folder in ('BetaGwent/scripts','BetaGwent/development/scripts','BetaGwent/ui/src','tools','data/beta924/duel','data/beta924/design','data/beta924/ai'):
  for p in (ROOT/folder).rglob('*'):
   if not p.is_file() or any(x in ('vendor','__pycache__','bin','obj') for x in p.relative_to(ROOT).parts):continue
   if p.name in EXCLUDE or p.suffix not in ('.py','.ws','.as','.json','.xml','.md','.cs','.csproj','.ps1'):continue
   paths.append(p)
 for name in ('BUILD_RU','BUILD_EN','ARCHITECTURE_AI_RU','ARCHITECTURE_AI_EN','ai_rules88','ai_rules88_adaptation','ROADMAP',
              'PRESENTATION93_RU','PRESENTATION93_EN','HD_PRESENTATION_PIPELINE93','PRESENTATION94_RU','PRESENTATION94_EN','BUILD_POLISH94'):
  paths.append(ROOT/f'docs/{name}.md')
 for p in (ROOT/'BetaGwent/release').glob('*.md'):paths.append(p)
 paths.extend([ROOT/'deck_rules.txt',ROOT/'BetaGwent/ui/board-config.xml'])
 for p in paths:
  dest=OUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 readme=(OLD/'README.md').read_text('utf8')
 readme=readme.replace('Changes0.2.0','Changes0.2.1').replace('Изменения 0.2.0','Изменения 0.2.1')
 marker='## Contributing'
 note='''## 0.2.1

HD Beta boards and deck-builder skins, 384x540 artwork, source-resolution
weather/hit frames, separate death/consume effects, White Frost presentation
fix, conservative leader/pass ordering and armor-aware Seltkirk estimates,
controller hand/placement/target navigation, transparent HD target highlights,
native RMB inspection/cancel routing and Aglais replay/banish ordering.
Save schema and deck IDs preserved.

Fresh RU/EN script compilation, six native menu builds, DDS/ABC/bridge checks,
25 policy cases,10 Aglais sequencing cases and package integrity checks passed.
Installed-game visual,
controller and battle acceptance of this revision remains pending.

- [Changes and acceptance: Russian](docs/PRESENTATION94_RU.md)
- [Changes and acceptance: English](docs/PRESENTATION94_EN.md)
- [Current build sequence and AI details](docs/BUILD_POLISH94.md)

'''
 readme=readme[:readme.index('The owner installed')]+readme[readme.index(marker):] if 'The owner installed' in readme else readme
 (OUT/'README.md').write_text(readme.replace(marker,note+marker),'utf8')
 files=[];delta=[]
 for p in sorted(OUT.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(OUT).as_posix();raw=p.read_bytes();text=raw.decode('utf-8-sig')
  assert not re.search(r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"',text),rel
  assert not re.search(r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s*$',text),rel
  assert not any(part in ('.git','vendor','assets','audio','depot') for part in Path(rel).parts),rel
  assert p.suffix not in ('.zip','.bnk','.wem','.wav','.redswf','.rsblob','.db','.log'),rel
  digest=hashlib.sha256(raw).hexdigest();files.append(dict(path=rel,bytes=len(raw),sha256=digest))
  previous=OLD/rel
  if not previous.exists() or previous.read_bytes()!=raw:
   delta.append(dict(path=rel,mode='100644',type='blob',content=raw.decode('utf8')))
 payload=OUT.parent/'tree-elements.json';payload.write_text(json.dumps(delta,ensure_ascii=False),'utf8')
 report=dict(directory=str(OUT),files=files,fileCount=len(files),changedFiles=len(delta),
             changedBytes=sum(len(x['content'].encode('utf8')) for x in delta),assetsExcluded=True,
             licenseKeysExcluded=True,parent='a75efa62831ecea6cff4131815863a58c5fc4fd9',
             baseTree='59753105d09a42c48c285e2ba13677131e6a9a44',repository='NikRegul/GwentBetaClassic-',
             payload=str(payload),uploaded=False)
 (OUT.parent/'manifest.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
if __name__=='__main__':main()

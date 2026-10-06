"""Stage source-only 0.2.6 relative to the verified public stage97 snapshot."""
from pathlib import Path
import hashlib,json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'BetaGwent/build/public-source97/GwentBetaClassic'
OUT=ROOT/'BetaGwent/build/public-source99/GwentBetaClassic'
EXCLUDE={'github_auth_probe89.py','stage89_prepare.py','prepare_github89.py','download_github_cli93.py','style_presentation93.py','prepare_polish94.py'}

def main():
    OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(OLD,OUT,dirs_exist_ok=True)
    for folder in ('BetaGwent/scripts','BetaGwent/development/scripts','BetaGwent/ui/src','tools','data/beta924/duel','data/beta924/design','data/beta924/ai'):
        for p in (ROOT/folder).rglob('*'):
            if not p.is_file() or any(x in ('vendor','__pycache__','bin','obj') for x in p.relative_to(ROOT).parts):continue
            if p.name in EXCLUDE or p.suffix not in ('.py','.ws','.as','.json','.xml','.md','.cs','.csproj','.ps1'):continue
            dest=OUT/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
    for pattern in ('*95*.md','*96*.md','*97*.md','*98*.md','*99*.md'):
        for p in (ROOT/'docs').glob(pattern):shutil.copyfile(p,OUT/'docs'/p.name)
    for p in (ROOT/'BetaGwent/release').glob('*.md'):shutil.copyfile(p,OUT/'BetaGwent/release'/p.name)
    old=(OLD/'README.md').read_text('utf8');tail=old[old.index('## Contributing'):] if '## Contributing' in old else ''
    note='''# Gwent Beta Classic 0.2.6

Gwent Beta 0.9.24 inside The Witcher 3: 479 collectible cards, 21 leaders,
five factions, saved decks, NPC rewards, kegs and controller support.

**Back up saves before installation and every update. Bugs can still occur.**

Russian 0.2.5 editor/NPC startup was accepted in the installed game. Compact
native menus remain below 55 MiB; cards are 288×405 and faction board halves
1536×531. Game memory settings are unchanged. 0.2.6 changes atlas sampling,
the native Bitmap fallback, card selection borders and controller body bounds.
Visual flicker/border acceptance and English acceptance still need testing.

Both packages retain the nested-play/cursor fixes from 0.2.4. Card rules and AI
are unchanged. RU sources match the reused stage97 compilation; EN voice durations
are synchronized with the English bank and freshly compiled in stage99. Six
native menus are rebuilt. Package checks do not replace native battle tests.
Original images, audio and Wwise keys are excluded. Original code is GPL-3.0-only.

- [Current build sequence](docs/BUILD99.md)
- [Russian acceptance notes](docs/PRESENTATION99_RU.md)
- [English acceptance notes](docs/PRESENTATION99_EN.md)
- [Manual AI editing / Russian](docs/AI_MANUAL95_RU.md)
- [Nexus and Steam preparation](docs/PUBLISH99_RU.md)

'''
    (OUT/'README.md').write_text(note+tail,'utf8')
    files=[];delta=[]
    for p in sorted(OUT.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(OUT).as_posix();raw=p.read_bytes();text=raw.decode('utf-8-sig')
        assert not re.search(r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"',text),rel
        assert not re.search(r'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\s*$',text),rel
        assert not any(x in ('.git','vendor','assets','audio','depot') for x in Path(rel).parts),rel
        assert p.suffix not in ('.zip','.bnk','.wem','.wav','.redswf','.rsblob','.db','.log'),rel
        files.append(dict(path=rel,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        previous=OLD/rel
        if not previous.exists() or previous.read_bytes()!=raw:delta.append(dict(path=rel,mode='100644',type='blob',content=raw.decode('utf8')))
    payload=OUT.parent/'tree-elements.json';payload.write_text(json.dumps(delta,ensure_ascii=False),'utf8')
    report=dict(directory=str(OUT),files=files,fileCount=len(files),changedFiles=len(delta),changedBytes=sum(len(x['content'].encode('utf8')) for x in delta),assetsExcluded=True,licenseKeysExcluded=True,parent='8fe12ff98d3f676b7a97d2dd6c9509ecb3c52d2f',baseTree='9ce733f01a0e68ead2930fed578288fb8c9568e5',repository='NikRegul/GwentBetaClassic-',payload=str(payload),uploaded=False)
    (OUT.parent/'manifest.json').write_text(json.dumps(report,indent=2)+'\n','utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))

if __name__=='__main__':main()

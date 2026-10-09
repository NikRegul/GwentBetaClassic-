"""Stage source-only publication and a bounded text upload manifest."""
from pathlib import Path
import json,shutil,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'BetaGwent/build/public-source89/GwentBetaClassic'
OUT.mkdir(parents=True,exist_ok=True)
paths=[]
for folder in ('BetaGwent/scripts','BetaGwent/development/scripts','BetaGwent/ui/src','tools','data/beta924/duel','data/beta924/design','data/beta924/ai'):
    for p in (ROOT/folder).rglob('*'):
        if not p.is_file() or any(x in ('vendor','__pycache__','bin','obj') for x in p.relative_to(ROOT).parts):continue
        if p.suffix not in ('.py','.ws','.as','.json','.xml','.md','.cs','.csproj','.txt','.ps1'):continue
        if p.name in ('github_auth_probe89.py','stage89_prepare.py','prepare_github89.py'):continue
        if p.suffix=='.txt' and p.name!='english89-indexed.txt':continue
        paths.append(p)
paths+=[ROOT/'deck_rules.txt',ROOT/'BetaGwent/ui/board-config.xml']
for name in ('BUILD_RU','BUILD_EN','ARCHITECTURE_AI_RU','ARCHITECTURE_AI_EN','ai_rules88','ai_rules88_adaptation','ROADMAP'):
    paths.append(ROOT/('docs/'+name+'.md'))
for name in ('README_RU','README_EN','CONTROLS_RU','CONTROLS_EN','CHANGELOG_RU','CHANGELOG_EN','NEXUS_DESCRIPTION_RU','NEXUS_DESCRIPTION_EN','NEXUS_FIELDS_RU','NEXUS_FIELDS_EN'):paths.append(ROOT/('BetaGwent/release/'+name+'.md'))
for p in paths:
    dst=OUT/p.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dst)
shutil.copyfile(ROOT/'BetaGwent/build/release89/GPL-3.0.txt',OUT/'LICENSE')
(OUT/'README.md').write_text('''# Gwent Beta Classic

The Witcher 3 Gwent replacement based on Gwent Beta **0.9.24**.
Russian and English packages, 479 collectible cards including 21 leaders,
five factions, saved deck builder, collection, NPC rewards, kegs and controller.

- [Русское описание и установка](BetaGwent/release/README_RU.md)
- [English description and installation](BetaGwent/release/README_EN.md)
- [Сборка](docs/BUILD_RU.md) / [Build guide](docs/BUILD_EN.md)
- [Устройство ИИ](docs/ARCHITECTURE_AI_RU.md) / [AI architecture](docs/ARCHITECTURE_AI_EN.md)
- [Контроллер](BetaGwent/release/CONTROLS_RU.md) / [Controls](BetaGwent/release/CONTROLS_EN.md)
- [Изменения 0.2.0](BetaGwent/release/CHANGELOG_RU.md) / [Changes](BetaGwent/release/CHANGELOG_EN.md)

**You must back up your saves before installing the mod and before every update. Bugs can still occur; use a separate test save for your first matches.**

Install **one** full RU or EN package under Mods/modBetaGwent0924. Source
checkout alone is not an installable mod. See Releases for packaged downloads
once uploaded. Players do not need REDkit or Wwise.

The owner installed and accepted the previous Russian battle build. This
revision fixes choice focus and adds four ordinary-NPC rewards plus English.
Its new gameplay paths need an installed-game acceptance pass. Current artwork,
animations and archetype heuristics will be refined towards the historical Beta.

## Contributing

Use Issues for bugs and strategy examples; include language/version, deck,
round, score, controller/mouse, recent actions and expected behavior. Submit
focused PRs. Modify generators instead of generated tables, preserve saved
field/preset identities, compile with REDkit and describe relevant validation.
Source-only publication intentionally excludes original clients, depot,
art/audio assets, SDKs, native resource templates and Wwise licenses. A fresh
clone needs those local build inputs; current setup is not fully portable.

Original project code is GPL-3.0-only; see LICENSE and ATTRIBUTIONS.md.
Gwent/The Witcher names, original card texts, art, sound and game resources
belong to their respective owners and are not relicensed under GPL.
''','utf8')
(OUT/'ATTRIBUTIONS.md').write_text('''# Attribution and license scope

Copyright (C) 2026 NikRegul and contributors — original mod implementation.
Original implementation is distributed under GPL-3.0-only; see LICENSE.

Gwent and The Witcher are CD Projekt properties. Historical card names,
descriptions, IDs and derived rule data retain their original provenance;
the mod license does not grant rights to original game content. Original game
clients, textures, voice recordings, sound banks and native project resources
are not included in this source distribution.

Board/card asset input is LegacyGwent DIY; gameplay identity and localization
input is the local Gwent 0.9.24.3.432 client. Their asset rights are separate
from this implementation. Build tooling uses external Apache Royale,
UnityPy, Pillow, vgmstream, wwiser, REDkit/Scaleform and Wwise; their respective
licenses apply. Wwise project license keys and third-party SDK binaries are
never part of this repository or player packages.
''','utf8')
(OUT/'.gitignore').write_text('''# Local game/tool/asset inputs and build outputs
BetaGwent/build/
BetaGwent/ui/build/
BetaGwent/ui/assets/
BetaGwent/audio/
BetaGwent/release/*.zip*
data/beta924/normalized/
data/beta924/raw/
GwentB/
depot/
Gwent 0.9.24.3.432/
LegacyGwent*/
tools/vendor/
__pycache__/
bin/
obj/
*.wproj
*.wwu
*.bnk
*.wem
*.wav
*.redswf
*.rsblob
*.db
*.log
*.sav
.env
.codex/
''','utf8')
files=[]
for p in sorted(OUT.rglob('*')):
    if not p.is_file():continue
    data=p.read_bytes();text=data.decode('utf-8-sig')
    # Match actual XML license material, not tool code that preserves it.
    if re.search(r'<Property[^>]+Name="LicenseKey"[^>]+Value="[^"\s]+"',text):raise RuntimeError('License material detected')
    if '-----BEGIN PRIVATE KEY-----' in text:raise RuntimeError('Private key detected')
    files.append(dict(path=p.relative_to(OUT).as_posix(),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
report=dict(directory=str(OUT),files=files,fileCount=len(files),bytes=sum(x['bytes'] for x in files),assetsExcluded=True,wwiseLicenseExcluded=True,repository='NikRegul/GwentBetaClassic-')
(OUT.parent/'manifest.json').write_text(json.dumps(report,indent=2),'utf8')
print(str(len(files))+' source files, '+str(report['bytes'])+' bytes staged.')

"""Install the RC2 UI-only update over the verified Steam RC1; keep a backup."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
BUILD=ROOT/'BetaGwent/build/release082-rc2'
GAME=Path('F:/Steam/steamapps/common/The Witcher 3')
MOD=GAME/'Mods/modBetaGwent0924'
SOURCE=BUILD/'nextgen/package/Mods/modBetaGwent0924'
PREVIOUS=ROOT/'BetaGwent/build/release082-rc1/nextgen/package/Mods/modBetaGwent0924'
NAMES=['content/blob0.bundle','content/metadata.store','info.json']
PRESERVED=['content/precompiled.rsblob','content/soundspc.cache','content/dep.cache']
PREVIOUS_VERSION='0.8.2-rc1'
VERSION='0.8.2-rc2'
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    # Read process state with native PowerShell; do not interrupt a player's game.
    probe=subprocess.run(['powershell','-NoProfile','-Command',"$ErrorActionPreference='Stop'; if(Get-Process witcher3 -ErrorAction SilentlyContinue){exit 7}; exit 0"],capture_output=True)
    assert probe.returncode==0,'Close the game before installing; no files were changed'
    assert (BUILD/'final-audit.json').is_file(),'Final archive audit required'
    assert json.loads((MOD/'info.json').read_text('utf8'))['version']==PREVIOUS_VERSION
    assert json.loads((SOURCE/'info.json').read_text('utf8'))['version']==VERSION
    expected={n:sha(MOD/n) for n in NAMES+PRESERVED}
    assert all(expected[n]==sha(PREVIOUS/n) for n in expected),'Installed files differ from tested previous release'
    backup=BUILD/'installed-before-nextgen';assert not backup.exists(),'Keep prior backups immutable'
    for n in NAMES:
        target=backup/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(MOD/n,target)
        assert sha(target)==expected[n]
    report=dict(game=str(GAME),before=expected,after={},backup=str(backup),savesModified=False)
    try:
        for n in NAMES:
            shutil.copy2(SOURCE/n,MOD/n);assert sha(MOD/n)==sha(SOURCE/n);report['after'][n]=sha(MOD/n)
        assert all(sha(MOD/n)==expected[n] for n in PRESERVED),'Preserved file changed'
    except BaseException:
        for n in NAMES:shutil.copy2(backup/n,MOD/n)
        raise
    (BUILD/'install-nextgen.json').write_text(json.dumps(report,indent=2),'utf8')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()

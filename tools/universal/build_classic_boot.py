"""Package Classic fix4 after the four pinned menu compilations."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'BetaGwent/build/classic081-boot-fix4'


def main():
    report=json.loads((BASE/'menus/menus.json').read_text('utf8'))
    for row in report['menus']:
        dump=Path(row['path']).with_name(Path(row['path']).stem+'-abc.txt').read_text('utf8',errors='replace')
        send=re.search(r'^  private function send\([^\n]*\n  \{\n.*?^  \}',dump,re.M|re.S).group()
        assert 'getglobalscope' not in send
        assert re.search(r'getlocal0\s+\d+\s+getlocal1\s+\d+\s+getlocal2\s+\d+\s+callpropvoid',send)
        assert not re.search(r'getlex\s+_NATIVE_callGameEvent\s+\d+\s+getlocal0\s+\d+\s+getlocal1\s+\d+\s+getlocal2\s+\d+\s+callpropvoid',send)
    subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/classic132/build_resources.py'),'--stage','202',
        '--menus',str(BASE/'menus'),'--game','D:/GOG Galaxy/Games/The Witcher 3 Wild Hunt',
        '--out',str(BASE/'resources-classic'),'--gui-limit-mib','63'],check=True)
    import package_language_layout as pack
    pack.BASE=BASE
    receipt=pack.package('classic',ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix3-LanguageLayout-AllLanguages.zip',
        ROOT/'BetaGwent/build/universal081-language-layout/resources-classic',
        out=ROOT/'BetaGwent/release/GwentBetaClassic-0.8.1-1.32-fix4-AllLanguages.zip',
        version='0.8.1-classic-boot-fix4')
    receipt.update(compiledMenus=4,compiledReceiverMatchesClassic=True,startupMethodChecks=19,
                   nativeGameplayVerified=False,fix3GameplayAccepted=False)
    (BASE/'package.json').write_text(json.dumps(receipt,indent=2)+'\n','utf8')


if __name__=='__main__':main()

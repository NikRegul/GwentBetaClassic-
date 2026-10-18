"""Freeze the tested RC3 revision separately from the first compile attempt."""
from pathlib import Path
import sys,shutil
sys.path.insert(0,str(Path(__file__).parent))
import finalize_ui_intro_sources as finalize
ROOT=finalize.ROOT
SOURCE=ROOT/'BetaGwent/build/release082-rc3'
BUILD=ROOT/'BetaGwent/build/release082-rc3-ready'
def main():
    assert not BUILD.exists();BUILD.mkdir()
    for platform in ['nextgen','classic']:
        shutil.copytree(SOURCE/platform/'ui',BUILD/platform/'ui')
        shutil.copytree(SOURCE/platform/'extra-resources',BUILD/platform/'extra-resources')
        shutil.copy2(SOURCE/platform/'ui-inputs.json',BUILD/platform/'ui-inputs.json')
    shutil.copytree(SOURCE/'scripts',BUILD/'scripts');shutil.copytree(SOURCE/'redux',BUILD/'redux')
    shutil.copy2(SOURCE/'classic/subimages.json',BUILD/'classic/subimages.json')
    for p in SOURCE.glob('*tests.json'):shutil.copy2(p,BUILD/p.name)
    shutil.copy2(SOURCE/'exchange-languages.json',BUILD/'exchange-languages.json')
    shutil.copy2(SOURCE/'exchange-fonts.json',BUILD/'exchange-fonts.json')
    finalize.BUILD=BUILD;finalize.main()
if __name__=='__main__':main()

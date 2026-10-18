"""Prepare RC2 without modifying the retained RC1 release."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'BetaGwent/build/release082-rc1'
BUILD=ROOT/'BetaGwent/build/release082-rc2'
OLD='if(!ready||nameOpen||!selectingDecks||!importing&&!editingDeck)return;'
NEW='if(!ready||nameOpen||!(selectingDecks||editingDeck)||(!importing&&!editingDeck))return;'
def patch(path):
    raw=path.read_bytes();assert raw.startswith(b'\xef\xbb\xbf') and b'\n' not in raw.replace(b'\r\n',b'')
    text=raw.decode('utf-8-sig');assert text.count(OLD)==1
    path.write_bytes(b'\xef\xbb\xbf'+text.replace(OLD,NEW).encode('utf8'))
def main():
    assert not BUILD.exists(),'Fresh build required';BUILD.mkdir()
    for platform in ['nextgen','classic']:
        shutil.copytree(SOURCE/platform/'ui',BUILD/platform/'ui')
        board=BUILD/platform/'ui/src/BetaGwentBoard.as';patch(board)
        for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
            shutil.copy2(board,board.parent.parent/mirror/board.name)
        manifest=json.loads((SOURCE/platform/'ui-inputs.json').read_text('utf8'))
        manifest['sources']['BetaGwentBoard.as']=hashlib.sha256(board.read_bytes()).hexdigest()
        (BUILD/platform/'ui-inputs.json').write_text(json.dumps(manifest,indent=2),'utf8')
    for name in ['classic-prepared','redux','compile-nextgen']:
        # Only published compiler output and result are reused; no native recompilation for a UI guard.
        if name=='compile-nextgen':
            out=BUILD/name;out.mkdir();shutil.copy2(SOURCE/name/'result.json',out/'result.json');shutil.copytree(SOURCE/name/'compiled',out/'compiled')
        else:shutil.copytree(SOURCE/name,BUILD/name)
    shutil.copy2(SOURCE/'classic/subimages.json',BUILD/'classic/subimages.json')
    board=ROOT/'BetaGwent/ui/src/BetaGwentBoard.as';patch(board)
    for mirror in ['src-BetaGwentBoard','src-GwintGame','src-DeckBuilder','src-BetaGwentKeg']:
        shutil.copy2(board,board.parent.parent/mirror/board.name)
    (BUILD/'source-change.json').write_text(json.dumps(dict(version='0.8.2-rc2',previous='0.8.2-rc1',changedMethod='BetaGwentBoard.openDeckExchange',scriptSourcesChanged=False,gameInstalled=False),indent=2),'utf8')
    print(BUILD)
if __name__=='__main__':main()

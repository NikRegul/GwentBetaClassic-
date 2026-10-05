"""Build/install all three entry movies together, without REDkit UI automation."""
from pathlib import Path
import argparse
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply',action='store_true')
parser.add_argument('--reuse-assets',action='store_true')
args=parser.parse_args()
for index,entry in enumerate(('BetaGwentBoard','DeckBuilder','GwintGame')):
    command=[sys.executable,str(ROOT/'tools/ui/build_board.py'),'--entry',entry]
    if index or args.reuse_assets:command+=['--reuse-assets']
    subprocess.run(command,cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/'tools/ui/check_board_bridge.py'),'--entry',entry],cwd=ROOT,check=True)
    if args.apply:
        subprocess.run([sys.executable,str(ROOT/'tools/ui/install_native_atlas.py'),'--entry',entry,'--apply'],cwd=ROOT,check=True)
if args.apply:subprocess.run([sys.executable,str(ROOT/'tools/ui/install_gwent_entries.py'),'--apply'],cwd=ROOT,check=True)

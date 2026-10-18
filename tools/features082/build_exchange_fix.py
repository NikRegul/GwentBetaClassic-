"""Ship RC2's UI fix with exactly the already compiled RC1 gameplay code."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import build_release as build
build.BUILD=build.ROOT/'BetaGwent/build/release082-rc2'
build.VERSION='0.8.2-rc2'
if __name__=='__main__':
    {'nextgen':build.nextgen,'classic':build.classic}[sys.argv[1]]()

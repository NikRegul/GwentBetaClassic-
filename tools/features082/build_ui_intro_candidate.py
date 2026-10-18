from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
import build_release as build
build.BUILD=build.ROOT/'BetaGwent/build/release082-rc3-ready';build.VERSION='0.8.2-rc3'
build.CLASSIC_COMPILE=build.ROOT/'BetaGwent/build/universal081/classic-runtime/runs/release082-rc3-ready/result.json'
if __name__=='__main__':{'nextgen':build.nextgen,'classic':build.classic}[sys.argv[1]]()

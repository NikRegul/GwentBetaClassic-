"""Build 0.9.3a with checked AI fixes and all selected Classic-profile gates."""
from pathlib import Path
from build093 import pipeline

pipeline.VERSION = '0.9.3a'
pipeline.LATEST = Path(__file__).resolve().parents[2]/'BetaGwent/build/release093a-latest.json'

if __name__ == '__main__':
    pipeline.main()

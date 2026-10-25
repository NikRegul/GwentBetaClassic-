"""Build the lock/resilience hotfix without changing saved 0.9.3/0.9.3a releases."""
from pathlib import Path
from build093 import pipeline

pipeline.VERSION = '0.9.3b'
pipeline.LATEST = Path(__file__).resolve().parents[2]/'BetaGwent/build/release093b-latest.json'

if __name__ == '__main__':
    pipeline.main()

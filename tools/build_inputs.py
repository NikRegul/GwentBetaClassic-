"""Permanent local inputs for the current Classic and Next-Gen pipelines."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / 'BetaGwent/build-inputs'
BASE_SCRIPTS = INPUTS / 'script-baseline'
BASE_ARCHIVES = INPUTS / 'package-baseline'
UI = INPUTS / 'ui'
UI_BASELINE = INPUTS / 'ui-baseline'
ASSETS = INPUTS / 'accepted-assets'
AUDIO = INPUTS / 'classic-audio'
CLASSIC_RUNTIME = ROOT / 'BetaGwent/toolchains/classic-runtime'
AUDIO_MANIFEST_SHA256 = '2c883f019f9de6f55e9d29221a795a1ec814b565c7274c51d85751c5ea5133e8'  # classic audio shipped in 0.9.2
PUBLIC = ROOT / 'BetaGwent/publication'

[CmdletBinding()]
param(
    [ValidateSet('package','verify')][string]$Step='package',
    [string]$Python='python'
)
$ErrorActionPreference='Stop'
$BuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $BuildRoot
try {
    & $Python -X utf8 tools/build_release143.py --step $Step
    if($LASTEXITCODE -ne 0){throw '0.6.7 failed; inspect BetaGwent/build/stage143/logs.'}
} finally { Pop-Location }

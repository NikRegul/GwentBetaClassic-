[CmdletBinding()]
param(
    [ValidateSet('package','verify')][string]$Step='package',
    [string]$Python='python'
)
$ErrorActionPreference='Stop'
$BuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $BuildRoot
try {
    & $Python -X utf8 tools/build_release142.py --step $Step
    if($LASTEXITCODE -ne 0){throw '0.6.6 failed; inspect BetaGwent/build/stage142/logs.'}
} finally { Pop-Location }

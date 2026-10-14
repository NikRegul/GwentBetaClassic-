[CmdletBinding()]
param([ValidateSet('full','scripts','menus','package','verify')][string]$Step='full',
      [ValidateSet('all','ru','en','de','it','pt-br')][string]$Language='ru')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:PYTHONIOENCODING='utf-8'
& python -X utf8 tools/build_release139.py --step $Step --language $Language
if($LASTEXITCODE -ne 0){throw '0.6.3 build failed; inspect BetaGwent/build/stage139/logs.'}

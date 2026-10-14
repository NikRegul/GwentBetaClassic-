[CmdletBinding()]
param([ValidateSet('full','scripts','menus','package','verify')][string]$Step='full',
      [ValidateSet('all','ru','en','de','it','pt-br')][string]$Language='ru',
      [string]$Python='python')
$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:PYTHONIOENCODING='utf-8'
& $Python -X utf8 tools/build_release140.py --step $Step --language $Language
if($LASTEXITCODE -ne 0){throw '0.6.4 build failed; inspect BetaGwent/build/stage140/logs.'}

[CmdletBinding()]
param([ValidateSet('full','prepare','scripts','menus','package','verify')][string]$Step='full',
      [ValidateSet('all','both','en','ru','de','it','pt-br')][string]$Language='all',
      [switch]$RebuildExisting)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:PYTHONIOENCODING='utf-8'
$BuildArguments=@('-X','utf8','tools/build_release137.py','--step',$Step,'--language',$Language)
if($RebuildExisting){$BuildArguments+='--rebuild-existing'}
& python @BuildArguments
if($LASTEXITCODE -ne 0){throw '0.6.1 build failed; inspect BetaGwent/build/stage137/logs137.'}

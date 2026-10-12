[CmdletBinding()]
param([ValidateSet('full','prepare','scripts','menus','package','verify')][string]$Step='full',
      [ValidateSet('all','both','en','ru','de','it','pt-br')][string]$Language='all',
      [switch]$RebuildExisting)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
$env:PYTHONIOENCODING='utf-8'
$BuildArguments=@('-X','utf8','tools/build_release138.py','--step',$Step,'--language',$Language)
if($RebuildExisting){$BuildArguments+='--rebuild-existing'}
& python @BuildArguments
if($LASTEXITCODE -ne 0){throw '0.6.2 build failed; inspect BetaGwent/build/stage138/logs138.'}
if($Step -eq 'full' -or $Step -eq 'verify'){
    Get-ChildItem -LiteralPath 'BetaGwent/release' -Filter 'GwentBetaClassic-0.6.2-*.zip' |
        ForEach-Object { '{0}  {1:N0} bytes  {2}' -f $_.Name,$_.Length,$_.LastWriteTime }
    'Report: docs/evidence/validation138.json'
}

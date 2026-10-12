# Build current gameplay and UI without the obsolete Redux compatibility layer.
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [ValidatePattern('^[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.]+)?$')][string]$Version='0.5.1',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI=$true
)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 131 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI
if ($Language -eq 'both' -and $Version -eq '0.5.1' -and $Step -in @('full','package')) {
    & python -X utf8 (Join-Path $PSScriptRoot 'verify_release131.py')
    if ($LASTEXITCODE -ne 0) { throw '0.5.1 release verification failed.' }
}

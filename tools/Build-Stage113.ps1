# Same convenient version-specific entry point as Build-Stage109.ps1 for 0.3.1.
param(
    [ValidateSet('ru','en','both')][string]$Language='ru',
    [string]$Version='0.3.4',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 113 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI

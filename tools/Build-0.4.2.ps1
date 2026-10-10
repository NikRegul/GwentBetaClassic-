# Editable 0.4.2 build: script checks, localized menus, native compilation and ZIPs.
[CmdletBinding()]
param(
    [ValidateSet('ru','en','both')][string]$Language='both',
    [string]$Version='0.4.2',
    [ValidateSet('full','prepare','scripts','menus','package')][string]$Step='full',
    [string]$Compiled='', [string]$KegVideo='', [switch]$CheckAI
)
& (Join-Path $PSScriptRoot 'Build-GwentBeta.ps1') -Stage 121 -Language $Language -Version $Version -Step $Step -Compiled $Compiled -KegVideo $KegVideo -CheckAI:$CheckAI

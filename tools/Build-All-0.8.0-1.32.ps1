# Five Classic 1.32 voice packages, using the same completed Next-Gen stage.
[CmdletBinding()]
param(
    [string]$Python='python',
    [string]$Version='0.8.0',
    [int]$SourceStage=0,
    [string]$GamePath='D:\GOG Galaxy\Games\The Witcher 3 Wild Hunt',
    [string]$OutputRoot='',
    [switch]$Verify,
    [switch]$CheckOnly
)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@('-X','utf8','tools/classic132/build_all.py','--version',$Version,'--game',$GamePath,'--gui-limit-mib','63')
    if($SourceStage -gt 0){$TaskArguments+=@('--source-stage',[string]$SourceStage)}
    if($OutputRoot){$TaskArguments+=@('--out',$OutputRoot)}
    if($Verify){$TaskArguments+='--verify'}
    if($CheckOnly){$TaskArguments+='--check-only'}
    & $Python @TaskArguments
    if($LASTEXITCODE -ne 0){throw 'Classic 1.32 voice build failed. Inspect the Classic output directory.'}
} finally {Pop-Location}

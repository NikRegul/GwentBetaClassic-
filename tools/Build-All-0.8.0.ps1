# Five Next-Gen voice packages; 13 selectable text languages in every ZIP.
[CmdletBinding()]
param([string]$Python='python',[string]$Version='0.8.0',[int]$Stage=0,[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@('-X','utf8','tools/build_voice_packages168.py','--version',$Version,'--gui-limit-mib','63')
    if($Stage -gt 0){$TaskArguments+=@('--stage',[string]$Stage)}
    if($Verify){$TaskArguments+='--verify'}
    if($CheckOnly){$TaskArguments+='--check-only'}
    & $Python @TaskArguments
    if($LASTEXITCODE -ne 0){throw 'Next-Gen voice build failed. Inspect the source stage logs.'}
} finally {Pop-Location}

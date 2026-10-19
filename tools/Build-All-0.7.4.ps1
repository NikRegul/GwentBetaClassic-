[CmdletBinding()]
param([string]$Python='python',[string]$Version='0.7.4b',[int]$Stage=200,[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@('-X','utf8','tools/build_voice_packages168.py','--version',$Version,'--stage',[string]$Stage)
    if($Verify){$TaskArguments+='--verify'}
    if($CheckOnly){$TaskArguments+='--check-only'}
    & $Python @TaskArguments
    if($LASTEXITCODE -ne 0){throw '0.7.4 voice batch failed. Inspect the selected stage logs.'}
} finally {Pop-Location}

# Five voice packages; every ZIP includes all 13 text languages.
[CmdletBinding()]
param([string]$Python='python',[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@('-X','utf8','tools/build_voice_packages168.py','--version','0.7.3a','--stage','190')
    if($Verify){$TaskArguments+='--verify'}
    if($CheckOnly){$TaskArguments+='--check-only'}
    & $Python @TaskArguments
    if($LASTEXITCODE -ne 0){throw '0.7.3a voice batch failed. Inspect BetaGwent/build/stage190/voice-package-logs.'}
} finally {Pop-Location}

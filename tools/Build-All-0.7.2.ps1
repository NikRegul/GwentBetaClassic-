# All five voices (RU, EN, DE, IT, PT-BR), with 13 text languages in every ZIP.
# Reuses the verified RU 0.7.2 revision; resumes unfinished voice packages.
[CmdletBinding()]
param([string]$Python='python',[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@('-X','utf8','tools/build_voice_packages168.py','--version','0.7.2')
    if($Verify){$TaskArguments+='--verify'}
    if($CheckOnly){$TaskArguments+='--check-only'}
    & $Python @TaskArguments
    if($LASTEXITCODE -ne 0){throw '0.7.2 voice batch failed. Inspect BetaGwent/build/stage*/voice-package-logs.'}
} finally {Pop-Location}

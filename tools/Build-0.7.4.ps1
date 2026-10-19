[CmdletBinding()]
param([string]$Python='python',[string]$Version='0.7.4b',[int]$Stage=0,[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    $TaskArguments=@{Version=$Version;Python=$Python;GuiLimitMiB=63}
    if($Verify -and $Stage -eq 0){
        $TaskStageText=& $Python -c "import json,zipfile,sys;print(json.loads(zipfile.ZipFile('BetaGwent/release/GwentBetaClassic-'+sys.argv[1]+'-RU.zip').read('manifest.json'))['stage'])" $Version
        if($LASTEXITCODE -ne 0){throw 'The selected RU archive is required for verification.'}
        $Stage=[int]$TaskStageText
    }
    if($Stage -gt 0){$TaskArguments.Stage=$Stage}
    if($Verify){$TaskArguments.Verify=$true}
    if($CheckOnly){$TaskArguments.CheckOnly=$true}
    & (Join-Path $PSScriptRoot 'Build-FromSource.ps1') @TaskArguments
    if(-not $?){throw '0.7.4 build failed.'}
} finally {Pop-Location}

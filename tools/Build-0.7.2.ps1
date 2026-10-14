[CmdletBinding()]
param([string]$Python='python',[int]$Stage=0,[switch]$Verify,[switch]$CheckOnly)
$ErrorActionPreference='Stop'
$TaskBuildRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskBuildRoot
try {
    if(-not $Verify -and -not $CheckOnly){
        & $Python -X utf8 tools/ui/build_ui_languages138.py
        if($LASTEXITCODE -ne 0){throw '13-language text/font preparation failed.'}
    }
    $TaskArguments=@{Version='0.7.2';Python=$Python;GuiLimitMiB=65}
    if($Verify -and $Stage -eq 0){
        $TaskStageText=& $Python -c "import json,zipfile;print(json.loads(zipfile.ZipFile('BetaGwent/release/GwentBetaClassic-0.7.2-RU.zip').read('manifest.json'))['stage'])"
        if($LASTEXITCODE -ne 0){throw 'RU 0.7.2 archive is required for verification.'}
        $Stage=[int]$TaskStageText
    }
    if($Stage -gt 0){$TaskArguments.Stage=$Stage}
    if($Verify){$TaskArguments.Verify=$true}
    if($CheckOnly){$TaskArguments.CheckOnly=$true}
    & (Join-Path $PSScriptRoot 'Build-FromSource.ps1') @TaskArguments
    if(-not $?){throw 'RU 0.7.2 build failed.'}
} finally {Pop-Location}

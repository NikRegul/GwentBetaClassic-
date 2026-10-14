[CmdletBinding()]
param([int]$SourceStage=148,[int]$Stage=149,[string]$Python='python')
$ErrorActionPreference='Stop'
$TaskRoot=Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $TaskRoot
try {
    $TaskArchive=Join-Path $TaskRoot 'BetaGwent\release\GwentBetaClassic-0.6.8b-RU.zip'
    if(Test-Path -LiteralPath $TaskArchive){
        & $Python -X utf8 tools/build_from_source.py --verify --version 0.6.8b --stage $Stage
    }else{
        & $Python -X utf8 tools/build_low_memory.py --source-stage $SourceStage --stage $Stage --version 0.6.8b
    }
    if($LASTEXITCODE -ne 0){throw '0.6.8b failed; inspect BetaGwent/build/stage149/logs.'}
} finally { Pop-Location }

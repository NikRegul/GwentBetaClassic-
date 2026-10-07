param(
    [Parameter(Mandatory=$true)][string]$TrainingFolder,
    [int]$Stage=102,
    [string]$Version='0.2.7-ai.1'
)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location -LiteralPath $taskRoot
$trainingLock=$null
function Invoke-AIPython([string[]]$Arguments) {
    & python -X utf8 @Arguments
    if($LASTEXITCODE -ne 0){throw "Build failed with exit code $LASTEXITCODE"}
}
try {
    $lockPath=Join-Path $taskRoot 'BetaGwent/build/ai-training.lock'
    [System.IO.Directory]::CreateDirectory((Split-Path $lockPath -Parent)) | Out-Null
    try {$trainingLock=[System.IO.File]::Open($lockPath,'OpenOrCreate','ReadWrite','None')}
    catch {throw 'Training is still running. Stop it before importing/rebuilding.'}
    if($Stage -lt 101){throw 'Use a new presentation stage, 101 or later.'}
    foreach($relative in @("BetaGwent/build/release$Stage","BetaGwent/build/stage$Stage","BetaGwent/build/board-compile${Stage}ru")) {
        if(Test-Path -LiteralPath (Join-Path $taskRoot $relative)){throw "Stage already exists: $relative. Choose a new -Stage."}
    }
    Invoke-AIPython -Arguments @('tools/ai/import_policy.py',$TrainingFolder)
    Invoke-AIPython -Arguments @('tools/ui/prepare_board_scripts.py')
    Invoke-AIPython -Arguments @('tools/recon/run_redkit_compile.py','--out',"BetaGwent/build/board-compile${Stage}ru",'--patch','BetaGwent/build/board-patch','--timeout','120','--terms-already-accepted')
    $compileResult=Get-Content -LiteralPath (Join-Path $taskRoot "BetaGwent/build/board-compile${Stage}ru/result.json") -Raw | ConvertFrom-Json
    if($compileResult.exitCode -ne 0 -or $compileResult.timedOut -or -not $compileResult.patchSourcesUnchangedDuringCompile){throw 'WitcherScript compilation did not succeed. Read the compiler log before continuing.'}
    if(-not (Test-Path -LiteralPath (Join-Path $taskRoot "BetaGwent/build/board-compile${Stage}ru/compiled/blob.rsblob"))){throw 'Compiler produced no blob.rsblob.'}
    Invoke-AIPython -Arguments @('tools/build_presentation94.py','--stage',"$Stage",'--language','ru')
    Invoke-AIPython -Arguments @('tools/package_presentation94.py','--stage',"$Stage",'--version',$Version,'--language','ru','--compiled',"BetaGwent/build/board-compile${Stage}ru")
    Write-Output (Join-Path $taskRoot "BetaGwent/release/GwentBetaClassic-$Version-RU.zip")
} finally {if($null -ne $trainingLock){$trainingLock.Dispose()};Pop-Location}

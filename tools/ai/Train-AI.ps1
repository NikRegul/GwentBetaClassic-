param([int]$Generations=100,[int]$Seed=924,[int]$Cycles=1,[string]$Output='BetaGwent\training\default',[switch]$Resume,[switch]$Smoke)
$ErrorActionPreference='Stop'
$taskRoot=Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Push-Location -LiteralPath $taskRoot
$trainingLock=$null
try {
    $lockPath=Join-Path $taskRoot 'BetaGwent/build/ai-training.lock'
    [System.IO.Directory]::CreateDirectory((Split-Path $lockPath -Parent)) | Out-Null
    try {$trainingLock=[System.IO.File]::Open($lockPath,'OpenOrCreate','ReadWrite','None')}
    catch {throw 'Another self-play/build run holds the training lock. Stop it before starting a second run.'}
    $taskArgs=@('-X','utf8','tools/ai/train.py','--generations',"$Generations",'--seed',"$Seed",'--cycles',"$Cycles",'--output',$Output)
    if($Resume){$taskArgs+='--resume'}
    if($Smoke){$taskArgs+='--smoke'}
    & python @taskArgs
    if($LASTEXITCODE -ne 0){throw "Self-play exited with code $LASTEXITCODE"}
} finally {if($null -ne $trainingLock){$trainingLock.Dispose()};Pop-Location}

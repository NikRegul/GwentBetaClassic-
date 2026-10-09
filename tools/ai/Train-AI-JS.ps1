# Immutable self-play run; all 46 researched decks, both seats and both model/deck assignments.
param([int]$Generations=30,[int]$Pairs=200,[int]$Strength=4,[int]$Shards=0,[string]$Output='',[switch]$Resume,[switch]$NoFast)
$ErrorActionPreference='Stop'
Set-Location (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)
if ($Pairs -lt 46 -or $Generations -lt 1 -or $Strength -lt 1 -or $Strength -gt 4) { throw 'Pairs >= 46; Generations >= 1; Strength 1..4' }
if (-not $Output) { $Output='BetaGwent\training\js-'+(Get-Date -Format 'yyyy-MM-dd-HHmmss') }
New-Item -ItemType Directory -Force -Path $Output | Out-Null
$Output=(Resolve-Path -LiteralPath $Output).Path
$lock=$null
try {
    $lock=[System.IO.File]::Open((Join-Path $Output 'run.lock'),[System.IO.FileMode]::OpenOrCreate,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
    $snapshot=Join-Path $Output 'snapshot'
    $freezeArgs=@('-X','utf8','tools/ai/snapshot.py',$snapshot)
    if ($Resume) { $freezeArgs+='--resume' }
    & python @freezeArgs
    if ($LASTEXITCODE -ne 0) { throw 'Snapshot verification failed' }
    $nodeArgs=@((Join-Path $snapshot 'train.js'),'--rules',(Join-Path $snapshot 'rules.js'),'--out',$Output,'--generations',"$Generations",'--pairs',"$Pairs",'--strength',"$Strength")
    if ($Shards -gt 0) { $nodeArgs+=@('--shards',"$Shards") }
    if ($Resume) { $nodeArgs+='--resume' }
    Write-Host "Training: $Generations generations, $($Pairs*4) games per set; $Output"
    & node @nodeArgs 2>&1 | Tee-Object -FilePath (Join-Path $Output 'train.log') -Append
    if ($LASTEXITCODE -ne 0) { throw "Training failed with exit $LASTEXITCODE; completed checkpoints remain available" }
} finally { if ($lock) { $lock.Dispose() } }

param(
    [Parameter(Mandatory=$true)][string]$Build,
    [Parameter(Mandatory=$true)][string]$Output,
    [ValidateRange(1,64)][int]$Grids = 16,
    [ValidateRange(1,4)][int]$Workers = 4,
    [switch]$Resume
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Push-Location -LiteralPath $taskRoot
try {
    $taskArgs = @('-X','utf8','tools/ai/launch_classic093_knockout.py','--build',$Build,'--out',$Output,'--grids',"$Grids",'--workers',"$Workers")
    if ($Resume) { $taskArgs += '--resume' }
    & python @taskArgs
    if ($LASTEXITCODE -ne 0) { throw "Tournament launcher exited with code $LASTEXITCODE. Read launch.json and tournament.log before resuming." }
} finally { Pop-Location }

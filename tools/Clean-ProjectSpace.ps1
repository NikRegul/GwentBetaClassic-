#requires -Version 5.1
<#
.SYNOPSIS
Preview or remove selected obsolete outputs in the configured Gwent workspace.
.EXAMPLE
.\tools\Clean-ProjectSpace.ps1
.EXAMPLE
.\tools\Clean-ProjectSpace.ps1 -Apply -WhatIf
.EXAMPLE
.\tools\Clean-ProjectSpace.ps1 -Apply
.EXAMPLE
.\tools\Clean-ProjectSpace.ps1 -Groups OldReleaseDuplicates,DownloadedZips
.NOTES
The default is preview only. -Apply permanently deletes the displayed targets.
Historical build scripts for deleted stages will need their outputs rebuilt.
Sizes are logical bytes; hard links and compression affect actual reclaimed space.
#>
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [string]$ProjectRoot = '',
    [ValidateSet('LegacyBuilds','PremiumExperiments','OldReleaseDuplicates','DownloadedZips')]
    [string[]]$Groups = @('LegacyBuilds','PremiumExperiments'),
    [switch]$Apply
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
}
$taskRoot = [IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\','/')
$taskPrefix = $taskRoot + [IO.Path]::DirectorySeparatorChar
foreach ($required in @('tools','docs','BetaGwent\build','BetaGwent\development','GwentB\myproject1')) {
    if (-not (Test-Path -LiteralPath (Join-Path $taskRoot $required) -PathType Container)) {
        throw "Not a configured project workspace: $taskRoot (missing $required)"
    }
}

function Assert-ProjectPath([string]$Path) {
    $absolute = [IO.Path]::GetFullPath($Path)
    if (-not $absolute.StartsWith($taskPrefix, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Path is outside the project or is its root: $absolute"
    }
    # Check the root and all parents too: a junction can redirect a safe-looking path.
    $part = $absolute
    while ($part) {
        $item = Get-Item -LiteralPath $part -Force -ErrorAction Stop
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing a link/junction: $part"
        }
        $parent = Split-Path -Parent $part
        if ($parent -eq $part) { break }
        $part = $parent
    }
    return $absolute
}

function Test-AllowedTarget([string]$Relative) {
    if ($Relative -match '^BetaGwent\\build\\(?:stage|release)(\d+)$') {
        $number = [int]$Matches[1]
        return ($number -ge 106 -and $number -le 132 -and $Relative -ne 'BetaGwent\build\stage114')
    }
    if ($Relative -match '^BetaGwent\\build\\board-compile(\d+)(?:ru|en)(?:-.+)?$') {
        return ([int]$Matches[1] -ge 106 -and [int]$Matches[1] -le 132)
    }
    if ($Relative -match '^BetaGwent\\build\\premium134-probe-\d{8}-\d{6}$') { return $true }
    return ($Relative -in @(
        'BetaGwent\build\premium-capture\frames134',
        'BetaGwent\release\old',
        'DiyGwent-AITest-Windows-2.1.10-premium.zip',
        'LegacyGwent-2.1.10.zip'
    ))
}

function Get-TreeStats([string]$Path) {
    [long]$bytes = 0
    [long]$files = 0
    $pending = New-Object 'System.Collections.Generic.Stack[string]'
    $pending.Push($Path)
    while ($pending.Count -gt 0) {
        $item = Get-Item -LiteralPath $pending.Pop() -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "Refusing a tree containing a link/junction: $($item.FullName)"
        }
        if ($item.Name -eq '.git') { throw "Refusing a tree containing Git data: $($item.FullName)" }
        if ($item.PSIsContainer) {
            foreach ($child in @(Get-ChildItem -LiteralPath $item.FullName -Force)) {
                $pending.Push($child.FullName)
            }
        } else {
            $bytes += $item.Length
            $files++
        }
    }
    return [pscustomobject]@{ Bytes=$bytes; Files=$files }
}

$targets = New-Object 'System.Collections.Generic.List[object]'
function Add-Target([string]$Relative, [string]$Group) {
    if (-not (Test-AllowedTarget $Relative)) { throw "Target is not allowlisted: $Relative" }
    $path = Join-Path $taskRoot $Relative
    if (-not (Test-Path -LiteralPath $path)) { return }
    $absolute = Assert-ProjectPath $path
    $stats = Get-TreeStats $absolute
    $targets.Add([pscustomobject]@{
        Group=$Group; RelativePath=$Relative; Path=$absolute
        Bytes=$stats.Bytes; GiB=[math]::Round($stats.Bytes / 1GB, 3); Files=$stats.Files
    })
}

# Hold the same exclusive lock as current PowerShell/Python build entry points.
# Opening an existing lock changes no contents. It is intentionally never deleted.
$taskLockPath = Join-Path $taskRoot 'BetaGwent\build\presentation-build.lock'
$taskLock = $null
try {
    $build = Join-Path $taskRoot 'BetaGwent\build'
    $null = Assert-ProjectPath $build
    if (Test-Path -LiteralPath $taskLockPath) { $null = Assert-ProjectPath $taskLockPath }
    try {
        $taskLock = [IO.File]::Open($taskLockPath, [IO.FileMode]::OpenOrCreate,
            [IO.FileAccess]::ReadWrite, [IO.FileShare]::None)
    } catch {
        throw "A build is running or its lock is inaccessible. Try after the build finishes. $($_.Exception.Message)"
    }
    foreach ($group in @($Groups | Select-Object -Unique)) {
        switch ($group) {
            'LegacyBuilds' {
                foreach ($directory in @(Get-ChildItem -LiteralPath $build -Directory -Force)) {
                    $name = $directory.Name
                    if ($name -match '^(stage|release)(\d+)$') {
                        $number = [int]$Matches[2]
                        if ($number -ge 106 -and $number -le 132 -and $name -ne 'stage114') {
                            Add-Target ('BetaGwent\build\' + $name) $group
                        }
                    } elseif ($name -match '^board-compile(\d+)(ru|en)(-.+)?$') {
                        $number = [int]$Matches[1]
                        if ($number -ge 106 -and $number -le 132) {
                            Add-Target ('BetaGwent\build\' + $name) $group
                        }
                    }
                }
            }
            'PremiumExperiments' {
                foreach ($directory in @(Get-ChildItem -LiteralPath $build -Directory -Force)) {
                    if ($directory.Name -match '^premium134-probe-\d{8}-\d{6}$') {
                        Add-Target ('BetaGwent\build\' + $directory.Name) $group
                    }
                }
                Add-Target 'BetaGwent\build\premium-capture\frames134' $group
            }
            'OldReleaseDuplicates' { Add-Target 'BetaGwent\release\old' $group }
            'DownloadedZips' {
                foreach ($name in @('DiyGwent-AITest-Windows-2.1.10-premium','LegacyGwent-2.1.10')) {
                    if (Test-Path -LiteralPath (Join-Path $taskRoot $name) -PathType Container) {
                        Add-Target ($name + '.zip') $group
                    } else {
                        Write-Warning "Keeping $name.zip: extracted original is missing."
                    }
                }
            }
        }
    }
    $plan = @($targets | Sort-Object Bytes -Descending)
    if ($plan.Count -eq 0) { Write-Host 'No matching obsolete outputs found.'; return }
    [long]$total = ($plan | Measure-Object -Property Bytes -Sum).Sum
    $plan | Format-Table Group,GiB,Files,Path -AutoSize | Out-Host
    Write-Host ('TOTAL: {0:N2} GiB in {1} targets (logical size).' -f ($total / 1GB), $plan.Count)
    Write-Host 'Preserved: stage114, stages 133+, current archives, inputs, resource backups, depot and Git.'
    # A plan file is also useful when the console truncates long paths.
    $reportDir = Join-Path $taskRoot 'docs\evidence\cleanup'
    $null = Assert-ProjectPath (Join-Path $taskRoot 'docs\evidence')
    if (Test-Path -LiteralPath $reportDir) { $null = Assert-ProjectPath $reportDir }
    if (-not $WhatIfPreference) {
        $null = New-Item -ItemType Directory -Path $reportDir -Force
        $report = Join-Path $reportDir ('plan-' + (Get-Date -Format 'yyyyMMdd-HHmmss-ffff') + '.csv')
        $plan | Export-Csv -LiteralPath $report -NoTypeInformation -Encoding UTF8
        Write-Host "Plan: $report"
    }
    if (-not $Apply) {
        Write-Host 'PREVIEW ONLY: nothing deleted. Run with -Apply to delete, or -Apply -WhatIf to simulate.'
        return
    }
    foreach ($target in $plan) {
        if (-not (Test-AllowedTarget $target.RelativePath)) { throw 'Target is no longer allowed.' }
        $absolute = Assert-ProjectPath $target.Path
        # Recheck the whole tree immediately before Remove-Item, including nested links.
        $null = Get-TreeStats $absolute
        if ($PSCmdlet.ShouldProcess($absolute, 'Permanently delete obsolete output')) {
            Remove-Item -LiteralPath $absolute -Recurse -Force -ErrorAction Stop
            Write-Host "Deleted: $absolute"
        }
    }
} finally {
    if ($null -ne $taskLock) { $taskLock.Dispose() }
}

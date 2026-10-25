#requires -Version 7.0
[CmdletBinding()]
param([switch]$Apply,[switch]$OldPackages,[string]$Plan='')
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$taskPrefix = $taskRoot.TrimEnd('\') + '\'
$taskTargets = [Collections.Generic.List[object]]::new()
function Assert-Local([string]$Path) {
    $absolute = [IO.Path]::GetFullPath($Path)
    if (-not $absolute.StartsWith($taskPrefix,[StringComparison]::OrdinalIgnoreCase)) { throw "Outside workspace: $absolute" }
    $parent = Split-Path $absolute -Parent
    while ($parent -and $parent.Length -ge $taskRoot.Length) {
        if ((Get-Item -LiteralPath $parent -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked parent: $parent" }
        $parent = Split-Path $parent -Parent
    }
    return $absolute
}
function Scan-Local([string]$Path) {
    $absolute = Assert-Local $Path
    $item = Get-Item -LiteralPath $absolute -Force
    if ($item.Name -eq '.git') { throw "Git data in cleanup: $absolute" }
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { return 0L }
    if (-not $item.PSIsContainer) { return [long]$item.Length }
    [long]$size = 0
    foreach ($child in Get-ChildItem -LiteralPath $absolute -Force) { $size += Scan-Local $child.FullName }
    return $size
}
function Remove-Local([string]$Path) {
    $absolute = Assert-Local $Path
    $item = Get-Item -LiteralPath $absolute -Force
    if ($item.Name -eq '.git') { throw 'Refusing Git data' }
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        # Delete the junction itself; never enumerate its target.
        if ($item.PSIsContainer) { [IO.Directory]::Delete($absolute) } else { [IO.File]::Delete($absolute) }
    } elseif ($item.PSIsContainer) {
        foreach ($child in Get-ChildItem -LiteralPath $absolute -Force) { Remove-Local $child.FullName }
        Remove-Item -LiteralPath $absolute -Force
    } else { Remove-Item -LiteralPath $absolute -Force }
}
if ($Plan) {
    $planPath = Assert-Local $Plan
    if (-not $planPath.StartsWith((Join-Path $taskRoot 'docs\evidence\cleanup091-'),[StringComparison]::OrdinalIgnoreCase)) { throw 'Not a cleanup091 plan' }
    $record = Get-Content -LiteralPath $planPath -Raw | ConvertFrom-Json -AsHashtable
    if ($record.applied) { throw 'Plan already applied' }
    foreach ($target in $record.targets) {
        $absolute = Assert-Local $target.Path
        $relative = [IO.Path]::GetRelativePath($taskRoot,$absolute)
        if ($relative -ne 'tmp\Portable Clean Build' -and $relative -notmatch '^BetaGwent\\build\\release(\d+|082-[a-zA-Z0-9-]+|090-[a-zA-Z0-9-]+)\\package-candidate$') { throw "Not a disposable target: $relative" }
        if ($relative -match 'release090-final17-release') { throw 'Active base release is protected' }
        if ((Scan-Local $absolute) -ne $target.Bytes) { throw "Target changed after audit: $absolute" }
    }
    if ($Apply) {
        $record.applied=$true
        $record.removed=@()
        $journal=$planPath.Replace('.json','-executed.json')
        foreach ($target in $record.targets) {
            Remove-Local $target.Path
            $record.removed+= $target.Path
            $record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $journal -Encoding utf8
            Write-Output "Removed $($target.Path)"
        }
        Write-Output "Cleanup report: $journal"
    } else { $record.targets | Format-Table Path,Bytes -AutoSize }
    return
}
$feedback = Join-Path $taskRoot 'BetaGwent\build\classic132-full-feedback'
if (Test-Path -LiteralPath $feedback) {
    foreach ($capture in Get-ChildItem -LiteralPath $feedback -Directory) {
        foreach ($dump in Get-ChildItem -LiteralPath $capture.FullName -File -Filter '*.dmp') {
            $taskTargets.Add([pscustomobject]@{Path=$dump.FullName;Reason='Raw diagnostic dump; text trace retained';Bytes=(Scan-Local $dump.FullName)})
        }
    }
}
$discard = Join-Path $taskRoot 'tmp\_to_delete'
if (Test-Path -LiteralPath $discard) { $taskTargets.Add([pscustomobject]@{Path=$discard;Reason='Previously discarded intermediates';Bytes=(Scan-Local $discard)}) }
$portable = Join-Path $taskRoot 'tmp\Portable Clean Build'
if (Test-Path -LiteralPath $portable) {
    $mismatch = [Collections.Generic.List[string]]::new()
    foreach ($section in @('source','tools','inputs','documentation','BetaGwent')) {
        $source = Join-Path $taskRoot "CleanBuild\$section"
        $copy = Join-Path $portable $section
        if (-not (Test-Path -LiteralPath $copy)) { continue }
        foreach ($file in Get-ChildItem -LiteralPath $copy -Recurse -File) {
            if ($file.FullName -match '\\(__pycache__|build|node_modules|obj)\\' -or $file.Extension -eq '.pyc') { continue }
            $relative = [IO.Path]::GetRelativePath($copy,$file.FullName)
            $original = Join-Path $source $relative
            if (-not (Test-Path -LiteralPath $original) -or (Get-FileHash -LiteralPath $file.FullName).Hash -ne (Get-FileHash -LiteralPath $original).Hash) { $mismatch.Add($relative) }
        }
    }
    if ($mismatch.Count -eq 0) { $taskTargets.Add([pscustomobject]@{Path=$portable;Reason='Verified duplicate portable kit and generated outputs';Bytes=(Scan-Local $portable)}) }
    else { Write-Warning "Portable copy retained: $($mismatch.Count) differences" }
}
if ($OldPackages) {
    # 0.9.1 consumes final17-release archives and final12 source/audit inputs.
    # Only obsolete packaged copies are removed; source snapshots, compiles,
    # templates, menus and the existing public Git checkout are retained.
    $release = Join-Path $taskRoot 'BetaGwent\release\GwentBetaClassic-0.9.0\release.json'
    $published = Get-Content -LiteralPath $release -Raw | ConvertFrom-Json
    if ($published.source -ne 'release090-final17-release') { throw 'Re-audit active release dependencies before cleanup' }
    foreach ($directory in Get-ChildItem -LiteralPath (Join-Path $taskRoot 'BetaGwent\build') -Directory) {
        if ($directory.Name -notmatch '^release(\d+|082-[a-zA-Z0-9-]+|090-[a-zA-Z0-9-]+)$' -or $directory.Name -eq $published.source) { continue }
        $candidate = Join-Path $directory.FullName 'package-candidate'
        if (Test-Path -LiteralPath $candidate) {
            $taskTargets.Add([pscustomobject]@{Path=$candidate;Reason='Obsolete packaged copies; frozen source/compile inputs retained';Bytes=(Scan-Local $candidate)})
        }
    }
}
$report = Join-Path $taskRoot ('docs\evidence\cleanup091-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$record = [ordered]@{applied=[bool]$Apply;targets=@($taskTargets);bytes=($taskTargets|Measure-Object Bytes -Sum).Sum;removed=@()}
$record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $report -Encoding utf8
$taskTargets | Select-Object Path,Reason,@{Name='GiB';Expression={[math]::Round($_.Bytes/1GB,2)}} | Format-Table -AutoSize
if ($Apply) {
    foreach ($target in $taskTargets) {
        if ((Scan-Local $target.Path) -ne $target.Bytes) { throw "Target changed: $($target.Path)" }
        Remove-Local $target.Path
        $record.removed += $target.Path
        $record | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $report -Encoding utf8
    }
}
Write-Output "Cleanup report: $report"

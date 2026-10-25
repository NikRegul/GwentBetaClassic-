# Remove only generated historical outputs after the permanent-input handoff.
[CmdletBinding()]
param([switch]$Apply)
$ErrorActionPreference='Stop'
Set-StrictMode -Version Latest
$taskRoot=[IO.Path]::GetFullPath((Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))
$buildRoot=Join-Path $taskRoot 'BetaGwent\build'
$proof=Join-Path $buildRoot 'release092-input-handoff'
$inputs=Join-Path $taskRoot 'BetaGwent\build-inputs'
if(!(Test-Path -LiteralPath (Join-Path $inputs 'manifest.json'))){throw 'Missing permanent inputs'}
$release=Get-Content -LiteralPath (Join-Path $proof 'release.json') -Raw | ConvertFrom-Json
if($release.archives.Count -ne 2){throw 'Incomplete handoff build'}
foreach($archive in $release.archives){
    if((Get-FileHash -LiteralPath $archive.path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $archive.sha256){throw 'Handoff archive changed'}
}
$keep=@('release092-input-handoff','release092-decks41','release091g-final2')
$donors=@('universal081','languages137','text137','text138','special-vfx142','element-vfx163','elements164',
    'leader-intros142','leader-intro-resources142','leaders137','leader-loops137','audio109','audio135','audio137','audio141',
    'classic081-geometry-effects-fix14','classic-audio091-split1','history137','history138')
$recordRoot=Join-Path $taskRoot 'BetaGwent\drafts\retired-outputs-20261023'
$null=New-Item -ItemType Directory -Path $recordRoot -Force
$journal=Join-Path $recordRoot 'removed.jsonl'
function Assert-Bounded([string]$path){
    $absolute=[IO.Path]::GetFullPath($path)
    if(!$absolute.StartsWith($buildRoot+'\',[StringComparison]::OrdinalIgnoreCase)){throw "Outside build root: $absolute"}
    $part=$absolute
    while($part){
        $item=Get-Item -LiteralPath $part -Force
        if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Target or parent is a link: $part"}
        $parent=Split-Path -Parent $part
        if($part -eq $parent){break};$part=$parent
    }
    return $absolute
}
function Inspect-Tree([string]$path){
    $stack=[Collections.Generic.Stack[string]]::new();$stack.Push($path)
    [long]$bytes=0;[long]$files=0;[long]$links=0
    while($stack.Count){
        $item=Get-Item -LiteralPath $stack.Pop() -Force
        if($item.Name -in @('.git','.hg','.svn')){throw "Embedded repository: $($item.FullName)"}
        if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){$links++;continue}
        if($item.PSIsContainer){foreach($child in Get-ChildItem -LiteralPath $item.FullName -Force){$stack.Push($child.FullName)}}
        else{$bytes+=$item.Length;$files++}
    }
    return @{bytes=$bytes;files=$files;links=$links}
}
function Remove-NoFollow([string]$path){
    $item=Get-Item -LiteralPath $path -Force
    if($item.Attributes -band [IO.FileAttributes]::ReparsePoint){Remove-Item -LiteralPath $path -Force;return}
    if($item.PSIsContainer){
        foreach($child in Get-ChildItem -LiteralPath $path -Force){Remove-NoFollow $child.FullName}
        Remove-Item -LiteralPath $path -Force
    }else{Remove-Item -LiteralPath $path -Force}
}
$targets=[Collections.Generic.List[string]]::new()
foreach($directory in Get-ChildItem -LiteralPath $buildRoot -Directory -Force){
    $name=$directory.Name
    if($name -in $keep){continue}
    $historical=$name -match '^(?:1?release\d|stage\d|board-compile\d|classic132-0\.8\.0-stage202)'
    if(!$historical -and $name -notin $donors){continue}
    $null=Assert-Bounded $directory.FullName
    # Keep exact rules snapshots and compact validation evidence at their existing paths.
    if($name -match '^release'){
        foreach($child in Get-ChildItem -LiteralPath $directory.FullName -Force){
            if($child.PSIsContainer -and $child.Name -notin @('rules','regressions','checkpoints')){$targets.Add($child.FullName)}
            elseif(!$child.PSIsContainer -and $child.Extension -notin @('.json','.md','.csv','.txt')){$targets.Add($child.FullName)}
        }
    }else{$targets.Add($directory.FullName)}
}
$lock=[IO.File]::Open((Join-Path $buildRoot 'presentation-build.lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
try{
    [long]$total=0;$done=0
    foreach($target in $targets){
        $absolute=Assert-Bounded $target
        $stats=Inspect-Tree $absolute
        # Preserve small top-level manifests of removed stages; no binaries or external links.
        if($Apply){
            $relative=[IO.Path]::GetRelativePath($buildRoot,$absolute)
            $saved=Join-Path $recordRoot $relative
            foreach($item in Get-ChildItem -LiteralPath $absolute -File -Force -ErrorAction SilentlyContinue){
                if($item.Extension -in @('.json','.md','.csv','.txt') -and $item.Length -le 4MB){
                    $null=New-Item -ItemType Directory -Path $saved -Force
                    Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $saved $item.Name)
                }
            }
            Remove-NoFollow $absolute
            if(Test-Path -LiteralPath $absolute){throw "Removal incomplete: $absolute"}
            @{relative=$relative;bytes=$stats.bytes;files=$stats.files;linksUnlinked=$stats.links;time=(Get-Date).ToString('o')} | ConvertTo-Json -Compress | Add-Content -LiteralPath $journal -Encoding utf8
        }
        $total+=$stats.bytes;$done++
        if($done%10 -eq 0){Write-Output ("{0}/{1}: {2:N2} GiB {3}" -f $done,$targets.Count,($total/1GB),$(if($Apply){'removed'}else{'planned'}))}
    }
    Write-Output ("COMPLETE {0}: {1} targets, {2:N2} GiB" -f $(if($Apply){'removed'}else{'preview'}),$done,($total/1GB))
}finally{$lock.Dispose()}

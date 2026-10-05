param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
$assemblyPath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if ((Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Canonical assembly changed' }
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($assemblyPath)
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($type in $assembly.MainModule.Types) {
    if ($type.Name -notin @('FilterCardFactionNode', 'FilterCardLocationTokenNode', 'FilterCardListNode')) { continue }
    foreach ($method in $type.Methods) {
        if (-not $method.HasBody -or $method.Name -notin @('CalculateImpl', 'ExecuteImpl')) { continue }
        $lines.Add('METHOD ' + $method.FullName)
        foreach ($instruction in $method.Body.Instructions) { $lines.Add([string]$instruction) }
    }
}
$lines | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\control63-filters-il.txt') -Encoding utf8
$assembly.Dispose()
Write-Output ('Read canonical control filters: ' + $lines.Count + ' IL lines; original code not executed.')

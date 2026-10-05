param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
$assemblyPath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
if ((Get-FileHash -LiteralPath $assemblyPath -Algorithm SHA256).Hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Canonical assembly changed' }
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($assemblyPath)
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($type in $assembly.MainModule.Types) {
    if ($type.Name -in @('FilterCardLogicNode','FilterDefinitionListNode')) {
        $lines.Add('TYPE ' + $type.FullName)
        foreach ($field in $type.Fields) {
            $lines.Add('FIELD ' + $field.FullName)
            if ($field.Name -eq 'Op') {
                $enumType = $field.FieldType.Resolve()
                foreach ($enumField in $enumType.Fields | Where-Object HasConstant) { $lines.Add('ENUM ' + $enumField.Name + '=' + $enumField.Constant) }
            }
        }
    }
    if ($type.Namespace -ne 'GwentGameplay' -and $type.Name -notin @('FilterCardLogicNode','FilterDefinitionListNode')) { continue }
    foreach ($method in $type.Methods) {
        if (-not $method.HasBody) { continue }
        if (($type.Name -eq 'SummonCardsNode' -and $method.Name -eq 'ExecuteImpl') -or
            ($type.Name -eq 'FilterCardLogicNode') -or
            ($type.Name -eq 'FilterDefinitionListNode') -or
            ($type.Name -eq 'Card' -and $method.Name -eq 'HasLinkedTemplate')) {
            $lines.Add('METHOD ' + $method.FullName)
            foreach ($instruction in $method.Body.Instructions) { $lines.Add([string]$instruction) }
        }
    }
}
$lines | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\crones62-il.txt') -Encoding utf8
$assembly.Dispose()
Write-Output ('Read canonical summon/filter/linked IL: ' + $lines.Count + ' lines; no original game code executed.')

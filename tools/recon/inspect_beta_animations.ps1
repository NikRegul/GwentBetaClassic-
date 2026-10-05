param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$dll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$before = (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($dll)
$names = @('CardBattleViewAnimation','EAnimationType','CardMovementParams','GlobalPreceduralAnimationParams','CardMovementVisualEffect','CardAmbushVisualEffect','CardMovementVFXHandler','CardMovementVFXData','CardPowerIndicatorVisualEffect','CardSpawnVisualEffect','CardDestroyVisualEffect','CardBanishVisualEffect','CardTransformVisualEffect','TweenerWrapper')
$selected = @($assembly.MainModule.Types | Where-Object { $_.Name -in $names })
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($type in $selected) {
    $lines.Add('TYPE '+$type.FullName)
    foreach ($field in $type.Fields) { $lines.Add('FIELD '+$field.FullName); if ($field.HasConstant) { $lines.Add('VALUE '+$field.Constant) } }
    foreach ($method in $type.Methods) {
        $lines.Add('METHOD '+$method.FullName)
        if ($method.HasBody) { foreach ($instruction in $method.Body.Instructions) { $lines.Add([string]$instruction) } }
    }
    foreach ($nested in $type.NestedTypes) { foreach ($field in $nested.Fields) { $lines.Add('NESTED FIELD '+$field.FullName) } }
}
$assembly.Dispose()
if ((Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash -ne $before) { throw 'Original assembly changed' }
$outDir=Join-Path $Workspace 'docs\evidence'
$lines | Set-Content (Join-Path $outDir 'beta-animations80-il.txt') -Encoding utf8
[ordered]@{source=$dll;sha256=$before;sourceUnchanged=$true;types=@($selected | ForEach-Object FullName);lines=$lines.Count;note='Read-only managed IL; serialized Unity curves/materials are not claimed imported into GFx.'} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $outDir 'beta-animations80-source.json') -Encoding utf8
Write-Output ('Extracted '+$selected.Count+' animation types, '+$lines.Count+' IL lines; source unchanged.')

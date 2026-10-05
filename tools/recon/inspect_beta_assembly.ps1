param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
$outDir = Join-Path $Workspace 'docs\evidence'
New-Item -ItemType Directory -Path $outDir -Force | Out-Null
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$dll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($dll)
$types = $assembly.MainModule.Types
$enums = [ordered]@{}
foreach ($type in $types | Where-Object { $_.IsEnum -and $_.Namespace -eq 'GwentGameplay' }) {
    $values = [ordered]@{}
    foreach ($field in $type.Fields | Where-Object HasConstant) { $values[$field.Name] = $field.Constant }
    $enums[$type.FullName] = $values
}
$enums | ConvertTo-Json -Depth 20 | Set-Content (Join-Path $outDir 'beta-enums.json') -Encoding utf8
$core = $types | Where-Object { $_.Namespace -match '^GwentGameplay' }
$metadata = foreach ($type in $core) {
    [ordered]@{type=$type.FullName; base=[string]$type.BaseType; methods=@($type.Methods | ForEach-Object FullName); fields=@($type.Fields | ForEach-Object FullName)}
}
$metadata | ConvertTo-Json -Depth 10 | Set-Content (Join-Path $outDir 'beta-types.json') -Encoding utf8
$names = @('GameController','FiniteStateMachine','ActionManager','AbilityManager','ExecutionStack','PlayStack','RoundManager','RequestManager','TriggerAction','TriggerComparer','InitGameState','DrawCardsGameState','MulliganGameState','ChoosePlayerGameState','RoundStartGameState','TurnStartGameState','TurnGameState','TurnEndGameState','RoundEndGameState','ClearBoardGameState','ResultsGameState','AGameState','BattleDeck','BattleDeckValidator','CardTemplateValidator')
$lines = [System.Collections.Generic.List[string]]::new()
foreach ($type in $types | Where-Object { $_.Name -in $names -or ($_.Namespace -eq 'GwentGameplay' -and $_.Name -match 'Trigger.*Comparer|Comparer.*Trigger') }) {
    $lines.Add('TYPE ' + $type.FullName)
    foreach ($method in $type.Methods) {
        $lines.Add('METHOD ' + $method.FullName)
        if ($method.HasBody) { foreach ($instruction in $method.Body.Instructions) { $lines.Add([string]$instruction) } }
    }
}
$lines | Set-Content (Join-Path $outDir 'beta-core-il.txt') -Encoding utf8
[ordered]@{assembly=$assembly.Name.FullName; source=$dll; sha256=(Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash; gameplayTypes=@($core).Count; ilLines=$lines.Count; note='Static metadata and IL only; game not executed.'} | ConvertTo-Json | Set-Content (Join-Path $outDir 'beta-assembly-summary.json') -Encoding utf8
$assembly.Dispose()
Write-Output ('Saved metadata and IL to ' + $outDir)

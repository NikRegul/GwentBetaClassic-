param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskNames = @('ADeckValidatorRuleSet', 'DefaultDeckValidatorRuleSet', 'ArenaDeckValidatorRuleSet', 'DeckValidator', 'DeckValidatorResult', 'GwentDeckValidator', 'RoundManager', 'ChoosePlayerGameState', 'TurnGameState', 'TurnStartGameState', 'TurnEndGameState', 'RoundEndGameState', 'RoundStartGameState', 'PassAction', 'PassPlayerAction', 'PlayerPassAction')
$taskLines = [System.Collections.Generic.List[string]]::new()
foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.Name -in $taskNames }) {
    $taskLines.Add('TYPE ' + $taskType.FullName)
    foreach ($taskField in $taskType.Fields) {
        $taskLines.Add('FIELD ' + $taskField.FullName + $(if ($taskField.HasConstant) { ' = ' + $taskField.Constant }))
    }
    foreach ($taskMethod in $taskType.Methods) {
        $taskLines.Add('METHOD ' + $taskMethod.FullName)
        if ($taskMethod.HasBody) {
            foreach ($taskInstruction in $taskMethod.Body.Instructions) { $taskLines.Add([string]$taskInstruction) }
        }
    }
}
$taskOut = Join-Path $Workspace 'docs\evidence\beta-legality-rounds-il.txt'
$taskLines | Set-Content -LiteralPath $taskOut -Encoding utf8
[ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash; lines=$taskLines.Count; note='Static IL, not a runtime oracle or proof of every match mode.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-legality-rounds-summary.json') -Encoding utf8
$taskAssembly.Dispose()
Write-Output ('Saved ' + $taskLines.Count + ' IL lines to ' + $taskOut)

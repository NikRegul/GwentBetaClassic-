param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskNames = @('DrawPlayerHandsAction', 'MulliganAction', 'FinishMulliganAction', 'RequestMulliganAction', 'EndGameAction', 'PassAction', 'PlayerPassAction', 'BattleSetupFactory')
$taskSelected = $taskAssembly.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay.Settings' -or $_.Name -in $taskNames }
$taskLines = [System.Collections.Generic.List[string]]::new()
foreach ($taskType in $taskSelected) {
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
$taskOut = Join-Path $Workspace 'docs\evidence\beta-defaults-il.txt'
$taskLines | Set-Content -LiteralPath $taskOut -Encoding utf8
$taskWatchedFields = @('GwentGameplay.Settings.MulliganDefinition::Choices', 'GwentGameplay.Settings.InitialDrawSettings::Mode', 'GwentGameplay.Settings.InitialDrawSettings::Count')
$taskWriterLines = [System.Collections.Generic.List[string]]::new()
function Get-TaskTypes($taskInputTypes) {
    foreach ($taskInputType in $taskInputTypes) {
        $taskInputType
        Get-TaskTypes $taskInputType.NestedTypes
    }
}
foreach ($taskType in Get-TaskTypes $taskAssembly.MainModule.Types) {
    foreach ($taskMethod in $taskType.Methods) {
        if (-not $taskMethod.HasBody) { continue }
        $taskMatches = @($taskMethod.Body.Instructions | Where-Object {
            $_.OpCode.Name -eq 'stfld' -and $_.Operand -and
            ($_.Operand.DeclaringType.FullName + '::' + $_.Operand.Name) -in $taskWatchedFields
        })
        if ($taskMatches.Count -gt 0) {
            $taskWriterLines.Add('METHOD ' + $taskMethod.FullName)
            foreach ($taskInstruction in $taskMethod.Body.Instructions) { $taskWriterLines.Add([string]$taskInstruction) }
        }
    }
}
$taskWriterLines | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-settings-writers-il.txt') -Encoding utf8
[ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash; types=@($taskSelected | ForEach-Object FullName); lines=$taskLines.Count; note='Static IL only, settings may be replaced by caller/network.'} | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $Workspace 'docs\evidence\beta-defaults-summary.json') -Encoding utf8
$taskAssembly.Dispose()
Write-Output ('Saved ' + $taskLines.Count + ' IL lines to ' + $taskOut)

param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
# Cecil reads metadata/IL. The original assembly is never loaded into the CLR.
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskNames = @('AAction','APlayerAction','ARequestAction','AChangeCardsAction`1',
    'ActionManager','AbilityManager','AbilityInstance','PlayedAbilityInstance',
    'TriggerAction','AbilityFlowState','ExecutionStack','ExecutionStackEntry',
    'PutCardInExecutionStackAction','PopCardFromExecutionStackAction','PlayStack',
    'RequestManager','RequestPlayCardAction','PlayCardAction','SelectPlayCardAction','SetCanBePlayedAction',
    'CardDestroyAttackAction','ApplyCardDestroyAttackAction','CardBanishAttackAction',
    'ApplyCardBanishAttackAction','CardResetAttackAction','ApplyCardResetAttackAction',
    'MoveCardsAction','MoveCardAction','SpawnRequest','SpawnCardsAction')
$taskMethods = [System.Collections.Generic.List[object]]::new()
$taskLines = [System.Collections.Generic.List[string]]::new()
$taskCalls = [System.Collections.Generic.List[object]]::new()
foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' }) {
    $taskSelectedMethods = @($taskType.Methods | Where-Object {
        $_.HasBody -and ($taskType.Name -in $taskNames -or $taskType.Name -like '*Trigger*Comparer*' -or
            ($taskType.Name -eq 'Card' -and $_.Name -eq 'Play') -or
            @($_.Body.Instructions | Where-Object { [string]$_.Operand -like '*SetCanBePlayedAction::Init*' }).Count -gt 0)
    })
    if ($taskSelectedMethods.Count -eq 0) { continue }
    $taskLines.Add('TYPE ' + $taskType.FullName + ' BASE ' + $taskType.BaseType)
    foreach ($taskField in $taskType.Fields) { $taskLines.Add('FIELD ' + $taskField.FullName) }
    foreach ($taskMethod in $taskSelectedMethods) {
        $taskLines.Add('METHOD ' + $taskMethod.FullName)
        $taskInstructions = @(foreach ($taskInstruction in $taskMethod.Body.Instructions) {
            $taskLines.Add([string]$taskInstruction)
            $taskBranch = $null
            if ($taskInstruction.Operand -is [Mono.Cecil.Cil.Instruction]) {
                $taskBranch = @($taskInstruction.Operand.Offset)
            } elseif ($taskInstruction.Operand -is [Mono.Cecil.Cil.Instruction[]]) {
                $taskBranch = @($taskInstruction.Operand | ForEach-Object Offset)
            }
            if ($taskInstruction.OpCode.Name -in @('call','callvirt','newobj')) {
                $taskCalls.Add([ordered]@{caller=$taskMethod.FullName; offset=$taskInstruction.Offset;
                    opcode=$taskInstruction.OpCode.Name; callee=[string]$taskInstruction.Operand})
            }
            [ordered]@{offset=$taskInstruction.Offset; opcode=$taskInstruction.OpCode.Name;
                operand=[string]$taskInstruction.Operand; branchOffsets=$taskBranch}
        })
        $taskMethods.Add([ordered]@{type=$taskType.FullName; name=$taskMethod.Name;
            signature=$taskMethod.FullName;
            parameters=@($taskMethod.Parameters | ForEach-Object { [ordered]@{name=$_.Name; type=[string]$_.ParameterType} });
            locals=@($taskMethod.Body.Variables | ForEach-Object { [ordered]@{index=$_.Index; type=[string]$_.VariableType} });
            instructions=$taskInstructions})
    }
}
$taskOut = Join-Path $Workspace 'docs\evidence'
$taskLines | Set-Content -LiteralPath (Join-Path $taskOut 'beta-resolution-il.txt') -Encoding utf8
$taskMethods | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-resolution-methods.json') -Encoding utf8
$taskCalls | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-resolution-calls.json') -Encoding utf8
[ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash;
    methods=$taskMethods.Count; lines=$taskLines.Count; callsites=$taskCalls.Count;
    types=@($taskMethods | ForEach-Object type | Sort-Object -Unique);
    note='Static IL only; no original game code execution or runtime parity claim.'} |
    ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-resolution-summary.json') -Encoding utf8
$taskAssembly.Dispose()
Write-Output ('Read ' + $taskMethods.Count + ' methods, ' + $taskLines.Count + ' IL lines, ' + $taskCalls.Count + ' callsites.')

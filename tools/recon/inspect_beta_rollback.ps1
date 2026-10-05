param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskLines = [System.Collections.Generic.List[string]]::new()
$taskMethods = [System.Collections.Generic.List[object]]::new()
function Get-TaskTypes($taskTypes) {
    foreach ($taskType in $taskTypes) {
        $taskType
        if ($taskType.HasNestedTypes) { Get-TaskTypes $taskType.NestedTypes }
    }
}
try {
    foreach ($taskType in Get-TaskTypes $taskAssembly.MainModule.Types) {
        foreach ($taskMethod in $taskType.Methods | Where-Object HasBody) {
            $taskWanted = $taskType.Namespace -eq 'GwentGameplay' -and (($taskType.Name -eq 'BoardManager' -and $taskMethod.Name -eq 'ReturnToHandOrLeader') -or
                ($taskType.Name -eq 'ExecutionStack' -and $taskMethod.Name -in @('Rollback','HandleRollback')) -or
                ($taskType.Name -eq 'RequestManager' -and $taskMethod.Name -in @('CancelRequest','Remove')) -or
                ($taskType.Name -eq 'ListExt' -and $taskMethod.Name -eq 'AddCards'))
            $taskWanted = $taskWanted -or
                ($taskType.FullName -eq 'GwentVisuals.LocalPlayerTurnHandlerComponent' -and $taskMethod.Name -eq 'HandleExecutionStackOnRollback') -or
                ($taskType.FullName -eq 'GwentVisuals.BattleMovementManager' -and $taskMethod.Name -eq 'HandleRollbackFromExecutionStack')
            $taskCalls = @($taskMethod.Body.Instructions | Where-Object {
                $_.Operand -is [Mono.Cecil.MethodReference] -and
                $_.Operand.DeclaringType.FullName -eq 'GwentGameplay.ExecutionStack' -and
                $_.Operand.Name -eq 'get_OnRollback'
            })
            $taskFields = @($taskMethod.Body.Instructions | Where-Object {
                $_.Operand -is [Mono.Cecil.FieldReference] -and
                $_.Operand.DeclaringType.FullName -eq 'GwentGameplay.ExecutionStack' -and
                $_.Operand.Name -eq 'OnRollback'
            })
            if (!$taskWanted -and !$taskCalls.Count -and !$taskFields.Count) { continue }
            $taskLines.Add('METHOD ' + $taskMethod.FullName)
            $taskInstructions = @(foreach ($taskInstruction in $taskMethod.Body.Instructions) {
                $taskLines.Add([string]$taskInstruction)
                [ordered]@{offset=$taskInstruction.Offset; opcode=$taskInstruction.OpCode.Name; operand=[string]$taskInstruction.Operand}
            })
            $taskMethods.Add([ordered]@{type=$taskType.FullName; name=$taskMethod.Name;
                signature=$taskMethod.FullName; instructions=$taskInstructions})
        }
    }
    $taskOut = Join-Path $Workspace 'docs\evidence'
    $taskLines | Set-Content -LiteralPath (Join-Path $taskOut 'beta-rollback-il.txt') -Encoding utf8
    $taskMethods | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-rollback-methods.json') -Encoding utf8
    [ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash;
        methods=$taskMethods.Count; lines=$taskLines.Count;
        scope='Metadata only: return-to-hand/leader, manager cancel/remove, stack rollback; recursive all-type scan of direct OnRollback accessor/field users. Reflection/external subscribers and whole-game rollback trace not covered.'} |
        ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-rollback-summary.json') -Encoding utf8
    Write-Output ('Read ' + $taskMethods.Count + ' methods, ' + $taskLines.Count + ' IL lines.')
}
finally { $taskAssembly.Dispose() }

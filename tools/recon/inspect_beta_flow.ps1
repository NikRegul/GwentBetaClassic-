param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskFullTypes = @('RoundInfo', 'RoundManager', 'AskPassPlayerAction', 'PassPlayerAction', 'TurnGameState', 'TurnEndGameState', 'TurnStartGameState', 'RoundEndGameState', 'RoundStartGameState', 'ChoosePlayerGameState', 'ClearBoardGameState', 'EndGameAction', 'BattleRestrictions', 'CardPosition')
$taskPlayerMethods = @('get_HasPassed', 'set_HasPassed', 'get_Crowns', 'set_Crowns', 'get_CurrentScore', 'get_Restrictions', 'AskPass', 'AskForfeit', 'OnPass', 'OnRoundStart', 'OnTurnStart', 'OnTurnEnd', 'GetPlayableCardsFromHand', 'NumFreeSlotsInLocation')
$taskManagerMethods = @('CanMakeDecision', 'OnPlayerPassed', 'AllPlayersPassed', 'SetCurrentPlayer', 'GetOpponentPlayerId', 'OnTurnStarted', 'OnTurnEnded')
$taskLines = [System.Collections.Generic.List[string]]::new()
$taskMetadata = [System.Collections.Generic.List[object]]::new()
foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' -and ($_.Name -in $taskFullTypes -or $_.Name -in @('Player', 'PlayerManager')) }) {
    $taskLines.Add('TYPE ' + $taskType.FullName)
    foreach ($taskField in $taskType.Fields) { $taskLines.Add('FIELD ' + $taskField.FullName + $(if ($taskField.HasConstant) { ' = ' + $taskField.Constant })) }
    foreach ($taskMethod in $taskType.Methods) {
        if ($taskType.Name -eq 'Player' -and $taskMethod.Name -notin $taskPlayerMethods) { continue }
        if ($taskType.Name -eq 'PlayerManager' -and $taskMethod.Name -notin $taskManagerMethods) { continue }
        $taskLines.Add('METHOD ' + $taskMethod.FullName)
        $taskParams = @($taskMethod.Parameters | ForEach-Object { [ordered]@{name=$_.Name; type=[string]$_.ParameterType; index=$_.Index} })
        $taskInstructions = @()
        $taskLocals = @()
        if ($taskMethod.HasBody) {
            $taskLocals = @($taskMethod.Body.Variables | ForEach-Object { [ordered]@{index=$_.Index; type=[string]$_.VariableType} })
            $taskLines.Add('LOCALS ' + ($taskLocals | ConvertTo-Json -Compress))
            $taskInstructions = @(foreach ($taskInstruction in $taskMethod.Body.Instructions) {
                $taskLines.Add([string]$taskInstruction)
                $taskOperand = $taskInstruction.Operand
                $taskBranch = $null
                if ($taskOperand -is [Mono.Cecil.Cil.Instruction]) { $taskBranch = @($taskOperand.Offset) }
                elseif ($taskOperand -is [Mono.Cecil.Cil.Instruction[]]) { $taskBranch = @($taskOperand | ForEach-Object Offset) }
                [ordered]@{offset=$taskInstruction.Offset; opcode=$taskInstruction.OpCode.Name; operand=[string]$taskOperand; branchOffsets=$taskBranch}
            })
        }
        $taskMetadata.Add([ordered]@{type=$taskType.FullName; name=$taskMethod.Name; signature=$taskMethod.FullName; parameters=$taskParams; locals=$taskLocals; instructions=$taskInstructions})
    }
}
$taskOut = Join-Path $Workspace 'docs\evidence'
$taskLines | Set-Content -LiteralPath (Join-Path $taskOut 'beta-flow-il.txt') -Encoding utf8
$taskMetadata | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-flow-methods.json') -Encoding utf8
[ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash; methods=$taskMetadata.Count; lines=$taskLines.Count; note='Read-only static IL. No Unity/client code executed; no oracle trace claim.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskOut 'beta-flow-summary.json') -Encoding utf8
$taskAssembly.Dispose()
Write-Output ('Saved ' + $taskLines.Count + ' IL lines, ' + $taskMetadata.Count + ' methods.')

param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$taskDll = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$taskAssembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($taskDll)
$taskNames = @('CancelPlayCardAction','AskCancelRequestAction','CancelRequestAction','RequestPlayCardAction','MersenneTwisterRandom')
$taskMethods = [System.Collections.Generic.List[object]]::new()
$taskLines = [System.Collections.Generic.List[string]]::new()
foreach ($taskType in $taskAssembly.MainModule.Types | Where-Object { $_.Namespace -in @('GwentGameplay','GwentCore') -and $_.Name -in $taskNames }) {
    $taskLines.Add('TYPE ' + $taskType.FullName + ' BASE ' + $taskType.BaseType)
    foreach ($taskField in $taskType.Fields) { $taskLines.Add('FIELD ' + $taskField.FullName) }
    foreach ($taskMethod in $taskType.Methods | Where-Object HasBody) {
        $taskLines.Add('METHOD ' + $taskMethod.FullName)
        $taskInstructions = @(foreach ($taskInstruction in $taskMethod.Body.Instructions) {
            $taskLines.Add([string]$taskInstruction)
            $taskBranch = $null
            if ($taskInstruction.Operand -is [Mono.Cecil.Cil.Instruction]) { $taskBranch = @($taskInstruction.Operand.Offset) }
            elseif ($taskInstruction.Operand -is [Mono.Cecil.Cil.Instruction[]]) { $taskBranch = @($taskInstruction.Operand | ForEach-Object Offset) }
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
$taskLines | Set-Content -LiteralPath (Join-Path $taskOut 'beta-cancel-rng-il.txt') -Encoding utf8
$taskMethods | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-cancel-rng-methods.json') -Encoding utf8
[ordered]@{source=$taskDll; sha256=(Get-FileHash -LiteralPath $taskDll -Algorithm SHA256).Hash;
    methods=$taskMethods.Count; lines=$taskLines.Count;
    types=@($taskMethods | ForEach-Object type | Sort-Object -Unique);
    note='Metadata-only cancellation/play/RNG source extraction. No original executable or rollback/RNG oracle run.'} |
    ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskOut 'beta-cancel-rng-summary.json') -Encoding utf8
$taskAssembly.Dispose()
Write-Output ('Read ' + $taskMethods.Count + ' methods, ' + $taskLines.Count + ' IL lines.')

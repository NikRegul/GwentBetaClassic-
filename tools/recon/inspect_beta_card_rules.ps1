param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$path = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($path)
$selection = @{
    BoardManager = @('GetCardsInLocation','ReturnToHandOrLeader')
    Card = @('Reset','UpdateRuntimeTemplate','Kill','CanBePlayed','CanPlay','get_CanPlay','get_IsPlayable','get_IsLeaderUsed','get_CurrentPower','get_BasePower','get_PermanentPower','get_Armor')
    CardManager = @('MarkAsWaitingToDie','KillWaitingToDie')
    RequestPlayCardAction = @('Init','IsFulfilled','CanPlayCard','HandleFulfilled','SetPlayerPassed')
    CardResetAttackAction = @('PrepareAttack','CreateApplyAction','AfterApplyTriggers')
    CardResetAction = @('ApplyImpl')
    CardData = @('get_CanBePlayed','set_CanBePlayed','get_LeaderUsed','set_LeaderUsed','ClearLeaderState','SetLeaderState')
    CardPower = @('Reset','SetPowerAndArmor','get_BasePower','get_CurrentPower','get_PermanentPower','get_CurrentArmor')
    Location = @('GetCards')
    EnumExtensions = @('Contains')
}
$lines = [System.Collections.Generic.List[string]]::new()
$metadata = [System.Collections.Generic.List[object]]::new()
foreach ($type in $assembly.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' }) {
    foreach ($method in $type.Methods | Where-Object HasBody) {
        $explicit = $selection.ContainsKey($type.Name) -and $method.Name -in $selection[$type.Name]
        $availabilityWriter = @($method.Body.Instructions | Where-Object { [string]$_.Operand -like '*CardData::set_CanBePlayed*' }).Count -gt 0
        if (-not $explicit -and -not $availabilityWriter) { continue }
        $lines.Add('METHOD ' + $method.FullName)
        $params = @($method.Parameters | ForEach-Object { [ordered]@{name=$_.Name; type=[string]$_.ParameterType} })
        $lines.Add('PARAMETERS ' + ($params | ConvertTo-Json -Compress))
        $locals = @($method.Body.Variables | ForEach-Object { [ordered]@{index=$_.Index; type=[string]$_.VariableType} })
        $lines.Add('LOCALS ' + ($locals | ConvertTo-Json -Compress))
        $instructions = @(foreach ($instruction in $method.Body.Instructions) {
            $lines.Add([string]$instruction)
            [ordered]@{offset=$instruction.Offset; opcode=$instruction.OpCode.Name; operand=[string]$instruction.Operand}
        })
        $metadata.Add([ordered]@{signature=$method.FullName; parameters=$params; locals=$locals; instructions=$instructions})
    }
}
$out = Join-Path $Workspace 'docs\evidence'
$lines | Set-Content -LiteralPath (Join-Path $out 'beta-card-rules-il.txt') -Encoding utf8
$metadata | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $out 'beta-card-rules-methods.json') -Encoding utf8
[ordered]@{source=$path; sha256=(Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash; methods=$metadata.Count; lines=$lines.Count; scope='Static IL inspection only. Original code, tests and game not executed.'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $out 'beta-card-rules-summary.json') -Encoding utf8
$assembly.Dispose()
Write-Output ('Read ' + $metadata.Count + ' methods, ' + $lines.Count + ' IL lines.')

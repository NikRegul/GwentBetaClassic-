param([string]$Workspace = 'D:\w3mod')
$ErrorActionPreference = 'Stop'
Add-Type -Path (Join-Path $Workspace 'Gwent 0.9.24.3.432\MelonLoader\Mono.Cecil.dll')
$sourcePath = Join-Path $Workspace 'Gwent 0.9.24.3.432\Gwent_Data\Managed\Assembly-CSharp.dll'
$hash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash
if ($hash -ne '0F77D0B7AC9D00445A47C2921F6E003F7F0AAAB081A47D2F2706A21C10D5B42F') { throw 'Original Beta baseline changed' }
$assembly = [Mono.Cecil.AssemblyDefinition]::ReadAssembly($sourcePath)
$selectedTypes = @($assembly.MainModule.Types | Where-Object {
    $_.Namespace -eq 'GwentGameplay' -and ($_.Name -eq 'CardPower' -or
    ($_.Name -match '(Power|Armor|Boost|Strengthen|Weaken|Damage)' -and $_.Name -match '(Action|Attack)(`[0-9]+)?$'))
})
$methods = @($selectedTypes | ForEach-Object Methods | Where-Object HasBody)
$card = $assembly.MainModule.Types | Where-Object FullName -eq 'GwentGameplay.Card'
$methods += @($card.Methods | Where-Object { $_.Name -in @('CanDie','Kill','get_IsWaitingToDie') -and $_.HasBody })
$records = @(foreach ($method in $methods) {
    $calls = @($method.Body.Instructions | Where-Object { $_.Operand -is [Mono.Cecil.MethodReference] } | ForEach-Object {
        [ordered]@{offset=$_.Offset; opcode=$_.OpCode.Name; target=$_.Operand.FullName}
    })
    [ordered]@{signature=$method.FullName; instructions=$method.Body.Instructions.Count;
        parameters=@($method.Parameters | ForEach-Object { [ordered]@{name=$_.Name; type=$_.ParameterType.FullName} });
        locals=@($method.Body.Variables | ForEach-Object { [ordered]@{index=$_.Index; type=$_.VariableType.FullName} });
        il=@($method.Body.Instructions | ForEach-Object ToString); calls=$calls}
})
$evidence = Join-Path $Workspace 'docs\evidence'
$ilPath = Join-Path $evidence 'beta-power-primitives-il.txt'
$enums = @(foreach ($type in $assembly.MainModule.Types | Where-Object { $_.Namespace -eq 'GwentGameplay' -and $_.IsEnum -and $_.Name -in @('EPowerType','ECardPowerOp','EAttackMethod','EElementType','ECardType') }) {
    [ordered]@{name=$type.FullName; values=@($type.Fields | Where-Object HasConstant | ForEach-Object { [ordered]@{name=$_.Name; value=$_.Constant} })}
})
$text = foreach ($record in $records) {
    'METHOD ' + $record.signature
    $record.il
}
$text | Set-Content -LiteralPath $ilPath -Encoding utf8
[ordered]@{source=$sourcePath; sourceSha256=$hash; originalCodeExecuted=$false;
    types=@($selectedTypes | ForEach-Object FullName); methods=$records; methodCount=$records.Count;
    enums=$enums;
    ilPath=$ilPath; ilSha256=(Get-FileHash -LiteralPath $ilPath -Algorithm SHA256).Hash;
    scope='Read-only IL and call targets for CardPower/power/armor action/attack classes and Card.CanDie/Kill. Static evidence only, not executed fixtures or handler coverage.'} |
    ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $evidence 'beta-power-primitives.json') -Encoding utf8
$assembly.Dispose()
Write-Output "Read-only power primitives: types$($selectedTypes.Count), methods$($records.Count)."
Write-Output ($selectedTypes.FullName -join "`n")

param([string]$Exe,[string]$Platform)
$ErrorActionPreference='Stop'
$taskWorkspace='C:\Users\NikR\Documents\Codex\2026-10-15\new-chat\work'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $taskWorkspace ('installer-test-'+[guid]::NewGuid().ToString('N'))))
if(-not $taskRoot.StartsWith($taskWorkspace+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Test path outside workspace'}
[IO.Directory]::CreateDirectory($taskRoot)|Out-Null
[Reflection.Assembly]::LoadFile($Exe)|Out-Null
$taskCount=0
function Check([bool]$Condition,[string]$Message){if(-not $Condition){throw $Message};$script:taskCount++}
function FakeGame([string]$Path,[int]$Format){
 [IO.Directory]::CreateDirectory((Join-Path $Path 'bin\x64'))|Out-Null
 [IO.File]::WriteAllText((Join-Path $Path 'bin\x64\witcher3.exe'),'test fixture')
 [IO.Directory]::CreateDirectory((Join-Path $Path 'content\content0\bundles'))|Out-Null
 $taskHeader=New-Object byte[] 32
 [Text.Encoding]::ASCII.GetBytes('POTATO70').CopyTo($taskHeader,0)
 [BitConverter]::GetBytes([uint16]$Format).CopyTo($taskHeader,20)
 [IO.File]::WriteAllBytes((Join-Path $Path 'content\content0\bundles\startup.bundle'),$taskHeader)
 [IO.Directory]::CreateDirectory((Join-Path $Path 'bin\config\r4game\user_config_matrix\pc'))|Out-Null
 [IO.File]::WriteAllText((Join-Path $Path 'bin\config\r4game\user_config_matrix\pc\hidden.xml'),'<UserConfig><Group id="Hidden"><VisibleVars><Var id="HasSetup" displayType="TOGGLE" /></VisibleVars></Group></UserConfig>')
 foreach($taskName in @('modBetaGwent0924','modBetaGwentClassic132','modUnrelated')){
  [IO.Directory]::CreateDirectory((Join-Path $Path ('Mods\'+$taskName)))|Out-Null
  [IO.File]::WriteAllText((Join-Path $Path ('Mods\'+$taskName+'\old.txt')),$taskName)
 }
}
try {
 Check ([Installer]::TextChoice('RU') -eq 1) 'Russian text detection'
 Check ([Installer]::VoiceChoice('PL') -eq 2) 'Unsupported speech falls back to English'
 Check ([Installer]::VoiceChoice('BR') -eq 5) 'Brazilian Portuguese speech detection'
 $taskGame=Join-Path $taskRoot 'Game';$taskFormat=if($Platform -eq '1.32'){3}else{5};FakeGame $taskGame $taskFormat
 Check ([Installer]::IsGame($taskGame,$Platform)) 'Matching resource format detected'
 $taskOther=if($Platform -eq '1.32'){'5.0+'}else{'1.32'}
 Check (-not [Installer]::IsGame($taskGame,$taskOther)) 'Wrong platform rejected'
 $taskSettings=Join-Path $taskRoot 'user.settings';[IO.File]::WriteAllText($taskSettings,"[Localization]`r`nTextLanguage=RU`r`nSpeechLanguage=PL`r`n[Other]`r`nKeep=123`r`n")
 $taskBackup=[Installer]::Install($taskGame,$taskSettings,3,4,$null)
 Check ([IO.File]::Exists((Join-Path $taskBackup 'Mods\modBetaGwent0924\old.txt'))) 'Old Next-Gen mod backed up'
 Check ([IO.File]::Exists((Join-Path $taskBackup 'Mods\modBetaGwentClassic132\old.txt'))) 'Old Classic mod backed up'
 Check ([IO.File]::ReadAllText((Join-Path $taskGame 'Mods\modUnrelated\old.txt')) -eq 'modUnrelated') 'Unrelated mod preserved'
 $taskPackage=[Installer]::ReadPackage();$taskSelected=Join-Path $taskGame ('Mods\'+$taskPackage.ModFolder)
 Check ([IO.File]::Exists((Join-Path $taskSelected 'content\soundspc.cache'))) 'All-language sound cache installed'
 $taskConfig=[IO.File]::ReadAllText($taskSettings)
 Check ($taskConfig.Contains('TextLanguage=RU') -and $taskConfig.Contains('SpeechLanguage=PL') -and $taskConfig.Contains('Keep=123')) 'Original game settings preserved'
 Check ($taskConfig.Contains('[Hidden]') -and $taskConfig.Contains('BetaGwentTextLanguage=3') -and $taskConfig.Contains('BetaGwentVoiceLanguage=4')) 'Independent mod defaults written'
 $taskHidden=[xml][IO.File]::ReadAllText((Join-Path $taskGame 'bin\config\r4game\user_config_matrix\pc\hidden.xml'))
 Check ($taskHidden.SelectNodes('//Var').Count -eq 3) 'Two defaults registered without removing native variables'
 Check ([IO.File]::ReadAllText((Join-Path $taskBackup 'Config\hidden.xml')).Contains('HasSetup')) 'Native configuration backed up'
 Check ([IO.File]::Exists((Join-Path $taskGame 'BetaGwentDocs\InstallReport.json'))) 'Install report created'
 $taskSecond=[Installer]::Install($taskGame,$taskSettings,0,0,$null)
 Check ([IO.File]::Exists((Join-Path $taskSecond ('Mods\'+$taskPackage.ModFolder+'\content\soundspc.cache')))) 'Update backs up previous installation'
 Check ([IO.File]::Exists((Join-Path $taskSelected 'content\soundspc.cache'))) 'Update installs verified replacement'
 $taskFailureGame=Join-Path $taskRoot 'FailedGame';FakeGame $taskFailureGame $taskFormat
 $taskBadSettings=Join-Path $taskRoot 'settings-is-a-directory';[IO.Directory]::CreateDirectory($taskBadSettings)|Out-Null
 $taskFailed=$false
 try{[Installer]::Install($taskFailureGame,$taskBadSettings,0,0,$null)|Out-Null}catch{$taskFailed=$true}
 Check $taskFailed 'Settings write failure reported'
 Check (-not [IO.File]::ReadAllText((Join-Path $taskFailureGame 'bin\config\r4game\user_config_matrix\pc\hidden.xml')).Contains('BetaGwentTextLanguage')) 'Configuration restored after failure'
 foreach($taskName in @('modBetaGwent0924','modBetaGwentClassic132','modUnrelated')){
  Check ([IO.File]::ReadAllText((Join-Path $taskFailureGame ('Mods\'+$taskName+'\old.txt'))) -eq $taskName) ('Rollback preserves '+$taskName)
 }
 Write-Output ('{"platform":"'+$Platform+'","checks":'+$taskCount+',"installerVerified":true,"realGameModified":false}')
} finally {
 $taskResolved=[IO.Path]::GetFullPath($taskRoot)
 if($taskResolved.StartsWith($taskWorkspace+'\installer-test-',[StringComparison]::OrdinalIgnoreCase) -and [IO.Directory]::Exists($taskResolved)){Remove-Item -LiteralPath $taskResolved -Recurse -Force}
}

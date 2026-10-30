# Liga o clone como tarefa do Windows: abre ao logar e às 7h50 (acordando o PC se estiver suspenso).
# Rodar uma vez, no PowerShell, a partir da pasta ARVEX:  powershell -ExecutionPolicy Bypass -File tools\maquina\clone\instalar-tarefa.ps1
# Para desligar:  Unregister-ScheduledTask -TaskName "ARVEX Clone - grupos" -Confirm:$false
$raiz = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$py = "$env:LOCALAPPDATA\Programs\Python\Python312\pythonw.exe"
$acao = New-ScheduledTaskAction -Execute $py -Argument "tools\maquina\clone\clone.py" -WorkingDirectory $raiz
$aoLogar = New-ScheduledTaskTrigger -AtLogOn -User "$env:USERDOMAIN\$env:USERNAME"
$cedo = New-ScheduledTaskTrigger -Daily -At "07:50"
$cfg = New-ScheduledTaskSettingsSet -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit 0 -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName "ARVEX Clone - grupos" -Action $acao -Trigger $aoLogar, $cedo -Settings $cfg `
    -Description "Clone do Vitor nos grupos de WhatsApp (tools/maquina/clone)" -Force | Out-Null
Start-ScheduledTask -TaskName "ARVEX Clone - grupos"
Write-Host "Clone ligado. Log: tools\maquina\clone\clone.log"

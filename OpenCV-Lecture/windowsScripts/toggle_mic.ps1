$mic = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*Microphone*" }
if ($mic.Status -eq "OK") {
    Disable-PnpDevice -InstanceId $mic.InstanceId -Confirm:$false
    Write-Host "Microphone Muted"
} else {
    Enable-PnpDevice -InstanceId $mic.InstanceId -Confirm:$false
    Write-Host "Microphone Unmuted"
}

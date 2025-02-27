# Get all devices with "Microphone" in the friendly name.
$micDevices = Get-PnpDevice | Where-Object { $_.FriendlyName -like "*Microphone*" }

# Check if any microphone device is found.
if (-not $micDevices) {
    Write-Host "No microphone device found."
    return
}

# Iterate over each microphone device.
foreach ($mic in $micDevices) {
    if ($mic.Status -eq "OK") {
        Disable-PnpDevice -InstanceId $mic.InstanceId -Confirm:$false
        Write-Host "$($mic.FriendlyName) Muted"
    } else {
        Enable-PnpDevice -InstanceId $mic.InstanceId -Confirm:$false
        Write-Host "$($mic.FriendlyName) Unmuted"
    }
}

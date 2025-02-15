$RegPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
$CurrentMode = Get-ItemProperty -Path $RegPath -Name AppsUseLightTheme | Select-Object -ExpandProperty AppsUseLightTheme

If ($CurrentMode -eq 1) {
    Set-ItemProperty -Path $RegPath -Name AppsUseLightTheme -Value 0
    Set-ItemProperty -Path $RegPath -Name SystemUsesLightTheme -Value 0
    Write-Host "Switched to Dark Mode"
} Else {
    Set-ItemProperty -Path $RegPath -Name AppsUseLightTheme -Value 1
    Set-ItemProperty -Path $RegPath -Name SystemUsesLightTheme -Value 1
    Write-Host "Switched to Light Mode"
}

@echo off
set /p SSID="Enter Wi-Fi Name: "
set /p PASSWORD="Enter Password: "
netsh wlan connect name=%SSID% key=%PASSWORD%
echo Connected to %SSID%
pause

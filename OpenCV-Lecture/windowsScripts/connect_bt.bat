@echo off

REM Path to NirSoft's BluetoothCL
set BTCL_PATH=C:\Users\domdd\Documents\Github\SHPE-Tech\OpenCV-Lecture\BluetoothCL\BluetoothCL.exe

REM Your device's MAC address
set DEVICE_MAC=7c:c1:80:26:84:6a

echo Connecting to Bluetooth device %DEVICE_MAC%...

REM /connect attempts an immediate connection without opening Bluetooth UI
"%BTCL_PATH%" /connect AA Caribbean Cinemas Surroundsound -timeout 30

echo Done.

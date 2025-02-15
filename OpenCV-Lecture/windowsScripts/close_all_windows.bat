@echo off
echo Closing all open windows...
taskkill /F /FI "USERNAME eq %USERNAME%" /FI "IMAGENAME ne explorer.exe"
echo All windows closed.
pause

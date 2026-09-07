@echo off
REM ASTERIX OS Master Command Dispatcher (Windows Batch Entrypoint)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0ax.ps1" %*

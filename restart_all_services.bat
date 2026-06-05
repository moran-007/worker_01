@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart_all_services.ps1"
pause

@echo off
cd /d "%~dp0"
echo Starting class attendance system...
echo Local: http://127.0.0.1:8000
echo LAN:   http://your-computer-ip:8000
py -3.11 app.py

$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

$python = "py"
$args = @("-3.11", "app.py")

Write-Host "Starting class attendance system..."
Write-Host "Local: http://127.0.0.1:8000"
Write-Host "LAN:   http://<your-computer-ip>:8000"

& $python @args

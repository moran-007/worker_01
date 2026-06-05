$ErrorActionPreference = "Stop"
Set-Location -Path (Join-Path $PSScriptRoot "frontend")

Write-Host "Starting Vue3 + Element Plus frontend..."
Write-Host "Local: http://127.0.0.1:5173"

npm run dev

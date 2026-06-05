$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$MainApp = Join-Path $Root "app"
$MainFrontend = Join-Path $MainApp "frontend"
$OjRoot = Join-Path (Split-Path -Parent $Root) "OJ_text"
$LogDir = Join-Path $Root "runtime_logs"

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$Ports = @(8000, 5173, 3000, 5174, 8601)

function Stop-PortProcess {
    param([int]$Port)

    $connections = Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($connection in $connections) {
        $processId = $connection.OwningProcess
        if (-not $processId -or $processId -eq 0) {
            continue
        }

        try {
            $process = Get-Process -Id $processId -ErrorAction Stop
            Write-Host "Stopping port $Port process $processId ($($process.ProcessName))"
            Stop-Process -Id $processId -Force -ErrorAction Stop
        }
        catch {
            Write-Host "Port $Port process $processId already stopped or inaccessible"
        }
    }
}

function Start-LoggedProcess {
    param(
        [string]$Name,
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$OutFile,
        [string]$ErrFile
    )

    if (-not (Test-Path $WorkingDirectory)) {
        Write-Host "Skipping $Name, missing directory: $WorkingDirectory"
        return $null
    }

    Write-Host "Starting $Name"
    return Start-Process `
        -FilePath $FilePath `
        -ArgumentList $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -RedirectStandardOutput $OutFile `
        -RedirectStandardError $ErrFile `
        -WindowStyle Hidden `
        -PassThru
}

function Wait-Url {
    param(
        [string]$Label,
        [string]$Url,
        [int]$Seconds = 60
    )

    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                Write-Host "$Label ready: $Url"
                return $true
            }
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }

    Write-Host "$Label not ready after ${Seconds}s: $Url"
    return $false
}

Write-Host "Stopping occupied service ports..."
foreach ($port in $Ports) {
    Stop-PortProcess -Port $port
}

Start-Sleep -Seconds 2

$processes = @()

$processes += Start-LoggedProcess `
    -Name "Class Worker API" `
    -FilePath "python" `
    -Arguments @("app.py") `
    -WorkingDirectory $MainApp `
    -OutFile (Join-Path $LogDir "class-worker-api.8000.out.log") `
    -ErrFile (Join-Path $LogDir "class-worker-api.8000.err.log")

$processes += Start-LoggedProcess `
    -Name "Class Worker Vue" `
    -FilePath "npm.cmd" `
    -Arguments @("run", "dev", "--", "--host", "127.0.0.1", "--port", "5173") `
    -WorkingDirectory $MainFrontend `
    -OutFile (Join-Path $LogDir "class-worker-vue.5173.out.log") `
    -ErrFile (Join-Path $LogDir "class-worker-vue.5173.err.log")

if (Test-Path $OjRoot) {
    $processes += Start-LoggedProcess `
        -Name "OJ_text Backend" `
        -FilePath "npm.cmd" `
        -Arguments @("run", "dev", "-w", "backend") `
        -WorkingDirectory $OjRoot `
        -OutFile (Join-Path $LogDir "oj-backend.3000.out.log") `
        -ErrFile (Join-Path $LogDir "oj-backend.3000.err.log")

    $processes += Start-LoggedProcess `
        -Name "OJ_text Frontend" `
        -FilePath "npm.cmd" `
        -Arguments @("run", "dev", "-w", "frontend", "--", "--host", "127.0.0.1", "--port", "5174") `
        -WorkingDirectory $OjRoot `
        -OutFile (Join-Path $LogDir "oj-frontend.5174.out.log") `
        -ErrFile (Join-Path $LogDir "oj-frontend.5174.err.log")

    $processes += Start-LoggedProcess `
        -Name "Scratch GUI" `
        -FilePath "npm.cmd" `
        -Arguments @("run", "dev:scratch-gui") `
        -WorkingDirectory $OjRoot `
        -OutFile (Join-Path $LogDir "scratch-gui.8601.out.log") `
        -ErrFile (Join-Path $LogDir "scratch-gui.8601.err.log")
}
else {
    Write-Host "OJ_text directory not found, skipped OJ/Scratch services: $OjRoot"
}

Write-Host ""
Write-Host "Waiting for services..."
Wait-Url -Label "Class Worker API" -Url "http://127.0.0.1:8000/" -Seconds 90 | Out-Null
Wait-Url -Label "Class Worker Vue" -Url "http://127.0.0.1:5173/login" -Seconds 90 | Out-Null
Wait-Url -Label "OJ_text Backend" -Url "http://127.0.0.1:3000/health" -Seconds 90 | Out-Null
Wait-Url -Label "OJ_text Frontend" -Url "http://127.0.0.1:5174/" -Seconds 90 | Out-Null
Wait-Url -Label "Scratch GUI" -Url "http://127.0.0.1:8601/" -Seconds 90 | Out-Null

Write-Host ""
Write-Host "Local services have been requested. Logs are in: $LogDir"
Write-Host "Main entry: http://127.0.0.1:8000/"

Start-Process "http://127.0.0.1:8000/"

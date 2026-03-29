# Check Point VPN Service Manager
# Commands: stop, start, restart
# No command shows current status and usage

param(
    [Parameter(Position = 0)]
    [ValidateSet("stop", "start", "restart", "")]
    [string]$Command = ""
)

$ServiceNames = @("TracSrvWrapper", "EPWD")
$TrGUIPath = "C:\Program Files (x86)\CheckPoint\Endpoint Connect\TrGUI.exe"

# Check if required services exist
foreach ($svc in $ServiceNames) {
    if (-not (Get-Service -Name $svc -ErrorAction SilentlyContinue)) {
        Write-Warning "$svc service not found. Is Check Point VPN installed?"
        exit 1
    }
}

function Get-VpnStatus {
    $trac = Get-Service -Name "TracSrvWrapper"
    $epwd = Get-Service -Name "EPWD"
    return @{ TracSrvWrapper = $trac.Status; EPWD = $epwd.Status }
}

function Stop-Vpn {
    Write-Host "Stopping Check Point VPN services..." -ForegroundColor Yellow
    try {
        Stop-Service -Name "EPWD" -Force -ErrorAction Stop
        Stop-Service -Name "TracSrvWrapper" -Force -ErrorAction Stop
        Start-Process "taskkill" -ArgumentList "/f", "/im", "TrGUI.exe" -ErrorAction SilentlyContinue
        Write-Host "✓ Check Point VPN stopped" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to stop VPN services: $($_.Exception.Message)"
        exit 1
    }
}

function Start-Vpn {
    Write-Host "Starting Check Point VPN services..." -ForegroundColor Yellow
    try {
        Start-Service -Name "TracSrvWrapper" -ErrorAction Stop
        Start-Service -Name "EPWD" -ErrorAction Stop
        Start-Process $TrGUIPath
        Write-Host "✓ Check Point VPN started" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to start VPN services: $($_.Exception.Message)"
        exit 1
    }
}

switch ($Command) {
    "stop" {
        Stop-Vpn
    }
    "start" {
        Start-Vpn
    }
    "restart" {
        Stop-Vpn
        Start-Vpn
    }
    default {
        $status = Get-VpnStatus
        Write-Host "=== Check Point VPN Status ===" -ForegroundColor Cyan
        Write-Host "  TracSrvWrapper: $($status.TracSrvWrapper)"
        Write-Host "  EPWD:           $($status.EPWD)"
        Write-Host ""
        Write-Host "Usage: checkpoint-vpn-service-toggle.ps1 <stop|start|restart>" -ForegroundColor Gray
    }
}

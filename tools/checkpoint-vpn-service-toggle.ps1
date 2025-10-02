# Check Point VPN Service Toggle
# Toggles Check Point VPN services on/off with proper error handling

Write-Host "=== Check Point VPN Service Toggle ===" -ForegroundColor Cyan

# Check if required services exist
$tracService = Get-Service -Name "TracSrvWrapper" -ErrorAction SilentlyContinue
$epwdService = Get-Service -Name "EPWD" -ErrorAction SilentlyContinue

if (-not $tracService) {
   Write-Warning "TracSrvWrapper service not found. Is Check Point VPN installed?"
   exit 1
}

if (-not $epwdService) {
   Write-Warning "EPWD service not found. Is Check Point VPN installed?"
   exit 1
}

try {
   $currentStatus = $tracService.Status

   if ($currentStatus -eq "Running") {
       Write-Host "Stopping Check Point VPN services..." -ForegroundColor Yellow

       # Stop services in correct order
       Stop-Service -Name "EPWD" -Force -ErrorAction Stop
       Stop-Service -Name "TracSrvWrapper" -Force -ErrorAction Stop

       # Verify services stopped
       $tracService = Get-Service -Name "TracSrvWrapper"
       if ($tracService.Status -eq "Stopped") {
           Write-Host "✓ Check Point VPN services stopped successfully" -ForegroundColor Green
       } else {
           Write-Warning "Failed to stop TracSrvWrapper service"
       }
   } else {
       Write-Host "Starting Check Point VPN services..." -ForegroundColor Yellow

       # Start services in correct order
       Start-Service -Name "TracSrvWrapper" -ErrorAction Stop
       Start-Service -Name "EPWD" -ErrorAction Stop

       # Verify services started
       $tracService = Get-Service -Name "TracSrvWrapper"
       if ($tracService.Status -eq "Running") {
           Write-Host "✓ Check Point VPN services started successfully" -ForegroundColor Green
       } else {
           Write-Warning "Failed to start TracSrvWrapper service"
       }
   }
}
catch {
   Write-Error "Error managing Check Point VPN services: $($_.Exception.Message)"
   exit 1
}

Write-Host "=== Done ===" -ForegroundColor Cyan

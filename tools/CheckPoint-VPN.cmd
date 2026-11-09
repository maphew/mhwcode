@echo off
setlocal

REM Double-click launcher for Check Point VPN GUI
REM If PowerShell is blocked, right-click and Run as administrator or adjust execution policy.

set "SCRIPT=%~dp0checkpoint-vpn-service-toggle.ps1"

if not exist "%SCRIPT%" (
  echo Could not find checkpoint-vpn-service-toggle.ps1 next to this launcher.
  echo Expected: "%SCRIPT%"
  pause
  exit /b 1
)

REM Try PowerShell 7 first, fall back to Windows PowerShell
where pwsh >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%SCRIPT%" -Gui
  exit /b %ERRORLEVEL%
)

powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File "%SCRIPT%" -Gui
exit /b %ERRORLEVEL%

# Check Point VPN Service Manager
#
# Commands (positional, non-interactive):
#   start     Start TracSrvWrapper, EPWD, and the tray UI
#   stop      Stop EPWD, TracSrvWrapper, and the tray UI
#   restart   Stop then start
#   toggle    Stop when both services are running, otherwise start
#   (none)    Show status and prompt
#   help      Show this help
#
# Options:
#   -Install              Copy the script to a directory already on PATH and
#                         put a "Check Point VPN Toggle" shortcut on the desktop
#   -Uninstall            Remove the PATH copy and the desktop shortcut
#   -Notify               Show a tray balloon with the result (used by the shortcut)
#   -ShortcutPath <path>  Override the shortcut location (default: Desktop)
#   -Help                 Show this help
#
# Examples:
#   .\checkpoint-vpn-service-toggle.ps1 toggle
#   .\checkpoint-vpn-service-toggle.ps1 -Install
#   .\checkpoint-vpn-service-toggle.ps1 -Uninstall

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("stop", "start", "restart", "toggle", "help", "")]
    [string]$Command = "",

    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Help,
    [switch]$Notify,

    [string]$ShortcutPath
)

$ServiceNames = @("TracSrvWrapper", "EPWD")
$TrGUIPath = "C:\Program Files (x86)\CheckPoint\Endpoint Connect\TrGUI.exe"
$ShortcutName = "Check Point VPN Toggle.lnk"
$IconDir = Join-Path $env:LOCALAPPDATA "CheckPointVpnToggle"
$IconFile = Join-Path $IconDir "checkpoint-vpn.ico"
$StateFile = Join-Path $IconDir "install.json"
$ScriptFileName = "checkpoint-vpn.ps1"
$CmdName = "checkpoint-vpn"

function Show-Usage {
    @'
Check Point VPN Service Manager

Usage:
  checkpoint-vpn.ps1 [start|stop|restart|toggle]
  checkpoint-vpn.ps1 -Install [-ShortcutPath <path>]
  checkpoint-vpn.ps1 -Uninstall
  checkpoint-vpn.ps1 -Help

Commands:
  start     Start TracSrvWrapper, EPWD, and the tray UI
  stop      Stop EPWD, TracSrvWrapper, and the tray UI
  restart   Stop then start
  toggle    Stop when both services are running, otherwise start
  (none)    Show status and prompt
  help      Show this help

Options:
  -Install              Copy the script to a directory already on PATH and
                        put a "Check Point VPN Toggle" shortcut on the desktop
  -Uninstall            Remove the PATH copy and the desktop shortcut
  -Notify               Show a tray balloon with the result
  -ShortcutPath <path>  Override the shortcut location (default: Desktop)
  -Help                 Show this help

Examples:
  checkpoint-vpn toggle
  checkpoint-vpn -Install
  checkpoint-vpn -Uninstall
'@ | Write-Host
}

function Assert-Services {
    $missing = @($ServiceNames | Where-Object { -not (Get-Service -Name $_ -ErrorAction SilentlyContinue) })
    if ($missing.Count -gt 0) {
        throw "Service not found: $($missing -join ', '). Is Check Point VPN installed?"
    }
}

function Get-VpnStatus {
    $status = [ordered]@{}
    foreach ($svc in $ServiceNames) {
        $service = Get-Service -Name $svc -ErrorAction SilentlyContinue
        $status[$svc] = if ($service) { $service.Status } else { "NotInstalled" }
    }
    $status.BothRunning = ($status["TracSrvWrapper"] -eq "Running" -and $status["EPWD"] -eq "Running")
    return [pscustomobject]$status
}

function Stop-Vpn {
    Assert-Services
    Write-Host "Stopping Check Point VPN..." -ForegroundColor Yellow
    $status = Get-VpnStatus
    if ($status.EPWD -ne "Stopped") {
        Stop-Service -Name "EPWD" -Force -ErrorAction Stop
    }
    if ($status.TracSrvWrapper -ne "Stopped") {
        Stop-Service -Name "TracSrvWrapper" -Force -ErrorAction Stop
    }
    Get-Process -Name "TrGUI" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "Check Point VPN stopped" -ForegroundColor Green
}

function Start-Vpn {
    Assert-Services
    Write-Host "Starting Check Point VPN..." -ForegroundColor Yellow
    $status = Get-VpnStatus
    if ($status.TracSrvWrapper -ne "Running") {
        Start-Service -Name "TracSrvWrapper" -ErrorAction Stop
    }
    if ($status.EPWD -ne "Running") {
        Start-Service -Name "EPWD" -ErrorAction Stop
    }
    if ((Test-Path -LiteralPath $TrGUIPath) -and -not (Get-Process -Name "TrGUI" -ErrorAction SilentlyContinue)) {
        Start-Process -FilePath $TrGUIPath
    }
    Write-Host "Check Point VPN started" -ForegroundColor Green
}

function Select-VpnAction {
    $status = Get-VpnStatus
    Write-Host "=== Check Point VPN Status ===" -ForegroundColor Cyan
    Write-Host "  TracSrvWrapper: $($status.TracSrvWrapper)"
    Write-Host "  EPWD:           $($status.EPWD)"
    Write-Host ""

    $choices = @(
        [System.Management.Automation.Host.ChoiceDescription]::new("&Start", "Start the Check Point VPN services")
        [System.Management.Automation.Host.ChoiceDescription]::new("S&top", "Stop the Check Point VPN services")
    )
    $defaultChoice = if ($status.BothRunning) { 1 } else { 0 }
    $selection = $Host.UI.PromptForChoice(
        "Check Point VPN",
        "Choose an action:",
        $choices,
        $defaultChoice
    )

    if ($selection -eq 0) { return "start" }
    return "stop"
}

function Invoke-Action {
    param([string]$Action)

    switch ($Action) {
        "stop" {
            Stop-Vpn
            return "stopped"
        }
        "start" {
            Start-Vpn
            return "started"
        }
        "restart" {
            Stop-Vpn
            Start-Vpn
            return "restarted"
        }
        "toggle" {
            if ((Get-VpnStatus).BothRunning) {
                Stop-Vpn
                return "stopped"
            }
            Start-Vpn
            return "started"
        }
        default {
            throw "Unknown action: $Action"
        }
    }
}

function Test-DirectoryWritable {
    param([string]$Path)

    try {
        $probe = Join-Path $Path (".checkpoint-vpn-write-test-" + [guid]::NewGuid().ToString("N") + ".tmp")
        [System.IO.File]::WriteAllText($probe, "")
        [System.IO.File]::Delete($probe)
        return $true
    }
    catch {
        return $false
    }
}

function Get-SearchPathDirectories {
    $entries = @()
    $machinePath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($machinePath) { $entries += $machinePath -split ";" }
    if ($userPath) { $entries += $userPath -split ";" }
    if ($entries.Count -eq 0) { $entries = $env:PATH -split ";" }

    $seen = @{}
    $dirs = @()
    foreach ($entry in $entries) {
        $dir = $entry.Trim().Trim('"').TrimEnd('\')
        if (-not $dir) { continue }
        $key = $dir.ToLowerInvariant()
        if ($seen.ContainsKey($key)) { continue }
        $seen[$key] = $true
        if (Test-Path -LiteralPath $dir -PathType Container) {
            $dirs += $dir
        }
    }
    return $dirs
}

function Get-VpnInstallDir {
    $pathDirs = @(Get-SearchPathDirectories)

    $preferred = @(
        (Join-Path $env:USERPROFILE ".local\bin"),
        (Join-Path $env:LOCALAPPDATA "Microsoft\WindowsApps")
    )
    foreach ($candidate in $preferred) {
        $match = $pathDirs | Where-Object { $_.TrimEnd('\') -ieq $candidate.TrimEnd('\') } | Select-Object -First 1
        if ($match -and (Test-DirectoryWritable -Path $match)) {
            return $match
        }
    }

    # Fall back to a user-owned PATH directory, then any writable PATH directory.
    $userDirs = @($pathDirs | Where-Object { $_.StartsWith($env:USERPROFILE, [System.StringComparison]::OrdinalIgnoreCase) })
    foreach ($dir in $userDirs) {
        if (Test-DirectoryWritable -Path $dir) { return $dir }
    }
    foreach ($dir in $pathDirs) {
        if (Test-DirectoryWritable -Path $dir) { return $dir }
    }

    return $null
}

function Install-PathScript {
    $source = $PSCommandPath
    if (-not $source -or -not (Test-Path -LiteralPath $source)) {
        throw "Cannot find the script file to install. Run this script from a file."
    }

    $dir = Get-VpnInstallDir
    if (-not $dir) {
        throw "No writable directory on PATH was found. Add a user directory such as $env:USERPROFILE\.local\bin to PATH and retry."
    }

    $target = Join-Path $dir $ScriptFileName
    if ($source -ieq $target) {
        Write-Host "Script is already in PATH: $target" -ForegroundColor Green
    }
    else {
        Copy-Item -LiteralPath $source -Destination $target -Force -ErrorAction Stop
        Write-Host "Script installed to PATH: $target" -ForegroundColor Green
    }
    return $target
}

function Get-VpnIconPath {
    if (Test-Path -LiteralPath $IconFile) { return $IconFile }

    $source = if (Test-Path -LiteralPath $TrGUIPath) {
        $TrGUIPath
    }
    else {
        Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
    }

    try {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        $icon = [System.Drawing.Icon]::ExtractAssociatedIcon($source)
        if (-not $icon) { return $null }
        New-Item -ItemType Directory -Path $IconDir -Force | Out-Null
        $stream = [System.IO.File]::Open($IconFile, [System.IO.FileMode]::Create)
        try {
            $icon.Save($stream)
        }
        finally {
            $stream.Dispose()
            $icon.Dispose()
        }
        return $IconFile
    }
    catch {
        Write-Warning "Could not create an icon file: $($_.Exception.Message)"
        return $null
    }
}

function Get-ShortcutPath {
    if ($ShortcutPath) { return $ShortcutPath }

    $desktop = [Environment]::GetFolderPath([Environment+SpecialFolder]::DesktopDirectory)
    if (-not $desktop) { $desktop = Join-Path $env:USERPROFILE "Desktop" }
    return Join-Path $desktop $ShortcutName
}

function Save-InstallState {
    param([string]$ScriptPath, [string]$LinkPath)

    New-Item -ItemType Directory -Path $IconDir -Force | Out-Null
    $state = [pscustomobject]@{ script = $ScriptPath; shortcut = $LinkPath }
    [System.IO.File]::WriteAllText($StateFile, ($state | ConvertTo-Json))
}

function Read-InstallState {
    if (-not (Test-Path -LiteralPath $StateFile)) { return $null }
    try {
        return Get-Content -LiteralPath $StateFile -Raw | ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Install-Shortcut {
    $linkPath = Get-ShortcutPath
    $scriptPath = Install-PathScript
    $psExe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
    if (-not (Test-Path -LiteralPath $psExe)) { $psExe = "powershell.exe" }

    $parent = Split-Path -Parent $linkPath
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    $iconPath = Get-VpnIconPath
    $iconLocation = if (Test-Path -LiteralPath $TrGUIPath) { "$TrGUIPath,0" } elseif ($iconPath) { "$iconPath,0" } else { $null }
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($linkPath)
    $shortcut.TargetPath = $psExe
    $shortcut.Arguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$scriptPath`" toggle -Notify"
    $shortcut.WorkingDirectory = Split-Path -Parent $scriptPath
    $shortcut.Description = "Start or stop the Check Point VPN service and tray UI"
    if ($iconLocation) { $shortcut.IconLocation = $iconLocation }
    $shortcut.Save()

    # Flip the "run as administrator" flag so the shortcut can control services.
    $bytes = [System.IO.File]::ReadAllBytes($linkPath)
    if ($bytes.Length -gt 0x15) {
        $bytes[0x15] = $bytes[0x15] -bor 0x20
        [System.IO.File]::WriteAllBytes($linkPath, $bytes)
    }

    Save-InstallState -ScriptPath $scriptPath -LinkPath $linkPath

    Write-Host "Shortcut installed: $linkPath" -ForegroundColor Green
    Write-Host "Command available:   $CmdName start|stop|toggle" -ForegroundColor Green
    Write-Host "The shortcut asks for elevation, which the VPN services require."
}

function Uninstall-Shortcut {
    $state = Read-InstallState
    $linkPath = if ($state -and $state.shortcut) { $state.shortcut } else { Get-ShortcutPath }

    if (Test-Path -LiteralPath $linkPath) {
        Remove-Item -LiteralPath $linkPath -Force -ErrorAction Stop
        Write-Host "Shortcut removed: $linkPath" -ForegroundColor Green
    }
    else {
        Write-Host "No shortcut found at $linkPath"
    }

    $scriptPath = if ($state -and $state.script) { $state.script } else { $null }
    if (-not $scriptPath) {
        $dir = Get-VpnInstallDir
        if ($dir) { $scriptPath = Join-Path $dir $ScriptFileName }
    }
    if ($scriptPath -and (Test-Path -LiteralPath $scriptPath)) {
        try {
            Remove-Item -LiteralPath $scriptPath -Force -ErrorAction Stop
            Write-Host "Removed from PATH: $scriptPath" -ForegroundColor Green
        }
        catch {
            Write-Warning "Could not remove ${scriptPath}: $($_.Exception.Message)"
        }
    }

    if (Test-Path -LiteralPath $StateFile) { Remove-Item -LiteralPath $StateFile -Force }
    if (Test-Path -LiteralPath $IconFile) { Remove-Item -LiteralPath $IconFile -Force }
    if ((Test-Path -LiteralPath $IconDir) -and -not (Get-ChildItem -LiteralPath $IconDir -Force -ErrorAction SilentlyContinue)) {
        Remove-Item -LiteralPath $IconDir -Force
    }
}

function Show-VpnNotification {
    param([string]$Text)

    if (-not $Text) { return }
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop

        $iconPath = Get-VpnIconPath
        $icon = if ($iconPath) { New-Object System.Drawing.Icon($iconPath) } else { [System.Drawing.SystemIcons]::Shield }

        $notify = New-Object System.Windows.Forms.NotifyIcon
        try {
            $notify.Icon = $icon
            $notify.BalloonTipTitle = "Check Point VPN"
            $notify.BalloonTipText = $Text
            $notify.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
            $notify.Visible = $true
            $notify.ShowBalloonTip(4000)
            Start-Sleep -Seconds 4
        }
        finally {
            $notify.Visible = $false
            $notify.Dispose()
            if ($iconPath) { $icon.Dispose() }
        }
    }
    catch {
        # Notification is best-effort.
    }
}

if ($Help -or $Command -eq "help") {
    Show-Usage
    exit 0
}

if ($Install -and $Uninstall) {
    Write-Error "Use either -Install or -Uninstall, not both."
    exit 1
}

if ($Install) {
    try {
        Install-Shortcut
        exit 0
    }
    catch {
        Write-Error "Install failed: $($_.Exception.Message)"
        exit 1
    }
}

if ($Uninstall) {
    try {
        Uninstall-Shortcut
        exit 0
    }
    catch {
        Write-Error "Uninstall failed: $($_.Exception.Message)"
        exit 1
    }
}

$action = $Command
if (-not $action) {
    $action = Select-VpnAction
}
if (-not $action) { exit 1 }

try {
    Assert-Services
    $state = Invoke-Action -Action $action
}
catch {
    $message = $_.Exception.Message
    Write-Error "Check Point VPN $action failed: $message (run elevated if this is an access error)"
    if ($Notify) { Show-VpnNotification "Check Point VPN $action failed: $message" }
    exit 1
}

if ($Notify) {
    Show-VpnNotification "Check Point VPN $state"
}
# Installs everything needed to reboot a remote machine and then reboots the
# machine.
# ugly and inelegant. they should be completely separate activities. Maybe
# I'll rewrite properly later.
param(
    $machine
)

if (!$machine) {
    Write-Host "`n-={ Reboot remote machine }=- Read inline comments for more info. Usage: `n`n$($MyInvocation.MyCommand.Name) [machine-name]`n"
    exit
}
# Might need to set this policy before running the script for the rest to work:
#   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
irm get.scoop.sh | iex
scoop install git
git config --global credential.helper manager-core
%USERPROFILE%\scoop\apps\7zip\current\install-context.reg
Scoop bucket add extras
Scoop install sysinternals

$env:remote = $machine

Psinfo \\$env:remote

Psshutdown -rf \\$env:remote

Ping -t $env:remote

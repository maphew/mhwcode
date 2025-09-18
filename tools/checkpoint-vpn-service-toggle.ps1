echo "--- Check Point VPN Service Toggle ---"
$svc = Get-Service TracSrvWrapper
if ($svc.Status -eq "Running") {
    Stop-Service TracSrvWrapper
    Write-Output "Check Point VPN stopped."
} else {
    Start-Service TracSrvWrapper
    Write-Output "Check Point VPN started."
}
echo "--- done ---"

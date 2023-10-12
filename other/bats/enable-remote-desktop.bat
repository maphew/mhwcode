@echo off
@setlocal
call :Main %1 %2 %3 %4 %5
goto :eof


:Main
    set .h=\\%1
    psexec %.h% %2 %3 %4 %5 reg add "hklm\system\currentcontrolset\control\terminal server" ^
      /f /v fDenyTSConnections /t REG_DWORD /d 0
    psexec %.h% %2 %3 %4 %5 netsh advfirewall firewall set rule group="remote admin" new enable=Yes
    psexec %.h% %2 %3 %4 %5 netsh advfirewall firewall set rule group="remote desktop" new enable=Yes
    endlocal
    goto :EOF


REM Remotely enable Remote Desktop (RDP)  
REM https://yukonnect.gov.yk.ca/collab/env-c1/GIS/_layouts/OneNote.aspx?id=%2Fcollab%2Fenv-c1%2FGIS%2FSiteAssets%2FENV%20GIS%20Unit%20notebook&wd=target%28Tips%20and%20Tricks.one%7CC3C1DDDC-F07F-4B44-AB2E-81D0EDB0A9EF%2FRemotely%20enable%20Remote%20Desktop%20%28RDP%5C%29%7C3673B622-8C9E-4B07-9294-06261CD27DC3%2F%29
    
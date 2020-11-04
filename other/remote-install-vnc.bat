@:: Courtesy of Mark Collins
@:: http://www.markcollins.ca/blog/remote-vnc-remote-support-network-pcs
@:: UNTESTED

color A0
mode con lines=3 cols=90
@echo This will install VNC on a remote computer to help you a user. 
@echo It will self delete once you close VNCViewer.
SET /P pcip=Please enter the IP Address of the computer:


color A8
mode con lines=2 cols=90


mode con lines=30 cols=90
@echo off
color A8
echo Y | xcopy %temp%\CSystem32\*.* \\%pcip%\c$\windows\system32
ping -n 2 127.0.0.1
%temp%\psexec.exe \\%pcip% c:\windows\system32\TVNCStart.bat
ping -n 2 127.0.0.1
%temp%\psexec.exe \\%pcip% c:\windows\system32\TVNCStart.bat
color A5
mode con lines=2 cols=90
%temp%\tvnviewer.exe %pcip%
@echo off
mode con lines=20 cols=90
%temp%\psexec.exe \\%pcip% taskkill /im tvnserver.exe /f
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\tvnserver.exe
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\screenhooks32.dll
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\screenhooks64.dll
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\OLEPRO32.dll
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\hookldr.exe
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\TVNCStart.bat
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\tvncreg.reg
ping -n 2 127.0.0.1
del \\%pcip%\c$\windows\system32\tvncreg.reg
ping -n 2 127.0.0.1
%temp%\psexec.exe \\%pcip% reg delete HKEY_LOCAL_MACHINE\SOFTWARE\TightVNC /f
IF NOT EXIST \\%pcip%\c$\windows\system32\tvnserver.exe goto exit
IF EXIST \\%pcip%\c$\windows\system32\tvnserver.exe goto RemoveVNC

:exit
exit

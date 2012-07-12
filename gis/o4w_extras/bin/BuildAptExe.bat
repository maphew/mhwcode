@echo off
@echo.
@echo.  Build standalone apt.exe
@echo.
if [%3]==[] goto :Usage
setlocal
set pyinstaller=%1
set aptpy=%2
set rev=r%3
set aptexe=%~dp2\%~n2-%rev%.exe

:Main
    pushd %pyinstaller% 
    @echo on
    python Makespec.py --onefile --out=.\apt-%rev% %aptpy% 
    python Build.py .\apt-%rev%\apt.spec
    move .\apt-%rev%\dist\apt.exe %aptexe%
    @echo off
    popd
    goto :eof

:Usage
    @echo.
    @echo.  %0 [path\to\pyinstaller\dir] [path\to\apt.py] [apt_version_#]
    @echo.
    goto :eof

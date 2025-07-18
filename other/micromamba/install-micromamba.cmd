@echo. Installing micromamba via CMD...
@echo.
::Requires: wget, 7zip, gsudo

sudo setx /M MAMBA_ROOT_PREFIX C:\apps\micromamba

wget -O micromamba.tar.bz2 --no-clobber https://micro.mamba.pm/api/micromamba/win-64/latest 
7z x micromamba.tar.bz2
7z x micromamba.tar
@for %%a in (mm.exe miromamba.exe) do if exist c:\bin\%%a del c:\bin\%%a 
move Library\bin\micromamba.exe c:\bin\
sudo mklink /h c:\bin\mm.exe c:\bin\micromamba.exe
rd /s/q info Library
del micromamba.tar

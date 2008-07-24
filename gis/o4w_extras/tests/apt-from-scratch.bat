@echo off
echo.
echo.	Install OSGeo4W from scratch 
echo.
echo.	THIS WILL REMOVE EXISTING C:\OSGEO_4W!
echo.

if not [%1]==[yes] goto :Usage

:SetEnv
	setlocal
	set pythonpath=
	set osgeo4w_root=C:\OSGeo4W
	set osgeo4w_root_msys=%osgeo4w_root%
	::set o4w-apt=c:\OSGeo4W.extras\bin\o4w-apt.py
	::set python=d:\PortablePython1.0\python.exe
	::echo %python% %o4w-apt% %%* > apt.bat
	echo @apt-r43.exe %%*> apt.bat

:CleanSlate
	if exist %osgeo4w_root% rd /s/q %osgeo4w_root%
	md %osgeo4w_root%

:DoIt
	call apt setup
	call apt update
	call apt install gdal

:Test
	%osgeo4w_root%\bin\gdalinfo --version

goto :eof

:Usage
echo.   if you don't say "%0 yes" I won't do it.

@echo off
echo.
echo.	Installing a few extra goodies into OSGeo4W
echo.

:: Environment settings
if [%OSGEO4W_ROOT%]==[] goto :EnvNotSet

:xcopy
	cd /d %~dp0
	if not exist xcopy_exclude.txt echo .svn > xcopy_exclude.txt
	xcopy /s /exclude:xcopy_exclude.txt /d /y .\* %OSGEO4W_ROOT%\
	call :MakeBats
	goto :Done

:MakeBats
	cd /d %OSGEO4W_ROOT%\bin
	for %%g in (*.py) do (
		if not exist %%~ng.bat echo @python "%%OSGEO4W_ROOT%%\bin\%%g" %%* > %%~ng.bat
		)
	goto :EOF

:EnvNotSet
	echo.
	echo.	*** OSGEO4W_ROOT not found. 
	echo.	*** Please run install-o4w-extras.bat from within OSGeo4W shell.
	echo.
	:: pause for a few seconds.
	ping localhost -n 5 >nul
	goto :EOF	

:Done
	echo.
	echo.	Finished.
	echo.
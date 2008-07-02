@echo off
echo.
echo.	Installing a few extra goodies into OSGeo4W
echo.

:: Environment settings
if [%OSGEO4W_ROOT%]==[] goto :EnvNotSet
setlocal enabledelayedexpansion
:: Capture drive letter and parent dir tree of where the o4w goodies are sitting
set _prefix=%~dp0

:Main
for /r %%g in (*) do (
	set srcFile=%%g
	REM strip parent dir tree,
	REM turn x:\temp\Osgeo4w.extras\bin\gdalcopyproj.py    into    c:\osgeo4w\bin\gdalcopyproj.py
	set dstFile=!srcFile:%_prefix%=%OSGEO4W_ROOT%\!
	
	if not exist "!dstFile!" echo.	!dstFile!
	if not exist "!dstFile!" copy "!srcFile!" "!dstFile!"
	
	)

cd /d %OSGEO4W_ROOT%\bin

for %%g in (*.py) do if not exist %%~ng.bat echo @python "%%OSGEO4W_ROOT%%\bin\%%g" %%* > %%~ng.bat

goto :Done


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

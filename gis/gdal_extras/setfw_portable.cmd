@echo off
:: A simple script to allow one to use FWTools for Windows from a USB device 
:: without installing anything on the host. 
::
:: Save with .cmd extension to ensure command.com is not used  (a hold over 
:: from Win9x). The script will only work on Windows 2000 and newer.
:: 
:: Initial version 2007 Feb 16, Matt Wilkie (maphew@gmail.com)  [mhw]
:: 2007-OCt-25 [mhw] added missing call for setfwenv.bat, (thanks to Farley Klotz)

if not %cmdextversion% GEQ 2 goto :WrongCmd

:Main
	cls & echo.
	rem Root fwtools home dir to the same directory this script exists in
	set FWTOOLS_DIR=%~dp0
	rem Rmove trailing backslash
	set FWTOOLS_DIR=%FWTOOLS_DIR:~0,-1%
	echo FWTools home is %FWTOOLS_DIR% & echo.

	rem Add fwtools bin directory to path and make sure gdal is there.
	for %%a in (gdalinfo.exe) do (
		if [%%~dp$PATH:a]==[] path=%FWTOOLS_DIR%\bin;%PATH%
		)
	gdalinfo --version || goto :NotFound
	
	rem Configure environment for python modules, proj lib data, drivers, etc.
	call %FWTOOLS_DIR%\bin\setfwenv.bat
	
	rem Add local preferences (e.g. for "--config" parameters)
	   rem For 'gdaladdo', use external pyramids in .aux file
	set USE_RRD=YES
	   rem Up the default amount of memory used
	set GDAL_CACHEMAX=512
	
	rem Remember the yukon albers projection parameters.
	set ytalbers="+proj=aea +lat_1=61.66666666666666 +lat_2=68 +lat_0=59 +lon_0=-132.5 +x_0=500000 +y_0=500000 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
	
	rem List available commands
	echo. & echo Available exe commands are: & echo.
	dir /d %FWTOOLS_DIR%\bin\*.exe |find ".exe"
	echo. & echo Available python commands are: & echo.
	dir /d %FWTOOLS_DIR%\bin\*.py |find ".py"

	goto :EOF

:WrongCmd
	echo.
	echo Sorry, this script requires CMD.exe with extension
	echo version 2 or above (Windows 2000 or later)
	echo.
	echo Yours appears to be: %CMDEXTVERSION%
	echo.
	goto :EOF

:NotFound
	echo.
	echo Sorry, I can't find GDAL Utilities
	echo.

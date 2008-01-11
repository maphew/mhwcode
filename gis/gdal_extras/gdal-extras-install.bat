@echo off
:: there are few things which are not included in the default fwtools install which I always need to add later.
if %GDAL_DATA%=="" goto :NotGdalShell
if %FWTOOLS_DIR%=="" goto :NotGdalShell
setlocal

:: remember where we started from
set rememberCD=%cd%

:: Root gdal_exrtas home dir to the same directory this script exists in
set gd-extras=%~dp0
:: Rmove trailing backslash
set gd-extras=%gd-extras:~0,-1%
echo gdal_extras home is %gd-extras% & echo.


:: copy each of the files in bin and data to gdal, but only if they don't exist already
:Bin
cd /d %gd-extras%\bin
for %%a in (*) do (
	if not exist "%FWTOOLS_DIR%\bin\%%~nxa" copy "%%a" "%FWTOOLS_DIR%\bin\%%~nxa"
	)
:Data
cd /d %gd-extras%\data
for %%a in (*) do (
	if not exist "%FWTOOLS_DIR%\data\%%~nxa" copy "%%a" "%FWTOOLS_DIR%\data\%%~nxa"
	)

:: for fwtools on a portable device
copy /-y %gd-extras%\setfw_portable.cmd %FWTOOLS_DIR%\

:: change  gdal_SDE_92.dll to match version of SDE (e.g. 9.1 or  9.2)
rem copy /-y %gd-extras%\gdal_plugins\gdal_SDE_91.dll %FWTOOLS_DIR%\gdal_plugins\gdal_SDE.dll

:: Add Yukon Albers (epsg:3578) to projection list (won't be needed after next epsg update)
rem type %gd-extras%\proj_lib\yukon_albers.epsg >> %PROJ_LIB%\epsg

:Samples
::: create a batch file to run each of the samples.
cd /d %FWTOOLS_DIR%\bin
for %%a in (*.py) do (
	if not exist %%~na.bat echo @python "%%FWTOOLS_DIR%%\bin\%%a" %%* > %%~na.bat
	)

cd /d %rememberCD%
goto :EOF

:NotGdalShell
	echo.
	echo.	Error! GDAL_DATA and/or FWTOOLS_DIR environment is not set
	echo.	Are you sure this is an FWTools or GDAL shell?
	echo.
	goto :EOF

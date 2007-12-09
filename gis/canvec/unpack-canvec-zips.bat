@echo off
echo.
echo.    Unpack downloaded CanVec files for area of interest.
echo.

:: Set to 1:50,000 NTS numbers for area of interest
set tileList=116b14 116b15 116b16 116a13 116b11 116b10 116b09 116a12 116b06 116b07 116b08 116a05 116b03 116b02 116b01 116a04

if “%2″ == “” goto :Usage

set xsrc=%1
set dst=%2
set _home=%cd%

if not exist %dst% mkdir %dst%

call :unZip
call :Organise
goto :EOF

:UnZip
	for %%f in (%tileList%) do (
	for /f “tokens=*” %%a in (’dir /s/b %src%\*%%f*’) do unzip -n -d %dst% %%a
	)
	goto :EOF

:Organise
	:: put all docs & metadata into it’s own folder
	cd %dst%
	mkdir meta
	for %%f in (*.html *.txt *.xml *.xsd) do move %%f meta
	cd %_home%
	goto :EOF

:Usage
	echo.
	echo.    Usage: %~n0 [path\to\canvec_archives] [output dir]
	echo.


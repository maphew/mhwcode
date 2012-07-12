@echo off
:: initial version, 2005-Nov-17, matt wilkie
:: this script is public domain
if [%1]==[] (
	echo.
	echo -={ gdal_wildmerge }=- Allow gdal_merge to accept wildcards for input files
	echo .
	echo . 	%~nx0 [input-file-wildcard] [output-file] {options}
	echo . 
	echo .	%~n0 d:\src\*.tif mosaick.tif -init -9999 -co compress=lzw
	echo.
	goto :EOF
	)
	:: %1 is the input wildcard mask
	:: This is inverted from normal gdal_merge usage in order to allow other
	:: options be passed to gdal_merge


:: delayed expansion requires windows NT or later command shell 
:: (it won't work on windows 9x)
	verify other 2>nul 
	setlocal ENABLEDELAYEDEXPANSION 
	if errorlevel 1 goto :wrong_version

:: gdal_merge won't overwrite an existing file	
	if exist %2 goto :file_exists

:: Build the input file list
	set infiles=
	for %%a in (%1) do set infiles=!infiles! "%%a"

:: Here is were the actual work happens
	set gdalcmd=gdal_merge %infiles% -o "%2"
   echo %gdalcmd%
   :: IMPORTANT, if gdal_merge is not call'ed control doesn't return 
	:: to the batch file
	call %gdalcmd%
	goto :EOF

:file_exists
	echo *** the output file "%2" already exists.
	goto :EOF

:wrong_version
	echo.
	echo	Sorry, this batchfile requires DELAYED EXPANSION which is 
	echo	not available in this shell. See 
	echo    http://www.google.com/search?q=enabledelayedexpansion
	goto :EOF


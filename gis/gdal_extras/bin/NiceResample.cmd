:: NiceResample.cmd
:: Matt.Wilkie@gov.yk.ca
:: Down-sample from 900x900 pixels down to 128x128 in 100px stages.
:: For indexed (colour palletted) images change the resampling to nearest neighbour
:: http://n2.nabble.com/Resampling-With-GDAL-td2029808.html
::
:: TODO:
::  + up or down sample from command parameter
::  + 
@echo off
echo.
echo.   %~n0: resample an image nicely, slow but with good results
echo.
if [%2]==[] goto :Usage
if not exist "%1" goto :NoFile
rem if exist "%2" goto :OutExists
set inFile=%1
set outFile=%2

:: enables variable expansion inside FOR loop (!x! syntax)
:: requires Windows 2000 or newer
setlocal enabledelayedexpansion

:Main
        set tmpFile=%infile%
        :: resample from 900x900 pixels down to 128x128
        :: in 100px stages.
        for %%a in (900 800 700 600 500 400 300 200 128) do (
                gdalwarp -r cubic -q -ts %%a %%a !tmpFile! xx_%%a_%inFile%
                set tmpFile=xx_%%a_%inFile%
                )
        :: "&& del" only deletes if previous command successful
        gdal_translate !tmpFile! %outFile% && del xx_*_%inFile%
        echo.
        echo   Finished writing 128x128px %outFile%
        goto :EOF

:NoFile
        echo *** Error: input %1 not found
        goto :EOF

:Usage
        echo. Usage: %~n0 [input image] [output image]
        echo.
        echo   output overwritten if it exists
        goto :EOF 
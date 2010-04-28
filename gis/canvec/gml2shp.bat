@echo off
:: Merge all gml files in specified directory to shapefiles, with optional OGR parameters
::
if "%2" =="" goto :Usage

:: Handle command line arguments,
:: kudos to Patrick Cuff - http://stackoverflow.com/questions/382587
for /f "tokens=1-3*" %%a in ("%*") do (
    set srcDir=%1
    set outDir=%2
    set arg3=%%c
    set argTheRest=%%d
)

set ogrArgs= -f "esri shapefile"

:: OGR parameters to project from NAD83CSRS to Yukon Albers
set yt_alb="+proj=aea +lat_1=61.66666666666666 +lat_2=68.0 +lat_0=59.0 +lon_0=-132.5 +x_0=500000 +y_0=500000 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"

if "%arg3%"=="yukon" (
   set ogrArgs=%ogrArgs% -s_srs epsg:4617 -t_srs %yt_alb% ) else (
   set ogrArgs=%ogrArgs% %argTheRest%
   )

call :Main
goto :EOF

:Main
    pushd %srcDir%
    for %%f in (*.gml) do (
        echo Processing %%f
        REM convert from GML to SHP and merge
        if not exist [%outDir%] (call :New %%f) else (call :Append %%f)
       )
    popd
    goto :EOF

:New
    echo ogr2ogr %ogrArgs% %outDir% %1
    ogr2ogr %ogrArgs% -append %outDir% %1
    goto :eof

:Append
    echo ogr2ogr %ogrArgs% -update -append %outDir% %1
    ogr2ogr %ogrArgs% -update -append %outDir% %1
    goto :eof

:Usage
    echo.
    echo. Usage: %~n0 [path\to\*.gml] [output dir] {ogr arguments}
    echo.

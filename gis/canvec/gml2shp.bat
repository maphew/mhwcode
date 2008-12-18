@echo off
:: Merge all gml files in specified directory to shapefiles, with optional OGR parameters
::
if "%2" =="" goto :Usage

set srcDir=%1
set outDir=%2
set ogrArgs= -f "esri shapefile"

:: OGR parameters to project from NAD83CSRS to Yukon Albers
set yt_alb="+proj=aea +lat_1=61.66666666666666 +lat_2=68.0 +lat_0=59.0 +lon_0=-132.5 +x_0=500000 +y_0=500000 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
if "%3"=="yukon" (
   set ogrArgs=%ogrArgs% -s_srs epsg:4617 -t_srs %yt_alb% ) else (
   set ogrArgs=%ogrAtrgs% %3
   )

call :Main
goto :EOF

:Main
	pushd %srcDir%
	for %%f in (*.gml) do (
   	echo Processing %%f

   	REM convert from GML to SHP and merge
   	if not exist %outDir% (
      	rem echo ogr2ogr %ogrArgs% %outDir% %%f
      	ogr2ogr %ogrArgs% -append %outDir% %%f) else (
         	rem echo ogr2ogr %ogrArgs% -update -append %outDir% %%f
         	ogr2ogr %ogrArgs% -update -append %outDir% %%f
            )
      rem pass
   )
	popd
	goto :EOF

:Usage
	echo.
	echo. Usage: %~n0 [path\to\*.gml] [output dir] {ogr arguments}
	echo.

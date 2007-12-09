@echo off
:: Merge all gml files in specified directory to shapefiles, with optional OGR parameters
::
if “%2″ == “” goto :Usage

set _home=%cd%
set srcDir=%1
set outDir=%2
set ogrArgs= -f “esri shapefile”

:: OGR parameters to project from NAD83CSRS to Yukon Albers
if “%3″==”yukon” (
set ogrArgs=%ogrArgs% -s_srs epsg:4617 -t_srs epsg:3578 ) else (
set ogrArgs=%ogrAtrgs% %3
)

call :Main
goto :EOF

:Main
	cd /d %srcDir%
	for %%f in (*.gml) do (
	echo Processing %%f…

	REM convert from GML to SHP and merge
	if not exist %outDir% (
	rem echo ogr2ogr %ogrArgs% %outDir% %%f
	ogr2ogr %ogrArgs% -append %outDir% %%f) else (
	rem echo ogr2ogr %ogrArgs% -update -append %outDir% %%f
	ogr2ogr %ogrArgs% -update -append %outDir% %%f)
	)
	cd /d %_home%
	goto :EOF

:Usage
	echo.
	echo. Usage: %~n0 [path\to\*.gml] [output dir] {ogr arguments}
	echo.


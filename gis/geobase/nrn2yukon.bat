@echo off
:: rev 0.1 ~ 2007 Nov 10, Matt Wilkie - maphew@gmail.com
echo.
echo. Going to download National Road Network files from Geobase
echo. for Yukon and adjacent regions.
echo. When finished downloading I will attempt to unpack the archives
echo. and project the data to Yukon Albers, in shapefiles.
echo.
echo.
setlocal

call :ChkReqs wget.exe
call :Unpack
call :gml2shp
goto :EOF

:ChkReqs
	:: test for wget, if it is in path we can carry on.
	if exist “%~$PATH:1″ (
	call :D ownload ) else (
	echo %1 not found! can’t continue
	)
	goto :EOF

:Download
	set urlRoot=http://ftp2.cits.rncan.gc.ca/pub/geobase/official/nrn_rrn/

	:: Regions to download (ab = alberta, etc.)
	set regions=yt nt bc ab

	:: gml or shapefiles?
	set type=gml
	rem set type=shp

	if not exist zips mkdir zips
	cd zips
	for %%a in (%regions%) do (
	wget –continue %urlRoot%/%%a/nrn_rrn_%%a_%type%_en.zip
	)
	cd ..

	goto :EOF

:Unpack
	:: FIXME: chkreq is hardcoded to download on successful check
	rem call :ChkReqs 7z.exe
	if not exist unpack mkdir unpack
	cd unpack
	7z x ..\zips\*.zip
	cd ..

	echo.
	echo. Finished unpacking.
	echo.
	goto :EOF

:gml2shp
	echo.
	echo. Now I’m going to convert from GML to shapefile,
	echo. and project to Yukon Albers in the process.
	echo. This could take awhile.
	echo.

	:: projection parameters. Example is of NAD83CSRS in lat-long to NAD83 Yukon Albers
	:: refer to gdal/ogr docs for more info on how to use these parameters
	set prj_params=-s_srs epsg:4617 -t_srs epsg:3578
	for %%a in (%regions%) do (
	echo ogr2ogr -f “esri shapefile” -overwrite %prj_params% %%a unpack\NRN_%%a*.gml
	ogr2ogr -f “esri shapefile” -overwrite %prj_params% %%a unpack\NRN_%%a*.gml
	)
	goto :EOF

@echo off
:: 2008-April-16 - Matt.wilkie@gov.yk.ca - this script is public domain
::
:: Need an automated way to convert coverage to shape with out knowing ahead of time geometry type (line, point, poly)
::  ArcCatalog drag 'n drop for coverages doesn't work, and FeatureClassToFeatureclassMultuple is broken for coverages
:: so using ogr2ogr instead (which is faster anyway)
::
:: Only polygons, lines and points are handled, so Region subcoverages and node networks etc. need to processed elsewhere

if [%2] == [] goto Usage
set incov=%1
set outshp=%2
set debug=%3

if not exist %incov% goto NoCov

set scratchDir=%outshp%_%random%
mkdir %scratchDir% 

if not exist %outshp% mkdir %outshp%

:Cov2shp
	ogr2ogr %scratchDir%\%incov% %incov%
	:: polygons
	if exist %incov%\pal.adf (
		copy %scratchDir%\%incov%\PAL.* %outshp%\%incov%_ply.* > nul
		goto :EndCov2shp	rem  With polys we don't need the lines or label points, so skip
		)
	:: lines, then points
	if exist %incov%\arc.adf copy %scratchDir%\%incov%\ARC.* %outshp%\%incov%_lin.*  > nul
	if exist %incov%\pat.adf copy %scratchDir%\%incov%\LAB.* %outshp%\%incov%_pnt.*  > nul
	:EndCov2shp
	
	::CleanUp
	if /i not [%debug%]==[--debug] (
		rd /s/q %scratchDir%
		) else (
			echo.	--debug specified, not removing "%scratchDir%"
			)
	
	::Report results
	echo.
	echo. Results in "%outshp%":
	echo.
	dir /b %outshp%\%incov%*
	echo.
	echo.  Note: polygon islands still need to be manually removed
	
	goto :EOF
	
:Usage
	echo.
	echo.	-={ Cover to Shape }=-
	echo.
	echo.	%~n0 [in cover] [out directory] {--debug}
	echo.
	goto :EOF

:NoCov
	echo.
	echo.	Input "%1" not found
	echo.
	goto :EOF

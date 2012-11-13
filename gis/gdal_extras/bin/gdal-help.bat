@echo off
echo.
if [%GDAL_DATA%]==[] goto :NoGDAL

	gdalinfo --version

	echo. & echo Available exe commands: & echo.
	dir /d %GDAL_DATA%\..\bin\*.exe |find ".exe"
	echo. & echo Available python commands: & echo.
	dir /d %GDAL_DATA%\..\bin\*.py |find ".py"

goto :EOF

:NoGDAL
echo	ERROR: GDAL environment not set
echo.

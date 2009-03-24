@echo off
setlocal enabledelayedexpansion

if [%2] ==[] goto :Usage

set _inFile=%1
set _outDir=%2

set _yt_alb="+proj=aea +lat_1=61_66666666666666 +lat_2=68_0 +lat_0=59_0 +lon_0=-132_5 +x_0=500000 +y_0=500000 +ellps=GRS80 +datum=NAD83 +units=m +no_defs"
set _opt=-s_srs epsg:4617 -t_srs %_yt_alb%

:Main
for /f "skip=1 tokens=1,2*" %%g in (bin\db-friendly-names.txt) do (
   set inLayer=%%g 
   set outLayer=%%h %%i
      
   echo  Processing "%_inFile%"
   if not exist "%_outDir%\!outLayer!*" (
      echo ogr2ogr -append %_opt% -nln "!outLayer!" %_outdir% "%_inFile%" !inLayer!
      ogr2ogr -append %_opt% -nln "!outLayer!" %_outdir% "%_inFile%" !inLayer!) else (
         rem echo___ogr2ogr -update -append %opt% -nln "!outLayer!" %outdir% %inFile% !inLayer!
         ogr2ogr -update -append -nln "!outLayer!" "%_outdir%" "%_inFile%" !inLayer! %_opt%
         )
   
   )
goto :eof

:Usage
	echo_
	echo_ Usage: %~n0 [path\to\*_gml] [output dir] {optional ogr arguments}
	echo_

@echo off
setlocal
:: use ghostscript to convert a pdf to jpeg
if "%3"=="" goto :usage

set infile=%1
set w_inch=%2
set h_inch=%3
if "%4"=="" (set outfile=%~n1.jpg) else (set outfile=%4) 


if "%2"=="#" (
  call :getPageSize %infile%
  ) else (
  call :calcPageSize %w_inch% %h_inch%
  )

call :main %infile% %w_pt% %h_pt% %outfile%
REM call :multiPage %infile% %w_pt% %h_pt% %outfile%
rem call :test %infile% %w_pt% %h_pt% %outfile%

goto :eof

:main
  %gs_dll%\%gsc%.exe ^
  -dNOPAUSE -P- -dSAFER -dBATCH -dQUIET ^
  -dGraphicsAlphaBits=4 ^
  -dTextAlphaBits=4 ^
  -sDEVICE=jpeg ^
  -dJPEGQ=90 ^
  -r300x300 ^
  -dDEVICEWIDTHPOINTS=%2 ^
  -dDEVICEHEIGHTPOINTS=%3 ^
  -sOutputFile=%outfile% ^
  %1
  echo.
  echo. Wrote: %outfile%
  echo.
  goto :eof


:multiPage
  :: note only diff from :main is -sOutputFile
  %gs_dll%\%gsc%.exe ^
  -dNOPAUSE -P- -dSAFER -dBATCH ^
  -dGraphicsAlphaBits=4 ^
  -dTextAlphaBits=4 ^
  -sDEVICE=jpeg ^
  -dJPEGQ=90 ^
  -r300x300 ^
  -dDEVICEWIDTHPOINTS=%2 ^
  -dDEVICEHEIGHTPOINTS=%3 ^
  -sOutputFile=pg%%02d_%outfile% ^
  %1
  echo.
  echo. Wrote: pg0x_%outfile%
  echo.
  goto :eof


:calcPageSize
  :: Ghostscript base unit 72pts per inch
  set /a w_pt=72 * %1
  set /a h_pt=72 * %2
  echo. Page size in points: %W_pt% x %h_pt%
  goto :eof

:getPageSize
  :: Use ghostscript 'bbox' device to read the bounding box from the pdf into a text file,
  :: read the width and height (in points) from that file
  ::
  :: produces a text file like this:
  ::    %%BoundingBox: 69 52 544 755
  ::    %%HiResBoundingBox: 69.025990 52.631998 543.066030 754.469977
  %gs_dll%\%gsc%.exe ^
  -dNOPAUSE -dBATCH -dSAFER -dQUIET ^
  -sDEVICE=bbox ^
  %1 ^
  2> xx-pagesize.txt
  
  for /f "tokens=4,5" %%g in ('findstr "%%" xx-pagesize.txt') do (
    set w_pt=%%g
    set h_pt=%%h
    )
  
  del xx-pagesize.txt
  
  echo. Read page size: %w_pt% %h_pt%
  goto :eof
  

:usage
  echo.
  echo. Convert a PDF to JPG using Ghostscript, to the specified page size in inches
  echo. (specify "#" to use internal bounding box)
  echo.
  echo. Usage: %~n0 infile.pdf [width, #] [height, #]
  echo.
  goto :eof


:test
  %gs_dll%\%gsc%.exe ^
  -dNOPAUSE -P- -dSAFER -dBATCH ^
  -dGraphicsAlphaBits=4 ^
  -dTextAlphaBits=4 ^
  -sDEVICE=jpeg ^
  -dJPEGQ=85 ^
  -r300x300 ^
  -sOutputFile=test_%4 ^
  %1
  echo.
  echo. Wrote: %4
  echo.
  goto :eof


:: ------ scrapbook ------

:: read only the 1st line of a file (only works for Windows CR/LF)
:: http://stackoverflow.com/a/7827243/14420
set /p _s=<xx-pagesize.txt
echo %_s%

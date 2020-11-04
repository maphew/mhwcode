@echo off
echo.
echo. Test pdf files for corruption
echo.
if "%1"=="" goto :usage
if not exist "%1" goto :notFound

setlocal enabledelayedexpansion

:Main
  echo. [error code] - [name of pdf]
  echo. -------------------------------------------------------------
  for %%a in (%*) do (
    call gs -o nul -sDEVICE=nullpage -dQUIET "%%a" 1>nul 2>nul
    echo. !errorlevel! - %%a
    )
  goto :eof
  
:usage
  echo. Usage:
  echo.
  echo.   %~n0 Fox_Lake_Bathymetry.pdf BisonHunting.pdf
  echo.
  echo.   %~n0 path\to\*.pdf
  echo.
  goto :eof

:notFound
  echo. "%1" not found
  echo.
  call :usage
  goto :eof
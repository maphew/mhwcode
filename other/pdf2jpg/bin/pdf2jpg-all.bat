@echo off
setlocal EnableDelayedExpansion
set "_attributes=%~a1"
if not "!_attributes:~0,1!" == "d" (goto :Usage)
  :: test if  param is directory
  :: directory will look like "d-a------" or "d--------"
  :: http://ss64.com/nt/syntax-args.html 
  ::    "Use %~a1 to display the Extended Attributes of a file"
  :: "What is the proper way to test if variable is empty in a batch file?"
  ::   https://stackoverflow.com/a/8452363/14420
  
:Main
  for %%a in (%1) do (
      pushd "%1"
      for %%b in (*.pdf) do (
        if not exist "%%~nb.jpg" call :convert "%%b"
        call :synctime "%%b"
        )
      popd
      )
  goto :eof
  
:Usage
  echo.
  echo. Usage:  %~n0 [path\to\folder]
  echo.
  goto :eof

:convert
  ::note we rely on filename coming in already quoted
  echo --- Running: call pdf2jpg %1 # #
  call pdf2jpg %1 # #
  goto :eof

:synctime
  echo --- Synchronizing jpg timestamp to pdf
  echo. touch --no-create --reference=%1 "%~n1.jpg"
  touch --no-create --reference=%1 "%~n1.jpg"
  goto :eof  

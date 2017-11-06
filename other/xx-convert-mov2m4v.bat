@echo off
@if not "%1"=="go" goto :Usage

for /r %%a in (*.avi *.mov) do (
  echo ----- %%a
  if exist "%%~dpna.mp4" del "%%~dpna.mp4"
  if not exist "%%~dpna.m4v" call :Main "%%a"
  if not exist "%%~dpna.m4v" echo no m4v for: "%%a" 
  if exist "%%~dpna.m4v" del "%%a" 
  )
goto :eof

:Main
  @echo on
  pushd "%~p1"
  
  HandBrakeCLI.exe ^
  --preset="Normal" ^
  --optimize ^
  --ipod-atom ^
  --encoder=x264 ^
  --encoder-preset=slow ^
  --quality=20 ^
  --input "%~nx1" ^
  --output "%~n1.m4v"
  
  popd
  @echo off
  goto :eof

:Usage
  echo. -=[ %~n0 ]=-
  echo.
  echo.     Usage: CD to folder to process and then run "%~n0 go"
  echo.
  handbrakecli
  echo.
  echo.  A "bad command" error means you might need to:
  echo.
  echo.  set path=%%path%%;c:\Program Files\Handbrake
  goto :eof
@echo off
@if not "%1"=="go" goto :Usage
@setlocal
@set _rate=192k

for /r %%a in (*.wma) do (
  echo ----- %%a
  if not exist "%%~dpna.mp3" call :Main "%%a"
  if not exist "%%~dpna.mp3" echo *** No mp3 for: "%%a"
  if exist "%%~dpna.mp3" del "%%a"
  )
goto :eof

:Main
  @echo on
  pushd "%~p1"
 
  ffmpeg.exe ^
  -i "%~nx1" ^
  -id3v2_version 3 ^
  -f mp3 ^
  -ab %_rate% ^
  -ar 44100 ^
  "%~n1.mp3"
  
  popd
  @echo off
  goto :eof
  
  
:Usage
  echo. -=[ %~n0 ]=-
  echo.
  handbrakecli
  echo.
  echo.  A "bad command" error means you might need to:
  echo.
  echo.  set path=%%path%%;c:\Program Files\Handbrake
  goto :eof
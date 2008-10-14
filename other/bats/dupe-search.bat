@echo off
:: dupe-search - Search PATH for duplicates of executables in specified directory
::
:: (c) 2008 Yukon Department of Environment 
:: License: MIT  - http://www.opensource.org/licenses/mit-license.php
::
:: Initial version Matt.wilkie@gov.yk.ca, (mhw) 2008-Oct-10 
:: http://code.google.com/p/maphew/source/browse/trunk/other/bats/dupe-search.bat
::
:: 2008-Oct-14 mhw - report location of dupe
::
if [%1]==[] goto Usage
set srcDir=%1
if not exist %srcDir% goto :NotFound

set dupes=%temp%\dupes.txt
if exist %dupes% del %dupes%

call :EditPath
call :Search
goto :End
:: ---------------------------------------------------------------------------

:EditPath
:: Make sure our search directory is not in PATH 
:: Adapted from http://www.ss64.com/nt/syntax-substring.html
::
:: Note - the User path can be edited, but the System path remains 
:: read-only for most users. This is pretty quirky so change with care. For 
::  instance a leading semi-colon in PATH means the script will *always* 
::  report dupes, even if there are none. 
   pushd %srcDir%
   :: Strip current dir
   call set PATH=%%PATH:%cd%=%%
   :: Replace double path delimiters with single 
   call set PATH=%%PATH:;;=;%%
   :: strip leading delimeter
   set _1=%PATH:~0,1%
   if "%_1%"==";" call set PATH=%%PATH:~1%%
   popd
   goto :eof

:Search
   pushd %srcDir%
   echo.
   echo --- Searching PATH for duplicates of %cd%\*
   for %%f in (*) do if not "%%~dp$PATH:f" =="" call :FoundDupe %%f
   if exist %dupes% (call :Report) else (
      echo.
      echo.     No dupes found :^)
      )
   popd
   goto :eof

:FoundDupe
  ::  Parse PATH, adapted from http://www.ss64.com/nt/path.html
  for %%p in ("%path:;=" "%") do (
      if exist %%p\%1 dir /s/b %%p\%1 >> %dupes%
   )
   goto :eof

:Report
   echo.
   echo. Duplicates:
   echo.
   type %dupes%
   echo.
   echo. List saved in %dupes%
   goto :eof

:Usage
   echo.
   echo. Usage:   %~nx0 [dir to use search template]
   echo.
   echo.          %~n0 c:\osgeo4w\bin
   echo.
   goto :eof
   
:NotFound
   echo.
   echo. Error, "%srcDir%" does not exist.
   echo.
   goto :eof
   
:End
   echo.
   echo --- %~n0 finished.

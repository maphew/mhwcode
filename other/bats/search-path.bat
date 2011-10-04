@echo off
REM @+leo-ver=5-thin
REM @+node:maphew.20101020152902.3710: * @file search-path.bat
REM @@first
REM @@language batch
::
:: Search PATH for specified filename(s)
::
REM @+<<readme>>
REM @+node:maphew.20101020152902.3714: ** <<readme>>
::
:: adapted from http://ss64.com/nt/path.html
:: this script is public domain
::
:: 2010-Oct-21, Matt Wilkie <maphew@gmail.com>
::
REM @-<<readme>>

setlocal
set _home=%CD%
set _targets=%*

echo.
echo -- Searching PATH for "%_targets%" --
echo.

:Main
    for %%g in ("%path:;=" "%") do (
        if not exist %%g (call :invalid_path %%g) else (
            pushd %%g
            call :lookfor %_targets%
            popd
            )
        )

REM One final check in the current directory before we finish
call :lookfor %_targets%

goto :End

REM @+others
REM @+node:maphew.20101020152902.3711: ** :invalid_path
:invalid_path
    set _msgs=%_msgs%; ** This directory is in PATH but does not exist: %1
    goto :eof

REM @+node:maphew.20101020152902.3713: ** :lookfor
:lookfor
    for %%h in (%*) do (
        if exist "%%h" (
            set /a _count=%_count% + 1
            echo.
            rem Report full path, size, and time stamp
            echo %%~dpnxh ^| %%~zh ^| %%~th
            )
    )
    goto :eof

REM @+node:maphew.20101020152902.3712: ** :End
:End
    if defined _msgs (
        echo.
        echo %_msgs%
        )

    if defined _count (
        echo.
        echo.   %_count% occurences found.
        echo.
        ) else (
            echo.
            echo.   No occurences found.
            )

    endlocal

REM @-others
REM @-leo

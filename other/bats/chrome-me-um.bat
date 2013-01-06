@echo off
:: Chrome-me-um - start Chrome browser with speficified user profile
:: Matt Wilkie, 2008-sept-26.
::  2013-Jan-06 + add FindChromeExe
:: this script is public domain
if [%1]==[] goto :Usage

setlocal
set _user=%1
set _root=%homedrive%%homepath%\Local Settings\Application Data\Google\Chrome
set _profile="%_root%\User Data\%_user%"
if not exist %_profile% set _opt=-first-run
call :FindChromeExe

if defined _chrome (
    start /b "%0" %_chrome% --user-data-dir=%_profile% %_opt%)

goto :eof
rem ---------- End ---------- 

:FindChromeExe
    if exist "%_root%\Application\chrome.exe" (
        set _chrome="%_root%\Application\chrome.exe")

    if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" (
        set _chrome="%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe")

    if exist "%ProgramFiles%Google\Chrome\Application\chrome.exe" (
        set _chrome="%ProgramFiles%Google\Chrome\Application\chrome.exe")

    if not defined _chrome echo. *** Error, couldn't locate chrome.exe
    goto :eof

:Usage
    echo.
    echo. Start Google Chrome browser with a profile. Example:
    echo.
    echo.    %~n0 Noah_Body
    echo.
    goto :eof
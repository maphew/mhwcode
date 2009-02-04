@echo off
:: Chrome-me-um - start Chrome browser with speficified user profile
:: Matt Wilkie, 2008-sept-26.
:: this script is public domain
if [%1]==[] goto :Usage

setlocal
set _user=%1
set _root=%homedrive%%homepath%\Local Settings\Application Data\Google\Chrome
set _chrome="%_root%\Application\chrome.exe"
set _profile="%_root%\User Data\%_user%"
if not exist %_profile% set _opt=-first-run

start /b "%0%" %_chrome% --user-data-dir=%_profile% %_opt%

goto :EOF

:Usage
echo.
echo. Start Google Chrome browser with a profile. Example:
echo.
echo.    %~n0 Noah_Body
echo.

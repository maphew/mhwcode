:: #########################################################################################
:: #   MICROSOFT LEGAL STATEMENT FOR SAMPLE SCRIPTS/CODE
:: #########################################################################################
:: #   This Sample Code is provided for the purpose of illustration only and is not 
:: #   intended to be used in a production environment.
:: #
:: #   THIS SAMPLE CODE AND ANY RELATED INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY 
:: #   OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED 
:: #   WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.
:: #
:: #   We grant You a nonexclusive, royalty-free right to use and modify the Sample Code 
:: #   and to reproduce and distribute the object code form of the Sample Code, provided 
:: #   that You agree: 
:: #   (i)      to not use Our name, logo, or trademarks to market Your software product 
:: #            in which the Sample Code is embedded; 
:: #   (ii)     to include a valid copyright notice on Your software product in which 
:: #            the Sample Code is embedded; and 
:: #   (iii)    to indemnify, hold harmless, and defend Us and Our suppliers from and 
:: #            against any claims or lawsuits, including attorneys’ fees, that arise 
:: #            or result from the use or distribution of the Sample Code.
:: #########################################################################################
:: #########################################################################################
:: //***************************************************************************
:: //
:: // File:      RelaunchElevated.cmd
:: //
:: // Additional files required:  elevate.cmd and elevate.vbs
:: //
:: // Purpose:   CMD script that will “re-launch itself” elevated if it is 
:: //            not already running elevated
:: //
:: // Usage:     RelaunchElevated.cmd <arguments>
:: //
:: // Version:   1.0.0
:: //
:: // History:
:: // 1.0.0   06/19/2010  Created initial version.
:: //
:: // ***** End Header *****
:: //***************************************************************************
:: //
:: // downloaded from: http://blogs.technet.com/b/elevationpowertoys/

@echo off
setlocal enabledelayedexpansion

set CmdDir=%~dp0
set CmdDir=%CmdDir:~0,-1%

:: Check for Mandatory Label\High Mandatory Level
whoami /groups | find "S-1-16-12288" > nul
if "%errorlevel%"=="0" (
    echo Running as elevated user.  Continuing script.
) else (
    echo Not running as elevated user.
    echo Relaunching Elevated: "%~dpnx0" %*

    if exist "%CmdDir%\elevate.cmd" (
        set ELEVATE_COMMAND="%CmdDir%\elevate.cmd"
    ) else (
        set ELEVATE_COMMAND=elevate.cmd
    )

    set CARET=^^
    !ELEVATE_COMMAND! cmd /k cd /d "%~dp0" !CARET!^& call "%~dpnx0" %*
    goto :EOF
)

:: Continue script here

echo Arguments passed: %*


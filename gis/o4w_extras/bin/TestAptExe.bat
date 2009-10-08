@echo off
if [%1]==[] goto :Usage
setlocal
set aptexe=%1

:Main
    prompt $g
    @echo on
    set path=.
    set osgeo4w_root=%temp%\%aptexe%
    %aptexe% setup
    %aptexe% update
    %aptexe% install msvcrt
    %aptexe% list
    %aptexe% remove msvcrt
    @goto :eof

:Usage
    echo.
    echo.   %0 [apt-r###.exe to test]
    echo.
    goto :eof

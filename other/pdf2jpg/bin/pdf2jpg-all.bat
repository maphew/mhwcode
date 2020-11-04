@echo off
echo.
echo.   Convert all PDFs in a folder tree to JPG
echo.

:Main
    pushd "%*"
    for /d /r %%a in (*) do call pdf2jpg-dir "%%a"            
    popd
  goto :eof

:Usage
  echo.
  echo. Usage:  %~n0 [path\to\top\folder]
  echo.
  goto :eof

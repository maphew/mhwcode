@Echo off
:: Install a wrapper around program, so we don't have add whole
:: new folder to PATH.
:: Using a batch file because I can never remember exeproxy's 
:: parameters.
setlocal
set src=%~dpnx1
set shim=%~nx1

if not exist "%src%" goto :Usage

exeproxy.exe exeproxy-copy "C:\Shims\%shim%" "%src%"
dir "c:\Shims\%shim%" | findstr "%shim%" 

endlocal
goto :eof

:Usage
	echo.
	echo.	%~n0 [path to exe to mirror in Shim folder]
	echo.
	goto :eof

@if [%1]==[] goto :Usage
@setlocal enabledelayedexpansion
@set _NetworkPath=
@pushd %1
@for /f "tokens=2" %%i in ('wmic path win32_mappedlogicaldisk get deviceid^, providername ^| findstr /i "%CD:~0,2%"') do @(set _NetworkPath=%%i)
@echo.%_NetworkPath%
@popd
@goto :EOF
:: ---------------------------------------------------------------------
:Usage
  @echo.
  @echo. Get the full UNC path for the specified mapped drive path
  @echo.
  @echo.  %~n0 [mapped drive path]
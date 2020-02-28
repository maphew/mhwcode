@pushd %~dp0
@echo.
@echo.--- %~n0: Local project commands (%~dp0) ---
@echo.
@dir /w/b *.bat *.cmd *.sh1 *.py *.com *.exe
@REM todo: use PATHEXT instead of hardcode types.
@popd
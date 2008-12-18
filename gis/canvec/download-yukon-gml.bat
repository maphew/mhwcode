@echo off
:: rev 0.1, 2007 May 02, maphew@gmail.com
echo.
echo.    Going to download 1:50,000 CanVec data for Yukon as GML, which could
echo.    take awhile. This script can be aborted and rerun, it will resume
echo.    where it left off.
echo.
setlocal

call :ChkReqs wget.exe
goto :EOF

:ChkReqs
	:: test for wget, if it is in path we can carry on.
	if exist "%~$PATH:1" (
	call :Download ) else (
	echo %1 not found! can't continue
	)
	goto :EOF

:Download
	set urlRoot=ftp://ftp2.cits.rncan.gc.ca/pub/canvec/50k_gml

	:: Change these NTS numbers as required for your area of interest
	set QuadList=115 105 095 106 116 117 114 094 104

	for %%a in (%QuadList%) do (
	wget -recursive -continue -level=3 -no-host-directories -cut-dirs=2  %urlRoot%/%%a/*
	)
	goto :EOF

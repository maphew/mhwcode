@ECHO OFF
:: Check Windows version, abort if not NT 4 or later
IF NOT "%OS%"=="Windows_NT" GOTO Syntax
SETLOCAL ENABLEDELAYEDEXPANSION

:: Initialize variables
SET PrintCmd=
SET Temp=%Temp:"=%
SET NumFiles=0
SET MultiPrint=0
SET ListTool=

:: Check command line arguments
IF     "%~1"=="" GOTO Syntax
IF NOT "%~3"=="" GOTO Syntax
IF     "%~2"=="" (
	SET FileSpec=%~1
) ELSE (
	IF /I "%~1"=="/M" SET FileSpec=%~2
	IF /I "%~2"=="/M" SET FileSpec=%~1
)
ECHO.%* | FIND /I "/M" >NUL && SET MultiPrint=1
ECHO.%FileSpec% | FIND "/" >NUL && GOTO Syntax
IF NOT EXIST "%FileSpec%" GOTO Syntax

:: Count the number of files specified by filespec
FOR %%A IN (%FileSpec%) DO SET /A NumFiles = !NumFiles! + 1
IF %NumFiles% EQU 0 GOTO Syntax

:: Check if we need to have access to a list of processes
:: currently running, and if so, which one is available
IF %NumFiles%   GTR 1 SET  MultiPrint=1
IF %MultiPrint% EQU 0 CALL :GetListTool

:: Get the file association from the registry
FOR /F "tokens=1* delims==" %%A IN ('ASSOC .PDF') DO (
	FOR /F "tokens=1 delims==" %%C IN ('FTYPE ^| FIND /I "%%~B"') DO (
		CALL :GetPrintCommand %%C
	)
)

:: Check if a print command was found
IF NOT DEFINED PrintCmd (
	ECHO.
	ECHO No print command seems to be assiociated with .PDF files on this computer.
	GOTO Syntax
)

:: Print the file using the print command we just found
FOR %%A IN (%FileSpec%) DO CALL :ExecPrintCommand "%%~fA"

:: A final message
IF "%MultiPrint%"=="1" (
	ECHO.
	ECHO You will need to close the Acrobat Reader window manually after the printing
	ECHO is finished.
	IF "%NumFiles%"=="1" IF "%ListTool%"=="" (
		ECHO To close that window automatically next time you print a single PDF file,
		ECHO download and install PSLIST from the Microsoft website:
		ECHO http://www.microsoft.com/technet/sysinternals/utilities/pstools.mspx
	)
)

:: Done
GOTO End


:ExecPrintCommand
CALL START /MIN "PrintPDF" %PrintCmd%
GOTO:EOF


:GetListTool
:: Now we need to find a tool to check for processes.
:: In XP and later this will be the native TASKLIST command,
:: in NT 4 and 2000 we'll need to find a non-native tool.
:: First we'll try TASKLIST ...
TASKLIST >NUL 2>&1
IF ERRORLEVEL 1 (
	REM ... if TASKLIST isn't available we'll try TLIST next ...
	TLIST >NUL 2>&1
	IF ERRORLEVEL 1 (
		REM ... and if that isn't available either we'll try PSLIST ...
		PSLIST >NUL 2>&1
		IF NOT ERRORLEVEL 1 SET ListTool=PSLIST
	) ELSE (
		SET ListTool=TLIST
	)
) ELSE (
	SET ListTool=TASKLIST
)
:: Don't worry if we didn't find ANY tool to list processes, in
:: that case we'll just assume multiple PDFs need to be printed
IF "%ListTool%"=="" SET MultiPrint=1
GOTO:EOF


:GetPrintCommand
:: Get the print command for this file type from the registry
START /WAIT REGEDIT.EXE /E "%Temp%.\pdf.dat" "HKEY_CLASSES_ROOT\%1\shell\print\command"
IF NOT EXIST "%Temp%.\pdf.dat" GOTO:EOF
FOR /F "tokens=1* delims==" %%D IN ('TYPE "%TEMP%.\pdf.dat" ^| FIND "@="') DO SET PrintCmd=%%E
DEL "%Temp%.\pdf.dat"
SET PrintCmd=%PrintCmd:\"="%
SET PrintCmd=%PrintCmd:""="%
SET PrintCmd=%PrintCmd:\\=\%
:: The /T switch terminates Acrobat Reader after printing.
:: Thanks to Fabio Quieti for sending me this tip.
:: However, as Michael Butler pointed out, it should not be
:: used when printing lots of files.
:: So I introduced a /M switch for this batch file, stating
:: that multiple files are to be printed.
:: Without specifying the /M switch, this will also be true
:: when wildcards are used in the filespec.
:: Finally, if another Adobe Reader process is running right
:: now, we won't be using the /T switch either.
IF %MultiPrint% EQU 0 CALL :CheckProcess %PrintCmd%
IF %MultiPrint% EQU 0 (
	SET PrintCmd=%PrintCmd:"%1"=/t "%%%~1"%
	rem SET PrintCmd=%PrintCmd% /t "%%~1"
) ELSE (
	SET PrintCmd=%PrintCmd:"%1"="%%%~1"%
	rem SET PrintCmd=%PrintCmd% "%%~1"
)
GOTO:EOF


:CheckProcess
IF "%ListTool%"=="" (
	SET MultiPrint=1
) ELSE (
	%ListTool% 2>&1 | FIND /I "%~n1" >NUL && SET MultiPrint=1
)
GOTO:EOF

:Syntax
ECHO.
ECHO PrintPDF.bat,  Version 3.11 for Windows NT 4 / 2000 / XP / Server 2003
ECHO Prints PDF files from the command line
ECHO.
ECHO Usage:  PRINTPDF  pdf_filespec  [ /M ]
ECHO.
ECHO Where:  "pdf_filespec"  is the file name or filespec of the PDF file(s)
ECHO                         to be printed; wildcards allowed (*); use double
ECHO                         quotes for long file names
ECHO.
ECHO Notes:  This batch file has been tested with Acrobat Reader versions 5-7 only.
ECHO         It requires Adobe/Acrobat Reader, and will NOT work if Acrobat "Writer"
ECHO         is installed.
ECHO         Thanks to Fabio Quieti, as of version 3.00, you no longer need to close
ECHO         the minimized Acrobat Reader window manually, after printing the file.
ECHO         Thanks to Michael Butler, printing lots of PDFs will no longer make the
ECHO         computer slow down to a crawl or even hang.
ECHO.
ECHO Written by Rob van der Woude
ECHO http://www.robvanderwoude.com


:End
IF "%OS%"=="Windows_NT" ENDLOCAL

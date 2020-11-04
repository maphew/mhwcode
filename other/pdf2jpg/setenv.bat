call y:\Arcutils\setenv_gs.bat
rsync.exe /? >nul 2>&1
if %errorlevel% equ 9009 set path=%path%;%~dp0\bin
@set prompt=(%~p0) $E[m$E[32m$E]9;8;"USERNAME"$E\@$E]9;8;"COMPUTERNAME"$E\$S$E[92m$P$E[90m$_$E[90m$$$E[m$S$E]9;12$E\
@cmd /k
goto :eof

:: ---- scrapbook -----
:: http://stackoverflow.com/questions/23639912/how-to-handle-embedded-x86-in-path-with-parameter-expansion/
  
:: old way, pukes on braces in path or filename

 for %%g in (touch.exe rsync.exe) do (
  if "%%~dp$PATH:g"=="" set PATH=%PATH%;%%~dp0\bin
  )

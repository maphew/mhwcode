@echo.
@echo.=== Setting environment for (%~dp0) ===
@path=%path%;%~dp0\scripts
@call x-help
@echo.
@set prompt=(%~p0) $E[m$E[32m$E]9;8;"USERNAME"$E\@$E]9;8;"COMPUTERNAME"$E\$S$E[92m$P$E[90m$_$E[90m$$$E[m$S$E]9;12$E\
@cmd /k

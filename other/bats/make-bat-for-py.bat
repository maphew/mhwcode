@echo off
for %%g in (*.py) do (
   @echo @python "%%~dpnxg" %%* 
   if not exist %%~ng.bat echo @python "%%~dpnxg" %%*  > %%~ng.bat
   )

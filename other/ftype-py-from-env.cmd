:: doesn't work, because we need to run elevated as admin,
:: and that user doesn't have pythonhome defined.
:: sigh. yet another time when we wish Windows had a true
:: sudo command....
::
rem ftype Python.File="%PYTHONHOME%\python.exe" "%%1" %*

ftype Python.File="c:\users\matt\dropbox\bin\py27.bat" "%%1" %*


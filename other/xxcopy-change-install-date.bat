:: The author of XXCOPY is deceased. The last version ever is 3.33.3, 2016-10-28.
:: There is no possiblity anymore of registering.
::
:: Courtesy of @ZoSTeR, https://ghisler.ch/board/viewtopic.php?p=104655#104655
:: is this recipe to remove the nag screen that shows up after >60 days since
:: xxcopy was installed for unregistered versions.
::
Echo Windows Registry Editor Version 5.00 >TempReg.reg

Echo [HKEY_LOCAL_MACHINE\SOFTWARE\Pixelab\XXCOPY] >>TempReg.reg
Echo "DateInstalled"="2014-11-23 09:51:18" >>TempReg.reg
Echo "DateLastUsed"="2014-11-23 09:51:18" >>TempReg.reg
Echo "Miscellaneous"=hex:00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,\ >>TempReg.reg
Echo   00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,00,5b,5a,5a,5a,5b,5a,5a,\ >>TempReg.reg
Echo   5a,fc,5f,ff,ff,50,8e,6b,07,03,07,d0,01,50,8e,6b,07,03,07,d0,01,5a,5a,5a,5a,\ >>TempReg.reg
Echo   5a,5a,5a,5a,00,00,00,00,38,a7,05,ec >>TempReg.reg

Regedit /s TempReg.reg

Subinacl /keyreg "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\vwintab.exe." /deny=Everyone=F
Subinacl /keyreg "HKEY_LOCAL_MACHINE\SOFTWARE\Pixelab\XXCOPY" /deny=Everyone=S

Del TempReg.reg

2008 January 08, matt wilkie (maphew@gmail.com)

A small collection of things I like to have or change in my FWTools or GDAL environment on Windows.
Basic use guide:

1. Unpack gdal_extras.zip somehwere
2. Install latest version of FWTools
3. Open 'FWTools Shell' and run c:\path\to\gdal_extras\gdal-extras-install.bat

And that's it!

Other than the ease of adding these improvements to new installs, the utility I like the best is gdal-help, because I’m forever forgetting how to spell the commands.

---
Optionally, create an NTFS Junction of c:\local\fwtools to c:\program files\fwtools2.0.4 so you can work with a path without spaces and still accept the installation defaults.
	http://www.microsoft.com/technet/sysinternals/FileAndDisk/Junction.mspx
	http://sourceforge.net/projects/ntfslinkext
	
The following components were written by others. There may be newer/better versions than what I have here.

.\bin\
	fusion.py			- Mario Beauchamp 
	gdalcopyproj.py	- Schuyler Erle
	gdal_vrtmerge.py	- Gabriel Ebner 

.\gdal_plugins\
	gdal_SDE_9x.dll	- Howard Butler
	
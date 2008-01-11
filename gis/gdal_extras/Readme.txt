2008 January 08, matt wilkie (maphew@gmail.com)

A small collection of things I like to have or change in my FWTools or GDAL environment on Windows.
Basic use guide:

1. Install latest version of FWTools
2. Open 'FWTools Shell' and run c:\path\to\gdal_extras\gdal-extras-install.bat

And that's it!

Optionally, create an NTFS Junction of c:\local\fwtools to c:\program files\fwtools2.0.4 so you can work with a path without spaces and still accept the defaults
	http://www.microsoft.com/technet/sysinternals/FileAndDisk/Junction.mspx
	http://sourceforge.net/projects/ntfslinkext
	
The following components were written by others. There may be newer/better versions than what I have here.

.\bin\
	fusion.py			- Mario Beauchamp 
	gdalcopyproj.py	- Schuyler Erle
	gdal_vrtmerge.py	- Gabriel Ebner 

.\gdal_plugins\
	gdal_SDE_9x.dll	- Howard Butler
	









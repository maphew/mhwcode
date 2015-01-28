'''Convert Well Known Text (WKT) spatial reference to Proj4.
    
    Adapted from http://spatialnotes.blogspot.ca/2010/11/converting-wkt-projection-info-to-proj4.html
'''
import os
import sys
import string
import osgeo.osr

if (len(sys.argv) <> 2):
        print 'Usage: wkt2proj.py [WKT Projection Text]'
else:
        srs = osgeo.osr.SpatialReference()
        srs.ImportFromWkt(sys.argv[1])
        print srs.ExportToProj4()
        print srs
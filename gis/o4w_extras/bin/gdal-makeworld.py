#!/usr/bin/env python
#@+leo-ver=5-thin
#@+node:maphew.20110912132233.1584: * @file gdal-makeworld.py
#@@first
#@@language python
#@@tabwidth -4
#@+<<docstring>>
#@+node:maphew.20110912132233.1585: ** <<docstring>>
# 
#  Name:    gdal-makeproj.py
#  Project: GDAL Python Interface
#  Purpose: Create a world file for a georeferenced raster dataset 
#  Author:  Matt Wilkie <matt.wilkie@gov.yk.ca>
# 
#@-<<docstring>>
#@+<<imports>>
#@+node:maphew.20110912132233.1589: ** <<imports>>
try:
    from osgeo import gdal
except ImportError:
    import gdal

import sys
import os.path
#@-<<imports>>
#@+others
#@+node:maphew.20110912132233.1591: ** handle command line args
if len(sys.argv) < 2:
    print "Usage: gdal-makeworld.py source_file"
    sys.exit(1)

input = sys.argv[1]
dataset = gdal.Open( input )
if dataset is None:
    print 'Unable to open', input, 'for reading'
    sys.exit(1)
#@-others

projection   = dataset.GetProjection()
geotransform = dataset.GetGeoTransform()

if projection is None and geotransform is None:
    print 'No projection or geotransform found on file' + input
    sys.exit(1)

# Figure out path and file names
# extension becomes .tfw for tiif, .jgw for jpeg, .blw for bil, etc.
(fpath, fname) = os.path.split(input)
(shortname, ext) = os.path.splitext(fname)
wext = '.' + ext[1] + ext[-1] + 'w'
output = os.path.join (fpath, shortname) + wext

world_file = open (output, 'w')
if world_file is None:
    print 'Unable to open', output, 'for writing'
    sys.exit(1)

if geotransform is not None:
    x, x_size, x_rot, y, y_rot, y_size = geotransform
    # correct for centre vs corner of pixel
    x = x_size/2+x
    y = y_size/2+y
    
    world_file.write('%s\n' % x_size)
    world_file.write('%s\n' % x_rot)
    world_file.write('%s\n' % y_rot)
    world_file.write('%s\n' % y_size)
    world_file.write('%s\n' % x)
    world_file.write('%s\n' % y)
    world_file.close()
    
    print '\nWrote georefencing for', input, 'as', output
    
    # report results, coment out to reduce noise.
    world_file = open(output,'r')
    print '\n', world_file.read()
    
    
#@+at
# @url http://wiki.gis.com/wiki/index.php/World_file
# World files do not specify a coordinate system, so the generic meaning of world file parameters are:
# 
#     Line 1: A, pixel size in the x-direction in map units/pixel
#     Line 2: D: rotation about y-axis
#     Line 3: B: rotation about x-axis
#     Line 4: E: pixel size in the y-direction in map units, almost always negative[3]
#     Line 5: C: x-coordinate of the center of the upper left pixel
#     Line 6: F: y-coordinate of the center of the upper left pixel 
# 
# @url http://www.gdal.org/gdal_tutorial.html 
# The results of gdal GetGeoTransform are:
# 
#     adfGeoTransform[0] /* top left x */
#     adfGeoTransform[1] /* w-e pixel resolution */
#     adfGeoTransform[2] /* rotation, 0 if image is "north up" */
#     adfGeoTransform[3] /* top left y */
#     adfGeoTransform[4] /* rotation, 0 if image is "north up" */
#     adfGeoTransform[5] /* n-s pixel resolution */    
#@@c

#@+<<license>>
#@+node:maphew.20110912132233.1590: ** <<license>>
#******************************************************************************
#  Copyright (c) 2005, Frank Warmerdam
# 
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#******************************************************************************
#@-<<license>>
#@-leo

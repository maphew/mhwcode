import gdal
import sys
import os.path

if len(sys.argv) < 2:
	 print "Usage: gdalsetnull.py raster_file null_value"
	 sys.exit(1)

input = sys.argv[1]
null_value = sys.argv[2]

dataset = gdal.Open( input, gdal.GA_Update )
if dataset is None:
    print 'Unable to open', input, 'for writing'
    sys.exit(1)

for i in range(1, dataset.RasterCount+1):
	band = dataset.GetRasterBand(i)
	print 'Initial nodata for band ',i,'\t', band.GetNoDataValue()
	band.SetNoDataValue( float(null_value) )
	print 'Output nodata for band ',i,'\t', band.GetNoDataValue()
#!/usr/bin/env python
# Tissot Circles
# Represent perfect circles of equal area on a globe
# but will appear distorted in ANY 2d projection.
# Used to show the size, shape and directional distortion
# by Matthew T. Perry
# 12/10/2005
	
import ogr
import os
import osr
	
output = 'tissot.shp'
debug = False
	
# Create the Shapefile
driver = ogr.GetDriverByName('ESRI Shapefile')
if os.path.exists(output):
        driver.DeleteDataSource(output)
ds = driver.CreateDataSource(output)
layer = ds.CreateLayer(output, geom_type=ogr.wkbPolygon)
	
# Set up spatial reference systems
latlong = osr.SpatialReference()
ortho = osr.SpatialReference()
latlong.ImportFromProj4('+proj=latlong')
	
# For each grid point, reproject to ortho centered on itself,
# buffer by 640,000 meters, reproject back to latlong,
# and output the latlong ellipse to shapefile
for x in range(-165,180,30):
    for y in range (-60,90,30):
        f= ogr.Feature(feature_def=layer.GetLayerDefn())
        wkt = 'POINT(%f %f)' % (x, y)
        p = ogr.CreateGeometryFromWkt(wkt)
        p.AssignSpatialReference(latlong)
        proj = '+proj=ortho +lon_0=%f +lat_0=%f' % (x,y)
        ortho.ImportFromProj4(proj)
        p.TransformTo(ortho)
        b = p.Buffer(640000)
        b.AssignSpatialReference(ortho)
        b.TransformTo(latlong)
        f.SetGeometryDirectly(b)
        layer.CreateFeature(f)
        f.Destroy()
	
ds.Destroy()
